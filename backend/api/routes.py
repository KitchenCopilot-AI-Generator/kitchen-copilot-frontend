"""
API Routes - Flask routes for the Kitchen Copilot application

This module preserves the exact API interface expected by the frontend,
while using Flask instead of FastAPI for implementation.
"""

import os
import json
import glob
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
            
        # Get file paths with the new naming convention
        paths = config.get_file_paths(file.filename)
        
        # Save the uploaded file directly to the results directory
        os.makedirs(os.path.dirname(paths["request_image"]), exist_ok=True)
        file.save(paths["request_image"])
        
        # Process synchronously
        result = vision_service.analyze_image(paths["request_image"])
        vision_service.save_analysis(result, paths["vision_output"])
        
        # Get a summary
        summary = vision_service.get_ingredients_summary(result)
        
        # Include request_id (which is the folder name)
        request_id = paths["request_id"]
        # Get just the filename, not the full path
        image_filename = os.path.basename(paths["request_image"])
        
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
            
            # Find the ingredients file that matches the pattern
            ingredients_files = glob.glob(os.path.join(request_dir, "ingredients_*.json"))
            
            if not ingredients_files:
                return jsonify({
                    "error": "No ingredients analysis found for the specified request ID."
                }), 404
                
            # Use the first matching file (should only be one)
            ingredients_file = ingredients_files[0]
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
            
            # Find the recipes file that matches the pattern
            recipes_files = glob.glob(os.path.join(request_dir, "recipes_*.json"))
            
            if not recipes_files:
                return jsonify({
                    "error": "No recipes found for the specified request ID."
                }), 404
                
            # Use the first matching file (should only be one)
            recipes_file = recipes_files[0]
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
            
            # Find the ingredients file that matches the pattern
            ingredients_files = glob.glob(os.path.join(request_dir, "ingredients_*.json"))
            
            if not ingredients_files:
                return jsonify({
                    "error": "No ingredients analysis found for the specified request ID."
                }), 404
                
            # Use the first matching file (should only be one)
            ingredients_file = ingredients_files[0]
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
            
            # Create a recipes filename based on the ingredients filename pattern
            ingredients_basename = os.path.basename(ingredients_file)
            timestamp_id_part = ingredients_basename.replace("ingredients_", "").replace(".json", "")
            recipes_output = os.path.join(request_dir, f"recipes_{timestamp_id_part}.json")
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