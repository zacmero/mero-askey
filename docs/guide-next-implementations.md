# Guide to Next Implementations, Architecture & Lab Topology

**Target:** Askey RTV9015VW Gateway (`BR_SO_RTK_V6.1.8t`).  
**Status:** Native MIPS32 execution proven on-target ([ASKEY-NET-010](experiments/askey-net-010.md)); hardware specifications measured directly on silicon ([`docs/hardware-specs-and-baremetal.md`](hardware-specs-and-baremetal.md)).

---

## 1. Quick Navigation: What Has Been Built & Learned

| Topic | Document / Artifact | Key Findings |
| :--- | :--- | :--- |
| **Native Execution Proof** | [ASKEY-NET-010](experiments/askey-net-010.md) | Synchronous MIPS32 execution under `webdll`, 10 matching mailbox markers, stable CLI return, clean RAM release. |
| **Bare-Metal & MMIO Lesson** | [Hardware Specs & Lesson](hardware-specs-and-baremetal.md) | How bare-metal MIPS memory mapping works, 3-layer proof of life (L2/L3/L7), and why KSEG1 bypasses CPU caches. |
| **Measured System Specs** | [`tools/probe_hardware_specs.py`](../tools/probe_hardware_specs.py) | Realtek RTL8672 / RLX5181 core, ~300 MHz CPU, 100.1 MHz bus clock, 64 MiB physical DRAM, 8 MiB flash. |
| **Next Phase Roadmap** | [Next Experiments](next_experiments.md) | Scaling memory allocations to megabytes, 3 two-way I/O architectures, home lab utilities. |

---

## 2. The Network Question: Can We Connect the Askey to the Main Switch?

### The Question
> *"I have a network switch here. The main router cable plugs into it and from it cables go to other devices. Can't we have a cable from the switch go to our Askey and from `mero-machine` run experiments directly, instead of relying on the slow MSI laptop?"*

### The Risk: Rogue DHCP Server on the Household Network
Connecting the Askey's LAN port directly into an unmanaged household switch without preparation creates a **high-risk network collision**:

```
[ Household Router: 192.168.1.1 ] (DHCP Server: assigns 192.168.1.x)
              │
              ▼
   [ Main Unmanaged Switch ]
     ├── mero-machine (192.168.1.97)
     ├── Household PC / Smart TVs / Phones (192.168.1.x)
     └── [ DANGER! ] ◄── (Cable) ──► [ Askey LAN Port: 192.168.15.1 ]
                                      (DHCP Server: assigns 192.168.15.x!)
```

#### What happens?
The Askey RTV9015VW runs its own active **DHCP server** (`DHCP` daemon in `show system task`) on its LAN bridge (`192.168.15.1`).  
If plugged into the main switch:
1. When your phone, smart TV, or `mero-machine` renews its DHCP lease, the Askey and your main router will **race to reply**.
2. If the Askey replies first, your household devices will receive an IP like `192.168.15.x` with gateway `192.168.15.1`.
3. **Result:** Household internet access immediately breaks, and devices lose communication with each other. This is why repository safety rule `AGENTS.md` explicitly forbids unisolated connections.

---

### Safe Solutions: How to Bypass the MSI Laptop

Here are the 4 safe, practical approaches to connect directly from `mero-machine`:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DIRECT CONNECTION SOLUTIONS                        │
└─────────────────────────────────────────────────────────────────────────────┘

  Solution 1: Transparent SSH Port-Forwarding (Zero Re-cabling, Instant Speed)
  ────────────────────────────────────────────────────────────────────────────
  mero-machine runs all Python scripts locally; MSI laptop acts as a pure,
  wire-speed TCP relay without executing Python.

  Solution 2: Secondary USB-Ethernet Adapter on mero-machine (Isolated Lab Link)
  ────────────────────────────────────────────────────────────────────────────
  Direct physical cable from mero-machine to Askey LAN. Zero household risk.

  Solution 3: Disable DHCP on Askey & Reconfigure LAN to Home Subnet
  ──────────────────────────────────────────────────────────────────
  Disable Askey DHCP daemon, set static IP 192.168.1.250, then plug into switch.

  Solution 4: Managed Switch VLAN Isolation
  ──────────────────────────────────────────
  Assign Askey port to an isolated 802.1Q VLAN.
