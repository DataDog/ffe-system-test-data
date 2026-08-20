#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF' >&2
usage: run-regex-conformance.sh \
  <fixture-repository> <downstream-repository> <fixture-submodule-path> \
  <downstream-fixture-sha> <candidate-fixture-sha> <log-directory> \
  -- <test-command> [args...]
EOF
}

if [[ $# -lt 8 ]]; then
  usage
  exit 2
fi

fixture_repository=$1
downstream_repository=$2
fixture_submodule_path=$3
downstream_fixture_sha=$4
candidate_fixture_sha=$5
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
log_file="$log_directory/candidate.log"

git -C "$fixture_repository" cat-file -e "$downstream_fixture_sha^{commit}"
git -C "$fixture_repository" cat-file -e "$candidate_fixture_sha^{commit}"
downstream_sha=$(git -C "$downstream_repository" rev-parse HEAD)
declared_fixture_sha=$(
  git -C "$downstream_repository" ls-tree HEAD -- "$fixture_submodule_path" |
    awk '{print $3}'
)
if [[ $declared_fixture_sha != "$downstream_fixture_sha" ]]; then
  printf 'downstream branch %s pins fixture %s, expected baseline %s\n' \
    "$downstream_sha" "$declared_fixture_sha" "$downstream_fixture_sha" >&2
  exit 1
fi
mkdir -p "$log_directory"

git -C "$downstream_repository" submodule sync -- "$fixture_submodule_path"
git -C "$downstream_repository" submodule update \
  --init \
  --depth 1 \
  -- "$fixture_submodule_path"
git -c protocol.file.allow=always \
  -C "$fixture_checkout" \
  fetch --no-tags "$fixture_repository" "$candidate_fixture_sha"
git -C "$fixture_checkout" checkout --detach FETCH_HEAD

status=0
set +e
(
  cd "$downstream_repository"
  "$@"
) >"$log_file" 2>&1
status=$?
set -e

printf '\n===== candidate fixture (%s) =====\n' "$candidate_fixture_sha"
printf '===== downstream branch (%s) =====\n' "$downstream_sha"
if [[ $status -ne 0 ]]; then
  printf '%s\n' '----- first reported failure -----'
  grep -m 1 -A 3 ' FAILED' "$log_file" || true
fi
printf '%s\n' '----- last 200 log lines -----'
tail -n 200 "$log_file"
printf '===== candidate exit code: %s =====\n' "$status"

if [[ $status -eq 0 ]]; then
  classification=candidate-pass
  summary="The proposed regex fixture passes this downstream conformance test."
else
  classification=candidate-failure
  summary="The proposed regex fixture disagrees with this downstream conformance test."
fi

printf '\nclassification=%s\n' "$classification"
printf 'candidate_exit_code=%s\n' "$status"

if [[ -n ${GITHUB_OUTPUT:-} ]]; then
  {
    printf 'classification=%s\n' "$classification"
    printf 'candidate_exit_code=%s\n' "$status"
  } >>"$GITHUB_OUTPUT"
fi

if [[ -n ${GITHUB_STEP_SUMMARY:-} ]]; then
  {
    printf '### Regex universality evidence\n\n'
    printf -- '- Downstream branch: `%s`\n' "$downstream_sha"
    printf -- '- Downstream fixture baseline: `%s`\n' "$downstream_fixture_sha"
    printf -- '- Candidate fixture: `%s`\n\n' "$candidate_fixture_sha"
    printf '| Candidate exit code | Classification |\n'
    printf '| ---: | --- |\n'
    # shellcheck disable=SC2016 # Backticks are Markdown, not shell syntax.
    printf '| `%s` | **%s** |\n\n' "$status" "$classification"
    printf '%s\n\n' "$summary"
    printf '%s\n' 'This evidence-only PR is not intended for merge. Inspect the attached consumer log before deciding whether the fixture or implementation is wrong.'
  } >>"$GITHUB_STEP_SUMMARY"
fi

# The workflow's artifact step uses if: always(), so preserve the actual unit
# test exit code while still retaining complete logs for the evidence report.
exit "$status"
