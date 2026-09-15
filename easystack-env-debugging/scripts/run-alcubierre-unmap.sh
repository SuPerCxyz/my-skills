#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

usage() {
  cat <<'EOF'
Usage:
  bash run-alcubierre-unmap.sh [ENV_ACCESS_ARGS...] -- preflight UUID...
  bash run-alcubierre-unmap.sh [ENV_ACCESS_ARGS...] -- execute UUID...
  bash run-alcubierre-unmap.sh [ENV_ACCESS_ARGS...] -- verify UUID...

The runner sends alcubierre-unmap.sh through env-access.sh without writing it
to the target environment.
EOF
}

access_args=()
found_separator=0
has_timeout=0

while [[ $# -gt 0 ]]; do
  if [[ "$1" == "--" ]]; then
    found_separator=1
    shift
    break
  fi
  access_args+=("$1")
  shift
done

[[ "$found_separator" == "1" && $# -ge 2 ]] || {
  usage >&2
  exit 2
}
case "$1" in
  preflight|execute|verify) ;;
  *)
    echo "unsupported action: $1" >&2
    exit 2
    ;;
esac

for arg in "${access_args[@]}"; do
  [[ "$arg" == "--timeout" ]] && has_timeout=1
done
if [[ "$has_timeout" == "0" ]]; then
  access_args+=(--timeout 1800)
fi

payload=$(
  sed -n '1,$p' "$script_dir/alcubierre-mapping.sh" \
    "$script_dir/alcubierre-unmap.sh" | base64 -w0
)
printf -v remote_invocation '%q ' --remote "$@"
remote_cmd="printf '%s' '$payload' | base64 -d | bash -s -- $remote_invocation"
access_script="${EASYSTACK_ENV_ACCESS_SCRIPT:-$script_dir/env-access.sh}"
bash "$access_script" "${access_args[@]}" --cmd "$remote_cmd"
