# Captured firmware: image, web controls and recovery evidence

Offline analysis on **2026-10-27**, of the owner's RTV9015VW image captured in [ASKEY-NET-006](../docs/experiments/askey-net-006.md). No firmware was executed, no router request was sent, and no configuration, service or flash contents were changed by this analysis. Proprietary page bodies and credentials remain private.

## Scope and confidence

The complete **running image** and completed **8 MiB full-flash file** are independently verified offline. The final dump contains an erased reported backup-image slot and two matching, checksum-valid settings containers. These are actual complete-region observations, not extrapolations from capture prefixes. File integrity does not establish a working recovery method or a safe updater input.

Evidence below distinguishes byte observations, static feature evidence and unresolved behavior. Source files are the captured binary in `firmware/` and ignored derived artifacts under `.local/askey-net-006/analysis/`. Independent verification artifacts are under its `image-agent/` directory.

## Image structure independently verified

`firmware/rtv9015vw-br_so_rtk_v6.1.8t-run-image.bin` contains **2,954,688 bytes**, SHA-256 **`74ff08b030051cce67e4c637cbb46d7cc7dfd629e04271a9fb83ebab3cc76ad6`**. The run-image flash offset is `0x10000`; its end is therefore `0x2e15c0`, exclusive.

All offsets in the next table are relative to that image, not to flash. Integers are interpreted as big-endian unless stated otherwise. Field semantics without a decoded consumer remain unassigned.

| Image offset | Observed value | What is established |
| --- | --- | --- |
| `0x00` | `0xa0000003` | Header identifier/flags value; bit meanings unverified |
| `0x04` | `0x80000000` | Runtime header diagnostic names this field `dramaddr`; actual loader use is a separate question |
| `0x08` | `0x002d1580` | Exactly 2,954,624 bytes: payload length **excluding** the 64-byte header |
| `0x0c` | `0x80949288` | Runtime header diagnostic names this field `entry` |
| `0x10` | `0xe020` (16 bits) | Matches the independently calculated payload checksum |
| `0x12` | `0x05` | Runtime header diagnostic names this byte `type`; downstream code also tests individual bits |
| `0x13` | Timestamp text | `Mon Feb 20 19:20:51 2017`; packaging metadata, not proof of the router's present clock |
| `0x2c` | Image/version text | Runtime header diagnostic calls this `version`; text terminates before `0x34` |
| `0x34` | `0x76000000` | The IC compatibility routine compares this 32-bit field against the current image's corresponding field |
| `0x38` | `0x0004b780` | Exactly the byte distance from payload start to the primary runtime stream |
| `0x3c` | `0xbfc10000` | Runtime diagnostic calls it `flashp`; the loader can use it as a destination in one branch, with other branches selecting layout addresses |

The checksum calculation uses every payload byte, including padding: sum consecutive big-endian 16-bit words, fold carries back into the low 16 bits until none remain, then invert those 16 bits. The result is **`0xe020`**, equal to the stored field. This is a reproducible integrity check, **not a cryptographic signature**; it does not prove that the updater performs no additional checks.

The payload has three observable parts:

| Image range, exclusive end | Contents | Verification |
| --- | --- | --- |
| `0x40..0x3c062` | 52 consecutive LZMA-alone streams | Each independently decompressed successfully with an end-of-stream indication |
| `0x3c062..0x4b7c0` | 63,326 bytes following the compressed page streams | Begins with a GIF signature; includes image assets; the whole range has not been individually catalogued |
| `0x4b7c0..0x2d15c0` | Primary compressed runtime and one trailing zero byte | Complete runtime independently decoded using installed `7z` |

The 52 page streams decode to **1,213,785 bytes**, SHA-256 **`aaec79eb50f5e5b9d814363a3a87163198a8d95880d3e0033b535dc55d681364`**. Independent concatenated output exactly matches the existing `web-pages.decoded`. The first stream starts at image `0x40`, occupies 6,308 compressed bytes and yields 32,742 bytes. The final stream starts at `0x3b9db`, occupies 1,671 bytes and yields 3,760 bytes.

