from pathlib import Path
import re
from typing import Dict, Optional

def find_wav_for_side(side: str, available_wavs: Dict[str, Optional[float]]) -> Optional[str]:
    """Pokročilé hledání WAV souboru pro danou stranu (A/B/C...)."""
    side_lower = side.lower()
    patterns = [
        f"side {side_lower}",
        f"side_{side_lower}",
        f"side-{side_lower}",
        f"side{side_lower}",
        f"{side_lower} side",
        f"{side_lower}_side",
        f"{side_lower}-side",
        f"{side_lower}side",
        f"^{side_lower}[._-]",
        f"[._-]{side_lower}[._-]",
        f"[._-]{side_lower}$",
    ]
    for wav_path in available_wavs:
        filename_lower = Path(wav_path).name.lower()
        for pattern in patterns:
            if pattern.startswith('^') or pattern.endswith('$') or '[' in pattern:
                if re.search(pattern, filename_lower):
                    return wav_path
            else:
                if pattern in filename_lower:
                    return wav_path
    return None

