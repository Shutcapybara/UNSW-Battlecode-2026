"""Scheduling, outcome parsing, standings and resume tests for the tournament."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import sys
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('tournament', Path(__file__).resolve().parents[1] / 'tools/benchmarking/tournament.py')
tournament = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tournament)


class Tournament(unittest.TestCase):
    def test_focus_bot_plays_only_its_opponents_on_both_sides(self):
        matches = tournament.schedule(['a', 'b', 'c', 'd'], ['x', 'y'], 'b')
        expected = {(board, a, b) for board in ('x', 'y') for opponent in ('a', 'c', 'd')
                    for a, b in (('b', opponent), (opponent, 'b'))}
        self.assertEqual(set(matches), expected)
        self.assertEqual(len(matches), 12)

    def test_focus_bot_selection_and_resume(self):
        def result(executable, board, a, b, *args, sandbox=False):
            self.assertFalse(sandbox)
            return dict(map=board.stem, team_a=a.name, team_b=b.name,
                        outcome='draw', winner=None, rounds=500, error=None)
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()), \
                patch.object(tournament.shutil, 'which', return_value='/test/unswbc'), \
                patch.object(tournament, 'play', side_effect=result) as play:
            args = ['--bots', 'fry-v02-dragon-hunters', 'fry-v03-portal-hunters', 'fry-v04-escorts', '--maps', 'arena',
                    '--output', directory, '--focus-bot', 'fry-v03-portal-hunters']
            self.assertEqual(tournament.main(args), 0)
            self.assertEqual(play.call_count, 4)
            self.assertEqual(tournament.main(args + ['--resume']), 0)
            self.assertEqual(play.call_count, 4)
            with self.assertRaises(SystemExit) as changed:
                tournament.main(args + ['--resume', '--focus-bot', 'fry-v04-escorts'])
            self.assertEqual(changed.exception.code, 2)
            with self.assertRaises(SystemExit) as invalid:
                tournament.main(['--focus-bot', 'not-a-bot', '--dry-run'])
            self.assertEqual(invalid.exception.code, 2)

    def test_parallel_matches_overlap_and_save_every_result(self):
        barrier = threading.Barrier(2, timeout=5)
        lock = threading.Lock()
        active = 0
        peak = 0

        def result(executable, board, a, b, *args, sandbox=False):
            self.assertFalse(sandbox)
            nonlocal active, peak
            with lock:
                active += 1
                peak = max(peak, active)
            barrier.wait()
            with lock:
                active -= 1
            return dict(map=board.stem, team_a=a.name, team_b=b.name,
                        outcome='A', winner=a.name, rounds=10, error=None)

        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()), \
                patch.object(tournament.shutil, 'which', return_value='/test/unswbc'), \
                patch.object(tournament, 'play', side_effect=result) as play:
            args = ['--bots', 'fry-v02-dragon-hunters', 'fry-v03-portal-hunters', 'fry-v04-escorts', '--maps', 'arena',
                    '--output', directory, '--jobs', '2']
            self.assertEqual(tournament.main(args), 0)
            self.assertEqual(peak, 2)
            saved = json.loads((Path(directory) / 'results.json').read_text())
            self.assertEqual(len(saved), 6)
            self.assertEqual(len({(r['team_a'], r['team_b']) for r in saved}), 6)
            self.assertEqual(tournament.main(args + ['--resume', '--jobs', '1']), 0)
            self.assertEqual(play.call_count, 6)

    def test_worker_cancellation_stops_running_process_and_prevents_new_ones(self):
        with tempfile.TemporaryDirectory() as directory:
            workers = tournament.MatchWorkers(directory)
            with (Path(directory) / 'worker.log').open('w') as log:
                process = workers.start([sys.executable, '-c', 'import time; time.sleep(30)'], log)
                workers.cancel()
                self.assertIsNotNone(process.poll())
                with self.assertRaises(tournament.CancelledError):
                    workers.start([sys.executable, '-c', 'pass'], log)

    def test_workers_have_separate_builds_and_do_not_reuse_partial_builds(self):
        with tempfile.TemporaryDirectory() as directory:
            workers = tournament.MatchWorkers(Path(directory) / 'workers')
            source = Path(directory) / 'bot-a'
            source.mkdir()
            (source / 'bot.toml').write_text('[project]\n')
            barrier = threading.Barrier(2, timeout=5)

            def prepare():
                target = workers.bot_path(source)
                built = target / '.unswbc-build'
                built.mkdir()
                (built / 'bot').touch()
                self.assertEqual(workers.bot_path(source), target)
                workers.mark_built(source)
                self.assertEqual(workers.bot_path(source), built)
                barrier.wait()
                return target

            with tournament.ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(prepare) for _ in range(2)]
                self.assertNotEqual(futures[0].result(), futures[1].result())

    def test_every_pair_both_sides_on_every_map(self):
        matches = tournament.schedule(['c', 'a', 'b'], ['z', 'x'])
        self.assertEqual(len(matches), 12)
        self.assertEqual(len(set(matches)), 12)
        for board, a, b in matches:
            self.assertNotEqual(a, b)
            self.assertIn((board, b, a), matches)

    def test_outcomes_and_errors(self):
        self.assertEqual(tournament.parse_result('\x1b[32mteam B wins after 27 rounds (by elimination)\x1b[0m\n', 0), ('B', 27))
        self.assertEqual(tournament.parse_result('draw after 500 rounds (equal length)\n', 0), ('draw', 500))
        self.assertEqual(tournament.parse_result('failed to draw replay\n', 0), ('error', None))
        self.assertEqual(tournament.parse_result('team A wins after 27 rounds\n', 1), ('error', None))

    def test_errors_do_not_count_as_losses(self):
        results = [dict(team_a='a', team_b='b', outcome=x) for x in ['A', 'draw', 'error']]
        with tempfile.TemporaryDirectory() as directory:
            ranked = tournament.save_results(Path(directory), results, ['a', 'b'])
            self.assertEqual(ranked[0]['points'], 4)
            self.assertEqual(ranked[0]['played'], 2)
            self.assertEqual(ranked[1]['losses'], 1)
            self.assertEqual(ranked[1]['errors'], 1)
            self.assertTrue((Path(directory) / 'standings.csv').exists())

    def test_resume_skips_successes_and_retries_errors(self):
        def result(executable, board, a, b, *args, sandbox=False):
            self.assertFalse(sandbox)
            return dict(map=board.stem, team_a=a.name, team_b=b.name,
                        outcome='A', winner=a.name, rounds=10, error=None)
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()), \
                patch.object(tournament.shutil, 'which', return_value='/test/unswbc'), \
                patch.object(tournament, 'play', side_effect=result) as play:
            args = ['--bots', 'fry-v02-dragon-hunters', 'fry-v03-portal-hunters', '--maps', 'arena', '--output', directory]
            self.assertEqual(tournament.main(args), 0)
            self.assertEqual(play.call_count, 2)
            self.assertEqual(tournament.main(args + ['--resume']), 0)
            self.assertEqual(play.call_count, 2)
            path = Path(directory) / 'results.json'
            results = json.loads(path.read_text())
            results[0]['outcome'] = 'error'
            path.write_text(json.dumps(results))
            self.assertEqual(tournament.main(args + ['--resume']), 0)
            self.assertEqual(play.call_count, 3)

    def test_timeout_is_saved_as_error_and_worker_is_stopped(self):
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(tournament.subprocess, 'Popen') as popen, \
                patch.object(tournament, 'stop_process') as stop:
            popen.return_value.wait.side_effect = subprocess.TimeoutExpired('unswbc', 1)
            result = tournament.play('unswbc', Path('arena.map'), Path('a'), Path('b'),
                                     Path(directory), 'match', 1, False)
            self.assertEqual(result['outcome'], 'error')
            self.assertIn('timed out', result['error'])
            stop.assert_called_once_with(popen.return_value)


if __name__ == '__main__':
    unittest.main()
