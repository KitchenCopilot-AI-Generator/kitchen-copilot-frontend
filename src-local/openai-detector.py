"""
Fridge Vision Script - Identifies food items in refrigerator images using Azure OpenAI Vision API
"""

import base64
import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

# Constants
INPUT_IMAGE_PATH = "./input/fridge.jpg"
OUTPUT_FILENAME = "results/gpt-vision-output.json"

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    return {
        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
        "api_version": os.getenv("API_VERSION"),
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "model_name": os.getenv("MODEL_NAME")
    }

def initialize_client(config):
    """Initialize the Azure OpenAI client"""
    return AzureOpenAI(
        api_key=config["api_key"],
        api_version=config["api_version"],
        azure_endpoint=config["endpoint"]
    )

def encode_image(image_path):
    """Encode an image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_system_prompt():
    """Return the system prompt for image analysis"""
    return """You are a helpful kitchen assistant with excellent vision capabilities.
Your task is to:
1. Identify ALL food ingredients and items visible in this refrigerator/kitchen image
2. List as many ingredients as you can possibly identify
3. Be specific about each item (e.g., "fresh spinach leaves" instead of just "vegetables")
4. Organize ingredients by categories (e.g., Dairy, Produce, Condiments, Beverages, etc.)
5. Return your analysis as a JSON object with:
   - A key "ingredients" containing an object with category names as keys
   - Each category should contain an array of specific ingredients
6. Be thorough and try to identify even partially visible items"""

def analyze_image(client, config, image_path):
    """Analyze the image using Azure OpenAI Vision API"""
    base64_image = encode_image(image_path)
    
    response = client.chat.completions.create(
        model=config["model_name"],
        messages=[
            {"role": "system", "content": get_system_prompt()},
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
    
    return json.loads(response.choices[0].message.content)

def save_result(result, output_path):
    """Save the analysis result to a JSON file"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as json_file:
        json.dump(result, json_file, indent=2)
    
    return output_path

def print_analysis_summary(result):
    """Print a summary of the analysis results"""
    if "ingredients" not in result:
        print("No ingredients detected in the image.")
        return
    
    # Count total ingredients
    total_ingredients = sum(len(items) for items in result["ingredients"].values())
    print(f"\nTotal ingredients detected: {total_ingredients}")
    
    # Print ingredients by category
    print("\nIngredients by category:")
    for category, items in result["ingredients"].items():
        print(f"\n{category} ({len(items)} items):")
        for item in items:
            print(f"- {item}")

def main():
    """Main function to execute the image analysis pipeline"""
    config = load_environment()
    client = initialize_client(config)
    
    print(f"Analyzing image: {INPUT_IMAGE_PATH}")
    result = analyze_image(client, config, INPUT_IMAGE_PATH)
    
    print(json.dumps(result, indent=2))
    print_analysis_summary(result)
    
    output_path = save_result(result, OUTPUT_FILENAME)
    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    main()