#!/usr/bin/env bash
#
# The OpenClaw runbook harness (#191): drives scripts/openclaw/runbook.sh through every stop and
# retention branch of procedures/openclaw/managed-worktrees.md it models, on disposable
# repositories under one temporary directory and a stub `openclaw`. Nothing here reads or writes a
# live checkout, OpenClaw state directory, configuration or Gateway: the host's git configuration
# is replaced for the run, and the only `openclaw` is the stub below.
#
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNBOOK="$ROOT/scripts/openclaw/runbook.sh"
fixture="$(cd "$(mktemp -d)" && pwd -P)"
cleanup_fixture() { rm -rf -- "$fixture"; }
trap cleanup_fixture EXIT

REAL_GIT="$(command -v git)"
export REAL_GIT
# The host's git configuration and hooks stay out of the fixtures.
printf '[user]\n\tname = Fixture\n\temail = fixture@example.com\n[init]\n\tdefaultBranch = master\n' \
  >"$fixture/gitconfig"
export GIT_CONFIG_GLOBAL="$fixture/gitconfig" GIT_CONFIG_NOSYSTEM=1
unset GIT_DIR GIT_COMMON_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES \
  GIT_CONFIG GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS OPENCLAW_STATE_DIR OPENCLAW_CONFIG_PATH OPENCLAW_HOME
export OPENCLAW_PROFILE=ambient  # the probing shell's profile, which no bound invocation may inherit

mkdir -p "$fixture/bin" "$fixture/shim"
cat >"$fixture/bin/openclaw" <<'EOF'
#!/bin/sh
# Stub openclaw: records argv and the Gateway values, answers from $STUB_DIR, refuses a CLI profile.
log=$STUB_DIR/calls
printf 'argv:' >>"$log"
for word in "$@"; do printf ' [%s]' "$word" >>"$log"; done
printf '\nenv: STATE=%s CONFIG=%s PROFILE=%s\n' "${OPENCLAW_STATE_DIR-<unset>}" \
  "${OPENCLAW_CONFIG_PATH-<unset>}" "${OPENCLAW_PROFILE-<unset>}" >>"$log"
for word in "$@"; do
  case $word in --profile* | --dev) echo "stub: refused $word" >&2; exit 64 ;; esac
done
[ "$1" = worktrees ] || exit 64
case $2 in
  list)
    [ -f "$STUB_DIR/list.exit" ] && exit "$(cat "$STUB_DIR/list.exit")"
    cat "$STUB_DIR/list.json" ;;
  remove)
    [ -f "$STUB_DIR/remove.sh" ] && sh "$STUB_DIR/remove.sh"
    cat "$STUB_DIR/remove.json" ;;
  *) exit 64 ;;
esac
EOF
# A git shim, on PATH only where a case asks: a remote that moves between the fetch and ls-remote,
# an inventory real git would not print, and a removal git refuses.
cat >"$fixture/shim/git" <<'EOF'
#!/bin/sh
case " $* " in
  *" ls-remote "*)
    [ -n "${SHIM_ADVANCE:-}" ] && SHIM_ADVANCE='' sh "$SHIM_ADVANCE" ;;
  *" worktree list --porcelain "*)
    count=$(cat "$SHIM_STATE/lists" 2>/dev/null || echo 0); count=$((count + 1))
    echo "$count" >"$SHIM_STATE/lists"
    if [ -n "${SHIM_PORCELAIN:-}" ]; then cat "$SHIM_PORCELAIN"; exit 0; fi
    if [ "$count" -ge 2 ] && [ -n "${SHIM_PORCELAIN_SECOND:-}" ]; then cat "$SHIM_PORCELAIN_SECOND"; exit 0; fi ;;
  *" worktree remove "*)
    [ -n "${SHIM_REMOVE_FAIL:-}" ] && { echo "fatal: refused by the test shim" >&2; exit 1; } ;;
esac
exec "$REAL_GIT" "$@"
EOF
chmod 755 "$fixture/bin/openclaw" "$fixture/shim/git"

fail=0
cases=0
out="$fixture/stdout"
err="$fixture/stderr"

# Run the runbook command; keep its exit status, stdout and stderr.
run() {
  "$RUNBOOK" "$@" >"$out" 2>"$err"
  code=$?
}

