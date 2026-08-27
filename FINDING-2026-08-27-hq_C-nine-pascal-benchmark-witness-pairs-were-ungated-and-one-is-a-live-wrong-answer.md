# FINDING — 9 Pascal benchmark witness pairs were reached by NO gate; one is a live wrong answer

**Seat:** `hq_C` · **Date:** 2026-08-27 · **Tree:** SCRIP `4ddea506` → `a90b684a` (post-rebase), `make pristine` `-O0` · **Oracle:** `fpc` 3.2.2 (ceo-ruled the same day)

## OCCASION

ceo corrected a stale-tree report of mine on `pascal-uplevel-nested-proc-hang` (I had graded a tree that predated `3579f7ef`; PULL-BOTH-REPOS-FIRST, my error, their measurement was right on all three arms). They also **honored the half of my T4 point that survived**: `benchmarks/pascal` has **no standing gate**, so T4 cannot distinguish *DONE+landed+ungated* from *DONE+not-landed* — and the cure for both is a gate. This is that gate, plus what building it found.

## WHAT WAS UNGATED

`test_gate_pascal_m3.sh` globs `corpus/tests/pascal/*.pas` plus a hand-maintained `crosscheck` family list. `corpus/benchmarks/pascal/` — **9 `.pas`/`.ref` witness pairs** — is in neither. Re-verified after the fix: with the new arm disabled the gate reports the identical pre-existing `FAIL=27`, so the arm contributes nothing but coverage.

## ⛔ MY FIRST TWO MEASUREMENTS WERE BOTH INSTRUMENT ERROR, IN THE SAME WAY, AND I NEARLY PUBLISHED THE FIRST

**Arm 1.** Ran all 9 under `< /dev/null` and measured **"7 of 9 produce WRONG ANSWERS"**. Every number was real. **7 of the 9 open with `readln(reps)`** — with no stdin, `reps` is 0, every loop body is skipped, and each program correctly prints its zero-iteration reduction. A full, plausible, entirely false red board.

**Arm 2.** Cross-checked against `fpc` and measured **"fpc disagrees with all 9 refs, so the refs are not oracle-derived"**. Also false: `fpc`'s default `integer` is **16-bit** and overflows the `seed*1309` multiply before the `mod 65536`, so the RNG diverges. The peer build needs `{$mode objfpc}`.

⭐ Both requirements are documented in `corpus/benchmarks/pascal/README.md`, **which I had not read.** Corrected: `printf '1\n'` and `{$mode objfpc}` → **8 of 9 match, `fpc` agrees with the `.ref` on value.** ⭐ The transferable half is not "read the README". It is that **both wrong arms were confidently, symmetrically wrong in the same direction — toward a red board** — and a red board is the shape a correctness seat is primed to believe. A number that confirms what you are looking for is the one to re-measure, not the one to publish. The `printf '1\n'` in the gate is load-bearing and commented as such.

## THE REAL FINDINGS, AFTER CORRECT INSTRUMENTATION

1. ⛔ **`quick.pas` is a LIVE WRONG ANSWER.** SCRIP prints `biggest = 10414`; `fpc` 3.2.2 **and** the checked-in `.ref` both say **15505** (`littlest = -50000` correct in all three). Its sibling `bubble.pas` — same RNG, same seed 74755, same reduction, differing only in the sort — gets 15505 **right** in SCRIP, so list construction is exonerated and the defect is in the sort. Row minted: `pascal-bench-quick-wrong-biggest`, with `bubble` named as the ASM-DIFF-FIRST passing sibling. **Invisible to every gate until today.**
2. **m4: 5 of the 9 SIGSEGV** (`bubble`, `intmm`, `queens`, `quick`, `sieve`; `perm`/`towers`/`uplevel2`/`uplevel3` match). This is the **already-tracked** `pascal-m4-registered-dispatch-segv` / `-intermittent-segv-pb30-sieve` class, not a new one — recorded as fresh evidence for those rows. It is also why the new gate arm is deliberately **m3-only**: wiring m4 would re-report two other rows as this gate's failure.
3. ⭐ **`README.md`'s `perm.pas` frontier note is STALE.** It states *"SCRIP currently returns 635 instead of 43300"*, tracked as PAS-FOR-RECURSE. Measured: `perm` = **43300**, matching both `.ref` and `fpc`. **Cured.** Recorded on the row for whoever next edits that file.
4. `uplevel2`/`uplevel3` **byte-match** their refs — ceo's correction confirmed in full, independently.

## THE GATE, AND WHY ITS EXCEPTION LIST FAILS BOTH WAYS

`quick` sits on `WITNESS_XFAIL`. ⛔ **An exception list that only permits FAILING lets a cure rot unnoticed** — so a listed witness that *passes* is a **RED** here (`XFAIL_STALE`), forcing the entry to be deleted in the same commit as the cure. Both rows' DONE-WHENs assert the removal of their own suppression for the same reason.

⚠️ **The Icon runner does not have this property, and it is worth fixing:** `test_icon_all_rungs.sh:89` returns XFAIL **without running the program**, so a cured `.xfail` there rots silently. Belongs to the V2-5 gate-honesty bucket.

**Negative-tested four arms** (honesty contract): green contributes `FAIL=0`; a mangled ref → `FAIL=1`; a listed-but-passing witness → `XFAIL_STALE=1`; all corpora empty → **REFUSES rc=2** with a named reason. Discovery is **by a file the directory must contain** (`uplevel2.pas`), never `-d` on the container — the s274 lesson, where a container survived the re-grid while its contents re-nested.

**Landed:** SCRIP `a90b684a`. Interim by construction — retires when `pascal-refs-regen-from-fpc-oracle` (rank 0) puts the directory on the graded board.
