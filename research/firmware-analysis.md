# Static analysis of the captured RTV9015VW firmware

Reviewed 2026-10-27. This summarizes the captured running image, not a sibling model's firmware. The complete running component is verified and saved in `firmware/`; the full 8 MiB flash capture and its independent verification are complete. No target code, write operation or new configuration change was performed for this analysis.

## Artifacts and independent checks

| Artifact | Size | SHA-256 |
| --- | --- | --- |
| [Running image](../firmware/rtv9015vw-br_so_rtk_v6.1.8t-run-image.bin) | 2954688 bytes | `74ff08b030051cce67e4c637cbb46d7cc7dfd629e04271a9fb83ebab3cc76ad6` |
| Decoded OSK runtime, private analysis artifact | 9752040 bytes | `b104789b795630eee7de1b50d64e49710535221f8baa6652021af6d00abb3941` |
| Decoded web-source records, private | 1213785 bytes | `aaec79eb50f5e5b9d814363a3a87163198a8d95880d3e0033b535dc55d681364` |

The 64-byte header is followed by a 2954624-byte payload. Its stored checksum `0xe020` matches the big-endian one's-complement payload checksum. Fifty-two page streams decode independently and expose 115 web files. The primary runtime decodes completely after excluding one zero-padding byte from decoder input; the saved original image retains every byte.

Addresses below use runtime load base `0x80000000`; an address is not a file offset. Details and short evidence are in the three specialized reports linked below.

## What the system actually runs

The image contains the OSK kernel and OSK1FS support, with mixed **big-endian MIPS32 and MIPS16** instruction streams. Startup code and mode-tagged control transfers provide opcode evidence; this is more than a string/chip-family inference. The entry is `0x80949288`, and the decoded-image end `0x8094cde8` exactly matches the independently observed live memory-pool start.

No ELF image, BusyBox, `/bin/sh` or Linux process/system-call ABI has been established. Pthread-like compatibility strings do not establish POSIX userland. A conventional Linux MIPS binary is therefore not a justified test artifact. An OSK-native routine would need the actual call, memory and cache contracts.

Exact SoC model, CPU clock, installed RAM and precise proprietary kernel revision remain unverified. The live 22.719 MiB pool must not be called total physical RAM. A code-supported RAM snapshot of a hardware identification register is a possible later read-only specification probe; its image initializer is not a live chip ID.

See [runtime/ABI analysis](firmware-runtime-analysis.md).

## Why the current CLI is restricted

`ENABLE_ADVANCE_PAGE` is an access mode, not merely a Boolean menu switch. The value is also rendered into pages as JavaScript `ServiceMode`.

- Modes `0` and `1` can clear both native CLI privilege bits during authentication for the tested session conditions. Mode `1` selects `user04Menu`.
- Mode `2` has an explicit administrator-menu branch and preserves account-derived privilege bits at that gate. It also changes HTTP routing restrictions; it is not an isolated terminal toggle.
- The actual `USERNAME_PASSWORD` descriptor proves that account field offset 132 is `PRIORITY`. Value `1` sets both checked CLI capability bits; value `2` sets only the weaker bit 7. Other values do not receive those bits through the mapped branch.
- Outer `config` and `diagnostic` entry checks require bit 7. The hidden `webdll`, `loaddll` and `chksum` root nodes require the stronger bit 6, and the help parser applies the same capability filter.

The owner accounts currently export `PRIORITY=2` and mode `1`; the observed privilege denials are consistent with this code. **Mode `2` alone would not grant the stronger native-call/copy nodes to those accounts.** It is predicted to pass the mapped outer configuration/diagnostic entry checks, conditional on the remaining session/path checks.

These are static control-flow conclusions, not a live authorization-bypass or shell demonstration. No priority or access-mode change has been applied during analysis. Hidden web-form privilege numbers must not be assumed to equal stored account priorities.

See [CLI privilege analysis](firmware-cli-analysis.md).

## Native execution interfaces found, with important limits

The captured code has proprietary native interfaces rather than a proven POSIX executable loader:

