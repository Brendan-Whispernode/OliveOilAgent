import requests
import json
import os
import base64
import re
from utils.config import load_config

class ShopifyPoster:
    def __init__(self):
        config = load_config()
        # Remove any protocol prefix from the store URL
        store_url = config['SHOPIFY_STORE_URL']
        if store_url.startswith('http://'):
            store_url = store_url[7:]
        if store_url.startswith('https://'):
            store_url = store_url[8:]
        # Remove any trailing slashes
        store_url = store_url.rstrip('/')
        
        self.store_url = store_url
        self.access_token = config['SHOPIFY_ACCESS_TOKEN']
        self.blog_id = config.get('SHOPIFY_BLOG_ID', None)  # We'll find the blog ID dynamically
        
        # Verify the store URL is properly formatted
        if 'placeholder' in self.store_url.lower() or 'your_store' in self.store_url.lower():
            raise ValueError("Please update your .env file with your actual Shopify store URL")
        
        self.headers = {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json'
        }
        
        print(f"Initialized Shopify poster for store: {self.store_url}")
        
        # Find available blogs
        if not self.blog_id:
            self.blog_id = self._find_blog_id()
            if not self.blog_id:
                raise ValueError("No blogs found in the Shopify store. Please create a blog first.")
    
    def _find_blog_id(self):
        """Find available blogs in the Shopify store"""
        try:
            print("Fetching available blogs...")
            api_url = f"https://{self.store_url}/admin/api/2023-07/blogs.json"
            response = requests.get(api_url, headers=self.headers)
            response.raise_for_status()
            
            blogs = response.json().get('blogs', [])
            if not blogs:
                print("No blogs found in the Shopify store.")
                return None
            
            # Print available blogs
            print("Available blogs:")
            for blog in blogs:
                print(f"  - ID: {blog['id']}, Title: {blog['title']}")
            
            # Use the first blog
            blog_id = str(blogs[0]['id'])
            print(f"Using blog ID: {blog_id}")
            return blog_id
            
        except Exception as e:
            print(f"Error finding blogs: {str(e)}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None
    
    def _clean_html_content(self, content):
        """Clean HTML content to ensure it renders properly in Shopify"""
        # Remove any code block markers that might be in the content
        content = re.sub(r'```html\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        
        # Ensure the content doesn't have <body> tags which can cause issues
        content = re.sub(r'</?body>', '', content)
        
        # Remove any <meta> tags
        content = re.sub(r'<meta[^>]*>', '', content)
        
        # Remove any <title> tags
        content = re.sub(r'<title>[^<]*</title>', '', content)
        
        # Remove any <style> blocks
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        
        # Remove any <script> blocks
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        
        return content.strip()
    
    def create_post(self, title, content, image_path=None, tags=None):
        """
        Create a blog post on Shopify
        
        Args:
            title (str): The title of the blog post
            content (str): The HTML content of the blog post
            image_path (str, optional): Path to the image file to upload
            tags (list, optional): List of tags for the blog post
            
        Returns:
            str: URL of the created blog post
        """
        try:
            # Clean the HTML content
            content = self._clean_html_content(content)
            
            # First try to upload the image directly to the article
            if image_path and os.path.exists(image_path):
                print(f"Using image: {image_path}")
                with open(image_path, 'rb') as img_file:
                    encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
            else:
                encoded_image = None
            
            # Create the blog post data
            post_data = {
                "article": {
                    "title": title,
                    "author": "Chef Olivo",
                    "body_html": content,
                    "published": True,  # Set as published
                    "tags": ",".join(tags) if tags else "recipe,olive oil,gourmet"
                }
            }
            
            # Add the image if available
            if encoded_image:
                post_data["article"]["image"] = {"attachment": encoded_image}
            
            # Make the API request to create the article
            print(f"Creating blog post on {self.store_url}...")
            api_url = f"https://{self.store_url}/admin/api/2023-07/blogs/{self.blog_id}/articles.json"
            print(f"API URL: {api_url}")
            
            response = requests.post(
                api_url,
                headers=self.headers,
                json=post_data,
                verify=True  # Ensure SSL verification is enabled
            )
            
            # Print response for debugging
            print(f"Response status code: {response.status_code}")
            
            # Check for errors
            response.raise_for_status()
            
            # Get the article data from the response
            article_data = response.json().get('article', {})
            article_id = article_data.get('id')
            
            print(f"Successfully created blog post with ID: {article_id}")
            
            # Return the article URL
            handle = article_data.get('handle', '')
            return f"https://{self.store_url}/blogs/{self.blog_id}/{handle}"
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error posting to Shopify: {str(e)}"
            if hasattr(e, 'response') and e.response:
                error_msg += f"\nResponse: {e.response.text}"
            raise Exception(error_msg)
        except Exception as e:
            raise Exception(f"Error posting to Shopify: {str(e)}")
    
    def _upload_image(self, image_path):
        """
        Upload an image to Shopify
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: URL of the uploaded image
        """
        try:
            # Read the image file
            with open(image_path, 'rb') as img_file:
                # Encode the image as base64
                encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
            
            # Create the upload data
            upload_data = {
                "image": {
                    "attachment": encoded_image,
                    "filename": os.path.basename(image_path)
                }
            }
            
            # Make the API request to upload the image
            api_url = f"https://{self.store_url}/admin/api/2023-07/images.json"
            print(f"Uploading image to: {api_url}")
            
            response = requests.post(
                api_url,
                headers=self.headers,
                json=upload_data,
                verify=True  # Ensure SSL verification is enabled
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Get the image URL from the response
            image_data = response.json().get('image', {})
            return image_data.get('src')
            
        except requests.exceptions.RequestException as e:
            print(f"Error uploading image to Shopify: {str(e)}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"Error uploading image to Shopify: {str(e)}")
            return None