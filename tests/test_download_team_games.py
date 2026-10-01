import importlib.util
import json
from pathlib import Path
import urllib.error


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "download_team_games.py"
SPEC = importlib.util.spec_from_file_location("download_team_games", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_game_page_parser_only_keeps_rows_for_requested_team():
    parser = MODULE.GamePageParser(7)
    parser.feed(
        """<main><p>1–2 of 2 games</p><table><tbody>
        <tr><td><a href='/teams/7'>Target</a></td><td><a href='/battles/42'>Watch</a></td></tr>
        <tr><td><a href='/teams/8'>Other</a></td><td><a href='/battles/99'>Watch</a></td></tr>
        </tbody></table></main>"""
    )
    parser.close()
    assert parser.game_ids == [42]
    assert parser.total == 2


def test_load_api_key_uses_ignored_file_and_environment_override(tmp_path, monkeypatch):
    key_file = tmp_path / ".battlecode-api-key"
    key_file.write_text("bc_from_file\n")
    monkeypatch.delenv("BATTLECODE_API_KEY", raising=False)
    class HomePath:
        @staticmethod
        def home():
            return tmp_path
    monkeypatch.setattr(MODULE, "Path", HomePath)
    assert MODULE.load_api_key(key_file) == "bc_from_file"
    store = tmp_path / ".unswbc" / "keys.json"
    store.parent.mkdir()
    store.write_text(json.dumps({MODULE.DEFAULT_BASE_URL: "bc_from_cli_store"}))
    assert MODULE.load_api_key(key_file) == "bc_from_cli_store"
    monkeypatch.setenv("BATTLECODE_API_KEY", "bc_from_environment")
    assert MODULE.load_api_key(key_file) == "bc_from_environment"


def test_discovers_pages(monkeypatch):
    def fake_request(url, **_kwargs):
        ids = [10, 11] if "page=1" in url else []
        rows = "".join(
            f"<tr><td><a href='/teams/7'>Team</a></td><td><a href='/battles/{game_id}'>Watch</a></td></tr>"
            for game_id in ids
        )
        return f"<main><p>1–2 of 2 games</p><table><tbody>{rows}</tbody></table></main>".encode()

    monkeypatch.setattr(MODULE, "request", fake_request)
    assert MODULE.discover_games(7, "https://game.battlecode.au") == [10, 11]


def test_discovers_older_completed_games_after_pending_page(monkeypatch):
    def fake_request(url, **_kwargs):
        assert 'kind=ranked' in url
        replay = '' if 'page=1' in url else "<a href='/battles/42'>Watch</a>"
        return f"<p>1 of 2 games</p><table><tr><td><a href='/teams/7'>Team</a>{replay}</td></tr></table>".encode()
    monkeypatch.setattr(MODULE, 'request', fake_request)
    assert MODULE.discover_games(7, 'https://example.test', kind='ranked') == [42]


def test_download_does_not_leak_key_to_signed_url(tmp_path, monkeypatch):
    seen_blob_authorization = []

    class RedirectOpener:
        def open(self, request, timeout):
            assert request.get_header("Authorization") == "Bearer bc_test"
            raise urllib.error.HTTPError(
                request.full_url,
                302,
                "Found",
                {"Location": "https://downloads.example/10"},
                None,
            )

    class Response:
        def read(self):
            return b"replay-bytes"

    class BlobOpener:
        def open(self, request, timeout):
            seen_blob_authorization.append(request.get_header("Authorization"))
            return Response()

    openers = iter([RedirectOpener(), BlobOpener()])
    monkeypatch.setattr(MODULE.urllib.request, "build_opener", lambda *_args: next(openers))
    destination = tmp_path / "10.replay"
    MODULE.download_replay(10, destination, "https://game.battlecode.au", "bc_test")
    assert destination.read_bytes() == b"replay-bytes"
    assert seen_blob_authorization == [None]


def test_submission_id_for_team_reads_battle_game_sides():
    game = {
        "id": 42,
        "teamA": {"id": 7, "submissionId": 8751},
        "teamB": {"id": 8, "submissionId": 9001},
    }
    assert MODULE.submission_id_for_team(game, 7) == 8751
    assert MODULE.submission_id_for_team(game, 8) == 9001
    assert MODULE.submission_id_for_team(game, 9) is None


def test_matching_games_filters_by_exact_submission(monkeypatch):
    payloads = {
        10: {"games": [{"id": 101, "teamA": {"id": 7, "submissionId": 8751}}]},
        11: {"games": [{"id": 111, "teamA": {"id": 7, "submissionId": 8752}}]},
    }
    monkeypatch.setattr(MODULE, "get_json", lambda _base, path, _key: payloads[int(path.rsplit('/', 1)[-1])])
    assert MODULE.matching_games([10, 11], 7, 8751, "https://example.test", "key") == [
        {"game_id": 101, "battle_id": 10, "metadata": payloads[10]["games"][0]}
    ]
