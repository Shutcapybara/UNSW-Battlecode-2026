#!/usr/bin/env python3
"""Asahi (Phase 3 Evaluator) native job daemon.

The Asahi coordinator runs in a Cowork VM that cannot run the engine. It writes job files into
<tree>/build/asahi/queue/; this daemon, started once by the user in a Mac terminal, runs them natively.

Only these job kinds exist (anything else is rejected, never executed):
  script   {"script": "tools/asahi/<name>.py", "argv": [str, ...], "heavy": bool, "timeout": seconds}
           runs <venv python> <tree>/<script> argv... with cwd=<tree>; the script must live in tools/asahi/.
  commit   {"paths": [...], "message": str}  git add + commit in <tree>, on branch r/asahi only; paths must be
           under tools/asahi/, bots/asahi-*, maps/m2tr/, claude/asahi-status.md, docs/learning/ or docs/hub/BOARD.md.
  merge_main {}                              git merge --no-edit main into r/asahi (aborts on conflict).
  reload   {}                                re-exec this daemon from <tree>/tools/asahi/jobd.py.

Learn queue (D-050 §8, D-052 §F): when Asahi's own queue is empty, the daemon also takes jobs from
<main>/build/learn/queue/*.json (main checkout), lowest name first, results in build/learn/{running,done,logs}/:
  script     {"script": "tools/learn/<name>.py" | "tools/hinata/<name>.py", "argv": [str, ...], "heavy": bool,
              "timeout": seconds, "by": "<lane>", "env": "learn" | "main"}   cwd = main checkout;
              env "learn" (default) = build/learn/venv (unswbc 1.2.9 + the learning stack), "main" = the repo's .venv.
  setup_env  {"by": "<lane>"}   (re)creates build/learn/venv and installs LEARN_PACKAGES.
Order of priority is the macro's: Evaluator panels (this daemon's own queue) before learn jobs; one job at a time.

Heavy jobs take build/learn/HEAVY.lock in the MAIN checkout (macro section 8): they wait while another owner holds
it; a lock whose pid is dead on this host and older than 10 minutes is treated as stale (logged). Everything runs
at nice 10 (inherited). Results: queue/<id>.json moves to done/<id>.json with rc, times and the log path
(logs/<id>.log). A heartbeat is written every loop to build/asahi/jobd.heartbeat.

    cd ~/Documents/Projects/wt-asahi
    caffeinate -is ../UNSW-Battlecode-2026/.venv/bin/python tools/asahi/jobd.py --main ../UNSW-Battlecode-2026
"""
from __future__ import annotations

import argparse, json, os, re, signal, socket, subprocess, sys, time
from pathlib import Path

KINDS = {'script', 'commit', 'merge_main', 'reload'}
LEARN_KINDS = {'script', 'setup_env'}
LEARN_SCRIPT = re.compile(r'^tools/(learn|hinata)/[A-Za-z0-9_]+\.py$')
LEARN_PACKAGES = ['unswbc==1.2.9', 'pycapnp', 'lightgbm', 'xgboost', 'torch', 'scikit-learn', 'pandas', 'pyarrow',
                  'duckdb', 'numpy']
COMMIT_OK = re.compile(r'^(tools/asahi/|bots/asahi-[A-Za-z0-9._-]+/|bots/(bokuto-[0-9]+-[A-Za-z0-9-]+|kenma-03-pocket-queen|kenma-21-proven-reserve|kenma-28-harvest-reserve)/|maps/m2tr/|claude/asahi-status\.md$|docs/learning/|docs/hub/BOARD\.md$)')
# D-077 §C / D-079: Asahi commits its byte copies of free-lane bots (with .asahi-source.json) so they are in git.
OWNER = 'asahi'


def learn_dyld_env(venv):
    """LightGBM's macOS wheel links @rpath/libomp.dylib and looks only in Homebrew/MacPorts paths (no libomp on this Mac:
    every learn job failed at import, 5 Oct 04:37Z). torch's wheel ships an LLVM libomp; put its directory on
    DYLD_LIBRARY_PATH for learn jobs so lightgbm and torch share that one copy. venv python is uv's (not SIP-protected)."""
    libs = sorted(Path(venv).glob('lib/python3*/site-packages/torch/lib/libomp.dylib'))
    return {'DYLD_LIBRARY_PATH': str(libs[0].parent)} if libs else {}


