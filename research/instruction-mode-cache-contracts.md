# Instruction Mode and Cache Handling Contracts

**Status: Complete (Roadmap Step 1 resolved).**
Analysis date: 2026-10-31.
Artifact: captured `BR_SO_RTK_V6.1.8t` runtime (`.local/askey-net-006/analysis/runtime.bin`, 9,752,040 bytes, SHA-256 `b104789b795630eee7de1b50d64e49710535221f8baa6652021af6d00abb3941`, load base `0x80000000`).

---

## 1. Architectural & Processor Context

The captured firmware identifies an OSK RTOS runtime executing on a Realtek MIPS processor core (RLX5181/RLX5281 family, SDK V1.2.1, family `8671x`).
The architecture features a Harvard cache layout with separate L1 Instruction Cache (I-cache) and L1 Data Cache (D-cache), both with 16-byte cache line granularity.

### Processor Cache Control Register: CP0 Register 20
In standard MIPS32 specifications, Coprocessor 0 (CP0) register 20 is `XContext` (used for 64-bit TLB). In Realtek RLX cores, CP0 register 20 is repurposed as the **Cache Control Register (CCR)**:
- **Bit 1 (`0x0002`):** Hardware L1 Instruction Cache global invalidate.
- **Bit 7 (`0x0080`):** Cache configuration / enable bit (present in boot mask `0x0282`).
- **Bit 9 (`0x0200`):** Hardware L1 Data Cache global writeback-and-invalidate.

The boot initialization sequence at `0x8094939c` and `0x809493e4` configures CP0 register 20 with `0x0282` (`li t0, 642; mtc0 t0, c0_xcontext`), establishing active instruction and data caching.

---

## 2. Resident Cache Management Routines

### A. Global Instruction Cache Invalidation: `0x801679e8` (`flush_icache_all`)

- **Entry Address:** `0x801679e8` (even address; executes in MIPS32 mode).
- **Callable Interface:** `void flush_icache_all(void)`.
- **Calling Convention:** Standard MIPS o32 ABI. Preserves `ra`, `s0`, `s1`. Frame size: 32 bytes (`addiu sp, sp, -32`).
- **Disassembly & Operation (`0x801679e8`–`0x80167a5c`):**
  1. `0x801679fc`: Calls `0x80005dc4` to read `c0_status` into `v0`.
  2. `0x80167a08`: Masks `a0 = v0 & -2` (clears `IE` bit 0, disabling interrupts).
  3. `0x80167a14`: Calls `0x80005dcc` to write `c0_status`, disabling interrupts; saves original status in `s0`.
  4. `0x80167a1c`: Reads CP0 register 20: `mfc0 v0, c0_xcontext`.
  5. `0x80167a28`: Clears bit 1: `andi v0, v0, 0xfffd`.
  6. `0x80167a2c`: Writes CP0 register 20: `mtc0 v0, c0_xcontext`.
  7. `0x80167a38`: Sets bit 1: `ori v0, v0, 0x0002`.
  8. `0x80167a3c`: Writes CP0 register 20: `mtc0 v0, c0_xcontext` (triggers hardware L1 I-cache invalidation).
  9. `0x80167a48`: Moves saved status to `a0 = s0`.
  10. `0x80167a4c`: Restores `ra`, `s0`, `s1`, and tail-calls `0x80005dcc` (`mtc0 a0, c0_status; jr ra`), restoring interrupts and returning to caller.
- **Firmware Provenance:**
  - Called at startup (`0x80949748`) immediately after `memcpy` (`0x8000607c`) copies 384 bytes of executable exception vector code to `0x80000000`. This establishes its explicit purpose: ensuring instruction fetch reads newly copied executable code.

---

### B. Data Cache Range Writeback & Invalidate: `0x800065ec` / `0x800064e4`

- **Entry Addresses:**
  - `0x800065ec` (`dcache_flush_range`): takes `a0 = start_addr`, `a1 = length`.
  - `0x800064e4` (`dcache_flush_bounds`): takes `a0 = start_addr`, `a1 = end_addr`.
