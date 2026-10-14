# Anima Random Studio

基于 [ComfyUI](https://github.com/comfyanonymous/ComfyUI) 与 [Anima Tools](https://github.com/nregret/Comfyui-Anima-Tools) 构建的本地随机生图工作台。将提示词池随机抽取、批量生成队列、LoRA 管理、多维度 Detailer 局部修复、收藏树、风格预设与生成历史整合于轻量化 WebUI 中，默认仅连接与运行在本机服务。

> **项目说明**：本项目为原开源项目的独立维护重构版（Community Hard Fork）。原项目存在导致核心功能瘫痪的缺陷且原作者已停止维护，本项目对已知恶性 Bug 进行了全面修复，重构了依赖检测与一键启动流程，并提供持续的维护与优化支持。原项目地址：https://github.com/159159pzy-crypto/comfyui-random-image-generation

---

## 界面预览

![Anima Random Studio 工作台界面](docs/screenshots/anima-studio-v7.png)

---

## 核心功能

* **提示词随机抽取与批量队列**
  * 支持角色、服装、姿势、背景、表情五大独立提示词池。
  * 各词池支持随机抽取、固定词条、禁用、分类/特征筛选、排除项与权重配置。
  * 批量生成支持多任务自动排队接续、随时中断任务以及基于 WebSocket 的单张采样实时预览。
  * 历史记录支持回放与三类变体：保持原双种子重跑、固定提示词仅换图、按维度局部重抽等。
* **模型、LoRA 与局部修复管线**
  * 实时读取 ComfyUI 已加载的主模型（UNET），切换安全可靠。
  * 深度适配 ComfyUI-Lora-Manager，直接读取已缓存的缩略图与触发词，支持自定义触发词覆盖与启闭。
  * 高清修复（Hires-Fix）与手部、面部、眼睛、NSFW 四类 Detailer 独立开关，支持与 SAMLoader 自动按需联动加载。
* **分级收藏夹与自定义词库**
  * 支持自定义词条批量导入（JSON / CSV），构建树状层级分组。
  * Finder 风格多级收藏夹，支持将当前抽取的词条组合一键归档与持久化管理。
* **风格预设与本地持久化**
  * 支持将模型、LoRA 组合、尺寸、采样步数、CFG 及 Detailer 配置一键保存为独立风格预设。
  * 运行时数据与历史记录采用本地 SQLite3 及 JSON 原子写入，不上传任何云端服务器。

---

## 运行环境要求

| 组件          | 要求                       | 说明                             |
|:----------- |:------------------------ |:------------------------------ |
| **操作系统**    | Windows 10 / 11 (64-bit) | 启动批处理脚本基于 Windows 平台优化         |
| **ComfyUI** | 正常运行的本机实例                | 默认监听地址 `http://127.0.0.1:8188` |
| **Python**  | 3.10 / 3.11 及以上          | 支持 ComfyUI 整合包内置便携 Python 环境   |
| **核心依赖**    | `aiohttp`                | 首次运行启动脚本时会自动检测并安装              |
| **浏览器**     | Chrome / Edge 等现代浏览器     | 默认访问 `http://127.0.0.1:8190`   |

---

## 安装与快速启动

### 步骤一：获取项目文件

1. 前往本项目的 [Releases 页面](../../releases) 下载最新发布的压缩包（ZIP）。
2. 将压缩包解压至你的 **ComfyUI 整合包根目录** 下（即与 `ComfyUI` 目录平级）。
   * 解压后的典型目录结构示例：

     ```text
     ComfyUI_windows_portable/
     ├── ComfyUI/
     ├── python_embeded/       (或 python311、py311、python 等)
     └── comfyui-random-image-generation-available/   (本项目目录)
     ```
   * *注意：请确保整合包内置的 Python 文件夹名称为 `python_embeded`、`python311`、`py311`、`python310`、`py310` 或 `python` 之一。*

### 步骤二：安装 ComfyUI 依赖节点

请确保 ComfyUI 中已安装以下 Custom Nodes（推荐通过 **ComfyUI Manager** 搜索安装或使用 Git 导入）：

| 节点项目                                                                         | 作用说明                            |
|:---------------------------------------------------------------------------- |:------------------------------- |
| [Comfyui-Anima-Tools](https://github.com/nregret/Comfyui-Anima-Tools)        | 提供提示词池解析、画师条目库与提示词编码核心          |
| [rgthree-comfy](https://github.com/rgthree/rgthree-comfy)                    | 提供 Power LoRA Loader、种子管理与工作流控制 |
| [ComfyUI-Impact-Pack](https://github.com/ltdrdata/ComfyUI-Impact-Pack)       | 提供 DetailerPipe 局部修复管线          |
| [ComfyUI-Impact-Subpack](https://github.com/ltdrdata/ComfyUI-Impact-Subpack) | 提供 Ultralytics 检测器加载支持          |
| [ComfyUI-Easy-Use](https://github.com/yolain/ComfyUI-Easy-Use)               | 提供高清放大与尺寸辅助节点                   |
| [ComfyUI-KJNodes](https://github.com/kijai/ComfyUI-KJNodes)                  | 提供图像尺寸预设与图像缩放节点                 |

> **提示**：安装完成后请检查 `ComfyUI/custom_nodes/` 路径，确保各插件文件夹名称正常，不要带有 `-main` 或 `-master` 等多余后缀。

### 步骤三：放置模型与检测器

请根据所使用的工作流将对应的模型放置在 `ComfyUI/models/` 对应子目录下：

| 模型分类          | 推荐/默认文件名                               | 存放路径                       | 依赖场景                  |
|:------------- |:-------------------------------------- |:-------------------------- |:--------------------- |
| **Anima 主模型** | `miaomiaoHarem_anima14.safetensors`    | `models/diffusion_models/` | 基础文生图（亦可在界面切换其他 UNET） |
| **文本编码器**     | `qwen_3_06b_base.safetensors`          | `models/text_encoders/`    | 必需                    |
| **VAE 模型**    | `qwen_image_vae.safetensors`           | `models/vae/`              | 必需                    |
| **高清放大模型**    | `4x_foolhardy_Remacri.pth`             | `models/upscale_models/`   | 开启高清修复时必需             |
| **SAM 权重**    | `sam_vit_b_01ec64.pth`                 | `models/sams/`             | 开启任意 Detailer 时必需     |
| **手部检测器**     | `hand_yolov9c.pt`                      | `models/ultralytics/bbox/` | 开启手部 Detailer 时必需     |
| **面部检测器**     | `face_yolov9c.pt`                      | `models/ultralytics/bbox/` | 开启面部 Detailer 时必需     |
| **眼睛检测器**     | `Eyeful_v2-Individual.pt`              | `models/ultralytics/bbox/` | 开启眼睛 Detailer 时必需     |
| **NSFW 分割器**  | `ntd11_anime_nsfw_segm_v5-variant1.pt` | `models/ultralytics/segm/` | 开启 NSFW Detailer 时必需  |

### 步骤四：启动与使用

1. **先启动 ComfyUI**：确保 ComfyUI 已在后台正常运行，且可在浏览器中正常打开 `http://127.0.0.1:8188`。
2. **运行本项目**：进入本项目文件夹，双击运行 `启动WebUI.bat`。
   * 批处理会自动识别整合包环境中的 Python 路径，首次运行时会自动安装补齐 `aiohttp`。
   * 启动成功后，会自动在默认浏览器打开工作台界面（`http://127.0.0.1:8190`）。若初次运行未弹出前端界面，再次双击执行即可。

---

## 常见问题与排查 (FAQ)

### Q1: 启动提示 `[WinError 10048]` 或 `Address already in use`？

* **原因**：本地 `8190` 端口被占用，通常是因为之前的 WebUI 窗口直接关闭后后台残留了 `python.exe` 进程，或者手滑重复双击了启动脚本。
* **解决方案**：
  * **方法一（推荐）**：按 `Ctrl + Shift + Esc` 打开任务管理器，切换到“详细信息”，找到名为 `python.exe` 的残留进程并结束任务，重新启动即可。
  * **方法二（命令行清理）**：打开 CMD 终端执行以下命令查询并终止占用进程：

    ```bat
    netstat -ano | findstr :8190
    taskkill /F /PID <查询到的PID数字>
    ```

### Q2: 界面可以正常打开，但点击生图时提示无法连接或请求超时？

* **原因**：WebUI 未能成功连接至 ComfyUI 服务。
* **解决方案**：
  1. 请确认在打开本项目之前，ComfyUI 是否已经在后台启动并在 `8188` 端口监听。
  2. 在浏览器中打开 `http://127.0.0.1:8188`，确认 ComfyUI 原生界面能够正常加载与工作。

### Q3: 界面主模型下拉框为空或提示“模型不存在”？

* **原因**：ComfyUI 刚加入新模型尚未更新缓存，或模型未放置在正确目录。
* **解决方案**：
  * 确认模型已存放在 `ComfyUI/models/diffusion_models/` 或 `checkpoints/` 下。
  * 重启 ComfyUI 服务，或在 ComfyUI 网页界面中点击“Refresh”重新加载资源列表。

### Q4: 提示词池内容全为空？

* **原因**：未正确探测到 `Comfyui-Anima-Tools` 节点所在路径。
* **解决方案**：
  * 检查 `ComfyUI/custom_nodes/` 下是否存在 `Comfyui-Anima-Tools` 文件夹。
  * 若你的节点放置在特殊自定义路径，可通过启动参数 `--anima-tools-dir "绝对路径"` 手动指定。

---

## 命令行高级参数

如果你不使用批处理脚本，也可以直接通过命令行传递参数启动 `run.py`：

```bash
python run.py --port 8190 --comfy-url http://127.0.0.1:8188
```

| 参数                  | 默认值                     | 说明                                 |
|:------------------- |:----------------------- |:---------------------------------- |
| `--host`            | `127.0.0.1`             | WebUI 监听地址（为确保安全，默认仅绑定本机）          |
| `--port`            | `8190`                  | WebUI 访问端口                         |
| `--comfy-url`       | `http://127.0.0.1:8188` | 后端 ComfyUI 服务地址                    |
| `--anima-tools-dir` | 自动探测                    | 手动指定 `Comfyui-Anima-Tools` 所在的物理路径 |
| `--output-dir`      | 自动探测                    | 指定 ComfyUI 输出目录，用于在历史记录中直接定位文件     |
| `--no-browser`      | 禁用                      | 启动后不自动在系统默认浏览器中唤起页面                |

---

## 目录结构说明

```text
├── anima_webui/             # 后端服务核心、ComfyUI WebSocket 通信与调度逻辑
├── static/                  # WebUI 前端静态资源 (HTML / CSS / JavaScript)
├── templates/               # 工作流模版文件 (workflow_api.json 等)
├── data/                    # 本地数据持久化目录（已配置 .gitignore，保护个人数据）
│   ├── history.sqlite3      # 生成历史与任务参数数据库
│   ├── style_presets.json   # 用户保存的风格预设
│   └── custom_prompts.json  # 自定义提示词库
├── run.py                   # Python 核心启动入口
└── 启动WebUI.bat            # Windows 整合包一键启动批处理
```

---

## 致谢与开源协议

* 本项目底层交互基于 [ComfyUI](https://github.com/comfyanonymous/ComfyUI) 与 [Comfyui-Anima-Tools](https://github.com/nregret/Comfyui-Anima-Tools)。
* 本项目对原开源仓库的结构进行了重构与缺陷修复。项目中涉及的模型权重、LoRA、检测器及第三方自定义节点均遵循其各自的原始开源授权协议。
