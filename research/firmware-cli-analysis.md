# RTV9015VW CLI privilege analysis

Offline analysis of the owner's complete `BR_SO_RTK_V6.1.8t` runtime, 2026-10-27. No router traffic, settings changes, firmware execution, memory writes, uploads or exploit tests were performed for this analysis.

## Artifact and method

The input is ignored `.local/askey-net-006/analysis/runtime.bin`, 9,752,040 bytes, SHA-256 `b104789b795630eee7de1b50d64e49710535221f8baa6652021af6d00abb3941`. Runtime address = file offset + `0x80000000`. Addresses below are runtime addresses; subtract this base for reproducible offsets. Most functions below use MIPS16; odd function pointers select that ISA, while the listed instruction addresses are even. This is not ARM Thumb.

Analysis used GNU MIPS objdump 2.35.2 privately extracted from Debian's `binutils-mips-linux-gnu_2.35.2-2cross2_amd64.deb`, without global installation. Private tools, full disassembly and `readbin.py` are under `.local/askey-net-006/analysis/cli-agent/`. These are analysis dependencies, not router firmware execution.

## Two independent CLI privilege bits are proven

At `0x8029a0fc`, a helper examines the request mask in `a1` and the session byte at offset `1196` (`0x4ac`):

| Request mask | Required session bit | Evidence |
| --- | --- | --- |
| bit 0 / value 1 | byte bit 6 (`0x40`) | `0x8029a100`–`0x8029a10c`: mask 1, load byte, shift 6, mask 1 |
| otherwise bit 1 / value 2 | byte bit 7 (`0x80`) | `0x8029a110`–`0x8029a120`: mask 2, signed byte load, shift 31 |
| neither bit | none | return value starts at 1 on the second branch |

This establishes bit tests, not an assumed Unix user/group or root mapping.

The authenticated account field is independently identified: MIB table descriptor `0x805f5344` has ID `0x81e9`, name `USERNAME_PASSWORD`, record length `0x94`, and field table pointer `0x805fb088`. Its `PRIORITY` field descriptor at `0x805fb0c4` declares offset `0x84` (132), size 4. Adjacent descriptors identify `FLAG`, `USERNAME` and `PASSWORD`; no credential values are reproduced here.

Authentication routine `0x8029b910` obtains the matching account and reads its field at +132 (`0x8029b944`). It sets privileges as follows:

| Stored PRIORITY | bit 6 | bit 7 |
| --- | --- | --- |
| 1 | set | set |
| 2 | clear | set |
| other | clear | clear |

The relevant branches/stores are `0x8029b948`–`0x8029b978`. A second authentication variant around `0x8029bf80` repeats this mapping (`0x8029bfbc`–`0x8029bfee`). Thus the numeric mapping is code evidence, rather than an inference from web labels.

## ENABLE_ADVANCE_PAGE can remove both privileges

After the mapping above, `0x8029b97c` loads the 32-bit session word at +1196. When it intersects `0x14000040`, the routine calls getter `0x802b7990`. If that getter returns 0 or 1, instructions `0x8029b99c`–`0x8029b9aa` clear both `0x80` and `0x40` from the session byte. Other getter values skip this clearing branch. The second authentication variant repeats the gate at `0x8029bff2`–`0x8029c020`.

The getter loads global `0x807c96a8` through literal `0x802b7998`. MIB entry `0x805f71ec` identifies that global as ID `0x8b4c`, `ENABLE_ADVANCE_PAGE`; its storage pointer is at `0x805f7200`. This is not a conjectured ServiceMode mapping: [web analysis](firmware-image-analysis.md) independently shows that the same getter is rendered to JavaScript as `ServiceMode`.

The `0x14000040` mask is a word test in a big-endian runtime; it must not be confused with a direct test of only the privilege byte. The meaning of each selected transport/session flag has not been fully named. Consequently the account/mode prediction is conditional on this session-mask branch being taken, and on no later privilege changes.

