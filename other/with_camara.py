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

def analyze_lighting_conditions(image):
    # Convert PIL image to OpenCV format
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Calculate histogram
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist_norm = hist.ravel() / hist.sum()

    # Compute cumulative distribution
    Q = hist_norm.cumsum()

    # Determine underexposure
    low_light = np.sum(hist_norm[:50])
    if low_light > 0.5:
        return False, "The image is underexposed. Please increase the lighting or adjust your camera settings."

    # Determine overexposure
    high_light = np.sum(hist_norm[-50:])
    if high_light > 0.5:
        return False, "The image is overexposed. Please decrease the lighting or adjust your camera settings."

    return True, "The lighting conditions are adequate."

def validate_image(image):
    # Convert PIL image to OpenCV format
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Check lighting conditions
    is_lighting_ok, lighting_message = analyze_lighting_conditions(image)
    if not is_lighting_ok:
        return False, lighting_message

    # Check if a face is detected
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = face_detection.process(img_rgb)
    
    if not results.detections:
        return False, "No face detected. Please align your face inside the circle."

    # Check if face is inside a round boundary
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


###********************************************************************************

# import os
# import time
# import google.generativeai as genai
# import streamlit as st
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Configure the Google Generative AI API key
# api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
# genai.configure(api_key=api_key)

# # Streamlit interface setup
# st.set_page_config(page_title="Video Scene Analysis with Gemini Flash 1.5–8B", layout="wide")
# st.title("Video Scene Analysis with Gemini Flash 1.5–8B")

# # Upload video
# uploaded_video = st.file_uploader("Upload a video file (mp4)", type=["mp4"])

# if uploaded_video is not None:
#     # Save the uploaded file temporarily
#     temp_video_path = f"temp_{uploaded_video.name}"
#     with open(temp_video_path, "wb") as f:
#         f.write(uploaded_video.getbuffer())

#     st.success("Video uploaded successfully! Processing...")

#     def upload_to_gemini(path, mime_type=None):
#         """Uploads the given file to Gemini."""
#         file = genai.upload_file(path, mime_type=mime_type)
#         st.info(f"Uploaded file '{file.display_name}' as: {file.uri}")
#         return file

#     def wait_for_file_active(file):
#         """Waits for the given file to be active."""
#         while True:
#             current_file = genai.get_file(file.name)
#             if current_file.state.name == "ACTIVE":
#                 return True
#             elif current_file.state.name != "PROCESSING":
#                 st.error(f"File {file.name} failed to process")
#                 return False
#             time.sleep(10)

#     # Upload file to Gemini and wait for it to become active
#     uploaded_file = upload_to_gemini(temp_video_path, mime_type="video/mp4")

#     if wait_for_file_active(uploaded_file):
#         # Create the model for generation
#         generation_config = {
#             "temperature": 1,
#             "top_p": 0.95,
#             "top_k": 40,
#             "max_output_tokens": 8192,
#             "response_mime_type": "text/plain",
#         }

#         model = genai.GenerativeModel(
#             model_name="gemini1.5flash8b",
#             generation_config=generation_config,
#         )

#         # Start chat session with the model
#         chat_session = model.start_chat(
#             history=[
#                 {
#                     "role": "user",
#                     "parts": [uploaded_file],
#                 }
#             ]
#         )

#         user_input = st.text_input("Ask a question about the video scene:", "Explain the scene in 2000 characters or less.")

#         if st.button("Get Response"):
#             response = chat_session.send_message(user_input)
#             st.subheader("Gemini Response:")
#             st.write(response.text)

#     # Clean up temporary video file
#     os.remove(temp_video_path)

###********************************************************************************

# import streamlit as st
# import cv2
# import numpy as np
# from PIL import Image
# import google.generativeai as genai
# from dotenv import load_dotenv
# import os
# from prompts import *
# import time
# from prompts import *
# import re
# import io

# # Load environment variables
# load_dotenv()
# api_key = os.getenv("GOOGLE_API_KEY")

# # Configure Generative AI
# genai.configure(api_key=api_key)
# model = genai.GenerativeModel(model_name="gemini-1.5-pro")

# def analyze_skin_and_recommend(image, prompt):
#     try:
#         response = model.generate_content([image, prompt])  # Send image directly
#         return response.text
#     except Exception as e:
#         return f"Error: {str(e)}"

# def remove_coordinates_from_result(result):
#     return re.sub(r'\[\d+, \d+, \d+, \d+\]', '', result).strip()

# def capture_image():
#     cap = cv2.VideoCapture(0)  # Open the webcam

#     if not cap.isOpened():
#         st.error("Could not open webcam")
#         return None

#     st.write("Camera will capture image in 3 seconds...")
#     time.sleep(3)  # Wait for 3 seconds

#     ret, frame = cap.read()  # Capture frame
#     cap.release()  # Release the webcam

#     if not ret:
#         st.error("Failed to capture image")
#         return None

#     # Convert BGR to RGB (OpenCV loads images in BGR format)
#     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     image = Image.fromarray(frame)  # Convert to PIL Image

#     return image

# # Streamlit App
# def main():
#     st.title("AI Skin Analysis and Recommendation App")
#     st.write("Click 'Capture Image' to take a photo using your webcam.")

#     if "captured_image" not in st.session_state:
#         st.session_state.captured_image = None  # Store captured image persistently

#     if st.button("Capture Image"):
#         st.session_state.captured_image = capture_image()

#     if st.session_state.captured_image:
#         st.image(st.session_state.captured_image, caption="Captured Image", use_column_width=True)

#         if st.button("Analyze Skin"):
#             with st.spinner("Analyzing your skin..."):
#                 result = analyze_skin_and_recommend(st.session_state.captured_image, analyses_prompt)
#                 result = remove_coordinates_from_result(result)
#                 st.write(result)

# if __name__ == "__main__":
#     main()