The runtime stream has LZMA properties byte `0x6f` (`lc=3`, `lp=2`, `pb=2`), an 8 MiB dictionary, and an explicit little-endian output size of **9,752,040 bytes**. The installed Python decoder rejects these properties; its failure is not evidence of damaged firmware. `7z` accepts the stream after removing **one zero byte from the decoder input only**, exits successfully and produces SHA-256 **`b104789b795630eee7de1b50d64e49710535221f8baa6652021af6d00abb3941`**. This output exactly matches `runtime.bin`. Preserve the original captured image, including its tail byte.

The header timestamp is later than the device-reported application build time `Feb 20 2017 19:16:25`. Separate packaging and application build timestamps are a plausible explanation; neither is a firmware-installation date.

## Compiled web and maintenance controls

These are observations of extracted templates, **not live endpoint tests**. Template names, form targets and server-side function names establish compiled features. They do not establish HTTP reachability, account authorization, current settings, safe effects or a usable OS shell.

| Extracted page | Static control evidence | Limitation |
| --- | --- | --- |
| `telnet_onoff.htm` | POST to `form2Telnet.cgi`; a `telnet` radio field uses `0`/`1` | A terminal-service control, not shell or privilege escalation proof |
| `modify_hide.htm` | “Hidden Settings”; POST to `formModify.cgi`; Telnet, wireless/account fields, MAC/serial fields, and “MP Web Access” controls; separate POST to `form2factorytestmode.cgi` | MP/factory semantics and actual authorization remain unverified; no values were submitted |
| `debug.htm` | POST to `form2debug.cgi`; SAR diagnostics and ATM/Ethernet port mirroring | The inspected page contains no general command-execution field |
| `upload.htm` | Multipart firmware POST to `form2file.htm` | Firmware write flow, not a firmware export |
| `replaceboot.htm` | Separate multipart firmware and boot-file forms; boot target `form2fileboot.cgi` | Compiled bootloader upload flow is not a recovery plan or authorization to use it |
| `saveconf.htm` | Configuration save POST to `form2saveConf.cgi`; configuration import POST to `form2fileConf.htm` | Exports/imports settings, not an established full-flash backup |
| `userconfig.htm` | Account-management POST to `form2userconfig.cgi`; dynamic privilege table and account rendering | Web-account roles must not be equated with native-console or OS privileges |

`modify_hide.htm`, `replaceboot.htm`, `telnet_onoff.htm`, `debug.htm` and `ledtest.htm` are absent from all four extracted `*Menu_vd.js` variants inspected. This means they are omitted from those menu definitions, not that their endpoints are unauthenticated or reachable.

The account-settings template contains a hidden privilege selector with value `2` labelled “Root”. This is a **web UI label**. No evidence here maps it to the native console's denied diagnostic/configuration privileges, proves account modification is accepted, or demonstrates arbitrary native execution.

The generic account template's selection callback accepts a password argument, assigns it to a hidden password field, and compares the old-password entry against that field in JavaScript. The server-generated account table and handler must be inspected before concluding which password representation is supplied or whether server-side checks are missing. No live account data was fetched for this analysis.

The login template computes MD5 of the entered username and password into separate POST fields and submits a distinct server-rendered `loginW` field. No per-password salt appears in those two browser-side MD5 expressions. The meaning and server verification of `loginW` remain unverified. Browser-side hashing by itself does not establish a challenge-response protocol or transport encryption.

Many mutation forms request `SendKeyCSRF()`, including hidden maintenance and upload forms. This establishes intended token insertion, **not verified enforcement**. Some templates have malformed-looking repeated `value=` text; browser parsing and server acceptance have not been tested. The config-save form differs from the import form; a missing visible token on one template is not enough to conclude an exploitable authorization failure.

## Hidden controls, menu flag and service-mode alias

This follow-up combines extracted template callbacks with static MIPS16 disassembly. Addresses in this section are runtime virtual addresses, using the decoded runtime's `0x80000000` base. Registry entries for MIPS16 code have their low bit set; the instruction-start addresses below clear that tag. No handler was invoked.

### `ENABLE_ADVANCE_PAGE` is rendered as `ServiceMode`

The MIB descriptor at `0x805f71ec` identifies **`ENABLE_ADVANCE_PAGE`, ID `0x8b4c`**, a four-byte field at global `0x807c96a8`, with a compiled default string of `0`. Getter `0x802b7990` returns that field. Two web renderers pass its return value to the format string at `0x804f4928`, which emits the JavaScript variable **`ServiceMode`**:

