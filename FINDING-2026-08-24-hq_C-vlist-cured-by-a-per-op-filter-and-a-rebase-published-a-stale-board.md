# FINDING 2026-08-24 hq_C — the `(A , B)` cure was a PER-OP FILTER, and a rebase published a board for a tree that never existed

**Seat:** `hq_C` · **session:** s270 · **mode:** FLEET-4 · **landing commit:** SCRIP `0e57de3b` (pushed)
**Authority:** Lon s269 via CEO-13, rank 0, verbatim: *"We want SNOBOL4 to be 364 out of 364, so get treebank fixed as a priority."*

## ⭐ RESULT: 364/364 IN BOTH MODES, ZERO FAILURES

Measured pristine `-O0` on a clean tree (`69449f94` + the cure): **corpus m3 364/364 · m4 364/364 · SKIP=0**.
Probe ladder `v01`–`v05` PASS, both controls `c01`/`c02` PASS. `demo_treebank` is **CURED**.
On today's `main` it reads **363/364**, the only red being `TDump_driver` — **not this change** (§ bisect below).

## ⛔⛔ THE ROOT CAUSE WAS NOT WHERE THE ROW'S OWN BRIEF POINTED

The s266 FINDING framed this as a **failure-path** defect — arm 1 fails, the spine is not restored, a cell
belonging to an already-succeeded expression gets popped. That framing survived three sessions and it is
**wrong**. With multi-arm lowering on, the selection yielded **NULL even when ARM 1 SUCCEEDED**: control
`c01`, whose first arm always wins, was red too. So the value never reached the enclosing expression **in
any case**, and the whole backtracking story was a red herring.

⭐ **The asm named it in one read.** The consumer (`n7_binop`) takes its operand from the ζ-**spine** —
after its own `sub rsp,16` the disjunction's cell is `[rsp+16]`. But `bb_disjunction` **never pushed a
spine cell**; it wrote its result into a fixed **frame** slot. `FRQ()` routes through `x86_zop_regime`,
which addresses the spine only for offsets inside a *granted flat cell*; with no grant every offset fell
back to the frame. **Producer and consumer were addressing different memory.**

## ⛔⛔⛔ AND THE GRANT WAS MISSING BECAUSE OF A PER-OP FILTER — THE STRUCTURE LON ALREADY OUTLAWED

`fc_geom()` (`zeta_storage.c`) is a ladder of `if (nd->op == IR_MATCH_ARB) … if (nd->op == IR_MATCH_SPAN) …`,
and `emit.cpp`'s dispatch additionally requires **every `case IR_*` to call `fc_geom` and set
`op_fc_bytes` itself**. `IR_DISJUNCTION` was in **neither** list, so an entire value-producing family was
**silently denied storage, with no error anywhere**.

⭐ **This is RULES.md's NO-PER-OP-FILTER violation, and it is the second instance beside `zd_wants()`** —
the standing per-op-structure row should cover `fc_geom` too, and deserves a higher rank. The class:
**a family member denied a resource by omission from a list, failing as wrong data rather than as an error.**

## ⭐ THE FIX KEYS ON STRUCTURE, NOT ON THE OP — DELIBERATELY, BECAUSE THE OP IS THE DEFECT

⛔ `IR_DISJUNCTION` is **shared** by SNOBOL4 selection, pattern alternation **and** Prolog. A blanket grant
changes pattern codegen tree-wide. The property that actually distinguishes a *value* disjunction is that
it carries **N arm-result operands past its 2N port pairs**; a pattern alternation carries only the pairs:

```c
nd->op == IR_DISJUNCTION && IR_LIT(nd).ival > 0 && nd->n_operands > 2 * (int)IR_LIT(nd).ival
```

No op list, no frontend test. `SCRIP_VLIST_ALT` is **retired in the correct direction** per CEO-13: the
multi-arm path is unconditional and the flag is deleted, so the **ON** arm survives. ⛔ That mattered on a
deadline — the flag was never-set, so a strip wave under the empirical rule would have deleted it with the
**broken arm-1-only default inlined as permanent code**.

