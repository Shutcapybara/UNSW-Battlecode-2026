"""Battlecode API client for the hub executor.

Read-only calls retry bounded transport failures; mutations never retry (the executor's durable intents reconcile
them by exact identity instead). The credential is read through `tools/download_team_games.py::load_api_key` and is
never logged. Replays are downloaded with `NoRedirect` so the bearer header is not forwarded to the signed URL.
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = 'https://game.battlecode.au'
RETRY_AFTER = re.compile(r'(\d+)\s*min')


class APIError(Exception):
    def __init__(self, status, message, retry_after=None):
        self.status = status
        self.message = message
        self.retry_after = retry_after
        super().__init__(f'HTTP {status}: {message[:200]}')

    @property
    def transient(self):
        return self.status == 0 or self.status >= 500


def parse_retry_after(status, headers, body):
    if status != 429:
        return None
    try:
        if headers and headers.get('Retry-After'):
            return int(headers.get('Retry-After'))
    except (TypeError, ValueError):
        pass
    m = RETRY_AFTER.search(body or '')
    return int(m.group(1)) * 60 if m else 3605


class Client:
    def __init__(self, repo, min_interval=0.55, base=BASE, key=None):
        self.repo = Path(repo)
        self.base = base
        self.min_interval = min_interval
        self.last = 0.0
        self.calls = 0
        if key is None:
            sys.path.insert(0, str(self.repo / 'tools'))
            import download_team_games as download  # noqa: WPS433
            self._download = download
            key = download.load_api_key(self.repo / '.battlecode-api-key')
            self.opener = urllib.request.build_opener(download.NoRedirect())
        else:
            self._download = None
            self.opener = urllib.request.build_opener()
        if not key:
            raise RuntimeError('no API key available')
        self._key = key

    def _request(self, path, body=None, content_type='application/json', timeout=40):
        assert path.startswith('/api/v1/') and not path.startswith('//')
        headers = {'Authorization': 'Bearer ' + self._key, 'User-Agent': 'JKS-hub/2.0', 'Origin': self.base.rstrip('/')}
        data = None
        if body is not None:
            data = json.dumps(body).encode() if isinstance(body, dict) else body
            headers['Content-Type'] = content_type
        req = urllib.request.Request(self.base + path, data=data, headers=headers)
        time.sleep(max(0.0, self.min_interval - (time.monotonic() - self.last)))
        self.last = time.monotonic()
        self.calls += 1
        try:
            with self.opener.open(req, timeout=timeout) as response:
                raw = response.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            text = e.read(1500).decode(errors='replace')
            raise APIError(e.code, text, parse_retry_after(e.code, e.headers, text)) from None
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            raise APIError(0, 'transport: ' + type(e).__name__ + ': ' + str(e)) from None

    def get(self, path, attempts=3):
        for attempt in range(attempts):
            try:
                return self._request(path)
            except APIError as e:
                if e.transient and attempt < attempts - 1:
                    time.sleep(2 * 3 ** attempt)
                    continue
                raise

    def post(self, path, body, content_type='application/json'):
        """One attempt only: the caller records a durable intent before calling and reconciles afterwards."""
        return self._request(path, body if body is not None else b'', content_type)

    def download_replay(self, game_id, destination):
        if self._download is None:
            raise RuntimeError('replay download needs the repository helper')
        self._download.download_replay(int(game_id), Path(destination), self.base, self._key)
        return Path(destination)
