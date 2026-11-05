# ASKEY-VOICE-001 — Private telephone lab baseline

Date: 2026-11-04, UTC−03:00. Target: owner's Askey RTV9015VW, `BR_SO_RTK_V6.1.8t`.

## Owner report

The Motorola MOTO700 is working and its base is connected to the Askey's green PHONE port. Pressing the call key produces **silence**. No completed call, incoming ring, digit recognition or bidirectional speech was reported.

## Read-only local observation

The workstation's route to `192.168.1.250` uses `enp5s0`, source `192.168.1.97`. Its neighbor entry matches the recorded Askey identity. The household connection was retained.

The bounded [voice inspector](../../tools/inspect_telephony.py) authenticated with the owner's existing private credentials, downloaded the native settings export, and retrieved the native `voip_status.htm`, `voip_basic.htm` and `voip_advanced.htm` pages. It submitted no voice-settings form and performed no service restart, settings import, reset or firmware write.

| Field | Observed live value |
|---|---|
| LAN address | `192.168.1.250` |
| DHCP service | `0x0` |
| `VOIP.INTERFACE` | empty |
| Port 0 proxy 0 enable | `0` |
| Port 0 proxy/registrar address | empty |
| Port 0 account login/password | empty; no credential values published |
| SIP signaling port | `5060` |
| Media port setting | `16384` |
| WAN voice VLAN enable | `0` |

The native basic form offers `voipinterface=any` (selected) and `voipinterface=br0`. It exposes first-account enable, number, login/password, proxy address/port, domain and outbound-proxy controls. Presence of these controls establishes a configuration path; registration to a private PBX remains untested.

The current export SHA-256 is `f34f093d50bdf1b78fb3a5d4b0083e7fd721b831e4059d5c12cd025eb7db35bb`, exactly matching the approved ASKEY-NET-011 candidate. This is a fresh preserved settings baseline, not a demonstration of total-lockout recovery.

Silence is consistent with an inactive or unconfigured voice service. The observation does not establish an FXS electrical fault, working off-hook detection or a working SIP path.

## Private evidence

Raw pages/export and safe summary: `.local/askey-voice-001/1793839798488748348/`.

| Artifact | SHA-256 |
|---|---|
| `config-current.img` | `f34f093d50bdf1b78fb3a5d4b0083e7fd721b831e4059d5c12cd025eb7db35bb` |
| `voip_status.htm` | `c039b5cfff7600a046c8782b5edc9ff92a6deb23ec49354e7625a4955b7c39ca` |
| `voip_basic.htm` | `33009ef483a5118f3698b64c76888db77d76a25bb1f58762e7f2115391f7900d` |
| `voip_advanced.htm` | `fabf300a3e20f9a94a63c3e4e627b92b903bfb3855d935cf5da5bf352ca6bef0` |

## Next experiment

Prepare an authenticated private PBX endpoint at `192.168.1.97:5060`, with endpoint `10` and echo extension `19`. Preserve the current export and review the native voice form before any persistent change. Proposed first voice change: select LAN interface `br0`, enable only the first account, and point it at this local PBX with newly generated lab credentials. Leave the second account, WAN, DHCP and other services intact. The reviewed operation must include a rollback path before applying it.

The [dial-code guide](../telephony-dial-code-lab.md) records planned voice-agent links and fixed network actions; none is claimed as active in this baseline.

## Approved PBX and voice configuration

The owner explicitly approved starting the dedicated PBX and applying the voice-only change: LAN interface `br0`, line identity/extension `10`, a new private lab password and SIP server `192.168.1.97`. The original export and native form values were retained before any submission.

The [PBX deployment](../../lab/telephony/README.md) is running in a dedicated Docker network. Only UDP SIP `192.168.1.97:5060` and RTP `192.168.1.97:10000–10019` are published. The endpoint ACL admits the Askey. No PSTN trunk, voice agent or network-command action is configured.

The first native submission populated account/interface fields, but a newly checked enable control was appended after the final dispatch marker and was ignored. The handler returns HTTP **301 to `voip_basic.htm`** on submission; an initial audit script incorrectly treated that response as failure. Readback was performed before any further write. A functional rollback restored the original disabled/interface state, but native empty-string submissions retained the new line identity fields. Exact original-export restoration was not claimed or attempted.

