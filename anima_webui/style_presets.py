from __future__ import annotations

import asyncio
import copy
import functools
import json
import logging
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .persistence import backup_corrupt_file
from .prompt_rules import PromptRuleStore
from .workflow import DEFAULT_SETTINGS, WorkflowError, validate_settings


logger = logging.getLogger(__name__)


def _locked(method: Any) -> Any:
    """变更方法整体串行化:内存修改在事件循环线程完成,写盘经 to_thread 让出循环。"""

    @functools.wraps(method)
    async def wrapper(self: "StylePresetStore", *args: Any, **kwargs: Any) -> Any:
        async with self._lock:
            return await method(self, *args, **kwargs)

    return wrapper


PRESET_SETTING_KEYS = (
    # 人物构成与角色细节:与 DEFAULT_SETTINGS 的 female_count/male_count/character_detail 对齐,
    # 否则保存/载入预设时人物构成(几女几男)与角色细节模式会被丢弃或触发未知参数报错。
    "female_count",
    "male_count",
    "character_detail",
    "model_name",
    "loras",
    "lora_managed_triggers",
    "hires",
    "detailers",
    "manual_artist",
    "quality_prompt",
    "extra_prompt",
    "negative_prompt",
    "width",
    "height",
    "steps",
    "cfg",
    "sampler_name",
    "scheduler",
    "cfg_zero_star",
    "second_sampler",
    # 提示词池:开关、抽取数量、固定提示词与随机池勾选条目。
    # 与 DEFAULT_SETTINGS 的 random_*/random_*_count/fixed_*/pools 保持一致,
    # 否则 preset_settings() 的 unknown 校验会拒绝前端提交的池字段。
    "random_character",
    "random_clothing",
    "random_pose",
    "random_background",
    "random_expression",
    "random_character_count",
    "random_clothing_count",
    "random_pose_count",
    "random_background_count",
    "random_expression_count",
    "fixed_character",
    "fixed_clothing",
    "fixed_pose",
    "fixed_background",
    "fixed_expression",
    "pools",
)
MAX_PRESETS = 256
# 内置系统收藏夹:ID 固定为 1,禁止删除或改名,与作品库默认收藏夹语义一致。
DEFAULT_COLLECTION_ID = 1
DEFAULT_COLLECTION_NAME = "默认收藏"
MAX_COLLECTION_NAME = 100


def _default_collections() -> list[dict[str, Any]]:
    """返回内置收藏夹列表的深拷贝,避免调用方误改模块级常量。"""
    return [{"id": DEFAULT_COLLECTION_ID, "name": DEFAULT_COLLECTION_NAME, "is_default": True}]


def _normalize_collections(value: Any) -> list[dict[str, Any]]:
    """归一化根级 collections:保证默认收藏夹存在、ID 为正整数且唯一、名称非空。"""
    raw_values = value if isinstance(value, list) else []
    collections: list[dict[str, Any]] = []
    seen_ids: set[int] = set()
    for raw in raw_values:
        if not isinstance(raw, dict):
            continue
        try:
            collection_id = int(raw.get("id"))
        except (TypeError, ValueError):
            continue
        if collection_id <= 0 or collection_id in seen_ids:
            continue
        name = str(raw.get("name") or "").strip()
        if not name:
            continue
        seen_ids.add(collection_id)
        collections.append(
            {
                "id": collection_id,
                "name": name[:MAX_COLLECTION_NAME],
                "is_default": collection_id == DEFAULT_COLLECTION_ID,
            }
        )
    default = next(
        (item for item in collections if item["id"] == DEFAULT_COLLECTION_ID), None
    )
    if default is None:
        collections.insert(0, _default_collections()[0])
    else:
        # 默认收藏夹的名称与标记由系统固定,历史数据中的偏差在此纠正。
        default["name"] = DEFAULT_COLLECTION_NAME
        default["is_default"] = True
    # 默认收藏夹始终排在最前,其余保持原有顺序。
    collections.sort(key=lambda item: (item["id"] != DEFAULT_COLLECTION_ID, item["id"]))
    return collections


