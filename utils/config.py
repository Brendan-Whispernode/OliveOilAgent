import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    
    required_vars = [
        'OPENAI_API_KEY',
        'SHOPIFY_ACCESS_TOKEN',
        'SHOPIFY_STORE_URL',
        'DALLE_API_KEY'
    ]
    
    config = {}
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f"Missing required environment variable: {var}")
        config[var] = value
    
    return config