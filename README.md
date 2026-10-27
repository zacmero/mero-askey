# Mero Askey — RTV9015VW

Ethernet-first investigation of Zac's **Askey RTV9015VW (Vivo VDSL gateway)**.

**Objective: a genuine operating-system shell, then a tiny native program running in temporary storage.** An advanced web page, a vendor command menu, or JavaScript executed in the laptop browser does not satisfy that objective.

## Start here

Read [HANDOFF.md](HANDOFF.md) for the current constraints and first bounded experiment. [Research sources](research/sources.md) separate other-unit findings from evidence on this device. [AGENTS.md](AGENTS.md) defines repository and experiment rules.

## Baseline — 2026-10-26, America/Sao_Paulo

| Item | Status |
| --- | --- |
| Device identity | Askey RTV9015VW, identified in earlier owner label photographs |
| Label power / manufacture | 12 V DC / 1 A; December 2018, as transcribed in the earlier photo review; verify supply polarity and connector before use |
| Current host | Owner is using a Linux Mint laptop; active interface/IP not yet inventoried for this target |
| Installed firmware / live IP / open services | **Unknown; not yet measured on the Askey** |
| Advanced configuration | External exact-model lead; not yet reproduced here |
| SSH, Telnet or Linux shell | **Not established** |
| UART/flash/pinout | No measurements on this unit in this session |
| Firmware image / recovery | Not acquired or validated |

The repository was empty when this documentation request began. No Askey scan, login, configuration change or hardware connection was performed by this publication.

## Why this is the immediate target

The [MitraStar investigation](https://github.com/zacmero/mero-mitrastar) has two independent SPI blockers: the received CH341A shows approximately 5 V on a reported data output, and its supplied SOIC8 clip cannot seat around the crowded flash. The incoming ESP32 has not arrived, and female–female jumpers are still missing. Its [session record](https://github.com/zacmero/mero-mitrastar/blob/master/docs/experiments/mitra-hardware-020.md) and [buying list](https://github.com/zacmero/mero-mitrastar/blob/master/BUYING-LIST.md) preserve that work.

Do **not** make this Askey software investigation wait for soldering equipment, clip replacement, or programmer repair. Start with the existing Ethernet cable, correct router supply and Mint laptop. A zero-purchase investigation is possible; an easy root shell is not promised.

## First experiment: ASKEY-NET-001 — planned, not run

Identify the directly connected Askey and laptop interface; preserve the laptop's control/internet path. Perform a bounded scan of likely local management ports and inspect the actual web firmware/status pages. If the verified address is the usual `192.168.15.1`, `/padrao` and `/saveconf.htm` are literature leads to inspect. They are not guaranteed endpoints on this firmware.

Both Vivo routers may use the same default IP. Connect **one lab router at a time**, leave DSL/WAN disconnected, and verify the route/device identity before any probe. Never scan the household gateway by assumption.

## Evidence layout

```text
HANDOFF.md             current plan, constraints and next test
AGENTS.md              agent and safety rules
research/sources.md    external references and applicability limits
.local/                ignored captures, credentials and exports
```

Add reviewed experiment reports under `docs/experiments/` as actual results arrive. Keep configuration exports, cookies, passwords, raw traffic and proprietary firmware private. Do not commit device-label passwords or copy credentials from the MitraStar.
