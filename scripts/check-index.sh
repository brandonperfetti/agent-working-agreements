#!/usr/bin/env bash
#
# check-index.sh — verify the composition contract: core → profile → client adapter.
#
# 1. Every clients/*.md has a row in a profile's "## Client adapters" table, and every row names
#    a file that exists: an unindexed adapter is never read, and a link elsewhere indexes nothing.
# 2. Openers of the root AGENTS.md, each profile and each client send the reader to the core
#    and keep the standard precedence clause; root and client openers also name an existing
#    profile, and each client opener names its own file: the opener alone carries the whole
#    core + profile + client binding, so a pointer naming only the core and a client file still
#    reaches the profile.
# 3. The core names no profile file: it stays portable and usable with no profile at all.
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

# Only the body rows of a profile's client index table index a client: the first table under
# "## Client adapters" whose header row starts "| You are |", from the row after its separator to
# the first line that is not a row. A link in prose, or in any other table, is never the index.
client_rows() {
  awk '
    function first_cell(s) {
      sub(/^[[:space:]]*\|[[:space:]]*/, "", s); sub(/[[:space:]]*\|.*$/, "", s); return s
    }
    done { next }
    /^#/ { if (state == 2) done = 1; else { in_sec = ($0 ~ /^## Client adapters/); state = 0 }; next }
    !in_sec { prev_row = 0; next }
    {
      row = ($0 ~ /^[[:space:]]*\|.*\|[[:space:]]*$/)
      if (state == 2) { if (row) print; else done = 1 }
      else if (state == 1) { state = ($0 ~ /^[[:space:]]*\|[[:space:]:|-]*-[[:space:]:|-]*\|[[:space:]]*$/) ? 2 : 0 }
      else if (row && !prev_row && first_cell($0) == "You are") state = 1
      prev_row = row
    }
  ' "$1"
}

indexed="$(
  for p in ${profiles[@]+"${profiles[@]}"}; do
    client_rows "$p" | grep -o 'clients/[a-z0-9-]*\.md' || true
  done | sort -u
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
  case "$f" in "$ROOT"/clients/*)
    [[ "$text" == *"clients/$name"* ]] || {
      echo "FAIL: $name opener does not name its own file" >&2; fail=1; } ;;
  esac
  required="$(grep -o 'profiles/[a-z0-9-]*\.md' <<<"$text" | sort -u || true)"
  if [ -z "$required" ]; then
    echo "FAIL: $name opener does not name its profile" >&2; fail=1; continue
  fi
  while read -r p; do
    [ -f "$ROOT/$p" ] || { echo "FAIL: $name opener names $p, which does not exist" >&2; fail=1; }
  done <<<"$required"
done

# The core is portable: it names no profile, so it reads whole with none.
if grep -nE 'profiles/[A-Za-z0-9._-]+' "$AWA" >&2; then
  echo "FAIL: the core names a profile file (above); adapter openers bind profiles" >&2; fail=1
fi

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
