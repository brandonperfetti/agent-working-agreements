#!/usr/bin/env bash
#
# check-index.sh — verify Part C/client correspondence and the opener invariants
# shared by root AGENTS.md and clients/*.md. Missing mappings, agreement pointers, or
# standard precedence clauses fail the build.
#
# Progressive disclosure makes both failure modes easy to miss: an unindexed
# appendix is never read, while later duplicate text can mask a drifting opener.
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

# Every repository and client opener must send the reader to Parts A and B and
# preserve the standard conflict-precedence clause. Read only the first paragraph
# after the H1 so later prose or sections cannot mask drift in the opener.
for f in "$ROOT/AGENTS.md" "$ROOT"/clients/*.md; do
  opener="$(
    awk '
      BEGIN { ORS = " " }
      NR == 1 && /^# / { next }
      !started && /^[[:space:]]*$/ { next }
      !started {
        if (/^#/) { exit }
        started = 1
      }
      started && ($0 ~ /^[[:space:]]*$/ || $0 ~ /^#/) { exit }
      {
        gsub(/[[:space:]]+/, " ")
        sub(/^ /, "")
        sub(/ $/, "")
        print
      }
    ' "$f"
  )"
  [[ "$opener" == *"AGENT-WORKING-AGREEMENTS.md"* ]] || {
    echo "FAIL: $(basename "$f") opener does not point back at Parts A and B" >&2; fail=1; }
  [[ "$opener" == *"$precedence_clause"* ]] || {
    echo "FAIL: $(basename "$f") opener is missing: $precedence_clause" >&2; fail=1; }
done

# Parts A and B must remain whole: no appendix may be referenced as a substitute for them.
grep -q '^# Part A' "$AWA" || { echo "FAIL: Part A missing from the root file" >&2; fail=1; }
grep -q '^# Part B' "$AWA" || { echo "FAIL: Part B missing from the root file" >&2; fail=1; }

if [ "$fail" -eq 0 ]; then echo "ok: index/client mapping and root/client opener checks pass ($(wc -l <<<"$present") client files)"; fi
exit "$fail"
