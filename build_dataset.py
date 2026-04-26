import cv2
import mediapipe as mp
import os
import numpy as np
import pandas as pd
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.feature_extractor import FeatureExtractor
from core.rep_segmenter import RepSegmenter
from utils.dataset_writer import rep_to_vector, FEATURES, N_FRAMES

DATA_DIR = "data"
LABELS = ["good_squat", "bad_squat", "good_pushup", "bad_pushup"]

SKIP_VIDEOS = []  # add filenames here if needed later

def process_video(video_path, exercise):
    cap = cv2.VideoCapture(video_path)
    extractor = FeatureExtractor()
    segmenter = RepSegmenter(exercise=exercise)
    pose = mp.solutions.pose.Pose(static_image_mode=False)
    reps = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)
        angles = extractor.process(results)
        if angles:
            rep = segmenter.update(angles)
            if rep:
                reps.append(rep)

    cap.release()
    pose.close()
    return reps

# ── Collect all reps ──────────────────────────────────────────────────────────
rows = []

for label in LABELS:
    exercise = "squat" if "squat" in label else "pushup"
    folder = os.path.join(DATA_DIR, label)

    if not os.path.exists(folder):
        print(f"⚠️  Folder not found: {folder}")
        continue

    for fname in os.listdir(folder):
        if fname in SKIP_VIDEOS:
            print(f"  ⏭️  Skipping {fname}")
            continue

        if not fname.endswith((".mp4", ".mov")):
            continue

        path = os.path.join(folder, fname)
        reps = process_video(path, exercise)
        print(f"  {fname}: {len(reps)} reps")

        for rep in reps:
            vector = rep_to_vector(rep)  # shape: (240,)
            row = {"label": label, "source": fname}
            for i, val in enumerate(vector):
                row[f"f{i}"] = val
            rows.append(row)

# ── Save CSV ──────────────────────────────────────────────────────────────────
df = pd.DataFrame(rows)
df.to_csv("data/dataset.csv", index=False)

print(f"\nTotal reps collected: {len(df)}")
print(f"CSV saved → data/dataset.csv")
print(f"Shape: {df.shape}")
print(f"\nLabel distribution:")
print(df["label"].value_counts())