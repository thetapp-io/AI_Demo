AI Skin Analysis and Recommendation App

Overview

This application uses AI-powered image analysis to provide personalized skin assessments and recommendations. It utilizes Google Generative AI (Gemini 1.5 Pro) for content generation and MediaPipe for face detection. Users can capture an image using their webcam, and the AI will analyze their skin condition and provide recommendations.

Features

Face Detection: Ensures the user's face is properly aligned within the image.

Lighting Validation: Checks for proper lighting conditions before analysis.

Skin Analysis: Uses Google's Generative AI to analyze skin conditions and provide recommendations.

Gradio UI: Provides a simple and interactive user interface.

Technologies Used

Python

Gradio

Google Generative AI (Gemini 1.5 Pro)

OpenCV

MediaPipe

NumPy

PIL (Pillow)

dotenv

Installation

Prerequisites

Ensure you have Python installed (Python 3.7+ recommended).

Steps

Clone the repository:

git clone https://github.com/your-repository/ai-skin-analysis.git
cd ai-skin-analysis

Create a virtual environment (optional but recommended):

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Set up environment variables:

Create a .env file in the root directory.

Add your Google API key:

GOOGLE_API_KEY=your_google_api_key_here

Run the application:

python app.py

Usage

Open the Gradio interface in your browser.

Capture an image using your webcam.

The app will validate the image and check lighting conditions.

If the image is valid, the AI will analyze your skin and provide recommendations.