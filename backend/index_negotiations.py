import json, uuid
from pathlib import Path
from backend.memory_manager import MemoryManager

mm = MemoryManager()
COL = "negotiation_cases"

for p in Path("data/negotiation_logs").glob("*.json"):
    obj = json.loads(p.read_text())
    text = (
        f"SCENARIO: {obj['scenario']}\n"
        f"DIALOGUE: {' '.join(obj['negotiation_dialogue'])}\n"
        f"OUTCOME: {obj['mediator_resolution_summary']}\n"
        f"FINAL_CLAUSE: {obj['proposed_revised_clause']}"
    )
    mm.add(COL, str(uuid.uuid4()), text, metadata={"file": p.name})

print("✅ Negotiation memory indexed.")
