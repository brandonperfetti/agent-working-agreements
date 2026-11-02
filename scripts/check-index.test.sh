#!/usr/bin/env bash
#
# Regression test for check-index.sh: the composition contract (core → profile → client),
# the client index, the openers and the stable anchors.
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture="$(mktemp -d)"
cleanup() { rm -rf -- "$fixture"; }
trap cleanup EXIT

repo="$fixture/repo"
mkdir -p "$repo/clients" "$repo/profiles" "$repo/scripts"
cp "$ROOT/scripts/check-index.sh" "$repo/scripts/"
chmod 755 "$repo/scripts/check-index.sh"

clause='and a rule here that contradicts one there is the rule that is wrong.'
pattern='s/and a rule\s+here that contradicts one there is the rule that is wrong\.'
pattern+='/and conflicts are resolved elsewhere./'

good() {
  rm -f "$repo/clients"/*.md "$repo/profiles"/*.md
  {
    printf '# Agreement\n\nRead the core, then any profile and adapter named.\n\n## Composition\n\n'
    printf 'Adapter openers name every layer they depend on.\n\n'
    printf '# Part A\n\n'
    for a in A1 A2 A3 A4 A5 A6 A7 A8; do printf '## %s. Rule\n\nText.\n\n' "$a"; done
    printf '# Part B\n\n'
    for b in B0 B1 B2; do printf '## %s. Mode\n\nText.\n\n' "$b"; done
  } >"$repo/AGENT-WORKING-AGREEMENTS.md"

  cat >"$repo/profiles/studio.md" <<EOF
# Studio profile

Read AGENT-WORKING-AGREEMENTS.md first, $clause

## Client adapters (read only yours)

| You are | Read |
| --- | --- |
| With | [\`clients/with-sections.md\`](../clients/with-sections.md) |
| Without | [\`clients/without-sections.md\`](../clients/without-sections.md) |

## Notes

Other profile text.
EOF

  cat >"$repo/clients/with-sections.md" <<EOF
# Client with sections

Read AGENT-WORKING-AGREEMENTS.md, [the profile](../profiles/studio.md), then
clients/with-sections.md, $clause

## Later section

Client mechanics.
EOF

  cat >"$repo/clients/without-sections.md" <<EOF
# Client without sections

Read AGENT-WORKING-AGREEMENTS.md, ../profiles/studio.md and clients/without-sections.md
first, and a rule
here that contradicts one there is the rule that is wrong.

Client mechanics without subheadings.
EOF

  cat >"$repo/AGENTS.md" <<EOF
# Repository instructions

Read AGENT-WORKING-AGREEMENTS.md, then profiles/studio.md, first, $clause

Repository rules without subheadings.
EOF
}

expect_pass() {
  local out
  if ! out="$("$repo/scripts/check-index.sh" 2>&1)"; then
    echo "FAIL: expected pass: $1" >&2; printf '%s\n' "$out" >&2; exit 1
  fi
}

expect_fail() {
  local out status
  set +e
  out="$("$repo/scripts/check-index.sh" 2>&1)"
  status=$?
  set -e
  if [ "$status" -eq 0 ]; then
    echo "FAIL: expected failure: $1" >&2; printf '%s\n' "$out" >&2; exit 1
  fi
  grep -qxF "$2" <<<"$out" || {
    echo "FAIL: $1: expected line missing: $2" >&2; printf '%s\n' "$out" >&2; exit 1; }
}

good; expect_pass "good fixture"

good; perl -0pi -e 's/and a rule\n/and a rule \n/' "$repo/clients/without-sections.md"
expect_pass "wrapped clause with trailing whitespace"

for target in with-sections.md without-sections.md; do
  good; perl -0pi -e "$pattern" "$repo/clients/$target"; printf '\n%s\n' "$clause" >>"$repo/clients/$target"
  expect_fail "$target clause outside its opener" "FAIL: $target opener is missing: $clause"

  good; perl -0pi -e 's/AGENT-WORKING-AGREEMENTS\.md/root agreement/' "$repo/clients/$target"
  printf '\nRead AGENT-WORKING-AGREEMENTS.md later.\n' >>"$repo/clients/$target"
  expect_fail "$target agreement pointer outside its opener" \
    "FAIL: $target opener does not point back at Parts A and B"

  good; perl -0pi -e 's#\.\./profiles/studio\.md#the profile#' "$repo/clients/$target"
  printf '\nRead ../profiles/studio.md later.\n' >>"$repo/clients/$target"
  expect_fail "$target profile pointer outside its opener" \
    "FAIL: $target opener does not name its profile"

  good; perl -0pi -e "s#clients/\Q$target\E#this file#" "$repo/clients/$target"
  printf '\nThis is clients/%s.\n' "$target" >>"$repo/clients/$target"
  expect_fail "$target own-file pointer outside its opener" \
    "FAIL: $target opener does not name its own file"
done

good; perl -0pi -e "$pattern" "$repo/AGENTS.md"; printf '\n%s\n' "$clause" >>"$repo/AGENTS.md"
expect_fail "AGENTS.md clause outside its opener" "FAIL: AGENTS.md opener is missing: $clause"

good; perl -0pi -e 's#, then profiles/studio\.md,#,#' "$repo/AGENTS.md"
expect_fail "AGENTS.md opener without its profile" "FAIL: AGENTS.md opener does not name its profile"

good; perl -0pi -e "$pattern" "$repo/profiles/studio.md"
expect_fail "profile opener drift" "FAIL: profiles/studio.md opener is missing: $clause"

good; perl -0pi -e 's#studio\.md\)#gone.md)#' "$repo/clients/with-sections.md"
expect_fail "client names a missing profile" \
  "FAIL: with-sections.md opener names profiles/gone.md, which does not exist"

good; printf 'Studio callers read [the profile](profiles/studio.md).\n' \
  >>"$repo/AGENT-WORKING-AGREEMENTS.md"
expect_fail "core names a profile" \
  "FAIL: the core names a profile file (above); adapter openers bind profiles"

unindexed="FAIL: clients/without-sections.md exists but no profile's client index points at it"
drop_row='s#^\| Without \|.*\n##m'

good; perl -0pi -e "$drop_row" "$repo/profiles/studio.md"
expect_fail "client missing from the profile's index" "$unindexed"

good; perl -0pi -e "$drop_row" "$repo/profiles/studio.md"
printf 'Prose naming [it](../clients/without-sections.md).\n' >>"$repo/profiles/studio.md"
expect_fail "client linked only in profile prose" "$unindexed"

good; perl -0pi -e "$drop_row" "$repo/profiles/studio.md"
printf '\n| Other | [x](../clients/without-sections.md) |\n' >>"$repo/profiles/studio.md"
expect_fail "client linked only in another section's table" "$unindexed"

good; perl -0pi -e "$drop_row" "$repo/profiles/studio.md"
perl -0pi -e 's{\n## Notes}{\nRetired:\n\n| You were | Read |\n| --- | --- |\n| Without | [x](../clients/without-sections.md) |\n\n## Notes}' \
  "$repo/profiles/studio.md"
expect_fail "client linked only in another table of the Client adapters section" "$unindexed"

good; perl -0pi -e "$drop_row" "$repo/profiles/studio.md"
perl -0pi -e 's{\n## Notes}{\n| Without | [x](../clients/without-sections.md) |\n\n## Notes}' \
  "$repo/profiles/studio.md"
expect_fail "client in a pipe line after the index table ends" "$unindexed"

good; perl -0pi -e 's{(## Client adapters \(read only yours\)\n)}{$1\n| Note |\n| --- |\n| a table before the index |\n}' \
  "$repo/profiles/studio.md"
expect_pass "another table before the client index"

good; perl -0pi -e "$drop_row" "$repo/profiles/studio.md"
perl -0pi -e 's#(Read AGENT-WORKING-AGREEMENTS\.md first)#$1, see clients/without-sections.md#' \
  "$repo/profiles/studio.md"
expect_fail "client linked only in the profile opener" "$unindexed"

good; perl -0pi -e 's#(\| Without \|.*\n)#$1| Gone | [`clients/gone.md`](../clients/gone.md) |\n#' \
  "$repo/profiles/studio.md"
expect_fail "profile index names a missing client" \
  "FAIL: a profile's client index references clients/gone.md, which does not exist"

good; printf 'A retired [`clients/gone.md`](../clients/gone.md).\n' >>"$repo/profiles/studio.md"
expect_pass "a missing client named outside the index is no index row"

good; perl -0pi -e 's/^## B1\. /## B9. /m' "$repo/AGENT-WORKING-AGREEMENTS.md"
expect_fail "stable anchor renamed" "FAIL: stable anchor B1 missing from the core"

echo "ok: check-index proves core → profile → client composition and rejects each drift class"
