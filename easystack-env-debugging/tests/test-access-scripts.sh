#!/usr/bin/env bash
set -euo pipefail

skill_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
test_root=$(mktemp -d /tmp/easystack-env-access-test.XXXXXX)
trap 'rm -rf -- "$test_root"' EXIT
fake_bin=$test_root/bin
mkdir -p "$fake_bin"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

assert_contains() {
  local file=$1 expected=$2
  grep -F -- "$expected" "$file" >/dev/null || fail "$file missing: $expected"
}

assert_contains "$skill_dir/SKILL.md" \
  "第一项环境相关命令 MUST 直接调用"
assert_contains "$skill_dir/SKILL.md" \
  "不要先读取组件参考文档"
assert_contains "$skill_dir/access.md" \
  'env-access.sh` 会通过'
assert_contains "$skill_dir/SKILL.md" \
  "[alcubierre-unmap.md](alcubierre-unmap.md)"
assert_contains "$skill_dir/alcubierre-unmap.md" \
  "获得一次批量确认后才能"
assert_contains "$skill_dir/alcubierre-unmap.md" \
  "停止处理后续 UUID"
assert_contains "$skill_dir/access.md" \
  "临时认证 Profile"

bash "$skill_dir/scripts/env-access.sh" --help >"$test_root/env-help"
assert_contains "$test_root/env-help" "Usage:"

set +e
bash "$skill_dir/scripts/env-access.sh" --env invalid >"$test_root/out" 2>"$test_root/err"
rc=$?
set -e
[[ $rc -eq 2 ]] || fail "invalid env returned $rc"
assert_contains "$test_root/err" "unsupported --env value"

cat >"$fake_bin/timeout" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$*" >>"$ACCESS_TEST_LOG"
cat >/dev/null
exit "${ACCESS_TIMEOUT_RC:-0}"
EOF
chmod +x "$fake_bin/timeout"

ACCESS_TEST_LOG=$test_root/timeout.log PATH="$fake_bin:$PATH" \
  bash "$skill_dir/scripts/env-access.sh" --target 192.0.2.10 --mode ssh \
  --no-root --timeout 1 -- hostname
assert_contains "$test_root/timeout.log" "-F $HOME/.ssh/config"
assert_contains "$test_root/timeout.log" "root@192.0.2.10"

: >"$test_root/timeout.log"
ACCESS_TEST_LOG=$test_root/timeout.log PATH="$fake_bin:$PATH" \
  bash "$skill_dir/scripts/env-access.sh" --via eswork \
  --target 192.0.2.10 --mode ssh --no-root --timeout 1 -- hostname
assert_contains "$test_root/timeout.log" "-J eswork"
assert_contains "$test_root/timeout.log" "root@192.0.2.10"

: >"$test_root/timeout.log"
ACCESS_TEST_LOG=$test_root/timeout.log PATH="$fake_bin:$PATH" \
  bash "$skill_dir/scripts/env-access.sh" --via eswork \
  --target 172.18.0.118 --mode jump18 --control-node 10.20.0.3 \
  --no-root --timeout 1 -- hostname
assert_contains "$test_root/timeout.log" "-J eswork"
assert_contains "$test_root/timeout.log" "root@172.18.0.118"

: >"$test_root/timeout.log"
ACCESS_TEST_LOG=$test_root/timeout.log PATH="$fake_bin:$PATH" \
  bash "$skill_dir/scripts/env-access.sh" \
  --target 172.18.0.118 --mode jump18 --control-node 10.20.0.3 \
  --no-root --timeout 1 -- hostname
assert_contains "$test_root/timeout.log" "-F $HOME/.ssh/config"
assert_contains "$test_root/timeout.log" "root@172.18.0.118"

: >"$test_root/timeout.log"
set +e
ACCESS_TEST_LOG=$test_root/timeout.log ACCESS_TIMEOUT_RC=124 PATH="$fake_bin:$PATH" \
  bash "$skill_dir/scripts/env-access.sh" --target 192.0.2.10 --mode ssh \
  --no-root -- "openstack server delete test"
rc=$?
set -e
[[ $rc -eq 124 ]] || fail "destructive timeout returned $rc"
[[ $(wc -l <"$test_root/timeout.log") -eq 1 ]] ||
  fail "destructive command was retried"

: >"$test_root/timeout.log"
set +e
ACCESS_TEST_LOG=$test_root/timeout.log ACCESS_TIMEOUT_RC=124 PATH="$fake_bin:$PATH" \
  bash "$skill_dir/scripts/env-access.sh" --target 192.0.2.10 --mode ssh \
  --no-root -- \
  "curl -X POST http://alcubierre/v2/volumes/id/disconnections"
rc=$?
set -e
[[ $rc -eq 124 ]] || fail "Alcubierre POST timeout returned $rc"
[[ $(wc -l <"$test_root/timeout.log") -eq 1 ]] ||
  fail "Alcubierre POST command was retried"

bash "$skill_dir/scripts/jumpserver-env.sh" --help >"$test_root/js-help"
assert_contains "$test_root/js-help" "Usage:"

set +e
bash "$skill_dir/scripts/jumpserver-env.sh" --asset node --jumpserver-host host \
  >"$test_root/out" 2>"$test_root/err"
rc=$?
set -e
[[ $rc -eq 2 ]] || fail "partial JumpServer override returned $rc"
assert_contains "$test_root/err" "jumpserver overrides require"

