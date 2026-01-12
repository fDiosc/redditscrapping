import numpy as np
import json
from typing import List, Dict, Any
from radar.process.embeddings import get_embeddings

def calculate_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two normalized vectors."""
    return np.dot(vec1, vec2)

def generate_product_context(product: Dict[str, Any]) -> str:
    """Combine name, description, and signals into a single semantic context string."""
    name = product.get('name', '')
    desc = product.get('description', '')
    
    pain = product.get('pain_signals', [])
    if isinstance(pain, str):
        try: pain = json.loads(pain)
        except: pain = []
        
    intent = product.get('intent_signals', [])
    if isinstance(intent, str):
        try: intent = json.loads(intent)
        except: intent = []
        
    context = f"Product: {name}\nDescription: {desc}\n\n"
    if pain:
        context += "Problems/Pain Points solved: " + ", ".join(pain) + "\n"
    if intent:
        context += "How users search for this / Solution intent: " + ", ".join(intent) + "\n"
        
    return context.strip()

class SemanticEngine:
    def __init__(self):
        self.product_embeddings = {}
        self._initialize_products()

    def _initialize_products(self):
        """Pre-calculate embeddings for all products from the database."""
        from radar.storage.db import get_products
        
        products = get_products()
        for product in products:
            # Generate rich context
            text = generate_product_context(product)
            
            # Save the context back to the DB record if it changed (optional but helpful)
            # For now, just generate the embedding
            emb = get_embeddings([text])[0]
            self.product_embeddings[product['id']] = emb

    def refresh_product(self, product_id: str):
        """Regenerate and cache the embedding for a specific product."""
        from radar.storage.db import get_product
        product = get_product(product_id)
        if product:
            text = generate_product_context(product)
            emb = get_embeddings([text])[0]
            self.product_embeddings[product_id] = emb

    def get_product_fit(self, post_embedding: List[float], product_key: str) -> float:
        """Get similarity score between a post and a specific product."""
        product_emb = self.product_embeddings.get(product_key)
        if not product_emb:
            return 0.0
        return calculate_similarity(post_embedding, product_emb)
