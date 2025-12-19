import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import glob
import re
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

app = Flask(__name__)
CORS(app)

# Initialize OpenAI Client (Expects DEEPSEEK_API_KEY env var)
try:
    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"), 
        base_url="https://api.deepseek.com"
    )
except Exception as e:
    print(f"Warning: DeepSeek client could not be initialized: {e}")
    client = None

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Docs')

def load_context():
    context = ""
    try:
        files = glob.glob(os.path.join(DOCS_DIR, '*'))
        for file_path in files:
            if file_path.lower().endswith(('.txt', '.md')):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        filename = os.path.basename(file_path)
                        context += f"\n--- Start of {filename} ---\n{content}\n--- End of {filename} ---\n"
                except Exception as ex:
                    print(f"Error reading {file_path}: {ex}")
    except Exception as e:
        print(f"Error loading context: {e}")
    return context

PROJECT_CONTEXT = load_context()

SYSTEM_PROMPT_TEMPLATE = """
你是一个“线性代数可视化 + Lean 科普和命题工具”的智能 Agent。
你有权限访问项目的文档和技术报告，以下是项目上下文：
{PROJECT_CONTEXT}

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
  "explanation": "用中文简要说明这次请求展示了什么。更重要的是，**也就是必须**要在回复中引导用户如何去交互（例如：'请尝试拖动滑块 a 和 b'，'拖动向量的箭头'，'观察当两个向量共线时会发生什么'）以直观体会数学概念。"
}

【四、注意事项】
- 只输出 JSON，不要写反引号 ```，不要写任何 JSON 之外的文字。
- Lean 代码目标版本：Lean 4 + mathlib，采用标准风格；不要求 proof 完成，可以用 `sorry` 占位。
- 当用户没有给出具体矩阵/向量，但提到主题（例如“来点关于特征值的 Lean 练习”），你可以自己设计简单的 2x2 或 3x3 矩阵。
- 所有解释和命题，请用中文说明，方便教学使用。
- **互动引导**：可视化不是终点，而是起点。你的 explanation 必须包含让用户“动起来”的指令。

【五、Few-Shot 示例】

示例 1（线性组合 + 互动）：
User: "请为我展示线性组合规则。"
Agent:
{
  "operation": "lin_comb",
  "inputs": {
    "vectors": [[1, 2], [2, 1]]
  },
  "visualization_config": {
    "show_grid": true,
    "show_unit_vectors": false,
    "animate": true,
    "comment": "初始化两个基向量，并自动选中线性组合对象以显示滑块。"
  },
  "lean": {},
  "explanation": "我已经为您生成了两个基向量 v1 (1,2) 和 v2 (2,1)。\n**请尝试操作：**\n1. 拖动页面下方的 **滑块 a** 和 **滑块 b**，观察合成向量（青色）是如何随着系数变化的。\n2. 试着把 a 和 b 都设为 1，看看向量加法的平行四边形法则。\n3. 思考：当 v1 和 v2 共线时，合成向量还能覆盖整个平面吗？"
}

示例 2（Lean 命题）：
User: "我们当前在图上展示的是二维平面上的旋转矩阵 R = [[0,-1],[1,0]] 对一堆点的作用。请给一个与旋转矩阵相关的 Lean 练习命题，简单一点。"
Agent:
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
    "lean_code": "theorem rotation90_preserve_norm\\n  (v : ℝ × ℝ) :\\n  ‖(0, -1; 1, 0) * v‖ = ‖v‖ := by\\n  sorry",
    "hint": "可以把旋转看成正交矩阵的一种特例，先证明 Rᵀ R = I，再推出范数保持。"
  },
  "explanation": "我们围绕当前展示的 90 度旋转矩阵，设计了一个关于“旋转保持长度”的 Lean 命题，供学生在 Lean 中尝试形式化。"
}

示例 2（可视化 + Lean 命题）：
User: "帮我演示一下一个 2x2 可逆矩阵对平面的作用，并给一个关于“可逆矩阵保持线性无关性”的 Lean 命题。"
Agent:
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
    "statement_informal": "若 T 可逆，且 {v1,...,vn} 线性无关，则 {T v1,...,T vn} 线性无关。",
    "lean_code": "theorem linear_map.linearIndependent_image\\n  {V : Type _} [AddCommGroup V] [Module ℝ V]\\n  (T : V →ₗ[ℝ] V) (hT : LinearMap.ker T = ⊥)\\n  {s : Set V} (hs : s.LinearIndependent ℝ) :\\n  (T '' s).LinearIndependent ℝ := by\\n  sorry",
    "hint": "可以利用 T 可逆 等价于 ker T = {0}，再用线性无关的定义展开证明。"
  },
  "explanation": "我们选取了一个 2x2 可逆矩阵展示其对平面的线性变换效果，同时给出一个关于可逆线性变换保持线性无关性的 Lean 命题骨架。"
}
"""

SYSTEM_PROMPT = SYSTEM_PROMPT_TEMPLATE.replace("{PROJECT_CONTEXT}", PROJECT_CONTEXT)

@app.route('/chat', methods=['POST'])
def chat():
    if not client:
        return jsonify({"error": "OpenAI API Key not configured."}), 500

    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = client.chat.completions.create(
            model="deepseek-chat", 
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        
        # Strip markdown code blocks if present
        if content.startswith("```"):
            content = re.sub(r'^```(json)?\n', '', content)
            content = re.sub(r'\n```$', '', content)
        
        try:
            parsed_json = json.loads(content)
            return jsonify(parsed_json)
        except json.JSONDecodeError:
            # Fallback if model failed to output pure JSON
            print(f"Failed to parse JSON: {content}")
            return jsonify({
                "operation": "other",
                "explanation": "Model output failed to parse as JSON.",
                "raw_content": content
            })

    except Exception as e:
        print(f"Error calling LLM: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5500, debug=True)

