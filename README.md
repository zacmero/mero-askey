# Mero Askey — RTV9015VW

Investigation of the owner's Askey RTV9015VW. Goal: a genuine OS shell and a reproducible program of our own running natively. Vendor menus, browser JavaScript and a custom web UI do not satisfy that goal.

## Latest device result — 2026-10-31

The MSI/Askey path is reverified. After an explicitly approved two-field settings import and reboot, admin Telnet now reaches **`XDSL#`**, and filtered help exposes **webdll, loaddll and chksum**. Support web access still works; the fresh export exactly matches the reviewed candidate. This is privileged vendor CLI access; no OS shell or custom native execution has been demonstrated. See [ASKEY-NET-007](docs/experiments/askey-net-007.md) and the [current handoff](HANDOFF.md).

## Firmware milestone — 2026-10-27

The complete 8 MiB flash map and complete running image are captured, verified and saved in [firmware/](firmware/README.md), as explicitly requested by the owner.

| Artifact | Size | SHA-256 |
| --- | --- | --- |
| [Full flash](firmware/rtv9015vw-br_so_rtk_v6.1.8t-fullflash.bin) | 8388608 bytes | `e5c171d08d5c3131cd7b8a4c7180e3ac277408c8072b96e335495f3b68e1fc2f` |
| [Running image](firmware/rtv9015vw-br_so_rtk_v6.1.8t-run-image.bin) | 2954688 bytes | `74ff08b030051cce67e4c637cbb46d7cc7dfd629e04271a9fb83ebab3cc76ad6` |

Verification covers 8192 contiguous chunks, raw-response reassembly, independent calibration/header captures, eight hardware readbacks, image checksum/decompression and settings-container checks. The detached capture service finished successfully and logged out. **Device-side work for today is complete; the Askey may be powered off.**

## Established access and runtime

- Model RTV9015VW, hardware UI revision `Rev:01`, firmware `BR_SO_RTK_V6.1.8t`, build `Feb 20 2017 19:16:25`, SDK `V1.2.1`, firmware family string `8671x`.
- Native admin/support web access and Telnet login work after explicitly approved settings changes. The persistent changes are only expanded-menu flags and Telnet enablement.
- Captured firmware identifies OSK with mixed big-endian MIPS32/MIPS16 code. Exact SoC/clock, physical RAM and a Linux/POSIX ABI remain unverified. The reported 22.719 MiB memory pool is not installed RAM capacity.
- `sh` opens another vendor console: initially `XDSL>`, now `XDSL#` after the approved privilege settings. `id` and `uname -a` were rejected in the earlier restricted console; they were not retested in the latest experiment. No genuine OS shell or arbitrary native program has run yet.
- Static analysis explains CLI privileges and identifies native call/copy/checksum handlers. Their appearance in privileged help is now verified; the handlers themselves remain unexercised. The reported backup-image slot is erased; working recovery is not demonstrated.

## Read next

- [Handoff](HANDOFF.md): authoritative state, operator constraints and next research questions.
- [Verified specifications](docs/device-specs.md) and [manual Telnet guide](docs/telnet.md).
- [Newly exposed native commands](docs/native-commands.md): what the higher-privilege console exposes and the distinct call/copy/checksum behaviors.
- [Consolidated firmware analysis](research/firmware-analysis.md), with three detailed static-analysis reports.
- [Open research leads](research/open-research-leads.md): live-session capability-field research remains **OPEN**, explicitly retained by the owner.
- [Extracted primary-source leads](research/related-investigations.md) and [source index](research/sources.md).
- [Full capture record](docs/experiments/askey-net-006.md) and [artifact manifest](firmware/manifest.json).

The full-flash artifact is retained unredacted per the owner's explicit instruction. Other raw sessions, passwords, settings exports and intermediate analysis stay in ignored `.local/`. No firmware/bootloader write, factory reset, hardware connection or native payload execution occurred in this milestone. See [AGENTS.md](AGENTS.md) before further work.
