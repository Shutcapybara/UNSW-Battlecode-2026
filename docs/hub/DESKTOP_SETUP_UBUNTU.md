# Ubuntu desktop setup — Claude Desktop, the repo, the hub, and the training stack (director, 29 Sep 2026)

Target machine: Ubuntu 22.04+ (24.04 assumed below), x86_64, RTX 4090, 64 GB. Everything lives under one
directory, `$ROOT`. Pick it once and keep the same layout the Mac uses so paths in findings stay meaningful:

```bash
export ROOT="$HOME/Projects"          # change once here; every path below derives from it
mkdir -p "$ROOT"
# layout:   $ROOT/UNSW-Battlecode-2026   the repo (REPO)
#           $ROOT/battlecode-hub         the hub root (HUB): hub.sqlite, hub.toml, candidates/, app/
#           $ROOT/wt-*                   git worktrees for the R lanes (../wt-r1 etc., as the prompts say)
```

Put `export ROOT=...` and the `JKS_HUB_ROOT` line from §5 in `~/.bashrc` so terminals, Claude Code and systemd
agree on the paths.

## 1. Claude Desktop (Linux beta) and Cowork

Official apt package; Cowork on Linux runs its VM through QEMU/KVM, so the machine needs virtualization on in
the firmware and your user in the `kvm` group.

```bash
sudo apt install -y curl gnupg
sudo curl -fsSLo /usr/share/keyrings/claude-desktop-archive-keyring.asc https://downloads.claude.ai/claude-desktop/key.asc
gpg --show-keys /usr/share/keyrings/claude-desktop-archive-keyring.asc   # expect 31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE
echo "deb [arch=amd64,arm64 signed-by=/usr/share/keyrings/claude-desktop-archive-keyring.asc] https://downloads.claude.ai/claude-desktop/apt/stable stable main" | sudo tee /etc/apt/sources.list.d/claude-desktop.list
sudo apt update && sudo apt install -y claude-desktop        # pulls qemu-system-x86, ovmf, virtiofsd as recommends
sudo usermod -aG kvm "$USER"                                  # then log out and back in
egrep -c '(vmx|svm)' /proc/cpuinfo                            # >0 = virtualization exposed; if 0, enable SVM/VT-x in firmware
ls -l /dev/kvm /dev/vhost-vsock                               # both must exist; if vhost-vsock is missing:
#   sudo modprobe vhost_vsock && echo vhost_vsock | sudo tee /etc/modules-load.d/vhost_vsock.conf
```

Launch `claude-desktop`, sign in with the claude.ai account (not an API key), open the Cowork tab: it should not
show a "requires QEMU / KVM / vhost_vsock" banner. Then **Add folder** → `$ROOT/UNSW-Battlecode-2026` so sessions
can link to this computer, exactly as on the Mac. Updates come through `apt upgrade`; the app does not self-update
on Linux. Not in the Linux beta: Computer Use (screen control) and dictation; nothing in this programme uses either.

Claude Code in the terminal (the R lanes run as well or better here than in Cowork, and it works on any distro):

```bash
sudo apt install -y nodejs npm            # or the NodeSource 22.x setup script if Ubuntu's node is < 18
sudo npm install -g @anthropic-ai/claude-code
claude --version && claude               # sign in once in the browser flow
```

## 2. System packages

```bash
sudo apt install -y git git-lfs build-essential g++ clang cmake ninja-build pkg-config \
    python3 python3-venv python3-dev python3-pip pipx rsync htop tmux jq sqlite3 \
    libcapnp-dev capnproto            # pycapnp builds against these
g++ --version    # need C++20: g++ >= 11 (Ubuntu 22.04 ships 11, 24.04 ships 13) — Ares builds with -std=c++20 -O2
nproc; free -g   # note the core count: game generation is CPU-bound and this number sets --jobs everywhere
```

## 3. The repository

```bash
cd "$ROOT"
git clone git@github.com:<org>/UNSW-Battlecode-2026.git      # or the https remote you use on the Mac
cd UNSW-Battlecode-2026
git config user.name "..." && git config user.email "..."
python3 -m venv .venv && . .venv/bin/activate
pip install -U pip wheel
pip install 'unswbc==1.2.2'                                    # the judge's toolkit version the harness is pinned to
pip install -r tools/requirements-benchmark.txt -r tools/requirements-rl.txt   # numpy/scipy/pandas/sklearn/pycapnp
pip install pyarrow lightgbm matplotlib                          # parquet (fights.parquet, F1 tables), GBTs, plots
unswbc --version
```

