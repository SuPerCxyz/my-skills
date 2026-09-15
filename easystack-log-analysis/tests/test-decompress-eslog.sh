#!/usr/bin/env bash
set -euo pipefail

skill_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
test_root=$(mktemp -d /tmp/easystack-eslog-test.XXXXXX)
cleanup() {
  find "$test_root" -depth -delete
}
trap cleanup EXIT
fixture=$test_root/fixture
output=$test_root/output
mkdir -p \
  "$fixture/tree/ecs.node-1.20260724.0/openstack/nova" \
  "$fixture/tree/ecs.node-1.20260724.0/openstack/cinder" \
  "$fixture/tree/ecs.node-2.20260724.0/openstack/cinder"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

log_path=$fixture/tree/ecs.node-1.20260724.0/openstack/nova/nova-compute.node-1.log
printf 'request-id=req-test instance=vm-test\n' >"$log_path"
gzip "$log_path"
small_component=$fixture/tree/ecs.node-1.20260724.0/openstack/cinder/cinder-volume.shared.log
large_component=$fixture/tree/ecs.node-2.20260724.0/openstack/cinder/cinder-volume.shared.log
printf 'small\n' >"$small_component"
printf 'large component log from node-2\n' >"$large_component"
gzip "$small_component"
gzip "$large_component"
tar -cf "$fixture/ecs-node.tar" -C "$fixture/tree" \
  ecs.node-1.20260724.0 ecs.node-2.20260724.0
mkdir "$fixture/inner"
cp "$fixture/ecs-node.tar" "$fixture/inner/"
(
  cd "$fixture/inner"
  zip -q "$fixture/nested.zip" ecs-node.tar
)
cp "$fixture/nested.zip" "$fixture/sample.eslog.0"
(
  cd "$fixture"
  zip -q "$test_root/sample.eslog" sample.eslog.0
)

default_file_dir=$test_root/default-file
mkdir "$default_file_dir"
cp "$test_root/sample.eslog" "$default_file_dir/bundle.eslog"
(
  cd "$test_root"
  bash "$skill_dir/scripts/decompress-eslog.sh" \
    --input "$default_file_dir/bundle.eslog"
)
default_file_result=$default_file_dir/ecs.node-1.20260724.0/openstack/nova/nova-compute.node-1.log
[[ -f $default_file_result ]] || fail "file input did not default output to its parent directory"

default_dir=$test_root/default-dir
mkdir "$default_dir"
cp "$test_root/sample.eslog" "$default_dir/bundle.eslog"
(
  cd "$test_root"
  bash "$skill_dir/scripts/decompress-eslog.sh" --input "$default_dir"
)
default_dir_result=$default_dir/ecs.node-1.20260724.0/openstack/nova/nova-compute.node-1.log
[[ -f $default_dir_result ]] || fail "directory input did not default output to the input directory"

bash "$skill_dir/scripts/decompress-eslog.sh" \
  --input "$test_root/sample.eslog" --output "$output"

result=$output/ecs.node-1.20260724.0/openstack/nova/nova-compute.node-1.log
[[ -f $result ]] || fail "readable .log was not generated"
grep -F "req-test" "$result" >/dev/null || fail "generated log content mismatch"
[[ -f $result.gz ]] || fail "original .log.gz was not preserved"

component_result=$output/components/openstack/cinder/cinder-volume.shared.log
[[ -f $component_result ]] || fail "component view file was not created"
[[ ! -L $component_result ]] || fail "component view used a symlink instead of a regular file"
grep -F "large component log from node-2" "$component_result" >/dev/null ||
  fail "larger component log did not win the filename conflict"

rm "$component_result"
ln -s "$large_component" "$component_result"
bash "$skill_dir/scripts/decompress-eslog.sh" \
  --input "$test_root/sample.eslog" --output "$output"
[[ ! -L $component_result ]] || fail "existing component symlink was not replaced"
grep -F "large component log from node-2" "$component_result" >/dev/null ||
  fail "regular file replacing a component symlink has wrong content"

printf 'tiny\n' >"$component_result"
bash "$skill_dir/scripts/decompress-eslog.sh" \
  --input "$test_root/sample.eslog" --output "$output"
grep -F "large component log from node-2" "$component_result" >/dev/null ||
  fail "larger source did not replace a smaller component file"

largest_source=$output/ecs.node-2.20260724.0/openstack/cinder/cinder-volume.shared.log
largest_size=$(wc -c <"$largest_source")
printf '%*s' "$largest_size" '' | tr ' ' E >"$component_result"
bash "$skill_dir/scripts/decompress-eslog.sh" \
  --input "$test_root/sample.eslog" --output "$output"
grep -E "^E{$largest_size}$" "$component_result" >/dev/null ||
  fail "equal-sized source unexpectedly replaced the existing component file"

printf 'existing component file is deliberately larger than every source log in this fixture\n' \
  >"$component_result"
bash "$skill_dir/scripts/decompress-eslog.sh" \
  --input "$test_root/sample.eslog" --output "$output"
grep -F "deliberately larger" "$component_result" >/dev/null ||
  fail "smaller source unexpectedly replaced a larger component file"

printf 'keep\n' >"$output/ecs.node-1.20260724.0/previous-file.txt"
bash "$skill_dir/scripts/decompress-eslog.sh" \
  --input "$test_root/sample.eslog" --output "$output"
[[ -f $output/ecs.node-1.20260724.0/previous-file.txt ]] ||
  fail "merge removed a file absent from the new bundle"

mkdir -p "$fixture/corrupt/ecs.node-1.20260724.0/openstack/nova"
printf 'not-gzip\n' \
  >"$fixture/corrupt/ecs.node-1.20260724.0/openstack/nova/nova-compute.node-1.log.gz"
tar -cf "$fixture/corrupt.tar" -C "$fixture/corrupt" ecs.node-1.20260724.0
mkdir "$fixture/corrupt-inner"
cp "$fixture/corrupt.tar" "$fixture/corrupt-inner/ecs-corrupt.tar"
(
  cd "$fixture/corrupt-inner"
  zip -q "$fixture/corrupt-nested.zip" ecs-corrupt.tar
)
cp "$fixture/corrupt-nested.zip" "$fixture/corrupt.eslog.0"
(
  cd "$fixture"
  zip -q "$test_root/corrupt.eslog" corrupt.eslog.0
)
set +e
bash "$skill_dir/scripts/decompress-eslog.sh" \
  --input "$test_root/corrupt.eslog" --output "$output" \
  >"$test_root/corrupt.out" 2>"$test_root/corrupt.err"
rc=$?
set -e
[[ $rc -ne 0 ]] || fail "corrupt gzip unexpectedly succeeded"
grep -F "req-test" "$result" >/dev/null ||
  fail "failed expansion overwrote the previous readable log"
[[ -z $(find "$output" -type f -name '*.part.*' -print -quit) ]] ||
  fail "failed expansion left a partial log"

set +e
bash "$skill_dir/scripts/decompress-eslog.sh" --decompress-logs \
  >"$test_root/out" 2>"$test_root/err"
rc=$?
set -e
[[ $rc -eq 2 ]] || fail "removed option returned $rc"
grep -F "Unknown argument: --decompress-logs" "$test_root/err" >/dev/null ||
  fail "removed option error was unclear"

echo "PASS: decompress-eslog.sh"
