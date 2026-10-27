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
