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
    Strictly avoid using the hyphen character (-) anywhere in the text fields. Use commas or periods instead.

    Structure:
    {
        "pain_point_summary": "1-2 sentence summary of the core problem",
        "pain_quote": "Exact short quote from the thread that confirms the struggle",
        "pain_author": "Username of the person who expressed the pain (exclude u/ prefix)",
        "is_from_comment": true/false (true if the pain was found in a comment, false if in the main post title or body),
        "urgency": "High/Medium/Low",
        "product_relevance": 1-10 (Numeric),
        "relevance_explanation": "Why this product helps this specific user",
        "response_angle": "Suggested tone/angle for a response without being spammy",
        "confidence": 0-1 (Numeric),
        
        "is_spam_or_ad": true/false (CRITICAL: detect if this looks like a promotional post, marketing content, or AI-generated spam),
        "spam_indicators": ["List any indicators that suggest this is spam/marketing/AI-generated, such as: overly polished writing, product mentions, affiliate links, fake engagement patterns, templated responses, suspiciously convenient problem-solution framing"]
    }
    
    SPAM/AD DETECTION PHILOSOPHY:
    - Focus on INTENT & VALUE: Is the author sharing hard-won insights and providing value, or is this a generic "thin" shell for a link?
    
    IS_SPAM_OR_AD = TRUE (PURE MARKETING / "SHELL" AD):
    - Generic Script: Uses a "Problem/Solution" template with no specific or unique insights.
    - Low Effort: The post looks like it could be copy-pasted for any product.
    - Primary Goal: Pricing validation ("Would you pay $X?") or landing page clicks without providing any community value.

    IS_SPAM_OR_AD = FALSE (AUTHENTIC STORY / VALUE-DRIVEN PROMOTION):
    - Deep Insight: The author shares specific learnings, data, or technical "war stories" (e.g., "I talked to 10 people and found X, Y, Z").
    - Discussion-First: Even if they mention their product or waitlist at the end, the post itself stands alone as a valuable piece of content for others.
    - Authentic Voice: Shows a journey, struggles, or a genuine request for feedback on a specific technical/growth strategy.
    
    CRITICAL: For SonarPro, founders sharing specific struggles with validation/outreach are HIGH-QUALITY LEADS, even if they mention they are building a tool. Do NOT flag them as spam if they share real insights.
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
