# Telephony progress — 2026-11-04

Owner requested frequent-use startup, container/secret/config explanation, and a Bravia cinema phone action. Corrected unsupported restart policy "yes" to unless-stopped and updated the live container without recreation. Located the existing cinema script's --monitor argument and the Sony display DP-1. Preparing a separate user-side host command dispatcher; no Askey changes are part of the phone command service.

Owner confirmed direct dialing 20, reported an unexpected mid-menu disconnect, and requested an explanation plus a less robotic female voice. Inspected live restart policy and media/session settings; Docker is enabled, but PBX restart policy is no. Removed the menu count cap, changed idle hang-up to retry after 60 seconds, and loaded NOTICE diagnostics. Installed Piper 1.8.0 in a private Python 3.12 environment, downloaded the Lessac female narration model, corrected stdout generation with -f -, and installed five local prompts. Owner liked the preview. Wrote the full implementation map; agent/cloud adapters remain deferred.

Committed and pushed the first telephony milestone as 2565e5b. Continued with an incoming keypad test: owner confirmed hearing seven after pressing 7. Added an incoming menu, local speech prompts and a fixed three-second Askey TCP connection check; requested the owner test menu option 2 then 0. No further router setting change was required.

Owner confirmed the menu's successful connection result and option 0 hang-up. Keypad-to-network-action-to-spoken-result path is demonstrated. Outgoing short-code forwarding and agent runtime integration remain separate work.

Reviewed the telephony handoff and archived settings, confirmed the current workstation route and recorded neighbor identity, and inventoried available local tools/listeners. No voice setting or PBX service has been changed.

Added the DSL copper guide, dial-code/voice-interface guide, links and baseline experiment. The read-only voice inspector passed live and saved a fresh export matching ASKEY-NET-011. Prepared private endpoint credentials and a minimal container PBX configuration. Container image build is in progress; no Askey voice changes have been applied.

Owner explicitly approved PBX startup and the reviewed voice-only change. Built/validated the image, started the dedicated container, applied the native form with fresh CSRF and correct DOM order, and verified extension 10 registration plus unchanged LAN/DHCP. Owner reports dial tone and dialing, but first echo had no voice. Fixed the omitted res_pjsip_pubsub dependency, loaded chan_pjsip, strengthened the validation and requested another echo trial. No successful speech/ringing/DTMF claim yet.

Owner requested a direct incoming call and confirmed ringing plus hello-world playback. A first record/playback call was missed; the owner explicitly requested another call when ready. The retry completed and the owner confirmed hearing their own voice. Retained a six-second, mono 8 kHz/16-bit PCM test recording and PBX evidence privately. Updated guides and next-agent handoff with the achieved milestone. No DTMF/network-action or agent-link success is claimed.

---

# Earlier recorded work (preserved)

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


## Repository milestone delivered

- Committed and pushed `b5cc63e` (`feat: archive verified Askey firmware`) to `origin/main`.
- Verified the published remote SHA equals the local milestone commit. Both staged binary blobs match their documented SHA-256 values; parser, text-link, secret-exclusion, and whitespace checks passed.
- Firmware binaries and reviewed reports are published. Raw sessions, private credentials, settings exports, and intermediate analysis remain in ignored `.local/`.
- Device work is complete; the Askey may remain powered off. The live-session capability-field research road remains OPEN.


## 2026-10-31 — Resumed live work; privileged vendor CLI verified

- Reverified MSI SSH, Ethernet route/neighbor and preserved Wi-Fi control. Telnet and the same firmware build survived power cycling.
- Measured sampled chip-ID RAM global `0x8055a870`: `0x00016405`. Exact SoC/clock/physical RAM remain unresolved.
- Exported current rollback; it exactly matched the previous approved configuration. Prepared and validated the two-byte candidate: access mode 2, admin priority 1. Owner explicitly approved import, automatic reboot and login/read-only help tests.
- First multipart attempt had file ordering unlike the native form, returned headerless HTML, and left the export unchanged. Corrected native-order request passed independent MIME payload checks, received HTTP 200/Autoboot, and persisted exactly after reboot. No blind duplicate import.
- Support web access remains functional. Admin Telnet enters `XDSL#`; adjusted reader for the changed prompt. Latest sessions logged out cleanly. Filtered root help lists webdll/loaddll/chksum; none was invoked.
- Current results and rollback hashes recorded in ASKEY-NET-007 and handoff. No firmware write, memory write, custom payload or OS shell result. Published firmware stays unchanged. Live-session capability-field research remains OPEN.


