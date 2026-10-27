# ASKEY-NET-006 — Full firmware/flash capture

Date: 2026-10-27, UTC−03:00. Status: full capture, independent verification and static analysis completed; final artifacts saved in the repository.

## Authorization and scope

The owner explicitly requested full firmware extraction for analysis, documentation of the online leads, and saving the firmware in the repository. This authorizes read-only capture. The final verified firmware artifacts will be retained under `firmware/` and made eligible for Git tracking, overriding the earlier ignored-only artifact convention for these requested final files. Raw logs, credentials and incomplete captures remain ignored under `.local/`.

No memory write, firmware upgrade, reset, new service activation or account change is part of this experiment.

## Source and local preflight

Extracted primary-source leads are in [related investigations](../../research/related-investigations.md). The locally verified flash map is `0xb4000000` through `0xb4800000` (8 MiB), run image start `0xb4010000`.

Reverified laptop Ethernet route, source address and target neighbor before each connection. A small Python standard-library reader runs Telnet on the already authorized laptop. Only verified login/navigation, `memory show`, and logout operations are used. Every response must provide complete contiguous byte rows for the exact requested address and length. Any malformed response, gap, duplicate or short read stops the job.

Each binary chunk is flushed and fsynced before its hash/checkpoint advances. Raw responses are retained as compressed JSONL. The reader can resume from a validated checkpoint. It never writes to the router.

Tool: `tools/capture_flash.py`. Parser self-check covers known data and malformed/gap/duplicate/short responses. No downloaded research script was executed.

## Header and calibration results

- 64-byte header read succeeded; its first 16 bytes match the independently captured ASKEY-NET-005 sample. Header SHA-256 `19cef9e17ca1c90cda12fd579af2ddc18c80ae9528e89c32130d5a2e0e871348`.
- Header fields under the related OSK layout: signature `0xa0000003`, load address `0x80000000`, payload length `0x002d1580` (2954624 bytes, plus the 64-byte header), entry `0x80949288`, timestamp `Mon Feb 20 19:20:51 2017`, image name `router.`, page size `0x4b780`. The remaining image must validate these interpretations; no executable ABI is inferred yet.
- Two separate 16 KiB reads of flash base using 1 KiB chunks match exactly: SHA-256 `da741736606dff7dedd3debb5aa4a6dfe2e3fe7b7fdd1c8ab79fba14204e3a2c`.
- TCP immediate-acknowledgement tuning did not materially improve the approximately 0.61-second command response time. Full capture uses one persistent connection, 1 KiB requests and 0.05-second pauses. Initial effective rate approximately 1500 bytes/second; estimated full-pass duration roughly 90–95 minutes.

## Active capture / recovery

Command on mero-machine:

```sh
rtk proxy python3 tools/capture_flash.py --start 0xb4000000 --size 0x800000 --chunk 0x400 --pause 0.05 --output .local/askey-net-006/fullflash-pass1.bin
```

Initial unified exec session at launch: `94387` (retired during the clean detached-service handoff below). Checkpoint `.local/askey-net-006/fullflash-pass1.bin.json` records captured bytes, prefix hash and completion. Resume only through the tool's `--resume` mode with the same start/size/chunk/output. Do not start another simultaneous capture or truncate/overwrite the active output.

The router should remain powered and Ethernet connected, with configuration unchanged during the read. Ordinary read-only show commands can coexist, but no settings change should be mixed into a flash snapshot. The capture does not provide a useful estimate of full installed RAM.

The laptop must remain awake because it owns the physical Ethernet path and runs the Telnet reader. Current parser validation has found no gaps, repeated addresses or malformed byte rows. The full-pass prefix and run-image header also match the independent calibration captures while the job continues.

## Early offline analysis while capture continues

The complete page region was already within the captured prefix. Standard-library LZMA decoding recovered 52 concatenated streams, yielding 1213785 bytes of encoded web-source records and 115 extracted files. The remaining 63326 bytes of the declared page region begin with `GIF89a`, consistent with image assets. No decoded source or firmware code was executed.

