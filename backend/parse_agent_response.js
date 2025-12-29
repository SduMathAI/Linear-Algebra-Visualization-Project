/**
 * AgentResponseHandler.js
 * 
 * 这个工具类用于演示如何在前端分解和使用后端返回的 JSON 数据。
 * 假设 response 是从 API 获取到的 JSON 对象。
 */

function handleAgentResponse(response) {
    if (!response || !response.operation) {
        console.error("收到了无效的响应格式");
        return;
    }

    console.log(`🤖收到指令: ${response.operation}`);
    console.log(`💬解释: ${response.explanation}`);

    // 1. 根据 operation 决定大方向
    switch (response.operation) {
        // --- 可视化类指令 ---
        case 'vector_add':
        case 'lin_comb':
        case 'mat_mul':
        case 'eigen':
        case 'custom_matrix':
            handleVisualization(response);
            break;

        // --- Lean / 数学类指令 ---
        case 'lean_intro':
        case 'lean_statement':
        case 'math_problem':
            handleLeanContent(response);
            break;

        default:
            console.warn("未知的操作类型:", response.operation);
    }
}

// 2. 处理可视化逻辑
function handleVisualization(data) {
    const config = data.visualization_config || {};
    const inputs = data.inputs || {};

    console.log(">> 🎨 启动可视化模块...");

    // 这里的逻辑对应前端具体的绘图函数
    if (config.show_grid) {
        console.log("   - [UI] 显示网格");
    }

    if (data.operation === 'mat_mul') {
        const matrix = inputs.matrix;
        const vectors = inputs.vectors; // 可能为空，取决于用户是否指定了向量
        console.log(`   - [Action] 应用矩阵变换: ${JSON.stringify(matrix)}`);
        if (vectors) {
            console.log(`   - [Action] 变换向量: ${JSON.stringify(vectors)}`);
        }
    } else if (data.operation === 'eigen') {
        console.log(`   - [Action] 计算并展示特征向量...`);
    }

    // 如果碰巧这个可视化请求里也夹带了 Lean 习题（如示例 2）
    if (data.lean && data.lean.statement_cn) {
        console.log("   - [UI] 注意：虽然是可视化，但右侧栏要显示 Lean 题目！");
        renderLeanCard(data.lean);
    }
}

// 3. 处理 Lean 逻辑
function handleLeanContent(data) {
    console.log(">> 📐 启动 Lean 教学模块...");
    const leanData = data.lean;

    renderLeanCard(leanData);
}

// 4. 渲染 Lean 卡片（模拟前端 UI 组件更新）
function renderLeanCard(leanData) {
    if (!leanData) return;

    console.log("   ------ Lean Card ------");
    console.log(`   题目: ${leanData.statement_cn}`);
    if (leanData.statement_informal) {
        console.log(`   符号: ${leanData.statement_informal}`);
    }
    console.log(`   代码: \n${leanData.lean_code}`);
    if (leanData.hint) {
        console.log(`   提示: 💡 ${leanData.hint}`);
    }
    console.log("   -----------------------");
}

// ==========================================
// 测试示例
// ==========================================

// 模拟场景 A：可视化响应
const sampleResponseA = {
    "operation": "mat_mul",
    "inputs": {
        "matrix": [[0, -1], [1, 0]]
    },
    "visualization_config": {
        "show_grid": true,
        "comment": "展示旋转"
    },
    "explanation": "这是一个 90 度旋转矩阵。"
};

// 模拟场景 B：Lean 题目响应
const sampleResponseB = {
    "operation": "lean_statement",
    "inputs": { "topic": "eigen" },
    "lean": {
        "statement_cn": "证明特征向量...",
        "lean_code": "theorem ...",
        "hint": "定义..."
    },
    "explanation": "请尝试证明。"
};

console.log("\n====== 测试场景 A (可视化) ======");
handleAgentResponse(sampleResponseA);

console.log("\n====== 测试场景 B (Lean) ======");
handleAgentResponse(sampleResponseB);
