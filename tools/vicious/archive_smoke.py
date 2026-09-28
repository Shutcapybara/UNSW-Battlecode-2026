"""Extract our verified release ZIPs, run native, and compare frozen fixtures."""
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

from panel import hashes
from tools.benchmarking.tournament import MatchWorkers, play
from verify import parity

ROOT = Path(__file__).resolve().parents[2]
C = Path(json.loads((ROOT / 'tools/vicious/current.json').read_text())['directory'])
out = C / 'release/archive_smoke'
out.mkdir(exist_ok=True)
checks = []
for record, reference, arm in [
    ('CROWN_ARCHIVE.json', 'cycle_04/broad', 'vicious-x12-crown-clear'),
    ('FEED_ARCHIVE.json', 'cycle_05/late_specialist', 'vicious-x15-late-time')]:
    metadata = C / 'release' / record
    if not metadata.exists():
        continue
    package = json.loads(metadata.read_text()); archive = Path(package['archive'])
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == package['sha256']
    p = C / reference
    ref = next(r for r in json.loads((p / 'results.json').read_text())
               if r['arm'] == arm and r['opponent'] == 'newton-x10-candidate'
               and r['map'] == 'Colosseum' and r['side'] == 'A')
    with tempfile.TemporaryDirectory(prefix='vicious-archive-', dir='/private/tmp') as tmp:
        tmp = Path(tmp); extracted = tmp / archive.stem; extracted.mkdir()
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            assert set(z.namelist()) == set(package['files'])
            assert all(Path(n).name == n for n in z.namelist())
            z.extractall(extracted)
        assert hashes(extracted) == package['files']
        workers = MatchWorkers(str(tmp / 'native-build'))
        try:
            result = play(str(ROOT / 'tools/vicious/runner'), p / 'sources/maps/Colosseum.map',
                          extracted, p / 'sources' / ref['opponent'], out, archive.stem,
                          300, True, workers, False, seed=int(ref['seed']))
        finally:
            workers.cancel()
        assert result['outcome'] != 'error', result
        check = parity(out / result['replay'], p / 'games' / ref['replay'])
        check.update(archive=str(archive), archive_sha256=package['sha256'],
                     verified_extracted_hashes=True, native_result=result)
        checks.append(check)
        print(archive.stem, result['outcome'], 'exact actions:', check['equal_actions'], flush=True)
(C / 'release/ARCHIVE_SMOKE.json').write_text(json.dumps(checks, indent=2) + '\n')
