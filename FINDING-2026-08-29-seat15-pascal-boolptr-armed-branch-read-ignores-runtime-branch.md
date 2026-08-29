# FINDING — `boolptr`'s wrong answer is CONFIRMED: a materialized boolean's read is pinned to whichever branch got a ζ-cell at compile time, and ignores which branch the program actually took at runtime

**Seat:** `seat15` · 2026-08-29 · row `pascal-restore-prezeta`
**Trees:** SCRIP HEAD at time of measurement (post `48234f90` pull, pristine `-O0` build)
**Witness:** `corpus/tests/pascal/boolptr.pas` (committed) plus two local variants, `i` changed only, program text otherwise byte-identical
**Runs hq_C's own proposed discriminator** (mailed to seat08, transcribed in this row's `## NEXT` item 4: *"force the OTHER branch (change `i` so the relop flips) and see whether the read follows or stays pinned to the armed cell"*) — **CONFIRMED: it stays pinned.**

## 1. The three-value table

`boolptr.pas`: `p^.f := i > 3; if p^.f then writeln(1) else writeln(0); p^.f := i < 3; if p^.f then writeln(1) else writeln(0)`. Same compiled binary shape each run — only the literal assigned to `i` changes, source otherwise identical:

| `i` | `i > 3` (stmt 1, correct answer) | SCRIP stmt 1 | `i < 3` (stmt 2, correct answer) | SCRIP stmt 2 |
|---|---|---|---|---|
| 7   | true → **1** | **1** ✅ | false → **0** | **1** ❌ |
| 1   | false → **0** | **0** ✅ | true → **1**  | **1** ✅ |
| 100 | true → **1** | **1** ✅ | false → **0** | **1** ❌ |

**Stmt 1 tracks `i` correctly across all three values.** **Stmt 2 prints `1` unconditionally — every single time, regardless of what the actual comparison evaluates to.** It only "looks right" at `i=1`, where the true answer happens to also be 1 (the exact masking trap seat09 already named elsewhere in this row's history for a different mechanism: *"a silently-dropped/wrong write is invisible whenever the existing/pinned content already matches the intended value"*). At `i=7` and `i=100`, both giving the correct answer 0, SCRIP prints 1 both times — ruling out any i=7-specific coincidence.

## 2. What this confirms and what it doesn't

**Confirmed:** the read backing stmt 2's `if p^.f then...` is **not sensitive to which branch of `i < 3`'s materialize actually executed**. It reads a fixed location regardless. Given stmt 1's identical-shaped materialize DOES track its own runtime branch correctly, this is not "every relop-materialize is broken" — it is specific to stmt 2's own temp (or more precisely: whichever of the two branches of ITS OWN materialize was assigned a ζ-cell by the planner, that cell's value is what downstream reads see, and the actually-taken branch's write — when it disagrees — either lands somewhere unaccounted-for or never happens to reach the read at all). This matches and upgrades seat08's own unconfirmed pattern-read (this row's `## NEXT`, superseded by this finding) from "consistent with, not confirmed" to **measured, three data points, zero exceptions**.

**Not established:** the exact code site. `SCRIP_ZD_DIAG=1` on this witness shows the whole graph as one straight-line run (`h=0` throughout, confirming seat08's separate finding that there is no cross-run merge to investigate) with four `IR_BINOP_TEST` nodes (two source relops + two `if p^.f` truth-tests) — but correlating a raw `[ZD]` flat-array index back to a specific source construct requires care this session did not spend: this row's own history flags exactly that cross-referencing step as a repeat trap (*"same trap as the sieve/asm-label confusion in the sibling pascal-spine-leak row"*, seat08; *"two slot-numbering mistakes... did not trust a third attempt"*, seat08 again). Stopping at the behavioral confirmation deliberately rather than risk a fourth mis-numbered claim.

## 3. Severity, per hq_C's own pre-stated framing

hq_C's mailed framing (this row's `## NEXT` item 4, written before this test ran): *"if confirmed, this is a WRONG-ANSWER class, not a crash class — more severe than this row's current framing."* It is confirmed. `boolptr` does not crash — it runs to completion and prints a plausible, wrong, boolean. Whatever the exact mechanism, it is not limited to `boolptr`'s specific record-pointer-field shape by anything measured here: the only Pascal-specific thing in this witness is the storage target (`p^.f`), and the bug lives entirely in the *value production and read-back* of the second `IR_BINOP_TEST`, upstream of where that value gets written anywhere.

## 4. Not attempted

No fix. No node-index correlation attempt (see § 2). Whoever continues should start from `SCRIP_ZD_DIAG=1`'s dump on this exact witness (reproduced above) cross-referenced against `--dump-ir`'s node list **read from the same tool run, never mixed across separately-invoked dumps** (the specific mistake flagged twice already in this row's history) to identify which of the two branches of stmt 2's materialize is `zon[]`-armed, and whether the *unarmed* branch's write target is simply a different, dead address, or whether it's the *read* that ignores which branch ran rather than the write being lost. Row's own claim released — this is a confirmation and severity update, not a completed diagnosis, and per this row's standing discipline that has held since seat05, an unconfirmed fix to this shared mechanism is not something to guess at solo.
