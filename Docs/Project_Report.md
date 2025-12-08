# AI 辅助线性代数可视化与形式化验证系统项目报告

## 1. 项目概况 (Executive Summary)

本项目旨在利用现代人工智能技术与Web开发框架，构建一个集“直观几何可视化”与“严谨数学形式化”于一体的线性代数教育平台。项目采用 **神经符号双引擎 (Neuro-Symbolic Dual-Engine)** 架构：前端通过 React + Mafs 引擎将抽象的矩阵运算转化为可交互的动态图形，后端结合 Flask 与模拟的 Lean 4 验证机制，展示了从直观理解到机器证明的完整数学探索路径。

## 2. 技术架构 (Technical Architecture)

基于团队“AI优先”的开发理念，我们构建了以下技术栈：

### 2.1 架构设计
- **前端 (Visualization Layer)**: 
  - **框架**: React 18 (Vite 构建)
  - **核心库**: `Mafs.dev` (高性能SVG数学可视化), `TailwindCSS` (样式), `Axios` (网络请求)
  - **功能**: 实时响应用户的拖拽操作，动态更新向量加法、线性变换与特征向量的几何形态。

- **后端 (Logic & Formalization Layer)**:
  - **框架**: Flask (Python 3.9)
  - **计算引擎**: NumPy (负责高精度的数值计算，如特征值求解)
  - **形式化模拟**: 模拟 Lean 4 定理证明器的接口，演示如何将自然语言命题转化为形式化代码并验证。

- **部署 (Deployment)**:
  - Docker Containerization: 编写了 `docker-compose.yml`，实现前后端一键编排启动，保证开发环境的一致性。

### 2.2 目录结构
```
Project Root
├── backend/            # Flask 后端
│   ├── app.py          # API 服务与 Lean 模拟逻辑
│   └── Dockerfile
├── frontend/           # React 前端
│   ├── src/components/ # 数学可视化组件 (VectorAddition, MatrixTransform, EigenVisualizer)
│   └── Dockerfile
├── Docs/               # 项目文档与资源
└── docker-compose.yml  # 容器编排配置
```

## 3. 核心功能实现 (Core Features)

### 3.1 向量加法交互演示 (Vector Addition)
- **功能**: 用户可拖拽两个向量 $\vec{u}$ 和 $\vec{v}$ 的终点。
- **视觉反馈**: 实时显示平移后的辅助线（平行四边形法则）以及合向量 $\vec{u}+\vec{v}$，直观展示向量加法的几何意义。

### 3.2 矩阵线性变换 (Matrix Transformation)
- **功能**: 用户通过拖拽基向量 $\hat{i}$ 和 $\hat{j}$ 来定义变换矩阵 $A$。
- **视觉反馈**: 整个坐标网格随之发生倾斜、旋转或缩放，用户可放置测试点观察变换前后的位置映射，深刻理解“矩阵即变换”的核心概念。

### 3.3 特征值与特征向量可视化 (Eigenvalues Visualization)
- **功能**: 用户输入矩阵数值，并在坐标系中拖动向量 $\vec{x}$。
- **创新点**: 
  - **Ground Truth 对比**: 调用后端 NumPy 计算真实特征值供参考。
  - **交互式发现**: 当用户手动将 $\vec{x}$ 拖动到与 $A\vec{x}$ 共线的位置时，系统会自动高亮并提示 "Found Eigenvector!"，将抽象的特征值概念具象化为“方向不变”的几何特征。

### 3.4 形式化验证 Agent 演示 (Formalization Agent)
- **功能**: 模拟“从自然语言到 Lean 代码”的转换过程。
- **流程**: 前端提交数学问题 -> 后端“Agent”生成对应的 Lean 4 代码模板 -> 模拟运行验证器并返回结果。这展示了未来数学工具的发展方向——AI辅助定理证明。

## 4. 结论与展望 (Conclusion)

本项目成功实现了一个低代码、高交互的线性代数可视化平台。通过 Docker 容器化部署，极大地降低了环境配置门槛。特别是形式化验证模块的引入，虽然目前处于演示阶段，但为后续引入真正的 Lean 4 编译器和大规模 Mathlib 库奠定了架构基础。该系统不仅适用于辅助教学，也展示了 AI 在数学教育和研究中的巨大潜力。




# 修改之后
矩阵变换 (MatrixTransform)：
现在背景里有一个深色的原始网格，和一个跟随变换的浅色网格。
中心还增加了一个淡蓝色的“单位正方形”。
动手试试：拖动红蓝基向量，您会直观地看到这个正方形是如何被“压扁”、“拉长”或“旋转”的。这就是线性变换的几何本质！
特征值可视化 (EigenVisualizer)：
我给橙色向量添加了一条虚线延长线 (Span Line)。
我还把真实的特征向量作为半透明的“幽灵”显示在图上。
游戏目标：您现在的任务变得非常简单直观——把橙色向量拖动去重合那些“幽灵线”。一旦重合，紫色向量 $Ax$ 就会稳稳地落在虚线上，那一行绿色的 "Found Eigenvector!" 就会亮起。