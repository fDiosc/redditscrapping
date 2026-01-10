from typing import List, Dict, Any
import json
from radar.config import INTENT_SIGNALS, PRODUCT_SIGNALS

def detect_signals(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    detected_intents = []
    
    # Check general intent
    for intent, keywords in INTENT_SIGNALS.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_intents.append(intent)
    
    # Check product-specific pain points
    product_matches = {}
    for product, signals in PRODUCT_SIGNALS.items():
        matched_pain = [kw for kw in signals['pain'] if kw in text_lower]
        matched_intent = [kw for kw in signals['intent'] if kw in text_lower]
        
        if matched_pain or matched_intent:
            product_matches[product] = {
                "pain_points": matched_pain,
                "intents": matched_intent
            }
            
    return {
        "intents": detected_intents,
        "product_matches": product_matches
    }

def calculate_intensity(post_data: Dict[str, Any]) -> float:
    """Calculate community pain intensity based on comments and score."""
    import math
    num_comments = post_data.get('num_comments', 0)
    reddit_score = post_data.get('score', 0)
    
    # log10(comments + 1) * weight + log10(score + 1)
    intensity = (math.log10(num_comments + 1) * 3.0) + math.log10(max(reddit_score, 0) + 1)
    return intensity

def classify_relevance(post_data: Dict[str, Any], signals: Dict[str, Any]) -> float:
    """Legacy relevance scorer (to be replaced by hybrid in CLI)."""
    # KEEPING THIS FOR BACKWARD COMPATIBILITY BUT WE WILL OVERRIDE IN CLI
    score = 0.0
    intent_weights = {"seeking_tool": 5.0, "complaint": 3.0, "comparison": 2.0}
    for intent in signals['intents']:
        score += intent_weights.get(intent, 0)
    return score
