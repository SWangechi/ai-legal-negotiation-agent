import json, uuid
from pathlib import Path
from backend.memory_manager import MemoryManager

mm = MemoryManager()
COL = "kenya_law_summaries"

for p in Path("data/legal/kenya_summaries").glob("*.jsonl"):
    for line in p.read_text().splitlines():
        row = json.loads(line)
        mm.add(COL, row["id"], row["summary"], metadata={"title": row["title"], "section": row["section_no"]})

print(" Kenyan law memory indexed.")
