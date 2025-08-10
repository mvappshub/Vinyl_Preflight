import csv
from pathlib import Path
from typing import Iterable, Mapping

def write_csv(path: Path, rows: Iterable[Mapping[str, object]], headers: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

