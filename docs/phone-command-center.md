# Phone command center: access, configuration and desktop actions

Implemented 2026-11-04. The owner verified menu `4` restoring screens and `3` entering cinema on the Bravia while the cursor was on another screen.

## Accessing Asterisk and the container

There is no browser UI installed. Asterisk provides a CLI. Its binary is inside the Ubuntu container, not installed in the host's PATH, so host `which asterisk` returning nothing is expected.

From the workstation:

```sh
# Attach to the running Asterisk console. exit / Ctrl-D detaches without stopping it.
rtk proxy docker exec -it mero-askey-pbx asterisk -rvvv

# Run one Asterisk command and return to the normal terminal.
rtk docker exec mero-askey-pbx asterisk -rx 'pjsip show contacts'
rtk docker exec mero-askey-pbx asterisk -rx 'core show channels'
rtk docker exec mero-askey-pbx asterisk -rx 'core show version'

# Enter a normal shell inside the container, rather than the Asterisk console.
rtk proxy docker exec -it mero-askey-pbx /bin/bash
```

`docker exec` starts another process in an already running container. The shell/CLI is not the PBX's main process. Exiting that shell or remote console leaves the PBX running. Asterisk's `core stop now` would stop the PBX; it is not the command for detaching.

No Asterisk HTTP or manager interface is enabled. A future web UI would be another component; it is not required for this implementation.

## Startup policy

`restart: "yes"` is not a Docker restart policy. The owner's intended startup behavior is now configured as **`unless-stopped`**, both in Compose and on the existing running container. Docker is enabled at host startup. A deliberate stop remains respected. The workstation has not been rebooted to test recovery.

The separate host command worker is an enabled **systemd user service**, `command-phone.service`. It starts with the user's service manager and restarts on failure. Its private Docker-bridge listener may need to wait for Docker's network; systemd retries startup. Desktop actions require the owner's Hyprland session. No lingering/boot-without-login policy was added.

## What `secrets.token_hex(4)` means

`secrets` is Python's standard library module for secure random values. `token_hex(4)` generates four random bytes encoded as eight hexadecimal characters. In the isolated test it only makes a unique temporary container name, preventing naming collisions. It does not load a password and is not an authentication secret stored elsewhere.

Real credentials are different:

| Private path | Purpose |
|---|---|
| `.local/router-login.json` | Owner's intended router login, used only by provisioning/audit tools |
| `.local/capture-target.json` | Target/connection metadata, including the SSH key path for older lab operations |
| `.local/telephony-pbx/account.json` | Generated SIP endpoint password and endpoint/server metadata |
| `.local/telephony-pbx/etc/pjsip.conf` | Generated Asterisk config containing the SIP password |
| `.local/telephony-command/account.json` | Independent random token and private bridge addresses for the host command worker |
| `.local/telephony-pbx/etc/extensions.conf` | Generated dialplan, now also containing the authenticated FastAGI URI |

These are ignored by Git. Credential files are mode `0600`, and their private directories are `0700`. They are local plaintext files protected by filesystem permissions, not an encrypted secret vault. Private captures/exports may also contain credentials. Avoid publishing raw dialplan/verbose AGI logs: those can contain the worker URI/token.

## Which configuration to edit

`extensions.conf` and `pjsip.conf` are generated from tracked **`tools/prepare_telephony_pbx.py`**. Their generated copies contain machine-specific settings and secrets, so they are not tracked. The tracked generator contains placeholders and reads the private account files.

For durable menu changes, edit the generator, regenerate and reload the dialplan:

```sh
rtk python3 tools/prepare_telephony_pbx.py
rtk docker exec mero-askey-pbx asterisk -rx 'dialplan reload'
```

For spoken wording/voice changes, edit `tools/build_telephony_prompts.py`, then run it when no call is active. Direct edits to generated config are possible for experiments, but preparation overwrites them. SIP transports/module changes need their own reviewed reload/restart; `dialplan reload` only reloads call routing.

Router configuration remains outside the phone runtime: the inspection/provisioning tools are invoked separately. Neither Asterisk nor the host command worker reads the router login file or imports Askey settings. The phone is becoming a command center and, later, a frontend for existing agent runtimes.

## Cinema action and host/container boundary

```text
Handset menu 3/4
  → Asterisk FastAGI request over the private Docker bridge
  → command_phone.py, running as the desktop user
  → existing archmeros-cinema-mode.sh with an explicit target
  → Hyprland and the existing display/service restore logic
```

The keyboard shortcut calls `~/.config/archmeros/scripts/archmeros-cinema-mode.sh`. That script already supports `enter --monitor OUTPUT`, so no change to the shortcut or global desktop script was required.

`tools/command_phone.py` resolves the unique connected monitor whose make/model are Sony / SONY TV. It currently resolves to **DP-1**. It invokes `enter --monitor DP-1`, independently of focus or cursor position. It never simulates Super+Shift+S or moves the cursor. Cinema-on refuses to silently retarget an already active cinema session on another output.

| Phone key | Named action | Behavior |
|---|---|---|
| `3` | `cinema_on` | Enter cinema on the explicit Bravia target; repeated calls leave it on |
| `4` | `cinema_off` | Invoke the existing restore logic; repeated restoration is harmless |

The host worker accepts only named registry entries, verifies an independent token and the PBX container's private source address, and serializes actions. There is no free-form command/argument interface. Display actions run as the owner, not as container root. Docker/Wayland/Hyprland sockets, the home directory and router credentials are not mounted into the PBX for this feature.

## Extending `command_phone.py`

Add an argument-free Python function for the exact action and register it in `COMMANDS`. That function should use fixed targets and `subprocess.run([...], timeout=..., check=True)` where a program is needed. Do not use `shell=True` with caller-controlled data. Return a small fixed result code, then add its explicit menu branch and spoken success/failure prompts in the tracked generators. Future Suzy/Sera adapters belong behind similarly explicit interfaces, preserving their own voices/state/tools.

Useful host commands:

```sh
rtk python3 tools/command_phone.py list
rtk python3 tools/command_phone.py plan cinema_on
rtk python3 tools/command_phone.py run cinema_status
rtk proxy systemctl --user status command-phone.service
rtk proxy journalctl --user -u command-phone.service -n 20 --no-pager
```

`plan` is read-only and shows the physical target and argument vector. `run cinema_on` and `run cinema_off` actually change displays; use them intentionally.

## Reproducing the worker

With the PBX already running on its private Docker network:

```sh
rtk python3 tools/command_phone.py configure
rtk proxy systemctl --user link /home/zacmero/projects/mero-askey/lab/telephony/command-phone.service
rtk proxy systemctl --user enable --now command-phone.service
rtk python3 tools/prepare_telephony_pbx.py
rtk python3 tools/build_telephony_prompts.py
rtk python3 tools/check_telephony_pbx.py
rtk python3 tools/test_command_phone.py --live
rtk docker exec mero-askey-pbx asterisk -rx 'dialplan reload'
```

The generated module list includes `res_speech` and `res_agi`; the former is an AGI dependency, not a configured speech-recognition/cloud service. A newly created PBX loads both at startup. An already running PBX needs them loaded before using AGI.

`configure` preserves the token and records the current private bridge gateway/container IP. If that network or container address changes, rerun it, restart the user worker and regenerate/reload the dialplan. The host service file is linked from this repository; after changing its unit definition, run `systemctl --user daemon-reload` and restart it.

Stop only host command execution with `systemctl --user disable --now command-phone.service`. This does not stop telephone calls or change router settings. The original desktop shortcut remains available. Restore cinema before disabling the worker if you want all screens on.
