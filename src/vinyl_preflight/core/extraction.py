from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional
import concurrent.futures
import logging

from vinyl_preflight.core.pdf_utils import extract_text_from_pdf
from vinyl_preflight.llm.service import LLMExtractionService

logger = logging.getLogger(__name__)

MAX_PARALLEL_API_REQUESTS = 10


def process_single_extraction_batch(batch: List[Path], llm_service: LLMExtractionService) -> Optional[List[Dict]]:
    documents_to_process: List[Dict[str, str]] = []
    for pdf_path in batch:
        try:
            if not pdf_path.exists():
                logger.error(f"PDF file does not exist: {pdf_path}")
                documents_to_process.append({"identifier": pdf_path.as_posix(), "content": "CHYBA: Soubor neexistuje."})
                continue
            if pdf_path.stat().st_size == 0:
                logger.error(f"PDF file is empty: {pdf_path.name}")
                documents_to_process.append({"identifier": pdf_path.as_posix(), "content": "CHYBA: Prázdný soubor."})
                continue
            text = extract_text_from_pdf(pdf_path)
            if not text.strip():
                text = f"VAROVÁNÍ: PDF soubor '{pdf_path.name}' neobsahuje žádný extrahovatelný text."
            documents_to_process.append({"identifier": pdf_path.as_posix(), "content": text})
        except Exception as e:
            logger.error(f"Unexpected error reading PDF: {pdf_path.name}, {e}")
            documents_to_process.append({"identifier": pdf_path.as_posix(), "content": f"CHYBA: Neočekávaná chyba. {e}"})

    if not documents_to_process:
        return None

    # Nyní používáme LLM service pro extrakci
    return llm_service.extract_tracks_from_documents(documents_to_process)


def process_all_pdf_batches(batches: List[List[Path]], llm_service: LLMExtractionService, status_callback, progress_callback) -> dict:
    all_results: Dict[str, Dict] = {}
    total_batches = len(batches)
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_PARALLEL_API_REQUESTS) as executor:
        future_to_batch = {executor.submit(process_single_extraction_batch, batch, llm_service): i for i, batch in enumerate(batches)}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_batch)):
            status_callback(f"4/5 Zpracovávám PDF dávku {i+1}/{total_batches}...")
            progress_callback(i + 1, total_batches)
            try:
                batch_results = future.result()
                if batch_results:
                    for result in batch_results:
                        all_results[result['source_identifier']] = result
            except Exception as e:
                logger.error(f"Chyba při zpracování dávky: {e}")
    return all_results

