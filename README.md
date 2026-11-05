# Mero Askey — RTV9015VW

Investigation of the owner's Askey RTV9015VW. Goal: a genuine OS shell and a reproducible program of our own running natively. Vendor menus, browser JavaScript and a custom web UI do not satisfy that goal.

## Major Milestone — 2026-10-31: Genuine Native MIPS32 Execution Proven (ASKEY-NET-010)

Genuine native MIPS32 code execution on the Askey RTV9015VW has been demonstrated and verified live on-target:
- **Verified Calling Contract:** Executed position-independent MIPS32 assembly payload conforming to the firmware's resident `webdll` two-call lifecycle contract (`f(magic, iface) -> next_fn; next_fn(magic, iface)`).
- **Physical DRAM Placement:** Owned RAM allocated dynamically via `xfile create` without touching baseline files.
- **Uncached KSEG1 Execution:** Staged and executed in uncached KSEG1 (`0xa0...`), completely bypassing L1 instruction/data cache hazards.
- **Independent Verification:** A separate, fresh Telnet session verified all 10 target fields (nonces, captured kernel arguments, `"ENTR"`, `"CLNP"`, and `"SUCC"` confirmation) in the allocated RAM mailbox via `memory show`.
- **Clean Release:** Allocation released cleanly; original 5-file filesystem inventory restored (`held=false`).
- Full report and hashes: [ASKEY-NET-010](docs/experiments/askey-net-010.md).
- Automated test harness: [`tools/run_native_trial.py`](tools/run_native_trial.py).

## System Specifications Measured on Silicon — 2026-11-01

Direct memory-mapped I/O (MMIO) register reads confirmed the exact hardware specifications:
- **SoC Processor:** Realtek RTL8672 / RTL8671x (RLX5181/RLX5281 MIPS32r2 + MIPS16e core, Big-Endian). MMIO `0xb8000000 = 0x00016405`.
- **Clock Frequencies:** System bus clock `100,100,100` Hz (100.1 MHz). PLL multiplier register `0xb8000024 = 0x03210321` (3x multiplier) yielding an effective CPU core frequency of **~300 MHz**.
- **Physical RAM:** **64 MiB** DDR2 SDRAM (`0xb8001000 = 0x10201de0`, boundary `0xb8001204 = 0x03e00000`). Divided into 32 MiB primary RTOS heap and 32 MiB high DSP/packet memory pool.
- **Flash ROM:** **8 MiB** SPI NOR flash (`0xb4000000`–`0xb4800000`).
- Documented lesson & specs: [Hardware Specs & Bare-Metal Programming Lesson](docs/hardware-specs-and-baremetal.md) and [`tools/probe_hardware_specs.py`](tools/probe_hardware_specs.py).

## Next Phase: Interactive I/O, Memory Scaling & Lab Topology

**Private telephony milestone — 2026-11-04:** The MOTO700/Askey line is registered to the self-hosted PBX as extension `10`. The owner confirmed incoming ringing, hello-world audio and hearing a six-second microphone recording played back. [ASKEY-VOICE-001](docs/experiments/askey-voice-001.md) records the live setup, errors/fixes and private evidence. DTMF menus, agent links and network actions are the next experiments.

**Keypad command menu verified:** [ASKEY-VOICE-002](docs/experiments/askey-voice-002.md) demonstrates in-call digit reception and a spoken menu with a fixed bounded Askey network connection check (`2`) and hang-up (`0`), both owner-confirmed. Agent bridges and phone-originated short-code forwarding remain next steps.

**Implementation map and current operation:** [How the telephone lab works](docs/telephony-implementation-map.md) explains PBX/process lifetime, startup behavior, source files/languages, call logic, the local neural female voice and the revised idle behavior. The owner has now confirmed direct handset dialing of `20`.

**Desktop command center:** Menu `3` now enables cinema specifically on the Sony Bravia, independent of cursor/focus, and `4` restores screens; both are owner-verified. [ASKEY-VOICE-003](docs/experiments/askey-voice-003.md) and the [CLI/configuration/secrets guide](docs/phone-command-center.md) explain the separate host-side command worker and how to extend it. PBX restart policy is `unless-stopped`.

- [**Telephone operations quick reference**](docs/telephony-operations.md): Asterisk CLI, container Linux shell, menu/prompt/worker updates, start/stop/rebuild and private evidence operations.
- [**Telephone expansion and ideas**](docs/telephone-expansion-and-ideas.md): Rotary compatibility, two phones sharing one line versus independent extensions, and a brainstorm of useful next experiments.

