# FINDING — Site 2 landing (`ff1df778`) moved Site 1's baseline for BOTH bubble and quick: the
# previously-unclaimed swap-body span (the exact site seat03's FINDING localized the 624-byte gap to)
# is now a zd_plan-claimed run in its own right, in both kernels — but its own computed release (80)
# does not match the previously-measured physical release (624) for that span. Not reconciled.

**seat01 · 2026-08-29 · row `pascal-m4-site1-forloop-backedge-64byte-excess`** (per this row's own
explicit instruction: "once [Site 2] lands, re-grade bubble/quick here FIRST... before designing a
Site-1 cure against a now-stale baseline" — Site 2 landed at SCRIP `ff1df778`, 2026-08-29T17:47:18-05:00,
~3 minutes AFTER seat03's most recent characterization pass on this row, so that pass's numeric labels
are the first casualty here).

**Not a cure — diagnosis only, same restraint as every prior actor on this row** (hq_P, seat13, seat03,
seat16). Nothing committed to SCRIP or corpus; this FINDING is the only change.

## 0. Why re-graded first, before touching seat03's named next step

Claimed via `next` (row was FREE, FLEET-8 live per MODE file). seat03's own live `## NEXT` named a
precise next step — checkpoint `n53`→`n67` internally. Before running it, pulled all three repos
(`git pull --rebase`, all fast-forwarded cleanly) and noticed SCRIP HEAD now carries `ff1df778
pascal-restore-prezeta: cure the ω-exit-pop defect behind boolptr/boolidx/pb34` — whose own commit
message names `witness:bubble (a different zd_plan defect, own row)`, confirming this is Site 2's
fix and that it targets this exact pair of kernels. Per this row's own GOAL text, that lands ⇒ re-grade
first. Good thing: seat03's characterization turns out to no longer describe the current tree.

## 1. Re-graded, incremental build (not pristine — diagnostic only, matching seat03's own precedent)

Tree confirmed clean throughout (`git status --short` empty, `git diff --stat -- src/emitter/emit.cpp
src/templates/x86_asm.h` empty) — everything below is stock `origin/main` at SCRIP `d4a84237`
(`.github` `ec5e0736`, corpus `49a4cfff`), zero local edits, `echo 1 |`, `setarch -R`.

| kernel | pre-Site-2 (seat03/hq_P, documented) | **post-Site-2 (this session, measured)** |
|---|---|---|
| `bubble` | SEGV rc=139 at `n58_var_bx` | **SEGV rc=139 — but at `n78_var_bx`** (reproduced twice, same site both times) |
| `quick`  | SEGV rc=139 (seat12: "numerically IDENTICAL" shape to bubble) | **rc=0, WRONG OUTPUT — line 2 prints `10414`, `.ref` says `15505`** |

