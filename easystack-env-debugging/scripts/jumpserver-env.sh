#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash jumpserver-env.sh --asset <ASSET_NAME> [--alias js] [--via <SSH_TARGET>]
  bash jumpserver-env.sh --asset <ASSET_NAME> --cmd 'whoami; id -u; hostname; pwd'

Options:
  --alias NAME       SSH config alias for JumpServer. Default: js
  --via SSH_TARGET   Reach JumpServer through one ordinary SSH jump host.
  --jumpserver-host HOST
                     JumpServer SSH host when SSH config is unavailable.
  --jumpserver-user USER
                     JumpServer SSH user when SSH config is unavailable.
  --jumpserver-port PORT
                     JumpServer SSH port when SSH config is unavailable.
  --jumpserver-identity-file PATH
                     JumpServer SSH identity file when SSH config is unavailable.
  --jumpserver-password-file PATH
                     Read the JumpServer password from a file.
  --auth-profile NAME Load a temporary authentication profile from /tmp.
  --save-auth-profile
                     Save supplied authentication data to --auth-profile.
  --asset NAME       JumpServer asset name or search text. Required.
  --query TEXT       JumpServer menu query. Default: same as --asset
  --asset-id ID      Asset ID to select after --query enters [Host]>.
  --cmd COMMAND      Run one command after sudo root, then exit cleanly.
  --timeout SECONDS  Use one timeout instead of retry ladder.
  --no-root          Do not run sudo su - after connecting to the asset.
  -h, --help         Show this help.

Default behavior opens an interactive root shell on the target asset.
EOF
}

jumpserver_alias="js"
via_target=""
jumpserver_host=""
jumpserver_user=""
jumpserver_port=""
jumpserver_identity_file=""
jumpserver_password_file=""
auth_profile=""
save_auth_profile="0"
asset_name=""
asset_query=""
asset_id=""
remote_cmd=""
single_timeout=""
become_root="1"
if [[ -r "${HOME}/.ssh/config" ]]; then
  ssh_config="${HOME}/.ssh/config"
else
  ssh_config="/dev/null"
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --alias)
      jumpserver_alias="${2:?missing value for --alias}"
      shift 2
      ;;
    --via)
      via_target="${2:?missing value for --via}"
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
    --asset)
      asset_name="${2:?missing value for --asset}"
      shift 2
      ;;
    --query)
      asset_query="${2:?missing value for --query}"
      shift 2
      ;;
    --asset-id)
      asset_id="${2:?missing value for --asset-id}"
      shift 2
      ;;
    --cmd)
      remote_cmd="${2:?missing value for --cmd}"
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

auth_cache_root="${EASYSTACK_AUTH_CACHE_DIR:-/tmp/easystack-env-access-${UID}}"
profile_dir=""

secure_cache_dir() {
  local path="$1"
  local owner

  if [[ -L "$path" ]]; then
    echo "authentication cache path must not be a symlink: $path" >&2
    exit 2
  fi
  if [[ -e "$path" ]]; then
    [[ -d "$path" ]] || {
      echo "authentication cache path is not a directory: $path" >&2
      exit 2
    }
    owner="$(stat -c '%u' "$path")"
    [[ "$owner" == "$UID" ]] || {
      echo "authentication cache path is not owned by current user: $path" >&2
      exit 2
    }
    chmod 700 "$path"
  else
    mkdir -m 700 "$path"
  fi
}

load_profile_value() {
  local variable_name="$1"
  local path="$2"
  local current_value="${!variable_name}"

  if [[ -z "$current_value" && -f "$path" ]]; then
    printf -v "$variable_name" '%s' "$(<"$path")"
  fi
}

secure_profile_file() {
  local path="$1"
  local owner

  [[ -e "$path" || -L "$path" ]] || return 0
  if [[ -L "$path" || ! -f "$path" ]]; then
    echo "authentication profile entry must be a regular file: $path" >&2
    exit 2
  fi
  owner="$(stat -c '%u' "$path")"
  [[ "$owner" == "$UID" ]] || {
    echo "authentication profile entry has an invalid owner: $path" >&2
    exit 2
  }
  chmod 600 "$path"
}

