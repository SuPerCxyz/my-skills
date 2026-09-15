#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash env-access.sh --target <TARGET> [--via <SSH_TARGET>] [--mode auto|ssh|jump18|jumpserver] [-- CMD...]
  bash env-access.sh --env <BJ_ENV> [-- CMD...]
  bash env-access.sh --asset <ASSET_NAME> --mode jumpserver [-- CMD...]
  bash env-access.sh --target <TARGET> --cmd 'kubectl get nodes -o name'

Examples:
  bash env-access.sh --env BJ-<ENV_ID>
  bash env-access.sh --env BJ-<ENV_ID> -- whoami
  bash env-access.sh --target 172.<ENV_ID>.0.2 -- kubectl get nodes -o name
  bash env-access.sh --via eswork --target 192.168.3.3 -- hostname
  bash env-access.sh --target 172.18.0.118 --control-node 10.20.0.3 -- hostname
  bash env-access.sh --via eswork --asset <ASSET_NAME> --mode jumpserver -- whoami

Options:
  --target TARGET       SSH target, IP, alias, or BJ-xx name.
  --via SSH_TARGET      Reach the selected mode through one ordinary SSH jump host.
  --env NAME            Environment name, such as BJ-<ENV_ID>. Converts to 172.<ENV_ID>.0.2.
  --asset NAME          JumpServer asset name for menu fallback.
  --mode MODE           auto, ssh, jump18, or jumpserver. Default: auto.
  --cmd COMMAND         Command string to run after login.
  --control-node IP     Inner control node for 172.18.* jump host mode. Default: 10.20.0.3.
  --alias NAME          SSH config alias for JumpServer menu mode. Default: js.
  --jumpserver-host HOST JumpServer SSH host when local SSH config is missing.
  --jumpserver-user USER JumpServer SSH user when local SSH config is missing.
  --jumpserver-port PORT JumpServer SSH port when local SSH config is missing.
  --jumpserver-identity-file PATH
                        JumpServer SSH identity file when local SSH config is missing.
  --jumpserver-password-file PATH
                        Read the JumpServer password from a file.
  --auth-profile NAME   Load a temporary JumpServer authentication profile.
  --save-auth-profile   Save supplied authentication data to --auth-profile.
  --asset-id ID         Asset ID for JumpServer menu mode.
  --timeout SECONDS     Use one timeout instead of automatic command timeout ladder.
  --no-root             Do not run sudo/root shell after login.
  -h, --help            Show this help.

Without CMD or --cmd, opens an interactive shell.
One-shot read-only commands retry on timeout by default. Timeout ladders:
  quick commands: 10 15 20 30 45 60
  medium commands: 15 20 30 45 60
  slow commands: 30 45 60
EOF
}

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
mode="auto"
target=""
via_target=""
env_name=""
asset_name=""
asset_id=""
remote_cmd=""
control_node="10.20.0.3"
jumpserver_alias="js"
jumpserver_host=""
jumpserver_user=""
jumpserver_port=""
jumpserver_identity_file=""
jumpserver_password_file=""
auth_profile=""
save_auth_profile="0"
single_timeout=""
become_root="1"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      target="${2:?missing value for --target}"
      shift 2
      ;;
    --via)
      via_target="${2:?missing value for --via}"
      shift 2
      ;;
    --env)
      env_name="${2:?missing value for --env}"
      shift 2
      ;;
    --asset)
      asset_name="${2:?missing value for --asset}"
      shift 2
      ;;
    --mode)
      mode="${2:?missing value for --mode}"
      shift 2
      ;;
    --cmd)
      remote_cmd="${2:?missing value for --cmd}"
      shift 2
      ;;
    --control-node)
      control_node="${2:?missing value for --control-node}"
      shift 2
      ;;
    --alias)
      jumpserver_alias="${2:?missing value for --alias}"
      shift 2
      ;;
    --jumpserver-host)
      jumpserver_host="${2:?missing value for --jumpserver-host}"
      shift 2
      ;;
    --jumpserver-user)
      jumpserver_user="${2:?missing value for --jumpserver-user}"
      shift 2
      ;;
    --jumpserver-port)
      jumpserver_port="${2:?missing value for --jumpserver-port}"
      shift 2
      ;;
    --jumpserver-identity-file)
      jumpserver_identity_file="${2:?missing value for --jumpserver-identity-file}"
      shift 2
      ;;
    --jumpserver-password-file)
      jumpserver_password_file="${2:?missing value for --jumpserver-password-file}"
      shift 2
      ;;
    --auth-profile)
      auth_profile="${2:?missing value for --auth-profile}"
      shift 2
      ;;
    --save-auth-profile)
      save_auth_profile="1"
      shift
      ;;
    --asset-id)
      asset_id="${2:?missing value for --asset-id}"
      shift 2
      ;;
    --timeout)
      single_timeout="${2:?missing value for --timeout}"
      shift 2
      ;;
    --no-root)
      become_root="0"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      remote_cmd="$*"
      break
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$via_target" == -* ]]; then
  echo "--via value must not start with '-': $via_target" >&2
  exit 2