- Simple renderer `0x8041301c` calls the getter through literal `0x80413084`, then formats its return at `0x80413054..0x8041305c`.
- `IncludeWebAllJsFile` implementation `0x8041308c` calls it at `0x80413196..0x8041319a`, then formats its return at `0x8041319c..0x804131a2`.

Thus a rendered `ServiceMode` value is a web alias for this configuration flag in these paths, **not evidence of a separate service-mode configuration field**. Relate a live value to the time and authentication context of its capture; a page captured before a configuration change is not the current state.

In the `index.htm` menu-rendering path, the same function first checks **`PADRAO_WIFI_ONLY`** through getter `0x802b799c`, then explicitly branches on the advanced-page value:

| Stored conditions | Selected menu | Rendered `AccessClass` |
| --- | --- | --- |
| `PADRAO_WIFI_ONLY == 1` | `wifiOnlyMenu_vd.js` | `1` if advanced-page value is `2`; otherwise `0` |
| Wi-Fi-only value differs from `1`; advanced-page value `2` | `adminMenu_vd.js` | `1` |
| Wi-Fi-only value differs from `1`; advanced-page value `1` | `user04Menu_vd.js` | `0` |
| Wi-Fi-only value differs from `1`; other advanced-page values | `userMenu_vd.js` | `0` in this path |

The relevant branches are `0x804130d8..0x8041314e`; literal `0x804131d0` identifies the advanced-page getter. The three non-Wi-Fi menus contain 50, 48 and 44 distinct page targets respectively. Compared with `user04Menu_vd.js`, the administrator menu adds firmware update, TR-069 and advanced wireless pages, while omitting DDNS. Menu routing does not prove that the server accepts every displayed operation.

The templates also use `ServiceMode` directly. For example, value `0` disables LAN address/mask inputs in `tcpiplan.htm` and DHCP controls in `dhcpd.htm`; `settings-local-network.html` hides/disables elements with the `Class02Hide`/`Class02Disable` classes. `wan.htm` treats values `0` and `1` differently from other values when restricting connection, VPI/VCI and add/delete controls. Therefore changing this flag can affect multiple web controls, not just native-console privilege behavior.

**Value `2` is an explicitly implemented UI case.** This establishes compiled semantics, not the configuration parser's accepted range, successful persistence, complete side effects or authorization to change it. The CLI analysis independently traces this same getter in its authentication gate; see [runtime analysis](firmware-runtime-analysis.md). Neither that result nor the menu branch establishes an OS shell.

### Complete hidden-page control map

`modify_hide.htm` uses `initHidePage()` to initialize its Telnet checkbox. The function registry at runtime offset `0x62e63c` maps that callback to tagged pointer `0x80417989`; code at `0x80417988` reads **`TELNET_STATE`, MIB `0x8821`**, and emits `tel_enable` using the string at `0x804f5cec`. This initializer does **not** read `ENABLE_ADVANCE_PAGE`.

The page's read/display callbacks are `xscrnAppBuilddate`, `getIsMibDefault`, `getIsProductClassDefault`, `xscrnDeviceName`, `xscrnEthStatus`, `webShowWlanEnc`, `webShowWlanKey`, `ctUserPassword`, `webShowWlanSSID`, `webShowWlanPSK`, `showLanMacAddr`, `xscrnSerialNo`, `xscrnWebAccessMode` and `xscrnFactoryTestMode`. Their presence means the hidden page can request sensitive setting renderers; this report does not reproduce rendered keys or account data. The exact output and access checks of those renderers remain separate questions.

The main form targets `formModify.cgi`. Its registration literals at `0x80417d98..0x80417da0` bind it to `formModify`, code **`0x804182d0`**. Its parsed-field schema at `0x8062ce3c` contains the form's identity, wireless, account and access inputs. The following actions are visible in the template or handler:

| Main-form action | Template control | Static handler evidence |
| --- | --- | --- |
| `access` | Telnet checkbox `telnetEnable` | At `0x8041831c..0x8041834c`, converts presence/truthiness of parsed inputs into integers and sets MIB `0x8821` plus MIB `0x8512` |
| `resetProductClass` | Reset product class to default | At `0x80418352..0x80418394`, operates on MIB `0xc017`, identified as `HW_PRODUCT_CLASS`, and calls additional reset/persistence helpers |
| `ssid` | SSID text field | Handler refers to native WLAN SSID configuration and a hardware-SSID setting path |
| `wifi_password` | WPA PSK text field | Handler refers to native WLAN PSK configuration, a hardware-PSK setting path and a wireless-wait response |
| `user_password` | User-password field | Handler invokes account/authentication helpers and a hardware-password setting path; also updates `GENDATA_FROM_MAC_FLAG` (MIB `0x8510`) |
| `modifymac` | MAC address field | Handler refers to the native `ELAN_MAC_ADDR` setting |
| `modifyserialno` | Serial-number field | Handler refers to the native hardware serial setting |
| `mpwebaccess` | “MP Web Access” checkbox `mpwebenable` | At `0x80418514..0x80418538`, chooses an integer from checkbox presence and invokes the native `MPWEB_ACCESS` setting path |
| `ipv6` | No matching control in the extracted template | Compiled handler branch and `ipv6Enable` parsed input exist; the template does not expose this branch |

The template's action submission helpers assign the hidden action field and submit the form. They do not interpret the actions as browser-only changes. The handler references native configuration paths, so these are potential device settings operations, not a general shell widget. Their command-construction safety and all downstream effects have not been established.

**Missing-field uncertainty:** the access branch also consumes `ftpEnable`, which is present in the backend parsed-field schema but absent from the extracted page's controls. Its second MIB target is `0x8512`; its exported configuration name has not been identified. The branch maps a missing/false parsed pointer to zero, so submitting only the Telnet control may also affect that other setting. Exact parser defaults, final commit behavior and daemon effects have not been tested. Do not silently equate MIB `0x8512` with a guessed configuration name or recommend this form as a one-field Telnet operation.

### MP web access and factory mode are separate settings

The MIB descriptor at `0x805f62ac` identifies **`MPWEB_ACCESS`, ID `0xc01b`**, a four-byte field at `0x807c9a88`, compiled default `1`. The `xscrnWebAccessMode` screen registry at runtime offset `0x62ed2c` points to object `0x805f1b30`; its callback `0x802a335c` reads MIB `0xc01b` and renders its state. This is separate from `ENABLE_ADVANCE_PAGE` and `PADRAO_WIFI_ONLY`. “MP” is the firmware's label; its full authentication/network-exposure effects remain unverified.

The separate factory form targets `form2factorytestmode.cgi`; registration literals `0x80417da4..0x80417dac` bind it to code **`0x804167a8`**. That function parses `factorymode`, chooses zero or one, and sets **`FACTORY_TEST_MODE`, MIB `0x9301`**, before calling the common form-completion helper. Its descriptor at `0x805f92ec` points to four-byte global `0x807caf10`, compiled default `0`. The screen object `0x805f1b24` calls `0x80165888`, which reads the same MIB and renders its state. No direct write to the advanced-page flag appears in this inspected handler; other code reacting to factory mode has not been exhaustively traced.

`form2MpSetting.cgi` is another registered handler, code `0x80418674`, distinct from the main form's `mpwebaccess` action. Its inspected code begins with MAC/identity parsing and hardware-identity setting paths. The similar names must not be treated as interchangeable operations.

None of these static mappings grants permission to activate factory mode, change MP access, alter accounts or import a new advanced-page value. They establish the concrete operations and uncertainties for review.

## Update validation and signing: evidence limits

Runtime offsets below refer to the **decoded runtime**, not image or flash offsets. They locate compact diagnostic/symbol evidence rather than a reconstructed call graph.

| Runtime offset | Static evidence | Interpretation |
| --- | --- | --- |
| `0x4b19d9` | Upload-handler diagnostic naming `form2file` and `checkImgIC` | A compiled image/IC compatibility-check path exists |
| `0x4b1a08` | Diagnostic refers to an image-header key and autoboot mode | Header interpretation and boot mode participate somewhere in the update path |
| `0x4baa60` | IC-type verification diagnostic | Supports a hardware/image-family check; exact accepted values unverified |
| `0x4bab08` | Checksum verification diagnostic, followed by original/calculated checksum failure reporting | Compiled integrity-validation machinery exists; call order and exact checksum consumer require disassembly |
| `0x4bac84` | Image-error diagnostic | At least one image-rejection path is compiled |
| `0x4bab8c`, `0x4babdc` | Diagnostics describe two valid images and recovery from one image when the other is broken | Supports compiled dual-image recovery logic; does not prove valid flash contents or that this boot path works |

