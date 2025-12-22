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
- 当用户提到线性代数运算（向量加法、线性组合、矩阵乘法、线性变换、特征值与特征向量等），你要把需求转成可视化指令。
- 你始终只输出一个 JSON 对象，不要有其它文字。

【二、operation 枚举值】
- "vector_add" : 向量加法可视化
- "lin_comb"   : 线性组合可视化
- "mat_mul"    : 矩阵乘法或线性变换
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
    "comment": "给前端的一些展示提示，可以为空字符串"
  },
  "explanation": "用中文简要说明这次请求展示了什么。更重要的是，**也就是必须**要在回复中引导用户如何去交互（例如：'请尝试拖动滑块 a 和 b'，'拖动向量的箭头'，'观察当两个向量共线时会发生什么'）以直观体会数学概念。"
}

【四、注意事项】
- 只输出 JSON，不要写反引号 ```，不要写任何 JSON 之外的文字。
- 当用户没有给出具体矩阵/向量，但提到主题（例如“演示一下特征值”），你可以自己设计简单的 2x2 矩阵。
- 所有解释请用中文说明，方便教学使用。
- **互动引导**：可视化不是终点，而是起点。你的 explanation 必须包含让用户“动起来”的指令。

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
  "explanation": "我已经为您生成了两个基向量 i(1,0) 和 j(0,1)。\n**请尝试操作：**\n1. 拖动页面下方的 **滑块 a** 和 **滑块 b**，观察合成向量（青色）是如何随着系数 a 和 b 变化的。\n2. 试着把 a 设为 2, b 设为 1，看看向量 (2, 1) 是如何由 2*i + 1*j 构成的。\n3. 思考：当 a 和 b 取不同值时，合成向量能覆盖平面上的哪些点？这体现了线性组合的什么核心思想？"
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
  "explanation": "我为您选取了一个矩阵 [[2,1],[1,2]]。在该变换下，绿色的箭头和橙色的箭头就是特征向量。它们在被矩阵作用后，方向没有改变，只是长度发生了缩放（λ1=3, λ2=1）。\n**互动提示：**\n1. 请观察那两个特殊的虚线方向，那是特征空间。\n2. 试着通过代码生成不同的矩阵，看看有些矩阵是否没有实数特征值。"
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

