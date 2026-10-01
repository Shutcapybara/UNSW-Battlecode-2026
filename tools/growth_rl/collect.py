"""Read-only top-team collection using the repository replay downloader."""
from datetime import datetime, timezone
from pathlib import Path
import time

from tools import download_team_games as downloader
from tools.hub.api import Client
from .data import ROOT, atomic_json


def _numeric_id(value):
    if isinstance(value, dict):
        value = value.get('id') or value.get('teamId') or value.get('team_id')
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _team_id(match, side):
    letter = side.upper()
    value = match.get(f'team{letter}Id')
    if value is None:
        value = match.get(f'team_{side.lower()}_id')
    if value is None:
        value = match.get(f'team{letter}') or match.get(f'team_{side.lower()}')
    return _numeric_id(value)


def _submission_id(match, team_id, side):
    # Battle payloads have used flat submissionAId fields as well as nested
    # team/submission objects. Use the maintained downloader's recursive
    # resolver whenever a team ID is available; leave absent IDs unknown.
    value = match.get(f'submission{side.upper()}Id')
    if value is not None:
        try:
            return int(value)
        except (TypeError, ValueError):
            pass
    return downloader.submission_id_for_team(match, team_id) if team_id is not None else None


def collect(config, destination, stop_file=None, stop_event=None):
    stopped = lambda: ((stop_file is not None and Path(stop_file).exists()) or
                       (stop_event is not None and stop_event.is_set()))
    if stopped():
        return dict(status='stopped', downloaded=0, examined=0, errors=[])
    if not downloader.load_api_key():
        return dict(status='waiting_for_api_key', downloaded=0)
    client = Client(ROOT, min_interval=max(0.6, config.get('delay', 0.6)))
    destination = Path(destination)
    ladder_payload = client.get('/api/v1/ratings')
    ladder = ladder_payload.get('ladder', [])
    if not ladder:
        raise ValueError('ratings API returned no ladder')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    atomic_json(destination / 'ladder' / f'{stamp}.json', ladder)
    teams = config.get('teams') or [dict(id=t['id']) for t in sorted(
        (t for t in ladder if t.get('rank') and not t.get('dev')),
        key=lambda t: t['rank'])[:config.get('top_n', 10)]]
    ranks = {int(t['id']): t.get('rank') for t in ladder}
    downloaded, examined, errors = 0, 0, []
    cap = config.get('max_downloads', 30)
    for team in teams:
        if stopped():
            break
        tid = int(team['id'])
        # Recent profile records are series, while public game pages can be
        # dominated by hundreds of unranked challenges to the strongest teams.
        # Expand ranked series first instead of assuming a UI query value.
        profile = client.get(f'/api/v1/teams/{tid}')
        ids, prefetched = [], {}
        for recent in profile.get('recent', []):
            if stopped():
                break
            if config.get('ranked_only', True) and not recent.get('ranked'):
                continue
            series_game = recent.get('replayId') or recent.get('id')
            if not series_game:
                continue
            series = client.get(f'/api/v1/battles/{series_game}')
            prefetched[int(series_game)] = series
            for item in series.get('games', []):
                if item.get('hasReplay'):
                    ids.append(int(item['id']))
            if (series.get('match') or {}).get('status') == 'completed':
                ids.append(int(series_game))
        if not ids and not stopped():
            ids = downloader.discover_games(tid, client.base, max_games=config.get('recent_games', 40), max_pages=20)
        ids = list(dict.fromkeys(ids))
        for gid in ids:
            if stopped():
                break
            path = destination / 'replays' / f'{gid}.replay'
            receipt_path = path.with_suffix('.json')
            if path.exists() and receipt_path.exists():
                continue
            examined += 1
            if downloaded >= cap or examined > cap * 5:
                break
            try:
                payload = prefetched.get(gid) or client.get(f'/api/v1/battles/{gid}')
                match = payload.get('match') or payload
                if config.get('ranked_only', True) and match.get('ranked') is not True:
                    continue
                # Preserve exact source revisions; never call a team name a
                # persistent policy or infer intentional tanking from a loss.
                team_a, team_b = _team_id(match, 'a'), _team_id(match, 'b')
                sub_a = _submission_id(match, team_a, 'a')
                sub_b = _submission_id(match, team_b, 'b')
                if team.get('submission') is not None:
                    actual = sub_a if team_a == tid else sub_b if team_b == tid else None
                    if actual != int(team['submission']):
                        continue
                if not path.exists() or not receipt_path.exists():
                    # Same downloader used by tools/download_team_games.py;
                    # the hub client adds pacing/retry, never upload calls. Rename
                    # only after a complete download so extraction sees no partial file.
                    temporary = path.with_suffix(path.suffix + '.part')
                    client.download_replay(gid, temporary)
                    temporary.replace(path)
                atomic_json(receipt_path, dict(
                    game_id=gid, battle_id=gid, series_id=match.get('seriesId'),
                    source='public', team_a=team_a, team_b=team_b,
                    submission_a=sub_a, submission_b=sub_b,
                    submission_identity_available=sub_a is not None and sub_b is not None,
                    rank_a=ranks.get(team_a), rank_b=ranks.get(team_b),
                    ranked=match.get('ranked'), requested_at=match.get('requestedAt'),
                    finished_at=match.get('finishedAt') or match.get('completedAt'),
                    fetched_at=stamp, watch_team=tid))
                downloaded += 1
            except Exception as exc:
                # Do not persist HTTP bodies, headers or signed redirect URLs.
                errors.append(dict(game=gid, error=type(exc).__name__))
                if len(errors) >= 5:
                    break
        if downloaded >= cap or len(errors) >= 5 or stopped():
            break
    report = dict(status='stopped' if stopped() else 'complete', downloaded=downloaded,
                  examined=examined, errors=errors)
    atomic_json(destination / 'collection_status.json', report)
    return report