fi

user_ssh_config() {
  if [[ -r "${HOME}/.ssh/config" ]]; then
    printf '%s\n' "${HOME}/.ssh/config"
  else
    printf '/dev/null\n'
  fi
}

target_from_env() {
  local value="$1"
  if [[ "$value" =~ ^[Bb][Jj]-?([0-9]+)$ ]]; then
    printf '172.%s.0.2\n' "${BASH_REMATCH[1]}"
    return 0
  fi
  return 1
}

ssh_config_value() {
  local host="$1"
  local key="$2"

  ssh -F "$(user_ssh_config)" -G "$host" 2>/dev/null | awk -v want="$key" '
    $1 == want {
      print $2
      exit
    }
  '
}

has_direct_target_ssh_config() {
  local host="${1:?missing host}"
  local resolved_host resolved_port

  resolved_host="$(ssh_config_value "$host" hostname || true)"
  resolved_port="$(ssh_config_value "$host" port || true)"

  [[ -n "$resolved_host" && "$resolved_host" != "$host" ]] || return 1
  [[ -n "$resolved_port" && "$resolved_port" != "22" ]] || return 1
  return 0
}

has_jumpserver_alias_ssh_config() {
  local alias="${1:?missing alias}"
  local resolved_host resolved_port

  resolved_host="$(ssh_config_value "$alias" hostname || true)"
  resolved_port="$(ssh_config_value "$alias" port || true)"

  [[ -n "$resolved_host" && "$resolved_host" != "$alias" ]] || return 1
  [[ -n "$resolved_port" && "$resolved_port" != "22" ]] || return 1
  return 0
}

if [[ -z "$target" && -n "$env_name" ]]; then
  if ! target="$(target_from_env "$env_name")"; then
    echo "unsupported --env value: $env_name" >&2
    exit 2
  fi
  if [[ -z "$asset_name" ]]; then
    asset_name="$env_name"
  fi
fi

if [[ -n "$target" ]]; then
  if converted="$(target_from_env "$target")"; then
    target="$converted"
  fi
fi

detect_mode() {
  if [[ -n "$target" && "$target" == 172.18.* ]]; then
    printf 'jump18\n'
  elif [[ -n "$target" && "$target" =~ ^172\.[0-9]+\.0\.2$ ]]; then
    if has_direct_target_ssh_config "$target"; then
      printf 'ssh\n'
    else
      printf 'jumpserver\n'
    fi
  elif [[ -n "$target" ]]; then
    printf 'ssh\n'
  elif [[ -n "$asset_name" ]]; then
    printf 'jumpserver\n'
  else
    echo "missing --target, --env, or --asset" >&2
    exit 2
  fi
}

requested_mode="$mode"

if [[ "$mode" == "auto" ]]; then
  mode="$(detect_mode)"
fi

ssh_destination() {
  if [[ "$target" == *@* ]]; then
    printf '%s\n' "$target"
  elif [[ "$target" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ && ! "$target" =~ ^172\.[0-9]+\.0\.2$ ]]; then
    printf 'root@%s\n' "$target"
  else
    printf '%s\n' "$target"
  fi
}

target_uses_interactive_ssh_config() {
  [[ "$target" =~ ^172\.[0-9]+\.0\.2$ ]] && has_direct_target_ssh_config "$target"
}

