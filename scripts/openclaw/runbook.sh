#!/usr/bin/env bash
#
# The decisions of procedures/openclaw/managed-worktrees.md, as commands a test can drive (#191):
# the named base capture, the created worktree's HEAD check, the path-overlap check, the protected
# root's release refresh and the post-merge cleanup route. The procedure is the authority; this
# file proves its stop and retention branches against fixture repositories and a stub `openclaw`.
#
# Each command acts only on the paths, repositories and `openclaw` command named in its arguments.
# None has a default that reaches a live checkout, state directory, configuration or Gateway: the
# cleanup refuses to run without --openclaw, --state-dir, --config-path and a profile binding.
# Resolving the Gateway service's own state directory, config and worktree root is not modelled;
# the cleanup takes the resolved values.
#
# Exit status: 0 done; 2 usage; 3 stop (the procedure's "stop, retain and report"); 4 retained by
# the removal route itself (`removed: false`, or git refused the removal or `git branch -d`).
# Audit lines go to stdout as `audit: ...`; the reason for a stop or a retention goes to stderr.

PYTHON=/usr/bin/python3
# `git -C <dir>` does not override an inherited repository selector: every command here acts on the
# repository its arguments name, so the selectors a caller exported are dropped, and so is the
# `-c`-style configuration a caller injected (which can name hooks); repository and global
# configuration still apply.
unset GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR GIT_INDEX_FILE GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES \
  GIT_CONFIG_COUNT GIT_CONFIG_PARAMETERS

audit() { printf 'audit: %s\n' "$*"; }
stop() { printf 'STOP: %s\n' "$*" >&2; exit 3; }
retained() { printf 'RETAINED: %s\n' "$*" >&2; exit 4; }
usage() { printf 'usage: runbook.sh %s\n' "$*" >&2; exit 2; }

# The canonical form of a directory, every symlink resolved; fails when it cannot be resolved.
canonical() {
  [ -n "$1" ] && (CDPATH='' cd -P -- "$1" 2>/dev/null && pwd -P)
}

# What a lookup of a path says: `exists`, `absent` (no such file), or `unknown` (it cannot say).
lookup() {
  "$PYTHON" -I -c '
import errno, os, sys
try:
    os.lstat(sys.argv[1])
    print("exists")
except OSError as error:
    print("absent" if error.errno == errno.ENOENT else "unknown")
' "$1"
}

# True when one canonical path equals, lies inside or contains the other; `/` contains every path.
overlaps() {
  [ "$1" = / ] || [ "$2" = / ] && return 0
  case "$1/" in "$2/"*) return 0 ;; esac
  case "$2/" in "$1/"*) return 0 ;; esac
  return 1
}

