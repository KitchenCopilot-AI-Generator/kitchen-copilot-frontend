"""
Image Utilities - Functions for handling images
"""

import base64
import os

def encode_image(image_path):
    """
    Encode an image to base64 string
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded string of the image
    
    Raises:
        FileNotFoundError: If the image file doesn't exist
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")
        
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')