def now():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError, TypeError):
        return False


class Daemon:
    def __init__(self, tree: Path, main: Path, python: str, max_workers: int):
        self.tree, self.main, self.python, self.max_workers = tree, main, python, max_workers
        self.base = tree / 'build/asahi'
        for d in ('queue', 'done', 'logs', 'running'):
            (self.base / d).mkdir(parents=True, exist_ok=True)
        self.lock = main / 'build/learn/HEAVY.lock'
        self.log = open(self.base / 'jobd.log', 'a', buffering=1)

    def say(self, *a):
        try:
            print(now(), *a, file=self.log)
        except OSError:
            pass
        print(now(), *a, flush=True)

    def wait_disk(self, job_id, min_gb=20):
        import shutil
        warned = False
        while shutil.disk_usage(self.tree).free < min_gb * 2 ** 30:
            if not warned:
                self.say(f'{job_id}: waiting, less than {min_gb} GB free on the disk')
                warned = True
            self.heartbeat(f'waiting disk for {job_id}')
            time.sleep(60)

    def heartbeat(self, state):
        try:
            self._heartbeat(state)
        except OSError as e:  # a full disk must not kill the daemon (4 Oct 18:48Z)
            print(now(), 'heartbeat failed:', e, flush=True)

    def _heartbeat(self, state):
        (self.base / 'jobd.heartbeat').write_text(json.dumps(dict(at=now(), pid=os.getpid(), host=socket.gethostname(),
                                                                  state=state, python=self.python)))

    # ---- heavy lock -------------------------------------------------------------------------------------------
    def take_lock(self, job_id):
        self.lock.parent.mkdir(parents=True, exist_ok=True)
        waited = False
        while True:
            if self.lock.exists():
                try:
                    cur = json.loads(self.lock.read_text())
                except Exception:
                    cur = {}
                age = time.time() - self.lock.stat().st_mtime
                stale = cur.get('host') == socket.gethostname() and not pid_alive(cur.get('pid')) and age > 600
                if not stale:
                    if not waited:
                        self.say(f'{job_id}: waiting for HEAVY.lock held by {cur.get("owner")}/{cur.get("job")}')
                        waited = True
                    self.heartbeat(f'waiting lock for {job_id}')
                    time.sleep(30)
                    continue
                self.say(f'{job_id}: stale HEAVY.lock {cur} (pid dead, {age:.0f}s old) taken over')
                try:  # move the stale lock aside, else the atomic link below fails forever (4 Oct 19:16Z)
                    self.lock.rename(self.lock.with_name(f'HEAVY.lock.stale-{cur.get("pid")}-{int(time.time())}'))
                except OSError:
                    time.sleep(5)
            body = dict(owner=OWNER, job=job_id, pid=os.getpid(), host=socket.gethostname(), started=now(),
                        workers=self.max_workers)
            tmp = self.lock.with_suffix('.tmp-asahi')
            tmp.write_text(json.dumps(body))
            try:
                os.link(tmp, self.lock)  # atomic: fails if someone created it meanwhile
            except FileExistsError:
                tmp.unlink(missing_ok=True)
                continue
            tmp.unlink(missing_ok=True)
            return

    def drop_lock(self):
        try:
            if json.loads(self.lock.read_text()).get('owner') == OWNER:
                self.lock.unlink()
        except Exception:
            pass

    # ---- jobs -------------------------------------------------------------------------------------------------
    def git(self, *args, check=True):
        return subprocess.run(['git', '-C', str(self.tree), *args], capture_output=True, text=True, check=check)

    def run_job(self, job, logf):
        kind = job.get('kind')
        if kind not in KINDS:
            raise ValueError(f'kind {kind!r} not allowed')
        if kind == 'script':
            script = str(job.get('script', ''))
            if not re.match(r'^tools/asahi/[A-Za-z0-9_]+\.py$', script) or not (self.tree / script).is_file():
                raise ValueError(f'script {script!r} not allowed')
            argv = [str(x) for x in job.get('argv', [])]
            env = dict(os.environ, ASAHI_MAX_WORKERS=str(self.max_workers), ASAHI_MAIN=str(self.main),
                       PYTHONUNBUFFERED='1', UNSWBC=str(Path(self.python).parent / 'unswbc'))
            return self.run_process(job, [self.python, script, *argv], self.tree, env, logf, self.base / 'queue')
        if kind == 'commit':
            if self.git('rev-parse', '--abbrev-ref', 'HEAD').stdout.strip() != 'r/asahi':
                raise ValueError('tree is not on r/asahi')
            paths = [str(x) for x in job.get('paths', [])]
            bad = [x for x in paths if not COMMIT_OK.match(x) or '..' in x]
            if bad or not paths:
                raise ValueError(f'paths not allowed: {bad}')
            msg = str(job.get('message', '')).strip()
            if not msg:
                raise ValueError('empty message')
            r1 = self.git('add', '--', *paths, check=False)
            numstat = self.git('diff', '--cached', '--numstat').stdout.splitlines()
            for path in self.git('diff', '--cached', '--name-only').stdout.split():
                f = self.tree / path
                big = f.exists() and not f.is_symlink() and f.lstat().st_size > 4 * 1024 * 1024
                if big:  # allowed only as a blob identical to one already in the repository (common rules)
                    sha = self.git('hash-object', '--', path).stdout.strip()
                    big = self.git('cat-file', '-e', sha, check=False).returncode != 0 or \
                        not self.git('log', '--all', '--find-object=' + sha, '-1', '--format=%h', 'main', check=False).stdout.strip()
                if big or path.endswith(('.replay',)) or path.startswith(('build/', 'hub-state/', 'public_replays/')):
                    self.git('reset', '-q', '--', path, check=False)
                    logf.write(f'unstaged forbidden file {path}\n')
            r2 = self.git('commit', '-m', msg, check=False)
            logf.write(r1.stdout + r1.stderr + r2.stdout + r2.stderr + '\n'.join(numstat) + '\n')
            return r2.returncode
        if kind == 'merge_main':
            r = self.git('merge', '--no-edit', 'main', check=False)
            logf.write(r.stdout + r.stderr)
            if r.returncode:
                self.git('merge', '--abort', check=False)
            return r.returncode
        return 0  # reload handled by the caller

    def run_process(self, job, cmd, cwd, env, logf, cancel_dir):
        heavy = bool(job.get('heavy'))
        if heavy:
            self.wait_disk(job['id'])
            self.take_lock(job['id'])
        try:
            p = subprocess.Popen(cmd, cwd=cwd, stdout=logf, stderr=subprocess.STDOUT, env=env, start_new_session=True)
            deadline = time.time() + float(job.get('timeout', 6 * 3600))
            while p.poll() is None:
                self.heartbeat(f'running {job["id"]} pid {p.pid}')
                if (cancel_dir / f'cancel-{job["id"]}').exists() or time.time() > deadline:
                    os.killpg(p.pid, signal.SIGTERM)
                    time.sleep(10)
                    if p.poll() is None:
                        os.killpg(p.pid, signal.SIGKILL)
                    (cancel_dir / f'cancel-{job["id"]}').unlink(missing_ok=True)
                    return -15
                time.sleep(15)
            return p.returncode
        finally:
            if heavy:
                self.drop_lock()

    def run_learn_job(self, job, logf):
        kind = job.get('kind')
        if kind not in LEARN_KINDS:
            raise ValueError(f'learn kind {kind!r} not allowed')
        lb = self.main / 'build/learn'
        venv = lb / 'venv'
        if kind == 'setup_env':
            r = subprocess.run([self.python, '-m', 'venv', '--clear', str(venv)], capture_output=True, text=True)
            logf.write(r.stdout + r.stderr)
            if r.returncode:
                return r.returncode
            pip = [str(venv / 'bin/python'), '-m', 'pip', 'install', '--upgrade']
            for pkgs in (['pip'], LEARN_PACKAGES):
                r = subprocess.run(pip + pkgs, stdout=logf, stderr=subprocess.STDOUT)
                if r.returncode:
                    return r.returncode
            r = subprocess.run([str(venv / 'bin/python'), '-m', 'pip', 'freeze'], capture_output=True, text=True)
            (lb / 'venv.freeze.txt').write_text(r.stdout)
            logf.write(r.stdout)
            return 0
        script = str(job.get('script', ''))
        if not LEARN_SCRIPT.match(script) or not (self.main / script).is_file():
            raise ValueError(f'learn script {script!r} not allowed (tools/learn/*.py or tools/hinata/*.py in main)')
        envname = job.get('env', 'learn')
        py = str(venv / 'bin/python') if envname == 'learn' else self.python
        if not Path(py).exists():
            raise ValueError(f'environment {envname!r} missing ({py}); queue a setup_env job')
        argv = [str(x) for x in job.get('argv', [])]
        env = dict(os.environ, ASAHI_MAX_WORKERS=str(self.max_workers), PYTHONUNBUFFERED='1',
                   UNSWBC=str(Path(py).parent / 'unswbc'), OMP_NUM_THREADS=str(self.max_workers),
                   PYTHONDONTWRITEBYTECODE='1')    # no __pycache__ in the main checkout (keeper blocker, 4 Oct 23:48Z)
        env.update(learn_dyld_env(venv) if envname == 'learn' else {})
        return self.run_process(job, [py, script, *argv], self.main, env, logf, lb / 'queue')

    def next_job(self):
        own = sorted((self.base / 'queue').glob('*.json'))
        if own:
            return own[0], self.base, 'asahi'
        lb = self.main / 'build/learn'
        for d in ('queue', 'running', 'done', 'logs'):
            (lb / d).mkdir(parents=True, exist_ok=True)
        learn = sorted((lb / 'queue').glob('*.json'))
        if learn:
            return learn[0], lb, 'learn'
        return None, None, None

    def loop(self):
        try:
            os.nice(10)
        except OSError as e:
            self.say('nice failed:', e)
        self.say(f'jobd up: tree={self.tree} main={self.main} python={self.python} workers<={self.max_workers}')
        while True:
          try:
            self.step()
          except Exception as e:  # keep serving; the failing job is already recorded where possible
            self.say('loop error:', type(e).__name__, e)
            time.sleep(60)

    def step(self):
        if True:
            self.heartbeat('idle')
            path, base, which = self.next_job()
            if path is None:
                time.sleep(20)
                return
            try:
                job = json.loads(path.read_text())
                job['id'] = job.get('id') or path.stem
            except Exception as e:
                self.say(f'bad job file {path.name}: {e}')
                path.rename(base / 'done' / (path.stem + '.bad'))
                return
            run_path = base / 'running' / path.name
            path.rename(run_path)
            logp = base / 'logs' / f'{job["id"]}.log'
            t0 = now()
            self.say(f'start [{which}] {job["id"]} {job.get("kind")} {job.get("script", "")} by={job.get("by", "asahi")}')
            rc, err = None, None
            with open(logp, 'a', buffering=1) as logf:
                try:
                    rc = self.run_job(job, logf) if which == 'asahi' else self.run_learn_job(job, logf)
                except Exception as e:
                    err = f'{type(e).__name__}: {e}'
                    logf.write(err + '\n')
            res = dict(job, started=t0, ended=now(), rc=rc, error=err, log=str(logp))
            (base / 'done' / path.name).write_text(json.dumps(res, indent=1))
            run_path.unlink(missing_ok=True)
            self.say(f'end {job["id"]} rc={rc} err={err}')
            if which == 'asahi' and job.get('kind') == 'reload' and err is None:
                new = self.tree / 'tools/asahi/jobd.py'
                self.say('reloading from', new)
                os.execv(self.python, [self.python, str(new), '--main', str(self.main), '--tree', str(self.tree),
                                       '--workers', str(self.max_workers)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--main', required=True, help='main checkout (holds build/learn/HEAVY.lock and .venv)')
    ap.add_argument('--tree', default='.', help='the r/asahi worktree')
    ap.add_argument('--workers', type=int, default=14)
    a = ap.parse_args()
    main_ = Path(a.main).resolve()
    py = str(main_ / '.venv/bin/python')
    if not Path(py).exists():
        sys.exit(f'no venv python at {py}')
    Daemon(Path(a.tree).resolve(), main_, py, min(a.workers, 14)).loop()


if __name__ == '__main__':
    main()
