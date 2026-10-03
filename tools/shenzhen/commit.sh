#!/bin/bash
# Commit the Shenzhen lane to branch r/shenzhen without touching HEAD, the index or the working tree of the shared checkout.
# Lane files are edited under build/shenzhen/tree/<repo path> (build/ is ignored) and mapped to <repo path> in the commit.
# Usage (repo root): bash build/shenzhen/tree/tools/shenzhen/commit.sh "message"
set -e
cd "$(dirname "$0")/../../../../.."
export GIT_AUTHOR_NAME="Shenzhen (Claude Opus 5.5)" GIT_AUTHOR_EMAIL="noreply@anthropic.com"
export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME" GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
G="git --no-optional-locks -c core.createObject=rename"
T=build/shenzhen/tree
export GIT_INDEX_FILE="$PWD/build/shenzhen/tmp/idx.$$"
BASE=$($G rev-parse -q --verify refs/heads/r/shenzhen || $G rev-parse refs/heads/main)
$G read-tree "$BASE"
( cd "$T" && find . -type f ! -name '*.pyc' ! -path '*/__pycache__/*' | sed 's|^\./||' ) | while read -r f; do
  sz=$(stat -c %s "$T/$f"); [ "$sz" -gt 4000000 ] && { echo "skip >4MB $f"; continue; }
  h=$($G hash-object -w "$T/$f"); m=100644; [ -x "$T/$f" ] && m=100755
  $G update-index --add --cacheinfo "$m,$h,$f"
done
TREE=$($G write-tree)
if [ "$TREE" = "$($G rev-parse "$BASE^{tree}")" ]; then echo "nothing to commit"; mkdir -p build/shenzhen/tmp/_old && mv "$GIT_INDEX_FILE" build/shenzhen/tmp/_old/ 2>/dev/null || true; exit 0; fi
C=$(printf '%s\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01XHKNZywwiB4YTzxZ2D63Xr\n' "$1" | $G commit-tree "$TREE" -p "$BASE")
$G update-ref refs/heads/r/shenzhen "$C"
mkdir -p build/shenzhen/tmp/_old && mv "$GIT_INDEX_FILE" build/shenzhen/tmp/_old/ 2>/dev/null || true
$G log --oneline -1 r/shenzhen; $G diff --stat "$BASE" r/shenzhen | tail -3
