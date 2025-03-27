"""
API Routes - Flask routes for the Kitchen Copilot application

This module preserves the exact API interface expected by the frontend,
while using Flask instead of FastAPI for implementation.
"""

import os
import json
from flask import Blueprint, request, jsonify

# Create a Blueprint instead of a Flask app
app = Blueprint('api', __name__)

# Store references to services initialized in main.py
vision_service = None
recipe_service = None
config = None

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
            
        # Create a unique filename using timestamp
        file_ext = os.path.splitext(file.filename)[1]
        image_filename = f"fridge_{os.urandom(8).hex()}{file_ext}"
        
        # Get file paths
        paths = config.get_file_paths(image_filename)
        
        # Save the uploaded file directly to the results directory
        os.makedirs(os.path.dirname(paths["request_image"]), exist_ok=True)
        file.save(paths["request_image"])
        
        # Process synchronously
        result = vision_service.analyze_image(paths["request_image"])
        vision_service.save_analysis(result, paths["vision_output"])
        
        # Get a summary
        summary = vision_service.get_ingredients_summary(result)
        
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