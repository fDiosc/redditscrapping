import chromadb
from chromadb.config import Settings
from radar.config import CHROMA_PATH
from typing import List, Dict, Any

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
