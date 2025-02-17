import streamlit as st
import cv2
import numpy as np
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
import os
from prompts import *
import time
from prompts import *
import re
import io

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Configure Generative AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

def analyze_skin_and_recommend(image, prompt):
    try:
        response = model.generate_content([image, prompt])  # Send image directly
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def remove_coordinates_from_result(result):
    return re.sub(r'\[\d+, \d+, \d+, \d+\]', '', result).strip()

def capture_image():
    cap = cv2.VideoCapture(0)  # Open the webcam

    if not cap.isOpened():
        st.error("Could not open webcam")
        return None

    st.write("Camera will capture image in 3 seconds...")
    time.sleep(3)  # Wait for 3 seconds

    ret, frame = cap.read()  # Capture frame
    cap.release()  # Release the webcam

    if not ret:
        st.error("Failed to capture image")
        return None

    # Convert BGR to RGB (OpenCV loads images in BGR format)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(frame)  # Convert to PIL Image

    return image

# Streamlit App
def main():
    st.title("AI Skin Analysis and Recommendation App")
    st.write("Click 'Capture Image' to take a photo using your webcam.")

    if "captured_image" not in st.session_state:
        st.session_state.captured_image = None  # Store captured image persistently

    if st.button("Capture Image"):
        st.session_state.captured_image = capture_image()

    if st.session_state.captured_image:
        st.image(st.session_state.captured_image, caption="Captured Image", use_column_width=True)

        if st.button("Analyze Skin"):
            with st.spinner("Analyzing your skin..."):
                result = analyze_skin_and_recommend(st.session_state.captured_image, analyses_prompt)
                result = remove_coordinates_from_result(result)
                st.write(result)

if __name__ == "__main__":
    main()


# import streamlit as st
# from PIL import Image, ImageDraw
# import google.generativeai as genai
# from dotenv import load_dotenv
# import json
# import re
# from langchain_google_genai import ChatGoogleGenerativeAI
# from prompts import *
# import os
# import warnings
# warnings.filterwarnings("ignore", category=DeprecationWarning)

# load_dotenv()

# # Configure Generative AI
# api_key = os.getenv("GOOGLE_API_KEY")

# genai.configure(api_key=api_key)
# model = genai.GenerativeModel(model_name="gemini-1.5-pro")
# # chat_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.5, max_output_tokens=8192)
# # Function to analyze skin and provide recommendations
# def analyze_skin_and_recommend(image, prompt):
#     try:
#         # Generate content using the AI model
#         response = model.generate_content([image, prompt])
#         return response.text
#     except Exception as e:
#         return f"Error: {str(e)}"

# def remove_coordinates_from_result(result):
#     cleaned_result = re.sub(r'\[\d+, \d+, \d+, \d+\]', '', result)
#     return cleaned_result.strip()

# # Streamlit App
# def main():
#     st.title("AI Skin Analysis and Recommendation App")
#     st.write("Upload an image of your face, and let our AI provide a detailed skin analysis, scores for specific concerns, and personalized skincare recommendations.")

#     # File uploader for image input
#     uploaded_image = st.file_uploader("Upload an image (JPEG/PNG)", type=["jpg", "jpeg", "png"])

#     if uploaded_image:
#         # Display the uploaded image
#         image = Image.open(uploaded_image)
#         width, height = image.size  # Get image dimensions
#         st.image(image, caption="Uploaded Image", use_container_width=True)

#         if st.button("Analyze Skin"):
#             with st.spinner("Analyzing your skin..."):
#                 result = analyze_skin_and_recommend(image, analyses_prompt).replace('json','').replace('```','')
#                 try:
#                     st.write(result)
#                 except json.JSONDecodeError as e:
#                     st.error("Failed to parse the AI response. Please try again.",e)


# if __name__ == "__main__":
#     main()
