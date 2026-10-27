# Verified device specifications — 2026-10-27

Target: owner's Askey RTV9015VW. These are live device reports obtained over the owner-authorized Telnet session, unless a row says otherwise. See [ASKEY-NET-004](experiments/askey-net-004.md) for command context and limits.

| Item | Verified report |
| --- | --- |
| Model/vendor | Askey RTV9015VW |
| Label/UI hardware revision | `Rev:01`, native About page |
| Firmware | `BR_SO_RTK_V6.1.8t` |
| Firmware build | `Feb 20 2017 19:16:25` |
| SDK | `SDK V1.2.1` |
| Firmware-reported hardware family | `8671x`; not a physical chip marking or exact CPU part identification |
| WLAN component string | `92ER-2013-10-29-r3070-20160309001` |
| Flash address range | `0xb4000000` to `0xb4800000`, reported `8MB` (8 MiB by address span) |
| Main/run image start | `0xb4010000` |
| Backup image address | `0xb4400000`, reported offset 4 MB; presence/integrity of backup contents not tested |
| Hardware settings | `0xb4005000` to `0xb4006000`, reported 4 KB |
| Current settings | `0xb47f0000` to `0xb4800000`, reported 64 KB |
| Backup settings | `0xb47e0000` to `0xb47f0000`, reported 64 KB |
| Flash file region | `0xb43f8000` to `0xb4400000`, reported 32 KB |
| Possible maximum firmware | 3997696 bytes, reported 3904 KB |
| Defined maximum firmware | 4063232 bytes, reported 3968 KB |

## Memory snapshot — not total physical RAM

`show system memory` reports hexadecimal pool counters:

| Counter | Raw hex | Bytes | MiB |
| --- | --- | --- | --- |
| Pool total size | `0x16b8010` | 23822352 | 22.719 |
| Pool free size | `0x105111c` | 17109276 | 16.317 |
| Pool used size | `0x666e88` | 6712968 | 6.402 |

These describe a memory pool at that instant. They do not establish total installed RAM, Linux `MemTotal`, or memory available to a future native program. Do not relabel the pool total as a RAM-chip capacity.

## Runtime and access

- Telnet is enabled by the explicitly authorized `TELNET_STATE=0x1` setting. Admin credentials work. The session was logged out and disconnected after testing; service remains enabled as requested.
- Initial `$` prompt is a vendor command parser. `id` is rejected. Its `sh` command enters a second `XDSL>` vendor console. `quit` returns to the outer parser, which still rejects `id`.
- `show system task` reports task-control blocks, fixed stacks and named tasks including `CFGTASK`, `CLITASK`, `GENTSK`, `XTCPIP`, `EWSTSK`, `Telnet`, `SSH`, `DHCP`, `NTP` and `IDLETSK`.
- This task/memory model is consistent with a proprietary RTOS. Captured firmware now directly identifies OSK and mixed big-endian MIPS32/MIPS16 code; the exact kernel revision remains unverified. A Linux/POSIX executable ABI has not been demonstrated.
- Outer `diagnostic ?` and `config ?` are denied with `Invalid privilege`. The current account cannot access those privileged modes through the tested entries.
- Native `show status` reports DSL unavailable and all listed WAN interfaces down. The router clock restarted at 2011; use workstation timestamps for this investigation.

## Still unknown

Exact CPU/SoC part and clock, installed RAM capacity/type, flash manufacturer/part, precise OS/kernel, executable ABI/loading mechanism, arbitrary OS command execution, and native-program execution. The external exact-model hardware report remains other-unit evidence for these unmeasured physical details.

Raw session: ignored `.local/askey-net-003/telnet-session.typescript`, SHA-256 `ebf9a206fd368d425d92b136848a9c7bf3accc6f497a06c19093e800165a2729`.

## Firmware milestone

Complete verified raw flash and running-image files are in [firmware/](../firmware/README.md). The complete snapshot shows an erased firmware backup slot, matching configuration copies and checksum-valid containers. No physical restoration has been tested. All device-side work for 2026-10-27 is finished; the owner may power the Askey off.
