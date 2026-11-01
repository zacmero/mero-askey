# Next agent — current implementation state

## Goal and current milestone

Run a minimal native program on the owner's Askey RTV9015VW. **COMPLETE (Roadmap Steps 1–4 verified).** Genuine native MIPS32 execution on the Askey RTV9015VW is fully demonstrated, independently verified via mailbox readback, and documented in [ASKEY-NET-010](docs/experiments/askey-net-010.md). The owned allocation was released cleanly (`held=false`) and baseline filesystem inventory verified. Complete hardware specs verified on silicon ([docs/hardware-specs-and-baremetal.md](docs/hardware-specs-and-baremetal.md)). **Next horizon: memory scaling, interactive two-way I/O architectures (TCP socket bind shell, shared-memory ring buffer, Telnet CLI hooking), and home lab utilities.** Detailed roadmap: [docs/next_experiments.md](docs/next_experiments.md).

## What works

- Firmware `BR_SO_RTK_V6.1.8t`; OSK, big-endian mixed MIPS32/MIPS16 on Realtek RLX5181/RLX5281 core. Hardware specs resolved: Realtek RTL8672 / RTL8671x SoC, ~300 MHz CPU, 100.1 MHz bus clock, 64 MiB physical DRAM, 8 MiB SPI flash ([docs/hardware-specs-and-baremetal.md](docs/hardware-specs-and-baremetal.md)).
- Admin access mode 2 / priority 1 vendor console **`XDSL#`** exposes `webdll`, `loaddll`, `chksum`.
- Native `xfile` RAM allocation, dynamic pointer discovery, and fail-closed cleanup verified.
- Position-independent MIPS32 payload (`tools/build_native_payload.py`, 576 bytes, 0 relocations) executes cleanly in uncached KSEG1 (`0xa0...`).
- Synchronous two-call `webdll` execution verified: `entry_func` ran, wrote Stage 1 nonces and captured arguments to mailbox, returned cleanup callback address in `$v0`, `webdll` called cleanup callback, `cleanup_func` ran, wrote Stage 2 nonces and `"SUCC"` confirmation to mailbox, set `$v0 = 0`, and returned cleanly to CLI prompt (`XDSL#`).
- Mailbox readback via `memory show` in a separate, fresh Telnet session verified all 10 target fields.
- Re-verified console responsiveness and cleanly closed/deleted the owned file. Baseline 5-file inventory intact. [ASKEY-NET-010](docs/experiments/askey-net-010.md).

## Working implementation

- [tools/build_native_payload.py](tools/build_native_payload.py): builds and verifies 576-byte PIC MIPS32 entry/cleanup binary adhering to `webdll` calling contract.
- [tools/run_native_trial.py](tools/run_native_trial.py): orchestrates phases **preflight → create → stage → execute → verify → cleanup**. Tested and verified live on device.
- [tools/probe_ram_placement.py](tools/probe_ram_placement.py): inert placement probe and readback baseline from ASKEY-NET-009.

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
