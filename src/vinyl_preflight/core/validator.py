from pathlib import Path
import re
from typing import List, Dict, Optional

VALIDATION_TOLERANCE_SECONDS = 10

def seconds_to_mmss(seconds: Optional[float]) -> str:
    if seconds is None:
        return "N/A"
    sign = '-' if seconds < 0 else '+'
    seconds = abs(seconds)
    minutes, remaining_seconds = divmod(round(seconds), 60)
    return f"{sign}{minutes:02d}:{remaining_seconds:02d}"


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