This flag has broader effects than CLI authentication. Exact pointer searches found getter references in both authentication variants, HTTP dispatch and two JavaScript emitters. HTTP dispatch at `0x802c1474`–`0x802c14e4` tests `tr069.htm`, `upload.htm`, and `wladvanced.htm` when mode is 0 or 1; mode 0 additionally tests `portmap.htm`, `fw-ipportfilter_adv.htm`, and `fw-ipportfilter_adv_v6.htm`. Matched paths take handler `0x802c04b4` with code 1028. Modes outside 0/1 skip those particular checks. Web analysis additionally establishes different menus and AccessClass values. This analysis does **not** recommend changing the flag or establish the full supported value range.

## Outer parser denial path

The outer parser has one literal reference to the privilege helper: `0x802aa3c8` contains pointer `0x8029a0fd`. At `0x802a5d0e` it supplies request mask **2** and calls the helper. If that returns false, it selects `0x805f2628 + 84`, error index 21, whose pointer at `0x805f267c` names `ERROR: Invalid privilege.` at `0x8049e908`.

The generated parser's semantic switch at `0x802a5664` sends grammar productions 21, 44 and 52 to this shared action (`0x802a5d0c`). A local walk of its LALR data tables establishes the command association without executing firmware instructions:

| Visible token | Token ID / definition | Initial parser shift | Immediate reduction | Required request mask |
| --- | --- | --- | --- | --- |
| `config` | `0x10a`, descriptor `0x80543aa4` | state 0 → 2 | rule 44 | 2: session bit 7 |
| `diagnostic` | `0x14e`, descriptor `0x80543f64` | state 0 → 4 | rule 21 | 2: session bit 7 |

The permission check therefore occurs before completing either mode's body. This matches, but does not replace, the prior live observations of both commands returning Invalid privilege. Rule 52's visible entry has not been assigned here.

The table walk uses `yypact=0x80547018`, terminal translation `0x805478b0`, `yycheck=0x80545dd0`, `yytable=0x805465e4`, default reductions `0x80544c74`, rule lengths `0x8054550c`, rule left-hand sides `0x80545744`, goto offsets `0x80545bb0`, and default gotos `0x80546df8`. It reproduces shifts/reductions only; it does not implement semantic actions or claim to simulate a complete interactive session. The decisive reductions occur immediately after the first command token, before any missing semantic effects matter.

## Inner parser: compiled native paths require the stronger bit

The token table starts at `0x805435c4` and consists of **ID, string-pointer** pairs. Reading it in reverse order produces an off-by-one command attribution. Correct relevant IDs are:

| Token ID | Name |
| --- | --- |
| 15 (`0x0f`) | `command` |
| 17 (`0x11`) | `timer` |
| 18 (`0x12`) | `webdll` |
| 19 (`0x13`) | `loaddll` |
| 20 (`0x14`) | `chksum` |

Registration routine `0x802a2220`, including `0x802a22b6` onward, registers grammar descriptors with callback `0x802a2de9` and the token table above via `0x8029d119`.

| Root descriptor | Token / dispatch ID | Flags word | Child syntax |
| --- | --- | --- | --- |
| `0x805f1704` | webdll / 18 | `0x00450000` | `0x805f1964` |
| `0x805f1718` | loaddll / 19 | `0x40450000` | `0x805f1964` |
| `0x805f1664` | chksum / 20 | `0x00450000` | `0x805f17b4` |

The shared child `0x805f1964` is numeric token `0xc2`, argument ID 1. The native handler later retrieves argument ID 1. The lexer IDs are not in sorted order: `command` is 15, while `timer` is 17. A separate root record for token 15 exists at `0x805f1740`; its behavior is not the native address-call handler described below.

Actual parser traversal at `0x8029a6ee`–`0x8029a712` reads `lhu(node+4)`: bit 0 requires session byte +1196 bit 6; otherwise bit 1 requires bit 7. A missing bit skips the node at `0x8029a83c`–`0x8029a84a`. Help/completion has the same privilege filter at `0x8029a3f2`–`0x8029a416`. All three descriptors above have bit 0 set in this halfword and therefore require **bit 6**, which authentication assigns to PRIORITY 1, not PRIORITY 2.

