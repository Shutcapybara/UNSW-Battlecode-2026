from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]

class Charybdis(unittest.TestCase):
    def test_local_game_rules_and_reply_search(self):
        with tempfile.TemporaryDirectory(prefix='charybdis-tests-') as directory:
            executable = str(Path(directory) / 'checks')
            subprocess.run(['clang++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic',
                            str(ROOT/'tools/leviathan/test_charybdis.cpp'), '-o', executable],
                           check=True, capture_output=True, text=True)
            result = subprocess.run([executable], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

if __name__ == '__main__':
    unittest.main()
