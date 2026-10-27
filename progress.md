# Session progress — 2026-10-27 (-03)

## Owner retained live-session investigation

- Owner explicitly directed that live CLI session capability-field research not be discarded because one optional sub-agent follow-up was tool-blocked.
- Created research/open-research-leads.md with OPEN status, existing static evidence, unanswered ownership/lifetime questions and precise automation-limit history. Linked it from research index and consolidated analysis; current handoff will retain it.

## Early firmware analysis during full capture

- Decoded the already captured page region: 52 LZMA streams, 115 web files. Exact firmware source confirms Telnet 0/1 disable/enable form. Debug page is packet tracing/mirroring, not an OS shell. Upload page is firmware writing only, not an export path.
- Primary LZMA declared decoded size 0x94cde8 plus load base exactly matches live MemPool start 0x8094cde8. Installed 7z decodes a partial prefix; full runtime is not complete yet.
- Full 8 MiB capture remains active in exec session 94387. Firmware README explicitly marks final artifacts pending until verification; raw/partial data remain private.

## Telnet activation authorized

- Fresh live export exactly matched the current rollback before upload. Submitted the authorized one-byte Telnet-state candidate once; HTTP 200 `Autoboot`, approximately 3.493 seconds. Verifying recovery before any login test.

- Owner explicitly instructed: enable Telnet and test it. Proceeding with the prepared one-byte TELNET_STATE change, native import/automatic reboot, recovery/export verification, and bounded login test. CPU/RAM/kernel/flash specs are not yet locally established.

## Latest progress

- First post-import recovery check succeeded; route/neighbor and Wi-Fi control verified. Fresh support login and settings re-export succeeded. Export exactly matches approved candidate; full `user04Menu` now loaded. No rollback needed.
- Read native account and diagnostic pages; no terminal activation control exposed. Started related-SDK source research. Code-search connector returned unusable HTML; GitHub API is usable. Public code index rate-limited (429), no retry.

- Reverified original/candidate hashes, current Ethernet route and target neighbor. Submitted the owner-authorized native configuration import once. HTTP 200 body `Autoboot`; automatic boot/recovery verification is now in progress. No separate reboot request or service activation sent.

- Owner explicitly approved importing the prepared two-flag advanced-menu configuration and rebooting. Proceeding with native restore workflow, retaining the original export for rollback.

- Owner clarified intended stock admin credentials. Confirmed normal admin login succeeds; advanced page rejects admin.
- Documented exact-model `support` login succeeds with the owner's label admin password. Advanced interface opened.
- Retrieved actual advanced menu and export page. Exported original config via the native Save Settings File form and retained the actual artifact/hash.
- Export shows advanced page disabled, Wi-Fi-only menu enabled, and SSH/Telnet state flags zero. Inspecting service controls and flag semantics before any proposed setting change.
- One service-page and one full-menu asset hypothesis returned 404. Native status page works; no repeated filename probing planned.
- Prepared an advanced-menu candidate from the real original export, verified exactly two changed bytes, and documented both hashes and recovery. No persistent action performed.
- Rewrote current README/HANDOFF status and the experiment report to resolve earlier pending credential stages and describe the next concrete import/reboot decision.

- Read README.md, HANDOFF.md, research/sources.md and owner-provided agent instructions.
- Confirmed repository initially clean.
- Recorded owner firmware, interface/route, and bounded port-scan reports.
- Inventoried mero-machine routes and identified the incoming laptop SSH source.
- Confirmed laptop TCP/22 reachable. Requested laptop SSH username/authentication details; continued documentation while waiting.
- No router settings changed and no router tests performed by the agent yet.
- Owner identified an existing key/alias. Adjacent project notes identified the actual reverse control route; successfully logged into the laptop with the established dedicated key and checked its current route and router neighbor.
- Performed first bounded router inspection: TCP/22 and TCP/23 EOF, HTTP root and saveconf redirects, `/padrao` login form. Raw capture saved privately with hash in findings.md.
- Search tool failed with HTTP 405; fetched the known exact-model primary source directly, retained it privately, and recorded its limited applicability.
- Created `.local/router-login.json` (mode 0600) as a private credential template. No credentials have been submitted to the router.
- Followed the two native web redirects and tested initial SSH/Telnet protocol bytes once. Both TCP services still closed immediately. Default HTTPS handshake failed.
- Independently confirmed model, hardware revision and firmware through the native About page. Shared JavaScript supplied no further service/authentication lead.
- Owner filled the private credential file and then corrected the direction before any submission. Login is on hold pending clarification.
- Updated README, HANDOFF and the experiment report with measured results, retained capture hashes, and pending credential clarification.

## Menu import completed; Telnet experiment prepared

