#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF' >&2
usage: run-downstream-conformance.sh \
  <fixture-repository> <downstream-repository> <fixture-submodule-path> \
  <base-fixture-sha> <head-fixture-sha> <log-directory> -- <test-command> [args...]
EOF
}

if [[ $# -lt 8 ]]; then
  usage
  exit 2
fi

fixture_repository=$1
downstream_repository=$2
fixture_submodule_path=$3
base_fixture_sha=$4
head_fixture_sha=$5
log_directory=$6
shift 6

if [[ $1 != "--" ]]; then
  usage
  exit 2
fi
shift

fixture_repository=$(cd "$fixture_repository" && pwd)
downstream_repository=$(cd "$downstream_repository" && pwd)
fixture_checkout="$downstream_repository/$fixture_submodule_path"

for fixture_sha in "$base_fixture_sha" "$head_fixture_sha"; do
  git -C "$fixture_repository" cat-file -e "$fixture_sha^{commit}"
done

mkdir -p "$log_directory"

git -C "$downstream_repository" submodule sync -- "$fixture_submodule_path"
git -C "$downstream_repository" submodule update \
  --init \
  --depth 1 \
  -- "$fixture_submodule_path"

run_fixture_revision() {
  local label=$1
  local fixture_sha=$2
  local log_file="$log_directory/$label.log"
  local status
  shift 2

  git -c protocol.file.allow=always \
    -C "$fixture_checkout" \
    fetch --no-tags "$fixture_repository" "$fixture_sha"
  git -C "$fixture_checkout" checkout --detach FETCH_HEAD

  set +e
  (
    cd "$downstream_repository"
    "$@"
  ) >"$log_file" 2>&1
  status=$?
  set -e

  printf '\n===== %s fixture (%s) =====\n' "$label" "$fixture_sha"
  if [[ $status -ne 0 ]]; then
    printf '%s\n' '----- first reported failure -----'
    grep -m 1 -A 3 ' FAILED' "$log_file" || true
  fi
  printf '%s\n' '----- last 200 log lines -----'
  tail -n 200 "$log_file"
  printf '===== %s exit code: %s =====\n' "$label" "$status"

  return "$status"
}

base_status=0
head_status=0
run_fixture_revision base "$base_fixture_sha" "$@" || base_status=$?
run_fixture_revision head "$head_fixture_sha" "$@" || head_status=$?

if [[ $base_status -eq 0 && $head_status -eq 0 ]]; then
  classification=compatible
  summary="Both the pull-request base and head fixtures pass."
elif [[ $base_status -eq 0 && $head_status -ne 0 ]]; then
  classification=new-regression
  summary="The base fixture passes and the proposed fixture fails."
elif [[ $base_status -ne 0 && $head_status -eq 0 ]]; then
  classification=improvement
  summary="The base fixture fails and the proposed fixture passes."
else
  classification=existing-drift
  summary="Both fixture revisions fail; the downstream repository was already incompatible with the pull-request base."
fi

printf '\nclassification=%s\n' "$classification"
printf 'base_exit_code=%s\n' "$base_status"
printf 'head_exit_code=%s\n' "$head_status"

if [[ -n ${GITHUB_OUTPUT:-} ]]; then
  {
    printf 'classification=%s\n' "$classification"
    printf 'base_exit_code=%s\n' "$base_status"
    printf 'head_exit_code=%s\n' "$head_status"
  } >>"$GITHUB_OUTPUT"
fi

if [[ -n ${GITHUB_STEP_SUMMARY:-} ]]; then
  {
    printf '### Downstream fixture compatibility\n\n'
    printf '| Base | Head | Classification |\n'
    printf '| ---: | ---: | --- |\n'
    # shellcheck disable=SC2016 # Backticks are Markdown, not shell syntax.
    printf '| `%s` | `%s` | **%s** |\n\n' "$base_status" "$head_status" "$classification"
    printf '%s\n' "$summary"
  } >>"$GITHUB_STEP_SUMMARY"
fi
