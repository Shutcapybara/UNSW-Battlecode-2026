"""Collect existing experiments and resolve source identities for benchmarking."""
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
from pathlib import Path
import tomllib
import uuid

from game_stats import ROOT, comparison_records, digest, make_record, publish_games, read_parquet


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def effective_hash(files, config):
    """Ignore only Markdown excluded by an explicit packaging include list."""
    includes = tomllib.loads(config).get('project', {}).get('include')
    if not includes:
        return digest(files)
    return digest({k: v for k, v in files.items() if not k.lower().endswith('.md')
                   or any(fnmatch.fnmatch(k, pattern) for pattern in includes)})


def register_source(files, folder, root=ROOT):
    config = folder / 'bot.toml'
    if not config.exists() or sha(config) != files.get('bot.toml'):
        return digest(files)
    content = config.read_text()
    value = dict(files=files, bot_toml=content, effective_sha256=effective_hash(files, content))
    target = root / 'game_stats/sources' / (digest(files) + '.json')
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if json.loads(target.read_text()) != value:
            raise ValueError(f'Conflicting source metadata: {target}')
    else:
        target.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')
    return value['effective_sha256']


def aliases(root=ROOT):
    result = {}
    for path in (root / 'game_stats/sources').glob('*.json'):
        value = json.loads(path.read_text())
        if digest(value['files']) != path.stem or hashlib.sha256(value['bot_toml'].encode()).hexdigest() != value['files']['bot.toml']:
            raise ValueError(f'Invalid source metadata: {path}')
        actual = effective_hash(value['files'], value['bot_toml'])
        if actual != value['effective_sha256']:
            raise ValueError(f'Invalid effective fingerprint: {path}')
        result[path.stem] = actual
    return result


def register_manifest(path, manifest, root):
    for key, files in manifest.get('hashes', {}).items():
        if not isinstance(files, dict) or 'bot.toml' not in files:
            continue
        name = key.removeprefix('bots/')
        for folder in (path.parent / 'sources/bots' / name, path.parent / 'sources' / name):
            if (folder / 'bot.toml').exists():
                register_source(files, folder, root)
                break


def lab_records(path, manifest, games, root):
    """Old lab snapshots hashed overrides AFTER applying them; verify that copy."""
    if not manifest.get('runner_version'):
        raise ValueError('No recorded toolkit version')
    fingerprints = manifest['hashes']
    for name in [manifest['focus'], *manifest['opponents']]:
        for file, expected in fingerprints[name].items():
            if sha(path.parent / 'sources' / name / file) != expected:
                raise ValueError(f'Frozen source changed: {name}/{file}')
    for board in manifest['maps']:
        if sha(path.parent / 'sources' / (board + '.map')) != fingerprints[board + '.map']:
            raise ValueError(f'Frozen map changed: {board}')
    run_id = uuid.uuid5(uuid.NAMESPACE_URL, 'unswbc-lab:' + digest(
        [str(path.parent.relative_to(root)), manifest])).hex
    # These manifests predate timestamps. Preserve an explicitly marked estimate;
    # never use it to decide whether a source revision is the current revision.
    provenance = root / 'game_stats/imports' / (run_id + '.json')
    if provenance.exists():
        started = json.loads(provenance.read_text())['run_started_at']
    else:
        started = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
        provenance.parent.mkdir(parents=True, exist_ok=True)
        provenance.write_text(json.dumps(dict(source=str(path.relative_to(root)),
            run_started_at=started, timestamp_basis='manifest mtime; estimated, not game time'), indent=2) + '\n')
    result = []
    for game in games:
        if game['outcome'] == 'error':
            continue
        a, b, board = game['team_a'], game['team_b'], game['map']
        if a == b or a not in [manifest['focus'], *manifest['opponents']] or b not in [manifest['focus'], *manifest['opponents']] or board not in manifest['maps']:
            raise ValueError('Game outside lab roster')
        winner = a if game['outcome'] == 'A' else b if game['outcome'] == 'B' else None
        if game['winner'] != winner:
            raise ValueError('Winner disagrees with outcome')
        result.append(make_record(run_id=run_id, game_key=json.dumps([board, a, b], separators=(',', ':')),
            source='leviathan_lab', run_started_at=started, bot_a=a, bot_b=b,
            bot_a_sha256=digest(fingerprints[a]), bot_b_sha256=digest(fingerprints[b]),
            map_name=board, map_sha256=fingerprints[board + '.map'],
            mode='sandbox' if manifest['sandbox'] else 'native', runner_version=manifest['runner_version'],
            outcome=game['outcome'], rounds=game.get('rounds')))
    return result


