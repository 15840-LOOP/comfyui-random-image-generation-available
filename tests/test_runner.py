import asyncio
import copy
import json
import tempfile
import unittest
from pathlib import Path

import sys

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from anima_webui.catalog import CatalogError, PromptCatalog  # noqa: E402
from anima_webui.combination_rules import CombinationRuleStore  # noqa: E402
from anima_webui.comfy import ComfyAborted  # noqa: E402
from anima_webui.history import HistoryStore  # noqa: E402
from anima_webui.runner import BatchConflict, BatchManager  # noqa: E402
from anima_webui.workflow import DEFAULT_SETTINGS  # noqa: E402


class FakeTemplates:
    def submission(self, settings, sample_seed, prompt_seed, filename_prefix, client_id, sequence, **resolved):
        return {
            "settings": settings,
            "sample_seed": sample_seed,
            "prompt_seed": prompt_seed,
            "filename_prefix": filename_prefix,
            "sequence": sequence,
            **resolved,
        }


class FakeCatalog:
    def validate_settings(self, settings):
        return None

    def resolve_prompt(self, settings, prompt_seed, blocked=None):
        return {
            "composer_prompt": "requested character, ",
            "full_prompt": "quality, requested character, ",
            "selected": {"character": [{"title": "requested character"}]},
        }


class FakeComfy:
    def __init__(self):
        self.submissions = []
        self.block = None
        self.error_at = None
        self.honor_abort = False
        self.interrupted = False
        self.available_loras = [item["filename"] for item in DEFAULT_SETTINGS["loras"]]
        self.available_models = [DEFAULT_SETTINGS["model_name"]]
        self.available_upscalers = [DEFAULT_SETTINGS["hires"]["model_name"]]
        self.available_samplers = [DEFAULT_SETTINGS["sampler_name"]]
        self.available_schedulers = [DEFAULT_SETTINGS["scheduler"]]

    async def lora_filenames(self):
        return list(self.available_loras)

    async def resource_inventory(self):
        return {
            "models": list(self.available_models),
            "upscale_models": list(self.available_upscalers),
            "samplers": list(self.available_samplers),
            "schedulers": list(self.available_schedulers),
        }

    async def submit(self, payload):
        self.submissions.append(payload)
        return f"prompt-{len(self.submissions)}"

    async def interrupt(self):
        self.interrupted = True

    async def wait_for_history(self, prompt_id, should_abort=None, missing_timeout=30.0):
        sequence = len(self.submissions)
        if self.block is not None:
            if self.honor_abort and should_abort is not None:
                while not self.block.is_set():
                    if should_abort():
                        raise ComfyAborted("stop")
                    await asyncio.sleep(0)
            else:
                await self.block.wait()
        if self.error_at == sequence:
            raise RuntimeError("render failed")
        return {
            "outputs": {
                "12": {
                    "images": [
                        {
                            "filename": f"image_{sequence}.png",
                            "subfolder": "AnimaRandom",
                            "type": "output",
                        }
                    ]
                }
            },
            "prompt": [0, prompt_id, {}, {"extra_pnginfo": {"anima_prompt": {"42": {"positive": f"prompt {sequence}"}}}}],
        }


class RedrawCatalog(FakeCatalog):
    """按真实 PromptCatalog 的语义抽取:未启用 random_* 的维度不出现在 selected 里。

    真实 resolve_prompt 对 `random_<section>` 为假的维度直接 continue,
    因此固定维度必须由 runner 在事后合并进 selected。替身若无视这个开关,
    content_redraw 下"固定维度缺失 → 组合规则静默失效"的缺陷会被掩盖。
    """

    MAX_REDRAW_ATTEMPTS = 20

    def prompt_parts(self, item, section, character_detail="trigger_tags", strip_person_tags=False):
        return [item.get("prompt") or item.get("title") or ""]

    def resolve_prompt(self, settings, prompt_seed, blocked=None):
        character = {"id": "character:new", "title": "character:new", "prompt": "character:new"}
        fixed_character = settings.get("fixed_character") or ""
        selected = {}
        if settings.get("random_character"):
            selected["character"] = [character]
        if settings.get("random_pose"):
            pose = None
            last_rule = ""
            for attempt in range(self.MAX_REDRAW_ATTEMPTS):
                # 三个候选,确保被禁项即使被选中也仍是"变了"的合法结果,
                # 否则 _changed 重试会替规则兜底、掩盖规则失效。
                pose_id = ("pose:old", "pose:new", "pose:other")[
                    (prompt_seed + attempt) % 3
                ]
                candidate = {"id": pose_id, "title": pose_id, "prompt": pose_id}
                trial = {**selected, "pose": [candidate]}
                last_rule = (blocked(trial) if blocked is not None else None) or ""
                if not last_rule:
                    pose = candidate
                    break
            if pose is None:
                # 与真实 PromptCatalog 一致:点名最后命中的规则 id。
                raise CatalogError(f"pose 维度无法避开组合规则 {last_rule}")
            selected["pose"] = [pose]
        pose_id = selected.get("pose", [{}])[0].get("id", "")
        return {
            "composer_prompt": f"{fixed_character}, {pose_id}, ",
            "full_prompt": f"quality, {fixed_character}, {pose_id}, ",
            "selected": selected,
        }


