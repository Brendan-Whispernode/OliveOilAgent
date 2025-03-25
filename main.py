import logging
from datetime import datetime
from generate_recipe import RecipeGenerator
from generate_image import ImageGenerator
from post_to_blog import ShopifyPoster
from utils.config import load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Load configuration and product data
        config = load_config()
        
        # Generate recipe
        recipe_generator = RecipeGenerator()
        recipe_data = recipe_generator.generate_recipe()
        
        # Generate image
        image_generator = ImageGenerator()
        image_path = image_generator.generate_image(recipe_data['title'])
        
        # Post to Shopify
        shopify_poster = ShopifyPoster()
        post_url = shopify_poster.create_post(
            title=recipe_data['title'],
            content=recipe_data['html_content'],
            image_path=image_path
        )
        
        logger.info(f"Successfully created blog post: {post_url}")
        
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")

if __name__ == "__main__":
    main()