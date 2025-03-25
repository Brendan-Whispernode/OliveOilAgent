import os
from datetime import datetime
import requests
from openai import OpenAI
from utils.config import load_config

class ImageGenerator:
    def __init__(self):
        config = load_config()
        self.client = OpenAI(api_key=config['OPENAI_API_KEY'])
        
    def generate_image(self, recipe_title):
        try:
            # Create DALL-E prompt
            prompt = self._create_image_prompt(recipe_title)
            
            # Generate image
            response = self.client.images.generate(
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            
            # Save image
            image_url = response.data[0].url
            image_path = self._save_image(image_url, recipe_title)
            
            return image_path
            
        except Exception as e:
            raise Exception(f"Error generating image: {str(e)}")
    
    def _create_image_prompt(self, recipe_title):
        return f"A professional food photography style image of {recipe_title}. " \
               f"The image should be well-lit, styled beautifully with props, " \
               f"and look appetizing. Food blog style, overhead shot."
    
    def _save_image(self, image_url, recipe_title):
        # Download and save image
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"images/{timestamp}-{recipe_title.lower().replace(' ', '-')}.png"
        
        # Ensure images directory exists
        os.makedirs('images', exist_ok=True)
        
        # Download image
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Save to file
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        return filename