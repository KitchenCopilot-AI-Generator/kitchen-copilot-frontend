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
        """Get file paths for input and output files"""
        paths = {
            "vision_output": os.path.join(self.results_dir, "ingredients.json"),
            "recipes_output": os.path.join(self.results_dir, "recipes.json")
        }
        
        if image_filename:
            paths["input_image"] = os.path.join(self.input_dir, image_filename)
            
        return paths