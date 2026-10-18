from __future__ import annotations

import asyncio
import copy
import logging
import secrets
import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

from .comfy import ComfyAborted, ComfyError, extract_images, extract_positive_prompt
from .catalog import PromptCatalog, fixed_selection_item
from .combination_rules import CombinationRuleStore
from .history import HistoryStore
from .prompt_rules import PromptRuleStore
from .workflow import MAX_SAMPLE_SEED, WorkflowError, WorkflowTemplates, validate_loras, validate_settings


logger = logging.getLogger(__name__)


class BatchConflict(RuntimeError):
    pass


MAX_QUEUE = 20
REGENERATION_MODES = {"replay", "prompt_variant", "content_redraw", "settings_reroll"}
PROMPT_SECTIONS = ("character", "clothing", "pose", "background", "expression")


def validate_seeds(value: Any) -> dict[str, int] | None:
    """校验复现用的固定种子。None 表示每张图随机(默认行为)。"""
    if value is None:
        return None
    if not isinstance(value, dict):
        raise WorkflowError("seeds 必须是对象")
    unknown = set(value) - {"sample_seed", "prompt_seed"}
    if unknown:
        raise WorkflowError(f"seeds 包含未知参数: {', '.join(sorted(unknown))}")
    result: dict[str, int] = {}
    for name, maximum in (("sample_seed", MAX_SAMPLE_SEED), ("prompt_seed", 2**31 - 1)):
        raw = value.get(name)
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise WorkflowError(f"seeds.{name} 必须是整数")
        if not 0 <= raw <= maximum:
            raise WorkflowError(f"seeds.{name} 必须在 0-{maximum} 之间")
        result[name] = raw
    return result


