# Badminton Form Analyzer

## Project Description

A computer vision tool for analyzing pre-recorded badminton strokes. The app tracks shoulder, elbow, and wrist landmarks frame by frame, computes elbow-angle kinematics and angular velocity, then returns coaching feedback with an annotated replay video.

## Features

- Pose tracking with MediaPipe for racket-arm landmarks
- Kinematic pipeline for angle smoothing and velocity estimation
- Shot diagnostics for smash, clear, and drop patterns
- Annotated output video with overlaid arm skeleton lines
- Interactive frontend dashboard with synced chart-to-video scrubbing
- Automatic cleanup of old generated videos in backend/outputs

## Setup

### 1. Start the backend

From the backend folder:

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the frontend

From the frontend folder:

```
npm install
npm run dev
```

The frontend calls the backend at http://localhost:8000.

## API

- POST /analyze
  - Form fields:
    - video: mp4 or mov upload
    - shot_type: smash | clear | drop
    - right_handed: true | false
  - Returns:
    - metrics and feedback
    - chart data for angles and velocities
    - annotated_video_url served from /outputs

## Backend Output Retention

Generated videos are saved in backend/outputs and removed automatically by a background cleanup task.

- OUTPUT_RETENTION_HOURS (default: 24)
  - Files older than this are deleted
  - Set to 0 or a negative value to disable deletion
- OUTPUT_CLEANUP_INTERVAL_SECONDS (default: 600)
  - Cleanup loop interval in seconds
  - Minimum effective interval is 60 seconds

Uploaded temp source videos in backend/temp_vids are removed after each analyze request.
