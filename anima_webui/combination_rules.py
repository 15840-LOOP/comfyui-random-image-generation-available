"""组合禁用规则:多个维度同时命中才跳过,用于排除"角色A + 服装B"这类具体搭配。"""

from __future__ import annotations

import asyncio
import copy
import json
import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from .catalog import SECTIONS
from .persistence import backup_corrupt_file
from .workflow import WorkflowError

MAX_COMBINATION_RULES = 500
MIN_PICKS = 2
MAX_ITEM_ID = 300
MAX_LABEL = 200


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class CombinationRuleStore:
    """组合规则持久化。写盘顺序:先落盘,再改内存(失败时状态不分叉)。"""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.rules: list[dict[str, Any]] = []
        self.load_warnings: list[str] = []
        self._lock = asyncio.Lock()
        self.reload()

    def reload(self) -> None:
        self.load_warnings = []
        if not self.path.is_file():
            self.rules = []
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict) or payload.get("version") != 1:
                raise WorkflowError("组合规则文件版本无效")
            raw = payload.get("rules", [])
            if not isinstance(raw, list):
                raise WorkflowError("组合规则文件内容无效")
            if len(raw) > MAX_COMBINATION_RULES:
                raise WorkflowError(f"组合规则不能超过 {MAX_COMBINATION_RULES} 条")
            self.rules = [self._normalize(item, existing=True) for item in raw]
        except (OSError, json.JSONDecodeError, WorkflowError) as error:
            # 坏文件不阻断启动:改名备份后以空规则继续,并向界面报告警告。
            backup = backup_corrupt_file(self.path)
            self.load_warnings.append(
                f"组合规则文件无法读取({error}),已备份为 {backup.name} 并以空规则启动"
            )
            self.rules = []

    def list(self) -> dict[str, Any]:
        return {"items": copy.deepcopy(self.rules), "count": len(self.rules)}

    async def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise WorkflowError("请求内容必须是对象")
        unknown = set(payload) - {"picks"}
        if unknown:
            raise WorkflowError(f"组合规则包含未知参数: {', '.join(sorted(unknown))}")
        async with self._lock:
            candidate = self._normalize(
                {"picks": payload.get("picks"), "id": f"combo_{uuid.uuid4().hex[:16]}"}
            )
            for existing in self.rules:
                if self._same_picks(existing["picks"], candidate["picks"]):
                    return copy.deepcopy(existing)
            if len(self.rules) >= MAX_COMBINATION_RULES:
                raise WorkflowError(f"组合规则不能超过 {MAX_COMBINATION_RULES} 条")
            updated = [*self.rules, candidate]
            await self._save(updated)
            self.rules = updated
        return copy.deepcopy(candidate)

    async def delete(self, rule_id: str) -> bool:
        async with self._lock:
            updated = [item for item in self.rules if item["id"] != rule_id]
            if len(updated) == len(self.rules):
                return False
            await self._save(updated)
            self.rules = updated
        return True

    async def clear(self) -> int:
        async with self._lock:
            previous = len(self.rules)
            await self._save([])
            self.rules = []
        return previous

    def match(self, selection: dict[str, list[dict[str, Any]]]) -> str | None:
        """返回命中的规则 id。规则内所有维度都必须命中本次抽取结果。"""
        # 该函数会在 server.py 的 except WorkflowError 之外被调用,
        # 任何非预期入参都不能变成 500:非法入参一律视为"未命中"。
        if not isinstance(selection, dict):
            return None
        for rule in self.rules:
            picks = rule["picks"]
            if all(
                any(
                    isinstance(item, dict) and item.get("id") == pick["id"]
                    for item in self._section_items(selection.get(section))
                )
                for section, pick in picks.items()
            ):
                return rule["id"]
        return None

    @staticmethod
    def _section_items(value: Any) -> list[Any]:
        """把抽取结果里的某一维度安全地读成列表;非 list 一律当作空。"""
        return value if isinstance(value, list) else []

    @staticmethod
    def _same_picks(left: dict[str, Any], right: dict[str, Any]) -> bool:
        if set(left) != set(right):
            return False
        return all(left[section]["id"] == right[section]["id"] for section in left)

    def _normalize(self, item: Any, existing: bool = False) -> dict[str, Any]:
        if not isinstance(item, dict):
            raise WorkflowError("组合规则条目必须是对象")
        raw_picks = item.get("picks")
        if not isinstance(raw_picks, dict):
            raise WorkflowError("组合规则缺少 picks")
        unknown = set(raw_picks) - set(SECTIONS)
        if unknown:
            raise WorkflowError(f"组合规则包含未知维度: {', '.join(sorted(unknown))}")
        if not MIN_PICKS <= len(raw_picks) <= len(SECTIONS):
            raise WorkflowError(
                f"组合规则需要同时指定 {MIN_PICKS} 到 {len(SECTIONS)} 个维度"
            )
        picks: dict[str, dict[str, str]] = {}
        for section, value in raw_picks.items():
            if not isinstance(value, dict):
                raise WorkflowError(f"组合规则的 {section} 必须是对象")
            item_id = str(value.get("id") or "").strip()
            if not item_id:
                # 固定提示词维度的伪条目 id 为空字符串:它不参与随机抽取,
                # match() 永远不会命中。在这里拦住,避免创建一条永不生效的规则。
                raise WorkflowError(
                    f"固定提示词维度不能用于组合规则: {section} 不是随机抽取维度"
                )
            if len(item_id) > MAX_ITEM_ID:
                raise WorkflowError(f"组合规则的 {section} 条目 id 过长")
            # catalog 条目的 id 恒为 "<section>:..."(见 catalog._simple_key),
            # 自定义词条恒为 "custom:<uuid4().hex>"(见 custom_prompts.py)。
            # 两者都不是的 id 永远不可能命中,match() 会静默失效,所以在入口拦住;
            # 这也自然拒绝了把 clothing:xx 填进 character 这类跨维度错填。
            if not (
                item_id.startswith(f"{section}:") or item_id.startswith("custom:")
            ):
                raise WorkflowError(f"组合规则的 {section} 条目 id 格式无效")
            label = str(value.get("label") or "").strip() or item_id.split(":", 1)[-1]
            if len(label) > MAX_LABEL:
                raise WorkflowError("组合规则标签过长")
            picks[section] = {"id": item_id, "label": label}
        result: dict[str, Any] = {"picks": picks}
        if existing:
            rule_id = str(item.get("id") or "").strip()
            if not rule_id.startswith("combo_"):
                raise WorkflowError("组合规则 id 无效")
            result["id"] = rule_id
            result["created_at"] = str(item.get("created_at") or _now())
        else:
            result["id"] = str(item["id"])
            result["created_at"] = _now()
        # 统一按 SECTIONS 顺序展开 picks,让落盘内容稳定、便于人工比对。
        result["picks"] = {
            section: result["picks"][section]
            for section in SECTIONS
            if section in result["picks"]
        }
        return result

    async def _save(self, rules: list[dict[str, Any]]) -> None:
        payload = json.dumps(
            {"version": 1, "rules": rules}, ensure_ascii=False, indent=2
        ) + "\n"
        await asyncio.to_thread(self._write_text, payload)

    def _write_text(self, text: str) -> None:
        fd, temp_name = tempfile.mkstemp(
            prefix="combination-rules-", suffix=".json", dir=self.path.parent
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
