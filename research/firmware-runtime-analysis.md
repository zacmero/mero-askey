# Captured runtime: OSK identity and native execution boundary

Offline analysis, **2026-10-27**, of the owner's `BR_SO_RTK_V6.1.8t` run image. No firmware code was executed, and no device command, memory write, upload, configuration change or hardware operation was performed for this analysis.

The captured runtime contains an OSK kernel and mixed big-endian MIPS instruction streams. It provides task creation, memory allocation and indirect native calls. A POSIX shell, Linux system-call ABI and general executable loader have **not** been established. A Linux MIPS binary is therefore not a justified next artifact.

## Artifact and address convention

The decompressed private artifact is `.local/askey-net-006/analysis/runtime.bin`: **9,752,040 bytes**, SHA-256 `b104789b795630eee7de1b50d64e49710535221f8baa6652021af6d00abb3941`. It comes from the validated captured [run image](../firmware/README.md), not a related device's firmware. Its supplied load base is `0x80000000`, entry is `0x80949288`, and exclusive end is `0x8094cde8`, which matches the independently observed memory-pool start. The runtime hash and size were rechecked here; decompression/header validation belongs to [ASKEY-NET-006](../docs/experiments/askey-net-006.md).

For this artifact, **runtime address = file offset + `0x80000000`**. Addresses below refer to this mapping, not flash offsets. Function-pointer values ending in `1` preserve the MIPS16 mode tag; the underlying bytes begin at the preceding even address. A raw pointer inside an instruction/data mixture is an analytical lead until its referring instruction is checked.

## Architecture and calling convention

| Local byte evidence | Interpretation | Limit |
| --- | --- | --- |
| Offset `0x949288`, address `0x80949288`: bytes `40 09 60 00`, decoded as `mfc0 t1,c0_status`; subsequent `mtc0`, `jal`, `lw` and `sw` form coherent startup code in big-endian order. | Actual MIPS code, with a conventional 32-bit instruction region and privileged CP0 access. | Does not identify the SoC model or all supported ISA extensions. |
| `0x809492a4`: `lui gp,0x8063`; delay slot at `0x809492ac`: `addiu gp,gp,0x7480`. | Startup establishes `gp = 0x80637480`. | A future routine using small/global data must respect this context; this is not an ELF ABI declaration. |
| `0x8094937c`–`0x8094938c`: builds stack address `0x8063d810`, masks it with `-16`, copies it into `s8`. | Startup explicitly aligns its stack to 16 bytes. | This is the startup stack, not a generally available payload region. |
| `0x809493b0`–`0x809493bc`: constructs `ra = 0x80949415`, then `jr ra`. Bytes at even address `0x80949414` decode coherently as MIPS16, beginning `addiu sp,-24; sw ra,20(sp)`. | Actual transition to tagged MIPS16 code; the image mixes instruction modes. | “All firmware is MIPS32” and mode-blind linear disassembly are incorrect. Exact MIPS16 extension requirements remain to be established. |
| `0x802a277c`–`0x802a27b8`: a 40-byte stack frame, saved `ra`/`s0`/`s1`, arguments in `a0`/`a1`, return value in `v0`, indirect `jalr`, and saved-register return. | Conventional MIPS C calling patterns, consistent with an o32-style 32-bit convention. | No ELF header, compiler metadata or complete callable prototype establishes the full ABI, floating-point convention or Linux compatibility. |
| Offset `0x45fe04`, address `0x8045fe04`: `MIPS16 exception :op %d, pc=%x, %x, %x, %x`. | The runtime's own exception code recognizes MIPS16. | The text alone would be insufficient; executable mode-switch evidence above corroborates it. |

GNU binutils `mips-linux-gnu-objdump` 2.35.2 was unpacked into ignored private scratch by the parallel CLI analysis. This report used its explicit big-endian raw-binary MIPS32 and MIPS16 modes on bounded regions, checking PC-relative literal values directly against bytes. No downloaded firmware was run. Related-device tools were retrieved and inspected as reference; their Python disassembler was not executed.

## Kernel/runtime identity

These are strings in this captured image, not borrowed device specifications:

