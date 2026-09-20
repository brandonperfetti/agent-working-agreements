#!/usr/bin/env bash
#
# Regression test for the client-opener precedence check.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture="$(mktemp -d)"
cleanup() { rm -rf -- "$fixture"; }
trap cleanup EXIT

repo="$fixture/repo"
mkdir -p "$repo/clients" "$repo/scripts"
cp "$ROOT/AGENT-WORKING-AGREEMENTS.md" "$repo/"
cp "$ROOT"/clients/*.md "$repo/clients/"
cp "$ROOT/scripts/check-index.sh" "$repo/scripts/"
chmod 755 "$repo/scripts/check-index.sh"

"$repo/scripts/check-index.sh" >/dev/null

clause='and a rule here that contradicts one there is the rule that is wrong.'
pattern='s/and a rule\s+here that contradicts one there is the rule that is wrong\.'
pattern+='/and conflicts are resolved elsewhere./'
perl -0pi -e "$pattern" "$repo/clients/openclaw.md"
printf '\n%s\n' "$clause" >>"$repo/clients/openclaw.md"

set +e
output="$("$repo/scripts/check-index.sh" 2>&1)"
status=$?
set -e

if [ "$status" -eq 0 ]; then
  echo "FAIL: check-index accepted a client whose opener lacks the clause" >&2
  exit 1
fi

expected="FAIL: openclaw.md opener is missing: $clause"
if ! grep -qxF "$expected" <<<"$output"; then
  echo "FAIL: unexpected check-index output" >&2
  printf '%s\n' "$output" >&2
  exit 1
fi

echo "ok: check-index rejects a missing opener precedence clause"
