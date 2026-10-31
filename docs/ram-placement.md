# Temporary RAM placement and observation

Verified on the owner's RTV9015VW / `BR_SO_RTK_V6.1.8t`, 2026-10-31. A supported RAM-file allocation, guarded inert-data placement, fresh-session readback and explicit cleanup all passed. This establishes a storage/write/readback path; execution permissions, instruction-cache behavior and a custom native callback remain untested.

The implementation is [probe_ram_placement.py](../tools/probe_ram_placement.py). It uses the existing private SSH/target/login files and strict dump parser. It creates no listener, persistent setting or firmware image. Evidence stays under ignored `.local/`.

## How the region is owned

The native `xfile create` operation opens a uniquely named RAM file. `xfile list` supplies its control-block address. The probe finds its unique matching descriptor, checks the owned filename, open state, single-buffer/zero-length state and pointer relationships, then loads the separate data pointer from control-block offset +88.

The default native path requested 1600 bytes of packet data. The allocator records backing storage at +84 and advances the data pointer by 128 bytes of headroom. The probe validates both that relationship and the backing-end marker before writing. It does not treat the displayed control block itself as payload storage.

The layout reserved within that allocation is:

| Offset from payload pointer | Purpose | Live test coverage |
| --- | --- | --- |
| 0–511 | Region reserved for a future small native image | First 64 bytes received inert marker data. No instruction image was executed. |
| 512–575 | 64-byte observation mailbox | All 64 bytes written and read back exactly. |
| 576–1599 | Unused packet data | Not written by this test. |

The mailbox starts with ASCII `MRO9`, a big-endian version word of 1, a fresh 16-byte nonce, and 40 zero bytes. It is an observation record, not an implemented native-entry/status protocol yet.

## Independent observation

The test made 32 aligned 32-bit stores, limited to the two 64-byte regions. A single-word pilot was read back before the remaining stores. Strict address-contiguous `memory show` parsing then verified the complete bytes.

A separate SSH/Python process opened a fresh Telnet connection, revalidated file ownership and pointers, and independently read both regions. Both nonce-bearing records matched exactly. This path uses Telnet's memory-display output, so it does not depend on the fixed-context printf-like callback or attached serial hardware.

A future native routine can use an agreed mailbox protocol in owned storage, with the host reading the same pointer alias. That routine's stores, completion and returned callback have not yet been demonstrated. A successful RAM round trip does not prove instruction fetching or cache coherency.

## Guarded workflow

Run on mero-machine from this repository:

```sh
rtk python3 tools/probe_ram_placement.py preflight --run-dir .local/ram-placement-next
rtk python3 tools/probe_ram_placement.py create --run-dir .local/ram-placement-next
rtk python3 tools/probe_ram_placement.py write --run-dir .local/ram-placement-next
rtk python3 tools/probe_ram_placement.py read --run-dir .local/ram-placement-next
rtk python3 tools/probe_ram_placement.py cleanup --run-dir .local/ram-placement-next
```

`write` places fixed inert test records, not a supplied executable. `read` is a new connection and checks against the recorded expected bytes. Use the same run directory for all phases of one allocation. The script pins the measured 64-byte running-image header, checks route/source/neighbor, restricts read ranges, checks live ownership before stores and accepts writes only within the two test regions. Raw logs have unique names.

Successful `create` holds a RAM file across disconnects; session logout alone does not release it. `cleanup` uses its matching allocation record, closes/deletes only that file and checks the original inventory. If a phase fails, inspect its private log and use the matching cleanup path rather than reuse old addresses.

## Completed test state

The tested allocation was closed/deleted; the original five-file inventory and metadata were restored. **No active allocation from this experiment remains.** Historical addresses in the [experiment record](experiments/askey-net-009.md) must not be reused. Recreate and revalidate storage for each future trial.

All four test sessions logged out cleanly. The delivered tool's target/header preflight also passed live. Detailed evidence hashes and the creation-parser surprise are recorded in [ASKEY-NET-009](experiments/askey-net-009.md).
