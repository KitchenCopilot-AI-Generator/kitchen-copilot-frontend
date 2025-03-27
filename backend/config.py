"""
Configuration module - Handles environment variables and configuration
"""

import os
import time
from dotenv import load_dotenv

class Config:
    """Configuration class that loads and provides access to environment variables"""
    
    def __init__(self):
        """Initialize configuration by loading environment variables"""
        load_dotenv()
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("API_VERSION")
        self.model_name = os.getenv("MODEL_NAME")
        
        # Default paths
        self.results_dir = os.getenv("RESULTS_DIR", "./container")
        
        # Ensure directories exist
        os.makedirs(self.results_dir, exist_ok=True)
    
    def get_azure_config(self):
        """Get Azure OpenAI configuration as a dictionary"""
        return {
            "api_key": self.azure_openai_api_key,
            "api_version": self.api_version,
            "endpoint": self.azure_openai_endpoint,
            "model_name": self.model_name
        }
    
    def get_file_paths(self, image_filename=None):
        """
        Get file paths for input and output files
        
        Args:
            image_filename: Optional image filename to create request-specific paths
            
        Returns:
            Dictionary with paths for input and output files
        """
        if image_filename:
            # Create a timestamp and unique ID for file naming
            timestamp = int(time.time())
            
            # Extract the unique part of the uploaded image filename or generate a new one
            if '_' in image_filename:
                unique_id = image_filename.split('_')[-1].split('.')[0]
            else:
                unique_id = os.urandom(4).hex()
                
            # Create a timestamp-based folder name
            folder_name = f"fridge_{timestamp}_{unique_id}"
            
            # Create request-specific result directory
            request_dir = os.path.join(self.results_dir, folder_name)
            os.makedirs(request_dir, exist_ok=True)
            
            # Create file names with timestamp and unique ID
            image_name = f"image_{timestamp}_{unique_id}{os.path.splitext(image_filename)[1]}"
            ingredients_name = f"ingredients_{timestamp}_{unique_id}.json"
            recipes_name = f"recipes_{timestamp}_{unique_id}.json"
            
            paths = {
                "request_dir": request_dir,
                "vision_output": os.path.join(request_dir, ingredients_name),
                "recipes_output": os.path.join(request_dir, recipes_name),
                "request_image": os.path.join(request_dir, image_name),
                "request_id": folder_name
            }
        else:
            # If no filename is provided, use the most recent request
            # by finding the most recently modified directory in results_dir
            try:
                subdirs = [os.path.join(self.results_dir, d) for d in os.listdir(self.results_dir) 
                        if os.path.isdir(os.path.join(self.results_dir, d))]
                if subdirs:
                    latest_dir = max(subdirs, key=os.path.getmtime)
                    folder_name = os.path.basename(latest_dir)
                    
                    # Find corresponding files in the directory
                    dir_files = os.listdir(latest_dir)
                    image_files = [f for f in dir_files if f.startswith("image_")]
                    ingredients_files = [f for f in dir_files if f.startswith("ingredients_")]
                    recipes_files = [f for f in dir_files if f.startswith("recipes_")]
                    
                    image_file = image_files[0] if image_files else f"image_{folder_name.split('_', 1)[1]}.jpg"
                    ingredients_file = ingredients_files[0] if ingredients_files else f"ingredients_{folder_name.split('_', 1)[1]}.json"
                    recipes_file = recipes_files[0] if recipes_files else f"recipes_{folder_name.split('_', 1)[1]}.json"
                    
                    paths = {
                        "request_dir": latest_dir,
                        "vision_output": os.path.join(latest_dir, ingredients_file),
                        "recipes_output": os.path.join(latest_dir, recipes_file),
                        "request_image": os.path.join(latest_dir, image_file),
                        "request_id": folder_name
                    }
                else:
                    # Fallback to default paths if no subdirectories exist
                    timestamp = int(time.time())
                    unique_id = os.urandom(4).hex()
                    folder_name = f"fridge_{timestamp}_{unique_id}"
                    
                    request_dir = os.path.join(self.results_dir, folder_name)
                    os.makedirs(request_dir, exist_ok=True)
                    
                    paths = {
                        "request_dir": request_dir,
                        "vision_output": os.path.join(request_dir, f"ingredients_{timestamp}_{unique_id}.json"),
                        "recipes_output": os.path.join(request_dir, f"recipes_{timestamp}_{unique_id}.json"),
                        "request_image": os.path.join(request_dir, f"image_{timestamp}_{unique_id}.jpg"),
                        "request_id": folder_name
                    }
            except (FileNotFoundError, ValueError):
                # Fallback to default paths if error occurs
                timestamp = int(time.time())
                unique_id = os.urandom(4).hex()
                folder_name = f"fridge_{timestamp}_{unique_id}"
                
                request_dir = os.path.join(self.results_dir, folder_name)
                os.makedirs(request_dir, exist_ok=True)
                
                paths = {
                    "request_dir": request_dir, 
                    "vision_output": os.path.join(request_dir, f"ingredients_{timestamp}_{unique_id}.json"),
                    "recipes_output": os.path.join(request_dir, f"recipes_{timestamp}_{unique_id}.json"),
                    "request_image": os.path.join(request_dir, f"image_{timestamp}_{unique_id}.jpg"),
                    "request_id": folder_name
                }
                
        return paths