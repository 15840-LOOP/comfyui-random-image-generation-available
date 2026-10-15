# 更新日志

## 未发布

### 新增

- **风格预设缩略图**：预设实体新增 `thumbnail_url` 字段，由物理文件推导（存在 `data/preset_thumbnails/{preset_id}.png` 时返回 `/api/style-presets/{preset_id}/thumbnail`，否则为 `null`），不写入 JSON，避免持久化状态与磁盘不一致。
- `StylePresetStore` 新增 `thumbnail_dir`（与预设 JSON 同级的 `preset_thumbnails/`，构造时自动创建）、`save_thumbnail(preset_id, image_bytes)`（临时文件 + 原子替换写入，并同步刷新内存记录的 `thumbnail_url`）与 `thumbnail_path(preset_id)` 辅助方法。
- 新增 `GET /api/style-presets/{preset_id}/thumbnail` 路由，返回 `FileResponse`（`image/png`）；文件缺失返回 404。
- `POST /api/style-presets` 与 `PUT/PATCH /api/style-presets/{preset_id}` 现支持两种提交形态：JSON 体可携带可选 `source_image_id`（引用作品库图片，经 `HistoryStore.get_image` 取原图字节作为封面）；`multipart/form-data` 可直接上传 `thumbnail`/`file`/`image` 文件字段。`PUT` 同时新增 `PATCH` 别名。
- 删除预设时联动物理删除对应缩略图文件，避免孤儿文件堆积。
- 新增 `POST /api/history/{image_id}/open-folder` 接口，路径经 `normalize_lora_path` 规范化与 `is_relative_to` 越界校验，文件缺失返回 404、未配置输出目录返回 400，均给出友好 JSON 提示。
- 新增 `--output-dir` 命令行参数与 `COMFYUI_OUTPUT_DIR` 环境变量；未显式指定时按便携包结构自动探测项目同级的 `../output` 与 `../ComfyUI/output`。
- `GET /api/config` 现返回 `output_dir` 字段。

### 修复

- 修复作品详情页「载入设置」误杀固定提示词的问题：此前载入逻辑仅依据 `resolved_selection[section]` 判定卡池是否使用，而纯固定词生图时该字段为空数组，导致 5 大卡池被错误关闭、手打固定词丢失。现改为**双轨优先级提取**（`getEffectivePromptForSection`）：优先取随机池抽中词条（`resolved_selection[section]` 非空数组，按 `, ` 拼接），其次回退取原图固定词（`settings["fixed_" + section]` 非空字符串），仅当两处皆空时才判定为「未使用」并关闭卡池。新增 `applyRecordSettings(record)` 专用载入函数，在 `applySettings` 还原模型/采样/人物/LoRA 等全部参数后，对 5 大卡池执行双轨回填：随机池抽卡图片自动跳到最右侧【固定】并固化实际抽中词条（ACTUAL DRAW），纯固定词图片保留原词并保持【固定】高亮，确实未使用的板块才清空并切换【关闭】。`ui.restoreSettings` 点击处理改用该函数并传入完整 `selectedRecord`（含 `resolved_selection`）。
- 修复风格预设（`StylePresetStore`）字段白名单遗漏导致人物构成与角色细节无法保存/还原的问题：后端 `PRESET_SETTING_KEYS` 与前端 `static/app.js` 的 `PRESET_SETTING_KEYS` 同步补齐 `female_count`、`male_count`、`character_detail` 三个字段，与 `DEFAULT_SETTINGS` 对齐。此前保存或载入预设时「几女几男」与角色细节模式会被 `presetSnapshot()` 丢弃，或在前端提交全量 `settings` 时触发 `WorkflowError("风格预设包含未知参数")`。
- `preset_settings()` 在校验未知参数前安全剔除运行期批次字段 `count`，避免前端直接提交完整工作台 state 时因 `count` 抛异常。
- 新增 `tests/test_style_presets.py` 回归用例：覆盖人物构成/角色细节字段的保存与更新、旧版预设文件缺失新字段时经 `DEFAULT_SETTINGS` 自动补齐（不触发 `.corrupt.bak` 备份）、以及 `count` 运行期字段被忽略。
- 修复 Node 60 合成器旁路后 `resolved_prompt` 被一并置空的问题：该字段仅作可回溯元数据，不参与抽卡，现恢复为 `frozen_positive_prompt or resolved_prompt`（API 与 UI 两处同步）。此前当历史条目缺少 `extra_pnginfo` 时，`extract_positive_prompt` 的兜底路径会读到空串，导致正向提示词丢失。`enable_*` 仍保持全 `False`、Node 42 仍为直接字符串注入。
- 同步更新 3 处过时单元测试，使其匹配「Node 60 旁路、Python 侧统一注入 Node 42」的新架构（`enable_clothing`/`enable_background` 期望值、`character_tags` 人数标签融合、UI `widgets_values` 结构）。
- 修复坏数据文件被其他进程占用时启动崩溃的问题：`backup_corrupt_file` 的 `os.replace` 在 Windows 下可能因文件被编辑器/杀毒软件/同步盘独占而抛 `PermissionError`，该异常在 `reload()` 的 `except` 块内抛出、不被同块捕获，会冒泡导致 WebUI 无法启动，与「坏文件不阻断启动」的设计相悖。现仅在改名失败时降级为保留原文件并返回原路径，正常路径行为完全不变。
- 新增 `tests/test_audit_bugs.py`：覆盖文件锁降级、空文件恢复与 `HistoryStore` 生命周期，作为上述边界行为的回归保护。
- 新增缩略图回归用例：`tests/test_style_presets.py` 覆盖缩略图目录创建、`thumbnail_url` 推导、`save_thumbnail` 原子写入无残留临时文件、删除预设联动清理缩略图；`tests/test_server.py` 覆盖 multipart 上传与静态路由、`source_image_id` 引用作品库图片、以及非法 `source_image_id` 返回 400。

