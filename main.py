import logging
from datetime import datetime
import time
from generate_recipe import RecipeGenerator
from generate_image import ImageGenerator
from post_to_blog import ShopifyPoster
from utils.config import load_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("=== Starting Blog Post Generation ===")
    
    try:
        # Load configuration
        config = load_config()
        
        # 1. Generate recipe
        logger.info("Generating recipe...")
        recipe_generator = RecipeGenerator()
        recipe_data = recipe_generator.generate_recipe()
        
        logger.info(f"Recipe generated: {recipe_data['title']}")
        logger.info(f"Featured products: {', '.join(recipe_data['featured_products'])}")
        
        # 2. Generate image
        logger.info("Generating image...")
        image_generator = ImageGenerator()
        image_path = image_generator.generate_image(
            recipe_data['title'],
            recipe_data  # Pass full recipe data for better prompt generation
        )
        
        if not image_path:
            raise Exception("Failed to generate image")
        
        logger.info(f"Image generated: {image_path}")
        
        # 3. Post to Shopify
        logger.info("Posting to Shopify...")
        shopify_poster = ShopifyPoster()
        
        # Create tags from featured products
        tags = ["recipe", "gourmet cooking"]
        tags.extend([p.lower().replace(' ', '-') for p in recipe_data['featured_products']])
        
        # Post to blog
        blog_url = shopify_poster.create_post(
            title=recipe_data['title'],
            content=recipe_data['html_content'],
            image_path=image_path,
            tags=tags
        )
        
        logger.info("=== Blog Post Created Successfully! ===")
        logger.info(f"Title: {recipe_data['title']}")
        logger.info(f"Image: {image_path}")
        logger.info(f"Blog URL: {blog_url}")
        
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    # Make sure the REVE image service is running
    logger.warning("⚠️  Make sure the REVE image service is running (npm start in image_service directory)")
    time.sleep(2)  # Give user time to read the warning
    
    main()