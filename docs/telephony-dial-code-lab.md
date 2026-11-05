# Private telephone interface and dial-code automation

Recorded 2026-11-04. Owner-requested direction: use the existing MOTO700 and Askey for local calls, voice-agent links, and keypad commands that trigger chosen actions elsewhere in the home lab.

## Current baseline

The owner reports that the MOTO700 is working and connected to the green PHONE port. Pressing call produces **silence**. Dial tone, SIP registration, incoming ringing, DTMF reception and two-way audio remain unverified. See the [pilot handoff](telephony-moto700-pilot-handoff.md).

**Implementation update:** The owner approved the private PBX and voice settings; extension `10` is registered. The owner confirmed dial tone, incoming ringing, hello-world playback and hearing a six-second microphone recording played back. Telephone-originated echo and DTMF forwarding remain unverified. The original silence above describes the starting baseline. See [ASKEY-VOICE-001](experiments/askey-voice-001.md) and the [PBX deployment](../lab/telephony/README.md).

## Intended interface

The handset is the initial interface: dial an extension or feature code, hear a prompt, enter a choice, receive spoken confirmation, and hang up. A private PBX on the home lab host handles the menu, call routing and named actions. The Askey supplies the analog phone interface and, if its resident stack permits it, SIP/RTP transport over Ethernet.

```text
MOTO700 — Askey PHONE/FXS — Ethernet — private PBX
                                         ├─ echo / status / DTMF tests
                                         ├─ Suzy and Sera voice bridges
                                         └─ named home-lab actions over authenticated local APIs
```

## Proposed numbering — not active assignments

| Code | Intended behavior | First verification |
|---|---|---|
| `10` | MOTO700 endpoint | PBX rings the handset; answer and hang up |
| `11` | Suzy voice bridge | Confirm the intended runtime receives audio |
| `12` | Sera voice bridge | Confirm the intended runtime receives audio |
| `19` | PBX echo test | Speech returns with intelligible audio |
| `*20` | Speak lab/service status | Initially return fixed local test text |
| `*21` | Speak the result of a chosen network check | Run a bounded, read-only check against an agreed lab target |
| `*22` | Run one chosen home-lab job | Initially use a harmless dry-run action with an audible result |
| `*29` | DTMF diagnostic menu | Record/report received digits without triggering actions |

Use short numeric extensions first. Star codes depend on the actual Askey dial plan forwarding the digits to the PBX. Their availability is a test question, not established behavior. No live code is assigned to a service restart, deletion, unlock, purchase or external message.

## Action contract

Map each code to a fixed action name and explicitly selected target. Digits select an allowed action; they must never become an arbitrary shell command, hostname, URL or executable argument. Use authenticated local APIs or a narrowly scoped worker for the chosen operations. Keep execution bounded and announce completion or failure, including timeouts.

Start with read-only status and dry-run jobs. For a later state-changing action, add an audible target description and explicit confirmation before execution, and define rollback where it applies. Limit command menus to authenticated lab endpoints. Keep secrets, voice recordings and raw call traces under ignored `.local/`; retain only necessary action results in reviewed notes.

## Experiment order

1. Inspect the current Askey voice configuration/status and whether it can use a LAN SIP server.
2. Prepare the PBX endpoint and echo route, with a fixed local bind address and removal procedure.
3. Apply only the reviewed, explicitly authorized voice changes after saving the current configuration.
4. Prove registration, outgoing echo, incoming ringing, two-way audio and hang-up cleanup.
5. Prove digit forwarding with the DTMF diagnostic route.
6. Add spoken status and a dry-run action; verify that invalid codes and repeated digits do not trigger another action.
7. Connect the existing voice-agent runtimes, then add individually chosen network actions.

Success for the first pilot is a reproducible private call. Native payloads remain a fallback if the resident voice stack cannot serve the lab; no new payload is required merely to create a PBX menu.

The separate [DSL copper lab](dsl-copper-lab.md) is a future data-link experiment and is not required for this sequence.