command_retry_safe() {
  local cmd="${remote_cmd,,}"
  local service_restart_re='service[[:space:]][^;|&]+[[:space:]]+restart'

  [[ -n "$cmd" ]] || return 1

  if [[ "$cmd" =~ kubectl[[:space:]]+(edit|delete|apply|patch|scale) ]]; then
    return 1
  fi
  if [[ "$cmd" =~ kubectl[[:space:]]+rollout[[:space:]]+restart ]]; then
    return 1
  fi
  if [[ "$cmd" =~ helm[[:space:]]+rollback ]]; then
    return 1
  fi
  if [[ "$cmd" =~ systemctl[[:space:]]+restart ]]; then
    return 1
  fi
  if [[ "$cmd" =~ $service_restart_re ]]; then
    return 1
  fi
  if [[ "$cmd" =~ mysql.*[[:space:]](update|delete|insert|alter|drop)[[:space:]] ]]; then
    return 1
  fi
  if [[ "$cmd" =~ openstack[[:space:]].*[[:space:]](create|delete|set|unset|add|remove|reboot|start|stop|suspend|resume|migrate|resize|evacuate)[[:space:]] ]]; then
    return 1
  fi
  if [[ "$cmd" =~ cinder[[:space:]].*[[:space:]](create|delete|set|reset-state|manage|unmanage)[[:space:]] ]]; then
    return 1
  fi
  if [[ "$cmd" =~ curl.*-x[[:space:]]+(post|put|patch|delete) ]]; then
    return 1
  fi
  if [[ "$cmd" =~ curl.*--request[[:space:]]+(post|put|patch|delete) ]]; then
    return 1
  fi
  return 0
}

command_timeout_ladder() {
  local cmd="${remote_cmd,,}"

  if [[ -n "$single_timeout" ]]; then
    printf '%s\n' "$single_timeout"
    return
  fi
  if [[ -z "$remote_cmd" ]]; then
    printf '60\n'
    return
  fi
  if ! command_retry_safe; then
    printf '60\n'
    return
  fi

  if [[ "$cmd" =~ (zgrep|zcat|/var/www/html/td-agent|journalctl|find[[:space:]]|du[[:space:]]|kubectl[[:space:]]+describe|helm[[:space:]]+history) ]]; then
    printf '%s\n' 30 45 60
  elif [[ "$cmd" =~ (kubectl[[:space:]]+get[[:space:]]+pods|kubectl[[:space:]]+logs|grep|openstack[[:space:]].*[[:space:]]list|cinder[[:space:]]+list|nova[[:space:]]+list|mysql) ]]; then
    printf '%s\n' 15 20 30 45 60
  else
    printf '%s\n' 10 15 20 30 45 60
  fi
}

run_with_timeout_ladder() {
  local label="$1"
  shift

  if [[ -z "$remote_cmd" ]]; then
    "$@"
    return
  fi

  if [[ -n "$single_timeout" ]] || ! command_retry_safe; then
    CURRENT_TIMEOUT="$(command_timeout_ladder | tail -1)"
    "$@"
    return
  fi

  local timeout_value rc
  for timeout_value in $(command_timeout_ladder); do
    echo "try $label timeout: ${timeout_value}s" >&2
    set +e
    CURRENT_TIMEOUT="$timeout_value" "$@"
    rc=$?
    set -e
    if [[ "$rc" -eq 0 ]]; then
      return 0
    fi
    if [[ "$rc" -ne 124 ]]; then
      return "$rc"
    fi
    echo "$label timed out after ${timeout_value}s" >&2
  done
  return 124
}

run_ssh_config_expect() {
  local timeout_value="${CURRENT_TIMEOUT:-${single_timeout:-60}}"

  SSH_TARGET="$target" \
  SSH_VIA_TARGET="$via_target" \
  SSH_CONFIG_FILE="$(user_ssh_config)" \
  SSH_REMOTE_CMD="$remote_cmd" \
  SSH_BECOME_ROOT="$become_root" \
  SSH_TIMEOUT="$timeout_value" \
  expect <<'EXPECT'
set timeout $env(SSH_TIMEOUT)
set target $env(SSH_TARGET)
set via_target $env(SSH_VIA_TARGET)
set ssh_config_file $env(SSH_CONFIG_FILE)
set remote_cmd $env(SSH_REMOTE_CMD)
set become_root $env(SSH_BECOME_ROOT)
set shell_re {\[[^]]+@[^]]+[[:space:]]+[^]]+\][#$][[:space:]]*$}
set root_re {\[root@[^]]+[[:space:]]+[^]]+\]#[[:space:]]*$}