if [[ -n "$auth_profile" ]]; then
  if [[ ! "$auth_profile" =~ ^[A-Za-z0-9_.-]+$ ]]; then
    echo "invalid --auth-profile name: $auth_profile" >&2
    exit 2
  fi
  umask 077
  secure_cache_dir "$auth_cache_root"
  secure_cache_dir "$auth_cache_root/profiles"
  profile_dir="$auth_cache_root/profiles/$auth_profile"
  if [[ "$save_auth_profile" == "1" || -e "$profile_dir" ||
        -L "$profile_dir" ]]; then
    secure_cache_dir "$profile_dir"
  fi
  if [[ -d "$profile_dir" ]]; then
    for profile_entry in via host user port identity password; do
      secure_profile_file "$profile_dir/$profile_entry"
    done
    load_profile_value via_target "$profile_dir/via"
    load_profile_value jumpserver_host "$profile_dir/host"
    load_profile_value jumpserver_user "$profile_dir/user"
    load_profile_value jumpserver_port "$profile_dir/port"
    if [[ -z "$jumpserver_identity_file" && -f "$profile_dir/identity" ]]; then
      jumpserver_identity_file="$profile_dir/identity"
    fi
    if [[ -z "$jumpserver_password_file" && -f "$profile_dir/password" ]]; then
      jumpserver_password_file="$profile_dir/password"
    fi
  elif [[ "$save_auth_profile" != "1" ]]; then
    echo "authentication profile not found: $auth_profile" >&2
    exit 2
  fi
elif [[ "$save_auth_profile" == "1" ]]; then
  echo "--save-auth-profile requires --auth-profile" >&2
  exit 2
fi

if [[ -z "$asset_name" && -z "$asset_query" ]]; then
  echo "missing required --asset or --query" >&2
  usage >&2
  exit 2
fi

if [[ -z "$asset_query" ]]; then
  asset_query="$asset_name"
fi

expand_tilde_path() {
  local value="$1"
  if [[ "$value" == "~/"* ]]; then
    printf '%s\n' "${HOME}/${value#~/}"
  else
    printf '%s\n' "$value"
  fi
}

if [[ -n "$jumpserver_identity_file" ]]; then
  jumpserver_identity_file="$(expand_tilde_path "$jumpserver_identity_file")"
fi

if [[ -n "$jumpserver_host$jumpserver_user$jumpserver_port$jumpserver_identity_file$jumpserver_password_file" ]]; then
  if [[ -z "$jumpserver_host" || -z "$jumpserver_user" ||
        -z "$jumpserver_port" ||
        -z "$jumpserver_identity_file$jumpserver_password_file" ]]; then
    echo "jumpserver overrides require host, user, port, and identity or password file" >&2
    exit 2
  fi
fi

if [[ -n "$jumpserver_identity_file" && ! -r "$jumpserver_identity_file" ]]; then
  echo "JumpServer identity file is not readable: $jumpserver_identity_file" >&2
  exit 2
fi
if [[ -n "$jumpserver_password_file" && ! -r "$jumpserver_password_file" ]]; then
  echo "JumpServer password file is not readable" >&2
  exit 2
fi

if [[ "$save_auth_profile" == "1" ]]; then
  umask 077
  install -d -m 700 "$profile_dir"
  printf '%s' "$via_target" >"$profile_dir/via"
  printf '%s' "$jumpserver_host" >"$profile_dir/host"
  printf '%s' "$jumpserver_user" >"$profile_dir/user"
  printf '%s' "$jumpserver_port" >"$profile_dir/port"
  chmod 600 "$profile_dir"/{via,host,user,port}

  if [[ -n "$jumpserver_identity_file" &&
        "$jumpserver_identity_file" != "$profile_dir/identity" ]]; then
    install -m 600 "$jumpserver_identity_file" "$profile_dir/identity"
  fi
  if [[ -n "$jumpserver_password_file" &&
        "$jumpserver_password_file" != "$profile_dir/password" ]]; then
    install -m 600 "$jumpserver_password_file" "$profile_dir/password"
  fi
  [[ -f "$profile_dir/identity" ]] &&
    jumpserver_identity_file="$profile_dir/identity"
  [[ -f "$profile_dir/password" ]] &&
    jumpserver_password_file="$profile_dir/password"
fi

jumpserver_password=""
if [[ -n "$jumpserver_password_file" ]]; then
  IFS= read -r jumpserver_password <"$jumpserver_password_file" || true
fi

