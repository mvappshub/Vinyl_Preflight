import re

def normalize_string(s: str) -> str:
    s = s.lower()
    s = re.sub(r'^\d+[\s.-]*', '', s)
    s = re.sub(r'[\W_]+', ' ', s)
    return " ".join(s.split())

