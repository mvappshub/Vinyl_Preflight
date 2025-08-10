from pathlib import Path
import fitz  # PyMuPDF

def extract_text_from_pdf(path: Path) -> str:
    doc = fitz.open(path)
    try:
        return "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()

