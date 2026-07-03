import numpy as np


def analyze_shot(kinematics, fps, shot_type="smash"):
    angles = kinematics["angles"]
    vels = kinematics["velocities"]

    impact_idx = int(np.argmax(vels))
    max_vel = vels[impact_idx]

    search_start = max(0, impact_idx - int(fps * 0.4))
    drop_idx = search_start + int(np.argmin(angles[search_start:impact_idx]))
    min_angle = angles[drop_idx]

    search_end = min(len(angles), impact_idx + int(fps * 0.3))
    ext_idx = impact_idx + int(np.argmax(angles[impact_idx:search_end]))
    max_angle = angles[ext_idx]

    feedback = []

    if min_angle > 60:
        feedback.append(
            "1. Racket Drop: Too shallow. Bend your elbow more behind your back to utilize the stretch-shortening cycle.")
    else:
        feedback.append(
            f"1. Racket Drop: Excellent ({min_angle:.1f}°). Deep wind-up for maximum whip.")

    if max_angle < 150:
        feedback.append(
            f"2. Extension: You hit with a bent arm ({max_angle:.1f}°). Reach up higher to hit the shuttle at your highest point.")
    else:
        feedback.append(
            f"2. Extension: Great reach ({max_angle:.1f}°). You are making contact at the peak of your swing.")

    if shot_type == "smash" or shot_type == "clear":
        if max_vel < 900:
            feedback.append(
                f"3. Pronation Speed: A bit slow ({max_vel:.1f}°/s). Focus on relaxing your grip and snapping right at contact.")
        else:
            feedback.append(
                f"3. Pronation Speed: Explosive snap ({max_vel:.1f}°/s) generating massive power.")

    elif shot_type == "drop":
        if max_vel > 1000:
            feedback.append(
                f"3. Deceleration: Too fast ({max_vel:.1f}°/s) for a drop. You are hitting it like a smash. Use 'soft hands' to decelerate before contact.")
        else:
            feedback.append(
                f"3. Deceleration: Good control ({max_vel:.1f}°/s). You masked the shot well without over-hitting.")

    return {
        "impact_frame": impact_idx,
        "metrics": {"drop": min_angle, "extension": max_angle, "velocity": max_vel},
        "feedback": feedback,
        "clip_bounds": (search_start, search_end)
    }
