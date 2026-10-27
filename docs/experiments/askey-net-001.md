# ASKEY-NET-001 — Ethernet management reconnaissance

Date: 2026-10-27, UTC−03:00. Status: normal and advanced web logins established; original configuration exported; genuine OS shell and native execution pending.

## Owner reports and target identity

The owner connected the Askey RTV9015VW to Mint laptop `cris-MS-1454` by Ethernet. Hardware revision is `Rev:01`; firmware is `BR_SO_RTK_V6.1.8t`. The agent independently confirmed these three fields on the device's native About page. Unnecessary serial/MAC identifiers are omitted.

| Laptop interface | Address | Role |
| --- | --- | --- |
| `enp6s0` | `192.168.15.3/24` | Direct lab route to `192.168.15.1`; Ethernet default metric 20100 |
| `wlp4s0` | `192.168.1.80/24` | Preferred household/control default via `192.168.1.1`, metric 600 |

Two owner runs of `nmap -Pn -sT -p 21,22,23,80,443,2323,8080 192.168.15.1` at 00:27 and 00:28 (-03) showed TCP 22, 23, 80 and 443 open; 21, 2323 and 8080 closed. The agent did not repeat this scan. Port labels alone do not identify daemons or establish shell access.

## Verified agent execution path

Execution host `mero-machine` is `192.168.1.97/24`. Its route to `192.168.15.1` goes through household gateway `192.168.1.1`; it is not a direct lab route, so router probes were not sent directly from this host.

The owner mentioned the existing key and `arch-local` alias. Adjacent project notes identified the established reverse control route as `cris@192.168.1.80`, key `/home/zacmero/.ssh/mero_stb_isolated_lab`; `arch-local` is the laptop-to-main alias. The agent reverified this route with `IdentitiesOnly=yes`, `BatchMode=yes`, and `StrictHostKeyChecking=yes`. Laptop hostname, interfaces, direct `enp6s0` route and Askey LAN neighbor matched the owner's supplied identity before router traffic. No adjacent-project router password was reused.

## Bounded device observations

| Test | Observed result | Meaning |
| --- | --- | --- |
| Initial TCP/22 and TCP/23 banner reads | Accepted, immediate EOF | No banner, authentication or shell established |
| Send SSH identification / Telnet initial negotiation | EOF after approximately 1 ms on each | Client-first protocol bytes did not open sessions |
| HTTP `/` | 200 JavaScript redirect to `/index.html` | Native front page identified |
| HTTP `/padrao`, before support login | 200 login form | Advanced login exists on this build |
| HTTP `/saveconf.htm`, before login | 200 JavaScript redirect to `/login.htm` | No export available at that stage |
| HTTP `/index.html` and `/login.htm` | Native pages returned | Normal UI and authentication flow identified |
| HTTPS `/login.htm`, default Python TLS client | `SSLV3_ALERT_HANDSHAKE_FAILURE` | TLS compatibility/access unresolved; no daemon identification |
| HTTP `/about-power-box_vd.html` | 200; model/build/revision match owner | Target identity independently confirmed |
| Native shared JavaScript | No login/password/SSH/Telnet references | No further authentication/service lead there |
| Authenticated `/idx_select.htm` | 404 | Not a usable document on this build despite its appearance in a form field name |
| Authenticated `/index.htm` | Advanced interface, Wi-Fi-only menu asset | Support web access established |
| Authenticated `/saveconf.htm` | Native Backup/Restore Settings page | Original settings export available |
| Authenticated `/status.htm` | Native DSL Router Status page | Additional native status access; no OS shell |
| `/rmtacc.htm` | 404 | One Realtek-family filename hypothesis rejected |
| Full-menu filename derived from Wi-Fi menu asset | 404 | One asset-name hypothesis rejected; do not repeat filename probing without a new lead |

The HTTP server header is `Virtual Web 0.9`. The login form posts MD5 fields `usernameEncrypt` and `passwordEncrypt` to `login.cgi`, with `loginW=0`. `loginfrompadrao=1` selects the advanced flow; normal `/login.htm` uses `0`. Asset names contain `BR_SO_RTK_V6.1.8t_Feb_20_2017_19_16_25`; this is not independent proof of the running build date.

## Authentication results

The owner explicitly supplied the stock admin credentials. No router password was present in the reviewed initialization documents. An earlier private-file clarification was resolved before any credential submission.

1. `admin` through `/padrao` returned `username/password incorrect`.
2. The same supplied `admin` credentials through normal `/login.htm` succeeded, redirecting to `index.html`; a protected settings page then loaded.
3. One attempt with the exact-model source's documented `support` account and the owner's same device-label admin password succeeded through `/padrao`, redirecting to `index.htm`.

These are web administrator/support sessions. No cookie was returned; subsequent requests from the same laptop remained authorized. The precise session-binding implementation was not established. No password list was used.

## Original settings export

The authenticated native page labels `form2saveConf.cgi` as Save Settings File. Submitted exactly its `submit.htm?saveconf.htm=Save...` field, without submitting the separate restore/upload form. Response: HTTP 200, `application/octet-stream`, attachment `config.img`.

The retained original is 205061 bytes of XML-like configuration beginning `<Config_Information_File_8671>`. It is a settings backup, not a firmware/flash backup.

| Setting | Exported value |
| --- | --- |
| `ENABLE_ADVANCE_PAGE` | `0x0` |
| `PADRAO_WIFI_ONLY` | `0x1` |
| `TELNET_STATE` | `0x0` |
| `TELNET_PORT` | `0x17` |
| `SSH_STATE` | `0x0` |

