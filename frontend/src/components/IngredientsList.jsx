import React from 'react';
import { FaCarrot } from 'react-icons/fa';
import Loader from './Loader';
import '../styles/IngredientsList.css';

const IngredientsList = ({ ingredients, isLoading, error }) => {
  // Fixed category colors mapping with all possible categories
  const categoryColors = {
    'Dairy': 'blue',
    'Produce': 'green',
    'Proteins': 'red',
    'Grains': 'orange',
    'Condiments': 'yellow',
    'Beverages': 'purple',
    'Snacks': 'pink',
    'Frozen': 'indigo',
    'Canned': 'teal',
    'Other': 'gray'
  };

  // Calculate total ingredients and categories
  const calculateSummary = () => {
    if (!ingredients) return { total: 0, categories: 0 };
    
    // Get normalized ingredients structure
    const ingredientsObj = getNormalizedIngredients();
    if (!ingredientsObj) return { total: 0, categories: 0 };
    
    // Get valid categories (those that have array values with at least 1 item)
    const nonEmptyCategories = Object.keys(ingredientsObj).filter(cat => 
      Array.isArray(ingredientsObj[cat]) && ingredientsObj[cat].length > 0
    );
    
    // Count total items across all categories
    const total = nonEmptyCategories.reduce((sum, cat) => {
      return sum + ingredientsObj[cat].length;
    }, 0);
    
    return { total, categories: nonEmptyCategories.length };
  };

  // Normalize ingredients structure for display
  const getNormalizedIngredients = () => {
    if (!ingredients) return null;
    
    // The specific structure we see in the debug view
    if (ingredients.result && ingredients.result.ingredients) {
      return ingredients.result.ingredients;
    }
    
    // Try other common structures
    if (ingredients.ingredients) {
      return ingredients.ingredients;
    }
    
    // If ingredients is directly the right format
    if (typeof ingredients === 'object' && !Array.isArray(ingredients)) {
      // Check if it has keys that look like categories - include ALL possible categories
      const keys = Object.keys(ingredients);
      const commonCategories = [
        'Dairy', 'Produce', 'Proteins', 'Grains', 'Condiments',
        'Beverages', 'Snacks', 'Frozen', 'Canned', 'Other'
      ];
      const hasCategories = keys.some(key => commonCategories.includes(key));
      
      if (hasCategories) {
        // Before returning, ensure all category values are arrays
        const normalizedIngredients = {};
        keys.forEach(key => {
          // Process all keys, not just the common ones
          // If it's a string, try to parse it (might be JSON)
          if (typeof ingredients[key] === 'string') {
            try {
              normalizedIngredients[key] = JSON.parse(ingredients[key]);
            } catch (e) {
              // If parsing fails, make it an empty array
              normalizedIngredients[key] = [];
            }
          } 
          // If it's already an array, use it
          else if (Array.isArray(ingredients[key])) {
            normalizedIngredients[key] = ingredients[key];
          } 
          // Otherwise, create an empty array
          else {
            normalizedIngredients[key] = [];
          }
        });
        
        return normalizedIngredients;
      }
    }
    
    console.log("Couldn't normalize ingredients:", ingredients);
    return null;
  };

  const { total, categories } = calculateSummary();

  // Debug rendering - if there's ingredients data but not in the expected format
  if (ingredients && !getNormalizedIngredients()) {
    return (
      <div className="ingredients-section card">
        <h2 className="section-title">
          <FaCarrot className="section-icon" /> Detected Ingredients (Debug View)
        </h2>
        <div className="debug-data">
          <p>Raw ingredients data structure:</p>
          <pre>{JSON.stringify(ingredients, null, 2)}</pre>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ingredients-section card">
        <h2 className="section-title">
          <FaCarrot className="section-icon" /> Detected Ingredients
        </h2>
        <div className="error-message">
          <p>Error loading ingredients: {error}</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="ingredients-section card">
        <h2 className="section-title">
          <FaCarrot className="section-icon" /> Detected Ingredients
        </h2>
        <Loader message="Analyzing your fridge contents..." />
      </div>
    );
  }

  // If no ingredients data
  const normalizedIngredients = getNormalizedIngredients();
  if (!normalizedIngredients) {
    return null;
  }

  // Sort categories in a specific order
  const categoryOrder = [
    'Produce', 'Proteins', 'Dairy', 'Grains', 'Condiments',
    'Beverages', 'Snacks', 'Frozen', 'Canned', 'Other'
  ];
  
  // Get sorted categories (only including those with non-empty arrays)
  const sortedCategories = Object.keys(normalizedIngredients)
    .filter(category => 
      Array.isArray(normalizedIngredients[category]) && 
      normalizedIngredients[category].length > 0
    )
    .sort((a, b) => {
      return categoryOrder.indexOf(a) - categoryOrder.indexOf(b);
    });

  return (
    <div className="ingredients-section card">
      <h2 className="section-title">
        <FaCarrot className="section-icon" /> Detected Ingredients
      </h2>

      <div className="ingredients-summary">
        <p>Found <strong>{total}</strong> ingredients in <strong>{categories}</strong> categories</p>
      </div>

      <div className="ingredients-categories">
        {sortedCategories.map((category) => {
          // We've already filtered to only include array values
          const items = normalizedIngredients[category];
          
          if (items.length === 0) return null; // Skip empty categories
          
          return (
            <div key={category} className="ingredient-category">
              <h3 className={`category-title color-${categoryColors[category] || 'gray'}`}>
                {category} <span className="category-count">({items.length})</span>
              </h3>
              <div className="ingredient-tags">
                {items.map((item, index) => (
                  <span 
                    key={`${category}-${index}`} 
                    className={`ingredient-tag ${categoryColors[category] || 'gray'}`}
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default IngredientsList;