# ASKEY-VOICE-002 — Keypad input and private command menu

Date: 2026-11-04, UTC−03:00. Baseline: [working private calls](askey-voice-001.md), Askey extension `10`, PBX `192.168.1.97`.

## Keypad proof

The PBX called the registered handset into `lab-keypad-selftest`, played a beep, collected one digit and spoke it back using `SayDigits`. The owner pressed **7** and confirmed hearing **seven**. This demonstrates digit reception at the PBX during an established call. It does not establish that dialing arbitrary short extensions or star codes before a call is forwarded correctly by the Askey's own dial plan.

## Implemented menu

The `lab-menu` context uses locally generated eSpeak prompts. No external speech service is involved. The PBX can originate a call into this menu; extension `20` also routes to it, although phone-originated dialing of `20` remains unverified.

| Key | Fixed behavior |
|---|---|
| `1` | Play the existing hello-world audio test |
| `2` | Run a fixed TCP connection check against Askey `192.168.1.250:80`, then speak success/failure |
| `9` | Repeat the menu |
| `0` | Hang up |

The connection check uses a literal command with `/usr/bin/timeout 3`; no keypad digit, hostname, URL or executable argument is interpolated into it. A reachable port is reported as such, not as internet availability or a complete HTTP/application health check. Invalid digits trigger a fixed error prompt. No-input waits are limited to 15 seconds and the menu permits at most four entries before ending the call.

Source: [PBX preparation](../../tools/prepare_telephony_pbx.py), [local prompt builder](../../tools/build_telephony_prompts.py). The isolated test checks the keypad/menu routes and required modules. Prompt generation uses the built PBX image and the workstation's existing FFmpeg, producing mono 8 kHz PCM files under ignored `.local/telephony-pbx/sounds/`. The existing pilot received copies in its container; future containers use the read-only prompt mount in Compose. The active PBX was not recreated, and router settings were not changed during this experiment.

An incoming menu call was placed and the owner selected `2`, then `0`. The owner confirmed the menu worked, announced a successful connection and hung up on `0`. This demonstrates the path **keypad → PBX fixed command → network connection attempt → spoken result → keypad hang-up**. It does not establish any arbitrary command interface or agent integration.
