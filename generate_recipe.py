import json
import os
import random
import re
from datetime import datetime
from openai import OpenAI
from utils.config import load_config
import html2text
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

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
            
            # Save to file
            self._save_recipe(recipe_data)
            print(f"Generated recipe: {recipe_data['title']}")  # Debug line
            
            return recipe_data
            
        except Exception as e:
            print(f"Error in generate_recipe: {str(e)}")
            raise
    
    def _create_recipe_prompt(self, featured_products):
        """Enhanced prompt for creating realistic recipes with specialty products as flavor enhancers"""
        # Load Chef Olivo's personality template
        try:
            with open('prompts/chef_template.txt', 'r') as f:
                chef_template = f.read()
        except FileNotFoundError:
            chef_template = "You are Chef Olivo, a passionate culinary expert..."

        # Determine product types and flavors
        olive_oils = [p for p in featured_products if "olive oil" in p.lower()]
        balsamics = [p for p in featured_products if "balsamic" in p.lower()]
        
        # Extract flavor profiles
        oil_flavors = [p.lower().replace("olive oil", "").strip() for p in olive_oils]
        balsamic_flavors = [p.lower().replace("balsamic", "").strip() for p in balsamics]
        
        # Create realistic usage examples
        usage_examples = []
        
        if olive_oils:
            usage_examples.extend([
                f"- Use {olive_oils[0]} as a finishing touch on soups, pastas, or grilled meats",
                f"- Substitute {olive_oils[0]} in place of regular olive oil in vinaigrettes or marinades",
                f"- Brush {olive_oils[0]} on bread before toasting for a subtle flavor enhancement",
                f"- Drizzle {olive_oils[0]} over completed dishes just before serving to preserve its delicate flavor notes"
            ])
        
        if balsamics:
            usage_examples.extend([
                f"- Add a small splash of {balsamics[0]} to pan sauces for depth and complexity",
                f"- Use {balsamics[0]} to deglaze a pan after searing meat",
                f"- Create a simple glaze with {balsamics[0]} and a touch of honey or maple syrup",
                f"- Add a few drops of {balsamics[0]} to fresh fruit for a surprising flavor contrast"
            ])
        
        prompt = f"""{chef_template}

Today's featured products: {', '.join(featured_products)}

I'd like you to create a delicious, realistic recipe that incorporates our specialty products as flavor enhancers rather than making them the star of the show. Think of how a professional chef would subtly use these ingredients to elevate an otherwise familiar dish.

Some ways to naturally incorporate these products:
{chr(10).join(usage_examples[:4])}

Important guidelines:
1. Create a recipe that would work perfectly well with regular olive oil/vinegar, but becomes EXCEPTIONAL with our specialty products
2. Use realistic quantities - often just 1-2 tablespoons of a specialty oil or a few teaspoons of balsamic is enough
3. Focus on how these products complement and enhance the other ingredients
4. Include specific notes on what flavors the specialty products contribute to the dish
5. Suggest regular olive oil/vinegar as substitutes for those who don't have our products

Please structure your response in clean HTML format with these sections:
1. <h1> for the recipe title (creative and SEO-friendly)
2. <div class="story"> for your personal story/introduction
3. <div class="product-spotlight"> for explaining how our specialty products enhance this dish
4. <div class="ingredients">
   - <ul> for ingredients list (with realistic measurements for specialty products)
   - <ul class="tools"> for required tools
   - <ul class="substitutions"> for possible substitutions
5. <div class="instructions">
   - <ol> for step-by-step instructions
6. <div class="chef-notes"> for your special tips and variations
7. <div class="serving"> for presentation and pairing suggestions
8. <div class="nutrition"> for nutritional info and allergens

Remember to maintain your warm, conversational tone throughout, sprinkling in occasional Italian phrases naturally. Sign off with your signature "Buon Appetito!"

Make the recipe approachable yet sophisticated, perfect for home cooks who appreciate quality ingredients but don't want to use excessive amounts of specialty products."""

        return prompt
    
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
    
    def _get_relevant_inspiration(self, featured_products):
        """Get relevant recipes from cache based on featured products"""
        relevant_recipes = []
        
        # Try to find recipes with each featured product
        for product in featured_products:
            # Extract the main ingredient from the product name
            # E.g., "Basil Olive Oil" -> "Basil"
            main_ingredient = product.split()[0].lower()
            
            # Find recipes with this ingredient
            matching_recipes = self.recipe_scraper.get_recipes_by_ingredient(main_ingredient)
            
            # Add up to 2 recipes per product
            for recipe in matching_recipes[:2]:
                relevant_recipes.append(
                    f"- {recipe['title']} ({recipe['source']}): {recipe['description'][:100]}..."
                )
        
        # If we didn't find enough, add some random ones
        if len(relevant_recipes) < 3:
            random_recipes = self.recipe_scraper.get_random_recipes(3 - len(relevant_recipes))
            for recipe in random_recipes:
                relevant_recipes.append(
                    f"- {recipe['title']} ({recipe['source']}): {recipe['description'][:100]}..."
                )
        
        # Return up to 5 relevant recipes
        return "\n".join(relevant_recipes[:5])

    def _search_saratoga_for_inspiration(self, featured_products, max_results=3):
        """
        Search Saratoga's website for recipes using similar products
        
        Args:
            featured_products (list): List of products to search for
            max_results (int): Maximum number of results to return
            
        Returns:
            str: Formatted inspiration text
        """
        inspiration_recipes = []
        base_url = "https://saratogaoliveoil.com/blogs/recipes"
        
        try:
            # Extract key terms from products
            search_terms = []
            for product in featured_products:
                # Extract flavor profile (e.g., "basil" from "Basil Olive Oil")
                parts = product.lower().split()
                if len(parts) > 1 and ("olive" in parts or "balsamic" in parts):
                    flavor = parts[0]
                    if flavor not in ["the", "a", "an"] and len(flavor) > 2:
                        search_terms.append(flavor)
            
            # If no good search terms, use generic ones
            if not search_terms:
                if any("olive oil" in p.lower() for p in featured_products):
                    search_terms.append("olive")
                if any("balsamic" in p.lower() for p in featured_products):
                    search_terms.append("balsamic")
            
            logger.info(f"Searching Saratoga for terms: {search_terms}")
            
            # Try each search term
            for term in search_terms:
                if len(inspiration_recipes) >= max_results:
                    break
                    
                # Construct search URL
                search_url = f"{base_url}?q={term}"
                logger.info(f"Searching: {search_url}")
                
                response = requests.get(search_url, timeout=10)
                if response.status_code != 200:
                    logger.warning(f"Failed to search Saratoga: {response.status_code}")
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find recipe cards
                recipe_cards = soup.find_all('div', class_='blog-post')
                
                for card in recipe_cards[:2]:  # Limit to 2 per search term
                    try:
                        # Extract title
                        title_elem = card.find('h2') or card.find('h3')
                        if not title_elem:
                            continue
                        title = title_elem.text.strip()
                        
                        # Extract description
                        desc_elem = card.find('div', class_='rte')
                        description = desc_elem.text.strip()[:150] + "..." if desc_elem else ""
                        
                        # Extract URL
                        link_elem = card.find('a', href=True)
                        if not link_elem:
                            continue
                        
                        recipe_url = f"https://saratogaoliveoil.com{link_elem['href']}"
                        
                        # Add to inspiration list
                        inspiration = f"- {title}: {description} (Source: Saratoga Olive Oil Co.)"
                        if inspiration not in inspiration_recipes:
                            inspiration_recipes.append(inspiration)
                            
                    except Exception as e:
                        logger.error(f"Error processing recipe card: {str(e)}")
            
            # If we didn't find enough, try the main recipes page
            if len(inspiration_recipes) < max_results:
                try:
                    response = requests.get(base_url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        recipe_cards = soup.find_all('div', class_='blog-post')
                        
                        # Randomly select a few
                        random_cards = random.sample(recipe_cards, min(max_results - len(inspiration_recipes), len(recipe_cards)))
                        
                        for card in random_cards:
                            title_elem = card.find('h2') or card.find('h3')
                            if not title_elem:
                                continue
                            title = title_elem.text.strip()
                            
                            desc_elem = card.find('div', class_='rte')
                            description = desc_elem.text.strip()[:150] + "..." if desc_elem else ""
                            
                            inspiration = f"- {title}: {description} (Source: Saratoga Olive Oil Co.)"
                            if inspiration not in inspiration_recipes:
                                inspiration_recipes.append(inspiration)
                except Exception as e:
                    logger.error(f"Error fetching random recipes: {str(e)}")
            
            return "\n".join(inspiration_recipes)
            
        except Exception as e:
            logger.error(f"Error searching Saratoga for inspiration: {str(e)}")
            return ""