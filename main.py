import numpy as np
import cv2
import mediapipe as mp
from scipy.interpolate import PchipInterpolator
from scipy.signal import savgol_filter

vid_path = 'vids/Untitled.mp4'
model_path = 'pose_landmarker_heavy.task'

vid = cv2.VideoCapture(vid_path)
fps = vid.get(cv2.CAP_PROP_FPS)
print(f"FPS: {fps}")

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO
)

right_hand = (input("Enter 'y' if right-handed: ").lower() ==
              "y") ^ (input("Enter 'y' if video is mirrored: ").lower() == "y")

if right_hand:
    shld_idx, elbow_idx, wrist_idx = 12, 14, 16
    ARM_COLOR = (0, 0, 255)
else:
    shld_idx, elbow_idx, wrist_idx = 11, 13, 15
    ARM_COLOR = (255, 255, 0)

TARGET_ARM_INDICES = [shld_idx, elbow_idx, wrist_idx]
VISIBILITY_THRESHOLD = 0.3

history = []
frame_idx = 0

print("2D Tracking")
with PoseLandmarker.create_from_options(options) as landmarker:
    while (vid.isOpened()):
        ret, frame = vid.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp = int((frame_idx / fps) * 1000)

        result = landmarker.detect_for_video(mp_image, timestamp)

        frame_data = {idx: np.array([np.nan, np.nan])
                      for idx in TARGET_ARM_INDICES}

        if result.pose_landmarks:
            lms_2d = result.pose_landmarks[0]
            h, w, _ = frame.shape

            for idx in TARGET_ARM_INDICES:
                lm = lms_2d[idx]
                if lm.visibility > VISIBILITY_THRESHOLD:
                    frame_data[idx] = np.array([lm.x * w, lm.y * h])

            pts = {}
            for idx in TARGET_ARM_INDICES:
                if not np.isnan(frame_data[idx][0]):
                    cx, cy = int(frame_data[idx][0]), int(frame_data[idx][1])
                    pts[idx] = (cx, cy)
                    cv2.circle(frame, (cx, cy), 5, ARM_COLOR, -1)

            if shld_idx in pts and elbow_idx in pts:
                cv2.line(frame, pts[shld_idx], pts[elbow_idx], ARM_COLOR, 3)
            if elbow_idx in pts and wrist_idx in pts:
                cv2.line(frame, pts[elbow_idx], pts[wrist_idx], ARM_COLOR, 3)

        history.append({
            "timestamp": timestamp,
            "coords": frame_data
        })

        cv2.imshow('frame', frame)
        frame_idx += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
vid.release()

print("\nSignal Processing")

total_frames = len(history)
timeline = np.arange(total_frames)

raw_shoulder = np.array([h["coords"][shld_idx] for h in history])
raw_elbow = np.array([h["coords"][elbow_idx] for h in history])
raw_wrist = np.array([h["coords"][wrist_idx] for h in history])


def interpolate_2d(joint_array):
    valid_idx = np.where(~np.isnan(joint_array[:, 0]))[0]
    if len(valid_idx) < 2:
        return np.zeros_like(joint_array)
    interp = PchipInterpolator(
        valid_idx, joint_array[valid_idx], axis=0, extrapolate=True)
    return interp(timeline)


p_shoulder = interpolate_2d(raw_shoulder)
p_elbow = interpolate_2d(raw_elbow)
p_wrist = interpolate_2d(raw_wrist)

u = p_shoulder - p_elbow
v = p_wrist - p_elbow

dot_product = np.sum(u * v, axis=1)
norm_u = np.linalg.norm(u, axis=1)
norm_v = np.linalg.norm(v, axis=1)

cos_theta = np.clip(dot_product / (norm_u * norm_v + 1e-6), -1.0, 1.0)
raw_elbow_angles = np.degrees(np.arccos(cos_theta))

window = 21
poly = 3
dt = 1.0 / fps

elbow_angles = savgol_filter(
    raw_elbow_angles, window_length=window, polyorder=poly)

elbow_vel = savgol_filter(
    raw_elbow_angles, window_length=window, polyorder=poly, deriv=1, delta=dt)

print("Angle, velocity, and acceleration found")
max_v = np.max(elbow_vel)
min_v = np.min(elbow_vel)

for idx in range(total_frames):
    t = history[idx]["timestamp"]
    ang = elbow_angles[idx]
    vel = elbow_vel[idx]

    if vel == max_v:
        flag = "   <<< MAX VELOCITY IMPACT >>>"
    elif vel == min_v:
        flag = "   <<< MAX PULLBACK SPEED >>>"
    else:
        flag = ""

    print(
        f"Frame {idx:04d} | Time: {t:5d}ms | Angle: {ang:6.2f}° | Vel: {vel:7.1f}°/s {flag}")