report() {
  cases=$((cases + 1))
  if [ "$1" = ok ]; then
    echo "ok: $2"
  else
    echo "FAIL: $2: $3" >&2
    sed 's/^/  stderr: /' "$err" >&2
    sed 's/^/  stdout: /' "$out" >&2
    fail=1
  fi
}

# expect <exit> <stderr text, or ''> <label> -- <runbook args>
expect() {
  local want=$1 text=$2 label=$3
  shift 4
  run "$@"
  if [ "$code" != "$want" ]; then
    report fail "$label" "exit $code, wanted $want"
  elif [ -n "$text" ] && ! grep -qF -- "$text" "$err"; then
    report fail "$label" "stderr lacks '$text'"
  else
    report ok "$label"
  fi
}

# holds <label> <test command...>: a follow-up assertion on the state a case left.
holds() {
  local label=$1
  shift
  if "$@"; then report ok "$label"; else report fail "$label" "does not hold"; fi
}

g() { "$REAL_GIT" "$@"; }

# One remote with develop and master, a seed clone to move it, and the protected root on master.
new_fixture() {
  base="$fixture/$1"
  mkdir -p "$base/stub" "$base/managed" "$base/state" "$base/_agent" "$base/shimstate"
  g init -q --bare "$base/origin.git"
  g clone -q "$base/origin.git" "$base/seed" 2>/dev/null
  g -C "$base/seed" commit -q --allow-empty -m init
  g -C "$base/seed" push -q origin master
  g -C "$base/seed" push -q origin master:develop
  g clone -q "$base/origin.git" "$base/root"
  printf '{"worktrees": []}\n' >"$base/stub/list.json"
  export STUB_DIR="$base/stub" SHIM_STATE="$base/shimstate"
}

# Move a branch of the remote by one commit, from the seed clone.
advance() {
  g -C "$base/seed" fetch -q origin "$1"
  g -C "$base/seed" checkout -q -B "$1" "origin/$1"
  g -C "$base/seed" commit -q --allow-empty -m "advance $1"
  g -C "$base/seed" push -q origin "$1"
}

# A delivery worktree on feature/x whose commit is merged into origin/develop.
delivery() {
  local path=$1
  shift
  g -C "$base/root" fetch -q origin
  g -C "$base/root" worktree add -q "$@" -b feature/x "$path" origin/develop 2>/dev/null
  g -C "$path" commit -q --allow-empty -m "feature x"
  g -C "$path" push -q origin HEAD:develop
}

cleanup_args() {
  args=(cleanup --repo "$base/root" --branch feature/x --protected-root "$base/root"
    --managed-root "$base/managed" --openclaw "$fixture/bin/openclaw" --state-dir "$base/state"
    --config-path "$base/state/openclaw.json" --no-profile)
}

has_branch() { g -C "$base/root" show-ref --verify -q "refs/heads/$1"; }
no_branch() { ! has_branch "$1"; }

# --- Named base capture and the created HEAD ---------------------------------------------------

new_fixture capture
stale=$(g -C "$base/root" rev-parse origin/develop)
advance develop
fresh=$(g -C "$base/seed" rev-parse HEAD)
expect 0 '' "capture: the named fetch makes a stale origin/develop current" -- capture-base "$base/root"
holds "capture: the captured base is the remote's develop, not the stale one" \
  grep -qx "base $fresh" "$out"
holds "capture: the stale ref differed before the fetch" test "$stale" != "$fresh"
holds "capture: each head's rev-parse and ls-remote are recorded as equal" \
  test "$(grep -c ', equal$' "$out")" -eq 2

g -C "$base/root" remote set-url origin "$base/missing.git"
expect 3 'named fetch failed' "capture: a failed fetch stops" -- capture-base "$base/root"
g -C "$base/root" remote set-url origin "$base/origin.git"

cat >"$base/advance.sh" <<EOF
"\$REAL_GIT" -C "$base/seed" commit -q --allow-empty -m race
"\$REAL_GIT" -C "$base/seed" push -q origin HEAD:develop
EOF
PATH="$fixture/shim:$PATH" SHIM_ADVANCE="$base/advance.sh" \
  expect 3 'on the remote; create no worktree' "capture: a remote that moved after the fetch stops" \
  -- capture-base "$base/root"

base_oid=$(g -C "$base/root" rev-parse origin/develop)
g -C "$base/root" worktree add -q --detach "$base/created" "$base_oid"
expect 0 '' "verify-head: a created HEAD equal to the base passes" -- verify-head "$base/created" "$base_oid"
expect 3 'retain and report the worktree, its HEAD and the base' "verify-head: a created HEAD mismatch stops" \
  -- verify-head "$base/created" "$(g -C "$base/root" rev-parse origin/master)"

