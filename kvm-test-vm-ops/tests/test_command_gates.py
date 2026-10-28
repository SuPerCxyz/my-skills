from __future__ import annotations

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = (ROOT / "references" / "clone-and-resize.md").read_text()
VERIFICATION = (ROOT / "references" / "verification.md").read_text()


def block(document: str, heading: str) -> str:
    section = document.split(heading, 1)[1].split("\n## ", 1)[0]
    return re.search(r"```bash\n(.*?)```", section, re.S).group(1)


MOCKS = r'''
set -eu
printf '%s\n' "$POWER" > "$TASK_TMP/power"
printf '%s\n' "$LIVE_CPUS" > "$TASK_TMP/cpus"
printf '%s\n' "$CONFIG_CPUS" > "$TASK_TMP/config-cpus"
printf '%s\n' "$CONFIG_MAX_CPUS" > "$TASK_TMP/config-max-cpus"
printf '%s\n' "$CONFIG_MEMORY" > "$TASK_TMP/config-memory"
printf '%s\n' "$CONFIG_MAX_MEMORY" > "$TASK_TMP/config-max-memory"
printf '%s\n' "$CAPACITY" > "$TASK_TMP/capacity"
log() { printf '%s\n' "$*" >> "$TASK_TMP/commands"; }
KVM_NODE_SSH=(mock_ssh)
mock_ssh() {
  log "$1"
  case "$1" in
    *domstate*) cat "$TASK_TMP/power" ;;
    *dominfo*) printf 'CPU(s): %s\nUsed memory: %s KiB\nMax memory: %s KiB\n' "$(cat "$TASK_TMP/cpus")" "$LIVE_MEMORY" "$LIVE_MAX_MEMORY" ;;
    *dumpxml*) printf '<domain><vcpu current="%s">%s</vcpu><memory unit="KiB">%s</memory><currentMemory unit="KiB">%s</currentMemory></domain>\n' "$(cat "$TASK_TMP/config-cpus")" "$(cat "$TASK_TMP/config-max-cpus")" "$(cat "$TASK_TMP/config-max-memory")" "$(cat "$TASK_TMP/config-memory")" ;;
    *shutdown*) printf 'shut off\n' > "$TASK_TMP/power" ;;
    *domblkinfo*) printf 'Capacity: %s\n' "$(cat "$TASK_TMP/capacity")" ;;
    *'qemu-img info'*) printf '{"virtual-size":%s}\n' "$(cat "$TASK_TMP/capacity")" ;;
    *'qemu-img resize'*) printf '%s\n' "$PLAN_DISK_BYTES" > "$TASK_TMP/capacity" ;;
    *setvcpus*--maximum*)
      printf '%s\n' "$PLAN_VCPUS" > "$TASK_TMP/config-max-cpus"
      if (( $(cat "$TASK_TMP/config-cpus") > PLAN_VCPUS )); then printf '%s\n' "$PLAN_VCPUS" > "$TASK_TMP/config-cpus"; fi
      ;;
    *setvcpus*) printf '%s\n' "$PLAN_VCPUS" > "$TASK_TMP/config-cpus" ;;
    *setmaxmem*) printf '%s\n' "$PLAN_MEMORY_MAX_KIB" > "$TASK_TMP/config-max-memory" ;;
    *setmem*) printf '%s\n' "$PLAN_MEMORY_KIB" > "$TASK_TMP/config-memory" ;;
    'command -v qemu-img') test "$MISSING_TOOL" != qemu-img ;;
    *' start '*) printf 'running\n' > "$TASK_TMP/power"; cp "$TASK_TMP/config-cpus" "$TASK_TMP/cpus" ;;
    *) printf 'unexpected mock SSH command\n' >&2; return 90 ;;
  esac
}
command() {
  if test "${1:-}" = -v; then
    log "check:$2"
    test "$2" != "$MISSING_TOOL" || return 1
    case "$2" in growpart|udevadm|xfs_growfs|resize2fs|pvs|vgs|lvs|pvresize|lvextend) return 0 ;; esac
  fi
  builtin command "$@"
}
findmnt() {
  case "$*" in
    *FSTYPE*) printf '%s\n' "$FILESYSTEM" ;;
    *SOURCE*) printf '/dev/vda1\n' ;;
    *) return 90 ;;
  esac
}
readlink() { printf '%s\n' "${@: -1}"; }
lsblk() {
  case "$*" in *PKNAME*) printf 'vda\n' ;; *PARTNUM*) printf '1\n' ;; *) : ;; esac
}
pvs() { printf '/dev/vda1 vg\n'; }
vgs() { :; }
lvs() { case "$*" in *vg_name*) printf 'vg\n' ;; *) printf '/dev/vg/root\n' ;; esac; }
growpart() { log "growpart:$*"; }
udevadm() { log "udevadm:$*"; }
xfs_growfs() { log "xfs_growfs:$*"; }
resize2fs() { log "resize2fs:$*"; }
pvresize() { log "pvresize:$*"; }
lvextend() { log "lvextend:$*"; }
df() { :; }
'''


