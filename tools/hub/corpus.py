"""Public-replay corpus: games of other teams, collected continuously by the daemon within a per-cycle budget.

Purpose (director, 29 Sep 2026): data from outside our bots and outside our live games — every recent game of the
top of the ladder and of the band that decides our rating — so the statistics that separate winners from losers can
be measured on the whole field, and so decoy submissions (a team fielding a weak bot between autoscrims) can be told
apart by time, series requester and the bot names in the replay header.

Layout under `<repo>/public_replays/corpus/`:
    index.jsonl          one line per game: identity, timing, teams/submissions (when the API gives them), header names
    replays/<gid>.replay the raw replay bytes as served (gzip when the server gzips)
    ladder/<stamp>.json  the ladder snapshot at each fetch pass (ratings over time)
    teams.json           the watch list and per-team progress
Discovery uses the public /games?teams=<id> pages (no key); metadata and replay bytes use the authenticated API
through the hub client (the key never leaves the client; the signed redirect is followed without the bearer header).
"""
import gzip
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from . import db

AUTOSCRIM_MINUTES = 40   # autoscrims start 4–36 min after the even UTC hour (A1-Q9)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def watch_list(cfg, ladder):
    """Explicit teams + top N + a rank band, deduplicated, with per-team targets."""
    c = cfg.get('corpus') or {}
    ranked = sorted((t for t in ladder or [] if t.get('rank') and not t.get('dev')), key=lambda t: t['rank'])
    out = {}
    for t in c.get('teams') or []:
        out[int(t['id'])] = dict(id=int(t['id']), target=int(t.get('games', c.get('per_team', 60))), why=t.get('why', 'explicit'))
    for t in ranked[:int(c.get('top_n', 0))]:
        out.setdefault(t['id'], dict(id=t['id'], target=int(c.get('per_team', 60)), why=f"top {c.get('top_n')}", rank=t['rank']))
    lo, hi = (c.get('band') or [0, -1])
    for t in ranked:
        if lo <= t['rank'] <= hi:
            out.setdefault(t['id'], dict(id=t['id'], target=int(c.get('per_team', 60)), why=f'band {lo}-{hi}', rank=t['rank']))
    for t in ranked:
        if t['id'] in out:
            out[t['id']].setdefault('rank', t['rank'])
            out[t['id']]['rating'] = t.get('rating') or t.get('elo')
    me = (cfg.get('team') or {}).get('id')
    out.pop(me, None)
    return out


def header(path):
    """Bot names and map hash from the replay header without decoding the rounds (the vendored Reader)."""
    raw = Path(path).read_bytes()
    packed = gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw
    tmp = Path(path).with_suffix('.hdr.tmp')
    tmp.write_bytes(packed)
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent / 'vendor' / 'leviathan'))
        from replay import Reader  # noqa: WPS433
        r = Reader(str(tmp))
        root = r.object(0, 0)
        maptext = root.text(0)
        return dict(version=root.num(0, 'I'), bot_a=root.text(1), bot_b=root.text(2), map_hash=hashlib.sha256(maptext.encode()).hexdigest(),
                    map_name=next((l[9:] for l in maptext.splitlines() if l.startswith('MAP_NAME ')), None))
    finally:
        tmp.unlink(missing_ok=True)


def autoscrim_window(requested_iso):
    try:
        t = datetime.fromisoformat(requested_iso.replace('Z', '+00:00'))
    except Exception:
        return None
    minute = t.hour * 60 + t.minute
    return any(h * 60 - 2 <= minute <= h * 60 + AUTOSCRIM_MINUTES for h in range(0, 24, 2))


def load_index(dest):
    have = {}
    path = dest / 'index.jsonl'
    if path.exists():
        for line in path.read_text().splitlines():
            try:
                row = json.loads(line)
                have[int(row['game_id'])] = row
            except (ValueError, KeyError):
                continue
    return have


