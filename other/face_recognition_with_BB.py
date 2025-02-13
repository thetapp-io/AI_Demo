import streamlit as st
from PIL import Image, ImageDraw
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from prompts import *
# Load environment variables
load_dotenv()

# Configure Generative AI
genai.configure(api_key="AIzaSyCHvis0l74Z4JAETgbbES_PPxaJgi-dD90")
model = genai.GenerativeModel(model_name="gemini-1.5-pro")
chat_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.5, max_output_tokens=8192)
# Function to analyze skin and provide recommendations
box_string =  "For each identified concern, return all bounding box coordinates that outline the affected areas, in the format [[ymin1, xmin1, ymax1, xmax1], [ymin2, xmin2, ymax2, xmax2], ...]. "
def analyze_skin_and_recommend(image, prompt):
    try:
        # Generate content using the AI model
        response = model.generate_content([image, prompt])
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def remove_coordinates_from_result(result):
    cleaned_result = re.sub(r'\[\d+, \d+, \d+, \d+\]', '', result)
    return cleaned_result.strip()

# Streamlit App
def main():
    st.title("AI Skin Analysis and Recommendation App")
    st.write("Upload an image of your face, and let our AI provide a detailed skin analysis, scores for specific concerns, and personalized skincare recommendations.")

    # File uploader for image input
    uploaded_image = st.file_uploader("Upload an image (JPEG/PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_image:
        # Display the uploaded image
        image = Image.open(uploaded_image)
        width, height = image.size  # Get image dimensions
        st.image(image, caption="Uploaded Image", use_column_width=True)

        if st.button("Analyze Skin"):
            with st.spinner("Analyzing your skin..."):
                result = analyze_skin_and_recommend(image, analyses_prompt+box_string).replace('json','').replace('```','')
                # coords = analyze_skin_and_recommend(image, coordinates_prompt).replace('json','').replace('```','')                #print(clean_result)
                bounding_boxes = chat_llm.invoke(coordinates_extract_prompt.format(input_string = result))
                print(bounding_boxes)
                result = remove_coordinates_from_result(result)
                print(result)
                try:
                    pass
                    bounding_boxes = json.loads(bounding_boxes.content.replace('json', '').replace('```', ''))
                    print(bounding_boxes)
                    # Annotate the image with bounding boxes for all concerns
                    annotated_image = image.copy()
                    draw = ImageDraw.Draw(annotated_image)

                    # Define a color map for concerns
                    color_map = {
                        "spots": "red",
                        "dark_circles": "blue",
                        "radiance": "green",
                        "eyebags": "orange",
                        "tear_trough": "purple",
                        "redness": "yellow",
                        "pores": "pink",
                        "texture": "brown",
                        "oiliness": "cyan",
                        "droopy_upper_eyelids": "magenta",
                        "droopy_lower_eyelids": "lime",
                        "wrinkles": "teal",
                        "moisture": "gold",
                        "firmness": "violet",
                        "acne": "navy",
                    }

                    for concern, boxes in bounding_boxes.items():
                        #print(concern)
                        if boxes:  # If there are bounding boxes for this concern
                            for box in boxes:
                                rel_y1, rel_x1, rel_y2, rel_x2 = box
                                abs_x1 = int(rel_x1 / 1000 * width)
                                abs_y1 = int(rel_y1 / 1000 * height)
                                abs_x2 = int(rel_x2 / 1000 * width)
                                abs_y2 = int(rel_y2 / 1000 * height)

                                # Draw rectangle with specific color
                                draw.rectangle(
                                    [abs_x1, abs_y1, abs_x2, abs_y2], 
                                    outline=color_map.get(concern, "black"), 
                                    width=1
                                )

                                # Add concern text with the same color
                                draw.text(
                                    (abs_x1, abs_y1 - 15),  # Position above the rectangle
                                    concern, 
                                    fill=color_map.get(concern, "black")
                                )

                    # Display the annotated image
                    st.image(annotated_image, caption="Skin Analysis with Concerns Highlighted", use_column_width=True)

                    # Display the analysis result
                    st.subheader("Skin Analysis and Recommendations:")
                    st.write(result)

                except json.JSONDecodeError as e:
                    st.error(f"Failed to parse the AI response. Please try again. Error: {e}")


if __name__ == "__main__":
    main()
