# ComfyUI Volcano Engine Seedream Node

这是一个为 [ComfyUI](https://github.com/comfyanonymous/ComfyUI) 设计的自定义节点，它允许用户直接在 ComfyUI 的工作流中调用**火山引擎（Volcano Engine）**的 [豆包·Seedream](https://www.volcengine.com/product/doubao-seedream) 系列大模型，实现强大的图生图功能。

[English](./README_en.md) | 中文

![node_preview](https://user-images.githubusercontent.com/…..png) <!-- 建议在这里放一张节点在ComfyUI中的截图 -->

## ✨ 功能特性

*   **无缝集成**：将火山引擎的先进图像生成能力带入 ComfyUI 的节点式工作流。
*   **参数可调**：所有核心 API 参数（如 `prompt`, `strength`, `size`, `watermark` 等）均可在节点UI上进行可视化调整。
*   **支持单图生图**：输入一张图片，根据文本提示生成新的创意图像。
*   **支持多图参考（组图）**：输入一个批次（Batch）的图片作为参考，实现更复杂的图像生成任务。
*   **安全便捷**：API Key 直接在节点内输入，无需硬编码在代码中。
*   **实时反馈**：API 的调用状态、耗时和错误信息会实时打印在 ComfyUI 的控制台窗口，方便调试。


## 🚀 使用方法

安装并重启后，你可以在 ComfyUI 中通过以下方式添加节点：
*   双击画布，搜索 `Volcano Engine API`。
*   右键菜单 -> `Add Node` -> `Volcano Engine API` -> `火山引擎图生图 (Volcano API)`。

### 基本用法 (单图生图)

1.  添加一个 `Load Image` 节点，加载你的原始图片。
2.  将 `Load Image` 节点的 `IMAGE` 输出连接到本节点的 `image` 输入。
3.  在本节点中填入你的 `api_key` 和 `prompt`。
4.  调整 `strength` 等参数。
5.  将本节点的 `IMAGE` 输出连接到 `Preview Image` 或 `Save Image` 节点。
6.  点击 "Queue Prompt" 运行。

### 高级用法 (多图参考)

1.  使用多个 `Load Image` 节点加载你的参考图片。
2.  添加一个 `ImageBatch` 节点（图像批处理节点）。
3.  将所有 `Load Image` 节点的 `IMAGE` 输出连接到 `ImageBatch` 节点的输入。
4.  将 `ImageBatch` 节点的 `IMAGE` 输出连接到本节点的 `image` 输入。
5.  **关键步骤**：在本节点中，将 `sequential_image_generation` 参数设置为 **`auto`**。
6.  设置 `max_images` 参数，指定你希望 API 返回的结果图片数量。
7.  运行工作流。API 将会接收到你提供的所有参考图。

## ⚙️ 节点参数详解

| 参数                          | 类型      | 描述                                                                                              |
| ----------------------------- | --------- | ------------------------------------------------------------------------------------------------- |
| `image`                       | `IMAGE`   | 输入的原始图片或图片批次。                                                                        |
| `api_key`                     | `STRING`  | 你的火山引擎 API Key。                                                                            |
| `prompt`                      | `STRING`  | 文本提示，用于指导图像的生成方向。                                                                |
| `model`                       | `STRING`  | 选择要使用的模型。目前多图功能仅 `doubao-seedream-4.0-250828` 支持。                                 |
| `strength`                    | `FLOAT`   | 控制对原始图片的修改程度。值越小，与原图越相似；值越大，AI 的创造性越强。                          |
| `size`                        | `STRING`  | 指定输出图像的尺寸。选择 `auto` 时，API 会根据输入图片自动判断尺寸，这是图生图模式下的推荐选项。 |
| `watermark`                   | `BOOLEAN` | 是否在生成的图片上添加水印。                                                                      |
| `sequential_image_generation` | `STRING`  | 组图功能开关。设置为 `auto` 以启用多图参考模式，`disabled` 则为单图模式（即使输入多图也会被逐一处理）。|
| `max_images`                  | `INT`     | 当组图功能为 `auto` 时生效，指定 API 最多返回的图片数量（1-15）。                                      |

## ⁉️ 故障排查

*   **节点未出现**：请确认你已完全重启 ComfyUI，并且 `requirements.txt` 中的依赖已成功安装。
*   **API 报错**：请检查你的 ComfyUI 命令行窗口。节点会将火山引擎服务器返回的详细错误信息（如 API Key 无效、参数错误等）打印出来，这有助于定位问题。

## 🤝 贡献

欢迎提交 Pull Requests 或在 Issues 中报告错误、提出功能建议。

## 📜 许可证

本项目采用 [MIT License](./LICENSE) 开源。