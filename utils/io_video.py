import cv2
from core.pose_estimator import PoseEstimator
from utils.draw import draw_pose
import os
import subprocess

pose = PoseEstimator()

def process_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    base, ext = os.path.splitext(output_path)
    temp_output_path = f"{base}_temp{ext}"

    if not cap.isOpened():
        print("Error: Could not open input video")
        return False

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"Input video width: {width}")
    print(f"Input video height: {height}")
    print(f"Input video fps: {fps}")

    if width == 0 or height == 0:
        print("Error: Invalid video dimensions")
        cap.release()
        return False

    ## save the output video in 20.0 fps smooth and normal video
    if fps == 0:
        fps = 20.0
    out = cv2.VideoWriter(temp_output_path, fourcc, fps,
                          (width, height))
    if not out.isOpened():
        print("Error: Could not open VideoWriter")
        cap.release()
        return False

    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = pose.process(frame)
        frame = draw_pose(frame, results)

        out.write(frame)
        frame_count += 1

    cap.release()
    out.release()

    print(f"Finished writing {frame_count} frames")
    print(f"Output exists: {os.path.exists(output_path)}")

    # Convert to browser-friendly H.264 mp4
    command = [
        "ffmpeg",
        "-y",
        "-i", temp_output_path,
        "-vcodec", "libx264",
        "-acodec", "aac",
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Converted output saved at: {output_path}")
        print(f"Output file size: {os.path.getsize(output_path)} bytes")
    except subprocess.CalledProcessError as e:
        print("FFmpeg conversion failed:", e)
        return False
    
    return True

def run_webcam():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        results = pose.process(frame)
        frame = draw_pose(frame, results)

        cv2.imshow("Pose Insight", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break
    cap.release()
    cv2.destroyAllWindows()