proc fail {code message} {
    send_user "$message\n"
    exit $code
}

if {$via_target ne ""} {
    spawn ssh -tt -F $ssh_config_file -J $via_target $target
} else {
    spawn ssh -tt -F $ssh_config_file $target
}

expect {
    "Are you sure you want to continue connecting" {
        send "yes\r"
        exp_continue
    }
    -re {开始连接到|Last login|Authorized users only|复用SSH连接} {
        exp_continue
    }
    -re $shell_re {
        send_user "connected to target asset\n"
    }
    "Permission denied" {
        fail 2 "SSH authentication failed"
    }
    timeout {
        fail 124 "timeout connecting to target asset"
    }
    eof {
        fail 2 "connection closed while connecting to target asset"
    }
}

if {$become_root eq "1"} {
    send "sudo su -\r"
    expect {
        -re $root_re {
            send_user "became root\n"
        }
        "not in the sudoers" {
            fail 2 "sudo permission denied"
        }
        "password" {
            fail 2 "sudo su - requires password"
        }
        timeout {
            send "exit\r"
            fail 124 "timeout becoming root"
        }
        eof {
            fail 2 "connection closed while becoming root"
        }
    }
}

if {$remote_cmd ne ""} {
    send -- "$remote_cmd\r"
    expect {
        -re $shell_re {}
        timeout {
            send "\003"
            send "exit\r"
            fail 124 "timeout waiting for command prompt"
        }
        eof {
            fail 2 "connection closed while running command"
        }
    }
    send "exit\r"
    expect {
        -re $shell_re {
            send "exit\r"
            expect {
                eof {}
                timeout { exit 0 }
            }
        }
        eof {}
        timeout { exit 0 }
    }
    exit 0
}

send "cd ~\r"
interact
EXPECT
}

run_ssh_target() {
  if [[ "$target" =~ ^172\.[0-9]+\.0\.2$ ]] && ! has_direct_target_ssh_config "$target"; then
    if [[ -n "$asset_name" ]]; then
      run_jumpserver
      return
    fi
    echo "no usable SSH config for $target; add a Host 172.*.0.2 entry or pass JumpServer auth info" >&2
    exit 2
  fi

  if target_uses_interactive_ssh_config; then
    run_ssh_config_expect
    return
  fi

  local destination
  destination="$(ssh_destination)"
  local destination_is_root="0"
  if [[ "$destination" == root@* ]]; then
    destination_is_root="1"
  fi
  local ssh_opts=(
    -F "$(user_ssh_config)"
  )
  if [[ -n "$via_target" ]]; then
    ssh_opts+=(-J "$via_target")
  fi
  ssh_opts+=(
    -o StrictHostKeyChecking=no
    -o UserKnownHostsFile=/dev/null
    -o ConnectTimeout=8
  )

  if [[ -n "$remote_cmd" ]]; then
    if [[ "$become_root" == "1" && "$destination_is_root" == "0" ]]; then
      timeout "${CURRENT_TIMEOUT:-60}" ssh "${ssh_opts[@]}" "$destination" 'sudo -n bash -s' <<<"$remote_cmd"
    else
      timeout "${CURRENT_TIMEOUT:-60}" ssh "${ssh_opts[@]}" "$destination" 'bash -s' <<<"$remote_cmd"
    fi
  else
    if [[ "$become_root" == "1" && "$destination_is_root" == "0" ]]; then
      ssh -tt "${ssh_opts[@]}" "$destination" 'sudo su -'
    else
      ssh -tt "${ssh_opts[@]}" "$destination"
    fi
  fi
}