The project is transitioning from a minimal execution proof to building interactive home lab tools:
- [**Network Migration & DHCP Deactivation (ASKEY-NET-011)**](docs/experiments/askey-net-011.md): Migrated LAN IP to static `192.168.1.250` and permanently disabled DHCP server daemon to enable direct unmanaged switch connection from `mero-machine`.
- [**Master Guide to Next Implementations & Lab Topology**](docs/guide-next-implementations.md): Complete guide to direct `mero-machine` connection, switch safety/DHCP risks, hard reset recovery, and interactive architectures.
- [**Hardware Specs & Phone Port Analysis**](docs/hardware-specs-and-baremetal.md): Low-level memory architecture, MMIO registers, and physical RJ11 Phone (FXS) port analysis (-48V DC, 90V AC ring generation, Realtek VoIP/DTMF subsystem).
- [**Motorola MOTO700 Telephony Pilot Handoff**](docs/telephony-moto700-pilot-handoff.md): Working private PBX registration and incoming audio tests, handset documentation, and remaining DTMF/voice-agent experiments.
- [**Telephony, Voice AI & Home Lab Automation Guide**](docs/telephony-and-voice-automation.md): Complete guide to using the Askey FXS phone port for local room intercoms, phoning an AI agent (Whisper/LLM/TTS over SIP), DTMF keypad automation, and physical alert ringing.
- [**Telephone interface and dial-code lab**](docs/telephony-dial-code-lab.md): Current phone observations, proposed extensions, voice-agent links and fixed network-action codes; [live read-only audit](docs/experiments/askey-voice-001.md).
- [**Future private DSL copper lab**](docs/dsl-copper-lab.md): Complementary modem roles, required peer equipment, link measurements and private network experiments over a copper pair.
- [**Next Experiments Roadmap**](docs/next_experiments.md): Memory scaling to megabytes (`sys_mem_alloc` at `0x80011b74`), the 3 two-way I/O architectures (TCP socket bind shell, shared-memory ring buffer, Telnet CLI hooking), and practical home lab utility concepts (micro-iperf server, hardware packet tap).


## Firmware Milestone — 2026-10-27

The complete 8 MiB flash map and complete running image are captured, verified and saved in [firmware/](firmware/README.md), as explicitly requested by the owner.

| Artifact | Size | SHA-256 |
| :--- | :--- | :--- |
| [Full flash](firmware/rtv9015vw-br_so_rtk_v6.1.8t-fullflash.bin) | 8388608 bytes | `e5c171d08d5c3131cd7b8a4c7180e3ac277408c8072b96e335495f3b68e1fc2f` |
| [Running image](firmware/rtv9015vw-br_so_rtk_v6.1.8t-run-image.bin) | 2954688 bytes | `74ff08b030051cce67e4c637cbb46d7cc7dfd629e04271a9fb83ebab3cc76ad6` |

Verification covers 8192 contiguous chunks, raw-response reassembly, independent calibration/header captures, eight hardware readbacks, image checksum/decompression and settings-container checks.

## Established Access and Runtime

- Model RTV9015VW, hardware UI revision `Rev:01`, firmware `BR_SO_RTK_V6.1.8t`, build `Feb 20 2017 19:16:25`, SDK `V1.2.1`, firmware family string `8671x`.
- Admin Telnet reaches privileged **`XDSL#`** prompt, exposing `webdll`, `loaddll`, `chksum`, and `xfile`.
- Monolithic Realtek OSK RTOS runtime with kernel-privilege execution and unmapped flat memory access.

## Read Next

- [Master Guide to Next Implementations](docs/guide-next-implementations.md): Direct connection methods, switch DHCP risk mitigation, and interactive I/O options.
- [Next Experiments Roadmap](docs/next_experiments.md): Multi-megabyte memory scaling, TCP socket listener, ring buffer, and home lab utility concepts.
- [Hardware Specs & Bare-Metal Lesson](docs/hardware-specs-and-baremetal.md): Low-level memory architecture, MMIO registers, and measured hardware specifications.
- [Handoff](HANDOFF.md): Authoritative state, operator constraints, and next research questions.
- [Verified specifications](docs/device-specs.md) and [manual Telnet guide](docs/telnet.md).
- [Native execution proof (ASKEY-NET-010)](docs/experiments/askey-net-010.md): Complete on-target execution log and evidence hashes.
- [Full capture record](docs/experiments/askey-net-006.md) and [artifact manifest](firmware/manifest.json).

The full-flash artifact is retained unredacted per the owner's explicit instruction. Other raw sessions, passwords, settings exports and intermediate analysis stay in ignored `.local/`. See [AGENTS.md](AGENTS.md) before further work.
