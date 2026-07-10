import React, { useState } from "react";
import { analyzeVideo } from "./services/api";
import Dashboard from "./components/Dashboard";
import { Loader2, UploadCloud, Activity } from "lucide-react";

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
      if (data.status === "error") {
        alert("Python Error: " + data.message);
        setIsProcessing(false);
        return;
      }
      setResults(data);
      setVideoUrl(data.annotated_video_url);
    } catch (error) {
      console.error(error);
      alert("Network Error: Could not reach the FastAPI server!");
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
          setFile(null);
        }}
      />
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-8 text-center text-white">
          <Activity className="w-12 h-12 mx-auto mb-3" />
          <h1 className="text-3xl font-bold mb-2">Badminton Form Analyzer</h1>
          <p className="text-blue-100 text-sm">
            Upload a 45-degree angle video to analyze your form.
          </p>
        </div>

        <form onSubmit={handleUpload} className="p-8 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Video File
            </label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-blue-500 transition-colors bg-gray-50">
              <div className="space-y-1 text-center">
                <UploadCloud className="mx-auto h-12 w-12 text-gray-400" />
                <div className="flex text-sm text-gray-600 justify-center">
                  <label
                    htmlFor="file-upload"
                    className="relative cursor-pointer bg-transparent rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none"
                  >
                    <span>Upload a file</span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      accept="video/mp4,video/quicktime"
                      onChange={(e) => setFile(e.target.files[0])}
                      disabled={isProcessing}
                    />
                  </label>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {file ? file.name : "MP4 or MOV up to 50MB"}
                </p>
              </div>
            </div>
          </div>

          <div>
            <label
              htmlFor="shotType"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Shot Type
            </label>
            <select
              id="shotType"
              name="shotType"
              value={shotType}
              onChange={(e) => setShotType(e.target.value)}
              disabled={isProcessing}
              className="block w-full pl-3 pr-10 py-3 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md bg-gray-50 border"
            >
              <option value="smash">Smash</option>
              <option value="clear">Clear</option>
              <option value="drop">Drop</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={isProcessing}
            className={`w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white transition-all ${
              isProcessing
                ? "bg-blue-400 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 hover:shadow-lg"
            }`}
          >
            {isProcessing ? (
              <>
                <Loader2 className="animate-spin -ml-1 mr-2 h-5 w-5" />{" "}
                Analyzing...
              </>
            ) : (
              "Analyze Video"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
