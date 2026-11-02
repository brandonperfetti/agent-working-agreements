#!/usr/bin/env bash
#
# check-structure.sh — keep the agreement small, portable and the procedures reachable.
#
# 1. The always-read load — the core plus one profile — stays under CORE_MAX lines:
#    progressive disclosure only works while what is read up front is short enough to be read
#    whole and attended to.
# 2. Every procedures/*.md carries Trigger / Owner / Implements / Stop and the precedence
#    clause, and is a row of both procedures/README.md's table and a profile's "## Triggers"
#    table: an unindexed procedure is never read, and a link in prose indexes nothing.
# 3. Core, profiles, clients and procedures hold no 40- or 64-hex pin: a hash of a mutable file
#    goes stale on the next edit and the rule that cites it is then wrong. CHANGELOG.md and
#    _agent evidence are exempt. `history/` is exempt: it exists to hold them.
# 4. Each clients/*.md stays under CLIENT_MAX lines, for the same reason as 1.
# 5. A client-specific procedure lives at procedures/<client>/<name>.md, carries the same
#    fields, is listed in procedures/README.md, and is linked from clients/<client>.md
#    rather than from a profile's Triggers table.
# 6. The core stays portable: no owner identity, studio staff, accounts, paths, client names,
#    base-branch names or studio profile name. Those belong to a profile or a client adapter.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AWA="$ROOT/AGENT-WORKING-AGREEMENTS.md"
PROC="$ROOT/procedures"
# 300 is the ceiling Brandon accepted on 2026-10-27 (hardening decision 3) for the always-read
# file; since #226 it bounds the core plus each profile together. Lower it as text is trimmed,
# never raise it without his word.
: "${CORE_MAX:=300}"
# 150 is the per-client ceiling Brandon accepted on 2026-10-27 (hardening decision 3).
: "${CLIENT_MAX:=150}"
fail=0

profiles=()
for p in "$ROOT"/profiles/*.md; do [ -e "$p" ] && profiles+=("$p"); done

lines="$(wc -l <"$AWA" | tr -d ' ')"
if [ "$lines" -gt "$CORE_MAX" ]; then
  echo "FAIL: AGENT-WORKING-AGREEMENTS.md is $lines lines; the ceiling is $CORE_MAX" >&2; fail=1
fi
for p in ${profiles[@]+"${profiles[@]}"}; do
  n="$(( lines + $(wc -l <"$p" | tr -d ' ') ))"
  if [ "$n" -gt "$CORE_MAX" ]; then
    echo "FAIL: the core plus profiles/$(basename "$p") is $n lines; the ceiling is $CORE_MAX" >&2
    fail=1
  fi
done

for f in "$ROOT"/clients/*.md; do
  [ -e "$f" ] || continue
  n="$(wc -l <"$f" | tr -d ' ')"
  if [ "$n" -gt "$CLIENT_MAX" ]; then
    echo "FAIL: clients/$(basename "$f") is $n lines; the ceiling is $CLIENT_MAX" >&2; fail=1
  fi
done

precedence='a rule here that contradicts one there is the rule that is wrong'

# The body rows of the actual index: the first table under the heading that starts with $2 (any
# heading when $2 is empty) whose header row's first cell is $3, from the row after its separator
# to the first line that is not a row. A link in prose, or in any other table of the same section
# or file, is no row of the index.
index_rows() {
  awk -v h="$2" -v c="$3" '
    function first_cell(s) {
      sub(/^[[:space:]]*\|[[:space:]]*/, "", s); sub(/[[:space:]]*\|.*$/, "", s); return s
    }
    done { next }
    /^#/ { if (state == 2) done = 1; else { in_sec = (h == "" || index($0, h) == 1); state = 0 }; next }
    !in_sec { prev_row = 0; next }
    {
      row = ($0 ~ /^[[:space:]]*\|.*\|[[:space:]]*$/)
      if (state == 2) { if (row) print; else done = 1 }
      else if (state == 1) { state = ($0 ~ /^[[:space:]]*\|[[:space:]:|-]*-[[:space:]:|-]*\|[[:space:]]*$/) ? 2 : 0 }
      else if (row && !prev_row && first_cell($0) == c) state = 1
      prev_row = row
    }
  ' "$1"
}
readme_rows="$(index_rows "$PROC/README.md" '' 'Procedure')"
trigger_rows="$(for p in ${profiles[@]+"${profiles[@]}"}; do index_rows "$p" '## Triggers' 'When'; done)"

