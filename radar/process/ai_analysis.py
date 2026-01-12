import openai
from typing import Dict, Any
from radar.config import OPENAI_API_KEY
from radar.products import PRODUCTS

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def analyze_post_with_ai(unified_text: str, product_rec: Dict[str, Any]) -> str:
    """Analyze a post with structured JSON output."""
    name = product_rec['name']
    description = product_rec['description']
    
    system_prompt = """
    You are a professional Market Research Analyst and Social Selling expert.
    Your goal is to analyze a Reddit thread (Post + Comments) and determine if it represents a high-quality lead for a specific product.
    
    You MUST respond with a valid JSON object only. No preamble, no markdown blocks.
    Structure:
    {
        "pain_point_summary": "1-2 sentence summary of the core problem",
        "pain_quote": "Exact short quote from the thread that confirms the struggle",
        "urgency": "High/Medium/Low",
        "product_relevance": 1-10 (Numeric),
        "relevance_explanation": "Why this product helps this specific user",
        "response_angle": "Suggested tone/angle for a response without being spammy",
        "confidence": 0-1 (Numeric)
    }
    """
    
    user_prompt = f"""
    PRODUCT: {name}
    DESCRIPTION: {description}
    
    THREAD CONTENT:
    {unified_text}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": "AI Error", "details": str(e)})
