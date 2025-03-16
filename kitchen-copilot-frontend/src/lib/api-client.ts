import axios from 'axios';
import { IngredientsResponse, RecipesResponse } from '@/types';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function analyzeImage(file: File): Promise<IngredientsResponse> {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post('/analyze-image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
}

export async function getIngredients(requestId?: string): Promise<IngredientsResponse> {
  const params = requestId ? { request_id: requestId } : {};
  const response = await apiClient.get('/ingredients', { params });
  return response.data;
}

export async function generateRecipes(
  requestId?: string, 
  numRecipes: number = 5
): Promise<RecipesResponse> {
  const response = await apiClient.post('/generate-recipes', {
    request_id: requestId,
    num_recipes: numRecipes,
  });
  
  return response.data;
}

export async function getRecipes(requestId?: string): Promise<RecipesResponse> {
  const params = requestId ? { request_id: requestId } : {};
  const response = await apiClient.get('/recipes', { params });
  return response.data;
}