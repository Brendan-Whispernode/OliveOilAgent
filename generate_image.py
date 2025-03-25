import os
import re
from datetime import datetime
import requests
from openai import OpenAI
from utils.config import load_config

class ImageGenerator:
    def __init__(self):
        config = load_config()
        self.client = OpenAI(api_key=config['OPENAI_API_KEY'])
        
    def generate_image(self, recipe_title, recipe_data=None):
        try:
            # Create DALL-E prompt based on recipe content
            prompt = self._create_image_prompt(recipe_title, recipe_data)
            
            # Print the prompt for debugging
            print(f"\nImage Generation Prompt:\n{prompt}\n")
            
            # Generate image
            response = self.client.images.generate(
                prompt=prompt,
                n=1,
                size="1024x1024",
                quality="hd",
                style="vivid"
            )
            
            # Save image
            image_url = response.data[0].url
            image_path = self._save_image(image_url, recipe_title)
            
            return image_path
            
        except Exception as e:
            raise Exception(f"Error generating image: {str(e)}")
    
    def _create_image_prompt(self, recipe_title, recipe_data=None):
        # Base prompt with the recipe title
        base_prompt = f"A professional food photography image of '{recipe_title}'."
        
        # If we have recipe data, extract key ingredients and details
        if recipe_data and 'html_content' in recipe_data:
            # Extract ingredients from the HTML content
            ingredients = self._extract_ingredients(recipe_data['html_content'])
            featured_products = recipe_data.get('featured_products', [])
            
            # Create a more detailed prompt based on the recipe
            prompt_parts = [
                base_prompt,
                f"The dish contains {', '.join(ingredients[:5])}." if ingredients else "",
                f"Highlight the use of {', '.join(featured_products)}." if featured_products else "",
                "The dish should be beautifully plated on an elegant dish, with perfect lighting that highlights the textures and colors.",
                "Style it like a professional food magazine photograph with a clean, appealing background.",
                "Use natural, soft lighting with subtle shadows to create depth.",
                "8k resolution, professional food photography."
            ]
            
            return " ".join(filter(None, prompt_parts))
        
        # Fallback to a generic but still good prompt
        return f"{base_prompt} The dish should be beautifully plated on an elegant dish, with perfect lighting that highlights the textures and colors. Style it like a professional food magazine photograph. 8k resolution, professional food photography."
    
    def _extract_ingredients(self, html_content):
        # Try to extract ingredients from the HTML content
        # Look for <ul> tags which typically contain ingredient lists
        ingredients = []
        
        # Simple regex to find list items within ul tags
        ul_pattern = re.search(r'<ul>(.*?)</ul>', html_content, re.DOTALL)
        if ul_pattern:
            ul_content = ul_pattern.group(1)
            # Extract individual list items
            li_items = re.findall(r'<li>(.*?)</li>', ul_content, re.DOTALL)
            
            # Process each list item to extract the main ingredient
            for item in li_items:
                # Try to get just the main ingredient name by taking the first few words
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
    
    def _save_image(self, image_url, recipe_title):
        # Download and save image
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safe_title = recipe_title.lower().replace(' ', '-').replace('/', '-')
        filename = f"images/{timestamp}-{safe_title}.png"
        
        # Ensure images directory exists
        os.makedirs('images', exist_ok=True)
        
        # Download image
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Save to file
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        print(f"Image saved to: {filename}")
        return filename