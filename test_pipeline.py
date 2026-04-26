import cv2
import mediapipe as mp
from core.feature_extractor import FeatureExtractor
from core.rep_segmenter import RepSegmenter
video_path = "data/good_squat/good_squat9.mp4"
# VIDEO = "data/good_squat/squat_20.mp4"

cap = cv2.VideoCapture(video_path)
extractor = FeatureExtractor()
segmenter = RepSegmenter(exercise="squat")
pose = mp.solutions.pose.Pose(static_image_mode=False)

rep_count = 0
frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame_count += 1
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)
    angles = extractor.process(results)

    if angles:
        # Print hip_y every frame so you can see the signal
        print(f"Frame {frame_count} | hip_y: {angles.get('hip_y'):.3f} | state: {segmenter.state} | peak: {segmenter.peak}")

        rep = segmenter.update(angles)
        if rep:
            rep_count += 1
            print(f"✅ Rep {rep_count} detected — {len(rep)} frames")

cap.release()
print(f"\nTotal frames: {frame_count}")
print(f"Total reps detected: {rep_count}")