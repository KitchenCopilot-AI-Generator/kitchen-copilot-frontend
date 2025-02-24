#!/usr/bin/env python3
"""
Fridge/Pantry Ingredient Detection Script

This script detects and classifies food ingredients in images using YOLOv8.
It can be used to identify what ingredients you have available in your fridge or pantry.
"""

import os
import sys

# Configuration settings (hardcoded instead of using argparse)
IMAGE_PATH = "./input/fridge.jpg"  # Path to the input image
OUTPUT_PATH = "./results/Y0L0v8-output.jpg"  # Path to save the output image
CONFIDENCE_THRESHOLD = 0.25  # Confidence threshold for detections
MODEL_NAME = "yolov8x"  # Model size: options are 'yolov8n', 'yolov8s', 'yolov8m', 'yolov8l', 'yolov8x'
FOOD_ONLY = True  # Only show food items if True

# Ensure all required packages are installed
required_packages = {
    'numpy': 'numpy',
    'torch': 'torch',
    'cv2': 'opencv-python',
    'PIL': 'pillow',
    'ultralytics': 'ultralytics'
}

missing_packages = []
for package, pip_name in required_packages.items():
    try:
        __import__(package)
    except ImportError:
        missing_packages.append(pip_name)

if missing_packages:
    print(f"Error: Missing required packages: {', '.join(missing_packages)}")
    print("Please install them using pip:")
    print(f"pip install {' '.join(missing_packages)}")
    sys.exit(1)

# Now import after checking
import numpy as np
import cv2
import torch
from ultralytics import YOLO
from PIL import Image


def download_model(model_name):
    """Download the YOLOv8 model if not already downloaded."""
    try:
        print(f"Loading {model_name} model...")
        return YOLO(model_name)
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)


def detect_ingredients(image_path, model, conf_threshold=0.25, food_only=False):
    """
    Detect ingredients in the given image.
    
    Args:
        image_path: Path to the input image
        model: YOLO model to use for detection
        conf_threshold: Confidence threshold for detections
        food_only: If True, only show food-related items
        
    Returns:
        Annotated image and list of detected objects
    """
    # COCO dataset food-related classes
    food_classes = [
        'apple', 'orange', 'banana', 'carrot', 'broccoli', 'hot dog', 'pizza',
        'donut', 'cake', 'sandwich', 'bottle', 'wine glass', 'cup', 'fork', 'knife',
        'spoon', 'bowl', 'fruit', 'vegetable', 'bread', 'cheese', 'egg', 'meat'
    ]
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    try:
        # Load the image
        image = Image.open(image_path)
        
        # Convert PIL image to numpy array for OpenCV
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Run detection
        results = model(image_path, conf=conf_threshold)
        
        # Get detection results
        detected_objects = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls.item())
                cls_name = result.names[cls_id]
                confidence = box.conf.item()
                
                # Skip non-food items if food_only is True
                if food_only and cls_name.lower() not in [c.lower() for c in food_classes]:
                    continue
                    
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # Add to detected objects list
                detected_objects.append({
                    'class': cls_name,
                    'confidence': confidence,
                    'bbox': [x1, y1, x2, y2]
                })
                
                # Draw bounding box
                color = (0, 255, 0)  # Green color for bounding box
                cv2.rectangle(img_cv, (x1, y1), (x2, y2), color, 2)
                
                # Add label with class name and confidence
                label = f"{cls_name}: {confidence:.2f}"
                label_size, baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                y1 = max(y1, label_size[1])
                cv2.rectangle(img_cv, (x1, y1 - label_size[1] - 10), (x1 + label_size[0], y1), color, -1)
                cv2.putText(img_cv, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        return img_cv, detected_objects
        
    except Exception as e:
        print(f"Error during ingredient detection: {e}")
        print("Full error traceback:")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main function."""
    # Check if CUDA is available
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    # Download/load the model
    model = download_model(MODEL_NAME)
    
    # Detect ingredients
    annotated_img, detected_objects = detect_ingredients(
        IMAGE_PATH, model, CONFIDENCE_THRESHOLD, FOOD_ONLY
    )
    
    # Save the annotated image
    cv2.imwrite(OUTPUT_PATH, annotated_img)
    print(f"Annotated image saved to {OUTPUT_PATH}")
    
    # Print the detected objects
    print("\nDetected ingredients:")
    for i, obj in enumerate(detected_objects, 1):
        print(f"{i}. {obj['class']} (Confidence: {obj['confidence']:.2f})")


if __name__ == "__main__":
    main()