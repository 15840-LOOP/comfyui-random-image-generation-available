from __future__ import annotations

import argparse
import asyncio
import hmac
import json
import logging
import os
import shutil
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlsplit

from aiohttp import web

from .comfy import ComfyClient, ComfyError
from .blocked_prompts import BlockedPromptStore
from .catalog import CatalogError, PromptCatalog, SECTIONS, resolve_output_dir
from .custom_prompts import CustomPromptStore
from .favorites import FavoritesService, favorite_key
from .history import CollectionError, HistoryStore
from .lora_triggers import LoraTriggerOverrideStore
from .persistence import load_app_settings, save_app_settings
from .prompt_rules import PromptRuleStore
from .runner import BatchConflict, BatchManager
from .style_presets import StylePresetStore
from .workflow import DEFAULT_SETTINGS, WorkflowError, WorkflowTemplates, normalize_lora_path
from .launcher import configure_resources


APP_DIR = Path(__file__).resolve().parents[1]

logger = logging.getLogger(__name__)

# aiohttp 4 将移除字符串 app key;统一使用 AppKey(消除弃用告警)。
COMFY_KEY: web.AppKey[Any] = web.AppKey("comfy", object)
HISTORY_KEY: web.AppKey[Any] = web.AppKey("history", object)
MANAGER_KEY: web.AppKey[Any] = web.AppKey("manager", object)
CATALOG_KEY: web.AppKey[Any] = web.AppKey("catalog", object)
CUSTOM_PROMPTS_KEY: web.AppKey[Any] = web.AppKey("custom_prompts", object)
FAVORITES_KEY: web.AppKey[Any] = web.AppKey("favorites", object)
STYLE_PRESETS_KEY: web.AppKey[Any] = web.AppKey("style_presets", object)
LORA_TRIGGER_OVERRIDES_KEY: web.AppKey[Any] = web.AppKey("lora_trigger_overrides", object)
PROMPT_RULES_KEY: web.AppKey[Any] = web.AppKey("prompt_rules", object)
BLOCKED_PROMPTS_KEY: web.AppKey[Any] = web.AppKey("blocked_prompts", object)
ALLOWED_HOSTNAMES_KEY: web.AppKey[frozenset[str]] = web.AppKey(
    "allowed_hostnames", frozenset
)
OUTPUT_DIR_KEY: web.AppKey[Any] = web.AppKey("output_dir", object)

LOCAL_HOSTNAMES = {"127.0.0.1", "localhost", "::1"}


def _hostname(value: str) -> str:
    """从 Host 头(host[:port])或 Origin(scheme://host[:port])提取主机名。"""
    try:
        target = value if "://" in value else f"//{value}"
        return (urlsplit(target).hostname or "").lower()
    except ValueError:
        return ""


@web.middleware
async def local_only_middleware(request: web.Request, handler: Any) -> web.StreamResponse:
    # 只信任本机来源:防御恶意网页发起的 CSRF 与 DNS 重绑定。
    allowed_hostnames = request.app[ALLOWED_HOSTNAMES_KEY]
    if _hostname(request.host or "") not in allowed_hostnames:
        return web.json_response({"error": "仅允许本机访问"}, status=403)
    origin = request.headers.get("Origin")
    if origin is not None and (origin == "null" or _hostname(origin) not in allowed_hostnames):
        return web.json_response({"error": "仅允许本机来源"}, status=403)
    return await handler(request)


@web.middleware
async def error_middleware(request: web.Request, handler: Any) -> web.StreamResponse:
    try:
        response = await handler(request)
    except WorkflowError as error:
        return web.json_response({"error": str(error)}, status=400)
    except CollectionError as error:
        return web.json_response({"error": str(error)}, status=400)
    except CatalogError as error:
        return web.json_response({"error": str(error)}, status=400)
    except BatchConflict as error:
        return web.json_response({"error": str(error)}, status=409)
    except KeyError:
        return web.json_response({"error": "记录不存在"}, status=404)
    except ComfyError as error:
        return web.json_response({"error": str(error)}, status=503)
    except json.JSONDecodeError:
        return web.json_response({"error": "请求 JSON 无效"}, status=400)
    if request.path == "/" or request.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache, max-age=0, must-revalidate"
        response.headers["Pragma"] = "no-cache"
    return response


async def _json_body(request: web.Request) -> dict[str, Any]:
    try:
        value = await request.json()
    except Exception as error:
        raise WorkflowError("请求 JSON 无效") from error
    if not isinstance(value, dict):
        raise WorkflowError("请求内容必须是对象")
    return value


def _query_bool(request: web.Request, name: str, default: bool = False) -> bool:
    raw = request.query.get(name)
    if raw is None:
        return default
    if raw.lower() in {"1", "true", "yes"}:
        return True
    if raw.lower() in {"0", "false", "no"}:
        return False
    raise WorkflowError(f"{name} 必须是布尔值")


def _resolve_image_disk_path(
    output_dir: Path | str | None, record: dict[str, Any]
) -> Path | None:
    """计算历史记录对应图片在磁盘中的绝对路径。

    - 未配置 output_dir 时返回 None;
    - filename / subfolder 非法(绝对路径、盘符、.. 等)时返回 None;
    - 解析后越出 output_dir 作用域(含符号链接越界)时返回 None。
    调用方据此决定是否执行 unlink,任何情况下都不会删除 output_dir 之外的文件。
    """
    if output_dir is None:
        return None
    try:
        filename = normalize_lora_path(record.get("filename"))
        subfolder = str(record.get("subfolder") or "").strip()
        if subfolder:
            subfolder = normalize_lora_path(subfolder)
    except WorkflowError:
        return None
    root = Path(output_dir)
    target = root / subfolder if subfolder else root
    target = (target / filename).resolve()
    # 二次确认解析结果仍位于 output 目录内(防符号链接/穿越越界)。
    if not target.is_relative_to(root.resolve()):
        return None
    return target


def _reveal_in_file_manager(path: Path) -> None:
    """在系统文件管理器中定位并高亮选中该文件(阻塞调用,须经 to_thread 执行)。

    Windows 使用 explorer /select 直接选中;其他平台退化为打开所在目录。
    """
    if sys.platform.startswith("win"):
        explorer = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "explorer.exe")
        subprocess.run([explorer, "/select,", str(path)], check=False)
    elif sys.platform == "darwin":
        subprocess.run(["open", "-R", str(path)], check=False)
    else:
        subprocess.run(["xdg-open", str(path.parent)], check=False)


def _open_directory(path: Path) -> None:
    """在系统文件管理器中直接打开目录本身(阻塞调用,须经 to_thread 执行)。"""
    if sys.platform.startswith("win"):
        os.startfile(str(path))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=False)
    else:
        subprocess.run(["xdg-open", str(path)], check=False)


def _system_pick_folder() -> str:
    """唤起本地原生目录选择弹窗,返回绝对路径字符串;取消则返回空字符串。

    优先使用 tkinter;整合包精简环境缺少 tkinter 时回退到 PowerShell 对话框。
    """
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askdirectory(title="选择图片快捷导出文件夹")
        root.destroy()
        return os.path.normpath(path) if path else ""
    except Exception:
        # 兼容无 tkinter 的嵌入式 Python 环境
        if sys.platform.startswith("win"):
            cmd = (
                'powershell -NoProfile -Command "'
                "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; "
                "$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
                "$f.Description = '选择图片快捷导出文件夹'; "
                "if ($f.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) "
                "{ Write-Output $f.SelectedPath }\""
            )
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, check=False)
                picked = res.stdout.strip()
                return os.path.normpath(picked) if res.returncode == 0 and picked else ""
            except Exception:
                return ""
        return ""


