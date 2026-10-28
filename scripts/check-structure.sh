#!/usr/bin/env bash
#
# check-structure.sh — keep the agreement small and the procedures reachable.
#
# 1. The core (Parts A–C) stays under CORE_MAX lines: progressive disclosure only works
#    while the always-loaded file is short enough to be read whole and attended to.
# 2. Every procedures/*.md carries Trigger / Owner / Implements / Stop and the precedence
#    clause, and is linked from both procedures/README.md and the core's Triggers table:
#    an unindexed procedure is never read.
# 3. Core and procedures hold no 40- or 64-hex pin: a hash of a mutable file goes stale on
#    the next edit and the rule that cites it is then wrong. CHANGELOG.md, clients/ and
#    _agent evidence are exempt. `history/` is exempt: it exists to hold them.
# 4. Each clients/*.md stays under CLIENT_MAX lines, for the same reason as 1.
# 5. A client-specific procedure lives at procedures/<client>/<name>.md, carries the same
#    fields, is listed in procedures/README.md, and is linked from clients/<client>.md
#    rather than from the core's Triggers table.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AWA="$ROOT/AGENT-WORKING-AGREEMENTS.md"
PROC="$ROOT/procedures"
# 300 is the ceiling Brandon accepted on 2026-10-27 (hardening decision 3); lower it as
# procedures are trimmed, never raise it without his word.
: "${CORE_MAX:=300}"
# 150 is the per-client ceiling Brandon accepted on 2026-10-27 (hardening decision 3).
: "${CLIENT_MAX:=150}"
fail=0

lines="$(wc -l <"$AWA" | tr -d ' ')"
if [ "$lines" -gt "$CORE_MAX" ]; then
  echo "FAIL: AGENT-WORKING-AGREEMENTS.md is $lines lines; the ceiling is $CORE_MAX" >&2; fail=1
fi

for f in "$ROOT"/clients/*.md; do
  [ -e "$f" ] || continue
  n="$(wc -l <"$f" | tr -d ' ')"
  if [ "$n" -gt "$CLIENT_MAX" ]; then
    echo "FAIL: clients/$(basename "$f") is $n lines; the ceiling is $CLIENT_MAX" >&2; fail=1
  fi
done

precedence='a rule here that contradicts one there is the rule that is wrong'
for f in "$PROC"/*.md "$PROC"/*/*.md; do
  [ -e "$f" ] || continue
  name="$(basename "$f")"
  [ "$name" = "README.md" ] && continue
  rel="${f#"$PROC"/}"                      # name.md, or <client>/name.md
  for field in Trigger Owner Implements Stop; do
    grep -q "^\*\*$field:\*\*" "$f" || { echo "FAIL: $rel lacks **$field:**" >&2; fail=1; }
  done
  grep -q "$precedence" "$f" || { echo "FAIL: $rel lacks the precedence clause" >&2; fail=1; }
  grep -q "]($rel)" "$PROC/README.md" || { echo "FAIL: $rel is not listed in procedures/README.md" >&2; fail=1; }
  if [ "$rel" = "$name" ]; then
    grep -q "](procedures/$rel)" "$AWA" || { echo "FAIL: $rel is not in the core's Triggers table" >&2; fail=1; }
  else
    client="$ROOT/clients/${rel%%/*}.md"
    if [ -f "$client" ]; then
      grep -q "](../procedures/$rel)" "$client" || { echo "FAIL: $rel is not linked from clients/${rel%%/*}.md" >&2; fail=1; }
    else
      echo "FAIL: $rel has no client file clients/${rel%%/*}.md" >&2; fail=1
    fi
  fi
done

# Every procedure the core or a client links must exist.
while read -r link; do
  [ -z "$link" ] && continue
  [ -f "$ROOT/$link" ] || { echo "FAIL: core links $link, which does not exist" >&2; fail=1; }
done < <(grep -o 'procedures/[a-z0-9-]*\.md' "$AWA" | sort -u)
for c in "$ROOT"/clients/*.md; do
  [ -e "$c" ] || continue
  while read -r link; do
    [ -z "$link" ] && continue
    [ -f "$ROOT/$link" ] || { echo "FAIL: clients/$(basename "$c") links $link, which does not exist" >&2; fail=1; }
  done < <(grep -o 'procedures/[a-z0-9-]*/[a-z0-9-]*\.md' "$c" | sort -u)
done

# No mutable-file pins in normative text. `git` SHAs in a commit citation are 7–12 hex; the
# pattern catches only full object or SHA-256 digests.
if grep -nE '\b[0-9a-f]{40}\b|\b[0-9a-f]{64}\b' "$AWA" "$PROC"/*.md "$PROC"/*/*.md "$ROOT"/clients/*.md 2>/dev/null; then
  echo "FAIL: a 40- or 64-hex pin appears in normative text (above); cite a learning or issue" >&2
  fail=1
fi

if [ "$fail" -eq 0 ]; then
  n=0; for f in "$PROC"/*.md "$PROC"/*/*.md; do [ -e "$f" ] && [ "$(basename "$f")" != README.md ] && n=$((n + 1)); done
  echo "ok: core $lines/$CORE_MAX lines; clients under $CLIENT_MAX; $n procedures indexed; no pins"
fi
exit "$fail"
