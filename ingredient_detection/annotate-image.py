import cv2
import numpy as np
import json
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import random

# Function to generate random colors for each bounding box
def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# Load your image
image_path = "input/fridge.jpg"
image = cv2.imread(image_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB for display

# Image dimensions
h, w, _ = image.shape

# Load detection results
with open("results/gpt-vision-output.json", 'r') as file:
    detection_results = json.load(file)

# Create a PIL Image for drawing
pil_image = Image.fromarray(image)
draw = ImageDraw.Draw(pil_image)

# Try to load a font, use default if not available
try:
    font = ImageFont.truetype("arial.ttf", 16)
except IOError:
    font = ImageFont.load_default()

# Draw bounding boxes and labels
for obj in detection_results["objects"]:
    # Get bounding box coordinates
    x1, y1, x2, y2 = obj["bounding_box"]
    
    # Convert normalized coordinates to pixel values
    x1, y1, x2, y2 = int(x1 * w), int(y1 * h), int(x2 * w), int(y2 * h)
    
    # Generate random color
    color = random_color()
    
    # Draw bounding box
    draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
    
    # Prepare label text
    label = f"{obj['label']} ({obj['confidence']:.2f})"
    
    # Draw label background
    text_width, text_height = draw.textbbox((0, 0), label, font=font)[2:4]
    draw.rectangle([x1, y1 - text_height - 5, x1 + text_width, y1], fill=color)
    
    # Draw label text
    draw.text((x1, y1 - text_height - 5), label, fill="white", font=font)

# Convert back to numpy for display
result_image = np.array(pil_image)

# Save the result
plt.figure(figsize=(12, 10))
plt.imshow(result_image)
plt.axis('off')
plt.tight_layout()
plt.savefig("results/gpt-vision-output.jpg", bbox_inches='tight', pad_inches=0)
plt.show()