| Offset | Runtime address | Evidence |
| --- | --- | --- |
| `0x4602b0` | `0x804602b0` | `oskFatal:%s line=%d %s` |
| `0x4602c8` | `0x804602c8` | `oskError:%s line=%d` |
| `0x4602f8` | `0x804602f8` | `../../swbase/kernel/SWITCH/osksub.c` |
| `0x4949f0` | `0x804949f0` | `../../swbase/drivers/rtl8192er/osk/os_lib.c` |
| `0x460178` | `0x80460178` | `../../swbase/csp/rtl8671/page.c` |
| `0x4bad54` | `0x804bad54` | `-OSK1FS-` |
| `0x4bad80` | `0x804bad80` | `flashfile_init>got OSK1FS, size=%u, cksum=%u` |
| `0x60a9bc` | `0x8060a9bc` | `SDK V1.2.1` |

OSK kernel/driver identity is supported by both strings and calls into the allocation/task machinery below. `SDK V1.2.1` is an SDK label; it does **not** independently establish an OSK kernel release of 1.2.1. Driver/build-path family names do not prove an exact board chip.

The runtime contains task/TCB diagnostics, fixed stack sizes, priorities, mailboxes, slab/pool allocation and page/TLB machinery. For example, task-state text is at offsets `0x468320` and `0x468360`; the pool-creation format is at `0x4681e8`. Startup at `0x80044230` writes CP0 TLB registers and uses `tlbwi`. This is positive evidence for an OSK task-based native runtime. Page tables and Linux-like driver compatibility names do not imply a Linux kernel or processes.

## Task and memory APIs recovered offline

| Routine / reference | Checked behavior | Remaining uncertainty |
| --- | --- | --- |
| Allocation wrapper, bytes at offset `0x11b74`, address `0x80011b74` | Calls `0x80012504` with the requested size in `a0`; on failure prints “no more memory” with the exact `osksub.c` path and line 44, or the zero-size diagnostic. Returns the pointer/zero in `v0`. | No source-level exported name was recovered. Its behavior is allocation-wrapper-like, not proof of a usable public SDK entry. |
| `registerTask` wrapper, offset `0x949b20`, physical address `0x80949b20` | References `registerTask` at `0x80503360` through literal `0x80949c00`. Allocates a requested-size stack through either `0x80011b74` or `0x803c53e1`, then allocates a **416-byte** task object. Records it in a task table and invokes tagged routine `0x80170de1`. | The diagnostic name identifies this wrapper, but the complete prototype, ownership rules, scheduling/start semantics and safe calling context still need recovery. |
| Task initializer, physical `0x80170de0`, tagged `0x80170de1` | Clears **408 bytes** of the object, links task state, checks supplied fields, initializes stack/context through tagged `0x8017006d`, and updates scheduler-related state. The wrapper supplies name/entry-like values and stack address/size. | Exact field meanings and task lifecycle are not fully mapped. These are analytical addresses, not commands to call. |
| Task-registration diagnostic at `0x80949b94`–`0x80949ba2` | Compares a task-count field with **50** and prints the maximum-task warning using `0x8046024c`. | The displayed warning path alone does not prove reliable rejection/cleanup at the limit. |
| Pool/slab code near `0x80170800` | References the pool-start/size format at `0x804681e8` through literal `0x801708fc`; image also has allocation/free error counters and slab diagnostics. | No complete allocator ABI or safe scratch allocation was established. The observed pool start is not free memory to overwrite. |

These interfaces make a small native task plausible in principle. They do not provide a terminal command, transfer path or permission to use them. A monolithic RTOS routine normally calls resident APIs and returns under scheduler rules; an ordinary Linux `_start`/`exit` program assumes services that have not been found here.

## Shell and native loading

Literal searches over the **entire decompressed artifact** found zero matches for ELF magic `7f 45 4c 46`, `/bin/sh`, `BusyBox`, `fork`, `execve`, `dlopen`, `dlsym`, `ld.so`, `Linux` and `FreeBSD`. This does not prove universal absence: firmware can omit diagnostic strings, use other formats, or obtain code elsewhere. Together with the positive OSK/kernel evidence and the live vendor-console behavior, it gives no basis to claim a POSIX shell is present.

There are `pthread` strings, including `pthread_attr_init()` at `0x804357ec`, `pthread_kill` at `0x804e9bcc`, and `cwmp_http_pthread` diagnostics. They show compatibility/application terminology; they do not establish Linux process creation. Likewise, `shell`/`exec` and `/usr/libexec/sftp-server` strings in the SSH-related area are not evidence that a runnable POSIX shell or that server binary exists. [ASKEY-NET-004](../docs/experiments/askey-net-004.md) already distinguishes `$` and `XDSL>` from an OS shell.

