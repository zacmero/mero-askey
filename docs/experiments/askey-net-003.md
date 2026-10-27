# ASKEY-NET-003 — Prepared Telnet activation experiment

Date: 2026-10-27, UTC−03:00. Status: explicitly authorized Telnet activation/import/reboot completed; persistence and login verified. Vendor console access established; no OS shell.

## Actual authorized import

The owner instructed: enable Telnet and test it. Reverified both local file hashes and the laptop's Ethernet route/Askey neighbor. A fresh live settings export exactly matched the known rollback hash before upload, so no intervening settings change was overwritten.

Submitted the verified one-byte candidate once through the parsed native restore form. HTTP 200 response body `Autoboot`, elapsed approximately 3.493 seconds. Upload began at Unix time `1793074591.9730203`. No separate reboot request was sent.

Raw response: `.local/askey-net-003/telnet-import-response.json`, SHA-256 `9a8ae3686ee74d0acf18e31484517d12a194a0aa424a5859badd2a610ee02334`.

Recovery, persisted flag and actual Telnet access are pending verification. The preparation/authorization discussion below is the historical preflight record.

## Verified recovery and Telnet result

At Unix time `1793074692.9060583`, approximately 101 seconds after upload began, the first recovery check received router HTTP 200. Ethernet target route/neighbor and Wi-Fi control route remained intact. Support web login worked.

Fresh export `.local/askey-net-003/config-telnet-enabled.img` is 205061 bytes with SHA-256 `721cc151716e65c733f6f37d3ca18525b1d901380ca990355ed774d9716ff1b9`, exactly equal to the authorized one-byte candidate. Response capture `.local/askey-net-003/post-telnet-import-export.json`, SHA-256 `d19ce0a642d3e5a6ee1ee2f883e38e8f5cd836d795a8e3aaa3b5f6e7f2f343e4`.

Telnet now presents an authentication prompt and accepts the supplied admin credentials. It exposes two vendor console levels rather than a demonstrated OS shell. Actual system inventory and privilege limits are recorded in [ASKEY-NET-004](askey-net-004.md) and [device specifications](../device-specs.md). The connection was logged out/disconnected; Telnet service remains enabled as requested.

The preparation and proposed-operation sections below are historical. This specific activation has now been authorized and completed. No additional service/account/ACL setting change was made.

## Current local evidence

The owner-approved advanced-menu import/reboot completed successfully in [ASKEY-NET-002](askey-net-002.md). Fresh settings export exactly matches its two-flag candidate. Normal admin and support web access work; no OS shell has been obtained.

The expanded native menu has no terminal-service control link. `/userconfig.htm` provides restricted web-user controls. No account or diagnostic action was submitted. Current exported values are `TELNET_STATE=0x0`, `TELNET_PORT=0x17`, `SSH_STATE=0x0`, `LAN_ACL_ENABLE=0x0`, and `WAN_ACL_DEFAULT_ACTION=0x1`. The configured `TELNET_ACL_ONCE_FLAG` mentioned by a related-device report is absent from this unit's export.

A fresh authenticated native status page reports DSL operational state/speeds as `--` and all listed WAN interfaces down. This is a software observation, not physical proof that every WAN cable is disconnected. The router's own clock reset to 2011 after boot; workstation timestamps remain the session reference.

Status capture `.local/askey-net-002/authenticated-status.json`, SHA-256 `6be87f22a8b4ca6f6d85921736d46e4e20b342b8a3abf2e3b05eeda210194af4`. An earlier unauthenticated status request returned a login redirect with HTTP 200 after the session expired; it was not treated as runtime status. Authenticated page content was verified after re-login.

## External evidence and applicability

A [firsthand Beetel 777VR1 report](https://gist.github.com/raghav20232023/39e3d88d1bc2bcef89bb0f3b5fbb73e0) describes the same accept-then-close Telnet symptom and reports that setting `TELNET_STATE` from `0x0` to `0x1` enables its Telnet console. That console reportedly offers a `sh` command. Its attached configuration shares the `TELNET_STATE`, `TELNET_PORT` and WAN/LAN ACL field names with this Askey.

This is related-device evidence, not a verified procedure for RTV9015VW firmware `BR_SO_RTK_V6.1.8t`. It supports a narrowly defined experiment, not a promise of Telnet login, OS shell or root privilege. No unrelated firmware or credentials will be imported.

Related public `ysleu/RTL8685` SDK source was also inspected. Its Boa `.asp` interface differs from this device's Virtual Web/form2 interface, and the inspected MIB/daemon files did not establish the Askey's terminal-state semantics. It is not used as proof of compatibility. Code-search connector output was unusable; direct GitHub API/raw source retrieval worked. A public code index returned HTTP 429 and was not retried.

## Exact prepared change

Prepared from the actual post-menu settings export:

```diff
-<V N="TELNET_STATE" V="0x0"/>
+<V N="TELNET_STATE" V="0x1"/>
```

Verified 205061 bytes before and after, with exactly one differing byte. No SSH, account, ACL or WAN setting is changed. Service binding is not yet known; existing WAN policy must not be represented as a verified LAN-only service restriction.

| File | SHA-256 |
| --- | --- |
| Current rollback export `.local/askey-net-002/config-after-menu.img` | `ae361192895261a4ed2f89655199be2ea844626a851155720c3fffdbbfadaf65` |
| Proposed `.local/askey-net-002/config-telnet-enable.img` | `721cc151716e65c733f6f37d3ca18525b1d901380ca990355ed774d9716ff1b9` |
| Retained primary report `.local/research/beetel-telnet-primary.json` | `1df5b43fb41bcda26e6dca82f3040a18e4a6e691593990a346099d26aa6792a8` |

## Proposed operation, verification and rollback

AGENTS.md requires an explicit instruction for the actual service activation/configuration restore. The prior approval covered the two menu flags; this separate service change is pending approval.

If approved: authenticate with the known support account, upload this one-byte candidate through the already observed native restore form, allow its automatic reboot, verify recovery and re-exported settings, then make one bounded Telnet connection. Use configured credentials or the owner's known credentials as appropriate to the actual login prompt; do not guess password lists. Classify the resulting prompt before attempting OS inventory. Do not infer a Linux shell from a vendor menu.

Rollback: while management works, restore `config-after-menu.img` through the same native form and allow its automatic reboot. This restores the known Telnet state while preserving the approved expanded menu. If management fails to return, stop remote probing; physical reset/recovery would require the owner's explicit instruction and action. Keep WAN disconnected during this experimental activation until service binding/access can be assessed.

No service activation, diagnostic command execution, second restore or second reboot has occurred as part of this prepared experiment.
