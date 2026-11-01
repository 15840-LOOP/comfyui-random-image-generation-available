from __future__ import annotations

import asyncio
import copy
import json
import os
import re
import struct
import tempfile
from pathlib import Path
from typing import Any

from .persistence import backup_corrupt_file
from .workflow import WorkflowError, normalize_lora_path


MAX_OVERRIDES = 4096
MAX_TRIGGER_WORDS = 256
MAX_TRIGGER_LENGTH = 500


def normalize_trigger_words(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise WorkflowError("triggerWords 必须是数组")
    if len(value) > MAX_TRIGGER_WORDS:
        raise WorkflowError(f"LoRA 触发词不能超过 {MAX_TRIGGER_WORDS} 个")
    result: list[str] = []
    seen: set[str] = set()
    for index, raw in enumerate(value):
        if not isinstance(raw, str):
            raise WorkflowError(f"triggerWords[{index}] 必须是字符串")
        word = raw.strip()
        if len(word) > MAX_TRIGGER_LENGTH:
            raise WorkflowError(f"triggerWords[{index}] 不能超过 {MAX_TRIGGER_LENGTH} 个字符")
        identity = word.casefold()
        if word and identity not in seen:
            result.append(word)
            seen.add(identity)
    return result


def extract_safetensors_triggers(file_path: str | Path) -> list[str]:
    """防御性提取本地 LoRA (safetensors 或同名辅助文件) 的默认触发词。

    解析优先级：
    1. 同名 .civitai.info 中的 trainedWords
    2. safetensors 头部元数据中的 modelspec.trigger_phrase 或 ss_tag_frequency (@标签优先)
    3. 同名 .txt 中的首选提示词
    任何异常均安全吞吐回退为 []。
    """
    path = Path(file_path)
    if not path.is_file():
        return []

    # 1. 优先检查同名 .civitai.info
    info_path = path.with_suffix(".civitai.info")
    if not info_path.is_file():
        info_path = path.parent / f"{path.stem}.civitai.info"
    if info_path.is_file():
        try:
            info_data = json.loads(info_path.read_text(encoding="utf-8"))
            if isinstance(info_data, dict):
                words = info_data.get("trainedWords")
                if isinstance(words, list) and words:
                    parsed = normalize_trigger_words(words)
                    if parsed:
                        return parsed
        except Exception:
            pass

    # 2. 如果是 safetensors，解析其 header
    if path.suffix.lower() == ".safetensors":
        try:
            with path.open("rb") as fp:
                length_bytes = fp.read(8)
                if len(length_bytes) == 8:
                    header_len = struct.unpack("<Q", length_bytes)[0]
                    # 安全限制：最大读取 16MB 头部
                    if 0 < header_len < 16 * 1024 * 1024:
                        header_raw = fp.read(header_len).decode("utf-8", errors="ignore")
                        header_obj = json.loads(header_raw)
                        metadata = header_obj.get("__metadata__")
                        if isinstance(metadata, dict):
                            # 2.1 检查 modelspec.trigger_phrase
                            trigger_phrase = metadata.get("modelspec.trigger_phrase")
                            if isinstance(trigger_phrase, str) and trigger_phrase.strip():
                                words = [w.strip() for w in trigger_phrase.split(",") if w.strip()]
                                if words:
                                    return normalize_trigger_words(words)

                            # 2.2 检查 ss_tag_frequency
                            raw_freq = metadata.get("ss_tag_frequency")
                            if raw_freq:
                                if isinstance(raw_freq, str):
                                    try:
                                        raw_freq = json.loads(raw_freq)
                                    except Exception:
                                        raw_freq = None
                                if isinstance(raw_freq, dict):
                                    at_tags: list[str] = []
                                    all_tags: dict[str, int] = {}
                                    for sub in raw_freq.values():
                                        if isinstance(sub, dict):
                                            for tag, count in sub.items():
                                                if isinstance(tag, str) and tag.strip():
                                                    t = tag.strip()
                                                    cnt = count if isinstance(count, int) else 0
                                                    all_tags[t] = max(all_tags.get(t, 0), cnt)
                                                    if t.startswith("@"):
                                                        # 过滤纯符号颜文字如 @_@
                                                        clean_ident = re.sub(r"[@_\-\s]", "", t)
                                                        if any(c.isalnum() for c in clean_ident):
                                                            at_tags.append(t)
                                    # 专有触发词优先提取 @ 开头的词条
                                    if at_tags:
                                        return normalize_trigger_words(at_tags)
                                    # 若无 @ 标签，提取频次最高的满频/高频标签（最多前 2 个）
                                    if all_tags:
                                        sorted_tags = sorted(
                                            all_tags.items(), key=lambda kv: kv[1], reverse=True
                                        )
                                        max_count = sorted_tags[0][1]
                                        candidates = [
                                            k
                                            for k, v in sorted_tags[:3]
                                            if v >= max(1, int(max_count * 0.9))
                                            and len(k) <= 80
                                        ]
                                        if candidates:
                                            return normalize_trigger_words(candidates)
        except Exception:
            pass

    # 3. 检查同名 .txt 文件
    txt_path = path.with_suffix(".txt")
    if txt_path.is_file():
        try:
            content = txt_path.read_text(encoding="utf-8").strip()
            if content:
                first_line = content.splitlines()[0]
                words = [w.strip() for w in re.split(r",|，|\n", first_line) if w.strip()]
                if words:
                    return normalize_trigger_words(words[:10])
        except Exception:
            pass

    return []


class LoraTriggerOverrideStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.overrides: dict[str, list[str]] = {}
        self.load_warnings: list[str] = []
        self._lock = asyncio.Lock()
        self.reload()

    def reload(self) -> None:
        self.load_warnings = []
        if not self.path.is_file():
            self.overrides = {}
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict) or payload.get("version") != 1:
                raise WorkflowError("LoRA 触发词覆盖文件版本无效")
            raw_overrides = payload.get("overrides", {})
            if not isinstance(raw_overrides, dict) or len(raw_overrides) > MAX_OVERRIDES:
                raise WorkflowError("LoRA 触发词覆盖内容无效")
            overrides: dict[str, list[str]] = {}
            for raw_filename, words in raw_overrides.items():
                filename = normalize_lora_path(raw_filename)
                overrides[filename] = normalize_trigger_words(words)
        except (OSError, json.JSONDecodeError, WorkflowError) as error:
            backup = backup_corrupt_file(self.path)
            self.load_warnings.append(
                f"LoRA 触发词覆盖文件无法读取({error}),已备份为 {backup.name} 并以空数据启动"
            )
            self.overrides = {}
            return
        self.overrides = overrides

    def has(self, filename: str) -> bool:
        identity = normalize_lora_path(filename).casefold()
        return any(key.casefold() == identity for key in self.overrides)

    def get(self, filename: str) -> list[str] | None:
        identity = normalize_lora_path(filename).casefold()
        for key, words in self.overrides.items():
            if key.casefold() == identity:
                return copy.deepcopy(words)
        return None

    def effective(self, filename: str, source_words: Any) -> tuple[list[str], bool]:
        override = self.get(filename)
        if override is not None:
            return override, True
        try:
            return normalize_trigger_words(source_words), False
        except WorkflowError:
            return [], False

    async def set(self, filename: str, words: Any) -> list[str]:
        normalized_filename = normalize_lora_path(filename)
        normalized_words = normalize_trigger_words(words)
        async with self._lock:
            existing_key = next(
                (key for key in self.overrides if key.casefold() == normalized_filename.casefold()),
                None,
            )
            if existing_key is None and len(self.overrides) >= MAX_OVERRIDES:
                raise WorkflowError(f"LoRA 触发词覆盖不能超过 {MAX_OVERRIDES} 项")
            if existing_key is not None and existing_key != normalized_filename:
                del self.overrides[existing_key]
            self.overrides[normalized_filename] = normalized_words
            await self._save()
        return copy.deepcopy(normalized_words)

    async def delete(self, filename: str) -> bool:
        identity = normalize_lora_path(filename).casefold()
        async with self._lock:
            key = next((item for item in self.overrides if item.casefold() == identity), None)
            if key is None:
                return False
            del self.overrides[key]
            await self._save()
        return True

    async def _save(self) -> None:
        payload = json.dumps(
            {"version": 1, "overrides": self.overrides},
            ensure_ascii=False,
            indent=2,
        ) + "\n"
        await asyncio.to_thread(self._write_text, payload)

    def _write_text(self, text: str) -> None:
        fd, temp_name = tempfile.mkstemp(
            prefix="lora-trigger-overrides-", suffix=".json", dir=self.path.parent
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
