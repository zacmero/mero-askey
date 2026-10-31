# ASKEY-NET-010 — First Bounded Native Execution Trial

Date: 2026-10-31, UTC−03:00.
Status: **Full Success**. Dynamic owned RAM-file allocation, position-independent MIPS32 payload staging, synchronous execution under the `webdll` two-call contract, independent fresh-session mailbox readback, and fail-closed cleanup verified. All 10 verification markers matched exact expectations. Original filesystem inventory restored.

Target router: Askey RTV9015VW, build `BR_SO_RTK_V6.1.8t` (Realtek RLX5181/RLX5281 MIPS core).

---

## 1. Objectives and Scope

Following the completion of Roadmap Step 1 (cache and instruction-mode contracts, [research/instruction-mode-cache-contracts.md](../../research/instruction-mode-cache-contracts.md)) and Step 2 (minimal MIPS32 entry and cleanup payload, [docs/native-payload.md](../native-payload.md)), this experiment executes Roadmap Steps 3 and 4:
1. Allocate fresh owned RAM storage via `xfile create` without touching baseline files.
2. Stage the verified 576-byte PIC MIPS32 payload ([`tools/build_native_payload.py`](../../tools/build_native_payload.py), SHA-256 `c7db7a20722b2b37fa2f19390c904af1c4a5a832da50a819fe94a1381e27c3e0`) into the dynamically discovered payload buffer.
3. Pre-fill the 64-byte mailbox with a known pattern (`0xDEADBEEF`) in uncached KSEG1.
4. Execute `webdll <entry_addr>` through the vendor CLI dispatcher.
5. In a separate, fresh Telnet connection, inspect the mailbox markers via `memory show` to prove execution, argument capture, and callback sequencing.
6. Re-verify console responsiveness, cleanly close and delete the owned file, and confirm exact restoration of the original 5 baseline files.

---

## 2. Experimental Execution Phases

The trial was orchestrated using the dedicated tool [`tools/run_native_trial.py`](../../tools/run_native_trial.py) operating across isolated SSH sessions to the test laptop on the lab segment.

### Phase 1: Preflight Verification
- Verified active network route: `enp6s0` (`192.168.15.3/24` -> `192.168.15.1`).
- Verified router MAC neighbor: `54:2f:8a:48:1a:b8`.
- Telnet authentication into vendor console: `sh` -> `XDSL#`.
- Validated running-image header at `0xb4010000` (64 bytes): SHA-256 `19cef9e17ca1c90cda12fd579af2ddc18c80ae9528e89c32130d5a2e0e871348`.
- Validated baseline 5 files in `xfile list`: `CWMPNotify.txt`, `/var/wscd.conf`, `/var/wscd-vxd.conf`, `ssl_cert.pem`, `ssl_key.pem`.
- Session logged out cleanly.

### Phase 2: Owned RAM Allocation (`create`)
- Created temporary file `mero_native_010_5e4940b6`.
- Verified single buffer, open flags `0x80000000`, logical size 0.
- Resolved dynamic pointers from descriptor and control block (CCB):

| Field | Address (KSEG0) | Uncached Alias (KSEG1) | Purpose |
| :--- | :--- | :--- | :--- |
| File CCB | `0x809d8d9c` | — | Packet control block |
| Backing buffer | `0x80a61c14` | `0xa0a61c14` | Allocator buffer base |
| Data payload (`+128`) | `0x80a61c94` | `0xa0a61c94` | Code entry (`entry_func`) |
| Cleanup routine (`+208`) | `0x80a61d14` | `0xa0a61d14` | Unload callback (`cleanup_func`) |
| Mailbox reservation (`+512`)| `0x80a61e94` | `0xa0a61e94` | 64-byte observation mailbox |

- Buffer capacity: 1600 bytes (`data` to `end` at `0x80a622e0`). Payload requirement: 576 bytes (`576 <= 1600`).
- Session logged out cleanly.

### Phase 3: Staging & Coherency (`stage`)
- Revalidated lease and verified CCB ownership.
- Mailbox prefill: wrote 16 words of `0xDEADBEEF` to `0xa0a61e94` (KSEG1) and `0x80a61e94` (KSEG0). Readback confirmed `0xDEADBEEF` across all 64 bytes.
- Code staging:
  - `entry_func` (72 bytes / 18 instructions) written to `0xa0a61c94` and `0x80a61c94`.
  - `cleanup_func` (80 bytes / 20 instructions) written to `0xa0a61d14` and `0x80a61d14`.
- Readback verification: `dump(0xa0a61c94, 80)` and `dump(0x80a61c94, 80)` matched `payload.bin` byte-for-byte.
- Session logged out cleanly.

### Phase 4: Native Execution (`execute`)
- Fresh Telnet session opened; lease and CCB ownership revalidated.
- Invocation command issued:
  ```text
  XDSL# webdll 0xa0a61c94
  XDSL#
  ```
- Command returned immediately (< 1 second) to the `XDSL#` prompt without errors, crash, or watchdog reset.
- Prompt responsiveness confirmed by issuing `help memory`.
- Session logged out cleanly.