Decoded source SHA-256: `aaec79eb50f5e5b9d814363a3a87163198a8d95880d3e0033b535dc55d681364` (retained privately in `.local/askey-net-006/analysis/web-pages.decoded`).

Concrete findings from this exact firmware's pages:

- `telnet_onoff.htm` posts to `form2Telnet.cgi`; radio values 0/1 are explicitly Disable/Enable. This corroborates the already completed Telnet-state experiment with local firmware evidence.
- `debug.htm` is SAR packet diagnostics/port mirroring, not an OS shell or arbitrary-command form. No diagnostic setting was submitted.
- `upload.htm` is firmware upload/update only; it is not a demonstrated firmware export/download path. No firmware-write form was submitted.

The primary runtime stream starts at flash-file offset `0x5b7c0` under the inspected header layout. Its LZMA properties byte is `0x6f`, dictionary 8388608 bytes, declared decoded length 9752040 (`0x94cde8`) bytes. Adding the reported load base `0x80000000` reaches `0x8094cde8`, exactly the memory-pool start printed by the live console. This is a strong local consistency check, not a completed decompression or executable-ABI identification.

The installed `7z` can decode the available prefix despite properties that standard liblzma may reject. The partial-input test intentionally returned Unexpected End of Data and is marked incomplete; it is not being treated as a valid full runtime artifact. No custom downloaded decoder was executed.

## Completion gate (still pending)

Before final artifacts are promoted into `firmware/`: confirm all 8388608 requested bytes, strict row/address validation, clean process completion and stable readback samples. Reconcile the flash prefix with calibration and the run-image prefix with the independent header; inspect the image layout and carve the complete declared run image only if its boundaries validate. Record actual SHA-256 hashes and all verification limits. A reported backup slot alone is not a verified recovery image.

## Complete running image validated and saved

The reference parser confirms that header field `0x08` is **payload length**, excluding the 64-byte header. The first tentative carve treated it as a total and was 64 bytes short; strict decompression rejected it before promotion. The corrected total is 2954688 bytes (`0x2d15c0`), not 2954624. The corrected image had a complete output plus one zero tail byte; the documented reference padding rule resolved that without altering any bytes in the retained original image.

Final running image: `firmware/rtv9015vw-br_so_rtk_v6.1.8t-run-image.bin`, 2954688 bytes, SHA-256 `74ff08b030051cce67e4c637cbb46d7cc7dfd629e04271a9fb83ebab3cc76ad6`.

- Header matches the independent 64-byte capture.
- Payload ones-complement 16-bit checksum is `0xe020`, matching the stored checksum.
- One zero-padding byte excluded only from decoder input, following the inspected reference rule.
- Installed 7z then exits 0 and produces exactly the declared 9752040 bytes.
- Decoded runtime SHA-256 `b104789b795630eee7de1b50d64e49710535221f8baa6652021af6d00abb3941`.
- Runtime contains `-OSK1FS-`, `oskFatal`, `oskError`, `../../swbase/kernel/SWITCH/osksub.c`, and OSK driver paths including rtl8192er. This directly identifies the captured firmware's OSK runtime family; the earlier RTOS inference now has local firmware evidence.

The full 8 MiB pass is still active. The running image is a complete firmware component, not a replacement for the still-pending full-map artifact. No image was executed or uploaded to the router. Capture state and validation metadata remain under `.local/askey-net-006/`.

## Detached service handoff — owner explicitly requested independence

The owner asked that the backup continue independently even if the agent stops. A user-systemd service preflight succeeded. The existing user already had `Linger=yes`; no linger/global setting was changed.

Requested SIGINT only for the positively identified remote reader process. It ran its logout cleanup and the initial capture exited intentionally incomplete at **4215808 bytes**, with the binary size and checkpoint SHA-256 both matching `a1e315fb181ef27adf9fa8eee96eede563da2287e37c615286eb26b9672ca89c`. No data was discarded or guessed.