## 未发布V2

### 变更 (Changed)

- **左侧边栏瘦身**：移除左侧「生成设置」中原有的「风格预设」折叠区（`.preset-section`，含预设名称输入框、保存当前按钮与旧预设列表），使「人物构成」直连「提示词池」，释放侧边栏垂直高度。
- **右侧主工作区顶层 Tab 化**：作品库顶部标题结构替换为平行标签页容器 `.main-tabs-header`，含「作品库」（`#tab-btn-gallery` + `#gallery-count` 徽章）与「预设库」（`#tab-btn-presets` + `#presets-count` 徽章）两组切换按钮；主显示区拆分为同级容器 `#gallery-view-container`（保留原有作品库网格与分页逻辑）与 `#presets-view-container`（默认隐藏）。

### 新增 (Added)

- **预设库视图**：`#presets-view-container` 内构建顶部控制栏（标题「预设库」、统计数量、`#btn-create-preset` 主按钮）与 `#presetGrid` 响应式网格容器（`auto-fill minmax(200px, 1fr)`，统一 3:4 宽高比）。
- **预设卡片组件**：每个 `.preset-card` 含 `.preset-thumb-wrapper`（缩略图容器，无缩略图时显示占位符）、`.preset-hover-overlay`（悬浮操作遮罩，含「⚡ 载入 / ⟳ 覆盖 / ✎ 改名 / 🗑 删除」四个差异化按钮）与 `.preset-info`（名称 + 收藏星标）。
- **卡片 Hover 动效**：遮罩默认 `opacity: 0`，卡片 hover/focus-within 时淡入；卡片上浮、缩略图轻微缩放、按钮差异化配色（载入蓝、覆盖/改名半透明白、删除红），并补充 620px 断点移动端适配。
- 前端新增 `switchMainTab()` 函数处理作品库/预设库 Tab 切换，`createStylePreset()` 改为弹窗输入名称模式。

### 新增 (Added) · 业务交互与状态联动闭环

- **四大悬浮按钮功能落地**：`.btn-load` 一键载入改为以预设 `settings` 为基准全量覆盖工作台（提示词池、LoRA、画师、主模型、分辨率、步数、CFG、采样器等），Toast 提示「已载入预设：【预设名】」；`.btn-overwrite` 弹出确认弹窗（含「同步更新缩略图」勾选框，勾选后以作品库最新生成图作为新封面，经 `source_image_id` 提交）；`.btn-rename` 弹出改名弹窗并做 1~100 字符与同名前端校验，提交 `PATCH /api/style-presets/{id}`；`.btn-delete` 弹出二次确认弹窗，成功后执行卡片淡出移除动画并同步更新总数。
- **「+ 新建预设」模态框流程**：`#btn-create-preset` 改为打开模态框，表单含必填名称、封面缩略图预览与「更换本地图片」上传按钮；默认自动取作品库最新生成图（`historyItems[0]`）作为封面预览，支持上传本地图片（`multipart/form-data`）或回退到最新作品图，确认后打包当前工作台全量 `settings` 提交 `POST /api/style-presets`，新增预设排在列表首位。
- 前端 `request()` 支持 `FormData` 请求体（不再强制 JSON `Content-Type`），以适配缩略图 multipart 上传。
- 预设卡片网格列宽与间距对齐作品库 `.gallery`（`minmax(215px, 1fr)` / `gap: 14px`），确保两类卡片尺寸规格统一；新增 `.preset-card.is-removing` 淡出动画与新建预设封面选择样式。

