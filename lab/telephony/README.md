# Private Askey PBX pilot

State on 2026-11-04: the approved PBX is running; Askey extension **10** is registered. The owner confirmed incoming ringing, hello-world audio and hearing a six-second microphone recording played back. This proves audio in both directions. Telephone-originated echo and DTMF routes remain separate tests.

## Deployment

The image installs Ubuntu 24.04's Asterisk packages. The tested package reports `20.6.0~dfsg+~cs6.13.40431414-2build5`. Private configs and the random endpoint password are generated under ignored `.local/telephony-pbx/`, with restrictive permissions. The Docker build context is only this directory and contains no credentials or captures.

A dedicated Docker network isolates the runtime. Only UDP `192.168.1.97:5060` and RTP `192.168.1.97:10000–10019` are published. The endpoint ACL admits the Askey at `192.168.1.250`; HTTP and manager interfaces are disabled. Required SIP, codec and dialplan modules are loaded explicitly. Internal ephemeral runtime sockets are not published. No physical LAN interfaces are bridged together, and no DHCP service is started.

Prepared commands, from the project root:

```sh
rtk python3 tools/prepare_telephony_pbx.py
rtk docker compose -f lab/telephony/compose.yaml build
rtk python3 tools/check_telephony_pbx.py
rtk docker compose -f lab/telephony/compose.yaml up -d
rtk python3 tools/build_telephony_prompts.py
rtk docker exec mero-askey-pbx asterisk -rx 'pjsip show contacts'
```

The preparation tool reuses the existing private password; it does not rotate a working endpoint. The check starts a disposable container with **no external network**, verifies the endpoint/dialplan/modules and removes that test container. A running PBX does not prove a completed call.

## Phone interface

| Dial | Current PBX route | Verification status |
|---|---|---|
| `19` | Answer, echo speech, hang up when caller ends | Handset test pending |
| `10` | Ring the registered phone for up to 20 seconds | Endpoint incoming ringing/playback verified by PBX-originated call; dialing `10` from another endpoint untested |
| `*20` | Fixed “hello world” audio | Handset test pending; not live system status |
| `*29` | Prompt, collect one digit, speak that digit | Handset test pending; star-code forwarding unverified |

The owner-confirmed in-call digit test received `7` and spoke seven back. The menu (extension `20` / context `lab-menu`) offers `1` audio, `2` the fixed Askey TCP-port check, `9` repeat and `0` hang-up. Its command has a three-second bound and no caller-controlled arguments. The owner confirmed the successful spoken connection result on `2` and hang-up on `0`. Phone-originated short-code forwarding remains unverified. See [ASKEY-VOICE-002](../../docs/experiments/askey-voice-002.md). Other fixed actions and agent routes remain proposals in the [dial-code lab](../../docs/telephony-dial-code-lab.md).

The owner-authorized incoming playback and record/playback tests use CLI origination and the `lab-audio-selftest` context. The one-off recording route has a fixed filename; preserve its recording and choose a new filename before reusing it. Private recording evidence is retained under `.local/askey-voice-001/`; no audio is committed or sent to an external voice service.

## Askey native form and evidence

Read-only inspection: `tools/inspect_telephony.py`. Proposal preparation: `tools/prepare_voice_trial.py`. The operation-specific approved application is performed by `tools/apply_voice_trial.py`, which checks the route/neighbor and current export, retrieves a fresh session CSRF field, submits controls in the native page's DOM order, saves the response, then exports and checks the resulting fields.

This firmware's native form returns **301 to `voip_basic.htm`** after applying. A newly checked control appended after its final `submit.htm?voip_basic.htm` dispatch marker was ignored. Preserving the DOM order resolved the enable flag. The single phone line shares identity fields between its main and backup SIP proxies; a backup proxy is not another analog handset/account. Its enable flag and server remain unchanged.

The final observed voice state is interface `br0`, main proxy enabled, endpoint `10`, server `192.168.1.97`. LAN IP and disabled DHCP are unchanged. Configuration export SHA-256: `196d00dc35953438be29c72fba6f7d5085c05586446387e2145496a7e44abab2`. Persistence across a router reboot has not been tested.

## Stop and rollback

Stop only this pilot and remove its dedicated container/network:

```sh
rtk docker compose -f lab/telephony/compose.yaml down
```

This retains private configs/evidence and the image. To disable the phone registration and restore the original interface/form values, use the reviewed proposal's `rollback` operation through `tools/apply_voice_trial.py` while support access remains available. **Native empty-string submissions retain the stored line identity/password**; this is a functional voice-disable rollback, not exact restoration of the original export. A byte-equivalent settings restoration would require the preserved original export, a separately explicit import/reboot instruction and the recorded network recovery precautions. Do not factory-reset a switch-connected Askey.

See [ASKEY-VOICE-001](../../docs/experiments/askey-voice-001.md) for baseline, application evidence and actual test results. Reference: [official Asterisk PJSIP configuration examples](https://docs.asterisk.org/Configuration/Channel-Drivers/SIP/Configuring-res_pjsip/res_pjsip-Configuration-Examples/).