- Verified recovery, same Ethernet neighbor and preserved Wi-Fi control after the authorized automatic reboot.
- Fresh export exactly matches the two-flag menu candidate. Native full menu/account/diagnostic pages read; no terminal-service control exposed.
- Related SDK source differs from this firmware; related-device firsthand report provides a specific Telnet-state hypothesis, not exact-model proof.
- Authenticated status confirms all WAN interfaces down. Earlier expired-session redirect was excluded from runtime evidence.
- Prepared a one-byte Telnet-state candidate, documented its limited evidence and rollback in ASKEY-NET-003, and updated current handoff/README/planning notes. No activation performed.

## Telnet enabled and tested; actual system inventory captured

- Native automatic reboot recovered; fresh export exactly equals approved Telnet candidate. Telnet admin login now succeeds.
- Outer parser and inner XDSL console are vendor CLIs; id rejected, diagnostic/config denied by privilege. No OS shell established.
- Captured SDK/build/hardware-family string, 8 MB flash layout, memory-pool counters and live task table. Pool total is not physical RAM.
- Task/memory model suggests RTOS-style runtime; exact OS/CPU/ABI unknown. Related OSK bootlog retained. Original Wi-Fi certificate API returned 401, so mirror OS label remains a lead only.
- Logged out and disconnected Telnet. Final export exactly matches approved candidate. Service remains enabled per instruction; no account/ACL/WAN settings changed.
- Created verified specs and console inventory report, updated current handoff/README/plan. Native program milestone remains unachieved; matching runtime/privilege/execution entry is the next evidence needed.

## New OSK lead and flash-read validation

- Found primary V2802RH OSK investigation matching Virtual Web/CLI patterns. Read source/docs via GitHub connector and saved snapshots; did not execute its scripts.
- Verified memory show operation and captured 16 bytes from the Askey's reported run-image address. Parsed artifact retained and hashed; header interpretation remains provisional.
- Owner asked whether sh was tried. Clarified earlier outer-only id test, then directly tested id and uname -a inside XDSL>; both rejected. Logged out/disconnected both sessions.
- Documented the lead, small read, limits and next 64-byte header question in ASKEY-NET-005; added manual owner Telnet guide and current handoff/source updates. No configuration change or full dump.

## ASKEY-NET-006 full flash extraction started

- Owner asked to save extracted leads and full firmware, then explicitly emphasized firmware must be in the repository.
- Added extracted primary-source notes and small stdlib capture tool with strict parser and per-chunk fsync/hash checkpoint.
- Header64 matches earlier sample. Two independent 16 KiB calibration captures match exactly; TCP ACK tuning did not improve rate.
- Full 8 MiB capture now active in unified exec session 94387, at approximately 1500 B/s. Capture state under .local/askey-net-006/fullflash-pass1.bin.json. No firmware promoted yet; wait for complete verified capture.

## Complete running image saved while full capture continues

- Strict validation caught and corrected a 64-byte header-length interpretation before artifact promotion. The legacy stream also has one zero tail byte; documented padding handling gives clean decompression with exact size.
- Running-image payload checksum matches stored 0xe020. Original unchanged 2954688-byte image saved under firmware/ with actual SHA-256 and incremental manifest.
- Decoded runtime has OSK1FS and OSK kernel/driver identifiers, upgrading the prior RTOS hypothesis to direct local firmware evidence.
- Full 8 MiB map still reading in session 94387; final full artifact/readback/manifest work remains.

## Detached capture and parallel analysis authorized

- Owner explicitly requested capture independence and analysis agents.
- Verified user systemd manager with pre-existing Linger=yes. Cleaned up old Telnet reader via targeted SIGINT/logout; durable prefix hash verified at4215808 bytes.
- Started mero-askey-firmware-capture.service with validated --resume. Verified systemd parent, null stdin, dedicated stdout/stderr log and advancing checkpoint. Old exec94387 intentionally ended; no data loss.
- Three offline agents analyzing CLI privilege, OSK/native pathways, image/web/recovery in owned reports. Device traffic forbidden for them.

## Full capture verified; device work finished for today

- Full 8388608-byte map finished, both capture sessions logged out, service exited 0 with no restarts. Actual SHA256 e5c171d08d5c3131cd7b8a4c7180e3ac277408c8072b96e335495f3b68e1fc2f.
- 8192 contiguous chunks reconstruct exactly from raw responses. Eight independent hardware readbacks match; source/calibration/header/run-image checks pass.
- Full binary atomically promoted under firmware/, alongside complete run image and final manifest. Independent whole-slot/config-container/XML verification completed.
- Owner explicitly requested commit and push, then asked to end device work and power off. Confirmed power-off safe because capture/verification sessions were complete. No further device operations planned today.
- Current README/HANDOFF/specs/research notes finalized. Open live-session lead retained, not discarded. Final repository validation/commit/push follows.