### 修复 (Fixed)

- **修复启动报错「界面资源版本不一致，缺少控件：btnCreatePreset、tabBtnGallery、tabBtnPresets、galleryCount、presetsCount、galleryViewContainer、presetsViewContainer」**：根因是新增的预设库标签页控件在 `static/index.html` 中使用了连字符式 id（如 `btn-create-preset`、`tab-btn-gallery`），而 `static/app.js` 的 `ui` 映射键名是驼峰式（`btnCreatePreset`、`tabBtnGallery`），且映射逻辑 `document.getElementById(id)` 直接以键名取元素、不做命名转换。项目其余控件 id 均为驼峰式，故仅这 7 个新控件取不到元素、触发 `missingUi` 校验抛错。现将这 7 个 id 统一改为驼峰式（`btnCreatePreset`/`tabBtnGallery`/`tabBtnPresets`/`galleryCount`/`presetsCount`/`galleryViewContainer`/`presetsViewContainer`），并同步更新 `aria-controls`/`aria-labelledby` 引用与 `static/styles.css` 中的 `#presetsViewContainer` 选择器。
- 同步调整 `static/app.js` 的 UI 元素引用列表：移除已删除的 `presetName`/`savePreset`/`presetList`，新增 `presetGrid`/`btnCreatePreset`/`tabBtnGallery`/`tabBtnPresets`/`galleryCount`/`presetsCount`/`galleryViewContainer`/`presetsViewContainer`，避免 `missingUi` 校验抛错。
- 补充 `tests/test_server.py` 回归断言：断言预设库标签页 7 个控件（驼峰式 id）随 HTML 一同下发，防止同类命名不一致问题复发。
- 作品库计数更新时同步刷新 `#gallery-count` 徽章，保持与 `#historyCount` 一致。
- 清理 `static/styles.css` 中失效的旧预设样式（`.preset-create-row`/`.preset-list`/`.preset-row`/`.preset-apply`/`.preset-actions`）。

## ？？？

- 作者我操你妈

## [v4.0.5]

### 新增 (Added)

- **快捷定位**：图片详情页新增“打开本地文件位置”快捷操作，方便快速访问生成的图像文件。

---

## [v4.0.4]

### 修复与优化 (Fixed & Improved)

- **提示词重复注入问题**：断开 Node 60 连向 Node 42 的冗余连线并清空多余输出端口，彻底解决正向提示词被重复拼接的问题。
- **额外提示词独立槽位恢复**：将 `extra_prompt` 调整为直接以纯文本格式注入对应端口，消除此前强行拼接至背景词槽所引起的语义污染。
- **工作流元数据残留清理**：清理 UI 拓扑中失效的连接线并将 Node 60 设为旁路（Bypass），确保由该工作流生成的图片拖回 ComfyUI 画布复现时，节点连线干净且无依赖冲突。
- **提示词末尾异常字符消除**：纠正节点输入传参类型，消除正向提示词末尾异常残留 `['60', 0]` 列表字面量的问题。
- **预设保存与应用功能**：修复预设配置未持久化写入数据的问题，恢复保存与加载预设的完整功能。

### 其他 (Other)

- 正式开启 GitHub Issues 反馈通道，便于收集并跟进问题。

---

## [v4.0.3]

### 修复 (Fixed)

- **表情词池**：修复表情池配置未能正常生效的问题。
- **固定提示词**：修复固定提示词在生成过程中未被正确应用的问题。

### 文档 (Documentation)

- 优化 README 文档的文字描述与排版，提升阅读体验。

---

## [v4.0.2]

### 脚本与环境 (Scripts & Environment)

