# Monolith Migration Map (src/vinyl_preflight_app.py → modular)

- Workspace & archives
  - _prepare_workspace → io.filesystem.ensure_dir / io.archives.safe_extract_zip/safe_extract_rar
  - _extract_zip_safely → io.archives.safe_extract_zip
  - _extract_rar_safely → io.archives.safe_extract_rar

- WAV & PDF utilities
  - _get_wav_duration_worker → core.wav_utils.get_wav_duration
  - PDF text extraction (inline) → core.pdf_utils.extract_text_from_pdf

- Text & time helpers
  - seconds_to_mmss → utils.timefmt.seconds_to_mmss
  - safe_round → utils.timefmt.safe_round
  - normalize_string → utils.text.normalize_string

- Validation & matching
  - _detect_consolidated_mode → core.validator.detect_consolidated_mode
  - _find_wav_for_side → core.matcher.find_wav_for_side
  - _validate_consolidated_project → core.validator.validate_consolidated_project
  - _validate_individual_project → core.validator.validate_individual_project

- PDF batching & extraction pipeline
  - _create_pdf_batches → core.pipeline.create_pdf_batches
  - _process_all_pdf_batches → core.extraction.process_all_pdf_batches
  - _process_single_extraction_batch → core.extraction.process_single_extraction_batch (LLM call remains to be delegated)

- Reporting
  - CSV write (inline) → io.output.write_csv_header / append_csv_rows / write_csv

- Orchestrator & adapter
  - Orchestrator steps → core.pipeline (ingest/extract/validate/report)
  - GUI adapter → src/vinyl_preflight/app.py: run(payload)

- LLM
  - Abstract + mock → llm.client.LLMClient / MockLLMClient
  - OpenRouter client → llm.client.OpenRouterLLMClient (prepared; monolith LLM call to be delegated subsequently)

Notes:
- GUI remains unchanged; monolith progressively delegates to modules.
- Each migration step accompanied by tests; pytest suite is green.

