# ASKEY-VOICE-003 — Cursor-independent Bravia cinema commands

Date: 2026-11-04, UTC−03:00. Owner requested phone-triggered cinema on the fourth Sony Bravia output, independently of cursor location, with future commands collected in `command_phone.py`.

## Implementation and evidence

- Existing Hyprland bindings call `archmeros-cinema-mode.sh`, which already supports `enter --monitor OUTPUT` and `restore`.
- Live read-only display inventory identified the unique Sony / SONY TV output as `DP-1`, while the focused output was `HDMI-A-1`. The command planner emitted `enter --monitor DP-1`.
- Added an allowlisted host-side FastAGI worker running under the owner's systemd user service. It authenticates the private bridge caller with a separate token and fixed peer address, and invokes the existing desktop script as the owner.
- Added menu `3` for cinema-on and `4` for restore, with local neural spoken acknowledgements. No keypress simulation or cursor movement is used.
- Unit guards passed: explicit monitor selection despite focus, ambiguous-monitor rejection, peer/token validation and unknown-action rejection. A live authenticated status request from the PBX container succeeded without changing displays.
- The isolated PBX validation passed after adding AGI's resident `res_speech` dependency and `res_agi` module.
- The owner tested restore, moved the cursor off the Bravia, invoked cinema and restored again, reporting: **everything works perfectly as intended**.
- User-service logs independently recorded successful `cinema_off` and `cinema_on` results. These logs contain action/result, not the authentication token or command output.

The owner also requested frequent-use PBX startup. Unsupported Docker policy `yes` was corrected to `unless-stopped` in Compose and applied to the existing live container without recreation. The worker is enabled as a user service. Reboot recovery has not been tested.

No Askey configuration was changed in this experiment. The worker does not read router credentials. The PBX was not given access to the Docker socket or desktop sockets. The global cinema script and keyboard shortcut were reused without modification.

See [access/configuration/extension guide](../phone-command-center.md) for source files, secret paths, container CLI access and adding future actions. GUI effects and background services remain governed by the owner's existing cinema/restore script.