| Entry | Bounded code-supported behavior | Unresolved prerequisite |
| --- | --- | --- |
| `webdll` | Calls an address, saves its returned callback, then calls that callback | A valid return/unload contract, ABI, safe allocation and cache coherence; returning zero would not be a safe marker |
| `loaddll` | Checks an image key and copies the header-described body to its destination | Range/ownership, payload format, allocation and later entry behavior; the bounded handler does not prove relocation or safe loading |
| `chksum` | Computes/displays a folded checksum over a region | It is not an executable loader |

The native callback receives a fixed argument and a pointer containing a printf-like callback; that pointer is not proven to be a general SDK symbol table. Task registration and allocation routines were identified offline, but callable signatures and lifecycle constraints have not all been established. No test payload or device-write recipe was produced.

The lexical table was independently reconciled: `command` is token 15 and has a root record; token 17 is `timer`. Neither fact changes the verified mapping of `webdll`/`loaddll`/`chksum`, and the `command` label is not proof of a POSIX shell.

### Memory access is a separate capability path

The recovered `memory show` and `memory set` roots, children and terminal numeric nodes do not request either of the two native parser capability bits. The display path reads byte-counted regions; a live display read was reproduced during capture. The set handler has direct compiled 8-, 16- and 32-bit store instructions. This is stronger evidence than a help label, but **no live write was tested**.

The bounded store handler did not reveal an address allowlist, alignment repair, ownership check or rollback mechanism. Its existence does not establish a safe/recoverable write target. It also means that hiding higher-privilege native commands is not the whole memory-access trust boundary. Our capture tool restricts itself to the independently measured flash range and never invokes a store operation.

## Web maintenance and updater findings

The exact firmware includes Telnet, hidden maintenance, factory-test, MP access, firmware-update and bootloader-related forms. Their existence does not demonstrate that the current web account may execute them.

- `telnet_onoff.htm` explicitly uses 0/1 for Disable/Enable, corroborating the completed service activation.
- `debug.htm` concerns SAR tracing and port mirroring, not a shell.
- Hidden maintenance callbacks affect multiple settings and identity fields. The backend also reads an `ftpEnable` input absent from the extracted template and writes an additional MIB whose exported name remains unresolved. A blind form submission could have collateral effects.
- Ordinary updater paths check recognized image keys, an IC/model field and payload checksum. The run image satisfies the mirrored bounded tests offline; the full-flash file begins with boot code, not an accepted raw firmware-image key.
- No signature-verification call was found in the bounded mapped validator chain. This is not proof that every update/boot path lacks signing, nor that a modified image would be accepted.
- Upload framing, complete destination/range handling, deferred writer behavior and bootloader constraints remain unresolved. The raw dump and carved image are not approved restoration/upgrade files.

See [image/web/recovery analysis](firmware-image-analysis.md).

## Backup and recovery

The reported backup slot starts at flash offset `0x400000`. The complete slot from offset 0x400000 through 0x7e0000 is erased, with no ordinary image header. Full snapshot and container checks are complete.

Static recovery code prefers the primary and includes backup cleanup when the primary validates; only the backup-valid/primary-invalid branch copies backup to primary. An erased backup can therefore be normal policy and is not by itself proof of a defect. No working fallback or physical restoration method has been demonstrated.

A small OSK1FS object at `0x3f8000` was independently parsed and checked. It contains one CWMP notification text file, not a native executable. Credentials and proprietary source bodies remain outside these reviewed reports.

## Next bounded work

1. Completed: full map retained in `firmware/`, hash/size and wire audit verified, and eight independent hardware readback samples match.
2. Completed: whole backup slot is erased; both configuration containers validate and match each other and the approved export. See the image report for exact scope and recovery limits.
3. Continue the unresolved session-object, hardware-snapshot and allocation/cache questions in [open research leads](open-research-leads.md). The owner explicitly retained the live-session capability-field path; the earlier automated review block does not close it.
4. If the owner requests a device experiment afterward, prepare exact settings/rollback and obtain the actual operation instruction required by AGENTS.md. A read-only diagnostic-entry test is a separate milestone from arbitrary native execution.

Broader success criteria remain open: a genuine OS shell and a reproducible program of our own have not yet run on the device.
