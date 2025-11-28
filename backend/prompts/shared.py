THINKING_INSTRUCTIONS = """
You may think step-by-step internally.
Do NOT reveal chain-of-thought to the user.
Only output the final structured result.
"""

KENYAN_LAW_CONTEXT = """
You must interpret all clauses using Kenyan law, including:
- Employment Act (Kenya)
- Data Protection Act 2019
- Companies Act 2015
- ADR principles under Arbitration Act (Kenya)
"""

OUTPUT_POLICY = """
Always return output in valid JSON. Do not add commentary outside JSON.
If you cannot answer, return JSON with an "error" field.
"""

