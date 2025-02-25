"""
Recipe Service - Service for generating recipe suggestions based on ingredients
"""

import json
import os
import pandas as pd
from data.prompts.recipe_prompt import get_recipe_system_prompt

class RecipeService:
    """Service for generating recipes based on available ingredients"""
    
    def __init__(self, azure_client):
        """
        Initialize the Recipe Service
        
        Args:
            azure_client: An initialized AzureClientService object
        """
        self.client = azure_client.get_client()
        self.model_name = azure_client.get_model_name()
    
    def load_ingredients(self, json_path):
        """
        Load and flatten ingredients from JSON file
        
        Args:
            json_path: Path to the JSON file with ingredients
            
        Returns:
            List of ingredient strings
        """
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Flatten the ingredients list
            all_ingredients = []
            for category, items in data['ingredients'].items():
                all_ingredients.extend(items)
            
            return all_ingredients
        except Exception as e:
            raise Exception(f"Error loading ingredients: {str(e)}")
    
    def generate_recipes(self, ingredients, num_recipes=5):
        """
        Generate recipe suggestions using Azure OpenAI API
        
        Args:
            ingredients: List of available ingredients
            num_recipes: Number of recipes to generate
            
        Returns:
            Dictionary containing recipe suggestions
        """
        ingredients_str = ", ".join(ingredients)
        user_prompt = f"""Here are the ingredients I have available: {ingredients_str}. 
Please suggest {num_recipes} diverse recipes that I could make with these ingredients. 
Include some recipes that use most of what I have, and some creative options that might 
require a few additional ingredients. Focus on wholesome, flavorful dishes."""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": get_recipe_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Error generating recipes: {str(e)}")
    
    def save_recipes(self, recipes_data, output_path):
        """
        Save recipes to a JSON file
        
        Args:
            recipes_data: Recipe data from generate_recipes
            output_path: Path to save the output file
            
        Returns:
            Path to the saved file
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(recipes_data, f, indent=2)
        return output_path
    
    def get_recipes_analysis(self, recipes_data):
        """
        Create a DataFrame with recipe analysis
        
        Args:
            recipes_data: Recipe data from generate_recipes
            
        Returns:
            DataFrame with recipe analysis or None if no recipes
        """
        if not recipes_data.get("recipes", []):
            return None
        
        return pd.DataFrame([{
            "recipe_name": r["name"],
            "completeness": r["completeness_score"],
            "available_count": len(r["available_ingredients"]),
            "missing_count": len(r["missing_ingredients"]),
            "total_ingredients": len(r["total_ingredients"]),
            "cooking_time": r["cooking_time"],
            "difficulty": r["difficulty"]
        } for r in recipes_data["recipes"]])