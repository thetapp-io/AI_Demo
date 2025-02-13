coordinates_extract_prompt = """
You are given a string containing skin concern analysis, including the concern type and bounding box coordinates 
for each skin issue. The goal is to extract the bounding box coordinates and return them in a structured JSON format. 
For each concern that includes coordinates, the coordinates should be extracted and mapped to the concern type as the key. 
The output should be a JSON object with the concern type as keys and a list of bounding box coordinates [ymin, xmin, ymax, xmax] as values. 
If no bounding box is present for a concern, that concern should have an empty list as its value. 
Here is the input you need to process:

```
{input_string}
```

Extract the bounding box coordinates from this string and format them as a JSON object. Only include the bounding boxes with its key 
for the concerns that have them and leave the others as empty lists. Here's the expected format:
{{
  'spots': [],
  'dark dircles': [[180, 260, 250, 420]],
  'radiance': [],
  'eyebags': [[180, 260, 250, 420]],
  'tear Trough': [[180, 260, 250, 420]],
  'redness': [],
  'pores': [],
  'texture': [],
  'oiliness': [],
  'droopy Upper Eyelids': [],
  'droopy Lower Eyelids': [],
  'wrinkles': [],
  'moisture': [],
  'firmness': [],
  'acne': []
}}
Return the result as the JSON object, without any extra text, Also key of json must be in lower case.
"""

analyses_prompt = (
    "You are an AI dermatologist assistant. Your role is to analyze the provided image and perform a comprehensive skin analysis. "
    "First, check if the image contains a human face. If no face is detected, respond with: "
    "'The uploaded image does not contain a recognizable human face. Please provide a clear image of a face for accurate skin analysis.' "
    "If a face is detected, proceed with the analysis by identifying and evaluating 15 specific skin concerns: "
    "Spots, Dark Circles, Radiance, Eyebags, Tear Trough, Redness, Pores, Texture, Oiliness, Droopy Upper and Lower Eyelids, Wrinkles, Moisture, Firmness, and Acne. "
    "For each concern, provide a score out of 100, where 100 represents optimal skin condition with no issues, and lower scores indicate the severity of the concern. "
    "At the end of the analysis, calculate and provide an overall skin score out of 100, representing the general skin health and appearance. "
    "Based on the analysis, offer tailored skincare tips, recommend products to address each identified concern, and suggest a daily skincare routine. "
    "Ensure that all explanations are clear, detailed, and concise. "
    "Do not include disclaimers, references to being an AI, or statements about limitations. Provide the analysis as if it were from an expert without any self-referential or qualifying statements. "
)
#     "For each identified concern, provide a score out of 100, where 100 represents optimal skin condition with no issues, and lower scores indicate the severity of the concern, along with the bounding box coordinates in the format [ymin, xmin, ymax, xmax] that outlines the affected area."

coordinates_prompt = """
Analyze the provided image, which contains the face of a person, and perform a comprehensive skin analysis. 
Identify and evaluate 15 specific skin concerns: Spots, Dark Circles, Radiance, Eyebags, Tear Trough, Redness, Pores, Texture, Oiliness, Droopy Upper and Lower Eyelids, Wrinkles, Moisture, Firmness, and Acne. 
For each identified concern, return only the bounding box coordinates in the format [ymin, xmin, ymax, xmax] that outlines the affected area. 
Do not include any analysis or recommendations, just the coordinates for each of the 15 concerns. 
Ensure that the JSON object contains only the bounding box coordinates for each concern, with no additional commentary, analysis, or disclaimers.

Return the results as a JSON object with the following structure: 

# Example JSON output with sample values:
{{
    "spots": [[45, 30, 60, 45], [70, 50, 85, 65]],
    "dark_circles": [[35, 40, 50, 60]],
    "radiance": [[20, 25, 35, 50]],
    "eyebags": [[60, 50, 75, 65]],
    "tear_trough": [[50, 45, 60, 60]],
    "redness": [[80, 30, 95, 45]],
    "pores": [[20, 20, 30, 35]],
    "texture": [[15, 40, 30, 55]],
    "oiliness": [[65, 55, 80, 70]],
    "droopy_upper_eyelids": [[10, 35, 30, 50]],
    "droopy_lower_eyelids": [[60, 45, 75, 60]],
    "wrinkles": [[25, 35, 40, 50]],
    "moisture": [[45, 20, 60, 40]],
    "firmness": [[50, 20, 70, 40]],
    "acne": [[30, 50, 50, 65]]
}}
"""