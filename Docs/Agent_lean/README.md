## 一、先把“需求类型”再细分一下

在原来的基础上，我们把 Agent 的能力分成两大块：

### A. 线性代数可视化（原有）

> 左侧UI展示

* `vector_add`
* `lin_comb`
* `mat_mul`
* `eigen`
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

```jsonc
{
  "operation": "lean_statement",      // 或 lean_intro / math_problem / 之前的 vector_add 等
  "inputs": {
    "topic": "eigen",                 // 主题，例如 eigen/mat_mul/invertible
    "difficulty": "easy",             // optional: easy/medium/hard
    "context": "我们刚刚在图上展示了一个 2x2 旋转矩阵。"
  },
  "visualization_config": {           // 对 Lean 请求可以为空 或给前端提示
    "show_grid": false,
    "show_unit_vectors": false,
    "animate": false,
    "comment": "本次请求主要是 Lean 命题，无需可视化。"
  },
  "lean": {                           // ★ 新增模块：只有 Lean 相关 operation 会填
    "statement_cn": "在实数域上，任何正交矩阵都保持向量长度不变。",
    "statement_informal": "∀ v, ∥A v∥ = ∥v∥",
    "lean_code": "theorem orthogonal_preserve_norm\n  {A : ℝ →ₗ[ℝ] ℝ} (hA : IsOrthogonal A) :\n  ∀ v, ‖A v‖ = ‖v‖ := by\n  sorry",
    "hint": "可以使用内积保持的性质，再推出范数保持。"
  },
  "explanation": "我们生成了一个关于正交线性变换保持向量长度的命题，并给出了一个 Lean 定理骨架，学生可以尝试补全 proof。"
}
```

对线代可视化类的请求，`lean` 字段可以省略；对 Lean 类请求，`visualization_config` 可以简化。

---

## 三、更新 System Prompt（直接可用）

在原先“线性代数可视化 Agent”的系统提示基础上，加上 Lean 的部分：

````text
你是一个“线性代数可视化 + Lean 科普和命题工具”的智能 Agent。

【一、总目标】
- 当用户提到线性代数运算（向量加法、线性组合、矩阵乘法、线性变换、特征值与特征向量等），你要把需求转成可视化指令。
- 当用户想了解 Lean、想得到和当前图形或主题相关的数学命题、Lean 代码骨架时，你要扮演 Lean 助教。
- 你始终只输出一个 JSON 对象，不要有其它文字。

【二、operation 枚举值】
（1）线性代数可视化：
- "vector_add" : 向量加法可视化
- "lin_comb"   : 线性组合可视化
- "mat_mul"    : 矩阵乘法或线性变换
- "eigen"      : 特征值与特征向量可视化
- "custom_matrix" : 用户自定义矩阵的通用变换展示

（2）Lean 相关：
- "lean_intro"     : 对 Lean / 形式化证明做科普讲解，面向初学者
- "lean_statement" : 生成与当前主题相关的数学命题 + 对应 Lean 定理代码骨架
- "math_problem"   : 生成若干线性代数练习题，可附带 Lean 形式化建议

（3）其它：
- "other" : 无法归类到上面时使用（尽量少用）

【三、JSON 输出格式】
你必须严格输出下列结构：

{
  "operation": "<上面的枚举之一>",
  "inputs": {
    // 若是可视化类：如 "vectors": [[x1,y1], ...] 或 "matrix": [[..],[..]]
    // 若是 Lean 类：如 "topic": "eigen", "difficulty": "easy", "context": "用户描述或当前图像概况"
  },
  "visualization_config": {
    "show_grid": true 或 false,
    "show_unit_vectors": true 或 false,
    "animate": true 或 false,
    "comment": "给前端的一些展示提示，可以为空字符串"
  },
  "lean": {
    // 只有在 operation 为 lean_intro / lean_statement / math_problem 时才需要：
    "statement_cn": "中文描述的命题或科普内容",
    "statement_informal": "可选：用数学符号非形式化写法，如 ∀ v, ...",
    "lean_code": "可选：对应的 Lean 代码片段或 theorem 骨架",
    "hint": "可选：给学生的提示或进一步学习建议"
  },
  "explanation": "用中文简要说明这次请求你打算展示什么或学什么。"
}