for f in "$PROC"/*.md "$PROC"/*/*.md; do
  [ -e "$f" ] || continue
  name="$(basename "$f")"
  [ "$name" = "README.md" ] && continue
  rel="${f#"$PROC"/}"                      # name.md, or <client>/name.md
  for field in Trigger Owner Implements Stop; do
    grep -q "^\*\*$field:\*\*" "$f" || { echo "FAIL: $rel lacks **$field:**" >&2; fail=1; }
  done
  grep -q "$precedence" "$f" || { echo "FAIL: $rel lacks the precedence clause" >&2; fail=1; }
  grep -qF "]($rel)" <<<"$readme_rows" || { echo "FAIL: $rel is not listed in procedures/README.md" >&2; fail=1; }
  if [ "$rel" = "$name" ]; then
    grep -qF "](../procedures/$rel)" <<<"$trigger_rows" ||
      { echo "FAIL: $rel is not in a profile's Triggers table" >&2; fail=1; }
  else
    client="$ROOT/clients/${rel%%/*}.md"
    if [ -f "$client" ]; then
      grep -q "](../procedures/$rel)" "$client" || { echo "FAIL: $rel is not linked from clients/${rel%%/*}.md" >&2; fail=1; }
    else
      echo "FAIL: $rel has no client file clients/${rel%%/*}.md" >&2; fail=1
    fi
  fi
done

# Every procedure the core, a profile or a client links must exist.
while read -r link; do
  [ -z "$link" ] && continue
  [ -f "$ROOT/$link" ] || { echo "FAIL: core links $link, which does not exist" >&2; fail=1; }
done < <(grep -o 'procedures/[a-z0-9/-]*\.md' "$AWA" | sort -u)
for p in ${profiles[@]+"${profiles[@]}"}; do
  while read -r link; do
    [ -z "$link" ] && continue
    [ -f "$ROOT/$link" ] || { echo "FAIL: profiles/$(basename "$p") links $link, which does not exist" >&2; fail=1; }
  done < <(grep -o '\.\./procedures/[a-z0-9/-]*\.md' "$p" | sed 's#^\.\./##' | sort -u)
done
for c in "$ROOT"/clients/*.md; do
  [ -e "$c" ] || continue
  while read -r link; do
    [ -z "$link" ] && continue
    [ -f "$ROOT/$link" ] || { echo "FAIL: clients/$(basename "$c") links $link, which does not exist" >&2; fail=1; }
  done < <(grep -o 'procedures/[a-z0-9-]*/[a-z0-9-]*\.md' "$c" | sort -u)
done

# The core is portable: studio identity, staff, accounts, paths, clients and base-branch names
# live in a profile or a client adapter; the core names no studio profile either.
studio='Brandon|brandonperfetti|Sans Faux|[Ss]ansfaux|Camina|Judy|Amos|Ashford|Kody|CodeRabbit|OpenClaw'
studio+='|Claude Code|Cowork|Codex|~/|_agent/|`develop`|`master`|[a-z0-9._-]+@[a-z0-9-]+\.[a-z]'
if grep -nE "$studio" "$AWA"; then
  echo "FAIL: studio-specific text in the portable core (above); move it to a profile or client" >&2
  fail=1
fi

# No mutable-file pins in normative text. `git` SHAs in a commit citation are 7–12 hex; the
# pattern catches only full object or SHA-256 digests.
normative=("$AWA")
for f in "$PROC"/*.md "$PROC"/*/*.md "$ROOT"/clients/*.md "$ROOT"/profiles/*.md; do
  [ -e "$f" ] && normative+=("$f")
done
if grep -nE '\b[0-9a-f]{40}\b|\b[0-9a-f]{64}\b' "${normative[@]}"; then
  echo "FAIL: a 40- or 64-hex pin appears in normative text (above); cite a learning or issue" >&2
  fail=1
fi

if [ "$fail" -eq 0 ]; then
  n=0; for f in "$PROC"/*.md "$PROC"/*/*.md; do [ -e "$f" ] && [ "$(basename "$f")" != README.md ] && n=$((n + 1)); done
  echo "ok: core $lines lines, core plus each profile under $CORE_MAX; clients under $CLIENT_MAX; $n procedures indexed; core portable; no pins"
fi
exit "$fail"
