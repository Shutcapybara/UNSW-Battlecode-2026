#!/usr/bin/env python3
"""Download every available UNSW Battlecode replay involving one team.

The public Games page is used to discover match IDs.  Replay bytes come from
the documented API download endpoint, authenticated with BATTLECODE_API_KEY.
Only Python's standard library is required.

Examples:
    BATTLECODE_API_KEY=bc_... python3 tools/download_team_games.py "Team Name" --submission v12
    python3 tools/download_team_games.py 112 --submission 8751 --dry-run --max-games 20
"""

from __future__ import annotations

import argparse
import html.parser
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable


DEFAULT_BASE_URL = "https://game.battlecode.au"
USER_AGENT = "UNSW-Battlecode-team-replay-downloader/1.0"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KEY_FILE = PROJECT_ROOT / ".battlecode-api-key"


class GamePageParser(html.parser.HTMLParser):
    """Extract completed game IDs and the result count from one Games page."""

    def __init__(self, team_id: int) -> None:
        super().__init__(convert_charrefs=True)
        self.team_path = f"/teams/{team_id}"
        self.game_ids: list[int] = []
        self.total: int | None = None
        self._row_depth = 0
        self._row_hrefs: list[str] = []
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "tr":
            if self._row_depth == 0:
                self._row_hrefs = []
            self._row_depth += 1
        if self._row_depth and tag == "a" and attributes.get("href"):
            self._row_hrefs.append(attributes["href"] or "")

    def handle_endtag(self, tag: str) -> None:
        if tag != "tr" or not self._row_depth:
            return
        self._row_depth -= 1
        if self._row_depth:
            return
        if any(urllib.parse.urlsplit(href).path == self.team_path for href in self._row_hrefs):
            for href in self._row_hrefs:
                match = re.fullmatch(r"/battles/(\d+)", urllib.parse.urlsplit(href).path)
                if match:
                    self.game_ids.append(int(match.group(1)))

    def handle_data(self, data: str) -> None:
        self._text.append(data)

    def close(self) -> None:
        super().close()
        text = " ".join(self._text)
        match = re.search(r"\bof\s+([\d,]+)\s+games\b", text, re.IGNORECASE)
        if match:
            self.total = int(match.group(1).replace(",", ""))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Expose the signed replay URL without forwarding the API key to it."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def request(
    url: str,
    *,
    api_key: str | None = None,
    opener: urllib.request.OpenerDirector | None = None,
    timeout: float = 30,
) -> bytes:
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, headers=headers)
    return (opener or urllib.request.build_opener()).open(req, timeout=timeout).read()


def get_json(base_url: str, path: str, api_key: str) -> Any:
    url = urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    try:
        return json.loads(request(url, api_key=api_key))
    except json.JSONDecodeError as error:
        raise RuntimeError(f"The API returned invalid JSON for {path}.") from error


