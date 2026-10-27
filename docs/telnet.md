# Test Telnet from the Mint laptop

Open a local terminal on `cris-MS-1454`, outside the SSH session to mero-machine. The router is directly reachable through laptop Ethernet; mero-machine has no direct lab route.

```sh
telnet 192.168.15.1
```

Log in as `admin` with the owner's label password. Password typing is normally invisible. The initial `$` is a vendor CLI prompt.

At `$`:

```text
show status
sh
```

The second command enters `XDSL>`. These read-only commands were verified on this device:

```text
show version
show system memory
show system task
show system flashlayout
```

`show system memory` reports a memory pool, not installed RAM capacity. `sh` has not produced a POSIX shell: both `id` and `uname -a` are rejected inside `XDSL>` as well as the earlier outer-parser test.

To leave: `quit` returns from `XDSL>` to `$`; `exit` logs out to the username prompt. Then press Ctrl+] and enter `quit` at `telnet>` to close the connection. Logging out alone leaves the TCP session open.

No new scan or settings change is needed to repeat these read-only observations. See [device specs](device-specs.md) and [ASKEY-NET-005](experiments/askey-net-005.md) for the flash-read lead. Avoid the `memory set`, reboot and configuration operations while exploring these status commands.