# Fetch both base heads by name, check each against ls-remote, print the captured base OID.
capture_base() {
  [ $# -eq 1 ] || usage "capture-base <repo-root>"
  local root=$1 status name local_oid remote_oid listing oid ref base=''
  git -C "$root" fetch -q origin +refs/heads/develop:refs/remotes/origin/develop \
    +refs/heads/master:refs/remotes/origin/master >&2
  status=$?
  audit "named fetch of develop and master: exit $status"
  [ "$status" -eq 0 ] || stop "the named fetch failed (exit $status); create no worktree"
  for name in develop master; do
    local_oid=$(git -C "$root" rev-parse --verify -q "refs/remotes/origin/$name^{commit}") ||
      stop "rev-parse of origin/$name failed; create no worktree"
    listing=$(git -C "$root" ls-remote origin "refs/heads/$name") ||
      stop "ls-remote of refs/heads/$name failed; create no worktree"
    remote_oid=''
    while read -r oid ref; do
      [ "$ref" = "refs/heads/$name" ] && remote_oid=$oid
    done <<EOF
$listing
EOF
    if [ -n "$remote_oid" ] && [ "$local_oid" = "$remote_oid" ]; then
      audit "origin/$name: rev-parse $local_oid, ls-remote $remote_oid, equal"
    else
      audit "origin/$name: rev-parse $local_oid, ls-remote ${remote_oid:-none}, differ"
      stop "origin/$name is $local_oid here and ${remote_oid:-absent} on the remote; create no worktree"
    fi
    [ "$name" = develop ] && base=$local_oid
  done
  audit "captured base $base, read from origin/develop"
  printf 'base %s\n' "$base"
}

# Before any delivery edit: the created worktree's HEAD is the captured base.
verify_head() {
  [ $# -eq 2 ] || usage "verify-head <worktree-path> <base-oid>"
  local head
  head=$(git -C "$1" rev-parse -q --verify HEAD) ||
    stop "HEAD of $1 cannot be read; retain and report the worktree and base $2"
  if [ "$head" = "$2" ]; then
    audit "created HEAD $head equals base $2"
  else
    audit "created HEAD $head differs from base $2"
    stop "the worktree $1 is at $head, not the base $2; retain and report the worktree, its HEAD and the base"
  fi
}

# The managed worktree root and the delivery worktree path neither lie inside nor contain the
# `_agent/` store or the protected instruction-source root.
check_overlap() {
  local store='' root='' path canonical_path canonical_store canonical_root
  while [ $# -gt 0 ]; do
    case $1 in --agent-store | --protected-root)
      [ $# -ge 2 ] || usage "check-overlap --agent-store <dir> --protected-root <dir> <path>..." ;;
    esac
    case $1 in
      --agent-store) store=$2; shift 2 ;;
      --protected-root) root=$2; shift 2 ;;
      --) shift; break ;;
      -*) usage "check-overlap --agent-store <dir> --protected-root <dir> <path>..." ;;
      *) break ;;
    esac
  done
  [ -n "$store" ] && [ -n "$root" ] && [ $# -gt 0 ] ||
    usage "check-overlap --agent-store <dir> --protected-root <dir> <path>..."
  canonical_store=$(canonical "$store") || stop "the artifact store $store cannot be canonicalized"
  canonical_root=$(canonical "$root") || stop "the protected root $root cannot be canonicalized"
  for path in "$@"; do
    canonical_path=$(canonical "$path") || stop "$path cannot be canonicalized; do not create or use the worktree"
    if overlaps "$canonical_path" "$canonical_store" || overlaps "$canonical_path" "$canonical_root"; then
      audit "$canonical_path overlaps $canonical_store or $canonical_root"
      stop "$canonical_path overlaps the artifact store or the protected root; do not create or use the worktree"
    fi
    audit "$canonical_path is apart from $canonical_store and $canonical_root"
  done
}

# Status of a working tree: exit 0 and empty output, or the stop.
require_clean() {
  local out status
  out=$(git --no-optional-locks -C "$1" status --porcelain --untracked-files=all "${@:3}" 2>&1)
  status=$?
  audit "status of $1 ($2): exit $status, ${out:+not }empty"
  [ "$status" -eq 0 ] && [ -z "$out" ]
}

# After a develop -> master release: fast-forward the protected root, each step only after the last.
refresh_root() {
  [ $# -eq 1 ] || usage "refresh-root <protected-root>"
  local root=$1 head want status
  require_clean "$root" "before the switch" || stop "the protected root is not clean; run no later step"
  git -C "$root" switch -q master >&2
  status=$?; audit "git switch master: exit $status"
  [ "$status" -eq 0 ] || stop "git switch master failed (exit $status); run no later step"
  git -C "$root" fetch -q origin +refs/heads/master:refs/remotes/origin/master >&2
  status=$?; audit "named fetch of master: exit $status"
  [ "$status" -eq 0 ] || stop "the named fetch of master failed (exit $status); run no later step"
  git -C "$root" merge -q --ff-only refs/remotes/origin/master >&2
  status=$?; audit "git merge --ff-only origin/master: exit $status"
  [ "$status" -eq 0 ] || stop "the fast-forward failed (exit $status); run no later step"
  require_clean "$root" "after the fast-forward" || stop "the protected root is not clean after the fast-forward"
  head=$(git -C "$root" rev-parse -q --verify HEAD) || stop "HEAD of the protected root cannot be read"
  want=$(git -C "$root" rev-parse -q --verify 'refs/remotes/origin/master^{commit}') || stop "origin/master cannot be read"
  audit "HEAD $head, origin/master $want"
  [ "$head" = "$want" ] || stop "the protected root is at $head, not origin/master $want"
  printf 'serves %s\n' "$head"
}

# `git worktree list --porcelain`, read into one array per field.
parse_inventory() {
  local line started=0
  count=0
  record_path=(); record_branch=(); record_detached=(); record_locked=(); record_has_path=()
  while IFS= read -r line || [ -n "$line" ]; do
    if [ -z "$line" ]; then
      [ "$started" -eq 1 ] && count=$((count + 1))
      started=0
      continue
    fi
    if [ "$started" -eq 0 ]; then
      record_path[count]=''; record_branch[count]=''; record_detached[count]=0
      record_locked[count]=0; record_has_path[count]=0; started=1
    fi
    case $line in
      'worktree '*) record_path[count]=${line#worktree }; record_has_path[count]=1 ;;
      'branch '*) record_branch[count]=${line#branch } ;;
      detached) record_detached[count]=1 ;;
      locked | 'locked '*) record_locked[count]=1 ;;
    esac
  done <<EOF