## ⛔ THE TAIL, NAMED RATHER THAN BURIED

Probe `v05_treebank_pushlist_235` **passes m3 and SIGSEGVs in m4** — an **m3 ≢ m4 divergence**, a
design-invariant violation. The corpus gate is green in *both* modes (`demo_treebank` and
`treebank-prepend` both pass m4), so this is the family's **tail, not its body**. ⛔ Do not read 364/364 as
*"selection expressions are finished."* Row: `vlist-v05-m4-sigsegv-m3-m4-divergence`.

## ⛔⛔ TDump_driver IS A DIFFERENT SEAT'S REGRESSION — BISECTED

Deterministic **12/12** SIGSEGV (rc=139), not flaky. `r12` — the `cas_mark` GVA pointer — reads **0**
inside a match, while the pinned VA slot at `0x70000000` still holds a valid pointer at fault time, so it
is **clobbered, not uninitialised**.

| commit | | TDump_driver |
|---|---|---|
| `15738e4a` | pre-strip baseline | ✅ PASS 3/3 |
| `f2347178` | hq_C wave 3a | ✅ PASS 2/2 |
| `69449f94` | hq_C wave 3b | ✅ PASS 2/2 |
| **`822bc8a1`** | **seat03 — `zd_plan` arm-relative depth / gin-oin self-edge suppression** | ⛔ **CRASH 3/3** |

> ⭐ **ATTRIBUTION CORRECTED 2026-08-24 s272.** This table originally read *"another seat"*. **`822bc8a1` is
> seat03's**, and seat03 owned it unprompted (`tdump-regression-was-mine`), independently worktree-bisecting
> `69449f94` PASS 3/3 vs `822bc8a1` CRASH 3/3 to confirm this table before claiming it. Everything else in the
> bisect stands unchanged. ⛔ The lesson seat03 draws is the one worth keeping, and it is sharper than the one
> written below: they certified *"inert for all current callers"* against SNOBOL4 crosscheck 325/325 plus a full
> Icon rung ladder, Rebus and Prolog — **all clean, and all irrelevant, because `crosscheck/` excludes
> `beauty_suite/`, where the gate's SOLE populator `TDump_driver` lives.** A verification corpus that cannot
> contain the victim cannot exonerate the change, however broad it looks.
| `ad56bb88` | hq_C wave 4a | ⛔ CRASH 12/12 (inherited) |

**The strip waves are clean.** Routed to `ceo` to assign, and to `hq_P` since it may touch bench ground.

## ⛔⛔⛔ THE PROCESS FINDING — MEASURE-THEN-REBASE PUBLISHES A STALE VERDICT

I measured wave 4a's board, **then** `pull --rebase`, **then** pushed. The rebase brought `822bc8a1` in
**after** the measurement. So **wave 4a's commit message certifies a board for a tree that never existed on
origin** — every number in it was true of my local tree and false of the pushed one.

⭐ **The rule this needs: re-run the board AFTER the rebase and BEFORE the push**, or the verdict names a
tree nobody can check out. PUSH-BEFORE-DISPATCH already says push early; it does not say *the rebase can
invalidate the receipt you are about to publish.*

⛔ **It also cost real work and produced two false conclusions of my own**, recorded because the failure is
instructive: mid-session I measured "grant ON → TDump crashes" and "grant OFF → TDump still crashes" and
briefly concluded **my own `fc_geom` grant had broken pattern disjunctions tree-wide**. It had not — the
crash arrived from outside my tree between two of my measurements. This is the same family as hq_P's
*"when one suite in a run is provably false, void the WHOLE run"*, except **the falsifier came from another
seat's push rather than from a concurrent build in my own tree** — a case the existing rule does not name.

Related: `[[FINDING-2026-08-24-hq_C-strip-waves-1-3-landed-the-platform-axis-is-gone]]` ·
`[[FINDING-2026-08-23-hq_C-treebank-is-really-the-comma-selection-expression]]`
