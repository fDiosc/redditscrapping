import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "python:radar:v0.1.0")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Storage Configuration
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/radar.db")
CHROMA_PATH = os.getenv("CHROMA_PATH", "data/chroma")

# Target Subreddits
SUBREDDITS = {
    # === CORE: SaaS/Business ===
    "saas": "SaaS general",
    "startups": "Startup founders",
    "entrepreneur": "Entrepreneurs",
    "indiehackers": "Indie hackers",
    
    # === ProfitDoctor: E-commerce ===
    "shopify": "Shopify merchants",
    "ecommerce": "E-commerce general",
    "dropship": "Dropshipping",
    "AmazonSeller": "Amazon sellers",
    "FulfillmentByAmazon": "FBA sellers",
    "PPC": "Ads/margins discussion",
    
    # === SocialGenius: Social Media ===
    "socialmedia": "Social media general",
    "Instagram": "Instagram users",
    "instagrammarketing": "Instagram marketing",
    "socialmediamarketing": "SMM general",
    "ContentCreators": "Content creators",
    "NewTubers": "YouTube creators",
    
    # === PromptLocker: AI/Prompts ===
    "ChatGPT": "ChatGPT users",
    "PromptEngineering": "Prompt engineering",
    "ClaudeAI": "Claude users",
    "LocalLLaMA": "Local LLM users",
    "OpenAI": "OpenAI general",
    "PromptDesign": "Prompt design",
    "aipromptprogramming": "AI prompts",
}

# Intent Keywords
INTENT_SIGNALS = {
    "seeking_tool": ["looking for", "is there a tool", "recommend", "best app for", "any tool", "how can i", "app to"],
    "complaint": ["frustrated", "hate", "why is it so hard", "horrible experience", "pain in the", "problem with", "issue", "scam", "wrong"],
    "comparison": ["vs", "alternative to", "switched from", "better than", "instead of"],
}

# Product-Specific Keywords
PRODUCT_SIGNALS = {
    "profitdoctor": {
        "pain": [
            "shopify profit", "profit margin", "losing money",
            "cogs tracking", "true profit", "shipping costs eating",
            "don't know if profitable", "spreadsheet nightmare",
            "fulfillment", "checkout", "orders", "customer", "selling"
        ],
        "intent": ["profit calculator", "profit tracker", "profit app shopify", "analytics"]
    },
    "socialgenius": {
        "pain": [
            "content ideas", "what to post", "posting schedule",
            "social media burnout", "creating content takes forever"
        ],
        "intent": ["content generator", "social media tool", "instagram scheduler"]
    },
    "promptlocker": {
        "pain": [
            "organize prompts", "lost my prompt", "reuse prompts",
            "prompt library", "save prompts", "prompt chaos"
        ],
        "intent": ["prompt manager", "prompt organizer", "prompt library", "prompt vault"]
    }
}
