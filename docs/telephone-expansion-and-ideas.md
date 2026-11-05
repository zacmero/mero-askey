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

## Owner's newly identified accessories — 2026-11-05 (photo inventory)

These are **owner-supplied photos and untested observations**, not hardware teardown results. No equipment was opened, electrically measured, connected, or modified during this documentation.

| Object observed | Identification and source | Proper role / current limit |
| --- | --- | --- |
| White Opticom **MF42T** box with one attached modular cord; female sockets marked **Telefone** and **ADSL**; cord marked **Linha** | Owner label: **Opticom Communications MF42T**, ANATEL **0030-07-1714** (printed 0030-07-1714), lot **08/08**. The exact older Opticom registration appears in [2007 certification listings](https://www.radardatelecom.com/certificacoes/fabricante/opticom-communications-do-brasil-ltda). | **ADSL/POTS microfilter**, with filtered telephone leg and unfiltered modem leg. **NOT a two-telephone parallel splitter**. Do not treat `ADSL` as a second telephone outlet. |
| Beige, square **PM-1** surface-mount unit; one modular phone jack in front | Owner's photograph shows **PM-1** and a single visible modular jack; manufacturer and internal terminals **not confirmed**. | Appears to be a passive **single-outlet telephone wall box**, potentially useful to terminate a future bedside cable **after its rear terminals/wiring are identified**. Not an independent second line or a two-way splitter. |

Relevant source references: [Cisco POTS splitters and microfilters](https://www.cisco.com/c/en/us/support/docs/long-reach-ethernet-lre-digital-subscriber-line-xdsl/asymmetric-digital-subscriber-line-adsl/12933-splitters.html) and [Netgear installation explanation](https://kb.netgear.com/22205/How-to-correctly-install-ADSL-micro-filters), which clearly distinguish a **filtered phone socket** from an **unfiltered DSL/modem socket**.

### Two actual phones on one Askey FXS line (no live trial yet)

Required object is **one-line RJ11/RJ12-compatible telephone *parallel* Y adapter / `duplicador de linha telefônica 1 macho → 2 fêmeas`**. Verify that its central tip/ring pair is physically **parallel to both female outputs**, not a two-line L1/L2 separator, DSL microfilter, or powered network equipment. A short telephone extension cable can lead to the PM-1 outlet by the bedside **if suitable wiring is confirmed**.

```text
Askey PHONE / FXS  (extension 10)
        |
   verified parallel Y
      /          \
  MOTO700      future vintage corded phone
   desktop            bedside
```

Both instruments are **one shared analog circuit**: same extension 10; both may ring; answering one seizes that line; picking up the other can join/hear the same conversation; **they cannot dial each other**. Additional old-fashioned bell loads may exceed Askey's as-yet-unknown REN capacity. Do not infer it from other ATAs. Test vintage phone **alone** first for off-hook, ringing/bell and pulse dialing separately; only then, after checking FXS load and parallel wiring, test together. Disconnect if ringing fails or speech quality deteriorates. Keep wiring isolated from active telco line and other FXS ports.

### Caller-ID lab — first priority, no handset modification

MOTO700 published specs describe **caller-ID reception using DTMF/FSK** and a **20-name/number phonebook** ([MOTO700 specs](https://www.kabum.com.br/produto/100695/telefone-sem-fio-motorola-identificador-de-chamadas-dect-6-0-digital-bivolt-preto-moto700)). Asterisk supports channel caller identity through `CALLERID(name)` and `CALLERID(num)` ([Asterisk documentation](https://docs.asterisk.org/Latest_API/API_Documentation/Dialplan_Functions/CALLERID/)).

A proposed **test-only** PBX outgoing call to `PJSIP/10` sets a **distinct private caller number** (for example `1100` or `1200`) and name (`SUZY` / `SERA`) **before** dial, using a dedicated private dialplan route. First determine what *actual* number, if any, the Askey passes as FSK/DTMF caller-ID to the handset. A SIP display name is **not a guarantee** of analog display-name delivery. If MOTO700 matches incoming number to a saved phonebook contact, manually create `1100 → SUZY` and `1200 → SERA` and test both. Match the exact digits the handset receives; if one route does not work, audit the FXS CLIP format/enable controls read-only before attempting persistent changes. No calls or configuration changes were made for this proposal.

### Scope and owner's explicit hardware boundary

Owner does **not** want to open or physically modify the Motorola handset/base now. Continue with PBX, caller-ID and other **external-only** experiments. Keep the firmware-archaeology idea for later experience on other devices. Do not request a PCB photo, connect CH341A/JTAG/UART probes, or schedule a teardown as the next step.

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
