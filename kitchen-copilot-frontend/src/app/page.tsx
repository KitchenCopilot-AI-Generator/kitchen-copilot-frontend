'use client';

import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { ImageUpload } from '@/components/kitchen/ImageUpload';
import { IngredientsDisplay } from '@/components/kitchen/IngredientsDisplay';
import { RecipesDisplay } from '@/components/kitchen/RecipesDisplay';
import { generateRecipes } from '@/lib/api-client';
import { IngredientsResponse, RecipesResponse } from '@/types';
import { toast } from 'sonner';
import { Toaster } from 'sonner';

export default function Home() {
  const [activeTab, setActiveTab] = useState('upload');
  const [ingredientsData, setIngredientsData] = useState<IngredientsResponse | null>(null);
  const [recipesData, setRecipesData] = useState<RecipesResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleAnalysisComplete = (result: IngredientsResponse) => {
    setIngredientsData(result);
    setActiveTab('ingredients');
  };

  const handleUploadStart = () => {
    // Reset everything when starting a new upload
    setIngredientsData(null);
    setRecipesData(null);
  };

  const handleGenerateRecipes = async () => {
    if (!ingredientsData?.request_id) {
      toast.error('No ingredients analysis found');
      return;
    }

    try {
      setLoading(true);
      const recipes = await generateRecipes(ingredientsData.request_id, 5);
      setRecipesData(recipes);
      setActiveTab('recipes');
      toast.success('Recipes generated successfully!');
    } catch (error) {
      toast.error('Failed to generate recipes');
      console.error('Recipe generation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartOver = () => {
    setActiveTab('upload');
    setIngredientsData(null);
    setRecipesData(null);
  };

  return (
    <main className="flex min-h-screen flex-col bg-gray-50">
      <header className="bg-white border-b shadow-sm py-6">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-8 w-8 text-primary"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
                />
              </svg>
              <h1 className="text-2xl font-bold">Kitchen Copilot</h1>
            </div>
            {(ingredientsData || recipesData) && (
              <Button variant="ghost" onClick={handleStartOver}>
                Start Over
              </Button>
            )}
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger 
              value="upload" 
              disabled={loading}
            >
              Upload Photo
            </TabsTrigger>
            <TabsTrigger 
              value="ingredients" 
              disabled={!ingredientsData || loading}
            >
              Ingredients
            </TabsTrigger>
            <TabsTrigger 
              value="recipes" 
              disabled={!recipesData || loading}
            >
              Recipes
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload" className="space-y-8">
            <div className="max-w-xl mx-auto">
              <div className="text-center mb-8 space-y-2">
                <h2 className="text-2xl font-bold">Upload a Photo of Your Fridge</h2>
                <p className="text-muted-foreground">
                  Our AI will analyze the contents and suggest recipes you can make
                </p>
              </div>

              <ImageUpload 
                onAnalysisComplete={handleAnalysisComplete} 
                onUploadStart={handleUploadStart}
              />
            </div>
          </TabsContent>

          <TabsContent value="ingredients" className="space-y-8">
            {ingredientsData && (
              <IngredientsDisplay 
                ingredientsData={ingredientsData} 
                onGenerateRecipes={handleGenerateRecipes}
                loading={loading}
              />
            )}
          </TabsContent>

          <TabsContent value="recipes" className="space-y-8">
            {recipesData && (
              <RecipesDisplay recipesData={recipesData} />
            )}
          </TabsContent>
        </Tabs>
      </div>

      <Toaster position="top-center" />
    </main>
  );
}