# Instruction-mode/cache checkpoint — 2026-10-31

Status: **RESOLVED; step 1 complete.** Traced and verified against captured runtime `b104789b795630eee7de1b50d64e49710535221f8baa6652021af6d00abb3941`. Detailed contracts and disassembly are documented in [instruction-mode and cache contracts](instruction-mode-cache-contracts.md).

---

## 1. Resolved Mechanics

- **Processor Cache Architecture:** Realtek RLX core (RLX5181/RLX5281 family, MIPS32 with MIPS16e extensions). Coprocessor 0 register 20 is the Cache Control Register (CCR).
  - Bit 1 (`0x0002`): Hardware L1 Instruction Cache global invalidate.
  - Bit 7 (`0x0080`): Cache configuration bit (in boot mask `0x0282`).
  - Bit 9 (`0x0200`): Hardware L1 Data Cache global writeback-and-invalidate.
- **Global Instruction Cache Invalidation (`0x801679e8`):**
  - MIPS32 function, standard o32 ABI, frame size 32 bytes.
  - Reads `c0_status` via `0x80005dc4`, clears `IE` (bit 0) to disable interrupts via `0x80005dcc`.
  - Toggles bit 1 (`0x2`) in CP0 register 20 (`c0_xcontext`), triggering hardware L1 I-cache invalidation.
  - Restores `c0_status` and returns cleanly.
  - Directly called at boot (`0x80949748`) immediately following `memcpy` (`0x8000607c`) of executable exception vector code to `0x80000000`.
- **Data Cache Range Writeback & Invalidation (`0x800065ec` / `0x800064e4`):**
  - MIPS32 functions, standard o32 ABI, frame size 32 bytes, returns `v0 = 0`.
  - `0x800065ec(void *addr, size_t length)` computes `end = addr + length` and tail-calls `0x800064e4(addr, end)`.
  - For ranges `< 8192` bytes: masks address to KSEG0 (`(addr & 0x1fffffff) | 0x80000000`), disables interrupts, and executes a loop of four `cache 0x15` instructions (Hit Writeback Invalidate D-cache) per 64-byte block.
  - For ranges `>= 8192` bytes: toggles bit 9 (`0x200`) in CP0 register 20 for full hardware D-cache writeback-and-invalidate.
  - Called across network drivers (`0x80014c2a`, etc.) on packet control block payload pointers (`88(s0)`) and lengths (`20(s0)`).
- **Instruction Mode Interlinking:**
  - Even target address for `webdll <addr>` forces execution in **MIPS32 mode** with full register availability.
- **Segment Semantics:**
  - KSEG0 (`0x80...`) is cached; KSEG1 (`0xa0...`) is uncached. Both map to identical physical DRAM.

Step 1 criteria are satisfied. Roadmap Step 2 (prepare entry/returned-callback pair) is now unblocked.
