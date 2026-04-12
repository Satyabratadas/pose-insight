import mediapipe as mp

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def draw_pose(frame, results):
    if results.pose_landmarks:

        # 🔴 Landmarks (points)
        landmark_style = mp_drawing.DrawingSpec(
            color=(0, 0, 255),   # GREEN (BGR)
            thickness=4,         # line thickness
            circle_radius=6      # 🔥 increase size here
        )

        # 🔵 Connections (lines)
        connection_style = mp_drawing.DrawingSpec(
            color=(0, 255, 255),   # BLUE
            thickness=3,
            circle_radius=2
        )

        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=landmark_style,
            connection_drawing_spec=connection_style
        )
    return frame