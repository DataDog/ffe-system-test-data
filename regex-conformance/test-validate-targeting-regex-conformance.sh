#!/bin/sh

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
fixture="$script_dir/targeting-regex-conformance.json"
validator="$script_dir/validate-targeting-regex-conformance.jq"
temporary_files=""

cleanup() {
  for file in $temporary_files; do
    rm -f "$file"
  done
}
trap cleanup EXIT INT TERM

expect_invalid() {
  description=$1
  mutation=$2
  temporary_file=$(mktemp)
  temporary_files="$temporary_files $temporary_file"

  jq "$mutation" "$fixture" >"$temporary_file"
  if jq -e -f "$validator" "$temporary_file" >/dev/null; then
    echo "validator accepted invalid fixture: $description" >&2
    exit 1
  fi
}

jq -e -f "$validator" "$fixture" >/dev/null

expect_invalid \
  "compile failure with a true match result" \
  '.cases |= map(if .id == "rejected-byte-escape" then .expectedMatch = true else . end)'

expect_invalid \
  "empty semantics" \
  '.semantics = {}'

expect_invalid \
  "empty portable syntax contract" \
  '.portableSyntax.accepted = [] | .portableSyntax.rejected = []'

echo "targeting regex conformance validator tests passed"
