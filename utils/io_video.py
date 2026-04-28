import os
import subprocess
from collections import Counter
from core.risk_detection import detect_risks
import cv2
import time
from core.pose_estimator import PoseEstimator
from core.feature_extractor import FeatureExtractor
from core.classifier import ExerciseClassifier
from core.quality_predictor import QualityPredictor
from utils.draw import draw_pose


def create_empty_session():
    return {
        "qualities": [],
        "scores": [],
        "feedback_set": set(),
        "risks": set(),
        "exercise": "unknown",
        "total_reps": 0,
        "avg_knees": [],
        "avg_elbows": [],
        "avg_trunks": [],
        "knee_angle": 0.0,
        "elbow_angle": 0.0,
        "trunk_angle": 0.0,
        "avg_score": 100,
        "quality_label": "Unknown",
        "feedback": [],
    }


def process_video(input_path, output_path):
    pose = PoseEstimator()
    feature_extractor = FeatureExtractor()
    classifier = ExerciseClassifier()
    quality_predictor = QualityPredictor()

    session = create_empty_session()

    cap = cv2.VideoCapture(input_path)

    base, _ = os.path.splitext(output_path)
    temp_output_path = f"{base}_temp.mp4"

    if not cap.isOpened():
        print("Error: Could not open input video")
        return False, session

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if width == 0 or height == 0:
        print("Error: Invalid video dimensions")
        cap.release()
        return False, session

    if not fps or fps == 0:
        fps = 20.0

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_output_path, fourcc, fps, (width, height))

    if not out.isOpened():
        print("Error: Could not open VideoWriter")
        cap.release()
        return False, session

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame, _ = analyze_frame(
            frame=frame,
            pose=pose,
            feature_extractor=feature_extractor,
            classifier=classifier,
            quality_predictor=quality_predictor,
            session=session,
        )

        out.write(frame)

    cap.release()
    out.release()

    command = [
        "ffmpeg",
        "-y",
        "-i",
        temp_output_path,
        "-vcodec",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-acodec",
        "aac",
        output_path,
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print("FFmpeg conversion failed:", e)
        return False, session

    if os.path.exists(temp_output_path):
        os.remove(temp_output_path)

    finalize_session(session)

    return True, session

def run_webcam(frame_placeholder, duration_seconds=10):
    pose = PoseEstimator()
    feature_extractor = FeatureExtractor()
    classifier = ExerciseClassifier()
    quality_predictor = QualityPredictor()

    session = create_empty_session()

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam")
        return None

    start_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame, _ = analyze_frame(
            frame,
            pose,
            feature_extractor,
            classifier,
            quality_predictor,
            session=session,
        )

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels="RGB", width=640)

        # Stop automatically after selected duration
        elapsed_time = time.time() - start_time
        if elapsed_time >= duration_seconds:
            break

    cap.release()

    finalize_session(session)

    return session


def analyze_frame(frame, pose, feature_extractor,
    classifier, quality_predictor, session=None):
    results = pose.process(frame)
    features = feature_extractor.process(results)

    label, rep_counts, last_score = classifier.update(features)
    quality = quality_predictor.update(features)
    risk_flags = detect_risks(features, quality)

    frame = draw_pose(frame, results)

    avg_knee = 0.0
    avg_elbow = 0.0
    trunk = 0.0

    if features is not None:
        avg_knee = (
            (features.get("left_knee") or 0.0) +
            (features.get("right_knee") or 0.0)
        ) / 2

        avg_elbow = (
            (features.get("left_elbow") or 0.0) +
            (features.get("right_elbow") or 0.0)
        ) / 2

        trunk = features.get("trunk") or 0.0

    if quality and "Squat" in quality:
        display_exercise = "squat"
        display_reps = rep_counts.get("squat", 0)

    elif quality and "Push-up" in quality:
        display_exercise = "push_up"
        display_reps = rep_counts.get("push_up", 0)

    else:
        display_exercise = label or "idle"
        display_reps = 0

    if session is not None:
        session["exercise"] = display_exercise
        session["total_reps"] = display_reps
        session["last_display_reps"] = display_reps

        session["squat_reps"] = rep_counts.get("squat", 0)
        session["pushup_reps"] = rep_counts.get("push_up", 0)

        if features is not None:
            session["avg_knees"].append(avg_knee)
            session["avg_elbows"].append(avg_elbow)
            session["avg_trunks"].append(trunk)

        if quality not in ["Collecting...", "Analyzing...", None]:
            session["qualities"].append(quality)

        score = last_score.get("score", 100)
        session["scores"].append(score)

        for feedback in last_score.get("feedback", []):
            session["feedback_set"].add(feedback)

        for risk in last_score.get("risks", []):
            session["risks"].add(risk)

        for risk in risk_flags:
            session["risks"].add(risk)

    cv2.putText(
        frame,
        f"Exercise: {display_exercise}",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"Reps: {display_reps}",
        (30, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 0),
        2,
        cv2.LINE_AA,
    )

    return frame, label


def finalize_session(session):
    def avg(values):
        return round(sum(values) / len(values), 1) if values else 0.0

    session["knee_angle"] = avg(session["avg_knees"])
    session["elbow_angle"] = avg(session["avg_elbows"])
    session["trunk_angle"] = avg(session["avg_trunks"])

    # Final quality from LSTM majority vote
    if session["qualities"]:
        session["quality_label"] = Counter(session["qualities"]).most_common(1)[0][0]
    else:
        session["quality_label"] = "Unknown"

    quality_label = session["quality_label"]

    # Final exercise from LSTM quality label
    if "Squat" in quality_label:
        session["exercise"] = "squat"
    elif "Push-up" in quality_label:
        session["exercise"] = "push_up"
    else:
        session["exercise"] = "unknown"

    # Final reps should be the highest rep count seen in the video
    # session["total_reps"] = session.get("max_reps", 0)
    session["total_reps"] = session.get("last_display_reps", 0)

    session["feedback"] = list(session["feedback_set"])
    session["risks"] = list(session["risks"])