class RuleAwareCatalog(FakeCatalog):
    """按真实 PromptCatalog 的语义抽样:命中 blocked 就换种子重抽,用尽则报错。"""
    MAX_REDRAW_ATTEMPTS = 200
    CLOTHING = ("clothing:x", "clothing:y")

    def __init__(self):
        self.blocked_calls = []

    def resolve_prompt(self, settings, prompt_seed, blocked=None):
        character = {"id": "character:alpha", "title": "alpha", "prompt": "alpha"}
        chosen = None
        for attempt in range(self.MAX_REDRAW_ATTEMPTS):
            candidate_id = self.CLOTHING[(prompt_seed + attempt) % len(self.CLOTHING)]
            candidate = {
                "id": candidate_id,
                "title": candidate_id,
                "prompt": candidate_id,
            }
            trial = {"character": [character], "clothing": [candidate]}
            rule = blocked(trial) if blocked is not None else None
            if blocked is not None:
                self.blocked_calls.append((trial, rule))
            if not rule:
                chosen = candidate
                break
        if chosen is None:
            raise CatalogError("clothing 维度无法避开组合规则:可用候选都被排除")
        return {
            "composer_prompt": f"alpha, {chosen['id']}, ",
            "full_prompt": f"quality, alpha, {chosen['id']}, ",
            "selected": {"character": [character], "clothing": [chosen]},
        }


class RecordingCatalog(FakeCatalog):
    """记录 resolve_prompt 收到的 blocked 关键字,用于验证接线开关。"""

    def __init__(self):
        self.blocked_values = []

    def resolve_prompt(self, settings, prompt_seed, blocked=None):
        self.blocked_values.append(blocked)
        return super().resolve_prompt(settings, prompt_seed)


class ProgressComfy(FakeComfy):
    """带 websocket 进度流的 fake:产出一条采样进度和一帧预览后挂起。"""

    def __init__(self):
        super().__init__()
        self.release_stream = asyncio.Event()

    async def progress_stream(self, client_id):
        yield {"kind": "event", "payload": {"type": "progress", "data": {"value": 12, "max": 30}}}
        yield {"kind": "preview", "format": "jpeg", "bytes": b"jpeg-frame"}
        await self.release_stream.wait()


