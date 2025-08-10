from typing import Optional


def seconds_to_mmss(seconds: Optional[float]) -> str:
    if seconds is None:
        return "N/A"
    if not isinstance(seconds, (int, float)):
        return "Chyba"
    sign = '-' if seconds < 0 else '+'
    seconds = abs(seconds)
    minutes, remaining_seconds = divmod(round(seconds), 60)
    return f"{sign}{minutes:02d}:{remaining_seconds:02d}"


def safe_round(value: Optional[float], decimals: int = 2) -> Optional[float]:
    """Safely round a float value, returning None if input is None"""
    return round(value, decimals) if value is not None else None

