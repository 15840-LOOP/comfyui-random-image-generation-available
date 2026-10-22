"""预设屏蔽池(隔离池)持久化存储。

被屏蔽的预设从正常卡池中物理隔离:检索阶段即被排除,只能通过
``blocked_only`` 视图查看。数据文件默认位于 ``data/blocked_prompts.json``,
启动时若目录或文件缺失会自动创建,写入采用临时文件原子替换。
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

from .catalog import SECTIONS

logger = logging.getLogger(__name__)


def default_blocked_dict() -> dict[str, list[str]]:
    """返回包含 5 大卡池键的空屏蔽结构。"""
    return {section: [] for section in SECTIONS}


class BlockedPromptStore:
    """持久化管理预设屏蔽词库 (data/blocked_prompts.json)。"""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.load_warnings: list[str] = []
        self._blocked: dict[str, set[str]] = {section: set() for section in SECTIONS}
        self._lock = asyncio.Lock()
        # 启动时确保文件和目录就绪(若无则自动创建)。
        self.ensure_initialized()

    def ensure_initialized(self) -> None:
        """若 data 目录或 json 文件不存在,自动创建并写入默认空结构。"""
        self.load_warnings.clear()
        self._blocked = {section: set() for section in SECTIONS}

        try:
            # 自动创建父级目录(如 data/)。
            self.path.parent.mkdir(parents=True, exist_ok=True)

            if not self.path.is_file():
                # 文件不存在,自动创建包含 5 大卡池键的空结构文件。
                self._atomic_save()
                logger.info("已自动创建并初始化屏蔽词库配置: %s", self.path)
                return

            content = self.path.read_text(encoding="utf-8").strip()
            if not content:
                self._atomic_save()
                return

            data = json.loads(content)
            if isinstance(data, dict):
                for section in SECTIONS:
                    items = data.get(section)
                    if isinstance(items, list):
                        self._blocked[section] = {
                            str(item).strip() for item in items if str(item).strip()
                        }
        except Exception as error:  # noqa: BLE001 - 任何异常都降级为空屏蔽池
            warning = (
                f"屏蔽词库文件读取失败 ({self.path.name}): {error}，已降级为空屏蔽池"
            )
            logger.warning(warning)
            self.load_warnings.append(warning)

    def get_blocked_ids(self, section: str) -> set[str]:
        """返回指定卡池的屏蔽 ID 集合(副本,调用方可安全修改)。"""
        return set(self._blocked.get(section, set()))

    def is_blocked(self, section: str, item_id: str) -> bool:
        return str(item_id).strip() in self._blocked.get(section, set())

    async def toggle(self, section: str, item_id: str) -> bool:
        """切换屏蔽状态,返回操作后的状态 (True=已屏蔽)。"""
        async with self._lock:
            is_blocked = self._apply_toggle(section, item_id)
            await asyncio.to_thread(self._atomic_save)
        return is_blocked

    def _apply_toggle(self, section: str, item_id: str) -> bool:
        """同步切换内存状态(调用方负责加锁与落盘)。"""
        if section not in SECTIONS:
            raise ValueError(f"不支持的卡池: {section}")
        item_id = str(item_id).strip()
        if not item_id:
            raise ValueError("item_id 不能为空")

        blocked_set = self._blocked[section]
        if item_id in blocked_set:
            blocked_set.remove(item_id)
            return False
        blocked_set.add(item_id)
        return True

    def _run_toggle(self, section: str, item_id: str) -> bool:
        """同步切换并立即落盘(供测试与同步上下文使用)。"""
        is_blocked = self._apply_toggle(section, item_id)
        self._atomic_save()
        return is_blocked

    def snapshot(self) -> dict[str, list[str]]:
        """返回可 JSON 序列化的完整快照(各卡池按 ID 排序)。"""
        return {section: sorted(self._blocked[section]) for section in SECTIONS}

    def _atomic_save(self) -> None:
        """原子写入文件,防止写文件中断导致损坏。"""
        data: dict[str, Any] = self.snapshot()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            dir=self.path.parent, prefix="blocked_", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_path, self.path)
        except Exception:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise
