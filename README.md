# Kitchen Copilot

An AI-powered kitchen assistant that helps you cook by scanning your pantry, suggesting recipes, and providing real-time cooking guidance.

## 🌟 Features
- **Pantry Scanner**: Computer vision system to detect and track ingredients
- **Recipe Generator**: Smart recipe suggestions based on available ingredients
- **Cooking Coach**: Real-time cooking guidance and technique correction
- **Inventory Management**: Track ingredient freshness and expiration dates

## 🏗️ Project Structure
```
smart-kitchen-assistant/
├── .github/
│   ├── workflows/
│   │   ├── tests.ymlx
│   │   └── lint.yml
├── src/
│   ├── pantry_scanner/
│   │   ├── __init__.py
│   │   ├── detector.py        # Object detection models
│   │   ├── inventory.py       # Inventory management
│   │   └── utils.py          # Scanner utilities
│   ├── recipe_generator/
│   │   ├── __init__.py
│   │   ├── generator.py      # Recipe generation logic
│   │   ├── matcher.py        # Ingredient matching
│   │   └── database.py       # Recipe database interactions
│   ├── cooking_coach/
│   │   ├── __init__.py
│   │   ├── monitor.py        # Real-time monitoring
│   │   ├── guidance.py       # Cooking instructions
│   │   └── analysis.py       # Technique analysis
│   └── common/
│       ├── __init__.py
│       ├── config.py         # Configuration management
│       ├── models.py         # Shared data models
│       └── utils.py          # Common utilities
├── tests/
│   ├── test_pantry_scanner.py
│   ├── test_recipe_generator.py
│   └── test_cooking_coach.py
├── api/
│   ├── __init__.py
│   ├── routes.py            # API endpoints
│   └── schemas.py           # API schemas
├── web/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page layouts
│   │   └── utils/          # Frontend utilities
│   └── public/
├── docs/
│   ├── api.md              # API documentation
│   ├── setup.md            # Setup instructions
│   └── architecture.md     # System architecture
├── scripts/
│   ├── setup.sh            # Setup script
│   └── train.py            # Model training
├── .gitignore
├── requirements.txt
├── setup.py
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- OpenCV
- PyTorch
- FastAPI
- React 18+
- Node.js 16+

### Installation
1. Clone the repository:
```bash
git clone https://github.com/ghchen99/kitchen-copilot.git
cd kitchen-copilot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
cd web && npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configurations
```

4. Run the application:
```bash
# Backend
uvicorn api.main:app --reload

# Frontend
cd web && npm start
```

## 📝 API Documentation

### Pantry Scanner
```python
@app.post("/api/v1/pantry/scan")
async def scan_pantry(image: UploadFile) -> PantryContents:
    """
    Scan pantry contents from an image
    """
```

### Recipe Generator
```python
@app.post("/api/v1/recipes/suggest")
async def suggest_recipes(
    ingredients: List[Ingredient],
    preferences: CookingPreferences
) -> List[Recipe]:
    """
    Generate recipe suggestions based on available ingredients
    """
```

### Cooking Coach
```python
@app.websocket("/api/v1/cooking/monitor")
async def monitor_cooking(websocket: WebSocket):
    """
    Real-time cooking monitoring and guidance
    """
```

## 🤝 Contributing
We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments
- OpenAI for function calling capabilities
- YOLO for object detection
- FastAPI for the web framework
- React for the frontend framework