def with_rating_context(manifest):
    """Retired versions anchor inference, but are never added to the play roster."""
    context = manifest.get('rating_context', {})
    effective = dict(context.get('effective_hashes', {})) | manifest['effective_hashes']
    return manifest | dict(bots=sorted(effective), effective_hashes=effective)


def preserve_published_fault_counts(records, existing):
    """Re-imports may not erase published diagnostics; audit metadata-only changes.

    Outcome, source identity and other conflicts still reach the strict publisher.
    """
    known = {row['game_id']: row for row in existing}
    resolved, disagreements = [], []
    for row in records:
        old = known.get(row['game_id'])
        if old and {key for key in row if row[key] != old[key]} == {'runtime_faults'}:
            disagreements.append(dict(game_id=row['game_id'], run_id=row['run_id'],
                published_runtime_faults=old['runtime_faults'],
                reimported_runtime_faults=row['runtime_faults'], action='preserved_published_record'))
            row = old
        resolved.append(row)
    return resolved, disagreements


def collect(root=ROOT):
    """Import identifiable games, inventory other results without inventing provenance."""
    from import_field_stats import field_records
    records, audit = [], []
    for base in ('build', 'experiment_data', 'tools'):
        for path in sorted((root / base).rglob('manifest.json')):
            if any(part in ('sources', '.unswbc-build', 'node_modules') for part in path.relative_to(root).parts):
                continue
            result_path = path.parent / 'results.json'
            if not result_path.exists() and not (path.parent / 'games.sqlite3').exists():
                continue
            entry = dict(path=str(path.relative_to(root)), recorded=0, imported=0)
            try:
                manifest = json.loads(path.read_text())
                games = json.loads(result_path.read_text()) if result_path.exists() else []
                entry['recorded'] = len(games)
                if manifest.get('benchmark_version'):
                    continue  # This runner publishes its own durable journal.
                register_manifest(path, manifest, root)
                if manifest.get('prepared') and (path.parent / 'games.sqlite3').exists():
                    batch, info = field_records(path.parent)
                    entry['recorded'] = info['completed'] + info['errors']
                elif 'candidate' in manifest and 'hashes' in manifest:
                    if 'run_id' not in manifest:
                        identity = {k: manifest[k] for k in ('created', 'candidate', 'opponents', 'maps', 'hashes')}
                        manifest['run_id'] = uuid.uuid5(uuid.NAMESPACE_URL, 'unswbc-comparison:' + digest(identity)).hex
                    batch = comparison_records(manifest, games)
                elif 'focus' in manifest and 'hashes' in manifest:
                    batch = lab_records(path, manifest, games, root)
                else:
                    raise ValueError('Missing individual bot/map fingerprints or unsupported manifest')
                records.extend(batch)
                entry.update(status='imported', imported=len(batch))
            except (ValueError, KeyError, OSError) as error:
                entry.update(status='unverified', reason=str(error))
            audit.append(entry)
        # Ouroboros's older JSONL runner did not save source/map fingerprints.
        for path in sorted((root / base).rglob('meta.json')):
            result = path.parent / 'results.jsonl'
            if result.exists() and not (path.parent / 'manifest.json').exists():
                audit.append(dict(path=str(path.relative_to(root)), status='unverified', imported=0,
                    recorded=sum(bool(line.strip()) for line in result.read_text().splitlines()),
                    reason='Older JSONL runner did not record bot/map fingerprints'))
    ledger = root/'game_stats.parquet'
    records, disagreements = preserve_published_fault_counts(
        records, read_parquet(ledger) if ledger.exists() else [])
    publication = publish_games(records, root)
    return dict(publication=publication, sources=audit, metadata_disagreements=disagreements)
