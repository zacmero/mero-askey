# ASKEY-NET-007 — Resume and privileged CLI access test

Date: 2026-10-31, UTC−03:00. Status: explicitly authorized configuration import persisted exactly; support web login and privileged admin vendor CLI verified. No OS shell or native payload execution demonstrated.

## Re-established path and read-only observations

- SSH key access to the MSI works. Its Ethernet interface is `enp6s0`, address `192.168.15.3/24`, with the Askey at `192.168.15.1`; the recorded LAN neighbor matches. Wi-Fi remains the preferred control/default route.
- Telnet authentication survived the power cycle. `show version` still reports RTV9015VW, `BR_SO_RTK_V6.1.8t`, build `Feb 20 2017 19:16:25`, SDK `V1.2.1`, hardware family `8671x`. This session logged out cleanly.
- A single 16-byte RAM read at `0x8055a870` returned first word **`0x00016405`**, unlike the firmware initializer `0x0000ffff`. Static analysis maps this global to a sampled hardware register; its low 16 bits, `0x6405`, match one initialization branch. This is a measured snapshot, not yet a retail SoC model, clock or RAM-capacity identification. No direct MMIO access was used.
- Raw Telnet response log: ignored `.local/askey-net-007/responses.jsonl`, SHA-256 `6b6920674fa6960cfed56ec06a6d30c8b6b7a6f7956faef0e6cf94aec64f4ed7`.
- The firmware describes the `command` root as “show cli command tree.” Its name alone does not establish a POSIX shell; it was not invoked during this read-only reconnection.

## Fresh rollback and exact candidate

The fresh native export is byte-identical to the last approved configuration: 205061 bytes, SHA-256 `721cc151716e65c733f6f37d3ca18525b1d901380ca990355ed774d9716ff1b9`. Support login/export works. A first HTTP/1.1 request closed without a response; HTTP/1.0 and the complete native login form work.

Prepared candidate `.local/askey-net-007/config-cli-admin-candidate.img`: 205061 bytes, SHA-256 `4c5c8a2fe7c533aee6f7cff98ab2bd7e89345d8b9b8bbcface0d323d1cae7d44`. XML comparison and byte comparison confirm exactly two changes:

| Field | Before | Candidate |
| --- | --- | --- |
| `ENABLE_ADVANCE_PAGE` | `0x1` | `0x2` |
| `USERNAME_PASSWORD` record for `admin`: `PRIORITY` | `0x2` | `0x1` |

The support record retains priority `0x2`; passwords, service flags and other fields are identical. Existing static analysis predicts these changes preserve both mapped CLI capability bits for admin. Access mode also affects web policy. This prediction is not an execution result or a shell claim.

The owner explicitly answered **“Apply and test CLI access”** to this exact two-field import, its automatic reboot, and login/read-only CLI-help verification. Rollback is the fresh native export through the established support restore flow while management remains reachable. Recovery from total management lockout is not demonstrated; no factory reset, firmware write or hardware intervention is included.

## Import outcome and protocol correction

The first multipart submission put text fields before the file. It returned headerless HTML, causing `BadStatusLine`; a fresh export immediately afterward still matched the rollback exactly. That first attempt did not apply the candidate. No blind repeat was performed.

The corrected submission follows native form order, with the file first. A MIME parser independently checked the generated first part and exact file payload before sending. Immediately before this submission, the live export again matched the rollback hash.

At Unix time `1793463686.9094543`, the corrected import received HTTP 200 and the native **Autoboot** page in 3.484 seconds. The page advertises a 50-second countdown. No separate reboot request was sent. Raw responses, settings and request scripts remain private in `.local/askey-net-007/`.

## Verified post-reboot result

At Unix time `1793463750.1910195`, support login/export succeeded. The new 205061-byte export exactly matches the candidate hash and bytes, proving both intended fields persisted without additional export differences.

Admin Telnet login works. `sh` now enters **`XDSL#`**, replacing the previous `XDSL>`. The first post-reboot reader expected `XDSL>` and timed out after `sh`; its socket was closed, but its logout was not confirmed. A bounded prompt-discovery session established `XDSL#`, then successfully used `quit` → `$` and `exit` → `Username:`. The subsequent help-capture session also logged out cleanly.

Sending `?` at `XDSL#` returns the filtered root-command list. It now explicitly lists **`webdll`, `loaddll` and `chksum`**. Their names were matched as complete command lines, not substrings of error/help prose. `command` was not present as a root line in this live list. The firmware descriptor remains separate static evidence, not a demonstrated live entry.

Raw privileged help/session log: `.local/askey-net-007/privileged-cli.jsonl`, SHA-256 `f691843badbfa17e2d80362f65631f15388fabc13e3da679744308524d0f069d`. Verification metadata is in `cli-verification.json`; the fresh rollback, applied candidate and post-import export remain private alongside it.

The predicted access change is locally confirmed. No native handler was invoked, no memory write was attempted, and no custom payload or OS shell was demonstrated. Neither `id` nor `uname` was retested in this experiment; their earlier rejection remains historical evidence. The complete flash dump in `firmware/` remains the unchanged 2026-10-27 snapshot and therefore contains the earlier configuration.

Next work should establish native allocation, callback-return, lifetime, calling-convention and cache contracts before choosing any executable experiment. The live-session capability-field research road remains OPEN; reaching privileged CLI through the approved configuration change does not discard it.