`upload.htm` invokes `showValidateCodeCheckBox()`; the configuration-import page invokes `showValidateCodeInterCheckBox()`. Related symbol variants also occur in the runtime. **The word “Code” and checkbox names do not establish their purpose**. They must not be described as a signature bypass or a safe way to disable integrity checks without reconstructing their renderers and upload consumers.

No firmware-signature scheme has been established by this inspection. Cryptographic/SSH/TLS material and algorithms also exist in the runtime, so searching for RSA, certificates or hashes alone cannot attribute them to update verification. Conversely, a checksum match and failure to find a signature label do **not** prove that firmware is unsigned. The following bounded control-flow analysis narrows that uncertainty without claiming a complete updater or bootloader audit.

### Bounded updater and recovery trace

This trace uses instruction addresses in the `0x80000000` runtime mapping. Complete disassembly slices, including instructions and literal pools, are retained privately as `image-agent/image-key-ic-checks.asm.txt`, `image-checksum-stream.asm.txt`, `image-checksum-primitive.asm.txt`, `image-recovery.asm.txt`, `web-image-validator.asm.txt` and `heap-image-loader.asm.txt`. No extracted firmware instructions were executed.

| Code address | Established behavior | Limit |
| --- | --- | --- |
| `0x802e8880` | Recognizes image keys `0xb0010001`, `0xa0000003`, `0xcf010002` through three comparisons | Image-class recognition, not an exact-model or signature check |
| `0x802e8938` | IC compatibility check against the current image header at `0xb4010000` | Compares a header field; it does not independently identify the physical board |
| `0x803c58f0` | Seeded additive big-endian 16-bit checksum, carry folding and normalization of `0xffff` to zero | Non-cryptographic; no digest or public-key operation in this primitive |
| `0x802e8a4c` | Validates a stream using the stored checksum as seed and 512-byte reads until end of stream | Does not itself compare the declared image length with a flash-region limit |
| `0x802c6612..0x802c66c8` | Web `form2file` raw-image branch reads exactly 64 header bytes, checks key, IC and checksum, then examines destination/type fields | Upstream multipart parsing, other file branches and complete authorization remain outside this slice |
| `0x802e8ed8` | `loadImageFromHeapToFlash`: distinct file branches, repeated header/key/IC/checksum checks on its ordinary image branch, then flash-write staging | Destination override state and final driver constraints are not fully reconstructed |
| `0x802e8c5c` | `check_flash_image`: checks primary/backup headers and payload checksums, then selects recovery or backup cleanup | Static runtime policy, not a captured boot/recovery result |

**Header interpretation.** Diagnostic function `0x802e8bdc` loads offsets `0`, `4` and `8` for its key/DRAM-address/length format; offsets `12`, `16` and `18` for entry/checksum/type; pointers `19` and `44` for date/version; and offset `60` for `flashp`. Its literal formats are at `0x802e8c48..0x802e8c58`. This supports the field names in the header table; it does not establish that every field is safe or meaningful in every update mode.

**IC compatibility.** Function `0x802e8938` copies the current 64-byte header from `0xb4010000` and loads its offset-`0x34` field at `0x802e8954..0x802e895a`. Its argument is the incoming header's corresponding field. Equal nonzero fields pass. Zero in either field, or legacy constant `0x6d670000` in either field, follows a warning/accept path. Otherwise differing fields print the IC-type error and return failure. The captured image's `0x76000000` equals the captured current header's field. This establishes a check the image can satisfy under that same reference header; it is not proof of compatibility with a different unit or hardware revision.

**Checksum coverage.** `0x802e8a4c` initializes its accumulator from the low 16 bits of the supplied stored checksum, then calls `0x803c58f0` for each 512-byte stream read. It accepts only when the final normalized accumulator is zero. The primitive sums big-endian 16-bit words, folds carries, and accounts for a final odd byte as the high byte of a word. This matches the independently verified image checksum: including stored `0xe020` as seed makes the captured payload validate. Header fields themselves are outside the payload checksum. The stream validator reads until stream end; this slice alone does not prove declared-length/actual-length consistency checks elsewhere.

