from backend.prompts.shared import THINKING_INSTRUCTIONS, KENYAN_LAW_CONTEXT, OUTPUT_POLICY

SYSTEM_PROMPT = f"""
You are a neutral mediator using Kenyan ADR principles.
Your function:
- extract key issues,
- extract interests (not positions),
- evaluate fairness,
- propose compromise acceptable to both parties.

Maintain neutrality. Avoid taking sides.

{KENYAN_LAW_CONTEXT}
{THINKING_INSTRUCTIONS}
{OUTPUT_POLICY}
"""

FEW_SHOT = [
    {
        "role": "user",
        "content": "PARTY A:\nThey owe me unpaid overtime.\nPARTY B:\nWe cannot pay because hours were not approved."
    },
    {
        "role": "assistant",
        "content": """{
  "neutral_summary": "Dispute involves unpaid overtime and lack of prior authorization.",
  "interests_party_a": ["Compensation for hours worked", "Fair treatment"],
  "interests_party_b": ["Budget control", "Following internal approval procedures"],
  "evaluation": "Both sides have legitimate concerns. Employment Act requires fair compensation but allows employers to set approval procedures.",
  "proposed_compromise": "Employer pays 50% of disputed overtime and updates policy to prevent future ambiguity."
}"""
    }
]

def build_mediation_messages(party_a: str, party_b: str):
    user_text = f"""
PARTY A:
{party_a}

PARTY B:
{party_b}
"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        *FEW_SHOT,
        {"role": "user", "content": user_text}
    ]
