# Final findings — 2026-10-27

## Verified capture

Full mapped flash 8388608 bytes SHA256 e5c171d08d5c3131cd7b8a4c7180e3ac277408c8072b96e335495f3b68e1fc2f.
Complete run image 2954688 bytes SHA256 74ff08b030051cce67e4c637cbb46d7cc7dfd629e04271a9fb83ebab3cc76ad6.
Both in firmware/ with manifest. All 8192 chunks audit, independent calibration/header, eight hardware samples, payload/decompression and settings/container checks passed. Capture service finished 0 with clean logout, no restarts. No device operation remains; power-off is safe.

## Access/runtime

Owner-approved menu flags and Telnet state persist; other settings/roles/SSH/ACL/WAN were not changed. Admin Telnet login works but sh gives another vendor console. No POSIX shell or own native program has run.

Firmware proves OSK and big-endian mixed MIPS32/MIPS16; decoded 9752040 bytes. Live pool 22.719 MiB is not physical RAM. Exact SoC/clock/RAM remain unknown.

Static code maps access mode, account priorities, CLI capability gates and native call/copy/checksum handlers. Memory store code exists without the mapped privilege bits, but no write was tested and safe live targets/lifetime are unproven. Whole backup-image slot is erased; primary-preferred recovery cleanup can explain it, not a proven defect/fallback. Both settings copies validate and match approved export semantically.

## Durable reports and open path

research/firmware-analysis.md links three exact-image reports; related-investigations.md extracts primary leads. research/open-research-leads.md retains the live-session capability-field avenue as OPEN, per owner direction; automated review of one optional follow-up is not technical rejection. Raw data/credentials/decoded settings stay .local/, except explicitly requested final firmware artifacts.


## 2026-10-31 live findings

- Code-supported sampled chip-ID global measured `0x00016405`; low 16 bits `0x6405` match a firmware branch. Exact chip/clock/RAM identification remains incomplete.
- Explicitly approved access mode 2/admin priority 1 import persisted byte-for-byte. Support web access survives; admin Telnet now reaches `XDSL#`.
- Filtered root help exposes `webdll`, `loaddll`, `chksum`. Privileged vendor CLI access is established; native handler execution and OS shell remain unproven.
- Full details, actual hashes, rollback and protocol correction: [ASKEY-NET-007](docs/experiments/askey-net-007.md). Live-session capability-field avenue remains OPEN.


## Native contract review — 2026-10-31

- webdll invokes the returned callback immediately; loaddll copies a body without entry execution or local allocation/decompression. Dispatcher overwrites handler returns with 1.
- Supplied formatter owns/frees a 3076-byte allocation, normally returns 1 and does not acknowledge Telnet delivery. It uses a fixed output context. Live callback pointer matches the captured firmware.
- The diagnostic ring is disabled; a live character hook traces statically to a UART-style backend. One bounded checksum request produced no numeric response, so the offline expected `0x347d` is not a live verified result.
- Evidence, limits and next questions: [native contracts](research/firmware-native-contracts.md) and [ASKEY-NET-008](docs/experiments/askey-net-008.md). No callback/copy/payload execution claimed.


## Temporary placement investigation — in progress

The captured firmware registers an `xfile` command family described as DRAM file system. Its lexer includes create/delete/list. Root descriptor `0x8060b310` and registration around `0x802e96d8` identify a supported RAM-filesystem route to examine before any guessed-address placement. No file operation has been issued yet; allocation/ownership/cleanup semantics are still being traced.

The live `xfile list` table prints reliably in Telnet and provides file-owned control-block addresses. Default files are packet-backed: the control block is not the payload. The packet write routine loads the payload pointer from control-block offset +88; allocation establishes separate backing storage. One `xfile create ?` request created an empty literal `?` file despite general help guidance; close/delete restored the exact original five-file inventory. Do not use `?` as a safe create-argument probe.


## Temporary placement and observation verified

- Native xfile allocation supplied a single owned packet buffer with separate backing storage and payload pointer, checked against the descriptor and unique filename. The default packet data request is 1600 bytes; 512 bytes were reserved for future code and a 64-byte mailbox at offset 512.
- Wrote only 64 inert marker bytes and 64 mailbox bytes through 32 aligned long stores. The pilot, immediate readback and fresh-process/fresh-Telnet readback matched exactly, including a fresh nonce. Metadata was not modified through memory stores.
- Closed/deleted the owned file and verified the original five-file inventory and all recorded metadata restored. No active allocation remains; historical addresses are invalid for reuse. All four sessions logged out.
- Published guarded source and workflow in [RAM placement](docs/ram-placement.md), with real evidence hashes in [ASKEY-NET-009](docs/experiments/askey-net-009.md). No custom instruction image or native address call occurred. Cache/fetch and entry/unload status remain next-stage work; the capability-field research road stays OPEN.


## Instruction mode and cache contracts verified — 2026-10-31

