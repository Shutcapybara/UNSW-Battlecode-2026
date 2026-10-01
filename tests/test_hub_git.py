"""Git keeper policy tests on a scratch repository with a bare origin."""
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools.hub import gitkeeper  # noqa: E402
from tools.hub.config import DEFAULTS  # noqa: E402


def run(*args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True)


@unittest.skipUnless(shutil.which('git'), 'git not installed')
class GitKeeperTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.origin = self.tmp / 'origin.git'
        run('git', 'init', '--bare', '-q', str(self.origin), cwd=self.tmp)
        self.repo = self.tmp / 'repo'
        run('git', 'clone', '-q', str(self.origin), str(self.repo), cwd=self.tmp)
        run('git', 'config', 'user.email', 't@e', cwd=self.repo)
        run('git', 'config', 'user.name', 'T', cwd=self.repo)
        run('git', 'checkout', '-q', '-b', 'main', cwd=self.repo)
        (self.repo / 'README.md').write_text('# r\n')
        run('git', 'add', 'README.md', cwd=self.repo)
        run('git', 'commit', '-q', '-m', 'init', cwd=self.repo)
        run('git', 'push', '-q', '-u', 'origin', 'main', cwd=self.repo)
        self.root = self.tmp / 'hub'
        self.policy = dict(DEFAULTS['git'])
        self.policy['quiet_minutes'] = 1

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def old(self, path):
        t = time.time() - 600
        os.utime(path, (t, t))

    def test_policy(self):
        bot = self.repo / 'bots' / 'x-s01'
        bot.mkdir(parents=True)
        (bot / 'bot.toml').write_text('[project]\nlanguage = "py"\n')
        (bot / 'main.py').write_text('print(1)\n')
        fresh = self.repo / 'bots' / 'y-s01'
        fresh.mkdir()
        (fresh / 'bot.toml').write_text('[project]\n')
        (fresh / 'main.py').write_text('print(2)\n')
        broken = self.repo / 'bots' / 'z-s01'
        broken.mkdir()
        (broken / 'bot.toml').write_text('[project]\n')
        (broken / 'main.py').write_text('def (:\n')
        (self.repo / 'experiment_data').mkdir()
        (self.repo / 'experiment_data' / 'big.json').write_text('{}')
        (self.repo / '.battlecode-api-key').write_text('bc_secret')
        (self.repo / 'notes.txt').write_text('x')
        for p in (bot / 'bot.toml', bot / 'main.py', broken / 'bot.toml', broken / 'main.py', self.repo / 'experiment_data' / 'big.json', self.repo / '.battlecode-api-key', self.repo / 'notes.txt'):
            self.old(p)
        plan = gitkeeper.classify(self.repo, self.policy)
        self.assertEqual(plan['commit'], ['bots/x-s01'])
        reasons = dict(plan['skipped'])
        self.assertIn('settling', reasons['bots/y-s01'])
        self.assertIn('parse', reasons['bots/z-s01'])
        self.assertEqual(reasons['.battlecode-api-key'], 'never list')
        self.assertEqual(reasons['experiment_data/big.json'], 'never list')
        self.assertEqual(reasons['notes.txt'], 'outside include list')
        report = gitkeeper.sync(self.repo, self.root, self.policy, dry_run=False)
        self.assertEqual(report['committed'], ['bots/x-s01'])
        self.assertTrue(report['pushed'])
        log = run('git', 'log', '--format=%s', 'origin/main', cwd=self.repo).stdout
        self.assertIn('[hub-git] 1 bot snapshot', log)
        status = run('git', '--no-optional-locks', 'status', '--porcelain', cwd=self.repo).stdout
        self.assertNotIn('bots/x-s01', status)
        self.assertIn('.battlecode-api-key', status)

    def test_stale_index_lock(self):
        lock = self.repo / '.git' / 'index.lock'
        lock.write_text('')
        report = gitkeeper.sync(self.repo, self.root, self.policy, dry_run=True)
        self.assertTrue(any('index.lock present' in a for a in report['attention']))
        self.assertTrue(lock.exists())  # fresh lock: a git command may hold it
        t = time.time() - gitkeeper.STALE_LOCK_SECONDS - 60
        os.utime(lock, (t, t))
        report = gitkeeper.sync(self.repo, self.root, self.policy, dry_run=True)
        self.assertTrue(any('stale .git/index.lock removed' in a for a in report['attention']))
        self.assertFalse(lock.exists())
        self.assertFalse(any('index.lock present' in a for a in report['attention']))

    def test_merge_and_conflict(self):
        other = self.tmp / 'other'
        run('git', 'clone', '-q', str(self.origin), str(other), cwd=self.tmp)
        run('git', 'config', 'user.email', 'o@e', cwd=other)
        run('git', 'config', 'user.name', 'O', cwd=other)
        run('git', 'checkout', '-q', 'main', cwd=other)
        (other / 'docs').mkdir()
        (other / 'docs' / 'a.md').write_text('a\n')
        run('git', 'add', 'docs/a.md', cwd=other)
        run('git', 'commit', '-q', '-m', 'other work', cwd=other)
        run('git', 'push', '-q', 'origin', 'main', cwd=other)
        report = gitkeeper.sync(self.repo, self.root, self.policy)
        self.assertTrue(report['merged'])
        self.assertTrue((self.repo / 'docs' / 'a.md').exists())
        # conflict: both sides edit README
        run('git', 'pull', '-q', 'origin', 'main', cwd=other)
        (other / 'README.md').write_text('# theirs\n')
        run('git', 'commit', '-q', '-am', 'theirs', cwd=other)
        run('git', 'push', '-q', 'origin', 'main', cwd=other)
        (self.repo / 'README.md').write_text('# ours\n')
        self.old(self.repo / 'README.md')
        report = gitkeeper.sync(self.repo, self.root, self.policy)
        self.assertEqual(report['committed'], ['README.md'])
        self.assertFalse(report['merged'])
        self.assertTrue(any('conflict' in a for a in report['attention']))
        self.assertFalse((self.repo / '.git' / 'MERGE_HEAD').exists())
        self.assertIsNone(report['pushed'])


if __name__ == '__main__':
    unittest.main()