def fetch_pass(root, cfg, client, log, discover=None, budget_seconds=None, max_downloads=None, ladder=None):
    """One bounded pass: pick the team furthest below its target, discover its games, download the new ones."""
    c = cfg.get('corpus') or {}
    if not c.get('enabled'):
        return None
    repo = Path(cfg['paths']['repo'])
    dest = repo / c.get('dest', 'public_replays/corpus')
    (dest / 'replays').mkdir(parents=True, exist_ok=True)
    (dest / 'ladder').mkdir(parents=True, exist_ok=True)
    budget = float(budget_seconds if budget_seconds is not None else c.get('per_cycle_seconds', 150))
    cap = int(max_downloads if max_downloads is not None else c.get('per_cycle_downloads', 40))
    started = time.monotonic()
    if ladder is None:
        conn = db.connect(root)
        ladder = db.kv_get(conn, 'ladder') or []
        conn.close()
    if ladder:
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        (dest / 'ladder' / f'{stamp}.json').write_text(json.dumps(ladder))
    teams = watch_list(cfg, ladder)
    have = load_index(dest)
    counts = {}
    for row in have.values():
        for tid in (row.get('team_a'), row.get('team_b')):
            if tid in teams:
                counts[tid] = counts.get(tid, 0) + 1
    progress = {tid: dict(t, have=counts.get(tid, 0)) for tid, t in teams.items()}
    (dest / 'teams.json').write_text(json.dumps(dict(at=now_iso(), teams=progress), indent=1))
    todo = sorted((t for t in progress.values() if t['have'] < t['target']), key=lambda t: (t['have'] / max(1, t['target']), t.get('rank', 10**6)))
    if not todo:
        return dict(teams=len(teams), fetched=0, note='all targets met')
    if discover is None:
        sys.path.insert(0, str(repo / 'tools'))
        import download_team_games as dtg  # noqa: WPS433
        discover = lambda tid, n: dtg.discover_games(tid, client.base, max_games=n)
    fetched, errors, tried = 0, [], []
    for t in todo:
        if time.monotonic() - started > budget or fetched >= cap:
            break
        tried.append(t['id'])
        try:
            ids = discover(t['id'], t['target'] + 20)
        except Exception as exc:
            errors.append(dict(team=t['id'], error=f'discover: {type(exc).__name__}: {str(exc)[:120]}'))
            continue
        new = [g for g in ids if g not in have][: max(0, t['target'] - t['have'])]
        for gid in new:
            if time.monotonic() - started > budget or fetched >= cap:
                break
            try:
                meta = client.get(f'/api/v1/battles/{gid}')
                m = meta.get('match') or meta
                path = dest / 'replays' / f'{gid}.replay'
                if not path.exists():
                    client.download_replay(gid, path)
                raw = path.read_bytes()
                try:
                    hdr = header(path)
                except Exception as exc:
                    hdr = dict(error=f'{type(exc).__name__}: {str(exc)[:80]}')
                row = dict(game_id=gid, series_id=m.get('seriesId'), team_a=m.get('teamAId'), team_b=m.get('teamBId'), sub_a=m.get('submissionAId'), sub_b=m.get('submissionBId'),
                           ranked=m.get('ranked'), requested_at=m.get('requestedAt'), started_at=m.get('startedAt'), finished_at=m.get('finishedAt') or m.get('completedAt'),
                           requested_by=m.get('requestedBy'), map_id=m.get('mapId'), map_name=meta.get('mapName'), winner=m.get('winner'), status=m.get('status'),
                           seed=m.get('seed'), autoscrim_window=autoscrim_window(m.get('requestedAt') or ''), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                           fetched_at=now_iso(), watch_team=t['id'])
                row.update({('header_' + k if k in row else k): v for k, v in hdr.items()})   # header map_name/map_hash beside the API's
                with (dest / 'index.jsonl').open('a') as handle:
                    handle.write(json.dumps(row, default=str) + '\n')
                have[gid] = row
                fetched += 1
            except Exception as exc:
                errors.append(dict(team=t['id'], game=gid, error=f'{type(exc).__name__}: {str(exc)[:120]}'))
                if len(errors) >= 5:
                    break
    out = dict(teams=len(teams), tried=tried, fetched=fetched, errors=errors[:5], seconds=round(time.monotonic() - started), have=len(have))
    if log:
        log(f"corpus: fetched {fetched} replays for {tried} in {out['seconds']} s (index {len(have)}); errors {len(errors)}")
    return out
