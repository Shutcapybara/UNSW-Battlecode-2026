import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.hub.api import BASE, load_hub_api_key


class HubApiKeyTests(unittest.TestCase):
    def test_unswbc_auth_store_is_preferred_to_stale_plaintext_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            repo = home / "repo"
            repo.mkdir()
            (repo / ".battlecode-api-key").write_text("stale-key")
            store = home / ".unswbc"
            store.mkdir()
            (store / "keys.json").write_text(json.dumps({BASE: "fresh-key"}))

            class Download:
                @staticmethod
                def load_api_key(path):
                    return path.read_text()

            with patch.object(Path, "home", return_value=home), patch.dict(os.environ, {}, clear=True):
                self.assertEqual(load_hub_api_key(repo, BASE, Download), "fresh-key")

    def test_environment_override_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            class Download:
                @staticmethod
                def load_api_key(path):
                    return "file-key"

            with patch.dict(os.environ, {"BATTLECODE_API_KEY": "environment-key"}, clear=True):
                self.assertEqual(load_hub_api_key(Path(tmp), BASE, Download), "environment-key")


if __name__ == "__main__":
    unittest.main()
