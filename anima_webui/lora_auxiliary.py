from __future__ import annotations

import asyncio
import copy
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .persistence import backup_corrupt_file
from .workflow import WorkflowError, normalize_lora_path


MAX_ENTRIES = 4096
MAX_AUXILIARY_WORDS = 256
MAX_WORD_LENGTH = 500


def normalize_auxiliary_words(value: Any) -> list[str]:
    """验证并规范化 LoRA 辅助词数组，防御性去重并过滤空项。"""
    if not isinstance(value, list):
        raise WorkflowError("auxiliaryWords 必须是数组")
    if len(value) > MAX_AUXILIARY_WORDS:
        raise WorkflowError(f"LoRA 辅助词不能超过 {MAX_AUXILIARY_WORDS} 个")
    result: list[str] = []
    seen: set[str] = set()
    for index, raw in enumerate(value):
        if not isinstance(raw, str):
            raise WorkflowError(f"auxiliaryWords[{index}] 必须是字符串")
        word = raw.strip()
        if len(word) > MAX_WORD_LENGTH:
            raise WorkflowError(f"auxiliaryWords[{index}] 不能超过 {MAX_WORD_LENGTH} 个字符")
        identity = word.casefold()
        if word and identity not in seen:
            result.append(word)
            seen.add(identity)
    return result


class LoraAuxiliaryStore:
    """持久化存储各 LoRA 效果辅助词配置。"""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.words: dict[str, list[str]] = {}
        self.load_warnings: list[str] = []
        self._lock = asyncio.Lock()
        self.reload()

    def reload(self) -> None:
        self.load_warnings = []
        if not self.path.is_file():
            self.words = {}
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict) or payload.get("version") != 1:
                raise WorkflowError("LoRA 辅助词配置文件版本无效")
            raw_words = payload.get("auxiliary_words", {})
            if not isinstance(raw_words, dict) or len(raw_words) > MAX_ENTRIES:
                raise WorkflowError("LoRA 辅助词配置内容无效")
            words: dict[str, list[str]] = {}
            for raw_filename, items in raw_words.items():
                filename = normalize_lora_path(raw_filename)
                words[filename] = normalize_auxiliary_words(items)
        except (OSError, json.JSONDecodeError, WorkflowError) as error:
            backup = backup_corrupt_file(self.path)
            self.load_warnings.append(
                f"LoRA 辅助词文件无法读取({error}),已备份为 {backup.name} 并以空数据启动"
            )
            self.words = {}
            return
        self.words = words

    def has(self, filename: str) -> bool:
        identity = normalize_lora_path(filename).casefold()
        return any(key.casefold() == identity for key in self.words)

    def get(self, filename: str) -> list[str]:
        identity = normalize_lora_path(filename).casefold()
        for key, words in self.words.items():
            if key.casefold() == identity:
                return copy.deepcopy(words)
        return []

    async def set(self, filename: str, words: Any) -> list[str]:
        normalized_filename = normalize_lora_path(filename)
        normalized_words = normalize_auxiliary_words(words)
        async with self._lock:
            existing_key = next(
                (key for key in self.words if key.casefold() == normalized_filename.casefold()),
                None,
            )
            if existing_key is None and len(self.words) >= MAX_ENTRIES:
                raise WorkflowError(f"LoRA 辅助词配置不能超过 {MAX_ENTRIES} 项")
            if existing_key is not None and existing_key != normalized_filename:
                del self.words[existing_key]
            self.words[normalized_filename] = normalized_words
            await self._save()
        return copy.deepcopy(normalized_words)

    async def delete(self, filename: str) -> bool:
        identity = normalize_lora_path(filename).casefold()
        async with self._lock:
            key = next((item for item in self.words if item.casefold() == identity), None)
            if key is None:
                return False
            del self.words[key]
            await self._save()
        return True

    async def _save(self) -> None:
        payload = json.dumps(
            {"version": 1, "auxiliary_words": self.words},
            ensure_ascii=False,
            indent=2,
        ) + "\n"
        await asyncio.to_thread(self._write_text, payload)

    def _write_text(self, text: str) -> None:
        fd, temp_name = tempfile.mkstemp(
            prefix="lora-auxiliary-words-", suffix=".json", dir=self.path.parent
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

