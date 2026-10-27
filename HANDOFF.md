# Askey handoff — next target for genuine shell access

Prepared **2026-10-26, America/Sao_Paulo**. Target: Zac's **Askey RTV9015VW** Vivo router. Repository: `zacmero/mero-askey`, branch `main`.

## Current session — 2026-10-27: firmware milestone complete

**All device-side work for today is finished. The owner asked to turn the Askey off; it is safe to do so. No capture, verification, write or upgrade operation is still running. Actual power-off was not observed by the agent.**

Read [firmware manifest](firmware/manifest.json), [ASKEY-NET-006](docs/experiments/askey-net-006.md), and [consolidated analysis](research/firmware-analysis.md). Earlier initialization-only statements below are historical.

### Saved artifacts and verification

- `firmware/rtv9015vw-br_so_rtk_v6.1.8t-fullflash.bin`:8388608 bytes, SHA-256 `e5c171d08d5c3131cd7b8a4c7180e3ac277408c8072b96e335495f3b68e1fc2f`.
- `firmware/rtv9015vw-br_so_rtk_v6.1.8t-run-image.bin`:2954688 bytes, SHA-256 `74ff08b030051cce67e4c637cbb46d7cc7dfd629e04271a9fb83ebab3cc76ad6`.
- Final firmware is in the repository per explicit owner instruction, including unredacted settings in the full snapshot. All other raw/private evidence remains `.local/`.
- Strict contiguous 8192-chunk capture, complete wire-log reconstruction, two matching 16 KiB calibration reads, independent 64-byte header and eight matching 1 KiB hardware readbacks. Image checksum/decompression and all settings containers validate.
- Service `mero-askey-firmware-capture.service` finished with Result=success, ExecMainStatus=0, NRestarts=0, with clean logout. It had an independent systemd parent and pre-existing Linger=yes. Checkpoint `.local/askey-net-006/fullflash-pass1.bin.json` is complete=true. No duplicate/resume read is needed.
- Capture took 5477.4 seconds, across a verified clean handoff at 4215808 bytes. Private raw source and logs remain under `.local/askey-net-006/`.

### Actual device and access state

- RTV9015VW, Rev:01, BR_SO_RTK_V6.1.8t, build Feb 20 2017 19:16:25, SDK V1.2.1, family 8671x. Exact physical SoC/clock/RAM unverified; memory-pool total is not physical RAM.
- Direct laptop path was `cris@192.168.1.80`, existing `/home/zacmero/.ssh/mero_stb_isolated_lab` key, strict host checking. Ethernet enp6s0/192.168.15.3 reached the verified Askey at 192.168.15.1. Wi-Fi preserved control; mero-machine itself had no direct lab route. Re-identify route/neighbor at the next powered-on session; do not assume DHCP/interface state persists.
- Known owner password remains `.local/router-login.json`. Normal admin web uses loginfrompadrao=0; advanced support uses 1 with the same label password. No credential guessing.
- Only explicitly approved persistent edits were ENABLE_ADVANCE_PAGE=1, PADRAO_WIFI_ONLY=0 and TELNET_STATE=1. SSH/account priorities/ACL/WAN settings were not changed. Telnet remains enabled in saved configuration as requested.
- Telnet `$` and `XDSL>` are vendor consoles. sh/quit navigation does not establish a POSIX shell; id/uname rejected. No custom native binary has executed.
- OSK and mixed big-endian MIPS32/MIPS16 are proven from the captured runtime. Decoded runtime is 9752040 bytes, hash `b104789b795630eee7de1b50d64e49710535221f8baa6652021af6d00abb3941`.

### Analysis and open paths

Three offline agents produced [CLI](research/firmware-cli-analysis.md), [runtime](research/firmware-runtime-analysis.md) and [image/web/recovery](research/firmware-image-analysis.md) reports. All work was offline; no agent contacted the device.

