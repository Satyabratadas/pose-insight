import cv2
from core.pose_estimator import PoseEstimator
from core.feature_extractor import FeatureExtractor

import cv2
from core.pose_estimator import PoseEstimator
from core.feature_extractor import FeatureExtractor
from core.classifier import ExerciseClassifier
from utils.draw import draw_pose
import os
import subprocess


def process_video(input_path, output_path):
    pose = PoseEstimator()
    feature_extractor = FeatureExtractor()
    classifier = ExerciseClassifier()

    cap = cv2.VideoCapture(input_path)
    base, ext = os.path.splitext(output_path)
    temp_output_path = f"{base}_temp{ext}"

    if not cap.isOpened():
        print("Error: Could not open input video")
        return False

    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS)

    print(f"Input video width: {width}")
    print(f"Input video height: {height}")
    print(f"Input video fps: {fps}")

    if width == 0 or height == 0:
        print("Error: Invalid video dimensions")
        cap.release()
        return False

    if not fps or fps == 0:
        fps = 20.0

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_output_path, fourcc, fps, (width, height))

    if not out.isOpened():
        print("Error: Could not open VideoWriter")
        cap.release()
        return False

    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame, label = analyze_frame(frame, pose, feature_extractor, classifier)
        # print("label", label)

        out.write(frame)
        frame_count += 1

    cap.release()
    out.release()

    print(f"Finished writing {frame_count} frames")
    print(f"Temp output exists: {os.path.exists(temp_output_path)}")

    command = [
        "ffmpeg", "-y",
        "-i", temp_output_path,
        "-vcodec", "libx264",
        "-acodec", "aac",
        output_path,
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Converted output saved at: {output_path}")
        print(f"Output exists: {os.path.exists(output_path)}")
        if os.path.exists(output_path):
            print(f"Output file size: {os.path.getsize(output_path)} bytes")
    except subprocess.CalledProcessError as e:
        print("FFmpeg conversion failed:", e)
        return False

    if os.path.exists(temp_output_path):
        os.remove(temp_output_path)

    return True


def run_webcam(frame_placeholder, stop_flag):
    pose = PoseEstimator()
    feature_extractor = FeatureExtractor()
    classifier = ExerciseClassifier()

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame, label = analyze_frame(frame, pose, feature_extractor, classifier)
        # print("label", label)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels="RGB")

        if stop_flag():
            break

    cap.release()


def analyze_frame(frame, pose, feature_extractor, classifier):
    results  = pose.process(frame)
    features = feature_extractor.process(results)

    # classifier returns (label, rep_counts) — unpack both
    label, rep_counts = classifier.update(features)

    frame = draw_pose(frame, results)

    avg_knee  = 0.0
    avg_elbow = 0.0
    trunk     = 0.0

    if features is not None:
        avg_knee  = (features["left_knee"]  + features["right_knee"])  / 2
        avg_elbow = (features["left_elbow"] + features["right_elbow"]) / 2
        trunk     = features["trunk"]

    # ── winner-takes-all: show only the exercise with more reps ──
    squat_reps  = rep_counts["squat"]
    pushup_reps = rep_counts["push_up"]

    if squat_reps == 0 and pushup_reps == 0:
        display_exercise = label   # nothing counted yet, show live label
        display_reps     = 0
    elif squat_reps >= pushup_reps:
        display_exercise = "squat"
        display_reps     = squat_reps
    else:
        display_exercise = "push_up"
        display_reps     = pushup_reps

    # ── overlay ──────────────────────────────────────────────────
    cv2.putText(
        frame, f"Exercise: {display_exercise}",
        (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA,
    )
    cv2.putText(
        frame, f"Reps: {display_reps}",
        (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2, cv2.LINE_AA,
    )
    cv2.putText(
        frame, f"Knee: {avg_knee:.1f}",
        (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA,
    )
    cv2.putText(
        frame, f"Elbow: {avg_elbow:.1f}",
        (30, 155), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA,
    )
    cv2.putText(
        frame, f"Trunk: {trunk:.1f}",
        (30, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA,
    )

    return frame, label