The first two flags agree with the restricted menu. The service flags are consistent with disabled service access, but their runtime mapping has not been confirmed from native controls or matching source. They were not changed. The export contains a separate `SSH2AUTH_PWD` account entry, so web credentials must not automatically be treated as SSH credentials.

## Prepared change — not applied

The [exact-model TripleOxygen source](https://www.tripleoxygen.net/wiki/modem/rtv9015vw) describes changing the following settings and importing the result, then rebooting, to expose advanced configuration:

```diff
-<V N="ENABLE_ADVANCE_PAGE" V="0x0"/>
+<V N="ENABLE_ADVANCE_PAGE" V="0x1"/>
-<V N="PADRAO_WIFI_ONLY" V="0x1"/>
+<V N="PADRAO_WIFI_ONLY" V="0x0"/>
```

Prepared `.local/askey-net-001/config-advanced-menu.img` from the actual original export. Verified identical size and exactly two differing bytes, corresponding only to these two flag values. No SSH/Telnet flag was edited. No upload or reboot has occurred. Exposing the menu does not guarantee OS shell access.

Before application, AGENTS.md requires an explicit instruction for the actual persistent operation and an understood rollback/recovery plan. The proposed operation is native settings import followed by a router reboot as required by that workflow. It will interrupt the lab router temporarily; laptop Wi-Fi carries the control connection independently.

Rollback while management remains available: log in with the known support account, restore the retained original `config.img` through the same native restore flow and reboot as required. If management does not return, stop remote probing; recovery may require the owner to perform an explicitly authorized physical factory reset, then restore the original export. There is no full flash backup, and no firmware/bootloader write is proposed.

The next decision is whether to apply this prepared menu change. If approved, inspect the resulting native service controls and their current values before proposing any service activation. Genuine OS shell output remains the success criterion, followed by native program execution.

## Retained artifact hashes

Raw captures, credentials and configuration contents remain in ignored `.local/`. The following SHA-256 values were computed from actual retained files.

| Artifact | SHA-256 |
| --- | --- |
| `.local/askey-net-001/about-and-share.json` | `9ecc2623119c0c24eebdab7831bdcb8b05c6208b232715a6bdcee2e22a33dddf` |
| `.local/askey-net-001/admin-login.json` | `e54d5a7ed7364b0d4987398b15c256495daf9035b128541d59bc506843f569d7` |
| `.local/askey-net-001/admin-normal-login.json` | `862afc86c0ce9c6113db3e6c2c5ade937881323eeb533c702db4125a44357852` |
| `.local/askey-net-001/advanced-index-and-saveconf.json` | `1fad25d951a2ae1cbe720cb94fde402c33af484af52df54e75893b854b6a2b97` |
| `.local/askey-net-001/advanced-menu-change.json` | `f58338434fe82f136bd22aaaf97e9f74fd3a550bed96a0a10f603f1436c4308b` |
| `.local/askey-net-001/advanced-menu-scripts.json` | `c061d034507f3931a2f79130ce05f611b9810b5b6878bc7fc20c44ac65bf5c0a` |
| `.local/askey-net-001/after-admin-login.json` | `ed05c3b82d1650092bd8fb8181638ac76ecee869a36f49ba4db529d3753d5700` |
| `.local/askey-net-001/configuration-export-response.json` | `1ca2d9e25b3d6c57b0c64a3e1d4a868d61b9030f44c941c11b7425753da1aabf` |
| `.local/askey-net-001/full-menu-candidate.json` | `5de9cacec59249b37ae4b52cf95fdae48c7c6ab70e5c4c9a67aefa3b6d0f1afd` |
| `.local/askey-net-001/normal-web-auth-check.json` | `4d3263c00de430bd1fbf0f41cbfbfa35577d63af6fc104ae7a665db163b295b9` |
| `.local/askey-net-001/protocol-and-login-pages.json` | `a586a313b963f8fe1f1743893bd2f5d2393ff4aacca8685cccfc8ade80e75fb8` |
| `.local/askey-net-001/service-page-check.json` | `05115746b385a9b792bcf874f52d32986362396e54c0355d9007cceda7ed2075` |
| `.local/askey-net-001/support-login.json` | `2bf0223779dc5b6ae78e645513b37af5a0e021320c306e385e8e0535edecdc18` |
| `.local/askey-net-001/unauth-recon.json` | `2b314a009fad728189f8885d91af44de1af35499b74da1634f64aa20b127cde7` |
| `.local/askey-net-001/config.img` | `f4f03b82fc9d927618e17241889e3fee6c990b77648c777cc5ec3c8d21ef42df` |
| `.local/askey-net-001/config-advanced-menu.img` | `ae361192895261a4ed2f89655199be2ea844626a851155720c3fffdbbfadaf65` |
| `.local/research/rtv9015vw.html` | `1c0ad0d45e96456d062460a6c6300490a6805a514c550ae0e2d9a327c81c68e5` |

The exact-model primary source was fetched again on this date. Its older-firmware web procedure is an external lead, now supported by matching local flags and working support/export pages. It does not establish a shell recipe for this build. Its hardware claims remain other-unit evidence. The search tool failed with HTTP 405 before returning results; direct primary-source retrieval succeeded.

No settings changes, service activation, restore, reset, firmware write, hardware connection, OS shell or native execution occurred during these tests.
