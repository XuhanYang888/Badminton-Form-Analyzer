import React, { useRef, useEffect } from "react";
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

export default function Dashboard({ data, videoUrl, onReset }) {
  const videoRef = useRef(null);
  const fps = data.fps || 120;
  const chartData = data.chart_data.angles.map((angle, index) => ({
    frame: index,
    angle: angle,
    velocity: data.chart_data.velocities[index],
  }));

  const SyncingTooltip = ({ active, payload, label }) => {
    useEffect(() => {
      if (active && payload && payload.length > 0 && videoRef.current) {
        const frameIndex = payload[0].payload.frame;
        const timeInSeconds = frameIndex / fps;

        if (videoRef.current.readyState >= 1) {
          if (!videoRef.current.paused) {
            videoRef.current.pause();
          }
          videoRef.current.currentTime = timeInSeconds;
        }
      }
    }, [active, payload]);

    if (active && payload && payload.length > 0) {
      return (
        <div
          style={{
            backgroundColor: "white",
            padding: "10px",
            border: "1px solid #ccc",
            borderRadius: "5px",
            boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
          }}
        >
          <p style={{ margin: "0 0 5px 0" }}>
            <strong>Frame: {payload[0].payload.frame}</strong>
          </p>
          <p style={{ margin: "0", color: "#2563eb" }}>
            Angle: {payload[0].payload.angle?.toFixed(1)}°
          </p>
          <p style={{ margin: "0", color: "#dc2626" }}>
            Velocity: {payload[0].payload.velocity?.toFixed(1)}°/s
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div
      style={{
        padding: "20px",
        maxWidth: "1200px",
        margin: "0 auto",
        fontFamily: "sans-serif",
      }}
    >
      <button
        onClick={onReset}
        style={{ marginBottom: "20px", padding: "10px", cursor: "pointer" }}
      >
        ← Analyze Another Video
      </button>

      <h1>{data.shot_type.toUpperCase()} Analysis Results</h1>

      <div
        style={{
          display: "flex",
          gap: "20px",
          marginBottom: "30px",
          flexWrap: "wrap",
        }}
      >
        <div
          style={{
            flex: "1 1 500px",
            backgroundColor: "#000",
            borderRadius: "8px",
            overflow: "hidden",
          }}
        >
          <video
            ref={videoRef}
            src={videoUrl}
            controls
            muted
            style={{
              width: "100%",
              height: "100%",
              objectFit: "contain",
              display: "block",
            }}
          />
        </div>
        <div
          style={{
            flex: "1 1 400px",
            display: "flex",
            flexDirection: "column",
            gap: "20px",
          }}
        >
          <div
            style={{
              padding: "20px",
              backgroundColor: "#f0fdf4",
              borderRadius: "8px",
              border: "1px solid #bbf7d0",
            }}
          >
            <h3 style={{ marginTop: 0 }}>Scientific Metrics</h3>
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
              padding: "20px",
              backgroundColor: "#eff6ff",
              borderRadius: "8px",
              border: "1px solid #bfdbfe",
            }}
          >
            <h3 style={{ marginTop: 0 }}>Coaching Feedback</h3>
            <ul style={{ paddingLeft: "20px", margin: 0 }}>
              {data.coaching_feedback.map((tip, i) => (
                <li key={i} style={{ marginBottom: "10px" }}>
                  {tip}
                </li>
              ))}
            </ul>
          </div>
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
          boxSizing: "border-box",
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

            <Tooltip content={<SyncingTooltip />} />
            <Legend verticalAlign="top" height={36} />

            <Line
              yAxisId="left"
              type="monotone"
              dataKey="angle"
              stroke="#2563eb"
              strokeWidth={2}
              name="Elbow Angle (°)"
              dot={false}
              activeDot={{ r: 6 }}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="velocity"
              stroke="#dc2626"
              strokeWidth={2}
              name="Angular Velocity (°/s)"
              dot={false}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
