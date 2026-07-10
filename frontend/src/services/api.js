import axios from "axios";

const API_URL =
  "https://badminton-form-analyzer-production-7c70.up.railway.app";

export const analyzeVideo = async (videoFile, shotType, rightHanded) => {
  const formData = new FormData();
  formData.append("video", videoFile);
  formData.append("shot_type", shotType);
  formData.append("right_handed", rightHanded);

  try {
    const response = await axios.post(`${API_URL}/analyze`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  } catch (error) {
    console.error("Error analyzing video:", error);
    throw error;
  }
};
