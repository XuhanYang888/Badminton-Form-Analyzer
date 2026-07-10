import os
import shutil
import asyncio
import time
from contextlib import suppress
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.staticfiles import StaticFiles
import uuid

from core.video_render import create_annotated_video
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
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

OUTPUT_RETENTION_HOURS = int(os.getenv("OUTPUT_RETENTION_HOURS", "24"))
OUTPUT_CLEANUP_INTERVAL_SECONDS = int(
    os.getenv("OUTPUT_CLEANUP_INTERVAL_SECONDS", "600")
)


def cleanup_old_output_files() -> int:
    if OUTPUT_RETENTION_HOURS <= 0:
        return 0

    now = time.time()
    retention_seconds = OUTPUT_RETENTION_HOURS * 3600
    deleted_count = 0

    for file_path in OUTPUT_DIR.iterdir():
        if not file_path.is_file():
            continue

        file_age_seconds = now - file_path.stat().st_mtime
        if file_age_seconds > retention_seconds:
            with suppress(FileNotFoundError):
                file_path.unlink()
                deleted_count += 1

    return deleted_count


async def output_cleanup_loop():
    while True:
        try:
            deleted_count = cleanup_old_output_files()
            if deleted_count > 0:
                print(f"Cleaned up {deleted_count} old output file(s).")
        except Exception as exc:
            print(f"Output cleanup error: {exc}")

        await asyncio.sleep(max(OUTPUT_CLEANUP_INTERVAL_SECONDS, 60))


@app.on_event("startup")
async def startup_event():
    app.state.output_cleanup_task = asyncio.create_task(output_cleanup_loop())


@app.on_event("shutdown")
async def shutdown_event():
    task = getattr(app.state, "output_cleanup_task", None)
    if task:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


@app.post("/analyze")
async def analyze_video(
    request: Request,
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

        print("4. Drawing AI Skeleton on Video...")
        output_filename = f"{uuid.uuid4()}.mp4"
        output_filepath = OUTPUT_DIR / output_filename
        create_annotated_video(str(file_location), str(
            output_filepath), kinematics, fps)

        os.remove(file_location)

        base_url = str(request.base_url)

        return {
            "status": "success",
            "fps": fps,
            "annotated_video_url": f"{base_url}outputs/{output_filename}",
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
