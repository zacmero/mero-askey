# Native callback and loader contracts

Reviewed 2026-10-31 against the owner's captured `BR_SO_RTK_V6.1.8t` runtime. Runtime SHA-256: `b104789b795630eee7de1b50d64e49710535221f8baa6652021af6d00abb3941`; load base `0x80000000`. Addresses below are runtime addresses, not file offsets. Odd function pointers select MIPS16; instruction listings use their even physical addresses.

This pass combines bounded static analysis with the read-only observations in [ASKEY-NET-008](../docs/experiments/askey-net-008.md). It does not execute a custom callback, copy a module, or establish a POSIX shell.

## What the new privilege exposes

`sh` already entered the restricted vendor console. The approved configuration change exposed additional handlers in `XDSL#`; it did not introduce a new operating system or interpreter. The [command reference](../docs/native-commands.md) distinguishes their operations. All three descriptors require the stronger mapped parser privilege bit.

The dispatcher at `0x802a2de8` selects `webdll` → `0x802a277c`, `loaddll` → `0x802a27d0`, and `chksum` → `0x802a2730`. After the selected handler returns, its shared epilogue at `0x802a308a`–`0x802a3094` sets `v0=1`. **The command-dispatch return therefore does not preserve a loader result or checksum value.** A returned prompt alone is not an acknowledgement of the intended effect.

## `webdll`: entry, returned callback, execution context

The bounded handler is `0x802a277c`–`0x802a27b8`:

| Stage | Code-supported contract |
| --- | --- |
| Argument lookup | Calls `0x8029b17d` with selector 1 and an output slot at `sp+16`, then loads that slot as the first target. |
| First call, `0x802a2796` | Indirect call through `v0`; `a0=0x12345678`, `a1=0x805f1648`. |
| First return | Copies returned `v0` to saved register `s1`; prints it using `going to unloadFunc=0x%x`. |
| Second call, `0x802a27aa` | Immediately calls `s1`, again with `a0=0x12345678`, `a1=0x805f1648`. No later unload event is awaited. |
| Return to dispatcher | Restores its 40-byte stack frame, `s0`, `s1` and return address. The dispatcher's shared epilogue replaces the handler result with 1. |

The first result must be a callable return/cleanup target, not an ordinary status code. Neither indirect call has a local null, range or instruction-mode check. There is no allocation, image transfer, checksum validation, relocation, cache maintenance, new task or process launch in this handler.

The handler calls synchronously in its inherited task/stack context. Its two calls use `v0` and `s1`; it does not establish that `$t9` contains the callee's entry address. An ordinary PIC/shared-library bootstrap that assumes that register is populated is therefore unverified. It also does not save/restore `gp` around the custom call. Startup's fixed `gp` and conventional saved-register behavior are evidence about the resident runtime, not a complete public ABI. Floating-point convention, stack alignment at this particular call boundary, scheduler/reentrancy rules and cleanup lifetime remain unproven.

Argument extraction at `0x8029b17c`–`0x8029b1aa` searches parsed argument IDs. A match stores the value and returns 1; failure returns 0 without initializing the destination slot. `webdll` and `loaddll` do not check this status before dereferencing/calling the slot. Missing or malformed arguments must not be used as help/discovery probes.

## Supplied interface: one confirmed output function

At `0x805f1648`, the captured word is the tagged pointer `0x8013733d`. A live read confirms that pointer and the following zero word. Adjacent data becomes CLI grammar/registration data; it is not evidence of a general exported SDK or allocator table.

The full 16-byte live window is **not** identical to the image: an adjacent descriptor's flags word at `0x805f1654` is `0x10400000`, versus initializer `0x00400000`. Its changed bit's role was not established here. This does not change the verified callback word, and it is not a reason to treat all runtime data as immutable firmware constants.

The wrapper at `0x8013733c` saves incoming argument registers into a varargs area and invokes `0x801372b5`. This supports a format-string/variadic argument interface. It does not establish compatibility with every C library format specifier.

### Allocation, lifetime and return value

The body at `0x801372b4`–`0x8013731a`:

1. Requests 3076 bytes through allocation wrapper `0x80011b74`. If allocation fails, it returns 0.
2. Constructs a formatting descriptor with a buffer pointer at allocation+4 and a count of 3072.
3. Enters a task/scheduling-related bracket through `0x801718f5`, calls formatter `0x80136d25` with emitter `0x8013746d`, then sends the descriptor to output routine `0x80137069`.
4. Leaves that bracket through `0x80171895`, frees the allocation through `0x80011b64`, and returns **1**.

This is a printf-like callback with a normal return of 1, **not a confirmed character-count return**. The normal path does not propagate output-delivery errors. The temporary formatting buffer is owned and freed within the call; no retained buffer is returned to a module. The 3072-byte descriptor count alone does not prove a total output-length limit, because the emitter contains flush/reset paths.