Dispatcher `0x802a2de8` reads the selected command ID, subtracts 1, bounds it below 20, then uses the halfword jump table at `0x802a2e10`:

| Selected ID | Dispatch branch | Handler | Static behavior |
| --- | --- | --- | --- |
| 18 | `0x802a2e9a` | `0x802a277c` | retrieves numeric argument 1, calls resulting address, then calls returned address; further contract in runtime report |
| 19 | `0x802a2e9e` | `0x802a27d0` | interprets header and conditionally copies bytes to header-supplied address |
| 20 | `0x802a2ea2` | `0x802a2730` | computes checksum over address and length |

See [runtime and native analysis](firmware-runtime-analysis.md) for handler contracts and limitations. These are dangerous native call/copy facilities, not a POSIX process loader or proof of a Linux shell. No handler was invoked here.

**Derived prediction:** with the currently reported PRIORITY 2 account, access mode 2 would preserve bit 7 through this authentication gate but still leave bit 6 clear. The recovered checks would permit entry past the specific `config` and `diagnostic` mask-2 checks, while still rejecting the three native paths above. This is conditional on successful authentication, the analyzed runtime, and no later privilege/session changes. It does not establish that every diagnostic/config subcommand is permitted, authorize any change, prove accepted settings values, or rule out additional session gates. PRIORITY 1 initially sets both bits, but modes 0/1 can still clear both through the same session-dependent gate.

## Bounded follow-up: memory read/write handlers

This is static evidence from the captured runtime. Only `memory show` has been tested on the device in the earlier experiments; **no memory write has been tested**. The write finding below comes from actual store instructions, not from help text.

The root descriptor at `0x805f1650` is token 6 (`memory`), flags `0x00400000`, with child array `0x805f1778`. Its relevant descendants are:

| Descriptor | Role | Flags word | Child / argument / selected dispatch ID |
| --- | --- | --- | --- |
| `0x805f1778` | `show`, token 9 | `0x00400000` | child `0x805f1a30` |
| `0x805f178c` | `set`, token 8 | `0x00400000` | child `0x805f1a80` |
| `0x805f1a30` | show numeric address | `0x00100000` | argument 1 |
| `0x805f1a44` | `length`, token 4 | `0x00040000` | selects dispatch 1 |
| `0x805f1a58` | show numeric count, terminal | `0x40100000` | argument 2 |
| `0x805f1a80` | `byte`, token 1 | `0x00040000` | selects dispatch 2 |
| `0x805f1a94` | `word`, token 12 | `0x00040000` | selects dispatch 3 |
| `0x805f1aa8` | `long`, token 5 | `0x00040000` | selects dispatch 4 |
| `0x805f1abc` | set numeric address | `0x00100000` | argument 1 |
| `0x805f1ad0` | `value`, token 11 | zero | value-keyword grammar element |
| `0x805f1ae4`, `0x805f1af8` | set numeric value, terminal alternatives | `0x40100000` | argument 38 (`0x26`) |

All numeric elements above use generic numeric token `0xc2`. The two terminal value alternatives have different parser-state bytes; their complete optional-keyword behavior was not separately emulated. No runnable write command or payload is provided here.

**Privilege result, including the leaves:** the upper halfword at +4 of every descriptor in this table has both privilege bits 0 and 1 clear. Thus none requests session privilege bit 6 or 7 through the recovered traversal gate at `0x8029a6ee`–`0x8029a712`. Registration at `0x8029ccf0` keeps the source descriptor pointer at wrapper +8; its observed flag modification ORs `0x1000` into source +4 (`0x8029cd1e`–`0x8029cd26`), leaving these privilege bits unchanged. This explains why the read path is available despite denied outer privileged modes. It also means the recovered account-bit checks do not protect the set path. Other parser/session checks and address-dependent hardware behavior are not excluded.

