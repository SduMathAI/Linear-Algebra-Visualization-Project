import React, { useState } from "react";
import { Mafs, Coordinates, Vector, Transform, Text, useMovablePoint, Polygon } from "mafs";

const MatrixTransform = () => {
    const [matrixVal, setMatrixVal] = useState([[1, 0], [0, 1]]);
    const iHat = useMovablePoint([1, 0], { color: "blue" });
    const jHat = useMovablePoint([0, 1], { color: "red" });

    // Build transformation matrix from basis vectors
    // Matrix format for Mafs/SVG: [a, b, c, d, tx, ty]
    // where columns are (a, b) and (c, d)
    const transformMatrix = [iHat.x, iHat.y, jHat.x, jHat.y, 0, 0];

    return (
        <div className="p-4 bg-white rounded-xl shadow-md">
            <h2 className="text-xl font-bold mb-4">矩阵变换 (Matrix Transform)</h2>

            <div className="mb-4 flex gap-4 items-center">
                <div>
                    Matrix:
                    <input
                        className="border p-1 w-12 ml-2"
                        type="number"
                        value={matrixVal[0][0]}
                        onChange={e => {
                            const m = [...matrixVal];
                            m[0][0] = Number(e.target.value);
                            setMatrixVal(m);
                        }}
                    />
                    <input
                        className="border p-1 w-12"
                        type="number"
                        value={matrixVal[0][1]}
                        onChange={e => {
                            const m = [...matrixVal];
                            m[0][1] = Number(e.target.value);
                            setMatrixVal(m);
                        }}
                    />
                    <br />
                    <input
                        className="border p-1 w-12 ml-[3.5rem]"
                        type="number"
                        value={matrixVal[1][0]}
                        onChange={e => {
                            const m = [...matrixVal];
                            m[1][0] = Number(e.target.value);
                            setMatrixVal(m);
                        }}
                    />
                    <input
                        className="border p-1 w-12"
                        type="number"
                        value={matrixVal[1][1]}
                        onChange={e => {
                            const m = [...matrixVal];
                            m[1][1] = Number(e.target.value);
                            setMatrixVal(m);
                        }}
                    />
                </div>
            </div>

            <Mafs height={400} viewBox={{ x: [-6, 6], y: [-6, 6] }}>
                {/* Static Background Grid (Gray) */}
                <Coordinates.Cartesian subdivisions={2} opacity={0.2} />

                {/* Transformed Layer */}
                <Transform matrix={transformMatrix}>
                    {/* Dynamic Grid (follows transformation) */}
                    <Coordinates.Cartesian
                        subdivisions={2}
                        opacity={0.5}
                        xAxis={{ labels: (n) => (n % 2 === 0 ? n : "") }}
                        yAxis={{ labels: (n) => (n % 2 === 0 ? n : "") }}
                    />

                    {/* Unit Square to show area distortion */}
                    <Polygon
                        points={[
                            [0, 0],
                            [1, 0],
                            [1, 1],
                            [0, 1],
                        ]}
                        color="rgba(100, 200, 255, 0.5)"
                        strokeStyle="dashed"
                    />
                    <Text x={0.5} y={0.5} attach="center">Unit Square</Text>
                </Transform>

                {/* Control vectors (basis) - Rendered on top, in untransformed space for easier grabbing */}
                <Vector tail={[0, 0]} tip={[iHat.x, iHat.y]} color="blue" weight={4} />
                {iHat.element}
                <Text x={iHat.x} y={iHat.y} attach="ne" color="blue">i-hat</Text>

                <Vector tail={[0, 0]} tip={[jHat.x, jHat.y]} color="red" weight={4} />
                {jHat.element}
                <Text x={jHat.x} y={jHat.y} attach="ne" color="red">j-hat</Text>
            </Mafs>
        </div>
    );
};

export default MatrixTransform;
