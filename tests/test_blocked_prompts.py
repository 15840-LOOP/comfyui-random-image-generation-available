"""预设屏蔽池(隔离池)功能测试。

覆盖:
- 存储层自动初始化 / 原子保存 / 切换与快照
- catalog.search 的屏蔽过滤与隔离池视图
- catalog 抽取阶段的底层防御
- 服务端 REST API 与分页无空洞
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

from aiohttp.test_utils import TestClient, TestServer


APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from anima_webui.blocked_prompts import SECTIONS, BlockedPromptStore  # noqa: E402
from anima_webui.catalog import PromptCatalog  # noqa: E402
from anima_webui.server import create_app  # noqa: E402


def _write_fake_tools(root: Path) -> Path:
    """构造最小可用的 Anima 工具目录(仅服装池,便于断言)。"""
    tools = root / "tools"
    js = tools / "js"
    js.mkdir(parents=True, exist_ok=True)
    clothing = [
        {
            "id": f"item{i}",
            "name": f"Item {i}",
            "name_zh": f"服装{i}",
            "tags": f"tag{i}",
            "categories": ["日常/休闲 (Casual & Daily)"],
            "traits": [f"trait{i}"],
        }
        for i in range(6)
    ]
    (js / "clothing_data.js").write_text(
        f"const data = {json.dumps(clothing)};\n", encoding="utf-8"
    )
    for filename in ("character_data.js", "pose_data.js", "background_data.js"):
        (js / filename).write_text("const data = [];\n", encoding="utf-8")
    return tools


class BlockedPromptStoreTests(unittest.TestCase):
    def test_auto_creates_file_and_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "data" / "blocked_prompts.json"
            self.assertFalse(path.parent.exists())
            store = BlockedPromptStore(path)
            self.assertTrue(path.is_file())
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(set(payload), set(SECTIONS))
            self.assertTrue(all(value == [] for value in payload.values()))
            self.assertEqual(store.load_warnings, [])

    def test_toggle_persists_and_snapshot_sorted(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "blocked_prompts.json"
            store = BlockedPromptStore(path)
            self.assertFalse(store.is_blocked("clothing", "b"))
            self.assertTrue(store._run_toggle("clothing", "b"))
            self.assertTrue(store._run_toggle("clothing", "a"))
            self.assertEqual(store.snapshot()["clothing"], ["a", "b"])
            reloaded = BlockedPromptStore(path)
            self.assertEqual(reloaded.get_blocked_ids("clothing"), {"a", "b"})
            self.assertFalse(reloaded._run_toggle("clothing", "a"))
            self.assertEqual(reloaded.get_blocked_ids("clothing"), {"b"})

    def test_corrupt_file_degrades_with_warning(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "blocked_prompts.json"
            path.write_text("{not json", encoding="utf-8")
            store = BlockedPromptStore(path)
            self.assertTrue(store.load_warnings)
            self.assertEqual(store.get_blocked_ids("clothing"), set())

    def test_empty_file_is_reinitialized(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "blocked_prompts.json"
            path.write_text("   ", encoding="utf-8")
            BlockedPromptStore(path)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(set(payload), set(SECTIONS))


class BlockedCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.catalog = PromptCatalog(root, _write_fake_tools(root))

    def tearDown(self):
        self.temp.cleanup()

    def test_search_excludes_blocked_items(self):
        result = self.catalog.search(
            "clothing", blocked_ids={"clothing:item1", "clothing:item2"}
        )
        ids = {item["id"] for item in result["items"]}
        self.assertNotIn("clothing:item1", ids)
        self.assertNotIn("clothing:item2", ids)
        self.assertEqual(result["total"], 4)

    def test_search_blocked_only_returns_isolated_items(self):
        result = self.catalog.search(
            "clothing",
            blocked_ids={"clothing:item1", "clothing:item2"},
            blocked_only=True,
        )
        ids = {item["id"] for item in result["items"]}
        self.assertEqual(ids, {"clothing:item1", "clothing:item2"})
        self.assertEqual(result["total"], 2)

    def test_pagination_has_no_holes(self):
        blocked = {"clothing:item0"}
        first = self.catalog.search("clothing", blocked_ids=blocked, page=1, limit=2)
        second = self.catalog.search("clothing", blocked_ids=blocked, page=2, limit=2)
        seen = [item["id"] for item in first["items"] + second["items"]]
        self.assertNotIn("clothing:item0", seen)
        self.assertEqual(len(seen), len(set(seen)))
        self.assertEqual(first["total"], 5)

    def test_selection_candidates_drop_blocked_ids(self):
        selection = {
            "mode": "include",
            "ids": ["clothing:item0", "clothing:item1", "clothing:item2"],
        }
        candidates = self.catalog._selection_candidates(
            "clothing", selection, {"clothing:item1"}
        )
        self.assertEqual(
            [item["id"] for item in candidates],
            ["clothing:item0", "clothing:item2"],
        )

    def test_selection_all_mode_excludes_blocked(self):
        selection = {"mode": "all", "ids": [], "excluded_ids": []}
        candidates = self.catalog._selection_candidates(
            "clothing", selection, {"clothing:item3"}
        )
        self.assertNotIn("clothing:item3", {item["id"] for item in candidates})
        self.assertEqual(len(candidates), 5)

    def test_resolve_prompt_never_picks_blocked(self):
        settings = {
            "random_clothing": True,
            "random_clothing_count": 1,
            "pools": {"clothing": {"mode": "all", "ids": [], "excluded_ids": []}},
        }
        blocked = {
            "clothing": {
                "clothing:item0",
                "clothing:item1",
                "clothing:item2",
                "clothing:item3",
                "clothing:item4",
            }
        }
        for seed in range(20):
            resolved = self.catalog.resolve_prompt(settings, seed, blocked)
            picked = {item["id"] for item in resolved["selected"]["clothing"]}
            self.assertEqual(picked, {"clothing:item5"})


class BlockedApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.blocked_path = root / "blocked_prompts.json"
        app = create_app(
            app_dir=APP_DIR,
            history_path=root / "history.sqlite3",
            custom_prompts_path=root / "custom_prompts.json",
            style_presets_path=root / "style_presets.json",
            lora_trigger_overrides_path=root / "lora_trigger_overrides.json",
            prompt_replacements_path=root / "prompt_replacements.json",
            blocked_prompts_path=self.blocked_path,
            anima_tools_dir=_write_fake_tools(root),
        )
        self.client = TestClient(TestServer(app))
        await self.client.start_server()

    async def asyncTearDown(self):
        await self.client.close()
        self.temp.cleanup()

    async def test_blocked_file_auto_created_on_startup(self):
        self.assertTrue(self.blocked_path.is_file())
        payload = json.loads(self.blocked_path.read_text(encoding="utf-8"))
        self.assertEqual(set(payload), set(SECTIONS))

    async def test_get_blocked_prompts_returns_empty_structure(self):
        response = await self.client.get("/api/blocked-prompts")
        self.assertEqual(response.status, 200)
        payload = await response.json()
        self.assertEqual(set(payload), set(SECTIONS))
        self.assertTrue(all(value == [] for value in payload.values()))

    async def test_toggle_and_pool_filtering(self):
        response = await self.client.post(
            "/api/blocked-prompts/clothing/toggle", json={"id": "clothing:item0"}
        )
        self.assertEqual(response.status, 200)
        payload = await response.json()
        self.assertTrue(payload["blocked"])
        self.assertEqual(payload["blocked_count"], 1)

        # 正常视图:被屏蔽项从源头消失,分页总数同步减少。
        normal = await (await self.client.get("/api/pools/clothing?limit=48")).json()
        self.assertNotIn("clothing:item0", {item["id"] for item in normal["items"]})
        self.assertEqual(normal["total"], 5)
        self.assertEqual(normal["blocked_count"], 1)

        # 隔离池视图:只返回被屏蔽项。
        vault = await (
            await self.client.get("/api/pools/clothing?blocked_only=1&limit=48")
        ).json()
        self.assertEqual({item["id"] for item in vault["items"]}, {"clothing:item0"})

        # 再次切换即恢复。
        restored = await (
            await self.client.post(
                "/api/blocked-prompts/clothing/toggle", json={"id": "clothing:item0"}
            )
        ).json()
        self.assertFalse(restored["blocked"])
        self.assertEqual(restored["blocked_count"], 0)

    async def test_toggle_rejects_unknown_section_and_empty_id(self):
        bad_section = await self.client.post(
            "/api/blocked-prompts/unknown/toggle", json={"id": "x"}
        )
        self.assertEqual(bad_section.status, 400)
        empty_id = await self.client.post(
            "/api/blocked-prompts/clothing/toggle", json={"id": ""}
        )
        self.assertEqual(empty_id.status, 400)

    async def test_pool_query_post_supports_blocked_only(self):
        await self.client.post(
            "/api/blocked-prompts/clothing/toggle", json={"id": "clothing:item2"}
        )
        response = await self.client.post(
            "/api/pools/clothing/query", json={"blocked_only": "1", "limit": 48}
        )
        payload = await response.json()
        self.assertEqual(
            {item["id"] for item in payload["items"]}, {"clothing:item2"}
        )


if __name__ == "__main__":
    unittest.main()
