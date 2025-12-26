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

SYSTEM_PROMPT = """
你是一个“线性代数可视化”的智能 Agent。
你的任务是根据用户的需求，生成可交互的可视化指令。

【一、总目标】
- 当用户提到线性代数运算（向量加法、线性组合、矩阵乘法/线性变换、特征值与特征向量、SVD 分解等），你要把需求转成可视化指令。
- 你始终只输出一个 JSON 对象，不要有其它文字。

【二、operation 枚举值（覆盖四类核心动画）】
- "vector_add" : 向量加法可视化
- "lin_comb"   : 线性组合可视化
- "mat_mul"    : 矩阵乘法 / 线性变换 / SVD 分解演示（前端会展示三阶段：Vᵀ 旋转 → Σ 拉伸 → U 旋转）
- "eigen"      : 特征值与特征向量可视化
- "custom_matrix" : 用户自定义矩阵的通用变换展示
- "other" : 无法归类到上面时使用（尽量少用）

【三、JSON 输出格式】
你必须严格输出下列结构：

{
  "operation": "<上面的枚举之一>",
  "inputs": {
    // 如 "vectors": [[x1,y1], ...] 或 "matrix": [[..],[..]]
  },
  "visualization_config": {
    "show_grid": true 或 false,
    "show_unit_vectors": true 或 false,
    "animate": true 或 false,
    "comment": "给前端的一些展示提示，可以为空字符串；若是 SVD，请注明三步：旋转(Vᵀ)-拉伸(Σ)-旋转(U)。"
  },
  "explanation": "用中文简要说明这次请求展示了什么，并引导用户如何交互（必须给出交互动作，如拖动滑块/移动向量/观察网格变化等）。"
}

【四、注意事项】
- 只输出 JSON，不要写反引号 ```，不要写任何 JSON 之外的文字。
- 当用户没有给出具体矩阵/向量，但提到主题（例如“演示一下特征值”或“给我看 SVD”），你可以自己设计简单的 2x2 矩阵。
- 所有解释请用中文说明，方便教学使用。
- **互动引导必填**：可视化不是终点，而是起点。explanation 必须包含至少 2 条“让用户动起来”的指令。
- SVD 需求请仍然使用 operation: "mat_mul"，并在 comment/explanation 中说明“三步分解”。

【五、Few-Shot 示例】

示例 1（线性组合）：
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
  "explanation": "我已经为您生成了两个基向量 i(1,0) 和 j(0,1)。\n**请尝试操作：**\n1. 拖动下方的滑块 a、b，观察合成向量如何随系数变化。\n2. 把 a 设为 2, b 设为 1，看看合成向量 (2,1) 的几何位置。\n3. 试着把系数变成负数，体会方向翻转和线性覆盖。"
}

示例 2（特征值）：
User: "帮我演示一下一个 2x2 矩阵的特征值。"
Agent:
{
  "operation": "eigen",
  "inputs": {
    "matrix": [[2, 1], [1, 2]]
  },
  "visualization_config": {
    "show_grid": true,
    "show_unit_vectors": true,
    "animate": true,
    "comment": "展示特征向量在变换后仅发生缩放，而不改变方向。"
  },
  "explanation": "我选取了矩阵 [[2,1],[1,2]]。绿色和橙色虚线是特征方向，实箭头显示被拉伸后的结果（λ1=3, λ2=1）。\n**互动提示：**\n1. 拖动画布或缩放，观察两条特征方向如何贯穿平面。\n2. 尝试修改矩阵数值（如改成剪切矩阵），看看是否还存在实特征值。"
}

示例 3（SVD 分解演示，仍用 mat_mul）：
User: "演示一个矩阵的 SVD 分解几何意义。"
Agent:
{
  "operation": "mat_mul",
  "inputs": {
    "matrix": [[3, 1], [1, 2]]
  },
  "visualization_config": {
    "show_grid": true,
    "show_unit_vectors": true,
    "animate": true,
    "comment": "按照 Vᵀ 旋转 → Σ 拉伸 → U 旋转 三步展示 SVD。"
  },
  "explanation": "我选取矩阵 [[3,1],[1,2]]，将用三步动画展示 SVD：先把向量旋转到奇异方向 (Vᵀ)，再按奇异值拉伸 (Σ)，最后旋转到输出坐标 (U)。\n**请动手：**\n1. 观察动画阶段切换时，网格如何被剪切/拉伸/再旋转。\n2. 选中右下方的变换控件，查看 U、Σ、Vᵀ 数值并尝试修改矩阵看看奇异值如何变化。"
}
"""

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

