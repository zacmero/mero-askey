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

## Direct dialing and usability follow-up

The owner subsequently confirmed dialing **20 directly from the handset** reaches the menu. They reported one unexpected disconnect during a connection check; a later call worked. The historical log contains an exit during result playback, but does not prove the precise disconnect cause.

Two prototype limits were identified in the dialplan: four menu entries and a 15-second no-input hang-up. The revised dialplan removes the count-based stop, waits 60 seconds for a digit, and announces/repeats on timeout rather than ending the call. The connection attempt still has its independent three-second bound. Menu input state and hang-up cause are logged at NOTICE for future diagnosis. The isolated configuration/module check passed and the revised dialplan was loaded without restarting the PBX or changing the router.

The robotic eSpeak prompts were replaced with local Piper 1.8.0 neural female narration (`en_US-lessac-medium`, length scale 1.12). The owner liked the initial local preview. Five prompts, including the idle announcement, were generated and installed as mono 8 kHz PCM WAV files. No OpenRouter/LLM, external speech service or agent voice was used. The first CLI attempt played the preview locally instead of streaming a WAV; explicit `-f -` corrected the generator before installation. See the [implementation map](../telephony-implementation-map.md) for code, startup and voice details.