class HistoryTests(unittest.IsolatedAsyncioTestCase):
    async def test_history_persists_and_delete_keeps_batch(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.sqlite3"
            store = HistoryStore(path)
            await store.create_batch("batch", 1, DEFAULT_SETTINGS)
            image = await store.add_image(
                batch_id="batch",
                sequence=1,
                prompt_id="prompt",
                image={"filename": "one.png", "subfolder": "folder", "type": "output"},
                positive_prompt="positive",
                negative_prompt="negative",
                sample_seed=1,
                prompt_seed=2,
                settings=DEFAULT_SETTINGS,
            )
            await store.close()
            reopened = HistoryStore(path)
            self.assertEqual((await reopened.list_images())["total"], 1)
            self.assertEqual((await reopened.get_image(image["id"]))["positive_prompt"], "positive")
            self.assertTrue(await reopened.delete_image(image["id"]))
            self.assertEqual((await reopened.list_images())["total"], 0)
            self.assertEqual((await reopened.get_batch("batch"))["id"], "batch")
            await reopened.close()

    async def test_corrupt_database_is_backed_up_and_rebuilt(self):
        # 回归 #P2-4:坏数据库不再阻断启动,改名备份后重建并给出警告。
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.sqlite3"
            path.write_bytes(b"this is not a sqlite database")
            store = HistoryStore(path)
            try:
                self.assertEqual(len(store.load_warnings), 1)
                self.assertIn("history.sqlite3.corrupt.bak", store.load_warnings[0])
                self.assertTrue(path.with_name("history.sqlite3.corrupt.bak").is_file())
                self.assertEqual((await store.list_images())["total"], 0)
            finally:
                await store.close()

    async def test_running_batch_is_marked_interrupted_after_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.sqlite3"
            store = HistoryStore(path)
            await store.create_batch("batch", 2, DEFAULT_SETTINGS)
            await store.close()
            reopened = HistoryStore(path)
            self.assertEqual((await reopened.get_batch("batch"))["status"], "interrupted")
            await reopened.close()


class BatchManagerTests(unittest.IsolatedAsyncioTestCase):
    @staticmethod
    def redraw_settings(**overrides):
        """RedrawCatalog 只在 random_* 为真时把该维度放进 selected,这里显式打开。"""
        settings = {
            **DEFAULT_SETTINGS,
            "count": 1,
            "random_character": True,
            "random_pose": True,
        }
        settings.update(overrides)
        return settings

    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.history = HistoryStore(Path(self.temp.name) / "history.sqlite3")
        self.comfy = FakeComfy()
        self.manager = BatchManager(FakeTemplates(), self.history, self.comfy)

    async def asyncTearDown(self):
        if self.manager.task and not self.manager.task.done():
            self.manager.task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await self.manager.task
        await self.history.close()
        self.temp.cleanup()

    async def test_generates_exact_count_sequentially(self):
        await self.manager.start({**DEFAULT_SETTINGS, "count": 3})
        result = await self.manager.wait()
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["completed"], 3)
        self.assertEqual([item["sequence"] for item in self.comfy.submissions], [1, 2, 3])
        self.assertTrue(all(item["filename_prefix"].endswith("/image") for item in self.comfy.submissions))
        self.assertEqual((await self.history.list_images())["total"], 3)

    async def test_second_start_is_queued_and_runs_after_first(self):
        # 0.2.0 起,运行中再开批次不再 409,而是进入队列自动接续。
        self.comfy.block = asyncio.Event()
        await self.manager.start({**DEFAULT_SETTINGS, "count": 2})
        await asyncio.sleep(0)
        queued_settings = {
            **DEFAULT_SETTINGS,
            "count": 1,
            "sampler_name": "euler",
            "scheduler": "karras",
        }
        self.comfy.available_samplers.append("euler")
        self.comfy.available_schedulers.append("karras")
        queued = await self.manager.start(queued_settings)
        self.assertEqual(queued["status"], "queued")
        self.assertEqual(queued["position"], 1)
        self.assertEqual(len(self.manager.queue), 1)
        self.assertEqual(self.manager.queue[0]["settings"]["sampler_name"], "euler")
        self.assertEqual(self.manager.queue[0]["settings"]["scheduler"], "karras")
        self.comfy.block.set()
        result = await self.manager.wait()
        # 队列自动接续:两个批次共 3 张图,全部按序生成
        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(self.comfy.submissions), 3)
        self.assertEqual(self.comfy.submissions[-1]["settings"]["sampler_name"], "euler")
        self.assertEqual(self.comfy.submissions[-1]["settings"]["scheduler"], "karras")
        self.assertEqual(len(self.manager.queue), 0)

    async def test_queue_is_full_at_limit(self):
        from anima_webui.runner import MAX_QUEUE

        self.comfy.block = asyncio.Event()
        await self.manager.start({**DEFAULT_SETTINGS, "count": 1})
        await asyncio.sleep(0)
        for _ in range(MAX_QUEUE):
            await self.manager.start({**DEFAULT_SETTINGS, "count": 1})
        with self.assertRaises(BatchConflict):
            await self.manager.start({**DEFAULT_SETTINGS, "count": 1})
        self.manager.queue.clear()
        self.comfy.block.set()
        await self.manager.wait()

    async def test_stop_clears_queue_by_default(self):
        self.comfy.block = asyncio.Event()
        state = await self.manager.start({**DEFAULT_SETTINGS, "count": 3})
        while not self.comfy.submissions:
            await asyncio.sleep(0)
        await self.manager.start({**DEFAULT_SETTINGS, "count": 5})
        self.assertEqual(len(self.manager.queue), 1)
        await self.manager.request_stop(state["id"])
        self.assertEqual(len(self.manager.queue), 0)
        self.comfy.block.set()
        result = await self.manager.wait()
        self.assertEqual(result["status"], "stopped")
        self.assertEqual(len(self.comfy.submissions), 1)

    async def test_stop_with_keep_queue_continues_next_batch(self):
        # 回归:clearQueue=false(只停当前批次)后,stop_requested 曾让
        # _advance_queue 直接返回,队列中的批次被永久卡死。
        self.comfy.block = asyncio.Event()
        self.comfy.honor_abort = True
        state = await self.manager.start({**DEFAULT_SETTINGS, "count": 3})
        while not self.comfy.submissions:
            await asyncio.sleep(0)
        await self.manager.start({**DEFAULT_SETTINGS, "count": 1})
        self.assertEqual(len(self.manager.queue), 1)
        await self.manager.request_stop(state["id"], clear_queue=False)
        self.comfy.block.set()
        result = await self.manager.wait()
        # 队列中的批次必须自动接续并跑完:最终状态来自接续批次
        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(self.manager.queue), 0)
        self.assertEqual(len(self.comfy.submissions), 2)
        self.assertEqual((await self.history.get_batch(state["id"]))["status"], "stopped")

    async def test_remove_queued_entry(self):
        self.comfy.block = asyncio.Event()
        await self.manager.start({**DEFAULT_SETTINGS, "count": 1})
        await asyncio.sleep(0)
        queued = await self.manager.start({**DEFAULT_SETTINGS, "count": 1})
        self.assertTrue(self.manager.remove_queued(queued["queue_id"]))
        self.assertFalse(self.manager.remove_queued("queue_missing"))
        self.assertEqual(self.manager.queue_snapshot(), [])
        self.comfy.block.set()
        await self.manager.wait()
        self.assertEqual(len(self.comfy.submissions), 1)

    async def test_start_race_during_validation_yields_serial_batches(self):
        # 回归 #P1-1(队列版):并发 start 被锁串行化,绝不出现两个 _run 并发;
        # 第二个进入队列并在第一个结束后自动接续。
        gate = asyncio.Event()
        original_lora_filenames = self.comfy.lora_filenames

        async def slow_lora_filenames():
            await gate.wait()
            return await original_lora_filenames()

        self.comfy.lora_filenames = slow_lora_filenames
        self.comfy.block = asyncio.Event()  # 让第一个批次保持运行,确保第二个进入队列
        first = asyncio.create_task(self.manager.start({**DEFAULT_SETTINGS, "count": 1}))
        second = asyncio.create_task(self.manager.start({**DEFAULT_SETTINGS, "count": 1}))
        await asyncio.sleep(0)
        gate.set()
        first_state = await first
        second_state = await second
        self.assertEqual(first_state["status"], "running")
        self.assertEqual(second_state["status"], "queued")
        self.comfy.block.set()
        await self.manager.wait()
        self.assertEqual(len(self.comfy.submissions), 2)
        self.assertEqual([item["sequence"] for item in self.comfy.submissions], [1, 1])

    async def test_progress_monitor_updates_state_and_preview(self):
        # 0.2.0:websocket 进度流应更新 state 里的采样进度并缓存预览帧。
        comfy = ProgressComfy()
        comfy.block = asyncio.Event()
        manager = BatchManager(FakeTemplates(), self.history, comfy)
        await manager.start({**DEFAULT_SETTINGS, "count": 1})
        for _ in range(500):
            if manager.preview is not None and manager.state.get("progress"):
                break
            await asyncio.sleep(0.01)
        self.assertEqual(manager.state["progress"], {"value": 12, "max": 30})
        seq, content_type, body = manager.preview
        self.assertEqual((content_type, body), ("image/jpeg", b"jpeg-frame"))
        self.assertEqual(manager.state["preview_id"], seq)
        comfy.block.set()
        comfy.release_stream.set()
        result = await manager.wait()
        self.assertEqual(result["status"], "completed")

    async def test_fixed_seeds_reproduce_submission(self):
        # 0.2.0:携带固定种子复现历史图片,提交给 ComfyUI 的种子必须一字不差。
        seeds = {"sample_seed": 123456789, "prompt_seed": 42}
        await self.manager.start({**DEFAULT_SETTINGS, "count": 1}, seeds=seeds)
        await self.manager.wait()
        self.assertEqual(self.comfy.submissions[0]["sample_seed"], 123456789)
        self.assertEqual(self.comfy.submissions[0]["prompt_seed"], 42)

    async def test_frozen_replay_bypasses_catalog_and_prompt_rules(self):
        manager = BatchManager(FakeTemplates(), self.history, self.comfy, FakeCatalog())
        regeneration = {
            "mode": "replay",
            "frozen_positive_prompt": "historical final prompt ",
            "frozen_negative_prompt": "historical negative ",
            "fixed_selection": {"pose": [{"id": "deleted", "title": "deleted"}]},
        }
        await manager.start(
            {**DEFAULT_SETTINGS, "count": 1},
            seeds={"sample_seed": 11, "prompt_seed": 12},
            regeneration=regeneration,
        )
        await manager.wait()
        submission = self.comfy.submissions[-1]
        self.assertEqual(submission["resolved_prompt"], "historical final prompt ")
        self.assertEqual(submission["frozen_positive_prompt"], "historical final prompt ")
        self.assertEqual(submission["sample_seed"], 11)
        self.assertEqual(submission["prompt_seed"], 12)
        image = (await self.history.list_images())["items"][0]
        self.assertEqual(image["positive_prompt"], "historical final prompt ")
        self.assertEqual(image["negative_prompt"], "historical negative ")

    async def test_content_redraw_keeps_unselected_dimensions_and_changes_selected(self):
        manager = BatchManager(FakeTemplates(), self.history, self.comfy, RedrawCatalog())
        original = {
            "character": [{"id": "character:old", "title": "character:old", "prompt": "character:old"}],
            "pose": [{"id": "pose:old", "title": "pose:old", "prompt": "pose:old"}],
        }
        regeneration = {
            "mode": "content_redraw",
            "redraw_sections": ["pose"],
            "fixed_selection": {"character": original["character"]},
            "original_selection": original,
        }
        await manager.start(self.redraw_settings(), regeneration=regeneration)
        await manager.wait()
        submitted = self.comfy.submissions[-1]
        self.assertEqual(submitted["resolved_selection"]["character"], original["character"])
        # 重抽维度必须换成与原图不同的姿势(候选含 old/new/other)。
        self.assertNotEqual(
            submitted["resolved_selection"]["pose"][0]["id"], "pose:old"
        )

    async def test_invalid_seeds_are_rejected(self):
        for bad in ({"sample_seed": -1, "prompt_seed": 1}, {"sample_seed": 1}, {"x": 1}, [1, 2], {"sample_seed": True, "prompt_seed": 1}):
            with self.subTest(seeds=bad):
                with self.assertRaises(ValueError):
                    await self.manager.start({**DEFAULT_SETTINGS, "count": 1}, seeds=bad)
        self.assertIsNone(self.manager.state)

    async def test_stop_during_wait_interrupts_comfy_and_stops(self):
        # 回归 #P1-3:等待渲染期间请求停止,应立即中断 ComfyUI 而不是等当前图完成。
        self.comfy.block = asyncio.Event()
        self.comfy.honor_abort = True
        state = await self.manager.start({**DEFAULT_SETTINGS, "count": 3})
        while not self.comfy.submissions:
            await asyncio.sleep(0)
        await self.manager.request_stop(state["id"])
        result = await self.manager.wait()
        self.assertEqual(result["status"], "stopped")
        self.assertEqual(result["completed"], 0)
        self.assertTrue(self.comfy.interrupted)
        self.assertEqual((await self.history.get_batch(state["id"]))["status"], "stopped")

    async def test_stop_finishes_current_image_then_stops(self):
        self.comfy.block = asyncio.Event()
        state = await self.manager.start({**DEFAULT_SETTINGS, "count": 3})
        while not self.comfy.submissions:
            await asyncio.sleep(0)
        await self.manager.request_stop(state["id"])
        self.comfy.block.set()
        result = await self.manager.wait()
        self.assertEqual(result["status"], "stopped")
        self.assertEqual(result["completed"], 1)
        self.assertEqual(len(self.comfy.submissions), 1)

    async def test_error_stops_without_retry(self):
        self.comfy.error_at = 2
        await self.manager.start({**DEFAULT_SETTINGS, "count": 4})
        result = await self.manager.wait()
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["completed"], 1)
        self.assertEqual(len(self.comfy.submissions), 2)
        self.assertIn("render failed", result["error"])

    async def test_history_uses_actual_comfy_prompt_when_catalog_is_present(self):
        manager = BatchManager(FakeTemplates(), self.history, self.comfy, FakeCatalog())

        await manager.start({**DEFAULT_SETTINGS, "count": 1})
        await manager.wait()

        image = (await self.history.list_images())["items"][0]
        self.assertEqual(image["positive_prompt"], "prompt 1")
        self.assertEqual(image["resolved_prompt"], "prompt 1")

    async def test_missing_lora_is_rejected_before_batch_creation(self):
        settings = {
            **DEFAULT_SETTINGS,
            "loras": [{"filename": "deleted.safetensors", "enabled": True, "strength": 1}],
        }

        with self.assertRaisesRegex(ValueError, "deleted.safetensors"):
            await self.manager.start(settings)

        self.assertIsNone(self.manager.state)
        self.assertEqual((await self.history.list_images())["total"], 0)

    async def test_missing_models_are_rejected_before_batch_creation(self):
        self.comfy.available_models = []
        with self.assertRaisesRegex(ValueError, "主模型不存在"):
            await self.manager.start(DEFAULT_SETTINGS)
        self.assertIsNone(self.manager.state)

        self.comfy.available_models = [DEFAULT_SETTINGS["model_name"]]
        self.comfy.available_upscalers = []
        with self.assertRaisesRegex(ValueError, "高清修复模型不存在"):
            await self.manager.start(DEFAULT_SETTINGS)
        self.assertIsNone(self.manager.state)

    async def test_second_sampler_resources_are_checked_when_enabled(self):
        settings = {
            **DEFAULT_SETTINGS,
            "second_sampler": {
                **DEFAULT_SETTINGS["second_sampler"],
                "enabled": True,
                "sampler_name": "euler",
                "scheduler": "karras",
            },
        }
        issues = await self.manager.resource_issues(settings)
        self.assertEqual(
            {(item["type"], item["name"]) for item in issues},
            {("second_sampler", "euler"), ("second_scheduler", "karras")},
        )
        self.comfy.available_samplers.append("euler")
        self.comfy.available_schedulers.append("karras")
        self.assertEqual(await self.manager.resource_issues(settings), [])

    async def test_missing_second_sampler_resources_are_rejected_only_when_enabled(self):
        settings = {
            **DEFAULT_SETTINGS,
            "second_sampler": {
                **DEFAULT_SETTINGS["second_sampler"],
                "enabled": True,
                "sampler_name": "euler",
                "scheduler": "karras",
            },
        }
        with self.assertRaisesRegex(ValueError, "2ndSampler Sampler 不可用"):
            await self.manager.start(settings)
        self.assertIsNone(self.manager.state)

        self.comfy.available_samplers.append("euler")
        with self.assertRaisesRegex(ValueError, "2ndSampler Scheduler 不可用"):
            await self.manager.start(settings)
        self.assertIsNone(self.manager.state)

        self.comfy.available_schedulers.append("karras")
        await self.manager.start(settings)
        await self.manager.wait()
        self.assertEqual(self.comfy.submissions[-1]["settings"]["second_sampler"]["enabled"], True)

    async def test_enabled_combination_rule_changes_submitted_selection(self):
        """本任务核心:真实 CombinationRuleStore 注入后,被禁组合不得进入提交载荷。"""
        store = CombinationRuleStore(Path(self.temp.name) / "combination_rules.json")
        rule = await store.create(
            {
                "picks": {
                    "character": {"id": "character:alpha", "label": "alpha"},
                    "clothing": {"id": "clothing:x", "label": "X"},
                }
            }
        )
        catalog = RuleAwareCatalog()
        manager = BatchManager(
            FakeTemplates(),
            self.history,
            self.comfy,
            catalog,
            combination_rules=store,
        )
        for prompt_seed in (0, 1, 2, 3, 4):
            with self.subTest(prompt_seed=prompt_seed):
                await manager.start(
                    {**DEFAULT_SETTINGS, "count": 1},
                    seeds={"sample_seed": 5, "prompt_seed": prompt_seed},
                )
                await manager.wait()
                submitted = self.comfy.submissions[-1]
                self.assertEqual(
                    [item["id"] for item in submitted["resolved_selection"]["clothing"]],
                    ["clothing:y"],
                )
                self.assertNotIn("clothing:x", submitted["resolved_prompt"])
        # 回调确实被调用过,且命中的正是这条规则:排除"规则根本没生效"的假通过。
        self.assertTrue(catalog.blocked_calls)
        self.assertEqual(
            {rule_id for _trial, rule_id in catalog.blocked_calls if rule_id},
            {rule["id"]},
        )

    async def test_same_seeds_without_rules_can_pick_blocked_combination(self):
        """对照组:同一种子下没有规则时必须能抽到 clothing:x,证明上一条断言有意义。"""
        catalog = RuleAwareCatalog()
        manager = BatchManager(FakeTemplates(), self.history, self.comfy, catalog)
        picked = set()
        for prompt_seed in (0, 1, 2, 3, 4):
            await manager.start(
                {**DEFAULT_SETTINGS, "count": 1},
                seeds={"sample_seed": 5, "prompt_seed": prompt_seed},
            )
            await manager.wait()
            picked.add(self.comfy.submissions[-1]["resolved_selection"]["clothing"][0]["id"])
        self.assertEqual(picked, {"clothing:x", "clothing:y"})
        self.assertEqual(catalog.blocked_calls, [])

    async def test_blocked_callback_is_omitted_when_no_store_is_configured(self):
        """未注入 store 时仍按旧签名调用 resolve_prompt,不能给外部目录替身传 blocked。"""
        catalog = RecordingCatalog()
        manager = BatchManager(FakeTemplates(), self.history, self.comfy, catalog)
        await manager.start({**DEFAULT_SETTINGS, "count": 1})
        await manager.wait()
        self.assertEqual(catalog.blocked_values, [None])
        self.assertIsNone(manager._blocked())

    async def test_redraw_catalog_honours_combination_rules(self):
        """RedrawCatalog 也吃 blocked:被禁姿势必须被换掉。"""
        store = CombinationRuleStore(Path(self.temp.name) / "redraw_rules.json")
        await store.create(
            {
                "picks": {
                    "character": {"id": "character:new", "label": "new"},
                    "pose": {"id": "pose:old", "label": "old"},
                }
            }
        )
        manager = BatchManager(
            FakeTemplates(),
            self.history,
            self.comfy,
            RedrawCatalog(),
            combination_rules=store,
        )
        for prompt_seed in (0, 2, 4):
            with self.subTest(prompt_seed=prompt_seed):
                await manager.start(
                    self.redraw_settings(),
                    seeds={"sample_seed": 3, "prompt_seed": prompt_seed},
                )
                await manager.wait()
                submitted = self.comfy.submissions[-1]
                self.assertNotEqual(
                    submitted["resolved_selection"]["pose"][0]["id"], "pose:old"
                )

    async def test_regeneration_redraw_also_respects_combination_rules(self):
        """content_redraw 走的是同一个 _resolve_catalog_prompt,规则同样必须生效。"""
        store = CombinationRuleStore(Path(self.temp.name) / "redraw_regeneration.json")
        await store.create(
            {
                "picks": {
                    "character": {"id": "character:new", "label": "new"},
                    "pose": {"id": "pose:old", "label": "old"},
                }
            }
        )
        manager = BatchManager(
            FakeTemplates(),
            self.history,
            self.comfy,
            RedrawCatalog(),
            combination_rules=store,
        )
        regeneration = {
            "mode": "content_redraw",
            "redraw_sections": ["pose"],
            "fixed_selection": {
                "character": [
                    {"id": "character:new", "title": "character:new", "prompt": "character:new"}
                ]
            },
            "original_selection": {
                "character": [
                    {"id": "character:new", "title": "character:new", "prompt": "character:new"}
                ],
                "pose": [{"id": "pose:old", "title": "pose:old", "prompt": "pose:old"}],
            },
        }
        await manager.start(self.redraw_settings(), regeneration=regeneration)
        await manager.wait()
        submitted = self.comfy.submissions[-1]
        self.assertNotEqual(
            submitted["resolved_selection"]["pose"][0]["id"], "pose:old"
        )

    async def test_content_redraw_rule_hits_a_dimension_that_is_not_redrawn(self):
        """回归:content_redraw 只重抽部分维度时,规则涉及固定维度也必须生效。

        此前 redraw_settings 把固定维度设成 random_*=False,resolve_prompt 因此
        不会把它们放进 selected,而 match() 要求规则里所有维度都命中 ——
        规则会静默失效,被禁组合照样进入提交载荷。

        original_selection 刻意设为 pose:new(而非被禁的 pose:old),这样"抽到
        pose:old"本身就构成 _changed,不会被"必须发生变化"的重试逻辑顺手排除,
        规则是否真的生效才有区分力。
        """
        store = CombinationRuleStore(Path(self.temp.name) / "redraw_fixed_dimension.json")
        rule = await store.create(
            {
                "picks": {
                    "character": {"id": "character:new", "label": "new"},
                    "pose": {"id": "pose:old", "label": "old"},
                }
            }
        )
        manager = BatchManager(
            FakeTemplates(),
            self.history,
            self.comfy,
            RedrawCatalog(),
            combination_rules=store,
        )
        fixed_character = [
            {"id": "character:new", "title": "character:new", "prompt": "character:new"}
        ]
        regeneration = {
            "mode": "content_redraw",
            "redraw_sections": ["pose"],
            "fixed_selection": {"character": fixed_character},
            "original_selection": {
                "character": fixed_character,
                "pose": [{"id": "pose:new", "title": "pose:new", "prompt": "pose:new"}],
            },
        }
        for prompt_seed in (0, 1, 2, 3):
            with self.subTest(prompt_seed=prompt_seed):
                await manager.start(
                    self.redraw_settings(),
                    seeds={"sample_seed": 3, "prompt_seed": prompt_seed},
                    regeneration=regeneration,
                )
                await manager.wait()
                submitted = self.comfy.submissions[-1]
                self.assertNotIn(
                    "pose:old",
                    [item["id"] for item in submitted["resolved_selection"]["pose"]],
                )
                self.assertNotIn("pose:old", submitted["resolved_prompt"])
        self.assertEqual(store.list()["items"][0]["id"], rule["id"])

    async def test_content_redraw_rule_exhaustion_raises_catalog_error_with_rule_id(self):
        """拦住不了就必须报错点名规则 id,不能静默返回被禁组合。"""
        store = CombinationRuleStore(Path(self.temp.name) / "redraw_exhausted.json")
        rule_ids = []
        # 三个候选姿势全部被禁 -> resolve_prompt 的重抽必然用尽,必须显式报错。
        for pose_id in ("pose:old", "pose:new", "pose:other"):
            rule = await store.create(
                {
                    "picks": {
                        "character": {"id": "character:new", "label": "new"},
                        "pose": {"id": pose_id, "label": pose_id},
                    }
                }
            )
            rule_ids.append(rule["id"])
        manager = BatchManager(
            FakeTemplates(),
            self.history,
            self.comfy,
            RedrawCatalog(),
            combination_rules=store,
        )
        fixed_character = [
            {"id": "character:new", "title": "character:new", "prompt": "character:new"}
        ]
        regeneration = {
            "mode": "content_redraw",
            "redraw_sections": ["pose"],
            "fixed_selection": {"character": fixed_character},
            "original_selection": {
                "character": fixed_character,
                "pose": [{"id": "pose:new", "title": "pose:new", "prompt": "pose:new"}],
            },
        }
        await manager.start(
            self.redraw_settings(),
            seeds={"sample_seed": 3, "prompt_seed": 1},
            regeneration=regeneration,
        )
        result = await manager.wait()
        self.assertEqual(result["status"], "error")
        self.assertTrue(
            any(rule_id in result["error"] for rule_id in rule_ids),
            f"错误信息应点名规则 id,实际为: {result['error']}",
        )
        self.assertEqual(self.comfy.submissions, [])

    async def test_replay_does_not_consult_combination_rules(self):
        """replay 是"复现原图":规则后来新增也必须能回放。

        该用例有区分力:若 replay 误走 resolve_prompt 或误做规则复检,
        RedrawCatalog 会把 pose 换成非 old 的值、甚至因规则耗尽而报错,
        下面的断言(照抄历史 selection 且 completed)就会失败。
        """
        store = CombinationRuleStore(Path(self.temp.name) / "replay_rules.json")
        await store.create(
            {
                "picks": {
                    "character": {"id": "character:old", "label": "old"},
                    "pose": {"id": "pose:old", "label": "old"},
                }
            }
        )
        # RedrawCatalog 的调用次数用来证明 replay 完全没有进抽取路径。
        catalog = RedrawCatalog()
        calls = []
        original_resolve = catalog.resolve_prompt

        def tracking_resolve(settings, prompt_seed, blocked=None):
            calls.append(blocked)
            return original_resolve(settings, prompt_seed, blocked=blocked)

        catalog.resolve_prompt = tracking_resolve
        manager = BatchManager(
            FakeTemplates(),
            self.history,
            self.comfy,
            catalog,
            combination_rules=store,
        )
        historical = {
            "character": [{"id": "character:old", "title": "old", "prompt": "old"}],
            "pose": [{"id": "pose:old", "title": "old", "prompt": "old"}],
        }
        regeneration = {
            "mode": "replay",
            "frozen_positive_prompt": "historical final prompt ",
            "frozen_negative_prompt": "historical negative ",
            "fixed_selection": historical,
        }
        await manager.start(
            {**DEFAULT_SETTINGS, "count": 1},
            seeds={"sample_seed": 1, "prompt_seed": 2},
            regeneration=regeneration,
        )
        result = await manager.wait()
        self.assertEqual(result["status"], "completed")
        # replay 不抽取:目录一次都不该被调用。
        self.assertEqual(calls, [])
        submitted = self.comfy.submissions[-1]
        self.assertEqual(submitted["resolved_selection"], historical)
        self.assertEqual(submitted["resolved_prompt"], "historical final prompt ")


