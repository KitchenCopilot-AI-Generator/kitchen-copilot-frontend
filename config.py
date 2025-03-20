"""
Configuration module - Handles environment variables and configuration
"""

import os
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
        self.input_dir = os.getenv("INPUT_DIR", "./input")
        self.results_dir = os.getenv("RESULTS_DIR", "./data/results")
        
        # Ensure directories exist
        os.makedirs(self.input_dir, exist_ok=True)
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
            # Extract the base name without extension for folder naming
            base_name = os.path.splitext(image_filename)[0]
            
            # Create request-specific result directory
            request_dir = os.path.join(self.results_dir, base_name)
            os.makedirs(request_dir, exist_ok=True)
            
            paths = {
                "request_dir": request_dir,
                "vision_output": os.path.join(request_dir, "ingredients.json"),
                "recipes_output": os.path.join(request_dir, "recipes.json"),
                "request_image": os.path.join(request_dir, image_filename)  # Store image in results directory
            }
        else:
            # If no filename is provided, use the most recent request
            # by finding the most recently modified directory in results_dir
            try:
                subdirs = [os.path.join(self.results_dir, d) for d in os.listdir(self.results_dir) 
                        if os.path.isdir(os.path.join(self.results_dir, d))]
                if subdirs:
                    latest_dir = max(subdirs, key=os.path.getmtime)
                    base_image_name = os.path.basename(latest_dir) + ".jpg"  # Assuming jpg extension
                    paths = {
                        "request_dir": latest_dir,
                        "vision_output": os.path.join(latest_dir, "ingredients.json"),
                        "recipes_output": os.path.join(latest_dir, "recipes.json"),
                        "request_image": os.path.join(latest_dir, base_image_name)
                    }
                else:
                    # Fallback to default paths if no subdirectories exist
                    paths = {
                        "vision_output": os.path.join(self.results_dir, "ingredients.json"),
                        "recipes_output": os.path.join(self.results_dir, "recipes.json")
                    }
            except (FileNotFoundError, ValueError):
                # Fallback to default paths if error occurs
                paths = {
                    "vision_output": os.path.join(self.results_dir, "ingredients.json"),
                    "recipes_output": os.path.join(self.results_dir, "recipes.json")
                }
                
        return paths