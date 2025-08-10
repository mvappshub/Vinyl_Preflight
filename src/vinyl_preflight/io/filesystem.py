from pathlib import Path
import shutil

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def safe_copy(src: Path, dest: Path):
    ensure_dir(dest.parent)
    shutil.copy2(src, dest)

