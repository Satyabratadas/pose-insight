# PoseInsight: Intelligent Movement Analysis System

**PoseInsight** is an AI-powered movement analysis system designed to evaluate exercise form. By bridging the gap between raw pose estimation and actionable coaching, the system extracts biomechanical features to predict movement quality and identify potential injury risks using a hybrid deep learning approach.

The system supports both uploaded video and real-time webcam input.

## Quick Start
To run the interactive prototype:

1. **Install dependencies**: ```pip install -r requirements.txt```
2. **Launch the interface**: ```streamlit run app.py```
3. **Analyze**: Upload a video from the ```data/``` folder (e.g., ```pushup1.mp4```) or use your webcam for real-time tracking.


##  Project Structure
The repository is organized to support a modular AI pipeline:

- ```app.py```: The main entry point for the Streamlit user interface.
- ```core/```: Core logic including ```pose_estimator.py``` (MediaPipe integration and landmark extraction).
- ```utils/```: Helper scripts for video I/O (```io_video.py```) and skeleton visualization (```draw.py```).
- ```data/```: Sample videos and datasets for testing and validation.
- ```project_docs/```: Technical reports, IEEE preliminary documents, and architecture diagrams.
- ```outputs/```: Processed videos with annotated pose overlays and metrics.


## Features & Technology
PoseInsight uses a multi-stage pipeline to transform raw pixels into coaching insights:

- **Pose Estimation:** Leverages **MediaPipe (BlazePose)** for real-time 3D body landmark extraction.
- **Feature Extraction**: Computes frame-level joint angles (knee, hip, elbow) and symmetry metrics.
- **Exercise Classification (Rule-Based)**: Uses a robust baseline logic to automatically detect the exercise type (e.g., Squat vs. Push-up) based on posture and angle thresholds.
- **Quality Analysis (LSTM)**: Employs a **Long Short-Term Memory (LSTM)** network to analyze the temporal sequence of the movement. This model classifies the quality of the specific exercise, distinguishing between "Good Form" and errors like "Forward Lean" or "Knee Misalignment."
- **Coaching Feedback**: Integrates the Gemini API to translate structured outputs into personalized, natural-language coaching tips.


## 📈 Current Status
The project has successfully moved from a design proposal to a functional end-to-end pipeline:

- [x] **Full Pipeline**: Video input $\rightarrow$ Pose estimation $\rightarrow$ Visualization.
- [x] **Feature Engine**: Automated calculation of biomechanical joint angles.
- [x] **Interface**: Working Streamlit UI with video upload and overlay capabilities.
- [x] **Hybrid Logic**: Rule-based exercise detection and preliminary quality scoring.
- [ ] **Next Step**: Training the LSTM on a larger labeled dataset for refined form analysis.


## ⚖️ Responsible AI & Privacy
We prioritize user privacy and system transparency:

- **Privacy**: All video processing is intended to remain local to minimize the storage of personally identifiable visual data.
- **Transparency**: The system is designed as an educational and assistive tool; it is not a replacement for professional medical advice or certified coaching.
- **Robustness**: Ongoing development focuses on ensuring the model performs consistently across different body types, clothing styles, and lighting conditions.

**Author**: Satyabrata Das

**Contact**: satyabradas@ufl.edu

**University**: University of Florida - Applied Deep Learning

**Instructor**: Andrea Ramirez-Salgado

