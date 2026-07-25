# FINDING 2026-07-25 (s165) — ICN: `not` IS A ONE-LINE REPRO OF THE s164 SCAN/`else` DEFECT; IT IS ALSO `geddump`'s ROOT CAUSE

**Status: geddump ROOT-CAUSED. Two harness honesty defects FIXED and committed (SCRIP `fbce47dc`).
The emitter defect itself is NOT fixed.** The unified-root-cause section below is INFERRED FROM TWO IR
DUMPS, not yet confirmed in `emit.cpp` — it is labelled as such and must be verified before being relied on.

## 1. THE HARNESS WAS GRADING A KNOWN DEFECT AS A PASS (fixed)

`honest_icon_correctness.sh`'s `window()` extracted output between post.icn's
`*** Benchmarking with output ***` marker and the elapsed-time line. **`geddump`, `micsum` and
`tgrlink` do not link `post.icn`** (see the script's own `LINKDEPS` — geddump and micsum have no
entry, tgrlink has only `options.icn`), so the marker never appears, the window came back EMPTY on
BOTH engines, and `cmp` of two empty files graded **IDENTICAL**.

Consequence: **`geddump` — carried in the goal file as a LIVE DEFECT — was reported as a PASS**, and
`tgrlink`/`micsum` passed on empty rather than on their real 3,239L/2L outputs. Measured raw:

| program | oracle | SCRIP | raw verdict | harness said |
|---|---|---|---|---|
| geddump | 12,568L | 13,645L | **DIVERGE** | IDENTICAL ❌ |
| micsum | 2L | 2L | identical | IDENTICAL (right by luck) |
| tgrlink | 3,239L | 3,239L | identical | IDENTICAL (right by luck) |

**Fix:** `window()` falls back to the whole file when the marker is absent; two empty windows now
grade `NO-OUTPUT`, never a pass.

**The mirror defect in `honest_icon_bench.sh` (also fixed):** that runner claimed a correctness
verdict from a pass whose output post.icn SUPPRESSES, so `concord`/`deal`/`ipxref`/`queens` always
printed DIVERGE — a **false red on four programs that are byte-identical to the oracle**. It now
prints `n/a` for post.icn-linked programs and defers to the correctness runner, plus a footer
warning that a speedup without a correctness verdict is the `rsg` short-circuit trap.

⚠ **THE LESSON IS THE ONE s164 ALREADY WROTE, RECURRING ONE LAYER DOWN.** s164 built these scripts
precisely because `test_icon_bench_corpus.sh` graded "did it run" instead of "was it right." The
replacement then graded "did the extraction find anything" instead of "was it right." **An empty
comparison must never be a pass** — that is the general form, and it is worth checking for in the
Prolog/SNOBOL4 runners too.

**Correctness is now truthful in ONE run: 6 IDENTICAL (concord deal ipxref queens tgrlink micsum),
2 DIVERGE (geddump rsg).** This agrees with the goal file's 6/9 headline, which previously required
cross-referencing two scripts that each lied in one direction.

## 2. `geddump`'s ROOT CAUSE: A FAILING `not` DELIVERS SUCCESS

Divergence shape is diagnostic: **1,077 lines present only in SCRIP, ZERO lines missing.** SCRIP's
output is a strict SUPERSET — it over-emits child records rather than computing anything wrong.

`geddump.icn` line 54 guards child printing:

```icon
if (p.r === gedref(fam, "HUSB")) | (not gedref(fam, "HUSB")) then {
   every r := gedref(fam, "CHIL") do { ... }   # emits the "son"/"dau" lines
}
```

Children print under the husband, or under the wife ONLY when there is no husband. Processing the
WIFE: arm A (`===`) fails, and `gedref(fam,"HUSB")` succeeds so `not` must FAIL — the guard should
fail and children should not print again. **In SCRIP the arm succeeds, so every child prints twice.**

Discriminating table (subject-free, both modes, vs `iconx` 9.5.25a):

| expression | iconx | SCRIP |
|---|---|---|
| `if not (1=1) then "THEN" else "ELSE"` | ELSE | ❌ **NEITHER branch runs** |
| `if (1=2) \| (not (1=1)) then "BAD" else "OK"` | OK | ❌ **BAD** (arm delivers success) |
| `if (1=2) \| (2=3) then "BAD" else "OK"` | OK | ✅ OK |
| `if not (1=2) then "OK" else "BAD"` | OK | ✅ OK |
| `x === y`, `"a" ~=== "b"` | — | ✅ both correct |

`===`, `~===` and plain failing comparisons are FINE. The defect is specific to a **failing `not`**.

