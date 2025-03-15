import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { IngredientsResponse } from '@/types';

interface IngredientsDisplayProps {
  ingredientsData: IngredientsResponse;
  onGenerateRecipes: () => void;
  loading: boolean;
}

export function IngredientsDisplay({ 
  ingredientsData, 
  onGenerateRecipes,
  loading 
}: IngredientsDisplayProps) {
  const { result, summary } = ingredientsData;
  const categories = Object.keys(result.ingredients);

  // Helper function to get an appropriate emoji for each category
  const getCategoryEmoji = (category: string): string => {
    const emojiMap: { [key: string]: string } = {
      Dairy: '🥛',
      Produce: '🥦',
      Proteins: '🥩',
      Grains: '🌾',
      Condiments: '🧂',
      Beverages: '🥤',
      Snacks: '🍪',
      Frozen: '🧊',
      Canned: '🥫',
      Other: '🍽️',
    };

    return emojiMap[category] || '📦';
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Your Ingredients</h2>
        <div className="text-sm text-muted-foreground">
          Found {summary.total_count} ingredients
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {categories.map((category) => {
          const ingredients = result.ingredients[category];
          if (ingredients.length === 0) return null;

          return (
            <Card key={category}>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center gap-2">
                  <span>{getCategoryEmoji(category)}</span>
                  <span>{category}</span>
                  <span className="ml-auto text-sm font-normal text-muted-foreground">
                    {ingredients.length}
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-1">
                  {ingredients.map((ingredient, index) => (
                    <li key={index} className="text-sm">
                      {ingredient}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Button 
        onClick={onGenerateRecipes} 
        className="w-full" 
        size="lg" 
        disabled={loading}
      >
        {loading ? 'Generating...' : 'Generate Recipe Suggestions'}
      </Button>
    </div>
  );
}