build_ssh_spawn_script() {
  local -a cmd=(
    ssh
    -tt
    -o StrictHostKeyChecking=no
    -o UserKnownHostsFile=/dev/null
    -o ConnectTimeout=8
    -F "$ssh_config"
  )

  if [[ -n "$via_target" ]]; then
    cmd+=(-J "$via_target")
  fi

  if [[ -n "$jumpserver_host" ]]; then
    if [[ -z "$jumpserver_user" || -z "$jumpserver_port" ||
          -z "$jumpserver_identity_file$jumpserver_password_file" ]]; then
      echo "jumpserver overrides require host, user, port, and identity or password file" >&2
      exit 2
    fi
    cmd+=(
      -o "HostName=$jumpserver_host"
      -o "User=$jumpserver_user"
      -o "Port=$jumpserver_port"
    )
    if [[ -n "$jumpserver_identity_file" ]]; then
      cmd+=(-i "$(expand_tilde_path "$jumpserver_identity_file")")
    else
      cmd+=(
        -o PubkeyAuthentication=no
        -o PreferredAuthentications=password,keyboard-interactive
      )
    fi
    cmd+=("$jumpserver_host")
  else
    cmd+=("$jumpserver_alias")
  fi

  local snippet="exec"
  local part quoted
  for part in "${cmd[@]}"; do
    printf -v quoted '%q' "$part"
    snippet+=" $quoted"
  done
  printf '%s\n' "$snippet"
}

if [[ -n "$single_timeout" ]]; then
  timeouts=("$single_timeout")
else
  timeouts=(10 15 20 30 45 60)
fi

run_expect() {
  local timeout_value="$1"
  JS_ALIAS="$jumpserver_alias" \
  JS_ASSET_QUERY="$asset_query" \
  JS_ASSET_ID="$asset_id" \
  JS_REMOTE_CMD="$remote_cmd" \
  JS_BECOME_ROOT="$become_root" \
  JS_SPAWN_SCRIPT="$(build_ssh_spawn_script)" \
  JS_PASSWORD="$jumpserver_password" \
  JS_TIMEOUT="$timeout_value" \
  expect <<'EXPECT'
set timeout $env(JS_TIMEOUT)
set jumpserver_alias $env(JS_ALIAS)
set asset_query $env(JS_ASSET_QUERY)
set asset_id $env(JS_ASSET_ID)
set remote_cmd $env(JS_REMOTE_CMD)
set become_root $env(JS_BECOME_ROOT)
set spawn_script $env(JS_SPAWN_SCRIPT)
set jumpserver_password $env(JS_PASSWORD)
set ssh_config "$env(HOME)/.ssh/config"
set shell_re {\[[^]]+@[^]]+[[:space:]]+[^]]+\][#$][[:space:]]*$}
set root_re {\[root@[^]]+[[:space:]]+[^]]+\]#[[:space:]]*$}
set menu_re {Opt>|\[Host\]>}

proc fail {code message} {
    send_user "$message\n"
    exit $code
}

proc close_from_shell {shell_re menu_re} {
    send "exit\r"
    expect {
        -re $menu_re {
            send "q\r"
            expect {
                eof {}
                timeout { exit 0 }
            }
        }
        -re $shell_re {
            send "exit\r"
            expect {
                -re $menu_re {
                    send "q\r"
                    expect {
                        eof {}
                        timeout { exit 0 }
                    }
                }
                eof {}
                timeout { exit 0 }
            }
        }
        eof {}
        timeout { exit 0 }
    }
}

spawn sh -c "$spawn_script"

expect {
    -nocase -re {password:} {
        if {$jumpserver_password eq ""} {
            fail 2 "JumpServer password is required"
        }
        send -- "$jumpserver_password\r"
        exp_continue
    }
    -re $menu_re {
        send_user "entered JumpServer menu\n"
    }
    "Bad owner or permissions" {
        fail 2 "ssh config permissions error"
    }
    "Permission denied" {
        fail 2 "JumpServer SSH authentication failed"
    }
    timeout {
        fail 124 "timeout waiting for JumpServer menu"
    }
    eof {
        fail 2 "JumpServer connection closed before menu"
    }
}

send -- "$asset_query\r"

expect {
    -re {\[Host\]>} {
        if {$asset_id ne ""} {
            send -- "$asset_id\r"
        } else {
            send -- "$asset_query\r"
        }
        exp_continue
    }
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
    timeout {
        send "exit\r"
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
    close_from_shell $shell_re $menu_re
    exit 0
}

send "cd ~\r"
interact
EXPECT
}

last_status=0
for timeout_value in "${timeouts[@]}"; do
  echo "try JumpServer timeout: ${timeout_value}s" >&2
  if run_expect "$timeout_value"; then
    exit 0
  fi
  last_status=$?
  if [[ "$last_status" -ne 124 ]]; then
    exit "$last_status"
  fi
done

exit "$last_status"
