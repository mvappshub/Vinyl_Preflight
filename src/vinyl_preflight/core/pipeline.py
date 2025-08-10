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

from pathlib import Path
from typing import List

MAX_PDFS_PER_BATCH = 50

def create_pdf_batches(projects: dict) -> List[List[Path]]:
    all_pdfs_to_process = [pdf_path for proj in projects.values() for pdf_path in proj.get('pdfs', [])]
    batches: List[List[Path]] = []
    for i in range(0, len(all_pdfs_to_process), MAX_PDFS_PER_BATCH):
        batches.append(all_pdfs_to_process[i:i + MAX_PDFS_PER_BATCH])
    return batches

