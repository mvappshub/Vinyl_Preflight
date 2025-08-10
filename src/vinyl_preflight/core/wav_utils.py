from pathlib import Path
import soundfile as sf

def get_wav_duration(path: Path) -> float:
    # vrátí délku v sekundách
    info = sf.info(path)
    return info.duration

