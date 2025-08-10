from pathlib import Path
import re
from typing import List, Dict, Optional
from vinyl_preflight.utils.timefmt import seconds_to_mmss, safe_round
from vinyl_preflight.core.matcher import find_wav_for_side

VALIDATION_TOLERANCE_SECONDS = 10


def detect_consolidated_mode(wav_paths: List[str]) -> bool:
    """Heuristika pro rozpoznání consolidated módu (A/B/C strany)."""
    wav_count = len(wav_paths)
    if wav_count == 0 or wav_count > 4:
        return False

    consolidated_patterns = [
        r'(?i)side[\s_-]*[abc123]',
        r'(?i)[abc123][\s_-]*side',
        r'(?i)^[abc123][\s_.-]*$',
        r'(?i)master[\s_-]*[abc123]',
        r'(?i)[abc123][\s_-]*master',
        r'(?i)full[\s_-]*side',
        r'(?i)complete[\s_-]*[abc]',
    ]
    individual_patterns = [
        r'^\d{1,2}[\s_.-]',
        r'track[\s_-]*\d+',
        r'\d{2,}[\s_.-]',
    ]

    consolidated_matches = 0
    individual_matches = 0
    for wav_path in wav_paths:
        filename = Path(wav_path).name
        if any(re.search(pattern, filename) for pattern in individual_patterns):
            individual_matches += 1
        elif any(re.search(pattern, filename) for pattern in consolidated_patterns):
            consolidated_matches += 1

    if individual_matches > wav_count / 2:
        return False
    return consolidated_matches > 0 or (wav_count <= 4 and individual_matches == 0)

def validate_consolidated_project(project_name: str, pdf_result: Dict, wav_durations: Dict[str, Optional[float]]) -> List[Dict]:
    rows: List[Dict] = []
    if not pdf_result or pdf_result.get('status') != 'success':
        pdf_path_str = next(iter([k for k in pdf_result.keys() if k != 'status']), 'N/A') if pdf_result else 'N/A'
        rows.append({"project_title": project_name, "status": "FAIL", "pdf_source": Path(pdf_path_str).name if pdf_path_str != 'N/A' else 'N/A', "notes": f"Extrakce dat z PDF selhala: {pdf_result.get('error_message', 'Neznámá chyba') if pdf_result else 'Neznámá chyba'}"})
        return rows

    pdf_tracks = pdf_result.get('data', [])
    pdf_path_str = pdf_result.get('source_identifier', 'N/A')

    sides: Dict[str, List[Dict]] = {}
    for track in pdf_tracks:
        side = str(track.get('side', 'N/A')).upper()
        sides.setdefault(side, []).append(track)

    available_wavs = dict(wav_durations)
    for side, tracks_on_side in sides.items():
        pdf_total_duration = sum(t.get('duration_seconds', 0) for t in tracks_on_side if t.get('duration_seconds') is not None)
        wav_path_for_side = find_wav_for_side(side, available_wavs) or next((p for p in available_wavs if "master" in Path(p).name.lower()), None)
        wav_dur = available_wavs.pop(wav_path_for_side, None) if wav_path_for_side else None

        diff = (wav_dur - pdf_total_duration) if wav_dur is not None else None
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
            "pdf_source": Path(pdf_path_str).name if pdf_path_str != 'N/A' else 'N/A',
            "wav_source": Path(wav_path_for_side).name if wav_path_for_side else "N/A",
            "notes": notes
        })
    return rows


def validate_individual_project(project_name: str, pdf_result: Dict, wav_durations: Dict[str, Optional[float]]) -> List[Dict]:
    from thefuzz import fuzz
    from vinyl_preflight.utils.text import normalize_string

    rows: List[Dict] = []
    if not pdf_result or pdf_result.get('status') != 'success':
        pdf_path_str = next(iter([k for k in pdf_result.keys() if k != 'status']), 'N/A') if pdf_result else 'N/A'
        rows.append({"project_title": project_name, "status": "FAIL", "pdf_source": Path(pdf_path_str).name if pdf_path_str != 'N/A' else 'N/A', "notes": f"Extrakce dat z PDF selhala: {pdf_result.get('error_message', 'Neznámá chyba') if pdf_result else 'Neznámá chyba'}"})
        return rows

    pdf_tracks = pdf_result.get('data', [])
    pdf_path_str = pdf_result.get('source_identifier', 'N/A')

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
        if highest_score > 70 and best_match_wav is not None:
            wav_path_str, wav_dur = best_match_wav, available_wavs.pop(best_match_wav)
        else:
            notes = "Nepodařilo se spárovat WAV soubor podle názvu."

        diff = (wav_dur - pdf_dur) if wav_dur is not None and pdf_dur is not None else None
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
            "pdf_source": Path(pdf_path_str).name if pdf_path_str != 'N/A' else 'N/A',
            "wav_source": Path(wav_path_str).name if wav_path_str else "N/A",
            "notes": notes
        })

    for wav_path_str, wav_dur in available_wavs.items():
        rows.append({"project_title": project_name, "status": "WARN", "wav_source": Path(wav_path_str).name, "notes": "Tento WAV soubor nebyl spárován s žádnou skladbou z PDF."})

    return rows
