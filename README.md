# Kitchen Copilot

An application that analyses your refrigerator contents through images and suggests recipes based on available ingredients.

![Kitchen Copilot Image Upload Interface](assets/ImageUpload.png)


## Features
- **Image Analysis**: Upload a photo of your fridge or food items to identify ingredients
- **Recipe Generation**: Get customized recipe suggestions based on identified ingredients
- **Dietary Restrictions**: Specify allergies or dietary preferences for personalized recipes
- **Cloud Storage**: All data is stored in Azure Blob Storage for reliability and scalability
- **Modern Frontend**: Interactive web interface for easy ingredient analysis and recipe browsing

## Requirements
- Python 3.8+
- Azure OpenAI API access with a deployed GPT-4 Vision model
- Node.js 18+ (for frontend)

## Setup

### Backend Setup
1. Clone the repository
2. Navigate to the project root
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the `.env.example` file to `.env` and add your configuration details:
   ```
   # Azure OpenAI API settings
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
   API_VERSION=2023-12-01-preview
   MODEL_NAME=your-gpt4-vision-deployed-model-name

   # Azure Blob Storage settings
   AZURE_STORAGE_CONNECTION_STRING=your_azure_storage_connection_string
   AZURE_STORAGE_CONTAINER=container01
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd kitchen-copilot-frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env.local` file with:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:5000
   ```

## Usage

### Running the Full Application
1. Navigate to the backend directory:
   ```bash
   cd kitchen-copilot-backend

2. Start the backend API server:
   ```bash
   python main.py --host 0.0.0.0 --port 5000
   ```

3. In a separate terminal, start the frontend development server:
   ```bash
   cd kitchen-copilot-frontend
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser to access the application

#### API Endpoints
- `POST /analyze-image`: Upload and analyze a fridge image
- `GET /ingredients`: Get ingredients from the most recent analysis
- `POST /generate-recipes`: Generate recipe suggestions based on available ingredients and dietary restrictions
- `GET /recipes`: Get previously generated recipes

## Demo Mode

For development and testing purposes, you can visit [http://localhost:3000/demo](http://localhost:3000/demo) to see the frontend with pre-filled sample data, without needing to connect to the backend API.

## Using Postman with the API

You can easily test the API endpoints using Postman. Here's how to make requests to each endpoint:

### 1. Analyze Image Endpoint (POST /analyze-image)

1. Open Postman and create a new POST request to `http://localhost:5000/analyze-image`
2. In the request builder, select the "Body" tab
3. Select "form-data"
4. Add a key named "file" and change the type from "Text" to "File"
5. Click "Select Files" and choose an image of your refrigerator
6. Click "Send" to submit the request

Example response:
```json
{
  "status": "complete",
  "result": {
    "ingredients": {
      "Dairy": ["milk", "cheddar cheese", "yogurt"],
      "Produce": ["carrots", "lettuce", "tomatoes", "onions"],
      "Proteins": ["chicken breast", "eggs"],
      "Condiments": ["ketchup", "mayonnaise", "mustard"]
    }
  },
  "summary": {
    "total_count": 10,
    "categories": 4,
    "by_category": {
      "Dairy": 3,
      "Produce": 4,
      "Proteins": 2,
      "Condiments": 3
    }
  },
  "image_filename": "image_1743074276_5115e30c.jpg",
  "request_id": "fridge_1743074276_5115e30c"
}
```

### 2. Get Ingredients Endpoint (GET /ingredients)

1. Create a new GET request to `http://localhost:5000/ingredients`
2. Optionally, you can add a query parameter named "request_id" if you want to get ingredients from a specific analysis
   - The request_id is returned in the analyze-image response (e.g., "fridge_630cee49")
3. Click "Send" to submit the request

![Ingredients Analysis Display](assets/Ingredients.png)

Example response:
```json
{
  "ingredients": {
    "Dairy": ["milk", "cheddar cheese", "yogurt"],
    "Produce": ["carrots", "lettuce", "tomatoes", "onions"],
    "Proteins": ["chicken breast", "eggs"],
    "Condiments": ["ketchup", "mayonnaise", "mustard"]
  }
}
```

### 3. Get Recipes Endpoint (GET /recipes)

1. Create a new GET request to `http://localhost:5000/recipes`
2. Optionally, you can add a query parameter named "request_id" if you want to get recipes from a specific analysis
   - The request_id is returned in the analyze-image response (e.g., "fridge_630cee49")
3. Click "Send" to submit the request

![Recipe Suggestions Display](assets/Recipes.png)

Example response:
```json
{
  "items": [
    {
      "name": "Quick Chicken Salad",
      "total_ingredients": ["chicken breast", "lettuce", "tomatoes", "onions", "mayonnaise", "salt", "pepper"],
      "available_ingredients": ["chicken breast", "lettuce", "tomatoes", "onions", "mayonnaise"],
      "missing_ingredients": ["salt", "pepper"],
      "completeness_score": 71,
      "instructions": ["Step 1...", "Step 2..."],
      "cooking_time": "15 minutes",
      "difficulty": "Easy"
    }
  ],
  "analysis": [
    {
      "recipe_name": "Quick Chicken Salad",
      "completeness": 71,
      "available_count": 5,
      "missing_count": 2,
      "total_ingredients": 7,
      "cooking_time": "15 minutes",
      "difficulty": "Easy"
    }
  ],
  "ingredient_count": 10,
  "dietary_restrictions": []
}
```