**Web raw-image branch.** After the exact 64-byte read at `0x802c6612..0x802c6624`, the branch calls key recognition at `0x802c668a..0x802c668e`, IC validation at `0x802c6694..0x802c6698`, and checksum validation at `0x802c66aa..0x802c66b4`. It then requires a nonzero header `flashp` or type bit `0x02` before proceeding (`0x802c66ba..0x802c66c8`). Other mode selection follows, including distinct cases for keys `0xcf010002` and `0xa0000003`. These are actual validation calls, beyond the mere presence of diagnostic strings.

**Destination and range uncertainty.** The ordinary heap-image loader reads the header at `0x802e8fd8..0x802e8fe8`, checks the three keys at `0x802e8ff4..0x802e9008`, checks IC at `0x802e900c..0x802e9016`, and validates the remaining stream at `0x802e901a..0x802e9026`. It uses the header length when staging a write, normally adding 64 bytes; a separate mode uses the payload length without that addition. It can obtain destination addresses from layout IDs `7`/`17` or fall back to header `flashp` (`0x802e9084..0x802e90d8`). The captured header's `flashp` is `0xbfc10000`, whereas its measured run-image mapping is `0xb4010000`. Whether the active updater branch overrides or translates that value remains unresolved. Do not substitute one address for the other or infer a safe upload from header recognition.

No explicit comparison against the complete 8 MiB map or the reported slot boundaries was identified in the bounded key/IC/checksum functions. This is **not proof that range checks are absent elsewhere**: upstream upload allocation, layout accessors, destination selection, deferred writer and low-level flash-driver callbacks have not all been audited. The image's measured end, checksum and successful decompression cannot establish those runtime constraints.

**Recovery policy explains an erased backup.** `check_flash_image` obtains layout IDs `7` and `17` at `0x802e8c74..0x802e8c98`. For each it reads a 64-byte header, recognizes the same three image keys, and checks exactly the declared payload length using the stored checksum as seed (`0x802e8ca4..0x802e8d04`). No IC call or cryptographic verification appears in this bounded validation loop. Its subsequent cases are:

| Valid primary | Valid backup | Static branch behavior |
| --- | --- | --- |
| Yes | Yes | Prints the two-valid-images message, then calls the backup erase path with length `0x3e0000` (`0x802e8d12..0x802e8d56`) |
| Yes | No | Selects backup cleanup, inspecting/skipping already erased words and erasing non-erased 4 KiB portions (`0x802e8d1c..0x802e8d24`, `0x802e8e36..0x802e8e64`) |
| No | Yes | Erases the primary destination and copies the valid backup's declared payload plus 64-byte header in 1 KiB pieces (`0x802e8d26..0x802e8d30`, `0x802e8d5c..0x802e8e34`) |
| No | No | Prints an internal-error diagnostic and enters the backup erase branch (`0x802e8d32..0x802e8d56`) |

The erase path calls `0x801674d8`; the copy path calls `0x80167420`. These wrappers dispatch through runtime flash-driver state; the final chip-driver implementations are outside this trace. With the reported backup start `0x400000`, the compiled cleanup span `0x3e0000` ends at `0x7e0000`, matching the reported backup-configuration boundary. The recovery function's tagged pointer is present at `0x80949e94` among other callback literals; their consumer, actual invocation and outcome were not observed here.

Consequently, an erased backup prefix is **consistent with a primary-preferred cleanup policy**. It does not by itself show a defective recovery design, and this code does not maintain an always-populated mirror. Conversely, compiled recovery branches do not create a valid backup in the current capture or demonstrate that this unit can recover from a bad update.

**Signing conclusion and stopping limit.** The mapped ordinary-image validation sequence reaches key comparisons, a numeric IC comparison and an additive checksum. No public-key, cryptographic-digest or signature-verification call was identified in those bounded validators or the recovery loop. That is narrower than proving the whole firmware unsigned: alternative file branches, multipart/upload processing, deferred driver behavior and bootloader validation remain outside this audit. This is the concrete control-flow boundary for this follow-up.

