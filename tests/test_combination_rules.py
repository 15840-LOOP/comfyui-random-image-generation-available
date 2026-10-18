import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from anima_webui.combination_rules import (  # noqa: E402
    MAX_COMBINATION_RULES,
    CombinationRuleStore,
)
from anima_webui.workflow import WorkflowError  # noqa: E402


def picks(**kwargs):
    """构造 picks 载荷：picks(character=("character:id1", "标签1"))"""
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
        """自定义词条 id 是 custom:<uuid4().hex>(不带维度前缀),不能被格式校验误杀。"""
        item = await self.store.create(
            {"picks": picks(character=("custom:" + "a" * 32, "自定义角色"), clothing=("clothing:b", "服装B"))}
        )
        self.assertEqual(item["picks"]["character"]["id"], "custom:" + "a" * 32)
        self.assertIsNotNone(
            self.store.match(
                {
                    "character": [{"id": "custom:" + "a" * 32}],
                    "clothing": [{"id": "clothing:b"}],
                }
            )
        )

    async def test_cross_section_id_is_rejected(self):
        with self.assertRaises(WorkflowError):
            await self.store.create(
                {"picks": picks(character=("clothing:b", "服装B"), clothing=("clothing:b", "服装B"))}
            )

    async def test_bare_id_without_prefix_is_rejected(self):
        """无前缀 id 永远命中不了 catalog 条目,必须在入口拒绝而不是静默失效。"""
        with self.assertRaises(WorkflowError):
            await self.store.create(
                {"picks": picks(character=("x", "垃圾id"), clothing=("clothing:b", "服装B"))}
            )

    async def test_fixed_prompt_dimension_is_accepted_with_text(self):
        """固定维度走 text 形态:固定提示词不参与抽取,只能按文本匹配。"""
        item = await self.store.create(
            {
                "picks": {
                    "character": {"text": "alpha, series", "label": "固定角色"},
                    "clothing": {"id": "clothing:b", "label": "服装B"},
                }
            }
        )
        pick = item["picks"]["character"]
        self.assertEqual(pick["text"], "alpha, series")
        self.assertEqual(pick["id"], "")
        self.assertTrue(pick["fixed"])
        self.assertEqual(pick["label"], "固定角色")
        self.assertEqual(self.store.list()["count"], 1)

    async def test_match_fixed_pick_by_text(self):
        """固定伪条目按主身份命中:title 是身份、subtitle 是精确化信息。"""
        await self.store.create(
            {
                "picks": {
                    "character": {"text": "alpha, series", "label": "固定角色"},
                    "clothing": {"id": "clothing:b", "label": "服装B"},
                }
            }
        )
        fixed_character = {
            "id": "",
            "section": "character",
            "title": "alpha",
            "subtitle": "series",
            "prompt": "alpha, series",
            "fixed": True,
        }
        clothing = {"id": "clothing:b"}
        self.assertIsNotNone(
            self.store.match({"character": [fixed_character], "clothing": [clothing]})
        )
        # 主身份不同 -> 不命中
        self.assertIsNone(
            self.store.match(
                {
                    "character": [{**fixed_character, "title": "beta", "prompt": "beta, series"}],
                    "clothing": [clothing],
                }
            )
        )
        # 系列不同 -> 不命中
        self.assertIsNone(
            self.store.match(
                {
                    "character": [
                        {**fixed_character, "subtitle": "other", "prompt": "alpha, other"}
                    ],
                    "clothing": [clothing],
                }
            )
        )
        # 服装不同 -> 不命中
        self.assertIsNone(
            self.store.match(
                {
                    "character": [fixed_character],
                    "clothing": [{"id": "clothing:other"}],
                }
            )
        )

    async def test_match_fixed_text_is_whitespace_normalized(self):
        """固定提示词是手写文本,多余空白不应让规则静默失效。"""
        await self.store.create(
            {
                "picks": {
                    "character": {"text": "alpha,   series", "label": "固定角色"},
                    "clothing": {"id": "clothing:b", "label": "服装B"},
                }
            }
        )
        self.assertIsNotNone(
            self.store.match(
                {
                    "character": [
                        {
                            "id": "",
                            "section": "character",
                            "title": "  alpha  ",
                            "subtitle": " series ",
                            "prompt": "  alpha, series  ",
                            "fixed": True,
                        }
                    ],
                    "clothing": [{"id": "clothing:b"}],
                }
            )
        )

    async def test_random_pick_does_not_match_fixed_pseudo_entry(self):
        """随机维度规则不能因为固定伪条目 id 为空而被误命中。"""
        await self.store.create(
            {"picks": picks(character=("character:a", "A"), clothing=("clothing:b", "B"))}
        )
        self.assertIsNone(
            self.store.match(
                {
                    "character": [{"id": "", "section": "character", "fixed": True}],
                    "clothing": [{"id": "clothing:b"}],
                }
            )
        )

    async def test_fixed_pick_matches_entry_by_descriptive_text(self):
        """固定维度按描述文本匹配,因此历史快照里的真实 catalog 条目也能命中。

        content_redraw 的固定维度直接来自历史快照(真实条目,带 id 与 title),
        与普通批次的伪条目结构不同;若只认 fixed 标记就会在两条路径上不一致。
        """
        await self.store.create(
            {
                "picks": {
                    "character": {"text": "alpha, series", "label": "固定角色"},
                    "clothing": {"id": "clothing:b", "label": "服装B"},
                }
            }
        )
        self.assertIsNotNone(
            self.store.match(
                {
                    "character": [
                        {
                            "id": "character:alpha||series",
                            "title": "alpha",
                            "subtitle": "series",
                            "prompt": "alpha, 1girl",
                        }
                    ],
                    "clothing": [{"id": "clothing:b"}],
                }
            )
        )
        # 描述文本对不上的条目仍然不命中。
        self.assertIsNone(
            self.store.match(
                {
                    "character": [
                        {"id": "character:beta||series", "title": "beta", "prompt": "beta"}
                    ],
                    "clothing": [{"id": "clothing:b"}],
                }
            )
        )

    async def test_generic_tag_does_not_hit_entries(self):
        """判据 1:通用标签(只出现在 prompt/tags 里)不得命中任何条目。

        否则 text="1girl" 会把所有女性角色条目判为命中,规则退化成"整维全禁"。
        """
        await self.store.create(
            {
                "picks": {
                    "character": {"text": "1girl", "label": "通用标签"},
                    "clothing": {"id": "clothing:b", "label": "服装B"},
                }
            }
        )
        entry = {
            "id": "character:alpha||series",
            "section": "character",
            "title": "alpha",
            "subtitle": "series",
            "prompt": "alpha, 1girl, long hair",
            "tags": ["1girl", "long hair"],
        }
        self.assertIsNone(
            self.store.match({"character": [entry], "clothing": [{"id": "clothing:b"}]})
        )

    async def test_identity_tag_hits_matching_title_only(self):
        """判据 2:text="alpha" 命中 title=alpha,不命中 title=beta。"""
        await self.store.create(
            {
                "picks": {
                    "character": {"text": "alpha", "label": "alpha"},
                    "clothing": {"id": "clothing:b", "label": "服装B"},
                }
            }
        )
        def entry(title):
            return {
                "id": f"character:{title}||series",
                "section": "character",
                "title": title,
                "subtitle": "series",
                "prompt": f"{title}, 1girl",
                "tags": ["1girl"],
            }
        self.assertIsNotNone(
            self.store.match(
                {"character": [entry("alpha")], "clothing": [{"id": "clothing:b"}]}
            )
        )
        self.assertIsNone(
            self.store.match(
                {"character": [entry("beta")], "clothing": [{"id": "clothing:b"}]}
            )
        )

    async def test_identity_plus_series_is_precise(self):
        """判据 3:"alpha, series" 命中 alpha+series,不命中 alpha+其它系列。"""
        await self.store.create(
            {
                "picks": {
                    "character": {"text": "alpha, series", "label": "alpha"},
                    "clothing": {"id": "clothing:b", "label": "服装B"},
                }
            }
        )
        def entry(series):
            return {
                "id": f"character:alpha||{series}",
                "section": "character",
                "title": "alpha",
                "subtitle": series,
                "prompt": "alpha, 1girl",
                "tags": ["1girl"],
            }
        self.assertIsNotNone(
            self.store.match(
                {"character": [entry("series")], "clothing": [{"id": "clothing:b"}]}
            )
        )
        self.assertIsNone(
            self.store.match(
                {"character": [entry("other")], "clothing": [{"id": "clothing:b"}]}
            )
        )

    async def test_random_pick_still_matches_by_id_only(self):
        """判据 4:随机维度按 id 匹配完全不变(不受 title/text 逻辑影响)。"""
        await self.store.create(
            {"picks": picks(character=("character:a", "A"), clothing=("clothing:b", "B"))}
        )
        self.assertIsNotNone(
            self.store.match(
                {
                    "character": [{"id": "character:a", "title": "完全不同"}],
                    "clothing": [{"id": "clothing:b"}],
                }
            )
        )
        # id 不同即便 title 相同也不命中
        self.assertIsNone(
            self.store.match(
                {
                    "character": [{"id": "character:z", "title": "A"}],
                    "clothing": [{"id": "clothing:b"}],
                }
            )
        )

    async def test_id_and_text_together_are_rejected(self):
        with self.assertRaisesRegex(WorkflowError, "不能同时提供 id 与 text"):
            await self.store.create(
                {
                    "picks": {
                        "character": {"id": "character:a", "text": "alpha"},
                        "clothing": {"id": "clothing:b", "label": "服装B"},
                    }
                }
            )

    async def test_empty_text_is_rejected_with_its_own_message(self):
        with self.assertRaisesRegex(WorkflowError, "固定提示词不能为空"):
            await self.store.create(
                {
                    "picks": {
                        "character": {"text": "   ", "label": "固定角色"},
                        "clothing": {"id": "clothing:b", "label": "服装B"},
                    }
                }
            )

    async def test_missing_id_without_text_says_missing_id(self):
        """忘填 id 与"想写固定维度"是两回事,文案必须区分。"""
        with self.assertRaisesRegex(WorkflowError, "缺少 id"):
            await self.store.create(
                {"picks": picks(character=("", "固定角色"), clothing=("clothing:b", "服装B"))}
            )
        self.assertEqual(self.store.list()["count"], 0)

    async def test_blank_id_after_strip_says_missing_id(self):
        """只有空白的 id 且没有 text,同样属于忘填 id。"""
        for blank in ("   ", "\t", "\n"):
            with self.subTest(blank=repr(blank)):
                with self.assertRaisesRegex(WorkflowError, "缺少 id"):
                    await self.store.create(
                        {
                            "picks": {
                                "character": {"id": blank, "label": "固定角色"},
                                "clothing": {"id": "clothing:b", "label": "服装B"},
                            }
                        }
                    )

    async def test_fixed_picks_dedupe_uses_text(self):
        """固定维度按 text 判同:文本不同的两条规则不能被误判为同一条。"""
        first = await self.store.create(
            {
                "picks": {
                    "character": {"text": "alpha", "label": "A"},
                    "clothing": {"id": "clothing:b", "label": "服装B"},
                }
            }
        )
        second = await self.store.create(
            {
                "picks": {
                    "character": {"text": "beta", "label": "B"},
                    "clothing": {"id": "clothing:b", "label": "服装B"},
                }
            }
        )
        self.assertNotEqual(first["id"], second["id"])
        self.assertEqual(self.store.list()["count"], 2)
        again = await self.store.create(
            {
                "picks": {
                    "character": {"text": "alpha", "label": "A"},
                    "clothing": {"id": "clothing:b", "label": "服装B"},
                }
            }
        )
        self.assertEqual(again["id"], first["id"])
        self.assertEqual(self.store.list()["count"], 2)

    async def test_match_tolerates_non_mapping_selection(self):
        await self.store.create(
            {"picks": picks(character=("character:a", "A"), clothing=("clothing:b", "B"))}
        )
        self.assertIsNone(self.store.match(None))
        self.assertIsNone(self.store.match([]))
        self.assertIsNone(self.store.match("character:a"))

    async def test_match_tolerates_non_list_section(self):
        await self.store.create(
            {"picks": picks(character=("character:a", "A"), clothing=("clothing:b", "B"))}
        )
        self.assertIsNone(self.store.match({"character": 5, "clothing": "clothing:b"}))
        self.assertIsNotNone(
            self.store.match({"character": [{"id": "character:a"}], "clothing": [{"id": "clothing:b"}]})
        )

    async def test_create_failure_does_not_mutate_memory(self):
        """_write_text 失败时 create 必须抛错且内存状态不变(本模块头部不变量)。"""
        with patch.object(self.store, "_write_text", side_effect=OSError("磁盘已满")):
            with self.assertRaises(OSError):
                await self.store.create(
                    {"picks": picks(character=("character:a", "A"), clothing=("clothing:b", "B"))}
                )
        self.assertEqual(self.store.list()["count"], 0)
        self.assertFalse(self.path.exists())

    async def test_delete_failure_keeps_rule(self):
        item = await self.store.create(
            {"picks": picks(character=("character:a", "A"), clothing=("clothing:b", "B"))}
        )
        with patch.object(self.store, "_write_text", side_effect=OSError("磁盘已满")):
            with self.assertRaises(OSError):
                await self.store.delete(item["id"])
        self.assertEqual(self.store.list()["count"], 1)
        self.assertEqual(self.store.list()["items"][0]["id"], item["id"])

    async def test_clear_failure_keeps_rules(self):
        await self.store.create(
            {"picks": picks(character=("character:a", "A"), clothing=("clothing:b", "B"))}
        )
        with patch.object(self.store, "_write_text", side_effect=OSError("磁盘已满")):
            with self.assertRaises(OSError):
                await self.store.clear()
        self.assertEqual(self.store.list()["count"], 1)

    async def test_clear_persists_empty_file(self):
        await self.store.create(
            {"picks": picks(character=("character:a", "A"), clothing=("clothing:b", "B"))}
        )
        await self.store.clear()
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(payload["rules"], [])
