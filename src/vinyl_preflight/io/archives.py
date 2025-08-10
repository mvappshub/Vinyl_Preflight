from pathlib import Path
import zipfile
import logging

logger = logging.getLogger(__name__)


def safe_extract_zip(zip_path: Path, dest: Path) -> None:
    # jednoduchá bezpečná extrakce: kontrola cesty a extrakce
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as z:
        for member in z.namelist():
            # zabránit path traversal
            p = Path(member)
            if p.is_absolute() or '..' in p.parts:
                raise RuntimeError('Unsafe zip member: ' + member)
        z.extractall(dest)


def safe_extract_rar(rar_path: Path, dest: Path) -> None:
    """Jednoduchá extrakce RAR (pokud je k dispozici rarfile)."""
    dest.mkdir(parents=True, exist_ok=True)
    try:
        import rarfile  # type: ignore
    except Exception:
        logger.warning("rarfile není dostupný, přeskočeno: %s", rar_path)
        return
    try:
        with rarfile.RarFile(rar_path, 'r') as rf:  # type: ignore
            rf.extractall(dest)
    except Exception as e:
        logger.error("Chyba při extrakci RAR '%s': %s", rar_path.name, e)

