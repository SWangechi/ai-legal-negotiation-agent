from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import re
from typing import Any

from backend.parser import split_into_clauses
from backend.reasoning import reason_over_clause
from backend.negotiation import negotiate
from backend.mediation import mediate
from backend.feedback import save_feedback

router = APIRouter()

def clean_llm_json(text: str) -> str:
    """
    Remove ```json ... ``` wrappers and return raw JSON string.
    """
    if not isinstance(text, str):
        return str(text)
    t = text.strip()
    t = re.sub(r"^```json\s*", "", t, flags=re.IGNORECASE)
    t = t.replace("```", "")
    return t.strip()


def try_parse_json_maybe(text_or_obj: Any):
    """
    Try to convert returned LLM value into a Python object.
    Returns (parsed_obj, raw_text).
    parsed_obj: Python object if JSON parsed, else None.
    raw_text: string representation to return/display.
    """
    if isinstance(text_or_obj, (dict, list)):
        return text_or_obj, json.dumps(text_or_obj)

    raw = "" if text_or_obj is None else str(text_or_obj)

    cleaned = clean_llm_json(raw)

    try:
        parsed = json.loads(cleaned)
        return parsed, cleaned
    except Exception:
        return None, cleaned


class Contract(BaseModel):
    text: str

class Negotiate(BaseModel):
    clause: str
    position: str

class Mediate(BaseModel):
    a: str
    b: str

class Feedback(BaseModel):
    username: str
    rating: int
    comments: str


@router.post("/analyze")
def analyze(req: Contract):
    clauses = split_into_clauses(req.text)
    output = []

    for c in clauses:
        raw_text, sources = reason_over_clause(c)

        cleaned = clean_llm_json(raw_text)

        try:
            reasoning = json.loads(cleaned)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"analysis failed: could not parse cleaned LLM JSON: {str(e)}\nCLEANED LLM OUTPUT:\n{cleaned[:4000]}"
            )

        output.append({
            "clause": c,
            "analysis": reasoning,
            "sources": sources
        })

    return {"clauses": output}


@router.post("/negotiate")
def negotiate_route(req: Negotiate):
    raw = negotiate(req.clause, req.position)

    if isinstance(raw, dict):
        return {"result": raw}

    try:
        parsed = json.loads(raw)
        return {"result": parsed}
    except:
        pass

    
    return {"result": str(raw)}


@router.post("/mediate")
def mediate_route(req: Mediate):
    raw = mediate(req.a, req.b)

    parsed, raw_text = try_parse_json_maybe(raw)

    if parsed is not None:
        return {"result": parsed}
    else:
        return {"result": raw_text}


@router.post("/feedback")
def feedback_route(req: Feedback):
    save_feedback(req.username, req.rating, req.comments)
    return {"status": "ok", "msg": "Feedback stored + added to memory"}
