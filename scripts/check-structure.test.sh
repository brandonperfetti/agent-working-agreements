#!/usr/bin/env bash
#
# Regression test for check-structure.sh: a good fixture passes; each failure class fails.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture="$(mktemp -d)"
cleanup() { rm -rf -- "$fixture"; }
trap cleanup EXIT

repo="$fixture/repo"
mkdir -p "$repo/procedures" "$repo/scripts"
cp "$ROOT/scripts/check-structure.sh" "$repo/scripts/"
chmod 755 "$repo/scripts/check-structure.sh"

clause='a rule here that contradicts one there is the rule that is wrong.'

good() {
  cat >"$repo/AGENT-WORKING-AGREEMENTS.md" <<EOF
# Agreement

## Triggers

| When | Read |
| --- | --- |
| x | [\`one.md\`](procedures/one.md) |
EOF
  cat >"$repo/procedures/README.md" <<EOF
# Procedures

| Procedure |
| --- |
| [\`one.md\`](one.md) |
EOF
  cat >"$repo/procedures/one.md" <<EOF
# One

This procedure never overrides Parts A–B, and $clause

**Trigger:** x

**Owner:** y

**Implements:** A1

**Stop:** none
EOF
}

expect_pass() {
  if ! out="$(cd "$repo" && ./scripts/check-structure.sh 2>&1)"; then
    echo "FAIL: expected pass: $1"; echo "$out"; exit 1
  fi
}
expect_fail() {
  if out="$(cd "$repo" && ./scripts/check-structure.sh 2>&1)"; then
    echo "FAIL: expected failure: $1"; echo "$out"; exit 1
  fi
  grep -q "$2" <<<"$out" || { echo "FAIL: $1: message missing '$2'"; echo "$out"; exit 1; }
}

good; expect_pass "good fixture"

good; printf '%.0s\n' $(seq 1 300) >>"$repo/AGENT-WORKING-AGREEMENTS.md"
expect_fail "core over the ceiling" "ceiling"

good; sed -i.bak '/^\*\*Stop:\*\*/d' "$repo/procedures/one.md"; rm -f "$repo/procedures/one.md.bak"
expect_fail "procedure missing a field" "lacks \*\*Stop:\*\*"

good; cp "$repo/procedures/one.md" "$repo/procedures/two.md"
expect_fail "unindexed procedure" "not listed in procedures/README.md"

good; printf '| y | [`gone.md`](procedures/gone.md) |\n' >>"$repo/AGENT-WORKING-AGREEMENTS.md"
expect_fail "dangling core link" "does not exist"

good; printf 'pinned at %s\n' "$(printf 'a%.0s' $(seq 1 40))" >>"$repo/procedures/one.md"
expect_fail "40-hex pin in a procedure" "hex pin"

good; sed -i.bak '/contradicts one there/d' "$repo/procedures/one.md"; rm -f "$repo/procedures/one.md.bak"
expect_fail "procedure missing the precedence clause" "precedence clause"

good; sed -i.bak '/procedures\/one.md/d' "$repo/AGENT-WORKING-AGREEMENTS.md"; rm -f "$repo/AGENT-WORKING-AGREEMENTS.md.bak"
expect_fail "procedure absent from the Triggers table" "Triggers table"

good; CORE_MAX=2 expect_fail "ceiling honours CORE_MAX" "ceiling"

echo "ok: check-structure passes the good fixture and rejects each failure class"
