# Final findings — 2026-10-27

## Verified capture

Full mapped flash 8388608 bytes SHA256 e5c171d08d5c3131cd7b8a4c7180e3ac277408c8072b96e335495f3b68e1fc2f.
Complete run image 2954688 bytes SHA256 74ff08b030051cce67e4c637cbb46d7cc7dfd629e04271a9fb83ebab3cc76ad6.
Both in firmware/ with manifest. All 8192 chunks audit, independent calibration/header, eight hardware samples, payload/decompression and settings/container checks passed. Capture service finished 0 with clean logout, no restarts. No device operation remains; power-off is safe.

## Access/runtime

Owner-approved menu flags and Telnet state persist; other settings/roles/SSH/ACL/WAN were not changed. Admin Telnet login works but sh gives another vendor console. No POSIX shell or own native program has run.

Firmware proves OSK and big-endian mixed MIPS32/MIPS16; decoded 9752040 bytes. Live pool 22.719 MiB is not physical RAM. Exact SoC/clock/RAM remain unknown.

Static code maps access mode, account priorities, CLI capability gates and native call/copy/checksum handlers. Memory store code exists without the mapped privilege bits, but no write was tested and safe live targets/lifetime are unproven. Whole backup-image slot is erased; primary-preferred recovery cleanup can explain it, not a proven defect/fallback. Both settings copies validate and match approved export semantically.

## Durable reports and open path

research/firmware-analysis.md links three exact-image reports; related-investigations.md extracts primary leads. research/open-research-leads.md retains the live-session capability-field avenue as OPEN, per owner direction; automated review of one optional follow-up is not technical rejection. Raw data/credentials/decoded settings stay .local/, except explicitly requested final firmware artifacts.


## 2026-10-31 live findings

- Code-supported sampled chip-ID global measured `0x00016405`; low 16 bits `0x6405` match a firmware branch. Exact chip/clock/RAM identification remains incomplete.
- Explicitly approved access mode 2/admin priority 1 import persisted byte-for-byte. Support web access survives; admin Telnet now reaches `XDSL#`.
- Filtered root help exposes `webdll`, `loaddll`, `chksum`. Privileged vendor CLI access is established; native handler execution and OS shell remain unproven.
- Full details, actual hashes, rollback and protocol correction: [ASKEY-NET-007](docs/experiments/askey-net-007.md). Live-session capability-field avenue remains OPEN.


## Native contract review — 2026-10-31

- webdll invokes the returned callback immediately; loaddll copies a body without entry execution or local allocation/decompression. Dispatcher overwrites handler returns with 1.
- Supplied formatter owns/frees a 3076-byte allocation, normally returns 1 and does not acknowledge Telnet delivery. It uses a fixed output context. Live callback pointer matches the captured firmware.
- The diagnostic ring is disabled; a live character hook traces statically to a UART-style backend. One bounded checksum request produced no numeric response, so the offline expected `0x347d` is not a live verified result.
- Evidence, limits and next questions: [native contracts](research/firmware-native-contracts.md) and [ASKEY-NET-008](docs/experiments/askey-net-008.md). No callback/copy/payload execution claimed.