# --- Overlap with the artifact store and the protected root ------------------------------------

new_fixture overlap
mkdir -p "$base/_agent/inside" "$base/elsewhere"
ln -s "$base/_agent" "$base/link"
overlap_args=(check-overlap --agent-store "$base/_agent" --protected-root "$base/root")
expect 0 '' "overlap: a root apart from the store and the protected root passes" \
  -- "${overlap_args[@]}" "$base/managed" "$base/elsewhere"
expect 3 'overlaps the artifact store' "overlap: a path inside the store stops" -- "${overlap_args[@]}" "$base/_agent/inside"
expect 3 'overlaps the artifact store' "overlap: a root containing the protected root stops" -- "${overlap_args[@]}" "$base"
expect 3 'overlaps the artifact store' "overlap: a symlink into the store stops" -- "${overlap_args[@]}" "$base/link/inside"
expect 3 'cannot be canonicalized' "overlap: a path that cannot be canonicalized stops" -- "${overlap_args[@]}" "$base/nowhere"
expect 3 'overlaps the artifact store' "overlap: the filesystem root contains both and stops" -- "${overlap_args[@]}" /
expect 2 '' "overlap: no store or root named is a usage error" -- check-overlap "$base/managed"
expect 2 '' "overlap: an option with no value is a usage error, not a loop" -- check-overlap --agent-store

# --- The protected root's release refresh -----------------------------------------------------

new_fixture refresh
advance master
expect 0 '' "refresh: a clean root fast-forwards to origin/master" -- refresh-root "$base/root"
holds "refresh: the root serves the remote's master" \
  grep -qx "serves $(g -C "$base/seed" rev-parse HEAD)" "$out"

new_fixture refresh-shadow
advance master
g -C "$base/root" branch -q origin/master master  # a local branch named like the remote-tracking ref
expect 0 '' "refresh: a local branch named origin/master does not shadow the remote-tracking ref" \
  -- refresh-root "$base/root"
holds "refresh: the shadowed root still serves the remote's master" \
  grep -qx "serves $(g -C "$base/seed" rev-parse HEAD)" "$out"

new_fixture refresh-selector
advance master
g init -q "$base/other"
g -C "$base/other" commit -q --allow-empty -m other
other_head=$(g -C "$base/other" rev-parse HEAD)
GIT_DIR="$base/other/.git" GIT_WORK_TREE="$base/other" \
  expect 0 '' "refresh: an inherited GIT_DIR does not redirect the refresh" -- refresh-root "$base/root"
holds "refresh: the named root, not the inherited repository, serves the remote's master" \
  grep -qx "serves $(g -C "$base/seed" rev-parse HEAD)" "$out"
holds "refresh: the inherited repository is untouched" test "$(g -C "$base/other" rev-parse HEAD)" = "$other_head"

new_fixture refresh-dirty
g -C "$base/root" switch -q develop
touch "$base/root/stray"
expect 3 'not clean; run no later step' "refresh: an untracked file stops before the switch" -- refresh-root "$base/root"
holds "refresh: no switch ran after the dirty status" test "$(g -C "$base/root" branch --show-current)" = develop

new_fixture refresh-fetch
advance master
before=$(g -C "$base/root" rev-parse HEAD)
g -C "$base/root" remote set-url origin "$base/missing.git"
expect 3 'named fetch of master failed' "refresh: a failed fetch stops" -- refresh-root "$base/root"
holds "refresh: no merge ran after the failed fetch" test "$(g -C "$base/root" rev-parse HEAD)" = "$before"

new_fixture refresh-switch
g -C "$base/root" switch -q develop
g -C "$base/root" branch -q -D master
g -C "$base/root" update-ref -d refs/remotes/origin/master
expect 3 'git switch master failed' "refresh: a failed switch stops" -- refresh-root "$base/root"
holds "refresh: no fetch ran after the failed switch" \
  test -z "$(g -C "$base/root" for-each-ref refs/remotes/origin/master)"

new_fixture refresh-diverged
advance master
g -C "$base/root" commit -q --allow-empty -m "local only"
expect 3 'fast-forward failed' "refresh: a diverged master stops at the fast-forward" -- refresh-root "$base/root"

