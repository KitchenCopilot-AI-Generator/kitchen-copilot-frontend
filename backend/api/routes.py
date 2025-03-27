"""
API Routes - Flask routes for the Kitchen Copilot application

This module preserves the exact API interface expected by the frontend,
while using Flask instead of FastAPI for implementation.
"""

from flask import Blueprint, request, jsonify

# Create a Blueprint instead of a Flask app
app = Blueprint('api', __name__)

# Store references to services initialized in main.py
vision_service = None
recipe_service = None
azure_blob_service = None
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
            
        # Get file paths for Azure Blob Storage
        paths = config.get_file_paths(file.filename)
        
        # Read the file into memory
        file_bytes = file.read()
        
        # Upload the image to Azure Blob Storage
        azure_blob_service.upload_file(file_bytes, paths["request_image"])
        
        # Process image from the uploaded bytes
        result = vision_service.analyze_image_bytes(file_bytes)
        
        # Save analysis to Azure Blob Storage
        vision_service.save_analysis(result, paths["vision_output"])
        
        # Get a summary
        summary = vision_service.get_ingredients_summary(result)
        
        # Include request_id and just the image filename (not the full path)
        request_id = paths["request_id"]
        image_filename = paths["request_image"].split('/')[-1]
        
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
            ingredients_blob = paths["vision_output"]
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        
        # Check if blob exists
        if not azure_blob_service.blob_exists(ingredients_blob):
            return jsonify({
                "error": f"No ingredients file found for request_id: {request_id}"
            }), 404
        
        # Load and return the ingredients from Azure Blob Storage
        ingredients_data = azure_blob_service.download_json(ingredients_blob)
        return jsonify(ingredients_data)
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
            recipes_blob = paths["recipes_output"]
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        
        # Check if blob exists
        if not azure_blob_service.blob_exists(recipes_blob):
            return jsonify({
                "error": f"No recipes file found for request_id: {request_id}"
            }), 404
        
        # Load and return the recipes from Azure Blob Storage
        recipes_data = azure_blob_service.download_json(recipes_blob)
        return jsonify(recipes_data)
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
            ingredients_blob = paths["vision_output"]
            recipes_blob = paths["recipes_output"]
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        
        # Check if ingredients blob exists
        if not azure_blob_service.blob_exists(ingredients_blob):
            return jsonify({
                "error": f"No ingredients file found for request_id: {request_id}"
            }), 404
        
        # Load ingredients from Azure Blob Storage
        ingredients = recipe_service.load_ingredients(ingredients_blob)
        
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
        
        # Save the full response to Azure Blob Storage
        recipe_service.save_recipes(full_response, recipes_blob)
        
        return jsonify(full_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500