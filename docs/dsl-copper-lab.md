# Future private DSL copper lab

Recorded 2026-11-04 at the owner's request. Status: a future learning experiment; no DSL connection, synchronization or DSL configuration change has been performed for this guide.

## Purpose and roles

Use the Askey RTV9015VW's DSL modem interface to study a digital network link over a copper telephone pair. Its DSL socket and green PHONE socket have different electrical and protocol roles even though their cables look similar. PHONE serves the analog handset; DSL connects the subscriber modem to a compatible DSL network peer. Do not connect the PHONE output to the DSL input.

ADSL defines a central-office transceiver (ATU-C) and subscriber transceiver (ATU-R). A private link would require a compatible DSLAM or another device with an explicitly supported central-office role. Two ordinary subscriber modems generally cannot establish that complementary link. No such central-office equipment is currently established as available in this project, and Askey central-office mode has not been demonstrated.

```text
Private server/LAN — compatible DSLAM/CO peer — isolated copper pair — Askey DSL — lab client
```

DSL mode, annex, supported profiles and framing must be checked on both endpoints before choosing a peer. Do not infer VDSL compatibility from the model name. The pair must be isolated from household telephone wiring, the public telephone network and active FXS outputs.

## Accessory from owner photo: Opticom MF42T (2026-11-05)

Owner has an **Opticom MF42T** ADSL microfilter (old ANATEL identification **0030-07-1714**, 2007 listing), visually labeled **Linha** (incoming), **Telefone** (filtered voice) and **ADSL** (unfiltered DSL/modem). It is a filter/splitter of **frequency bands on one existing line**, not a second modem, a DSLAM, a signal source or a two-phone parallel splitter. No bench test was performed.

Its normal historical circuit is `telephone-company copper line → Linha → ADSL modem on ADSL socket + analog phone on Telefone socket`. That is documented as an ADSL-era accessory; **do not assume it is suitable for every VDSL2 profile**, especially higher-frequency modes, without electrical specifications and a verified peer. The ADSL socket may expose live line conditions and is not an alternate phone or LAN jack.

For a private Askey DSL experiment the real missing piece is a **known DSLAM/central-office-mode device**, and an isolated copper pair. Neither the microfilter nor the PM-1 wall box provides the missing CO transceiver. Do not connect Askey **PHONE/FXS** into its **DSL** port, into another FXS, or into unverified public wiring. Existing Askey-phone communication goes over Ethernet to Asterisk and does **not** require DSL. References: [Cisco ADSL troubleshooting](https://www.cisco.com/c/pt_br/support/docs/long-reach-ethernet-lre-digital-subscriber-line-xdsl/asymmetric-digital-subscriber-line-adsl/200456-Troubleshoot-ADSL-on-Cisco-Routers.html), [Cisco DSL back-to-back CO/CPE roles (SHDSL example)](https://www.cisco.com/c/pt_br/support/docs/wan/point-to-point-protocol-ppp/200636-EHWIC-4SHDSL-EA-Back-to-Back-SHDSL-Con.html).

## Learning experiments

| Experiment | Observation | What it teaches |
|---|---|---|
| Establish a baseline link | Negotiated mode, upstream/downstream sync, training time | The two modem roles and link negotiation |
| Compare known cable lengths | Attenuation, SNR margin, attainable and negotiated rates | Copper loss and rate adaptation |
| Observe normal link quality over time | CRC/FEC counters, errored seconds and retrains | Distinguishing corrected errors from service interruption |
| Carry private network traffic | Throughput, latency, loss and bidirectional voice quality | The difference between DSL sync rate and useful network capacity |
| Add a private access service | Bridging, VLANs, and PPPoE if supported by the selected setup | How the access link reaches a local service network |

Do not inject voltages or construct noise sources as an initial experiment. Use supported configuration controls and known cables. Any later electrical experiment needs its own equipment assessment and procedure.

## Entry criteria and first trial

1. Inventory the Askey's actual DSL capabilities through read-only status/configuration.
2. Identify an available peer and verify its central-office role, electrical interface, DSL mode and annex compatibility from its own documentation.
3. Agree on an isolated topology and preserve both devices' current configuration and a management path.
4. Connect only the agreed copper pair, then observe one bounded training attempt.
5. If synchronization succeeds, record both ends' status before testing private IP traffic.
6. Disconnect the experimental pair and restore any explicitly changed configuration after the trial.

Success means independently observed synchronization at both ends, followed by reproducible private network traffic. A lit power LED or matching connector is insufficient.

## Relationship to the telephone lab

The current telephone lab uses **MOTO700 → Askey PHONE/FXS → Ethernet → private PBX**. It does not require DSL, a telecom subscription or the future copper experiment. Later, the DSL link could carry that private SIP/RTP traffic to compare voice behavior under different link rates and conditions.

Sources: [RFC 4706, ADSL2 terminology and management](https://www.rfc-editor.org/rfc/rfc4706.html), [ITU-T G.992.1, ADSL transceivers](https://www.itu.int/rec/T-REC-G.992.1/en). These establish DSL concepts; they do not certify this Askey's supported modes or a compatible peer.