The API credential: copy it from the Mac over ssh, never through git, chat or a screenshot:

```bash
scp alik@<mac>:/Users/alik/Documents/Projects/UNSW-Battlecode-2026/.battlecode-api-key "$ROOT/UNSW-Battlecode-2026/.battlecode-api-key"
chmod 600 "$ROOT/UNSW-Battlecode-2026/.battlecode-api-key"
git check-ignore .battlecode-api-key      # must print the path (it is in .gitignore); if not, stop and fix that first
```

Smoke test — one Python game, one C++ game (native), one sandbox-priced game, the hub gate tests:

```bash
unswbc run maps/schooltime.map bots/yuna-v05-core bots/fenrir-v18-arrival-ready-beds
unswbc run maps/schooltime.map bots/ares-v06-expanded-search-support bots/yuna-v05-core
python3 tools/cx/arena.py --sandbox maps/portals.map bots/ares-v06-expanded-search-support bots/yuna-v05-core   # judge pricing; must report points/turn
JKS_HUB_FIXTURE="$PWD/build/hub-fixture" python3 -m unittest tests.test_hub_core tests.test_hub_git tests.test_hub_legacy_ops tests.test_hub_executor tests.test_hub_daemon tests.test_hub_quota_filler tests.test_hub_discord_bot tests.test_hub_api
```

If `--sandbox` fails on a missing wasm toolchain, follow the message; unswbc 1.2.2 fetches its own sandbox
runtime on first use and caches wasm by `.c/.cpp` hash (`arena.py` purges that cache per game so header edits count).

Worktrees for the lanes, as the R prompts assume (`../wt-<lane>` beside the repo, branch `r/<lane>`):

```bash
cd "$ROOT/UNSW-Battlecode-2026"
for lane in r1 ra rg r3 r4 r5; do git worktree add "../wt-$lane" -b "r/$lane" 2>/dev/null || git worktree add "../wt-$lane" "r/$lane"; done
```

## 4. Bring the data over from the Mac (once, before the Mac is retired)

```bash
M=alik@<mac>; MREPO=/Users/alik/Documents/Projects/UNSW-Battlecode-2026
rsync -a --info=progress2 "$M:$MREPO/public_replays/" "$ROOT/UNSW-Battlecode-2026/public_replays/"   # ~32 GB corpus (28k+ replays); gitignored
rsync -a "$M:$MREPO/build/zoo/" "$ROOT/UNSW-Battlecode-2026/build/zoo/"     # optional: past panel replays (scorecards reuse them by fingerprint)
rsync -a "$M:$MREPO/build/cx/"  "$ROOT/UNSW-Battlecode-2026/build/cx/"      # optional: golden transcripts and CPU probes
rsync -a "$M:$MREPO/build/c2-0/" "$ROOT/UNSW-Battlecode-2026/build/c2-0/"   # fights.parquet (182k contact events)
rsync -a "$M:$MREPO/hub-state/" "$ROOT/UNSW-Battlecode-2026/hub-state/"     # the mirror (small; control/, review/, decisions.jsonl)
rsync -a "$M:/Users/alik/Documents/Projects/battlecode-hub/" "$ROOT/battlecode-hub/"   # HUB root: hub.sqlite (the record), hub.toml, candidates/*.zip, app/
```

`hub.sqlite` is the only copy of the experiment/candidate/decision record; copy it with the Mac daemon **stopped**
(§5) so WAL is flushed, then check `sqlite3 "$ROOT/battlecode-hub/hub.sqlite" 'pragma integrity_check;'`.

## 5. The hub on Linux (one live executor, ever)

The daemon is Mac-first (LaunchAgent, `/Users/alik/...` defaults) but the code runs on Linux: `hub_root()` honours
`JKS_HUB_ROOT`, non-Darwin hosts get repo-relative defaults, and Rory's `tools/hub/jks-hub-actuator.service.example`
is a systemd user unit. Rules that do not change: exactly one daemon holds the executor lease; the executor stays in
`shadow` (D-031) until the lead flips it; the key never leaves the two files above.

