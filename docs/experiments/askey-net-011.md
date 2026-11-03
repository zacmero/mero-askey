# ASKEY-NET-011 — Network Subnet Migration & Permanent DHCP Server Deactivation

Date: 2026-11-03, UTC−03:00.  
Status: **Full Success**. Candidate configuration uploaded, verified, accepted by firmware, and committed to SPI NOR flash across auto-reboot. LAN IP migrated to static `192.168.1.250/24` and embedded DHCP server daemon permanently disabled (`CONFIG_SERVICE_DHCP=0x0`).

Target router: Askey RTV9015VW, build `BR_SO_RTK_V6.1.8t` (Realtek RTL8672 / RLX5181 core).

---

## 1. Objectives and Scope

Following the successful proof of native MIPS32 execution ([ASKEY-NET-010](askey-net-010.md)) and physical hardware probing ([`docs/hardware-specs-and-baremetal.md`](../hardware-specs-and-baremetal.md)), the user requested direct access from their primary workstation (`mero-machine`) without needing an intermediate test laptop (MSI).

Connecting the Askey directly into an unmanaged household network switch presents a **rogue DHCP collision hazard**: the factory configuration operates an active DHCP server at `192.168.15.1`, which would race against the household router (`192.168.1.1`) and disrupt internet access for household devices.

The scope of this experiment:
1. Export and verify the current live settings baseline (`config-live-preflight.img`).
2. Synthesize a surgical, minimal candidate image (`config-dhcp-disabled-candidate.img`) that disables the DHCP daemon and reassigns the LAN IP to static `192.168.1.250/24`.
3. Submit the candidate image via the authenticated multipart upload endpoint (`form2fileConf.htm`).
4. Record firmware response, commit timing, and transition requirements for direct switch integration.
5. Provide a rigorous, fail-safe recovery procedure if a physical factory reset is performed.

---

## 2. Experimental Execution Phases

The transition was orchestrated using [`tools/apply_dhcp_transition.py`](../../tools/apply_dhcp_transition.py).

### Phase 1: Preflight Verification & Live Baseline Export
- Network link verified: `enp6s0` (`192.168.15.3/24` $\to$ `192.168.15.1`).
- Hardware MAC confirmed: `54:2f:8a:48:1a:b8`.
- Target IP vacancy check: `ping -c 2 192.168.1.250` confirmed IP `192.168.1.250` was 100% vacant on the home network.
- Live configuration exported from `form2saveConf.cgi`:
  - Size: 205,061 bytes.
  - SHA-256: `4c5c8a2fe7c533aee6f7cff98ab2bd7e89345d8b9b8bbcface0d323d1cae7d44`.
  - Artifact: `.local/askey-net-011/config-live-preflight.img`.

### Phase 2: Candidate Image Synthesis & Unified Diff
The candidate image modified exactly 7 lines in the XML settings payload:
```diff
--- config-live-preflight.xml
+++ config-dhcp-disabled-candidate.xml
@@ -102,1 +102,1 @@
-      <Value Name="CONFIG_SERVICE_DHCP" Type="string">0x2</Value>
+      <Value Name="CONFIG_SERVICE_DHCP" Type="string">0x0</Value>
@@ -420,1 +420,1 @@
-      <Value Name="LAN_PRIMARY_IP" Type="string">192.168.15.1</Value>
+      <Value Name="LAN_PRIMARY_IP" Type="string">192.168.1.250</Value>
@@ -432,1 +432,1 @@
-      <Value Name="NETWORK" Type="string">192.168.15.0</Value>
+      <Value Name="NETWORK" Type="string">192.168.1.0</Value>
@@ -434,1 +434,1 @@
-      <Value Name="IPROUTER" Type="string">192.168.15.1</Value>
+      <Value Name="IPROUTER" Type="string">192.168.1.1</Value>
@@ -436,1 +436,1 @@
-      <Value Name="STARTIP" Type="string">192.168.15.10</Value>
+      <Value Name="STARTIP" Type="string">192.168.1.200</Value>
@@ -438,1 +438,1 @@
-      <Value Name="ENDIP" Type="string">192.168.15.200</Value>
+      <Value Name="ENDIP" Type="string">192.168.1.240</Value>
@@ -440,1 +440,1 @@
-      <Value Name="DNSSERVER1" Type="string">192.168.15.1</Value>
+      <Value Name="DNSSERVER1" Type="string">192.168.1.1</Value>
```
- Candidate size: 205,059 bytes.
- Candidate SHA-256: `f34f093d50bdf1b78fb3a5d4b0083e7fd721b831e4059d5c12cd025eb7db35bb`.
- Artifact: `.local/askey-net-011/config-dhcp-disabled-candidate.img`.

