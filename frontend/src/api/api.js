import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: '/api', // This will use the proxy defined in vite.config.js
  timeout: 60000, // 60 seconds timeout for long-running operations
});

// API methods
export const analyzeImage = async (imageFile) => {
  try {
    const formData = new FormData();
    formData.append('file', imageFile);
    formData.append('async_processing', false);

    console.log("Sending image analysis request...");
    const response = await api.post('/analyze-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    console.log("Raw API response from analyze-image:", response.data);
    return response.data;
  } catch (error) {
    console.error('Error analyzing image:', error);
    throw error.response?.data || error.message || 'Failed to analyze image';
  }
};

export const getIngredients = async (filename = null) => {
  try {
    const params = filename ? { filename } : {};
    const response = await api.get('/ingredients', { params });
    return response.data;
  } catch (error) {
    console.error('Error getting ingredients:', error);
    throw error.response?.data || error.message || 'Failed to get ingredients';
  }
};

export const generateRecipes = async (numRecipes = 5, ingredientsFile = null) => {
  try {
    console.log("Sending generate recipes request...");
    const response = await api.post('/generate-recipes', {
      num_recipes: numRecipes,
      ingredients_file: ingredientsFile,
    });
    console.log("Raw API response from generate-recipes:", response.data);
    return response.data;
  } catch (error) {
    console.error('Error generating recipes:', error);
    throw error.response?.data || error.message || 'Failed to generate recipes';
  }
};

export default {
  analyzeImage,
  getIngredients,
  generateRecipes,
};