new_fixture refresh-ahead
g -C "$base/root" commit -q --allow-empty -m "local only"
expect 3 'not origin/master' "refresh: a master ahead of origin/master stops at the HEAD check" -- refresh-root "$base/root"

new_fixture refresh-after
advance master
mkdir -p "$base/hooks"
printf '#!/bin/sh\ntouch stray\n' >"$base/hooks/post-merge"
chmod 755 "$base/hooks/post-merge"
g -C "$base/root" config core.hooksPath "$base/hooks"
expect 3 'not clean after the fast-forward' "refresh: a tree dirty after the fast-forward stops" -- refresh-root "$base/root"

# --- Post-merge cleanup: the routes ------------------------------------------------------------

new_fixture plain
delivery "$base/wt-x"
cleanup_args
mkdir -p "$base/tmp"
TMPDIR="$base/tmp" expect 0 '' "cleanup: a clean, merged plain worktree is removed" -- "${args[@]}"
holds "cleanup: a successful cleanup leaves no scratch directory" test -z "$(ls -A "$base/tmp")"
holds "cleanup: the plain worktree is gone" test ! -e "$base/wt-x"
holds "cleanup: its branch is deleted" no_branch feature/x
holds "cleanup: the inventory query ran bound, with the profile unset" \
  grep -qxF "env: STATE=$base/state CONFIG=$base/state/openclaw.json PROFILE=<unset>" "$STUB_DIR/calls"
holds "cleanup: the inventory query is list --json, with no --profile or --dev" \
  grep -qxF 'argv: [worktrees] [list] [--json]' "$STUB_DIR/calls"

new_fixture managed
delivery "$base/managed/fp/x"
ln -s "$base/managed" "$base/managed-link"
printf '{"worktrees": [{"id": "wt-1", "path": "%s", "branch": "feature/x"}]}\n' \
  "$base/managed-link/fp/x" >"$STUB_DIR/list.json"
