import numpy as np
import cv2
import mediapipe as mp


def extract_2d_pose_data(video_path, right_handed=True):
    vid = cv2.VideoCapture(video_path)
    fps = vid.get(cv2.CAP_PROP_FPS) or 120.0

    mp_pose = mp.tasks.vision.PoseLandmarker
    options = mp.tasks.vision.PoseLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(
            model_asset_path='pose_landmarker_heavy.task'),
        running_mode=mp.tasks.vision.RunningMode.VIDEO
    )

    shld_idx, elbow_idx, wrist_idx = (
        12, 14, 16) if right_handed else (11, 13, 15)
    target_indices = [shld_idx, elbow_idx, wrist_idx]

    history = []
    frame_idx = 0

    with mp_pose.create_from_options(options) as landmarker:
        while vid.isOpened():
            ret, frame = vid.read()
            if not ret:
                break

            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            timestamp = int((frame_idx / fps) * 1000)

            result = landmarker.detect_for_video(mp_image, timestamp)
            frame_data = {idx: np.array([np.nan, np.nan])
                          for idx in target_indices}

            if result.pose_landmarks:
                for idx in target_indices:
                    lm = result.pose_landmarks[0][idx]
                    if lm.visibility > 0.3:
                        frame_data[idx] = np.array([lm.x * w, lm.y * h])

            history.append({"timestamp": timestamp, "coords": frame_data})
            frame_idx += 1

    vid.release()
    return history, fps, target_indices
