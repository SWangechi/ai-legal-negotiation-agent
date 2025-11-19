"""
embedding_manager.py
---------------------
Handles embedding generation and ChromaDB storage for adaptive learning.
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.Client(Settings(persist_directory="data/chroma_memory"))

collection = client.get_or_create_collection("feedback_memory")


def generate_embedding(text: str):
    """Generate a vector embedding for text."""
    return model.encode([text])[0].tolist()


def store_in_chromadb(text: str, metadata: dict, embedding: list):
    """Store feedback text and metadata in ChromaDB."""
    collection.add(
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata],
        ids=[f"feedback_{metadata['timestamp']}"]
    )
print(f"Stored feedback from {metadata['username']} in ChromaDB.")
    
    