cat >"$fake_bin/expect" <<'EOF'
#!/usr/bin/env bash
if [[ -n "${EXPECTED_JS_PASSWORD:-}" &&
      "$JS_PASSWORD" != "$EXPECTED_JS_PASSWORD" ]]; then
  exit 3
fi
printf '%s|%s|%s|%s\n' \
  "$JS_ASSET_QUERY" "$JS_REMOTE_CMD" "$JS_BECOME_ROOT" "$JS_SPAWN_SCRIPT" \
  >"$ACCESS_TEST_LOG"
cat >/dev/null
EOF
chmod +x "$fake_bin/expect"
touch "$test_root/id"
ACCESS_TEST_LOG=$test_root/expect.log PATH="$fake_bin:$PATH" \
  bash "$skill_dir/scripts/jumpserver-env.sh" --asset node --cmd hostname --no-root \
  --jumpserver-host host --jumpserver-user user --jumpserver-port 2222 \
  --jumpserver-identity-file "$test_root/id" --timeout 1
assert_contains "$test_root/expect.log" "node|hostname|0"

ACCESS_TEST_LOG=$test_root/expect.log PATH="$fake_bin:$PATH" \
  bash "$skill_dir/scripts/jumpserver-env.sh" --via eswork \
  --asset node --cmd hostname --no-root \
  --jumpserver-host host --jumpserver-user user --jumpserver-port 2222 \
  --jumpserver-identity-file "$test_root/id" --timeout 1
assert_contains "$test_root/expect.log" "-J eswork"

ACCESS_TEST_LOG=$test_root/expect.log PATH="$fake_bin:$PATH" \
  bash "$skill_dir/scripts/env-access.sh" --via eswork \
  --asset node --mode jumpserver --cmd hostname --no-root \
  --jumpserver-host host --jumpserver-user user --jumpserver-port 2222 \
  --jumpserver-identity-file "$test_root/id" --timeout 1
assert_contains "$test_root/expect.log" "-J eswork"
assert_contains "$test_root/expect.log" "node|hostname|0"

printf '%s\n' 'profile-password' >"$test_root/password"
chmod 600 "$test_root/password"
profile_cache=$test_root/auth-cache

ACCESS_TEST_LOG=$test_root/expect.log \
EXPECTED_JS_PASSWORD=profile-password PATH="$fake_bin:$PATH" \
  bash "$skill_dir/scripts/jumpserver-env.sh" --asset node --cmd hostname --no-root \
  --jumpserver-host host --jumpserver-user user --jumpserver-port 2222 \
  --jumpserver-password-file "$test_root/password" --timeout 1
assert_contains "$test_root/expect.log" "PubkeyAuthentication=no"

ACCESS_TEST_LOG=$test_root/expect.log \
EXPECTED_JS_PASSWORD=profile-password \
EASYSTACK_AUTH_CACHE_DIR=$profile_cache PATH="$fake_bin:$PATH" \
  bash "$skill_dir/scripts/jumpserver-env.sh" --via eswork \
  --auth-profile bj-123 --save-auth-profile \
  --asset node --cmd hostname --no-root \
  --jumpserver-host host --jumpserver-user user --jumpserver-port 2222 \
  --jumpserver-identity-file "$test_root/id" \
  --jumpserver-password-file "$test_root/password" --timeout 1

[[ $(stat -c '%a' "$profile_cache/profiles/bj-123") == 700 ]] ||
  fail "auth profile directory permissions are not 700"
[[ $(stat -c '%a' "$profile_cache") == 700 ]] ||
  fail "auth cache root permissions are not 700"
[[ $(stat -c '%a' "$profile_cache/profiles/bj-123/password") == 600 ]] ||
  fail "cached password permissions are not 600"
[[ $(stat -c '%a' "$profile_cache/profiles/bj-123/identity") == 600 ]] ||
  fail "cached identity permissions are not 600"

ACCESS_TEST_LOG=$test_root/expect.log \
EXPECTED_JS_PASSWORD=profile-password \
EASYSTACK_AUTH_CACHE_DIR=$profile_cache PATH="$fake_bin:$PATH" \
  bash "$skill_dir/scripts/jumpserver-env.sh" \
  --auth-profile bj-123 --asset node --cmd hostname --no-root --timeout 1
assert_contains "$test_root/expect.log" "-J eswork"
assert_contains "$test_root/expect.log" "HostName=host"

ACCESS_TEST_LOG=$test_root/expect.log \
EXPECTED_JS_PASSWORD=profile-password \
EASYSTACK_AUTH_CACHE_DIR=$profile_cache PATH="$fake_bin:$PATH" \
  bash "$skill_dir/scripts/env-access.sh" \
  --auth-profile bj-123 --asset node --mode jumpserver \
  --cmd hostname --no-root --timeout 1
assert_contains "$test_root/expect.log" "-J eswork"
assert_contains "$test_root/expect.log" "HostName=host"

unsafe_cache=$test_root/unsafe-cache
mkdir -p "$unsafe_cache/profiles"
ln -s "$test_root" "$unsafe_cache/profiles/unsafe"
set +e
EASYSTACK_AUTH_CACHE_DIR=$unsafe_cache PATH="$fake_bin:$PATH" \
  bash "$skill_dir/scripts/jumpserver-env.sh" \
  --auth-profile unsafe --asset node --cmd hostname --no-root --timeout 1 \
  >"$test_root/out" 2>"$test_root/err"
rc=$?
set -e
[[ $rc -eq 2 ]] || fail "unsafe auth profile returned $rc"
assert_contains "$test_root/err" "must not be a symlink"

echo "PASS: env-access.sh and jumpserver-env.sh"
