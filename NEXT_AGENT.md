# Next agent — current implementation state

## Goal and next step

Run a minimal native program on the owner's Askey RTV9015VW. Step 1 (instruction-mode and cache contracts) is **COMPLETE**: verified RLX CP0 register 20 cache bits, range D-cache writeback (`0x800065ec`) and global I-cache invalidate (`0x801679e8`), plus even-address MIPS32 mode entry. **Next (Step 2): prepare the minimal entry and returned callback pair** that preserves calling state, writes nonce-bearing entry and cleanup status into the owned mailbox, and returns through the verified two-call `webdll` contract. [Roadmap](docs/native-execution-roadmap.md); [cache contracts](research/instruction-mode-cache-contracts.md); [step-1 checkpoint](research/instruction-cache-checkpoint.md).

## What works

- Firmware `BR_SO_RTK_V6.1.8t`; OSK, big-endian mixed MIPS32/MIPS16. No Linux/POSIX shell or custom native program demonstrated.
- `sh` already worked before. Approved access mode 2/admin priority 1 now gives vendor prompt **`XDSL#`** and exposes `webdll`, `loaddll`, `chksum`. Support web login still works.
- Native `xfile` RAM allocation, ownership checks, 128-byte inert placement, independent fresh-session readback and close/delete all passed. Original five-file inventory restored. **No active test allocation; old addresses are invalid.**
- Reliable observation: owned RAM mailbox read with `memory show`. Do not depend on native printf appearing in Telnet.

## Working implementation

[tools/probe_ram_placement.py](tools/probe_ram_placement.py): phases **preflight → create → write → read → cleanup**, using the same `--run-dir .local/<name>`. `write` places inert records, not an executable. [Usage and validation](docs/ram-placement.md); [measured evidence](docs/experiments/askey-net-009.md).

- `xfile list` FILEBASE is a packet control block, **not payload storage**. The checked payload pointer is at control-block +88; backing pointer at +84, with 128-byte headroom.
- Default data request: 1600 bytes. Reserved layout: code area 0–511; mailbox 512–575. Only 64 code-placeholder bytes and 64 mailbox bytes were tested.
- Probe pins the firmware header, checks route/neighbor and live ownership, limits stores, and preserves private evidence. Recreate/revalidate before using any address.
- `xfile create ?` creates a literal `?` file; it is not a safe help query. That accidental file was removed and inventory verified.

## Native contracts already recovered

[Detailed evidence](research/firmware-native-contracts.md).

- `webdll`: calls its parsed target with fixed magic/interface arguments, then **immediately calls the returned function pointer**. Zero/status return is not a valid cleanup target. No placement or cache operation occurs inside this handler.
- `loaddll`: checks header magic and copies its body to a header-specified address. It does not allocate, decompress, relocate or execute the entry field. **Do not load the archived compressed firmware as a module.**
- Supplied formatter returns 0/1, owns/frees its temporary buffer, and uses a fixed output context. The diagnostic ring was disabled; the character hook traces to a UART-style backend. No attached hardware is needed for mailbox readback.
- The dispatcher overwrites handler returns with 1. A returned prompt alone proves neither a checksum nor execution. One bounded checksum request produced no visible numeric result.
- Cache procedure and executable placement remain unverified. The image mixes instruction modes and data: linear disassembly matches alone are insufficient. Review the linked cache checkpoint before acting on candidate routines.

## Connection and artifacts

- Work from `/home/zacmero/projects/mero-askey` on mero-machine. Prefix shell commands with `rtk`.
- Known MSI SSH endpoint: `cris@192.168.1.80`, key `/home/zacmero/.ssh/mero_stb_isolated_lab`, strict host checking. Recheck current route/neighbor before device traffic.
- MSI Ethernet was `enp6s0`, `192.168.15.3`; Askey `192.168.15.1`. Preserve Wi-Fi control. Mero-machine has no direct lab route.
- Private target/login inputs: `.local/capture-target.json`, `.local/router-login.json`. Raw experiments: `.local/askey-net-007/`, `008/`, `009/`.
- Full 8 MiB flash and running image are committed in `firmware/`; [manifest](firmware/manifest.json) has hashes. They are the **2026-10-27 snapshot**, before the latest settings change.
- Decoded runtime: `.local/askey-net-006/analysis/runtime.bin`, load base `0x80000000`. Private GNU MIPS objdump/readbin: `.local/askey-net-006/analysis/cli-agent/`.

Record actual outcomes and commit/push meaningful checkpoints. Keep raw/private/generated artifacts ignored. No firmware write, reset, new persistent setting/service or hardware connection is implied by this next step. The separate session-capability-field research avenue remains OPEN.
