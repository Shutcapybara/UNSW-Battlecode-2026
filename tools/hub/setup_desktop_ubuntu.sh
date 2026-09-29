#!/usr/bin/env bash
# JKS desktop setup for Ubuntu 22.04+/24.04 — automates docs/hub/DESKTOP_SETUP_UBUNTU.md §2–§7.
# Idempotent: every step checks before it acts, so re-running after a failure or a reboot is safe.
#
#   ROOT=~/Projects MAC=alik@mac.local bash setup_desktop_ubuntu.sh [--with-corpus] [--hub] [--gpu] [--all]
#
#   ROOT          where everything lives (default ~/Projects): $ROOT/UNSW-Battlecode-2026, $ROOT/battlecode-hub, $ROOT/wt-*
#   MAC           ssh target of the Mac (user@host). Unset = skip every copy from the Mac (key, corpus, hub root).
#   --with-corpus rsync public_replays/ (~32 GB) and build/ caches from the Mac
#   --hub         copy the hub root from the Mac, rewrite hub.toml paths, install the systemd user unit (mode stays shadow)
#   --gpu         NVIDIA driver (reboot if newly installed) + CUDA torch + tree-model libs
#   --all         all three
#
# Not automated (needs you): claude-desktop sign-in and "Add folder"; `claude` CLI sign-in; git identity if unset;
# an ssh key / credential helper for non-interactive `git push` (the hub's git keeper needs it); the firmware
# virtualization switch; stopping the Mac's LaunchAgent before --hub (the script refuses to install the unit until you confirm).
set -euo pipefail

ROOT="${ROOT:-$HOME/Projects}"
MAC="${MAC:-}"
REPO_URL="${REPO_URL:-https://github.com/Shutcapybara/UNSW-Battlecode-2026}"
MAC_REPO="${MAC_REPO:-/Users/alik/Documents/Projects/UNSW-Battlecode-2026}"
MAC_HUB="${MAC_HUB:-/Users/alik/Documents/Projects/battlecode-hub}"
UNSWBC_VERSION="${UNSWBC_VERSION:-1.2.2}"
WITH_CORPUS=0; WITH_HUB=0; WITH_GPU=0
for a in "$@"; do case "$a" in
  --with-corpus) WITH_CORPUS=1;; --hub) WITH_HUB=1;; --gpu) WITH_GPU=1;; --all) WITH_CORPUS=1; WITH_HUB=1; WITH_GPU=1;;
  -h|--help) sed -n '2,20p' "$0"; exit 0;; *) echo "unknown flag $a"; exit 2;; esac; done

