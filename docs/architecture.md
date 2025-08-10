# Architektura projektu

Moduly:
- core: pipeline, extraction, wav_utils, pdf_utils, validator, matcher
- io: filesystem, archives, output
- llm: client (LLMClient, MockLLMClient, OpenRouterLLMClient)
- utils: timefmt, text

Pipeline: ingest → extract → validate → report.

GUI adapter zůstává tenký (src/vinyl_preflight/app.py). Žádná business logika v GUI.