printf '"$REAL_GIT" -C "%s" worktree remove "%s"\n' "$base/root" "$base/managed/fp/x" >"$STUB_DIR/remove.sh"
printf '{"removed": true, "cleanup": "lossless"}\n' >"$STUB_DIR/remove.json"
cleanup_args
args[${#args[@]} - 1]=--profile
args+=(fleet)
expect 0 '' "cleanup: a managed worktree is matched by canonical path and removed losslessly" -- "${args[@]}"
holds "cleanup: the managed removal is remove <id> --if-lossless --json" \
  grep -qxF 'argv: [worktrees] [remove] [wt-1] [--if-lossless] [--json]' "$STUB_DIR/calls"
holds "cleanup: every openclaw call carried the bound profile" \
  test "$(grep -c "PROFILE=fleet$" "$STUB_DIR/calls")" -eq 2
holds "cleanup: the managed worktree's branch is deleted" no_branch feature/x

new_fixture managed-kept
delivery "$base/managed/fp/x"
printf '{"worktrees": [{"id": "wt-1", "path": "%s", "branch": "feature/x"}]}\n' \
  "$base/managed/fp/x" >"$STUB_DIR/list.json"
printf '{"removed": false, "cleanup": "retained: unpublished commits"}\n' >"$STUB_DIR/remove.json"
cleanup_args
expect 4 'retained: unpublished commits' "cleanup: removed false is a retention, reported" -- "${args[@]}"
holds "cleanup: the retained worktree is still there" test -d "$base/managed/fp/x"
holds "cleanup: the retained worktree keeps its branch" has_branch feature/x
printf 'not json\n' >"$STUB_DIR/remove.json"
expect 3 'cannot be read' "cleanup: an unreadable removal result stops" -- "${args[@]}"

new_fixture inventory
delivery "$base/wt-x"
cleanup_args
echo 1 >"$STUB_DIR/list.exit"
expect 3 'openclaw worktrees list cannot be read' "cleanup: a failed inventory query stops" -- "${args[@]}"
rm "$STUB_DIR/list.exit"
printf '{"worktrees": \n' >"$STUB_DIR/list.json"
expect 3 'openclaw inventory cannot be read' "cleanup: an unparseable inventory stops" -- "${args[@]}"
printf '{"worktrees": [{"id": "a", "branch": "feature/x"}]}\n' >"$STUB_DIR/list.json"
expect 3 'openclaw inventory cannot be read' "cleanup: a record whose path cannot be determined stops" -- "${args[@]}"
printf '{"worktrees": [{"id": "a", "path": "%s", "branch": "feature/other"}]}\n' "$base/wt-x" >"$STUB_DIR/list.json"
expect 3 'not feature/x' "cleanup: a record at the path on another branch stops" -- "${args[@]}"
printf '{"worktrees": [{"id": "a", "path": "%s", "branch": "feature/x"}, {"id": "b", "path": "%s/", "branch": "feature/x"}]}\n' \
  "$base/wt-x" "$base/wt-x" >"$STUB_DIR/list.json"
expect 3 'openclaw records name' "cleanup: two records at one canonical path stop" -- "${args[@]}"
printf '{"worktrees": [{"id": "a", "path": "%s", "branch": "feature/x"}]}\n' "$base/gone" >"$STUB_DIR/list.json"
expect 3 'cannot be matched' "cleanup: an absent record on the same branch stops" -- "${args[@]}"
mkdir -p "$base/locked-out"
chmod 000 "$base/locked-out"
printf '{"worktrees": [{"id": "a", "path": "%s/x", "branch": "feature/old"}]}\n' "$base/locked-out" >"$STUB_DIR/list.json"
if [ "$(id -u)" -ne 0 ]; then
  expect 3 'cannot be matched' "cleanup: a record whose existence cannot be read stops" -- "${args[@]}"
fi
chmod 755 "$base/locked-out"
printf '{"worktrees": [{"id": "a", "path": "%s", "branch": "feature/old"}]}\n' "$base/gone" >"$STUB_DIR/list.json"
expect 0 '' "cleanup: an absent record on another branch is skipped" -- "${args[@]}"
holds "cleanup: the skip led to the plain route" test ! -e "$base/wt-x"

new_fixture unrecorded
delivery "$base/managed/fp/x"
cleanup_args
expect 3 'in the managed worktree root with no openclaw record' \
  "cleanup: an unrecorded worktree inside the managed root stops" -- "${args[@]}"
holds "cleanup: the unrecorded worktree is retained" test -d "$base/managed/fp/x"

# --- Post-merge cleanup: eligibility ------------------------------------------------------------

new_fixture dirty
delivery "$base/wt-x"
cleanup_args
touch "$base/wt-x/untracked"
expect 3 'untracked or ignored files' "cleanup: an untracked file stops" -- "${args[@]}"
rm "$base/wt-x/untracked"
mkdir -p "$base/root/.git/info"
printf '*.log\n' >>"$base/root/.git/info/exclude"  # the common directory's exclude covers every worktree
touch "$base/wt-x/build.log"
holds "cleanup: the ignored file alone leaves a plain status empty" \
  test -z "$(g -C "$base/wt-x" status --porcelain --untracked-files=all)"
expect 3 'untracked or ignored files' "cleanup: an ignored file stops" -- "${args[@]}"
holds "cleanup: the worktree with ignored content is retained" test -e "$base/wt-x/build.log"
holds "cleanup: no inventory query ran for a dirty worktree" test ! -e "$STUB_DIR/calls"

new_fixture ancestry
delivery "$base/wt-x"
g -C "$base/wt-x" commit -q --allow-empty -m "not merged"
cleanup_args
expect 3 'not an ancestor of origin/develop' "cleanup: a branch not merged into develop stops" -- "${args[@]}"

new_fixture matches
delivery "$base/wt-x"
g -C "$base/root" branch -q feature/y origin/develop
cleanup_args
args[4]=feature/y
expect 3 '0 worktrees have feature/y' "cleanup: a branch no worktree has checked out stops" -- "${args[@]}"
g -C "$base/root" worktree add -q -f "$base/wt-x2" feature/x 2>/dev/null
cleanup_args
expect 3 '2 worktrees have feature/x' "cleanup: a branch checked out twice stops" -- "${args[@]}"

new_fixture canonical
delivery "$base/wt-x"
rm -rf "$base/wt-x"
cleanup_args
expect 3 'cannot be canonicalized' "cleanup: a worktree path that cannot be canonicalized stops" -- "${args[@]}"

new_fixture protected
delivery "$base/wt-x"
cleanup_args
args[6]="$base/wt-x"
expect 3 'protected instruction-source root' "cleanup: the named protected root is never eligible" -- "${args[@]}"
g -C "$base/root" worktree lock --reason 'protected base worktree' "$base/wt-x"
cleanup_args
expect 3 'protected worktree (locked)' "cleanup: a locked worktree is retained" -- "${args[@]}"
g -C "$base/root" worktree unlock "$base/wt-x"
g -C "$base/root" worktree add -q "$base/wt-dev" develop 2>/dev/null
cleanup_args
args[4]=develop
expect 3 'protected worktree (base branch)' "cleanup: a worktree on develop is retained" -- "${args[@]}"
mkdir -p "$base/elsewhere"
cleanup_args
args[2]="$base/wt-x"
args[4]=master
args[6]="$base/elsewhere"
expect 3 'protected worktree (first record)' "cleanup: the main working tree is retained" -- "${args[@]}"
holds "cleanup: the protected worktrees all remain" test -d "$base/root" -a -d "$base/wt-x" -a -d "$base/wt-dev"
cleanup_args
args[2]="$base/wt-x"
expect 3 'from another worktree' "cleanup: a cleanup run from the worktree it removes stops" -- "${args[@]}"

new_fixture indeterminate
delivery "$base/wt-x"
cleanup_args
printf 'worktree %s\nHEAD 0\nbranch refs/heads/master\n\nworktree %s\nHEAD 0\nbranch refs/heads/feature/x\n\nworktree %s\nHEAD 0\n\n' \
  "$base/root" "$base/wt-x" "$base/odd" >"$base/porcelain"
PATH="$fixture/shim:$PATH" SHIM_PORCELAIN="$base/porcelain" \
  expect 3 'neither a branch nor a detached line' "cleanup: an unclassified inventory record stops" -- "${args[@]}"
printf 'worktree %s\nHEAD 0\nbranch refs/heads/master\n\nworktree %s\nHEAD 0\nbranch refs/heads/feature/x\n\nHEAD 0\nbranch refs/heads/z\n\n' \
  "$base/root" "$base/wt-x" >"$base/porcelain"
PATH="$fixture/shim:$PATH" SHIM_PORCELAIN="$base/porcelain" \
  expect 3 'no worktree line' "cleanup: an inventory record with no worktree line stops" -- "${args[@]}"
g -C "$base/root" worktree list --porcelain | sed 's|refs/heads/feature/x|refs/heads/feature/swapped|' >"$base/porcelain"
rm -f "$SHIM_STATE/lists"
PATH="$fixture/shim:$PATH" SHIM_PORCELAIN_SECOND="$base/porcelain" \
  expect 3 'second inventory' "cleanup: a second inventory that changed stops before removal" -- "${args[@]}"
holds "cleanup: the worktree survives the changed inventory" test -d "$base/wt-x"
rm -f "$SHIM_STATE/lists"
PATH="$fixture/shim:$PATH" SHIM_REMOVE_FAIL=1 \
  expect 4 'git refused to remove' "cleanup: a refused plain removal is a retention" -- "${args[@]}"
holds "cleanup: a refused removal keeps the branch" has_branch feature/x

new_fixture branch-kept
delivery "$base/wt-x" --no-track
cleanup_args
expect 4 'git refused to delete feature/x' "cleanup: a refused branch -d is a retention, never forced" -- "${args[@]}"
holds "cleanup: the worktree is removed before the refused branch delete" test ! -e "$base/wt-x"
holds "cleanup: the refused branch stays" has_branch feature/x

new_fixture fetch
delivery "$base/wt-x"
g -C "$base/root" remote set-url origin "$base/missing.git"
cleanup_args
expect 3 'named fetch of develop failed' "cleanup: a failed fetch stops" -- "${args[@]}"

new_fixture usage
delivery "$base/wt-x"
expect 2 '' "cleanup: no openclaw command named is a usage error" -- cleanup --repo "$base/root" --branch feature/x \
  --protected-root "$base/root" --managed-root "$base/managed" --state-dir "$base/state" \
  --config-path "$base/state/openclaw.json" --no-profile
expect 2 '' "cleanup: no profile binding is a usage error" -- cleanup --repo "$base/root" --branch feature/x \
  --protected-root "$base/root" --managed-root "$base/managed" --openclaw "$fixture/bin/openclaw" \
  --state-dir "$base/state" --config-path "$base/state/openclaw.json"
holds "cleanup: a usage error touches nothing" test -d "$base/wt-x" -a ! -e "$STUB_DIR/calls"

if [ "$fail" -ne 0 ]; then
  echo "FAIL: the OpenClaw runbook harness" >&2
  exit 1
fi
echo "ok: $cases runbook cases"
