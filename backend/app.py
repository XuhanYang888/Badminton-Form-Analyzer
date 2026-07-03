import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from core.tracking import extract_2d_pose_data
from core.kinematics import process_kinematics
from core.diagnostics import analyze_shot

app = FastAPI(title="Badminton Kinematic API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMP_DIR = Path("temp_vids")
TEMP_DIR.mkdir(exist_ok=True)


@app.post("/analyze")
async def analyze_video(
    video: UploadFile = File(...),
    shot_type: str = Form("smash"),
    right_handed: bool = Form(True)
):
    file_location = TEMP_DIR / video.filename

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    try:
        print(f"1. Extracting AI Tracking Data for {video.filename}...")
        history, fps, indices = extract_2d_pose_data(
            str(file_location), right_handed)

        print("2. Processing Kinematic Math...")
        kinematics = process_kinematics(history, fps, indices)

        print(f"3. Running Diagnostics for: {shot_type.upper()}...")
        analysis = analyze_shot(kinematics, fps, shot_type)

        os.remove(file_location)

        return {
            "status": "success",
            "shot_type": shot_type,
            "critical_clip": {
                "start_frame": analysis["clip_bounds"][0],
                "impact_frame": analysis["impact_frame"],
                "end_frame": analysis["clip_bounds"][1]
            },
            "metrics": analysis["metrics"],
            "coaching_feedback": analysis["feedback"],
            "chart_data": {
                "angles": kinematics["angles"].tolist(),
                "velocities": kinematics["velocities"].tolist()
            }
        }

    except Exception as e:
        if file_location.exists():
            os.remove(file_location)
        return {"status": "error", "message": str(e)}


@app.get("/")
def read_root():
    return {"message": "Badminton Kinematics API is running."}
