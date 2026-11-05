# Telephone expansion and next experiments

Recorded 2026-11-05. Current proof covers the MOTO700 on the Askey PHONE port, SIP registration, calls/audio, in-call DTMF, a spoken menu and fixed desktop/network actions. No rotary phone or parallel-phone experiment has been performed.

## Which phones can work?

An ordinary **analog telephone intended for a subscriber telephone line** is the relevant type for the Askey FXS port. A matching connector alone does not establish compatibility. Proprietary digital office/PBX handsets and Ethernet SIP phones use different interfaces.

| Telephone | What to establish |
|---|---|
| Analog push-button phone using DTMF | Ringing, speech, dialing, hook behavior and electrical/ringing load |
| Powered cordless analog base | Its own supply/batteries plus the same analog-line tests; MOTO700 already works here |
| Mechanical rotary phone | Speech/off-hook, mechanical bell ringing, and pulse dialing as separate tests |
| Proprietary digital PBX handset | Not directly compatible merely because it has an RJ11-looking plug |
| SIP phone or softphone | Can be a separate PBX endpoint over Ethernet/Wi-Fi; does not connect to FXS |

A rotary dial sends loop interruptions, not DTMF tones. The existing successful keypad test proves DTMF behavior only. Askey pulse decoding, its firmware setting semantics and a particular old phone's bell/load compatibility remain unverified. Do not change guessed pulse settings.

Even if initial rotary dialing works, in-call menu digits need separate verification: pulse dialing does not automatically become the RTP DTMF events our menu receives. An appropriate pulse-to-DTMF adapter may be a later solution, but it must support the intended phone and in-call behavior. Do not assume every converter does. [A converter manufacturer's explanation](https://www.dialgizmo.com/) describes pulse-to-tone conversion for VoIP equipment; it is a source for the mechanism, not a tested product recommendation for this Askey. Incoming calls or a deliberately configured off-hook hotline could provide other ways to use an old phone without its rotary dial controlling the current menu; those are proposals, not active features.

## Two phones on the existing port

A genuine **one-line parallel telephone splitter** could connect the old analog phone and the MOTO700's analog base to the same PHONE/FXS pair, subject to the Askey's load capacity and each phone's compatibility. It must not be a two-line L1/L2 separator or a DSL filter mistaken for a parallel splitter.

```text
Askey PHONE / one FXS line
              ├─ MOTO700 analog base
              └─ old analog telephone
```

Both sets would share extension **10**, the same call and line state. Both may ring; either can answer. Picking up the other set may let it join/listen to the existing call and change audio level/quality. They would not have separate numbers, private independent calls or an intercom between those two branches.

The ringer loads add together. An old mechanical bell may be more demanding than a modern powered base. The Askey's supported total **ringer equivalence/load (REN)** has not been established locally, so we cannot promise that both will ring reliably. The rating of some other adapter is not this router's rating. Off-hook current/speech behavior also needs verification with both connected.

To obtain two independent analog extensions, use two independent FXS ports with separate SIP accounts, or keep this Askey line and add a separate SIP endpoint. A passive splitter cannot create the second telephone channel. For example, a manufacturer's two-FXS adapter explicitly provides two SIP/FXS profiles; this illustrates the architecture, not an equipment purchase recommendation or Askey compatibility claim. [Grandstream HT802 manufacturer specifications](https://www.grandstream.com/products/gateways-and-atas/analog-telephone-adaptors/product/ht802).

## Bounded compatibility experiment, when equipment is available

1. Identify the exact old phone, connector/wiring requirements, line/bell rating if marked and whether it is a standard analog set.
2. Test it **alone** on the known PHONE output: off-hook/speech, incoming ring and dialing separately. Confirm the actual wiring rather than guessing pins.
3. If those tests and the available FXS load specification justify it, explicitly plan a parallel-splitter trial with both sets.
4. Observe ringing with both attached, answer from each, then check the effect of lifting both during one call.
5. Return to the proven MOTO700-only arrangement after any failed test.

Keep this isolated from live household/public telephone wiring. Never connect two FXS outputs together, and do not route the PHONE output into DSL. This guide does not authorize making a new hardware connection; it records the options for a later explicit experiment.

The [MOTO700 handoff](telephony-moto700-pilot-handoff.md#gate-3--subsequent-rotary-replacement) already distinguishes mechanical pulse dialing from speech/ringing compatibility.

## Useful and playful next ideas

| Idea | First small implementation | Additional requirement |
|---|---|---|
| **The house operator** | Ask for workstation/PBX availability and hear a short status report | Fixed read-only status functions and fresh result-to-speech generation |
| **Cinema concierge** | Announce the selected media, then offer Bravia cinema/restore | Read the actual player state; do not guess which player/session to control |
| **A private answering machine** | Leave a short voice memo, then retrieve it from a menu | Explicit recording prompt, private storage, retention and playback access rules |
| **A bell for completed work** | Ring once when a selected render/build/backup finishes | One chosen job's completion hook, quiet hours and duplicate/rate limits |
| **Focus session** | Start a named timer and call with an end-of-session announcement | Scheduler persistence and a cancellation action |
| **A local extension for another room** | Call between the MOTO700 and a separate SIP endpoint | A second independent endpoint; a passive splitter is not enough |
| **A mystery line / audio room** | Play a local atmospheric story or soundscape, with keypad branches | Approved audio assets; preserve intelligibility over the narrowband handset |
| **Suzy and Sera direct lines** | Route to their real existing runtimes and voices | Realtime audio/STT/TTS adapters, interruption handling and their existing tool permissions |
| **Old-phone hotline** | On pickup, connect a vintage set to the operator/menu | Verified old-phone electrical compatibility and an explicitly reviewed hotline configuration |

Good next steps are the read-only house operator, voice memos, or one chosen job-completion bell. Each introduces one useful capability without needing the full realtime agent bridge. No new job, recording flow, scheduled alert or agent integration is active merely because it appears here.
