# Related investigations — extracted leads

Reviewed 2026-10-27. Local results are in ASKEY-NET-001 through 006. A shared command or chipset family does not establish firmware compatibility.

## Exact model: O3 Labs RTV9015VW

Source: https://www.tripleoxygen.net/wiki/modem/rtv9015vw

- Reports another unit with RTL8685SF, MX25L6406E 8 MB flash, RTL8192ER wireless and RTL8275 DSL hardware.
- Documents `/padrao`, support login with the label admin password, and `/saveconf.htm` settings export.
- Documents `ENABLE_ADVANCE_PAGE=1` and `PADRAO_WIFI_ONLY=0` to expose advanced pages through settings import/reboot.
- Warns that newer firmware changed availability of some pages.

**Locally reproduced:** support login, settings export, and the explicitly approved two-flag menu change/reboot. The local console independently reports 8 MB flash and a `8671x` hardware-family string. Physical chip markings and the reported external chip models remain unverified on this unit. This source supplies no demonstrated POSIX shell recipe for the running build.

## Related terminal gate: Beetel 777VR1

Source: https://gist.github.com/raghav20232023/39e3d88d1bc2bcef89bb0f3b5fbb73e0

- Firsthand report describes Telnet accepting TCP and then immediately closing while `TELNET_STATE=0`.
- Changing that field to `1` enables its management console; its configuration uses matching terminal/ACL field names.
- Describes a `sh` transition and a diagnostic console. Its root/shell terminology is broader than the proof required in this project.

**Locally reproduced:** the owner-approved one-flag change persists and permits Telnet admin login. On the Askey, `sh` opens another vendor console (`XDSL>`), and both `id` and `uname -a` are rejected inside it. `config` and `diagnostic` are privilege-denied at the outer parser. The source is therefore useful for the terminal gate, not proof of Linux or arbitrary native execution. Its ACL changes and credentials were not copied.

## Strongest extraction lead: V2802RH OSK research

Repository: https://github.com/1234205a/vsol-v2802rh-research

Analysis: https://github.com/1234205a/vsol-v2802rh-research/blob/main/docs/firmware-and-flash-analysis.md

The author investigates an RTL9601D-based V2802RH running customized OSK RTOS and Virtual Web 0.9. Main useful findings:

- `memory show <address> length <bytes>` exposes memory-mapped flash without Linux filesystem tools.
- Small, paced reads can be assembled into a binary. The reported working chunk size is approximately 1 KiB.
- The documented image has a 64-byte big-endian header, a page region, and a primary compressed firmware stream.
- Firmware analysis required legacy LZMA1 handling and both MIPS32/MIPS16e disassembly on that other device. Function-pointer low-bit tagging matters for its MIPS16e regions.
- Its OSK1FS parser and image tools are useful references for offline format investigation.
- Its apparent backup variables did not prove a real fallback image. Recovery claims must be checked against actual layout/content.

**Locally reproduced:** the Askey exposes `memory show`, and a 16-byte read from its own reported image address succeeded. The full 64-byte local header has consistent load/length/entry fields, a 2017 timestamp, `router.` name and a page-size field. The provisional length also aligns with the unused-region boundary reported by the device.

**Not transferable:** the V2802RH's 4 MB size, flash base/offsets, SoC/ISA, bootloader, firmware images, write procedures or UART wiring. This Askey reports an 8 MB map at `0xb4000000` and a run image at `0xb4010000`.

**Implementation caution grounded in source inspection:** despite the CLI client's read-only name, its inspected source also offers diagnostic-setting modes and `omcicli set` calls. None of that downloaded code was executed. Our capture tool issues only login/navigation, the verified memory display operation, and logout/disconnect; it validates every returned address and byte count.

## Runtime comparison: O3 Labs V2801Q bootlog

Source: https://www.tripleoxygen.net/wiki/ont/vsol/v2801q

- Primary bootlog identifies an OSK image and task names including CFGTASK, CLITASK, GENTSK, XTCPIP and EWSTSK.
- Those task names agree with the Askey's live task table, supporting a related runtime-family hypothesis.
- This does not identify the exact Askey kernel, ABI or instruction set.

## Leads explicitly excluded as proof

- Public `ysleu/RTL8685` source uses a different Boa/.asp interface; inspected files did not explain this Virtual Web/form2 build's service flags.
- A certification mirror labels RTV9015VW as RTOS v1.2.1, but the original certificate API returned HTTP 401. It remains a lead, not primary proof of the running OS.
- No matching downloaded firmware has been executed or flashed. Settings exports are not full flash backups.

## Current next work

The owner explicitly requested full firmware extraction and saving verified firmware in the Git repository. ASKEY-NET-006 captured the device's entire measured 8 MiB flash map through the validated read-only primitive, with raw/partial data private until verification. Then extract and inspect the running image offline and retain final artifacts under `firmware/`, with hashes and verification limits.

## Completion update

The full 8 MiB read, complete running image, readback samples and static analysis are finished. Verified artifacts and actual hashes are in [firmware/](../firmware/README.md); exact local conclusions are in [firmware analysis](firmware-analysis.md). Related-device ISA/offset/loader assumptions were not substituted for local evidence. The live-session capability-field path remains [open for later research](open-research-leads.md).