The dispatch table at `0x802a2e10` maps selected ID 1 to `0x802a2ba4`, and IDs 2, 3 and 4 to `0x802a2170`.

Read handler `0x802a2ba4` retrieves argument 1 as the starting address and argument 2 as the count. Its loop advances by 16, sends the remaining count capped at 16 to `0x802e7df4`, and stops when the signed offset is no longer below the count (`0x802a2bfc`–`0x802a2c00`). The formatter reads one byte at a time with `lb` (`0x802e7e3a`) and advances the address by one. Therefore the count denotes bytes, not 32-bit words. The existing positive 16-byte experiment remains the live validation; large, invalid or overflowing counts have not been tested.

Write handler `0x802a2170` scans parsed argument IDs: 1 supplies address `s0`, and 38 supplies value `s1` (`0x802a2186`–`0x802a21a4`). It branches on selected dispatch ID and contains:

| Width selection | Addressed store | Value treatment |
| --- | --- | --- |
| byte / ID 2 | `sb` at `0x802a21ca` | low 8 bits (`& 0xff`) |
| word / ID 3 | `sh` at `0x802a21e4` | low 16 bits (`& 0xffff`) |
| long / ID 4 | `sw` at `0x802a21f2` | 32-bit value |

This handler performs one store rather than a count-controlled write loop. Byte and halfword branches first read the old value (`lbu` at `0x802a21b6`, `lhu` at `0x802a21ce`) for output. No handler-local address allowlist, alignment repair, privilege check, or rollback mechanism was found between argument extraction and those stores. Invalid or device-mapped addresses can still fault or have hardware effects. The disassembly therefore establishes compiled direct-memory write behavior and its parser path; it does **not** establish a successful, safe or recoverable write on the unit, nor an authorization to attempt one.

## Reproduction and bounded next work

All following commands operate on local files only:

```sh
rtk sha256sum .local/askey-net-006/analysis/runtime.bin
rtk proxy python3 .local/askey-net-006/analysis/cli-agent/readbin.py dis 0x8029a0fc 0x28
rtk proxy python3 .local/askey-net-006/analysis/cli-agent/readbin.py dis 0x8029b910 0xba
rtk proxy python3 .local/askey-net-006/analysis/cli-agent/readbin.py words 0x805f5344 0x28
rtk proxy python3 .local/askey-net-006/analysis/cli-agent/readbin.py words 0x805fb088 0x50
rtk proxy python3 .local/askey-net-006/analysis/cli-agent/readbin.py words 0x805f71ec 0x20
rtk proxy python3 .local/askey-net-006/analysis/cli-agent/readbin.py dis 0x8029a6ee 0x28
rtk proxy python3 .local/askey-net-006/analysis/cli-agent/grammar_walk.py 0x10a 10
rtk proxy python3 .local/askey-net-006/analysis/cli-agent/grammar_walk.py 0x14e 10
rtk proxy python3 .local/askey-net-006/analysis/cli-agent/readbin.py words 0x805f1778 0x28
rtk proxy python3 .local/askey-net-006/analysis/cli-agent/readbin.py words 0x805f1a30 0xdc
rtk proxy python3 .local/askey-net-006/analysis/cli-agent/readbin.py dis 0x802a2170 0x9c
```

Confidence is high for the MIB mapping, branch comparisons, token/dispatch association and parser masks: each has independent data references and coherent MIPS16 control flow. The names of all transport bits and all later setting/handler effects remain incomplete. Exact pointer searches also cannot exclude dynamically synthesized references.

The next useful offline step is to recover permitted diagnostic command syntax and identify read-only inventory entries before proposing any future live operation. A future read-only device check should compare the already supported help output against these filtered tables only after the actual session privilege bits can be identified without writes. Do not try `webdll`, `loaddll`, arbitrary addresses or configuration values as discovery probes. This report has not established a presently reachable genuine OS shell or a safe arbitrary-code execution test.