```

---

### Solution 1: Transparent SSH Port-Forwarding (*Recommended — Immediate, Zero Hardware Changes*)

You do **not** have to run slow Python scripts on the MSI laptop. The MSI laptop can act as a **transparent TCP pipe**:

1. On `mero-machine`, open an SSH port-forward tunnel:
   ```sh
   ssh -i ~/.ssh/mero_stb_isolated_lab -L 2323:192.168.15.1:23 cris@192.168.1.80 -N -f
   ```
2. Now, port `2323` on `mero-machine` connects directly to the Askey's Telnet port!
3. `mero-machine` runs all Python probes and tools locally at full native speed. The MSI laptop executes zero Python code; its kernel simply forwards raw network packets across interfaces with < 1 ms latency.

---

### Solution 2: Secondary USB-Ethernet Adapter on `mero-machine` (*Best Long-Term Hardware Setup*)

If you want to take the MSI laptop completely out of the equation:
1. Plug an inexpensive USB-to-Gigabit Ethernet adapter into `mero-machine` (creating interface `enpX`).
2. Run a patch cable directly from `mero-machine` to the Askey's LAN port.
3. Configure `mero-machine`'s secondary interface with static IP `192.168.15.3/24`:
   ```sh
   sudo ip addr add 192.168.15.3/24 dev enpX
   sudo ip link set enpX up
   ```
4. `mero-machine`'s primary interface (`enp5s0`) remains on the household network (`192.168.1.97`), while its secondary interface communicates directly with the Askey (`192.168.15.1`) at 0.2 ms wire latency.

---

### Solution 3: Reconfigure Askey to a Client Node (Disable DHCP)

If you want the Askey permanently connected to your main switch:
1. While connected through the lab link, disable the Askey's DHCP server:
   - Via web UI: `dhcp_onoff.htm` $\to$ Disable DHCP.
   - Or via CLI: `cfgmib` / settings export modification.
2. Change the Askey's LAN IP address from `192.168.15.1` to an unused static IP on your household subnet outside the main router's DHCP pool (e.g., `192.168.1.250`).
3. Reboot the Askey and plug it into the switch.
4. Now the Askey acts as a standard network node on your LAN; any device on your home network can reach `192.168.1.250:23` directly.

---

## 3. Next Implementation Roadmap & Possibilities

Detailed in [**`docs/next_experiments.md`**](next_experiments.md):

### A. Memory Scaling (Pushing the System to the Edge)
- Allocate multi-megabyte RAM buffers directly using resident kernel allocator `sys_mem_alloc` (`0x80011b74`).
- Benchmark system stability under 64 KiB, 256 KiB, 1 MiB, and 4 MiB allocations out of the router's 64 MiB DRAM pool.

### B. The Three Two-Way Interactive I/O Architectures
1. **Option A (TCP Bind Shell):** Launch a resident background task listening on TCP port 9999 for interactive `nc 192.168.15.1 9999` access.
2. **Option B (Shared-Memory Ring Buffer):** Dual-channel asynchronous input/output mailbox for decoupled cross-device communication.
3. **Option C (Telnet CLI Hooking):** Dynamically inject custom commands into the `XDSL#` prompt.

### C. Home Lab Utility Applications
1. **Micro-Iperf Server:** Wire-speed network throughput and jitter tester across Ethernet and Wi-Fi.
2. **Hardware Telemetry & Packet Tap:** Real-time port bandwidth and SAR register monitoring (`0xb800a000`).
3. **Automated Lab Gateway / Watchdog:** Automated connectivity monitor and GPIO/link controller.
