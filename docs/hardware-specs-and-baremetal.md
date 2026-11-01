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
