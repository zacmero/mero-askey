# ASKEY-NET-005 — Related OSK research and flash-read syntax check

Date: 2026-10-27, UTC−03:00. Status: online research and bounded flash-read validation completed; no OS shell or native execution.

The owner asked for the next step, laptop Telnet instructions, and other investigations. Existing authorization covers bounded read-only reconnaissance. No new settings change, service activation or firmware write is proposed here.

## New primary source

[VSOL V2802RH research](https://github.com/1234205a/vsol-v2802rh-research) documents a Realtek RTL9601D device running OSK RTOS with Virtual Web 0.9 and a similar management console. Its [firmware/flash analysis](https://github.com/1234205a/vsol-v2802rh-research/blob/main/docs/firmware-and-flash-analysis.md) describes a `memory show` primitive for reading memory-mapped NOR, chunk reassembly, firmware decompression and mixed MIPS32/MIPS16e analysis. This is a related-platform lead, not evidence of the Askey's CPU/ISA, exact OS, image offsets or command permissions.

Read the analysis, configuration backup/restore document, and the first 300 lines of its CLI client through the connected GitHub tool. Retained text snapshots under ignored `.local/research/vsol-v2802rh/`. Analysis document Git blob SHA: `16e2e5f92ed0cadc2d182301364f9155f35a1ca5`; CLI file blob SHA: `9e2711c9e1fd9519129ca4c1dabbc7b8e7376e2e`; configuration document blob SHA: `d6bb0fcd1c0bddd391a6c56688f6327eba53acf5`.

The client name says read-only, but inspected code also includes diagnostic-setting modes and `omcicli set` operations. It has not been executed. Do not adopt its whole command list as read-only or copy the other device's flash ranges. The Askey reports an 8 MB map, whereas this source's device has 4 MB and different mapped ranges.

## Next bounded question

Does the Askey's already advertised inner-console `memory` command expose an explicit read-only display operation? Inspect help first. If the actual grammar confirms a display operation, a later tiny read at the Askey's own reported run-image address can identify the firmware header. Do not start a full flash dump or any memory-write/call/test operation on a filename/label assumption.

## Actual console validation

Authenticated as admin through the existing Telnet service and entered `XDSL>` with `sh`. `memory ?` lists `show` and `set`. `memory show` with no address requests a number, rather than reading a default address.

Submitted one 16-byte display read at this device's own reported run-image start:

```text
memory show 0xb4010000 length 0x10
0xb4010000: a0 00 00 03 80 00 00 00 00 2d 15 80 80 94 92 88
```

This proves a flash-region read primitive on this unit without a POSIX shell. No memory write, call, reset or settings command was submitted. The session was logged out and disconnected.

Raw transcript `.local/askey-net-005/memory-help.typescript`, SHA-256 `93870d2fbefe9a68ac21d4685a1974eaf441e08e5af2e151d1398952a21999ff`. Extracted 16-byte artifact `.local/askey-net-005/run-image-header-16.bin`, SHA-256 `baad35d1f06b066b7e01cc40aac7a2fbb7d72eadb1c26243afa11b44ed390e13`. This is a tiny header sample, not a firmware image or recoverable flash backup.

The related image parser reads the first four words as big-endian signature/load address/image length/entry. Under that unconfirmed layout, this sample gives `0xa0000003`, `0x80000000`, `0x002d1580` and `0x80949288`. Treat those field meanings as hypotheses until the full header is examined. A useful consistency check: candidate length 2954624 bytes plus local run-image address ends at `0xb42e1580`, which rounds up to the device-reported unused-region start `0xb42e2000` on a 4 KiB boundary. No exact OS/ISA or checksum validation follows from that agreement alone.

## Owner question about sh — follow-up validation

The owner reported entering `sh`. The earlier session had tested `id` only in the outer parser, so a new bounded session checked the inner prompt directly. After `sh` produced `XDSL>`, both `id` and `uname -a` returned unknown-command errors listing vendor commands. No POSIX shell was demonstrated. The owner reported no useful additional commands yet. This check was logged out/disconnected.

Follow-up transcript `.local/askey-net-005/inner-shell-check.typescript`, SHA-256 `cc1f76762df5e287ebacf2ac5b4b53a6b546fc7d2d839b1c4c450f849439317c`.

## Next bounded step

Read the complete 64-byte header from the same validated flash region and compare all fields against the related parser before trusting image length or compression metadata. If consistent, plan paced chunk reads of the running image and offline validation/decompression to locate the actual privilege checks and native execution interfaces. Do not begin an unbounded dump or execute the related device's client scripts as a package. No full firmware capture has been performed.

Manual laptop instructions: [Telnet guide](../telnet.md).
