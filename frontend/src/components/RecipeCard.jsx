import React from 'react';
import { FaClock, FaChartLine } from 'react-icons/fa';
import '../styles/RecipeCard.css';

const RecipeCard = ({ recipe, onClick }) => {
  // Function to determine color based on completeness score
  const getCompletenessColor = (score) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'blue';
    if (score >= 40) return 'yellow';
    return 'red';
  };

  // Get the color class for this recipe
  const completenessColor = getCompletenessColor(recipe.completeness_score);

  // Truncate a list of ingredients to n items plus "..." if longer
  const truncateList = (list, n = 3) => {
    if (!list || list.length === 0) return 'None';
    
    if (list.length <= n) return list.join(', ');
    
    return `${list.slice(0, n).join(', ')}...`;
  };

  return (
    <div className="recipe-card" onClick={() => onClick(recipe)}>
      <div className="recipe-header">
        <h3 className="recipe-title">{recipe.name}</h3>
        <span className={`completeness-badge ${completenessColor}`}>
          {recipe.completeness_score}% Complete
        </span>
      </div>
      
      <div className="recipe-meta">
        <span className="recipe-meta-item">
          <FaClock /> {recipe.cooking_time}
        </span>
        <span className="recipe-meta-item">
          <FaChartLine /> {recipe.difficulty}
        </span>
      </div>
      
      <div className="recipe-ingredients">
        <div className="ingredients-column">
          <h4 className="ingredients-title">Available ({recipe.available_ingredients.length})</h4>
          <p className="ingredients-list">{truncateList(recipe.available_ingredients)}</p>
        </div>
        <div className="ingredients-column">
          <h4 className="ingredients-title">Missing ({recipe.missing_ingredients.length})</h4>
          <p className="ingredients-list">{truncateList(recipe.missing_ingredients)}</p>
        </div>
      </div>
      
      <button className="btn btn-primary view-recipe-btn">
        View Recipe Details
      </button>
    </div>
  );
};

export default RecipeCard;