"""Candidate registration from a `CANDIDATE.toml` manifest (Part B §5.2) and the bridge into the legacy executor."""
import ast
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

from . import db
from .toml_lite import loads as toml_loads

NAME_RE = re.compile(r'^[a-z0-9][a-z0-9-]{2,60}$')
EXCLUDE_DIRS = {'__pycache__', 'build', '.unswbc-build', '.git'}
EXCLUDE_FILES = {'.DS_Store'}
CONTRACT_KINDS = {'divergence_window', 'behavioural_signature', 'trace_marker', 'legacy_none'}
REQUIRED = ('name', 'lineage', 'author', 'language', 'hypothesis', 'mechanism', 'expected_change')
LANGUAGES = {'python': 'python', 'py': 'python', 'c': 'c', 'cpp': 'cpp', 'c++': 'cpp', 'cxx': 'cpp'}   # manifest spellings -> stored language (the CLI's own aliases)


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree_files(directory):
    directory = Path(directory)
    out = {}
    for path in sorted(directory.rglob('*')):
        rel = path.relative_to(directory)
        if any(part in EXCLUDE_DIRS for part in rel.parts) or path.name in EXCLUDE_FILES or path.suffix == '.pyc':
            continue
        if path.is_file():
            out[rel.as_posix()] = sha256_file(path)
    return out


def fingerprints(files):
    full = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    code = {k: v for k, v in files.items() if not (k == 'CANDIDATE.toml' or k.lower().startswith('readme') or k.lower().endswith('.md'))}
    return full, hashlib.sha256(json.dumps(code, sort_keys=True).encode()).hexdigest()


def legacy_fingerprint(directory):
    """The legacy live-validation identity: top-level .py/.toml only."""
    files = {p.name: sha256_file(p) for p in sorted(Path(directory).iterdir()) if p.is_file() and p.suffix in ('.py', '.toml')}
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest(), files


def validate_manifest(manifest):
    problems = []
    for key in REQUIRED:
        if not str(manifest.get(key, '')).strip():
            problems.append(f'missing {key}')
    if manifest.get('name') and not NAME_RE.match(manifest['name']):
        problems.append('name must be lowercase [a-z0-9-], 3-61 chars')
    if manifest.get('name', '').endswith('-ai'):
        problems.append('name must not end with -ai (the upload name gets the suffix)')
    if LANGUAGES.get(str(manifest.get('language', '')).lower()) is None:
        problems.append('language must be python|c|cpp|c++')
    contract = manifest.get('activation_contract') or {}
    if contract.get('kind') not in CONTRACT_KINDS:
        problems.append('activation_contract.kind must be one of ' + ', '.join(sorted(CONTRACT_KINDS)))
    if contract.get('kind') == 'trace_marker' and not contract.get('markers'):
        problems.append('trace_marker contract needs markers = [[tag, round_lo, round_hi, min_count], ...]')
    if contract.get('kind') == 'divergence_window' and not contract.get('reference'):
        problems.append('divergence_window contract needs reference')
    if contract.get('kind') == 'behavioural_signature' and not contract.get('statistics'):
        problems.append('behavioural_signature contract needs statistics')
    return problems


def register_from_dir(conn, root, directory, actor, priority=None):
    root = Path(root)
    directory = Path(directory).resolve()
    manifest_path = directory / 'CANDIDATE.toml'
    if not manifest_path.exists():
        raise ValueError('CANDIDATE.toml is required in the bot directory')
    if not (directory / 'bot.toml').exists():
        raise ValueError('bot.toml must be at the bot directory root')
    manifest = toml_loads(manifest_path.read_text())
    problems = validate_manifest(manifest)
    if problems:
        raise ValueError('invalid manifest: ' + '; '.join(problems))
    name = manifest['name']
    if conn.execute('SELECT 1 FROM candidates WHERE name=?', (name,)).fetchone():
        raise ValueError(f'candidate {name} already registered; never overwrite a frozen candidate')
    before = tree_files(directory)
    full, code = fingerprints(before)
    dup = conn.execute('SELECT name FROM candidates WHERE code_fingerprint=? OR fingerprint=?', (code, full)).fetchone()
    if dup:
        raise ValueError(f'same code already registered as {dup["name"]} (documentation-only edits are not a new candidate)')
    parent = manifest.get('lineage_parent') or ''
    if parent:
        rejected = conn.execute("SELECT verdict FROM experiments WHERE candidate_name=? AND verdict LIKE 'reject%' OR candidate_name=? AND verdict LIKE 'strategy_lost%'", (parent, parent)).fetchone()
        if rejected and not str(manifest.get('supersedes', '')).strip():
            raise ValueError(f'lineage_parent {parent} was live-rejected; `supersedes` (name + one-line mechanism difference) is required')
    if LANGUAGES[str(manifest['language']).lower()] == 'python':
        for rel in before:
            if rel.endswith('.py'):
                ast.parse((directory / rel).read_text(), filename=rel)
    archive_dir = root / 'candidates'
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive = archive_dir / f'{name}.zip'
    if archive.exists():
        raise ValueError(f'archive {archive} exists; refusing to overwrite')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for rel in before:
            z.write(directory / rel, rel)
    if tree_files(directory) != before:
        archive.unlink()
        raise ValueError('source tree changed while freezing; re-run')
    with zipfile.ZipFile(archive) as z:
        for rel, digest in before.items():
            if hashlib.sha256(z.read(rel)).hexdigest() != digest:
                archive.unlink()
                raise ValueError(f'archive byte-check failed for {rel}')
    row = dict(name=name, fingerprint=full, code_fingerprint=code, archive_path=str(archive), archive_sha256=sha256_file(archive), source_files=before,
               language=LANGUAGES[str(manifest['language']).lower()], lineage=manifest['lineage'], author=manifest['author'], lineage_parent_name=parent or None,
               lineage_parent_fingerprint=None, source_ref='dir:' + str(directory), hypothesis=manifest['hypothesis'], mechanism=manifest['mechanism'],
               expected_change=manifest['expected_change'], activation_contract=manifest.get('activation_contract'),
               local_evidence=manifest.get('local_evidence'), priority=int(priority if priority is not None else manifest.get('priority', 100)),
               status='needs_runtime', registered_by=actor, registered_at=db.now_iso(), dev_only=int(bool(manifest.get('dev_only', False))))
    db.ensure_column(conn, 'candidates', 'dev_only', 'INTEGER DEFAULT 0')
    db.upsert(conn, 'candidates', row, 'name')
    db.event(conn, root, actor, 'candidate_registered', dict(name=name, fingerprint=full, code_fingerprint=code, lineage=manifest['lineage'], dev_only=row['dev_only']))
    return row