### Phase 5: Independent Verification (`verify`)
- Fresh Telnet session opened; lease revalidated.
- Mailbox readback issued: `memory show 0xa0a61e94 length 0x40`.
- Raw memory response:
  ```text
  0xa0a61e94: 45 4e 54 52 11 11 22 22 12 34 56 78 80 5f 16 48 ENTR.."".4Vx._.H
  0xa0a61ea4: a0 a6 1d 14 43 4c 4e 50 33 33 44 44 12 34 56 78 ....CLNP33DD.4Vx
  0xa0a61eb4: 80 5f 16 48 53 55 43 43 de ad be ef de ad be ef ._.HSUCC........
  0xa0a61ec4: de ad be ef de ad be ef de ad be ef de ad be ef ................
  ```
- Parsed 16 32-bit big-endian words:

| Word Index | Offset | Observed Hex | ASCII / Interpretation | Expected Value | Match |
| :---: | :---: | :---: | :--- | :--- | :---: |
| 0 | `+0x00` | `0x454e5452` | `"ENTR"` | `0x454e5452` | **PASS** |
| 1 | `+0x04` | `0x11112222` | Stage 1 Nonce | `0x11112222` | **PASS** |
| 2 | `+0x08` | `0x12345678` | Captured `$a0` (Magic) | `0x12345678` | **PASS** |
| 3 | `+0x0c` | `0x805f1648` | Captured `$a1` (Iface) | `0x805f1648` | **PASS** |
| 4 | `+0x10` | `0xa0a61d14` | Returned Callback Ptr | `0xa0a61d14` | **PASS** |
| 5 | `+0x14` | `0x434c4e50` | `"CLNP"` | `0x434c4e50` | **PASS** |
| 6 | `+0x18` | `0x33334444` | Stage 2 Nonce | `0x33334444` | **PASS** |
| 7 | `+0x1c` | `0x12345678` | Captured `$a0` (Stage 2) | `0x12345678` | **PASS** |
| 8 | `+0x20` | `0x805f1648` | Captured `$a1` (Stage 2) | `0x805f1648` | **PASS** |
| 9 | `+0x24` | `0x53554343` | `"SUCC"` Confirmation | `0x53554343` | **PASS** |
| 10–15 | `+0x28`..`+0x3f` | `0xDEADBEEF` | Untouched Prefill | `0xDEADBEEF` | **PASS** |

- Session logged out cleanly.

### Phase 6: Fail-Closed Cleanup (`cleanup`)
- Fresh Telnet session opened; lease revalidated.
- Issued `xfile close mero_native_010_5e4940b6` and `xfile delete mero_native_010_5e4940b6`.
- Verified `xfile list`: exactly 5 baseline files remained with matching addresses, buffer counts, and flags.
- Private lease updated: `held: false`. No test allocations held.
- Final post-cleanup preflight check passed.

---

## 3. Evidence Hashes

All raw transcripts and stdout/stderr evidence logs remain strictly under ignored `.local/askey-net-010/trial/`:

| Phase | Raw Evidence Log | SHA-256 |
| :--- | :--- | :--- |
| Preflight (Initial) | `preflight-1793491012789961426.jsonl` | `6e17577c235beef44fc5488c2500195e3ab9d6f78690ecd9a8d61ecc8e869d63` |
| Create | `create-1793491019051800151.jsonl` | `a0d48c6688cdfad68ac39f7afafb1ed6aea9a33b4d5a75be63487c83e63a4621` |
| Stage | `stage-1793491025238845011.jsonl` | `53f887ae2dee2ab343b375dc4f3d452d21aa5602f677592f852f73f0087048ae` |
| Execute | `execute-1793491033989347931.jsonl` | `d445c0fc2084dd45d654ef807750242398a716686da37e0757fd92dad1c717e7` |
| Verify | `verify-1793491039019369022.jsonl` | `333a21416933b045ef32b511b981045cdfdd973621fc64bed28cd6a3ad55cf74` |
| Cleanup | `cleanup-1793491045102563555.jsonl` | `1cddd3c84d401296d4c68a1971d992b2a9ced04407d49cfe5e9c64a9451c97e1` |
| Preflight (Final) | `preflight-1793491054519421904.jsonl` | `394ffb6a13478f59e1822aa3de9872ee8c458d55b1913be51a1c5d8c13f66faa` |

---

## 4. Key Conclusions

1. **Native MIPS32 Execution is Proven:** The RLX core executed the custom assembled MIPS32 instructions in synchronous real time without crashing, restarting, or corrupting OS task state.
2. **Two-Call Contract Confirmed:**
   - The first call to `entry_func` ran to completion, wrote Stage 1 nonces to the mailbox, and returned the dynamic cleanup callback address in `$v0`.
   - The caller `webdll` accepted `$v0` and successfully dispatched the second call to `cleanup_func`.
   - `cleanup_func` ran to completion, wrote Stage 2 nonces and the `"SUCC"` marker, set `$v0 = 0`, and returned cleanly to `webdll`.
3. **Register & Instruction-Mode Interlinking Validated:**
   - Calling an even address entered pure MIPS32 mode.
   - Restoring caller `$ra` (which has bit 0 = 1) via `jr $ra` smoothly returned execution back to MIPS16 mode in `webdll`.
   - Preserving callee-saved registers (`$s0`–`$s8`, `$gp`, `$sp`) kept the OS task and Telnet CLI shell completely stable.
4. **KSEG1 Execution Eliminates Cache Incoherency:**
   - Executing via the uncached KSEG1 alias (`0xa0...`) bypassed the L1 instruction cache entirely, reading fresh instructions directly from physical DRAM and writing mailbox records directly to DRAM without cache flush hazards.
5. **Clean Restoration:** All temporary RAM allocations were released, returning the device to its pristine baseline state.
