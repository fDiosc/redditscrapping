import openai
import logging
from typing import Optional, Dict, Any
from radar.config import OPENAI_API_KEY
from radar.storage.db import get_post, get_product, get_analysis, save_generated_response, get_generated_responses, update_response_feedback

logger = logging.getLogger(__name__)

RESPONSE_SYSTEM_PROMPT = """You are a helpful Reddit community member who genuinely wants to help others.
{referral_guidance}

Your responses must:
1. Feel authentic and human - NOT like marketing copy or AI-generated
2. Provide genuine value and insight FIRST
3. Show empathy by referencing their specific situation
4. End with an engaging question to continue the conversation
5. Be 80-150 words (Reddit sweet spot for engagement)
6. SOUND LIKE A HUMAN TYPING: Use natural flow, occasional lowercase at start of sentences, and casual sentence structures.
7. NO HYPHENS: Strictly avoid using the hyphen character (-) anywhere in your response text. Use commas, periods, or just start new lines instead.

CRITICAL RULES - NEVER BREAK THESE:
* {primary_promotion_rule}
* NEVER use marketing phrases like "game-changer", "revolutionary", "amazing tool"
* NEVER start with "Hey there!" or "Great question!" (too generic)
* NEVER use bullet points or formatted lists (not natural for Reddit)
* DO reference their specific words/situation to show you read their post
* DO share genuine experiences
* DO sound like a real person who's been in their shoes
* DO use casual language, contractions, and occasional typos feel OK
* REMEMBER: NO HYPHENS (-) IN THE FINAL CONTENT.

Remember: You're a community member FIRST, not a salesperson."""

STYLE_MODIFIERS = {
    "empathetic": """
Tone: Warm, understanding, supportive
Focus: Acknowledge their feelings first, then offer perspective
Voice: Like a friend who's been through something similar
Example phrases: "I totally get it", "Been there", "That's rough"
""",
    "helpful_expert": """
Tone: Knowledgeable but approachable
Focus: Share specific actionable insights
Voice: Like a mentor or experienced colleague
Example phrases: "What worked for me was", "The key thing I learned", "One approach that helps"
""",
    "casual": """
Tone: Relaxed, conversational, friendly
Focus: Light touch, relatable
Voice: Like chatting with a peer
Example phrases: "Yeah honestly", "Haha same", "Lowkey"
""",
    "technical": """
Tone: Detailed, precise, informative
Focus: Specifics and how-tos
Voice: Like a knowledgeable community expert
Example phrases: "Specifically", "The way this works", "In practice"
""",
    "brief": """
Tone: Concise, direct, helpful
Focus: Quick value, no fluff
Voice: Like a busy person giving their best tip
Length: 40-80 words max
Example phrases: "Quick tip:", "Honestly just", "The move is"
""",
    "product_referral": """
Tone: Recommending, helpful, direct
Focus: Solving the user's problem by suggesting the product specifically
Voice: Someone who found a great tool and wants to share it
Example phrases: "I've been using {product_name}", "Check out {website_url}", "This actually solves exactly that"
"""
}

class ResponseGenerator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)

    def generate_response(self, user_id: str, post_id: str, product_id: str, style: str = "empathetic") -> Dict[str, Any]:
        """Generate a response for a user's product."""
        post = get_post(post_id)
        if not post:
            raise ValueError(f"Post {post_id} not found")
        
        product = get_product(product_id, user_id)
        if not product:
            raise ValueError(f"Product {product_id} not found for this user")
            
        analysis = get_analysis(post_id, product_id)
        if analysis and isinstance(analysis.get('ai_analysis'), str):
            try:
                import json
                ai_data = json.loads(analysis['ai_analysis'])
            except:
                ai_data = {"pain_point_summary": analysis['ai_analysis']}
        else:
            ai_data = analysis.get('ai_analysis') if analysis else {}
            if ai_data is None: ai_data = {}

        style_mod = STYLE_MODIFIERS.get(style, STYLE_MODIFIERS["empathetic"])
        
        prompt = f"""## The Reddit Post You're Responding To
Subreddit: r/{post.get('source', 'unknown')}
Title: {post['title']}

Post Content:
{post['body'][:800] if post.get('body') else '(no body)'}

---
---
## Context for the Response
Target User: u/{ai_data.get('pain_author', 'unknown')}
Source Location: {"Comment" if ai_data.get('is_from_comment') else "Main Post"}
Their Core Struggle: {ai_data.get('pain_point_summary', 'Not specified')}
Their Exact Words: "{ai_data.get('pain_quote', 'Not available')}"

---
## Style Instructions
{style_mod}

## CRITICAL: RECIPIENT AWARENESS
If the source is a "Comment", write the response as a direct reply to u/{ai_data.get('pain_author', 'unknown')}. Acknowledge that you saw their specific comment in the thread. 
If the source is the "Main Post", address the original author's post.

Write the response now (plain text, no markdown formatting):"""

        if style == "product_referral":
            referral_guidance = f"You are a big fan of {product['name']} and you want to recommend it directly because it solves the user's problem. You should mention the product name and its website ({product.get('website_url', 'the product website')}) naturally."
            primary_promotion_rule = f"DO mention that you use {product['name']} and give the link if it helps."
        else:
            referral_guidance = f"You have experience with {product['name']} but you NEVER directly promote it or mention it by name in this specific response style."
            primary_promotion_rule = "NEVER say 'I work for [product]' or 'You should try [product]'"

        system_content = RESPONSE_SYSTEM_PROMPT.format(
            product_name=product['name'],
            referral_guidance=referral_guidance,
            primary_promotion_rule=primary_promotion_rule
        )
        
        # Also ensure product name and url are available in the style modifier if needed
        style_mod = style_mod.format(product_name=product['name'], website_url=product.get('website_url', ''))

        try:
            # Using GPT-5.2 flagship with x-high reasoning effort as per docs
            response = self.client.chat.completions.create(
                model="gpt-5.2",
                messages=[
                    {"role": "developer", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                reasoning_effort="xhigh"
            )
            
            response_text = response.choices[0].message.content.strip()
            
            tokens_used = response.usage.total_tokens
            
            res_id = save_generated_response(user_id, post_id, product_id, style, response_text, tokens_used)
            
            return {
                "id": res_id,
                "response_text": response_text,
                "style": style,
                "tokens_used": tokens_used
            }
        except Exception as e:
            logger.error(f"Error calling GPT-5.2: {e}")
            raise
