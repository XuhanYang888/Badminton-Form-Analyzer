import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

cap = cv2.VideoCapture('vids/test1.mp4')
model_path = 'pose_landmarker.task'

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO
)

racket_hand = "R" if (
    input("Enter 'y' if right-handed: ").lower() == "y") else "L"

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


with PoseLandmarker.create_from_options(options) as landmarker:
    while (cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        result = landmarker.detect_for_video(mp_image, timestamp)

        if result.pose_landmarks:
            for pose_landmarks in result.pose_landmarks:
                coords = {}
                for idx, landmark in enumerate(pose_landmarks):
                    if idx in ALLOWED_INDICES and landmark.visibility > 0.2:
                        coords[idx] = (int(landmark.x * w),
                                       int(landmark.y * h))

                def draw_bones(connections, color, thickness=3):
                    for start, end in connections:
                        if start in coords and end in coords:
                            cv2.line(
                                frame, coords[start], coords[end], color, thickness, cv2.LINE_AA)

                draw_bones(CHEST_TORSO, C_TORSO, thickness=4)
                draw_bones(TARGET_ARM_CONNECTIONS, ARM_COLOR, thickness=3)

                for idx, (cx, cy) in coords.items():
                    if idx in TARGET_ARM_INDICES:
                        joint_color = ARM_COLOR
                    else:
                        joint_color = C_TORSO

                    cv2.circle(frame, (cx, cy), 6, (0, 0, 0), -1, cv2.LINE_AA)
                    cv2.circle(frame, (cx, cy), 4,
                               joint_color, -1, cv2.LINE_AA)

        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
