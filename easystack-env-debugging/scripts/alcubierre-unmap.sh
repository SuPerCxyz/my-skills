#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash alcubierre-unmap.sh preflight|execute|verify UUID...
EOF
}

declare -a volume_ids=()
declare -A disconnected_ids=()
manul_pod=""
volume_snapshot=""
volume_output=""
mapping_snapshot=""
disk_id=""
protocol=""
volume_state=""
task_state=""
error_message=""
mapping_output=""
map_count=0
client_count=0
clients=""
api_total_seconds=0

handle_interruption() {
  echo "INTERRUPTED|RERUN_SAME_BATCH=1" >&2
  exit 130
}

trap handle_interruption INT TERM

normalize_uuids() {
  local value
  declare -A seen=()

  volume_ids=()
  for value in "$@"; do
    if [[ ! "$value" =~ ^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[1-5][0-9A-Fa-f]{3}-[89ABab][0-9A-Fa-f]{3}-[0-9A-Fa-f]{12}$ ]]; then
      echo "invalid volume UUID: $value" >&2
      return 2
    fi
    if [[ -z "${seen[$value]:-}" ]]; then
      seen[$value]=1
      volume_ids+=("$value")
    fi
  done
  [[ ${#volume_ids[@]} -gt 0 ]] || {
    echo "at least one volume UUID is required" >&2
    return 2
  }
}

select_manul_pod() {
  manul_pod=$(kubectl -n alcubierre get pod \
    -l 'application=alcubierre,component=manul' --no-headers |
    awk '$3 == "Running" {
      split($2, ready, "/")
      if (ready[1] == ready[2]) {
        print $1
        exit
      }
    }')
  [[ -n "$manul_pod" ]] || {
    echo "no Running and Ready Manul pod found" >&2
    return 3
  }
}

refresh_volume_snapshot() {
  volume_snapshot=$(kubectl exec -n alcubierre "$manul_pod" -c manul -- \
    kvctl list volume --format object)
}

query_volume() {
  local volume_id="$1"
  local matches

  volume_output=$(printf '%s\n' "$volume_snapshot" |
    grep -- "$volume_id" || true)
  matches=$(printf '%s\n' "$volume_output" | grep -c '^Volume' || true)
  [[ "$matches" == "1" ]] || return 1

  disk_id=$(printf '%s\n' "$volume_output" |
    sed -n "s/.*id='\\(alcub_[^']*\\)'.*/\\1/p")
  protocol=$(printf '%s\n' "$volume_output" |
    sed -n "s/.*protocol='\\([^']*\\)'.*/\\1/p")
  volume_state=$(printf '%s\n' "$volume_output" |
    sed -n "s/.*state=<State\\.\\([A-Z_]*\\):.*/\\1/p")
  task_state=$(printf '%s\n' "$volume_output" |
    sed -n "s/.*task_state=<TaskState\\.\\([A-Z_]*\\):.*/\\1/p")
  error_message=$(printf '%s\n' "$volume_output" |
    sed -n "s/.*error_message='\\([^']*\\)'.*/\\1/p")
  [[ -n "$disk_id$protocol$volume_state" ]]
}

if ! declare -F refresh_mapping_snapshot >/dev/null; then
  script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
  source "$script_dir/alcubierre-mapping.sh"
fi

print_preflight() {
  local volume_id="$1"
  local result

  if ! query_volume "$volume_id"; then
    echo "PREFLIGHT|$volume_id|RESULT=BLOCKED_NOT_FOUND"
    return 1
  fi
  if ! query_mapping; then
    echo "PREFLIGHT|$volume_id|DISK_ID=$disk_id|RESULT=BLOCKED_PROTOCOL"
    return 1
  fi

  if [[ "$map_count" == "0" ]]; then
    result="NOOP"
  elif [[ "$client_count" != "1" ]]; then
    result="BLOCKED_MULTI_CLIENT"
  elif [[ "$volume_state" != "LINKED" ]]; then
    result="BLOCKED_STATE"
  else
    result="READY"
  fi

  echo "PREFLIGHT|$volume_id|DISK_ID=$disk_id|PROTOCOL=$protocol|STATE=$volume_state|TASK_STATE=$task_state|MAP_COUNT=$map_count|CLIENT_COUNT=$client_count|CLIENTS=$clients|RESULT=$result"
  [[ "$result" == "READY" || "$result" == "NOOP" ]]
}

execute_one() {
  local volume_id="$1"
  local expected_client api_url api_data api_output api_started api_elapsed

  query_volume "$volume_id" || {
    echo "FAILED_VOLUME_QUERY|$volume_id"
    return 20
  }
  query_mapping || {
    echo "FAILED_MAPPING_QUERY|$volume_id|DISK_ID=$disk_id"
    return 21
  }

  if [[ "$map_count" == "0" ]]; then
    echo "SUCCESS_NOOP|$volume_id|MAPPING=0|STATE=$volume_state|TASK_STATE=$task_state"
    return 0
  fi
  if [[ "$client_count" != "1" || "$volume_state" != "LINKED" ]]; then
    echo "FAILED_PRECHECK|$volume_id|MAPPING=$map_count|STATE=$volume_state|CLIENTS=$clients"
    return 22
  fi

  expected_client="$clients"
  if [[ "$protocol" == "ISCSI" ]]; then
    api_url="http://alcubierre-manul.alcubierre.svc.cluster.local:8192/v2/volumes/${disk_id}/disconnections"
    api_data="{\"disconnection\": {\"iqn\": \"$expected_client\"}}"
  else
    api_url="http://alcubierre-manul.alcubierre.svc.cluster.local:8192/v2/volumes/${disk_id}/nvme_disconnections"
    api_data="{\"nvme_disconnection\": {\"hostnqn\": \"$expected_client\"}}"
  fi

  api_started=$SECONDS
  if api_output=$(curl --fail-with-body -sS -X POST "$api_url" \
    -H 'Accept: */*' -H 'Content-Type: application/json' \
    -d "$api_data" 2>&1); then
    api_elapsed=$((SECONDS - api_started))
  else
    api_elapsed=$((SECONDS - api_started))
    api_total_seconds=$((api_total_seconds + api_elapsed))
    echo "TIMING|PHASE=API|VOLUME_ID=$volume_id|SECONDS=$api_elapsed"
    echo "FAILED_API|$volume_id|$api_output"
    return 23
  fi
  api_total_seconds=$((api_total_seconds + api_elapsed))
  echo "TIMING|PHASE=API|VOLUME_ID=$volume_id|SECONDS=$api_elapsed"
  disconnected_ids[$volume_id]=1
  echo "API_ACCEPTED|$volume_id"
}

verify_one() {
  local volume_id="$1"
  local require_unlinked="${2:-0}"

  query_volume "$volume_id" || {
    echo "VERIFY|$volume_id|RESULT=NOT_FOUND"
    return 1
  }
  query_mapping || {
    echo "VERIFY|$volume_id|DISK_ID=$disk_id|RESULT=QUERY_FAILED"
    return 1
  }
  if [[ "$map_count" == "0" && "$require_unlinked" == "1" &&
        ("$volume_state" != "UNLINKED" || -n "$error_message") ]]; then
    echo "VERIFY|$volume_id|PROTOCOL=$protocol|MAPPING=0|STATE=$volume_state|TASK_STATE=$task_state|ERROR=$error_message|RESULT=FAILED"
    return 1
  elif [[ "$map_count" == "0" ]]; then
    echo "VERIFY|$volume_id|PROTOCOL=$protocol|MAPPING=0|STATE=$volume_state|TASK_STATE=$task_state|ERROR=$error_message|RESULT=SUCCESS"
    return 0
  fi
  echo "VERIFY|$volume_id|PROTOCOL=$protocol|MAPPING=$map_count|STATE=$volume_state|TASK_STATE=$task_state|ERROR=$error_message|RESULT=FAILED"
  return 1
}

run_remote() {
  local action="${1:-}"
  local volume_id phase_started rc=0 failures=0
  local total_started=$SECONDS

  [[ -n "$action" ]] || {
    usage >&2
    return 2
  }
  shift
  normalize_uuids "$@"
  select_manul_pod
  echo "MANUL_POD|$manul_pod"
  phase_started=$SECONDS
  refresh_volume_snapshot || {
    echo "FAILED_VOLUME_SNAPSHOT|PHASE=INITIAL"
    return 10
  }
  echo "TIMING|PHASE=INITIAL_VOLUME|SECONDS=$((SECONDS - phase_started))"
  phase_started=$SECONDS
  refresh_mapping_snapshot || {
    echo "FAILED_MAPPING_SNAPSHOT|PHASE=INITIAL"
    return 11
  }
  echo "TIMING|PHASE=INITIAL_MAPPING|SECONDS=$((SECONDS - phase_started))"

  case "$action" in
    preflight)
      for volume_id in "${volume_ids[@]}"; do
        print_preflight "$volume_id" || failures=1
      done
      ;;
    execute)
      for volume_id in "${volume_ids[@]}"; do
        if execute_one "$volume_id"; then
          :
        else
          rc=$?
          break
        fi
      done
      echo "TIMING|PHASE=API_TOTAL|SECONDS=$api_total_seconds"
      if [[ "$rc" != "0" ]]; then
        echo "TIMING|PHASE=TOTAL|SECONDS=$((SECONDS - total_started))"
        return "$rc"
      fi
      phase_started=$SECONDS
      refresh_mapping_snapshot || {
        echo "FAILED_MAPPING_SNAPSHOT|PHASE=FINAL"
        return 24
      }
      echo "TIMING|PHASE=FINAL_MAPPING|SECONDS=$((SECONDS - phase_started))"
      for volume_id in "${volume_ids[@]}"; do
        [[ "${disconnected_ids[$volume_id]:-0}" == "1" ]] || continue
        if ! query_volume "$volume_id" || ! query_mapping; then
          echo "FAILED_POST_MAPPING_QUERY|$volume_id"
          failures=1
          continue
        fi
        if [[ "$map_count" == "0" ]]; then
          echo "MAPPING_CLEARED|$volume_id|MAPPING=0"
        else
          echo "FAILED_VERIFY|$volume_id|MAPPING=$map_count"
          failures=1
        fi
      done
      phase_started=$SECONDS
      refresh_volume_snapshot || {
        echo "FAILED_VOLUME_SNAPSHOT|PHASE=FINAL"
        return 27
      }
      echo "TIMING|PHASE=FINAL_VOLUME|SECONDS=$((SECONDS - phase_started))"
      echo "FINAL_VERIFY_BEGIN|COUNT=${#volume_ids[@]}"
      for volume_id in "${volume_ids[@]}"; do
        verify_one "$volume_id" \
          "${disconnected_ids[$volume_id]:-0}" || failures=1
      done
      ;;
    verify)
      for volume_id in "${volume_ids[@]}"; do
        verify_one "$volume_id" || failures=1
      done
      ;;
    *)
      echo "unsupported action: $action" >&2
      usage >&2
      return 2
      ;;
  esac
  echo "TIMING|PHASE=TOTAL|SECONDS=$((SECONDS - total_started))"
  return "$failures"
}

if [[ "${1:-}" == "--remote" ]]; then
  shift
fi
run_remote "$@"
