# ASKEY-NET-002 — Authorized advanced-menu configuration import

Date: 2026-10-27, UTC−03:00. Status: authorized import/reboot completed and verified; full native menu available; no OS shell yet.

## Authorization and rollback

The owner explicitly approved importing the prepared configuration and rebooting after reviewing the exact two-flag change and rollback described in [ASKEY-NET-001](askey-net-001.md).

Original `.local/askey-net-001/config.img`: 205061 bytes, SHA-256 `f4f03b82fc9d927618e17241889e3fee6c990b77648c777cc5ec3c8d21ef42df`.

Imported `.local/askey-net-001/config-advanced-menu.img`: 205061 bytes, SHA-256 `ae361192895261a4ed2f89655199be2ea844626a851155720c3fffdbbfadaf65`. Both hashes were reverified immediately before import, along with identical size and exactly two changed bytes:

- `ENABLE_ADVANCE_PAGE`: `0x0` → `0x1`.
- `PADRAO_WIFI_ONLY`: `0x1` → `0x0`.

No SSH/Telnet state flag was edited. Rollback while management is available is restoration of the retained original export through the native restore form and reboot as required. If management fails to return, stop remote probing; physical recovery/reset would require the owner and an explicit instruction for that recovery operation.

## Actual operation

Reverified the laptop's direct Ethernet route and target neighbor, authenticated as the known support account, fetched the native `/saveconf.htm` page, and parsed its actual restore form. Submitted a single multipart POST to `form2fileConf.htm`, using the form's actual file input `download image file`, `send=Upload`, and its hidden `submit` field. The payload was the verified prepared configuration, named `config.img` for upload.

Router response: HTTP 200, body `Autoboot`, elapsed approximately 3.473 seconds. The upload started at Unix time `1793073774.0463345`. This indicates that the native handler initiated automatic boot; no separate reboot request was sent.

Raw response retained in `.local/askey-net-001/import-menu-response.json`, SHA-256 `a3fb73da696c03f803f392dcebcb7b652600e96b806147083fc1090e728db04e`.

The next step is bounded recovery verification, then inspection of the resulting native menu and service controls. An HTTP success response alone does not prove that the flags persisted or that a shell is available.

## Recovery and persistence verification

At Unix time `1793073837.2470095`, approximately 63 seconds after upload began, the first recovery check received HTTP 200 from the router. The Ethernet route and original Askey neighbor identity were intact. The laptop's control route to mero-machine still used Wi-Fi.

Support login succeeded after reboot. Re-exported settings through the native backup form: 205061 bytes, SHA-256 `ae361192895261a4ed2f89655199be2ea844626a851155720c3fffdbbfadaf65`, exactly matching the approved candidate. All 4627 configuration field names/order match the original export; only the two approved flag values differ.

The advanced index now loads `user04Menu_vd_BR_SO_RTK_V6.1.8t_Feb_20_2017_19_16_25_0.js` instead of the prior Wi-Fi-only menu. It exposes routing, firewall, backup and diagnostic pages, but contains no SSH/Telnet service-control link. Native `/userconfig.htm` offers restricted web-user account controls, not terminal activation. Native `/ping.htm` exposes a diagnostic form; it was read only, with no diagnostic POST submitted.

Raw post-import verification: `.local/askey-net-002/post-import-verification.json`, SHA-256 `c08ef72fe18c73636ec3f3ae805a0e5cf0d1e1b5efac098a95574568969f3ef0`.

Actual re-export: `.local/askey-net-002/config-after-menu.img`, hash above. Full-menu capture: `.local/askey-net-002/full-native-menu.json`, SHA-256 `7ab2900ddfb7c05c07284301d03c4f8df6a56eb9cab2e1f53aa6319290c2e1f0`. Account/diagnostic page capture: `.local/askey-net-002/native-account-and-ping-pages.json`, SHA-256 `dba52c093e2bbc2efd681dd9ab21e1100d2bf27eef1fbef2fe097631de66b39f`.

No rollback was needed. No service activation, account change, factory reset or firmware write was performed. The current next step is matching-source research to understand SSH/Telnet state flags and locate actual controls; flag meanings must not be guessed.

Follow-up research and the separate, unapplied Telnet-state candidate are recorded in [ASKEY-NET-003](askey-net-003.md). The menu import/reboot authorized in this report is complete.
