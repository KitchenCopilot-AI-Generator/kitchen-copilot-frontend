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
    Get ingredients for the specified request ID
    
    Returns:
        Ingredients data
    """
    try:
        # Get request ID (folder name) from query parameter
        request_id = request.args.get('request_id')
        
        if not request_id:
            return jsonify({
                "error": "Missing required parameter: request_id. Please specify a request_id to retrieve ingredients."
            }), 400
        
        try:
            # Get paths using the request_id
            paths = config.get_file_paths(request_id=request_id)
            ingredients_file = paths["vision_output"]
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        
        # Check if file exists
        if not os.path.exists(ingredients_file):
            return jsonify({
                "error": f"No ingredients file found for request_id: {request_id}"
            }), 404
        
        # Load and return the ingredients
        with open(ingredients_file, "r") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/recipes', methods=['GET'])
def get_recipes():
    """
    Get recipes for the specified request ID
    
    Returns:
        Recipes data
    """
    try:
        # Get request ID (folder name) from query parameter
        request_id = request.args.get('request_id')
        
        if not request_id:
            return jsonify({
                "error": "Missing required parameter: request_id. Please specify a request_id to retrieve recipes."
            }), 400
        
        try:
            # Get paths using the request_id
            paths = config.get_file_paths(request_id=request_id)
            recipes_file = paths["recipes_output"]
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        
        # Check if file exists
        if not os.path.exists(recipes_file):
            return jsonify({
                "error": f"No recipes file found for request_id: {request_id}"
            }), 404
        
        # Load and return the recipes
        with open(recipes_file, "r") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-recipes', methods=['POST'])
def generate_recipes():
    """
    Generate recipe suggestions based on available ingredients for the specified request ID
    
    Returns:
        Generated recipes
    """
    try:
        # Parse request data
        data = request.get_json() or {}
        num_recipes = data.get('num_recipes', 5)
        request_id = data.get('request_id')
        
        if not request_id:
            return jsonify({
                "error": "Missing required parameter: request_id. Please specify a request_id to generate recipes."
            }), 400
        
        try:
            # Get paths using the request_id
            paths = config.get_file_paths(request_id=request_id)
            ingredients_file = paths["vision_output"]
            recipes_output = paths["recipes_output"]
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        
        # Check if file exists
        if not os.path.exists(ingredients_file):
            return jsonify({
                "error": f"No ingredients file found for request_id: {request_id}"
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
        
        # Save the full response
        os.makedirs(os.path.dirname(recipes_output), exist_ok=True)
        with open(recipes_output, "w") as f:
            json.dump(full_response, f, indent=2)
        
        return jsonify(full_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500