def preset_settings(
    value: Any, prompt_rules: PromptRuleStore | None = None
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise WorkflowError("风格预设 settings 必须是对象")
    # 前端可能直接提交完整工作台 state(含运行期批次字段 count),
    # 该校验前安全剔除,避免因 "count" 触发未知参数异常。
    cleaned_value = {key: item for key, item in value.items() if key != "count"}
    unknown = set(cleaned_value) - set(PRESET_SETTING_KEYS)
    if unknown:
        raise WorkflowError(f"风格预设包含未知参数: {', '.join(sorted(unknown))}")
    candidate = copy.deepcopy(DEFAULT_SETTINGS)
    candidate.update(cleaned_value)
    if prompt_rules is not None:
        candidate, _ = prompt_rules.normalize_settings(candidate)
    normalized = validate_settings(candidate)
    return {key: copy.deepcopy(normalized[key]) for key in PRESET_SETTING_KEYS}


class StylePresetStore:
    def __init__(self, path: str | Path, prompt_rules: PromptRuleStore | None = None):
        self.path = Path(path)
        self.prompt_rules = prompt_rules
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # 缩略图与预设 JSON 同目录下的 preset_thumbnails/,以预设 ID 命名。
        self.thumbnail_dir = self.path.parent / "preset_thumbnails"
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)
        self.items: list[dict[str, Any]] = []
        self.collections: list[dict[str, Any]] = _default_collections()
        self.load_warnings: list[str] = []
        self._lock = asyncio.Lock()
        self.reload()

    def reload(self) -> None:
        self.load_warnings = []
        if not self.path.is_file():
            self.items = []
            self.collections = _default_collections()
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            values = payload.get("items", []) if isinstance(payload, dict) else []
            raw_collections = payload.get("collections") if isinstance(payload, dict) else None
            # 先归一化收藏夹,再归一化预设:预设的 collection_ids 需要按合法分类裁剪。
            collections = _normalize_collections(raw_collections)
            self.collections = collections
            items = [self._normalize(item, existing=True) for item in values if isinstance(item, dict)]
        except (OSError, json.JSONDecodeError, WorkflowError) as error:
            # 坏文件不再阻断启动:改名备份后以空数据继续,并向界面报告警告。
            backup = backup_corrupt_file(self.path)
            logger.warning("风格预设文件无法读取(%s),已备份为 %s 并以空数据启动", error, backup.name)
            self.load_warnings.append(f"风格预设文件无法读取,已备份为 {backup.name} 并以空数据启动")
            self.items = []
            self.collections = _default_collections()
            return
        self.items = items

    def list(self, collection_id: int | None = None) -> dict[str, Any]:
        """返回预设列表,统一按 updated_at 倒序。

        加星仅作为分类标识,不再影响排序;传入 collection_id 时只返回
        归属该收藏夹的预设,count 仍为全库总数。
        """
        items = self.items
        if collection_id is not None and collection_id > 0:
            items = [item for item in items if collection_id in item["collection_ids"]]
        ordered = sorted(items, key=lambda item: item["updated_at"], reverse=True)
        return {"items": copy.deepcopy(ordered), "count": len(self.items)}

    @_locked
    async def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        if len(self.items) >= MAX_PRESETS:
            raise WorkflowError(f"风格预设不能超过 {MAX_PRESETS} 个")
        self._ensure_unique_name(payload.get("name"))
        now = self._now()
        item = self._normalize(
            {
                **payload,
                "id": f"preset_{uuid.uuid4().hex[:16]}",
                "created_at": now,
                "updated_at": now,
            }
        )
        self.items.append(item)
        await self._save()
        return copy.deepcopy(item)

    @_locked
    async def update(self, preset_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        index = next((index for index, item in enumerate(self.items) if item["id"] == preset_id), None)
        if index is None:
            raise KeyError(preset_id)
        if "name" in payload:
            self._ensure_unique_name(payload.get("name"), excluding_id=preset_id)
        current = self.items[index]
        merged = {
            **current,
            **payload,
            "id": preset_id,
            "created_at": current["created_at"],
            "updated_at": self._now(),
        }
        # 载荷显式给出 favorite 而未给出 collection_ids 时,以 favorite 为准,
        # 避免继承自旧记录的 collection_ids 覆盖调用方意图。
        if "favorite" in payload and "collection_ids" not in payload:
            merged.pop("collection_ids", None)
        item = self._normalize(merged)
        self.items[index] = item
        await self._save()
        return copy.deepcopy(item)

    @_locked
    async def delete(self, preset_id: str) -> bool:
        previous = len(self.items)
        self.items = [item for item in self.items if item["id"] != preset_id]
        if len(self.items) == previous:
            return False
        # 内存与 JSON 记录删除的同时,物理删除对应缩略图,避免孤儿文件堆积。
        thumb_path = self.thumbnail_dir / f"{preset_id}.png"
        if thumb_path.is_file():
            thumb_path.unlink(missing_ok=True)
        await self._save()
        return True

    @_locked
    async def delete_batch(self, preset_ids: list[str]) -> int:
        """批量删除预设,并同步清理磁盘上的缩略图文件。

        单次写盘完成全部删除,避免逐条 _save 造成的多次 fsync;
        不存在的 ID 静默跳过,保证接口幂等。
        """
        target_ids = {str(value) for value in preset_ids if str(value or "").strip()}
        if not target_ids:
            return 0
        to_delete = [item for item in self.items if item["id"] in target_ids]
        if not to_delete:
            return 0
        # 内存列表过滤
        self.items = [item for item in self.items if item["id"] not in target_ids]
        # 同步物理删除对应的缩略图文件,避免孤儿文件残留
        for item in to_delete:
            thumb = self.thumbnail_dir / f"{item['id']}.png"
            if thumb.is_file():
                thumb.unlink(missing_ok=True)
        await self._save()
        return len(to_delete)

    @_locked
    async def save_thumbnail(self, preset_id: str, image_bytes: bytes) -> Path:
        """把二进制图片写入缩略图目录,以预设 ID 命名。

        写盘经 to_thread 让出事件循环;先写临时文件再原子替换,
        避免半截文件被静态路由读到。写入后同步刷新内存记录的
        thumbnail_url,使 list() 立即反映最新封面。
        """
        target = self.thumbnail_dir / f"{preset_id}.png"
        await asyncio.to_thread(self._write_thumbnail, target, image_bytes)
        for item in self.items:
            if item["id"] == preset_id:
                item["thumbnail_url"] = self.thumbnail_url(preset_id)
                break
        return target

    @staticmethod
    def _write_thumbnail(target: Path, image_bytes: bytes) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(
            prefix="preset-thumb-", suffix=".png", dir=target.parent
        )
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(image_bytes)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, target)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _ensure_unique_name(self, value: Any, excluding_id: str | None = None) -> None:
        name = str(value or "").strip().casefold()
        if name and any(
            item["id"] != excluding_id and item["name"].strip().casefold() == name
            for item in self.items
        ):
            raise WorkflowError("已有同名风格预设")

    def _normalize(self, payload: dict[str, Any], existing: bool = False) -> dict[str, Any]:
        preset_id = str(payload.get("id") or "").strip()
        name = str(payload.get("name") or "").strip()
        favorite = payload.get("favorite", False)
        if not preset_id or not name or len(name) > 100:
            raise WorkflowError("风格预设名称需要 1-100 个字符")
        if not isinstance(favorite, bool):
            raise WorkflowError("风格预设 favorite 必须是布尔值")
        created_at = str(payload.get("created_at") or "")
        updated_at = str(payload.get("updated_at") or created_at)
        if existing and not created_at:
            created_at = updated_at = StylePresetStore._now()
        collection_ids = self._normalize_collection_ids(payload, favorite)
        # 双向同步:collection_ids 含默认收藏夹即视为加星,反之亦然。
        favorite = DEFAULT_COLLECTION_ID in collection_ids
        return {
            "id": preset_id,
            "name": name,
            "favorite": favorite,
            "collection_ids": collection_ids,
            "settings": preset_settings(payload.get("settings"), self.prompt_rules),
            "thumbnail_url": self.thumbnail_url(preset_id),
            "created_at": created_at,
            "updated_at": updated_at,
        }

    def _normalize_collection_ids(self, payload: dict[str, Any], favorite: bool) -> list[int]:
        """归一化预设的 collection_ids,并兼容仅有 favorite 的历史数据。

        - 历史数据只有 favorite=True 而无 collection_ids 时,自动补 [1];
        - 传入的 ID 必须存在于当前收藏夹,非法值静默丢弃;
        - 结果去重并升序,保证持久化稳定。
        """
        valid_ids = {collection["id"] for collection in self.collections}
        raw_ids = payload.get("collection_ids")
        if isinstance(raw_ids, list):
            collection_ids: list[int] = []
            for raw in raw_ids:
                if isinstance(raw, bool):
                    continue
                try:
                    collection_id = int(raw)
                except (TypeError, ValueError):
                    continue
                if collection_id in valid_ids and collection_id not in collection_ids:
                    collection_ids.append(collection_id)
        else:
            # 无 collection_ids 字段:由 favorite 推导,保证老数据平滑迁移。
            collection_ids = [DEFAULT_COLLECTION_ID] if favorite else []
        if favorite and DEFAULT_COLLECTION_ID not in collection_ids:
            collection_ids.append(DEFAULT_COLLECTION_ID)
        return sorted(collection_ids)

    def thumbnail_url(self, preset_id: str) -> str | None:
        """本地缩略图存在时返回静态资源 URL,否则返回 None。

        该字段由物理文件推导而非持久化,避免 JSON 与磁盘状态不一致。
        """
        if (self.thumbnail_dir / f"{preset_id}.png").is_file():
            return f"/api/style-presets/{preset_id}/thumbnail"
        return None

    def thumbnail_path(self, preset_id: str) -> Path:
        """返回预设缩略图的物理路径(不保证存在)。"""
        return self.thumbnail_dir / f"{preset_id}.png"

    # ---------- 收藏夹(分类)管理 ----------
    def list_collections(self) -> dict[str, Any]:
        """返回全库总数与各收藏夹的预设数量统计。"""
        collections = [
            {
                **collection,
                "count": sum(
                    collection["id"] in item["collection_ids"] for item in self.items
                ),
            }
            for collection in self.collections
        ]
        return {"all_total": len(self.items), "collections": copy.deepcopy(collections)}

    @_locked
    async def create_collection(self, name: str) -> dict[str, Any]:
        cleaned = str(name or "").strip()
        if not cleaned:
            raise WorkflowError("收藏夹名称不能为空")
        if len(cleaned) > MAX_COLLECTION_NAME:
            raise WorkflowError(f"收藏夹名称不能超过 {MAX_COLLECTION_NAME} 个字符")
        if any(
            collection["name"].strip().casefold() == cleaned.casefold()
            for collection in self.collections
        ):
            raise WorkflowError(f"收藏夹已存在: {cleaned}")
        # 自增分配:取现有最大 ID + 1,保证唯一正整数且不复用已删除的 ID。
        next_id = max((collection["id"] for collection in self.collections), default=0) + 1
        collection = {"id": next_id, "name": cleaned, "is_default": False}
        self.collections.append(collection)
        await self._save()
        return copy.deepcopy(collection)

    @_locked
    async def delete_collection(self, collection_id: int) -> bool:
        """删除自定义收藏夹,仅从预设中解绑,绝不删除预设本体。"""
        if collection_id == DEFAULT_COLLECTION_ID:
            raise WorkflowError("默认收藏夹不能删除")
        previous = len(self.collections)
        self.collections = [
            collection for collection in self.collections if collection["id"] != collection_id
        ]
        if len(self.collections) == previous:
            return False
        for item in self.items:
            if collection_id in item["collection_ids"]:
                item["collection_ids"] = [
                    value for value in item["collection_ids"] if value != collection_id
                ]
                item["favorite"] = DEFAULT_COLLECTION_ID in item["collection_ids"]
        await self._save()
        return True

    @_locked
    async def toggle_default_favorite(self, preset_id: str) -> dict[str, Any]:
        item = next((entry for entry in self.items if entry["id"] == preset_id), None)
        if item is None:
            raise KeyError(preset_id)
        if DEFAULT_COLLECTION_ID in item["collection_ids"]:
            item["collection_ids"] = [
                value for value in item["collection_ids"] if value != DEFAULT_COLLECTION_ID
            ]
            is_favorite = False
        else:
            item["collection_ids"] = sorted([*item["collection_ids"], DEFAULT_COLLECTION_ID])
            is_favorite = True
        item["favorite"] = is_favorite
        # 星标仅作分类标识,不刷新 updated_at,避免切换收藏改变列表排序。
        await self._save()
        return {
            "id": preset_id,
            "is_favorite": is_favorite,
            "collection_ids": list(item["collection_ids"]),
        }

    @_locked
    async def set_preset_collections(
        self, preset_id: str, collection_ids: list[int]
    ) -> dict[str, Any]:
        item = next((entry for entry in self.items if entry["id"] == preset_id), None)
        if item is None:
            raise KeyError(preset_id)
        if not isinstance(collection_ids, list):
            raise WorkflowError("collection_ids 必须是数组")
        valid_ids = {collection["id"] for collection in self.collections}
        wanted: list[int] = []
        for raw in collection_ids:
            if isinstance(raw, bool):
                raise WorkflowError("collection_ids 必须是整数数组")
            try:
                collection_id = int(raw)
            except (TypeError, ValueError):
                raise WorkflowError("collection_ids 必须是整数数组")
            if collection_id not in valid_ids:
                raise WorkflowError(f"收藏夹不存在: {collection_id}")
            if collection_id not in wanted:
                wanted.append(collection_id)
        item["collection_ids"] = sorted(wanted)
        item["favorite"] = DEFAULT_COLLECTION_ID in item["collection_ids"]
        item["updated_at"] = self._now()
        await self._save()
        return copy.deepcopy(item)

    @_locked
    async def batch_update_collections(
        self, preset_ids: list[str], collection_ids: list[int], mode: str
    ) -> list[str]:
        """批量调整预设所属分类,支持 add / remove / set 模式。

        - add:在原有归属上追加;
        - remove:从原有归属中移除;
        - set:整体覆盖为给定归属。
        星标(favorite)始终由是否包含默认收藏夹推导,保证双向同步。
        非法/不存在的分类 ID 静默丢弃,避免整批失败。
        """
        if mode not in {"add", "remove", "set"}:
            raise WorkflowError("mode 必须是 add、remove 或 set")
        valid_ids = {collection["id"] for collection in self.collections}
        wanted: list[int] = []
        for raw in collection_ids:
            if isinstance(raw, bool):
                continue
            try:
                collection_id = int(raw)
            except (TypeError, ValueError):
                continue
            if collection_id in valid_ids and collection_id not in wanted:
                wanted.append(collection_id)

        target_ids = {str(value) for value in preset_ids if str(value or "").strip()}
        updated: list[str] = []
        now = self._now()

        for item in self.items:
            if item["id"] not in target_ids:
                continue
            current_ids = set(item.get("collection_ids") or [])
            if mode == "add":
                new_ids = current_ids | set(wanted)
            elif mode == "remove":
                new_ids = current_ids - set(wanted)
            else:  # set 模式
                new_ids = set(wanted)

            item["collection_ids"] = sorted(new_ids)
            item["favorite"] = DEFAULT_COLLECTION_ID in new_ids
            item["updated_at"] = now
            updated.append(item["id"])

        if updated:
            await self._save()
        return updated

    async def _save(self) -> None:
        # 快照序列化在事件循环线程完成(状态一致),fsync 等慢速 I/O 移入工作线程。
        payload = json.dumps(
            {"version": 1, "collections": self.collections, "items": self.items},
            ensure_ascii=False,
            indent=2,
        ) + "\n"
        await asyncio.to_thread(self._write_text, payload)

    def _write_text(self, text: str) -> None:
        fd, temp_name = tempfile.mkstemp(prefix="style-presets-", suffix=".json", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
