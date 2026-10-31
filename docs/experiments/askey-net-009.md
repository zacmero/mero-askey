# ASKEY-NET-009 — Temporary placement and observation

Date: 2026-10-31, UTC−03:00. Status: owned RAM allocation, bounded inert-data placement, fresh-session readback and explicit cleanup verified. No custom native code executed.

The owner explicitly requested establishing temporary code placement and a reliable observation channel. This is a volatile-RAM investigation, not an instruction to modify flash, restore settings, activate a persistent service or connect hardware.

## Supported storage and observation route

The firmware registers `xfile` as “DRAM file system,” with create/delete/list/close operations. The live `xfile list` table returns file base, size, buffer count, flags, timeout and name **in Telnet**. Five existing files were inventoried without reading their contents or modifying them.

The default open/write path at `0x802e86b8` allocates packet-backed storage through `0x80006318` with a 1600-byte data request. The displayed FILEBASE is a **control-block pointer, not the payload address**. The packet-write path at `0x802e8092`–`0x802e80a2` loads the data pointer from control-block offset +88, then adds the current fill count before copying bytes.

The allocator establishes separate backing storage and records its base at control-block +84. Helper `0x80161c9d` advances the data pointer by 128 bytes of headroom. These relationships must be checked against a newly created owned file before any raw-RAM placement; a displayed file base or memory-pool start alone is insufficient.

The observation method is a known owned RAM mailbox read through `memory show`, independently of the printf-like fixed-context output path. The completed data round trip and fresh-session verification are recorded below.

## Parser surprise and verified cleanup

The general `help` text says `?` requests argument help. However, `xfile create ?` consumed `?` as a literal filename and created a new empty, open RAM file. The before/after inventories proved that this file was new and isolated from the original five. No code was written to it.

`xfile close ?`, then `xfile delete ?`, removed that exact file. The resulting table matched the original five-file inventory and metadata. Do not use `?` as a safe create-argument probe. `xfile write ?` and `xfile set ?` did return grammar help, so the generic help guidance is not uniform across leaves.

Raw captures and scratch analysis remain ignored in `.local/askey-net-009/`. No custom native call or executable payload was part of this placement test.

## Owned allocation and checked bounds

The guarded probe created a unique `mero_native_009_` file after confirming absence of its name and the original inventory. Existing file rows remained unchanged. It resolved the unique live descriptor and verified the owned filename, open flag, zero logical length, single unchained control block, backing pointer, payload pointer and end-marker relationship.

Historical addresses for this allocation were:

| Object | Observed address |
| --- | --- |
| Packet control block | `0x809fc0b4` |
| Backing allocation | `0x80c07194` |
| Data pointer, backing +128 | `0x80c07214` |
| Observation mailbox, data +512 | `0x80c07414` |

These addresses are now released and are not current placement targets.

## Bounded placement and independent observation

The first 64 bytes of the reserved code region received an inert nonce-bearing data record. Another 64-byte record at data+512 contained `MRO9`, version 1, the same 16-byte nonce and zeroed remaining fields. This was ordinary data, not executable instructions.

The write phase revalidated ownership and pointers before touching storage. It first issued one aligned long store, read back that word, then completed 32 long stores total across the two exact regions. Strict readback matched both 64-byte records. No control-block or filesystem metadata was written through memory-store commands, and logical file length remained zero.

A new process and fresh Telnet session then independently rediscovered/revalidated the same allocation and read both complete records. They matched the expected bytes exactly. This establishes a RAM observation channel independent of the silent native formatter. It does not yet establish a custom routine's execution or instruction-cache behavior.

## Cleanup and evidence

The final session revalidated ownership, closed and deleted the owned file, and compared the resulting table against all original file rows. The original five-file inventory and metadata matched exactly. The private allocation record now says `held=false`; **no test allocation remains active**. All four allocation/write/read/cleanup sessions logged out cleanly.

| Private raw log | SHA-256 |
| --- | --- |
| `create.jsonl` | `856adf21f148d92b723abe89bb9d67521b236ebf3b41f580a1e37d095733ba94` |
| `write.jsonl` | `0981a4e868bbd942008b2c462e71e800e0d2ba837ee4796e976a40d5ae958303` |
| `read.jsonl` | `09377163d436a119a2842b3fe7a92925e651726303168c149d54dd4edf8c646e` |
| `cleanup.jsonl` | `110296f0f34600a29235544267a1e995e466d5cc83ce3002d1af70bc1a74d0a8` |

The reviewed implementation is [probe_ram_placement.py](../../tools/probe_ram_placement.py), with [operator documentation](../ram-placement.md). Its allocation/ownership/store core is the tested probe; the delivered wrapper adds repository-relative paths, CLI arguments, unique evidence names and a fixed image-header check. Live delivered-tool preflight passed, raw-log SHA-256 `d8247fc4371e6111eb7c821a5274d71cb3b7a93ffd1062e91586c906b095e021`.

No listener, persistent setting, firmware write, reset, direct MMIO access, native address call or hardware connection was performed. The existing firmware snapshot is unchanged. Recreate/revalidate ownership before any next experiment; instruction-mode/cache and actual entry/returned-callback execution remain separate work.
