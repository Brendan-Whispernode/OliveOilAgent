# AI Recipe Blog Generator

An automated system that generates recipe blog posts using AI, featuring specialty olive oils and vinegars. The system generates recipes, creates images, and posts directly to Shopify.

## Features
- Generates unique recipes using product catalog
- Creates AI-generated recipe images
- Writes blog posts in a chef's voice
- Automatically posts to Shopify
- Stores generated content locally

## Setup

1. Clone the repository
2. Install dependencies:

pip install -r requirements.txt3. 

3. Create a .env file with your credentials:

OPENAI_API_KEY=your_key_here
SHOPIFY_ACCESS_TOKEN=your_token_here
SHOPIFY_STORE_URL=your_store_url
DALLE_API_KEY=your_key_here

4. Run the script:

python main.py

## Directory Structure- main.py - Main orchestration script- generate_recipe.py - Recipe generation logic- generate_image.py - Image generation using DALL-E- post_to_blog.py - Shopify blog posting- utils/ - Helper functions and configuration