Started transient user unit **`mero-askey-firmware-capture.service`** using the same capture arguments plus `--resume`. It validated the saved prefix and resumed at the next byte. Verified that its process is parented by the user systemd manager, stdin is `/dev/null`, and stdout/stderr append to its own log. Its capture counter advanced after this handoff.

- Unit: `mero-askey-firmware-capture.service`.
- Log: `.local/askey-net-006/capture-service.log`.
- Process/unit record: `.local/askey-net-006/capture-service.json`.
- Authoritative data/checkpoint paths remain unchanged.
- Restart on failure: 30-second delay, bounded by three starts within 600 seconds; every restart revalidates target identity and prefix hash before continuing.
- This survives the agent turn and SSH logout through the already-enabled lingering user manager. A machine reboot/power loss still requires resuming the on-disk checkpoint; the transient unit is not a boot-enabled service.

Read-only status commands on mero-machine:

```sh
rtk proxy systemctl --user status mero-askey-firmware-capture.service
rtk proxy cat .local/askey-net-006/fullflash-pass1.bin.json
```

No new router setting was changed during the handoff. Do not start a duplicate capture. The old unified exec session is no longer the process owner.

## Parallel offline analysis

The owner explicitly authorized analysis agents. Three agents own separate reviewed reports: `research/firmware-cli-analysis.md`, `research/firmware-runtime-analysis.md`, and `research/firmware-image-analysis.md`. They analyze the captured image and checkpoint-bounded snapshots only; no device traffic, firmware execution, account change or memory write is authorized for those agents. Their hypotheses must remain separate from code-supported conclusions.

## Completed full capture and readback verification

The service completed all 8388608 bytes at Unix time 1793082875.3403845, logged out, and exited successfully with zero restarts. Total capture duration was 5477.4 seconds (approximately 91 minutes 17 seconds). The final checkpoint is complete=true.

Final full artifact: `firmware/rtv9015vw-br_so_rtk_v6.1.8t-fullflash.bin`, SHA-256 `e5c171d08d5c3131cd7b8a4c7180e3ac277408c8072b96e335495f3b68e1fc2f`.

An offline audit of every retained raw response confirms 8192 contiguous 1 KiB chunks, two logged-in/logged-out data sessions across the deliberate handoff, and one completion record. Reassembling all responses exactly reproduces the full-file hash. Eight new independent 1 KiB reads at offsets 0,0x5000,0x10000,0x2e1000,0x3f8000,0x400000,0x7e0000 and 0x7ffc00 all match the completed file. This is sample readback, not a second entire 8 MiB capture.

Private records: `wire-audit.json`, `readback-verification.json`, capture log/checkpoint, and all original raw responses under `.local/askey-net-006/`. Public [manifest](../../firmware/manifest.json) records actual files, hashes, ranges and limits.

Independent final image analysis verifies:

- Entire backup-image slot 0x400000..0x7e0000 (4063232 bytes) is 0xff. Runtime recovery cleanup policy can explain this; no working fallback is claimed.
- Both 64 KiB configuration regions are identical: SHA-256 `019ecc4de8ac7c16b16ff4b41916fcce7fe18aae3b44de22364ef810530202ce`. Container checksums validate.
- Their decoded XML is canonically identical to the approved settings export. The raw XML byte-length difference is formatting; all 4798 flattened records match.
- Hardware settings and the OSK1FS object also validate. Decoded settings remain private; the owner explicitly requested preservation of the full unredacted flash artifact in Git.

Detailed [image analysis](../../research/firmware-image-analysis.md) and [consolidated report](../../research/firmware-analysis.md) distinguish byte observations, static code conclusions and unresolved behavior.

The owner requested to power off the Askey after capture. Confirmed safe because all device-side capture and verification had completed and sessions were closed. Actual power-off was not observed. No further device operation is planned today; reporting and Git publication operate on local files only.