- Step 1 of the native execution roadmap is COMPLETE. Traced and verified resident cache management and instruction mode transitions against captured runtime `b104789b795630eee7de1b50d64e49710535221f8baa6652021af6d00abb3941`.
- Hardware CP0 register 20 is Realtek RLX Cache Control Register: bit 1 (`0x2`) triggers L1 I-cache global invalidate; bit 9 (`0x200`) triggers L1 D-cache global writeback-and-invalidate.
- Routine `0x801679e8`: MIPS32 `flush_icache_all` (disables interrupts via `c0_status` bit 0, toggles CP0 register 20 bit 1, restores interrupts). Provenance: invoked at boot (`0x80949748`) immediately after `memcpy` (`0x8000607c`) copies 384 bytes of executable exception vectors to `0x80000000`.
- Routine `0x800065ec` / `0x800064e4`: MIPS32 `dcache_flush_range(addr, len)`. For `< 8192` bytes, masks to KSEG0, disables interrupts, and executes a 64-byte block loop of four `cache 0x15` instructions (Hit Writeback Invalidate D-cache). For `>= 8192` bytes, toggles CP0 register 20 bit 9. Provenance: invoked in network drivers (`0x80014c2a`, etc.) on packet control block payload pointers (`88(s0)`) and lengths (`20(s0)`).
- Calling `webdll` with an even entry address guarantees execution in pure MIPS32 mode with full 32-register access.
- Roadmap Step 2 (prepare entry and returned callback pair) is now unblocked. Detailed contracts: [research/instruction-mode-cache-contracts.md](research/instruction-mode-cache-contracts.md).


## Native entry and cleanup callback pair verified — 2026-10-31

- Step 2 of the native execution roadmap is COMPLETE. Assembled and verified 576-byte position-independent MIPS32 payload adhering strictly to the `webdll` two-call contract (`f(magic, iface) -> next_fn; next_fn(magic, iface)`).
- `entry_func` at offset `0x00` (72 bytes, 18 instructions) discovers PC via `bal`, writes Stage 1 nonces and captured arguments to mailbox (`offset 512`), and returns cleanup address (`offset 128`) in `$v0`.
- `cleanup_func` at offset `0x80` (80 bytes, 20 instructions) discovers PC via `bal`, writes Stage 2 nonces and `"SUCC"` confirmation to mailbox, sets `$v0 = 0`, and returns cleanly to `webdll`.
- Zero relocations; callee-saved registers (`$s0`–`$s8`, `$gp`, `$sp`) and stack frame untouched; operates position-independently in KSEG0 or KSEG1.
- Delivered build and verification tool [`tools/build_native_payload.py`](tools/build_native_payload.py). Binary SHA-256: `c7db7a20722b2b37fa2f19390c904af1c4a5a832da50a819fe94a1381e27c3e0`. Documented in [`docs/native-payload.md`](docs/native-payload.md). Step 3 is now unblocked.


## Genuine native MIPS32 execution verified on-target (ASKEY-NET-010) — 2026-10-31

- Steps 3 & 4 of the native execution roadmap are COMPLETE. Full native code execution demonstrated on the owner's Askey RTV9015VW under `webdll`.
- Orchestrated via dedicated test harness [`tools/run_native_trial.py`](tools/run_native_trial.py) across isolated SSH/Telnet sessions.
- Dynamic owned allocation created: `mero_native_010_5e4940b6` at CCB `0x809d8d9c`, data payload at `0x80a61c94`, mailbox at `0x80a61e94`.
- Binary staged into uncached KSEG1 (`0xa0a61c94`) and KSEG0 (`0x80a61c94`), with mailbox prefilled with `0xDEADBEEF`. Both readbacks matched `payload.bin` byte-for-byte.
- Issued `webdll 0xa0a61c94`. The command executed synchronously in < 1 second and cleanly returned to the `XDSL#` prompt. Telnet console remained completely stable and responsive.
- Independent fresh-session mailbox readback (`memory show 0xa0a61e94 length 0x40`) confirmed all 10 expected fields:
  1. `0x454e5452` ("ENTR"): Entry routine reached.
  2. `0x11112222`: Stage 1 nonce confirmed.
  3. `0x12345678`: Argument 0 (`magic`) verified.
  4. `0x805f1648`: Argument 1 (`iface`) verified.
  5. `0xa0a61d14`: Returned cleanup callback address verified.
  6. `0x434c4e50` ("CLNP"): Cleanup routine reached.
  7. `0x33334444`: Stage 2 nonce confirmed.
  8. `0x12345678`: Argument 0 in cleanup verified.
  9. `0x805f1648`: Argument 1 in cleanup verified.
  10. `0x53554343` ("SUCC"): Complete execution lifecycle verified.
- Uncached KSEG1 execution completely bypassed L1 I-cache/D-cache hazards, eliminating Harvard cache coherency obstacles.
- Clean fail-closed release: file closed and deleted, and baseline 5-file filesystem inventory verified restored (`held=false`). Documented in [`docs/experiments/askey-net-010.md`](docs/experiments/askey-net-010.md).
