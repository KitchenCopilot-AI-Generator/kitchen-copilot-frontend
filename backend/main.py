"""
Fridge Recipe Generator - Main entry point for the application

This application:
1. Analyzes fridge/food images to identify ingredients
2. Generates recipe suggestions based on available ingredients

The application can be run in:
- CLI mode for direct command line use
- API mode for integration with other applications or frontends
"""

import argparse
import os
from flask import Flask, request, jsonify
import uuid
import json
from typing import Optional

# Import services and config
from config import Config
from services.azure_client import AzureClientService
from services.vision_service import VisionService
from services.recipe_service import RecipeService

from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)

CORS(app)  # This enables CORS for all routes

# Global services - will be initialized in setup_api_mode
config = None
vision_service = None
recipe_service = None

class CLIProcessor:
    """Command-line interface processor for the application"""
    
    def __init__(self, config, vision_service, recipe_service):
        """
        Initialize CLI processor
        
        Args:
            config: Configuration object
            vision_service: Vision analysis service
            recipe_service: Recipe generation service
        """
        self.config = config
        self.vision_service = vision_service
        self.recipe_service = recipe_service
    
    def analyze_image(self, image_filename: str) -> dict:
        """
        Analyze a fridge/food image and identify ingredients
        
        Args:
            image_filename: Filename of the image to analyze
            
        Returns:
            Analysis result
        """
        # Check if image already exists in the results directory
        paths = self.config.get_file_paths(image_filename)
        if os.path.exists(paths.get("request_image", "")):
            print(f"Analyzing image: {paths['request_image']}")
            result = self.vision_service.analyze_image(paths["request_image"])
        else:
            raise FileNotFoundError(f"Image file {image_filename} not found in input or results directory")
        
        # Save full result including summary
        summary = self.vision_service.get_ingredients_summary(result)
        full_result = {
            "status": "complete",
            "result": result,
            "summary": summary,
            "image_filename": image_filename
        }
        output_path = self.vision_service.save_analysis(full_result, paths["vision_output"])
        print(f"Analysis saved to {output_path}")
        
        # Get summary
        summary = self.vision_service.get_ingredients_summary(result)
        print(f"\nFound {summary['total_count']} ingredients in {summary['categories']} categories:")
        for category, count in summary["by_category"].items():
            print(f"- {category}: {count} items")
        
        return result
    
    def generate_recipes(self, image_filename: Optional[str] = None, num_recipes: int = 5) -> dict:
        """
        Generate recipe suggestions based on available ingredients
        
        Args:
            image_filename: Optional filename of previously analyzed image
            num_recipes: Number of recipes to generate
            
        Returns:
            Generated recipes
        """
        paths = self.config.get_file_paths(image_filename)
        
        # Check if ingredients file exists
        if not os.path.exists(paths["vision_output"]):
            print("No ingredients analysis found. Please analyze an image first.")
            return {}
        
        # Load ingredients
        ingredients = self.recipe_service.load_ingredients(paths["vision_output"])
        print(f"Loaded {len(ingredients)} ingredients from analysis")
        
        # Generate recipes
        print(f"Generating {num_recipes} recipe suggestions...")
        recipes_data = self.recipe_service.generate_recipes(ingredients, num_recipes=num_recipes)
        
        # Save recipes
        output_path = self.recipe_service.save_recipes(recipes_data, paths["recipes_output"])
        print(f"Recipes saved to {output_path}")
        
        # Print recipe analysis
        df = self.recipe_service.get_recipes_analysis(recipes_data)
        if df is not None:
            print("\n==== RECIPE ANALYSIS ====")
            print(df)
        else:
            print("No recipes were generated.")
        
        return recipes_data

# Flask route handlers
@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    """
    Analyze a fridge/food image and identify ingredients
    
    Returns:
        Analysis result or processing status
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        # Create a unique filename
        file_ext = os.path.splitext(file.filename)[1]
        image_filename = f"fridge_{uuid.uuid4().hex[:8]}{file_ext}"
        
        # Get file paths
        paths = config.get_file_paths(image_filename)
        
        # Save the uploaded file directly to the results directory
        file.save(paths["request_image"])
        
        # Process image
        result = vision_service.analyze_image(paths["request_image"])
        
        # Get a summary
        summary = vision_service.get_ingredients_summary(result)
        
        # Create full response
        full_response = {
            "status": "complete",
            "result": result,
            "summary": summary,
            "image_filename": image_filename
        }
        
        # Save the full response
        vision_service.save_analysis(full_response, paths["vision_output"])
        
        # Include request_id (which is the base name of the image)
        request_id = os.path.splitext(image_filename)[0]
        
        return jsonify({
            "status": "complete",
            "result": result,
            "summary": summary,
            "image_filename": image_filename,
            "request_id": request_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ingredients', methods=['GET'])
def get_ingredients():
    """
    Get ingredients from the most recent analysis or specified request ID
    
    Returns:
        Ingredients data
    """
    try:
        # Get request ID (folder name) from query parameter
        request_id = request.args.get('request_id')
        
        if request_id:
            # Look for the request folder
            request_dir = os.path.join(config.results_dir, request_id)
            ingredients_file = os.path.join(request_dir, "ingredients.json")
        else:
            # Use most recent analysis
            paths = config.get_file_paths()
            ingredients_file = paths["vision_output"]
        
        # Check if file exists
        if not os.path.exists(ingredients_file):
            return jsonify({
                "error": "No ingredients analysis found. Please analyze an image first."
            }), 404
        
        # Load and return the ingredients
        with open(ingredients_file, "r") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recipes', methods=['GET'])
def get_recipes():
    """
    Get recipes from the most recent generation or specified request ID
    
    Returns:
        Recipes data
    """
    try:
        # Get request ID (folder name) from query parameter
        request_id = request.args.get('request_id')
        
        if request_id:
            # Look for the request folder
            request_dir = os.path.join(config.results_dir, request_id)
            recipes_file = os.path.join(request_dir, "recipes.json")
        else:
            # Use most recent analysis
            paths = config.get_file_paths()
            recipes_file = paths["recipes_output"]
        
        # Check if file exists
        if not os.path.exists(recipes_file):
            return jsonify({
                "error": "No recipes found. Please generate recipes first."
            }), 404
        
        # Load and return the recipes
        with open(recipes_file, "r") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-recipes', methods=['POST'])
def generate_recipes():
    """
    Generate recipe suggestions based on available ingredients
    
    Returns:
        Generated recipes
    """
    try:
        # Parse request data
        data = request.get_json() or {}
        num_recipes = data.get('num_recipes', 5)
        request_id = data.get('request_id')
        
        # Determine ingredients file path
        if request_id:
            request_dir = os.path.join(config.results_dir, request_id)
            ingredients_file = os.path.join(request_dir, "ingredients.json")
        else:
            paths = config.get_file_paths()
            ingredients_file = paths["vision_output"]
        
        # Check if file exists
        if not os.path.exists(ingredients_file):
            return jsonify({
                "error": "No ingredients analysis found. Please analyze an image first."
            }), 404
        
        # Load ingredients
        ingredients = recipe_service.load_ingredients(ingredients_file)
        
        # Generate recipes
        recipes_data = recipe_service.generate_recipes(
            ingredients, 
            num_recipes=num_recipes
        )
        
        # Get analysis
        analysis = recipe_service.get_recipes_analysis(recipes_data)
        analysis_dict = analysis.to_dict('records') if analysis is not None else []
        
        # Create full response
        full_response = {
            "items": recipes_data["recipes"],
            "analysis": analysis_dict,
            "ingredient_count": len(ingredients)
        }
        
        # Determine the recipes output path - use the same request_id if provided
        if request_id:
            request_dir = os.path.join(config.results_dir, request_id)
            recipes_output = os.path.join(request_dir, "recipes.json")
        else:
            paths = config.get_file_paths()
            recipes_output = paths["recipes_output"]
        
        # Save the full response
        os.makedirs(os.path.dirname(recipes_output), exist_ok=True)
        with open(recipes_output, "w") as f:
            json.dump(full_response, f, indent=2)
        
        return jsonify(full_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def setup_api_mode():
    """
    Set up the application in API mode
    """
    global config, vision_service, recipe_service
    
    # Initialize configuration
    config = Config()
    
    # Initialize services
    azure_client = AzureClientService(config)
    vision_service = VisionService(azure_client)
    recipe_service = RecipeService(azure_client)

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description="Fridge Recipe Generator")
    parser.add_argument("--mode", choices=["cli", "api"], default="cli", help="Run mode (cli or api)")
    parser.add_argument("--action", choices=["analyze", "recipes", "both"], default="both", help="Action to perform in CLI mode")
    parser.add_argument("--image", help="Image filename for analysis (in input directory)")
    parser.add_argument("--recipes", type=int, default=5, help="Number of recipes to generate")
    parser.add_argument("--host", default="127.0.0.1", help="Host for API server")
    parser.add_argument("--port", type=int, default=5000, help="Port for API server")
    
    args = parser.parse_args()
    
    if args.mode == "api":
        # API mode
        setup_api_mode()
        print(f"Starting Flask API server on {args.host}:{args.port}")
        app.run(host=args.host, port=args.port, debug=False)
    else:
        # CLI mode
        config = Config()
        azure_client = AzureClientService(config)
        vision_service = VisionService(azure_client)
        recipe_service = RecipeService(azure_client)
        
        cli = CLIProcessor(config, vision_service, recipe_service)
        
        if args.action in ["analyze", "both"]:
            if not args.image:
                print("Error: Image filename required for analysis")
                return
            cli.analyze_image(args.image)
        
        if args.action in ["recipes", "both"]:
            cli.generate_recipes(args.image, args.recipes)

if __name__ == "__main__":
    main()