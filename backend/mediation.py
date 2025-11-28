import os, json, re
from openai import OpenAI
from backend.prompts.mediation import build_mediation_messages
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def mediate(party_a: str, party_b: str):
    """
    Generates a mediation decision using:
    - System + Few-shot prompt builder
    - Kenyan ADR principles
    - Markdown output for the UI
    """

    messages = build_mediation_messages(party_a, party_b)

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.3
    )

    return {"result": res.choices[0].message.content}
