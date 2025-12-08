import React, { useState } from "react";
import { Mafs, Coordinates, Vector, MovablePoint, Text, useMovablePoint } from "mafs";

const VectorAddition = () => {
    const u = useMovablePoint([2, 1], { color: "blue" });
    const v = useMovablePoint([1, 2], { color: "red" });
    console.log("VectorAddition u:", u, "v:", v);

    const sum = [u.x + v.x, u.y + v.y];

    return (
        <div className="p-4 bg-white rounded-xl shadow-md">
            <p className="mb-4 text-gray-600">
                拖动蓝色和红色向量的终点，观察绿色向量（和）的变化。
                <br />
                {(() => {
                    const ux = u.x.toFixed(1);
                    const uy = u.y.toFixed(1);
                    const vx = v.x.toFixed(1);
                    const vy = v.y.toFixed(1);
                    const sx = sum[0].toFixed(1);
                    const sy = sum[1].toFixed(1);
                    return `$\\vec{u} + \\vec{v} = (${ux}, ${uy}) + (${vx}, ${vy}) = (${sx}, ${sy})$`;
                })()}
            </p>
            <Mafs height={400} viewBox={{ x: [-1, 8], y: [-1, 8] }}>
                <Coordinates.Cartesian />

                {/* Vector u */}
                <Vector tail={[0, 0]} tip={[u.x, u.y]} color="blue" />
                <Text x={u.x / 2} y={u.y / 2} attach="sl">u</Text>
                {u.element}

                {/* Vector v (placed at origin for standard view) */}
                <Vector tail={[0, 0]} tip={[v.x, v.y]} color="red" />
                <Text x={v.x / 2} y={v.y / 2} attach="se">v</Text>
                {v.element}

                {/* Vector v (placed at tip of u for parallelogram/triangle) */}
                <Vector tail={[u.x, u.y]} tip={sum} color="red" opacity={0.5} style="dashed" />

                {/* Vector u (placed at tip of v) */}
                <Vector tail={[v.x, v.y]} tip={sum} color="blue" opacity={0.5} style="dashed" />

                {/* Result Vector */}
                <Vector tail={[0, 0]} tip={sum} color="green" weight={3} />
                <Text x={sum[0]} y={sum[1]} attach="ne" color="green">u + v</Text>
            </Mafs>
        </div>
    );
};

export default VectorAddition;