class BatchManager:
    def __init__(
        self,
        templates: WorkflowTemplates,
        history: HistoryStore,
        comfy: Any,
        catalog: PromptCatalog | None = None,
        prompt_rules: PromptRuleStore | None = None,
        combination_rules: CombinationRuleStore | None = None,
    ):
        self.templates = templates
        self.history = history
        self.comfy = comfy
        self.task: asyncio.Task[None] | None = None
        self.state: dict[str, Any] | None = None
        self.stop_requested = False
        self.client_id = str(uuid.uuid4())
        self.catalog = catalog
        self.prompt_rules = prompt_rules
        self.combination_rules = combination_rules
        # 排队中的批次(仅内存;WebUI 重启后队列清空,历史记录只在真正开跑时创建)。
        self.queue: list[dict[str, Any]] = []
        self.shutting_down = False
        # 实时进度:由 _monitor_progress 通过 ComfyUI websocket 更新。
        self.preview: tuple[int, str, bytes] | None = None
        self._monitor_task: asyncio.Task[None] | None = None
        self._preview_seq = 0
        # start 里的资源校验要 await 多次 ComfyUI 请求,期间若不上锁,
        # 第二个并发 start 也能通过 active() 检查并启动重复批次。
        self._start_lock = asyncio.Lock()

    def active(self) -> bool:
        return bool(self.task and not self.task.done())

    def _blocked(self) -> Callable[[dict[str, list[dict[str, Any]]]], str | None] | None:
        """返回给 resolve_prompt 的组合规则回调;未配置规则时返回 None(完全保持旧行为)。"""
        rules = self.combination_rules
        if rules is None:
            return None
        return rules.match

    @staticmethod
    def _fixed_pinned(
        settings: dict[str, Any],
    ) -> dict[str, list[dict[str, Any]]] | None:
        """把固定提示词维度整理成 pinned 结构,供组合规则匹配。

        固定维度不参与随机抽取,但用户完全可能"固定角色 + 随机服装"后
        想在图上禁用某个搭配。伪条目由 catalog.fixed_selection_item() 统一
        生成,与写进 selected 的条目**是同一个函数**,因此固定维度在所有
        抽取路径上的形状与规则行为必然一致(不会出现两处结构漂移)。

        形状对齐 catalog 条目,但**不假设 tag 顺序**:用户完全可能把
        fixed_character 写成 "1girl, alpha"(通用标签在前、角色名在后),
        若把 title 设为第一个 tag,规则 text="alpha" 的主身份判据就会因为
        primary={1girl} 而永不命中,规则静默失效。因此 title 直接放完整原文、
        tags 保留全部 tag,由 _pick_hit 对 fixed 伪条目用"完整 tag 集"判身份。

        已知差异:这里直接用 settings["fixed_<section>"] 原文,而 workflow.py
        提交时对 character 走 get_resolved_tags()(character_detail="trigger"
        时只保留触发词)。即 pinned 文本可能比实际提交的更长,匹配只会更宽松,
        不会漏禁;若将来要求逐字一致,需在此复用 workflow 的拼装口径。
        """
        pinned: dict[str, list[dict[str, Any]]] = {}
        for section in PROMPT_SECTIONS:
            if settings.get(f"random_{section}"):
                continue
            fixed_text = str(settings.get(f"fixed_{section}") or "").strip()
            if not fixed_text:
                continue
            pinned[section] = [fixed_selection_item(section, fixed_text)]
        return pinned or None

    def _resolve_catalog_prompt(
        self,
        settings: dict[str, Any],
        prompt_seed: int,
        pinned: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """按当前配置抽取提示词。

        只有在确实配置了组合规则时才传 blocked,未配置时保持旧调用形态:
        这样按旧签名实现的目录替身/外部插件不会被新关键字参数打挂,
        resolve_prompt 的 blocked 也因此始终是可选参数。

        pinned 用于 content_redraw:未重抽的维度在 resolve_prompt 内部会被
        `random_*=False` 跳过,因而恒不出现在它构造的 selection 里,而
        CombinationRuleStore.match() 要求规则里所有维度都命中。把已固定的
        条目并进 trial 再交给 blocked,规则才能对固定维度生效,同时仍复用
        resolve_prompt 自己的"换种子重抽 + 用尽报错"语义。
        """
        blocked = self._blocked()
        if blocked is None:
            return self.catalog.resolve_prompt(settings, prompt_seed)
        if not pinned:
            return self.catalog.resolve_prompt(settings, prompt_seed, blocked=blocked)

        def blocked_with_pinned(trial: dict[str, list[dict[str, Any]]]) -> str | None:
            merged = {**trial, **copy.deepcopy(pinned)}
            return blocked(merged)

        return self.catalog.resolve_prompt(
            settings, prompt_seed, blocked=blocked_with_pinned
        )

    @staticmethod
    def _validate_regeneration(value: Any) -> dict[str, Any] | None:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise WorkflowError("regeneration 必须是对象")
        unknown = set(value) - {
            "mode",
            "frozen_positive_prompt",
            "frozen_negative_prompt",
            "fixed_selection",
            "redraw_sections",
            "original_selection",
            "prompt_seed",
        }
        if unknown:
            raise WorkflowError(
                f"regeneration 包含未知参数: {', '.join(sorted(unknown))}"
            )
        mode = value.get("mode")
        if mode not in REGENERATION_MODES:
            raise WorkflowError("regeneration.mode 无效")
        result = copy.deepcopy(value)
        result["mode"] = mode
        if mode in {"replay", "prompt_variant"}:
            positive = str(value.get("frozen_positive_prompt") or "")
            if not positive.strip():
                raise WorkflowError("历史记录缺少可回放的最终正向提示词")
            result["frozen_positive_prompt"] = positive
            result["frozen_negative_prompt"] = str(
                value.get("frozen_negative_prompt") or ""
            )
            fixed_selection = value.get("fixed_selection") or {}
            if not isinstance(fixed_selection, dict):
                raise WorkflowError("regeneration.fixed_selection 必须是对象")
            result["fixed_selection"] = copy.deepcopy(fixed_selection)
            if mode == "prompt_variant":
                prompt_seed = value.get("prompt_seed")
                if isinstance(prompt_seed, bool) or not isinstance(prompt_seed, int):
                    raise WorkflowError("regeneration.prompt_seed 必须是整数")
                if not 0 <= prompt_seed <= 2**31 - 1:
                    raise WorkflowError("regeneration.prompt_seed 超出范围")
                result["prompt_seed"] = prompt_seed
        elif mode == "content_redraw":
            sections = value.get("redraw_sections")
            if not isinstance(sections, list) or not sections:
                raise WorkflowError("content_redraw 至少选择一个重抽维度")
            if any(not isinstance(section, str) for section in sections):
                raise WorkflowError("regeneration.redraw_sections 必须是字符串数组")
            if len(sections) != len(set(sections)):
                raise WorkflowError("重抽维度不能重复")
            invalid = set(sections) - set(PROMPT_SECTIONS)
            if invalid:
                raise WorkflowError(f"不支持的重抽维度: {', '.join(sorted(invalid))}")
            fixed_selection = value.get("fixed_selection") or {}
            original_selection = value.get("original_selection") or {}
            if not isinstance(fixed_selection, dict) or not isinstance(
                original_selection, dict
            ):
                raise WorkflowError("历史实际抽取结果无效")
            result["redraw_sections"] = list(sections)
            result["fixed_selection"] = copy.deepcopy(fixed_selection)
            result["original_selection"] = copy.deepcopy(original_selection)
        return result

    async def resource_issues(self, overrides: dict[str, Any]) -> list[dict[str, str]]:
        settings = validate_settings(overrides)
        issues: list[dict[str, str]] = []
        lora_filenames = getattr(self.comfy, "lora_filenames", None)
        available_loras = {
            str(value).replace("\\", "/").casefold(): str(value)
            for value in await lora_filenames()
        } if lora_filenames else {}
        for item in settings["loras"]:
            if item["enabled"] and item["filename"].replace("\\", "/").casefold() not in available_loras:
                issues.append({"type": "lora", "name": item["filename"], "label": "LoRA"})
        resource_inventory = getattr(self.comfy, "resource_inventory", None)
        if resource_inventory:
            resources = await resource_inventory()
            checks = [
                ("model", "主模型", settings["model_name"], resources.get("models", [])),
                ("sampler", "Sampler", settings["sampler_name"], resources.get("samplers", [])),
                ("scheduler", "Scheduler", settings["scheduler"], resources.get("schedulers", [])),
            ]
            if settings["second_sampler"]["enabled"]:
                checks.extend(
                    [
                        (
                            "second_sampler",
                            "2ndSampler Sampler",
                            settings["second_sampler"]["sampler_name"],
                            resources.get("samplers", []),
                        ),
                        (
                            "second_scheduler",
                            "2ndSampler Scheduler",
                            settings["second_sampler"]["scheduler"],
                            resources.get("schedulers", []),
                        ),
                    ]
                )
            if settings["hires"]["enabled"]:
                checks.append(
                    (
                        "upscale_model",
                        "高清模型",
                        settings["hires"]["model_name"],
                        resources.get("upscale_models", []),
                    )
                )
            for kind, label, name, available in checks:
                if name not in available:
                    issues.append({"type": kind, "name": name, "label": label})
        return issues

    async def start(
        self,
        overrides: dict[str, Any],
        seeds: dict[str, int] | None = None,
        regeneration: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        async with self._start_lock:
            regeneration = self._validate_regeneration(regeneration)
            normalized_overrides = overrides
            if self.prompt_rules is not None and not (
                regeneration and regeneration.get("frozen_positive_prompt")
            ):
                normalized_overrides, _ = self.prompt_rules.normalize_settings(overrides)
            settings = validate_settings(normalized_overrides)
            seeds = validate_seeds(seeds)
            if self.catalog and not (
                regeneration and regeneration.get("frozen_positive_prompt")
            ):
                self.catalog.validate_settings(settings)
            lora_filenames = getattr(self.comfy, "lora_filenames", None)
            if not lora_filenames:
                raise ComfyError("ComfyUI 客户端无法读取 LoRA 列表")
            settings["loras"] = validate_loras(settings, await lora_filenames())
            resource_inventory = getattr(self.comfy, "resource_inventory", None)
            if resource_inventory:
                resources = await resource_inventory()
                if settings["model_name"] not in resources.get("models", []):
                    raise WorkflowError(f"主模型不存在: {settings['model_name']}")
                if settings["hires"]["enabled"] and settings["hires"]["model_name"] not in resources.get("upscale_models", []):
                    raise WorkflowError(f"高清修复模型不存在: {settings['hires']['model_name']}")
                if settings["sampler_name"] not in resources.get("samplers", []):
                    raise WorkflowError(f"Sampler 不可用: {settings['sampler_name']}")
                if settings["scheduler"] not in resources.get("schedulers", []):
                    raise WorkflowError(f"Scheduler 不可用: {settings['scheduler']}")
                if settings["second_sampler"]["enabled"]:
                    second_sampler = settings["second_sampler"]
                    if second_sampler["sampler_name"] not in resources.get("samplers", []):
                        raise WorkflowError(f"2ndSampler Sampler 不可用: {second_sampler['sampler_name']}")
                    if second_sampler["scheduler"] not in resources.get("schedulers", []):
                        raise WorkflowError(f"2ndSampler Scheduler 不可用: {second_sampler['scheduler']}")
            if self.active():
                # 有批次在跑:进入队列,当前批次结束后自动接续。
                if len(self.queue) >= MAX_QUEUE:
                    raise BatchConflict(f"队列已满(最多 {MAX_QUEUE} 个)")
                entry = {
                    "queue_id": f"queue_{uuid.uuid4().hex[:8]}",
                    "settings": settings,
                    "seeds": seeds,
                    "regeneration": regeneration,
                }
                self.queue.append(entry)
                return {
                    "status": "queued",
                    "queue_id": entry["queue_id"],
                    "position": len(self.queue),
                    "count": settings["count"],
                }
            await self._begin_batch(settings, seeds, regeneration)
            return self.snapshot()

    async def _begin_batch(
        self,
        settings: dict[str, Any],
        seeds: dict[str, int] | None,
        regeneration: dict[str, Any] | None = None,
    ) -> None:
        batch_id = uuid.uuid4().hex[:12]
        self.stop_requested = False
        self.preview = None
        self.state = {
            "id": batch_id,
            "status": "running",
            "total": settings["count"],
            "completed": 0,
            "current": 0,
            "prompt_id": "",
            "error": "",
            "settings": settings,
        }
        await self.history.create_batch(batch_id, settings["count"], settings)
        self.task = asyncio.create_task(self._run(batch_id, settings, seeds, regeneration))
        self._ensure_monitor()

    def queue_snapshot(self) -> list[dict[str, Any]]:
        return [
            {
                "queue_id": entry["queue_id"],
                "position": index + 1,
                "count": entry["settings"]["count"],
                "model_name": entry["settings"]["model_name"],
            }
            for index, entry in enumerate(self.queue)
        ]

    def remove_queued(self, queue_id: str) -> bool:
        previous = len(self.queue)
        self.queue = [entry for entry in self.queue if entry["queue_id"] != queue_id]
        return len(self.queue) < previous

    def snapshot(self) -> dict[str, Any] | None:
        return dict(self.state) if self.state else None

    async def request_stop(self, batch_id: str, clear_queue: bool = True) -> dict[str, Any]:
        if not self.state or self.state["id"] != batch_id:
            raise KeyError(batch_id)
        if clear_queue:
            self.queue.clear()
        if self.active():
            self.stop_requested = True
            self.state["status"] = "stopping"
            await self.history.update_batch(batch_id, status="stopping")
        return self.snapshot()

    async def wait(self) -> dict[str, Any] | None:
        # 队列自动接续会替换 self.task,循环等待直到全部批次收尾。
        while self.task and not self.task.done():
            await self.task
            await asyncio.sleep(0)
        return self.snapshot()

    async def _run(
        self,
        batch_id: str,
        settings: dict[str, Any],
        seeds: dict[str, int] | None = None,
        regeneration: dict[str, Any] | None = None,
    ) -> None:
        # settings 在批次内不变,固定维度的 pinned 结构只需算一次。
        fixed_pinned = self._fixed_pinned(settings)
        try:
            for sequence in range(1, settings["count"] + 1):
                if self.stop_requested:
                    break
                # 固定种子用于复现历史图片;未指定时每张随机。
                sample_seed = seeds["sample_seed"] if seeds else secrets.randbelow(MAX_SAMPLE_SEED + 1)
                prompt_seed = (
                    seeds["prompt_seed"]
                    if seeds
                    else regeneration.get("prompt_seed")
                    if regeneration and regeneration.get("mode") == "prompt_variant"
                    else secrets.randbelow(2**31)
                )
                date_folder = datetime.now().strftime("%Y-%m-%d")
                prefix = f"AnimaRandom/{date_folder}/{batch_id}/image"
                resolved = self._resolve_regeneration(settings, prompt_seed, regeneration) if regeneration else (
                    self._resolve_catalog_prompt(
                        settings,
                        prompt_seed,
                        pinned=fixed_pinned,
                    ) if self.catalog else {
                        "composer_prompt": "",
                        "full_prompt": "",
                        "selected": {},
                    }
                )
                if regeneration and regeneration.get("mode") == "content_redraw":
                    for attempt in range(512):
                        candidate_seed = (prompt_seed + attempt) % (2**31)
                        resolved = self._resolve_regeneration(
                            settings, candidate_seed, regeneration
                        )
                        if resolved.pop("_changed", False):
                            prompt_seed = candidate_seed
                            break
                    else:
                        raise WorkflowError("所选维度无可用替代组合")
                if self.prompt_rules is not None and not (
                    regeneration and regeneration.get("frozen_positive_prompt")
                ):
                    protected = settings.get("lora_managed_triggers", [])
                    composer_prompt, _ = self.prompt_rules.normalize_text(
                        resolved["composer_prompt"],
                        "positive",
                        protected_lora_words=protected,
                    )
                    full_prompt, _ = self.prompt_rules.normalize_text(
                        resolved["full_prompt"],
                        "positive",
                        protected_lora_words=protected,
                    )
                    resolved = {
                        **resolved,
                        "composer_prompt": composer_prompt,
                        "full_prompt": full_prompt,
                    }
                submission_args = (
                    settings, sample_seed, prompt_seed, prefix, self.client_id, sequence
                )
                if self.catalog:
                    payload = self.templates.submission(
                        *submission_args,
                        resolved_prompt=resolved["composer_prompt"],
                        resolved_selection=resolved["selected"],
                        resolved_prompt_full=resolved["full_prompt"],
                        frozen_positive_prompt=(regeneration or {}).get(
                            "frozen_positive_prompt", ""
                        ),
                        frozen_negative_prompt=(regeneration or {}).get(
                            "frozen_negative_prompt", ""
                        ),
                    )
                else:
                    payload = self.templates.submission(*submission_args)
                self.state["current"] = sequence
                prompt_id = await self.comfy.submit(payload)
                self.state["prompt_id"] = prompt_id
                try:
                    entry = await self.comfy.wait_for_history(
                        prompt_id, should_abort=lambda: self.stop_requested
                    )
                except ComfyAborted:
                    await self._interrupt_current()
                    break
                images = extract_images(entry)
                if not images:
                    raise ComfyError("任务完成但未返回保存图片")
                frozen_positive = (regeneration or {}).get("frozen_positive_prompt", "")
                frozen_negative = (regeneration or {}).get("frozen_negative_prompt", "")
                positive = frozen_positive or extract_positive_prompt(entry)
                for image in images:
                    await self.history.add_image(
                        batch_id=batch_id,
                        sequence=sequence,
                        prompt_id=prompt_id,
                        image=image,
                        positive_prompt=positive,
                        negative_prompt=frozen_negative or settings["negative_prompt"],
                        sample_seed=sample_seed,
                        prompt_seed=prompt_seed,
                        settings=settings,
                        resolved_selection=resolved["selected"],
                        resolved_prompt=positive or resolved["full_prompt"],
                    )
                self.state["completed"] = sequence
                await self.history.update_batch(batch_id, completed=sequence)
                if self.stop_requested:
                    break

            status = "stopped" if self.stop_requested else "completed"
            self.state["status"] = status
            await self.history.update_batch(batch_id, completed=self.state["completed"], status=status)
        except Exception as error:
            logger.warning("批次 %s 出错: %s", batch_id, error)
            self.state["status"] = "error"
            self.state["error"] = str(error)
            await self.history.update_batch(
                batch_id,
                completed=self.state["completed"],
                status="error",
                error=str(error),
            )
        finally:
            await self._advance_queue()

    async def _advance_queue(self) -> None:
        """当前批次收尾后自动接续队列中的下一个;关闭时不再接续。

        stop_requested 只作用于当前批次:clearQueue=true 的停止已经清空了队列,
        clearQueue=false(只停当前)则应继续接续,_begin_batch 会复位该标志。
        """
        if self.shutting_down or not self.queue:
            self._stop_monitor()
            return
        entry = self.queue.pop(0)
        try:
            await self._begin_batch(
                entry["settings"], entry["seeds"], entry.get("regeneration")
            )
        except Exception as error:  # 接续失败不应吞掉:记录并继续尝试下一个
            logger.warning("队列批次启动失败: %s", error)
            await self._advance_queue()

    def _ensure_monitor(self) -> None:
        if self._monitor_task and not self._monitor_task.done():
            return
        stream = getattr(self.comfy, "progress_stream", None)
        if stream is None:
            return
        self._monitor_task = asyncio.create_task(self._monitor_progress())

    def _stop_monitor(self) -> None:
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
        self._monitor_task = None

    async def _monitor_progress(self) -> None:
        """通过 ComfyUI websocket 更新采样进度与实时预览。

        尽力而为:连接失败或断开只影响进度展示,不影响批次本身
        (批次完成仍由 wait_for_history 轮询判定)。
        """
        while self.active():
            try:
                async for item in self.comfy.progress_stream(self.client_id):
                    state = self.state
                    if state is None or state.get("status") not in ("running", "stopping"):
                        continue
                    if item.get("kind") == "event":
                        payload = item.get("payload") or {}
                        data = payload.get("data") or {}
                        if payload.get("type") == "progress":
                            state["progress"] = {
                                "value": int(data.get("value") or 0),
                                "max": int(data.get("max") or 0),
                            }
                        elif payload.get("type") == "executing":
                            state["progress_node"] = str(data.get("node") or "")
                            if data.get("node") is None:
                                state.pop("progress", None)
                    elif item.get("kind") == "preview":
                        self._preview_seq += 1
                        self.preview = (
                            self._preview_seq,
                            f"image/{item.get('format') or 'jpeg'}",
                            item.get("bytes") or b"",
                        )
                        state["preview_id"] = self._preview_seq
            except asyncio.CancelledError:
                raise
            except Exception as error:
                logger.debug("进度 websocket 中断,稍后重连: %s", error)
            if not self.active():
                break
            await asyncio.sleep(2.0)

    async def _interrupt_current(self) -> None:
        """停止时尽力中断 ComfyUI 正在渲染的任务;失败不影响批次收尾。"""
        interrupt = getattr(self.comfy, "interrupt", None)
        if interrupt is None:
            return
        try:
            await interrupt()
        except ComfyError:
            pass

    @staticmethod
    def _backfill_fixed_sections(
        settings: dict[str, Any], selected: dict[str, list[dict[str, Any]]]
    ) -> dict[str, list[dict[str, Any]]]:
        """为未重抽且无快照的维度补上固定词伪条目,使变体图也带可读信息。

        与 catalog.resolve_prompt 的固定分支共用 fixed_selection_item(),
        保证两处条目同构(组合规则 _pick_hit 对 fixed 条目按完整 tag 集判身份)。

        守卫顺序与 _fixed_pinned() 保持一致:`random_*` 为真的维度**永不回填**。
        否则该维度只是"这一张快照里为空"(例如 Task 4 之前落库的老记录),残留的
        fixed_* 文本会被塞进去标成 fixed=True,详情弹窗就把它显示成"(固定)"——
        正是本任务要治的"显示与实际不符",方向反了。

        本函数只往非 redraw_sections 的维度写,而 _resolve_regeneration 的
        changed 判定只读 redraw_sections 的 id,因此回填不影响变更判定。
        """
        result = dict(selected)
        for section in PROMPT_SECTIONS:
            if settings.get(f"random_{section}"):
                continue
            if result.get(section):
                continue
            fixed_text = str(settings.get(f"fixed_{section}") or "").strip()
            if fixed_text:
                result[section] = [fixed_selection_item(section, fixed_text)]
        return result

    def _resolve_regeneration(
        self,
        settings: dict[str, Any],
        prompt_seed: int,
        regeneration: dict[str, Any],
    ) -> dict[str, Any]:
        mode = regeneration["mode"]
        fixed_selection = copy.deepcopy(regeneration.get("fixed_selection") or {})
        if mode in {"replay", "prompt_variant"}:
            # 复现原图不复检组合规则:这两个模式的语义是把历史图片的最终提示词
            # 原样回放,selection 直接取自历史快照。规则后来才新增也允许复现旧图,
            # 否则"复现此图"会在规则变更后突然失败。这是有意为之,不是遗漏。
            positive = regeneration["frozen_positive_prompt"]
            return {
                "composer_prompt": positive,
                "full_prompt": positive,
                "selected": self._backfill_fixed_sections(settings, fixed_selection),
            }
        if mode == "settings_reroll":
            # 与普通批次同一路径:整体重抽也必须让固定维度参与规则匹配,
            # 否则同一份规则在"生成"和"设置重抽"之间行为不一致。
            resolved = self._resolve_catalog_prompt(
                settings, prompt_seed, pinned=self._fixed_pinned(settings)
            ) if self.catalog else {
                "composer_prompt": "",
                "full_prompt": "",
                "selected": {},
            }
            return {
                **resolved,
                "selected": self._backfill_fixed_sections(settings, resolved["selected"]),
            }
        if not self.catalog:
            raise WorkflowError("当前提示词目录不可用，无法重新抽取内容")
        redraw_settings = copy.deepcopy(settings)
        for section, entries in fixed_selection.items():
            redraw_settings[f"random_{section}"] = False
            parts: list[str] = []
            for item in entries:
                parts.extend(
                    self.catalog.prompt_parts(
                        item,
                        section,
                        settings.get("character_detail", "trigger_tags"),
                        bool(settings.get("female_count") or settings.get("male_count"))
                        and section == "character",
                    )
                )
            redraw_settings[f"fixed_{section}"] = ", ".join(parts)
        resolved = self._resolve_catalog_prompt(
            redraw_settings, prompt_seed, pinned=fixed_selection or None
        )
        merged = copy.deepcopy(resolved["selected"])
        for section, entries in fixed_selection.items():
            merged[section] = copy.deepcopy(entries)
        redraw_sections = regeneration["redraw_sections"]
        original = regeneration.get("original_selection") or {}
        # 变更判定只看 redraw_sections 的 id,固定词回填不得参与。
        changed = any(
            [item.get("id") for item in merged.get(section, [])]
            != [item.get("id") for item in original.get(section, [])]
            for section in redraw_sections
        )
        return {
            **resolved,
            "selected": self._backfill_fixed_sections(settings, merged),
            "_changed": changed,
        }