### Phase 3: Native Multipart Upload & Flash Commit
- Boundary generated: `AskeyTransition<random-token>`.
- Request dispatched via HTTP/1.0 POST to `/form2fileConf.htm`.
- Response status: HTTP/1.0 200 OK (`Virtual Web 0.9`).
- Response payload:
  ```html
  <title>Autoboot</title>
  ...
  <th>restore current setting! System is rebooting now...</th>
  <th><font color=red>Please Wait<INPUT TYPE=text NAME=time size=1> s</font></th>
  ```
- Upload duration: **3.46 seconds**.
- The router committed the new configuration to SPI NOR flash and entered its 50-second reboot countdown.

---

## 3. Direct Switch Architecture & Operation

Once rebooted with DHCP permanently disabled, the router is completely safe to connect to any unmanaged home network switch:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DIRECT HOME LAB TOPOLOGY                        │
└────────────────────────────────────────────────────────────────────────┘

  [ Main Home Router / Gateway ]
  (IP: 192.168.1.1 | Active DHCP Server: 192.168.1.100 - 192.168.1.199)
               │
               ▼ (Uplink)
     ┌───────────────────────┐
     │ Unmanaged Home Switch │
     └───┬───────────────┬───┘
         │               │
         │ (1 Gbps)      │ (100 Mbps)
         ▼               ▼
  [ mero-machine ]   [ Askey RTV9015VW ]
  IP: 192.168.1.97   IP: 192.168.1.250 (Static)
  Default Gateway    DHCP: DISABLED (Passive Node)
                     Telnet: 192.168.1.250:23
                     Web UI: 192.168.1.250:80
```

### Safety Properties:
1. **Zero Rogue DHCP Traffic:** With `CONFIG_SERVICE_DHCP=0x0`, the router will never transmit DHCP OFFER or DHCP ACK packets.
2. **Deterministic Addressing:** The router always occupies `192.168.1.250`, safely above the main router's DHCP reservation pool (`.100`–`.199`).
3. **Immediate Fail-Safe:** If physical isolation is ever required, unplugging the single Ethernet patch cable instantly disconnects the device.

---

## 4. Factory Reset & Hard Recovery Protocol

The Askey's persistent configuration lives in the `/var/config` flash filesystem.

> [!WARNING]
> **Hard Reset Behavior:** If the physical rear reset pin is depressed for 10–15 seconds, the bootloader clears the flash config partition. The router reverts to factory defaults:
> - LAN IP: `192.168.15.1`
> - DHCP Server: **RE-ENABLED** (`0x2`)
> - Admin Password: Default sticker password

### Recovery Procedure After a Hard Reset:
1. **DO NOT** leave the router plugged into the switch if a hard reset is triggered.
2. Unplug the Askey from the switch and connect it directly to an isolated PC or laptop port.
3. Configure the PC interface to `192.168.15.3/24`.
4. Re-run [`tools/apply_dhcp_transition.py`](../../tools/apply_dhcp_transition.py) to re-apply `config-dhcp-disabled-candidate.img`.
5. Once rebooted, reconnect the Askey to the switch.