- ENABLE_ADVANCE_PAGE is a broader access mode and is rendered as ServiceMode. Modes 0/1 can remove CLI privilege; mode 2 selects admin menu and preserves account-derived bits at that gate. PRIORITY 2 retains only the weaker bit when not stripped; stronger native nodes require the bit assigned by PRIORITY 1. These are static conclusions, not applied changes or a shell demonstration.
- Memory display is locally proven. Compiled memory store paths exist without the mapped CLI capability bits, but no live write target/rollback or safe native execution test has been established. Do not invent one from a help label.
- Native callbacks have strict contracts: webdll calls an address and then its returned callback; loaddll copies a header-described body; chksum is not a loader. Allocation, lifetime, cache and ABI guarantees remain incomplete.
- Entire backup-image slot 0x400000..0x7e0000 is erased. Runtime recovery code prefers valid primary and can clear backup; erasure alone is not a defect. No working restoration is demonstrated.
- Current/backup settings are identical, checksum-valid and canonically match the approved export; decoded values stay private. Raw full-flash capture is not an approved web-upgrade image.
- **The live CLI session-object/capability-field avenue remains OPEN.** Owner explicitly rejected discarding it after one automated optional follow-up was blocked. Preserve [open research leads](research/open-research-leads.md), existing evidence and missing ownership/lifetime questions for later work. That tool event is not a technical rejection of the path.

No additional device action is authorized merely by these static findings. Finish today with repository reporting/commit/push, as explicitly requested. Next live work needs a concrete question and the existing operation-specific rules; no guessed credentials, settings, ABI, pinout or recovery procedure.

## 1. Mission and owner constraints

Get an actual operating-system shell and then prove native code execution. Prioritize a bounded **Ethernet/software-only investigation using the equipment already present**. The owner wants practical progress toward shell access, not another custom browser interface or repeated unproductive multimeter instructions.

This request initializes documentation only. **No Askey connection, scan, login, firmware change or UART capture has yet been performed in this project.** Proceed with the hands-on investigation when the owner resumes it; do not report the planned steps below as completed.

Keep explanations short and grounded in one concrete step/result at a time. Do not ask the owner to reconfirm information already given. Do not promise root access from a web page, an open SSH port, a related-model tutorial, or the number of header pins.

## 2. Known device and host information

- Earlier owner-label photographs identify **RTV9015VW**, manufacture **12/2018**, supply **12 V DC / 1 A**. Before powering, use the matching adapter and verify connector/polarity. Do not interchange it with the 9 V Intelbras supply.
- The owner is currently on a **Linux Mint laptop**. Use `apt` if a needed package is absent. Do not use Arch's `pacman` here or assume the laptop has `rtk`.
- Current network interface names, addresses, routes, router MAC, firmware build, administrator login and management-service policy are **not yet inventoried for this Askey**.
- External research suggests default management `192.168.15.1`, with older-firmware `/padrao` and `/saveconf.htm` routes. These are candidates, not observed endpoints on our unit. See [sources](research/sources.md).
- Hardware claims such as the Realtek chipset, flash model and serial support come from another RTV9015VW. Do not carry them into the confirmed local inventory until supported by our board/runtime evidence.

## 3. Why we are switching from MitraStar

The MitraStar's [2026-10-26 session](https://github.com/zacmero/mero-mitrastar/blob/master/docs/experiments/mitra-hardware-020.md) established:

- CH341A MiniProgrammer works over USB in programmer mode (`1a86:5512`) and serial mode (`1a86:5523`, `/dev/ttyUSB0`). This proves interface enumeration, not target voltage safety or successful memory access.
- Unloaded measurements included 3.31 V at the 3.3 V rail, 5.03 V at the 5 V rail, and approximately 5 V at the reported data contacts. Do not connect it directly to 3.3 V targets.
- The SOIC8 clip cannot physically seat around that router's crowded flash. A nearby header and another component block it. Do not assume it will fit this Askey either.
- MitraStar header readings, farthest populated pin toward flash: **0 / 3.2 / 3.3 / 3.3 V**; farthest pin had ground continuity. The remaining TX/RX/VCC functions are not assigned, and no serial boot log exists.
- The ESP32 is ordered but has **not arrived**. The owner has **no female–female Dupont leads and no soldering equipment**. The supplied SOIC8 ribbon is not a general set of jumpers.
- The [MitraStar buying list](https://github.com/zacmero/mero-mitrastar/blob/master/BUYING-LIST.md) and Todoist task cover the missing leads. No soldering-station purchase or CH341A modification is scheduled as a prerequisite to this project.

These are MitraStar/programmer observations, **not Askey measurements**. Leave the CH341A disconnected from this target. Do not repeat the earlier probe sequence just because it appears in old chat logs.

## 4. ASKEY-NET-001 — planned first experiment

### A. Identify the direct network path before traffic

Use one router at a time. Disconnect the MitraStar from the lab Ethernet segment; both Vivo routers can use the same default IP. Connect the laptop directly to an Askey LAN port and leave Askey DSL/WAN disconnected. Do not bridge Wi-Fi and Ethernet, start DHCP/DNS impersonation, or alter the household router.

On Mint, inspect the host first:

```sh
ip -br link
ip -br -4 addr
ip -4 route
ip neigh
```

Record the cable-facing interface and its IPv4 address. Preserve a separate Wi-Fi/control route if in use. Determine the Askey address from the direct connection/lease rather than assuming the default. Check `ip route get <confirmed-router-ip>` and neighbor identity before scanning. If there is no usable lease, diagnose the link before proposing one explicit, reversible connection-profile change; do not blindly assign old MitraStar addresses.

### B. Small, bounded management-service check

Only after verifying the target and cable-facing path, check the relevant TCP ports rather than immediately repeating the 65,535-port MitraStar scan. Install `nmap` only if absent:

```sh
sudo apt install nmap
```

Template — replace `CONFIRMED_ASKEY_IP`; do not paste a household gateway by guess:

```sh
nmap -n -Pn -sT --max-retries 1 --host-timeout 45s \
  -p 21,22,23,80,443,2323,8080 CONFIRMED_ASKEY_IP
```

Run no NSE/exploit scripts, password guessing, subnet scan or stress test. Record open/refused/timeout distinctly. A timeout does not prove that a daemon is absent.

### C. Inspect the real management interface

Open the verified device's root web page and record the firmware/build and visible maintenance controls. If the address is indeed `192.168.15.1`, the external candidates are:

```text
http://192.168.15.1/padrao
http://192.168.15.1/saveconf.htm
```

The original exact-model research describes `support` with the device's own label administrator password on older firmware. Use only the owner's intended credentials; never copy the MitraStar password, print secrets, or try password lists. If an interface appears Wi-Fi-only, record that constraint; a change of access path can be considered without assuming the page does not exist.

Inspect before applying. A configuration export, if available through its native flow, belongs in ignored `.local/`, with only a reviewed summary/hash committed. It is **not** a bootloader/kernel/root-filesystem backup. If the page is absent on this build, record the response and stop repeating the same URL.

### D. Choose the next step from evidence

| Observation | Next useful action | Do not infer |
| --- | --- | --- |
| SSH/Telnet open | Owner-credential login; classify resulting prompt and access | Open port means root shell |
| Native LAN management-service controls visible | Document exact current values, LAN-only restriction and rollback; obtain an explicit instruction before enabling | All hidden services should be enabled |
| Export available | Analyze actual config structure offline; preserve original | Export can be flashed as complete firmware |
| No usable management route | Narrow exact-build firmware/source research based on captured identity | Another model's image will work |
| Genuine OS shell | Bounded inventory below, then ABI/transfer assessment | Root privileges or binary compatibility without testing |

Once a genuine shell exists, use a small read-only inventory such as:

```sh
id
uname -a
cat /proc/cpuinfo
cat /proc/mtd
mount
```

Then inspect available transfer tools, writable/executable temporary storage and ELF ABI before compiling a tiny marker program. Vendor CLI help may be inspected when appropriate, but rejection of `id` must be recorded as a CLI limitation, not shell success. Do not flood the console with guessed commands.

## 5. Persistence and hardware boundaries

Native service activation, configuration restore, resets, firmware upgrades, bootloader changes and physical flash writes require a concrete operation and explicit owner instruction. This document is not authorization to run them automatically. Record an understood rollback before a settings change.

The old Askey tutorial's edited `config.img` import/reboot is **not** the first step. Newer firmware may remove those pages; neither applicability nor shell access is established here. Never flash a MitraStar, sibling Askey or internet dump based on a similar enclosure.

Hardware is a later branch only if software evidence justifies it. We have no measured Askey UART pinout, logic level, clip clearance or flash power arrangement. Do not attach the known approximately 5 V CH341A, assume ESP32 availability, or short pins to force recovery.

## 6. Recording results and avoiding repeated work

Create `docs/experiments/askey-net-001.md` after the first actual session. Include the date/timezone, device/build, confirmed host route, commands, bounded output, positive and negative observations, limitations and one next decision. Store raw credentials, exports, traffic, firmware and serial logs under ignored `.local/`; never claim hashes for artifacts that were not retained.

Prior MitraStar measurements and older GVT tests are references, not fresh Askey evidence. GVT [mero-stb-lab](https://github.com/zacmero/mero-stb-lab) has already demonstrated Ekioh application execution, but the owner rejected more UI-only work as the next goal. Preserve it without redirecting this session back into UI polishing.

**Success criterion:** captured output from a genuine device OS shell, followed by a reproducible native-program milestone. Until then, label the exact intermediate achievement honestly.
