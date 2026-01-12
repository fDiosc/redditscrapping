from typing import Dict, Any, List
from radar.storage.db import save_product_record, get_product
from radar.process.semantic import generate_product_context
from radar.process.embeddings import get_embeddings

def upsert_product(product_data: Dict[str, Any]):
    """Save product and immediately regenerate its semantic embedding context."""
    # 1. Generate the rich context string
    rich_context = generate_product_context(product_data)
    product_data['embedding_context'] = rich_context
    
    # 2. Get new embedding (optional: we could just store the context and let SemanticEngine handle it)
    # But storing it here ensures we only call OpenAI once per edit.
    # Note: We don't store the full vector in SQLite (usually too big), 
    # but we store the context which SemanticEngine will use.
    
    # 3. Save to DB
    save_product_record(product_data)
    
    return product_data

def get_all_products_with_stats():
    """Return products with basic stats metadata (stub for now)."""
    from radar.storage.db import get_products
    return get_products()
