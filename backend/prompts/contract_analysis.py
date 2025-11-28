from backend.prompts.shared import THINKING_INSTRUCTIONS, KENYAN_LAW_CONTEXT, OUTPUT_POLICY

SYSTEM_PROMPT = f"""
You are a Kenyan contract lawyer and junior legal analyst.
Your role:
- interpret clauses,
- identify risks & ambiguities,
- assess fairness,
- check compliance with Kenyan law,
- propose improved versions.

{KENYAN_LAW_CONTEXT}
{THINKING_INSTRUCTIONS}
{OUTPUT_POLICY}
"""

FEW_SHOT = [
    {
        "role": "user",
        "content": "CLAUSE:\nThe Employer may terminate the Employee at any time without notice and without cause."
    },
    {
        "role": "assistant",
        "content": """{
  "clause_summary": "Employer can fire employee at any time without reason or notice.",
  "issues": [
    "Likely violates Employment Act.",
    "No notice period.",
    "No disciplinary procedure."
  ],
  "compliance_notes": [
    "Kenyan employment law requires valid reason + fair process."
  ],
  "suggested_revision": "The Employer may terminate this Contract by providing at least one (1) month's written notice or salary in lieu, and only for a valid reason following a fair process in accordance with the Employment Act (Kenya)."
}"""
    }
]

def build_contract_analysis_messages(clause: str):
    user_content = f"CLAUSE TO ANALYSE:\n{clause}"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *FEW_SHOT,
        {"role": "user", "content": user_content}
    ]
    return messages

