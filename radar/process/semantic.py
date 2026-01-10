import numpy as np
from typing import List, Dict, Any
from radar.process.embeddings import get_embeddings
from radar.products import PRODUCTS

def calculate_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two normalized vectors."""
    # OpenAI embeddings are normalized to length 1.0 by default, 
    # so dot product is equivalent to cosine similarity.
    return np.dot(vec1, vec2)

class SemanticEngine:
    def __init__(self):
        self.product_embeddings = {}
        self._initialize_products()

    def _initialize_products(self):
        """Pre-calculate embeddings for all products in the knowledge base."""
        for key, product in PRODUCTS.items():
            # Use name + description for a rich embedding
            text = f"{product['name']}: {product['description']}"
            emb = get_embeddings([text])[0]
            self.product_embeddings[key] = emb

    def get_product_fit(self, post_embedding: List[float], product_key: str) -> float:
        """Get similarity score between a post and a specific product."""
        product_emb = self.product_embeddings.get(product_key)
        if not product_emb:
            return 0.0
        return calculate_similarity(post_embedding, product_emb)
