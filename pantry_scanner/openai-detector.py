from openai import AzureOpenAI
import base64
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize the client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version=os.getenv("API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Prepare the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

base64_image = encode_image("./input/fridge.jpg")

# More detailed prompt requiring comprehensive object detection
system_prompt = """You are a precise computer vision object detection system. 
Your task is to:
1. Identify ALL objects visible in the image (minimum 5 objects if present)
2. For each object, provide:
   - A specific label (be specific, e.g. "wooden chair" not just "chair")
   - A confidence score between 0.0-1.0
   - Bounding box coordinates (x1, y1, x2, y2) normalized from 0-1
3. Return your analysis as a JSON object with a key "objects" containing an array of all detected items
4. Be thorough and don't miss any visible objects in the scene
5. Even small objects should be identified"""

# Make the API call
response = client.chat.completions.create(
    model=os.getenv("MODEL_NAME"),
    messages=[
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Perform comprehensive object detection on this image. Identify ALL visible objects (at least 5 if present), with their labels, confidence scores, and precise bounding box coordinates. Be thorough and specific."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }
    ],
    max_tokens=2000,
    response_format={"type": "json_object"}
)

# Parse and print the response
result = json.loads(response.choices[0].message.content)
print(json.dumps(result, indent=2))

# Count detected objects
if "objects" in result:
    print(f"\nTotal objects detected: {len(result['objects'])}")
    
# Save the JSON result to a file
output_filename = "results/gpt-vision-output.json"
with open(output_filename, "w") as json_file:
    json.dump(result, json_file, indent=2)

print(f"\nResults saved to {output_filename}")