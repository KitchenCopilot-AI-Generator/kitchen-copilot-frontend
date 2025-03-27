import argparse
from flask import Flask

# Import services and config
from config import Config
from services.azure_client import AzureClientService
from services.azure_blob_service import AzureBlobService
from services.vision_service import VisionService
from services.recipe_service import RecipeService

from flask_cors import CORS

import sys
sys.dont_write_bytecode = True

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

# Global services
config = None
azure_client = None
azure_blob_service = None
vision_service = None
recipe_service = None

def setup_services():
    """
    Set up the application services
    """
    global config, azure_client, azure_blob_service, vision_service, recipe_service
    
    # Initialize configuration
    config = Config()
    
    # Initialize services
    azure_client = AzureClientService(config)
    
    # Initialize Azure Blob Storage service
    storage_config = config.get_azure_storage_config()
    azure_blob_service = AzureBlobService(
        connection_string=storage_config["connection_string"],
        container_name=storage_config["container_name"]
    )
    
    # Initialize vision and recipe services with blob storage
    vision_service = VisionService(azure_client, azure_blob_service)
    recipe_service = RecipeService(azure_client, azure_blob_service)
    
    # Import routes after Flask app is initialized
    from api.routes import app as routes_blueprint
    
    # Register blueprint with the main Flask app
    app.register_blueprint(routes_blueprint)
    
    # Provide services to routes module
    import api.routes as routes
    routes.vision_service = vision_service
    routes.recipe_service = recipe_service
    routes.azure_blob_service = azure_blob_service
    routes.config = config

def main():
    """Main entry point for the application"""
    parser = argparse.ArgumentParser(description="Kitchen Copilot API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host for API server")
    parser.add_argument("--port", type=int, default=5000, help="Port for API server")
    
    args = parser.parse_args()
    
    # Setup services
    setup_services()
    
    print(f"Starting Kitchen Copilot API server on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False)

if __name__ == "__main__":
    main()