- **启动脚本兼容性优化**：重构并优化 `.bat` 启动脚本，增强对 ComfyUI 根目录下不同变体命名 Python 嵌入式环境文件夹的自动识别与兼容，防止因特定路径名导致的初始化报错。

### 文档 (Documentation)

- **安装指南完善**：更新 README 安装教程，补充 Python 环境依赖与配置注意事项，降低初次部署的报错概率。

---

## [v4.0.1]

### 修复 (Fixed)

- **角色随机词池逻辑**：修复提交 ComfyUI 工作流时的参数透传错误；将后端二次随机抽卡调整为前端一致计算注入，彻底解决随机词池失效问题。

### 新增与环境 (Added & Environment)

- **一键启动脚本**：新增适配内置便携式 ComfyUI 的一键启动脚本 `启动WebUI.bat`，支持首次启动时静默检测环境依赖并自动安装 `aiohttp`。

### 文档 (Documentation)

- **安装指南重构**：重新整理 README 安装指引，针对自定义节点目录命名规范及目录层级结构做出明确说明。

---

## 0.4.0 - 2026-10-03

### 新增

- 新增 CFGZeroStar 可选开关，并支持配置第二次采样的步数、CFG、Sampler、Scheduler 与 Denoise；第二次采样复用当前图片的主 seed。
- Detailer 开关现在会自动联动 SAM Loader，关闭全部 Detailer 时从提交的工作流中移除 SAM Loader。
- 新增 2ndSampler 与 CFGZeroStar 的资源校验、工作流渲染、设置持久化和测试覆盖。
- README 增加 v7 工作台界面预览截图。

## 0.3.0 - 2026-09-26

### Windows 启动器

- 新增 .NET 8 WinUI 3 自包含文件夹托盘启动器，支持导入 ComfyUI / 便携版、新建 NVIDIA 环境、固定提交的七个节点安装和来源选择。
- 新增版本化运行环境、模型和镜像清单；模型按功能勾选下载，支持续传、暂停、重试、取消、SHA-256 与原子替换；缺少可靠来源的模型仅检测。
- 兼容 clip/unet、模型子目录与 extra_model_paths.yaml；按 ComfyUI 实际名称映射工作流；未安装可选高清模型时允许基础生成。
- 新增独立启动器数据目录、服务身份健康检查、端口冲突处理、进程所有权恢复、应用版本回退、日志与 Windows 凭据管理器集成。
- 新增 Windows 构建脚本、SHA-256 清单、可选 Authenticode 签名、核心验收程序和 Windows CI。

### 变更

- **可靠历史回放**：历史“复现此图”改为先检查模型、已启用 LoRA、高清模型、Sampler 与 Scheduler，再用保存的最终正负提示词和原双种子重跑；词库之后被编辑或删除不再改变回放提示词。资源缺失时明确阻止，不自动替换。
- **变体模式**：“再抽变体”现在可选择同提示词换图像种子、按角色/服装/姿势/背景/表情重抽指定维度，或按原配置全部再抽。同提示词变体仍为文生图，不使用 Img2Img。
- **历史再生成 API**：新增 `GET /api/history/{image_id}/regeneration-options` 与 `POST /api/history/{image_id}/regenerate`；原 `/api/batches` 固定种子接口保持兼容。
- **全尺寸图片预览**：历史详情图可点开全屏预览，支持滚轮/双指缩放、放大拖动、双击切换适配/2x、键盘加减与方向键；带弹性开合动画并遵循 prefers-reduced-motion。
- **启动器版本管理**：启动器可将工作台切换到 EXE 内捆绑版本；检测批次/队列空闲后再执行，旧实例先经令牌化停机端点优雅退出；开发模式 AppRoot 与外来进程占用端口时跳过。
- **新增 `POST /api/launcher-shutdown`**：需携带启动器下发的令牌（HMAC 比较）；未配置令牌时返回 404，供旧版本探测能力。
- 新增独立官网落地页 `website.html`。

## 0.2.0 - 2026-07-26

### 新增

- **批次队列**:运行中再点"开始"不再报冲突,而是进入队列(上限 20 个)自动接续;顶栏队列徽标可展开查看、单独移除;"停止"默认中断当前批次并清空队列(`clearQueue=false` 可只停当前)。
- **实时进度与预览**:经由 ComfyUI websocket 显示单张采样进度(如"采样 18/30")与实时预览缩略图;连接断开只影响展示,批次本身不受影响。新增 `GET /api/batches/current/preview`。
- **历史复现与变体**:历史详情新增"复现此图"(相同设置 + 相同种子,`POST /api/batches` 携带 `seeds`)与"再抽变体"(相同设置、随机种子、自定数量)。

