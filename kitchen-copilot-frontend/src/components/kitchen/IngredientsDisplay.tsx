import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { IngredientsResponse } from '@/types';
import { 
  Milk, Carrot, Egg, Wheat, FlaskRound, Coffee, Cookie, 
  ShoppingBag, Package, Utensils, ChevronRight 
} from 'lucide-react';

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

  // Helper function to get an appropriate icon for each category
  const getCategoryIcon = (category: string) => {
    switch(category) {
      case 'Dairy': return <Milk className="size-5" />;
      case 'Produce': return <Carrot className="size-5" />;
      case 'Proteins': return <Egg className="size-5" />;
      case 'Grains': return <Wheat className="size-5" />;
      case 'Condiments': return <FlaskRound className="size-5" />;
      case 'Beverages': return <Coffee className="size-5" />;
      case 'Snacks': return <Cookie className="size-5" />;
      case 'Frozen': return <ShoppingBag className="size-5" />;
      case 'Canned': return <Package className="size-5" />;
      default: return <Utensils className="size-5" />;
    }
  };

  // Helper function to get ingredient emoji
  const getIngredientEmoji = (ingredient: string): string => {
    const ingredientEmojiMap: { [key: string]: string } = {
      // Dairy
      'mayonnaise': '🥄',
      'cream cheese': '🧀',
      'butter': '🧈',
      // Produce
      'banana': '🍌',
      'pear': '🍐',
      'apple': '🍎',
      'pepper': '🫑',
      'orange': '🍊',
      'lemon': '🍋',
      'lime': '🍈',
      'cilantro': '🌿',
      'basil': '🌿',
      'arugula': '🥬',
      'cabbage': '🥬',
      'carrot': '🥕',
      'zucchini': '🥒',
      // Proteins
      'egg': '🥚',
      // Grains
      'tortilla': '🌮',
      // Condiments
      'ketchup': '🍅',
      'mustard': '🟡',
      'syrup': '🍯',
      'soy sauce': '🍶',
      // Beverages
      'wine': '🍷',
      // Other
      'pasta': '🍝',
      'almond': '🥜',
      'seed': '🌱',
      'date': '🌴',
      'pickle': '🥒',
    };

    // Check if any key in the map is contained in the ingredient name
    for (const [key, emoji] of Object.entries(ingredientEmojiMap)) {
      if (ingredient.toLowerCase().includes(key.toLowerCase())) {
        return emoji;
      }
    }
    
    return '•';
  };

  // Calculate if we need to show in one or two columns
  const nonEmptyCategories = categories.filter(category => 
    result.ingredients[category].length > 0
  );
  const useOneColumn = nonEmptyCategories.length <= 3;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Your Ingredients</h2>
        <Badge variant="outline" className="px-3 py-1">
          {summary.total_count} items found
        </Badge>
      </div>

      <div className={`grid gap-4 ${useOneColumn ? 'md:grid-cols-1' : 'md:grid-cols-2'}`}>
        {categories.map((category) => {
          const ingredients = result.ingredients[category];
          if (ingredients.length === 0) return null;

          return (
            <Card key={category} className="overflow-hidden transition-all hover:shadow-md">
              <CardHeader className="pb-2 border-b bg-muted/30">
                <CardTitle className="text-lg flex items-center gap-2">
                  {getCategoryIcon(category)}
                  <span>{category}</span>
                  <Badge variant="secondary" className="ml-auto">
                    {ingredients.length}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <ul className="divide-y divide-border">
                  {ingredients.map((ingredient, index) => (
                    <li key={index} className="p-3 flex items-center gap-2 hover:bg-muted/50 transition-colors">
                      <span className="text-lg w-6 text-center">{getIngredientEmoji(ingredient)}</span>
                      <span className="text-sm flex-1">{ingredient}</span>
                      <ChevronRight className="size-4 text-muted-foreground opacity-50" />
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
        {loading ? 'Generating Recipes...' : 'Generate Recipe Suggestions'}
      </Button>
    </div>
  );
}