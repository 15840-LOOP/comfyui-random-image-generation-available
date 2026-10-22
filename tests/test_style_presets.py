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

    async def test_list_orders_by_updated_at_regardless_of_favorite(self):
        # 加星仅作分类标识,不再置顶:顺序完全由 updated_at 决定。
        favorite = await self.store.create(
            {"name": "Favorite", "favorite": True, "settings": snapshot(width=768)}
        )
        regular = await self.store.create(
            {"name": "Regular", "favorite": False, "settings": snapshot(width=832)}
        )
        self.assertEqual(
            [item["id"] for item in self.store.list()["items"]],
            [regular["id"], favorite["id"]],
        )

        updated = await self.store.update(
            regular["id"],
            {"name": "Renamed", "favorite": True, "settings": snapshot(width=1024)},
        )
        self.assertEqual(updated["name"], "Renamed")
        self.assertEqual(updated["settings"]["width"], 1024)
        self.assertTrue(updated["favorite"])
        self.assertEqual(updated["collection_ids"], [1])
        self.assertTrue(await self.store.delete(favorite["id"]))
        self.assertFalse(await self.store.delete("missing"))

    async def test_favorite_toggle_does_not_change_relative_order(self):
        first = await self.store.create({"name": "First", "settings": snapshot()})
        second = await self.store.create({"name": "Second", "settings": snapshot()})
        before = [item["id"] for item in self.store.list()["items"]]
        self.assertEqual(before, [second["id"], first["id"]])

        # 给较早的预设加星,它仍应排在后面。
        await self.store.toggle_default_favorite(first["id"])
        after = [item["id"] for item in self.store.list()["items"]]
        self.assertEqual(after, [second["id"], first["id"]])

    async def test_list_filters_by_collection_id(self):
        plain = await self.store.create({"name": "Plain", "settings": snapshot()})
        starred = await self.store.create({"name": "Starred", "settings": snapshot()})
        await self.store.toggle_default_favorite(starred["id"])

        filtered = self.store.list(collection_id=1)
        self.assertEqual([item["id"] for item in filtered["items"]], [starred["id"]])
        # count 始终为全库总数,不受过滤影响。
        self.assertEqual(filtered["count"], 2)
        self.assertEqual(len(self.store.list()["items"]), 2)
        self.assertEqual(self.store.list(collection_id=999)["items"], [])
        self.assertEqual(len(self.store.list(collection_id=0)["items"]), 2)
        self.assertIn(plain["id"], [item["id"] for item in self.store.list()["items"]])

    async def test_atomic_save_leaves_valid_json_without_temp_files(self):
        await self.store.create({"name": "Atomic", "settings": snapshot(), "favorite": False})
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        # 两级分类结构落盘版本号为 2。
        self.assertEqual(payload["version"], 2)
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

    def test_people_and_character_detail_fields_are_part_of_the_snapshot(self):
        # 回归:预设白名单必须包含人物构成与角色细节字段,
        # 否则保存/载入预设时几女几男与角色细节模式会被丢弃。
        for key in ("female_count", "male_count", "character_detail"):
            self.assertIn(key, PRESET_SETTING_KEYS)

    def test_people_and_character_detail_round_trip_through_preset_settings(self):
        settings = preset_settings(
            {
                "female_count": 2,
                "male_count": 1,
                "character_detail": "trigger_tags",
                "loras": [{"filename": "detail.safetensors", "enabled": True, "strength": 0.8}],
            }
        )
        self.assertEqual(settings["female_count"], 2)
        self.assertEqual(settings["male_count"], 1)
        self.assertEqual(settings["character_detail"], "trigger_tags")
        self.assertEqual(len(settings["loras"]), 1)
        self.assertEqual(settings["loras"][0]["filename"], "detail.safetensors")

    async def test_people_and_character_detail_persist_through_create_and_update(self):
        created = await self.store.create(
            {
                "name": "Duo",
                "favorite": False,
                "settings": snapshot(
                    female_count=2,
                    male_count=1,
                    character_detail="trigger_tags",
                    loras=[{"filename": "detail.safetensors", "enabled": True, "strength": 0.8}],
                ),
            }
        )
        self.assertEqual(created["settings"]["female_count"], 2)
        self.assertEqual(created["settings"]["male_count"], 1)
        self.assertEqual(created["settings"]["character_detail"], "trigger_tags")
        self.assertEqual(created["settings"]["loras"][0]["filename"], "detail.safetensors")

        updated = await self.store.update(
            created["id"],
            {
                "settings": snapshot(
                    female_count=1,
                    male_count=2,
                    character_detail="trigger",
                    loras=[],
                )
            },
        )
        self.assertEqual(updated["settings"]["female_count"], 1)
        self.assertEqual(updated["settings"]["male_count"], 2)
        self.assertEqual(updated["settings"]["character_detail"], "trigger")
        self.assertEqual(updated["settings"]["loras"], [])

    def test_legacy_snapshot_without_people_fields_receives_defaults(self):
        # 向下兼容:旧版 style_presets.json 缺少新字段时,reload() 应通过
        # DEFAULT_SETTINGS 自动补齐默认值,而不是判定为坏文件备份。
        payload = {
            "version": 1,
            "items": [
                {
                    "id": "preset_legacy",
                    "name": "Legacy",
                    "favorite": False,
                    "settings": {"width": 1024, "manual_artist": "anmi"},
                    "created_at": "2024-01-01T00:00:00+00:00",
                    "updated_at": "2024-01-01T00:00:00+00:00",
                }
            ],
        }
        self.path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        store = StylePresetStore(self.path)
        self.assertEqual(store.load_warnings, [])
        self.assertFalse(self.path.with_name("style_presets.json.corrupt.bak").exists())
        self.assertEqual(len(store.items), 1)
        settings = store.items[0]["settings"]
        self.assertEqual(settings["female_count"], DEFAULT_SETTINGS["female_count"])
        self.assertEqual(settings["male_count"], DEFAULT_SETTINGS["male_count"])
        self.assertEqual(settings["character_detail"], DEFAULT_SETTINGS["character_detail"])
        self.assertEqual(settings["width"], 1024)
        self.assertEqual(settings["manual_artist"], "@anmi")

    def test_runtime_count_field_is_ignored(self):
        # 前端可能直接提交完整工作台 state(含运行期批次字段 count),
        # 校验前应安全剔除,避免因 "count" 触发未知参数异常。
        settings = preset_settings({"count": 4, "width": 1024})
        self.assertEqual(settings["width"], 1024)
        self.assertNotIn("count", settings)

    async def test_runtime_count_field_is_ignored_on_create(self):
        created = await self.store.create(
            {"name": "WithCount", "favorite": False, "settings": {**snapshot(), "count": 4}}
        )
        self.assertNotIn("count", created["settings"])

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

    def test_thumbnail_dir_is_created_next_to_preset_file(self):
        # 缩略图目录应与预设 JSON 同级的 preset_thumbnails/。
        self.assertEqual(self.store.thumbnail_dir, self.path.parent / "preset_thumbnails")
        self.assertTrue(self.store.thumbnail_dir.is_dir())

    async def test_thumbnail_url_is_none_without_local_file(self):
        created = await self.store.create(
            {"name": "NoThumb", "settings": snapshot(), "favorite": False}
        )
        self.assertIsNone(created["thumbnail_url"])
        self.assertIsNone(self.store.thumbnail_url(created["id"]))

    async def test_save_thumbnail_writes_file_and_exposes_url(self):
        created = await self.store.create(
            {"name": "WithThumb", "settings": snapshot(), "favorite": False}
        )
        await self.store.save_thumbnail(created["id"], b"\x89PNG\r\n\x1a\nfake")
        thumb_path = self.store.thumbnail_dir / f"{created['id']}.png"
        self.assertTrue(thumb_path.is_file())
        self.assertEqual(thumb_path.read_bytes(), b"\x89PNG\r\n\x1a\nfake")
        self.assertEqual(
            self.store.thumbnail_url(created["id"]),
            f"/api/style-presets/{created['id']}/thumbnail",
        )
        # 重新归一化后应携带 thumbnail_url 字段。
        reloaded = StylePresetStore(self.path)
        item = next(entry for entry in reloaded.items if entry["id"] == created["id"])
        self.assertEqual(
            item["thumbnail_url"], f"/api/style-presets/{created['id']}/thumbnail"
        )

    async def test_delete_removes_thumbnail_file(self):
        created = await self.store.create(
            {"name": "Doomed", "settings": snapshot(), "favorite": False}
        )
        await self.store.save_thumbnail(created["id"], b"png-bytes")
        thumb_path = self.store.thumbnail_dir / f"{created['id']}.png"
        self.assertTrue(thumb_path.is_file())
        self.assertTrue(await self.store.delete(created["id"]))
        self.assertFalse(thumb_path.exists())

    async def test_save_thumbnail_leaves_no_temp_files(self):
        created = await self.store.create(
            {"name": "AtomicThumb", "settings": snapshot(), "favorite": False}
        )
        await self.store.save_thumbnail(created["id"], b"png-bytes")
        self.assertEqual(list(self.store.thumbnail_dir.glob("preset-thumb-*.png")), [])

    # ---------- 收藏夹(分类) ----------
    def test_default_collection_is_always_present(self):
        payload = self.store.list_collections()
        self.assertEqual(payload["all_total"], 0)
        self.assertEqual(
            payload["collections"],
            [
                {
                    "id": 1,
                    "name": "默认收藏",
                    "is_default": True,
                    "parent_id": None,
                    "count": 0,
                }
            ],
        )

    async def test_create_collection_assigns_incrementing_ids(self):
        first = await self.store.create_collection("风景")
        second = await self.store.create_collection("人物")
        self.assertEqual(first["id"], 2)
        self.assertEqual(second["id"], 3)
        self.assertFalse(first["is_default"])
        self.assertEqual([item["name"] for item in self.store.list_collections()["collections"]], ["默认收藏", "风景", "人物"])

    async def test_create_collection_validates_name(self):
        with self.assertRaisesRegex(WorkflowError, "不能为空"):
            await self.store.create_collection("   ")
        with self.assertRaisesRegex(WorkflowError, "100"):
            await self.store.create_collection("x" * 101)
        await self.store.create_collection("风景")
        with self.assertRaisesRegex(WorkflowError, "已存在"):
            await self.store.create_collection("风景")

    async def test_list_collections_counts_members(self):
        # 预设只能归入子文件夹,母文件夹计数为其下子文件夹的去重聚合数。
        parent = await self.store.create_collection("风景")
        collection = await self.store.create_collection("山景", parent_id=parent["id"])
        first = await self.store.create({"name": "A", "settings": snapshot()})
        second = await self.store.create({"name": "B", "settings": snapshot()})
        await self.store.set_preset_collections(first["id"], [collection["id"]])
        await self.store.set_preset_collections(second["id"], [1, collection["id"]])

        payload = self.store.list_collections()
        self.assertEqual(payload["all_total"], 2)
        counts = {item["id"]: item["count"] for item in payload["collections"]}
        self.assertEqual(counts[1], 1)
        self.assertEqual(counts[collection["id"]], 2)
        self.assertEqual(counts[parent["id"]], 2)

    async def test_delete_collection_unbinds_presets_without_deleting_them(self):
        parent = await self.store.create_collection("风景")
        collection = await self.store.create_collection("山景", parent_id=parent["id"])
        created = await self.store.create({"name": "Kept", "settings": snapshot()})
        await self.store.set_preset_collections(created["id"], [1, collection["id"]])

        # 删除子分类:返回级联信息,预设仅解绑该子分类。
        result = await self.store.delete_collection(collection["id"])
        self.assertTrue(result["deleted"])
        self.assertFalse(result["is_parent"])
        self.assertEqual(result["deleted_sub_ids"], [collection["id"]])
        # 预设本体必须保留,仅解绑被删除的分类。
        self.assertEqual(len(self.store.items), 1)
        item = self.store.items[0]
        self.assertEqual(item["collection_ids"], [1])
        self.assertTrue(item["favorite"])

        # 重复删除同一分类应抛出 KeyError(由路由层转为 404)。
        with self.assertRaises(KeyError):
            await self.store.delete_collection(collection["id"])

    async def test_default_collection_cannot_be_deleted(self):
        with self.assertRaisesRegex(WorkflowError, "默认收藏夹不能删除"):
            await self.store.delete_collection(1)
        self.assertEqual(len(self.store.collections), 1)

    async def test_toggle_default_favorite_round_trip(self):
        created = await self.store.create({"name": "Toggle", "settings": snapshot()})
        self.assertEqual(created["collection_ids"], [])
        self.assertFalse(created["favorite"])

        added = await self.store.toggle_default_favorite(created["id"])
        self.assertEqual(added, {"id": created["id"], "is_favorite": True, "collection_ids": [1]})
        self.assertTrue(self.store.items[0]["favorite"])

        removed = await self.store.toggle_default_favorite(created["id"])
        self.assertEqual(removed, {"id": created["id"], "is_favorite": False, "collection_ids": []})
        self.assertFalse(self.store.items[0]["favorite"])

        with self.assertRaises(KeyError):
            await self.store.toggle_default_favorite("missing")

    async def test_set_preset_collections_syncs_favorite_flag(self):
        parent = await self.store.create_collection("风景")
        collection = await self.store.create_collection("山景", parent_id=parent["id"])
        created = await self.store.create({"name": "Sync", "settings": snapshot()})

        updated = await self.store.set_preset_collections(created["id"], [collection["id"]])
        self.assertEqual(updated["collection_ids"], [collection["id"]])
        self.assertFalse(updated["favorite"])

        updated = await self.store.set_preset_collections(created["id"], [1, collection["id"]])
        self.assertEqual(updated["collection_ids"], [1, collection["id"]])
        self.assertTrue(updated["favorite"])

        with self.assertRaisesRegex(WorkflowError, "所选分类不存在或为母文件夹"):
            await self.store.set_preset_collections(created["id"], [999])
        # 母文件夹不能直接作为预设归属。
        with self.assertRaisesRegex(WorkflowError, "所选分类不存在或为母文件夹"):
            await self.store.set_preset_collections(created["id"], [parent["id"]])
        with self.assertRaises(KeyError):
            await self.store.set_preset_collections("missing", [])

    async def test_collections_persist_and_reload(self):
        parent = await self.store.create_collection("风景")
        collection = await self.store.create_collection("山景", parent_id=parent["id"])
        created = await self.store.create({"name": "Persisted", "settings": snapshot()})
        await self.store.set_preset_collections(created["id"], [collection["id"]])

        payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(payload["collections"][0]["id"], 1)
        self.assertEqual(payload["collections"][1]["name"], "风景")
        self.assertIsNone(payload["collections"][1]["parent_id"])
        self.assertEqual(payload["collections"][2]["parent_id"], parent["id"])

        reloaded = StylePresetStore(self.path)
        self.assertEqual(
            [item["id"] for item in reloaded.collections],
            [1, parent["id"], collection["id"]],
        )
        item = next(entry for entry in reloaded.items if entry["id"] == created["id"])
        self.assertEqual(item["collection_ids"], [collection["id"]])

    def test_legacy_favorite_without_collections_gains_default_collection(self):
        # 老版本只有 favorite=True,加载后应自动获得 collection_ids=[1]。
        payload = {
            "version": 1,
            "items": [
                {
                    "id": "preset_old_fav",
                    "name": "OldFav",
                    "favorite": True,
                    "settings": {"width": 1024},
                    "created_at": "2024-01-01T00:00:00+00:00",
                    "updated_at": "2024-01-01T00:00:00+00:00",
                },
                {
                    "id": "preset_old_plain",
                    "name": "OldPlain",
                    "favorite": False,
                    "settings": {"width": 1024},
                    "created_at": "2024-01-02T00:00:00+00:00",
                    "updated_at": "2024-01-02T00:00:00+00:00",
                },
            ],
        }
        self.path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        store = StylePresetStore(self.path)
        self.assertEqual(store.load_warnings, [])
        by_id = {item["id"]: item for item in store.items}
        self.assertEqual(by_id["preset_old_fav"]["collection_ids"], [1])
        self.assertTrue(by_id["preset_old_fav"]["favorite"])
        self.assertEqual(by_id["preset_old_plain"]["collection_ids"], [])
        self.assertFalse(by_id["preset_old_plain"]["favorite"])
        # 老文件缺少根级 collections 时自动补默认收藏夹。
        self.assertEqual(
            store.collections,
            [
                {
                    "id": 1,
                    "name": "默认收藏",
                    "is_default": True,
                    "parent_id": None,
                }
            ],
        )

    def test_collection_ids_containing_default_implies_favorite(self):
        payload = {
            "version": 1,
            "collections": [{"id": 1, "name": "默认收藏", "is_default": True}],
            "items": [
                {
                    "id": "preset_ids_only",
                    "name": "IdsOnly",
                    "favorite": False,
                    "collection_ids": [1],
                    "settings": {"width": 1024},
                    "created_at": "2024-01-01T00:00:00+00:00",
                    "updated_at": "2024-01-01T00:00:00+00:00",
                }
            ],
        }
        self.path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        store = StylePresetStore(self.path)
        self.assertTrue(store.items[0]["favorite"])
        self.assertEqual(store.items[0]["collection_ids"], [1])

    async def test_update_with_favorite_only_overrides_collections(self):
        created = await self.store.create({"name": "Flip", "favorite": True, "settings": snapshot()})
        self.assertEqual(created["collection_ids"], [1])
        updated = await self.store.update(created["id"], {"favorite": False})
        self.assertEqual(updated["collection_ids"], [])
        self.assertFalse(updated["favorite"])

    async def test_delete_batch_removes_records_and_thumbnails(self):
        first = await self.store.create({"name": "BatchA", "settings": snapshot()})
        second = await self.store.create({"name": "BatchB", "settings": snapshot()})
        keep = await self.store.create({"name": "Keep", "settings": snapshot()})
        await self.store.save_thumbnail(first["id"], b"\x89PNG\r\n\x1a\nA")
        await self.store.save_thumbnail(second["id"], b"\x89PNG\r\n\x1a\nB")
        await self.store.save_thumbnail(keep["id"], b"\x89PNG\r\n\x1a\nK")

        # 重复 ID 与不存在的 ID 都应被静默忽略,保证接口幂等。
        deleted = await self.store.delete_batch(
            [first["id"], second["id"], first["id"], "missing"]
        )
        self.assertEqual(deleted, 2)
        self.assertEqual([item["id"] for item in self.store.items], [keep["id"]])
        self.assertFalse((self.store.thumbnail_dir / f"{first['id']}.png").exists())
        self.assertFalse((self.store.thumbnail_dir / f"{second['id']}.png").exists())
        self.assertTrue((self.store.thumbnail_dir / f"{keep['id']}.png").exists())

        # 落盘后重新加载,删除结果应持久化。
        reloaded = StylePresetStore(self.path)
        self.assertEqual([item["id"] for item in reloaded.items], [keep["id"]])

        # 空列表与全不存在时返回 0,且不产生额外写盘。
        self.assertEqual(await self.store.delete_batch([]), 0)
        self.assertEqual(await self.store.delete_batch(["missing"]), 0)

    async def test_batch_update_collections_add_remove_set(self):
        landscape_parent = await self.store.create_collection("风景")
        landscape = await self.store.create_collection(
            "山景", parent_id=landscape_parent["id"]
        )
        portrait_parent = await self.store.create_collection("人像")
        portrait = await self.store.create_collection(
            "半身", parent_id=portrait_parent["id"]
        )
        first = await self.store.create({"name": "BatchOne", "settings": snapshot()})
        second = await self.store.create({"name": "BatchTwo", "settings": snapshot()})

        added = await self.store.batch_update_collections(
            [first["id"], second["id"]], [landscape["id"]], "add"
        )
        self.assertEqual(sorted(added), sorted([first["id"], second["id"]]))
        by_id = {item["id"]: item for item in self.store.items}
        self.assertEqual(by_id[first["id"]]["collection_ids"], [landscape["id"]])
        self.assertFalse(by_id[first["id"]]["favorite"])

        # add 模式应幂等,重复添加不会产生重复 ID。
        await self.store.batch_update_collections([first["id"]], [landscape["id"]], "add")
        by_id = {item["id"]: item for item in self.store.items}
        self.assertEqual(by_id[first["id"]]["collection_ids"], [landscape["id"]])

        # set 模式覆盖为默认收藏夹,应同步点亮 favorite。
        await self.store.batch_update_collections([first["id"]], [1], "set")
        by_id = {item["id"]: item for item in self.store.items}
        self.assertEqual(by_id[first["id"]]["collection_ids"], [1])
        self.assertTrue(by_id[first["id"]]["favorite"])

        # remove 模式移除默认收藏夹,应同步熄灭 favorite。
        await self.store.batch_update_collections([first["id"]], [1], "remove")
        by_id = {item["id"]: item for item in self.store.items}
        self.assertEqual(by_id[first["id"]]["collection_ids"], [])
        self.assertFalse(by_id[first["id"]]["favorite"])

        # 非法 mode 与非法分类 ID 的处理。
        with self.assertRaisesRegex(WorkflowError, "mode"):
            await self.store.batch_update_collections([first["id"]], [1], "toggle")
        await self.store.batch_update_collections([second["id"]], [999, True, "x"], "add")
        by_id = {item["id"]: item for item in self.store.items}
        self.assertEqual(by_id[second["id"]]["collection_ids"], [landscape["id"]])

        # 不存在的预设 ID 不应报错,返回空列表。
        self.assertEqual(
            await self.store.batch_update_collections(["missing"], [portrait["id"]], "add"),
            [],
        )


if __name__ == "__main__":
    unittest.main()
