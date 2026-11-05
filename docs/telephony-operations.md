# Telephone lab operations quick reference

Recorded 2026-11-05. Run the commands below **on mero-machine, from the project root**, unless a command explicitly opens the container shell. These operations manage the PBX or host worker; none imports or changes Askey configuration.

## Know the three environments

| Environment | What runs there | Access |
|---|---|---|
| Workstation | Python generators, private files, desktop command worker, Docker | Normal terminal in this repository |
| Ubuntu container `mero-askey-pbx` | Asterisk and its CLI | `docker exec` |
| Askey router | Its existing OSK firmware, analog phone interface and SIP client | Separate router audit/provisioning tools |

The container has its own installed programs and filesystem, while sharing the host's Linux kernel. A container shell is not an Askey shell. The host need not have an `asterisk` binary installed. RTK is a host tool; it is not installed in this container.

## Status and read-only inspection

```sh
rtk docker compose -f lab/telephony/compose.yaml ps
rtk docker exec mero-askey-pbx asterisk -rx 'core show version'
rtk docker exec mero-askey-pbx asterisk -rx 'pjsip show contacts'
rtk docker exec mero-askey-pbx asterisk -rx 'core show channels'
rtk docker exec mero-askey-pbx asterisk -rx 'core show channeltypes'
rtk proxy systemctl --user status command-phone.service
rtk proxy journalctl --user -u command-phone.service -n 20 --no-pager
rtk python3 tools/command_phone.py list
rtk python3 tools/command_phone.py plan cinema_on
```

`contacts` shows registered phone destinations; `channels` shows active calls. `plan` previews the target and argument list without changing screens. `run cinema_on` / `run cinema_off`, unlike `plan`, really change displays.

Keep raw logs and full dialplan dumps private: generated AGI URIs can contain the command-worker authentication token.

```sh
rtk docker logs --tail 50 mero-askey-pbx
```

## Interactive Asterisk CLI

```sh
rtk proxy docker exec -it mero-askey-pbx asterisk -rvvv
```

This attaches a remote console to the existing Asterisk process. Type `exit` or press Ctrl-D to detach. The call service keeps running. Use `help` inside the console to list commands. `-rx` in the inspection examples runs one CLI command and returns to your normal terminal.

Do not use `core stop now` to detach: it stops Asterisk, and Docker's restart policy may then restart the container. Use Docker's explicit stop command when you intend to keep the service stopped.

## Linux shell inside the container

```sh
rtk proxy docker exec -it mero-askey-pbx /bin/bash
```

This starts a separate Linux shell process in the running container. Inside that shell, use normal Linux/Asterisk commands; RTK is not available there. `exit` returns to the host and leaves Asterisk running.

The generated `/etc/asterisk` configuration is mounted read-only. Edit its tracked generator on the host rather than attempting to change permissions or edit those mounted files inside the container. Changes made only to other container-local files may be lost when the container is removed/recreated. Files in the documented host mounts persist independently.

## Change menu logic

Finish active calls first. Edit tracked `tools/prepare_telephony_pbx.py`, then:

```sh
rtk python3 tools/prepare_telephony_pbx.py
rtk docker exec mero-askey-pbx asterisk -rx 'dialplan reload'
```

The generator preserves the existing private account password and writes the generated configuration. The reload applies call routing without restarting the container. This does not provision the router. Direct edits to generated `.local/telephony-pbx/etc/extensions.conf` can be overwritten by the generator.

Verify what loaded with an appropriate CLI query. A full menu dump can expose the private AGI URI; do not paste it publicly.

SIP transport, authentication and module changes are separate from dialplan changes. `dialplan reload` does not apply every possible Asterisk setting. Check the corresponding reload/restart requirement before making those changes. Do not delete the private account file to rotate a password: that would also require coordinating the Askey's credentials.

## Change voice wording or delivery

Edit tracked `tools/build_telephony_prompts.py`. With no active call:

```sh
rtk python3 tools/build_telephony_prompts.py
```

It generates local Piper speech, converts to telephone WAV format and installs the prompts. It refuses to replace prompts while a call is active. The private Piper environment/model must already be installed; see the [implementation map](telephony-implementation-map.md#voice-generation). No router change or dialplan reload is needed merely to replace a WAV at the same configured path.

## Change a host command

Edit the named action in tracked `tools/command_phone.py`, test it, then restart the worker while no command is executing:

```sh
rtk python3 tools/test_command_phone.py
rtk python3 tools/test_command_phone.py --live
rtk proxy systemctl --user restart command-phone.service
```

The default test checks targeting/authorization without changing displays. `--live` performs only an authenticated cinema-status query from the PBX. A new phone menu entry also requires generator changes, prompt generation and dialplan reload. Do not accept arbitrary caller-supplied command text or executable arguments.

After changing the systemd unit itself:

```sh
rtk proxy systemctl --user daemon-reload
rtk proxy systemctl --user restart command-phone.service
```

## Start, stop and restart

The PBX policy is `unless-stopped`. Docker is enabled at host startup. A deliberate stop is respected; restart-after-reboot behavior has not been verified by actually rebooting this workstation. The host worker is an enabled user service and requires the user's graphical session for desktop actions.

Stop/start the existing container without applying changed Compose definitions:

```sh
rtk docker stop mero-askey-pbx
rtk docker start mero-askey-pbx
```

Restarting interrupts active calls:

```sh
rtk docker restart mero-askey-pbx
```

Start or update the declared deployment:

```sh
rtk docker compose -f lab/telephony/compose.yaml up -d
```

Compose may recreate the container if its definition/image changed. Check phone registration afterward. Container-local test recordings are not permanent storage; preserve needed recordings privately before recreation/removal.

## Image rebuild and removal

Python menu/command edits do not require rebuilding the image. Rebuild when changing the Dockerfile/packages:

```sh
rtk docker compose -f lab/telephony/compose.yaml build
```

Building alone does not replace the running container. Applying the new image with `up -d` can recreate it and interrupt calls.

With calls ended and needed recordings preserved, remove this container and its dedicated network:

```sh
rtk docker compose -f lab/telephony/compose.yaml down
```

This retains the image and host `.local/` configuration, secrets, prompts and copied evidence. It does not preserve arbitrary files that existed only in the removed container. It does not reset the router or restore desktop cinema state.

If recreation changes the private bridge/container addresses, refresh the authenticated worker connection after the PBX starts:

```sh
rtk python3 tools/command_phone.py configure
rtk proxy systemctl --user restart command-phone.service
rtk python3 tools/prepare_telephony_pbx.py
rtk docker exec mero-askey-pbx asterisk -rx 'dialplan reload'
```

## Tests and private evidence

```sh
rtk python3 tools/check_telephony_pbx.py
rtk python3 tools/test_voice_form.py
rtk python3 tools/collect_telephony_evidence.py
```

The PBX check uses a disposable container with no external network and removes it afterward. Evidence collection reads status/logs; it does not initiate a call or recording. Its `--recording` option copies an existing authorized test recording. Keep raw evidence under ignored `.local/`.

See [command-center internals and secrets](phone-command-center.md) and [implementation map](telephony-implementation-map.md) for the underlying logic.
