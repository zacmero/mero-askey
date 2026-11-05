# Telephony pilot handoff — Motorola MOTO700 + Askey RTV9015VW

**Recorded:** 2026-11-04 (America/Sao_Paulo)  
**Status, updated 2026-11-04:** The private PBX is running and the Askey phone line is registered as extension **10**. The owner confirmed **dial tone, incoming ringing, hello-world playback, and hearing their own six-second microphone recording played back**. This proves a private call with audio in both directions. Telephone-originated echo, DTMF menus, voice-agent links and network-command actions remain separate next tests. See [ASKEY-VOICE-001](experiments/askey-voice-001.md).

**Keypad/menu continuation:** [ASKEY-VOICE-002](experiments/askey-voice-002.md) now confirms in-call digit reception, a spoken menu, option `2` running the fixed bounded Askey connection check and reporting success, and `0` hanging up. Outgoing short-code dialing and voice-agent bridges remain unverified.
**Purpose:** Use the owner's available Motorola MOTO700 cordless telephone as the first analog handset for a self-hosted Askey/VoIP/voice-agent experiment, before replacing it with a vintage rotary telephone.

## 1. Exact device and evidence

- **Owner photo of the underside of the base:** Motorola **MOTO700**; ANATEL approval **05037-16-06652**; black case; telephone-line modular connector visible. This is a **cordless DECT telephone base**, **not** a line-powered corded or rotary telephone.
- The owner's individual serial number is intentionally **not copied** into the repository.
- **Manufacturer-model manual:** [MOTO700 / MOTO700-W / MOTO700-MRD2 / MOTO700-MRD3 Portuguese user manual](https://images.colombo.com.br/produtos/911591/911591_1572110916856.pdf) (22 pages, see especially manual pp. 3–5 and 9–12).
- [Black MOTO700 product specs](https://www.kabum.com.br/produto/100695/telefone-sem-fio-motorola-identificador-de-chamadas-dect-6-0-digital-bivolt-preto-moto700), [Hayamax product description](https://origin.hayamax.com.br/telefone-sfio-digital-moto700-preto-motorola), and [MOTO700 family specification, matching ANATEL approval](https://www.magazineluiza.com.br/telefone-motorola-moto700-sem-fio-branco/p/ef80g2e18g/tf/tfra/) corroborate the family identification.

### Features relevant to this experiment

| Fact | Source / confidence | Consequence |
| --- | --- | --- |
| Cordless **DECT 6.0** handset communicates by radio with its base | Exact-model manual and retail specifications | Handset itself does **not** plug into the Askey; the **base** supplies the analog telephone-line interface |
| Base has **separate phone-line and external power connections** | Manual, installation section; owner photo | The analog RJ11 port is **not** a power source for the DECT base |
| **Base must be electrically powered**, including when not actively charging | Manual p. 9, explicit note | Cannot make the phone function by connecting RJ11 alone |
| Handset uses **two rechargeable batteries**, commonly **NiMH AAA** in MOTO700 family | Manual pp. 4, 9; family specifications | Check installed batteries and polarity; **never charge disposable alkaline cells** |
| Manual instructs initial/after-install **15-hour charge** | Manual p. 9 | If equipment has been unused, charge according to manufacturer instructions before diagnosing telephony |
| Tone (DTMF) and pulse dialing modes | Model/family specification | Choose **tone/DTMF** for initial PBX tests; pulse mode here is an **output mode of the electronic base**, not proof the Askey recognizes mechanical rotary dialing |
| Redial, phonebook (20 entries), adjustable ringing and receiver volume, flash, caller ID | Manual and model specifications | Can save proposed AI extensions and debug outgoing/incoming call handling |
| Up to five registered handsets depending on model/bundle | Manual and retail specifications | Not relevant to first single-handset test; do not assume extra handsets are present |

**Power caution:** Some *other MOTO700 variants* list a 6 V DC adapter, but the owner's base adapter requirements **must be read from its own supply/base labeling** before connection. Do not guess voltage, plug polarity, current capacity or connector size. Do not borrow the Askey's **12 V / 1 A** adapter. Use the correct manufacturer-specified compatible power supply; the manual says to use the supplied adapter.

## 2. Actual existing Askey baseline (not newly tested here)

- Router: **Askey RTV9015VW**, firmware `BR_SO_RTK_V6.1.8t`, OSK/Realtek RTOS. Native MIPS execution is genuinely demonstrated in [ASKEY-NET-010](experiments/askey-net-010.md); the [full flash capture](experiments/askey-net-006.md) is verified and preserved. This is **not** an ordinary Linux router with an established shell/package manager.
- [ASKEY-NET-011](experiments/askey-net-011.md) documents a successful configuration migration to **static LAN IP `192.168.1.250/24`**, **Askey DHCP server disabled**, main household gateway `192.168.1.1`; `mero-machine` is documented as `192.168.1.97`. Confirm current reachability before any traffic; don't assume yesterday's IP is live without checking.
- Device has a physical **PHONE/TEL FXS** interface candidate (not to be confused with DSL). Related-device teardown identifies a **Le9641PQC** telephone-interface chip; it has not been identified/measured directly on this owner unit. See [sources](../research/sources.md) and [hardware/phone analysis](hardware-specs-and-baremetal.md).
- Existing [telephony and voice guide](telephony-and-voice-automation.md) describes a **proposed** SIP/RTP/Asterisk topology. It is **not a completed voice experiment**. Its exact idle/ringing voltage, demonstrated SIP registration, 'zero latency', ringing and live DTMF statements are **not verified by on-device phone tests**. Do not promote assumptions to observations.

## 3. Desired connection (target design, not yet a measured result)

```text
MOTO700 handset  --DECT radio-->  MOTO700 powered base
                                           |
                                  analog phone-line cable
                                           |
                                 Askey PHONE/TEL FXS
                                           |
                        (candidate native VoIP/SIP/RTP over LAN)
                                           |
                              mero-machine / Asterisk PBX
                                    |              |
                            PBX echo test    agent voice bridge
                                                    |
                                       Suzy / Sera existing runtimes
```

The Askey is a **telephone line source (FXS)**, and the MOTO700 base is the **analog telephone endpoint**. Neither the gray **DSL** connector nor a LAN RJ45 port should be used for the phone cable.

**Critical unresolved gate:** Determine whether the Askey's **actual vendor VoIP stack can register/configure a SIP trunk/endpoint to an arbitrary LAN Asterisk server** without an ISP connection or further RTOS work. Firmware strings/configuration fields alone do not demonstrate it. If the resident VoIP stack is locked to the provider, investigate read-only first. Building and running new native code on the Askey is possible in principle, but should be the **later fallback**, not the automatic first step.

## 4. Minimal, sequenced tests — record each outcome separately

All below are **proposed tests, not results**. This handoff does not authorize changing router settings, deploying services, attaching hardware remotely, firmware writes or flash modifications.

### Gate 0 — inventory and safe setup (no Askey needed)

1. Confirm presence of **MOTO700 base, handset, matching/label-verified power adapter, two rechargeable compatible cells, and a standard phone-line cable**. Record missing items instead of assuming they exist.
2. With power off, inspect the supply's **output voltage, DC/AC, polarity, current, connector** and the base's input marking before plugging it in. Never substitute a generic adapter or the 12 V Askey supply.
3. Inspect handset batteries for leakage/swelling/damage; install only compatible rechargeable chemistry and polarity. Follow manufacturer charging procedure.
4. Power the base; ensure handset starts and its DECT signal icon indicates registration. Press the **PAGE/locate button on the base**; the manual describes an audible handset search/paging event. This tests **base + handset + DECT** independent of Askey/SIP.
5. Record **PASS/FAIL/UNKNOWN** separately for base power, handset startup, handset charging, base registration, and PAGE signal.

### Gate 1 — analog physical-line check (phone and Askey)

1. Confirm Askey's designated **PHONE/TEL FXS** socket and its LAN isolation/normal household topology. Never connect active PSTN/DSL input into FXS. Keep RJ11 line plugs away from exposed conductors while ring voltage may be present.
2. Connect phone-line socket on MOTO700 base to **Askey FXS** with an ordinary telephone cable. Each device retains its own correct supply.
3. Choose **TOM / DTMF** dialing on the handset/base (consult menu/manual or observe actual menu; no unverified menu path is asserted here).
4. On MOTO700: **green call key** begins an outgoing call; enter digits; **red/end** terminates. Alternatively pre-dial number then green call key (manual, p. 10). Observe dial tone/line error/silence separately.
5. Ensure ringing is not muted: manual p. 11 says **hold `#` while idle** to toggle handset ringer. During a call, **up/down arrows** adjust receiver volume; raising/lowering ring volume during ringing also uses arrows.
6. Record whether Askey senses off-hook, whether a dial tone is present, whether digits are recognized, whether incoming ringing is delivered, and whether speech works in *each* direction. A dial tone is not proof that SIP works.

### Gate 2 — VoIP/PBX only after confirming feasibility

1. Audit owner firmware/configuration **read-only** for the actual `VOIP.PORT[0]`/SIP server fields, LAN egress binding, service state, dial plan, and any vendor/ISP restrictions; do not assume the guide's config keys are sufficient.
2. Set up Asterisk on `mero-machine` **only after** a reviewed architecture/config and approval for service activation. Keep SIP/RTP limited to local network or private VPN, and **never port-forward Telnet/admin or unauthenticated SIP to the public internet**.
3. Proposed internal extensions (not assigned yet): **10 MOTO700 bedside**, **11 Suzy**, **12 Sera**, **19 PBX echo test**. Use a bounded, explicit dial plan; do not pretend these currently exist.
4. Test **outbound MOTO700 → 19 echo**, **PBX → 10 inbound ring**, then **two-way audio**, hang-up cleanup and re-dial. Record actual signaling response and packet captures **without credentials**, then verify normal network behavior.
5. Only after successful local calls, build an audio bridge (for example, Asterisk ARI External Media / AudioSocket or media WebSocket) to the actual Suzy and Sera runtimes. A generic TTS model with similar voice is not the existing agent's memory/tool continuity.
6. Test mobile softphone over a private VPN (Tailscale or WireGuard); ordinary public telephone numbers would additionally require a PSTN/SIP trunk provider. iPhone incoming-call behavior needs push/foreground considerations.

### Gate 3 — subsequent rotary replacement

A mechanical rotary dial sends **loop-disconnect pulses**. The MOTO700's `PULSO` option does **not** verify that the Askey can decode a vintage rotary phone. Test a real mechanical set for (a) off-hook and speech, (b) ringing/bell compatibility, and (c) pulse dialing as **three distinct behaviors**. Manufacturer Le9641 literature mentions pulse-dial detection, but chip existence and firmware enablement remain unverified on this unit.

## 5. Practical diagnostic notes and stop conditions

- **No handset display / no PAGE:** solve power, charger, battery and DECT registration first; Askey and PBX are not involved.
- **Handset registered / no dial tone:** may be unconfigured Askey analog/voice service; does not by itself diagnose handset failure.
- **Can hear dial tone / digits ignored:** verify the MOTO700 is using DTMF; distinguish local tone generation from a complete SIP dial plan.
- **Outgoing works / incoming doesn't ring:** check ringer mute (`#` hold), ring-volume setting, FXS ring configuration and PBX signaling separately.
- **Can call / no one-way or two-way audio:** isolate RTP routing, codec (e.g. G.711), network/firewall, and line gain; no need to involve AI during an echo test.
- **No Internet/household disruption:** do not enable a second DHCP server, bridge the ISP DSL side into the home switch, reset Askey while switch-connected, or accidentally expose privileged Telnet.
- **Electrical stop:** if adapter labeling/compatibility uncertain, damaged battery, suspected short, unexpected heat or unusual odor, stop. Do not probe or manually inject phone ringing voltages.

## 6. Source index

1. Owner's 2026-11-04 **MOTO700 label photo** (ANATEL 05037-16-06652), conversation attachment; **do not commit the image or serial**.
2. [Motorola MOTO700 family Portuguese user manual](https://images.colombo.com.br/produtos/911591/911591_1572110916856.pdf): setup, external adapter, battery charging, dialing, answer/end, volume/mute, base page and phonebook.
3. [KaBuM MOTO700 black specs](https://www.kabum.com.br/produto/100695/telefone-sem-fio-motorola-identificador-de-chamadas-dect-6-0-digital-bivolt-preto-moto700).
4. [Hayamax MOTO700 black specs](https://origin.hayamax.com.br/telefone-sfio-digital-moto700-preto-motorola).
5. [Model-family homologation, tone/pulse and other features](https://www.magazineluiza.com.br/telefone-motorola-moto700-sem-fio-branco/p/ef80g2e18g/tf/tfra/); white variant shares the referenced MOTO700 family designation but isn't necessarily identical in adapter details.
6. [RTV9015VW external teardown](https://www.tripleoxygen.net/wiki/modem/rtv9015vw): related-device FXS hardware lead; not evidence of live owner's specific circuit.
7. [ASKEY-NET-010](experiments/askey-net-010.md), [ASKEY-NET-011](experiments/askey-net-011.md), [telephony architecture proposal](telephony-and-voice-automation.md).

## 7. Handoff decision

Current implementation tracks the [telephone interface and dial-code lab](telephony-dial-code-lab.md). The separate [future DSL copper lab](dsl-copper-lab.md) records the owner's additional learning experiment. Existing numbered steps above retain their original proposed-test status unless a dated experiment reports completion.

**Start with the hardware already present**, not new purchases. Confirm base/handset power and DECT registration first, then verify basic Askey analog-line behavior and investigate local SIP configuration. Use the MOTO700 in **DTMF** mode for the first PBX/agent calls. The eventual rotary phone becomes a separate analog/pulse/bell compatibility experiment. Record each newly observed result in a dated `docs/experiments/askey-voice-00x.md` before declaring another milestone.
