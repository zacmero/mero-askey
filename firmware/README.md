# Verified RTV9015VW firmware milestone

Captured 2026-10-27 from the owner's Askey RTV9015VW, firmware `BR_SO_RTK_V6.1.8t`. The owner explicitly requested that these final firmware artifacts be saved, committed and pushed with the repository.

| Artifact | Bytes | SHA-256 |
| --- | --- | --- |
| [Full mapped flash](rtv9015vw-br_so_rtk_v6.1.8t-fullflash.bin) | 8388608 (8 MiB) | `e5c171d08d5c3131cd7b8a4c7180e3ac277408c8072b96e335495f3b68e1fc2f` |
| [Complete running image](rtv9015vw-br_so_rtk_v6.1.8t-run-image.bin) | 2954688 | `74ff08b030051cce67e4c637cbb46d7cc7dfd629e04271a9fb83ebab3cc76ad6` |

[Manifest](manifest.json) records timing, ranges, hashes, region statistics and verification scope. The full-flash file is an unchanged, unredacted device snapshot, including settings regions, retained per the owner's explicit request. Raw sessions, credentials and incomplete/intermediate analysis remain in ignored `.local/`.

## Verification completed

- All 8192 addressed 1 KiB chunks received contiguously; raw responses independently reassemble to the exact full-file hash.
- Two independent 16 KiB calibration reads match; the independently captured 64-byte running-image header matches.
- Eight new 1 KiB hardware readbacks across boot, hardware settings, running image, flashfile, backup and end/config regions match.
- The running image retains its 64-byte header plus 2954624-byte payload. Stored checksum 0xe020 matches the big-endian one's-complement payload checksum.
- Primary LZMA decodes cleanly to 9752040 bytes after omitting only one documented zero tail byte from decoder input. Original image bytes are unchanged. Decoded runtime SHA-256: `b104789b795630eee7de1b50d64e49710535221f8baa6652021af6d00abb3941`.
- Both 64 KiB settings regions are identical, checksum-valid and canonically equivalent to the approved settings export. Hardware settings and the OSK1FS object also validate.
- The entire reported backup-image slot is erased. Recovery code contains a primary-preferred cleanup policy, so erasure alone is not evidence of a defect; a working fallback has not been demonstrated.

The sequential capture took approximately 91 minutes 17 seconds. It ran first in an attached reader, then resumed cleanly under an independent user-systemd service. Both data sessions logged out; the service finished successfully with zero restarts. This was a read-only capture. No firmware/native code was executed or flashed.

## Analysis and limits

[Consolidated findings](../research/firmware-analysis.md) link the [CLI](../research/firmware-cli-analysis.md), [OSK runtime](../research/firmware-runtime-analysis.md) and [image/web/recovery](../research/firmware-image-analysis.md) reports. [Open research leads](../research/open-research-leads.md) explicitly retain the live-session capability-field avenue for later work.

The captured code identifies OSK and mixed big-endian MIPS32/MIPS16. A POSIX shell, Linux executable ABI, safe native program loader and demonstrated restoration procedure remain unproven. Exact SoC, installed RAM and CPU clock are still not measured. These files are not approved upgrade images or proof of recoverability. Readback sampling is not a second independent 8 MiB capture.

Capture procedure, checkpoint history and raw-evidence locations: [ASKEY-NET-006](../docs/experiments/askey-net-006.md). Primary online leads: [related investigations](../research/related-investigations.md).
