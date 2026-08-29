# FINDING: SCRIP ff71adfc was committed NON-COMPILING and its quoted green boards were vacuous-build artifacts (ceo, 2026-08-29)

**Claim:** SCRIP ff71adfc ("icon break-value channel, half one") shipped a `lower_icon.c` that cannot compile — `IR_t * slb` redefined THREE times on one line in lower_while plus a `return H` with no `H` in scope — because a three-function edit (save/publish for while/until/repeat) landed stacked in ONE function. The commit's quoted boards (Icon rungs 259/8, SNOBOL4 1344/1344) therefore ran on stale objects: the vacuous-build class (equal-mtime incremental make) struck again, this time masking a syntax error, not just a semantic one.

**Repair:** SCRIP d1a447ea (after dfe01da6's independent partial de-triplication — merged state read line-by-line before trusting the clean rebase, per the seat01 silent-mash lesson). One save + one publish per loop. `gcc -fsyntax-only` green; execution verification handed off (pristine was in flight when Lon called handoff).

**Lesson (two-layer):** (1) multi-site edits into three near-identical functions must anchor on per-function unique context, never on shared text — the shared-anchor edit applied thrice to the first match; (2) any board quoted in a commit REQUIRES a compile-proof of the edited TU at minimum — a green board after an edit that was never compiled is the strongest false signal this workspace produces. Related: the HQ-27 pristine rule exists for exactly this; it was skipped at ff71adfc.

**Route:** row `icon-scan-env-value-residue` baton NEXT corrected in place; repair commit message carries the full trace.
