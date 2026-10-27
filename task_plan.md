# 2026-10-27 milestone — device work complete

## Completed

- Identified device/laptop path and preserved household control.
- Explicitly approved menu/Telnet edits applied and verified; no other persistent device change.
- Full 8388608-byte flash and complete 2954688-byte run image captured and saved under firmware/ with actual hashes.
- Detached systemd capture survived a clean checkpoint handoff and finished successfully. No device read/write remains active; Askey may be powered off.
- 8192-chunk wire audit, independent calibration/header, eight hardware readbacks and image/settings/container checks passed.
- Three offline analysis reports and consolidated findings saved, with exact evidence and limits.
- Primary-source leads extracted into docs. Open live-session capability-field path explicitly retained per owner instruction; one tool-blocked follow-up did not close it.
- Full unredacted firmware retained in repository per explicit owner request; other raw/private data remain .local/.

## Final repository delivery

Completed final link/hash/secret/whitespace checks and parser self-check. Verified the staged firmware blobs against the artifact hashes. Committed and pushed milestone `b5cc63e` to `origin/main`; remote SHA and local HEAD matched, and the working tree was clean. This final reporting update records that delivery. No more device operations today.

## Future research, not discarded

See research/open-research-leads.md. Genuine OS shell and own native program execution remain unachieved. Exact CPU/clock/physical RAM, safe native loader/ABI/cache/ownership and demonstrated restoration remain unresolved. A future experiment needs its concrete question and existing operation-specific authorization; do not infer permissions or safe addresses from names.
