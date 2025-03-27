"""
Image Utilities - Functions for handling images
"""

import base64
import os
import glob

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

def find_image_in_folder(folder_path):
    """
    Find the image file in a given folder that follows the naming pattern
    
    Args:
        folder_path: Path to the folder containing the image
        
    Returns:
        Path to the image file or None if not found
    """
    image_files = glob.glob(os.path.join(folder_path, "image_*.*"))
    return image_files[0] if image_files else None