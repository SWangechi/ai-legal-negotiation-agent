import os, json, re
from openai import OpenAI
from backend.prompts.contract_analysis import build_contract_analysis_messages
from backend.utils.embedding_manager import search_memory
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def reason_over_clause(clause: str):
    """
    Performs contract clause analysis using:
    - Chroma memory retrieval
    - New system + few-shot + CoT-suppressed prompts
    - JSON output structure from prompt template
    """

    retrieved = search_memory(clause, k=4)
    context = "\n\n---\n\n".join([r.get("text", "") for r in retrieved])

    messages = build_contract_analysis_messages(clause)

    if context.strip():
        messages.append({
            "role": "user",
            "content": f"\nADDITIONAL CONTEXT FROM MEMORY:\n{context}"
        })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2,
        max_tokens=1500,
    )

    result_text = response.choices[0].message.content
    return result_text, retrieved

def format_revision(revision_dict, style="legal"):
    """Format suggested revisions in two possible styles: plain or legal."""

    if style == "plain":
        lines = []
        for key, value in revision_dict.items():
            title = key.replace("_", " ").title()
            lines.append(f"**{title}:** {value.strip()}")
        return "\n\n".join(lines)

    lines = []
    counter = 1
    for key, value in revision_dict.items():
        title = key.replace("_", " ").title()
        lines.append(f"**{counter}. {title}**")
        lines.append(f"{counter}.1 {value.strip()}\n")
        counter += 1
    return "\n".join(lines)

