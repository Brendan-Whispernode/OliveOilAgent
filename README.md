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

```pip install -r requirements.txt```
```cd image_service```
```npm install```

3. Create a .env file with your credentials:


OPENAI_API_KEY=your_key_here
SHOPIFY_ACCESS_TOKEN=your_token_here
SHOPIFY_STORE_URL=your_store_url
REVE_AUTH_TOKEN=your_reve_auth_token
REVE_COOKIE=your_reve_cookie
REVE_PROJECT_ID=your_reve_project_id

To get the REVE credentials:
1. Go to preview.reve.art and log in
2. Open Developer Tools (F12)
3. Go to the Network tab
4. Make any image generation
5. Look for requests to the API
6. Find the Authorization header and Cookie values

4. Run the services:

Start the image generation service:

```cd image_service```
```npm start```

Start the main application (in a new terminal):

```python main.py```


## Directory Structure

- main.py # Main orchestration script /n
generate_recipe.py # Recipe generation logic /n
generate_image.py # Image generation using REVE /n
post_to_blog.py # Shopify blog posting
- image_service/ # REVE image generation service
- server.js # Image service main server
- test_reve.js # Test script for image generation
- utils/ # Helper functions and configuration

## Testing

To test the image generation service:

bash
cd image_service
node test_reve.js 

To test the recipe generation:

bash
python main.py
