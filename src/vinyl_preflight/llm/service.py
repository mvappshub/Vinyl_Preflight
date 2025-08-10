import json
import logging
from typing import List, Dict, Optional
from pathlib import Path

from vinyl_preflight.llm.client import LLMClient

logger = logging.getLogger(__name__)


class LLMExtractionService:
    def __init__(self, llm_client: LLMClient, detailed_logger=None):
        self.llm_client = llm_client
        self.detailed_logger = detailed_logger

    def extract_tracks_from_documents(self, documents_to_process: List[Dict]) -> Optional[List[Dict]]:
        """Extract track information from documents using LLM."""
        if not documents_to_process:
            return None

        prompt = f"""
Jsi expert na hudební mastering. Tvým úkolem je precizně extrahovat informace o skladbách z několika dokumentů.
Analyzuj KAŽDÝ dokument v poli a vrať VÝHRADNĚ JEDEN JSON objekt s klíčem "results". Hodnota klíče "results" bude pole, kde každý prvek reprezentuje jeden zpracovaný dokument.

Struktura pro každý prvek v poli "results":
- "source_identifier": Unikátní identifikátor dokumentu.
- "status": 'success' nebo 'error'.
- "data": Pokud 'success', zde bude pole skladeb. Každá skladba musí obsahovat "side", "track_number", "title", "duration_seconds".
- "error_message": Popis chyby, pokud status je 'error'.

Zde jsou dokumenty ke zpracování:
---
{json.dumps(documents_to_process, indent=2, ensure_ascii=False)}
---
"""

        # Logování LLM požadavku
        if self.detailed_logger:
            self.detailed_logger.log_llm_request({
                "documents_count": len(documents_to_process),
                "documents": [{"identifier": d["identifier"], "content_length": len(d["content"])} for d in documents_to_process],
                "prompt_length": len(prompt),
            })

        try:
            response = self.llm_client.call(prompt)
            
            # Pro OpenRouter response format
            if "choices" in response:
                content_str = response["choices"][0]["message"]["content"]
                parsed_results = json.loads(content_str).get("results", [])
            else:
                # Pro mock nebo jiné formáty
                parsed_results = response.get("results", [])

            # Logování LLM odpovědi
            if self.detailed_logger:
                self.detailed_logger.log_llm_response({
                    "raw_response": response,
                    "parsed_results": parsed_results,
                })

            return parsed_results

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            if self.detailed_logger:
                self.detailed_logger.log_llm_error({"error": str(e)})
            return None
