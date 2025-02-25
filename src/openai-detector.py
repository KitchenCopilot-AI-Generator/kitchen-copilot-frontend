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

# Updated prompt focusing on ingredients identification
system_prompt = """You are a helpful kitchen assistant with excellent vision capabilities.
Your task is to:
1. Identify ALL food ingredients and items visible in this refrigerator/kitchen image
2. List as many ingredients as you can possibly identify
3. Be specific about each item (e.g., "fresh spinach leaves" instead of just "vegetables")
4. Organize ingredients by categories (e.g., Dairy, Produce, Condiments, Beverages, etc.)
5. Return your analysis as a JSON object with:
   - A key "ingredients" containing an object with category names as keys
   - Each category should contain an array of specific ingredients
6. Be thorough and try to identify even partially visible items"""

# Make the API call
response = client.chat.completions.create(
    model=os.getenv("MODEL_NAME"),
    messages=[
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Please identify all the food ingredients and items in this refrigerator image. List as many as you can see and be specific about each item."},
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

# Count total ingredients
total_ingredients = 0
if "ingredients" in result:
    for category, items in result["ingredients"].items():
        total_ingredients += len(items)
    print(f"\nTotal ingredients detected: {total_ingredients}")
    
    # Print ingredients by category
    print("\nIngredients by category:")
    for category, items in result["ingredients"].items():
        print(f"\n{category} ({len(items)} items):")
        for item in items:
            print(f"- {item}")
    
# Save the JSON result to a file
output_filename = "results/gpt-vision-output.json"
os.makedirs(os.path.dirname(output_filename), exist_ok=True)
with open(output_filename, "w") as json_file:
    json.dump(result, json_file, indent=2)

print(f"\nResults saved to {output_filename}")