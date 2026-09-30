"""Size of a bot's upload zip as `unswbc submit` builds it (deflate of project.include; limit 4 MiB).

    .venv/bin/python tools/hb1/zip_size.py BOTDIR [BOTDIR ...]
"""
import io, sys, zipfile
from pathlib import Path
EXT = ('.cpp', '.hpp', '.cc', '.hh', '.c', '.h')
for d in sys.argv[1:]:
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w', zipfile.ZIP_DEFLATED) as a:
        for f in sorted(Path(d).iterdir()):
            if f.suffix in EXT:
                a.write(f, f.name)
    n = len(b.getvalue())
    print(f'{d}: {n / 2**20:.2f} MiB zip ({"OK" if n <= 4 * 2**20 else "OVER"} 4 MiB limit)')
