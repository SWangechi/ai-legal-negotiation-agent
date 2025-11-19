# backend/reasoning.py
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from backend.memory_manager import search_memory

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def reason_over_clause(clause: str):
    retrieved = search_memory(clause, k=4)
    context = "\n\n---\n\n".join([r.get("text", "") for r in retrieved])

    prompt = (
        "You are an expert Kenyan contract lawyer AI.\n\n"
        "Use the context below ONLY to support your reasoning.\n\n"
        "CONTEXT:\n"
        "{}\n\n"
        "CLAUSE:\n"
        "{}\n\n"
        "TASK:\n"
        "1) Identify the legal issue (short string)\n"
        "2) Identify compliance risks under Kenyan Law (short string)\n"
        "3) Propose a fair and balanced revision (string)\n"
        "4) Explain rationale (string)\n"
        "5) Cite Kenyan legal references (array of strings)\n\n"
        "Return JSON ONLY in this exact structure:\n"
        "{{\n"
        "  \"issue\": \"...\",\n"
        "  \"risk\": \"...\",\n"
        "  \"revision\": \"...\",\n"
        "  \"rationale\": \"...\",\n"
        "  \"legal_refs\": [\"...\",\"...\"]\n"
        "}}\n"
    ).format(context, clause)

    res = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
        max_output_tokens=1500
    )

    text = res.output_text if hasattr(res, "output_text") else "".join([o.get("content","") for o in res.output or []])
    return text, retrieved
