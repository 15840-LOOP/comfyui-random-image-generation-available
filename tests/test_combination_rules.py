import json
import sys
import tempfile
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from anima_webui.combination_rules import (  # noqa: E402
    MAX_COMBINATION_RULES,
    CombinationRuleStore,
)
from anima_webui.workflow import WorkflowError  # noqa: E402


def picks(**kwargs):
    """构造 picks 载荷：picks(character=("id1", "标签1"), clothing=("id2", "标签2"))"""
    return {
        section: {"id": value[0], "label": value[1]}
        for section, value in kwargs.items()
    }


class CombinationRuleStoreTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "combination_rules.json"
        self.store = CombinationRuleStore(self.path)

    def tearDown(self):
        self.temp.cleanup()

    async def test_create_persists_and_returns_rule(self):
        item = await self.store.create(
            {"picks": picks(character=("character:a", "角色A"), clothing=("clothing:b", "服装B"))}
        )
        self.assertTrue(item["id"].startswith("combo_"))
        self.assertEqual(set(item["picks"]), {"character", "clothing"})
        self.assertIn("created_at", item)

        reloaded = CombinationRuleStore(self.path)
        self.assertEqual(reloaded.list()["count"], 1)
        self.assertEqual(reloaded.list()["items"][0]["id"], item["id"])

    async def test_single_dimension_is_rejected(self):
        with self.assertRaises(WorkflowError):
            await self.store.create({"picks": picks(character=("character:a", "角色A"))})

    async def test_unknown_section_is_rejected(self):
        with self.assertRaises(WorkflowError):
            await self.store.create(
                {"picks": {"nonsense": {"id": "x", "label": "y"}}}
            )

    async def test_duplicate_picks_is_idempotent(self):
        payload = {"picks": picks(character=("character:a", "角色A"), clothing=("clothing:b", "服装B"))}
        first = await self.store.create(payload)
        second = await self.store.create(payload)
        self.assertEqual(first["id"], second["id"])
        self.assertEqual(self.store.list()["count"], 1)

    async def test_match_requires_all_dimensions(self):
        await self.store.create(
            {"picks": picks(character=("character:a", "角色A"), clothing=("clothing:b", "服装B"))}
        )
        # 两项都命中 -> 命中
        self.assertIsNotNone(
            self.store.match(
                {
                    "character": [{"id": "character:a"}],
                    "clothing": [{"id": "clothing:b"}],
                }
            )
        )
        # 只有角色命中 -> 不命中
        self.assertIsNone(
            self.store.match(
                {"character": [{"id": "character:a"}], "clothing": [{"id": "clothing:x"}]}
            )
        )
        # 只有服装命中 -> 不命中
        self.assertIsNone(
            self.store.match(
                {"character": [{"id": "character:x"}], "clothing": [{"id": "clothing:b"}]}
            )
        )

    async def test_match_ignores_missing_section(self):
        await self.store.create(
            {"picks": picks(character=("character:a", "角色A"), clothing=("clothing:b", "服装B"))}
        )
        self.assertIsNone(self.store.match({"character": [{"id": "character:a"}]}))

    async def test_match_handles_multi_item_section(self):
        await self.store.create(
            {"picks": picks(character=("character:a", "角色A"), pose=("pose:p", "姿势P"))}
        )
        # 角色抽了 3 个，其中一个是 a；姿势也命中 -> 命中
        self.assertIsNotNone(
            self.store.match(
                {
                    "character": [{"id": "character:x"}, {"id": "character:a"}, {"id": "character:z"}],
                    "pose": [{"id": "pose:p"}],
                }
            )
        )

    async def test_delete_and_clear(self):
        a = await self.store.create(
            {"picks": picks(character=("character:a", "A"), clothing=("clothing:a", "B"))}
        )
        b = await self.store.create(
            {"picks": picks(character=("character:b", "C"), clothing=("clothing:b", "D"))}
        )
        self.assertTrue(await self.store.delete(a["id"]))
        self.assertFalse(await self.store.delete(a["id"]))
        self.assertEqual(self.store.list()["count"], 1)
        self.assertEqual(await self.store.clear(), 1)
        self.assertEqual(self.store.list()["count"], 0)

    async def test_rule_limit(self):
        for index in range(MAX_COMBINATION_RULES):
            await self.store.create(
                {
                    "picks": picks(
                        character=(f"character:{index}", "A"),
                        clothing=(f"clothing:{index}", "B"),
                    )
                }
            )
        with self.assertRaises(WorkflowError):
            await self.store.create(
                {"picks": picks(character=("character:x", "A"), clothing=("clothing:x", "B"))}
            )

    async def test_corrupt_file_is_backed_up(self):
        self.path.write_text("{not json", encoding="utf-8")
        store = CombinationRuleStore(self.path)
        self.assertEqual(store.list()["count"], 0)
        self.assertTrue(store.load_warnings)
        self.assertTrue(any(self.path.parent.glob("combination_rules.json.corrupt*")))

    async def test_save_is_atomic_no_temp_leftovers(self):
        await self.store.create(
            {"picks": picks(character=("character:a", "A"), clothing=("clothing:b", "B"))}
        )
        leftovers = list(self.path.parent.glob("combination-rules-*.json"))
        self.assertEqual(leftovers, [])
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(payload["version"], 1)

    async def test_custom_items_are_allowed(self):
        """自定义词条 id 是 custom:N(不带维度前缀),不能被前缀校验误杀。"""
        item = await self.store.create(
            {"picks": picks(character=("custom:c01", "自定义角色"), clothing=("clothing:b", "服装B"))}
        )
        self.assertEqual(item["picks"]["character"]["id"], "custom:c01")
        self.assertIsNotNone(
            self.store.match(
                {
                    "character": [{"id": "custom:c01"}],
                    "clothing": [{"id": "clothing:b"}],
                }
            )
        )

    async def test_cross_section_id_is_rejected(self):
        with self.assertRaises(WorkflowError):
            await self.store.create(
                {"picks": picks(character=("clothing:b", "服装B"), clothing=("clothing:b", "服装B"))}
            )

    async def test_clear_persists_empty_file(self):
        await self.store.create(
            {"picks": picks(character=("character:a", "A"), clothing=("clothing:b", "B"))}
        )
        await self.store.clear()
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(payload["rules"], [])
