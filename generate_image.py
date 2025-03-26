import os
import requests
from datetime import datetime
from utils.config import load_config

class ImageGenerator:
    def __init__(self):
        self.service_url = "http://localhost:3000/generate-image"
    
    def generate_image(self, recipe_title, recipe_data=None):
        """
        Generate an image using REVE
        
        Args:
            recipe_title (str): Title of the recipe
            recipe_data (dict, optional): Full recipe data for better prompt generation
            
        Returns:
            str: Path to the generated image
        """
        try:
            # Create a detailed prompt based on the recipe
            prompt = self._create_image_prompt(recipe_title, recipe_data)
            
            print(f"\nImage Generation Prompt:\n{prompt}\n")
            
            # Call the REVE service
            response = requests.post(
                self.service_url,
                json={"prompt": prompt}
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Get the image path from the response
            result = response.json()
            if not result.get('success'):
                raise Exception(f"Image generation failed: {result.get('error')}")
            
            print(f"Image generated successfully: {result['filename']}")
            print(f"Generation seed: {result.get('seed', 'unknown')}")
            
            return result['filepath']
            
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return None
    
    def _create_image_prompt(self, recipe_title, recipe_data=None):
        """Create a detailed prompt for image generation based on the full recipe"""
        if not recipe_data:
            return self._create_basic_prompt(recipe_title)
        
        # Extract main ingredients and cooking method
        ingredients = self._extract_key_ingredients(recipe_data.get('ingredients', []))
        
        # Try to determine the main protein/dish type from the recipe
        main_components = []
        for ingredient in ingredients:
            if any(protein in ingredient.lower() for protein in 
                   ['chicken', 'beef', 'fish', 'pork', 'tofu', 'shrimp', 'lamb']):
                main_components.append(ingredient)
        
        # Create a more detailed prompt using the complete recipe information
        prompt = (
            f"Professional food photography of {recipe_title}, featuring a plated dish of "
            f"{', '.join(main_components) if main_components else recipe_title}, "
            f"with visible {', '.join(ingredients[:2])}. "
            "Styled on a rustic wooden table with natural lighting, "
            "overhead shot at a 45-degree angle, soft shadows, shallow depth of field, "
            "garnished with fresh herbs, olive oil drizzle visible and glistening, "
            "4k, high resolution, food magazine quality, professional lighting setup, "
            "Canon EOS R5, 50mm f/1.2 lens, backlit with window light, "
            "styled like a high-end restaurant presentation"
        )
        
        return prompt
    
    def _create_basic_prompt(self, recipe_title):
        """Fallback prompt when no recipe data is available"""
        return (
            f"Professional food photography of {recipe_title}, "
            "styled elegantly on a rustic wooden table with natural lighting, "
            "overhead shot, 4k, high resolution, soft shadows, "
            "food magazine quality, professional lighting, "
            "Canon EOS R5, 50mm f/1.2 lens"
        )
    
    def _extract_key_ingredients(self, ingredients_list):
        """Extract key ingredients from the ingredients list"""
        ingredients = []
        for item in ingredients_list:
            # This is a simple approach - could be improved with NLP
            words = item.split()
            if words:
                # Take first word if it's a measurement, otherwise include it
                if words[0].lower() in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'one', 'two', 'three', 'four', 'a', 'an', 'the', 'some', 'few', 'little', 'tablespoon', 'teaspoon', 'cup', 'ounce', 'oz', 'pound', 'lb', 'gram', 'g', 'kg', 'ml', 'l']:
                    # Take a few words but not the whole thing
                    ingredient = ' '.join(words[1:3])
                else:
                    ingredient = ' '.join(words[:2])
                
                ingredients.append(ingredient.strip(',.:;()'))
        
        return ingredients