【四、注意事项】
- 只输出 JSON，不要写反引号 ```，不要写任何 JSON 之外的文字。
- Lean 代码目标版本：Lean 4 + mathlib，采用标准风格；不要求 proof 完成，可以用 `sorry` 占位。
- 当用户没有给出具体矩阵/向量，但提到主题（例如“来点关于特征值的 Lean 练习”），你可以自己设计简单的 2x2 或 3x3 矩阵。
- 所有解释和命题，请用中文说明，方便教学使用。
````

> 你在调用 LLM API 时，把这段当作 `system` 消息；用户的自然语言当作 `user` 消息即可。

---

## 四、给你几个“结合图形内容”的示例（Few-shot 用）

### 示例 1：根据当前旋转矩阵图形，生成 Lean 命题

**用户（你们前端会发给 LLM 的 prompt 可以长这样）：**

> 我们当前在图上展示的是二维平面上的旋转矩阵
> R = [[0,-1],[1,0]] 对一堆点的作用。
> 请给一个与旋转矩阵相关的 Lean 练习命题，简单一点。

**期望 LLM 返回 JSON：**

```json
{
  "operation": "lean_statement",
  "inputs": {
    "topic": "rotation_matrix",
    "difficulty": "easy",
    "context": "二维平面上 90 度旋转矩阵 R = [[0,-1],[1,0]]"
  },
  "visualization_config": {
    "show_grid": false,
    "show_unit_vectors": false,
    "animate": false,
    "comment": "本次侧重 Lean 命题，不需要额外可视化。"
  },
  "lean": {
    "statement_cn": "证明二维平面上的 90 度旋转矩阵保持向量的长度不变。",
    "statement_informal": "对于任意 v ∈ ℝ²，有 ‖R v‖ = ‖v‖。",
    "lean_code": "theorem rotation90_preserve_norm\n  (v : ℝ × ℝ) :\n  ‖(0, -1; 1, 0) * v‖ = ‖v‖ := by\n  sorry",
    "hint": "可以把旋转看成正交矩阵的一种特例，先证明 Rᵀ R = I，再推出范数保持。"
  },
  "explanation": "我们围绕当前展示的 90 度旋转矩阵，设计了一个关于“旋转保持长度”的 Lean 命题，供学生在 Lean 中尝试形式化。"
}
```

（Lean 代码细节你之后可以再手动润色，这里主要是结构和思路。）

---

### 示例 2：让 Agent 既给图形操作又给 Lean 任务

**用户：**

> 帮我演示一下一个 2x2 可逆矩阵对平面的作用，并给一个关于“可逆矩阵保持线性无关性”的 Lean 命题。

期望 LLM 识别出：既要可视化，又要 Lean 命题。这里你可以让它仍然选 `operation: "mat_mul"`，但在 `lean` 部分顺便给练习：

```json
{
  "operation": "mat_mul",
  "inputs": {
    "matrix": [[2, 1], [1, 1]]
  },
  "visualization_config": {
    "show_grid": true,
    "show_unit_vectors": true,
    "animate": true,
    "comment": "展示单位方格被拉伸、平行四边形变形，但不过原点。"
  },
  "lean": {
    "statement_cn": "证明在实数向量空间中，可逆线性变换将线性无关组变成线性无关组。",
    "statement_informal": "若 T 可逆，且 {v₁,…,vₙ} 线性无关，则 {T v₁,…,T vₙ} 线性无关。",
    "lean_code": "theorem linear_map.linearIndependent_image\n  {V : Type _} [AddCommGroup V] [Module ℝ V]\n  (T : V →ₗ[ℝ] V) (hT : LinearMap.ker T = ⊥)\n  {s : Set V} (hs : s.LinearIndependent ℝ) :\n  (T '' s).LinearIndependent ℝ := by\n  sorry",
    "hint": "可以利用 T 可逆 等价于 ker T = {0}，再用线性无关的定义展开证明。"
  },
  "explanation": "我们选取了一个 2x2 可逆矩阵展示其对平面的线性变换效果，同时给出一个关于可逆线性变换保持线性无关性的 Lean 命题骨架。"
}
```

---

## 五、你们在报告/PPT里可以怎么说？

在**技术报告 / PPT**的“Agent 设计”部分，你可以这样描述（我帮你概括几句话，后面你可以让我单独写成报告段落）：

* 我们将用户需求划分为
  ① 线性代数可视化类操作
  ② Lean 科普与命题生成类操作
* 通过统一的 JSON 协议，前端只需要关心 `operation` 和数据结构，不必关心 LLM 的具体行为。
* Agent 不仅能把“想看的实验”翻译成具体的矩阵和向量，还能自动生成与当前实验相关的 Lean 命题与代码骨架，实现了**可视化教学 + 形式化证明练习的一体化平台**。

---

## 六、怎么判断“合格的 Agent”？

在你们的大作业展示里，可以从这几个维度讲：

1. **鲁棒性**：

   * 输入不同说法（“画一下”、“可视化”、“演示……的几何意义”），Agent 都能归到正确的 `operation`
2. **结构化输出**：

   * 始终输出合法 JSON，易于前端调用
3. **教学友好**：

   * `explanation` 简短清晰、配合可视化理解线性代数概念
4. **可扩展性**：

   * 以后想新增「奇异值分解 SVD 可视化」只需要：

     * 新增一个 `operation: "svd"`
     * 后端增加对应计算与画图函数
     * 在 Prompt 中说明 SVD 的用法
