import os
import faiss
import pickle
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE = Path(__file__).resolve().parents[1]
FAISS_DIR = BASE / "data" / "vectorstore_faiss"

FAISS_DIR.mkdir(parents=True, exist_ok=True)

INDEX_PATH = FAISS_DIR / "/data/vectorstore_faiss/documents.index"
META_PATH = FAISS_DIR / "/data/vectorstore_faiss/metadata.pkl"

def load_faiss_index(dim=1536):
    if INDEX_PATH.exists():
        index = faiss.read_index(str(INDEX_PATH))
    else:
        index = faiss.IndexFlatL2(dim)
    return index

index = load_faiss_index()

if META_PATH.exists():
    with open(META_PATH, "rb") as f:
        store = pickle.load(f)
else:
    store = {"chunks": [], "metadata": []}

def embed(text):
    emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=[text]
    )
    return np.array(emb.data[0].embedding).astype("float32")

def add_to_memory(content, meta):
    vector = embed(content).reshape(1, -1)
    index.add(vector)

    store["chunks"].append({"doc": content, **meta})
    store["metadata"].append(meta)

    persist_memory()

def persist_memory():
    faiss.write_index(index, str(INDEX_PATH))
    with open(META_PATH, "wb") as f:
        pickle.dump(store, f)

def search_memory(query, k=5):
    vec = embed(query).reshape(1, -1)
    distances, indices = index.search(vec, k)
    results = []

    for idx, dist in zip(indices[0], distances[0]):
        if idx == -1:
            continue
        results.append({
            "text": store["chunks"][idx]["doc"],
            "meta": store["metadata"][idx],
            "score": float(dist)
        })

    return results
