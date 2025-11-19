from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def mediate(party_a: str, party_b: str):
    prompt = f"""
You are a professional Kenyan mediation AI assistant.

Your output MUST be clean markdown with headings:
### Neutral Summary of the Dispute
### Party A Interests
### Party B Interests
### Objective Evaluation
### Fair Compromise
### Legal Grounding (Kenyan ADR Law)

DO NOT return JSON. 
DO NOT wrap output in code blocks.
DO NOT use quotes around sections.

PARTY A:
{party_a}

PARTY B:
{party_b}
"""

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return {"result": res.choices[0].message.content}
