import json
import os
import random
import re
from datetime import datetime
from openai import OpenAI
from utils.config import load_config
import html2text

class RecipeGenerator:
    def __init__(self):
        config = load_config()
        self.products = self._load_products()
        self.client = OpenAI(api_key=config['OPENAI_API_KEY'])
        self.html_converter = html2text.HTML2Text()
        self.html_converter.body_width = 0  # Don't wrap text
        
    def _load_products(self):
        with open('product_memory.json', 'r') as f:
            return json.load(f)
    
    def _select_random_products(self):
        # Select 1-2 random categories
        categories = random.sample(list(self.products.keys()), k=random.randint(1, 2))
        
        selected_products = []
        for category in categories:
            # Select 1-2 products from each chosen category
            num_products = random.randint(1, 2)
            category_products = random.sample(self.products[category], k=min(num_products, len(self.products[category])))
            selected_products.extend(category_products)
        
        return selected_products
    
    def generate_recipe(self):
        try:
            # Select random products to feature
            featured_products = self._select_random_products()
            
            # Generate recipe using OpenAI
            prompt = self._create_recipe_prompt(featured_products)
            
            # Updated API call with proper response handling
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are Chef Olivo, a passionate chef who loves creating recipes with premium olive oils and vinegars. 
                        Your tone is fun, engaging, and educational. You specialize in creating recipes that showcase the unique flavors of 
                        specialty oils and vinegars. Always format your recipes in clean, well-structured HTML."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            # Properly access the response content
            recipe_content = completion.choices[0].message.content
            
            # Parse and format the recipe
            recipe_data = self._format_recipe(recipe_content)
            
            # Save to files (both JSON and Markdown)
            self._save_recipe(recipe_data)
            print(f"Generated recipe: {recipe_data['title']}")  # Debug line
            
            return recipe_data
            
        except Exception as e:
            print(f"Error in generate_recipe: {str(e)}")
            raise
    
    def _create_recipe_prompt(self, featured_products):
        return f"""Create a gourmet recipe that showcases these specialty products: {', '.join(featured_products)}.

        Please structure your response in HTML format with these sections:
        1. A catchy, SEO-friendly title (in <h1> tags)
        2. A brief, engaging introduction about why this recipe is special (in <p> tags)
        3. Ingredients list (in <ul> tags)
        4. Step-by-step instructions (in <ol> tags)
        5. Chef's tips for using the featured products (in <div class="tips"> tags)
        6. Serving suggestions (in <div class="serving"> tags)

        Make sure to emphasize how the featured products enhance the dish's flavor. Keep the tone friendly and approachable while highlighting the gourmet aspects of the recipe."""
    
    def _format_recipe(self, content):
        # Basic parsing of the GPT response into structured data
        # Try to extract title from h1 tags, fallback to first line if not found
        title_match = re.search(r'<h1>(.*?)</h1>', content, re.DOTALL)
        title = title_match.group(1) if title_match else content.split('\n')[0].strip('# ')
        
        # Convert HTML to Markdown
        markdown_content = self.html_converter.handle(content)
        
        return {
            "title": title,
            "html_content": content,
            "markdown_content": markdown_content,
            "timestamp": datetime.now().isoformat(),
            "featured_products": self._extract_featured_products(content)
        }
    
    def _extract_featured_products(self, content):
        # Try to extract mentioned products from the content
        all_products = []
        for category in self.products.values():
            all_products.extend(category)
        
        mentioned_products = []
        for product in all_products:
            if product.lower() in content.lower():
                mentioned_products.append(product)
        
        return mentioned_products
    
    def _save_recipe(self, recipe_data):
        # Create base filename without extension
        base_filename = f"{recipe_data['timestamp']}-{recipe_data['title'].lower().replace(' ', '-').replace('/', '-')}"
        
        # Ensure recipes directory exists
        os.makedirs('recipes', exist_ok=True)
        
        # Save JSON version
        json_filename = f"recipes/{base_filename}.json"
        with open(json_filename, 'w') as f:
            json.dump(recipe_data, f, indent=2)
        
        # Save Markdown version
        md_filename = f"recipes/{base_filename}.md"
        with open(md_filename, 'w') as f:
            f.write(f"# {recipe_data['title']}\n\n")
            f.write(f"*Generated on: {recipe_data['timestamp']}*\n\n")
            f.write(f"**Featured Products:** {', '.join(recipe_data['featured_products'])}\n\n")
            f.write(recipe_data['markdown_content'])
        
        print(f"Recipe saved as JSON: {json_filename}")
        print(f"Recipe saved as Markdown: {md_filename}")
        
        return md_filename