### 4. Generate Recipes Endpoint (POST /generate-recipes)

1. Create a new POST request to `http://localhost:5000/generate-recipes`
2. In the request builder, select the "Body" tab
3. Select "raw" and choose "JSON" from the dropdown
4. Enter the request body:
   ```json
   {
     "num_recipes": 5,
     "request_id": "fridge_1743074276_5115e30c",
     "dietary_restrictions": [
       {
         "id": "vegetarian",
         "name": "Vegetarian"
       },
       {
         "id": "nuts",
         "name": "Nuts"
       }
     ]
   }
   ```
   - Replace "fridge_1743074276_5115e30c" with the actual request_id from your analyze-image response
   - You can omit the request_id to use the most recent analysis
   - The "dietary_restrictions" field is optional and can include multiple restrictions
5. Click "Send" to submit the request

Example response:
```json
{
  "items": [
    {
      "name": "Vegetarian Mediterranean Wrap",
      "total_ingredients": ["tortillas", "lettuce", "tomatoes", "onions", "mayonnaise", "yogurt", "salt", "pepper"],
      "available_ingredients": ["tortillas", "lettuce", "tomatoes", "onions", "mayonnaise", "yogurt"],
      "missing_ingredients": ["salt", "pepper"],
      "completeness_score": 75,
      "instructions": ["Step 1...", "Step 2..."],
      "cooking_time": "15 minutes",
      "difficulty": "Easy"
    }
  ],
  "analysis": [
    {
      "recipe_name": "Vegetarian Mediterranean Wrap",
      "completeness": 75,
      "available_count": 6,
      "missing_count": 2,
      "total_ingredients": 8,
      "cooking_time": "15 minutes",
      "difficulty": "Easy"
    }
  ],
  "ingredient_count": 10,
  "dietary_restrictions": [
    {
      "id": "vegetarian",
      "name": "Vegetarian"
    },
    {
      "id": "nuts",
      "name": "Nuts"
    }
  ]
}
```

## Dietary Restrictions Feature

The Kitchen Copilot app allows users to specify dietary restrictions for personalized recipe suggestions:

![Allergy & Dietary Display](assets/Allergy.png)

### Available Restrictions

#### Allergies & Intolerances
- Nuts (peanuts, tree nuts)
- Dairy (milk, cheese, yogurt)
- Gluten (wheat, barley, rye)
- Shellfish (shrimp, crab, lobster)
- Eggs
- Soy
- Fish
- Sesame

#### Diets
- Vegetarian (no meat or fish)
- Vegan (no animal products)
- Keto (low carb, high fat)
- Paleo (no processed foods, grains, dairy)
- Pescatarian (vegetarian plus fish)

## Project Structure
```
kitchen-copilot/
├── .env                                                  # Environment variables
├── kitchen-copilot-backend/                              # Backend directory
│   ├── main.py                                           # Main entry point
│   ├── config.py                                         # Configuration and environment loading
│   ├── utils/                                            # Utility functions
│   │   └── image_utils.py                                # Image handling utilities
│   ├── services/                                         # Core services
│   │   ├── azure_openai_client.py                        # Azure OpenAI API client
│   │   ├── azure_blob_service.py                         # Azure Blob Storage service
│   │   ├── vision_service.py                             # Image analysis service
│   │   └── recipe_service.py                             # Recipe generation service
│   ├── models/                                           # Data models
│   │   ├── ingredients.py                                # Ingredients data model
│   │   └── recipes.py                                    # Recipes data model
│   ├── prompts/                                          # Prompt templates
│   │   ├── vision_prompt.py                              # Image analysis prompt
│   │   └── recipe_prompt.py                              # Recipe generation prompt
│   └── api/                                              # API endpoints
│       └── routes.py                                     # Flask routes
└── kitchen-copilot-frontend/                             # Next.js frontend application
    ├── src/                                              # Frontend source code
    │   ├── app/                                          # Next.js app router pages
    │   ├── components/                                   # React components
    │   │   ├── kitchen/                                  # Kitchen-specific components
    │   │   │   ├── ImageUpload.tsx                       # Image upload component
    │   │   │   ├── IngredientsDisplay.tsx                # Ingredients display component
    │   │   │   ├── DietaryRestrictions.tsx               # Dietary restrictions component
    │   │   │   └── RecipesDisplay.tsx                    # Recipes display component
    │   ├── lib/                                          # Utility functions and API client
    │   └── types/                                        # TypeScript type definitions
    ├── public/                                           # Static assets
    └── package.json                                      # Frontend dependencies
```

## Troubleshooting

### API Connection Issues
- Verify that the backend API is running on the correct host and port
- Check that `NEXT_PUBLIC_API_URL` in the frontend's `.env.local` matches the backend URL
- Try accessing the API directly in the browser (e.g., http://localhost:5000/ingredients)