class ContentRedrawRealCatalogTests(unittest.IsolatedAsyncioTestCase):
    """用真实 PromptCatalog 覆盖 content_redraw + 组合规则(替身可能掩盖语义差异)。"""

    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        tools = root / "tools"
        js = tools / "js"
        js.mkdir(parents=True)
        datasets = {
            "character_data.js": [
                {"name": "alpha", "copyright": "series", "gender": "1girl", "hair": "blue", "eye": "red", "post_count": 5},
            ],
            "clothing_data.js": [
                {"id": "x", "name": "X", "name_zh": "X装", "tags": "x-tag", "categories": ["日常/休闲 (Casual & Daily)"], "traits": ["red"]},
                {"id": "y", "name": "Y", "name_zh": "Y装", "tags": "y-tag", "categories": ["日常/休闲 (Casual & Daily)"], "traits": ["red"]},
                {"id": "z", "name": "Z", "name_zh": "Z装", "tags": "z-tag", "categories": ["日常/休闲 (Casual & Daily)"], "traits": ["red"]},
            ],
            "pose_data.js": [
                {"id": "stand", "name": "Standing", "name_zh": "站立", "tags": "standing", "categories": ["站立与动态 (Standing & Dynamic)"], "traits": ["standing"]},
            ],
            "background_data.js": [
                {"id": "room", "name": "Room", "name_zh": "房间", "tags": "indoors", "categories": ["都市与日常 (Urban & Daily)"], "traits": ["indoor"]},
            ],
        }
        for filename, values in datasets.items():
            (js / filename).write_text(
                f"const data = {json.dumps(values, ensure_ascii=False)};\n",
                encoding="utf-8",
            )
        self.catalog = PromptCatalog(root, tools)
        self.history = HistoryStore(root / "history.sqlite3")
        self.comfy = FakeComfy()
        self.rules_path = root / "combination_rules.json"

    async def asyncTearDown(self):
        await self.history.close()
        self.temp.cleanup()

    def _settings(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings.update(
            {
                "count": 1,
                "random_character": False,
                "fixed_character": "alpha, series",
                "random_clothing": True,
                "pools": {
                    "character": {"mode": "include", "ids": [], "excluded_ids": []},
                    "clothing": {
                        "mode": "include",
                        "ids": ["clothing:x", "clothing:y", "clothing:z"],
                        "excluded_ids": [],
                    },
                    "pose": {"mode": "include", "ids": [], "excluded_ids": []},
                    "background": {"mode": "include", "ids": [], "excluded_ids": []},
                    "expression": {"mode": "include", "ids": [], "excluded_ids": []},
                },
            }
        )
        return settings

    def _regeneration(self, fixed_character):
        # original_selection 刻意用未被禁的 clothing:z(而非被禁的 clothing:x):
        # 这样"抽到 clothing:x"本身就满足 _changed,不会被"必须发生改变"的
        # 重试逻辑顺手排除,规则是否真的生效因此有区分力。
        return {
            "mode": "content_redraw",
            "redraw_sections": ["clothing"],
            "fixed_selection": {"character": fixed_character},
            "original_selection": {
                "character": fixed_character,
                "clothing": [{"id": "clothing:z", "title": "Z", "prompt": "z-tag"}],
            },
        }

    async def test_fixed_character_rule_blocks_clothing_under_real_catalog(self):
        """固定角色 + 随机服装:规则必须真的把被禁服装换掉。"""
        store = CombinationRuleStore(self.rules_path)
        await store.create(
            {
                "picks": {
                    "character": {"id": "character:alpha||series", "label": "alpha"},
                    "clothing": {"id": "clothing:x", "label": "X"},
                }
            }
        )
        manager = BatchManager(
            FakeTemplates(),
            self.history,
            self.comfy,
            self.catalog,
            combination_rules=store,
        )
        fixed_character = [
            self.catalog.get("character:alpha||series"),
        ]
        for prompt_seed in (1, 2, 3, 4, 5, 6, 7, 8):
            with self.subTest(prompt_seed=prompt_seed):
                await manager.start(
                    self._settings(),
                    seeds={"sample_seed": 9, "prompt_seed": prompt_seed},
                    regeneration=self._regeneration(fixed_character),
                )
                await manager.wait()
                submitted = self.comfy.submissions[-1]
                ids = [
                    item["id"]
                    for item in submitted["resolved_selection"]["clothing"]
                ]
                self.assertNotIn("clothing:x", ids)
                self.assertNotIn("x-tag", submitted["resolved_prompt"])

    async def test_exhausted_candidates_raise_error_naming_rule(self):
        """所有候选都被规则禁掉时必须报错并点名规则 id,不能交出被禁组合。"""
        store = CombinationRuleStore(self.rules_path)
        rule_ids = []
        for clothing_id in ("clothing:x", "clothing:y", "clothing:z"):
            rule = await store.create(
                {
                    "picks": {
                        "character": {"id": "character:alpha||series", "label": "alpha"},
                        "clothing": {"id": clothing_id, "label": clothing_id},
                    }
                }
            )
            rule_ids.append(rule["id"])
        manager = BatchManager(
            FakeTemplates(),
            self.history,
            self.comfy,
            self.catalog,
            combination_rules=store,
        )
        fixed_character = [self.catalog.get("character:alpha||series")]
        await manager.start(
            self._settings(),
            seeds={"sample_seed": 9, "prompt_seed": 1},
            regeneration=self._regeneration(fixed_character),
        )
        result = await manager.wait()
        self.assertEqual(result["status"], "error")
        self.assertTrue(
            any(rule_id in result["error"] for rule_id in rule_ids),
            f"错误信息应点名规则 id,实际为: {result['error']}",
        )
        self.assertEqual(self.comfy.submissions, [])

    async def test_plain_batch_rule_blocks_fixed_character_pairing(self):
        """普通批次 + 固定角色 + 随机服装:规则必须生效(此前普通路径不传 pinned)。"""
        store = CombinationRuleStore(self.rules_path / "plain_rules.json")
        rule = await store.create(
            {
                "picks": {
                    "character": {"text": "alpha, series", "label": "固定角色"},
                    "clothing": {"id": "clothing:x", "label": "X"},
                }
            }
        )
        manager = BatchManager(
            FakeTemplates(),
            self.history,
            self.comfy,
            self.catalog,
            combination_rules=store,
        )
        for prompt_seed in (1, 2, 3, 4, 5, 6, 7, 8):
            with self.subTest(prompt_seed=prompt_seed):
                await manager.start(
                    self._settings(),
                    seeds={"sample_seed": 9, "prompt_seed": prompt_seed},
                )
                await manager.wait()
                submitted = self.comfy.submissions[-1]
                ids = [
                    item["id"]
                    for item in submitted["resolved_selection"]["clothing"]
                ]
                self.assertNotIn("clothing:x", ids)
                self.assertNotIn("x-tag", submitted["resolved_prompt"])
        self.assertEqual(store.list()["items"][0]["id"], rule["id"])

    async def test_plain_batch_exhaustion_raises_error_naming_rule(self):
        """普通批次下候选全被禁也必须报错,而不是安静交出被禁组合。"""
        store = CombinationRuleStore(self.rules_path / "plain_exhausted.json")
        rule_ids = []
        for clothing_id in ("clothing:x", "clothing:y", "clothing:z"):
            rule = await store.create(
                {
                    "picks": {
                        "character": {"text": "alpha, series", "label": "固定角色"},
                        "clothing": {"id": clothing_id, "label": clothing_id},
                    }
                }
            )
            rule_ids.append(rule["id"])
        manager = BatchManager(
            FakeTemplates(),
            self.history,
            self.comfy,
            self.catalog,
            combination_rules=store,
        )
        await manager.start(
            self._settings(),
            seeds={"sample_seed": 9, "prompt_seed": 1},
        )
        result = await manager.wait()
        self.assertEqual(result["status"], "error")
        self.assertTrue(
            any(rule_id in result["error"] for rule_id in rule_ids),
            f"错误信息应点名规则 id,实际为: {result['error']}",
        )
        self.assertEqual(self.comfy.submissions, [])

    async def test_same_rule_blocks_consistently_across_all_paths(self):
        """同一份规则在普通批次 / content_redraw / settings_reroll 上行为必须一致。"""
        store = CombinationRuleStore(self.rules_path / "consistency_rules.json")
        await store.create(
            {
                "picks": {
                    "character": {"text": "alpha, series", "label": "固定角色"},
                    "clothing": {"id": "clothing:x", "label": "X"},
                }
            }
        )
        fixed_character = [self.catalog.get("character:alpha||series")]
        results = {}
        for label, kwargs in (
            ("plain", {}),
            ("content_redraw", {"regeneration": self._regeneration(fixed_character)}),
            (
                "settings_reroll",
                {"regeneration": {"mode": "settings_reroll"}},
            ),
        ):
            manager = BatchManager(
                FakeTemplates(),
                self.history,
                self.comfy,
                self.catalog,
                combination_rules=store,
            )
            blocked_any = []
            for prompt_seed in (1, 2, 3, 4, 5):
                await manager.start(
                    self._settings(),
                    seeds={"sample_seed": 9, "prompt_seed": prompt_seed},
                    **kwargs,
                )
                await manager.wait()
                submitted = self.comfy.submissions[-1]
                ids = [
                    item["id"]
                    for item in submitted["resolved_selection"].get("clothing", [])
                ]
                blocked_any.append("clothing:x" in ids)
            results[label] = any(blocked_any)
        self.assertEqual(
            results,
            {"plain": False, "content_redraw": False, "settings_reroll": False},
            f"被禁服装在以下路径出现: {results}",
        )


if __name__ == "__main__":
    unittest.main()
