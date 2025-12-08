from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import subprocess

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Neuro-Symbolic Linear Algebra Backend is Running!"

@app.route('/api/eigen', methods=['POST'])
def calculate_eigen():
    try:
        data = request.json
        matrix_data = data.get('matrix')
        if not matrix_data:
            return jsonify({"error": "No matrix provided"}), 400
        
        # Expecting a list of lists, e.g., [[2, 0], [0, 3]]
        matrix = np.array(matrix_data)
        
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        
        # Format for frontend
        result = {
            "eigenvalues": eigenvalues.tolist(),
            "eigenvectors": eigenvectors.tolist() # Note: eigenvectors are columns
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/formalize', methods=['POST'])
def formalize_problem():
    # Simulate Agent converting text/problem to Lean code
    data = request.json
    problem_text = data.get('problem', '')
    
    # Mock response for demo purposes
    lean_code = f"""
import Mathlib.LinearAlgebra.Matrix.Basic

-- Auto-generated from: {problem_text}
-- Validating basic properties
example : 1 + 1 = 2 := by rfl
"""
    return jsonify({"lean_code": lean_code, "status": "generated"})

@app.route('/api/verify', methods=['POST'])
def verify_lean():
    # Simulate running Lean 4
    # In a real environment, this would subprocess call 'lake env lean ...'
    data = request.json
    code = data.get('code', '')
    
    # Mock verification
    return jsonify({
        "verified": True,
        "output": "Goals solved!",
        "message": "Verification successful (Simulated)"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
