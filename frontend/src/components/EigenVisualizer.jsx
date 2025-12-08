import React, { useState } from "react";
import { Mafs, Coordinates, Vector, useMovablePoint, Text, Line } from "mafs";
import axios from "axios";

const EigenVisualizer = () => {
    const [matrixVal, setMatrixVal] = useState([[2, 0], [0, 3]]);
    const [eigenData, setEigenData] = useState(null);

    // Interactive vector (Renamed 'inputVector' to avoid any 'x' variable shadowing confusion)
    const inputVector = useMovablePoint([1, 1], { color: "orange" });

    // Calculate Ax
    const outputX = matrixVal[0][0] * inputVector.x + matrixVal[0][1] * inputVector.y;
    const outputY = matrixVal[1][0] * inputVector.x + matrixVal[1][1] * inputVector.y;

    // Check if aligned (approx)
    // Cross product in 2D: x1*y2 - x2*y1. If 0, parallel.
    const crossProduct = inputVector.x * outputY - inputVector.y * outputX;

    // Thresholds for eigen detection
    const isParallel = Math.abs(crossProduct) < 0.1;
    const nonZero = Math.abs(inputVector.x) > 0.1 || Math.abs(inputVector.y) > 0.1;
    const isEigen = isParallel && nonZero;

    // Calculate ratio (eigenvalue) safely
    const ratio = Math.abs(inputVector.x) > 0.1 ? outputX / inputVector.x : outputY / inputVector.y;

    const fetchEigen = async () => {
        try {
            const res = await axios.post("http://localhost:5000/api/eigen", { matrix: matrixVal });
            setEigenData(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const verifyFormal = async () => {
        try {
            const res = await axios.post("http://localhost:5000/api/formalize", { problem: `Eigenvalues of [[${matrixVal}]]` });
            alert(`Simulated Lean Code:\n${res.data.lean_code}`);
        } catch (err) {
            console.error(err);
        }
    }

    return (
        <div className="p-4 bg-white rounded-xl shadow-md">
            <h2 className="text-xl font-bold mb-4">特征值与特征向量 (Eigenvalues & Eigenvectors)</h2>

            <div className="mb-4 flex gap-4 items-center">
                <div>
                    Matrix:
                    <input className="border p-1 w-12 ml-2" type="number" value={matrixVal[0][0]} onChange={e => { const m = [...matrixVal]; m[0][0] = Number(e.target.value); setMatrixVal(m) }} />
                    <input className="border p-1 w-12" type="number" value={matrixVal[0][1]} onChange={e => { const m = [...matrixVal]; m[0][1] = Number(e.target.value); setMatrixVal(m) }} />
                    <br />
                    <input className="border p-1 w-12 ml-[3.5rem]" type="number" value={matrixVal[1][0]} onChange={e => { const m = [...matrixVal]; m[1][0] = Number(e.target.value); setMatrixVal(m) }} />
                    <input className="border p-1 w-12" type="number" value={matrixVal[1][1]} onChange={e => { const m = [...matrixVal]; m[1][1] = Number(e.target.value); setMatrixVal(m) }} />
                </div>
                <button onClick={fetchEigen} className="bg-blue-500 text-white px-4 py-2 rounded">Check Ground Truth</button>
                <button onClick={verifyFormal} className="bg-purple-600 text-white px-4 py-2 rounded">Formalize & Verify (Agent)</button>
            </div>

            <p className="mb-2">
                Orange: Vector x | Purple: Vector Ax <br />
                {isEigen && <span className="text-green-600 font-bold text-lg animate-pulse">Found Eigenvector! Lambda approx {ratio.toFixed(2)}</span>}
            </p>

            <Mafs height={400} viewBox={{ x: [-6, 6], y: [-6, 6] }}>
                <Coordinates.Cartesian />

                {/* Visual Aid: Linear Span of x */}
                <Line.ThroughPoints
                    point1={[0, 0]}
                    point2={[inputVector.x, inputVector.y]}
                    color="orange"
                    style="dashed"
                    opacity={0.4}
                />

                {/* Step 2: Input Vector x */}
                <Vector tail={[0, 0]} tip={[inputVector.x, inputVector.y]} color="orange" weight={3} />
                <Text x={inputVector.x} y={inputVector.y} attach="ne" color="orange">x</Text>
                {inputVector.element}

                {/* Step 3: Transformed Vector Ax */}
                <Vector tail={[0, 0]} tip={[outputX, outputY]} color="purple" weight={3} />
                <Text x={outputX} y={outputY} attach="ne" color="purple">Ax</Text>

                {/* Show actual eigenvectors if loaded */}
                {eigenData && eigenData.eigenvectors.map((vec, i) => (
                    // Eigenvectors from numpy are columns.
                    <React.Fragment key={i}>
                        <Line.ThroughPoints
                            point1={[0, 0]}
                            point2={[eigenData.eigenvectors[0][i], eigenData.eigenvectors[1][i]]}
                            color="gray"
                            style="dashed"
                            opacity={0.2}
                        />
                        <Vector tail={[0, 0]} tip={[eigenData.eigenvectors[0][i], eigenData.eigenvectors[1][i]]} color="black" opacity={0.2} style="dashed" />
                    </React.Fragment>
                ))}
            </Mafs>
        </div>
    );
};

export default EigenVisualizer;
