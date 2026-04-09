import cv2
from core.pose_estimator import PoseEstimator
from utils.draw import draw_pose
import os

pose = PoseEstimator()

def process_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    ## save the output video in 20.0 fps smooth and normal video
    if fps == 0:
        fps = 20.0
    out = cv2.VideoWriter(output_path, fourcc, fps,
                          (width, height))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = pose.process(frame)
        frame = draw_pose(frame, results)

        out.write(frame)
    cap.release()
    out.release()

def run_webcam():
    cap = cv2.VideoCapture(0)

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
