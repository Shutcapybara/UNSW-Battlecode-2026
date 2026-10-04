#!/bin/bash
# Commit the Daichi lane to branch r/daichi without touching HEAD, the index or the working tree of the shared checkout.
# Lane files are edited under build/daichi/tree/<repo path> (build/ is ignored) and mapped to <repo path> in the commit.
# Usage (repo root): bash build/daichi/tree/tools/daichi/commit.sh "message"
set -e
cd "$(dirname "$0")/../../../../.."
export GIT_AUTHOR_NAME="Daichi (Claude Opus 5.5)" GIT_AUTHOR_EMAIL="noreply@anthropic.com"
export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME" GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
G="git --no-optional-locks -c core.createObject=rename"
T=build/daichi/tree
export GIT_INDEX_FILE="$PWD/build/daichi/tmp/idx.$$"
BASE=$($G rev-parse -q --verify refs/heads/r/daichi || $G rev-parse refs/heads/main)
# once main contains the lane (the coherence task merged it), build on main so shared files are current
if $G merge-base --is-ancestor "$BASE" refs/heads/main; then BASE=$($G rev-parse refs/heads/main); fi
$G read-tree "$BASE"
( cd "$T" && find . -type f ! -name '*.pyc' ! -path '*/__pycache__/*' | sed 's|^\./||' ) | while read -r f; do
  sz=$(stat -c %s "$T/$f"); [ "$sz" -gt 4000000 ] && { echo "skip >4MB $f"; continue; }
  h=$($G hash-object -w "$T/$f"); m=100644; [ -x "$T/$f" ] && m=100755
  $G update-index --add --cacheinfo "$m,$h,$f"
done
TREE=$($G write-tree)
if [ "$TREE" = "$($G rev-parse "$BASE^{tree}")" ]; then echo "nothing to commit"; mkdir -p build/daichi/tmp/_old && mv "$GIT_INDEX_FILE" build/daichi/tmp/_old/ 2>/dev/null || true; exit 0; fi
C=$(printf '%s\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_016bFTpC5zvco5T4jPtZ2jFp\n' "$1" | $G commit-tree "$TREE" -p "$BASE")
$G update-ref refs/heads/r/daichi "$C"
mkdir -p build/daichi/tmp/_old && mv "$GIT_INDEX_FILE" build/daichi/tmp/_old/ 2>/dev/null || true
$G log --oneline -1 r/daichi; $G diff --stat "$BASE" r/daichi | tail -3
