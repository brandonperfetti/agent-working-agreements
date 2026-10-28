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
#    _agent evidence are exempt (clients/ joins once the OpenClaw appendix is slimmed).
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AWA="$ROOT/AGENT-WORKING-AGREEMENTS.md"
PROC="$ROOT/procedures"
# 300 is the ceiling Brandon accepted on 2026-10-27 (hardening decision 3); lower it as
# procedures are trimmed, never raise it without his word.
: "${CORE_MAX:=300}"
fail=0

lines="$(wc -l <"$AWA" | tr -d ' ')"
if [ "$lines" -gt "$CORE_MAX" ]; then
  echo "FAIL: AGENT-WORKING-AGREEMENTS.md is $lines lines; the ceiling is $CORE_MAX" >&2; fail=1
fi

precedence='a rule here that contradicts one there is the rule that is wrong'
for f in "$PROC"/*.md; do
  name="$(basename "$f")"
  [ "$name" = "README.md" ] && continue
  for field in Trigger Owner Implements Stop; do
    grep -q "^\*\*$field:\*\*" "$f" || { echo "FAIL: $name lacks **$field:**" >&2; fail=1; }
  done
  grep -q "$precedence" "$f" || { echo "FAIL: $name lacks the precedence clause" >&2; fail=1; }
  grep -q "]($name)" "$PROC/README.md" || { echo "FAIL: $name is not listed in procedures/README.md" >&2; fail=1; }
  grep -q "](procedures/$name)" "$AWA" || { echo "FAIL: $name is not in the core's Triggers table" >&2; fail=1; }
done

# Every procedure the core links must exist.
while read -r link; do
  [ -z "$link" ] && continue
  [ -f "$ROOT/$link" ] || { echo "FAIL: core links $link, which does not exist" >&2; fail=1; }
done < <(grep -o 'procedures/[a-z0-9-]*\.md' "$AWA" | sort -u)

# No mutable-file pins in normative text. `git` SHAs in a commit citation are 7–12 hex; the
# pattern catches only full object or SHA-256 digests.
if grep -nE '\b[0-9a-f]{40}\b|\b[0-9a-f]{64}\b' "$AWA" "$PROC"/*.md; then
  echo "FAIL: a 40- or 64-hex pin appears in normative text (above); cite a learning or issue" >&2
  fail=1
fi

if [ "$fail" -eq 0 ]; then
  echo "ok: core $lines/$CORE_MAX lines; $(ls "$PROC"/*.md | grep -vc README) procedures indexed; no pins"
fi
exit "$fail"
