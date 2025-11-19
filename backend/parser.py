import re

def split_into_clauses(text):
    """
    Split contract into clauses using section headers, numbering, etc.
    """

    patterns = [
        r"\n\d+\.",        
        r"\n\d+\)",        
        r"\n[A-Z][a-zA-Z ]+:" 
    ]

    combined = "|".join(patterns)

    pieces = re.split(combined, text)
    clauses = [c.strip() for c in pieces if len(c.strip()) > 30]

    return clauses
