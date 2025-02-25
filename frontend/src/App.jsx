import React, { useState } from 'react';
import ImageUpload from './components/ImageUpload';
import IngredientsList from './components/IngredientsList';
import RecipesList from './components/RecipesList';
import { analyzeImage, generateRecipes } from './api/api';
import './index.css';

function App() {
  // State for ingredients, recipes, loading states, and errors
  const [ingredients, setIngredients] = useState(null);
  const [recipes, setRecipes] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGeneratingRecipes, setIsGeneratingRecipes] = useState(false);
  const [ingredientsError, setIngredientsError] = useState(null);
  const [recipesError, setRecipesError] = useState(null);

  // Handle analyze image
  const handleAnalyzeImage = async (imageFile) => {
    try {
      // Reset states
      setIngredients(null);
      setRecipes(null);
      setIngredientsError(null);
      setRecipesError(null);
      
      console.log("Starting image analysis...");
      // Start loading
      setIsAnalyzing(true);
      
      // Analyze image
      const analysisResult = await analyzeImage(imageFile);
      console.log("Analysis completed with result:", analysisResult);
      
      // Set ingredients
      setIngredients(analysisResult);
      console.log("Ingredients state set with:", analysisResult);
      
      console.log("Starting recipe generation...");
      // Generate recipes
      setIsGeneratingRecipes(true);
      const recipesResult = await generateRecipes(5);
      console.log("Recipes generated with result:", recipesResult);
      
      // Set recipes
      setRecipes(recipesResult);
      console.log("Recipes state set with:", recipesResult);
      
    } catch (error) {
      console.error('Error in analyze workflow:', error);
      
      if (!ingredients) {
        setIngredientsError(typeof error === 'string' ? error : 'Failed to analyze image');
      } else {
        setRecipesError(typeof error === 'string' ? error : 'Failed to generate recipes');
      }
    } finally {
      // Stop loading
      console.log("Setting loading states to false");
      setIsAnalyzing(false);
      setIsGeneratingRecipes(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">Fridge Recipe Generator</h1>
        <p className="app-subtitle">Upload a photo of your fridge and get recipe suggestions</p>
      </header>
      
      <main className="container">
        <div className="grid grid-cols-2">
          <div className="section">
            {/* Image Upload Section */}
            <ImageUpload 
              onAnalyzeImage={handleAnalyzeImage} 
              isLoading={isAnalyzing || isGeneratingRecipes} 
            />
            
            {/* Ingredients Section */}
            {(ingredients || isAnalyzing || ingredientsError) && (
              <IngredientsList 
                ingredients={ingredients} 
                isLoading={isAnalyzing} 
                error={ingredientsError}
              />
            )}
          </div>
          
          <div className="section">
            {/* Recipes Section */}
            {(recipes || isGeneratingRecipes || recipesError) && (
              <RecipesList 
                recipes={recipes} 
                isLoading={isGeneratingRecipes} 
                error={recipesError}
              />
            )}
          </div>
        </div>
      </main>
      
      <footer className="footer">
        <div className="container">
          <p>&copy; {new Date().getFullYear()} Fridge Recipe Generator</p>
        </div>
      </footer>
    </div>
  );
}

export default App;