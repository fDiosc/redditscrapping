"""
Product Extractor Service - Uses LLM to extract structured product information from website content.
"""
import openai
import json
from typing import Dict, Any, Optional
from radar.config import OPENAI_API_KEY
from radar.services.url_extractor import WebsiteExtractor

client = openai.OpenAI(api_key=OPENAI_API_KEY)

EXTRACTION_SYSTEM_PROMPT = """You are a product analyst extracting structured information from a website.

Given website content, extract the following information in JSON format:

{
    "name": "Product/Company name (short, clean)",
    "description": "A detailed 3-4 sentence description explaining: what the product/service does, who it's for, and what makes it unique. Be specific and include key features or benefits mentioned on the site.",
    "category": "One of: saas, ecommerce, marketing, ai_tools, finance, health, education, productivity, consulting, other",
    "pain_signals": ["List of 6-10 specific problems/pain points the product solves. Think about what frustrations or challenges users have BEFORE finding this product. Use lowercase."],
    "intent_signals": ["List of 4-6 search terms/queries users might type to find this type of product. Be specific to this product category."],
    "target_audience": "Detailed description of the ideal customer (industry, role, company size, etc.)",
    "competitors": ["List of 2-3 likely competitors if identifiable"],
    "confidence": 0.0-1.0 (how confident you are in the extraction based on available content)
}

CRITICAL RULES:
- ONLY use information that is EXPLICITLY stated in the provided content
- DO NOT invent, assume, or hallucinate any information not present in the text
- If the content is empty, corrupted, or unreadable, return: {"error": "Unable to extract - content not readable", "confidence": 0}
- If you cannot determine what the product does from the text, set confidence below 0.3

Guidelines:
- For description, be DETAILED but ONLY based on actual content provided
- For pain_signals, focus on problems mentioned or implied in the actual content
- For intent_signals, derive from what the product actually does per the content
- All text should be lowercase except proper nouns
- Return ONLY valid JSON, no additional text"""

EXTRACTION_USER_PROMPT = """Extract product information from this website content:

URL: {url}
Title: {title}
Meta Description: {meta_description}

Hero/Value Proposition:
{hero_text}

Main Headings:
{headings}

Features:
{features}

Additional Context:
{full_text}"""


class ProductExtractor:
    """Extracts structured product information using LLM."""
    
    def __init__(self):
        self.website_extractor = WebsiteExtractor()
    
    async def extract_from_url(self, url: str) -> Dict[str, Any]:
        """
        Full pipeline: fetch URL -> extract content -> LLM analysis.
        
        Returns:
            Dict with extracted product data or error
        """
        # Step 1: Fetch and parse website
        website_data = await self.website_extractor.extract(url)
        
        if "error" in website_data:
            return website_data
        
        # Check if website is a SPA with minimal content
        full_text = website_data.get('full_text', '')
        if len(full_text) < 100:
            return {
                "error": "This website appears to be a Single Page Application (SPA) that loads content via JavaScript. Please fill in the product details manually.",
                "is_spa": True
            }
        
        # Step 2: Extract with LLM
        return await self._extract_with_llm(website_data)
    
    async def _extract_with_llm(self, website_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to extract structured product data."""
        
        # Build prompt from website data
        user_prompt = EXTRACTION_USER_PROMPT.format(
            url=website_data.get('url', ''),
            title=website_data.get('title', ''),
            meta_description=website_data.get('meta_description', ''),
            hero_text=website_data.get('hero_text', '')[:1200],
            headings='\n'.join([website_data.get('h1', '')] + website_data.get('h2s', [])[:10]),
            features='\n'.join(website_data.get('features', [])[:15]),
            full_text=website_data.get('full_text', '')[:4000]
        )
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.4,
                max_tokens=1500
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Add source URL
            result['source_url'] = website_data.get('url', '')
            result['extraction_tokens'] = response.usage.total_tokens
            
            # Warn if confidence is low
            if result.get('confidence', 0) < 0.5:
                result['warning'] = "Low confidence extraction. Please review and adjust the details."
            
            return result
            
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse LLM response: {str(e)}"}
        except Exception as e:
            return {"error": f"LLM extraction failed: {str(e)}"}


# Synchronous wrapper
def extract_product_from_url_sync(url: str) -> Dict[str, Any]:
    """Synchronous wrapper for product extraction."""
    import asyncio
    extractor = ProductExtractor()
    return asyncio.run(extractor.extract_from_url(url))


# Subreddit suggestion based on category
SUBREDDIT_CATEGORIES = {
    "saas": ["SaaS", "startups", "entrepreneur", "indiehackers", "smallbusiness"],
    "ecommerce": ["shopify", "ecommerce", "dropship", "FulfillmentByAmazon", "AmazonSeller", "Etsy"],
    "marketing": ["socialmedia", "marketing", "PPC", "SEO", "socialmediamarketing", "DigitalMarketing"],
    "ai_tools": ["ChatGPT", "OpenAI", "PromptEngineering", "LocalLLaMA", "artificial", "MachineLearning"],
    "finance": ["personalfinance", "FinancialPlanning", "investing", "smallbusiness", "Entrepreneur"],
    "health": ["HealthIT", "digitalhealth", "fitness", "nutrition", "mentalhealth"],
    "education": ["edtech", "OnlineLearning", "education", "Teachers", "eLearning"],
    "productivity": ["productivity", "GetMotivated", "productivity", "lifehacks", "Entrepreneur"],
    "other": ["startups", "Entrepreneur", "SideProject", "smallbusiness"]
}


def suggest_subreddits(category: str, pain_signals: list = None, intent_signals: list = None) -> list:
    """
    Suggest relevant subreddits based on product category and signals.
    
    Returns:
        List of suggested subreddit names (without r/ prefix)
    """
    suggestions = set()
    
    # Get category-based suggestions
    category_subs = SUBREDDIT_CATEGORIES.get(category.lower(), SUBREDDIT_CATEGORIES["other"])
    suggestions.update(category_subs)
    
    # Add general entrepreneurship subs for B2B products
    if category.lower() in ["saas", "productivity", "marketing"]:
        suggestions.update(["startups", "entrepreneur", "SideProject"])
    
    return sorted(list(suggestions))
