# Low-Level Bare-Metal Programming & Hardware Specifications

Target: Askey RTV9015VW (`BR_SO_RTK_V6.1.8t`).
Orchestration tool: [`tools/probe_hardware_specs.py`](../tools/probe_hardware_specs.py).

---

## 1. How Do We Know the Actual Physical Device is Responding?

In low-level firmware engineering, we never assume a response came from the intended target without cryptographic and physical verification across three independent layers of the OSI model:

```
+-------------------------------------------------------------------------+
| Layer 2 (Data Link) : Physical Ethernet MAC Neighbor                     |
|                      Target: 54:2F:8A:48:1A:B8 (Askey Computer Corp OUI)|
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| Layer 3 (Network)   : Direct ICMP Ping (0.2 ms round trip)               |
|                      Target IP: 192.168.15.1 on dedicated cable enp6s0  |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| Layer 7 (Application): Cryptographic Running-Image Flash Header         |
|                      64 bytes at 0xb4010000 -> SHA-256: 19cef9e1...     |
+-------------------------------------------------------------------------+
```

1. **Layer 2 (Hardware Link):** The Linux kernel checks the ARP neighbor table on the laptop's dedicated Ethernet interface `enp6s0`. The MAC address `54:2F:8A:48:1A:B8` begins with `54:2F:8A`, the IEEE Organizationally Unique Identifier (OUI) assigned to Askey Computer Corp.
2. **Layer 3 (IP Latency):** Round-trip ICMP latency is ~0.20 ms, which is only physically possible over a direct copper patch cable (no Wi-Fi, switches, or cloud routing).
3. **Layer 7 (Cryptographic Identity):** Reading the first 64 bytes of the SPI flash running-image partition at `0xb4010000` produces the exact SHA-256 hash `19cef9e17ca1c90cda12fd579af2ddc18c80ae9528e89c32130d5a2e0e871348`, proving byte-exact identity with our baseline firmware capture.

---

## 2. What Does "Accessing the Bare Metal" Mean?

### Desktop OS vs. Embedded RTOS
On modern operating systems (Ubuntu, Windows, macOS):
- User programs run in **User Mode** using **Virtual Memory**.
- The Memory Management Unit (MMU) translates virtual addresses into physical addresses through page tables.
- If a C program tries to access a raw physical address (e.g. `*(volatile int*)0xb8000000 = 1`), the MMU blocks the bus access and the operating system raises a `SIGSEGV` ("Segmentation Fault").

On the Askey router:
- The CPU runs permanently in **MIPS Kernel Privilege Mode**.
- Virtual paging is disabled; the 32-bit address space is divided into architectural hardware segments:

| MIPS Segment | Address Range | Cache Policy | Description |
| :--- | :--- | :--- | :--- |
| **KUSEG** | `0x00000000`–`0x7FFFFFFF` | User/Mapped | Not used by this single-binary RTOS. |
| **KSEG0** | `0x80000000`–`0x9FFFFFFF` | **Cached** | Physical DRAM. Accesses go through L1 I-cache & D-cache. |
| **KSEG1** | `0xA0000000`–`0xBFFFFFFF` | **Uncached** | Physical Memory & Peripherals. Bypasses all CPU caches! |

$$\text{Physical Bus Address} = \text{Virtual Address} \ \& \ \text{0x1FFFFFFF}$$

---

## 3. What is Memory-Mapped I/O (MMIO)?

Hardware peripherals on the Realtek silicon die (the clock generator, DRAM controller, timers, UART serial controller, Ethernet MAC) are wired directly to physical memory addresses on the internal chip bus (AHB/APB).

When a MIPS instruction executes:
```assembly
lui   $a0, 0xb800         # $a0 = 0xb8000000 (KSEG1 uncached)
lw    $v0, 0($a0)         # Read 32-bit word from 0xb8000000
```
The CPU does **not** fetch data from DRAM chips. Instead, the chip's internal bus controller routes the request to the silicon registers of the System Controller. The bits returned represent the physical wiring and PLL multipliers on the silicon chip.

