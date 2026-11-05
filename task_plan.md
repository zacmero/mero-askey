# Telephony lab implementation — 2026-11-04

Goal: document the future DSL copper lab and dial-code automation, then establish the current Askey voice state and prepare the first private PBX call experiment.

## Phases

1. Record scope, existing equipment and current network — complete.
2. Add DSL guide and telephony dial-code design — complete.
3. Inspect live voice settings/status through authenticated read-only operations — complete.
4. Prepare the smallest justified PBX experiment, with a concrete configuration and rollback — complete. Owner explicitly approved and the deployment/voice change were applied; registration and dial tone are confirmed.
5. Verify documentation/tools and run handset call tests — complete. Owner confirmed incoming ringing, hello-world audio and six-second microphone recording/playback. The call path works in both directions. Outgoing digit/DTMF menus are the next separate experiment.

Persistent Askey voice changes need an explicit operation and rollback under AGENTS.md. Prepare and review the actual fields before deciding whether a change is covered by the owner's instruction. No factory reset, DSL hookup or firmware write is part of this task.

## Errors

- apt-cache was absent; host OS inspection shows EndeavourOS. Use the isolated Ubuntu PBX build instead of host package installation.
- One documentation patch expected 'for this handoff'; exact text was 'by this handoff'. Read the exact line and corrected the patch.
- Isolated PBX startup exposed Ubuntu package paths: modules live under /usr/lib/x86_64-linux-gnu/asterisk/modules and data/documentation under /usr/share/asterisk. Correct the generated paths; retain startup diagnostics privately.
- Default runtime opens internal ephemeral sockets. Replaced host networking with a private Docker network publishing only approved SIP/RTP ports.
- Native form submission returns 301; new checked controls must preserve DOM order before the final dispatch marker. Fresh readback and an audited partial-state continuation were used before completing the approved change.
- chan_pjsip requires res_pjsip_pubsub. Added the dependency and strengthened the isolated validation to check the actual call driver.

---

# Earlier recorded work (preserved)

# Native execution road — 2026-10-31

Recorded in [native execution roadmap](docs/native-execution-roadmap.md). **Roadmap Steps 1–4 are COMPLETE**: resident cache contracts resolved ([research/instruction-mode-cache-contracts.md](research/instruction-mode-cache-contracts.md)), the 576-byte PIC MIPS32 entry/cleanup payload built and verified ([docs/native-payload.md](docs/native-payload.md), [`tools/build_native_payload.py`](tools/build_native_payload.py)), and genuine native execution verified on-target with 10 matching mailbox markers, stable CLI console, and clean allocation release ([ASKEY-NET-010](docs/experiments/askey-net-010.md), [`tools/run_native_trial.py`](tools/run_native_trial.py)). Next goal: explore OS shell enablement and interactive execution. No test allocation remains held (`held=false`).

---

# Temporary placement and observation — 2026-10-31

Completed: native RAM-file allocation and ownership checks, 128-byte inert placement through 32 aligned stores, exact readback through a fresh connection, and close/delete restoring the original inventory. The guarded implementation and operator guide are tools/probe_ram_placement.py and docs/ram-placement.md; ASKEY-NET-009 records actual hashes. No allocation remains held. Custom code execution and instruction-cache behavior were not tested. Do not reuse historical addresses.

---

# Native contract pass — 2026-10-31

Completed the exposed-command reference, bounded callback/copy/formatter/dispatcher analysis, and ordinary-RAM output-interface/sink readbacks. Recorded the checksum result as unverified because no numeric output appeared. See [native contracts](research/firmware-native-contracts.md) and [ASKEY-NET-008](docs/experiments/askey-net-008.md). No custom call/copy/payload test performed.

Remaining execution prerequisites are safe temporary placement/transfer, a reliable observation channel, and full ABI/cache/cleanup contracts. Preserve the OPEN session-object avenue independently of the approved privilege-setting result.

---

# 2026-10-31 resumption — bounded CLI experiment complete

Reverified the physical network path, retained a fresh rollback, and applied the exact owner-approved access-mode/admin-priority candidate through native import. Verified reboot recovery, exact persisted export, support management, admin `XDSL#` and filtered native-command help. No native handler or memory write was exercised. See [ASKEY-NET-007](docs/experiments/askey-net-007.md).

Next unresolved work: establish native allocation, callback-return, ABI, lifetime and cache contracts before an executable experiment. Preserve the OPEN live-session capability-field road. Further settings imports, resets or firmware writes are not implied by the help result.

---

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
