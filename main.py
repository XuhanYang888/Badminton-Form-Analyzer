import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from scipy.signal import butter, sosfiltfilt
from scipy.interpolate import interp1d


def draw_bones(frame, coords, connections, color, thickness=3):
    for start, end in connections:
        if start in coords and end in coords:
            cv2.line(frame, coords[start], coords[end],
                     color, thickness, cv2.LINE_AA)


cap = cv2.VideoCapture('vids/sample.mp4')
model_path = 'pose_landmarker.task'

fps = cap.get(cv2.CAP_PROP_FPS)
frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
print(f"FPS: {fps}")
print(f"Total Frames: {frame_count}")

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO
)

racket_hand = "R" if ((input("Enter 'y' if right-handed: ").lower() == "y")
                      ^ (input("Enter 'y' if video is mirrored: ").lower() == "y")) else "L"

UPPER_BODY_INDICES = {11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24}

LEFT_ARM = [(11, 13), (13, 15), (15, 17), (15, 19), (15, 21)]
RIGHT_ARM = [(12, 14), (14, 16), (16, 18), (16, 20), (16, 22)]
CHEST_TORSO = [(11, 12), (11, 23), (12, 24), (23, 24)]

if racket_hand == "R":
    TARGET_ARM_CONNECTIONS = RIGHT_ARM
    TARGET_ARM_INDICES = {14, 16, 18, 20, 22}
    ARM_COLOR = (0, 0, 255)
else:
    TARGET_ARM_CONNECTIONS = LEFT_ARM
    TARGET_ARM_INDICES = {13, 15, 17, 19, 21}
    ARM_COLOR = (255, 255, 0)

TORSO_INDICES = {11, 12, 23, 24}
C_TORSO = (255, 255, 255)
ALLOWED_INDICES = TORSO_INDICES.union(TARGET_ARM_INDICES)

kinematic_history = []
frame_idx = 0

with PoseLandmarker.create_from_options(options) as landmarker:
    while (cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        timestamp = int((frame_idx / fps) * 1000)

        result = landmarker.detect_for_video(mp_image, timestamp)

        frame_world_data = {}

        if result.pose_landmarks and result.pose_world_landmarks:
            for pose_landmarks, world_landmarks in zip(result.pose_landmarks, result.pose_world_landmarks):
                coords = {}

                for idx, landmark in enumerate(pose_landmarks):
                    if idx in ALLOWED_INDICES and landmark.visibility > 0.2:
                        coords[idx] = (int(landmark.x * w),
                                       int(landmark.y * h))

                for idx, w_landmark in enumerate(world_landmarks):
                    if idx in ALLOWED_INDICES and w_landmark.visibility > 0.2:
                        frame_world_data[idx] = (
                            w_landmark.x, w_landmark.y, w_landmark.z)

                draw_bones(frame, coords, CHEST_TORSO, C_TORSO, thickness=4)
                draw_bones(frame, coords, TARGET_ARM_CONNECTIONS,
                           ARM_COLOR, thickness=3)

                for idx, (cx, cy) in coords.items():
                    joint_color = ARM_COLOR if idx in TARGET_ARM_INDICES else C_TORSO
                    cv2.circle(frame, (cx, cy), 6, (0, 0, 0), -1, cv2.LINE_AA)
                    cv2.circle(frame, (cx, cy), 4,
                               joint_color, -1, cv2.LINE_AA)

        kinematic_history.append({
            "timestamp": timestamp,
            "world_coords": frame_world_data
        })

        cv2.imshow('frame', frame)
        frame_idx += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
