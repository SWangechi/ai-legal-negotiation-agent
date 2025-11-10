import re

def clean_text(text: str) -> str:
    """
    Cleans up PDF artifacts and formatting issues from extracted text.
    """
    text = re.sub(r'\s+', ' ', text)  
    text = re.sub(r'-\s', '', text)
    text = text.replace(" .", ".")
    return text.strip()


def split_clauses(text: str):
    """
    Splits contract text into logical clauses for AI analysis.
    """
    cleaned = clean_text(text)

    
    parts = re.split(r'(?=\b\d+\.\s|\b[a-zA-Z]\)\s|Article\s+\d+|Clause\s+\d+)', cleaned)
    clauses = [p.strip() for p in parts if len(p.strip()) > 40]  

    return clauses
