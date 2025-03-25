import os
import json
import logging
from post_to_blog import ShopifyPoster
from utils.config import load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_shopify_post():
    try:
        # Verify Shopify credentials
        config = load_config()
        if 'placeholder' in config['SHOPIFY_STORE_URL'].lower() or 'your' in config['SHOPIFY_STORE_URL'].lower():
            logger.error("Please update your .env file with your actual Shopify store URL")
            return
        
        # Print Shopify configuration for debugging
        logger.info(f"Shopify Store URL: {config['SHOPIFY_STORE_URL']}")
        logger.info(f"Shopify Access Token: {config['SHOPIFY_ACCESS_TOKEN'][:5]}...{config['SHOPIFY_ACCESS_TOKEN'][-5:]}")
        
        # Find the most recent recipe and image
        recipe_path = find_most_recent_file('recipes', '.json')
        image_path = find_most_recent_file('images', '.png')
        
        if not recipe_path:
            logger.error("No recipe found. Please generate a recipe first.")
            return
        
        logger.info(f"Using recipe: {recipe_path}")
        logger.info(f"Using image: {image_path}")
        
        # Load the recipe data
        with open(recipe_path, 'r') as f:
            recipe_data = json.load(f)
        
        # Extract title and content
        title = recipe_data['title']
        content = recipe_data['html_content']
        
        # Extract featured products for tags
        tags = recipe_data.get('featured_products', [])
        tags.extend(['recipe', 'gourmet', 'olive oil'])
        
        # Create Shopify post
        logger.info("Posting to Shopify...")
        shopify_poster = ShopifyPoster()
        post_url = shopify_poster.create_post(
            title=title,
            content=content,
            image_path=image_path,
            tags=tags
        )
        
        logger.info(f"Successfully created blog post: {post_url}")
        
    except Exception as e:
        logger.error(f"Error in Shopify post test: {str(e)}")
        raise

def find_most_recent_file(directory, extension):
    """Find the most recently created file with the given extension in the directory"""
    if not os.path.exists(directory):
        return None
    
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(extension)]
    if not files:
        return None
    
    # Sort by creation time, newest first
    files.sort(key=lambda x: os.path.getctime(x), reverse=True)
    return files[0]

if __name__ == "__main__":
    test_shopify_post() 