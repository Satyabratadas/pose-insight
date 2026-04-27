# 🏋️ PoseInsight: Intelligent Movement Analysis System

**PoseInsight** is an AI-powered movement analysis platform that evaluates exercise form using **computer vision, machine learning, deep learning, and generative AI feedback**.

The system bridges the gap between raw pose estimation and actionable coaching by transforming human movement into biomechanical insights, exercise classification, repetition counting, movement-quality prediction, injury-risk detection, and Gemini-powered personalized coaching.

PoseInsight supports:

- 🎥 Uploaded Video Analysis  
- 📷 Live Webcam Analysis  
- 🧠 ML / DL-based Quality Prediction  
- ⚠️ Injury Risk Detection  
- 💬 Gemini AI Coaching Feedback

## 🎥 Demo Video

Watch the full live demo here:  
[PoseInsight Live Demo on YouTube](https://youtu.be/U1MOYg6Z4TA?si=G4oPQe-vSMmITzt8)

[![Watch the demo](https://img.youtube.com/vi/U1MOYg6Z4TA/0.jpg)](https://youtu.be/U1MOYg6Z4TA?si=G4oPQe-vSMmITzt8)


---

# 🚀 Quick Start

## 1. Clone the repository
```bash
git clone <your_repo_url>
cd PoseInsight

```

## Install dependencies

```
pip install -r requirements.txt
```

## (Optional but recommended) Add Gemini API Key

```
export GEMINI_API_KEY="your_api_key_here"
```

## Launch the Streamlit app

```
streamlit run app.py
```


##  Project Structure
```
PoseInsight/
├── app.py                       # Main Streamlit UI
├── build_dataset.py             # Dataset creation pipeline
├── models_training.ipynb        # RF / MLP / LSTM training notebook
├── requirements.txt
│
├── core/
│   ├── pose_estimator.py        # MediaPipe pose engine
│   ├── feature_extractor.py     # Joint angles + biomechanical features
│   ├── classifier.py            # Rule-based exercise classification
│   ├── rep_segmenter.py         # Repetition counting
│   ├── quality_predictor.py     # RF / LSTM quality predictor
│   ├── risk_detection.py        # Injury risk analysis
│   └── feedback_generator.py    # Gemini coaching + risk summary
│
├── utils/
│   ├── draw.py                  # Pose skeleton overlay
│   ├── io_video.py              # Upload + webcam processing pipeline
│   └── dataset_writer.py        # Dataset export utilities
│
├── models/
│   ├── random_forest_quality.pkl
│   ├── mlp_quality.pt
│   ├── lstm_quality.pt
│   └── model_metadata.json
│
├── data/                        # Good / bad squat + push-up datasets
├── outputs/                     # Processed videos
├── plots_charts/                # Model comparisons + confusion matrices
└── project_docs/                # Architecture + reports

```

## System Pipeline

```
Video / Webcam Input
        ↓
MediaPipe Pose Estimation
        ↓
Biomechanical Feature Extraction
        ↓
Rule-Based Exercise Classification
        ↓
Rep Counting + Movement Segmentation
        ↓
RF / MLP / LSTM Quality Prediction
        ↓
Risk Detection
        ↓
Gemini AI Coaching Feedback
        ↓
Interactive Streamlit UI
```

## Core Features

### 🎯 Pose Estimation
- MediaPipe BlazePose for real-time landmark extraction
- 33 body landmarks
- Upload + webcam compatible

### 📐 Feature Extraction
- Knee angles
- Hip angles
- Elbow angles
- Trunk angle
- Symmetry metrics
- Motion progression

### 🏃 Exercise Classification

Rule-based baseline detects:
- Squat
- Push-up
- Idle / Unknown

### 🔁 Repetition Counting

Tracks:
- Squat reps
- Push-up reps

### 🧠 Quality Prediction

Trained and compared:
- Random Forest
- MLP
- LSTM

Predicted classes:
- Good Squat
- Bad Squat
- Good Push-up
- Bad Push-up
  
### ⚠️ Injury Risk Detection

Examples:
- Forward lean
- Knee asymmetry
- Shallow squat
- Core collapse
- Shoulder strain
  
### 💬 Gemini Coaching Feedback

Transforms model outputs into:
- Personalized coaching
- Form correction
- Safety recommendations

## Model Training Summary

### Models Evaluated:
- Random Forest
- MLP
- LSTM
  
### Current Deployment:

***Random Forest / LSTM hybrid depending stability and demo mode***

### Saved Assets:
- Dataset distribution
- RF / MLP / LSTM comparison
- Confusion matrices
- Training curves

## 🖥️ User Interface

### Upload Mode

✔ Upload exercise video
✔ Process full session
✔ Pose overlay
✔ Exercise + reps
✔ Quality prediction
✔ Gemini coaching
✔ Injury risk summary

### Live Mode

✔ Real-time webcam
✔ Fixed-duration movement session
✔ Post-session review
✔ Gemini summary

## 📈 Current Project Status
 - Full end-to-end pipeline
 - Dataset creation
 - RF / MLP / LSTM training
 - Uploaded video analysis
 - Live webcam analysis
 - Quality prediction
 - Risk detection
 - Gemini AI feedback
 - Streamlit deployment
 - Larger dataset expansion (Next step)
 - FastAPI backend (Next step)
 - Docker deployment (Next step)

## Responsible AI & Privacy
### Privacy
All processing is intended for local execution to reduce exposure of personal video data.

### Transparency
PoseInsight is an assistive educational system and should not replace:

- Medical diagnosis
- Physical therapy
- Professional coaching
  
### Fairness & Robustness
Future improvements include:

- Broader body-type robustness
- Lighting robustness
- More exercise classes
- Larger datasets

## Challenges
- Limited labeled dataset
- Frame-level pose noise
- Rule-based baseline limitations
- Small-data deep learning instability
- Webcam variability

## Future Work
- FastAPI backend
- Docker deployment
- Expanded dataset
- Multi-exercise support
- Better temporal transformers
- Mobile deployment
- Real-time corrective audio coaching

## Academic Context

Course: Applied Deep Learning
University: University of Florida
Instructor: Andrea Ramirez-Salgado

## Author

Satyabrata Das
M.S. Artificial Intelligence Systems
University of Florida
satyabradas@ufl.edu