Three native-entry leads must remain distinct:

1. **Firmware loader.** The routine whose diagnostic name is `load` (`0x8054b64c`, referenced at `0x802e91c4`) reads a 64-byte image header, checks image identifiers and manipulates firmware-related state. It is not established as a general RAM executable loader. Image upload/recovery behavior requires separate analysis.
2. **CLI address call and image-copy handlers.** The native address call is the inner console's `webdll` handler at physical `0x802a277c`; `loaddll` copies a header-described body. Their register/return contracts and the adjacent checksum handler are detailed below. This is a concrete native callback calling convention lead, not ELF loading. Even a supplied existing address can have arbitrary side effects.
3. **Task entry.** The recovered task wrapper can construct resident task state and an execution context. Calling it requires correct mode-tagged entry, full argument contract, stack/context rules and allocation ownership. It does not itself receive a file or create a command interpreter.

No native-address call, filesystem execution, native module upload, or safe arbitrary-code entry was demonstrated on the device by this work. The presence of a callback path is not native execution success.

### Bounded follow-up: `webdll`, `loaddll` and `chksum`

The parallel [CLI analysis](firmware-cli-analysis.md) mapped dispatcher `0x802a2de8` and its halfword switch table at `0x802a2e10`. The lexer table beginning at `0x805435c4` stores **ID followed by string pointer**, not the reverse. Root grammar records independently confirm the IDs passed to the dispatcher. This corrected interpretation establishes these distinct operations:

| Token table address | Token ID / spelling | Physical handler | Actual bounded behavior |
| --- | --- | --- | --- |
| `0x80543654` | `0x12` / `webdll` | `0x802a277c` | Calls the parsed address and immediately calls its returned callback. |
| `0x8054365c` | `0x13` / `loaddll` | `0x802a27d0` | Inspects a supplied 64-byte image header and conditionally copies its body to the header-specified destination. |
| `0x80543664` | `0x14` / `chksum` | `0x802a2730` | Calculates and prints a checksum of the supplied address/length. No loading or native call occurs in this handler. |

Root descriptors `0x805f1704` (`webdll`, argument/dispatch ID 18) and `0x805f1718` (`loaddll`, ID 19) share numeric child `0x805f1964`, argument ID 1. The preceding lexical token `command` has ID 15, not 17 (`timer`); it must not be confused with the native callback handler. The CLI analysis also traces both native nodes' requirement for session privilege bit 6; the currently reported PRIORITY 2/access-mode-2 combination does not satisfy that gate. These are static predictions, not successful device invocations.

For `chksum`, at `0x802a273a`/`0x802a2740`, the handler obtains length/address from context offsets 140/136. It calls tagged checksum routine `0x803c58f1` with seed zero, masks the result to 16 bits, and prints the address, decimal/hex length and checksum through format `0x80499508`. Inspection of `0x803c58f0`–`0x803c594c` confirms a folded 16-bit checksum loop. This handler has no allocation, body copy, symbol lookup or entry call.

For `webdll`, helper `0x8029b17d` is called with argument selector 1 and an output slot at `sp+16`. The helper's status is not checked before that slot is loaded as the first target. The locally observed call contract is:

| Call site | Target | Defined argument registers at the call | Result handling |
| --- | --- | --- | --- |
| `0x802a2796` | Parsed 32-bit value in `v0` | `a0 = 0x12345678`; `a1 = 0x805f1648` | Return value `v0` is retained in `s1` and printed as `unloadFunc`. |
| `0x802a27aa` | That returned value in `s1` | The same `a0` and `a1` are reloaded. | Handler restores its stack/saved registers and returns; no deferred cleanup mechanism was found here. |

Neither indirect call has a local null/range/mode check. No allocation, transfer, relocation, cache maintenance, new task creation or module-header verification occurs inside this handler. Other argument registers are unspecified at these call sites. It inherits its caller's task, stack and global-data context. The module interface is therefore narrower than a process-launch API.

The object passed in `a1` has one directly established member: the word at `0x805f1648` is tagged function pointer `0x8013733d` (physical `0x8013733c`). That routine saves argument registers into a varargs area and calls `0x801372b5`, whose body allocates a 3,076-byte buffer, formats into it and invokes output-related functions. This supports a printf-like output callback interpretation. The following words at `0x805f164c` onward enter CLI registration/grammar data; no multi-entry symbol-resolution table or complete module SDK was established. The callback's output destination, allocation failure behavior and exact public prototype still need confirmation from callers.

