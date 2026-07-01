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


vid = cv2.VideoCapture('vids/Untitled.mp4')
model_path = 'pose_landmarker_heavy.task'

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

UPPER_BODY_INDICES = {11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24}

LEFT_ARM = [(11, 13), (13, 15), (15, 17), (15, 19), (15, 21)]
RIGHT_ARM = [(12, 14), (14, 16), (16, 18), (16, 20), (16, 22)]
CHEST_TORSO = [(11, 12), (11, 23), (12, 24), (23, 24)]

if right_hand:
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

history = []
frame_idx = 0

with PoseLandmarker.create_from_options(options) as landmarker:
    while (vid.isOpened()):
        ret, frame = vid.read()
        if not ret:
            break

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        timestamp = int((frame_idx / fps) * 1000)

        result = landmarker.detect_for_video(mp_image, timestamp)

        coords = {}
        frame_world_data = {}

        if result.pose_landmarks and result.pose_world_landmarks:
            for pose_landmarks, world_landmarks in zip(result.pose_landmarks, result.pose_world_landmarks):
                for idx, landmark in enumerate(pose_landmarks):
                    if idx in ALLOWED_INDICES and landmark.visibility > 0.65:
                        coords[idx] = (int(landmark.x * w),
                                       int(landmark.y * h))

                for idx, w_landmark in enumerate(world_landmarks):
                    if idx in ALLOWED_INDICES and w_landmark.visibility > 0.65:
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

        history.append({
            "timestamp": timestamp,
            "world_coords": frame_world_data,
            "pixel_coords": coords
        })

        cv2.imshow('frame', frame)
        frame_idx += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyWindow('frame')

print("\nSignal Processing")

total_frames = len(history)
timeline = np.arange(total_frames)
smoothed_kinematics = {}

master_kinematic_matrix = np.full((total_frames, 33, 3), np.nan)

for f_idx, frame_data in enumerate(history):
    world_coords = frame_data["world_coords"]
    for joint_idx, coords in world_coords.items():
        master_kinematic_matrix[f_idx, joint_idx] = coords

fc = 7.0
nyq = fps / 2.0
if fc >= nyq:
    fc = nyq * 0.5
sos = butter(N=4, Wn=fc, btype='low', fs=fps, output='sos')

for joint_idx in ALLOWED_INDICES:
    joint_matrix = master_kinematic_matrix[:, joint_idx, :]

    valid_frame_indices = np.where(~np.isnan(joint_matrix[:, 0]))[0]

    if len(valid_frame_indices) == 0:
        smoothed_kinematics[joint_idx] = np.zeros((total_frames, 3))
        continue

    interpolation_kind = 'cubic' if len(valid_frame_indices) >= 4 else 'linear'

    interp_func = interp1d(
        valid_frame_indices,
        joint_matrix[valid_frame_indices],
        kind=interpolation_kind,
        axis=0,
        bounds_error=False,
        fill_value="extrapolate" if interpolation_kind == 'linear' else (
            joint_matrix[valid_frame_indices[0]],
            joint_matrix[valid_frame_indices[-1]]
        )
    )
    interpolated_matrix = interp_func(timeline)

    smoothed_matrix = sosfiltfilt(sos, interpolated_matrix, axis=0)
    smoothed_kinematics[joint_idx] = smoothed_matrix

print("Signal processing complete, matrix generated.")

print("\nCalculate angles and kinematics")

if right_hand:
    shld_idx, elbow_idx, wrist_idx = 12, 14, 16
else:
    shld_idx, elbow_idx, wrist_idx = 11, 13, 15

p_shoulder = smoothed_kinematics[shld_idx]
p_elbow = smoothed_kinematics[elbow_idx]
p_wrist = smoothed_kinematics[wrist_idx]

u = p_shoulder - p_elbow
v = p_wrist - p_elbow

dot_product = np.sum(u * v, axis=1)
norm_u = np.linalg.norm(u, axis=1)
norm_v = np.linalg.norm(v, axis=1)

with np.errstate(invalid='ignore', divide='ignore'):
    cos_theta = dot_product / (norm_u * norm_v)
    cos_theta = np.nan_to_num(cos_theta, nan=1.0)

cos_theta = np.clip(cos_theta, -1.0, 1.0)
elbow_angles = np.degrees(np.arccos(cos_theta))

dt = 1.0 / fps

elbow_vel = np.gradient(elbow_angles, dt)
elbow_acc = np.gradient(elbow_vel, dt)

for f_idx, frame_data in enumerate(history):
    frame_data["elbow_angle"] = elbow_angles[f_idx]
    frame_data["elbow_vel"] = elbow_vel[f_idx]
    frame_data["elbow_acc"] = elbow_acc[f_idx]

print("Angle, velocity, and acceleration found")

print("\nKinematics Trajectory:")
for idx in range(total_frames):
    t = history[idx]["timestamp"]
    ang = history[idx]["elbow_angle"]
    vel = history[idx]["elbow_vel"]
    acc = history[idx]["elbow_acc"]
    print(
        f"Frame {idx:04d} | Time: {t:5d}ms | Angle: {ang:6.2f}° | Vel: {vel:7.1f}°/s")
