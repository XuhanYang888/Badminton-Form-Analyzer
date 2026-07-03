import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function Dashboard({ data, onReset }) {
  const chartData = data.chart_data.angles.map((angle, index) => ({
    frame: index,
    angle: angle,
    velocity: data.chart_data.velocities[index],
  }));

  return (
    <div
      style={{
        padding: "20px",
        maxWidth: "1000px",
        margin: "0 auto",
        fontFamily: "sans-serif",
      }}
    >
      <button
        onClick={onReset}
        style={{ marginBottom: "20px", padding: "10px" }}
      >
        ← Analyze Another Video
      </button>

      <h1>{data.shot_type.toUpperCase()} Analysis Results</h1>

      <div style={{ display: "flex", gap: "20px", marginBottom: "30px" }}>
        <div
          style={{
            flex: 1,
            padding: "20px",
            backgroundColor: "#f0fdf4",
            borderRadius: "8px",
          }}
        >
          <h3>Scientific Metrics</h3>
          <p>
            <strong>Max Racket Drop Angle:</strong>{" "}
            {data.metrics.drop.toFixed(1)}°
          </p>
          <p>
            <strong>Contact Extension:</strong>{" "}
            {data.metrics.extension.toFixed(1)}°
          </p>
          <p>
            <strong>Peak Pronation Speed:</strong>{" "}
            {data.metrics.velocity.toFixed(1)}°/s
          </p>
        </div>
        <div
          style={{
            flex: 1,
            padding: "20px",
            backgroundColor: "#eff6ff",
            borderRadius: "8px",
          }}
        >
          <h3>Coaching Feedback</h3>
          <ul style={{ paddingLeft: "20px" }}>
            {data.coaching_feedback.map((tip, i) => (
              <li key={i} style={{ marginBottom: "10px" }}>
                {tip}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <h2>Kinematic Telemetry</h2>
      <div
        style={{
          height: "400px",
          width: "100%",
          backgroundColor: "#fff",
          padding: "20px",
          borderRadius: "8px",
          border: "1px solid #ccc",
        }}
      >
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="frame"
              label={{
                value: "Frames",
                position: "insideBottomRight",
                offset: 0,
              }}
            />
            <YAxis
              yAxisId="left"
              label={{ value: "Angle (°)", angle: -90, position: "insideLeft" }}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              label={{
                value: "Velocity (°/s)",
                angle: 90,
                position: "insideRight",
              }}
            />
            <Tooltip />
            <Legend verticalAlign="top" height={36} />

            <Line
              yAxisId="left"
              type="monotone"
              dataKey="angle"
              stroke="#2563eb"
              strokeWidth={2}
              name="Elbow Angle (°)"
              dot={false}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="velocity"
              stroke="#dc2626"
              strokeWidth={2}
              name="Angular Velocity (°/s)"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
