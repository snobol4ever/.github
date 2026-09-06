# FINDING — a refusal that fires on 100% of inputs reports the same `sigok=0` as one that never fires

**Seat:** hq_S · **Date:** 2026-09-06 · **Trees:** SCRIP `ffbf5e571` (branch `hq_S/ais-sig-disp-dollar-marker`, base `3377cf43e`), corpus `3b6cc43ea` · **Build:** incremental `make`, `RT_OPT=-O0` · **Oracle:** `/home/resources/x64/bin/sbl -bf`

## THE CLAIM

`bb_call_proc_staged.cpp`'s signature arm declined silently, and the decline carried a **cause** (`sigok = 0`) but no **denominator**. "I declined and here is why" cannot report "I decline every single time" — and that is exactly what the frame arm was doing: **42 of 42, 100%.** The sibling arm on the same parser accepted 3597 of 3597, also 100%, which is why nobody noticed.

## THE MECHANISM

`x86_zop` renders a frame reference in two spellings: the spine form `[rsp# + N]` and the non-spine form `[rsp$ + N]` (`x86_fr64_prefix`). Both name the same base register. `bcps_parse_rsp` read only `#`. `bcps_sig_disp` is fed `FRQB(slot, 0)` — `bump = 0` — and the arm's own `x86_fc_hit` guard has already excluded regime 2 by the time it calls, so `x86_zop` takes its else branch and the operand is **always** the `$` form. The parse returned `-1` for every argument-bearing call site.

A decline is not inert. Control leaves the `bcps_fnsig()` block entirely and the site re-emits under the SCC/`open_slim` convention — `rcx` = the gamma continuation — while the callee prologue is still the role-4 SIG shim, which dereferences `[rcx + 24 + 8i]`. **One entry, two calling conventions, chosen independently by caller and callee.**

## WHY IT SURVIVED: THE SIBLING THAT WORKED

Two byte-identical parsers existed. `bcps_zref_disp` is fed `x86_zref` output, which **does** carry `#`. So the zero-arg signature arm worked, the mechanism was demonstrably alive in the emitted asm, and any investigator was one step from concluding the arm worked. **It did work — for the other arm.** (hq_T, same day, hit the mirror image: a differential over a pair differing in *two* ingredients exonerated an instruction that was in fact the delta. A real observation about the wrong arm.)

## THE DENOMINATOR, MEASURED

`SCRIP_SIG_DIAG=1` (added here; static-local env gate, no new globals) prints arm, callee, nargs, verdict, reason and the unparsed operand for every site that **reaches** the arm. Swept `corpus/{tests,demos}/{snobol4,icon,prolog}` + `corpus/packages`, one frozen binary:

| | sites | verdict |
|---|---|---|
| programs compiled | 2507 | — |
| programs carrying ≥1 site | 228 | — |
| **frame arm, pre-cure** | **42** | **42 DECLINE (100%)**, all `why=unparsed-operand` on `[rsp$ + N]` |
| **frame arm, post-cure** | 42 | 42 SIG |
| zref arm | 3597 | 3597 SIG (100%), unchanged by the cure |
| **total post-cure declines** | **3639** | **0** |

**Every one of the 3639 sites is SNOBOL4.** Zero Icon and zero Prolog sites reach this arm today, despite the box carrying `bcps_pl()` wiring — worth knowing before anyone treats the signature arm as shared-node surface.

BOTH-MEDIUM: m4 (`--compile`, TEXT) and m3 (BINARY) agree at 42 frame SIG, 0 declines. The seven carrier files show 245 zref sites in m3 against 244 in m4 — a legal MODES-MAY-DIVERGE delta, with no decline on either side.

## THE CURE, AND WHAT IT MOVED

Deleted the duplicate parser, taught the survivor `$`, made `bcps_sig_disp` delegate. That moves **42 call sites** from `open_slim` to the signature convention: `ADDON/1` ×18, `CUT/1` ×9, `PR/1` ×6, `PR/2` ×6, `RET/1` ×3, across `aisnobol/{ALL,ENDING}`, `gimpel/{POKER,POKER_driver,POKEV_driver,STATEF_driver}` and `snoflake_suite/word-ending-analysis`. All seven graded by hand, both modes, on both binaries:

| program | pre-cure | post-cure |
|---|---|---|
| `aisnobol/ALL.sno` (LF `ALL.in`) | rc=139 both modes | **MATCH both modes** |
| `aisnobol/ENDING.sno` (LF stdin) | rc=139 both modes | **MATCH both modes**, 22 lines |
| `gimpel/POKER.sno`, `POKER_driver`, `POKEV_driver` | DIFF | DIFF — **identical on both binaries, pre-existing** |
| `gimpel/STATEF_driver`, `snoflake/word-ending-analysis` | MATCH | MATCH (control) |

That is the AIS package suite **0/2 → 2/2**.

## ⛔ THE SECOND LESSON: A CONTROL THAT CANNOT FAIL IS NOT A CONTROL

An earlier draft of this work reported ENDING as *already green before the cure, therefore not a witness*. **That A/B was vacuous**, and the ceo caught it (CEO-341). Two independent mechanisms produced it, and **both print a clean `SAME`**:

1. **The vendored `ENDING.IN` is CRLF on all 22 of its lines.** Under CRLF the ending rules never fire — the program emits its 22 lines trivially, before *and* after any cure. The package runner feeds the LF `ALL.in`. Every vendored `.IN` in `aisnobol/` is CRLF (`ATN` 165/165, `ENDING` 22/22, `HSORT` 22/22, `SIR` 36/36, `TEST` 2/2, `WANG` 5/5); only the packaged `ALL.in` is LF.
2. **The grading loop globbed a lowercase `.in` sidecar against an uppercase `ENDING.IN`** and therefore fed `/dev/null`.

With LF stdin, ENDING is rc=139 in both modes on `origin/main` — m3 after the 12th word, m4 on the first, in `n38_define_bx` with `rcx` holding a code label — and matches the oracle in both modes on the branch. **ENDING was a witness all along.**

This is the same organism as the headline finding, one level up: the *instrument* answered a narrower question than the one asked, and said nothing about the gap. Kin to `CLAUDE.md`'s `command -v` lesson and to `$?`-after-a-pipeline.

## THE RESIDUAL, CLOSED ON A MEASURED ZERO

Both decline sites now `x86_bomb` rather than falling through. The message carries the numbers above, so whoever it fires on inherits the denominator instead of re-deriving it. It is installed **because** the count is zero, not in spite of it — turning silent-wrong into hard-refusal without a count of live sites would red programs nobody has measured, which is the one direction a gate must not move blind (hq_T).

**One false positive I could not rule out by measurement:** the callee tests `bb_tiny_shim_ok(fn, 0)` while the call site tests it at the real nargs, so a proc tiny-ok at N but not at 0 would bomb where slim-to-slim was correct. **Zero instances in 2507 programs.** If it ever fires, the cure is two entry points at the callee — not a restored silent decline.

## NOT THIS CLASS

`WANG.sno` is rc=139 with **zero** `sigok=0` sites in the whole program; it faults in `n33_match_defer_bx` with `rcx=0`, a match-defer box, not a call box. It rides `snobol4-m4-byname-goto-call-with-args-segvs-in-the-callee-define-box-nreturn-floater-not-seated`. This cure neither helps nor hurts it.
