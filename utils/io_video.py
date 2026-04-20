import cv2
from core.pose_estimator import PoseEstimator
from core.feature_extractor import FeatureExtractor
from core.classifier import ExerciseClassifier
from exercises.squat import SquatCounter
from exercises.pushup import PushUpCounter
from utils.draw import draw_pose
import os
import subprocess

pose = PoseEstimator()
feature_extractor = FeatureExtractor()
classifier = ExerciseClassifier()
squat_counter = SquatCounter()
pushup_counter = PushUpCounter()
squat_reps, squat_state = 0, "UP"
pushup_reps, pushup_state = 0, "UP"

def process_video(input_path, output_path):
    # cap = cv2.VideoCapture(input_path)
    # base, ext = os.path.splitext(output_path)
    # temp_output_path = f"{base}_temp{ext}"

    # if not cap.isOpened():
    #     print("Error: Could not open input video")
    #     return False

    # fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    # width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # fps = cap.get(cv2.CAP_PROP_FPS)

    # print(f"Input video width: {width}")
    # print(f"Input video height: {height}")
    # print(f"Input video fps: {fps}")

    # if width == 0 or height == 0:
    #     print("Error: Invalid video dimensions")
    #     cap.release()
    #     return False

    # ## save the output video in 20.0 fps smooth and normal video
    # if fps == 0:
    #     fps = 20.0
    # out = cv2.VideoWriter(temp_output_path, fourcc, fps,
    #                       (width, height))
    # if not out.isOpened():
    #     print("Error: Could not open VideoWriter")
    #     cap.release()
    #     return False

    # frame_count = 0

    # while cap.isOpened():
    #     ret, frame = cap.read()
    #     if not ret:
    #         break

    #     results = pose.process(frame)
    #     features = feature_extractor.process(results)  
    #     if features is not None:
    #         clean_features = {k: round(float(v), 2) for k, v in features.items()}
    #         label = classifier.update(clean_features)
    #         # print("features", clean_features)
    #         print("label", label)
    #     else:
    #         label = "unknown"

    #     if label == "squat":
    #         squat_reps, squat_state = squat_counter.update(features)
    #     elif label == "push_up":
    #         pushup_reps, pushup_state = pushup_counter.update(features)
                
    #     frame = draw_pose(frame, results)
        
    #     cv2.putText(frame, f"Exercise: {label}", (30, 50),
    #         cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
    #         cv2.LINE_AA)

    #     out.write(frame)
    #     frame_count += 1

    # cap.release()
    # out.release()

    # print(f"Finished writing {frame_count} frames")
    # print(f"Output exists: {os.path.exists(output_path)}")

    # # Convert to browser-friendly H.264 mp4
    # command = [
    #     "ffmpeg",
    #     "-y",
    #     "-i", temp_output_path,
    #     "-vcodec", "libx264",
    #     "-acodec", "aac",
    #     output_path
    # ]

    # try:
    #     subprocess.run(command, check=True)
    #     print(f"Converted output saved at: {output_path}")
    #     print(f"Output file size: {os.path.getsize(output_path)} bytes")
    # except subprocess.CalledProcessError as e:
    #     print("FFmpeg conversion failed:", e)
    #     return False
    
    # return True
    pose = PoseEstimator()
    feature_extractor = FeatureExtractor()
    classifier = ExerciseClassifier()
    squat_counter = SquatCounter()
    pushup_counter = PushUpCounter()

    cap = cv2.VideoCapture(input_path)
    base, ext = os.path.splitext(output_path)
    temp_output_path = f"{base}_temp{ext}"

    if not cap.isOpened():
        print("Error: Could not open input video")
        return False

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

        frame, label = analyze_frame(
            frame,
            pose,
            feature_extractor,
            classifier,
            squat_counter,
            pushup_counter,
        )

        print("label", label)

        out.write(frame)
        frame_count += 1

    cap.release()
    out.release()

    print(f"Finished writing {frame_count} frames")
    print(f"Temp output exists: {os.path.exists(temp_output_path)}")

    command = [
        "ffmpeg",
        "-y",
        "-i",
        temp_output_path,
        "-vcodec",
        "libx264",
        "-acodec",
        "aac",
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
    # cap = cv2.VideoCapture(0)

    # if not cap.isOpened():
    #     print("Error: Could not open webcam")
    #     return
    
    # while cap.isOpened():
    #     ret, frame = cap.read()
    #     if not ret:
    #         break
            
    #     results = pose.process(frame)
    #     features = feature_extractor.process(results)  
    #     if features is not None:
    #         clean_features = {k: round(float(v), 2) for k, v in features.items()}
    #         label = classifier.update(clean_features)
    #         # print("features", clean_features)
    #         print("label", label)
    #     else:
    #         label = "unknown"
        
    #     if label == "squat":
    #         squat_reps, squat_state = squat_counter.update(features)
    #     elif label == "push_up":
    #         pushup_reps, pushup_state = pushup_counter.update(features)

    #     frame = draw_pose(frame, results)

    #     # convert BGR to RGB for Streamlit
    #     frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #     frame_placeholder.image(frame_rgb, channels= "RGB")

    #     cv2.putText(frame, f"Exercise: {label}", (30, 50),
    #         cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
    #         cv2.LINE_AA)

    #     if stop_flag():
    #         break
    # cap.release()
    pose = PoseEstimator()
    feature_extractor = FeatureExtractor()
    classifier = ExerciseClassifier()
    squat_counter = SquatCounter()
    pushup_counter = PushUpCounter()

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam")
        return

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame, label = analyze_frame(
            frame,
            pose,
            feature_extractor,
            classifier,
            squat_counter,
            pushup_counter,
        )

        print("label", label)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels="RGB")

        if stop_flag():
            break

    cap.release()

def analyze_frame(frame, pose, feature_extractor, classifier, squat_counter, pushup_counter):
    """
    Process one frame:
    - pose estimation
    - feature extraction
    - classification
    - rep counting
    - drawing overlay
    """
    results = pose.process(frame)
    features = feature_extractor.process(results)

    if features is not None:
        label = classifier.update(features)
    else:
        label = "unknown"

    if label == "squat":
        squat_counter.update(features)
    elif label == "push_up":
        pushup_counter.update(features)

    frame = draw_pose(frame, results)

    avg_knee = 0.0
    avg_elbow = 0.0
    trunk = 0.0

    if features is not None:
        avg_knee = (features["left_knee"] + features["right_knee"]) / 2
        avg_elbow = (features["left_elbow"] + features["right_elbow"]) / 2
        trunk = features["trunk"]

    cv2.putText(
        frame,
        f"Exercise: {label}",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"Squat Reps: {squat_counter.reps}",
        (30, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 0),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"Push-up Reps: {pushup_counter.reps}",
        (30, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 0),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"Knee: {avg_knee:.1f}",
        (30, 160),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"Elbow: {avg_elbow:.1f}",
        (30, 195),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"Trunk: {trunk:.1f}",
        (30, 230),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    return frame, label