run_jump18() {
  local outer=(
    sshpass -p "easystack" ssh
    -F "$(user_ssh_config)"
  )
  if [[ -n "$via_target" ]]; then
    outer+=(-J "$via_target")
  fi
  outer+=(
    -o StrictHostKeyChecking=no
    -o UserKnownHostsFile=/dev/null
    -o ConnectTimeout=8
  )
  local inner=(
    ssh
    -F /dev/null
    -i /root/.ssh/id_rsa.roller
    -o StrictHostKeyChecking=no
    -o UserKnownHostsFile=/dev/null
    -o ConnectTimeout=5
    "root@$control_node"
  )
  local inner_cmd

  printf -v inner_cmd '%q ' "${inner[@]}"

  if [[ -n "$remote_cmd" ]]; then
    timeout "${CURRENT_TIMEOUT:-60}" "${outer[@]}" "root@$target" "${inner_cmd} bash -s" <<<"$remote_cmd"
  else
    "${outer[@]}" -tt "root@$target" "${inner_cmd}"
  fi
}

run_jumpserver() {
  local args=(--alias "$jumpserver_alias")

  if [[ -n "$via_target" ]]; then
    args+=(--via "$via_target")
  fi
  if [[ -n "$asset_name" ]]; then
    args+=(--asset "$asset_name")
  elif [[ -n "$target" ]]; then
    args+=(--asset "$target")
  else
    echo "jumpserver mode requires --asset or --target" >&2
    exit 2
  fi

  if [[ -n "$asset_id" ]]; then
    args+=(--asset-id "$asset_id")
  fi
  if [[ -n "${CURRENT_TIMEOUT:-}" ]]; then
    args+=(--timeout "$CURRENT_TIMEOUT")
  elif [[ -n "$single_timeout" ]]; then
    args+=(--timeout "$single_timeout")
  fi
  if [[ "$become_root" == "0" ]]; then
    args+=(--no-root)
  fi
  if [[ -n "$remote_cmd" ]]; then
    args+=(--cmd "$remote_cmd")
  fi
  if [[ -n "$jumpserver_host" ]]; then
    args+=(--jumpserver-host "$jumpserver_host")
  fi
  if [[ -n "$jumpserver_user" ]]; then
    args+=(--jumpserver-user "$jumpserver_user")
  fi
  if [[ -n "$jumpserver_port" ]]; then
    args+=(--jumpserver-port "$jumpserver_port")
  fi
  if [[ -n "$jumpserver_identity_file" ]]; then
    args+=(--jumpserver-identity-file "$jumpserver_identity_file")
  fi
  if [[ -n "$jumpserver_password_file" ]]; then
    args+=(--jumpserver-password-file "$jumpserver_password_file")
  fi
  if [[ -n "$auth_profile" ]]; then
    args+=(--auth-profile "$auth_profile")
  fi
  if [[ "$save_auth_profile" == "1" ]]; then
    args+=(--save-auth-profile)
  fi

  if [[ -z "$jumpserver_host$auth_profile" ]] &&
      ! has_jumpserver_alias_ssh_config "$jumpserver_alias"; then
    echo "missing JumpServer SSH config for alias $jumpserver_alias" >&2
    echo "Provide --jumpserver-host/--jumpserver-user/--jumpserver-port/--jumpserver-identity-file or add a Host $jumpserver_alias block to ~/.ssh/config" >&2
    exit 2
  fi

  bash "$script_dir/jumpserver-env.sh" "${args[@]}"
}

case "$mode" in
  ssh)
    [[ -n "$target" ]] || { echo "ssh mode requires --target or --env" >&2; exit 2; }
    set +e
    run_with_timeout_ladder "ssh command" run_ssh_target
    ssh_rc=$?
    set -e
    if [[ "$ssh_rc" -eq 0 ]]; then
      exit 0
    fi
    if [[ "$requested_mode" == "auto" && -n "$asset_name" ]]; then
      echo "ssh mode failed, falling back to JumpServer menu for asset: $asset_name" >&2
      run_with_timeout_ladder "JumpServer command" run_jumpserver
    else
      exit "$ssh_rc"
    fi
    ;;
  jump18)
    [[ -n "$target" ]] || { echo "jump18 mode requires --target" >&2; exit 2; }
    run_with_timeout_ladder "jump18 command" run_jump18
    ;;
  jumpserver)
    run_with_timeout_ladder "JumpServer command" run_jumpserver
    ;;
  *)
    echo "unsupported --mode: $mode" >&2
    usage >&2
    exit 2
    ;;
esac
