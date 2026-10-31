# ASKEY-NET-009 — Temporary placement and observation

Date: 2026-10-31, UTC−03:00. Status: RAM-filesystem allocation path traced; bounded allocation/write/readback test in preparation.

The owner explicitly requested establishing temporary code placement and a reliable observation channel. This is a volatile-RAM investigation, not an instruction to modify flash, restore settings, activate a persistent service or connect hardware.

## Supported storage and observation route

The firmware registers `xfile` as “DRAM file system,” with create/delete/list/close operations. The live `xfile list` table returns file base, size, buffer count, flags, timeout and name **in Telnet**. Five existing files were inventoried without reading their contents or modifying them.

The default open/write path at `0x802e86b8` allocates packet-backed storage through `0x80006318` with a 1600-byte data request. The displayed FILEBASE is a **control-block pointer, not the payload address**. The packet-write path at `0x802e8092`–`0x802e80a2` loads the data pointer from control-block offset +88, then adds the current fill count before copying bytes.

The allocator establishes separate backing storage and records its base at control-block +84. Helper `0x80161c9d` advances the data pointer by 128 bytes of headroom. These relationships must be checked against a newly created owned file before any raw-RAM placement; a displayed file base or memory-pool start alone is insufficient.

The candidate observation method is a known owned RAM mailbox read through `memory show`, independently of the printf-like fixed-context output path. It still requires a bounded data round trip and fresh-session readback before being called established.

## Parser surprise and verified cleanup

The general `help` text says `?` requests argument help. However, `xfile create ?` consumed `?` as a literal filename and created a new empty, open RAM file. The before/after inventories proved that this file was new and isolated from the original five. No code was written to it.

`xfile close ?`, then `xfile delete ?`, removed that exact file. The resulting table matched the original five-file inventory and metadata. Do not use `?` as a safe create-argument probe. `xfile write ?` and `xfile set ?` did return grammar help, so the generic help guidance is not uniform across leaves.

Raw captures and scratch analysis remain ignored in `.local/askey-net-009/`. Allocation ownership, a bounded inert-data round trip, independent observation, retention/cleanup state and real artifact hashes will be recorded below after measurement. No custom native call or executable payload is part of this initial placement test.
