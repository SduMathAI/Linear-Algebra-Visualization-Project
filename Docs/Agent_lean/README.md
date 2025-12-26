## 一、先把“需求类型”再细分一下

在原来的基础上，我们把 Agent 的能力分成两大块：

### A. 线性代数可视化（左侧 UI）——覆盖四类动画

* `vector_add`：向量加法
* `lin_comb`：线性组合（滑块调系数 + 平移演示）
* `mat_mul`：矩阵乘法 / 线性变换 / **SVD 分解演示**（前端会三阶段播放：Vᵀ 旋转 → Σ 拉伸 → U 旋转；右下控件展示 U/Σ/Vᵀ 数值）
* `eigen`：特征值与特征向量
* `custom_matrix`
* `other`

### B. Lean 相关（你新增）

> 右侧UI展示

我建议增加 3 类 Lean 功能：

1. **Lean 科普讲解**（`lean_intro`）

   * 介绍 Lean 是什么、和数学/线代有什么关系
   * 解释“定理证明助手”“形式化证明”等概念
   * 适合在系统里做“帮助/教学区域”

2. **Lean 命题/代码生成**（`lean_statement`）
   根据用户需求，生成：

   * 一个数学命题（中文 + 非形式化）
   * 对应的 Lean 语句/定理骨架（不一定完全可过，但结构正确）
     例如：关于矩阵可逆、特征值、线性变换等

3. **练习/题目生成**（`math_problem`）
   根据当前可视化内容或用户要求，生成：

   * 一些矩阵/线代练习题
   * 可选附带 Lean 形式化目标（`theorem` stub）

---

## 二、更新 JSON 协议（在原来基础上加字段）

统一仍然只有一个 JSON，但对 Lean 相关多加一块：

# Agent Prompt（可视化版）

仅关注线性代数可视化，供 LLM 生成前端可执行的 JSON 指令。

## 1. 支持的 operation
- `vector_add`: 向量加法
- `lin_comb`: 线性组合（滑块调系数 + 平移演示）
- `mat_mul`: 矩阵乘法 / 线性变换 / SVD 分解演示（前端三步动画：Vᵀ 旋转 → Σ 拉伸 → U 旋转；右下控件展示 U/Σ/Vᵀ 数值）
- `eigen`: 特征值与特征向量
- `custom_matrix`: 自定义矩阵的通用变换展示
- `other`: 兜底

## 2. JSON 协议（只要这几个字段）
```jsonc
{
  "operation": "lin_comb | mat_mul | eigen | vector_add | custom_matrix | other",
  "inputs": {
    // 例如 vectors: [[x1,y1], [x2,y2]]
    // 或 matrix: [[a,b],[c,d]]
  },
  "visualization_config": {
    "show_grid": true,
    "show_unit_vectors": true,
    "animate": true,
    "comment": "可为空；SVD 请写明三步：Vᵀ-Σ-U；若要强调复合，写清先右乘再左乘。"
  },
  "explanation": "中文说明 + 至少 2 条交互指令（如拖动滑块/点击对象列表/拖动画布/缩放/改矩阵）。"
}
```

## 3. 注意
- 只输出 JSON，别用反引号或额外文字。
- 用户没给矩阵/向量可自造简单 2x2 示例。
- 互动引导必须存在，鼓励用户点击左侧对象列表选中 `trans_vec` / `trans_mat` / `lin_comb` 等查看右下控件的分步动画与数值。

## 4. Few-shot 示例（顺序已排好）

### 示例 1：线性组合（滑块 + 对象列表）
```json
{
  "operation": "lin_comb",
  "inputs": {
    "vectors": [[1, 2], [2, 1]]
  },
  "visualization_config": {
    "show_grid": true,
    "show_unit_vectors": false,
    "animate": true,
    "comment": "初始化两个基向量，自动选中线性组合对象以显示滑块。"
  },
  "explanation": "生成了基向量 (1,0) 和 (0,1)。\n1) 拖动下方滑块 a、b 观察合成向量变化；\n2) 把 a=2,b=1 看合成向量位置；\n3) 改成负系数体验方向翻转；\n4) 点击左侧对象列表选中 lin_comb，可在下方控件精细调节并观看动画。"
}
```

### 示例 2：特征值与特征向量
```json
{
  "operation": "eigen",
  "inputs": {
    "matrix": [[2, 1], [1, 2]]
  },
  "visualization_config": {
    "show_grid": true,
    "show_unit_vectors": true,
    "animate": true,
    "comment": "展示特征方向虚线与被拉伸后的实箭头。"
  },
  "explanation": "矩阵 [[2,1],[1,2]] 的特征方向用虚线标出，实箭头显示拉伸（λ1=3, λ2=1）。\n1) 拖动画布或缩放观察特征方向；\n2) 修改矩阵（如剪切矩阵）看是否还有实特征值；\n3) 点击左侧列表选中 eigen 或矩阵，在属性面板查看特征值/向量数值并配合动画理解。"
}
```

### 示例 3：SVD 几何意义（仍用 `mat_mul`）
```json
{
  "operation": "mat_mul",
  "inputs": {
    "matrix": [[3, 1], [1, 2]]
  },
  "visualization_config": {
    "show_grid": true,
    "show_unit_vectors": true,
    "animate": true,
    "comment": "按 Vᵀ → Σ → U 三步展示 SVD。"
  },
  "explanation": "用三步动画展示 SVD：先旋转到奇异方向 (Vᵀ)，再按奇异值拉伸 (Σ)，再旋转到输出坐标 (U)。\n1) 看网格三阶段形变；\n2) 点击左侧列表选中 trans_vec/trans_mat，在右下控件查看 U/Σ/Vᵀ 数值与分步动画；\n3) 改矩阵，比较奇异值和旋转角度变化。"
}
```

### 示例 4：矩阵乘法的几何意义（复合 = 相乘）
```json
{
  "operation": "mat_mul",
  "inputs": {
    "matrix": [[0, -1], [1, 1]]
  },
  "visualization_config": {
    "show_grid": true,
    "show_unit_vectors": true,
    "animate": true,
    "comment": "展示单位方格被剪切+旋转，并强调先右乘再左乘的两步复合。"
  },
  "explanation": "网格先被右侧矩阵剪切/旋转，再被左侧矩阵继续作用，等价于乘积矩阵一次完成——矩阵乘法=线性变换复合。\n1) 观察测试向量的中间态与终点；\n2) 点击左侧列表选中 trans_vec/trans_mat，看右下控件的分步动画与数值；\n3) 拖动画布或缩放看整体形变；\n4) 换成对角矩阵体验纯拉伸；\n5) 把其中一步改为纯旋转，对比“先旋转后拉伸”与“先拉伸后旋转”不交换。"
}
```
**期望 LLM 返回 JSON：**
