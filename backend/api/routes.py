"""
API Routes - FastAPI routes for the application
"""

import os
import json
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel

# This will be initialized by main.py
app = FastAPI()

# Store references to services initialized in main.py
vision_service = None
recipe_service = None
config = None

class RecipeRequest(BaseModel):
    """Model for recipe generation request"""
    num_recipes: Optional[int] = 5
    ingredients_file: Optional[str] = None  # If not provided, use latest analysis

async def process_image_async(image_path, output_path):
    """Process image asynchronously"""
    try:
        result = vision_service.analyze_image(image_path)
        vision_service.save_analysis(result, output_path)
        return result
    except Exception as e:
        raise e

@app.post("/analyze-image")
async def analyze_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    async_processing: bool = False
):
    """
    Analyze a fridge/food image and identify ingredients
    
    Args:
        file: Uploaded image file
        async_processing: Whether to process the image asynchronously
        
    Returns:
        Analysis result or processing status
    """
    try:
        # Create a unique filename using timestamp
        file_ext = os.path.splitext(file.filename)[1]
        image_filename = f"fridge_{os.urandom(8).hex()}{file_ext}"
        
        # Get file paths
        paths = config.get_file_paths(image_filename)
        
        # Save the uploaded file directly to the results directory
        with open(paths["request_image"], "wb") as image_file:
            shutil.copyfileobj(file.file, image_file)
        
        if async_processing:
            # Process in background
            background_tasks.add_task(
                process_image_async, 
                paths["request_image"], 
                paths["vision_output"]
            )
            return {
                "status": "processing",
                "message": "Image analysis started in background",
                "image_filename": image_filename
            }
        else:
            # Process synchronously
            result = vision_service.analyze_image(paths["request_image"])
            vision_service.save_analysis(result, paths["vision_output"])
            
            # Get a summary
            summary = vision_service.get_ingredients_summary(result)
            
            return {
                "status": "complete",
                "result": result,
                "summary": summary,
                "image_filename": image_filename
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ingredients")
async def get_ingredients(filename: Optional[str] = None):
    """
    Get ingredients from the most recent analysis or specified file
    
    Args:
        filename: Optional filename to load specific analysis
        
    Returns:
        Ingredients data
    """
    try:
        # Get path to the ingredients file
        if filename:
            ingredients_file = os.path.join(config.results_dir, filename)
        else:
            paths = config.get_file_paths()
            ingredients_file = paths["vision_output"]
        
        # Check if file exists
        if not os.path.exists(ingredients_file):
            raise HTTPException(
                status_code=404, 
                detail="No ingredients analysis found. Please analyze an image first."
            )
        
        # Load and return the ingredients
        with open(ingredients_file, "r") as f:
            return JSONResponse(content=json.load(f))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-recipes")
async def generate_recipes(request: RecipeRequest):
    """
    Generate recipe suggestions based on available ingredients
    
    Args:
        request: Recipe generation request parameters
        
    Returns:
        Generated recipes
    """
    try:
        # Determine ingredients file path
        if request.ingredients_file:
            ingredients_file = os.path.join(config.results_dir, request.ingredients_file)
        else:
            paths = config.get_file_paths()
            ingredients_file = paths["vision_output"]
        
        # Check if file exists
        if not os.path.exists(ingredients_file):
            raise HTTPException(
                status_code=404, 
                detail="No ingredients analysis found. Please analyze an image first."
            )
        
        # Load ingredients
        ingredients = recipe_service.load_ingredients(ingredients_file)
        
        # Generate recipes
        recipes_data = recipe_service.generate_recipes(
            ingredients, 
            num_recipes=request.num_recipes
        )
        
        # Save recipes
        paths = config.get_file_paths()
        recipe_service.save_recipes(recipes_data, paths["recipes_output"])
        
        # Get analysis
        analysis = recipe_service.get_recipes_analysis(recipes_data)
        analysis_dict = analysis.to_dict('records') if analysis is not None else []
        
        return {
            "recipes": recipes_data,
            "analysis": analysis_dict,
            "ingredient_count": len(ingredients)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))