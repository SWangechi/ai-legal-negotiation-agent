import json
import re
import os
from openai import OpenAI
from backend.prompts.negotiation import build_negotiation_messages
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
    """
    Attempts to repair invalid JSON output from LLM.
    """

    fix_prompt = f"""
Convert the following into STRICT JSON with these keys only:
dialogue, mutually_beneficial_revision, tradeoffs, win_win_justification, legal_refs.

Return ONLY JSON. No explanations.

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


def negotiate(clause: str, position: str, turns: int = 4):
    """
    Runs a contract negotiation simulation between Party A & Party B.
    """

    messages = build_negotiation_messages(clause, position, turns)

    try:
        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.25
        )
        raw_text = res.choices[0].message.content.strip()
    except Exception as e:
        return {"error": f"LLM request failed: {e}"}

    try:
        return json.loads(raw_text)
    except:
        pass

    match = re.search(r"\{[\s\S]*\}", raw_text)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass

    repaired = force_json_repair(raw_text)
    if repaired:
        return repaired

    return {
        "error": "Unable to parse negotiation JSON.",
        "raw_output": raw_text
    }
