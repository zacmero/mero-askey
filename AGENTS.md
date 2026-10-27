# Agent instructions — mero-askey

Read `README.md`, `HANDOFF.md` and `research/sources.md` before work. Target is the owner's Askey RTV9015VW. Goal is a genuine OS shell and native execution, not a custom web UI.

## Practical workflow

- Current owner workstation is a Linux Mint laptop. Do not assume Arch package commands, RTK installation, interface names, old SSH routes or the MitraStar's IP/MAC.
- Identify the cable-facing interface, route and target before traffic. Keep only one default-address Vivo router on the lab segment; preserve the household/control connection. No bridge, DHCP/DNS service or household ARP interception by default.
- Prefer one bounded, informative step and interpretation over repeated scans/probe loops. Do not repeat completed work without a stated new question.
- Present local measurements, owner reports, external reports and hypotheses separately. Open port, web administrator, vendor CLI, bootloader and Linux shell are distinct access levels.
- No Askey tests were performed during repository initialization. Planned commands in the handoff are not results.

## Equipment and authorization

- Known CH341A has approximately 5 V at a reported SPI data output; USB programmer/serial enumeration does not certify electrical safety. Do not connect it directly to this router.
- ESP32 has not arrived; female–female jumpers and soldering equipment are absent. Do not propose work that silently assumes those tools exist.
- Preserve ownership/permissions already established; do not repeatedly ask for them. Hardware connections, persistent settings changes, service activation, configuration restore, factory reset and firmware/bootloader writes require an explicit instruction for the actual operation and an understood recovery/rollback plan.
- Do not guess credentials, wire pinouts, safe voltages, firmware compatibility or hidden handler semantics. Use the owner's intended device credentials privately.
- The documentation request does not start device tests or purchase equipment.

## Repository hygiene

- Keep raw captures, private credentials, settings exports, firmware dumps and generated binaries in ignored `.local/`.
- Commit reviewed experiment notes and real artifact hashes only. Redact password fields, session cookies, WAN credentials, keys and unnecessary device identifiers.
- Do not execute downloaded firmware, import modified configs or upload guessed images as part of source research.
- Preserve other agents' changes and record actual outcomes. A matching image and recoverable backup are prerequisites to a future firmware write, not a configuration export alone.
