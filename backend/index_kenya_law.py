from backend.memory_manager import MemoryManager

def main():
    print("⚖️ Indexing Kenyan Legal References into ChromaDB...")
    mm = MemoryManager()
    n = mm.ingest_kenya_law_jsonl(
        folder_path="data/legal/kenya_summaries",
        collection_name="kenya_legal_refs"
    )
    print(f"✅ Indexed {n} legal documents into 'kenya_legal_refs' collection.")

if __name__ == "__main__":
    main()