Static inspection of the native handler at `0x8029015c`–`0x80290186` confirmed that the enable bit depends on the parsed control's presence. Repeating the approved change with the native DOM field order, a fresh authenticated form/CSRF field and proper handling of the observed redirect produced:

| Check | Result |
|---|---|
| Voice interface | `br0` |
| Main proxy enable | `1` |
| SIP endpoint | `10` |
| PBX dynamic contact | `sip:10@192.168.1.250:5060` |
| LAN IP / DHCP | `192.168.1.250` / `0x0`, unchanged |
| Final export SHA-256 | `196d00dc35953438be29c72fba6f7d5085c05586446387e2145496a7e44abab2` |

Private final submission evidence: `.local/askey-voice-001/1793839798488748348/apply-1793840980994827927/`. The native form shares one phone-line identity between its main and backup proxy entries. The backup proxy server and enable control were not activated; the initial wording describing it as a separate account was corrected.

Registration is demonstrated. Persistence through a router reboot has not been tested.

## Handset and call-driver follow-up

The owner subsequently reported **dial tone and dialing**, but **no echoed voice** on the first attempt at `19`. The PBX's registrar had loaded, while `chan_pjsip` had failed to load because its required `res_pjsip_pubsub` module was absent from the explicit module list. This was a PBX configuration error, not a diagnosed Askey audio failure.

Both modules were then loaded successfully in the running PBX. The prepared module list and isolated test were corrected to verify the PJSIP channel driver as well as registration/configuration. The isolated test passes. A second handset echo trial was requested; its result is pending.

## Completed incoming call and microphone tests

The second outgoing echo attempt still produced no audible voice for the owner. Instead of repeating keypad instructions, the owner requested a direct incoming call. The PBX originated a call to `PJSIP/10` and used `Playback(hello-world)` after answer. A live channel snapshot showed `Ringing`; the owner then confirmed **receiving the call and hearing the hello-world message**. This establishes incoming ringing and PBX-to-phone audio.

A second incoming test was configured to answer, play a beep, record six seconds of microphone audio, play the recording back and hang up. The first attempt was unanswered; the owner explicitly asked to call again when ready. The retried call completed, and the owner confirmed **hearing their own recorded voice**. The resulting file is mono, 8 kHz, 16-bit PCM, exactly 48000 frames / 6.0 seconds.

This establishes the private path **MOTO700 microphone → Askey → PBX recording → Askey → MOTO700 receiver**. Incoming ringing, answer, audio in both directions and call completion are demonstrated. The result does not establish telephone-originated echo extension `19`, DTMF menu behavior, a voice-agent bridge or any network-command action.

Private evidence bundle: `.local/askey-voice-001/pbx-1793842751261590295/`. The voice recording is private and ignored; it has not been committed or sent to a transcription/voice service.

| Evidence | SHA-256 |
|---|---|
| PBX call log | `1e23b2fcd69168ef9ff470f57f1d2a13f2b132c9472b9340d9c7747bcb056739` |
| Dynamic contact snapshot | `818074d6d657c5059ad9ba9b2bce450bc46b3495ca578b486feff199fc8f8cf4` |
| Six-second test WAV | `a7f2b149ab5eb986e55612775e4676d27fbff94efac3ac19dc70bcb6265ba738` |

`res_clioriginate` and `app_record` were loaded for these owner-authorized calls and added to the reproducible module list. The one-off recording route uses `moto700-selftest-001.wav`; archive the test and choose a fresh filename before reusing that route, to avoid overwriting its container copy. The retained private evidence bundle is independent of that container file.

## Validation and rollback limits

The PBX image built successfully. An isolated disposable container with no external network loaded the endpoint, SIP call driver, codecs and echo/audio/DTMF dialplan. The test container was removed. A regression check verifies checkbox presence and the native form's final dispatch-marker ordering. Secrets and settings exports remain ignored/private.

Stopping the pilot uses `rtk docker compose -f lab/telephony/compose.yaml down`. Native voice-form rollback can disable registration and revert the interface; it does not erase stored identity/password fields when their original values were empty. Exact restoration needs the preserved original export and a separately explicit import/reboot instruction. No factory reset or firmware/bootloader write was performed.
