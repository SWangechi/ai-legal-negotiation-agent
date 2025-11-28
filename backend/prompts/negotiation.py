from backend.prompts.shared import THINKING_INSTRUCTIONS, KENYAN_LAW_CONTEXT, OUTPUT_POLICY

SYSTEM_PROMPT = f"""
You are simulating a professional contract negotiation between two parties:

Party A = User
Party B = Counterparty

Rules:
- Use Kenyan professional negotiation practice.
- Keep tone professional and realistic.
- Each turn must clearly show "Party A" or "Party B".
- Number turns: Turn 1, Turn 2, Turn 3...
- After all turns, propose a revised clause AND justification.

{KENYAN_LAW_CONTEXT}
{THINKING_INSTRUCTIONS}
{OUTPUT_POLICY}
"""

FEW_SHOT = [
    {
        "role": "user",
        "content": "CLAUSE:\nPayment within 3 days.\nCOUNTERPARTY POSITION:\nThey want 30 days.\nTURNS: 3"
    },
    {
        "role": "assistant",
        "content": """{
  "negotiation": [
    "Turn 1 - Party A: We prefer 3 days for early liquidity.",
    "Turn 2 - Party B: Our cash flow cycles require 30 days.",
    "Turn 3 - Party A: We can agree to 14 days as a midpoint."
  ],
  "revised_clause": "Payment shall be made within fourteen (14) days from date of invoice.",
  "justification": "14 days balances both liquidity needs and operational cash flow."
}"""
    }
]


def build_negotiation_messages(clause: str, counterparty: str, turns: int):
    user_text = f"""
CLAUSE:
{clause}

COUNTERPARTY POSITION:
{counterparty}

TURNS:
{turns}
"""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        *FEW_SHOT,
        {"role": "user", "content": user_text}
    ]
