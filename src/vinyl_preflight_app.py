#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import concurrent.futures
import time
import os
import sys
import json
import csv
from pathlib import Path
from datetime import datetime
import math
from typing import Callable, Dict, List, Tuple, Optional
import shutil
import tempfile
import zipfile
import re

import requests
import soundfile as sf
from dotenv import load_dotenv
import multiprocessing as mp
import fitz
from thefuzz import fuzz
import logging
from vinyl_preflight.utils.timefmt import seconds_to_mmss as _util_seconds_to_mmss, safe_round as _util_safe_round
from vinyl_preflight.core.validator import detect_consolidated_mode as _detect_mode
from vinyl_preflight.core.wav_utils import get_wav_duration as _get_wav_duration
from vinyl_preflight.core.pdf_utils import extract_text_from_pdf as _extract_text_from_pdf
from vinyl_preflight.io.output import write_csv



logger = logging.getLogger(__name__)

rarfile = None
try:
    import rarfile
    if not shutil.which("unrar"):
        logger.warning("Příkaz 'unrar' nebyl nalezen v systémové PATH. Extrakce RAR nemusí fungovat.")
except ImportError:
    logger.warning("Knihovna 'rarfile' není nainstalována. Podpora pro .rar archivy je vypnuta.")

MODEL_NAME = "google/gemini-2.5-flash"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_PDFS_PER_BATCH = 50
MAX_PARALLEL_API_REQUESTS = 10
API_REQUEST_TIMEOUT = 180
VALIDATION_TOLERANCE_SECONDS = 10
MAX_ARCHIVE_SIZE_MB = 1024
MAX_EXTRACTION_TIME_SECONDS = 300
CSV_HEADERS = [
    "project_title", "status", "validation_item", "item_type",
    "pdf_duration_mmss", "wav_duration_mmss", "difference_mmss",
    "pdf_duration_sec", "wav_duration_sec", "difference_sec",
    "pdf_source", "wav_source", "notes"
]

def seconds_to_mmss(seconds: Optional[float]) -> str:
    return _util_seconds_to_mmss(seconds)

def safe_round(value: Optional[float], decimals: int = 2) -> Optional[float]:
    return _util_safe_round(value, decimals)

