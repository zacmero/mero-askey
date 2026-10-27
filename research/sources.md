# Askey RTV9015VW — source index

Extracted main information and local applicability of the leads: [related investigations](related-investigations.md). The owner-requested full extraction is complete in [ASKEY-NET-006](../docs/experiments/askey-net-006.md); verified final artifacts are saved in [firmware/](../firmware/README.md).

Analysis of the actual captured running image is now saved separately: [consolidated local findings](firmware-analysis.md). These local code-supported conclusions supersede related-device hypotheses where explicitly reproduced; neither a source report nor a hidden command name is proof of live native execution.

Unfinished paths, including the owner's explicitly retained live-session capability-field investigation, are recorded in [open research leads](open-research-leads.md). A prior automated tool block is not a technical rejection of that avenue.

## New OSK investigation and locally reproduced read primitive — 2026-10-27

[VSOL V2802RH research](https://github.com/1234205a/vsol-v2802rh-research) is a primary related-device investigation of OSK RTOS/Virtual Web 0.9. Its [flash-analysis document](https://github.com/1234205a/vsol-v2802rh-research/blob/main/docs/firmware-and-flash-analysis.md) describes memory-mapped NOR reads, firmware decompression and mixed MIPS32/MIPS16e analysis. Its CPU, image offsets, ISA, flash layout and recovery claims do not automatically apply to this Askey.

Local validation now confirms this Askey's inner console supports `memory show`; a single 16-byte read at the independently reported run-image address succeeded. See [ASKEY-NET-005](../docs/experiments/askey-net-005.md). This gives a concrete path toward obtaining the unit's own firmware for offline analysis, without assuming Linux shell access. No full firmware dump or memory write occurred.

Retained related-source text snapshots are in ignored `.local/research/vsol-v2802rh/`. The client file's inspected first 300 lines also contain diagnostic-setting operations despite its read-only name; no downloaded script was executed. Older pending/prepared descriptions below are historical snapshots; use the latest experiment/handoff for current state.

## Live console findings — 2026-10-27

The related Telnet-state lead is now locally confirmed for terminal activation: `TELNET_STATE=0x1` persists, and admin login works. Its claimed shell access must not be generalized: on this unit `sh` opens another vendor console, `id` is rejected, and privileged diagnostic/configuration entries are denied. See [ASKEY-NET-004](../docs/experiments/askey-net-004.md) and [verified specifications](../docs/device-specs.md).

[Related primary V-SOL bootlog](https://www.tripleoxygen.net/wiki/ont/vsol/v2801q) identifies an OSK image and reports many matching task names. It supports a related runtime-family lead, not exact OS/firmware compatibility. Local task/memory observations are consistent with an RTOS-style system. A certification mirror for RTV9015VW reports RTOS v1.2.1, but the original certificate endpoint returned HTTP 401; that mirror remains an unverified lead and is not primary proof of the running OS.

## Terminal-service lead — 2026-10-27

[Firsthand Beetel 777VR1 report](https://gist.github.com/raghav20232023/39e3d88d1bc2bcef89bb0f3b5fbb73e0): reports Telnet accepting then immediately closing while `TELNET_STATE=0x0`, and console access after changing it to `0x1`. Its configuration uses several matching terminal/ACL field names. This is related-device evidence; RTV9015VW applicability remains unconfirmed. A one-byte candidate is prepared, pending explicit service activation instruction. See [ASKEY-NET-003](../docs/experiments/askey-net-003.md).

[Related public RTL8685 SDK](https://github.com/ysleu/RTL8685): inspected `uClinux-dist/user/boa/src/LINUX/mib.h`, `utility.c`, `form_src/fmacc.c`, `web_default/rmtacc.asp`, and `user/telnetd/telnetd.c`. Its Boa/.asp interface differs from the unit's Virtual Web/form2 interface; inspected files did not establish this firmware's `TELNET_STATE`/`SSH_STATE` mapping. Do not use it as an exact firmware match or proof that Telnet runs an OS shell.

## 2026-10-27 follow-up

The exact-model TripleOxygen page was fetched again and retained privately. Local tests now confirm the documented `support` account works with the owner's label admin password on `BR_SO_RTK_V6.1.8t`, and the native settings export is available after support login. The actual export contains `ENABLE_ADVANCE_PAGE=0x0` and `PADRAO_WIFI_ONLY=0x1`, matching the source's prerequisites. A two-flag candidate is prepared but has not been imported or rebooted. This remains an advanced-menu procedure, with no demonstrated OS shell result. See [ASKEY-NET-001](../docs/experiments/askey-net-001.md) for local evidence and actual artifact hashes.

Checked **2026-10-26**. These are external references, not measurements from Zac's router. Do not turn a published same-model finding into a local result.

## Primary exact-model investigation

**O3 Labs — Askey RTV9015VW**

https://www.tripleoxygen.net/wiki/modem/rtv9015vw

The retrieved page reports this other-unit hardware:

| Role | Reported part/detail |
| --- | --- |
| SoC / bootloader family | Realtek RTL8685SF / RTL867X |
| Flash | Macronix MX25L6406E, 8 MB |
| Wireless | RTL8192ER, 2.4 GHz b/g/n |
| DSL component | RTL8275 |
| Telephone interface | Le9641PQC |
| USB / serial / JTAG | No USB; serial reported; JTAG unspecified |

For older firmware, it describes `/padrao`, `support` with the device-label admin password, and configuration download via `/saveconf.htm`. It describes editing `ENABLE_ADVANCE_PAGE` and `PADRAO_WIFI_ONLY` in `config.img`, importing it and rebooting. The page also reports updated firmware removing the straightforward Saveconf/DDNS pages.

**Applicability:** this establishes useful management and hardware leads, not a demonstrated root-shell recipe for Zac's firmware. A retrieved configuration is not a full flash backup. The described import/reboot is a persistent procedure to evaluate later, not an authorized first experiment.

## Earlier secondary tutorial — retrieval incomplete

Academia Técnica, earlier conversation link:

https://www.academiatecnica.com.br/2021/03/19/como-liberar-o-modo-de-configuracao-avancada-no-modem-adsl-askey/

This URL could not be retrieved in the publication session. It is preserved as a **location lead only**, not counted as independent verification of the method. Prefer the primary O3 Labs record above.

## Project-specific evidence

The owner's earlier enclosure-label photos identify RTV9015VW and were transcribed as 12 V DC / 1 A, manufactured 12/2018. No Askey internal-board photographs, exact firmware string, live service scan, serial log or shell output were supplied in this initialization session. No CPU ABI, RAM capacity, flash package, UART pin mapping or recovery mode is locally established.

The [MitraStar hardware report](https://github.com/zacmero/mero-mitrastar/blob/master/docs/experiments/mitra-hardware-020.md) explains the shared equipment limitations. Its chip, account, voltage and header observations do not belong to this Askey.

## Source questions for the next actual session

First capture this router's exact software/build and management behavior. Then search that build for an original firmware/source release or matching documented service behavior. Record the source date, model/revision, applicability and whether the text was actually retrieved. No matching image, OpenWrt installation path or network-to-shell method has been verified by this handoff.
