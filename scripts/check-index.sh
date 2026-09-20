#!/usr/bin/env bash
#
# check-index.sh — the Part C index in AGENT-WORKING-AGREEMENTS.md and the files in
# clients/ must correspond exactly. A client file with no index row, or an index row
# pointing at a file that does not exist, fails the build.
#
# This is the one piece of drift progressive disclosure introduces that nobody notices
# by reading: the root file looks fine, and the missing appendix is simply never read.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AWA="$ROOT/AGENT-WORKING-AGREEMENTS.md"
precedence_clause='and a rule here that contradicts one there is the rule that is wrong.'
fail=0

indexed="$(grep -o 'clients/[a-z0-9-]*\.md' "$AWA" | sort -u)"
present="$(cd "$ROOT" && ls clients/*.md | sort -u)"

while read -r f; do
  [ -z "$f" ] && continue
  if ! grep -qxF "$f" <<<"$present"; then
    echo "FAIL: index references $f, which does not exist" >&2; fail=1
  fi
done <<<"$indexed"

while read -r f; do
  [ -z "$f" ] && continue
  if ! grep -qxF "$f" <<<"$indexed"; then
    echo "FAIL: $f exists but no row in the Part C index points at it" >&2; fail=1
  fi
done <<<"$present"

# Every client opener must send the reader to Parts A and B first and preserve the
# standard conflict-precedence clause. Stop at the first H2 so a later mention
# cannot mask drift in the opener.
for f in "$ROOT"/clients/*.md; do
  grep -q 'AGENT-WORKING-AGREEMENTS.md' "$f" || {
    echo "FAIL: $(basename "$f") does not point back at Parts A and B" >&2; fail=1; }

  opener="$(awk 'BEGIN { ORS=" " } /^## / { exit } { print }' "$f")"
  [[ "$opener" == *"$precedence_clause"* ]] || {
    echo "FAIL: $(basename "$f") opener is missing: $precedence_clause" >&2; fail=1; }
done

# Parts A and B must remain whole: no appendix may be referenced as a substitute for them.
grep -q '^# Part A' "$AWA" || { echo "FAIL: Part A missing from the root file" >&2; fail=1; }
grep -q '^# Part B' "$AWA" || { echo "FAIL: Part B missing from the root file" >&2; fail=1; }

if [ "$fail" -eq 0 ]; then echo "ok: index and clients/ agree ($(wc -l <<<"$present") client files)"; fi
exit "$fail"