def _items(payload: Any, *keys: str) -> list[dict[str, Any]]:
    """Return an API collection regardless of its common envelope shape."""
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in keys:
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def _number(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdecimal():
        return int(value)
    return None


def _field(node: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in node:
            return node[key]
    return None


def _nested_id(node: Any, *keys: str) -> int | None:
    if isinstance(node, dict):
        value = _field(node, *keys)
        number = _number(value)
        if number is not None:
            return number
        for child in node.values():
            number = _nested_id(child, *keys)
            if number is not None:
                return number
    elif isinstance(node, list):
        for child in node:
            number = _nested_id(child, *keys)
            if number is not None:
                return number
    return None


def submission_id_for_team(game: dict[str, Any], team_id: int) -> int | None:
    """Extract the submission ID belonging to team_id from one game record."""
    if not isinstance(game, dict):
        return None
    direct_team = _number(_field(game, "teamId", "team_id"))
    direct_submission = _number(_field(game, "submissionId", "submission_id"))
    if direct_team == team_id and direct_submission is not None:
        return direct_submission
    for value in game.values():
        if isinstance(value, dict):
            nested_team = _number(_field(value, "id", "teamId", "team_id"))
            team = value.get("team")
            if isinstance(team, dict):
                nested_team = nested_team or _number(_field(team, "id", "teamId", "team_id"))
            submission = _number(_field(value, "submissionId", "submission_id"))
            submission_node = value.get("submission")
            if isinstance(submission_node, dict):
                submission = submission or _number(_field(submission_node, "id", "submissionId"))
            if nested_team == team_id and submission is not None:
                return submission
            found = submission_id_for_team(value, team_id)
            if found is not None:
                return found
    return None


def battle_games(payload: Any, battle_id: int) -> list[dict[str, Any]]:
    games = _items(payload, "games", "matches", "results")
    if games:
        return games
    if isinstance(payload, dict) and any(key in payload for key in ("teamA", "teamB", "team_a", "team_b")):
        return [dict(payload, id=payload.get("id", battle_id))]
    return []


def resolve_submission(team_id: int, name_or_id: str | None, base_url: str, api_key: str) -> dict[str, Any]:
    submissions = _items(get_json(base_url, "/api/v1/submissions", api_key), "submissions", "versions")
    if not submissions:
        raise RuntimeError("The submissions API returned no usable submission records.")
    wanted_id = _number(name_or_id) if name_or_id else None
    wanted_name = None if wanted_id is not None else (name_or_id or "").casefold().strip()
    matches = []
    for submission in submissions:
        identifier = _number(_field(submission, "id", "submissionId", "submission_id"))
        name = _field(submission, "name", "submissionName", "submission_name")
        owner = _number(_field(submission, "teamId", "team_id"))
        if isinstance(submission.get("team"), dict):
            owner = owner or _number(_field(submission["team"], "id", "teamId", "team_id"))
        if identifier is None or (owner is not None and owner != team_id):
            continue
        if (wanted_id is not None and identifier == wanted_id) or (wanted_name and isinstance(name, str) and name.casefold() == wanted_name):
            matches.append(submission)
    if len(matches) != 1:
        descriptor = name_or_id or "the requested submission"
        raise RuntimeError(f"Could not resolve exactly one submission {descriptor!r} for team {team_id}.")
    result = matches[0]
    result["id"] = _number(_field(result, "id", "submissionId", "submission_id"))
    return result


def matching_games(game_ids: list[int], team_id: int, submission_id: int, base_url: str, api_key: str, *, delay: float = 0.0) -> list[dict[str, Any]]:
    """Fetch battle metadata and retain only games using submission_id."""
    matches = []
    for index, battle_id in enumerate(game_ids):
        payload = get_json(base_url, f"/api/v1/battles/{battle_id}", api_key)
        for game in battle_games(payload, battle_id):
            game_id = _number(_field(game, "id", "gameId", "game_id")) or battle_id
            if submission_id_for_team(game, team_id) == submission_id:
                matches.append({"game_id": game_id, "battle_id": battle_id, "metadata": game})
        if delay and index + 1 < len(game_ids):
            time.sleep(delay)
    return matches


def _team_candidates(value: Any) -> Iterable[tuple[int, str]]:
    if isinstance(value, list):
        for item in value:
            yield from _team_candidates(item)
        return
    if not isinstance(value, dict):
        return

    identifier = value.get("id", value.get("teamId", value.get("team_id")))
    name = value.get("name", value.get("teamName", value.get("team_name")))
    teamish = bool(
        {"rating", "rank", "members", "teamId", "team_id", "bio", "wins", "losses"}
        & set(value)
    )
    if teamish and isinstance(identifier, int) and isinstance(name, str):
        yield identifier, name
    for key, item in value.items():
        if key.lower() == "team" and isinstance(item, dict):
            nested_id = item.get("id")
            nested_name = item.get("name")
            if isinstance(nested_id, int) and isinstance(nested_name, str):
                yield nested_id, nested_name
        yield from _team_candidates(item)


def resolve_team(team: str, base_url: str, api_key: str) -> tuple[int, str | None]:
    if team.isdecimal():
        return int(team), None

    wanted = team.casefold().strip()
    candidates = set(_team_candidates(get_json(base_url, "/api/v1/ratings", api_key)))
    matches = sorted((identifier, name) for identifier, name in candidates if name.casefold() == wanted)
    if not matches:
        similar = sorted(name for _, name in candidates if wanted in name.casefold())[:8]
        hint = f" Similar names: {', '.join(similar)}." if similar else ""
        raise RuntimeError(f"No exact team named {team!r} was found.{hint} Use the numeric team ID if needed.")
    if len(matches) > 1:
        choices = ", ".join(f"{name} (ID {identifier})" for identifier, name in matches)
        raise RuntimeError(f"More than one team has that name: {choices}. Use a numeric team ID.")
    return matches[0]


def discover_games(
    team_id: int,
    base_url: str,
    *,
    max_games: int | None = None,
    timeout: float = 30,
) -> list[int]:
    found: list[int] = []
    seen: set[int] = set()
    page = 1
    expected_total: int | None = None

    while max_games is None or len(found) < max_games:
        query = urllib.parse.urlencode({"teams": team_id, "page": page})
        url = f"{base_url.rstrip('/')}/games?{query}"
        parser = GamePageParser(team_id)
        parser.feed(request(url, timeout=timeout).decode("utf-8", "replace"))
        parser.close()
        expected_total = parser.total if parser.total is not None else expected_total
        new_ids = [game_id for game_id in parser.game_ids if game_id not in seen]
        if not new_ids:
            break
        for game_id in new_ids:
            seen.add(game_id)
            found.append(game_id)
            if max_games is not None and len(found) >= max_games:
                break
        print(f"History page {page}: found {len(found)} game(s)", file=sys.stderr)
        if expected_total is not None and len(found) >= expected_total:
            break
        page += 1
    return found


def _validate_download_url(url: str, base_url: str) -> None:
    parsed = urllib.parse.urlsplit(url)
    base = urllib.parse.urlsplit(base_url)
    local_test = base.hostname in {"127.0.0.1", "localhost"}
    if parsed.scheme not in ({"http", "https"} if local_test else {"https"}) or not parsed.netloc:
        raise RuntimeError("The replay endpoint returned an unsafe download URL.")


def download_replay(
    game_id: int,
    destination: Path,
    base_url: str,
    api_key: str,
    *,
    timeout: float = 60,
) -> None:
    endpoint = f"{base_url.rstrip('/')}/api/v1/battles/{game_id}/replay"
    req = urllib.request.Request(
        endpoint,
        headers={"Authorization": f"Bearer {api_key}", "User-Agent": USER_AGENT},
    )
    no_redirect = urllib.request.build_opener(NoRedirect())
    try:
        response = no_redirect.open(req, timeout=timeout)
        payload = response.read()
        location = None
    except urllib.error.HTTPError as error:
        if error.code not in {301, 302, 303, 307, 308}:
            raise
        payload = b""
        location = error.headers.get("Location")

    if location:
        signed_url = urllib.parse.urljoin(endpoint, location)
        _validate_download_url(signed_url, base_url)
        # Deliberately make a fresh request without Authorization.  The signed
        # storage URL rejects (and must never receive) the Battlecode API key.
        payload = request(signed_url, timeout=timeout)
    if not payload:
        raise RuntimeError(f"Replay {game_id} was empty.")

    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    partial.write_bytes(payload)
    partial.replace(destination)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download replays played by one exact Battlecode submission version."
    )
    parser.add_argument("team", help="exact team name or numeric team ID")
    parser.add_argument("--submission", required=True, help="exact submission name or numeric submission ID")
    parser.add_argument("--out", type=Path, default=Path("public_replays"), help="output directory")
    parser.add_argument("--max-games", type=int, help="download only the newest N games")
    parser.add_argument("--delay", type=float, default=0.55, help="seconds between API downloads")
    parser.add_argument("--overwrite", action="store_true", help="replace replay files already present")
    parser.add_argument("--dry-run", action="store_true", help="list matching game IDs without downloading")
    args = parser.parse_args(argv)
    if args.max_games is not None and args.max_games < 1:
        parser.error("--max-games must be at least 1")
    if args.delay < 0:
        parser.error("--delay cannot be negative")
    return args


def load_api_key(key_file: Path = DEFAULT_KEY_FILE) -> str:
    """Read the environment override or the repository-local ignored key file."""
    environment_key = os.environ.get("BATTLECODE_API_KEY", "").strip()
    if environment_key:
        return environment_key
    try:
        return key_file.read_text().strip()
    except FileNotFoundError:
        return ""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    api_key = load_api_key()
    if not api_key:
        print(
            "Set BATTLECODE_API_KEY or place the bc_... key in .battlecode-api-key; "
            "submission filtering requires authenticated API metadata.",
            file=sys.stderr,
        )
        return 2

    try:
        team_id, team_name = resolve_team(args.team, DEFAULT_BASE_URL, api_key)
        submission = resolve_submission(team_id, args.submission, DEFAULT_BASE_URL, api_key)
        submission_id = submission["id"]
        label = team_name or f"team-{team_id}"
        games = discover_games(team_id, DEFAULT_BASE_URL, max_games=args.max_games)
        if not games:
            print(f"No completed games found for {label} (ID {team_id}).", file=sys.stderr)
            return 0
        print(f"Found {len(games)} candidate battle(s) for {label} (ID {team_id}); "
              f"filtering for submission {submission.get('name', submission_id)!r} (ID {submission_id}).")
        matched = matching_games(games, team_id, submission_id, DEFAULT_BASE_URL, api_key, delay=args.delay)
        output = args.out / f"team-{team_id}" / f"submission-{submission_id}"
        print(f"Submission filter kept {len(matched)} game(s).")
        if args.dry_run:
            print("\n".join(str(item["game_id"]) for item in matched))
            return 0
        downloaded = skipped = failed = 0
        manifest = {
            "team_id": team_id,
            "team_name": team_name,
            "submission_id": submission_id,
            "submission": submission,
            "candidate_battles": games,
            "matched_games": matched,
        }
        (output / "download_manifest.json").parent.mkdir(parents=True, exist_ok=True)
        (output / "download_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        for index, item in enumerate(matched, 1):
            game_id = item["game_id"]
            destination = output / f"{game_id}.replay"
            if destination.exists() and not args.overwrite:
                skipped += 1
                print(f"[{index}/{len(matched)}] {game_id}: already present")
                continue
            try:
                download_replay(game_id, destination, DEFAULT_BASE_URL, api_key)
                destination.with_suffix(".json").write_text(json.dumps({
                    "team_id": team_id,
                    "submission_id": submission_id,
                    "battle_id": item["battle_id"],
                    "game_id": game_id,
                    "metadata": item["metadata"],
                }, indent=2) + "\n")
                downloaded += 1
                print(f"[{index}/{len(matched)}] {game_id}: downloaded")
            except (OSError, RuntimeError, urllib.error.URLError) as error:
                failed += 1
                print(f"[{index}/{len(matched)}] {game_id}: {error}", file=sys.stderr)
            if index < len(matched) and args.delay:
                time.sleep(args.delay)
        print(f"Complete: {downloaded} downloaded, {skipped} skipped, {failed} failed.")
        return 1 if failed else 0
    except (OSError, RuntimeError, urllib.error.URLError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