### 变更

- `GET /api/batches/current` 现返回 `{batch, queue}`;开始按钮在批次运行时变为"加入队列"。
- 前端提交增加在途守卫,双击不再产生重复批次/重复排队。
- 界面对齐新版设计:批次数量、批次/采样双层进度、实时预览、队列徽标与停止/开始集中到底部悬浮操作条,顶栏简化为品牌 + 连接状态 + 主题;风格预设显示「模型 · 宽×高 · 步数 · 修复状态」摘要;词池抽屉眉标统一为 PROMPT POOL。
- `data/webui.log` 改为轮转日志(单文件 2MB,保留 3 份)。
- 界面切换为 Liquid Glass 主题包(液态玻璃重设计 v2):浮动圆角顶栏、氛围背景、底部胶囊指令台;0.2.0 控件(队列徽标、实时预览、采样进度、复现/变体)已嫁接进该主题。
- 词池分类标签接入插件自带中文:「中文优先」下姿势/服装/背景的分类(侧栏与卡片)显示中文半边,角色性别筛选显示 女性/男性;「仅英文」显示英文规范值;筛选逻辑不变。
- 内置热门角色/系列中文译名表(`anima_webui/zh_names.json`,315 个角色 + 69 个系列):「中文优先」显示中文名(双语档显示「中文 / 罗马字」),系列与性别筛选同步中文,支持直接用中文搜索角色;未收录条目回退英文原名。

## 0.1.0 - 2026-07-26

首个有版本号的整理版本。基于一次完整代码审查,集中修复了 P0/P1/P2 三档问题。

### 修复(正确性)

- 每张输出图内嵌的 UI 工作流元数据被写坏的问题:`_set_ui_widget` 漏传 index,宽/高/步数/CFG/文件名前缀在拖回 ComfyUI 时全部丢失(100% 复现)。
- 前端两处存储型 XSS:`escapeHtml` 不转义引号导致的属性注入;姿势冲突提示未转义标题导致的内容注入。
- 批次启动的检查-后-启动竞态:快速双击"开始"可能并发跑两个批次。
- 收藏"读全量-改-写回"无锁导致的并发丢更新。
- 批次永久卡死:任务从 ComfyUI 队列与历史双双消失时无限轮询;"停止"必须等当前图完成且从不调用 `/interrupt`。
- 非密闭测试:`test_server` 依赖本机 Anima Tools 安装,现改为 tempdir 内的假数据。

### 改进(健壮性与性能)

- sqlite 与 fsync 写盘移出事件循环(专用单线程 executor / to_thread),批次落库不再冻结界面请求。
- `data/` 下任一数据文件损坏不再阻断启动:自动改名 `.corrupt.bak` 备份后以空数据继续,并在界面警告。
- 工作流模板加载时一次性校验全部必需节点,重新导出(节点重编号)的模板会得到明确报错。
- 引入 logging(控制台 + `data/webui.log`),消除静默吞错。
- 仅本机来源校验(Host/Origin),防御恶意网页的 CSRF 与 DNS 重绑定。
- `/object_info` 增加 5 秒复用缓存,批次启动不再重复拉取两遍数 MB 数据。
- 迁移 aiohttp `web.AppKey`,消除 91 条弃用告警;历史/图片路由限定数字 id。
- 关闭的池抽屉加 `inert` 并管理焦点;修复收藏树键盘焦点框;轮询后台暂停、空闲降频、错误提示去重;历史翻页竞态守卫;LoRA/子分组搜索去抖。
- 移除源码中的 `F:/` 硬编码探测路径(同级目录规则已覆盖);启动批处理支持 `ANIMA_PYTHON` 环境变量覆盖。

### 工程化

- 新增 `pyproject.toml`(依赖与版本约束)、`tests/conftest.py`、GitHub Actions CI(ubuntu + windows)、MIT LICENSE、本文件。
- `static/app.js` 全量 Prettier 格式化(纯格式,无逻辑改动)。
- 测试从 66 个增至 80+,覆盖并发竞态、轮询超时、坏文件恢复、模板校验、本机来源校验等。