def create_app(
    *,
    app_dir: str | Path = APP_DIR,
    comfy: Any | None = None,
    history_path: str | Path | None = None,
    custom_prompts_path: str | Path | None = None,
    style_presets_path: str | Path | None = None,
    lora_trigger_overrides_path: str | Path | None = None,
    prompt_replacements_path: str | Path | None = None,
    blocked_prompts_path: str | Path | None = None,
    anima_tools_dir: str | Path | None = None,
    trusted_hostnames: set[str] | frozenset[str] | None = None,
    data_dir: str | Path | None = None,
    resource_paths: dict[str, str] | None = None,
    shutdown_token: str | None = None,
    output_dir: str | Path | None = None,
) -> web.Application:
    root = Path(app_dir)
    storage = Path(data_dir) if data_dir is not None else root / "data"
    client = comfy or ComfyClient()
    resolved_output_dir = resolve_output_dir(root, output_dir)
    history = HistoryStore(history_path or storage / "history.sqlite3")
    catalog = PromptCatalog(root, anima_tools_dir)
    custom_prompts = CustomPromptStore(
        custom_prompts_path or storage / "custom_prompts.json", catalog
    )
    favorites = FavoritesService(client, catalog)
    prompt_rules = PromptRuleStore(
        prompt_replacements_path or storage / "prompt_replacements.json"
    )
    lora_trigger_overrides = LoraTriggerOverrideStore(
        lora_trigger_overrides_path or storage / "lora_trigger_overrides.json"
    )
    style_presets = StylePresetStore(
        style_presets_path or storage / "style_presets.json", prompt_rules
    )
    blocked_prompts = BlockedPromptStore(
        blocked_prompts_path or storage / "blocked_prompts.json"
    )
    templates = WorkflowTemplates.load(root / "templates")
    startup_defaults = configure_resources(templates, resource_paths)
    manager = BatchManager(
        templates, history, client, catalog, prompt_rules, blocked_prompts
    )

    startup_warnings = [
        *history.load_warnings,
        *custom_prompts.load_warnings,
        *style_presets.load_warnings,
        *lora_trigger_overrides.load_warnings,
        *prompt_rules.load_warnings,
        *blocked_prompts.load_warnings,
    ]

    app = web.Application(middlewares=[error_middleware, local_only_middleware])
    normalized_trusted_hostnames = {
        hostname
        for value in trusted_hostnames or set()
        if (hostname := _hostname(value))
    }
    app[ALLOWED_HOSTNAMES_KEY] = frozenset(LOCAL_HOSTNAMES | normalized_trusted_hostnames)
    app[COMFY_KEY] = client
    app[HISTORY_KEY] = history
    app[MANAGER_KEY] = manager
    app[CATALOG_KEY] = catalog
    app[CUSTOM_PROMPTS_KEY] = custom_prompts
    app[FAVORITES_KEY] = favorites
    app[STYLE_PRESETS_KEY] = style_presets
    app[LORA_TRIGGER_OVERRIDES_KEY] = lora_trigger_overrides
    app[PROMPT_RULES_KEY] = prompt_rules
    app[BLOCKED_PROMPTS_KEY] = blocked_prompts
    app[OUTPUT_DIR_KEY] = resolved_output_dir

    async def favorite_keys(section: str, collection: str = "") -> set[str] | None:
        if not collection:
            return None
        payload = await favorites.get(section)
        collection_ids = {collection}
        if collection != "__all__":
            pending = [collection]
            while pending:
                parent_id = pending.pop()
                children = [
                    group["id"]
                    for group in payload["groups"]
                    if group.get("parentId") == parent_id and group["id"] not in collection_ids
                ]
                collection_ids.update(children)
                pending.extend(children)
        return {
            favorite_key(section, item)
            for item in payload["items"]
            if (collection == "__all__" and item.get("groupIds"))
            or bool(collection_ids.intersection(item.get("groupIds") or []))
        }

    async def config(_: web.Request) -> web.Response:
        return web.json_response(
            {
                "defaults": startup_defaults,
                "comfy_url": getattr(client, "base_url", "local"),
                "output_dir": str(resolved_output_dir or ""),
                "catalog": {
                    "available": catalog.available,
                    "path": str(catalog.tools_dir or ""),
                    "counts": {section: catalog.count(section) for section in SECTIONS},
                },
                "warnings": startup_warnings,
            }
        )

    async def _pool_response(
        section: str, params: dict[str, Any], selection: dict[str, Any] | None
    ) -> web.Response:
        """GET /api/pools 与 POST /api/pools/query 共用的参数归一化与搜索。"""
        try:
            page = int(params.get("page") or 1)
            limit = int(params.get("limit") or 48)
        except (TypeError, ValueError) as error:
            raise WorkflowError("分页参数无效") from error
        collection = str(params.get("collection") or "")
        sort = str(params.get("sort") or "")
        custom_group = str(params.get("custom_group") or "")
        blocked_only = str(params.get("blocked_only") or "").lower() in {"1", "true"}
        blocked_set = blocked_prompts.get_blocked_ids(section)
        keys = await favorite_keys(section, collection or ("__all__" if sort == "favorite-first" else ""))
        result = catalog.search(
            section,
            query=str(params.get("q") or ""),
            categories=[str(value) for value in params.get("categories") or []],
            traits=[str(value) for value in params.get("traits") or []],
            gender=str(params.get("gender") or ""),
            hair=str(params.get("hair") or ""),
            eye=str(params.get("eye") or ""),
            series=str(params.get("series") or ""),
            custom_group=custom_prompts.group_filter_ids(section, custom_group)
            if custom_group
            else "",
            favorite_keys=keys,
            favorites_only=bool(collection),
            sort=sort,
            page=page,
            limit=limit,
            selection=selection,
            blocked_ids=blocked_set,
            blocked_only=blocked_only,
        )
        result["blocked_count"] = len(blocked_set)
        return web.json_response(result)

    async def pool(request: web.Request) -> web.Response:
        params: dict[str, Any] = {
            key: request.query.get(key, "")
            for key in (
                "q", "gender", "hair", "eye", "series", "custom_group",
                "collection", "sort", "blocked_only",
            )
        }
        params["page"] = request.query.get("page", "1")
        params["limit"] = request.query.get("limit", "48")
        params["categories"] = request.query.getall("category", [])
        params["traits"] = request.query.getall("trait", [])
        return await _pool_response(request.match_info["section"], params, None)

    async def pool_query(request: web.Request) -> web.Response:
        body = await _json_body(request)
        params = dict(body)
        params["categories"] = body.get("categories") if isinstance(body.get("categories"), list) else []
        params["traits"] = body.get("traits") if isinstance(body.get("traits"), list) else []
        selection = body.get("selection") if isinstance(body.get("selection"), dict) else None
        return await _pool_response(request.match_info["section"], params, selection)

    async def get_blocked_prompts(_: web.Request) -> web.Response:
        return web.json_response(blocked_prompts.snapshot())

    async def toggle_blocked_prompt(request: web.Request) -> web.Response:
        section = request.match_info["section"]
        if section not in SECTIONS:
            raise WorkflowError(f"不支持的卡池: {section}")
        body = await _json_body(request)
        item_id = body.get("id")
        if not item_id:
            raise WorkflowError("id 不能为空")
        is_blocked = await blocked_prompts.toggle(section, str(item_id))
        return web.json_response(
            {
                "section": section,
                "id": str(item_id),
                "blocked": is_blocked,
                "blocked_count": len(blocked_prompts.get_blocked_ids(section)),
            }
        )

    async def get_favorites(request: web.Request) -> web.Response:
        return web.json_response(await favorites.get(request.match_info["section"]))

    async def update_favorite(request: web.Request) -> web.Response:
        return web.json_response(
            await favorites.update_item(request.match_info["section"], await _json_body(request))
        )

    async def update_favorite_selection(request: web.Request) -> web.Response:
        body = await _json_body(request)
        return web.json_response(
            await favorites.update_selection(
                request.match_info["section"], body.get("selection"), body.get("groupIds")
            )
        )

    async def create_favorite_group(request: web.Request) -> web.Response:
        return web.json_response(
            await favorites.create_group(request.match_info["section"], await _json_body(request)),
            status=201,
        )

    async def update_favorite_group(request: web.Request) -> web.Response:
        return web.json_response(
            await favorites.update_group(
                request.match_info["section"], request.match_info["group_id"], await _json_body(request)
            )
        )

    async def import_favorite_child_group(request: web.Request) -> web.Response:
        section = request.match_info["section"]
        body = await _json_body(request)
        custom_group_id = str(body.get("customGroupId") or "").strip()
        if not custom_group_id:
            raise WorkflowError("customGroupId 不能为空")
        source_group = next(
            (
                group
                for group in custom_prompts.list_groups(section)["groups"]
                if group["id"] == custom_group_id
            ),
            None,
        )
        if source_group is None:
            raise KeyError(custom_group_id)
        return web.json_response(
            await favorites.import_custom_group(
                section,
                request.match_info["parent_id"],
                source_group,
                custom_prompts.list(section, custom_group_id),
            ),
            status=201,
        )

    async def delete_favorite_group(request: web.Request) -> web.Response:
        return web.json_response(
            await favorites.delete_group(
                request.match_info["section"],
                request.match_info["group_id"],
                _query_bool(request, "deleteItems"),
            )
        )

    async def list_custom_prompts(request: web.Request) -> web.Response:
        section = request.query.get("section") or None
        return web.json_response({"items": custom_prompts.list(section)})

    async def create_custom_prompt(request: web.Request) -> web.Response:
        return web.json_response(await custom_prompts.create(await _json_body(request)), status=201)

    async def update_custom_prompt(request: web.Request) -> web.Response:
        item = await custom_prompts.update(request.match_info["item_id"], await _json_body(request))
        try:
            await favorites.sync_custom(item["section"], item)
        except ComfyError as error:
            logger.warning("同步收藏昵称失败(条目 %s): %s", item.get("id"), error)
        return web.json_response(item)

    async def delete_custom_prompt(request: web.Request) -> web.Response:
        if not await custom_prompts.delete(request.match_info["item_id"]):
            raise KeyError(request.match_info["item_id"])
        return web.json_response({"deleted": True})

    async def list_custom_groups(request: web.Request) -> web.Response:
        return web.json_response(custom_prompts.list_groups(request.match_info["section"]))

    async def create_custom_group(request: web.Request) -> web.Response:
        return web.json_response(
            await custom_prompts.create_group(request.match_info["section"], await _json_body(request)),
            status=201,
        )

    async def update_custom_group(request: web.Request) -> web.Response:
        return web.json_response(
            await custom_prompts.update_group(
                request.match_info["section"], request.match_info["group_id"], await _json_body(request)
            )
        )

    async def delete_custom_group(request: web.Request) -> web.Response:
        delete_mode = request.query.get("deleteMode")
        delete_items = False if delete_mode is not None else _query_bool(request, "deleteItems")
        return web.json_response(
            await custom_prompts.delete_group(
                request.match_info["section"],
                request.match_info["group_id"],
                delete_items,
                delete_mode,
            )
        )

    async def custom_template(request: web.Request) -> web.Response:
        filename, content_type, body = custom_prompts.template(
            request.match_info["section"], request.match_info["format"]
        )
        return web.Response(
            body=body,
            content_type=content_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    async def preview_custom_import(request: web.Request) -> web.Response:
        body = await _json_body(request)
        return web.json_response(
            custom_prompts.preview_import(
                str(body.get("format") or ""),
                str(body.get("content") or ""),
                str(body.get("section") or ""),
                str(body.get("bundleName") or ""),
            )
        )

    async def commit_custom_import(request: web.Request) -> web.Response:
        body = await _json_body(request)
        return web.json_response(
            await custom_prompts.commit_import(
                body.get("rows"),
                str(body.get("section") or ""),
                body.get("targetGroupIds"),
                str(body.get("bundleName") or ""),
            )
        )

    async def status(_: web.Request) -> web.Response:
        try:
            stats = await client.status()
            system = stats.get("system") or {}
            devices = stats.get("devices") or []
            return web.json_response(
                {
                    "online": True,
                    "version": system.get("comfyui_version", ""),
                    "device": devices[0].get("name", "") if devices else "",
                }
            )
        except ComfyError as error:
            return web.json_response({"online": False, "error": str(error)})

    async def _lora_inventory_item(filename: Any) -> tuple[dict[str, Any], str]:
        target = str(filename or "")
        if not target:
            raise WorkflowError("filename 不能为空")
        from .workflow import normalize_lora_path

        identity = normalize_lora_path(target).casefold()
        inventory = await client.lora_inventory()
        matches = [
            item
            for item in inventory.get("items") or []
            if normalize_lora_path(item.get("filename")).casefold() == identity
        ]
        if len(matches) != 1:
            raise WorkflowError(f"LoRA 文件不存在: {target}")
        return matches[0], normalize_lora_path(matches[0]["filename"])

    def _public_lora_item(item: dict[str, Any]) -> dict[str, Any]:
        value = dict(item)
        source_words = value.get("trigger_words") or []
        effective_words, overridden = lora_trigger_overrides.effective(
            value["filename"], source_words
        )
        value["source_trigger_words"] = source_words
        value["trigger_words"] = effective_words
        value["trigger_override"] = overridden
        if overridden:
            value["trigger_metadata_available"] = True
        preview = str(value.get("preview") or "")
        value["preview"] = (
            f"/api/loras/preview?{urlencode({'filename': value['filename']})}"
            if preview
            else ""
        )
        return value

    async def loras(_: web.Request) -> web.Response:
        inventory = await client.lora_inventory()
        public = {
            "items": [],
            "count": inventory.get("count", 0),
        }
        for item in inventory.get("items") or []:
            public["items"].append(_public_lora_item(item))
        return web.json_response(public)

    async def update_lora_triggers(request: web.Request) -> web.Response:
        body = await _json_body(request)
        item, filename = await _lora_inventory_item(body.get("filename"))
        words = await lora_trigger_overrides.set(filename, body.get("triggerWords"))
        value = _public_lora_item({**item, "filename": filename})
        value["trigger_words"] = words
        value["trigger_override"] = True
        return web.json_response(value)

    async def reset_lora_triggers(request: web.Request) -> web.Response:
        item, filename = await _lora_inventory_item(request.query.get("filename"))
        await lora_trigger_overrides.delete(filename)
        return web.json_response(_public_lora_item({**item, "filename": filename}))

    async def lora_preview(request: web.Request) -> web.Response:
        filename = request.query.get("filename")
        if not filename:
            raise WorkflowError("filename 不能为空")
        body, content_type, cache_control = await client.lora_preview(filename)
        return web.Response(
            body=body,
            content_type=content_type.split(";", 1)[0],
            headers={"Cache-Control": cache_control},
        )

    async def resources(_: web.Request) -> web.Response:
        return web.json_response(await client.resource_inventory())

    async def list_style_presets(request: web.Request) -> web.Response:
        # collection_id 为空或 0 表示“全部预设”,仅正整数才按收藏夹过滤。
        raw_collection = request.query.get("collection_id", "")
        try:
            collection_id = int(raw_collection) if raw_collection else 0
        except ValueError as error:
            raise WorkflowError("collection_id 必须是整数") from error
        return web.json_response(
            style_presets.list(collection_id=collection_id if collection_id > 0 else None)
        )

    async def _parse_preset_request(request: web.Request) -> tuple[dict[str, Any], bytes | None]:
        """解析预设提交,返回 (payload, 缩略图字节)。

        支持两种形态:
        - multipart/form-data:表单字段 name/settings/favorite + 文件字段 thumbnail/file/image;
        - application/json:JSON 体,可选 source_image_id 引用作品库图片作为缩略图。
        """
        if request.content_type.startswith("multipart/"):
            # request.post() 一次性消费 body 并解析出文本字段与文件字段,
            # 不可再调用 request.multipart()(body 已被读取)。
            form = await request.post()
            payload: dict[str, Any] = {}
            raw_settings = form.get("settings")
            if raw_settings is not None:
                try:
                    payload["settings"] = json.loads(str(raw_settings))
                except json.JSONDecodeError as error:
                    raise WorkflowError("settings 不是有效 JSON") from error
            if form.get("name") is not None:
                payload["name"] = str(form.get("name"))
            if form.get("favorite") is not None:
                payload["favorite"] = str(form.get("favorite")).lower() in {"1", "true", "yes"}
            thumbnail_bytes: bytes | None = None
            for field in ("thumbnail", "file", "image"):
                upload = form.get(field)
                # aiohttp 的 FileField 暴露 .file(BytesIO);文本字段是 str。
                if upload is not None and hasattr(upload, "file"):
                    handle = upload.file
                    handle.seek(0)
                    thumbnail_bytes = handle.read()
                    break
            return payload, thumbnail_bytes
        payload = await _json_body(request)
        thumbnail_bytes = await _resolve_source_thumbnail(payload.pop("source_image_id", None))
        return payload, thumbnail_bytes

    async def _resolve_source_thumbnail(source_image_id: Any) -> bytes | None:
        """按作品库图片 ID 取原图字节作为缩略图;ID 非法或不存在时报错。"""
        if source_image_id is None or isinstance(source_image_id, bool):
            return None
        try:
            image_id = int(source_image_id)
        except (TypeError, ValueError):
            raise WorkflowError("source_image_id 必须是整数")
        try:
            record = await history.get_image(image_id)
        except KeyError:
            raise WorkflowError(f"作品库图片不存在: {image_id}")
        body, _content_type = await client.image_bytes(record)
        return body

    async def create_style_preset(request: web.Request) -> web.Response:
        payload, thumbnail_bytes = await _parse_preset_request(request)
        item = await style_presets.create(payload)
        if thumbnail_bytes:
            await style_presets.save_thumbnail(item["id"], thumbnail_bytes)
            item = {**item, "thumbnail_url": style_presets.thumbnail_url(item["id"])}
        return web.json_response(item, status=201)

    async def update_style_preset(request: web.Request) -> web.Response:
        preset_id = request.match_info["preset_id"]
        payload, thumbnail_bytes = await _parse_preset_request(request)
        item = await style_presets.update(preset_id, payload)
        if thumbnail_bytes:
            await style_presets.save_thumbnail(preset_id, thumbnail_bytes)
            item = {**item, "thumbnail_url": style_presets.thumbnail_url(preset_id)}
        return web.json_response(item)

    async def style_preset_thumbnail(request: web.Request) -> web.Response:
        preset_id = request.match_info["preset_id"]
        path = style_presets.thumbnail_path(preset_id)
        if not path.is_file():
            raise web.HTTPNotFound()
        return web.FileResponse(path, headers={"Cache-Control": "no-cache"})

    async def delete_style_preset(request: web.Request) -> web.Response:
        if not await style_presets.delete(request.match_info["preset_id"]):
            raise KeyError(request.match_info["preset_id"])
        return web.json_response({"deleted": True})

    async def list_style_preset_collections(_: web.Request) -> web.Response:
        # 与 /api/gallery/collections 对称:一次性返回全库总数与各收藏夹统计。
        return web.json_response(style_presets.list_collections())

    async def create_style_preset_collection(request: web.Request) -> web.Response:
        body = await _json_body(request)
        name = body.get("name")
        if not isinstance(name, str):
            raise WorkflowError("name 必须是字符串")
        # 可选 parent_id:缺省创建母文件夹,给出时创建其下的子文件夹。
        raw_parent = body.get("parent_id")
        parent_id: int | None = None
        if raw_parent is not None:
            try:
                parent_id = int(raw_parent)
            except (TypeError, ValueError) as error:
                raise WorkflowError("parent_id 必须是整数") from error
        created = await style_presets.create_collection(name, parent_id=parent_id)
        return web.json_response(created, status=201)

    async def delete_style_preset_collection(request: web.Request) -> web.Response:
        collection_id = int(request.match_info["collection_id"])
        # 默认收藏夹(ID:1)与不存在的分类由 store 抛出 WorkflowError/KeyError,
        # 中间件统一转为 400/404;返回值携带级联删除的子分类信息。
        result = await style_presets.delete_collection(collection_id)
        return web.json_response(result)

    async def update_style_preset_collection(request: web.Request) -> web.Response:
        collection_id = int(request.match_info["collection_id"])
        body = await _json_body(request)
        name = body.get("name")
        if not isinstance(name, str):
            raise WorkflowError("name 必须是字符串")
        return web.json_response(await style_presets.update_collection(collection_id, name))

    async def toggle_style_preset_default_favorite(request: web.Request) -> web.Response:
        preset_id = request.match_info["preset_id"]
        return web.json_response(await style_presets.toggle_default_favorite(preset_id))

    async def set_style_preset_collections(request: web.Request) -> web.Response:
        preset_id = request.match_info["preset_id"]
        body = await _json_body(request)
        collection_ids = body.get("collection_ids")
        if not isinstance(collection_ids, list):
            raise WorkflowError("collection_ids 必须是整数数组")
        return web.json_response(
            await style_presets.set_preset_collections(preset_id, collection_ids)
        )

    def _batch_preset_ids(body: dict[str, Any]) -> list[str]:
        """归一化批量预设 ID 入参:必须是数组,去空去重并保持原顺序。"""
        raw = body.get("preset_ids")
        if not isinstance(raw, list):
            raise WorkflowError("preset_ids 必须是数组")
        result: list[str] = []
        for val in raw:
            if isinstance(val, bool):
                continue
            text = str(val or "").strip()
            if text and text not in result:
                result.append(text)
        return result

    async def batch_delete_style_presets(request: web.Request) -> web.Response:
        """批量删除预设:单事务写盘,并同步物理删除封面缩略图。"""
        body = await _json_body(request)
        preset_ids = _batch_preset_ids(body)
        if not preset_ids:
            raise WorkflowError("preset_ids 不能为空")
        deleted_count = await style_presets.delete_batch(preset_ids)
        return web.json_response(
            {"deleted": deleted_count, "requested": len(preset_ids)}
        )

    async def batch_update_preset_collections(request: web.Request) -> web.Response:
        """批量调整预设所属分类,支持 add / remove / set 三种模式。"""
        body = await _json_body(request)
        preset_ids = _batch_preset_ids(body)
        if not preset_ids:
            raise WorkflowError("preset_ids 不能为空")
        mode = str(body.get("mode") or "").strip()
        collection_ids = body.get("collection_ids")
        if not isinstance(collection_ids, list):
            raise WorkflowError("collection_ids 必须是整数数组")
        updated = await style_presets.batch_update_collections(
            preset_ids, collection_ids, mode
        )
        return web.json_response(
            {"mode": mode, "updated": updated, "updated_count": len(updated)}
        )

    async def list_prompt_rules(_: web.Request) -> web.Response:
        return web.json_response(prompt_rules.list())

    async def create_prompt_rule(request: web.Request) -> web.Response:
        return web.json_response(
            await prompt_rules.create(await _json_body(request)), status=201
        )

    async def update_prompt_rule(request: web.Request) -> web.Response:
        return web.json_response(
            await prompt_rules.update(
                request.match_info["rule_id"], await _json_body(request)
            )
        )

    async def delete_prompt_rule(request: web.Request) -> web.Response:
        rule_id = request.match_info["rule_id"]
        if not await prompt_rules.delete(rule_id):
            raise KeyError(rule_id)
        return web.json_response({"deleted": True})

    async def normalize_prompts(request: web.Request) -> web.Response:
        body = await _json_body(request)
        unknown = set(body) - {"fields", "managedTriggers"}
        if unknown:
            raise WorkflowError(f"提示词规范请求包含未知参数: {', '.join(sorted(unknown))}")
        return web.json_response(
            prompt_rules.normalize_fields(
                body.get("fields"), body.get("managedTriggers", [])
            )
        )

    async def start_batch(request: web.Request) -> web.Response:
        await client.status()
        body = await _json_body(request)
        seeds = body.pop("seeds", None)  # 复现历史图片时携带固定种子,不属于 settings
        if resource_paths is not None:
            body = {**startup_defaults, **body}
        state = await manager.start(body, seeds=seeds)
        return web.json_response(state, status=201)

    async def current_batch(_: web.Request) -> web.Response:
        return web.json_response({"batch": manager.snapshot(), "queue": manager.queue_snapshot()})

    async def stop_batch(request: web.Request) -> web.Response:
        state = await manager.request_stop(
            request.match_info["batch_id"],
            clear_queue=_query_bool(request, "clearQueue", True),
        )
        return web.json_response({"batch": state, "queue": manager.queue_snapshot()})

    async def remove_queued_batch(request: web.Request) -> web.Response:
        if not manager.remove_queued(request.match_info["queue_id"]):
            raise KeyError(request.match_info["queue_id"])
        return web.json_response({"queue": manager.queue_snapshot()})

    async def batch_preview(_: web.Request) -> web.Response:
        preview = manager.preview
        if preview is None:
            return web.Response(status=204)
        _seq, content_type, body = preview
        return web.Response(body=body, content_type=content_type, headers={"Cache-Control": "no-store"})

    async def list_history(request: web.Request) -> web.Response:
        try:
            page = int(request.query.get("page", "1"))
            limit = int(request.query.get("limit", "24"))
            raw_collection = request.query.get("collection_id", "")
            collection_id = int(raw_collection) if raw_collection else 0
        except ValueError as error:
            raise WorkflowError("分页参数无效") from error
        # 0 或空值表示“全部作品”,仅正整数才按收藏夹过滤。
        return web.json_response(
            await history.list_images(
                page, limit, collection_id=collection_id if collection_id > 0 else None
            )
        )

    async def list_gallery_collections(_: web.Request) -> web.Response:
        # 同时返回全库图片总数,前端胶囊栏无需依赖其他异步请求的时序。
        collections = await history.list_collections()
        all_total = await history.count_images()
        return web.json_response({"all_total": all_total, "collections": collections})

    async def create_gallery_collection(request: web.Request) -> web.Response:
        body = await _json_body(request)
        name = body.get("name")
        if not isinstance(name, str):
            raise CollectionError("name 必须是字符串")
        return web.json_response(await history.create_collection(name), status=201)

    async def delete_gallery_collection(request: web.Request) -> web.Response:
        collection_id = int(request.match_info["collection_id"])
        await history.delete_collection(collection_id)
        return web.json_response({"deleted": True, "id": collection_id})

    async def update_gallery_collection(request: web.Request) -> web.Response:
        collection_id = int(request.match_info["collection_id"])
        body = await _json_body(request)
        name = body.get("name")
        if not isinstance(name, str):
            raise CollectionError("name 必须是字符串")
        return web.json_response(await history.update_collection(collection_id, name))

    async def toggle_default_favorite(request: web.Request) -> web.Response:
        image_id = int(request.match_info["image_id"])
        return web.json_response(await history.toggle_default_favorite(image_id))

    async def set_image_collections(request: web.Request) -> web.Response:
        image_id = int(request.match_info["image_id"])
        body = await _json_body(request)
        collection_ids = body.get("collection_ids")
        if not isinstance(collection_ids, list):
            raise CollectionError("collection_ids 必须是整数数组")
        updated = await history.set_image_collections(image_id, collection_ids)
        return web.json_response({"image_id": image_id, "collection_ids": updated})

    async def _regeneration_context(image_id: int) -> tuple[dict[str, Any], dict[str, Any]]:
        record = await history.get_image(image_id)
        settings = dict(record.get("settings") or {})
        positive = ""
        for candidate in (record.get("positive_prompt"), record.get("resolved_prompt")):
            text = str(candidate or "")
            if text.strip():
                positive = text
                break
        negative = ""
        for candidate in (record.get("negative_prompt"), settings.get("negative_prompt")):
            text = str(candidate or "")
            if text.strip():
                negative = text
                break
        selected = record.get("resolved_selection") or {}
        if not isinstance(selected, dict):
            selected = {}
        resource_issues = await manager.resource_issues(settings)
        sections: dict[str, Any] = {}
        for section in SECTIONS:
            random_enabled = bool(settings.get(f"random_{section}"))
            actual = selected.get(section) if isinstance(selected.get(section), list) else []
            sections[section] = {
                "random": random_enabled,
                "hasSnapshot": bool(actual),
                "canRedraw": random_enabled,
            }
        warnings = [
            "资源文件内容已被覆盖时无法识别，原种子重跑不承诺像素级一致。"
        ]
        if not positive:
            warnings.append("历史记录缺少最终正向提示词，无法可靠回放。")
        context = {
            "positive": positive,
            "negative": negative,
            "selected": selected,
            "resourceIssues": resource_issues,
            "sections": sections,
            "warnings": warnings,
        }
        return record, context

    async def regeneration_options(request: web.Request) -> web.Response:
        _record, context = await _regeneration_context(
            int(request.match_info["image_id"])
        )
        resources_ok = not context["resourceIssues"]
        positive_ok = bool(context["positive"])
        random_sections = [
            section for section, value in context["sections"].items() if value["random"]
        ]
        return web.json_response(
            {
                "modes": {
                    "replay": {
                        "available": resources_ok and positive_ok,
                        "reasons": _regeneration_reasons(context, require_prompt=True),
                    },
                    "prompt_variant": {
                        "available": resources_ok and positive_ok,
                        "reasons": _regeneration_reasons(context, require_prompt=True),
                    },
                    "content_redraw": {
                        "available": resources_ok and bool(random_sections),
                        "reasons": _regeneration_reasons(
                            context, require_random=bool(random_sections)
                        ),
                    },
                    "settings_reroll": {
                        "available": resources_ok,
                        "reasons": _regeneration_reasons(context),
                    },
                },
                "resourceIssues": context["resourceIssues"],
                "warnings": context["warnings"],
                "sections": context["sections"],
            }
        )

    def _regeneration_reasons(
        context: dict[str, Any],
        *,
        require_prompt: bool = False,
        require_random: bool = True,
    ) -> list[str]:
        reasons = [
            f"{item['label']} 不可用: {item['name']}"
            for item in context["resourceIssues"]
        ]
        if require_prompt and not context["positive"]:
            reasons.append("历史记录缺少最终正向提示词")
        if require_random is False:
            reasons.append("历史设置没有可重新抽取的随机维度")
        return reasons

    async def regenerate_history(request: web.Request) -> web.Response:
        await client.status()
        record, context = await _regeneration_context(
            int(request.match_info["image_id"])
        )
        body = await _json_body(request)
        unknown = set(body) - {"mode", "count", "sections"}
        if unknown:
            raise WorkflowError(
                f"再生成请求包含未知参数: {', '.join(sorted(unknown))}"
            )
        mode = body.get("mode")
        if mode not in {"replay", "prompt_variant", "content_redraw", "settings_reroll"}:
            raise WorkflowError("mode 无效")
        if context["resourceIssues"]:
            missing = "；".join(
                f"{item['label']}: {item['name']}" for item in context["resourceIssues"]
            )
            raise WorkflowError(f"历史资源不可用: {missing}")
        settings = dict(record.get("settings") or {})
        if mode == "replay":
            if set(body) - {"mode"}:
                raise WorkflowError("replay 不接受 count 或 sections")
            if not context["positive"]:
                raise WorkflowError("历史记录缺少可回放的最终正向提示词")
            settings["count"] = 1
            regeneration = {
                "mode": mode,
                "frozen_positive_prompt": context["positive"],
                "frozen_negative_prompt": context["negative"],
                "fixed_selection": context["selected"],
            }
            seeds = {
                "sample_seed": record["sample_seed"],
                "prompt_seed": record["prompt_seed"],
            }
        else:
            count = body.get("count", 4)
            if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 100:
                raise WorkflowError("count 必须是 1-100 之间的整数")
            settings["count"] = count
            seeds = None
            if mode == "prompt_variant":
                if "sections" in body:
                    raise WorkflowError("prompt_variant 不接受 sections")
                if not context["positive"]:
                    raise WorkflowError("历史记录缺少可回放的最终正向提示词")
                regeneration = {
                    "mode": mode,
                    "frozen_positive_prompt": context["positive"],
                    "frozen_negative_prompt": context["negative"],
                    "fixed_selection": context["selected"],
                    "prompt_seed": record["prompt_seed"],
                }
            elif mode == "settings_reroll":
                if "sections" in body:
                    raise WorkflowError("settings_reroll 不接受 sections")
                regeneration = {"mode": mode}
            else:
                sections = body.get("sections")
                if not isinstance(sections, list) or not sections:
                    raise WorkflowError("content_redraw 至少选择一个重抽维度")
                if any(not isinstance(section, str) for section in sections):
                    raise WorkflowError("sections 必须是字符串数组")
                if len(sections) != len(set(sections)):
                    raise WorkflowError("重抽维度不能重复")
                invalid = set(sections) - set(SECTIONS)
                if invalid:
                    raise WorkflowError(f"不支持的重抽维度: {', '.join(sorted(invalid))}")
                not_random = [
                    section for section in sections if not context["sections"][section]["random"]
                ]
                if not_random:
                    raise WorkflowError(
                        f"这些维度在历史设置中不是随机池: {', '.join(not_random)}"
                    )
                missing_fixed = [
                    section
                    for section, value in context["sections"].items()
                    if value["random"] and section not in sections and not value["hasSnapshot"]
                ]
                if missing_fixed:
                    raise WorkflowError(
                        "缺少历史实际抽取结果，请同时重抽: " + ", ".join(missing_fixed)
                    )
                fixed_selection = {
                    section: context["selected"].get(section, [])
                    for section, value in context["sections"].items()
                    if value["random"] and section not in sections
                }
                regeneration = {
                    "mode": mode,
                    "redraw_sections": sections,
                    "fixed_selection": fixed_selection,
                    "original_selection": context["selected"],
                }
        state = await manager.start(settings, seeds=seeds, regeneration=regeneration)
        return web.json_response(state, status=201)

    async def delete_history(request: web.Request) -> web.Response:
        image_id = int(request.match_info["image_id"])
        # 先取元数据:记录不存在时由 get_image 抛 KeyError,统一映射为 404。
        record = await history.get_image(image_id)
        target_file = _resolve_image_disk_path(app[OUTPUT_DIR_KEY], record)
        file_deleted = False
        if target_file is not None and target_file.is_file():
            try:
                await asyncio.to_thread(target_file.unlink)
                file_deleted = True
            except FileNotFoundError:
                # 幽灵记录:文件已被用户手动移走,继续清理数据库记录。
                logger.info("物理图片文件已不存在,仅清理记录(%s)", target_file)
            except OSError as error:
                # 文件被占用等场景:不提交数据库删除,保证状态一致。
                logger.warning("删除本地物理图片文件失败(%s): %s", target_file, error)
                return web.json_response(
                    {"error": f"无法删除本地物理文件: {error}"}, status=500
                )
        if not await history.delete_image(image_id):
            raise KeyError(image_id)
        return web.json_response({"deleted": True, "file_deleted": file_deleted})

    def _batch_image_ids(body: dict[str, Any]) -> list[int]:
        """校验并归一化批量接口的 image_ids 字段(去重、保持提交顺序)。"""
        raw = body.get("image_ids")
        if not isinstance(raw, list):
            raise WorkflowError("image_ids 必须是整数数组")
        result: list[int] = []
        for value in raw:
            if isinstance(value, bool):
                raise WorkflowError("image_ids 必须是整数数组")
            try:
                number = int(value)
            except (TypeError, ValueError) as error:
                raise WorkflowError("image_ids 必须是整数数组") from error
            if number <= 0:
                raise WorkflowError("image_ids 必须是正整数")
            if number not in result:
                result.append(number)
        return result

    async def batch_delete_history(request: web.Request) -> web.Response:
        """批量删除作品:先物理删文件,再单事务删记录。

        文件被占用等 OSError 视为致命错误:整批不提交数据库删除,
        返回 500 并列出失败项,保证磁盘与数据库状态一致。
        文件已不存在(幽灵记录)则跳过,继续清理记录。
        """
        body = await _json_body(request)
        image_ids = _batch_image_ids(body)
        if not image_ids:
            raise WorkflowError("image_ids 不能为空")
        output_dir = app[OUTPUT_DIR_KEY]
        records: list[dict[str, Any]] = []
        for image_id in image_ids:
            try:
                records.append(await history.get_image(image_id))
            except KeyError:
                # 记录已不存在:幂等跳过,不阻断整批。
                continue
        deleted_files = 0
        missing_files = 0
        failures: list[dict[str, Any]] = []
        for record in records:
            target = _resolve_image_disk_path(output_dir, record)
            if target is None or not target.is_file():
                missing_files += 1
                continue
            try:
                await asyncio.to_thread(target.unlink)
                deleted_files += 1
            except FileNotFoundError:
                missing_files += 1
            except OSError as error:
                logger.warning("批量删除本地物理图片文件失败(%s): %s", target, error)
                failures.append({"id": record["id"], "error": str(error)})
        if failures:
            return web.json_response(
                {
                    "error": f"有 {len(failures)} 个文件无法删除,已取消整批删除",
                    "failures": failures,
                },
                status=500,
            )
        deleted_records = await history.delete_images_batch(
            [int(record["id"]) for record in records]
        )
        return web.json_response(
            {
                "deleted": deleted_records,
                "file_deleted": deleted_files,
                "file_missing": missing_files,
                "requested": len(image_ids),
            }
        )

    def _cleanup_keep_count(body: dict[str, Any]) -> int:
        """校验 keep_hundreds(1~1000)并换算为保留张数 K = keep_hundreds * 100。"""
        raw = body.get("keep_hundreds")
        if isinstance(raw, bool):
            raise WorkflowError("keep_hundreds 必须是 1 到 1000 之间的整数")
        try:
            hundreds = int(raw)
        except (TypeError, ValueError) as error:
            raise WorkflowError("keep_hundreds 必须是 1 到 1000 之间的整数") from error
        if hundreds < 1 or hundreds > 1000:
            raise WorkflowError("keep_hundreds 必须是 1 到 1000 之间的整数")
        return hundreds * 100

    async def cleanup_preview(request: web.Request) -> web.Response:
        """清理预检:统计待删除数量并估算可释放的磁盘空间(不产生任何写操作)。"""
        body = await _json_body(request)
        keep_count = _cleanup_keep_count(body)
        stats = await history.preview_cleanup_non_favorites(keep_count)
        output_dir = app[OUTPUT_DIR_KEY]
        candidates = await history.fetch_cleanup_candidates(keep_count)
        estimated_bytes = 0
        for record in candidates:
            target = _resolve_image_disk_path(output_dir, record)
            if target is None:
                continue
            try:
                if target.is_file():
                    estimated_bytes += int(target.stat().st_size)
            except OSError as error:
                # 单个文件元数据读取失败不影响整体预估。
                logger.debug("读取待清理文件大小失败(%s): %s", target, error)
        return web.json_response(
            {
                "total": stats["total"],
                "keep_latest": stats["keep_latest"],
                "protected_favorites": stats["protected_favorites"],
                "to_delete": stats["to_delete"],
                "estimated_bytes": estimated_bytes,
                "estimated_mb": round(estimated_bytes / (1024 * 1024), 1),
            }
        )

    async def cleanup_execute(request: web.Request) -> web.Response:
        """执行清理:先删物理文件,再单事务批量删库记录。

        - 生成任务运行中直接拒绝(409),避免索引漂移与文件句柄冲突;
        - FileNotFoundError 视为幽灵记录,照常清理数据库;
        - OSError(文件被占用)保留该记录不删库,避免磁盘与数据库不一致;
        - 数据库删除按每批 500 个 ID 分块,规避 SQLite 占位符上限。
        """
        body = await _json_body(request)
        keep_count = _cleanup_keep_count(body)
        manager = app[MANAGER_KEY]
        snapshot = manager.snapshot() or {}
        if snapshot.get("status") in ("running", "stopping"):
            raise BatchConflict("当前正在生成图片，请等待批次完成后再执行清理")
        output_dir = app[OUTPUT_DIR_KEY]
        candidates = await history.fetch_cleanup_candidates(keep_count)
        cleanup_ids: list[int] = []
        file_deleted = 0
        file_missing = 0
        file_failed = 0
        for record in candidates:
            target = _resolve_image_disk_path(output_dir, record)
            if target is None:
                # 路径非法或未配置输出目录:无法定位物理文件,保留记录不删库。
                file_failed += 1
                continue
            try:
                if not target.is_file():
                    file_missing += 1
                else:
                    await asyncio.to_thread(target.unlink)
                    file_deleted += 1
            except FileNotFoundError:
                file_missing += 1
            except OSError as error:
                logger.warning("清理本地物理图片文件失败(%s): %s", target, error)
                file_failed += 1
                continue
            cleanup_ids.append(int(record["id"]))
        deleted_records = 0
        for start in range(0, len(cleanup_ids), 500):
            chunk = cleanup_ids[start : start + 500]
            deleted_records += await history.delete_images_batch(chunk)
        return web.json_response(
            {
                "deleted": deleted_records,
                "file_deleted": file_deleted,
                "file_missing": file_missing,
                "file_failed": file_failed,
                "keep_latest": keep_count,
            }
        )

    async def batch_export_history(request: web.Request) -> web.Response:
        """批量导出作品到已配置的导出文件夹,同名文件自动递增重命名防覆盖。"""
        body = await _json_body(request)
        image_ids = _batch_image_ids(body)
        if not image_ids:
            raise WorkflowError("image_ids 不能为空")
        settings = load_app_settings(storage)
        export_dir = str(settings.get("export_dir") or "").strip()
        if not export_dir:
            raise WorkflowError("尚未配置导出文件夹，请先设置")
        target_dir = Path(export_dir)
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise WorkflowError(f"无法创建或访问导出文件夹: {error}")

        output_dir = app[OUTPUT_DIR_KEY]
        exported: list[dict[str, Any]] = []
        failures: list[dict[str, Any]] = []
        for image_id in image_ids:
            try:
                record = await history.get_image(image_id)
            except KeyError:
                failures.append({"id": image_id, "error": "记录不存在"})
                continue
            source = _resolve_image_disk_path(output_dir, record)
            if source is None or not source.is_file():
                failures.append({"id": image_id, "error": "源图片在磁盘中不存在"})
                continue
            # 防重名自增:绝不覆盖目标目录中的历史文件。
            dest = target_dir / source.name
            counter = 1
            while dest.exists():
                dest = target_dir / f"{source.stem}_{counter}{source.suffix}"
                counter += 1
            try:
                await asyncio.to_thread(shutil.copy2, source, dest)
            except OSError as error:
                logger.warning("批量导出图片失败(%s): %s", source, error)
                failures.append({"id": image_id, "error": str(error)})
                continue
            exported.append({"id": image_id, "filename": dest.name, "dest_path": str(dest)})
        return web.json_response(
            {
                "success": not failures,
                "exported": exported,
                "exported_count": len(exported),
                "failed_count": len(failures),
                "failures": failures,
                "folder_name": target_dir.name or str(target_dir),
            }
        )

    async def batch_update_collections(request: web.Request) -> web.Response:
        """批量调整收藏夹归属,支持 add / remove / set 三种模式。"""
        body = await _json_body(request)
        image_ids = _batch_image_ids(body)
        if not image_ids:
            raise WorkflowError("image_ids 不能为空")
        mode = body.get("mode")
        if not isinstance(mode, str) or mode not in {"add", "remove", "set"}:
            raise CollectionError("mode 必须是 add、remove 或 set")
        collection_ids = body.get("collection_ids")
        if not isinstance(collection_ids, list):
            raise CollectionError("collection_ids 必须是整数数组")
        updated = await history.batch_update_image_collections(
            image_ids, collection_ids, mode
        )
        return web.json_response(
            {"mode": mode, "updated": updated, "updated_count": len(updated)}
        )

    async def image(request: web.Request) -> web.Response:
        record = await history.get_image(int(request.match_info["image_id"]))
        body, content_type = await client.image_bytes(record)
        return web.Response(body=body, content_type=content_type.split(";", 1)[0])

    async def open_folder(request: web.Request) -> web.Response:
        record = await history.get_image(int(request.match_info["image_id"]))
        output_dir = app[OUTPUT_DIR_KEY]
        if output_dir is None:
            return web.json_response(
                {"error": "未配置或未找到 ComfyUI 输出目录"}, status=400
            )
        # 复用统一的安全路径解析:拒绝绝对路径、盘符、.. 与越界解析结果。
        target = _resolve_image_disk_path(output_dir, record)
        if target is None:
            return web.json_response({"error": "图片路径无效"}, status=400)
        if not target.is_file():
            return web.json_response({"error": "文件在本地磁盘中不存在"}, status=404)
        try:
            await asyncio.to_thread(_reveal_in_file_manager, target)
        except OSError as error:
            logger.warning("打开文件位置失败(%s): %s", target, error)
            return web.json_response({"error": "无法打开文件资源管理器"}, status=500)
        return web.json_response({"opened": True})

    async def get_export_folder(_: web.Request) -> web.Response:
        settings = load_app_settings(storage)
        export_dir = str(settings.get("export_dir") or "").strip()
        exists = bool(export_dir and Path(export_dir).is_dir())
        return web.json_response({"export_dir": export_dir, "exists": exists})

    async def update_export_folder(request: web.Request) -> web.Response:
        body = await _json_body(request)
        raw_path = str(body.get("export_dir") or "").strip()
        settings = load_app_settings(storage)
        if raw_path:
            norm_path = os.path.normpath(raw_path)
            target = Path(norm_path)
            try:
                target.mkdir(parents=True, exist_ok=True)
            except OSError as error:
                raise WorkflowError(f"无法创建或访问指定文件夹: {error}")
            settings["export_dir"] = norm_path
            save_app_settings(storage, settings)
            return web.json_response({"export_dir": norm_path, "exists": True})
        settings.pop("export_dir", None)
        save_app_settings(storage, settings)
        return web.json_response({"export_dir": "", "exists": False})

    async def pick_export_folder(_: web.Request) -> web.Response:
        picked = await asyncio.to_thread(_system_pick_folder)
        return web.json_response({"path": picked})

    async def open_export_folder(_: web.Request) -> web.Response:
        settings = load_app_settings(storage)
        export_dir = str(settings.get("export_dir") or "").strip()
        if not export_dir or not Path(export_dir).is_dir():
            raise WorkflowError("导出文件夹尚未设置或在磁盘中不存在")
        await asyncio.to_thread(_open_directory, Path(export_dir))
        return web.json_response({"opened": True})

    async def copy_image_to_export(request: web.Request) -> web.Response:
        image_id = int(request.match_info["image_id"])
        record = await history.get_image(image_id)
        source = _resolve_image_disk_path(app[OUTPUT_DIR_KEY], record)
        if source is None or not source.is_file():
            raise web.HTTPNotFound(text="源图片在磁盘中不存在")

        settings = load_app_settings(storage)
        export_dir = str(settings.get("export_dir") or "").strip()
        if not export_dir:
            raise WorkflowError("尚未配置导出文件夹，请先设置")

        target_dir = Path(export_dir)
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise WorkflowError(f"无法创建或访问导出文件夹: {error}")

        # 防重名自增:绝不覆盖目标目录中的历史文件。
        dest = target_dir / source.name
        counter = 1
        while dest.exists():
            dest = target_dir / f"{source.stem}_{counter}{source.suffix}"
            counter += 1

        try:
            await asyncio.to_thread(shutil.copy2, source, dest)
        except OSError as error:
            raise WorkflowError(f"复制图片失败: {error}")
        return web.json_response(
            {
                "success": True,
                "filename": dest.name,
                "folder_name": target_dir.name or str(target_dir),
                "dest_path": str(dest),
            }
        )

    async def index(_: web.Request) -> web.FileResponse:
        return web.FileResponse(root / "static" / "index.html")

    async def favicon(_: web.Request) -> web.Response:
        return web.Response(status=204)

    async def launcher_health(_: web.Request) -> web.Response:
        return web.json_response({
            "app": "anima-random-studio",
            "app_dir": str(root.resolve()),
            "data_dir": str(storage.resolve()),
            "comfy_url": getattr(client, "base_url", "local"),
        })

    async def launcher_shutdown(request: web.Request) -> web.Response:
        # 未配置 token 时端点不存在,旧版本天然返回 404 —— 启动器据此探测能力。
        if shutdown_token is None:
            raise web.HTTPNotFound()
        try:
            body = await request.json()
        except Exception:
            body = None
        candidate = body.get("token") if isinstance(body, dict) else None
        if not isinstance(candidate, str) or not hmac.compare_digest(candidate, shutdown_token):
            raise web.HTTPForbidden()
        # 先让响应发出,再整体退出;升级路径只在空闲时调用,可跳过 on_cleanup。
        asyncio.get_running_loop().call_later(0.5, os._exit, 0)
        return web.json_response({"stopping": True})

    app.router.add_get("/api/launcher-health", launcher_health)
    app.router.add_post("/api/launcher-shutdown", launcher_shutdown)
    app.router.add_get("/api/config", config)
    app.router.add_get("/api/status", status)
    app.router.add_get("/api/loras", loras)
    app.router.add_get("/api/loras/preview", lora_preview)
    app.router.add_put("/api/loras/triggers", update_lora_triggers)
    app.router.add_delete("/api/loras/triggers", reset_lora_triggers)
    app.router.add_get("/api/resources", resources)
    app.router.add_get("/api/style-presets", list_style_presets)
    app.router.add_post("/api/style-presets", create_style_preset)
    # 收藏夹静态段必须先于 /api/style-presets/{preset_id} 动态段注册,
    # 否则 "collections" 会被当作 preset_id 吞掉。
    app.router.add_get("/api/style-presets/collections", list_style_preset_collections)
    app.router.add_post("/api/style-presets/collections", create_style_preset_collection)
    app.router.add_delete(
        r"/api/style-presets/collections/{collection_id:\d+}",
        delete_style_preset_collection,
    )
    app.router.add_patch(
        r"/api/style-presets/collections/{collection_id:\d+}",
        update_style_preset_collection,
    )
    app.router.add_put(
        r"/api/style-presets/collections/{collection_id:\d+}",
        update_style_preset_collection,
    )
    # 批量静态段同样必须先于 /api/style-presets/{preset_id} 动态段注册,
    # 否则 "batch-delete" / "batch-collections" 会被当作 preset_id 吞掉。
    app.router.add_post("/api/style-presets/batch-delete", batch_delete_style_presets)
    app.router.add_post(
        "/api/style-presets/batch-collections", batch_update_preset_collections
    )
    app.router.add_get("/api/style-presets/{preset_id}/thumbnail", style_preset_thumbnail)
    app.router.add_post(
        "/api/style-presets/{preset_id}/toggle-default-favorite",
        toggle_style_preset_default_favorite,
    )
    app.router.add_post(
        "/api/style-presets/{preset_id}/collections", set_style_preset_collections
    )
    app.router.add_put("/api/style-presets/{preset_id}", update_style_preset)
    app.router.add_patch("/api/style-presets/{preset_id}", update_style_preset)
    app.router.add_delete("/api/style-presets/{preset_id}", delete_style_preset)
    app.router.add_get("/api/prompt-rules", list_prompt_rules)
    app.router.add_post("/api/prompt-rules", create_prompt_rule)
    app.router.add_put("/api/prompt-rules/{rule_id}", update_prompt_rule)
    app.router.add_delete("/api/prompt-rules/{rule_id}", delete_prompt_rule)
    app.router.add_post("/api/prompts/normalize", normalize_prompts)
    app.router.add_get("/api/favorites/{section}", get_favorites)
    app.router.add_put("/api/favorites/{section}/item", update_favorite)
    app.router.add_post("/api/favorites/{section}/selection", update_favorite_selection)
    app.router.add_post("/api/favorites/{section}/groups", create_favorite_group)
    app.router.add_put("/api/favorites/{section}/groups/{group_id}", update_favorite_group)
    app.router.add_post(
        "/api/favorites/{section}/groups/{parent_id}/children/import",
        import_favorite_child_group,
    )
    app.router.add_delete("/api/favorites/{section}/groups/{group_id}", delete_favorite_group)
    app.router.add_get("/api/pools/{section}", pool)
    app.router.add_post("/api/pools/{section}/query", pool_query)
    app.router.add_get("/api/blocked-prompts", get_blocked_prompts)
    app.router.add_post(
        r"/api/blocked-prompts/{section}/toggle", toggle_blocked_prompt
    )
    app.router.add_get("/api/custom-prompts", list_custom_prompts)
    app.router.add_post("/api/custom-prompts", create_custom_prompt)
    app.router.add_put("/api/custom-prompts/{item_id}", update_custom_prompt)
    app.router.add_delete("/api/custom-prompts/{item_id}", delete_custom_prompt)
    app.router.add_get("/api/custom-prompts/templates/{section}/{format}", custom_template)
    app.router.add_post("/api/custom-prompts/import/preview", preview_custom_import)
    app.router.add_post("/api/custom-prompts/import", commit_custom_import)
    app.router.add_get("/api/custom-groups/{section}", list_custom_groups)
    app.router.add_post("/api/custom-groups/{section}", create_custom_group)
    app.router.add_put("/api/custom-groups/{section}/{group_id}", update_custom_group)
    app.router.add_delete("/api/custom-groups/{section}/{group_id}", delete_custom_group)
    app.router.add_post("/api/batches", start_batch)
    app.router.add_get("/api/batches/current", current_batch)
    app.router.add_get("/api/batches/current/preview", batch_preview)
    app.router.add_post("/api/batches/{batch_id}/stop", stop_batch)
    app.router.add_delete("/api/batches/queue/{queue_id}", remove_queued_batch)
    app.router.add_get("/api/history", list_history)
    # 批量端点必须先于 /api/history/{image_id} 系列注册,避免被动态段吞掉。
    app.router.add_post("/api/history/batch-delete", batch_delete_history)
    app.router.add_post("/api/history/batch-export", batch_export_history)
    app.router.add_post("/api/history/batch-collections", batch_update_collections)
    # 作品库清理:同样必须先于 /api/history/{image_id} 正则路由注册。
    app.router.add_post("/api/history/cleanup-preview", cleanup_preview)
    app.router.add_post("/api/history/cleanup-execute", cleanup_execute)
    app.router.add_get("/api/gallery/collections", list_gallery_collections)
    app.router.add_post("/api/gallery/collections", create_gallery_collection)
    app.router.add_delete(
        r"/api/gallery/collections/{collection_id:\d+}", delete_gallery_collection
    )
    app.router.add_patch(
        r"/api/gallery/collections/{collection_id:\d+}", update_gallery_collection
    )
    app.router.add_put(
        r"/api/gallery/collections/{collection_id:\d+}", update_gallery_collection
    )
    app.router.add_post(
        r"/api/history/{image_id:\d+}/toggle-default-favorite", toggle_default_favorite
    )
    app.router.add_post(
        r"/api/history/{image_id:\d+}/collections", set_image_collections
    )
    app.router.add_get(
        r"/api/history/{image_id:\d+}/regeneration-options",
        regeneration_options,
    )
    app.router.add_post(
        r"/api/history/{image_id:\d+}/regenerate", regenerate_history
    )
    app.router.add_delete(r"/api/history/{image_id:\d+}", delete_history)
    app.router.add_post(r"/api/history/{image_id:\d+}/open-folder", open_folder)
    app.router.add_get("/api/settings/export-folder", get_export_folder)
    app.router.add_post("/api/settings/export-folder", update_export_folder)
    app.router.add_post("/api/system/pick-folder", pick_export_folder)
    app.router.add_post("/api/settings/open-export-folder", open_export_folder)
    app.router.add_post(
        r"/api/history/{image_id:\d+}/copy-to-export", copy_image_to_export
    )
    app.router.add_get(r"/api/images/{image_id:\d+}", image)
    app.router.add_get("/", index)
    app.router.add_get("/favicon.ico", favicon)
    app.router.add_static("/static/", root / "static", show_index=False)

    async def cleanup(_: web.Application) -> None:
        manager.shutting_down = True
        manager.queue.clear()
        manager._stop_monitor()
        if manager.task and not manager.task.done():
            manager.stop_requested = True
            try:
                await asyncio.wait_for(manager.task, timeout=2)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                manager.task.cancel()
        close = getattr(client, "close", None)
        if close:
            result = close()
            if asyncio.iscoroutine(result):
                await result
        await history.close()

    app.on_cleanup.append(cleanup)
    return app


def _setup_logging(root: Path, data_dir: Path | None = None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    try:
        directory = data_dir if data_dir is not None else root / "data"
        directory.mkdir(parents=True, exist_ok=True)
        from logging.handlers import RotatingFileHandler
        handlers.append(RotatingFileHandler(directory / "webui.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"))
    except OSError:
        pass
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=handlers,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Anima Random WebUI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8190)
    parser.add_argument("--comfy-url", default="http://127.0.0.1:8188")
    parser.add_argument("--anima-tools-dir", default=None)
    parser.add_argument(
        "--output-dir",
        default=None,
        help="ComfyUI 输出目录；缺省时按 COMFYUI_OUTPUT_DIR 与便携包相对路径探测",
    )
    parser.add_argument("--data-dir", default=None, help="用户数据目录；默认仍为项目 data")
    parser.add_argument("--resource-paths", default=None, help="启动器解析的模型相对路径映射 JSON")
    parser.add_argument(
        "--trusted-host",
        action="append",
        default=[],
        help="额外允许的反向代理主机名；可重复指定",
    )
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--shutdown-token", default=None, help="启动器下发的停机令牌;未提供则关闭停机端点")
    args = parser.parse_args()
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("WebUI 只允许监听本机地址")
    _setup_logging(APP_DIR, Path(args.data_dir) if args.data_dir else None)
    app = create_app(
        comfy=ComfyClient(args.comfy_url),
        anima_tools_dir=args.anima_tools_dir,
        trusted_hostnames=set(args.trusted_host),
        data_dir=args.data_dir,
        resource_paths=json.loads(Path(args.resource_paths).read_text(encoding="utf-8")) if args.resource_paths else None,
        shutdown_token=args.shutdown_token,
        output_dir=args.output_dir,
    )
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(f"http://127.0.0.1:{args.port}")).start()
    web.run_app(app, host=args.host, port=args.port, print=lambda message: print(message, flush=True))
