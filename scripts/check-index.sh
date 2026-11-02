#!/usr/bin/env bash
#
# check-index.sh — verify the composition contract: core → profile → client adapter.
#
# 1. Every clients/*.md has a row in a profile's client index, and every row names a file
#    that exists: an unindexed adapter is never read.
# 2. Openers of the root AGENTS.md, each profile and each client send the reader to the core
#    and keep the standard precedence clause; root and client openers also name an existing
#    profile, so a studio reader never reaches an adapter without its profile.
# 3. The core's Composition section links every profile an opener requires: a caller whose
#    pointer names only the core and a client file is still routed to the profile.
# 4. The core keeps Parts A and B and the stable anchors A1–A8 and B0–B2.
#
# Progressive disclosure makes each failure easy to miss: an unindexed file is never read,
# and later duplicate text can mask a drifting opener.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AWA="$ROOT/AGENT-WORKING-AGREEMENTS.md"
precedence_clause='and a rule here that contradicts one there is the rule that is wrong.'
fail=0

profiles=()
for p in "$ROOT"/profiles/*.md; do [ -e "$p" ] && profiles+=("$p"); done

indexed="$(
  for p in ${profiles[@]+"${profiles[@]}"}; do grep -o 'clients/[a-z0-9-]*\.md' "$p" || true; done |
    sort -u
)"
present="$(cd "$ROOT" && ls clients/*.md 2>/dev/null | sort -u || true)"

while read -r f; do
  [ -z "$f" ] && continue
  if ! grep -qxF "$f" <<<"$present"; then
    echo "FAIL: a profile's client index references $f, which does not exist" >&2; fail=1
  fi
done <<<"$indexed"

while read -r f; do
  [ -z "$f" ] && continue
  if ! grep -qxF "$f" <<<"$indexed"; then
    echo "FAIL: $f exists but no profile's client index points at it" >&2; fail=1
  fi
done <<<"$present"

# The first paragraph after the H1, whitespace-collapsed, so later text cannot mask drift.
opener() {
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
  ' "$1"
}

# A markdown section's body, from its heading to the next heading of the same or higher level.
section() {
  awk -v want="$2" '
    $0 == want { on = 1; next }
    on && /^##? / { exit }
    on { print }
  ' "$1"
}

composition="$(section "$AWA" '## Composition')"
[ -n "$composition" ] || { echo "FAIL: the core has no ## Composition section" >&2; fail=1; }

for f in "$ROOT/AGENTS.md" ${profiles[@]+"${profiles[@]}"} "$ROOT"/clients/*.md; do
  [ -e "$f" ] || continue
  name="$(basename "$f")"
  case "$f" in "$ROOT"/profiles/*) name="profiles/$name" ;; esac
  text="$(opener "$f")"
  [[ "$text" == *"AGENT-WORKING-AGREEMENTS.md"* ]] || {
    echo "FAIL: $name opener does not point back at Parts A and B" >&2; fail=1; }
  [[ "$text" == *"$precedence_clause"* ]] || {
    echo "FAIL: $name opener is missing: $precedence_clause" >&2; fail=1; }
  case "$f" in "$ROOT"/profiles/*) continue ;; esac
  required="$(grep -o 'profiles/[a-z0-9-]*\.md' <<<"$text" | sort -u || true)"
  if [ -z "$required" ]; then
    echo "FAIL: $name opener does not name its profile" >&2; fail=1; continue
  fi
  while read -r p; do
    [ -f "$ROOT/$p" ] || { echo "FAIL: $name opener names $p, which does not exist" >&2; fail=1; }
    grep -qF "]($p)" <<<"$composition" || {
      echo "FAIL: the core's Composition section does not route callers to $p" >&2; fail=1; }
  done <<<"$required"
done

# Parts A and B and the stable anchors stay whole in the core.
grep -q '^# Part A' "$AWA" || { echo "FAIL: Part A missing from the root file" >&2; fail=1; }
grep -q '^# Part B' "$AWA" || { echo "FAIL: Part B missing from the root file" >&2; fail=1; }
for a in A1 A2 A3 A4 A5 A6 A7 A8 B0 B1 B2; do
  grep -q "^## $a\. " "$AWA" || { echo "FAIL: stable anchor $a missing from the core" >&2; fail=1; }
done

if [ "$fail" -eq 0 ]; then
  echo "ok: core → profile → client composition holds ($(wc -l <<<"$present") client files, ${#profiles[@]} profile(s))"
fi
exit "$fail"