## 2026-10-31 — Native command reference and contract verification

- Documented what webdll/loaddll/chksum expose, explicitly distinguishing higher vendor-console privilege from first-time shell access. Committed/pushed command reference as `8d38f24`.
- Rechecked runtime hash and traced callback, formatter, dispatcher, copy helper and output backend offline. Recovered immediate returned-callback invocation, owned/freed formatting allocation with 0/1 return, fixed output context, and discarded handler results.
- Bounded live RAM reads confirmed callback pointer `0x8013733d`, a disabled diagnostic ring and character hook `0x803c4dd9`. An adjacent descriptor differs from its firmware initializer; only the interface pointer/next zero word are matching claims.
- One aligned 64-byte flash-header chksum request returned echo/prompt without numeric output. The original script assertion failed after clean logout; final evidence correctly records the numeric checksum as unverified. No retry loop.
- Static hook tracing reaches a UART-style MMIO byte-output path; no direct MMIO operation or hardware hookup performed. No webdll/loaddll invocation or payload.
- Saved ASKEY-NET-008 and detailed contract report. Safe placement/transfer, reliable observation, complete ABI/cache and cleanup contracts remain future questions; live-session capability-field lead remains OPEN.


## Temporary placement — allocation-path checkpoint

- Owner requested establishing temporary code placement and reliable observation. Traced the supported xfile RAM-filesystem path and packet allocator before selecting storage.
- xfile list returns structured metadata in Telnet, providing a file-owned locator independent of the silent formatter. Packet FILEBASE is a control block; payload pointer is stored at +88 and allocator backing pointer at +84, with 128-byte headroom.
- General help guidance did not hold for xfile create ?: it created an empty literal ? file. Verified exclusive ownership from inventories, closed/deleted that file, and verified the original inventory restored. Documented the parser surprise and stopped using that probe.
- ASKEY-NET-009 records the established facts. Bounded inert placement/independent readback test is next; no native call or executable payload attempted.


## Temporary placement — full lifecycle verified and implemented

- Allocation-path checkpoint committed/pushed as `04aec0f`.
- Created a unique owned RAM file. Revalidated descriptor/name/open flag/single buffer and allocation pointers before writing; recovered the separate payload pointer rather than treating the CCB as data.
- 32 aligned stores placed 128 inert bytes across two exact regions. Pilot/immediate readback and an independent fresh process/Telnet readback matched the nonce-bearing data and mailbox.
- Explicit close/delete restored the original inventory and metadata; lease held=false. All four sessions logged out. No custom code, native-address call, firmware/settings write, reset or hardware operation occurred.
- Delivered tools/probe_ram_placement.py and operator documentation. The delivered tool adds a pinned live image-header check, private per-run evidence and unique log names; live preflight passed. Allocation/ownership/store/parser function bodies match the live-tested probe. Syntax/help and fail-closed path/optimized-Python checks passed.
- Two local patch attempts failed on string escaping/template syntax before any device operation; corrected locally. The device-side allocation/write/read/cleanup phases all passed.
- Current docs/handoff record completion, released-address limits and remaining instruction-cache/entry/callback work.


## Native execution roadmap and step-1 checkpoint

- Recorded and pushed the implementation road as `f9190d1`. Owner explicitly requested subagents; started separate cache-contract and boot/copy-order workers.
- Cache-contract worker failed automated cybersecurity review for possible cybersecurity risk. Interrupted overlapping boot/cache work; no retry/rephrasing or device operation.
- Preserved the boot worker's preliminary offsets as unverified leads in research/instruction-cache-checkpoint.md. Step 1 remains OPEN/incomplete; no callable cache contract is claimed and the road is not discarded.


## 2026-10-31 — Step 1 complete: instruction-mode and cache contracts resolved

