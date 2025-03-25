import logging
from generate_recipe import RecipeGenerator
from generate_image import ImageGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_generation():
    try:
        # Test recipe generation
        logger.info("Starting recipe generation...")
        recipe_generator = RecipeGenerator()
        recipe_data = recipe_generator.generate_recipe()
        logger.info(f"Successfully generated recipe: {recipe_data['title']}")
        
        # Test image generation with recipe data
        logger.info("Starting image generation...")
        image_generator = ImageGenerator()
        image_path = image_generator.generate_image(recipe_data['title'], recipe_data)
        logger.info(f"Successfully generated image: {image_path}")
        
        return recipe_data, image_path
        
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        raise

if __name__ == "__main__":
    test_generation() 