REPO="$ROOT/UNSW-Battlecode-2026"; HUB="$ROOT/battlecode-hub"; VENV="$REPO/.venv"; PY="$VENV/bin/python"
LOG="$ROOT/setup_desktop_$(date -u +%Y%m%dT%H%M%SZ).log"
mkdir -p "$ROOT"; exec > >(tee -a "$LOG") 2>&1
step() { printf '\n\033[1;34m== %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m   ok: %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m   !! %s\033[0m\n' "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }
[ "$(id -u)" -eq 0 ] && { echo "run as your normal user, not root (sudo is used where needed)"; exit 1; }
if ! grep -qiE 'ubuntu|debian' /etc/os-release; then warn "not Ubuntu/Debian; apt steps will fail"; fi

# ---------------------------------------------------------------- 0. shell env
step "0. shell environment (~/.bashrc)"
touch ~/.bashrc
grep -q 'JKS_ROOT=' ~/.bashrc || printf '\n# JKS battlecode\nexport JKS_ROOT="%s"\nexport ROOT="$JKS_ROOT"\nexport JKS_HUB_ROOT="%s"\n' "$ROOT" "$HUB" >> ~/.bashrc
export JKS_HUB_ROOT="$HUB"; ok "ROOT=$ROOT  HUB=$HUB  log=$LOG"

# ---------------------------------------------------------------- 1. packages
step "1. apt packages (build toolchain, python, capnp, rsync)"
sudo apt-get update -qq
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq git git-lfs build-essential g++ clang cmake ninja-build pkg-config \
  python3 python3-venv python3-dev python3-pip pipx rsync htop tmux jq sqlite3 curl gnupg ca-certificates \
  libcapnp-dev capnproto openssh-client
GXX_MAJOR=$(g++ -dumpversion | cut -d. -f1); [ "$GXX_MAJOR" -ge 11 ] && ok "g++ $(g++ -dumpversion) (C++20 ok)" || warn "g++ < 11: Ares needs C++20"
ok "cores: $(nproc)  ram: $(free -g | awk '/Mem/{print $2}') GB"

# ---------------------------------------------------------------- 2. node + claude code
step "2. Claude Code CLI"
if ! have node || [ "$(node -v | sed 's/v//' | cut -d. -f1)" -lt 18 ]; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt-get install -y -qq nodejs
fi
have claude || sudo npm install -g @anthropic-ai/claude-code
ok "node $(node -v), claude $(claude --version 2>/dev/null | head -1 || echo '(installed; sign in with: claude)')"
have claude-desktop && ok "claude-desktop present" || warn "claude-desktop not installed (guide §1)"
id -nG | grep -qw kvm && ok "user in kvm group" || warn "not in kvm group: sudo usermod -aG kvm $USER, then log out/in (Cowork needs it)"

# ---------------------------------------------------------------- 3. repo + venv
step "3. repository and virtualenv"
if [ ! -d "$REPO/.git" ]; then git clone "$REPO_URL" "$REPO"; else (cd "$REPO" && git fetch -q origin && git status -sb | head -1); fi
cd "$REPO"
git config user.name  >/dev/null || warn "git user.name unset: git config --global user.name '...'"
git config user.email >/dev/null || warn "git user.email unset: git config --global user.email '...'"
[ -x "$PY" ] || python3 -m venv "$VENV"
"$PY" -m pip install -q -U pip wheel
"$PY" -m pip install -q "unswbc==$UNSWBC_VERSION"
"$PY" -m pip install -q -r tools/requirements-benchmark.txt -r tools/requirements-rl.txt 2>/dev/null || \
  "$PY" -m pip install -q 'numpy>=2.0' 'pandas>=2.2' 'scikit-learn>=1.6' 'pycapnp>=2.0' scipy
"$PY" -m pip install -q pyarrow polars lightgbm xgboost matplotlib
ok "unswbc $("$VENV/bin/unswbc" --version 2>&1 | head -1)"
grep -q 'JKS venv' ~/.bashrc || printf '# JKS venv\n[ -f "%s/bin/activate" ] && . "%s/bin/activate"\n' "$VENV" "$VENV" >> ~/.bashrc

step "3b. worktrees for the R lanes"
for lane in r1 ra rg r3 r4 r5; do
  [ -d "$ROOT/wt-$lane" ] && continue
  if git show-ref --verify -q "refs/heads/r/$lane" || git show-ref --verify -q "refs/remotes/origin/r/$lane"; then
    git worktree add -q "$ROOT/wt-$lane" "r/$lane" 2>/dev/null || git worktree add -q "$ROOT/wt-$lane" -b "r/$lane" "origin/r/$lane"
  else git worktree add -q "$ROOT/wt-$lane" -b "r/$lane"; fi
done; ok "$(git worktree list | wc -l) worktrees"

# ---------------------------------------------------------------- 4. API key
step "4. API credential"
if [ -f "$REPO/.battlecode-api-key" ]; then ok "key present"
elif [ -n "$MAC" ]; then scp -q "$MAC:$MAC_REPO/.battlecode-api-key" "$REPO/.battlecode-api-key" && ok "key copied from the Mac"
else warn "no key: copy $MAC_REPO/.battlecode-api-key from the Mac to $REPO/.battlecode-api-key (scp; never git/chat)"; fi
[ -f "$REPO/.battlecode-api-key" ] && chmod 600 "$REPO/.battlecode-api-key"
git check-ignore -q .battlecode-api-key && ok "key is gitignored" || { echo "FATAL: .battlecode-api-key is not gitignored"; exit 1; }

# ---------------------------------------------------------------- 5. data from the Mac
if [ "$WITH_CORPUS" -eq 1 ]; then
  step "5. corpus and caches from the Mac"
  [ -n "$MAC" ] || { warn "MAC unset; skipping"; }
  if [ -n "$MAC" ]; then
    mkdir -p public_replays build hub-state
    rsync -a --info=progress2 "$MAC:$MAC_REPO/public_replays/" public_replays/
    for d in zoo cx c2-0 f1; do rsync -a "$MAC:$MAC_REPO/build/$d/" "build/$d/" 2>/dev/null || true; done
    rsync -a "$MAC:$MAC_REPO/hub-state/" hub-state/
    ok "corpus: $(find public_replays -type f | wc -l) files"
  fi
fi

# ---------------------------------------------------------------- 6. hub
if [ "$WITH_HUB" -eq 1 ]; then
  step "6. hub root, hub.toml, systemd user unit"
  if [ ! -f "$HUB/hub.sqlite" ]; then
    [ -n "$MAC" ] || { echo "MAC unset: cannot copy the hub root (hub.sqlite is the only copy of the record)"; exit 1; }
    read -r -p "   Is the Mac LaunchAgent stopped? (launchctl unload ~/Library/LaunchAgents/au.battlecode.jks-hub.plist) [y/N] " yn
    [ "$yn" = y ] || { echo "stop it first: two daemons must never hold the executor lease"; exit 1; }
    rsync -a "$MAC:$MAC_HUB/" "$HUB/"
  fi
  sqlite3 "$HUB/hub.sqlite" 'pragma integrity_check;' | grep -q ok && ok "hub.sqlite integrity ok" || { echo "hub.sqlite integrity failed"; exit 1; }
  mkdir -p "$HUB/legacy_live/state"
  "$PY" - "$HUB/hub.toml" "$REPO" "$PY" "$HUB" <<'EOF'
import re, sys
path, repo, py, hub = sys.argv[1:]
t = open(path).read()
new = {'repo': repo, 'python': py, 'key_file': f'{repo}/.battlecode-api-key', 'legacy_live': f'{hub}/legacy_live', 'mirror': f'{repo}/hub-state'}
m = re.search(r'^\[paths\][^\[]*', t, re.M)
body = m.group(0) if m else '[paths]\n'
for k, v in new.items():
    line = f'{k} = "{v}"'
    body = re.sub(rf'^{k}\s*=.*$', line, body, count=1, flags=re.M) if re.search(rf'^{k}\s*=', body, re.M) else body.rstrip('\n') + '\n' + line + '\n'
t = t.replace(m.group(0), body) if m else body + t
if re.search(r'^\[executor\]', t, re.M):
    t = re.sub(r'^mode\s*=.*$', 'mode = "shadow"', t, count=1, flags=re.M)
else:
    t += '\n[executor]\nmode = "shadow"\n'
open(path, 'w').write(t)
print(body)
EOF
  grep -q 'mode = "shadow"' "$HUB/hub.toml" && ok "executor mode shadow (D-031)" || { echo "mode not shadow"; exit 1; }
  export JKS_HUB_FIXTURE="$REPO/build/hub-fixture"
  "$PY" -m unittest -q tests.test_hub_core tests.test_hub_git tests.test_hub_legacy_ops tests.test_hub_executor tests.test_hub_daemon \
    tests.test_hub_quota_filler tests.test_hub_discord_bot tests.test_hub_api 2>&1 | tail -2
  mkdir -p ~/.config/systemd/user
  cat > ~/.config/systemd/user/jks-hub-actuator.service <<EOF
[Unit]
Description=JKS hub actuator and quota executor
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$REPO
Environment=JKS_HUB_ROOT=$HUB
Environment=JKS_AGENT=hub/actuator/systemd
Environment=PYTHONUNBUFFERED=1
ExecStart=$PY -m tools.hub.actuator --serve
Restart=on-failure
RestartSec=60

[Install]
WantedBy=default.target
EOF
  systemctl --user daemon-reload && systemctl --user enable --now jks-hub-actuator
  loginctl enable-linger "$USER" || true
  sleep 20; systemctl --user is-active jks-hub-actuator && ok "daemon active; watch: journalctl --user -u jks-hub-actuator -f" || warn "daemon not active: journalctl --user -u jks-hub-actuator -n 50"
  (cd "$REPO" && git push --dry-run -q 2>/dev/null) && ok "git push works non-interactively" || warn "git push needs a credential helper or ssh key before the keeper can push"
fi

# ---------------------------------------------------------------- 7. GPU
if [ "$WITH_GPU" -eq 1 ]; then
  step "7. NVIDIA driver + CUDA torch"
  if ! have nvidia-smi; then
    sudo ubuntu-drivers install && { warn "driver installed: REBOOT, then re-run with --gpu to install torch"; }
  else
    CUDA=$(nvidia-smi | grep -oE 'CUDA Version: [0-9]+\.[0-9]+' | grep -oE '[0-9]+\.[0-9]+' || echo 12.8)
    IDX="cu$(echo "$CUDA" | tr -d .)"; case "$IDX" in cu12[0-5]) IDX=cu124;; cu12[6-7]) IDX=cu126;; cu12[89]|cu13*) IDX=cu128;; esac
    "$PY" -c 'import torch' 2>/dev/null || "$PY" -m pip install -q torch --index-url "https://download.pytorch.org/whl/$IDX"
    "$PY" -c "import torch;print('   torch', torch.__version__, 'cuda', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')"
  fi
fi

# ---------------------------------------------------------------- 8. smoke tests
step "8. smoke tests"
cd "$REPO"; UB="$VENV/bin/unswbc"
"$UB" run maps/schooltime.map bots/yuna-v05-core bots/fenrir-v18-arrival-ready-beds >/dev/null 2>&1 && ok "python game" || warn "python game failed (run it by hand to see why)"
"$UB" run maps/schooltime.map bots/ares-v06-expanded-search-support bots/yuna-v05-core >/dev/null 2>&1 && ok "c++ game (native)" || warn "c++ game failed: check g++/clang and the unswbc build output"
"$PY" tools/cx/arena.py --sandbox maps/portals.map bots/ares-v06-expanded-search-support bots/yuna-v05-core 2>&1 | tail -3 || warn "sandbox arena failed"
"$PY" -c 'import lightgbm, pyarrow, sklearn, pandas' && ok "ml libs import"
step "done — open a new shell (bashrc changed). Checklist: docs/hub/DESKTOP_SETUP_UBUNTU.md §7. Log: $LOG"
