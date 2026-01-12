import openai
import logging
from typing import Optional, Dict, Any
from radar.config import OPENAI_API_KEY
from radar.storage.db import get_post, get_product, get_analysis, save_generated_response, get_generated_responses, update_response_feedback

logger = logging.getLogger(__name__)

RESPONSE_SYSTEM_PROMPT = """You are a helpful Reddit community member who genuinely wants to help others.
You have experience with {product_name} but you NEVER directly promote it or mention it by name.

Your responses must:
1. Feel authentic and human - NOT like marketing copy or AI-generated
2. Provide genuine value and insight FIRST
3. Show empathy by referencing their specific situation
4. Only hint at solutions existing after establishing connection
5. End with an engaging question to continue the conversation
6. Be 80-150 words (Reddit sweet spot for engagement)
7. SOUND LIKE A HUMAN TYPING: Use natural flow, occasional lowercase at start of sentences, and casual sentence structures.
8. NO HYPHENS: Strictly avoid using the hyphen character (-) anywhere in your response text. Use commas, periods, or just start new lines instead.

CRITICAL RULES - NEVER BREAK THESE:
* NEVER say "I work for [product]" or "You should try [product]"
* NEVER use marketing phrases like "game-changer", "revolutionary", "amazing tool"
* NEVER start with "Hey there!" or "Great question!" (too generic)
* NEVER use bullet points or formatted lists (not natural for Reddit)
* DO reference their specific words/situation to show you read their post
* DO share genuine experiences and subtle hints about solutions
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
"""
}

class ResponseGenerator:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)

    def generate_response(self, post_id: str, product_id: str, style: str = "empathetic") -> Dict[str, Any]:
        post = get_post(post_id)
        if not post:
            raise ValueError(f"Post {post_id} not found")
        
        product = get_product(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
            
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
## What We Know About This Person
Their Core Struggle: {ai_data.get('pain_point_summary', 'Not specified')}
Their Exact Words: "{ai_data.get('pain_quote', 'Not available')}"

---
## Style Instructions
{style_mod}

Write the response now (plain text, no markdown formatting):"""

        system_content = RESPONSE_SYSTEM_PROMPT.format(product_name=product['name'])

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
            
            res_id = save_generated_response(post_id, product_id, style, response_text, tokens_used)
            
            return {
                "id": res_id,
                "response_text": response_text,
                "style": style,
                "tokens_used": tokens_used
            }
        except Exception as e:
            logger.error(f"Error calling GPT-5.2: {e}")
            raise