The bracketing routines manipulate a current-task flag and a nesting counter while protecting updates through a status/interrupt-related helper. Their complete public locking/reentrancy contract was not recovered. They must not be renamed a proved mutex API.

### Output destination: fixed context, not guaranteed Telnet

The formatter passes the **fixed context address `0x80914ffc`** to `0x80137069`. The latter selects output paths from context state; it does not receive the calling module's Telnet socket as an argument. A sibling formatter used for the handler's `unloadFunc` diagnostic also uses this fixed context. A successful formatter return is not proof that text reached the current Telnet client.

One branch uses a diagnostic ring through `0x802edb69` / `0x802edb9d`. Static code accesses its control object at `0x8091ec68`, with buffer pointer at +0, indices at +8/+12, and enable/state at +16. The bounded live read found the pointer, indices and enable/state all zero. No ring payload was read.

The default character path reaches `0x80167781`, which uses a hook at `0x8064c2b4`. Live hook value: **`0x803c4dd9`**. Its captured code calls `0x803c4a9d`; that routine checks a status byte at **`0xb8002014`** for mask `0x40`, and on the ready path stores the output byte at **`0xb8002000`**. This is consistent with a UART-style console backend. It is not proof of physical pinout, voltage, observed serial output, or which routing branch the live fixed context selected for every call. No direct MMIO read/write or hardware connection was performed in this experiment.

## `loaddll`: a header-described copy, not execution

The bounded handler is `0x802a27d0`–`0x802a283a`. It looks up argument 1, prints header fields, and only then checks the first word against `0xa0000003`.

| Header offset | Use in this handler |
| --- | --- |
| +0 | Printed key; compared with `0xa0000003`. |
| +4 | Copy destination, also printed as `dramaddr`. |
| +8 | Body byte count. |
| +12 | Printed as entry; not called. |
| +16 | Printed 16-bit checksum; not checked against the body here. |
| +18 | Printed type byte. |
| +19 / +44 | Printed as date/version strings. Their termination is not bounded locally. |
| +60 | Printed `flashp`; not a flash-write operation in this handler. |

On magic match it calls `0x8000607c` with destination from +4, source=header+64, and length from +8. No mismatch-to-safe-buffer check protects the earlier header/string reads. The bounded handler contains no allocation, source/destination range validation, destination ownership test, checksum enforcement, decompression, relocation, instruction-cache operation or branch to the entry field.

The copy wrapper returns the destination on its normal path. It uses a forward byte path and an optimized helper at `0x80007380`; some bulk-helper instructions are not decoded by the standard MIPS32 configuration used here. Complete overlap behavior and read/write footprints have not been established, nor has cache coherency for newly copied instructions. Do not infer `memmove` semantics or executable placement from the wrapper's name/shape.

`loaddll` consumes an address of an already present header; it does not fetch a filename or receive bytes over the network. Its copy and `webdll`'s call are separate operations with separate prerequisites. The archived compressed running image is not a native module for this command: its load destination is the current runtime base and the handler does not decompress it.

## `chksum`: bounded read test and its limit

The handler loads address and length from parsed slots +136/+140, sets initial accumulator 0, and calls `0x803c58f1`. The routine accumulates big-endian 16-bit words, uses the high half of a final odd byte, folds carry, and on the nonempty path normalizes `0xffff` to zero. It does not complement the final nonzero folded sum. The handler prints through the fixed-context callback and returns 1; the dispatcher does not expose the numeric checksum as a command result.

One live command, **`chksum 0xb4010000 0x40`**, targeted only the independently captured, aligned 64-byte image header. The offline expected folded checksum is **`0x347d`**. The response contained the command echo and `XDSL#`, with no checksum line or error text. **The numeric checksum was not observed or verified live.** This is compatible with the output-routing gap above, but does not prove that routing was the only cause. No alternate address, repeated checksum loop or output-state change was attempted.

## Verification boundary and next questions

Established: privileged help visibility; the live interface word; a live output hook and disabled ring; the two-stage callback call contract; allocator/free ownership within the formatter; the formatter's 0/1 return; loader copy/header behavior; and the dispatcher's discarded handler result.

Still needed before a custom executable trial:

- A supported temporary transfer/allocation path with demonstrated ownership and bounds. Neither the published pool start nor `loaddll` itself provides it.
- A reliable observation channel for the entry and immediate returned callback. Formatter return 1 and a returned CLI prompt are insufficient acknowledgements.
- Confirmed instruction-mode, caller/callee state, cache and cleanup contracts for that placement and call path. A Linux executable/shared library remains unjustified.

No loader copy, arbitrary address call, custom program, firmware write, direct MMIO operation or hardware hookup occurred. The separate live-session capability-field research road remains OPEN; this pass did not retry the previously blocked follow-up.