```bash
# on the Mac, first: stop and disable the LaunchAgent so two daemons never race for the API and the lease
#   launchctl unload ~/Library/LaunchAgents/<the jks hub plist>   (see tools/hub/bootstrap_mac.sh for the label)
# on the desktop:
echo "export JKS_HUB_ROOT=\"$ROOT/battlecode-hub\"" >> ~/.bashrc && export JKS_HUB_ROOT="$ROOT/battlecode-hub"
cd "$ROOT/UNSW-Battlecode-2026"
sed -n '/^\[paths\]/,/^\[/p' "$JKS_HUB_ROOT/hub.toml"     # rewrite these four to the desktop paths:
#   repo        = "$ROOT/UNSW-Battlecode-2026"
#   python      = "$ROOT/UNSW-Battlecode-2026/.venv/bin/python"
#   key_file    = "$ROOT/UNSW-Battlecode-2026/.battlecode-api-key"
#   legacy_live = "$ROOT/battlecode-hub/legacy_live"     # any empty dir: the legacy worker is dead (D-016 cutover); mkdir it
#   mirror      = "$ROOT/UNSW-Battlecode-2026/hub-state"
grep -n '^mode' "$JKS_HUB_ROOT/hub.toml"                    # must read: mode = "shadow"
.venv/bin/python -m tools.hub.hubctl --root "$JKS_HUB_ROOT" executor status
.venv/bin/python -m tools.hub.actuator --serve &             # foreground trial: watch hub-state/daemon.json update, then Ctrl-C / kill
```

Then the service (edit the two paths and the python line in the example to `$ROOT/...` and `.venv/bin/python`):

```bash
mkdir -p ~/.config/systemd/user
sed -e "s#%h/CLionProjects/UNSW-Battlecode-2026-good#$ROOT/UNSW-Battlecode-2026#g" \
    -e "s#Environment=JKS_HUB_ROOT=.*#Environment=JKS_HUB_ROOT=$ROOT/battlecode-hub#" \
    -e "s#%h/anaconda3/bin/python#$ROOT/UNSW-Battlecode-2026/.venv/bin/python#" \
    tools/hub/jks-hub-actuator.service.example > ~/.config/systemd/user/jks-hub-actuator.service
systemctl --user daemon-reload && systemctl --user enable --now jks-hub-actuator
loginctl enable-linger "$USER"                    # keeps user services running when you are logged out
systemctl --user status jks-hub-actuator --no-pager; journalctl --user -u jks-hub-actuator -f
```

Redeploys from a Cowork or Claude Code session work as before (`python3 tools/hub/request_redeploy.py --note ...`);
the daemon snapshots `tools/hub` into `$JKS_HUB_ROOT/app/<sha>` and exits non-zero so systemd relaunches it
(`Restart=on-failure`, 60 s). The git keeper needs an ssh key or credential helper that works non-interactively
for `git push`; test `git push --dry-run` as the same user first. The Discord quota bot is optional and off.

## 6. GPU and the training stack

```bash
sudo ubuntu-drivers install                       # current NVIDIA driver; reboot; then:
nvidia-smi                                        # 4090 visible, driver >= 550
. "$ROOT/UNSW-Battlecode-2026/.venv/bin/activate"
pip install torch --index-url https://download.pytorch.org/whl/cu128    # pick the cu12x index matching nvidia-smi's CUDA version
python3 -c "import torch;print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
pip install lightgbm xgboost scikit-learn pandas pyarrow polars      # tree models train on CPU in seconds at our data sizes
```

What the hardware changes, and what it does not: training is not the bottleneck at this scale — every model on
the ledger (L27) trains in seconds to minutes on CPU, and even the fitted-Q/self-play nets fit on the 4090 in
minutes. **Game generation is the bottleneck.** The cloud container does ~290 games/h on 2 cores; unswbc games are
single-threaded, so this machine does roughly `(nproc − 2) × 145` games/h — a 160-game panel in a few minutes on a
16-core part, and a 2,000-game tuner run (R-5) in under an hour. Set `--jobs $(( $(nproc) - 2 ))` in `run_panel`,
`bench.py`, `tools/lune/run.py`, `tools/ra/lane.py`. Keep two cores free for the hub daemon and the corpus thread.

## 7. Verification checklist

1. `claude-desktop` opens; Cowork tab has no requirements banner; folder `$ROOT/UNSW-Battlecode-2026` is added.
2. `unswbc --version` = 1.2.2; the three smoke games ran; `arena.py --sandbox` prints points/turn.
3. Gate tests: `OK` (skips allowed).
4. `hub-state/daemon.json` `at` updates every cycle; `mode` = `shadow`; `api_calls` rising; the Mac LaunchAgent is unloaded.
5. `git push --dry-run` works non-interactively; a `hub-state/control/git.json` request produces `git.done.json` with `pushed: true`.
6. `torch.cuda.is_available()` = True; `python3 -c "import lightgbm, pyarrow, pycapnp"` silent.
7. `python -m tools.analysis.features.run_panel --panel z1 --jobs N --no-logs` runs one shard end to end.
