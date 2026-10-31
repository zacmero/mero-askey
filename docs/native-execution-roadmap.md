# Road to a minimal native execution proof

Owner-approved direction, 2026-10-31. RAM allocation, inert placement, independent mailbox readback and cleanup are already verified in ASKEY-NET-009. No custom program has executed.

1. **Instruction mode and cache handling — in progress.** Trace the captured firmware's instruction/data-cache routines and existing copy-to-execution ordering. Establish their arguments, side effects and applicability before using them. Do not assume that readable/writable RAM is ready for instruction fetching.
2. **Prepare a minimal entry and returned callback.** Assemble/disassemble two small routines that preserve calling state, write agreed nonce-bearing entry/cleanup status into the owned mailbox, and return through the verified two-call contract. Avoid relying on printf output or Linux services.
3. **One bounded execution trial.** Create fresh owned RAM storage, revalidate pointers, place and read back the exact image, apply the established cache procedure, then invoke the entry through the verified native interface. Never reuse released addresses.
4. **Independent proof and cleanup.** In a fresh connection, verify nonce, entry and cleanup markers, confirm CLI responsiveness, then close/delete the owned allocation and verify the original inventory. Record actual results and hashes; a prompt alone is not execution proof.

Each step receives a documentation/commit checkpoint. Firmware writes, resets, persistent service/settings changes and hardware connections are outside this road unless separately instructed. A successful marker program is a native-execution milestone; an interactive OS shell remains a separate goal.