def stage_live(conn, root, cfg, name, actor, priority=None):
    """Bridge a hub candidate into the legacy executor's registry (control-following, D-003).

    The legacy preflight copies only top-level .py/.toml files, so the bot must be flat with main.py at the root.
    """
    live = Path(cfg['paths']['legacy_live'])
    row = conn.execute('SELECT * FROM candidates WHERE name=?', (name,)).fetchone()
    if not row:
        raise ValueError(f'unknown candidate {name}')
    row = db.loads_row(row, 'source_files', 'activation_contract', 'local_evidence')
    if row['language'] != 'python':
        raise ValueError('the legacy bridge supports python candidates only; C/C++ waits for the hub actuator')
    src = Path(row['source_ref'][4:]) if row['source_ref'].startswith('dir:') else None
    if not src or not (src / 'main.py').is_file():
        raise ValueError('a flat source tree with main.py at the root is required for the legacy bridge')
    if any('/' in rel for rel in row['source_files']):
        raise ValueError('the legacy bridge cannot freeze subdirectories; flatten the bot first')
    legacy_name = ('hub-' + name)[:60]
    state = json.loads((live / 'state/state.json').read_text())
    reg = json.loads((live / 'registry.json').read_text())
    if any(c['name'] == legacy_name for c in reg):
        raise ValueError(f'{legacy_name} already in the legacy registry')
    dst = live / 'candidates' / legacy_name
    if dst.exists():
        raise ValueError(f'{dst} exists')
    before, _ = legacy_fingerprint(src)
    if any(c.get('fingerprint') == before for c in reg):
        raise ValueError('same code already in the legacy registry')
    dst.mkdir()
    for f in src.iterdir():
        if f.is_file() and f.suffix in ('.py', '.toml') and f.name != 'CANDIDATE.toml':
            shutil.copy2(f, dst / f.name)
    identity, files = legacy_fingerprint(dst)
    archive = dst.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for n in files:
            z.write(dst / n, n)
    live_mac = cfg['paths']['legacy_live'].rstrip('/')
    entry = dict(name=legacy_name, source=f'{live_mac}/candidates/{legacy_name}', archive=f'{live_mac}/candidates/{legacy_name}.zip',
                 archive_sha256=sha256_file(archive), fingerprint=identity, files=files, parent_submission=state['incumbent'], submission=None,
                 changes={}, status='needs_runtime', priority=int(priority if priority is not None else row['priority']),
                 hypothesis=f"{row['hypothesis']} Mechanism: {row['mechanism']} Expected: {row['expected_change']}",
                 registered=db.now_iso(), control_policy='current', hub_candidate=name, registered_by=actor)
    reg.append(entry)
    tmp = live / 'registry.json.tmp'
    tmp.write_text(json.dumps(reg, ensure_ascii=False, indent=2))
    tmp.replace(live / 'registry.json')
    (live / 'state/runner.renew').touch()
    conn.execute('UPDATE candidates SET legacy_name=?, legacy_status=?, legacy_parent_submission=?, control_policy=?, updated_at=? WHERE name=?',
                 (legacy_name, 'needs_runtime', state['incumbent'], 'current', db.now_iso(), name))
    db.event(conn, root, actor, 'candidate_staged_live', dict(name=name, legacy_name=legacy_name, legacy_fingerprint=identity, control=state['incumbent']))
    return entry
