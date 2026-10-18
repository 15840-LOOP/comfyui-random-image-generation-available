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
MAX_PICK_TEXT = 500


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _normalize_text(value: Any) -> str:
    """固定维度按文本匹配时使用的归一化:折叠空白、去掉首尾空白。

    固定提示词是用户手写的自然语言(如 "alpha, series"),大小写与逗号后的
    空格都可能不一致,因此必须归一化后再比较,否则规则会因一个空格而静默失效。
    """
    return " ".join(str(value or "").split())


def _text_tags(value: Any) -> frozenset[str]:
    """把一段提示词拆成归一化后的 tag 集合。"""
    text = str(value or "").replace("，", ",")
    return frozenset(
        tag for tag in (_normalize_text(part) for part in text.split(",")) if tag
    )


def _item_tags(item: dict[str, Any]) -> frozenset[str]:
    """汇总一个条目所有可读的描述文本,供固定维度按 tag 包含关系匹配。

    固定维度的文本在两条路径上来源不同:普通批次来自 settings 的 fixed_*
    原文(如 "alpha, series"),content_redraw 来自历史快照里的真实 catalog
    条目(触发词在 title/prompt,系列在 subtitle,copyright 另存)。单一字段
    比较必然对不上,因此汇总 title/subtitle/prompt/tags 后再判断包含关系,
    同一份规则才能在两条路径上一致命中。
    """
    parts: set[str] = set()
    for field in ("title", "subtitle", "prompt"):
        parts |= _text_tags(item.get(field))
    tags = item.get("tags")
    if isinstance(tags, list):
        for tag in tags:
            parts |= _text_tags(tag)
    return frozenset(parts)


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
        """返回命中的规则 id。规则内所有维度都必须命中本次抽取结果。

        匹配键有两种:
        - 随机抽取维度:按 catalog 条目 id 全等比对;
        - 固定提示词维度(pick 带 text):按提示词 tag 集合比对,因为固定维度
          不参与随机抽取,拿不到稳定的 catalog id —— 且它在普通批次与
          content_redraw 两条路径上的来源结构不同。
        两种键都只与"同一维度"的条目比较,不会互相串味。
        """
        # 该函数会在 server.py 的 except WorkflowError 之外被调用,
        # 任何非预期入参都不能变成 500:非法入参一律视为"未命中"。
        if not isinstance(selection, dict):
            return None
        for rule in self.rules:
            picks = rule["picks"]
            if all(
                any(
                    self._pick_hit(item, pick, section)
                    for item in self._section_items(selection.get(section))
                )
                for section, pick in picks.items()
            ):
                return rule["id"]
        return None

    @classmethod
    def _pick_hit(cls, item: Any, pick: dict[str, Any], section: str) -> bool:
        """单个条目是否命中某条规则在该维度上的 pick。"""
        if not isinstance(item, dict):
            return False
        if item.get("section") not in (None, section):
            return False
        text = pick.get("text")
        if text is None:
            # 随机维度:只与随机条目比 id,绝不把固定伪条目(空 id)算进来。
            if item.get("fixed"):
                return False
            return item.get("id") == pick["id"]
        # 固定维度:按 tag 集合包含关系比对。content_redraw 里固定维度来自历史
        # 快照,是真实 catalog 条目(触发词在 title/prompt、系列在 subtitle);
        # 普通批次里来自 settings 的 fixed_* 原文(如 "alpha, series")。两者字段
        # 分布不同,汇总全部描述字段后判断"规则标签是否都被该维度包含",才能一致。
        wanted = _text_tags(text)
        return bool(wanted) and wanted.issubset(_item_tags(item))

    @staticmethod
    def _section_items(value: Any) -> list[Any]:
        """把抽取结果里的某一维度安全地读成列表;非 list 一律当作空。"""
        return value if isinstance(value, list) else []

    @staticmethod
    def _same_picks(left: dict[str, Any], right: dict[str, Any]) -> bool:
        if set(left) != set(right):
            return False
        for section in left:
            # 固定维度按 text 判同,随机维度按 id 判同:两者不可混为一谈,
            # 否则"固定角色A + 服装x"与"固定角色B + 服装x"会被误判为同一条。
            l_key = _normalize_text(left[section].get("text") or "") or left[section].get("id", "")
            r_key = _normalize_text(right[section].get("text") or "") or right[section].get("id", "")
            if l_key != r_key:
                return False
        return True

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
        picks: dict[str, dict[str, Any]] = {}
        for section, value in raw_picks.items():
            if not isinstance(value, dict):
                raise WorkflowError(f"组合规则的 {section} 必须是对象")
            item_id = str(value.get("id") or "").strip()
            raw_text = value.get("text")
            text = _normalize_text(raw_text) if raw_text is not None else ""
            if text and item_id:
                raise WorkflowError(
                    f"组合规则的 {section} 不能同时提供 id 与 text,请只选其中一种"
                )
            if text:
                # 固定提示词维度的匹配形态:固定维度不参与随机抽取,拿不到
                # catalog id,只能按提示词文本匹配(见 match()/_pick_hit)。
                if len(text) > MAX_PICK_TEXT:
                    raise WorkflowError(f"组合规则的 {section} 固定提示词过长")
                label = str(value.get("label") or "").strip() or text
                if len(label) > MAX_LABEL:
                    raise WorkflowError("组合规则标签过长")
                picks[section] = {
                    "id": "",
                    "text": text,
                    "label": label,
                    "fixed": True,
                }
                continue
            if not item_id:
                if raw_text is not None:
                    # 显式给了 text 却是空的:是想写固定维度但没填内容。
                    raise WorkflowError(
                        f"组合规则的 {section} 固定提示词不能为空"
                    )
                raise WorkflowError(f"组合规则的 {section} 缺少 id")
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
