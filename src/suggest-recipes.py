import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# Initialize the Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Function to load the ingredients from JSON
def load_ingredients(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Flatten the ingredients list
    all_ingredients = []
    for category, items in data['ingredients'].items():
        all_ingredients.extend(items)
    
    return all_ingredients

# Function to generate recipe suggestions using LLM
def generate_recipe_suggestions(ingredients, num_recipes=5):
    ingredients_str = ", ".join(ingredients)
    
    system_prompt = """You are a creative chef who specializes in creating recipes based on available ingredients.
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
    
    try:
        response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here are the ingredients I have available: {ingredients_str}. Please suggest {num_recipes} diverse recipes that I could make with these ingredients. Include some recipes that use most of what I have, and some creative options that might require a few additional ingredients. Focus on wholesome, flavorful dishes."}
            ],
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error generating recipes: {str(e)}")
        return {"recipes": []}

# Function to display recipes in a user-friendly way
def display_recipes(recipes_data):
    # Sort recipes by completeness score (highest first)
    sorted_recipes = sorted(recipes_data["recipes"], key=lambda x: x["completeness_score"], reverse=True)
    
    print("\n==== RECIPE SUGGESTIONS BASED ON YOUR INGREDIENTS ====\n")
    
    for i, recipe in enumerate(sorted_recipes, 1):
        print(f"Recipe {i}: {recipe['name']}")
        print(f"Completeness Score: {recipe['completeness_score']}% (you have {len(recipe['available_ingredients'])} of {len(recipe['total_ingredients'])} ingredients)")
        print(f"Cooking Time: {recipe['cooking_time']}")
        print(f"Difficulty: {recipe['difficulty']}")
        
        print("\nAvailable Ingredients:")
        for ing in recipe['available_ingredients']:
            print(f"  ✓ {ing}")
        
        print("\nMissing Ingredients:")
        if recipe['missing_ingredients']:
            for ing in recipe['missing_ingredients']:
                print(f"  ✗ {ing}")
        else:
            print("  None - you have everything you need!")
        
        print("\nInstructions:")
        for j, step in enumerate(recipe['instructions'], 1):
            print(f"  {j}. {step}")
        
        print("\n" + "="*60 + "\n")

# Function to save recipes to a file
def save_recipes(recipes_data, output_file="results/suggested_recipes.json"):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(recipes_data, f, indent=2)
    print(f"Recipes saved to {output_file}")

# Main function
def main():
    # Load ingredients from the JSON file
    ingredients = load_ingredients("results/gpt-vision-output.json")
    print(f"Loaded {len(ingredients)} ingredients from your fridge")
    
    # Generate recipe suggestions
    print("Generating recipe suggestions...")
    recipes_data = generate_recipe_suggestions(ingredients, num_recipes=7)
    
    # Display recipes
    display_recipes(recipes_data)
    
    # Save recipes to file
    save_recipes(recipes_data)
    
    # Create a simple pandas DataFrame for analysis
    if recipes_data["recipes"]:
        df = pd.DataFrame([{
            "Recipe": r["name"],
            "Completeness": r["completeness_score"],
            "Available": len(r["available_ingredients"]),
            "Missing": len(r["missing_ingredients"]),
            "Total": len(r["total_ingredients"]),
            "Cooking Time": r["cooking_time"],
            "Difficulty": r["difficulty"]
        } for r in recipes_data["recipes"]])
        
        print("\n==== RECIPE ANALYSIS ====")
        print(df)

if __name__ == "__main__":
    main()