$1
EOF
  [ "$started" -eq 1 ] && count=$((count + 1))
}

# Run one `openclaw worktrees` subcommand bound to the given Gateway values, never --profile or --dev;
# its output goes to the file named first, so the audit line stays out of it.
openclaw_bound() {
  local status result=$1
  shift
  if [ "$profile_bound" = set ]; then
    env OPENCLAW_PROFILE="$profile" OPENCLAW_STATE_DIR="$state_dir" OPENCLAW_CONFIG_PATH="$config_path" \
      "$openclaw" worktrees "$@" >"$result"
  else
    env -u OPENCLAW_PROFILE OPENCLAW_STATE_DIR="$state_dir" OPENCLAW_CONFIG_PATH="$config_path" \
      "$openclaw" worktrees "$@" >"$result"
  fi
  status=$?
  audit "openclaw worktrees $*: OPENCLAW_STATE_DIR=$state_dir OPENCLAW_CONFIG_PATH=$config_path" \
    "OPENCLAW_PROFILE ${profile_bound}${profile:+ to $profile}, no --profile or --dev, exit $status"
  return "$status"
}

# Remove a delivery worktree and its local branch once its feature PR has merged into develop.
cleanup() {
  local repo='' branch='' root='' managed_root='' openclaw='' state_dir='' config_path=''
  local profile='' profile_bound='' scratch
  local usage_line="cleanup --repo <dir> --branch <name> --protected-root <dir> --managed-root <dir>"
  usage_line="$usage_line --openclaw <cmd> --state-dir <dir> --config-path <file> (--profile <name> | --no-profile)"
  while [ $# -gt 0 ]; do
    [ $# -ge 2 ] || [ "$1" = --no-profile ] || usage "$usage_line"
    case $1 in
      --repo) repo=$2; shift 2 ;;
      --branch) branch=$2; shift 2 ;;
      --protected-root) root=$2; shift 2 ;;
      --managed-root) managed_root=$2; shift 2 ;;
      --openclaw) openclaw=$2; shift 2 ;;
      --state-dir) state_dir=$2; shift 2 ;;
      --config-path) config_path=$2; shift 2 ;;
      --profile) profile=$2; profile_bound=set; shift 2 ;;
      --no-profile) profile=''; profile_bound=unset; shift ;;
      *) usage "$usage_line" ;;
    esac
  done
  [ -n "$repo" ] && [ -n "$branch" ] && [ -n "$root" ] && [ -n "$managed_root" ] && [ -n "$openclaw" ] &&
    [ -n "$state_dir" ] && [ -n "$config_path" ] && [ -n "$profile_bound" ] || usage "$usage_line"
  # A template, so TMPDIR is honoured on macOS too, where a bare `mktemp -d` ignores it.
  scratch=$(mktemp -d "${TMPDIR:-/tmp}/openclaw-runbook.XXXXXX") || stop "no scratch directory for the inventory"
  # Expanded now: the trap runs at exit, after this function's locals are gone.
  # shellcheck disable=SC2064
  trap "rm -rf -- $(printf '%q' "$scratch")" EXIT

  local inventory status i path='' candidates='' matches=0 why canonical_other canonical_repo
  inventory=$(git -C "$repo" worktree list --porcelain) ||
    stop "git worktree list --porcelain cannot be read; retain and report $branch and its worktree"
  audit "inventory read: $(printf '%s' "$inventory" | tr '\n' '|')"

  git -C "$repo" fetch -q origin +refs/heads/develop:refs/remotes/origin/develop >&2
  status=$?; audit "named fetch of develop: exit $status"
  [ "$status" -eq 0 ] || stop "the named fetch of develop failed; retain and report $branch and its worktree"
  git -C "$repo" merge-base --is-ancestor "refs/heads/$branch" refs/remotes/origin/develop
  status=$?; audit "merge-base --is-ancestor $branch origin/develop: exit $status"
  [ "$status" -eq 0 ] || stop "$branch is not an ancestor of origin/develop (exit $status); retain and report it"

  parse_inventory "$inventory"
  for ((i = 0; i < count; i++)); do
    [ "${record_branch[i]}" = "refs/heads/$branch" ] || continue
    matches=$((matches + 1)); path=${record_path[i]}; candidates="$candidates [${record_path[i]}]"
  done
  audit "records on refs/heads/$branch: $matches:$candidates"
  [ "$matches" -eq 1 ] || stop "$matches worktrees have $branch checked out; retain and report:$candidates"
  path=$(canonical "$path") || stop "the worktree of $branch cannot be canonicalized; retain and report it"
  [ "$(lookup "$path")" = exists ] || stop "$path is not positively there; retain and report it"
  canonical_repo=$(canonical "$repo") || stop "the repository directory cannot be canonicalized"
  [ "$canonical_repo" != "$path" ] || stop "run the cleanup from another worktree than $path"

  # The protected-worktree inventory: the named root, the first record, base branches, detached and locked.
  for ((i = 0; i < count; i++)); do
    [ "${record_has_path[i]}" -eq 1 ] ||
      stop "inventory record $i has no worktree line; retain and report $branch, $path and every record"
    if [ "$i" -gt 0 ] && [ -z "${record_branch[i]}" ] && [ "${record_detached[i]}" -eq 0 ]; then
      stop "inventory record ${record_path[i]} has neither a branch nor a detached line; retain and report it"
    fi
  done
  canonical_other=$(canonical "$root") || stop "the protected root $root cannot be canonicalized; retain and report"
  audit "protected root $canonical_other compared with $path"
  [ "$canonical_other" != "$path" ] || stop "$path is the protected instruction-source root; never eligible"
  for ((i = 0; i < count; i++)); do
    why=''
    [ "$i" -eq 0 ] && why='first record'
    case ${record_branch[i]} in refs/heads/master | refs/heads/develop) why="${why:-base branch}" ;; esac
    [ "${record_detached[i]}" -eq 1 ] && why="${why:-detached}"
    [ "${record_locked[i]}" -eq 1 ] && why="${why:-locked}"
    [ -n "$why" ] || continue
    canonical_other=$(canonical "${record_path[i]}") ||
      stop "protected worktree ${record_path[i]} ($why) cannot be canonicalized; retain and report $path"
    audit "protected ${record_path[i]} ($why) compared with $path"
    [ "$canonical_other" != "$path" ] || stop "$path is a protected worktree ($why); retain and report it"
  done

  require_clean "$path" "before the inventory query" --ignored ||
    stop "$path has local changes, untracked or ignored files; retain and report it"

  openclaw_bound "$scratch/list.json" list --json ||
    stop "openclaw worktrees list cannot be read; retain and report $path and $branch"
  "$PYTHON" -I - "$scratch/list.json" "$scratch/records" <<'PY' || stop "the openclaw inventory cannot be read; retain and report $path"
