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
import { ArrowLeft, Zap, Target, ArrowDownCircle } from "lucide-react";

export default function Dashboard({ data, videoUrl, onReset }) {
  const videoRef = useRef(null);
  const fps = data.fps || 120;
  const chartData = data.chart_data.angles.map((angle, index) => ({
    frame: index,
    angle: angle,
    velocity: data.chart_data.velocities[index],
  }));

  const SyncingTooltip = ({ active, payload }) => {
    useEffect(() => {
      if (active && payload && payload.length > 0 && videoRef.current) {
        const frameIndex = payload[0].payload.frame;
        const timeInSeconds = frameIndex / fps;

        if (videoRef.current.readyState >= 1) {
          if (!videoRef.current.paused) videoRef.current.pause();
          videoRef.current.currentTime = timeInSeconds;
        }
      }
    }, [active, payload]);

    if (active && payload && payload.length > 0) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-xl border border-gray-100 text-sm">
          <p className="font-bold text-gray-800 border-b pb-1 mb-2">
            Frame {payload[0].payload.frame}
          </p>
          <p className="text-blue-600 font-medium">
            Angle: {payload[0].payload.angle?.toFixed(1)}°
          </p>
          <p className="text-red-600 font-medium">
            Velocity: {payload[0].payload.velocity?.toFixed(1)}°/s
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 font-sans">
      <div className="flex items-center justify-between mb-8">
        <button
          onClick={onReset}
          className="flex items-center text-sm font-medium text-gray-500 hover:text-blue-600 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-2" /> Analyze Another Video
        </button>
        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 capitalize">
          {data.shot_type} Analysis
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div className="bg-black rounded-xl overflow-hidden shadow-lg border border-gray-800 flex items-center justify-center min-h-[400px]">
          <video
            ref={videoRef}
            src={videoUrl}
            controls
            muted
            className="w-full h-full max-h-[600px] object-contain"
          />
        </div>

        <div className="flex flex-col gap-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 flex flex-col items-center text-center">
              <ArrowDownCircle className="w-8 h-8 text-indigo-500 mb-2" />
              <p className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-1">
                Racket Drop
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {data.metrics.drop.toFixed(1)}°
              </p>
            </div>
            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 flex flex-col items-center text-center">
              <Target className="w-8 h-8 text-blue-500 mb-2" />
              <p className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-1">
                Extension
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {data.metrics.extension.toFixed(1)}°
              </p>
            </div>
            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 flex flex-col items-center text-center">
              <Zap className="w-8 h-8 text-red-500 mb-2" />
              <p className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-1">
                Speed
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {data.metrics.velocity.toFixed(0)}°/s
              </p>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex-1">
            <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-bold text-gray-800">
                AI Coaching Feedback
              </h3>
            </div>
            <ul className="p-6 space-y-4">
              {data.coaching_feedback.map((tip, i) => (
                <li key={i} className="flex text-gray-700">
                  <span>{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h2 className="text-lg font-bold text-gray-800 mb-6">
          Kinematic History{" "}
          <span className="text-sm font-normal text-gray-500 ml-2">
            (Hover to scrub video)
          </span>
        </h2>
        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={chartData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke="#e5e7eb"
              />
              <XAxis
                dataKey="frame"
                tick={{ fill: "#6b7280" }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                yAxisId="left"
                tick={{ fill: "#2563eb" }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                tick={{ fill: "#dc2626" }}
                tickLine={false}
                axisLine={false}
              />

              <Tooltip content={<SyncingTooltip />} />
              <Legend wrapperStyle={{ paddingTop: "20px" }} />

              <Line
                yAxisId="left"
                type="monotone"
                dataKey="angle"
                stroke="#2563eb"
                strokeWidth={3}
                name="Elbow Angle (°)"
                dot={false}
                activeDot={{ r: 8, strokeWidth: 0 }}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="velocity"
                stroke="#dc2626"
                strokeWidth={3}
                name="Angular Velocity (°/s)"
                dot={false}
                activeDot={{ r: 8, strokeWidth: 0 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
