import sqlite3
import json
import math
import os
from typing import List, Dict, Any

# Replication of config parameters from radar/config.py
DATABASE_PATH = "data/radar.db"
INTENT_SIGNALS = {
    "seeking_tool": ["looking for", "is there a tool", "recommend", "best app for", "any tool", "how can i", "app to"],
    "complaint": ["frustrated", "hate", "why is it so hard", "horrible experience", "pain in the", "problem with", "issue", "scam", "wrong"],
    "comparison": ["vs", "alternative to", "switched from", "better than", "instead of"],
}

SCORING_CONFIG = {
    "intent_weights": {
        "seeking_tool": 5.0,
        "complaint": 3.0,
        "comparison": 2.0
    },
    "structural_gating": {
        "min_semantic_fit": 0.20,
        "require_product_context": True
    },
    "relevance_weights": {
        "semantic_multiplier": 15.0,
        "intensity_multiplier": 1.0
    }
}

def detect_signals(text: str, product_pain: List[str], product_intent: List[str]) -> Dict[str, Any]:
    text_lower = text.lower()
    detected_intents = []
    
    # Check general intent
    for intent, keywords in INTENT_SIGNALS.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_intents.append(intent)
    
    # Check product-specific
    matched_pain = [kw for kw in product_pain if kw.lower() in text_lower]
    matched_intent = [kw for kw in product_intent if kw.lower() in text_lower]
    
    return {
        "intents": detected_intents,
        "product_matches": {
            "pain_points": matched_pain,
            "intents": matched_intent
        }
    }

def calculate_intensity(num_comments: int, reddit_score: int) -> float:
    intensity = (math.log10(num_comments + 1) * 3.0) + math.log10(max(reddit_score, 0) + 1)
    return intensity

def classify_relevance(detected_intents: List[str]) -> float:
    score = 0.0
    weights = SCORING_CONFIG["intent_weights"]
    for intent in detected_intents:
        score += weights.get(intent, 0)
    return score

USER_ID = "user_38AZ6aLnRe6N9Oe22TjNdpn5DFF"

def debug_scoring(post_id: str, product_id: str, f_out):
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get Product
    cursor.execute("SELECT * FROM products WHERE id = ? AND user_id = ?", (product_id, USER_ID))
    product = cursor.fetchone()
    if not product:
        f_out.write(f"Product {product_id} for user {USER_ID} not found\n")
        return

    product_pain = json.loads(product['pain_signals'])
    product_intent = json.loads(product['intent_signals'])

    # Get Post and its Analysis
    cursor.execute("""
        SELECT p.title, p.body, p.score, p.num_comments, pa.semantic_similarity AS analysis_sim
        FROM posts p 
        JOIN post_analysis pa ON p.id = pa.post_id 
        WHERE p.id = ? AND pa.product_id = ? AND pa.user_id = ?
    """, (post_id, product_id, USER_ID))
    post = cursor.fetchone()
    if not post:
        f_out.write(f"Post {post_id} or analysis for {product_id} not found for user {USER_ID}\n")
        return

    f_out.write(f"\n{'='*80}\n")
    f_out.write(f"DEBUGGING POST: {post['title']}\n")
    f_out.write(f"ID: {post_id}\n")
    f_out.write(f"{'='*80}\n")

    # 1. Similarity
    similarity = post['analysis_sim'] or 0.0
    weighted_sim = similarity * SCORING_CONFIG['relevance_weights']['semantic_multiplier']
    f_out.write(f"1. SEMANTIC FIT: {similarity*100:.1f}%\n")
    f_out.write(f"   Contribution: {weighted_sim:.2f} (multiplier: 15.0)\n")

    # 2. Intensity
    intensity = calculate_intensity(post['num_comments'], post['score'])
    f_out.write(f"2. COMMUNITY INTENSITY: {intensity:.2f}\n")
    f_out.write(f"   (Reddit Score: {post['score']}, Comments: {post['num_comments']})\n")

    # Correct Baseline simulation: 0.50 instead of 0.20
    SIMULATED_BASELINE = 0.50
    
    # 3. SIGNALS AND GATING
    unified_text = f"{post['title']} {post['body']}"
    signals = detect_signals(unified_text, product_pain, product_intent)
    
    has_product_context = len(signals['product_matches']['pain_points']) > 0 or len(signals['product_matches']['intents']) > 0
    
    f_out.write(f"3. SIGNALS AND GATING:\n")
    f_out.write(f"   Detected Intents: {signals['intents']}\n")
    f_out.write(f"   Product Keywords Matched: {signals['product_matches']}\n")
    f_out.write(f"   Has Product Context? {'YES' if has_product_context else 'NO'}\n")
    f_out.write(f"   Similarity >= New Baseline ({SIMULATED_BASELINE})? {'YES' if similarity >= SIMULATED_BASELINE else 'NO'} ({similarity:.2f})\n")
    
    # Simulation: Require EITHER product context OR a very high similarity
    if has_product_context or similarity >= SIMULATED_BASELINE:
        intent_bonus = classify_relevance(signals['intents'])
        f_out.write(f"   GATE STATUS -> Intent Bonus applied: +{intent_bonus:.1f}\n")
    else:
        intent_bonus = 0.0
        f_out.write(f"   GATE STATUS -> Intent Bonus blocked: 0.0 (Reason: No context and Similarity < {SIMULATED_BASELINE})\n")

    # 4. Final Total
    total = weighted_sim + intensity + intent_bonus
    f_out.write(f"\nFINAL CALCULATED SCORE: {total:.2f}\n")
    
    # Compare with stored score
    cursor.execute("SELECT relevance_score FROM post_analysis WHERE post_id = ? AND product_id = ?", (post_id, product_id))
    stored = cursor.fetchone()
    if stored:
        f_out.write(f"STORED SCORE IN DB: {stored['relevance_score']:.2f}\n")
    
    conn.close()

if __name__ == "__main__":
    groups = {
        "IRRELEVANT (Noise)": ["t3_1q97dvq", "t3_1q96fy4", "t3_1q8k3uh"],
        "TRICKY NOISE (Comment Match)": ["t3_1q8a99r"],
        "RELEVANT (True Leads)": ["t3_1q9xv0c", "t3_1qaxjm8"]
    }
    
    with open("debug_report.txt", "w", encoding="utf-8") as f:
        for group_name, pids in groups.items():
            f.write(f"\n\n### {group_name} ###\n")
            for pid in pids:
                debug_scoring(pid, "socialgenius", f)
                
    print("Debug report written to debug_report.txt")