**Restoration status.** The captured run image has the expected 64-byte structure, an accepted key, a current-header-matching IC field and a valid payload checksum. It is therefore a well-supported original firmware artifact for further analysis. It is **not a tested restoration package**: destination selection, accepted upload framing, complete size restrictions, bootloader behavior and an actual recovery route remain unresolved. A raw full-flash map also contains bootloader, settings and other regions; no whole-flash import path was established by these image-specific functions. No upload, flash erase/write, boot test or restoration was attempted.

## Completed flash map and recovery status

The completed source `.local/askey-net-006/fullflash-pass1.bin` contains exactly **8,388,608 bytes**, SHA-256 **`e5c171d08d5c3131cd7b8a4c7180e3ac277408c8072b96e335495f3b68e1fc2f`**. This analysis independently recomputed the file hash and checked that the atomic checkpoint reports `captured=8388608` and `complete=true` with the same hash. The completion checkpoint is **2026-10-27 06:34:35 UTC**. Earlier partial snapshots are superseded for whole-region conclusions.

An immutable local copy and metadata are retained as `image-agent/fullflash-final-snapshot.bin` and `fullflash-final-verification.json`. The original capture and checkpoint were not modified. This is offline file/structure verification; independent hardware readback samples belong to the main experiment record.

All ranges below are flash offsets with exclusive ends:

| Region inspected | Range | Bytes | Complete-region result |
| --- | --- | --- | --- |
| Running image | `0x10000..0x2e15c0` | 2,954,688 | Exactly matches the independently validated run-image artifact |
| Gap after running image | `0x2e15c0..0x3f8000` | 1,141,312 | Entirely `0xff` |
| Flash-file area | `0x3f8000..0x400000` | 32,768 | One valid OSK1FS container, then `0xff` padding |
| Reported backup-image slot | `0x400000..0x7e0000` | **4,063,232** | **Entire slot is `0xff`; no second image is present there** |
| Backup configuration | `0x7e0000..0x7f0000` | 65,536 | Checksum-valid compressed XML container, followed by `0xff` padding |
| Configuration | `0x7f0000..0x800000` | 65,536 | Byte-identical to the backup-configuration region |
| Hardware configuration, inspected 8 KiB window | `0x5000..0x7000` | 8,192 | Checksum-valid compressed XML container, followed by `0xff` padding |

| Complete region | SHA-256 |
| --- | --- |
| Erased backup-image slot | `a1356e82e5efa5c32ce7f1a8d39b2a19681b7aafa04d0965f29ccb0276f51e9a` |
| Flash-file area | `9dcf84ba206c1baf281382fe6a8f9f2ce8a43fce2c4f75c6b1f7e17cd5ea6b8c` |
| Either configuration region | `019ecc4de8ac7c16b16ff4b41916fcce7fe18aae3b44de22364ef810530202ce` |
| Inspected hardware-configuration window | `6bb33d916a41351cc427656a83bd1eb0cf7946f0778721cd20b2fa694f9fbff2` |

The whole erased backup slot confirms the earlier prefix observation. It remains consistent with the compiled primary-preferred cleanup policy above. This dump provides **no populated fallback firmware image in that slot**, and no recovery or restoration operation has been demonstrated. The two configuration copies are settings containers, not alternate firmware images.

### Configuration containers and checksums

Both configuration regions use an eight-byte header: a big-endian 32-bit **compressed-payload length** followed by a big-endian 32-bit checksum. The inspected hardware-configuration container uses the same observed structure. For all three containers, the checksum equals the **unfolded sum of big-endian 16-bit compressed-payload words**, with a final odd byte placed in the high half of a word and a zero low byte. This differs from the carry-folded OSK1FS checksum and the complemented running-image checksum.

| Container | Compressed payload | Stored and calculated checksum | Bytes after header and payload |
| --- | --- | --- | --- |
| Hardware configuration | 357 bytes | `0x0038e47a` | Remaining 7,827 bytes of the inspected window are `0xff` |
| Backup configuration | 32,091 bytes | `0x1cfdc2e0` | Remaining 33,437 bytes of the region are `0xff` |
| Configuration | 32,091 bytes | `0x1cfdc2e0` | Remaining 33,437 bytes of the region are `0xff` |

