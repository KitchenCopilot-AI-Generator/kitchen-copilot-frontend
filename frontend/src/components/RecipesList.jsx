// src/components/RecipesList.jsx
import React, { useState, useMemo } from 'react';
import { FaBookOpen } from 'react-icons/fa';
import RecipeCard from './RecipeCard';
import RecipeDetails from './RecipeDetails';
import Loader from './Loader';
import '../styles/RecipesList.css';

const RecipesList = ({ recipes, isLoading, error }) => {
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [sortBy, setSortBy] = useState('completeness');
  
  // Sort recipes based on selected criteria
  const sortedRecipes = useMemo(() => {
    // If recipes is null or undefined, return empty array
    if (!recipes) return [];
    
    // Extract recipes array from the structure
    let recipesList = [];
    
    // Handle various nesting possibilities
    if (Array.isArray(recipes)) {
      recipesList = [...recipes];
    } 
    // Handle the deeply nested structure shown in the debug view
    else if (recipes.recipes && recipes.recipes.recipes && Array.isArray(recipes.recipes.recipes)) {
      recipesList = [...recipes.recipes.recipes];
    }
    // Handle one level of nesting
    else if (recipes.recipes && Array.isArray(recipes.recipes)) {
      recipesList = [...recipes.recipes];
    }
    // Log any unexpected structure
    else {
      console.log("Unexpected recipes structure:", recipes);
      return [];
    }
    
    // Sort based on criteria
    switch (sortBy) {
      case 'completeness':
        return recipesList.sort((a, b) => b.completeness_score - a.completeness_score);
      case 'missing':
        return recipesList.sort((a, b) => a.missing_ingredients.length - b.missing_ingredients.length);
      case 'difficulty':
        const difficultyWeight = { 'Easy': 1, 'Medium': 2, 'Hard': 3 };
        return recipesList.sort((a, b) => difficultyWeight[a.difficulty] - difficultyWeight[b.difficulty]);
      default:
        return recipesList;
    }
  }, [recipes, sortBy]);
  
  const handleSortChange = (e) => {
    setSortBy(e.target.value);
  };
  
  const handleRecipeClick = (recipe) => {
    setSelectedRecipe(recipe);
  };
  
  const closeRecipeDetails = () => {
    setSelectedRecipe(null);
  };
  
  if (error) {
    return (
      <div className="recipes-section card">
        <h2 className="section-title">
          <FaBookOpen className="section-icon" /> Recipe Suggestions
        </h2>
        <div className="error-message">
          <p>Error loading recipes: {error}</p>
        </div>
      </div>
    );
  }
  
  if (isLoading) {
    return (
      <div className="recipes-section card">
        <h2 className="section-title">
          <FaBookOpen className="section-icon" /> Recipe Suggestions
        </h2>
        <Loader message="Generating recipe suggestions..." />
      </div>
    );
  }

  // Debug rendering - if there's recipe data but sortedRecipes is empty
  if (recipes && sortedRecipes.length === 0) {
    return (
      <div className="recipes-section card">
        <h2 className="section-title">
          <FaBookOpen className="section-icon" /> Recipe Suggestions (Debug View)
        </h2>
        <div className="debug-data">
          <p>Raw recipes data structure:</p>
          <pre>{JSON.stringify(recipes, null, 2)}</pre>
        </div>
      </div>
    );
  }
  
  if (!sortedRecipes.length) {
    return null;
  }
  
  return (
    <>
      <div className="recipes-section card">
        <h2 className="section-title">
          <FaBookOpen className="section-icon" /> Recipe Suggestions
        </h2>
        
        <div className="recipes-controls">
          <div className="recipes-count">
            Found <strong>{sortedRecipes.length}</strong> recipes
          </div>
          
          <div className="recipes-sort">
            <select 
              value={sortBy} 
              onChange={handleSortChange} 
              className="sort-select"
            >
              <option value="completeness">Sort by Completeness</option>
              <option value="missing">Sort by Fewest Missing</option>
              <option value="difficulty">Sort by Difficulty</option>
            </select>
          </div>
        </div>
        
        <div className="recipes-grid">
          {sortedRecipes.map((recipe, index) => (
            <RecipeCard 
              key={`${recipe.name}-${index}`} 
              recipe={recipe} 
              onClick={handleRecipeClick}
            />
          ))}
        </div>
      </div>
      
      {selectedRecipe && (
        <RecipeDetails recipe={selectedRecipe} onClose={closeRecipeDetails} />
      )}
    </>
  );
};

export default RecipesList;