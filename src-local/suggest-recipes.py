"""
Recipe Generator Script - Generates recipe suggestions based on available ingredients
using Azure OpenAI API
"""

import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
import pandas as pd

# Constants
INGREDIENTS_FILE = "results/gpt-vision-output.json"
OUTPUT_FILE = "results/suggested_recipes.json"
DEFAULT_RECIPE_COUNT = 7

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

def load_ingredients(json_path):
    """Load and flatten ingredients from JSON file"""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Flatten the ingredients list
        all_ingredients = []
        for category, items in data['ingredients'].items():
            all_ingredients.extend(items)
        
        return all_ingredients
    except Exception as e:
        print(f"Error loading ingredients: {str(e)}")
        return []

def get_system_prompt():
    """Return the system prompt for recipe generation"""
    return """You are a creative chef who specializes in creating recipes based on available ingredients.
Your task is to suggest recipes that can be made with the provided ingredients.
For each recipe, you will:
1. Generate the recipe name
2. List all required ingredients (both those provided and those missing)
3. Provide detailed cooking instructions
4. Rate what percentage of necessary ingredients are available

Return your suggestions as a JSON object with the following structure:
{
  "recipes": [
    {
      "name": "Recipe Name",
      "total_ingredients": [list of all ingredients needed],
      "available_ingredients": [list of ingredients from user's inventory],
      "missing_ingredients": [list of ingredients not in user's inventory],
      "completeness_score": 85,  // percentage of available ingredients
      "instructions": ["Step 1...", "Step 2...", ...],
      "cooking_time": "30 minutes",
      "difficulty": "Easy/Medium/Hard"
    },
    ...
  ]
}
"""

def generate_recipe_suggestions(client, config, ingredients, num_recipes=5):
    """Generate recipe suggestions using Azure OpenAI API"""
    ingredients_str = ", ".join(ingredients)
    user_prompt = f"""Here are the ingredients I have available: {ingredients_str}. 
Please suggest {num_recipes} diverse recipes that I could make with these ingredients. 
Include some recipes that use most of what I have, and some creative options that might 
require a few additional ingredients. Focus on wholesome, flavorful dishes."""

    try:
        response = client.chat.completions.create(
            model=config["model_name"],
            messages=[
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error generating recipes: {str(e)}")
        return {"recipes": []}

def save_recipes(recipes_data, output_file):
    """Save recipes to a JSON file"""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(recipes_data, f, indent=2)
    return output_file

def create_recipe_analysis(recipes_data):
    """Create a pandas DataFrame for recipe analysis"""
    if not recipes_data["recipes"]:
        return None
    
    return pd.DataFrame([{
        "Recipe": r["name"],
        "Completeness": r["completeness_score"],
        "Available": len(r["available_ingredients"]),
        "Missing": len(r["missing_ingredients"]),
        "Total": len(r["total_ingredients"]),
        "Cooking Time": r["cooking_time"],
        "Difficulty": r["difficulty"]
    } for r in recipes_data["recipes"]])

def main():
    """Main function to execute the recipe generation pipeline"""
    config = load_environment()
    client = initialize_client(config)
    
    # Load ingredients from the JSON file
    ingredients = load_ingredients(INGREDIENTS_FILE)
    print(f"Loaded {len(ingredients)} ingredients from your fridge")
    
    if not ingredients:
        print("No ingredients found. Please run the vision script first.")
        return
    
    # Generate recipe suggestions
    print("Generating recipe suggestions...")
    recipes_data = generate_recipe_suggestions(client, config, ingredients, num_recipes=DEFAULT_RECIPE_COUNT)
    
    # Save recipes to file
    output_path = save_recipes(recipes_data, OUTPUT_FILE)
    print(f"Recipes saved to {output_path}")
    
    # Create and display analysis
    df = create_recipe_analysis(recipes_data)
    if df is not None:
        print("\n==== RECIPE ANALYSIS ====")
        print(df)
    else:
        print("No recipes were generated.")

if __name__ == "__main__":
    main()