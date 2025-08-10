from vinyl_preflight.io.archives import safe_extract_zip
from pathlib import Path
import zipfile

def test_safe_extract(tmp_path):
    z = tmp_path / 't.zip'
    d = tmp_path / 'out'
    # vytvořit jednoduchý zip
    with zipfile.ZipFile(z, 'w') as zz:
        file = tmp_path / 'a.txt'
        file.write_text('hello')
        zz.write(file, arcname='a.txt')
    safe_extract_zip(z, d)
    assert (d / 'a.txt').exists()

