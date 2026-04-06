# PoseInsight: Intelligent Movement Analysis System

PoseInsight is an AI-powered system for analyzing human movement, specifically squat form. It uses computer vision, feature extraction, and deep learning to evaluate movement quality and provide actionable feedback.

The system supports both uploaded video and real-time webcam input.

## Features

- Pose estimation using MediaPipe
- Joint angle and movement feature extraction
- Deep learning-based movement classification (MLP/LSTM - planned)
- Rule-based baseline comparison
- LLM-generated coaching feedback (Gemini API)
- Real-time and offline video analysis

## Project Structure

data/        # Sample or collected data  
notebooks/   # Jupyter notebooks  
src/         # Core pipeline and model code  
ui/          # Streamlit interface  
results/     # Outputs and visualizations  
docs/        # Diagrams and report assets  

## Installation

```
pip install -r requirements.txt

```
## Run

Open the notebook:

```
jupyter notebook notebooks/setup.ipynb
```

## Dataset

- Self-collected squat videos
- Features extracted using MediaPipe
- Labels: good form, forward lean, knee misalignment, asymmetry (planned)

