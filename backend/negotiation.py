import os, json, re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

STRICT_SCHEMA = {
    "dialogue": [
        {"party": "A", "text": "string"},
        {"party": "B", "text": "string"}
    ],
    "mutually_beneficial_revision": "string",
    "tradeoffs": ["string"],
    "win_win_justification": "string",
    "legal_refs": ["string"]
}

def force_json_repair(bad_text: str):
    """Second-pass attempt: Ask the LLM to fix bad JSON into correct JSON dict."""
    fix_prompt = f"""
Convert the following into valid strict JSON with keys:
dialogue, mutually_beneficial_revision, tradeoffs, win_win_justification, legal_refs.

Return ONLY JSON. No explanation.

Input:
{bad_text}
"""
    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": fix_prompt}],
            temperature=0
        )
        txt = res.choices[0].message.content.strip()
        return json.loads(txt)
    except:
        return None

def negotiate(clause: str, position: str):
    prompt = f"""
You MUST output ONLY VALID JSON. NO markdown, NO code fences, NO prose.

JSON structure:
{json.dumps(STRICT_SCHEMA, indent=2)}

Now generate negotiation JSON.

CLAUSE:
{clause}

COUNTERPARTY POSITION:
{position}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        txt = res.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR contacting LLM: {e}"

    try:
        return json.loads(txt)
    except:
        pass

    m = re.search(r"\{[\s\S]*\}", txt)
    if m:
        try:
            return json.loads(m.group(0))
        except:
            pass

    repaired = force_json_repair(txt)
    if repaired:
        return repaired

    return txt