A bounded conventional **LZSS** decode succeeds on each payload: 4,096-byte ring, initial position 4,078, least-significant-bit-first flag bits, one bit for literals, and two-byte backreferences with a 12-bit ring offset and low-nibble length plus three. The outputs parse as complete XML with root `Config_Information_File_8671`. That root is a configuration-format label, not independent identification of the exact physical SoC.

| Decoded data | Size | XML elements | SHA-256 |
| --- | --- | --- | --- |
| Hardware configuration | 851 bytes | 19 | `008926a1d716f3c139675ef5661a1dde36a9fef0e7b7caf98c3b8caf48efdc78` |
| Either settings configuration | 204,800 bytes | 4,798 | `581a389b9e866c2d18aeb9a246d52fa49121def493bd35e0516be539157fc7bf` |

The 32,091-byte compressed settings payload has SHA-256 `393cf8892682e2346ff5cbb45c282c22a9f0fb0cbdce384249568e4b8de8d55f`; the 357-byte hardware payload has SHA-256 `57c46cae929a92a27bc7a88295b757f02dbf50f6d62cbc78421d8336cfc37c68`.

The decoded settings XML is **semantically identical to the retained approved Telnet-era native export**, `.local/askey-net-003/config-after-cli.img` (205,061 bytes, SHA-256 `721cc151716e65c733f6f37d3ca18525b1d901380ca990355ed774d9716ff1b9`). XML canonicalization with text whitespace stripped produces identical output, and all 4,798 flattened tag/attribute/text records match in order. The raw byte-length/hash difference is formatting, not a detected setting difference.

Decoded XML remains in ignored scratch files with mode `0600`. No configuration values, credentials, account records, WAN details or device identifiers are reproduced here. Checksums establish container integrity and successful decoding; they do not authenticate the data or prove a safe configuration/flash restore.

### The actual OSK1FS area

The structure at flash `0x3f8000` starts with the eight-byte OSK1FS marker. Its next two big-endian 32-bit fields are **`0x1a0` (416)** and **`0x0000fad5`**. Interpreting the former as payload size yields a 16-byte header and payload ending exactly at `0x3f81b0`, followed by **32,336 bytes of `0xff` through the flash-file region end `0x400000`**. The final complete dump confirms this entire area.

The 416-byte payload has SHA-256 **`0c776773f57a2811b8c75980eee16061b0ee986a5c3ea7ad1dcacdf936ace2da`**. Summing its big-endian 16-bit words and folding carries yields **`0xfad5`**, matching the second field. This checksum stores the folded sum itself, whereas the running-image checksum stores its complement. The parse and checksum agreement provide strong evidence for this structure without assuming another model's layout.

The payload contains one record: a 28-byte filename field, a big-endian 32-bit content length, 369 bytes of file content, and 15 zero padding bytes. Its name is **`CWMPNotify.txt`**. Content is seven printable parameter-path lines beginning with `InternetGatewayDevice.`. No file contents are reproduced here. There is no ELF marker or script interpreter marker in this payload; **no executable file was identified**. This is a small notification-data store, not a recovered second firmware image or a general-purpose executable filesystem.

The decoded runtime's OSK1FS markers at `0x2e9698` and `0x4bad54` occur in a code/literal-pointer context and validation-string context respectively. They are not embedded filesystem archives. The first context contains a pointer-shaped value `0xb43f8010`, consistent with the newly observed flash-area payload address; this strengthens the mapping but does not replace disassembly of its consumer.

## Next useful offline questions

1. Complete the destination/layout, range-check, deferred-writer and bootloader analysis beyond the bounded validation paths above. Resolve the header `flashp` mapping and any further signing checks before treating either artifact as updater input.
2. Establish a concrete recovery route and its accepted input format. The completed dump contains an original running image and settings containers, but its reported backup-image slot is erased and no restoration operation has been tested.
3. Reconstruct web dispatch authorization and `SendKeyCSRF` validation, then remaining maintenance/account handlers. This can separate menu hiding, web roles and native-console privileges without changing the router.
4. Reconcile the separately authorized hardware readback results with the completed artifact's experiment/manifest record. Offline checks here do not claim a second full hardware read pass. Preserve the owner's publication instructions while keeping private settings, keys and proprietary source bodies out of this report.
