import requests
import json

BASE_URL = "http://127.0.0.1:5000/chat"

def request_agent(message):
    """
    通用请求函数，发送消息给 Agent 并打印返回的 JSON。
    """
    try:
        response = requests.post(BASE_URL, json={"message": message})
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status {response.status_code}", "body": response.text}
    except Exception as e:
        return {"error": str(e)}

def scenario_visualization_default(input_text="展示一个 90 度的旋转矩阵作用在向量上"):
    """
    场景 A：请求可视化 (线性代数)
    默认输入: "展示一个 90 度的旋转矩阵作用在向量上"
    """
    print(f"\n--- 场景 A: 可视化请求 ---\n输入: {input_text}")
    result = request_agent(input_text)
    print("Agent 回复:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

def scenario_lean_exercise(input_text="给我出一个关于旋转矩阵保持长度不变的 Lean 练习题"):
    """
    场景 B：请求 Lean 命题
    默认输入: "给我出一个关于旋转矩阵保持长度不变的 Lean 练习题"
    """
    print(f"\n--- 场景 B: Lean 命题请求 ---\n输入: {input_text}")
    result = request_agent(input_text)
    print("Agent 回复:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

def scenario_lean_intro(input_text="Lean 是什么？"):
    """
    场景 C：Lean 科普
    默认输入: "Lean 是什么？"
    """
    print(f"\n--- 场景 C: Lean 科普请求 ---\n输入: {input_text}")
    result = request_agent(input_text)
    print("Agent 回复:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    # 为了演示，你可以直接运行这个脚本（确保 backend/app.py 正在运行）
    # 如果你也想在这里 mock，那需要写在单元测试里。这里作为客户端示例。
    
    # 1. 场景 A
    scenario_visualization_default()
    
    # 2. 场景 B
    scenario_lean_exercise()
    
    # 3. 场景 C
    scenario_lean_intro()
