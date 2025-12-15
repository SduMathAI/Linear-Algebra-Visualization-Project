
import sys
import os
import json
from unittest.mock import MagicMock
from app import app

# Mock the OpenAI client within app
import app as app_module
mock_client = MagicMock()
app_module.client = mock_client

def test_lean_intro():
    # Setup mock response for Lean Intro
    mock_response_content = json.dumps({
        "operation": "lean_intro",
        "inputs": {"topic": "lean_intro"},
        "visualization_config": {"comment": ""},
        "lean": {
            "statement_cn": "Lean 是一个交互式定理证明器...",
            "statement_informal": "",
            "lean_code": "",
            "hint": ""
        },
        "explanation": "Test explanation"
    })
    
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content=mock_response_content))]
    mock_client.chat.completions.create.return_value = mock_completion

    with app.test_client() as client:
        payload = {"message": "给我讲讲什么是 Lean"}
        response = client.post('/chat', json=payload)
        
        if response.status_code != 200:
            print(f"Failed with status {response.status_code}: {response.get_data(as_text=True)}")
        
        assert response.status_code == 200
        data = response.get_json()
        print(f"\n[Lean Intro Test]\nInput: {payload['message']}\nOutput: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        assert "operation" in data
        assert data["operation"] == "lean_intro"
        assert "lean" in data

def test_rotation_matrix():
    # Setup mock response for Rotation Matrix (Markdown stripped test)
    # Simulate LLM returning markdown code block
    mock_response_content = "```json\n" + json.dumps({
        "operation": "mat_mul",
        "inputs": {"matrix": [[0, -1], [1, 0]]},
        "visualization_config": {"show_grid": True},
        "lean": {
            "statement_cn": "旋转保持长度",
            "lean_code": "theorem rotation_preserves_norm..."
        },
        "explanation": "展示旋转矩阵"
    }) + "\n```"

    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content=mock_response_content))]
    mock_client.chat.completions.create.return_value = mock_completion

    with app.test_client() as client:
        payload = {"message": "展示一个 90 度的旋转矩阵"}
        response = client.post('/chat', json=payload)
        
        assert response.status_code == 200
        data = response.get_json()
        print(f"\n[Rotation Matrix Test (Markdown Strip)]\nInput: {payload['message']}\nOutput: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        assert data["operation"] == "mat_mul"
        assert "lean" in data

if __name__ == "__main__":
    print("Starting verification (with Mocks)...")
    try:
        from app import SYSTEM_PROMPT
        # Basic check that System Prompt was updated
        if "lean_statement" not in SYSTEM_PROMPT:
            raise Exception("SYSTEM_PROMPT does not contain 'lean_statement'")
            
        test_lean_intro()
        test_rotation_matrix()
        print("\nVerification SUCCESS!")
    except Exception as e:
        print(f"\nVerification FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