import json, sys
try:
    with open(sys.argv[1], encoding="utf-8") as handle:
        data = json.load(handle)
except (OSError, ValueError) as error:
    sys.exit("unreadable: {}".format(error))
records = data.get("worktrees") if isinstance(data, dict) else None
if not isinstance(records, list):
    sys.exit("no worktrees list")
with open(sys.argv[2], "wb") as out:
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str) or not record["path"]:
            sys.exit("a record whose path cannot be determined: {!r}".format(record))
        branch = record.get("branch") if isinstance(record.get("branch"), str) else ""
        if branch.startswith("refs/heads/"):
            branch = branch[len("refs/heads/"):]
        ident = record.get("id")
        ident = str(ident) if isinstance(ident, (str, int)) and not isinstance(ident, bool) else ""
        fields = (record["path"], branch, ident)
        if any("\0" in field for field in fields):
            sys.exit("a record holding a NUL")
        out.write(b"".join(field.encode("utf-8") + b"\0" for field in fields))
PY

  local record_path_value record_branch_value record_id seen managed_id='' managed_count=0
  while IFS= read -r -d '' record_path_value && IFS= read -r -d '' record_branch_value &&
    IFS= read -r -d '' record_id; do
    if canonical_other=$(canonical "$record_path_value"); then
      audit "openclaw record $record_id: $canonical_other, branch $record_branch_value"
      [ "$canonical_other" = "$path" ] || continue
      managed_count=$((managed_count + 1))
      [ "$record_branch_value" = "$branch" ] ||
        stop "openclaw record $record_id at $path is on ${record_branch_value:-no branch}, not $branch; retain and report it"
      managed_id=$record_id
      continue
    fi
    seen=$(lookup "$record_path_value")
    if [ "$seen" = absent ] && [ "$record_branch_value" != "$branch" ]; then
      audit "openclaw record $record_id: $record_path_value absent, branch $record_branch_value, skipped"
      continue
    fi
    stop "openclaw record $record_id ($record_path_value, $seen, branch $record_branch_value) cannot be matched; retain and report it"
  done <"$scratch/records"
  [ "$managed_count" -le 1 ] || stop "$managed_count openclaw records name $path; retain and report every candidate"

  if [ "$managed_count" -eq 1 ]; then
    [ -n "$managed_id" ] || stop "the openclaw record for $path has no id; retain and report it"
    openclaw_bound "$scratch/remove.json" remove "$managed_id" --if-lossless --json ||
      stop "openclaw worktrees remove $managed_id failed; retain and report $path"
    local removed
    removed=$("$PYTHON" -I -c '
import json, sys
try:
    with open(sys.argv[1], encoding="utf-8") as handle:
        result = json.load(handle)
except (OSError, ValueError):
    sys.exit(1)
if not isinstance(result, dict) or not isinstance(result.get("removed"), bool):
    sys.exit(1)
print("{} {}".format(str(result["removed"]).lower(), json.dumps(result.get("cleanup"))))
' "$scratch/remove.json") || stop "the result of openclaw worktrees remove $managed_id cannot be read; retain and report $path"
    audit "managed removal of $managed_id: removed ${removed%% *}, cleanup ${removed#* }"
    [ "${removed%% *}" = true ] || retained "openclaw kept $path (cleanup ${removed#* }); $branch stays"
  else
    local root_canonical second
    root_canonical=$(canonical "$managed_root") ||
      stop "the managed worktree root $managed_root cannot be canonicalized; retain and report $path"
    audit "plain route: $path compared with managed root $root_canonical"
    ! overlaps "$path" "$root_canonical" ||
      stop "$path lies in the managed worktree root with no openclaw record; retain and report it"
    require_clean "$path" "immediately before removal" --ignored ||
      stop "$path is no longer clean; retain and report it"
    second=$(git -C "$repo" worktree list --porcelain) ||
      stop "the second git worktree list --porcelain cannot be read; retain and report $path"
    parse_inventory "$second"
    local at_path=0 on_branch=0
    for ((i = 0; i < count; i++)); do
      canonical_other=$(canonical "${record_path[i]}") || continue
      [ "$canonical_other" = "$path" ] || continue
      at_path=$((at_path + 1))
      [ "${record_branch[i]}" = "refs/heads/$branch" ] && on_branch=$((on_branch + 1))
    done
    audit "second inventory: $at_path record(s) at $path, $on_branch on $branch"
    [ "$at_path" -eq 1 ] && [ "$on_branch" -eq 1 ] ||
      stop "the second inventory does not show exactly one $path on $branch; retain and report it"
    git -C "$repo" worktree remove "$path" >&2
    status=$?; audit "git worktree remove $path: exit $status"
    [ "$status" -eq 0 ] || retained "git refused to remove $path (exit $status); $branch stays"
  fi

  if git -C "$repo" show-ref --verify -q "refs/heads/$branch"; then
    git -C "$repo" branch -d "$branch" >&2
    status=$?; audit "git branch -d $branch: exit $status"
    [ "$status" -eq 0 ] || retained "git refused to delete $branch (exit $status); the worktree is gone, the branch stays"
  fi
  printf 'removed %s and %s\n' "$path" "$branch"
}

command=${1:-}
[ $# -gt 0 ] && shift
case $command in
  capture-base) capture_base "$@" ;;
  verify-head) verify_head "$@" ;;
  check-overlap) check_overlap "$@" ;;
  refresh-root) refresh_root "$@" ;;
  cleanup) cleanup "$@" ;;
  *) usage "capture-base | verify-head | check-overlap | refresh-root | cleanup" ;;
esac
