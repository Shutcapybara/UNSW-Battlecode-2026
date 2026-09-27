"""Build and exercise the independent C++ family's rule-level checks."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from lab import apply_overrides
ROOT = Path(__file__).resolve().parents[2]


class Riptide(unittest.TestCase):
    def test_cpp_rule_invariants(self):
        with tempfile.TemporaryDirectory(prefix='riptide-tests-') as directory:
            executable = str(Path(directory) / 'checks')
            subprocess.run(['clang++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic',
                            str(ROOT / 'tools/leviathan/test_riptide.cpp'), '-o', executable],
                           check=True, capture_output=True, text=True)
            result = subprocess.run([executable], check=True, capture_output=True, text=True)
            self.assertIn('checks passed', result.stdout)
            subprocess.run(['clang++', '-std=c++17', '-O2', '-DRIPTIDE_VIABILITY',
                            str(ROOT / 'tools/leviathan/test_riptide.cpp'), '-o', executable],
                           check=True, capture_output=True, text=True)
            subprocess.run([executable], check=True, capture_output=True, text=True)

    def test_cpp_snapshot_overrides(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / 'main.cpp').write_text('int main() {}\n')
            (folder / 'params.h').write_text('constexpr auto horizon = 6; // turns\nconstexpr auto radio = true;\n')
            apply_overrides(folder, {'horizon': 1, 'radio': False})
            self.assertIn('horizon = 1;', (folder / 'params.h').read_text())
            self.assertIn('radio = false;', (folder / 'params.h').read_text())
            with self.assertRaises(ValueError):
                apply_overrides(folder, {'missing': 1})
            with self.assertRaises(ValueError):
                apply_overrides(folder, {'horizon': 'code'})
            with self.assertRaises(ValueError):
                apply_overrides(folder, {'horizon': float('inf')})


if __name__ == '__main__':
    unittest.main()
