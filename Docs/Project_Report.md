# AI 辅助线性代数可视化与形式化验证系统项目报告

## 1. 项目概述

本项目聚焦“线性代数概念的交互式可视化 + AI 助教讲解”。前端为单页 Web 画布，[index.html](../index.html) 直接运行即可完成向量、矩阵、特征值等核心概念的几何演示；后端 [backend/app.py](../backend/app.py) 通过 DeepSeek Chat 生成结构化指令（JSON），驱动前端自动搭建场景，并可返回 Lean 风格的练习提示，形成“看得见、可操作、能讲清”的一站式学习体验。

## 2. 功能亮点

- 交互式几何画布：创建点、向量、矩阵，支持矩阵作用于向量/矩阵、线性组合、特征系展示、SVD 动画分解；网格吸附、右键菜单、撤销/重做、变换动画齐全。
- AI 助教聊天：输入自然语言（如“演示剪切矩阵”“展示特征向量”），后端返回 `operation` + `inputs` 的 JSON，前端自动绘制对应场景并给出中文解释。
- Lean 提示占位：Agent 可在响应中附带 `lean.statement_cn/lean_code/hint` 字段，前端在聊天区以卡片形式展示，方便扩展正式的 Lean 练习。
- 易于试验：默认载入示例对象，支持 Ctrl+Z/Ctrl+Y 历史回溯、Alt 取消吸附、中键平移、滚轮缩放，降低上手成本。

## 3. 系统架构

### 3.1 前端（单页 Canvas）
- 技术：原生 HTML/JS/CSS + `<canvas>` 绘制；仅依赖 marked.js（渲染聊天区 Markdown）。
- 数学内核：`MathLib` 提供向量/矩阵运算、特征值求解、SVD 分解、极分解近似等；`SceneObject` 体系封装点、向量、矩阵、特征系、线性组合及变换结果。
- 交互与动画：`HistoryManager` 负责撤销/重做与状态序列化；`AnimationEngine` 驱动矩阵乘法、SVD 分步动画；右键上下文菜单、网格吸附、拖拽聊天窗口等交互都内置。
- AI 桥接：`AIBridge.handleResponse` 接收后端 JSON（operation ∈ vector_add/lin_comb/mat_mul/eigen/lean_*），自动创建或重置场景并输出解释文本。

### 3.2 后端（Flask + DeepSeek）
- 接口：`POST /chat`，请求体 `{ "message": "..." }`，返回统一 JSON：`operation`、`inputs`、`visualization_config`、`explanation`（可选 `lean` 字段）。
- Prompt 约束：在 [backend/app.py](../backend/app.py) 中通过 `SYSTEM_PROMPT` 明确输出枚举、交互引导与 JSON 模板，若模型返回 Markdown 代码块会被自动剥离再解析。
- 异常兜底：解析失败时返回 `operation: other` 与原始内容，便于前端提示错误；DeepSeek API 未配置时直接返回 500。
- 示例与自检：
  - [backend/example_scenarios.py](../backend/example_scenarios.py) 提供调用样例，需将 `BASE_URL` 调整为后端实际端口。
  - [backend/verify_agent.py](../backend/verify_agent.py) 使用 `unittest.mock` 演示接口的 JSON 解析与 Markdown 剥离逻辑。

## 4. 运行与调试

1) 配置环境变量：在 `backend/.env`（若有 `.env.example` 先复制再重命名）中写入 `DEEPSEEK_API_KEY=<你的 key>`。
2) 安装依赖：`pip install -r backend/requirements.txt`。
3) 启动后端：`python backend/app.py`，默认监听 `http://127.0.0.1:5500/chat`。
4) 启动前端：直接用浏览器打开 [index.html](../index.html)（或启一个静态服务器）。聊天框会向上面的接口发起请求，请确保同源或允许 CORS。
5) 快速自测：
   - 浏览器聊天输入 “展示一个 90 度的旋转矩阵”，应出现矩阵作用向量的动画；
   - `curl -X POST http://127.0.0.1:5500/chat -H "Content-Type: application/json" -d '{"message":"展示剪切矩阵"}'` 查看原始 JSON 响应；
   - 若使用 [backend/example_scenarios.py](../backend/example_scenarios.py)，请把 `BASE_URL` 改为 `http://127.0.0.1:5500/chat`。

## 5. 文件概览

- [index.html](../index.html)：核心前端，包含 UI、数学内核、动画、AI 桥接与聊天 UI。
- [parse_agent_response.js](../parse_agent_response.js)：演示如何在前端解析 `operation`/`inputs`/`lean` 的示例脚本。
- [backend/app.py](../backend/app.py)：Flask 服务，封装 DeepSeek Chat 调用与 JSON 解析。
- [backend/example_scenarios.py](../backend/example_scenarios.py)：调用 /chat 的演示代码。
- [backend/verify_agent.py](../backend/verify_agent.py)：Mock 自检脚本，验证 Markdown 剥离和字段存在性。
- [backend/requirements.txt](../backend/requirements.txt)：后端依赖（flask、flask-cors、openai、python-dotenv）。
- [README.md](../README.md)：简要启动说明（记得替换/配置 API Key）。

## 6. 后续改进方向

- 完善 Lean 集成：为 `lean_code` 提供真实的编译/检查环节，并增加 Mathlib 依赖示例。
- 统一端口与脚本：将示例脚本默认端口改为 5500，避免新用户踩坑。
- 数据持久化：将 `HistoryManager` 状态导出为 JSON，支持课后回放与分享。
- 移动端体验：为触屏优化拖拽、缩放手势，并压缩 Canvas 绘制开销。
- 更丰富的教学模板：预置更多矩阵类型（旋转、缩放、剪切、投影、退化矩阵）与任务化互动提示。