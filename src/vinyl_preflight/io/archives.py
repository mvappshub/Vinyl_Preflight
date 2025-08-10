from pathlib import Path
import zipfile

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