---

## 4. Recovered Hardware Specifications

By querying the hardware registers and bootloader memory structures via [`tools/probe_hardware_specs.py`](../tools/probe_hardware_specs.py), we recovered the full system specifications:

### A. Processor Core & SoC Architecture
- **CPU Core:** Realtek RLX5181 / RLX5281 MIPS processor core (MIPS32 Release 2 ISA with MIPS16e extensions, Big-Endian).
- **Silicon Chip ID (MMIO `0xb8000000`):** `0x00016405`.
  - Architecture Family: `0x0001` (Realtek RLX).
  - Silicon Model: `0x6405` (Realtek **RTL8672 / RTL8671x** SoC series).
- **Silicon Revision (MMIO `0xb8000004`):** `0x06405f00`.

### B. Clock & Bus Frequencies
- **System Bus Clock (Global `0x8055a87c`):** `100,100,100` Hz (**100.1 MHz**).
- **PLL Multiplier Register (MMIO `0xb8000024`):** `0x03210321`.
- **Effective CPU Core Frequency:** **~300.0 MHz** (3x PLL multiplier of the 100.1 MHz bus clock).

### C. Memory & Storage Specifications
- **Flash ROM:** **8 MiB** (8,388,608 bytes) SPI NOR Flash mapped at `0xb4000000`–`0xb4800000`. Dual-bank partition layout.
- **Physical DRAM (SDRAM):** **64 MiB** DDR2 SDRAM.
  - Memory timing register (`0xb8001000`): `0x10201de0`.
  - Memory boundary register (`0xb8001204`): `0x03e00000`.
  - Physical memory mask (`0x8094966c`): `0xffe00000` (indicates 32 MiB / 64 MiB physical mapping).
  - Memory distribution:
    - RTOS Heap: `0x80000000` through `0x82004df8` (32 MiB primary space).
    - DSP / Packet Acceleration Pool: `0xa8000000` through `0xa8008000` (extended high memory).

---

## 5. How to Run the Probe Tool

The probe tool is completely safe, read-only, idempotent, and produces formatted educational diagnostics:

```sh
python3 tools/probe_hardware_specs.py
```

---

## 6. The Telephone Connection (RJ11 FXS vs RJ11 DSL WAN vs RJ45 Ethernet)

The Askey RTV9015VW features physical phone jacks alongside its 4 yellow RJ45 Ethernet ports:
1. **DSL Port (RJ11, Gray):** WAN uplink for copper telephone lines carrying VDSL2 / ADSL2+ high-frequency carrier signals (up to 17 MHz / 30 MHz DMT modulation).
2. **Phone Port (RJ11, Green / "TEL 1"):** **FXS (Foreign eXchange Station)** analog station interface for standard analog telephone sets.

```
┌────────────────────────────────────────────────────────────────────────┐
│               PORT COMPARISON: ETHERNET vs. PHONE (FXS)                │
└────────────────────────────────────────────────────────────────────────┘

  RJ45 Ethernet (LAN 1–4)            RJ11 Phone (FXS / TEL 1)
  ───────────────────────            ────────────────────────
  • Connector: 8P8C (4 pairs)        • Connector: 6P2C (1 pair: Tip & Ring)
  • Signal: Digital differential     • Signal: Analog baseband audio (300–3400 Hz)
  • Level: ~1.0V to 2.5V logic       • Idle Voltage: -48V DC battery feed!
  • Isolation: Pulse transformers    • Ringing: 70–90V AC at 20–25 Hz!
  • Controller: RTL8672 MAC/Switch   • Controller: SLIC (Subscriber Line Circuit)
  • Stack: TCP/IP packet switching   • Stack: Realtek rtk_voip DSP / SIP client
```

### A. How FXS Differs Electrically & Architecturally

A standard Ethernet port carries low-voltage high-speed digital pulses isolated by magnetic transformers. It cannot deliver analog telephone power.

