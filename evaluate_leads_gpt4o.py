import sqlite3
import json
import os
from openai import OpenAI
from radar.config import OPENAI_API_KEY

# Configuration
DB_PATH = "data/radar.db"
USER_ID = "user_38AZ6aLnRe6N9Oe22TjNdpn5DFF"
PRODUCT_ID = "socialgenius"
OUTPUT_FILE = "ai_lead_evaluation.md"
MODEL = "gpt-4o"

client = OpenAI(api_key=OPENAI_API_KEY)

def get_product_info(cursor):
    cursor.execute("SELECT name, description FROM products WHERE id = ? AND user_id = ?", (PRODUCT_ID, USER_ID))
    return cursor.fetchone()

def get_top_leads(cursor):
    query = """
    SELECT 
        pa.post_id, 
        pa.relevance_score, 
        pa.semantic_similarity,
        p.title, 
        p.body
    FROM post_analysis pa
    JOIN posts p ON pa.post_id = p.id
    WHERE pa.product_id = ? AND pa.user_id = ?
    ORDER BY pa.relevance_score DESC
    LIMIT 30
    """
    cursor.execute(query, (PRODUCT_ID, USER_ID))
    return cursor.fetchall()

def get_post_comments(cursor, post_id):
    cursor.execute("SELECT body FROM comments WHERE post_id = ? ORDER BY score DESC LIMIT 10", (post_id,))
    comments = cursor.fetchall()
    return "\n---\n".join([c[0] for c in comments])

def evaluate_lead(product_info, post_content):
    name, desc = product_info
    
    system_prompt = f"""
    You are a lead qualification expert. Your task is to evaluate if a Reddit post is a GOOD lead for a specific product.
    
    PRODUCT: {name}
    DESCRIPTION: {desc}
    
    Evaluate based on:
    1. Intent: Is the user looking for a solution?
    2. Pain Point: Does the user have a problem this product solves?
    3. Context: Is the thread relevant to the product's niche?
    4. You can be more generous in your analysis, IF someone is seeking for a solution that matches with our product, being an automated version or human one, it may be a lead as the user may not know our product exists.
    
    Respond in Markdown format:
    ### [Post Title or ID]
    **AI Judgment:** [AGREE/DISAGREE] (Agree = Good Lead, Disagree = Not a Lead)
    **Explanation:** [Brief 2-3 sentence explanation]
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"POST CONTENT:\n{post_content}"}
            ],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"### Error evaluating lead\n**Error:** {str(e)}"

def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print(f"Fetching product info for {PRODUCT_ID}...")
    product_info = get_product_info(cursor)
    if not product_info:
        print("Product not found.")
        return
    
    print("Fetching top 30 leads...")
    leads = get_top_leads(cursor)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"# AI Lead Evaluation Report for {product_info[0]}\n")
        f.write(f"Evaluating the top 30 leads using {MODEL}.\n\n")
        
        for i, lead in enumerate(leads, 1):
            post_id, score, sim, title, body = lead
            print(f"[{i}/30] Evaluating {post_id}: {title[:50]}...")
            
            comments = get_post_comments(cursor, post_id)
            full_content = f"TITLE: {title}\nBODY: {body}\n\nCOMMENTS:\n{comments}"
            
            evaluation = evaluate_lead(product_info, full_content)
            
            f.write(f"## Lead #{i}: {post_id} (Internal Score: {score:.2f})\n")
            f.write(evaluation)
            f.write("\n\n---\n\n")
            f.flush()
            
    conn.close()
    print(f"Done! Evaluation saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
