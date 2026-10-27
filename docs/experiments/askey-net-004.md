# ASKEY-NET-004 — Telnet console classification and system inventory

Date: 2026-10-27, UTC−03:00. Result: working vendor CLI and live system specifications; genuine OS shell and arbitrary native execution not established.

## Connection and authentication

Following the owner-authorized Telnet activation in [ASKEY-NET-003](askey-net-003.md), connected from the verified Ethernet laptop to `192.168.15.1:23`. The service now presents `User Access Verification`, accepts the owner's admin credentials, and displays `$`. This is a measured change from the earlier immediate EOF.

Raw terminal transcript was captured on mero-machine in ignored `.local/askey-net-003/telnet-session.typescript`; it was finalized and restricted to mode 0600 after logout/disconnection. SHA-256 `ebf9a206fd368d425d92b136848a9c7bf3accc6f497a06c19093e800165a2729`.

## Prompt classification

1. `id` at `$` is rejected by a vendor parser listing `config`, `debug`, `diagnostic`, `exit`, `reboot`, `sh`, and `show`.
2. The advertised `sh` enters `XDSL>`. Its help/error output lists vendor operations, including `show` and `quit` described as going to shell.
3. `quit` returns to `$`; `id` is still rejected there. Neither transition established a POSIX shell.
4. Outer `show status` succeeds. `diagnostic ?` returns `cmd "diagnostic" ERROR: Invalid privilege.`
5. Advertised outer `debug` returns without visible output. No claim is made about an unobservable volatile effect. A final settings export exactly matches the authorized candidate, ruling out a persistent exported-setting change from this exploration.
6. Re-entered `XDSL>` and inspected its advertised read-only `show` tree. Captured `show version`, `show system memory`, `show system task`, `show system flashlayout`, `show system status`, and `show twsfversion`.
7. After returning to `$`, `config ?` also returns `Invalid privilege`. No guessed credential, privilege value, memory-write, diagnostic execution or configuration command was submitted.
8. `exit` logged out to the authentication prompt; disconnected using the Telnet client's escape/quit, then the SSH transport closed.

The related Beetel report's `sh` terminology therefore cannot be treated as proof of Linux shell access on this Askey. We reproduced terminal access and two vendor console levels, not a Linux `id`/`uname` session.

## Device-reported specifications

See [verified device specifications](../device-specs.md) for the reviewed inventory and flash map. Main findings:

- Firmware `BR_SO_RTK_V6.1.8t`, build `Feb 20 2017 19:16:25`.
- SDK `V1.2.1`, firmware-reported hardware family `8671x`.
- Flash reports 8 MB, with run-image and backup-image addresses and separate settings regions.
- Hexadecimal memory-pool total `0x16b8010` = 23822352 bytes (22.719 MiB); this is not a measured physical RAM capacity.
- Live task table exposes task-control blocks, fixed stacks and network/management task names, consistent with an RTOS-style runtime. Exact OS and CPU/ABI remain unverified.
- All listed WAN interfaces remain down in native status output.

## Configuration and resulting state

A final native web settings export after CLI exploration is retained as `.local/askey-net-003/config-after-cli.img`: 205061 bytes, SHA-256 `721cc151716e65c733f6f37d3ca18525b1d901380ca990355ed774d9716ff1b9`, exactly equal to the explicitly authorized Telnet candidate. Response capture `.local/askey-net-003/post-cli-verification.json`, SHA-256 `be1fd6cbe0e64276d5a78a5705b6e0722633b7844b8b9e2c650792a5e5caf329`.

Thus the current persisted changes from the original baseline are the two approved menu flags and the approved Telnet flag. SSH, account privileges, ACL and WAN settings remain identical in the exported configuration. Telnet remains enabled per the owner's instruction. No rollback, factory reset, firmware/bootloader write, native binary upload or hardware connection occurred.

## OS identification evidence and next boundary

A [related V-SOL primary bootlog](https://www.tripleoxygen.net/wiki/ont/vsol/v2801q) identifies an OSK image and shows many of the same task names. This is related-platform evidence, not an exact firmware or kernel identification. Its retained HTML is `.local/research/v2801q-rtos-related.html`, SHA-256 `8280d5871dc2a775f21b8f6d2a91d3c779118b0c90a1ecb6a70c9aa86f02d3ee`.

A certification-mirror search lead labels this exact model as RTOS version v1.2.1, but the attempted original Wi-Fi Alliance certificate endpoint returned HTTP 401. The mirror is not used as primary proof of the running OS. No exact runtime firmware/source or native executable loader is available locally.

The next useful investigation is matching this task-based runtime/CLI to its actual SDK or firmware and establishing the privilege mapping or a documented native execution entry. Do not assume a Linux ELF will execute, change account priority values blindly, treat a reported backup slot as a verified recovery image, or write arbitrary memory to force execution. Current credentials deny the tested privileged diagnostic/configuration modes.