- **Calling Convention:** Standard MIPS o32 ABI (even address; MIPS32 mode). Preserves `ra`, `s0`, `s1`, `s2` in a 32-byte frame. Returns `v0 = 0`.
- **Disassembly & Operation:**
  - `0x800065ec`: Computes `addu a1, a1, a0` (converts length to end address), then tail-calls `0x800064e4`.
  - In `0x800064e4`:
    1. Checks `a0 & 0xe0000000`: if zero, branches to global flush at `0x80006528`.
    2. Computes `subu s2, a1, a0` (length).
    3. Evaluates `sltiu v0, length + 16, 8192`:
       - If `length + 16 >= 8192` (exceeds 8 KiB cache capacity), branches to global flush at `0x80006528`.
    4. **Global D-Cache Flush Path (`0x80006528`):**
       - `mfc0 v0, c0_xcontext`
       - `andi v0, v0, 0xfdff` (clears bit 9 / `0x200`)
       - `mtc0 v0, c0_xcontext`
       - `ori v0, v0, 0x0200` (sets bit 9 / `0x200`)
       - `mtc0 v0, c0_xcontext`
       - Jumps to epilogue and returns `v0 = 0`.
    5. **Line-by-Line Range Flush Path (`0x8000655c`–`0x800065bc`):**
       - Masks start address to KSEG0: `s0 = (a0 & 0x1fffffff) | 0x80000000`.
       - Rounds length to 64-byte block boundaries: `s2 = ((length + 79) >> 6) << 6`.
       - Disables interrupts via `0x80005dc4` / `0x80005dcc`.
       - Computes end address `s2 = s0 + s2`.
       - Tight loop stepping 64 bytes (`0x800065a8`–`0x800065bc`):
         ```assembly
         800065a8: cache 0x15,  0(s0)
         800065ac: cache 0x15, 16(s0)
         800065b0: cache 0x15, 32(s0)
         800065b4: cache 0x15, 48(s0)
         800065b8: addiu s0, s0, 64
         800065bc: bne   s0, s2, 0x800065a8
         ```
         In MIPS/RLX architecture, opcode `cache 0x15` is **Hit Writeback and Invalidate D-Cache** (bits [1:0] = 1: D-cache; bits [4:2] = 5: hit-writeback-invalidate).
       - Restores interrupts via `0x80005dcc`.
       - Returns `v0 = 0`.
- **Firmware Provenance:**
  - Invoked across network drivers (`0x80014c2a`, `0x80014ccc`, `0x80161a6c`, `0x80242d3c`) passing packet control block payload pointer (`88(s0)`) and length (`20(s0)`), ensuring cache-to-RAM coherency for DMA buffers.
  - Invoked at `0x8013621c` passing 4096-byte page ranges.

---

## 3. Instruction Mode & Interlinking Rules

1. **Instruction Mode Switching:**
   - Big-endian MIPS32 and MIPS16e coexist in the firmware.
   - Any indirect jump or call (`jr reg` / `jalr reg`) checks the low-order bit (bit 0) of the target address:
     - **Bit 0 = 0 (Even Address):** CPU transitions to or remains in **MIPS32** execution mode.
     - **Bit 0 = 1 (Odd Address):** CPU transitions to or remains in **MIPS16** execution mode.
2. **`webdll` Call Context:**
   - Handler `0x802a277c` performs an unmasked `jalr v0` to the parsed 32-bit address argument.
   - Providing an even address guarantees the CPU enters our routine in **pure MIPS32 mode**.
   - Pure MIPS32 provides full access to all 32 general-purpose registers (`$zero` through `$ra`), avoiding MIPS16 register-starvation constraints.

---

## 4. Memory Segments: KSEG0 vs KSEG1

In 32-bit MIPS architecture:
- **KSEG0 (`0x80000000`–`0x9fffffff`):** Cached, unmapped. Accesses pass through L1 D-cache and I-cache.
- **KSEG1 (`0xa0000000`–`0xbfffffff`):** Uncached, unmapped. Accesses bypass L1 D-cache and I-cache entirely, directly hitting physical DRAM.
- Both segments map to the identical physical address space:
  $$\text{Physical Address} = \text{Virtual Address} \ \& \ \text{0x1fffffff}$$

For an allocated `xfile` RAM buffer at KSEG0 address `P = 0x8095xxxx`:
- The uncached KSEG1 alias is `P_{\text{uncached}} = P \mid \text{0x20000000} = \text{0xa095xxxx}`.
- In KSEG1, instruction fetch is guaranteed to bypass L1 I-cache, reading directly from physical DRAM.
- However, since `memory set` writes to KSEG0 (`0x80...`), dirty cache lines must be flushed to physical DRAM via `0x800065ec` before instruction fetch from either KSEG0 or KSEG1 can safely observe the new code.

---

## 5. End-to-End Cache Coherency Procedure for Roadmap Step 3

When placing and executing code in RAM:
1. **Memory Placement:** Write code and mailbox placeholder into owned `xfile` RAM buffer at `data` (`0x80xxxxxx`) using aligned 32-bit stores via `memory set long`.
2. **Data-Cache Writeback:** Call `0x800065ec(data_addr, code_len)`:
   - Flushes dirty D-cache lines to physical DRAM.
3. **Instruction-Cache Invalidation:** Call `0x801679e8()`:
   - Toggles bit 1 in CP0 register 20, invalidating L1 I-cache so that subsequent instruction fetches read fresh code from physical DRAM.
4. **Execution:** Invoke `webdll <entry_addr>` (where `<entry_addr>` is an even address).
   - CPU executes entry code in MIPS32 mode.
5. **Two-Call Return Contract:**
   - Entry routine writes nonce to mailbox, preserves calling registers, and returns the address of cleanup callback in `v0`.
   - `webdll` immediately calls cleanup callback.
   - Cleanup callback writes second nonce, restores state, and returns cleanly to CLI dispatcher.
