import gradio as gr
import google.generativeai as genai
import os
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image
import re
from dotenv import load_dotenv
from prompts import *

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Configure Generative AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.7)

def analyze_skin_and_recommend(image):
    try:
        response = model.generate_content([image, analyses_prompt])
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def remove_coordinates_from_result(result):
    return re.sub(r'\[\d+, \d+, \d+, \d+\]', '', result).strip()

# Validate Image
def validate_image(image):
    # Convert PIL image to OpenCV format
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    if brightness < 50:
        return False, "Lighting is too dark. Please take the photo in better lighting."

    if brightness > 200:
        return False, "Lighting is too bright. Please adjust your environment."

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = face_detection.process(img_rgb)
    
    if not results.detections:
        return False, "No face detected. Please align your face inside the circle."

    height, width, _ = img.shape
    center_x, center_y = width // 2, height // 2
    radius = min(width, height) // 3  # Define circle size

    for detection in results.detections:
        bbox = detection.location_data.relative_bounding_box
        x_min = int(bbox.xmin * width)
        y_min = int(bbox.ymin * height)
        box_width = int(bbox.width * width)
        box_height = int(bbox.height * height)

        face_center_x = x_min + box_width // 2
        face_center_y = y_min + box_height // 2

        distance = np.sqrt((face_center_x - center_x) ** 2 + (face_center_y - center_y) ** 2)

        if distance > radius:
            return False, "Face is not properly aligned in the circle. Please adjust your position."

    return True, "Valid image"

# Gradio UI
def process_image(image):
    if image is None:
        return "No image provided. Please capture an image."

    # Validate image
    is_valid, message = validate_image(image)
    if not is_valid:
        return message

    # Process valid image
    result = analyze_skin_and_recommend(image)
    result = remove_coordinates_from_result(result)

    return result

iface = gr.Interface(
    fn=process_image,
    inputs=gr.Image(type="pil", label="Capture Image"),
    outputs=gr.Markdown(),
    title="AI Skin Analysis and Recommendation App",
    description="Capture an image using your webcam and get a skin analysis with recommendations."
)

# Launch Gradio App
if __name__ == "__main__":
    iface.launch(share=True)

#***************************************************************************
# import gradio as gr
# import google.generativeai as genai
# from dotenv import load_dotenv
# import os
# from PIL import Image
# import re
# from prompts import *
# import markdown
# # Load environment variables
# load_dotenv()
# api_key = os.getenv("GOOGLE_API_KEY")

# # Configure Generative AI
# genai.configure(api_key=api_key)
# model = genai.GenerativeModel(model_name="gemini-1.5-pro")

# def analyze_skin_and_recommend(image):
#     try:
#         response = model.generate_content([image, analyses_prompt])  # Send image directly
#         return response.text
#     except Exception as e:
#         return f"Error: {str(e)}"

# def remove_coordinates_from_result(result):
#     return re.sub(r'\[\d+, \d+, \d+, \d+\]', '', result).strip()

# # Gradio UI
# def process_image(image):
#     if image is None:
#         return "No image provided. Please capture an image."
    
#     result = analyze_skin_and_recommend(image)
#     result = remove_coordinates_from_result(result)
#     result = result.replace('*','')
#     #result = markdown.markdown(result)

#     return result

# iface = gr.Interface(
#     fn=process_image,
#     inputs=gr.Image(type="pil", label="Capture Image"),  # Webcam input
#     outputs="text",
#     title="AI Skin Analysis and Recommendation App",
#     description="Capture an image using your webcam and get a skin analysis with recommendations."
# )

# # Launch Gradio App
# if __name__ == "__main__":
#     iface.launch(share=True)