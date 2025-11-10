import os
import json
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

load_dotenv()

class MemoryManager:
    def __init__(self, db_path=None):
        chroma_path = db_path or os.getenv("CHROMADB_PATH", "./data/memory_store")
        Path(chroma_path).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.embedder = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        )

    def get_or_create_collection(self, name: str):
        return self.client.get_or_create_collection(
            name=name,
            embedding_function=self.embedder
        )

    def add_documents(self, collection_name: str, ids, docs, metadatas=None, embeddings=None):
        col = self.get_or_create_collection(collection_name)
        if embeddings:
            col.upsert(ids=ids, documents=docs, metadatas=metadatas or [], embeddings=embeddings)
        else:
            col.upsert(ids=ids, documents=docs, metadatas=metadatas or [])

    def search(self, query: str, collection_name: str = "kenya_legal_refs", n_results: int = 3):
        if not query or not isinstance(query, str):
            return {"documents": [], "metadatas": [], "distances": []}

        try:
            col = self.get_or_create_collection(collection_name)
            res = col.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            documents = res.get("documents", [[]])[0] if isinstance(res.get("documents"), list) else []
            metadatas = res.get("metadatas", [[]])[0] if isinstance(res.get("metadatas"), list) else []
            distances = res.get("distances", [[]])[0] if isinstance(res.get("distances"), list) else []
            return {"documents": documents, "metadatas": metadatas, "distances": distances}
        except Exception as e:
            print(f"⚠️ Memory search error: {e}")
            return {"documents": [], "metadatas": [], "distances": []}

    def ingest_kenya_law_jsonl(self, folder_path="data/legal/kenya_summaries", collection_name="kenya_legal_refs"):
        p = Path(folder_path)
        if not p.exists():
            print(f"⚠️ No Kenya law folder at {folder_path}")
            return 0

        docs, ids, metas = [], [], []
        for f in p.glob("*.jsonl"):
            for line in f.read_text(encoding="utf-8").splitlines():
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                ids.append(row.get("id") or os.urandom(8).hex())
                docs.append(row.get("summary", row.get("text", "")))
                metas.append({"title": row.get("title"), "section": row.get("section_no"), "source": f.name})
        if ids:
            self.add_documents(collection_name, ids, docs, metadatas=metas)
            print(f"✅ Indexed {len(ids)} legal documents into '{collection_name}'")
            return len(ids)
        return 0