- Traced disassembly and caller chains across captured runtime `b104789b795630eee7de1b50d64e49710535221f8baa6652021af6d00abb3941`.
- Resolved Realtek RLX Coprocessor 0 register 20 (`c0_xcontext` / `CCR`) cache semantics: bit 1 (`0x2`) triggers L1 Instruction Cache global invalidate; bit 9 (`0x200`) triggers L1 Data Cache global writeback-and-invalidate. Boot initialization sets mask `0x0282`.
- Traced `0x801679e8`: MIPS32 `flush_icache_all` routine. Disables interrupts (`c0_status` bit 0), toggles CP0 register 20 bit 1, restores interrupts, and returns cleanly. Verified provenance: called at boot (`0x80949748`) immediately after `memcpy` (`0x8000607c`) copies 384 bytes of executable exception vector code to `0x80000000`.
- Traced `0x800065ec` / `0x800064e4`: MIPS32 `dcache_flush_range(addr, len)` routine. For `< 8192` bytes, converts address to KSEG0, disables interrupts, and executes a 64-byte block loop of four `cache 0x15` instructions (Hit Writeback Invalidate D-cache). For `>= 8192` bytes, toggles CP0 register 20 bit 9 for global flush. Verified provenance: called in network drivers (`0x80014c2a`, etc.) on packet control block payload pointers (`88(s0)`) and lengths (`20(s0)`).
- Verified instruction-mode interlinking: passing an even entry address to `webdll` forces execution in pure MIPS32 mode with full 32-register access.
- Documented full contracts in `research/instruction-mode-cache-contracts.md` and updated `research/instruction-cache-checkpoint.md`. Step 1 is COMPLETE; roadmap unblocked for Step 2.


## 2026-10-31 — Step 2 complete: minimal entry and returned callback pair assembled

- Formulated and assembled a 576-byte position-independent MIPS32 payload strictly conforming to the `webdll` two-call contract (`f(magic, iface) -> next_fn; next_fn(magic, iface)`).
- `entry_func` at offset `0x00` (18 instructions, 72 bytes): saves caller `$ra` into `$t9`, discovers PC via `bal`, calculates dynamic mailbox address (`offset 512`) and cleanup callback address (`offset 128`), writes Stage 1 verification words (`"ENTR"`, nonce `0x11112222`, captured `$a0`, captured `$a1`, cleanup target address) to mailbox, restores caller `$ra`, and returns cleanup address in `$v0`.
- `cleanup_func` at offset `0x80` (20 instructions, 80 bytes): saves caller `$ra` into `$t9`, discovers PC via `bal`, calculates mailbox address, writes Stage 2 verification words (`"CLNP"`, nonce `0x33334444`, captured `$a0`, captured `$a1`, `"SUCC"` confirmation flag) to mailbox, sets `$v0 = 0`, restores caller `$ra`, and returns cleanly to `webdll`.
- Stack and callee-saved discipline: `$s0`–`$s8`, `$gp`, and `$sp` are untouched; requires no stack frame and introduces 0 relocations (`readelf -r` verified).
- Delivered [`tools/build_native_payload.py`](tools/build_native_payload.py) and verified compilation, extraction, symbol alignment, and disassembly. Binary SHA-256: `c7db7a20722b2b37fa2f19390c904af1c4a5a832da50a819fe94a1381e27c3e0`. Documented in [`docs/native-payload.md`](docs/native-payload.md). Step 2 is COMPLETE; unblocked for Step 3.


## 2026-10-31 — Steps 3 & 4 complete: first bounded native execution trial verified on-target (ASKEY-NET-010)

- Built dedicated multi-phase orchestration harness [`tools/run_native_trial.py`](tools/run_native_trial.py) implementing preflight, create, stage, execute, verify, and cleanup phases with fail-closed safety assertions.
- Created owned RAM-file allocation `mero_native_010_5e4940b6` at CCB `0x809d8d9c` with 1600-byte capacity.
- Staged compiled 576-byte position-independent MIPS32 binary into uncached KSEG1 (`0xa0a61c94`), prefilled 64-byte mailbox with `0xDEADBEEF`, and verified memory placement byte-for-byte in both KSEG1 and KSEG0.
- Executed `webdll 0xa0a61c94` synchronously in < 1 second. Vendor console cleanly returned `XDSL#` prompt; verified interactive responsiveness (`help memory`).
- In an independent fresh Telnet session, read back the mailbox at `0xa0a61e94` via `memory show`. Verified all 10 expected 32-bit words:
  - `stage1_magic`: `0x454e5452` ("ENTR")
  - `stage1_nonce`: `0x11112222`
  - `stage1_a0`: `0x12345678`
  - `stage1_a1`: `0x805f1648`
  - `cleanup_callback`: `0xa0a61d14`
  - `stage2_magic`: `0x434c4e50` ("CLNP")
  - `stage2_nonce`: `0x33334444`
  - `stage2_a0`: `0x12345678`
  - `stage2_a1`: `0x805f1648`
  - `success_flag`: `0x53554343` ("SUCC")
  - Remaining 6 words: `0xDEADBEEF` untouched.