The printed name `unloadFunc` describes the returned value, but the code invokes it **immediately**. A future marker routine that merely returns integer zero would send the second indirect call to address zero. A safe contract would need both a first entry and a verified return callback, correct instruction-mode tags, and an understood behavior for both returns. This analysis did not construct or run either routine.

For `loaddll`, the supplied header pointer comes from the same selector-1 helper. It prints words at offsets 0/4/8/12, the halfword at 16, byte at 18, strings beginning at 19/44, and the word at 60. It compares header word 0 with **`0xa0000003`** (literal at `0x802a2854`). On equality, instructions `0x802a2822`–`0x802a282c` call the MIPS32 copy routine `0x8000607c` with destination = header word at +4, source = header pointer +64, and length = header word at +8. This is an existing native memory-write path. The bounded handler shows no allocation, bounds check, checksum enforcement, relocation, symbol resolution or execution of the printed entry field. A header-shaped buffer alone therefore does not provide safe executable placement. Its existence is not authorization to invoke it.

## Prerequisites for a later native milestone

The next useful offline work is to confirm the output callback's contract and recover task/API prototypes from several callers. A tiny resident marker routine would need verified instruction mode and endian order, register/stack/`gp` preservation, a known output API, a bounded return path including the second callback, and verified cache coherency requirements. An independent task additionally needs its scheduler and cleanup contract. The recovered `webdll`/`loaddll` grammar and access checks do not themselves establish access from the current account/session.

A device trial also requires a verified temporary transfer/allocation mechanism, a region proven safe for executable code and data, and explicit authorization for the actual upload/write/call operation with an understood recovery plan. None is supplied by a flash backup or by knowing the pool's start address. If the immediate target remains a genuine interactive shell, finding or implementing that interpreter is a separate milestone from running a marker routine; the image currently supplies no demonstrated POSIX shell to launch.

## Bounded hardware-inventory lead

A follow-up static pass found one code-supported **RAM global containing a sampled hardware register**, but did not establish detected RAM size or CPU clock. The routine at physical `0x8004d200` reads a word from `0xb8000000` and stores the entire word at **`0x8055a870`** (`0x8004d20e`–`0x8004d21a`). It masks the low 16 bits for the first argument to diagnostic `ChipId: 0x%08x 0x%08x` (`0x804357d4`); the second printed value comes from `0xb8000024`. Literal words at `0x8004d37c`/`0x8004d380`/`0x8004d384` confirm these addresses. Subsequent code compares the masked ID with `0x0561`, `0x0705` and `0x6405`, selecting related initialization paths.

Thus `0x8055a870` is a candidate for a later authorized read of an already sampled value in RAM, avoiding a direct MMIO access. The code's execution/completion and the meaning of each register field still require validation; this is not a detected CPU model. In the **firmware artifact**, that global's initializer is `0x0000ffff`, while other selection fields have compiled initializers. Those bytes are not a live-memory snapshot and must not be recorded as measured hardware. No device read was performed.

The pass also found `SDRAM unknown(0x%08X)` at `0x80031380`, UTOPIA clock diagnostics, pool-size diagnostics and RF-chip terminology. None was traced to a validated detected-RAM-size or CPU-clock global within this bounded question. UTOPIA is a peripheral-interface clock; it must not be reported as CPU frequency. Physical RAM capacity, exact CPU identity and CPU frequency remain unresolved.

## Related primary research and retained evidence

[VSOL V2802RH firmware analysis](https://github.com/1234205a/vsol-v2802rh-research/blob/main/docs/firmware-and-flash-analysis.md) describes another OSK image with mixed MIPS32/MIPS16e code, mode-tagged pointers and PC-relative literal loads. Its [MIPS16 decoder](https://github.com/1234205a/vsol-v2802rh-research/blob/main/tools/mips16.py) and [firmware helper](https://github.com/1234205a/vsol-v2802rh-research/blob/main/tools/mips16_fw.py) were reference material only. Their reported CPU, addresses, task APIs and recovery characteristics were not imported as facts about this Askey. The public repository search service failed; the repository tree and these source files were retrieved directly from GitHub for inspection.

Private scratch `.local/askey-net-006/analysis/runtime-agent/` retains bounded disassembly excerpts for startup, allocation wrapper, task registration/initialization and the module-call routine, plus retrieved reference files. All runtime-derived code bytes and tooling remain ignored. This report contains only sanitized analytical evidence.
