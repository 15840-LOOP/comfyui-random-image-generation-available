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
        self.load_warnings: list[str] = []
        self._lock = asyncio.Lock()
        self.reload()

    def reload(self) -> None:
        self.load_warnings = []
        if not self.path.is_file():
            self.items = []
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            values = payload.get("items", []) if isinstance(payload, dict) else []
            items = [self._normalize(item, existing=True) for item in values if isinstance(item, dict)]
        except (OSError, json.JSONDecodeError, WorkflowError) as error:
            # 坏文件不再阻断启动:改名备份后以空数据继续,并向界面报告警告。
            backup = backup_corrupt_file(self.path)
            logger.warning("风格预设文件无法读取(%s),已备份为 %s 并以空数据启动", error, backup.name)
            self.load_warnings.append(f"风格预设文件无法读取,已备份为 {backup.name} 并以空数据启动")
            self.items = []
            return
        self.items = items

    def list(self) -> dict[str, Any]:
        favorites = sorted(
            (item for item in self.items if item["favorite"]),
            key=lambda item: item["updated_at"],
            reverse=True,
        )
        regular = sorted(
            (item for item in self.items if not item["favorite"]),
            key=lambda item: item["updated_at"],
            reverse=True,
        )
        return {"items": copy.deepcopy(favorites + regular), "count": len(self.items)}

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
        item = self._normalize(
            {
                **current,
                **payload,
                "id": preset_id,
                "created_at": current["created_at"],
                "updated_at": self._now(),
            }
        )
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
        return {
            "id": preset_id,
            "name": name,
            "favorite": favorite,
            "settings": preset_settings(payload.get("settings"), self.prompt_rules),
            "thumbnail_url": self.thumbnail_url(preset_id),
            "created_at": created_at,
            "updated_at": updated_at,
        }

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

    async def _save(self) -> None:
        # 快照序列化在事件循环线程完成(状态一致),fsync 等慢速 I/O 移入工作线程。
        payload = json.dumps({"version": 1, "items": self.items}, ensure_ascii=False, indent=2) + "\n"
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
