import asyncio
import copy
import json
import os
import tempfile
import unittest
from unittest import mock
from pathlib import Path
import sys

import aiohttp
from aiohttp.test_utils import TestClient, TestServer


APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from anima_webui.server import COMFY_KEY, HISTORY_KEY, MANAGER_KEY, create_app  # noqa: E402
from anima_webui.workflow import DEFAULT_SETTINGS  # noqa: E402


# 测试必须密闭:池数据来自 tempdir 里的假 Anima Tools 目录,
# 不依赖本机 ComfyUI 安装,也不吸入真实词库(回归 #P1-5)。
FAKE_TOOLS_DATASETS = {
    "character_data.js": [
        {"name": "alpha", "copyright": "series", "gender": "1girl", "hair": "blue", "eye": "red", "post_count": 5},
    ],
    "clothing_data.js": [
        {"id": "coat", "name": "Coat", "name_zh": "外套", "tags": "red coat", "categories": ["日常/休闲 (Casual & Daily)"], "traits": ["red"]},
    ],
    "pose_data.js": [
        {"id": "stand", "name": "Standing", "name_zh": "站立", "tags": "standing", "categories": ["站立与动态 (Standing & Dynamic)"], "traits": ["standing"]},
        {"id": "sit", "name": "Sitting", "name_zh": "坐姿", "tags": "sitting", "categories": ["坐姿 (Sitting Poses)"], "traits": ["sitting"]},
    ],
    "background_data.js": [
        {"id": "room", "name": "Room", "name_zh": "房间", "tags": "indoors", "categories": ["都市与日常 (Urban & Daily)"], "traits": ["indoor"]},
    ],
}


def _write_fake_tools(root: Path) -> Path:
    js = root / "tools" / "js"
    js.mkdir(parents=True)
    for filename, values in FAKE_TOOLS_DATASETS.items():
        (js / filename).write_text(
            f"const data = {json.dumps(values, ensure_ascii=False)};\n", encoding="utf-8"
        )
    return root / "tools"


class FakeComfy:
    base_url = "http://127.0.0.1:8188"

    def __init__(self):
        self.preview_items = []
        self.submissions = []
        self.favorites_data = {
            section: {"groups": [{"id": "default", "name": "Default Favorites", "isSystem": True}], "items": []}
            for section in ("artist", "character", "lora", "clothing", "background", "pose", "expression")
        }

    async def status(self):
        return {"system": {"comfyui_version": "test"}, "devices": [{"name": "GPU"}]}

    async def lora_inventory(self):
        if self.preview_items:
            return {"items": copy.deepcopy(self.preview_items), "count": len(self.preview_items)}
        items = [
            {
                "filename": item["filename"],
                "display_name": item["filename"].removesuffix(".safetensors"),
                "preview": "",
                "has_preview": False,
                "size": None,
            }
            for item in DEFAULT_SETTINGS["loras"]
        ]
        return {"items": items, "count": len(items)}

    async def lora_preview(self, filename):
        item = next((value for value in self.preview_items if value["filename"] == filename), None)
        if not item:
            raise KeyError(filename)
        return b"preview", "image/webp", "private, max-age=60"

    async def lora_filenames(self):
        return [item["filename"] for item in DEFAULT_SETTINGS["loras"]]

    async def resource_inventory(self):
        return {
            "models": [DEFAULT_SETTINGS["model_name"]],
            "upscale_models": [DEFAULT_SETTINGS["hires"]["model_name"]],
            "samplers": [DEFAULT_SETTINGS["sampler_name"], "euler"],
            "schedulers": [DEFAULT_SETTINGS["scheduler"], "karras"],
        }

    async def favorites(self):
        return copy.deepcopy(self.favorites_data)

    async def save_favorites(self, payload):
        for section, value in payload.items():
            self.favorites_data[section] = copy.deepcopy(value)
        return {"success": True}

    async def submit(self, payload):
        self.submissions.append(copy.deepcopy(payload))
        return "prompt-id"

    async def wait_for_history(self, prompt_id, should_abort=None, missing_timeout=30.0):
        return {
            "outputs": {"12": {"images": [{"filename": "test.png", "subfolder": "", "type": "output"}]}},
            "prompt": [0, prompt_id, {}, {"extra_pnginfo": {"anima_prompt": {"42": {"positive": "generated"}}}}],
        }

    async def image_bytes(self, image):
        return b"png", "image/png"

    async def close(self):
        return None


class ServerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self._saved_env = {
            name: os.environ.pop(name, None)
            for name in ("ANIMA_TOOLS_DIR", "COMFYUI_ANIMA_TOOLS")
        }
        self.comfy = FakeComfy()
        app = create_app(
            app_dir=APP_DIR,
            comfy=self.comfy,
            history_path=Path(self.temp.name) / "history.sqlite3",
            custom_prompts_path=Path(self.temp.name) / "custom_prompts.json",
            style_presets_path=Path(self.temp.name) / "style_presets.json",
            lora_trigger_overrides_path=Path(self.temp.name) / "lora_trigger_overrides.json",
            prompt_replacements_path=Path(self.temp.name) / "prompt_replacements.json",
            anima_tools_dir=_write_fake_tools(Path(self.temp.name)),
        )
        self.client = TestClient(TestServer(app))
        await self.client.start_server()

    async def asyncTearDown(self):
        await self.client.close()
        self.temp.cleanup()
        for name, value in self._saved_env.items():
            if value is not None:
                os.environ[name] = value

    async def test_index_and_status(self):
        response = await self.client.get("/")
        self.assertEqual(response.status, 200)
        index_html = await response.text()
        self.assertIn("Anima", index_html)
        self.assertIn(
            'id="hires_percent" type="number" min="1" max="1000" step="1" value="45" required',
            index_html,
        )
        self.assertIn("控制放大模型输出的最终缩放比例", index_html)
        self.assertEqual(
            response.headers["Cache-Control"], "no-cache, max-age=0, must-revalidate"
        )
        # 回归:预设库标签页控件必须随 HTML 一起下发,且 id 采用驼峰式,
        # 与 app.js 的 ui 映射键名严格一致,防止再次出现
        # 「缺少控件:btnCreatePreset/tabBtnGallery/...」的启动报错。
        for control_id in (
            "btnCreatePreset",
            "tabBtnGallery",
            "tabBtnPresets",
            "galleryCount",
            "presetsCount",
            "galleryViewContainer",
            "presetsViewContainer",
        ):
            self.assertIn(f'id="{control_id}"', index_html)
        static_response = await self.client.get("/static/app.js")
        app_js = await static_response.text()
        self.assertIn('"hires_percent"', app_js)
        self.assertIn("percent: Number(ui.hires_percent.value)", app_js)
        self.assertIn("function reconcileLoraTriggers", app_js)
        self.assertIn("lora_managed_triggers", app_js)
        self.assertIn("lora-catalog-preview", index_html + app_js)
        self.assertIn('id="loraTriggerDialog"', index_html)
        self.assertIn('id="promptRuleDialog"', index_html)
        self.assertIn('id="sampler_name"', index_html)
        self.assertIn('id="scheduler"', index_html)
        self.assertIn('id="cfg_zero_star"', index_html)
        self.assertIn('id="second_sampler_enabled"', index_html)
        self.assertIn('id="secondSamplerDrawer"', index_html)
        self.assertIn('id="second_sampler_denoise"', index_html)
        self.assertIn('sampler_name: ui.sampler_name.value', app_js)
        self.assertIn('scheduler: ui.scheduler.value', app_js)
        self.assertIn('cfg_zero_star: ui.cfg_zero_star.checked', app_js)
        self.assertIn('second_sampler:', app_js)
        self.assertIn("normalizePromptFields", app_js)
        self.assertIn('id="deleteGroupAll"', index_html)
        self.assertIn('value="exclusive"', index_html)
        self.assertIn("deleteMode=${deleteMode}", app_js)
        self.assertIn('id="favoriteSelection"', index_html)
        self.assertIn('id="favoriteSelectionDialog"', index_html)
        self.assertIn("/api/favorites/${activeSection}/selection", app_js)
        self.assertEqual(
            static_response.headers["Cache-Control"],
            "no-cache, max-age=0, must-revalidate",
        )
        status = await (await self.client.get("/api/status")).json()
        self.assertTrue(status["online"])
        self.assertEqual(status["device"], "GPU")

    async def test_lora_inventory(self):
        response = await self.client.get("/api/loras")
        self.assertEqual(response.status, 200)
        payload = await response.json()
        self.assertEqual(payload["count"], 0)
        self.assertEqual(
            [item["filename"] for item in payload["items"]],
            [item["filename"] for item in DEFAULT_SETTINGS["loras"]],
        )

    async def test_lora_inventory_uses_same_origin_preview_proxy(self):
        self.comfy.preview_items = [
            {
                "filename": "风格\\one.safetensors",
                "normalized_path": "风格/one.safetensors",
                "folder": "风格",
                "basename": "one.safetensors",
                "display_name": "One",
                "preview": "/api/lm/previews?path=secret",
                "has_preview": True,
                "trigger_words": ["@one"],
                "trigger_metadata_available": True,
                "metadata_source": "lora-manager",
                "size": 123,
            }
        ]
        payload = await (await self.client.get("/api/loras")).json()
        item = payload["items"][0]
        self.assertEqual(item["trigger_words"], ["@one"])
        self.assertEqual(item["source_trigger_words"], ["@one"])
        self.assertFalse(item["trigger_override"])
        self.assertNotIn("secret", item["preview"])
        self.assertTrue(item["preview"].startswith("/api/loras/preview?filename="))

        preview = await self.client.get(item["preview"])
        self.assertEqual(preview.status, 200)
        self.assertEqual(await preview.read(), b"preview")
        self.assertEqual(preview.headers["Content-Type"], "image/webp")
        self.assertEqual(preview.headers["Cache-Control"], "private, max-age=60")

        invalid = await self.client.get("/api/loras/preview?filename=../one.safetensors")
        self.assertEqual(invalid.status, 404)

    async def test_lora_trigger_override_can_be_edited_cleared_and_reset(self):
        self.comfy.preview_items = [
            {
                "filename": "风格/one.safetensors",
                "display_name": "One",
                "preview": "",
                "trigger_words": ["@One", "Second"],
                "trigger_metadata_available": True,
            }
        ]
        updated = await self.client.put(
            "/api/loras/triggers",
            json={"filename": "风格/one.safetensors", "triggerWords": [" @Exact_One ", "@exact_one"]},
        )
        self.assertEqual(updated.status, 200)
        payload = await updated.json()
        self.assertEqual(payload["source_trigger_words"], ["@One", "Second"])
        self.assertEqual(payload["trigger_words"], ["@Exact_One"])
        self.assertTrue(payload["trigger_override"])

        cleared = await self.client.put(
            "/api/loras/triggers",
            json={"filename": "风格/one.safetensors", "triggerWords": []},
        )
        self.assertEqual((await cleared.json())["trigger_words"], [])
        listing = await (await self.client.get("/api/loras")).json()
        self.assertEqual(listing["items"][0]["trigger_words"], [])
        self.assertTrue(listing["items"][0]["trigger_override"])
        self.assertTrue(Path(self.temp.name, "lora_trigger_overrides.json").is_file())

        reset = await self.client.delete(
            "/api/loras/triggers?filename=%E9%A3%8E%E6%A0%BC%2Fone.safetensors"
        )
        self.assertEqual(reset.status, 200)
        reset_payload = await reset.json()
        self.assertEqual(reset_payload["trigger_words"], ["@One", "Second"])
        self.assertFalse(reset_payload["trigger_override"])

    async def test_prompt_normalization_and_rule_crud(self):
        normalized = await self.client.post(
            "/api/prompts/normalize",
            json={
                "fields": {
                    "quality_prompt": "2025，SCORE 9, Blue_Hair",
                    "extra_prompt": "@Niji9il, Blue_Hair",
                },
                "managedTriggers": ["@Niji9il"],
            },
        )
        self.assertEqual(normalized.status, 200)
        payload = await normalized.json()
        self.assertEqual(payload["fields"]["quality_prompt"], "year 2025, score_9, blue hair")
        self.assertEqual(payload["fields"]["extra_prompt"], "@Niji9il, blue hair")

        created = await self.client.post(
            "/api/prompt-rules",
            json={"from": "wrong_tag", "to": "Right_Tag", "scopes": ["positive"], "enabled": True},
        )
        self.assertEqual(created.status, 201)
        item = await created.json()
        custom = await self.client.post(
            "/api/prompts/normalize",
            json={"fields": {"extra_prompt": "WRONG_TAG"}},
        )
        self.assertEqual((await custom.json())["fields"]["extra_prompt"], "right tag")

        disabled = await self.client.put(
            "/api/prompt-rules/lowercase-tags", json={"enabled": False}
        )
        self.assertEqual(disabled.status, 200)
        listing = await (await self.client.get("/api/prompt-rules")).json()
        self.assertFalse(next(rule for rule in listing["items"] if rule["id"] == "lowercase-tags")["enabled"])
        deleted = await self.client.delete(f"/api/prompt-rules/{item['id']}")
        self.assertEqual(deleted.status, 200)
        self.assertTrue(Path(self.temp.name, "prompt_replacements.json").is_file())

    async def test_config_has_empty_default_loras(self):
        payload = await (await self.client.get("/api/config")).json()
        self.assertEqual(payload["defaults"]["loras"], [])
        self.assertFalse(payload["defaults"]["cfg_zero_star"])
        self.assertEqual(payload["defaults"]["second_sampler"]["steps"], 16)
        self.assertFalse(payload["defaults"]["second_sampler"]["enabled"])

    async def test_resources_and_style_preset_crud(self):
        resources = await (await self.client.get("/api/resources")).json()
        self.assertEqual(resources["models"], [DEFAULT_SETTINGS["model_name"]])
        self.assertEqual(resources["samplers"], [DEFAULT_SETTINGS["sampler_name"], "euler"])
        self.assertEqual(resources["schedulers"], [DEFAULT_SETTINGS["scheduler"], "karras"])
        snapshot = {
            key: copy.deepcopy(DEFAULT_SETTINGS[key])
            for key in ("model_name", "loras", "lora_managed_triggers", "hires", "detailers", "manual_artist", "quality_prompt", "extra_prompt", "negative_prompt", "width", "height", "steps", "cfg", "sampler_name", "scheduler")
        }
        snapshot["quality_prompt"] = "2025, Blue_Hair"
        created = await self.client.post(
            "/api/style-presets",
            json={"name": "Soft", "favorite": False, "settings": snapshot},
        )
        self.assertEqual(created.status, 201)
        item = await created.json()
        self.assertEqual(item["settings"]["quality_prompt"], "year 2025, blue hair")
        updated = await self.client.put(
            f"/api/style-presets/{item['id']}", json={"favorite": True, "name": "Soft Light"}
        )
        self.assertEqual(updated.status, 200)
        self.assertTrue((await updated.json())["favorite"])
        listing = await (await self.client.get("/api/style-presets")).json()
        self.assertEqual(listing["items"][0]["name"], "Soft Light")
        self.assertTrue(Path(self.temp.name, "style_presets.json").is_file())
        deleted = await self.client.delete(f"/api/style-presets/{item['id']}")
        self.assertEqual(deleted.status, 200)
        self.assertEqual((await (await self.client.get("/api/style-presets")).json())["count"], 0)

    async def test_style_preset_thumbnail_upload_and_serving(self):
        snapshot = {
            key: copy.deepcopy(DEFAULT_SETTINGS[key])
            for key in ("model_name", "loras", "lora_managed_triggers", "hires", "detailers", "manual_artist", "quality_prompt", "extra_prompt", "negative_prompt", "width", "height", "steps", "cfg", "sampler_name", "scheduler")
        }
        created = await self.client.post(
            "/api/style-presets",
            json={"name": "Thumbed", "favorite": False, "settings": snapshot},
        )
        self.assertEqual(created.status, 201)
        item = await created.json()
        self.assertIsNone(item["thumbnail_url"])

        # 未上传缩略图时,资源路由应返回 404。
        missing = await self.client.get(f"/api/style-presets/{item['id']}/thumbnail")
        self.assertEqual(missing.status, 404)

        # 通过 multipart 上传缩略图。
        form = aiohttp.FormData()
        form.add_field("thumbnail", b"\x89PNG\r\n\x1a\nbytes", filename="cover.png", content_type="image/png")
        uploaded = await self.client.put(
            f"/api/style-presets/{item['id']}", data=form
        )
        self.assertEqual(uploaded.status, 200)
        updated = await uploaded.json()
        self.assertEqual(
            updated["thumbnail_url"], f"/api/style-presets/{item['id']}/thumbnail"
        )

        served = await self.client.get(f"/api/style-presets/{item['id']}/thumbnail")
        self.assertEqual(served.status, 200)
        self.assertEqual(await served.read(), b"\x89PNG\r\n\x1a\nbytes")

        # 列表接口应携带 thumbnail_url。
        listing = await (await self.client.get("/api/style-presets")).json()
        self.assertEqual(
            listing["items"][0]["thumbnail_url"],
            f"/api/style-presets/{item['id']}/thumbnail",
        )

        # 删除预设应同时移除缩略图文件。
        await self.client.delete(f"/api/style-presets/{item['id']}")
        gone = await self.client.get(f"/api/style-presets/{item['id']}/thumbnail")
        self.assertEqual(gone.status, 404)

    async def test_style_preset_thumbnail_from_source_image_id(self):
        snapshot = {
            key: copy.deepcopy(DEFAULT_SETTINGS[key])
            for key in ("model_name", "loras", "lora_managed_triggers", "hires", "detailers", "manual_artist", "quality_prompt", "extra_prompt", "negative_prompt", "width", "height", "steps", "cfg", "sampler_name", "scheduler")
        }
        # 先跑一个批次,让历史库里有可引用的图片。
        started = await self.client.post(
            "/api/batches", json={**snapshot, "count": 1}
        )
        self.assertEqual(started.status, 201)
        history = await (await self.client.get("/api/history")).json()
        image_id = history["items"][0]["id"]

        created = await self.client.post(
            "/api/style-presets",
            json={
                "name": "FromHistory",
                "favorite": False,
                "settings": snapshot,
                "source_image_id": image_id,
            },
        )
        self.assertEqual(created.status, 201)
        item = await created.json()
        self.assertEqual(
            item["thumbnail_url"], f"/api/style-presets/{item['id']}/thumbnail"
        )
        served = await self.client.get(f"/api/style-presets/{item['id']}/thumbnail")
        self.assertEqual(served.status, 200)

    async def test_style_preset_batch_delete_and_collections(self):
        snapshot = {
            key: copy.deepcopy(DEFAULT_SETTINGS[key])
            for key in ("model_name", "loras", "lora_managed_triggers", "hires", "detailers", "manual_artist", "quality_prompt", "extra_prompt", "negative_prompt", "width", "height", "steps", "cfg", "sampler_name", "scheduler")
        }
        ids = []
        for name in ("BatchA", "BatchB", "BatchC"):
            created = await self.client.post(
                "/api/style-presets",
                json={"name": name, "favorite": False, "settings": snapshot},
            )
            self.assertEqual(created.status, 201)
            ids.append((await created.json())["id"])

        # 批量分类:add 模式挂到新建收藏夹。
        collection = await self.client.post(
            "/api/style-presets/collections", json={"name": "批量测试"}
        )
        self.assertEqual(collection.status, 201)
        collection_id = (await collection.json())["id"]

        added = await self.client.post(
            "/api/style-presets/batch-collections",
            json={"preset_ids": ids[:2], "collection_ids": [collection_id], "mode": "add"},
        )
        self.assertEqual(added.status, 200)
        added_payload = await added.json()
        self.assertEqual(added_payload["mode"], "add")
        self.assertEqual(added_payload["updated_count"], 2)

        listing = await (await self.client.get("/api/style-presets")).json()
        by_id = {item["id"]: item for item in listing["items"]}
        self.assertEqual(by_id[ids[0]]["collection_ids"], [collection_id])
        self.assertEqual(by_id[ids[2]]["collection_ids"], [])

        # set 模式覆盖为默认收藏夹,应同步 favorite。
        await self.client.post(
            "/api/style-presets/batch-collections",
            json={"preset_ids": [ids[0]], "collection_ids": [1], "mode": "set"},
        )
        listing = await (await self.client.get("/api/style-presets")).json()
        by_id = {item["id"]: item for item in listing["items"]}
        self.assertTrue(by_id[ids[0]]["favorite"])
        self.assertEqual(by_id[ids[0]]["collection_ids"], [1])

        # 参数校验:空数组、非法 mode、非数组 collection_ids 均返回 400。
        empty = await self.client.post(
            "/api/style-presets/batch-collections",
            json={"preset_ids": [], "collection_ids": [1], "mode": "add"},
        )
        self.assertEqual(empty.status, 400)
        bad_mode = await self.client.post(
            "/api/style-presets/batch-collections",
            json={"preset_ids": [ids[0]], "collection_ids": [1], "mode": "toggle"},
        )
        self.assertEqual(bad_mode.status, 400)
        bad_ids = await self.client.post(
            "/api/style-presets/batch-collections",
            json={"preset_ids": [ids[0]], "collection_ids": "1", "mode": "add"},
        )
        self.assertEqual(bad_ids.status, 400)

        # 批量删除:静态段路由必须命中批量端点,而不是被 {preset_id} 吞掉。
        deleted = await self.client.post(
            "/api/style-presets/batch-delete",
            json={"preset_ids": [ids[0], ids[1], "missing"]},
        )
        self.assertEqual(deleted.status, 200)
        deleted_payload = await deleted.json()
        self.assertEqual(deleted_payload["deleted"], 2)
        self.assertEqual(deleted_payload["requested"], 3)

        listing = await (await self.client.get("/api/style-presets")).json()
        self.assertEqual([item["id"] for item in listing["items"]], [ids[2]])

        empty_delete = await self.client.post(
            "/api/style-presets/batch-delete", json={"preset_ids": []}
        )
        self.assertEqual(empty_delete.status, 400)

    async def test_style_preset_thumbnail_rejects_unknown_source_image(self):
        snapshot = {
            key: copy.deepcopy(DEFAULT_SETTINGS[key])
            for key in ("model_name", "loras", "lora_managed_triggers", "hires", "detailers", "manual_artist", "quality_prompt", "extra_prompt", "negative_prompt", "width", "height", "steps", "cfg", "sampler_name", "scheduler")
        }
        response = await self.client.post(
            "/api/style-presets",
            json={
                "name": "BadSource",
                "favorite": False,
                "settings": snapshot,
                "source_image_id": 999999,
            },
        )
        self.assertEqual(response.status, 400)

    async def test_favorite_crud_preserves_other_sections(self):
        pool = await (await self.client.get("/api/pools/pose?page=1&limit=1")).json()
        item_id = pool["items"][0]["id"]
        created = await self.client.post("/api/favorites/pose/groups", json={"name": "Test Group"})
        self.assertEqual(created.status, 201)
        group_id = (await created.json())["group"]["id"]
        saved = await self.client.put(
            "/api/favorites/pose/item",
            json={"id": item_id, "favorite": True, "groupIds": [group_id], "nickname": "memo"},
        )
        self.assertEqual(saved.status, 200)
        payload = await saved.json()
        self.assertEqual(payload["items"][0]["nickname"], "memo")
        self.assertIn(group_id, payload["items"][0]["groupIds"])
        self.assertEqual(self.client.server.app[COMFY_KEY].favorites_data["character"]["items"], [])

        deleted = await self.client.delete(f"/api/favorites/pose/groups/{group_id}")
        self.assertEqual(deleted.status, 200)
        payload = await deleted.json()
        self.assertEqual(len(payload["items"]), 1)
        self.assertEqual(payload["items"][0]["groupIds"], ["default"])

    async def test_batch_favorite_selection_api_appends_groups_and_preserves_nickname(self):
        pose = await (await self.client.get("/api/pools/pose?page=1&limit=2")).json()
        first_id, second_id = [item["id"] for item in pose["items"]]
        first_group = await self.client.post("/api/favorites/pose/groups", json={"name": "First"})
        first_group_id = (await first_group.json())["group"]["id"]
        second_group = await self.client.post("/api/favorites/pose/groups", json={"name": "Second"})
        second_group_id = (await second_group.json())["group"]["id"]
        saved = await self.client.put(
            "/api/favorites/pose/item",
            json={"id": first_id, "favorite": True, "groupIds": [first_group_id], "nickname": "memo"},
        )
        self.assertEqual(saved.status, 200)

        response = await self.client.post(
            "/api/favorites/pose/selection",
            json={
                "selection": {"mode": "include", "ids": [first_id, second_id, first_id], "excluded_ids": []},
                "groupIds": [second_group_id],
            },
        )
        self.assertEqual(response.status, 200)
        payload = await response.json()
        self.assertEqual(payload["selectedCount"], 2)
        self.assertEqual(payload["createdCount"], 1)
        self.assertEqual(payload["updatedCount"], 1)
        by_id = {item["id"]: item for item in payload["items"]}
        first_key = first_id.split(":", 1)[-1]
        second_key = second_id.split(":", 1)[-1]
        self.assertEqual(by_id[first_key]["groupIds"], [first_group_id, second_group_id])
        self.assertEqual(by_id[first_key]["nickname"], "memo")
        self.assertEqual(by_id[second_key]["groupIds"], [second_group_id])

        all_response = await self.client.post(
            "/api/favorites/pose/selection",
            json={
                "selection": {"mode": "all", "ids": [], "excluded_ids": [second_id]},
                "groupIds": ["default"],
            },
        )
        self.assertEqual(all_response.status, 200)
        all_payload = await all_response.json()
        self.assertEqual(all_payload["selectedCount"], 1)
        self.assertEqual(all_payload["updatedCount"], 1)
        self.assertIn("default", next(item for item in all_payload["items"] if item["id"] == first_key)["groupIds"])

        invalid = await self.client.post(
            "/api/favorites/pose/selection",
            json={"selection": {"mode": "include", "ids": ["missing"]}, "groupIds": ["default"]},
        )
        self.assertEqual(invalid.status, 400)

    async def test_favorite_child_import_parent_filter_and_safe_delete_api(self):
        source = await self.client.post("/api/custom-groups/pose", json={"name": "Snapshot"})
        source_id = (await source.json())["group"]["id"]
        custom = await self.client.post(
            "/api/custom-prompts",
            json={
                "section": "pose",
                "title": "Snapshot Pose",
                "prompt": "snapshot pose",
                "groupIds": [source_id],
            },
        )
        custom_id = (await custom.json())["id"]
        parent = await self.client.post("/api/favorites/pose/groups", json={"name": "Parent"})
        parent_id = (await parent.json())["group"]["id"]

        imported = await self.client.post(
            f"/api/favorites/pose/groups/{parent_id}/children/import",
            json={"customGroupId": source_id},
        )
        self.assertEqual(imported.status, 201)
        imported_payload = await imported.json()
        child = imported_payload["group"]
        self.assertEqual(child["parentId"], parent_id)
        self.assertEqual(child["sourceCustomGroupId"], source_id)
        child_with_stats = next(
            group for group in imported_payload["groups"] if group["id"] == child["id"]
        )
        self.assertEqual(child_with_stats["directCount"], 1)

        duplicate = await self.client.post(
            f"/api/favorites/pose/groups/{parent_id}/children/import",
            json={"customGroupId": source_id},
        )
        self.assertEqual(duplicate.status, 400)
        filtered = await (
            await self.client.get(
                f"/api/pools/pose?collection={parent_id}&q=Snapshot%20Pose"
            )
        ).json()
        self.assertEqual([item["id"] for item in filtered["items"]], [custom_id])

        invalid_bool = await self.client.delete(
            f"/api/favorites/pose/groups/{child['id']}?deleteItems=maybe"
        )
        self.assertEqual(invalid_bool.status, 400)
        deleted = await self.client.delete(f"/api/favorites/pose/groups/{parent_id}")
        self.assertEqual(deleted.status, 200)
        payload = await deleted.json()
        self.assertEqual(payload["deletedGroupCount"], 2)
        favorite = next(item for item in payload["items"] if item["id"] == custom_id)
        self.assertEqual(favorite["groupIds"], ["default"])

    async def test_custom_group_delete_modes_and_legacy_query_compatibility(self):
        async def create_group(name):
            response = await self.client.post("/api/custom-groups/pose", json={"name": name})
            return (await response.json())["group"]

        first = await create_group("First")
        second = await create_group("Second")
        exclusive = await (
            await self.client.post(
                "/api/custom-prompts",
                json={"section": "pose", "title": "Exclusive", "prompt": "exclusive", "groupIds": [first["id"]]},
            )
        ).json()
        shared = await (
            await self.client.post(
                "/api/custom-prompts",
                json={"section": "pose", "title": "Shared", "prompt": "shared", "groupIds": [first["id"], second["id"]]},
            )
        ).json()

        deleted = await self.client.delete(
            f"/api/custom-groups/pose/{first['id']}?deleteMode=all&deleteItems=maybe"
        )
        self.assertEqual(deleted.status, 200)
        payload = await deleted.json()
        self.assertEqual(payload["deleteMode"], "all")
        self.assertEqual(set(payload["deletedItemIds"]), {exclusive["id"], shared["id"]})
        self.assertEqual(
            (await (await self.client.get("/api/custom-prompts?section=pose")).json())["items"],
            [],
        )

        legacy = await create_group("Legacy")
        legacy_item = await (
            await self.client.post(
                "/api/custom-prompts",
                json={"section": "pose", "title": "Legacy", "prompt": "legacy", "groupIds": [legacy["id"]]},
            )
        ).json()
        legacy_deleted = await self.client.delete(
            f"/api/custom-groups/pose/{legacy['id']}?deleteItems=true"
        )
        self.assertEqual(legacy_deleted.status, 200)
        legacy_payload = await legacy_deleted.json()
        self.assertEqual(legacy_payload["deleteMode"], "exclusive")
        self.assertEqual(legacy_payload["deletedItemIds"], [legacy_item["id"]])

        invalid = await create_group("Invalid")
        invalid_response = await self.client.delete(
            f"/api/custom-groups/pose/{invalid['id']}?deleteMode=invalid"
        )
        self.assertEqual(invalid_response.status, 400)
        self.assertIn("deleteMode", (await invalid_response.json())["error"])

    async def test_artist_favorites_normalize_prefix_and_preserve_other_sections(self):
        response = await self.client.put(
            "/api/favorites/artist/item",
            json={"name": "@rella", "favorite": True},
        )
        self.assertEqual(response.status, 200)
        payload = await response.json()
        self.assertEqual(payload["items"][0]["name"], "rella")
        self.assertEqual(payload["items"][0]["groupIds"], ["default"])
        self.assertEqual(self.client.server.app[COMFY_KEY].favorites_data["pose"]["items"], [])

    async def test_custom_group_templates_and_import_flow(self):
        expected_titles = {
            "character": "示例角色",
            "clothing": "休闲连帽衫",
            "pose": "站立挥手",
            "background": "樱花街道",
            "expression": "期待",
        }
        for section, title in expected_titles.items():
            template = await self.client.get(f"/api/custom-prompts/templates/{section}/json")
            self.assertEqual(template.status, 200)
            self.assertIn(f"custom-prompts-{section}-template.json", template.headers["Content-Disposition"])
            item = json.loads(await template.text())["items"][0]
            self.assertEqual(item["section"], section)
            self.assertEqual(item["title"], title)
        csv_template = await self.client.get("/api/custom-prompts/templates/pose/csv")
        self.assertEqual(csv_template.status, 200)
        self.assertIn("section,title,prompt", (await csv_template.text()).lstrip("\ufeff"))

        group_response = await self.client.post("/api/custom-groups/expression", json={"name": "Mood"})
        self.assertEqual(group_response.status, 201)
        target_group_response = await self.client.post("/api/custom-groups/expression", json={"name": "Imported"})
        self.assertEqual(target_group_response.status, 201)
        target_group_id = (await target_group_response.json())["group"]["id"]
        preview_response = await self.client.post(
            "/api/custom-prompts/import/preview",
            json={"format": "json", "section": "expression", "bundleName": "Expression Pack", "content": '{"items":[{"section":"expression","title":"Calm","prompt":"calm face","groups":["Mood"]}]}'},
        )
        self.assertEqual(preview_response.status, 200)
        preview = await preview_response.json()
        self.assertEqual(preview["summary"]["new"], 1)
        committed = await self.client.post("/api/custom-prompts/import", json={
            "rows": preview["rows"], "section": "expression", "targetGroupIds": [target_group_id],
            "bundleName": "Expression Pack",
        })
        self.assertEqual(committed.status, 200)
        committed_payload = await committed.json()
        self.assertEqual(committed_payload["imported"], 1)
        pool = await (await self.client.get("/api/pools/expression?q=Calm")).json()
        self.assertEqual(pool["items"][0]["title"], "Calm")
        groups = (await (await self.client.get("/api/custom-groups/expression")).json())["groups"]
        bundle = next(item for item in groups if item["id"] == committed_payload["bundleId"])
        children = [item for item in groups if item.get("parentId") == bundle["id"]]
        self.assertEqual(bundle["count"], 1)
        self.assertEqual([item["name"] for item in children], ["Mood"])
        self.assertEqual(next(item for item in groups if item["id"] == target_group_id)["count"], 1)
        parent_pool = await (
            await self.client.get(f"/api/pools/expression?custom_group={bundle['id']}")
        ).json()
        self.assertEqual([item["title"] for item in parent_pool["items"]], ["Calm"])

        mixed_preview = await self.client.post(
            "/api/custom-prompts/import/preview",
            json={"format": "json", "section": "expression", "bundleName": "Expression Pack", "content": '{"items":[{"section":"pose","title":"Wave","prompt":"waving"}]}'},
        )
        self.assertEqual(mixed_preview.status, 200)
        self.assertEqual((await mixed_preview.json())["summary"]["error"], 1)

        invalid_target = await self.client.post("/api/custom-prompts/import", json={
            "rows": [{"action": "create", "item": {"section": "expression", "title": "Unsafe", "prompt": "unsafe"}}],
            "section": "expression", "targetGroupIds": ["custom_group_missing"], "bundleName": "Unsafe Pack",
        })
        self.assertEqual(invalid_target.status, 400)
        unsafe_pool = await (await self.client.get("/api/pools/expression?q=Unsafe")).json()
        self.assertEqual(unsafe_pool["total"], 0)

    async def test_missing_lora_returns_clear_error(self):
        settings = {
            **DEFAULT_SETTINGS,
            "loras": [{"filename": "missing.safetensors", "enabled": True, "strength": 1}],
        }
        response = await self.client.post("/api/batches", json=settings)
        self.assertEqual(response.status, 400)
        self.assertIn("missing.safetensors", (await response.json())["error"])

    async def test_invalid_settings_return_400(self):
        response = await self.client.post("/api/batches", json={**DEFAULT_SETTINGS, "count": 0})
        self.assertEqual(response.status, 400)
        self.assertIn("生成数量", (await response.json())["error"])

        for percent in (0, 1001, "", 60.5):
            with self.subTest(percent=percent):
                invalid_hires = {**DEFAULT_SETTINGS["hires"], "percent": percent}
                response = await self.client.post(
                    "/api/batches", json={**DEFAULT_SETTINGS, "hires": invalid_hires}
                )
                self.assertEqual(response.status, 400)
                self.assertIn("hires.percent", (await response.json())["error"])

        for field, value in (("sampler_name", ""), ("sampler_name", 1), ("scheduler", ""), ("scheduler", False)):
            with self.subTest(field=field, value=value):
                response = await self.client.post(
                    "/api/batches", json={**DEFAULT_SETTINGS, field: value}
                )
                self.assertEqual(response.status, 400)
                self.assertIn(field, (await response.json())["error"])

        for field, value in (("sampler_name", "missing"), ("scheduler", "missing")):
            with self.subTest(field=field):
                response = await self.client.post(
                    "/api/batches", json={**DEFAULT_SETTINGS, field: value}
                )
                self.assertEqual(response.status, 400)
                self.assertIn("不可用", (await response.json())["error"])

    async def test_new_dimension_settings_are_returned_and_persisted(self):
        settings = {
            **DEFAULT_SETTINGS,
            "random_character": False,
            "random_character_count": 2,
            "fixed_character": "hero",
            "random_clothing_count": 5,
        }
        response = await self.client.post("/api/batches", json=settings)
        self.assertEqual(response.status, 201)
        manager = self.client.server.app[MANAGER_KEY]
        await manager.wait()
        history = await (await self.client.get("/api/history")).json()
        saved = history["items"][0]["settings"]
        self.assertEqual(saved["random_character_count"], 2)
        self.assertEqual(saved["fixed_character"], "hero")
        self.assertEqual(saved["random_clothing_count"], 5)

    async def test_optional_sampling_settings_are_submitted_and_persisted(self):
        settings = {
            **DEFAULT_SETTINGS,
            "count": 1,
            "cfg_zero_star": True,
            "second_sampler": {**DEFAULT_SETTINGS["second_sampler"], "enabled": True},
        }
        response = await self.client.post("/api/batches", json=settings)
        self.assertEqual(response.status, 201)
        await self.client.server.app[MANAGER_KEY].wait()
        prompt = self.comfy.submissions[-1]["prompt"]
        self.assertIn("49", prompt)
        self.assertIn("25", prompt)
        self.assertEqual(prompt["25"]["inputs"]["seed"], ["37", 0])
        self.assertEqual(prompt["48"]["inputs"]["samples"], ["25", 0])
        history = await (await self.client.get("/api/history")).json()
        saved = history["items"][0]["settings"]
        self.assertTrue(saved["cfg_zero_star"])
        self.assertTrue(saved["second_sampler"]["enabled"])

    async def test_batch_submission_normalizes_settings_and_resolved_prompt(self):
        settings = {
            **DEFAULT_SETTINGS,
            "count": 1,
            "quality_prompt": "2025，SCORE 9, Blue_Hair",
            "extra_prompt": "@Niji9il, Blue_Hair",
            "lora_managed_triggers": ["@Niji9il"],
        }
        response = await self.client.post("/api/batches", json=settings)
        self.assertEqual(response.status, 201)
        state = await response.json()
        self.assertEqual(
            state["settings"]["quality_prompt"], "year 2025, score_9, blue hair"
        )
        self.assertEqual(state["settings"]["extra_prompt"], "@Niji9il, blue hair")
        await self.client.server.app[MANAGER_KEY].wait()
        submitted = self.comfy.submissions[-1]["prompt"]
        self.assertEqual(
            submitted["42"]["inputs"]["quality_prompt"],
            "year 2025, score_9, blue hair",
        )
        self.assertEqual(
            submitted["60"]["inputs"]["resolved_prompt"],
            "1girl, @Niji9il, blue hair",
        )

    async def test_batch_completes_and_history_is_paged(self):
        response = await self.client.post("/api/batches", json={**DEFAULT_SETTINGS, "count": 1})
        self.assertEqual(response.status, 201)
        manager = self.client.server.app[MANAGER_KEY]
        await manager.wait()
        current = await (await self.client.get("/api/batches/current")).json()
        self.assertEqual(current["batch"]["status"], "completed")
        history = await (await self.client.get("/api/history?page=1&limit=10")).json()
        self.assertEqual(history["total"], 1)
        image_id = history["items"][0]["id"]
        image = await self.client.get(f"/api/images/{image_id}")
        self.assertEqual(await image.read(), b"png")
        deleted = await self.client.delete(f"/api/history/{image_id}")
        self.assertEqual(deleted.status, 200)
        self.assertEqual((await (await self.client.get("/api/history")).json())["total"], 0)

    async def test_missing_history_record_returns_404(self):
        self.assertEqual((await self.client.get("/api/images/999")).status, 404)

    async def test_non_numeric_image_id_returns_404_not_500(self):
        # 回归 #P2-1:此前 int() 裸抛 ValueError 变成 500。
        self.assertEqual((await self.client.get("/api/images/abc")).status, 404)
        self.assertEqual((await self.client.delete("/api/history/abc")).status, 404)

    async def test_pool_query_endpoint_filters_and_selection(self):
        # 此前 POST /api/pools/{section}/query 零测试覆盖(#P2-13)。
        payload = await (
            await self.client.post(
                "/api/pools/pose/query",
                json={"page": 1, "limit": 48, "q": "Standing"},
            )
        ).json()
        self.assertEqual([item["id"] for item in payload["items"]], ["pose:stand"])
        excluded = await (
            await self.client.post(
                "/api/pools/pose/query",
                json={
                    "page": 1,
                    "limit": 48,
                    "selection": {"mode": "include", "ids": ["pose:sit"], "excluded_ids": []},
                },
            )
        ).json()
        self.assertEqual([item["id"] for item in excluded["items"]], ["pose:sit"])
        bad = await self.client.post("/api/pools/pose/query", json={"page": "abc"})
        self.assertEqual(bad.status, 400)

    async def test_non_local_host_or_origin_is_rejected(self):
        # 回归 #P2-2:恶意网页的 CSRF/DNS 重绑定应被本机来源校验拦截。
        spoofed_host = await self.client.get("/api/config", headers={"Host": "evil.example:8190"})
        self.assertEqual(spoofed_host.status, 403)
        evil_origin = await self.client.post(
            "/api/style-presets", json={}, headers={"Origin": "http://evil.example"}
        )
        self.assertEqual(evil_origin.status, 403)
        null_origin = await self.client.post("/api/style-presets", json={}, headers={"Origin": "null"})
        self.assertEqual(null_origin.status, 403)
        local_origin = await self.client.get(
            "/api/config", headers={"Origin": f"http://127.0.0.1:{self.client.port}"}
        )
        self.assertEqual(local_origin.status, 200)

    async def test_explicit_trusted_proxy_host_and_origin_are_allowed(self):
        trusted_host = "anima.165-99-43-225.sslip.io"
        trusted_app = create_app(
            app_dir=APP_DIR,
            comfy=FakeComfy(),
            history_path=Path(self.temp.name) / "trusted-history.sqlite3",
            custom_prompts_path=Path(self.temp.name) / "trusted-custom-prompts.json",
            style_presets_path=Path(self.temp.name) / "trusted-style-presets.json",
            anima_tools_dir=Path(self.temp.name) / "tools",
            trusted_hostnames={trusted_host},
        )
        trusted_client = TestClient(TestServer(trusted_app))
        await trusted_client.start_server()
        try:
            trusted = await trusted_client.get(
                "/api/config",
                headers={
                    "Host": trusted_host,
                    "Origin": f"https://{trusted_host}",
                },
            )
            self.assertEqual(trusted.status, 200)
            evil = await trusted_client.get(
                "/api/config",
                headers={"Host": "evil.example", "Origin": "https://evil.example"},
            )
            self.assertEqual(evil.status, 403)
        finally:
            await trusted_client.close()

    async def test_config_exposes_startup_warnings(self):
        payload = await (await self.client.get("/api/config")).json()
        self.assertEqual(payload["warnings"], [])

    async def test_current_batch_includes_queue_and_preview_endpoint(self):
        # 0.2.0:current 返回队列;预览端点无帧时 204,有帧时回图。
        current = await (await self.client.get("/api/batches/current")).json()
        self.assertEqual(current["queue"], [])
        self.assertEqual((await self.client.get("/api/batches/current/preview")).status, 204)
        manager = self.client.server.app[MANAGER_KEY]
        manager.preview = (1, "image/jpeg", b"frame")
        preview = await self.client.get("/api/batches/current/preview")
        self.assertEqual(preview.status, 200)
        self.assertEqual(await preview.read(), b"frame")
        self.assertEqual(preview.headers["Content-Type"], "image/jpeg")
        missing = await self.client.delete("/api/batches/queue/queue_missing")
        self.assertEqual(missing.status, 404)

    async def test_batch_with_seeds_reproduces_exact_image(self):
        # 0.2.0:复现请求携带 seeds,历史记录里的种子必须一字不差。
        response = await self.client.post(
            "/api/batches",
            json={**DEFAULT_SETTINGS, "count": 1, "seeds": {"sample_seed": 987654321, "prompt_seed": 24680}},
        )
        self.assertEqual(response.status, 201)
        await self.client.server.app[MANAGER_KEY].wait()
        history = await (await self.client.get("/api/history")).json()
        self.assertEqual(history["items"][0]["sample_seed"], 987654321)
        self.assertEqual(history["items"][0]["prompt_seed"], 24680)
        bad = await self.client.post(
            "/api/batches",
            json={**DEFAULT_SETTINGS, "count": 1, "seeds": {"sample_seed": -5, "prompt_seed": 1}},
        )
        self.assertEqual(bad.status, 400)

    async def _create_history_image(self):
        response = await self.client.post(
            "/api/batches", json={**DEFAULT_SETTINGS, "count": 1}
        )
        self.assertEqual(response.status, 201)
        await self.client.server.app[MANAGER_KEY].wait()
        history = await (await self.client.get("/api/history")).json()
        return history["items"][0]

    async def test_regeneration_options_and_frozen_modes(self):
        image = await self._create_history_image()
        options = await (
            await self.client.get(
                f"/api/history/{image['id']}/regeneration-options"
            )
        ).json()
        self.assertTrue(options["modes"]["replay"]["available"])
        self.assertTrue(options["modes"]["prompt_variant"]["available"])
        original_submissions = len(self.comfy.submissions)
        replay = await self.client.post(
            f"/api/history/{image['id']}/regenerate", json={"mode": "replay"}
        )
        self.assertEqual(replay.status, 201)
        await self.client.server.app[MANAGER_KEY].wait()
        replay_prompt = self.comfy.submissions[original_submissions]["prompt"]
        self.assertEqual(replay_prompt["37"]["inputs"]["seed"], image["sample_seed"])
        self.assertEqual(replay_prompt["60"]["inputs"]["seed"], image["prompt_seed"])
        self.assertEqual(replay_prompt["60"]["inputs"]["resolved_prompt"], "generated")
        self.assertEqual(replay_prompt["42"]["inputs"]["quality_prompt"], "")

        variant = await self.client.post(
            f"/api/history/{image['id']}/regenerate",
            json={"mode": "prompt_variant", "count": 2},
        )
        self.assertEqual(variant.status, 201)
        await self.client.server.app[MANAGER_KEY].wait()
        variant_prompts = self.comfy.submissions[-2:]
        self.assertTrue(
            all(item["prompt"]["60"]["inputs"]["seed"] == image["prompt_seed"] for item in variant_prompts)
        )
        self.assertTrue(
            all(item["prompt"]["37"]["inputs"]["seed"] != image["sample_seed"] for item in variant_prompts)
        )

    async def test_regeneration_validation_and_missing_resources(self):
        image = await self._create_history_image()
        endpoint = f"/api/history/{image['id']}/regenerate"
        cases = [
            ({"mode": "replay", "count": 2}, "不接受"),
            ({"mode": "prompt_variant", "count": 0}, "count"),
            ({"mode": "content_redraw", "count": 2, "sections": []}, "至少"),
            ({"mode": "content_redraw", "count": 2, "sections": ["pose", "pose"]}, "重复"),
            ({"mode": "content_redraw", "count": 2, "sections": ["unknown"]}, "不支持"),
        ]
        for payload, text in cases:
            with self.subTest(payload=payload):
                response = await self.client.post(endpoint, json=payload)
                self.assertEqual(response.status, 400)
                self.assertIn(text, (await response.json())["error"])

        async def missing_inventory():
            return {
                "models": [],
                "upscale_models": [],
                "samplers": [],
                "schedulers": [],
            }

        self.comfy.resource_inventory = missing_inventory
        options = await (
            await self.client.get(
                f"/api/history/{image['id']}/regeneration-options"
            )
        ).json()
        self.assertFalse(options["modes"]["replay"]["available"])
        self.assertTrue(options["resourceIssues"])

    async def _open_folder_client(self, output_dir):
        """构造一个显式绑定 output_dir 的独立 app,用于定位文件测试。"""
        app = create_app(
            app_dir=APP_DIR,
            comfy=FakeComfy(),
            history_path=Path(self.temp.name) / "open-folder-history.sqlite3",
            custom_prompts_path=Path(self.temp.name) / "open-folder-custom-prompts.json",
            style_presets_path=Path(self.temp.name) / "open-folder-style-presets.json",
            anima_tools_dir=Path(self.temp.name) / "tools",
            output_dir=output_dir,
        )
        client = TestClient(TestServer(app))
        await client.start_server()
        return client

    async def test_open_folder_reveals_existing_file(self):
        output_dir = Path(self.temp.name) / "output"
        output_dir.mkdir()
        (output_dir / "test.png").write_bytes(b"png")
        client = await self._open_folder_client(output_dir)
        try:
            response = await client.post("/api/batches", json={**DEFAULT_SETTINGS, "count": 1})
            self.assertEqual(response.status, 201)
            await client.server.app[MANAGER_KEY].wait()
            history = await (await client.get("/api/history")).json()
            image_id = history["items"][0]["id"]
            with mock.patch(
                "anima_webui.server._reveal_in_file_manager"
            ) as reveal_mock:
                opened = await client.post(f"/api/history/{image_id}/open-folder")
            self.assertEqual(opened.status, 200)
            self.assertEqual(await opened.json(), {"opened": True})
            reveal_mock.assert_called_once()
            self.assertEqual(reveal_mock.call_args.args[0], (output_dir / "test.png").resolve())
        finally:
            await client.close()

    async def test_open_folder_missing_file_returns_404(self):
        output_dir = Path(self.temp.name) / "output-missing"
        output_dir.mkdir()
        client = await self._open_folder_client(output_dir)
        try:
            response = await client.post("/api/batches", json={**DEFAULT_SETTINGS, "count": 1})
            self.assertEqual(response.status, 201)
            await client.server.app[MANAGER_KEY].wait()
            history = await (await client.get("/api/history")).json()
            image_id = history["items"][0]["id"]
            with mock.patch("anima_webui.server._reveal_in_file_manager") as reveal_mock:
                missing = await client.post(f"/api/history/{image_id}/open-folder")
            self.assertEqual(missing.status, 404)
            self.assertEqual((await missing.json())["error"], "文件在本地磁盘中不存在")
            reveal_mock.assert_not_called()
        finally:
            await client.close()

    async def test_open_folder_without_output_dir_returns_400(self):
        # 未配置 output 目录时,定位接口返回 400 且不阻断其他功能。
        # 屏蔽相对路径探测,避免测试机恰好存在 ../ComfyUI/output 导致误命中。
        with mock.patch("anima_webui.server.resolve_output_dir", return_value=None):
            client = await self._open_folder_client(None)
            try:
                response = await client.post(
                    "/api/batches", json={**DEFAULT_SETTINGS, "count": 1}
                )
                self.assertEqual(response.status, 201)
                await client.server.app[MANAGER_KEY].wait()
                history = await (await client.get("/api/history")).json()
                image_id = history["items"][0]["id"]
                blocked = await client.post(f"/api/history/{image_id}/open-folder")
                self.assertEqual(blocked.status, 400)
                self.assertEqual(
                    (await blocked.json())["error"], "未配置或未找到 ComfyUI 输出目录"
                )
                # 其他功能不受影响:图片仍可读取。
                self.assertEqual((await client.get(f"/api/images/{image_id}")).status, 200)
            finally:
                await client.close()

    async def test_open_folder_rejects_path_traversal(self):
        output_dir = Path(self.temp.name) / "output-traversal"
        output_dir.mkdir()
        client = await self._open_folder_client(output_dir)
        try:
            response = await client.post("/api/batches", json={**DEFAULT_SETTINGS, "count": 1})
            self.assertEqual(response.status, 201)
            await client.server.app[MANAGER_KEY].wait()
            history = await (await client.get("/api/history")).json()
            image_id = history["items"][0]["id"]
            # 直接篡改数据库里的 filename 为穿越路径,验证接口拒绝。
            store = client.server.app[HISTORY_KEY]
            store.connection.execute(
                "UPDATE images SET filename = ? WHERE id = ?",
                ("../../etc/passwd", image_id),
            )
            store.connection.commit()
            with mock.patch("anima_webui.server._reveal_in_file_manager") as reveal_mock:
                rejected = await client.post(f"/api/history/{image_id}/open-folder")
            self.assertEqual(rejected.status, 400)
            self.assertEqual((await rejected.json())["error"], "图片路径无效")
            reveal_mock.assert_not_called()
        finally:
            await client.close()

    async def _delete_history_client(self, output_dir):
        """构造一个显式绑定 output_dir 的独立 app,用于物理删除测试。"""
        app = create_app(
            app_dir=APP_DIR,
            comfy=FakeComfy(),
            history_path=Path(self.temp.name) / "delete-history.sqlite3",
            custom_prompts_path=Path(self.temp.name) / "delete-custom-prompts.json",
            style_presets_path=Path(self.temp.name) / "delete-style-presets.json",
            anima_tools_dir=Path(self.temp.name) / "tools",
            output_dir=output_dir,
        )
        client = TestClient(TestServer(app))
        await client.start_server()
        return client

    async def test_delete_history_removes_physical_file_and_tolerates_missing(self):
        # 删除作品必须同步清理磁盘文件;文件已被手动移走时仍应清理数据库记录。
        output_dir = Path(self.temp.name) / "output-delete"
        output_dir.mkdir()
        client = await self._delete_history_client(output_dir)
        try:
            response = await client.post("/api/batches", json={**DEFAULT_SETTINGS, "count": 1})
            self.assertEqual(response.status, 201)
            await client.server.app[MANAGER_KEY].wait()
            history = await (await client.get("/api/history")).json()
            first_id = history["items"][0]["id"]
            physical = output_dir / "test.png"
            physical.write_bytes(b"png")

            deleted = await client.delete(f"/api/history/{first_id}")
            self.assertEqual(deleted.status, 200)
            self.assertEqual(
                await deleted.json(), {"deleted": True, "file_deleted": True}
            )
            self.assertFalse(physical.exists())
            self.assertEqual((await client.get(f"/api/images/{first_id}")).status, 404)

            # 第二条记录:磁盘上没有对应文件(幽灵记录),删除不应报错。
            second = await client.post("/api/batches", json={**DEFAULT_SETTINGS, "count": 1})
            self.assertEqual(second.status, 201)
            await client.server.app[MANAGER_KEY].wait()
            history = await (await client.get("/api/history")).json()
            second_id = history["items"][0]["id"]
            self.assertFalse((output_dir / "test.png").exists())

            ghost = await client.delete(f"/api/history/{second_id}")
            self.assertEqual(ghost.status, 200)
            self.assertEqual(
                await ghost.json(), {"deleted": True, "file_deleted": False}
            )
            self.assertEqual((await client.get(f"/api/images/{second_id}")).status, 404)
        finally:
            await client.close()

    async def test_delete_history_rejects_path_traversal(self):
        # 篡改为穿越路径的记录:绝不 unlink 作用域外文件,但仍清理数据库记录。
        output_dir = Path(self.temp.name) / "output-delete-traversal"
        output_dir.mkdir()
        outside = Path(self.temp.name) / "outside.png"
        outside.write_bytes(b"keep")
        client = await self._delete_history_client(output_dir)
        try:
            response = await client.post("/api/batches", json={**DEFAULT_SETTINGS, "count": 1})
            self.assertEqual(response.status, 201)
            await client.server.app[MANAGER_KEY].wait()
            history = await (await client.get("/api/history")).json()
            image_id = history["items"][0]["id"]
            store = client.server.app[HISTORY_KEY]
            store.connection.execute(
                "UPDATE images SET filename = ? WHERE id = ?",
                ("../outside.png", image_id),
            )
            store.connection.commit()

            deleted = await client.delete(f"/api/history/{image_id}")
            self.assertEqual(deleted.status, 200)
            self.assertEqual(
                await deleted.json(), {"deleted": True, "file_deleted": False}
            )
            self.assertTrue(outside.exists())
            self.assertEqual((await client.get(f"/api/images/{image_id}")).status, 404)
        finally:
            await client.close()

    async def test_delete_history_keeps_record_when_file_is_locked(self):
        # 文件被占用时返回 500 且不提交数据库删除,保证状态一致。
        output_dir = Path(self.temp.name) / "output-delete-locked"
        output_dir.mkdir()
        client = await self._delete_history_client(output_dir)
        try:
            response = await client.post("/api/batches", json={**DEFAULT_SETTINGS, "count": 1})
            self.assertEqual(response.status, 201)
            await client.server.app[MANAGER_KEY].wait()
            history = await (await client.get("/api/history")).json()
            image_id = history["items"][0]["id"]
            physical = output_dir / "test.png"
            physical.write_bytes(b"png")

            with mock.patch.object(Path, "unlink", side_effect=PermissionError("locked")):
                locked = await client.delete(f"/api/history/{image_id}")
            self.assertEqual(locked.status, 500)
            self.assertIn("无法删除本地物理文件", (await locked.json())["error"])
            self.assertTrue(physical.exists())
            self.assertEqual((await client.get(f"/api/images/{image_id}")).status, 200)
        finally:
            await client.close()

    async def test_config_exposes_output_dir(self):
        output_dir = Path(self.temp.name) / "output-config"
        output_dir.mkdir()
        client = await self._open_folder_client(output_dir)
        try:
            payload = await (await client.get("/api/config")).json()
            self.assertEqual(payload["output_dir"], str(output_dir.resolve()))
        finally:
            await client.close()

    async def test_launcher_shutdown_requires_token(self):
        # 未配置 token 时端点不存在;配置了也必须携带正确令牌。
        self.assertEqual(
            (await self.client.post("/api/launcher-shutdown", json={"token": "x"})).status,
            404,
        )
        app = create_app(
            app_dir=APP_DIR,
            comfy=FakeComfy(),
            history_path=Path(self.temp.name) / "shutdown-history.sqlite3",
            custom_prompts_path=Path(self.temp.name) / "shutdown-custom-prompts.json",
            style_presets_path=Path(self.temp.name) / "shutdown-style-presets.json",
            anima_tools_dir=Path(self.temp.name) / "tools",
            shutdown_token="secret-token",
        )
        client = TestClient(TestServer(app))
        await client.start_server()
        try:
            self.assertEqual(
                (await client.post("/api/launcher-shutdown", json={"token": "wrong"})).status,
                403,
            )
            self.assertEqual(
                (await client.post("/api/launcher-shutdown", json={})).status,
                403,
            )
            with mock.patch("anima_webui.server.os._exit") as exit_mock:
                ok = await client.post("/api/launcher-shutdown", json={"token": "secret-token"})
                self.assertEqual(ok.status, 200)
                await asyncio.sleep(0.7)
                exit_mock.assert_called_once_with(0)
        finally:
            await client.close()


    # ---------- 批量管理:批处理接口 ----------
    async def _batch_client(self, output_dir, name="batch"):
        """构造一个显式绑定 output_dir 的独立 app,用于批量接口测试。

        data_dir 必须指向 tempdir:否则 app_settings.json 会落到项目 data/ 下,
        导致导出目录配置在测试之间互相污染。
        """
        data_dir = Path(self.temp.name) / f"{name}-data"
        data_dir.mkdir(parents=True, exist_ok=True)
        app = create_app(
            app_dir=APP_DIR,
            comfy=FakeComfy(),
            history_path=Path(self.temp.name) / f"{name}-history.sqlite3",
            custom_prompts_path=Path(self.temp.name) / f"{name}-custom-prompts.json",
            style_presets_path=Path(self.temp.name) / f"{name}-style-presets.json",
            anima_tools_dir=Path(self.temp.name) / "tools",
            output_dir=output_dir,
            data_dir=data_dir,
        )
        client = TestClient(TestServer(app))
        await client.start_server()
        return client

    async def _seed_images(self, client, count):
        """跑 count 个单图批次,返回按 id 倒序的历史记录列表。"""
        for _ in range(count):
            response = await client.post(
                "/api/batches", json={**DEFAULT_SETTINGS, "count": 1}
            )
            self.assertEqual(response.status, 201)
            await client.server.app[MANAGER_KEY].wait()
        history = await (await client.get("/api/history?page=1&limit=60")).json()
        return history["items"]

    async def test_batch_delete_removes_files_and_records(self):
        output_dir = Path(self.temp.name) / "output-batch-delete"
        output_dir.mkdir()
        client = await self._batch_client(output_dir, "batch-delete")
        try:
            items = await self._seed_images(client, 3)
            ids = [item["id"] for item in items]
            # 三张图共用 test.png 文件名,分别落到不同子目录以验证逐条删除。
            for index, image_id in enumerate(ids):
                subfolder = output_dir / f"sub{index}"
                subfolder.mkdir()
                (subfolder / "test.png").write_bytes(b"png")
                store = client.server.app[HISTORY_KEY]
                store.connection.execute(
                    "UPDATE images SET subfolder = ? WHERE id = ?",
                    (f"sub{index}", image_id),
                )
                store.connection.commit()

            response = await client.post(
                "/api/history/batch-delete", json={"image_ids": ids}
            )
            self.assertEqual(response.status, 200)
            payload = await response.json()
            self.assertEqual(payload["deleted"], 3)
            self.assertEqual(payload["file_deleted"], 3)
            self.assertEqual(payload["file_missing"], 0)
            self.assertEqual(payload["requested"], 3)
            for index in range(3):
                self.assertFalse((output_dir / f"sub{index}" / "test.png").exists())
            self.assertEqual(
                (await (await client.get("/api/history")).json())["total"], 0
            )
        finally:
            await client.close()

    async def test_batch_delete_tolerates_missing_files_and_unknown_ids(self):
        # 幽灵记录(磁盘无文件)与不存在的 id 都不应阻断整批删除。
        output_dir = Path(self.temp.name) / "output-batch-delete-missing"
        output_dir.mkdir()
        client = await self._batch_client(output_dir, "batch-delete-missing")
        try:
            items = await self._seed_images(client, 2)
            ids = [item["id"] for item in items]
            response = await client.post(
                "/api/history/batch-delete", json={"image_ids": [*ids, 999999]}
            )
            self.assertEqual(response.status, 200)
            payload = await response.json()
            self.assertEqual(payload["deleted"], 2)
            self.assertEqual(payload["file_deleted"], 0)
            self.assertEqual(payload["file_missing"], 2)
            self.assertEqual(
                (await (await client.get("/api/history")).json())["total"], 0
            )
        finally:
            await client.close()

    async def test_batch_delete_aborts_when_file_is_locked(self):
        # 任一文件被占用时整批不提交数据库删除,保证磁盘与数据库一致。
        output_dir = Path(self.temp.name) / "output-batch-delete-locked"
        output_dir.mkdir()
        client = await self._batch_client(output_dir, "batch-delete-locked")
        try:
            items = await self._seed_images(client, 2)
            ids = [item["id"] for item in items]
            physical = output_dir / "test.png"
            physical.write_bytes(b"png")
            with mock.patch.object(Path, "unlink", side_effect=PermissionError("locked")):
                locked = await client.post(
                    "/api/history/batch-delete", json={"image_ids": ids}
                )
            self.assertEqual(locked.status, 500)
            payload = await locked.json()
            self.assertIn("无法删除", payload["error"])
            self.assertEqual(len(payload["failures"]), 2)
            self.assertTrue(physical.exists())
            self.assertEqual(
                (await (await client.get("/api/history")).json())["total"], 2
            )
        finally:
            await client.close()

    async def test_batch_delete_validates_payload(self):
        client = await self._batch_client(
            Path(self.temp.name) / "output-batch-delete-invalid", "batch-delete-invalid"
        )
        try:
            for payload in (
                {},
                {"image_ids": "1"},
                {"image_ids": []},
                {"image_ids": [True]},
                {"image_ids": ["abc"]},
                {"image_ids": [0]},
            ):
                with self.subTest(payload=payload):
                    response = await client.post(
                        "/api/history/batch-delete", json=payload
                    )
                    self.assertEqual(response.status, 400)
        finally:
            await client.close()

    async def test_batch_export_copies_files_without_overwriting(self):
        output_dir = Path(self.temp.name) / "output-batch-export"
        output_dir.mkdir()
        export_dir = Path(self.temp.name) / "export-batch"
        client = await self._batch_client(output_dir, "batch-export")
        try:
            items = await self._seed_images(client, 2)
            ids = [item["id"] for item in items]
            physical = output_dir / "test.png"
            physical.write_bytes(b"png")

            configured = await client.post(
                "/api/settings/export-folder", json={"export_dir": str(export_dir)}
            )
            self.assertEqual(configured.status, 200)

            first = await client.post(
                "/api/history/batch-export", json={"image_ids": ids}
            )
            self.assertEqual(first.status, 200)
            payload = await first.json()
            self.assertTrue(payload["success"])
            self.assertEqual(payload["exported_count"], 2)
            self.assertEqual(payload["failed_count"], 0)
            # 同名源文件:第二份必须递增重命名,绝不覆盖。
            self.assertEqual(
                [item["filename"] for item in payload["exported"]],
                ["test.png", "test_1.png"],
            )
            self.assertTrue((export_dir / "test.png").is_file())
            self.assertTrue((export_dir / "test_1.png").is_file())

            # 再次导出应继续递增,已有文件内容不被覆盖。
            (export_dir / "test.png").write_bytes(b"original")
            second = await client.post(
                "/api/history/batch-export", json={"image_ids": ids}
            )
            second_payload = await second.json()
            self.assertEqual(
                [item["filename"] for item in second_payload["exported"]],
                ["test_2.png", "test_3.png"],
            )
            self.assertEqual((export_dir / "test.png").read_bytes(), b"original")
        finally:
            await client.close()

    async def test_batch_export_reports_missing_sources_and_requires_folder(self):
        output_dir = Path(self.temp.name) / "output-batch-export-missing"
        output_dir.mkdir()
        client = await self._batch_client(output_dir, "batch-export-missing")
        try:
            items = await self._seed_images(client, 1)
            image_id = items[0]["id"]

            # 未配置导出文件夹时返回 400。
            unset = await client.post(
                "/api/history/batch-export", json={"image_ids": [image_id]}
            )
            self.assertEqual(unset.status, 400)
            self.assertIn("导出文件夹", (await unset.json())["error"])

            export_dir = Path(self.temp.name) / "export-batch-missing"
            await client.post(
                "/api/settings/export-folder", json={"export_dir": str(export_dir)}
            )
            # 源文件不存在 + 未知 id:逐条记录失败但不抛 500。
            response = await client.post(
                "/api/history/batch-export", json={"image_ids": [image_id, 999999]}
            )
            self.assertEqual(response.status, 200)
            payload = await response.json()
            self.assertFalse(payload["success"])
            self.assertEqual(payload["exported_count"], 0)
            self.assertEqual(payload["failed_count"], 2)
            self.assertEqual(
                {item["id"] for item in payload["failures"]}, {image_id, 999999}
            )
        finally:
            await client.close()

    async def test_batch_collections_add_remove_and_set_modes(self):
        client = await self._batch_client(
            Path(self.temp.name) / "output-batch-collections", "batch-collections"
        )
        try:
            items = await self._seed_images(client, 2)
            ids = [item["id"] for item in items]
            first = await client.post(
                "/api/gallery/collections", json={"name": "Batch A"}
            )
            first_id = (await first.json())["id"]
            second = await client.post(
                "/api/gallery/collections", json={"name": "Batch B"}
            )
            second_id = (await second.json())["id"]

            added = await client.post(
                "/api/history/batch-collections",
                json={"image_ids": ids, "collection_ids": [first_id], "mode": "add"},
            )
            self.assertEqual(added.status, 200)
            added_payload = await added.json()
            self.assertEqual(added_payload["mode"], "add")
            self.assertEqual(sorted(added_payload["updated"]), sorted(ids))
            self.assertEqual(added_payload["updated_count"], 2)
            listing = await (
                await client.get(f"/api/history?collection_id={first_id}")
            ).json()
            self.assertEqual(listing["total"], 2)

            # add 幂等:重复添加不产生重复成员关系。
            await client.post(
                "/api/history/batch-collections",
                json={"image_ids": ids, "collection_ids": [first_id], "mode": "add"},
            )
            self.assertEqual(
                (await (await client.get(f"/api/history?collection_id={first_id}")).json())["total"],
                2,
            )

            # 再追加第二个收藏夹,验证多夹并存。
            await client.post(
                "/api/history/batch-collections",
                json={"image_ids": ids, "collection_ids": [second_id], "mode": "add"},
            )
            self.assertEqual(
                (await (await client.get(f"/api/history?collection_id={second_id}")).json())["total"],
                2,
            )

            removed = await client.post(
                "/api/history/batch-collections",
                json={"image_ids": ids, "collection_ids": [first_id], "mode": "remove"},
            )
            self.assertEqual(removed.status, 200)
            self.assertEqual((await removed.json())["updated_count"], 2)
            self.assertEqual(
                (await (await client.get(f"/api/history?collection_id={first_id}")).json())["total"],
                0,
            )
            self.assertEqual(
                (await (await client.get(f"/api/history?collection_id={second_id}")).json())["total"],
                2,
            )

            # set 全量覆盖:只保留 first_id,second_id 归属被清除。
            replaced = await client.post(
                "/api/history/batch-collections",
                json={"image_ids": ids, "collection_ids": [first_id], "mode": "set"},
            )
            self.assertEqual(replaced.status, 200)
            self.assertEqual((await replaced.json())["updated_count"], 2)
            self.assertEqual(
                (await (await client.get(f"/api/history?collection_id={first_id}")).json())["total"],
                2,
            )
            self.assertEqual(
                (await (await client.get(f"/api/history?collection_id={second_id}")).json())["total"],
                0,
            )
        finally:
            await client.close()

    async def test_batch_collections_validates_payload_and_rolls_back(self):
        client = await self._batch_client(
            Path(self.temp.name) / "output-batch-collections-invalid",
            "batch-collections-invalid",
        )
        try:
            items = await self._seed_images(client, 1)
            image_id = items[0]["id"]
            cases = [
                ({"image_ids": [image_id], "collection_ids": [1], "mode": "toggle"}, "mode"),
                ({"image_ids": [image_id], "collection_ids": "1", "mode": "add"}, "collection_ids"),
                ({"image_ids": [image_id], "collection_ids": [], "mode": "add"}, "collection_ids"),
                ({"image_ids": [], "collection_ids": [1], "mode": "add"}, "image_ids"),
                ({"image_ids": [image_id], "collection_ids": [999999], "mode": "add"}, "收藏夹不存在"),
            ]
            for payload, text in cases:
                with self.subTest(payload=payload):
                    response = await client.post(
                        "/api/history/batch-collections", json=payload
                    )
                    self.assertEqual(response.status, 400)
                    self.assertIn(text, (await response.json())["error"])

            # 校验失败后不应留下任何成员关系(事务未提交)。
            self.assertEqual(
                (await (await client.get("/api/history?collection_id=1")).json())["total"],
                0,
            )
        finally:
            await client.close()

    async def test_batch_collections_skips_unknown_images(self):
        client = await self._batch_client(
            Path(self.temp.name) / "output-batch-collections-unknown",
            "batch-collections-unknown",
        )
        try:
            items = await self._seed_images(client, 1)
            image_id = items[0]["id"]
            response = await client.post(
                "/api/history/batch-collections",
                json={"image_ids": [image_id, 999999], "collection_ids": [1], "mode": "add"},
            )
            self.assertEqual(response.status, 200)
            payload = await response.json()
            self.assertEqual(payload["updated"], [image_id])
            self.assertEqual(payload["updated_count"], 1)
        finally:
            await client.close()


if __name__ == "__main__":
    unittest.main()
