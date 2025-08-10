from typing import Dict
from vinyl_preflight.models import Project, ExtractionResult

# definice kroků pipeline jako samostatné funkce

def ingest(source_path: str) -> Project:
    # stub: najde projekty v rozbaleném adresáři
    return Project(name=source_path)

def extract(project: Project) -> ExtractionResult:
    # stub: extrahuje tracky z PDFs pomocí LLM + pdf_utils (později)
    return ExtractionResult(source=project.name, status='ok')

def validate(result: ExtractionResult) -> ExtractionResult:
    # stub validace
    return result

def report(result: ExtractionResult) -> Dict:
    return {'report_for': result.source}

