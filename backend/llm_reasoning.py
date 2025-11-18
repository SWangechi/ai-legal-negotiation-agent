import os
import json
import re
import time
from openai import OpenAI
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# ==============================
# ⚙️ Environment Setup
# ==============================
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
CHROMA_PATH = os.getenv("CHROMA_MEMORY_PATH", "data/memory_store")

client = OpenAI(api_key=API_KEY)

# ==============================
# 🧠 Initialize ChromaDB Memory (Feedback Adaptive Layer)
# ==============================
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
chroma_client = chromadb.Client(Settings(persist_directory=CHROMA_PATH))
feedback_memory = chroma_client.get_or_create_collection(
    "feedback_memory",
    embedding_function=embedding_fn
)

# ==============================
# 🧩 Helper Functions
# ==============================
def _extract_json(text: str):
    """Extract JSON object from text (handles code fences and plain JSON)."""
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        candidate = m.group(0)
        try:
            return json.loads(candidate)
        except Exception:
            pass
    return None

def _get_feedback_context(query_text: str, top_k: int = 3) -> str:
    """Retrieve top feedback memories most related to the current contract or clause."""
    try:
        results = feedback_memory.query(
            query_texts=[query_text],
            n_results=top_k
        )
        if not results or not results.get("documents") or not results["documents"][0]:
            return ""
        
        memories = results["documents"][0]
        context = "\n\n".join(
            [f"User Feedback Memory {i+1}: {m}" for i, m in enumerate(memories)]
        )
        return f"\n\n🧠 Learned Feedback Insights:\n{context}\n"
    except Exception as e:
        return f"\n\n⚠️ No feedback context available ({e})"

# ==============================
# 🧠 Core LLM Reasoning Function
# ==============================
def generate(prompt: str, temperature: float = 0.3, max_tokens: int = 800, retries: int = 3, backoff: float = 1.2):
    """
    Generates negotiation insights with adaptive memory from prior feedback.
    Returns a dict with {"revised_clause": str, "rationale": str}.
    """
    # Step 1: Retrieve adaptive memory context
    memory_context = _get_feedback_context(prompt)

    # Step 2: Combine prompt with memory context
    adaptive_prompt = (
        "You are an expert Kenyan legal negotiation and mediation assistant.\n"
        "Your goal is to propose fair, lawful, and mutually beneficial revisions.\n"
        "Incorporate the following learned insights from prior feedback when analyzing clauses:\n"
        f"{memory_context}\n\n"
        f"Now analyze and respond to this clause:\n{prompt}"
    )

    # Step 3: Send to LLM with retry logic
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Kenyan legal negotiation assistant. Return only valid JSON as requested."},
                    {"role": "user", "content": adaptive_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = resp.choices[0].message.content.strip()
            parsed = _extract_json(content)

            if parsed and isinstance(parsed, dict):
                return {
                    "revised_clause": parsed.get("revised_clause", parsed.get("revision", content)),
                    "rationale": parsed.get("rationale", parsed.get("reasoning", "")),
                    "memory_used": bool(memory_context.strip())
                }

            # fallback if not JSON
            return {
                "revised_clause": content,
                "rationale": "Model returned non-JSON text.",
                "memory_used": bool(memory_context.strip())
            }

        except Exception as e:
            last_exc = e
            time.sleep(backoff * attempt)
            continue

    return {"revised_clause": "⚠️ OpenAI error.", "rationale": str(last_exc), "memory_used": False}
# Example usage:
# result = generate("Clause text to analyze...")
# print(result)
