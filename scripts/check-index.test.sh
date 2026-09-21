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
cp "$ROOT/scripts/check-index.sh" "$repo/scripts/"
chmod 755 "$repo/scripts/check-index.sh"

clause='and a rule here that contradicts one there is the rule that is wrong.'
pattern='s/and a rule\s+here that contradicts one there is the rule that is wrong\.'
pattern+='/and conflicts are resolved elsewhere./'

cat >"$repo/AGENT-WORKING-AGREEMENTS.md" <<'EOF'
# Part A

Portable rules.

# Part B

Mode rules.

- `clients/with-sections.md`
- `clients/without-sections.md`
EOF

write_clients() {
  cat >"$repo/clients/with-sections.md" <<EOF
# Client with sections

Read AGENT-WORKING-AGREEMENTS.md first, $clause

## Later section

Client mechanics.
EOF

  cat >"$repo/clients/without-sections.md" <<EOF
# Client without sections

Read AGENT-WORKING-AGREEMENTS.md first, and a rule
here that contradicts one there is the rule that is wrong.

Client mechanics without subheadings.
EOF
}

assert_opener_drift_rejected() {
  local target="$1"
  local output status

  write_clients
  perl -0pi -e "$pattern" "$repo/clients/$target"
  printf '\n%s\n' "$clause" >>"$repo/clients/$target"

  set +e
  output="$("$repo/scripts/check-index.sh" 2>&1)"
  status=$?
  set -e

  if [ "$status" -eq 0 ]; then
    echo "FAIL: check-index accepted $target with clause outside its opener" >&2
    exit 1
  fi

  expected="FAIL: $target opener is missing: $clause"
  if ! grep -qxF "$expected" <<<"$output"; then
    echo "FAIL: unexpected check-index output for $target" >&2
    printf '%s\n' "$output" >&2
    exit 1
  fi
}

assert_pointer_drift_rejected() {
  local target="$1"
  local output status

  write_clients
  perl -0pi -e 's/AGENT-WORKING-AGREEMENTS\.md/root agreement/' "$repo/clients/$target"
  printf '\nRead AGENT-WORKING-AGREEMENTS.md later.\n' >>"$repo/clients/$target"

  set +e
  output="$("$repo/scripts/check-index.sh" 2>&1)"
  status=$?
  set -e

  if [ "$status" -eq 0 ]; then
    echo "FAIL: check-index accepted $target with the agreement pointer outside its opener" >&2
    exit 1
  fi

  expected="FAIL: $target opener does not point back at Parts A and B"
  if ! grep -qxF "$expected" <<<"$output"; then
    echo "FAIL: unexpected check-index output for $target" >&2
    printf '%s\n' "$output" >&2
    exit 1
  fi
}

assert_wrapped_clause_with_trailing_space_accepted() {
  local output

  write_clients
  perl -0pi -e 's/and a rule\n/and a rule \n/' "$repo/clients/without-sections.md"
  if ! output="$("$repo/scripts/check-index.sh" 2>&1)"; then
    echo "FAIL: check-index rejected a wrapped clause with trailing whitespace" >&2
    printf '%s\n' "$output" >&2
    exit 1
  fi
}

write_clients
"$repo/scripts/check-index.sh" >/dev/null
assert_wrapped_clause_with_trailing_space_accepted
assert_opener_drift_rejected with-sections.md
assert_opener_drift_rejected without-sections.md
assert_pointer_drift_rejected with-sections.md
assert_pointer_drift_rejected without-sections.md

echo "ok: check-index rejects pointer and precedence drift and accepts wrapped clauses"
