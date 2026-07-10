import cv2
import numpy as np
import subprocess
import os


def create_annotated_video(input_video_path, output_video_path, kinematics, fps):
    cap = cv2.VideoCapture(input_video_path)
    ret, test_frame = cap.read()
    if not ret:
        cap.release()
        return
    true_height, true_width = test_frame.shape[:2]
    cap.release()
    cap = cv2.VideoCapture(input_video_path)

    temp_path = output_video_path.replace(".mp4", "_temp.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_path, fourcc, fps,
                          (int(true_width), int(true_height)))

    s_points = kinematics["points"]["s"]
    e_points = kinematics["points"]["e"]
    w_points = kinematics["points"]["w"]

    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx < len(s_points):
            s = s_points[frame_idx]
            e = e_points[frame_idx]
            w = w_points[frame_idx]

            if not np.isnan(s[0]) and not np.isnan(e[0]) and not np.isnan(w[0]):
                p1 = (int(s[0]), int(s[1]))
                p2 = (int(e[0]), int(e[1]))
                p3 = (int(w[0]), int(w[1]))

                cv2.line(frame, p1, p2, (0, 255, 0), 4)
                cv2.line(frame, p2, p3, (0, 255, 255), 4)
                cv2.circle(frame, p1, 6, (0, 0, 255), -1)
                cv2.circle(frame, p2, 6, (0, 0, 255), -1)
                cv2.circle(frame, p3, 6, (0, 0, 255), -1)

        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()

    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", temp_path,
        "-vcodec", "libx264",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        output_video_path
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr)

    if os.path.exists(temp_path):
        os.remove(temp_path)
