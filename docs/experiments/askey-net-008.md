# ASKEY-NET-008 — Native interface and output-contract verification

Date: 2026-10-31, UTC−03:00. Status: bounded offline contract review and read-only live observations complete; native callback/copy execution remains untested.

The owner requested documentation of the newly exposed commands and continued native callback/loader contract verification. This experiment makes no further persistent setting change. Detailed static evidence and open questions are in [native contracts](../../research/firmware-native-contracts.md).

## Method and live scope

Reused the known MSI SSH key. Before device traffic, the reader rechecked the laptop's cable route, source interface/address and recorded Askey neighbor. Admin login reached `XDSL#`. Raw captures, scripts and analysis remain ignored under `.local/askey-net-008/`.

The first session performed only:

1. `memory show 0x805f1648 length 0x10` — bounded ordinary RAM read of the supplied interface and adjacent descriptor.
2. `chksum 0xb4010000 0x40` — one checksum request over the independently captured 64-byte flash image header.

The interface word is `0x8013733d`, matching the captured formatter callback; the next word is zero. An adjacent grammar descriptor's flags at `0x805f1654` differ from the image initializer: live `0x10400000`, image `0x00400000`. The entire window must not be reported as matching.

The checksum request returned only echo and `XDSL#`. No checksum line was observed. The local verification script originally required that line and therefore failed its assertion **after the session had already logged out cleanly**. The final result records an unverified live checksum, not a successful numeric comparison. Offline expected value is `0x347d`; the test was not repeated.

Raw first-session log SHA-256: `e73b2c07443807c657771e667515e80723594ae8a97506d66e84a4cc1004a7b7` (`contract-readback.jsonl`).

A second session addressed the new question of which fixed output sinks were initialized, without calling a native address or issuing a direct MMIO access:

1. `memory show 0x8091ec68 length 0x20` — diagnostic ring control object, identified statically.
2. `memory show 0x8064c2b4 length 0x10` — output-hook data, identified statically.

The ring buffer pointer, indices and enable/state are zero. No ring payload read followed. The live character hook is `0x803c4dd9`; captured code traces it to a UART-style byte-output backend. This supports a concrete reason to investigate output routing but does not prove the precise branch used by the earlier checksum call. Both sessions logged out and closed their sockets cleanly.

## New contract findings

- `webdll` immediately invokes the callback returned by its first target, with the same fixed arguments. It does not defer cleanup to a later unload command.
- The supplied printf-like callback owns a temporary allocation, frees it within the call, and normally returns 1; initial allocation failure returns 0. It does not return a confirmed character count or delivery acknowledgement.
- The formatter routes through a fixed context, not an explicit caller-supplied Telnet endpoint. The ring is disabled; the installed character hook leads to a status-check/byte-write MMIO backend in static code. No physical output was captured.
- `loaddll` prints header fields, checks one magic word and copies a body. It does not execute the entry field or perform decompression/relocation in this bounded path.
- The common CLI dispatcher overwrites a handler's returned value with 1. A returned prompt cannot validate a copy or checksum result.
- The native argument extractor can fail without initializing the output slot, and these two handlers ignore its status. No malformed native-command probe was attempted.

No `webdll`/`loaddll` invocation, custom callback, memory-store command, new upload, reset, firmware write or hardware connection occurred. The original firmware snapshot remains unchanged. No genuine OS shell or custom native program is claimed.
