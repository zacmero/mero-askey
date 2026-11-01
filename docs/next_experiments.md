# Next Experiments: Interactive I/O, Memory Scaling & Home Lab Utility

**Document Version:** 1.0  
**Date:** 2026-11-01  
**Target:** Askey RTV9015VW Gateway (`BR_SO_RTK_V6.1.8t`, Realtek RTL8672 / RLX5181 MIPS32 core, 64 MiB DRAM).

---

## 1. Context & Motivation

With Roadmap Steps 1–4 complete ([`docs/experiments/askey-net-010.md`](experiments/askey-net-010.md)), genuine bare-metal MIPS32 execution on the Askey RTV9015VW is fully established. We have proven that the CPU can execute position-independent machine code staged into physical DRAM, preserve kernel registers, capture arguments, update memory mailboxes, and return cleanly without crashing.

The goal now transitions from a **minimal execution proof** to **building interactive, scalable, and genuinely useful home lab tools**.

---

## 2. Memory Scaling: Taking the System Capacity to the Edge

In ASKEY-NET-010, our payload used only 576 bytes inside a 1,600-byte single-cluster buffer. However, the router possesses **64 MiB of physical DRAM**:
- Monolithic OSK runtime occupies `~9.7 MB` (`0x80000000`–`0x80950000`).
- The remaining tens of megabytes are dynamic heap, packet buffers, and unreserved physical memory.

### Methods to Scale Allocation to Megabytes

1. **Resident Kernel Allocator Invocation (`0x80011b74`):**
   - The resident RTOS memory allocator (`sys_mem_alloc` / `malloc`) resides at `0x80011b74`, and `free` resides at `0x80011b64`.
   - A native MIPS32 bootstrap can pass `$a0 = <size_in_bytes>` and receive a dynamically allocated pointer in `$v0`.
   - **Experiment Idea (Memory Stress Test):** Write an allocator probe that incrementally tests allocating 64 KiB, 256 KiB, 1 MiB, 4 MiB, and 16 MiB blocks, recording heap limits and verifying system stability.
2. **Direct Unmapped High-DRAM Staging:**
   - Physical DRAM extends up to `0x04000000` (64 MiB). High addresses in KSEG1 (`0xa2000000`–`0xa4000000`) can be reserved as scratchpad memory for large binaries, network capture buffers, or data stores.

---

## 3. The Three Two-Way Interactive I/O Architectures

To achieve full bidirectional communication (input via Ethernet cable, output via Wi-Fi, or vice-versa), three distinct architectures are available:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ARCHITECTURE OPTIONS                               │
└─────────────────────────────────────────────────────────────────────────────┘

  Option A: The TCP Bind Shell (Pure Network Socket)
  ──────────────────────────────────────────────────
  [ Client (Wi-Fi or Cable) ] ◄── TCP Socket (e.g. Port 9999) ──► [ Native Payload ]
  Connect via 'nc 192.168.15.1 9999'. Native code runs an RTOS background task
  with BSD sockets (xtcp/xudp/socket). Full real-time bidirectional stream.

  Option B: Shared-Memory Ring Buffer (Dual-Channel Mailbox)
  ─────────────────────────────────────────────────────────
  [ Cable Connection ] ──► memory set long ──► [ Input RAM Mailbox ]
                                                      │
                                             (Native Worker Loop)
                                                      │
  [ Wi-Fi Connection ] ◄── memory show ◄────── [ Output RAM Mailbox ]

  Option C: Telnet CLI Hooking (Native Command Injection)
  ───────────────────────────────────────────────────────
  [ Any Telnet Console ] ──► "exec <command>" ──► [ Resident Native Hook ]
  Native payload hooks the CLI token table (0x805435c4) to register a new
  console command that streams output directly to the existing Telnet terminal.
