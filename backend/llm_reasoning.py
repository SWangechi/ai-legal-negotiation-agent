import os
import json
import re
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=API_KEY)

def _extract_json(text: str):
    """
    Extract JSON object from text (handles code fences and plain JSON).
    Returns dict or None.
    """
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

def generate(prompt: str, temperature: float = 0.3, max_tokens: int = 800, retries: int = 3, backoff: float = 1.2):
    """
    Synchronous call to OpenAI Chat Completion. Returns a dict with at least keys:
    {"revised_clause": str, "rationale": str}
    """
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert Kenyan legal negotiation assistant. Return only valid JSON as requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = resp.choices[0].message.content.strip()
            parsed = _extract_json(content)
            if parsed and isinstance(parsed, dict):
                
                return {
                    "revised_clause": parsed.get("revised_clause", parsed.get("revision", content)),
                    "rationale": parsed.get("rationale", parsed.get("reasoning", ""))
                }
            
            return {"revised_clause": content, "rationale": "Model returned non-JSON text."}
        except Exception as e:
            last_exc = e
            time.sleep(backoff * attempt)
            continue
    return {"revised_clause": "⚠️ OpenAI error.", "rationale": str(last_exc)}
