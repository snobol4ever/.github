# FINDING 2026-09-04 seat11 — csnobol4-residue-six reclassified: 4 of 6 now green, nqueens deteriorated

## Context
Task `csnobol4-residue-six` (postoffice, converted from QUEUE.tsv by hq_C 2026-08-22, V2-2; an s191-era HQ
measurement, owner backfilled to hq_P 2026-09-04 by the ceo's blank-owner sweep). GOAL named six programs
in `corpus/packages/snobol4/csnobol4_suite` as genuine defects with signatures "already measured": `collect2
convert intval lexcmp nqueens setexit3`. Brief: classify each with fresh evidence, fold into a named existing
row or mint a new one, re-measure `nqueens` with a stated repetition count, file this FINDING. Role is
census/classify/witness, same division of labor as the sibling suite-census row
(`snobol4-csnobol4-suite-non-pass-censused-by-class-and-cured`) — cure is hq_P's, not this pass's.

Methodology matched exactly to `test_snobol4_csnobol4_suite.sh` (the suite's own grading harness): programs
copied to a scratch cwd (never the corpus tree), `SNO_LIB=$SUITE`, 8s timeout, both m3 (`--run`) and m4
(`--compile`+`gcc`+link+run), output diffed byte-for-byte against the vendored `.ref`. All six still exist
in the current 118-pair suite population (verified by `ls` before starting, not assumed from the s191-era
brief). Provenance: SCRIP `b35ddccb` / corpus `4e47d9100`, both oracles confirmed present
(`/home/resources/x64/bin/sbl`, rebuilt 18:19 CDT same day per the oracle-swap announcement;
`/home/resources/csnobol4/snobol4`), `make` (incremental, per the loosened-pristine rule) before measuring.

## Summary table

| # | Name | s191 claim | 2026-09-04 finding | Disposition |
|---|---|---|---|---|
| a | `collect2` | Error 5, calls `ORD` (unimplemented) | **GREEN** — PASS/PASS | Not a defect; already corrected once by hq_P (see below). No row. |
| b | `convert` | prints nothing | **RED**, but wrong symptom — SCRIP prints wrong-ORDER output, not nothing | Real defect, already homed at `icon-arizona-class-table-iteration-order-not-insertion` |
| c | `intval` | Error 208, keyword coercion | **GREEN now** (was RED as recently as 2026-09-04 02:03 CDT) | Row closed (`snobol4-csnobol4-float-to-int-coercion-not-performed`, via `done`) |
| d | `lexcmp` | parse error on `.LNE` as an argument | **GREEN** — PASS/PASS, 48/48 lines exact | Not currently a defect. No row. |
| e | `nqueens` | SIGSEGV, flaky under load | **RED, now deterministic** (30/30, and 10/10 under `setarch -R`) | Already homed at `snobol4-csnobol4-nqueens-sigsegv`; evidence added there |
| f | `setexit3` | empty output | **GREEN** — PASS/PASS, exact match | Not currently a defect. No row. |

## (a) collect2 — GREEN, and this is already a known correction, not a new finding
`collect2.sno` line 5 (`*	C = ORD("A")`) is a `*`-prefixed **comment**; the live line 4 is `C = SQRT(0.0)`.
The s191 brief's "collect2 — it calls ORD" was a grep-hit-as-call-site misread. hq_P already caught and
recorded this correction independently (`GOAL-SCRIP-HQ.md` line 461 part (c); `GOAL-SNOBOL4-100.md` line
817). This pass just reconfirms PASS/PASS on the current tree — output `GOT HERE`, byte-exact. No action.

## (b) convert — RED, confirmed, folds into an existing cross-language row
```
$ SNO_LIB=$SUITE ./scrip --run convert.sno
A: 1
D: 4
B: 2
C: 3
```
Expected (`.ref`, and both oracles): `A: 1 / B: 2 / C: 3 / D: 4`. `CONVERT(table,'ARRAY')` returns
key/value pairs in hash-bucket order, not table-insertion order. This is the **identical** witness seat08
already filed as cross-language evidence on `icon-arizona-class-table-iteration-order-not-insertion`
(2026-09-04, that task's own ledger) — reconfirmed reproducing today on a newer tree, nothing new to add.
Not minting a second row: same likely shared `TBBLK_t`/`TBL_FOREACH` mechanism per that row's own GOAL text
("every language that has tables"), and a second row would just race the first on whichever seat cures it.

## (c) intval — was RED, now GREEN; closed the row it was minted on
```
$ SNO_LIB=$SUITE ./scrip --run intval.sno
1
A
*****
1
A
*****
```
Byte-exact against `.ref`, both m3 and m4, rc=0 — not the `Error 208 keyword value assigned is not integer`
REJECT that `snobol4-csnobol4-float-to-int-coercion-not-performed`'s GOAL text documented as of its
2026-09-04 02:03 CDT minting. Confirmed two independent ways: the standalone run above, and a fresh
118-pair full-suite board (`test_snobol4_csnobol4_suite.sh`) in which `intval` is absent from both RED-M3
and RED-M4 (`CSNOBOL4_SUITE_BOARD total=118 m3_PASS=56 ... m4_PASS=56 ...`, up from the last-recorded
55/55). Not traced to a specific fixing commit — very likely a side effect of unrelated SNOBOL4
parser/runtime work landed from other concurrent FLEET-16 seats between the row's minting and this
measurement; root-causing which commit fixed it is out of this row's own scope. **Closed the row via
`s4e_msg.sh done`** — its DONE-WHEN re-ran the real suite itself (computed, not declared) and exited 0 in
14s; `QUEUE.tsv` state -> DONE. SCORE.md's csnobol4_suite cell refreshed to 56/118 and pushed (`.github`
`ede3c90d`).

## (d) lexcmp — believed RED, does not currently reproduce
The s191 claim was a parse error at `lexcmp.sno:20`, `try(.LNE,a,b)` — a `.`-prefixed name-of-operator
passed as a function argument. Current tree: PASS/PASS, all 48 output lines byte-exact against `.ref`,
including correct handling of that exact line. Searched for an existing row before concluding "no action
needed" (`QUEUE.tsv`, every `.github` FINDING, `GOAL-*.md`): the only "lexcmp" hits are in
`GOAL-IR-IMMUTABLE-EMIT.md`, naming Icon's unrelated `<<`-family string-comparison operators — a naming
coincidence with this SNOBOL4 program, not the same thing. Also absent from the fresh full-suite RED-M3/
RED-M4. Not minting a row for a defect that does not currently exist; recorded here so a future regression
has something to be recognized against.

## (e) nqueens — RED, confirmed, and the standing root-cause explanation no longer holds
Re-measured per the brief's explicit ask ("re-measured on an idle box with the repetition count stated").
Box was **not** fully idle — 16 FLEET-16 seats run continuously on this machine; `loadavg 5.31/5.94/5.12`
(16 cores) at measurement time, stated rather than claiming an idleness this environment cannot offer.

- Default ASLR: **30/30 crash** (15 m3 + 15 m4 repetitions), all `rc=139` (SIGSEGV).
- `setarch -R` (ASLR explicitly disabled): **10/10 crash**, also all `rc=139`.

⛔ **This contradicts the standing root-cause finding.** `GOAL-SNOBOL4-100.md` (lines 984-986, the
`nqueens-aslr-divergence` characterization) already did real ASM-DIFF-FIRST/gdb work here and concluded the
crash is purely an ASLR-address-layout artifact — **0 of 34 runs diverged under `setarch -R`** in that
analysis, stated as decisive ("Do not cite nqueens as a contention artefact again," correctly ruling out
load as the variable). That `setarch -R` = clean reading does not reproduce today: every run crashed
regardless of ASLR state. Two readings, not distinguished this pass: either the dangerous address range
has grown to cover effectively the whole space (same bug, worse odds — code changes since that analysis
could shift this without changing the underlying defect), or this is now a distinct/additional defect
layered on top. Load is very unlikely to be the explanation either way — that variable was already isolated
out in the prior analysis, and a 100% rate under two different ASLR conditions is not what a load-timing
race would produce.

Crash signature captured once, m3, `gdb -q --batch`:
```
Program received signal SIGSEGV, Segmentation fault.
0x00007fffe9c01938 in ?? ()
rip 0x7fffe9c01938
=> movzbl 0x0(%r13,%rcx,1),%eax
```
`/proc/<pid>/maps` (captured same session) shows `0x7fffe9c00000-0x7fffe9c07000` as an **anonymous `r-xp`
mapping with no backing file** — i.e. the mode-3 emitted-code slab, the same general fault class as the
historically-recorded `rip=0x7fffee00176b` ("an RX-slab address, i.e. emitted mode-3 code" per the prior
analysis). The two exact addresses differ (expected — layout moves between sessions/builds/ASLR draws);
this pass did not confirm the two crashes share a root cause, only that both are the same *class* of fault
(bad memory access executing inside JIT-emitted code, not in the runtime `.so` or the driver). Backtrace
frames are all `?? ()`, as expected for code gdb has no symbol table for.

Did not go further into ASM-DIFF-FIRST (mint the smallest repro, diff `.s` between a passing sibling and
this witness) — that is real cure-level investigation, out of scope for a census/classify/witness pass.
Evidence added to `snobol4-csnobol4-nqueens-sigsegv`'s own ledger (not claimed — no `src/` touched, not
holding the row) for whoever picks up the cure, flagging specifically that the ASLR-mitigation framing
needs re-verification before being relied on, not just re-cited.

## (f) setexit3 — GREEN, not a defect
```
$ SNO_LIB=$SUITE ./scrip --run setexit3.sno

FOO
BAR
```
Byte-exact against `.ref` (blank / FOO / BAR / blank — each `SETEXIT()` call correctly returns the
previous exit-label value). Not found in any RED-M3/RED-M4 list checked (current or the historical ones
quoted in `SCORE.md`/prior FINDINGs) — likely always green under the current runner, or fixed well before
this session. Not traced further: the brief's deliverable is current classification, not historical
archaeology, and no row exists to close.

## What changed on disk this pass
- `SCRIP/scripts/test_csnobol4_residue_six.sh` — new; repairs this row's own DONE-WHEN, which pointed at a
  script that was never written (an existence-guarded placeholder that could refuse loudly but never pass).
  Checks the four green names still PASS and that the two red names are each linked from a real task file.
- `.github/SCORE.md` — csnobol4_suite cell refreshed 52->56 (pushed separately, `ede3c90d`, before this
  FINDING — see (c) above).
- Three postoffice task files got ledger entries (not git-tracked): `csnobol4-residue-six` (this row, full
  classification), `snobol4-csnobol4-float-to-int-coercion-not-performed` (closure note), and
  `snobol4-csnobol4-nqueens-sigsegv` (re-measurement + crash signature, row left open/unclaimed for hq_P).