## 3. IT IS THE SAME DEFECT AS THE s164 SCAN/`else` BUG — AND `not` IS A STRICTLY BETTER REPRO

s164's repro needed a scan environment:
`procedure f(s); if s ? (="'") then return "THEN" else return "ELSE"; end`

**The `not` repro needs no scan machinery, no subject, no procedure, and is one line:**

```icon
procedure main(); if not (1 = 1) then write("THEN") else write("ELSE"); end
```

`iconx` → `ELSE`. SCRIP m3 AND m4 → **nothing at all**. Identical symptom to the scan case (a failing
condition never reaching `else`), with the scan variables removed. **Use this repro, not the scan one.**

## 4. UNIFIED ROOT CAUSE (INFERRED FROM IR DUMPS — VERIFY IN `emit.cpp` BEFORE RELYING ON IT)

`--dump-ir` on the `not` repro:

```
1      2@   2@   DISJUNCTION   [3,9@,10,9@,8,11]   <- the if: arm0 entry=3, arm1 (else) entry=10
5      1    6    BINOP_TEST    [3,4] binop=9       <- 1=1 : gamma=1, omega=6
6      7    1    VAR           [] var="&null"      <- not's success value, exactly ir_a_Not
```

LOWER is FAITHFUL to canonical `ir_a_Not` (`refs/jcon-master/tran/irgen.icn` L142-159): inner-expr
failure writes `&null` into the target then routes to success (node 6); inner-expr success routes to
the `not`'s FAILURE. **That failure edge is node 5's gamma = node 1 — the DISJUNCTION node itself —
and node 1's own gamma and omega are BOTH `2@` = FAIL.** So "arm 0 failed, advance to arm 1" is
executed as EXHAUSTION, and neither branch runs.

Now compare s164's scan dump (its own FINDING, verbatim):

```
14  gamma=1  omega=1   SCAN [4]   <- leave_fail: restore env, then -> node 1 (DISJUNCTION beta)
```

**SAME SHAPE.** Both constructs express arm-failure as a transition INTO the DISJUNCTION node (its
beta/resume edge). A plain failing comparison does NOT — and plain failing comparisons work
correctly in both engines. **THEREFORE THE CANDIDATE ROOT CAUSE, COVERING BOTH `geddump` AND `rsg`:
when an arm's failure re-enters the nary-DISJUNCTION node itself, the emitter treats the re-entry as
arm-list exhaustion instead of advancing to the next arm.**

This is consistent with, and sharpens, s164's conclusion ("START IN THE EMITTER... the arm neither
fails cleanly nor yields the alternative — it delivers an EMPTY VALUE SLOT"): an empty value slot is
what a consumer sees when the advance never happens.

⚠ **HONEST STATUS OF THIS SECTION:** this is read off two IR dumps plus a behavioural table. It has
NOT been confirmed by reading the DISJUNCTION arm-advance code in `emit.cpp`, and s164 recorded that
reasoning from source about this exact area was wrong once already. **Confirm in the emitter first.**

## 5. WHAT TO DO NEXT

1. In `emit.cpp`, read the nary-DISJUNCTION arm-advance path — what happens on re-entry at the
   DISJUNCTION node vs. arrival at an arm's fail-glue label (`na_s`/`na_f`, the `op_parts`/CV10
   channel s164 named).
2. Fix so re-entry advances to the next arm; the LAST arm's failure alone is exhaustion — this is
   canonical `ir_a_Alt` (`irgen.icn` L196-198): arm *i* failure goes to arm *i+1* START, and only
   `p.eList[-1].ir.failure` goes to the disjunction's failure.
3. Re-test in this order (cheapest first): the 1-line `not` repro, the s164 2-line scan repro,
   `geddump`, `rsg`, then `rung36_jcon_scan`/`scan1`/`scan2`, `recogn`, and the FZ-E cluster.
4. Do NOT re-try anything in s164's falsified table, including the `lower_icon.c` TT_SCAN subject-beta
   guard. **LOWER is not where this lives** — section 4 above shows LOWER matching canonical for `not`.

## 6. MEASUREMENT STATE AT CLOSE (RT_OPT=-O0, oracle iconx 9.5.25a built from the uploaded source)

Correctness 6/8 IDENTICAL, geddump + rsg DIVERGE. Timing (m4, minimum of 3): concord 0.61x ·
deal 0.31x · ipxref 0.51x · queens 1.10x · tgrlink 0.94x — reproduces s164's recorded
0.56/0.33/0.52/1.10/0.86 within run-to-run noise on a 1-CPU sandbox. **`rsg`'s 2.83x and `geddump`'s
0.68x are VOID** (both DIVERGE); the footer now says so in the runner's own output.