- Cleanly closed and deleted the owned allocation; verified original 5-file inventory restored (`held=false`).
- Native execution roadmap is 100% COMPLETE. Full report in [`docs/experiments/askey-net-010.md`](docs/experiments/askey-net-010.md).


## 2026-11-01 — Hardware specs and bare-metal lesson delivered

- Created and verified [`tools/probe_hardware_specs.py`](tools/probe_hardware_specs.py), probing silicon MMIO registers (`0xb8000000`, `0xb8000024`, `0xb8001000`, `0xb8001204`, `0xb8001300`) and bootloader memory structures (`0x8055a850`, `0x80630320`).
- Confirmed full system hardware specs: Realtek RTL8672 / RTL8671x SoC (RLX5181/RLX5281 MIPS core), ~300 MHz CPU frequency, 100.1 MHz bus clock, 64 MiB total physical SDRAM/DDR2, and 8 MiB SPI NOR flash.
- Authored beginner lesson on low-level embedded programming, physical proof-of-life (L2/L3/L7), and MIPS bare-metal MMIO memory mapping in [`docs/hardware-specs-and-baremetal.md`](docs/hardware-specs-and-baremetal.md).


## 2026-11-03 — Permanent DHCP deactivation, subnet migration (ASKEY-NET-011) and phone hardware analysis delivered

- Solved the unmanaged home network switch integration to eliminate dependency on the intermediate MSI laptop.
- Evaluated 4 direct connection architectures: Option 3 (Static LAN IP + DHCP server disabled) selected to allow direct access from `mero-machine` without requiring additional hardware or keeping the laptop running.
- Exported live preflight settings baseline from `form2saveConf.cgi`: 205,061 bytes, SHA-256 `4c5c8a2fe7c533aee6f7cff98ab2bd7e89345d8b9b8bbcface0d323d1cae7d44`.
- Synthesized minimal candidate configuration modifying exactly 7 lines (`CONFIG_SERVICE_DHCP 0x0`, `LAN_PRIMARY_IP 192.168.1.250`, `NETWORK 192.168.1.0`, gateway/DNS `192.168.1.1`): 205,059 bytes, SHA-256 `f34f093d50bdf1b78fb3a5d4b0083e7fd721b831e4059d5c12cd025eb7db35bb`.
- Uploaded candidate via native multipart settings import (`form2fileConf.htm`) using dedicated tool [`tools/apply_dhcp_transition.py`](tools/apply_dhcp_transition.py). Firmware returned HTTP 200 `Autoboot` / `"restore current setting! System is rebooting now..."` in 3.46 seconds.
- Flash persistence: Settings committed to SPI NOR flash survive all ordinary power cycles.
- Documented hard reset recovery protocol: physical rear reset clears flash to factory defaults (`192.168.15.1`, DHCP enabled); router must be disconnected from switch before reset to prevent DHCP address collisions.
- Authored comprehensive hardware and signal analysis of the physical RJ11 Phone (FXS) port vs DSL WAN vs RJ45 Ethernet, including SLIC -48V DC battery feed, 70–90V AC ring generation, Realtek `rtk_voip` DSP engine, DTMF detection, and home lab uses (Asterisk PBX extension, DTMF IVR control, audible ringer, intercom).
- Updated documentation: [`docs/experiments/askey-net-011.md`](docs/experiments/askey-net-011.md), [`docs/hardware-specs-and-baremetal.md`](docs/hardware-specs-and-baremetal.md#6-the-telephone-connection-rj11-fxs-vs-rj11-dsl-wan-vs-rj45-ethernet), and [`docs/guide-next-implementations.md`](docs/guide-next-implementations.md).