class DetailedLogger:
    """Třída pro detailní logování průběhu zpracování"""

    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self.start_time = datetime.now()

        # Vytvoř log soubor s hlavičkou
        with open(log_file_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("VINYL PREFLIGHT PROCESSOR - DETAILNÍ LOG\n")
            f.write("=" * 80 + "\n")
            f.write(f"Spuštěno: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

    def log_step(self, step_name: str, data: any = None):
        """Zaloguje krok s časovým razítkem"""
        timestamp = datetime.now()
        elapsed = (timestamp - self.start_time).total_seconds()

        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n[{timestamp.strftime('%H:%M:%S')}] (+{elapsed:.1f}s) {step_name}\n")
            f.write("-" * 60 + "\n")

            if data is not None:
                if isinstance(data, dict):
                    f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
                elif isinstance(data, (list, tuple)):
                    for i, item in enumerate(data):
                        f.write(f"  [{i}] {item}\n")
                else:
                    f.write(str(data) + "\n")
            f.write("\n")

    def log_llm_request(self, request_data: dict):
        """Zaloguje požadavek na LLM"""
        self.log_step("🤖 LLM REQUEST - DATA ODESLANÁ DO LLM", {
            "model": request_data.get("model"),
            "messages": request_data.get("messages"),
            "temperature": request_data.get("temperature"),
            "max_tokens": request_data.get("max_tokens")
        })

    def log_llm_response(self, response_data: dict):
        """Zaloguje odpověď z LLM"""
        self.log_step("🤖 LLM RESPONSE - DATA PŘIJATÁ Z LLM", response_data)

    def log_extracted_data(self, pdf_path: str, extracted_data: dict):
        """Zaloguje extrahovaná data z PDF"""
        self.log_step(f"📄 EXTRAHOVANÁ DATA Z PDF: {Path(pdf_path).name}", extracted_data)

    def log_wav_durations(self, wav_durations: dict):
        """Zaloguje délky WAV souborů"""
        formatted_data = {}
        for wav_path, duration in wav_durations.items():
            filename = Path(wav_path).name
            if duration is not None:
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                formatted_data[filename] = f"{minutes:02d}:{seconds:02d} ({duration:.2f}s)"
            else:
                formatted_data[filename] = "CHYBA"

        self.log_step("🎵 DÉLKY WAV SOUBORŮ", formatted_data)

    def log_validation_results(self, project_name: str, validation_data: dict):
        """Zaloguje výsledky validace"""
        self.log_step(f"✅ VALIDACE PROJEKTU: {project_name}", validation_data)

def _get_wav_duration_worker(filepath: Path) -> Tuple[str, Optional[float]]:
    try:
        if not filepath.exists():
            logger.error(f"WAV file does not exist: {filepath}")
            return filepath.as_posix(), None

        if filepath.stat().st_size == 0:
            logger.error(f"WAV file is empty: {filepath.name}")
            return filepath.as_posix(), None

        dur = _get_wav_duration(filepath)
        if dur is None or dur <= 0:
            logger.warning(f"WAV file has invalid duration: {filepath.name}")
            return filepath.as_posix(), None

        return filepath.as_posix(), dur
    except (sf.LibsndfileError, RuntimeError) as e:
        logger.error(f"Corrupted or invalid WAV file '{filepath.name}': {e}")
        return filepath.as_posix(), None
    except (OSError, PermissionError) as e:
        logger.error(f"Cannot access WAV file '{filepath.name}': {e}")
        return filepath.as_posix(), None
    except Exception as e:
        logger.error(f"Unexpected error reading WAV '{filepath.name}': {e}")
        return filepath.as_posix(), None

from vinyl_preflight.utils.text import normalize_string

class PreflightProcessor:
    def __init__(self, api_key: str, progress_callback: Callable, status_callback: Callable):
        if not api_key: raise ValueError("API klíč nesmí být prázdný.")
        self.api_key = api_key
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        self.detailed_logger = None

    def run(self, source_directory: str):
        try:
            start_time = time.time()
            output_dir = Path(__file__).resolve().parent.parent / "output"
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
            output_filename = output_dir / f"Preflight_Report_{timestamp}.csv"

            # Inicializace detailního loggeru
            log_filename = output_dir / f"Detailed_Log_{timestamp}.txt"
            self.detailed_logger = DetailedLogger(str(log_filename))
            self.detailed_logger.log_step("🚀 SPUŠTĚNÍ ZPRACOVÁNÍ", {
                "source_directory": source_directory,
                "output_file": str(output_filename),
                "log_file": str(log_filename)
            })

            with tempfile.TemporaryDirectory(prefix="preflight_") as tmpdir:
                temp_path = Path(tmpdir)
                self.status_callback("1/5 Připravuji pracovní prostor a extrahuji archivy...")
                self._prepare_workspace(Path(source_directory), temp_path)

                self.status_callback("2/5 Skenuji soubory a připravuji projekty...")
                projects = self._scan_and_group_projects(temp_path)

                # Detailní výpis nalezených projektů
                if projects:
                    self.status_callback(f"NALEZENO {len(projects)} PROJEKTŮ:")

                    # Logování nalezených projektů
                    projects_data = {}
                    for project_name, project_info in projects.items():
                        pdf_count = len(project_info['pdfs'])
                        wav_count = len(project_info['wavs'])
                        self.status_callback(f"  📁 {project_name}: {pdf_count} PDF, {wav_count} WAV")

                        projects_data[project_name] = {
                            "pdf_files": [pdf.name for pdf in project_info['pdfs']],
                            "wav_files": [wav.name for wav in project_info['wavs']],
                            "pdf_count": pdf_count,
                            "wav_count": wav_count
                        }

                        for pdf in project_info['pdfs']:
                            self.status_callback(f"    📄 PDF: {pdf.name}")
                        for wav in project_info['wavs']:
                            self.status_callback(f"    🎵 WAV: {wav.name}")

                    self.detailed_logger.log_step("📁 NALEZENÉ PROJEKTY", projects_data)
                else:
                    self.status_callback("Ve vybraném adresáři (včetně archivů) nebyly nalezeny žádné relevantní podsložky s PDF a WAV soubory.")
                    self.status_callback("Připraveno.")
                    return None

                self.status_callback("3/5 Zjišťuji délky WAV souborů...")
                wav_durations = self._get_all_wav_durations(projects)

                # Detailní výpis délek WAV souborů
                self.status_callback(f"ZJIŠTĚNY DÉLKY {len(wav_durations)} WAV SOUBORŮ:")
                for wav_path, duration in wav_durations.items():
                    if duration is not None:
                        minutes = int(duration // 60)
                        seconds = int(duration % 60)
                        self.status_callback(f"  🎵 {Path(wav_path).name}: {minutes:02d}:{seconds:02d} ({duration:.2f}s)")
                    else:
                        self.status_callback(f"  ❌ {Path(wav_path).name}: CHYBA při čtení")

                # Logování WAV délek
                self.detailed_logger.log_wav_durations(wav_durations)

                self.status_callback("4/5 Vytvářím dávky PDF pro efektivní extrakci...")
                pdf_batches = self._create_pdf_batches(projects)

                # Detailní výpis PDF dávek
                self.status_callback(f"VYTVOŘENO {len(pdf_batches)} DÁVEK PDF:")

                batches_data = {}
                for i, batch in enumerate(pdf_batches):
                    batch_name = f"batch_{i+1}"
                    batches_data[batch_name] = [pdf_path.name for pdf_path in batch]

                    self.status_callback(f"  📦 Dávka {i+1}: {len(batch)} PDF souborů")
                    for pdf_path in batch:
                        self.status_callback(f"    📄 {pdf_path.name}")

                self.detailed_logger.log_step("📦 PDF DÁVKY", batches_data)

                self.status_callback(f"4/5 Budu zpracovávat {len(pdf_batches)} dávek PDF. Odesílám k LLM...")
                extracted_pdf_data = self._process_all_pdf_batches(pdf_batches)

                # Detailní výpis výsledků extrakce
                self.status_callback(f"EXTRAKCE DOKONČENA - VÝSLEDKY PRO {len(extracted_pdf_data)} PDF:")
                for pdf_path, result in extracted_pdf_data.items():
                    status = result.get('status', 'unknown')
                    if status == 'success':
                        tracks = result.get('data', [])
                        self.status_callback(f"  ✅ {Path(pdf_path).name}: {len(tracks)} skladeb")
                        for track in tracks:
                            side = track.get('side', 'N/A')
                            title = track.get('title', 'N/A')
                            duration = track.get('duration_seconds', 0)
                            minutes = int(duration // 60)
                            seconds = int(duration % 60)
                            self.status_callback(f"    🎵 Side {side}: {title} ({minutes:02d}:{seconds:02d})")
                    else:
                        error = result.get('error_message', 'Neznámá chyba')
                        self.status_callback(f"  ❌ {Path(pdf_path).name}: CHYBA - {error}")

                    # Logování extrahovaných dat pro každý PDF
                    if self.detailed_logger:
                        self.detailed_logger.log_extracted_data(pdf_path, result)

                self.status_callback("5/5 Zahajuji finální validaci a zápis do reportu...")
                # modulární CSV zápis: hlavička + řádky
                from vinyl_preflight.io.output import write_csv_header, append_csv_rows
                write_csv_header(output_filename, CSV_HEADERS)

                total_projects = len(projects)
                for i, (project_name, project_info) in enumerate(projects.items()):
                    self.status_callback(f"5/5 Validuji projekt {i+1}/{total_projects}: {project_name}")
                    self.progress_callback(i, total_projects)

                    project_pdf_results = {p.as_posix(): extracted_pdf_data.get(p.as_posix()) for p in project_info['pdfs']}
                    project_wav_durations = {p.as_posix(): wav_durations.get(p.as_posix()) for p in project_info['wavs']}

                    # Detailní výpis před validací
                    self.status_callback(f"  🔍 VALIDUJI PROJEKT '{project_name}':")
                    self.status_callback(f"    📄 PDF výsledky: {len(project_pdf_results)} souborů")
                    self.status_callback(f"    🎵 WAV délky: {len(project_wav_durations)} souborů")

                    # Detekce módu
                    wav_paths = list(project_wav_durations.keys())
                    is_consolidated = self._detect_consolidated_mode(wav_paths)
                    mode = "CONSOLIDATED (strany)" if is_consolidated else "INDIVIDUAL (tracky)"
                    self.status_callback(f"    🎯 Detekovaný mód: {mode}")

                    validation_rows = self._validate_project(project_name, project_pdf_results, project_wav_durations)

                    # Výpis výsledků validace
                    self.status_callback(f"    📊 VÝSLEDKY VALIDACE: {len(validation_rows)} položek")
                    for row in validation_rows:
                        status = row.get('status', 'N/A')
                        item = row.get('validation_item', 'N/A')
                        item_type = row.get('item_type', 'N/A')
                        pdf_dur = row.get('pdf_duration_mmss', 'N/A')
                        wav_dur = row.get('wav_duration_mmss', 'N/A')
                        diff = row.get('difference_mmss', 'N/A')

                        status_icon = "✅" if status == "OK" else "❌"
                        self.status_callback(f"      {status_icon} {item} ({item_type}): PDF {pdf_dur} vs WAV {wav_dur} = {diff}")

                    # Logování validace projektu
                    if self.detailed_logger:
                        validation_data = {
                            "project_name": project_name,
                            "pdf_results_count": len(project_pdf_results),
                            "wav_durations_count": len(project_wav_durations),
                            "detected_mode": "CONSOLIDATED" if is_consolidated else "INDIVIDUAL",
                            "validation_rows": validation_rows
                        }
                        self.detailed_logger.log_validation_results(project_name, validation_data)

                    append_csv_rows(output_filename, validation_rows, CSV_HEADERS)

                self.progress_callback(total_projects, total_projects)

            end_time = time.time()
            total_time = end_time - start_time

            # Závěrečné logování
            if self.detailed_logger:
                self.detailed_logger.log_step("🏁 DOKONČENÍ ZPRACOVÁNÍ", {
                    "total_time_seconds": total_time,
                    "output_csv_file": str(output_filename),
                    "log_file": str(log_filename),
                    "projects_processed": len(projects) if 'projects' in locals() else 0,
                    "success": True
                })

            self.status_callback(f"Hotovo! Celkový čas: {total_time:.2f} s. Report uložen do: {output_filename}")
            self.status_callback(f"Detailní log uložen do: {log_filename}")
            return str(output_filename)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status_callback(f"Chyba: Proces byl přerušen. {e}")
            return None

    def _prepare_workspace(self, source_root: Path, temp_root: Path):
        for item in source_root.iterdir():
            if item.is_dir():
                shutil.copytree(item, temp_root / item.name, dirs_exist_ok=True)
            elif item.is_file():
                target_dir = temp_root / item.stem
                if item.suffix.lower() == '.zip':
                    self._extract_zip_safely(item, target_dir)
                elif item.suffix.lower() == '.rar' and rarfile:
                    self._extract_rar_safely(item, target_dir)

    def _extract_zip_safely(self, zip_path: Path, target_dir: Path):
        """Safely extract ZIP with size and time limits"""
        # Check file size
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        if size_mb > MAX_ARCHIVE_SIZE_MB:
            logger.warning(f"ZIP soubor '{zip_path.name}' je příliš velký ({size_mb:.1f}MB > {MAX_ARCHIVE_SIZE_MB}MB). Přeskakuji.")
            return

        logger.info(f"Extrahuji ZIP: {zip_path.name} ({size_mb:.1f}MB)")
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check total uncompressed size
                total_size = sum(info.file_size for info in zip_ref.infolist())
                if total_size > MAX_ARCHIVE_SIZE_MB * 1024 * 1024 * 2:  # 2x limit for uncompressed
                    logger.warning(f"ZIP '{zip_path.name}' má příliš velký nekomprimovaný obsah. Přeskakuji.")
                    return

                # Extract with progress reporting
                members = zip_ref.infolist()
                for i, member in enumerate(members):
                    if i % 100 == 0:  # Report progress every 100 files
                        self.status_callback(f"Extrahuji ZIP: {zip_path.name} ({i}/{len(members)} souborů)")
                    zip_ref.extract(member, target_dir)

        except Exception as e:
            logger.error(f"Chyba při extrakci ZIP '{zip_path.name}': {e}")

    def _extract_rar_safely(self, rar_path: Path, target_dir: Path):
        """Safely extract RAR with size and time limits"""
        # Check file size
        size_mb = rar_path.stat().st_size / (1024 * 1024)
        if size_mb > MAX_ARCHIVE_SIZE_MB:
            logger.warning(f"RAR soubor '{rar_path.name}' je příliš velký ({size_mb:.1f}MB > {MAX_ARCHIVE_SIZE_MB}MB). Přeskakuji.")
            return

        logger.info(f"Extrahuji RAR: {rar_path.name} ({size_mb:.1f}MB)")
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            with rarfile.RarFile(rar_path, 'r') as rar_ref:
                rar_ref.extractall(target_dir)

        except Exception as e:
            logger.error(f"CHYBA: Nepodařilo se extrahovat RAR soubor '{rar_path.name}'. Důvod: {e}")

    def _scan_and_group_projects(self, root_dir: Path) -> Dict[str, Dict[str, List[Path]]]:
        projects = {}
        if not root_dir.exists() or not root_dir.is_dir():
            logger.warning(f"Root directory does not exist or is not a directory: {root_dir}")
            return projects

        try:
            items = list(root_dir.iterdir())
        except (OSError, PermissionError) as e:
            logger.error(f"Cannot access directory {root_dir}: {e}")
            return projects

        if not items:
            logger.info(f"Directory {root_dir} is empty")
            return projects

        for item in items:
            if item.is_dir():
                try:
                    pdfs = list(item.rglob("*.pdf"))
                    wavs = list(item.rglob("*.wav"))

                    if not pdfs:
                        logger.debug(f"No PDF files found in {item.name}")
                    if not wavs:
                        logger.debug(f"No WAV files found in {item.name}")

                    if pdfs and wavs:
                        projects[item.name] = {'pdfs': pdfs, 'wavs': wavs}
                        logger.debug(f"Project {item.name}: {len(pdfs)} PDFs, {len(wavs)} WAVs")
                except (OSError, PermissionError) as e:
                    logger.warning(f"Cannot access project directory {item.name}: {e}")

        return projects

    def _get_all_wav_durations(self, projects: dict) -> Dict[str, Optional[float]]:
        if not projects:
            logger.warning("No projects provided for WAV duration analysis")
            return {}

        all_wav_paths = []
        for proj_name, proj_data in projects.items():
            if 'wavs' not in proj_data or not proj_data['wavs']:
                logger.warning(f"Project {proj_name} has no WAV files")
                continue
            all_wav_paths.extend(proj_data['wavs'])

        if not all_wav_paths:
            logger.warning("No WAV files found in any project")
            return {}

        durations = {}
        try:
            with mp.Pool() as pool:
                results = pool.map(_get_wav_duration_worker, all_wav_paths)
            for path_str, duration in results:
                durations[path_str] = duration
        except Exception as e:
            logger.error(f"Error processing WAV durations: {e}")
            # Fallback to sequential processing
            for wav_path in all_wav_paths:
                path_str, duration = _get_wav_duration_worker(wav_path)
                durations[path_str] = duration

        return durations

    def _create_pdf_batches(self, projects: dict) -> List[List[Path]]:
        all_pdfs_to_process = [pdf_path for proj in projects.values() for pdf_path in proj['pdfs']]
        batches = []
        for i in range(0, len(all_pdfs_to_process), MAX_PDFS_PER_BATCH):
            batches.append(all_pdfs_to_process[i:i + MAX_PDFS_PER_BATCH])
        return batches

    def _process_all_pdf_batches(self, batches: list) -> dict:
        all_results = {}
        total_batches = len(batches)

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_PARALLEL_API_REQUESTS) as executor:
            future_to_batch = {executor.submit(self._process_single_extraction_batch, batch): i for i, batch in enumerate(batches)}

            for i, future in enumerate(concurrent.futures.as_completed(future_to_batch)):
                self.status_callback(f"4/5 Zpracovávám PDF dávku {i+1}/{total_batches}...")
                self.progress_callback(i + 1, total_batches)
                try:
                    batch_results = future.result()
                    if batch_results:
                        for result in batch_results:
                            all_results[result['source_identifier']] = result
                except Exception as e:
                    logger.error(f"Chyba při zpracování dávky: {e}")
        return all_results

    def _process_single_extraction_batch(self, batch: List[Path]) -> Optional[List[Dict]]:
        documents_to_process = []
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

                text = _extract_text_from_pdf(pdf_path)
                if not text.strip():
                    text = f"VAROVÁNÍ: PDF soubor '{pdf_path.name}' neobsahuje žádný extrahovatelný text."

                documents_to_process.append({"identifier": pdf_path.as_posix(), "content": text})

            except fitz.FileDataError as e:
                logger.error(f"Corrupted PDF file: {pdf_path.name}, {e}")
                documents_to_process.append({"identifier": pdf_path.as_posix(), "content": f"CHYBA: Poškozený PDF soubor. {e}"})
            except (OSError, PermissionError) as e:
                logger.error(f"Cannot access PDF file: {pdf_path.name}, {e}")
                documents_to_process.append({"identifier": pdf_path.as_posix(), "content": f"CHYBA: Nelze přistoupit k souboru. {e}"})
            except Exception as e:
                logger.error(f"Unexpected error reading PDF: {pdf_path.name}, {e}")
                documents_to_process.append({"identifier": pdf_path.as_posix(), "content": f"CHYBA: Neočekávaná chyba. {e}"})

        if not documents_to_process: return None

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
        payload = { "model": MODEL_NAME, "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}, "temperature": 0.0 }

        # Logování LLM požadavku
        if self.detailed_logger:
            self.detailed_logger.log_llm_request({
                "model": MODEL_NAME,
                "documents_count": len(documents_to_process),
                "documents": [{"identifier": d["identifier"], "content_length": len(d["content"])} for d in documents_to_process],
                "prompt_length": len(prompt),
                "full_payload": payload
            })

        try:
            response = requests.post(API_URL, headers=self.headers, json=payload, timeout=API_REQUEST_TIMEOUT)
            response.raise_for_status()
            response_json = response.json()
            content_str = response_json["choices"][0]["message"]["content"]
            parsed_results = json.loads(content_str).get("results", [])

            # Logování LLM odpovědi
            if self.detailed_logger:
                self.detailed_logger.log_llm_response({
                    "raw_response": response_json,
                    "parsed_results": parsed_results,
                    "results_count": len(parsed_results)
                })

            return parsed_results
        except Exception as e:
            logger.error(f"Chyba API volání pro dávku: {e}")
            return [{"source_identifier": d["identifier"], "status": "error", "data": [], "error_message": str(e)} for d in documents_to_process]

    def _validate_project(self, project_name: str, pdf_results: Dict[str, Dict], wav_durations: Dict[str, Optional[float]]) -> List[Dict]:
        """
        Hlavní validační metoda, která funguje jako "dispečer".
        Na základě předem určeného módu volá správnou validační funkci.
        """
        wav_paths = list(wav_durations.keys())
        is_consolidated = _detect_mode(wav_paths)

        if is_consolidated:
            return self._validate_consolidated_project(project_name, pdf_results, wav_durations)
        else:
            return self._validate_individual_project(project_name, pdf_results, wav_durations)

    def _detect_consolidated_mode(self, wav_paths: List[str]) -> bool:
        return _detect_mode(wav_paths)

    def _find_wav_for_side(self, side: str, available_wavs: Dict[str, Optional[float]]) -> Optional[str]:
        """
        Pokročilé hledání WAV souboru pro danou stranu.
        Podporuje různé formáty pojmenování: SIDE A, Side_A, side-a, A, atd.
        """
        side_lower = side.lower()

        # Různé patterns pro hledání WAV souboru pro stranu
        patterns = [
            f"side {side_lower}",           # "side a", "side b", "side c"
            f"side_{side_lower}",           # "side_a", "side_b", "side_c"
            f"side-{side_lower}",           # "side-a", "side-b", "side-c"
            f"side{side_lower}",            # "sidea", "sideb", "sidec"
            f"{side_lower} side",           # "a side", "b side", "c side"
            f"{side_lower}_side",           # "a_side", "b_side", "c_side"
            f"{side_lower}-side",           # "a-side", "b-side", "c-side"
            f"{side_lower}side",            # "aside", "bside", "cside"
            f"^{side_lower}[._-]",          # "a.", "b_", "c-" na začátku
            f"[._-]{side_lower}[._-]",      # "_a_", ".b.", "-c-" uprostřed
            f"[._-]{side_lower}$",          # "_a", ".b", "-c" na konci
        ]

        # Hledáme první WAV soubor, který odpovídá některému z patterns
        for wav_path in available_wavs:
            filename_lower = Path(wav_path).name.lower()

            # Přímé hledání v názvu souboru
            for pattern in patterns:
                if pattern.startswith('^') or pattern.endswith('$') or '[' in pattern:
                    # Regex pattern
                    if re.search(pattern, filename_lower):
                        return wav_path
                else:
                    # Jednoduchý substring
                    if pattern in filename_lower:
                        return wav_path

        return None

    def _validate_consolidated_project(self, project_name: str, pdf_results: Dict[str, Dict], wav_durations: Dict[str, Optional[float]]) -> List[Dict]:
        """Zpracovává POUZE projekty v konsolidovaném módu."""
        rows = []
        pdf_result = next(iter(pdf_results.values()), None)
        if not pdf_result or pdf_result.get('status') != 'success':
            pdf_path_str = next(iter(pdf_results.keys()))
            rows.append({"project_title": project_name, "status": "FAIL", "pdf_source": Path(pdf_path_str).name, "notes": f"Extrakce dat z PDF selhala: {pdf_result.get('error_message', 'Neznámá chyba')}"})
            return rows

        pdf_tracks = pdf_result.get('data', [])
        pdf_path_str = pdf_result.get('source_identifier')

        sides = {}
        for track in pdf_tracks:
            side = str(track.get('side', 'N/A')).upper()
            if side not in sides: sides[side] = []
            sides[side].append(track)

        available_wavs = wav_durations.copy()

        for side, tracks_on_side in sides.items():
            pdf_total_duration = sum(t.get('duration_seconds', 0) for t in tracks_on_side if t.get('duration_seconds') is not None)

            # Pokročilé hledání WAV souboru pro stranu
            wav_path_for_side = self._find_wav_for_side(side, available_wavs)
            if not wav_path_for_side:
                wav_path_for_side = next((p for p in available_wavs if "master" in Path(p).name.lower()), None)

            wav_dur = available_wavs.pop(wav_path_for_side, None) if wav_path_for_side else None

            diff = wav_dur - pdf_total_duration if wav_dur is not None else None
            status = "OK"
            notes = f"Celkem {len(tracks_on_side)} skladeb."
            if diff is not None and abs(diff) > VALIDATION_TOLERANCE_SECONDS:
                status = "ERROR"
                notes += f" Rozdíl překročil toleranci {VALIDATION_TOLERANCE_SECONDS}s."
            elif wav_dur is None:
                status = "FAIL"
                notes = "Nepodařilo se najít odpovídající WAV pro stranu."

            rows.append({
                "project_title": project_name, "status": status, "validation_item": f"Side {side}",
                "item_type": "SIDE", "pdf_duration_mmss": seconds_to_mmss(pdf_total_duration).replace('+', ''),
                "wav_duration_mmss": seconds_to_mmss(wav_dur).replace('+', ''), "difference_mmss": seconds_to_mmss(diff),
                "pdf_duration_sec": safe_round(pdf_total_duration),
                "wav_duration_sec": safe_round(wav_dur),
                "difference_sec": safe_round(diff),
                "pdf_source": Path(pdf_path_str).name,
                "wav_source": Path(wav_path_for_side).name if wav_path_for_side else "N/A",
                "notes": notes
            })
        return rows

    def _validate_individual_project(self, project_name: str, pdf_results: Dict[str, Dict], wav_durations: Dict[str, Optional[float]]) -> List[Dict]:
        """Zpracovává POUZE projekty v individuálním módu."""
        rows = []
        pdf_result = next(iter(pdf_results.values()), None)
        if not pdf_result or pdf_result.get('status') != 'success':
            pdf_path_str = next(iter(pdf_results.keys()))
            rows.append({"project_title": project_name, "status": "FAIL", "pdf_source": Path(pdf_path_str).name, "notes": f"Extrakce dat z PDF selhala: {pdf_result.get('error_message', 'Neznámá chyba')}"})
            return rows

        pdf_tracks = pdf_result.get('data', [])
        pdf_path_str = pdf_result.get('source_identifier')

        available_wavs = {k: v for k, v in wav_durations.items() if v is not None}
        for track in pdf_tracks:
            pdf_dur = track.get('duration_seconds')
            track_title = track.get('title', '')

            best_match_wav, highest_score = None, 0
            for wav_path, wav_dur in available_wavs.items():
                score = fuzz.token_set_ratio(normalize_string(track_title), normalize_string(Path(wav_path).stem))
                if score > highest_score:
                    highest_score, best_match_wav = score, wav_path

            wav_path_str, wav_dur, notes = None, None, ""
            if highest_score > 70:
                wav_path_str, wav_dur = best_match_wav, available_wavs.pop(best_match_wav)
            else:
                notes = "Nepodařilo se spárovat WAV soubor podle názvu."

            diff = wav_dur - pdf_dur if wav_dur is not None and pdf_dur is not None else None
            status = "OK"
            if diff is not None and abs(diff) > VALIDATION_TOLERANCE_SECONDS:
                status, notes = "ERROR", f"Rozdíl překročil toleranci {VALIDATION_TOLERANCE_SECONDS}s"
            elif wav_path_str is None:
                status = "FAIL"

            rows.append({
                "project_title": project_name, "status": status, "validation_item": track_title,
                "item_type": "TRACK", "pdf_duration_mmss": seconds_to_mmss(pdf_dur).replace('+', ''),
                "wav_duration_mmss": seconds_to_mmss(wav_dur).replace('+', ''), "difference_mmss": seconds_to_mmss(diff),
                "pdf_duration_sec": safe_round(pdf_dur),
                "wav_duration_sec": safe_round(wav_dur),
                "difference_sec": safe_round(diff),
                "pdf_source": Path(pdf_path_str).name,
                "wav_source": Path(wav_path_str).name if wav_path_str else "N/A",
                "notes": notes
            })

        for wav_path_str, wav_dur in available_wavs.items():
            rows.append({"project_title": project_name, "status": "WARN", "wav_source": Path(wav_path_str).name, "notes": "Tento WAV soubor nebyl spárován s žádnou skladbou z PDF."})

        return rows

# Grafické uživatelské rozhraní
class VinylPreflightApp:
    def __init__(self, root: tk.Tk, api_key: str):
        self.root = root
        self.api_key = api_key
        self.processor_thread = None
        root.title("Vinyl Preflight Processor v2.5")
        root.geometry("800x400")
        root.minsize(600, 300)

        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill="both", expand=True)

        input_frame = ttk.LabelFrame(main_frame, text="1. Výběr zdroje", padding="10")
        input_frame.pack(fill="x", pady=5)

        self.folder_path = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.folder_path, state="readonly").pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(input_frame, text="Procházet...", command=self.browse_directory).pack(side="left")

        run_frame = ttk.LabelFrame(main_frame, text="2. Zpracování", padding="10")
        run_frame.pack(fill="x", pady=5)

        self.start_button = ttk.Button(run_frame, text="Spustit zpracování", command=self.start_processing, state="disabled")
        self.start_button.pack(pady=10)

        self.progress_bar = ttk.Progressbar(run_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", pady=5)

        self.status_label = ttk.Label(run_frame, text="Připraveno. Vyberte adresář s projekty.")
        self.status_label.pack(pady=5)

    def browse_directory(self):
        directory = filedialog.askdirectory(title="Vyberte kořenový adresář s projekty")
        if directory:
            self.folder_path.set(directory)
            self.start_button.config(state="normal")
            self.status_label.config(text=f"Vybrán adresář: {directory}")

    def start_processing(self):
        source_dir = self.folder_path.get()
        if not source_dir or not os.path.isdir(source_dir):
            messagebox.showerror("Chyba", "Vyberte prosím platný adresář.")
            return

        self.start_button.config(state="disabled")

        processor = PreflightProcessor(self.api_key, self.update_progress, self.update_status)
        self.processor_thread = threading.Thread(target=processor.run, args=(source_dir,), daemon=True)
        self.processor_thread.start()

    def update_progress(self, value: int, maximum: int):
        self.root.after(0, self._do_update_progress, value, maximum)

    def _do_update_progress(self, value: int, maximum: int):
        if maximum > 0:
            self.progress_bar["maximum"] = maximum
            self.progress_bar["value"] = value

    def update_status(self, text: str):
        self.root.after(0, self._do_update_status, text)

    def _do_update_status(self, text: str):
        self.status_label.config(text=text)

# Vstupní bod aplikace

if __name__ == "__main__":
    if os.name == 'nt' or sys.platform == 'darwin':
        mp.freeze_support()

    dotenv_path = Path(__file__).resolve().parent.parent / '.env'
    load_dotenv(dotenv_path=dotenv_path)
    API_KEY = os.getenv("OPENROUTER_API_KEY")

    if not API_KEY:
        messagebox.showerror(
            "Chyba konfigurace",
            "API klíč (OPENROUTER_API_KEY) nebyl nalezen.\n\n"
            "Ujistěte se, že máte v hlavní složce projektu soubor '.env' se správným obsahem."
        )
        sys.exit(1)

    root = tk.Tk()
    app = VinylPreflightApp(root, API_KEY)
    root.mainloop()