import React from 'react';
import { FaClock, FaChartLine, FaPercentage, FaTimes } from 'react-icons/fa';
import '../styles/RecipeDetails.css';

const RecipeDetails = ({ recipe, onClose }) => {
  if (!recipe) return null;

  return (
    <div className="recipe-modal-overlay" onClick={onClose}>
      <div className="recipe-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="recipe-modal-header">
          <h2 className="recipe-modal-title">{recipe.name}</h2>
          <button className="recipe-modal-close" onClick={onClose}>
            <FaTimes />
          </button>
        </div>

        <div className="recipe-modal-body">
          <div className="recipe-modal-grid">
            <div className="recipe-modal-main">
              <h3 className="recipe-section-title">Instructions</h3>
              <ol className="recipe-instructions">
                {recipe.instructions.map((instruction, index) => (
                  <li key={index} className="recipe-instruction-step">{instruction}</li>
                ))}
              </ol>
            </div>

            <div className="recipe-modal-sidebar">
              <div className="recipe-details-section">
                <h3 className="recipe-section-title">Details</h3>
                <div className="recipe-detail-item">
                  <FaClock className="recipe-detail-icon" />
                  <span>{recipe.cooking_time}</span>
                </div>
                <div className="recipe-detail-item">
                  <FaChartLine className="recipe-detail-icon" />
                  <span>{recipe.difficulty}</span>
                </div>
                <div className="recipe-detail-item">
                  <FaPercentage className="recipe-detail-icon" />
                  <span>Completeness: <strong>{recipe.completeness_score}%</strong></span>
                </div>
              </div>

              <div className="recipe-ingredients-section">
                <h3 className="recipe-section-title available-title">
                  Available Ingredients
                </h3>
                <ul className="recipe-ingredients-list available-list">
                  {recipe.available_ingredients.map((ingredient, index) => (
                    <li key={`available-${index}`} className="recipe-ingredient-item">
                      {ingredient}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="recipe-ingredients-section">
                <h3 className="recipe-section-title missing-title">
                  Missing Ingredients
                </h3>
                <ul className="recipe-ingredients-list missing-list">
                  {recipe.missing_ingredients.map((ingredient, index) => (
                    <li key={`missing-${index}`} className="recipe-ingredient-item">
                      {ingredient}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecipeDetails;