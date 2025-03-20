"""
Vision Service - Service for analyzing fridge/food images
"""

import json
import os
from utils.image_utils import encode_image
from prompts.vision_prompt import get_vision_system_prompt

class VisionService:
    """Service for analyzing food/fridge images using Azure OpenAI Vision API"""
    
    def __init__(self, azure_client):
        """
        Initialize the Vision Service
        
        Args:
            azure_client: An initialized AzureClientService object
        """
        self.client = azure_client.get_client()
        self.model_name = azure_client.get_model_name()
    
    def analyze_image(self, image_path):
        """
        Analyze the image using Azure OpenAI Vision API
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Dictionary containing the analysis results
            
        Raises:
            Exception: If the API call fails or parsing fails
        """
        try:
            base64_image = encode_image(image_path)
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": get_vision_system_prompt()},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Please identify all the food ingredients and items in this refrigerator image. List as many as you can see and be specific about each item."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }
                ],
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Error analyzing image: {str(e)}")
    
    def save_analysis(self, analysis_data, output_path):
        """
        Save the analysis result to a JSON file
        
        Args:
            analysis_data: The complete analysis data to save
            output_path: Path to save the JSON output
            
        Returns:
            Path to the saved file
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as json_file:
            json.dump(analysis_data, json_file, indent=2)
        
        return output_path
    
    def get_ingredients_summary(self, analysis_result):
        """
        Generate a summary of the ingredients from the analysis
        
        Args:
            analysis_result: The analysis result from analyze_image
            
        Returns:
            Dictionary with summary statistics
        """
        if "ingredients" not in analysis_result:
            return {
                "total_count": 0,
                "categories": 0,
                "by_category": {}
            }
        
        categories = analysis_result["ingredients"]
        by_category = {category: len(items) for category, items in categories.items()}
        total_count = sum(by_category.values())
        
        return {
            "total_count": total_count,
            "categories": len(categories),
            "by_category": by_category
        }