import requests
import json
from utils.config import load_config

class ShopifyPoster:
    def __init__(self):
        config = load_config()
        self.store_url = config['SHOPIFY_STORE_URL']
        self.access_token = config['SHOPIFY_ACCESS_TOKEN']
        self.headers = {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json'
        }
    
    def create_post(self, title, content, image_path):
        try:
            # First upload the image
            image_url = self._upload_image(image_path)
            
            # Create the blog post
            post_data = {
                "article": {
                    "title": title,
                    "author": "Chef Olivo",
                    "body_html": content,
                    "published": False,  # Set as draft
                    "image": {"src": image_url}
                }
            }
            
            # Get your blog ID (you'll need to set this up)
            blog_id = "your_blog_id"
            
            response = requests.post(
                f"https://{self.store_url}/admin/api/2023-01/blogs/{blog_id}/articles.json",
                headers=self.headers,
                json=post_data
            )
            
            response.raise_for_status()
            return response.json()['article']['url']
            
        except Exception as e:
            raise Exception(f"Error posting to Shopify: {str(e)}")
    
    def _upload_image(self, image_path):
        # Add code here to upload image to Shopify
        # Return the URL of the uploaded image
        pass