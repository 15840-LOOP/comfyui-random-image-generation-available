from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import json
import struct
from anima_webui.lora_triggers import (
    LoraTriggerOverrideStore,
    extract_safetensors_triggers,
    normalize_trigger_words,
)
from anima_webui.workflow import WorkflowError


class LoraTriggerOverrideStoreTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "lora_trigger_overrides.json"
        self.store = LoraTriggerOverrideStore(self.path)

    def tearDown(self) -> None:
        self.temp.cleanup()

    async def test_override_empty_reset_and_case_insensitive_lookup(self):
        words = await self.store.set(
            "Style/Test.safetensors", [" @Exact_One ", "@exact_one", "Second"]
        )
        self.assertEqual(words, ["@Exact_One", "Second"])
        self.assertEqual(
            self.store.effective("style/test.safetensors", ["source"]),
            (["@Exact_One", "Second"], True),
        )

        await self.store.set("Style/Test.safetensors", [])
        reopened = LoraTriggerOverrideStore(self.path)
        self.assertEqual(reopened.effective("STYLE/TEST.safetensors", ["source"]), ([], True))
        self.assertTrue(await reopened.delete("style/test.safetensors"))
        self.assertEqual(reopened.effective("Style/Test.safetensors", ["source"]), (["source"], False))

    def test_validation_preserves_exact_spelling(self):
        self.assertEqual(normalize_trigger_words(["@Niji9il", "A_B"]), ["@Niji9il", "A_B"])
        with self.assertRaisesRegex(WorkflowError, "必须是数组"):
            normalize_trigger_words("@bad")
        with self.assertRaisesRegex(WorkflowError, "必须是字符串"):
            normalize_trigger_words([1])

    def test_extract_safetensors_triggers_from_header_and_info(self):
        # 1. 模拟 safetensors 文件
        st_file = Path(self.temp.name) / "mock_lora.safetensors"
        meta = {
            "__metadata__": {
                "modelspec.trigger_phrase": "@primary, second tag",
                "ss_tag_frequency": json.dumps({"sub": {"@at_tag": 100, "general tag": 50}}),
            }
        }
        header_bytes = json.dumps(meta).encode("utf-8")
        with st_file.open("wb") as fp:
            fp.write(struct.pack("<Q", len(header_bytes)))
            fp.write(header_bytes)
            fp.write(b"mock_tensor_bytes")

        triggers = extract_safetensors_triggers(st_file)
        self.assertEqual(triggers, ["@primary", "second tag"])

        # 2. 模拟仅有 ss_tag_frequency 的情况
        st_file_freq = Path(self.temp.name) / "mock_freq.safetensors"
        meta_freq = {
            "__metadata__": {
                "ss_tag_frequency": {"dir": {"@special_style": 88, "@_@": 88, "common": 88}}
            }
        }
        header_freq_bytes = json.dumps(meta_freq).encode("utf-8")
        with st_file_freq.open("wb") as fp:
            fp.write(struct.pack("<Q", len(header_freq_bytes)))
            fp.write(header_freq_bytes)

        triggers_freq = extract_safetensors_triggers(st_file_freq)
        self.assertEqual(triggers_freq, ["@special_style"])

        # 3. 模拟 civitai.info 覆盖
        info_file = Path(self.temp.name) / "mock_lora.civitai.info"
        info_file.write_text(json.dumps({"trainedWords": ["@civitai_trained"]}), encoding="utf-8")
        self.assertEqual(extract_safetensors_triggers(st_file), ["@civitai_trained"])

        # 4. 模拟损坏文件安全回退
        corrupt_file = Path(self.temp.name) / "corrupt.safetensors"
        corrupt_file.write_bytes(b"bad")
        self.assertEqual(extract_safetensors_triggers(corrupt_file), [])

    def test_corrupt_file_is_backed_up(self):
        self.path.write_text("[]", encoding="utf-8")
        reopened = LoraTriggerOverrideStore(self.path)
        self.assertEqual(reopened.overrides, {})
        self.assertTrue(reopened.load_warnings)
        self.assertTrue((self.path.with_name(self.path.name + ".corrupt.bak")).is_file())


if __name__ == "__main__":
    unittest.main()