```

---

### Option A: The TCP Socket Server ("Bind Shell")

- **Concept:** Deploy a resident network listener that accepts TCP connections on a dedicated port (e.g., `9999`).
- **Mechanism:**
  - The firmware includes Realtek's resident TCP/IP stack (`xtcp`, `xudp`, `socket`) and POSIX thread support (`pthread_attr_init` at `0x804357ec`).
  - Native MIPS32 code initializes a socket, binds to `0.0.0.0:9999`, listens, and spawns a worker loop.
  - When a client connects via `nc 192.168.15.1 9999` (over Ethernet or Wi-Fi), the socket acts as standard `stdin`/`stdout`.
- **Advantages:**
  - Fully decoupled from the vendor CLI.
  - Zero polling overhead on the client; true real-time character streaming.
  - Can be accessed from any device on the LAN (phone, tablet, PC).
- **Home Lab Value:** High. Acts as a genuine, permanent remote management and diagnostic port.

---

### Option B: The Shared-Memory Ring Buffer (Dual-Channel Asynchronous Pipe)

- **Concept:** Carve out two distinct memory circular queues (ring buffers) inside an owned RAM allocation:
  - **Input Ring Buffer (`0xa0...`):** Receives commands or data words.
  - **Output Ring Buffer (`0xa0... + offset`):** Receives formatted ASCII response streams.
- **Mechanism:**
  - One connection (e.g. Ethernet cable) pushes command words using `memory set long`.
  - A native worker loop (or timer hook) reads new words, executes them, and writes results to the Output Ring Buffer.
  - A second connection (e.g. Wi-Fi client) polls the Output Ring Buffer using `memory show`.
- **Advantages:**
  - Requires zero network socket permissions or ports.
  - Impossible to block or interfere with the router's existing TCP/IP servers.
  - 100% fail-closed: releasing the RAM file immediately stops the channel.
- **Home Lab Value:** Medium-High. Ideal for hardware telemetry logging and asynchronous monitoring.

---

### Option C: Telnet CLI Command Injection (Vendor Console Hooking)

- **Concept:** Dynamically patch the vendor CLI parser table in RAM (`0x805435c4`) to register custom commands (e.g. `native`, `peek`, `poke`, `exec`) directly into the `XDSL#` prompt.
- **Mechanism:**
  - In [`research/firmware-cli-analysis.md`](../research/firmware-cli-analysis.md), we mapped the complete lexical table (`0x805435c4`) and command dispatch table (`0x802a2e10`).
  - Native code appends a new token record and command dispatch handler to this table.
  - Any user logged into Telnet can immediately type `native help` or `native ping` and receive direct interactive text output in that session.
- **Advantages:**
  - Seamless integration with the existing admin console.
  - Uses the router's built-in text formatting and terminal handling.
- **Home Lab Value:** High. Extends the router's native CLI into a powerful diagnostic tool without running extra daemons.

---

## 4. Genuinely Useful Home Lab Utility Applications

Beyond academic experiments, what practical roles can this router perform in a home lab?

### 1. Embedded Network Throughput Probe & Micro-Iperf Server
- **Problem:** Testing true wire-speed switching and Wi-Fi throughput between lab subnets often requires dedicated test machines.
- **Solution:** A native MIPS32 UDP/TCP throughput generator that receives or blasts packets at full wire speed across Ethernet and Wi-Fi, reporting packet drop rates, jitter, and throughput.

### 2. Physical Network Packet Tap & Traffic Telemetry Monitor
- **Problem:** Seeing raw packet statistics, link errors, and SAR ATM/PTM framing without physical network taps.
- **Solution:** Native code directly queries the Ethernet switch registers (`0xb800a000`) and WAN DSP registers, streaming real-time per-port bandwidth statistics (bytes/sec, CRC errors, collisions) to a lightweight dashboard.

### 3. Isolated Lab Watchdog & Network Gateway Controller
- **Problem:** Automating isolated lab power or connectivity states.
- **Solution:** A resident lightweight watchdog that monitors upstream lab health and can dynamically toggle hardware GPIO pins or Ethernet port links (`ethstatus`) via MMIO.

---

## 5. Proposed Implementation Roadmap for Next Phase

| Milestone | Objective | Primary Deliverables | Safety Boundaries |
| :---: | :--- | :--- | :--- |
| **Phase A** | **Memory Allocator Probe** | Test dynamic allocation of 64 KiB–4 MiB via `0x80011b74` | Pure volatile RAM; revalidate pointers before use |
| **Phase B** | **Two-Way Shared Memory Ring Buffer** | Implement asynchronous command/response mailbox | Clean allocation release on shutdown |
| **Phase C** | **Interactive TCP Socket Listener** | Deploy lightweight TCP echo/command server on port 9999 | Bound strictly to LAN subnet `192.168.15.0/24` |
| **Phase D** | **Lab Network Monitor Tool** | Real-time port bandwidth & MMIO telemetry streamer | Read-only register access |
