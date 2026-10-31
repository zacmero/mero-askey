# Newly exposed native commands

On 2026-10-31, the owner's approved access-mode/account-priority change made `webdll`, `loaddll` and `chksum` visible in the filtered help at **`XDSL#`**. `sh` already opened the vendor console before this change, at `XDSL>`. The gain is privilege within that console, not first-time shell access. See [ASKEY-NET-007](experiments/askey-net-007.md).

The table separates live help visibility from behavior recovered from the captured firmware. It is a command reference, not an executable-test procedure.

| Command | What the captured handler exposes | What it does not establish |
| --- | --- | --- |
| `webdll` | A synchronous call to a parsed native address, followed immediately by a call to the callback returned by that first function. Both receive a fixed magic value and an interface pointer. | No process creation, OS shell, ELF loading, safe code placement or verified custom program. Returning zero would leave the caller attempting a second call through zero. |
| `loaddll` | Reads a header at a parsed address. If its magic matches, copies the body after the 64-byte header to the destination and length specified in the header. | No allocation, decompression, relocation, symbol lookup or call to the printed entry field in this bounded handler. A header/checksum display is not proof of validation. |
| `chksum` | Reads an address/length region and calculates a folded 16-bit checksum. Its help states `chksum address length`. | No transfer, loading or execution. Reading arbitrary hardware/register ranges is not implied to be safe. |

The `webdll` entry is not an ordinary one-call function runner: its first return value must itself be a valid callable target. The supplied interface has a confirmed printf-like callback, but a general SDK symbol table, allocator and complete output-delivery contract have not been established. The loader's destination, length and source must not be guessed from the reported memory-pool start.

The archived running image is not an approved `loaddll` module. Its header names the running system's load base and its payload contains compressed firmware components; this handler performs a direct copy, not the decompression performed during boot analysis.

The original [CLI analysis](../research/firmware-cli-analysis.md) and [runtime analysis](../research/firmware-runtime-analysis.md) retain addresses and bounded evidence. A visible command name establishes parser exposure; it does not establish a safe execution recipe or working restoration.
