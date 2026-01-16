import chromadb
from chromadb.config import Settings
from radar.config import CHROMA_PATH
from typing import List, Dict, Any, Optional

def get_client():
    return chromadb.PersistentClient(path=CHROMA_PATH)

def get_or_create_collection(name: str = "radar_posts"):
    client = get_client()
    return client.get_or_create_collection(name=name)

def add_embeddings(collection, ids: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]], documents: List[str]):
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents
    )

def query_collection(collection, query_embeddings: List[List[float]], n_results: int = 10):
    return collection.query(
        query_embeddings=query_embeddings,
        n_results=n_results
    )


# ============================================
# Enhanced ChromaDB Query Functions (Phase 7)
# ============================================

def query_similar_posts(
    query_embedding: List[float],
    n_results: int = 50,
    collection_name: str = "radar_posts",
    where_filter: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Query for posts similar to a given embedding using ChromaDB's native vector search.
    
    This is more efficient than fetching all posts and computing similarity manually.
    
    Args:
        query_embedding: The embedding vector to search with (e.g., product embedding)
        n_results: Number of results to return
        collection_name: Name of the ChromaDB collection
        where_filter: Optional metadata filter (e.g., {"source": "shopify"})
    
    Returns:
        Dict with 'ids', 'distances', 'metadatas', 'documents'
    """
    client = get_client()
    collection = client.get_or_create_collection(name=collection_name)
    
    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": n_results,
        "include": ["metadatas", "documents", "distances"]
    }
    
    if where_filter:
        query_params["where"] = where_filter
    
    results = collection.query(**query_params)
    
    # Flatten single-query results
    return {
        "ids": results["ids"][0] if results["ids"] else [],
        "distances": results["distances"][0] if results["distances"] else [],
        "metadatas": results["metadatas"][0] if results["metadatas"] else [],
        "documents": results["documents"][0] if results["documents"] else []
    }


def get_collection_count(collection_name: str = "radar_posts") -> int:
    """Get the number of items in a collection."""
    client = get_client()
    collection = client.get_or_create_collection(name=collection_name)
    return collection.count()


def delete_embeddings(collection_name: str, ids: List[str]):
    """Delete embeddings by ID from a collection."""
    client = get_client()
    collection = client.get_or_create_collection(name=collection_name)
    collection.delete(ids=ids)

