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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function AppPage() {
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
    <div className=" py-8">
      <div className="container mx-auto px-4">
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Kitchen Copilot Tool</CardTitle>
            <CardDescription>Upload a photo of your fridge to get recipe suggestions</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Use this tool to analyze your refrigerator contents and receive personalized recipe suggestions based on what you have available.</p>
          </CardContent>
        </Card>

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

        {(ingredientsData || recipesData) && (
          <div className="mt-8 text-center">
            <Button variant="outline" onClick={handleStartOver}>
              Start Over
            </Button>
          </div>
        )}
      </div>

      <Toaster position="top-center" />
    </div>
  );
}