class CommandGateTest(unittest.TestCase):
    def run_snippet(self, snippet: str, expected: int = 0, **overrides: str) -> tuple[str, list[str]]:
        with tempfile.TemporaryDirectory(prefix="kvm-command-gates.") as directory:
            environment = os.environ.copy()
            environment.update({
                "TASK_TMP": directory, "POWER": "running", "CAPACITY": "21474836480",
                "MISSING_TOOL": "", "FILESYSTEM": "xfs", "KVM_MODE": "resize",
                "LIVE_CPUS": "2", "CONFIG_CPUS": "2", "CONFIG_MAX_CPUS": "2",
                "LIVE_MEMORY": "1048576", "LIVE_MAX_MEMORY": "4194304",
                "CONFIG_MEMORY": "1048576", "CONFIG_MAX_MEMORY": "4194304",
                "LIBVIRT_URI": "qemu:///system", "KVM_DOMAIN": "test-vm",
                "KVM_DISK_TARGET": "vda", "KVM_DEST_DISK": "/test/vm.qcow2",
                "KVM_SHUTDOWN_WAIT_SECONDS": "1", "PLAN_DISK_BYTES": "21474836480",
                "PLAN_VCPUS": "2", "PLAN_MEMORY_KIB": "1048576",
                "PLAN_MEMORY_MAX_KIB": "4194304", "PYTHONDONTWRITEBYTECODE": "1",
            })
            environment.update(overrides)
            result = subprocess.run(
                ["bash", "-c", MOCKS + snippet], env=environment,
                capture_output=True, text=True, timeout=10, check=False,
            )
            log_path = Path(directory) / "commands"
            commands = log_path.read_text().splitlines() if log_path.exists() else []
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return result.stdout, commands

    def host_section(self, heading: str) -> str:
        return block(DOCUMENT, "## Controlled Shutdown") + block(DOCUMENT, heading)

    def guest_section(self, lvm: bool = False) -> str:
        section = DOCUMENT.split("## Guest Filesystem", 1)[1].split("## Memory Escalation", 1)[0]
        bodies = re.findall(r"<<'GUEST'\n(.*?)\nGUEST", section, re.S)
        return bodies[1 if lvm else 0]

    def test_satisfied_compute_never_shuts_down(self) -> None:
        output, commands = self.run_snippet(self.host_section("## Compute Resources"))
        self.assertIn("already_satisfied", output)
        self.assertFalse(any("shutdown" in command or "setvcpus" in command or "setmem" in command for command in commands))

    def test_resize_contract_does_not_invent_creation_defaults(self) -> None:
        snippet = "unset PLAN_VCPUS PLAN_MEMORY_KIB PLAN_MEMORY_MAX_KIB PLAN_DISK_BYTES\n"
        snippet += block(DOCUMENT, "## Variable Contract")
        snippet += '\nprintf "values=[%s][%s][%s][%s]\\n" "$PLAN_VCPUS" "$PLAN_MEMORY_KIB" "$PLAN_MEMORY_MAX_KIB" "$PLAN_DISK_BYTES"\n'
        output, commands = self.run_snippet(snippet, KVM_NODE="mock-host", KVM_SSH_USER="mock-user")
        self.assertIn("values=[][][][]", output)
        self.assertEqual([], commands)

    def test_cpu_change_reads_before_shutdown_and_preserves_unspecified_memory(self) -> None:
        _, commands = self.run_snippet(
            self.host_section("## Compute Resources"), PLAN_VCPUS="4",
            PLAN_MEMORY_KIB="", PLAN_MEMORY_MAX_KIB="",
        )
        shutdown = next(i for i, command in enumerate(commands) if "shutdown" in command)
        read = next(i for i, command in enumerate(commands) if "dominfo" in command)
        write = next(i for i, command in enumerate(commands) if "setvcpus" in command)
        self.assertLess(read, shutdown)
        self.assertLess(shutdown, write)
        self.assertFalse(any("setmem" in command or "setmaxmem" in command for command in commands))

    def test_live_target_with_different_persistent_cpu_is_corrected_without_shutdown(self) -> None:
        snippet = self.host_section("## Compute Resources")
        snippet += '\nprintf "config-cpus=%s\\n" "$(cat "$TASK_TMP/config-cpus")"\n'
        output, commands = self.run_snippet(snippet, CONFIG_CPUS="4", CONFIG_MAX_CPUS="4")
        self.assertIn("config-cpus=2", output)
        self.assertNotIn("already_satisfied", output)
        self.assertTrue(any("setvcpus" in command for command in commands))
        self.assertFalse(any("shutdown" in command for command in commands))

    def test_persistent_target_with_different_live_cpu_restarts_without_rewriting_config(self) -> None:
        snippet = self.host_section("## Compute Resources")
        snippet += block(VERIFICATION, "## Domain And QGA")
        snippet += '\nprintf "live-cpus=%s\\n" "$(cat "$TASK_TMP/cpus")"\n'
        output, commands = self.run_snippet(snippet, LIVE_CPUS="4")
        self.assertIn("live-cpus=2", output)
        self.assertTrue(any("shutdown" in command for command in commands))
        self.assertTrue(any(" start " in command for command in commands))
        self.assertFalse(any("setvcpus" in command for command in commands))

    def test_memory_only_change_preserves_unrequested_persistent_cpu_and_reports_drift(self) -> None:
        snippet = self.host_section("## Compute Resources")
        snippet += '\nprintf "config-cpus=%s config-memory=%s\\n" "$(cat "$TASK_TMP/config-cpus")" "$(cat "$TASK_TMP/config-memory")"\n'
        output, commands = self.run_snippet(
            snippet, CONFIG_CPUS="4", CONFIG_MAX_CPUS="4", PLAN_VCPUS="",
            PLAN_MEMORY_KIB="2097152", PLAN_MEMORY_MAX_KIB="",
        )
        self.assertIn("config-cpus=4 config-memory=2097152", output)
        self.assertIn("pending_unrequested_vcpus", output)
        self.assertFalse(any("setvcpus" in command for command in commands))

    def test_cpu_reduction_keeps_confirmed_maximum_then_current_order(self) -> None:
        snippet = self.host_section("## Compute Resources")
        snippet += '\nprintf "config-cpus=%s max=%s\\n" "$(cat "$TASK_TMP/config-cpus")" "$(cat "$TASK_TMP/config-max-cpus")"\n'
        output, commands = self.run_snippet(snippet, PLAN_VCPUS="1")
        setters = [command for command in commands if "setvcpus" in command]
        self.assertEqual(2, len(setters))
        self.assertIn("--maximum", setters[0])
        self.assertNotIn("--maximum", setters[1])
        self.assertIn("config-cpus=1 max=1", output)

    def test_satisfied_disk_never_shuts_down_or_opens_image(self) -> None:
        _, commands = self.run_snippet(self.host_section("## Host Disk"))
        self.assertFalse(any("shutdown" in command or "qemu-img" in command for command in commands))

    def test_disk_growth_checks_capacity_before_shutdown_and_image_write(self) -> None:
        _, commands = self.run_snippet(self.host_section("## Host Disk"), CAPACITY="10737418240")
        capacity = next(i for i, command in enumerate(commands) if "domblkinfo" in command)
        shutdown = next(i for i, command in enumerate(commands) if "shutdown" in command)
        resize = next(i for i, command in enumerate(commands) if "qemu-img resize" in command)
        self.assertLess(capacity, shutdown)
        self.assertLess(shutdown, resize)

    def test_missing_image_tool_stops_before_shutdown(self) -> None:
        _, commands = self.run_snippet(
            self.host_section("## Host Disk"), expected=2,
            CAPACITY="10737418240", MISSING_TOOL="qemu-img",
        )
        self.assertFalse(any("shutdown" in command for command in commands))

    def test_unchanged_stopped_vm_is_not_started_for_verification(self) -> None:
        output, commands = self.run_snippet(
            block(VERIFICATION, "## Domain And QGA"), POWER="shut off",
        )
        self.assertIn("remains shut off", output)
        self.assertFalse(any(" start " in command for command in commands))

    def test_unsupported_filesystems_stop_before_any_disk_write(self) -> None:
        for lvm in (False, True):
            with self.subTest(lvm=lvm):
                _, commands = self.run_snippet(self.guest_section(lvm), expected=2, FILESYSTEM="btrfs")
                self.assertFalse(any(command.startswith(("growpart:", "pvresize:", "lvextend:")) for command in commands))

    def test_missing_filesystem_tool_stops_before_partition_write(self) -> None:
        for lvm, tool in ((False, "xfs_growfs"), (True, "lvextend")):
            with self.subTest(lvm=lvm, tool=tool):
                _, commands = self.run_snippet(self.guest_section(lvm), expected=2, MISSING_TOOL=tool)
                self.assertFalse(any(command.startswith(("growpart:", "pvresize:", "lvextend:")) for command in commands))

    def test_supported_lvm_checks_tools_then_grows_in_order(self) -> None:
        _, commands = self.run_snippet(self.guest_section(True))
        check = commands.index("check:lvextend")
        partition = next(i for i, command in enumerate(commands) if command.startswith("growpart:/dev"))
        pv = next(i for i, command in enumerate(commands) if command.startswith("pvresize:"))
        lv = next(i for i, command in enumerate(commands) if command.startswith("lvextend:"))
        self.assertLess(check, partition)
        self.assertLess(partition, pv)
        self.assertLess(pv, lv)


if __name__ == "__main__":
    unittest.main()
