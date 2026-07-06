import React, { useState } from "react";
import { analyzeVideo } from "./services/api";
import Dashboard from "./components/Dashboard";
import { Loader2 } from "lucide-react";

function App() {
  const [file, setFile] = useState(null);
  const [shotType, setShotType] = useState("smash");
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return alert("Please select a video file!");

    setIsProcessing(true);
    try {
      const data = await analyzeVideo(file, shotType, true);
      setResults(data);
      setVideoUrl(data.annotated_video_url);
    } catch (error) {
      alert("Error processing video. Make sure FastAPI is running!");
    } finally {
      setIsProcessing(false);
    }
  };

  if (results && videoUrl) {
    return (
      <Dashboard
        data={results}
        videoUrl={videoUrl}
        onReset={() => {
          setResults(null);
          setVideoUrl(null);
        }}
      />
    );
  }

  return (
    <div
      style={{
        maxWidth: "600px",
        margin: "100px auto",
        fontFamily: "sans-serif",
        textAlign: "center",
      }}
    >
      <style>
        {`
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                .spin-animation {
                    animation: spin 1s linear infinite;
                }
                `}
      </style>

      <h1>Badminton Form Analyzer</h1>
      <p>Upload a 45-degree angle video to analyze your form.</p>

      <form
        onSubmit={handleUpload}
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "20px",
          marginTop: "40px",
        }}
      >
        <input
          type="file"
          id="videoUpload"
          name="videoUpload"
          accept="video/mp4,video/quicktime"
          onChange={(e) => setFile(e.target.files[0])}
          style={{ padding: "10px", border: "1px dashed #ccc" }}
          disabled={isProcessing}
        />

        <select
          id="shotType"
          name="shotType"
          value={shotType}
          onChange={(e) => setShotType(e.target.value)}
          style={{ padding: "10px", fontSize: "16px" }}
          disabled={isProcessing}
        >
          <option value="smash">Smash</option>
          <option value="clear">Clear</option>
          <option value="drop">Drop</option>
        </select>

        <button
          type="submit"
          disabled={isProcessing}
          style={{
            padding: "15px",
            backgroundColor: isProcessing ? "#93c5fd" : "#2563eb",
            color: "white",
            border: "none",
            borderRadius: "5px",
            fontSize: "16px",
            cursor: isProcessing ? "not-allowed" : "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "10px",
          }}
        >
          {isProcessing ? (
            <>
              <Loader2 className="spin-animation" size={20} /> Analyzing...
            </>
          ) : (
            "Analyze Video"
          )}
        </button>
      </form>
    </div>
  );
}

export default App;
