# Minimal Native Entry and Returned Callback Design

**Status: Complete (Roadmap Step 2 resolved).**
Artifact tool: [`tools/build_native_payload.py`](../tools/build_native_payload.py)
Target architecture: Realtek RLX / MIPS32 big-endian (`-mips32r2 -EB`)
Total binary size: 576 bytes (512-byte code region + 64-byte mailbox)
Binary SHA-256: `c7db7a20722b2b37fa2f19390c904af1c4a5a832da50a819fe94a1381e27c3e0`

---

## 1. Objectives and Constraints

Step 2 of the native execution roadmap requires preparing a minimal entry and returned callback pair that:
1. Conforms strictly to the `webdll` two-call contract (`f(magic, iface) -> next_fn; next_fn(magic, iface)`).
2. Preserves all calling state and register conventions without modifying callee-saved registers or corrupting the stack.
3. Operates position-independently (PIC) so it can execute at any dynamically allocated `xfile` RAM buffer address.
4. Avoids dependence on standard library printf, console stdout, or Linux system calls.
5. Writes distinct, nonce-bearing status markers to the allocated RAM mailbox for independent verification via `memory show`.

---

## 2. Calling Contract & Register Conventions

### Caller Behavior (`webdll` at `0x802a277c`)
1. **Entry Invocation:**
   - Calls target via `jalr v0`.
   - Arguments passed:
     - `a0 = 0x12345678` (magic validation constant).
     - `a1 = 0x805f1648` (CLI interface descriptor).
   - Caller `$ra` contains a MIPS16-tagged return address (bit 0 = 1, pointing to `0x802a279a`).
   - Expects return value in `$v0`: a valid, callable 32-bit function pointer to the cleanup routine.
2. **Intermediate Logging:**
   - Prints `going to unloadFunc=0x%x` using the returned `$v0`. (Output routes to UART MMIO backend).
3. **Cleanup Invocation:**
   - Calls returned pointer via `jalr s1`.
   - Arguments reloaded: `a0 = 0x12345678`, `a1 = 0x805f1648`.
   - Caller `$ra` points to `0x802a27ae` (MIPS16 tagged).
   - Cleanup routine returns cleanly; dispatcher subsequently resets return status to 1 and returns to the CLI prompt (`XDSL#`).

### Callee Register & Stack Discipline
- **Callee-saved registers:** `$s0`–`$s8`, `$gp`, and `$sp` are **never touched**.
- **Stack pointer `$sp`:** Untouched. No stack frame allocation is required.
- **Temporaries used:** `$t0`, `$t1`, `$t2`, `$t9`, and `$v0`.
- **Return address preservation:** `$ra` is saved into `$t9` before the PC-discovery branch, and restored from `$t9` immediately before `jr $ra`.

---

## 3. Position-Independent Code (PIC) Architecture

Because the `xfile` RAM filesystem assigns buffer base addresses dynamically at runtime (e.g. `0x8095xxxx`), the payload cannot use hardcoded absolute pointers.

Both `entry_func` and `cleanup_func` employ standard MIPS PC-relative discovery via `bal`:
```assembly
    bal     get_pc
    nop
get_pc:
    move    $t0, $ra    # $t0 = absolute address of get_pc
```
From `$t0`, the assembler calculates relative offsets to the labels:
- `entry_func`:
  - `cleanup_func = $t0 + (cleanup_func - entry_get_pc)`
  - `mailbox = $t0 + (mailbox - entry_get_pc)`
- `cleanup_func`:
  - `mailbox = $t0 + (mailbox - cleanup_get_pc)`

This eliminates relocations completely (`readelf -r` confirms 0 relocations), enabling execution at any address in KSEG0 (`0x80...`) or KSEG1 (`0xa0...`).

---

## 4. Mailbox Layout & Verification Nonces

The payload writes verification records to the 64-byte mailbox at payload offset `0x200` (512 bytes):

| Offset | Field Name | Written Value | Significance |
| :--- | :--- | :--- | :--- |
| `+0x00` | `stage1_magic` | `0x454e5452` ("ENTR") | Entry function was reached and executed |
| `+0x04` | `stage1_nonce` | `0x11112222` | Confirms Stage 1 execution nonce |
| `+0x08` | `stage1_a0` | `0x12345678` | Verifies `webdll` argument 0 passed to entry |
| `+0x0c` | `stage1_a1` | `0x805f1648` | Verifies `webdll` argument 1 passed to entry |
| `+0x10` | `stage1_cleanup` | Dynamic address | Cleanup routine pointer returned to `webdll` in `$v0` |
| `+0x14` | `stage2_magic` | `0x434c4e50` ("CLNP") | Cleanup function was reached and executed |
| `+0x18` | `stage2_nonce` | `0x33334444` | Confirms Stage 2 execution nonce |
| `+0x1c` | `stage2_a0` | `0x12345678` | Verifies `webdll` argument 0 passed to cleanup |
| `+0x20` | `stage2_a1` | `0x805f1648` | Verifies `webdll` argument 1 passed to cleanup |
| `+0x24` | `success_flag` | `0x53554343` ("SUCC") | Both stages completed cleanly |

---

## 5. Binary Layout

- **Offset `0x00`–`0x47` (72 bytes):** `entry_func` (18 instructions).
- **Offset `0x48`–`0x7f` (56 bytes):** Zero-padding.
- **Offset `0x80`–`0xcf` (80 bytes):** `cleanup_func` (20 instructions).
- **Offset `0xd0`–`0x1ff` (304 bytes):** Zero-padding.
- **Offset `0x200`–`0x23f` (64 bytes):** Mailbox reservation.

Total: 576 bytes. Built and verified via [`tools/build_native_payload.py`](../tools/build_native_payload.py).
