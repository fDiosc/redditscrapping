"""Force reanalysis of the suspicious post with NEW spam detection."""
from radar.storage.db import get_connection, save_analysis, get_product, get_comments
from radar.process.ai_analysis import analyze_post_with_ai
from radar.process.truncation import build_unified_context
import sqlite3
import json

# Get product info
product = get_product('sonarpro')

conn = get_connection()
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Find the specific suspicious post
# Use explicit column naming for pa.relevance_score to avoid collision with p.relevance_score (if exists)
c.execute("""
    SELECT p.*, 
           pa.relevance_score as actual_score, 
           pa.semantic_similarity as actual_fit, 
           pa.ai_analysis
    FROM posts p
    JOIN post_analysis pa ON p.id = pa.post_id
    WHERE pa.product_id = 'sonarpro' 
    ORDER BY pa.relevance_score DESC 
    LIMIT 30
""")
rows = c.fetchall()
if not rows:
    print("No posts found")
    exit()

print(f"Found {len(rows)} posts. Starting reanalysis with INTENT-BASED detection...\n")

for i, row in enumerate(rows, 1):
    post = dict(row)
    print(f"--- [{i}/{len(rows)}] ---")
    print(f"Post: {post['title']}")
    print(f"   Score: {float(post['actual_score']):.1f}")
    
    # Build context and run NEW analysis
    comments = get_comments(post['id'])
    unified = build_unified_context(post, comments)

    print(f"   Context size: {len(unified)} characters. Running AI...")

    result = "No result"
    try:
        def analyze_with_sincerity(text, prod):
            import openai
            from radar.config import OPENAI_API_KEY
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            # Use a clean string without leading indentation
            sys_instructions = (
                "You are a strict Reddit moderator trained to kill 'Pure/Shell Ads' while allowing 'Insightful Founders'.\n\n"
                "SPAM DETECTION PHILOSOPHY:\n"
                "- Focus on INTENT & VALUE: Is the author sharing hard-won insights and providing value, or is this a generic 'thin' shell for a link?\n\n"
                "IS_SPAM_OR_AD = TRUE (PURE MARKETING / 'SHELL' AD):\n"
                "- Generic Script: Uses a 'Problem/Solution' template with no specific or unique insights.\n"
                "- Low Effort: The post looks like it could be copy-pasted for any product.\n"
                "- Primary Goal: Pricing validation ('Would you pay $X?') or landing page clicks without providing any community value.\n\n"
                "IS_SPAM_OR_AD = FALSE (AUTHENTIC STORY / VALUE-DRIVEN PROMOTION):\n"
                "- Deep Insight: Sharing specific learnings, data, or technical 'war stories' (e.g., 'I talked to 10 people and found X, Y, Z').\n"
                "- Discussion-First: Even if they mention their product/waitlist at the end, the post stands alone as valuable content.\n\n"
                "CRITICAL: For SonarPro, founders sharing specific struggles/learnings about validation and outreach are HIGH-QUALITY LEADS. Only flag them as spam if they are providing ZERO value other than a link.\n\n"
                "You MUST respond in valid JSON format with fields: is_spam_or_ad (bool), spam_indicators (list), pain_point_summary (str)."
            )
            
            user_msg = f"PRODUCT: {prod['name']}\nDESCRIPTION: {prod['description']}\n\nTHREAD TO ANALYZE:\n{text}"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {"role": "system", "content": sys_instructions},
                    {"role": "user", "content": user_msg}
                ],
                response_format={"type": "json_object"},
                temperature=0
            )
            return response.choices[0].message.content

        result = analyze_with_sincerity(unified, product)
        
        # Parse and show result summary
        ai = json.loads(result)
        status = "SPAM/AD" if ai.get('is_spam_or_ad') else "OK"
        print(f"   Result: {status}")
        if ai.get('is_spam_or_ad'):
            print(f"   Indicators: {ai.get('spam_indicators')}")
            
        # Save to DB
        save_analysis(post['id'], 'sonarpro', product['user_id'], {
            'relevance_score': post['actual_score'],
            'semantic_similarity': post['actual_fit'],
            'community_score': post.get('community_score', 0),
            'ai_analysis': result,
            'signals_json': post.get('signals_json', '{}'),
            'last_processed_score': post.get('score', 0),
            'last_processed_comments': post.get('num_comments', 0)
        })
        print(f"   Saved to DB")
        
    except Exception as e:
        print(f"   Error processing post {post['id']}: {e}")

print(f"\nAll {len(rows)} posts processed! Refresh the UI.")
conn.close()