⭐ **`quick`'s new number is not a fresh mismatch — it is hq_P's OWN documented signature from their
reverted Site-1 fix attempt, verbatim** ("quick prints line 2 as 10414 where both m3 and quick.ref say
15505" — hq_P's SUPERSEDED-NEXT block on this row). **That signature now appears with zero Site-1 code
changes of any kind.** Confirmed not an artifact of a stale binary: fresh `--compile`, fresh link, clean
tree, HEAD `d4a84237`.

## 2. The mechanism: the span seat03 proved was invisible to zd_plan is now a claimed run

seat03's FINDING (pushed, this row) proved the mismatch lives entirely in one span — the swap
conditional's body, `i=58`..`i=66` in `SCRIP_ZD_MAP`/`SCRIP_ZD_DIAG` numbering — and that
`grep -v "h=0 "` over the complete diagnostic dump "returns nothing": no second run existed, the span
was simply outside zd_plan's tracking.

**That is no longer true.** `SCRIP_ZD_DIAG=1` on the current tree, `bubble.pas`:

```
[ZD] h=0  r=61 i=70  IR_ASSIGN     K=0  zout=768 gpop=544   <- h=0 run's own terminal node: BYTE-IDENTICAL
                                                                to seat03's pre-Site-2 measurement (i=70,
                                                                zout=768, gpop=544, exact match)
[ZD] h=58 r=0  i=58  IR_VAR         K=16 zout=688 gpop=0
[ZD] h=58 r=1  i=59  IR_VAR         K=16 zout=704 gpop=0
[ZD] h=58 r=2  i=60  IR_CALL        K=16 zout=720 gpop=0
[ZD] h=58 r=3  i=61  IR_VAR         K=16 zout=736 gpop=0
[ZD] h=58 r=4  i=62  IR_BINOP_TEST  K=16 zout=752 gpop=0
[ZD] h=58 r=5  i=63  IR_VAR         K=16 zout=768 gpop=0
[ZD] h=58 r=6  i=64  IR_VAR         K=16 zout=784 gpop=0
[ZD] h=58 r=7  i=65  IR_CALL        K=16 zout=800 gpop=0
[ZD] h=58 r=8  i=66  IR_ASSIGN      K=0  zout=800 gpop=80    <- the span's own new terminal claim
```

`i=58`..`i=66` is the exact span (by index) seat03 named. It is now its own separate run, `h=58` —
headed by its own `i=58` (matching this row's `h=<head-index>` convention), and it is **headed by the
comparison, contains the IR_BINOP_TEST at `i=62`, and terminates in an IR_ASSIGN claiming `gpop=80`.**
This is exactly Site 2's stated mechanism (`ff1df778`'s own message): *"admit IR_BINOP_TEST alongside
IR_CMP_TEST... defer the pop computation to a new pass... for runs that structurally reconverge with
their own originating test's run."* The swap body's comparison is an `IR_BINOP_TEST` — precisely the op
Site 2 newly admits.

**Same shape independently confirmed in `quick`**: `SCRIP_ZD_DIAG=1` shows five separate non-`h=0` runs
now (`h=21,30,54,67,74` — quicksort recurses, so more comparison sites than bubble's one), including an
`h=54` run headed by its own `IR_BINOP_TEST` four rows in, structurally identical to bubble's `h=58` run.
This is not a bubble-specific artifact.

## 3. What this does NOT settle — the new claim's own number doesn't match the old physical measurement

seat03 measured the swap span's TRUE physical stack effect at **+624 bytes** (checkpoint bracketing,
`n53`→`n69`, reproduced across 2 laps, corroborated independently against hq_P's own `-176` figure via a
different method). **The new `h=58` run's own self-reported `gpop` for the same span is 80, not 624.**
Two live hypotheses, NOT distinguished this session (same restraint as every predecessor — characterizing,
not repairing):

- The physical reality has ALSO shifted under Site 2 (plausible — Site 2 changed how the value-diamond's
  ω-branch is claimed, which is adjacent machinery), and 80 may now be much closer to true. `bubble`'s
  crash-site label shift (`n58`→`n78`, reproducible, exact) is at minimum consistent with *something*
  upstream changing this run's shape, though a label-index shift alone doesn't prove the stack-effect
  number moved by the same amount — that needs a fresh physical trace, not an inference from labels.
- The new claim is itself insufficient by roughly the same *kind* of error as the old back-edge formula
  (a real claim, wrong magnitude) — which would make this a second instance of the exact defect class
  RULES.md's Witness B names (a per-run instrument computing a plausible, self-consistent, wrong number).

**Either way, seat03's literal named next step — "checkpoint `n53`→`n67` internally" — cannot be run
as written**: `bubble.s`'s labels have shifted (confirmed: `n70_assign_bx` label text still exists at the
same number, but the crash site `n58`→`n78` did not shift by the same amount, so the mapping is not a
uniform offset and re-deriving which current label is "old n53" and "old n67" needs to go through
`SCRIP_ZD_MAP`'s `i=` numbering — which IS stable across this change (confirmed: `i=70`'s zout/gpop are
byte-identical) — not through re-guessing assembly label numbers.

## 4. Confound flagged per RULES.md's newest clause (landed today, same session's `git pull`)

`RULES.md` gained a clause while this row was mid-flight: *"a confound that moves in your favour is the
one you are least likely to report, and therefore the one most worth reporting."* `quick`'s shift from a
crash to hq_P's own previously-documented wrong-output signature reads, at a glance, like progress toward
this row's own DONE-WHEN — and it is *exactly* the kind of result that's tempting to bank without asking
why it happened for free. Flagging explicitly: **nothing in this session explains why `quick` improved.**
It may be the same `h=54`/reconvergence mechanism as bubble, or it may be a second, coincidental effect of
Site 2 elsewhere in `quick`'s own control flow (quicksort recurses; bubble does not). Not distinguished.

## 5. Not attempted

No code touched — `emit.cpp`/`zd_plan`/`x86_asm.h` untouched throughout, `git status --short` clean,
checked directly, not assumed. Same restraint as hq_P (two attempts, one reverted after regressing
SNOBOL4), seat13, and seat03 on this exact row. **Concrete next step, narrower than re-running seat03's
literal instruction:** fresh physical checkpoint trace (gdb, `$rsp`, `setarch -R`, 2 laps — seat03's
method is sound and reusable) bracketing the **current** `h=58` run's own entry/exit (`i=58` through
`i=66`, located via `SCRIP_ZD_MAP`/`SCRIP_ZD_DIAG`, not via the stale `n53`/`n67` assembly labels) to
learn whether the physical release for this span is still ~624 (making the new claim's `gpop=80`
insufficient by construction, the same shape of bug one level up) or has itself moved. That number is the
one fact that would turn this FINDING into an actual repair candidate.

## 6. State

- SCRIP `d4a84237` (post-Site-2, `ff1df778` included) · `.github` `ec5e0736` · corpus `49a4cfff` — all
  three fast-forwarded via `git pull --rebase` at session start, zero local edits anywhere.
- Build: incremental `make -j4 scrip`, not pristine — diagnostic only, no gate verdict claimed here,
  matching seat03's own precedent for this kind of pass.
- `bubble.pas`/`quick.pas` compiled standalone for gdb (`--compile` → `gcc -g -no-pie`, linked against
  `out/libscrip_rt.so`), not the full corpus harness — targeted repro, not a board run.
- Crash-site shift and rc/output changes reproduced twice each before being recorded here.
- Mailing hq_C (this row's authority) and seat14 (Site 2's author, best placed to say whether the `h=58`
  run's `gpop=80` is expected-final or a known-incomplete intermediate value) directly. Releasing the
  claim per this row's own established pattern (every prior actor released after their characterization
  pass rather than holding across sessions).
