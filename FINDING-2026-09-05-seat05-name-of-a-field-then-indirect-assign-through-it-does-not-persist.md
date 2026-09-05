# FINDING seat05 2026-09-05: `.field(x)` produces a name; assigning through that name does not persist

**Context:** row `snobol4-name-operator-over-this-form` (hq_C lane). The named defect (the lowerer's
`sno_fatal("name operator over this form is outside the landed subset")` at `src/lower/lower_snobol4.c:323`,
refusing `.` applied to any function-call operand except a statically-known DATA field) is CURED — see the
LEDGER on that task file for the fix (a general fallback through the existing `SNO$WANTNM`/`rt_g_want_name`
mechanism, landed narrowly at exactly two call sites so the ambient flag can't leak into an unrelated
callee -- see that file for why a broader version regressed LAST/POL/GPM and was reverted).

**This finding is a SEPARATE, deeper defect the fix exposed, not caused by it** -- it blocks
`LSORT_driver.sno` from a full PASS (currently DIFF/DIFF: prints `banana .` instead of the full sorted
`apple banana cherry date fig pear .`), but is NOT specific to OPSYN aliasing, APPLY-indirection, or
anything this row's fix touched. It reproduces with the *original, pre-existing, statically-recognized*
`.field(x)` fast path alone (`src/lower/lower_snobol4.c:311-322`, untouched by this row).

## Minimal repro (no OPSYN, no DEFINE recursion, no `.` over a dynamic call)

```snobol4
        DATA('LINK(NEXT,VALUE)')
        A = LINK(NIL, 'A')
        B = LINK(NIL, 'B')
        C = LINK(NIL, 'C')
        HEAD = A
        PTR = .NEXT(A)
        $PTR = B
        PTR = .NEXT(B)
        $PTR = C
        T = HEAD
L1      OUTPUT = VALUE(T)
        T = NEXT(T)
        IDENT(T)                        :F(L1)
        OUTPUT = 'DONE'
END
```

**Expected** (SPITBOL, and by inspection of the SNOBOL4 semantics -- `.NEXT(A)` names A's NEXT cell,
`$PTR = B` assigns B into it): `A` / `B` / `C` / `DONE`.
**Got** (`./scrip --run`, this tree, post-fix): `A` / `DONE` -- i.e. `NEXT(A)` reads back empty after
`$PTR = B` supposedly wrote B into it. The splice does not persist across the `PTR = .NEXT(A)` /
`$PTR = B` statement boundary.

**Not yet isolated further** (ran out of budget in this row -- ASM-DIFF-FIRST says mint smaller, this
already is small): whether the write in `$PTR = B` lands in the wrong place, doesn't land at all, or lands
correctly but `NEXT(A)` re-resolves a *different* cell on the next read. `rt_field_var` (`pattern_match.c:1345`)
wraps a raw `data_field_ptr(fname, obj)` pointer in a `VCELL_t`/`NAMETRAP` -- the DESCR_t assignment path for
that shape (`rt_assign_var`, presumably) is the next thing to trace with ASM-DIFF-FIRST / gdb, not by more
reasoning from source.

**Why this doesn't invalidate the `snobol4-name-operator-over-this-form` fix:** `FLD_driver.sno` (this
row's other witness) exercises name-then-indirect-assign too (`Y = .APPLY(...)`, `$Y = 'ccc'`, then
`OUTPUT = B(X)` reads back `'ccc'` correctly) and board-PASSes clean in both modes -- so the write-back
mechanism is not *uniformly* broken, only under some condition this repro hits and FLD's shape doesn't.
That distinction is the next lead.

**Repro file:** not yet vendored into the corpus (this is a probe, not a suite entry) -- copy from this
finding, or ask seat05/hq_C.
