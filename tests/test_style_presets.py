import json
import sys
import tempfile
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from anima_webui.style_presets import PRESET_SETTING_KEYS, StylePresetStore, preset_settings  # noqa: E402
from anima_webui.workflow import DEFAULT_SETTINGS, WorkflowError  # noqa: E402


def snapshot(**overrides):
    values = {key: DEFAULT_SETTINGS[key] for key in PRESET_SETTING_KEYS}
    values.update(overrides)
    return values


class StylePresetTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "style_presets.json"
        self.store = StylePresetStore(self.path)

    def tearDown(self):
        self.temp.cleanup()

    async def test_favorites_sort_first_and_updates_replace_the_snapshot(self):
        favorite = await self.store.create(
            {"name": "Favorite", "favorite": True, "settings": snapshot(width=768)}
        )
        regular = await self.store.create(
            {"name": "Regular", "favorite": False, "settings": snapshot(width=832)}
        )
        self.assertEqual([item["id"] for item in self.store.list()["items"]], [favorite["id"], regular["id"]])

        updated = await self.store.update(
            regular["id"],
            {"name": "Renamed", "favorite": True, "settings": snapshot(width=1024)},
        )
        self.assertEqual(updated["name"], "Renamed")
        self.assertEqual(updated["settings"]["width"], 1024)
        self.assertTrue(await self.store.delete(favorite["id"]))
        self.assertFalse(await self.store.delete("missing"))

    async def test_atomic_save_leaves_valid_json_without_temp_files(self):
        await self.store.create({"name": "Atomic", "settings": snapshot(), "favorite": False})
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(payload["version"], 1)
        self.assertEqual(payload["items"][0]["name"], "Atomic")
        self.assertEqual(list(self.path.parent.glob("style-presets-*.json")), [])

    def test_corrupt_file_is_backed_up_and_store_starts_empty(self):
        # 回归 #P2-4:坏文件不再阻断启动,改名备份后以空数据继续并给出警告。
        self.path.write_text("{ not valid json", encoding="utf-8")
        store = StylePresetStore(self.path)
        self.assertEqual(store.items, [])
        self.assertEqual(len(store.load_warnings), 1)
        self.assertIn("style_presets.json.corrupt.bak", store.load_warnings[0])
        self.assertTrue(self.path.with_name("style_presets.json.corrupt.bak").is_file())
        self.assertFalse(self.path.exists())

    def test_partial_legacy_snapshot_receives_current_defaults(self):
        settings = preset_settings({"width": 1024, "manual_artist": "anmi"})
        self.assertEqual(settings["model_name"], DEFAULT_SETTINGS["model_name"])
        self.assertEqual(settings["hires"], DEFAULT_SETTINGS["hires"])
        self.assertEqual(settings["detailers"], DEFAULT_SETTINGS["detailers"])
        self.assertEqual(settings["sampler_name"], DEFAULT_SETTINGS["sampler_name"])
        self.assertEqual(settings["scheduler"], DEFAULT_SETTINGS["scheduler"])
        self.assertEqual(settings["cfg_zero_star"], DEFAULT_SETTINGS["cfg_zero_star"])
        self.assertEqual(settings["second_sampler"], DEFAULT_SETTINGS["second_sampler"])
        self.assertEqual(settings["manual_artist"], "@anmi")

    def test_prompt_pool_fields_are_part_of_the_snapshot(self):
        # 回归:预设白名单必须包含提示词池字段,否则保存时被丢弃、应用时无法回填。
        for key in (
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
        ):
            self.assertIn(key, PRESET_SETTING_KEYS)

    def test_prompt_pool_snapshot_round_trips_through_preset_settings(self):
        pools = {
            "character": {"mode": "include", "ids": ["char_a", "char_b"], "excluded_ids": ["char_c"]},
            "clothing": {"mode": "all", "ids": [], "excluded_ids": ["cloth_x"]},
            "pose": {"mode": "include", "ids": ["pose_a"], "excluded_ids": []},
            "background": {"mode": "include", "ids": [], "excluded_ids": []},
            "expression": {"mode": "include", "ids": ["expr_a"], "excluded_ids": []},
        }
        settings = preset_settings(
            {
                # 角色抽取数不能超过画面总人数(默认 1),否则触发 validate_settings 校验。
                "random_character": True,
                "random_character_count": 1,
                "random_pose": True,
                "fixed_clothing": "school uniform",
                "pools": pools,
            }
        )
        self.assertTrue(settings["random_character"])
        self.assertEqual(settings["random_character_count"], 1)
        self.assertTrue(settings["random_pose"])
        self.assertEqual(settings["fixed_clothing"], "school uniform")
        self.assertEqual(settings["pools"]["character"]["ids"], ["char_a", "char_b"])
        self.assertEqual(settings["pools"]["character"]["excluded_ids"], ["char_c"])
        self.assertEqual(settings["pools"]["clothing"]["mode"], "all")
        self.assertEqual(settings["pools"]["expression"]["ids"], ["expr_a"])

    async def test_prompt_pool_snapshot_persists_and_reloads(self):
        pools = {
            "character": {"mode": "include", "ids": ["char_a"], "excluded_ids": []},
            "clothing": {"mode": "include", "ids": [], "excluded_ids": []},
            "pose": {"mode": "all", "ids": [], "excluded_ids": ["pose_x"]},
            "background": {"mode": "include", "ids": [], "excluded_ids": []},
            "expression": {"mode": "include", "ids": [], "excluded_ids": []},
        }
        created = await self.store.create(
            {
                "name": "Pooled",
                "favorite": False,
                "settings": snapshot(random_pose=True, fixed_character="miku", pools=pools),
            }
        )
        self.assertTrue(created["settings"]["random_pose"])
        self.assertEqual(created["settings"]["fixed_character"], "miku")
        self.assertEqual(created["settings"]["pools"]["pose"]["mode"], "all")
        self.assertEqual(created["settings"]["pools"]["pose"]["excluded_ids"], ["pose_x"])

        # 重新加载存储,确认池字段被持久化而非仅存在于内存。
        reloaded = StylePresetStore(self.path)
        item = next(entry for entry in reloaded.items if entry["id"] == created["id"])
        self.assertEqual(item["settings"]["pools"]["character"]["ids"], ["char_a"])
        self.assertEqual(item["settings"]["pools"]["pose"]["mode"], "all")
        self.assertEqual(item["settings"]["fixed_character"], "miku")

    async def test_duplicate_names_are_rejected_case_insensitively(self):
        first = await self.store.create({"name": "Soft Light", "settings": snapshot(), "favorite": False})
        with self.assertRaisesRegex(WorkflowError, "同名"):
            await self.store.create({"name": "soft light", "settings": snapshot(), "favorite": False})

        second = await self.store.create({"name": "Ink", "settings": snapshot(), "favorite": False})
        with self.assertRaisesRegex(WorkflowError, "同名"):
            await self.store.update(second["id"], {"name": "SOFT LIGHT"})
        self.assertEqual((await self.store.update(first["id"], {"name": "Soft Light"}))["name"], "Soft Light")


if __name__ == "__main__":
    unittest.main()