An analog telephone is a **current-loop circuit**:
1. **Battery Feed (-48V DC):** When the telephone is sitting on its cradle (on-hook), the Askey's internal power supply feeds **-48V DC** across the two copper wires (Tip and Ring).
2. **Loop Current & Hook Detection:** When someone picks up the handset (off-hook), the telephone's internal switch closes. A DC loop current of **20 mA to 30 mA** begins flowing. The router detects this current draw and triggers a hook event.
3. **High-Voltage Ring Generator (70V–90V AC):** To make the physical brass bell inside an analog telephone ring, -48V DC is not enough. The router's internal DC-to-DC boost inverter generates an **AC sinusoidal wave of ~70V to 90V AC at 20 Hz to 25 Hz**. (Touching bare copper wires during ringing delivers a noticeable shock).
4. **Hybrid 2-Wire to 4-Wire Separation:** In an RJ11 cable, both speaking and listening happen simultaneously across the **same single pair of wires** (full-duplex analog). The router's hybrid circuit separates incoming microphone audio from outgoing earphone audio.

### B. The Silicon Hardware: The SLIC (Subscriber Line Interface Circuit)

The Realtek RTL8672 SoC cannot drive -48V DC or 90V AC directly from its 3.3V / 1.8V silicon die.  
Instead, the motherboard pairs the SoC with a specialized mixed-signal high-voltage chip called a **SLIC** (e.g. Silicon Labs ProSLIC or Zarlink).

The SLIC chip performs all **BORSCHT** functions:
- **B**attery Feed: Supplies constant current / -48V DC.
- **O**vervoltage Protection: Clamps lightning surges and line faults.
- **R**inging Generation: Synthesizes the ~80V AC ringing burst.
- **S**upervision: Detects on-hook, off-hook, and hook-flash pulse dialing.
- **C**odec: Converts analog audio to 8 kHz digital PCM samples (G.711 A-law/$\mu$-law).
- **H**ybrid: Separates 2-wire bi-directional speech into 4-wire TX/RX.
- **T**esting: Performs loop resistance and capacitance testing.

### C. The Resident Firmware VoIP Subsystem (`rtk_voip`)

The firmware contains a complete Realtek VoIP DSP engine:
- **Driver / Tasks:** Driven by the `rtk_voip` kernel module and resident RTOS DSP tasks (`VOIP`, `IVR`).
- **DTMF Tone Detector:** Dedicated DSP hardware filters detect touch-tone keypresses (`0`–`9`, `*`, `#`) from telephone keypads.
- **Tone Synthesizer:** Can generate dial tones (350 Hz + 440 Hz), busy tones, and ringing tones.
- **SIP Client:** Resident Session Initiation Protocol (SIP) user agent in `/var/config` (`VOIP.PORT[0]`).

### D. Practical Home Lab Uses for the Phone Port

The FXS port turns the router into an **ATA (Analog Telephone Adapter)**. Practical home lab applications:

1. **Self-Hosted PBX Extension (Asterisk / FreePBX):**
   - Run Asterisk or FreePBX on `mero-machine` or a local server.
   - Configure the Askey's SIP client to register with Asterisk as extension `101`.
   - Plug any standard desk phone or cordless phone into the Askey. You now have a working landline extension on your local network.

2. **DTMF Tele-Operator / Physical Console Interface:**
   - Because the DSP detects keypad tones in real-time, you can program the router to act as an **Interactive Voice Response (IVR) controller**.
   - Example: Pick up the phone handset, press `*1` to hear network status, press `*2` to trigger a server backup, or press `*9` to reboot a lab machine.

3. **Physical Alert Ringer (Network Bell):**
   - The router can trigger the 80V AC ringer via software command.
   - You can connect an old mechanical telephone or bell to serve as an audible alert for critical system failures (e.g., server offline, critical alert, automated doorbell).

4. **Zero-Telco Room-to-Room Intercom:**
   - If two routers with FXS ports (or an ATA and an IP phone) exist on the LAN, direct IP dialing can connect them without needing an outside telephone provider or cloud service.

