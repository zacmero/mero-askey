# Open research leads — owner's RTV9015VW

These paths remain open. A tool refusing a particular follow-up is not technical evidence that a path is impossible, inapplicable or abandoned. The owner explicitly instructed that the live-session capability-field avenue be retained for later research.

## Live CLI session object and capability fields

**Status: OPEN / pending further research. Not ruled out.**

### Existing evidence

The captured firmware's [CLI analysis](firmware-cli-analysis.md) identifies session capability checks, account-priority assignment, access-mode filtering and parser privilege gates. These are preserved static findings, not inferred from command names.

- Helper `0x8029a0fc` implements the mapped capability checks.
- Authentication routines derive capability bits from the actual `USERNAME_PASSWORD.PRIORITY` field.
- `ENABLE_ADVANCE_PAGE` / rendered `ServiceMode` can remove those capabilities during authentication.
- Native command availability and help filtering depend on those checks.
- The live address and ownership of a specific session object have not been established. Image-relative code/global addresses are not a substitute for a verified live-session address.

### Unanswered questions to retain

- How does the firmware locate the current session object: an explicit argument, global reference, session table or task-local context?
- What proves that an object belongs to a particular authenticated connection, rather than the independent capture connection or another client?
- When is the object initialized, reused or released, and which fields identify that lifecycle?
- Does a future read-only observation agree with the static structure and capability interpretation?
- What further evidence is needed before considering any separate runtime experiment?

No live-session field address, safe mutation target, successful privilege change or native execution result is claimed. No device request or memory write was performed for this follow-up.

### Previous attempt and why it is unfinished

On 2026-10-27, an optional sub-agent follow-up asking for a code-supported locator for a future read-only session-field confirmation was stopped by automated cybersecurity review with the stated reason “possible cybersecurity risk.” That records an automation limit, **not a finding about the device or a rejection of the owner's established authorization**.

The existing static report, offsets and private evidence remain retained. This lead must remain linked from the handoff and research index so later authorized work can resume from the evidence rather than treating it as a discarded path.

## Other open questions

- Exact live ChipId snapshot interpretation, installed RAM capacity and CPU clock; do not substitute compile-time support strings for hardware measurements.
- OSK native allocation, calling convention, lifetime and cache contracts needed for a program of our own.
- Full updater/bootloader destination and range validation beyond the already mapped bounded checks.
- A demonstrated restoration procedure; a captured file or reported backup address alone does not prove recovery.
