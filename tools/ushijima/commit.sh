#!/bin/bash
# Commit the Chair lane (Ushijima) to branch r/ushijima without touching HEAD, the index or the working tree of the
# shared checkout. Lane files are edited under build/ushijima/tree/<repo path> (build/ is ignored) and mapped to
# <repo path> in the commit. Copied from tools/kanazawa/commit.sh; the first commit is based on origin/main.
# Usage (repo root): bash build/ushijima/tree/tools/ushijima/commit.sh "message"
set -e
cd "$(dirname "$0")/../../../../.."
export GIT_AUTHOR_NAME="Ushijima (Chair, Claude Fable 5.1)" GIT_AUTHOR_EMAIL="noreply@anthropic.com"
export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME" GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
G="git --no-optional-locks -c core.createObject=rename"
T=build/ushijima/tree
mkdir -p build/ushijima/tmp
export GIT_INDEX_FILE="$PWD/build/ushijima/tmp/idx.$$"
BASE=$($G rev-parse -q --verify refs/heads/r/ushijima || $G rev-parse refs/remotes/origin/main)
$G read-tree "$BASE"
( cd "$T" && find . -type f ! -name '*.pyc' ! -path '*/__pycache__/*' | sed 's|^\./||' ) | while read -r f; do
  sz=$(stat -c %s "$T/$f"); [ "$sz" -gt 4000000 ] && { echo "skip >4MB $f"; continue; }
  h=$($G hash-object -w "$T/$f"); m=100644; [ -x "$T/$f" ] && m=100755
  $G update-index --add --cacheinfo "$m,$h,$f"
done
TREE=$($G write-tree)
if [ "$TREE" = "$($G rev-parse "$BASE^{tree}")" ]; then echo "nothing to commit"; mkdir -p build/ushijima/tmp/_old && mv "$GIT_INDEX_FILE" build/ushijima/tmp/_old/ 2>/dev/null || true; exit 0; fi
C=$(printf '%s\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01AxB1aseUMDmHZyB6N8o2jy\n' "$1" | $G commit-tree "$TREE" -p "$BASE")
$G update-ref refs/heads/r/ushijima "$C"
mkdir -p build/ushijima/tmp/_old && mv "$GIT_INDEX_FILE" build/ushijima/tmp/_old/ 2>/dev/null || true
$G log --oneline -1 r/ushijima; $G diff --stat "$BASE" r/ushijima | tail -3
