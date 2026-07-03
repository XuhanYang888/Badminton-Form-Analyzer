import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.signal import savgol_filter


def process_kinematics(history, fps, target_indices):
    shld_idx, elbow_idx, wrist_idx = target_indices
    total_frames = len(history)
    timeline = np.arange(total_frames)

    raw_s = np.array([h["coords"][shld_idx] for h in history])
    raw_e = np.array([h["coords"][elbow_idx] for h in history])
    raw_w = np.array([h["coords"][wrist_idx] for h in history])

    def interpolate_2d(arr):
        valid = np.where(~np.isnan(arr[:, 0]))[0]
        if len(valid) < 2:
            return np.zeros_like(arr)
        return PchipInterpolator(valid, arr[valid], axis=0, extrapolate=True)(timeline)

    p_s, p_e, p_w = interpolate_2d(raw_s), interpolate_2d(
        raw_e), interpolate_2d(raw_w)

    u = p_s - p_e
    v = p_w - p_e
    dot = np.sum(u * v, axis=1)
    norm_u, norm_v = np.linalg.norm(u, axis=1), np.linalg.norm(v, axis=1)

    cos_theta = np.clip(dot / (norm_u * norm_v + 1e-6), -1.0, 1.0)
    raw_angles = np.degrees(np.arccos(cos_theta))

    window = max(5, int(fps * 0.15) | 1)
    dt = 1.0 / fps

    smooth_angles = savgol_filter(
        raw_angles, window_length=window, polyorder=3)
    velocities = savgol_filter(
        raw_angles, window_length=window, polyorder=3, deriv=1, delta=dt)

    kinematics = {
        "angles": smooth_angles,
        "velocities": velocities,
        "points": {"s": p_s, "e": p_e, "w": p_w}
    }
    return kinematics
