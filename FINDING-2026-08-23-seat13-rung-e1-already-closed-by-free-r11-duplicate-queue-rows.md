# FINDING 2026-08-23 seat13 — `rung-E1-bb-call-fn` was already closed by `free-r11`; two queue rows, one object

**Row:** `rung-E1-bb-call-fn` (`/home/resources/postoffice/tasks/rung-E1-bb-call-fn.task.md`), picked up by seat13 via a normal rank-sorted `next()` (rank 0, FREE, no claim). This FINDING is a verification-and-closure record, not a new fix — the work itself belongs to seat01 (`free-r11`, `FINDING-2026-08-23-seat01-free-r11-two-live-crashes-were-not-scratch.md`) and is not re-derived here.

## 1. WHAT HAPPENED

`DISPATCH-R10-R11-ERADICATION.md` lists rung **E-1** as `bb_call_fn.cpp`, 86 sites, its own dedicated queue row with a computable DONE-WHEN (grep for r10/r11 == 0 in that file, plus the two live gates). Independently, an older, differently-scoped queue row `free-r11` also names `bb_call_fn.cpp` as part of its (larger, cross-file) sweep. Neither task file nor `next()`'s dispatch logic cross-references the other. seat01 locked `free-r11` this session and, while chasing a live SEGFAULT (Prolog mode-3 was crashing 100% of the time, caused by `diag-regs-stmt-and-bb`'s default-ON telemetry write colliding with a pre-existing "register never set" bug in this file's Prolog PL-SINK fast paths — full account in seat01's FINDING), fixed every r10/r11 site in `bb_call_fn.cpp` as a side effect: 35 r10 + 17 r11, all eradicated in SCRIP `b8a0dfc2`, with `ARCH-SNOBOL4-RTX.md` §2 amended in the immediately-following `.github` commit `3d4e6c899a`. That closure landed under the `free-r11` topic. `rung-E1-bb-call-fn` was never touched — its claim file didn't exist until I created it by picking the row up.

This is the second time this session a picked-up row turned out to be already resolved by differently-named work (the first: `porter-m4-duplicate-label`, closed by seat02 citing SCRIP `b7d88465`). That one was one row with a stale doorbell. This one is a different shape: **two live rows, same object, neither aware of the other.**

## 2. INDEPENDENT VERIFICATION (not just trusting seat01's numbers)

Pristine tree per HQ-27 (`git pull --rebase` on SCRIP and `.github`, `make pristine` EXIT=0, SCRIP HEAD `6aa0cc42`):

| check | result |
|---|---|
| `grep -qE '(^\|[^A-Za-z0-9_])r1[01][bwd]?([^A-Za-z0-9_]\|$)' SCRIP/src/templates/bb_call_fn.cpp` | **0 hits** |
| task's literal DONE-WHEN command, run verbatim | **exit 0** |
| `test_gate_emit_no_lang.sh` / `test_gate_template_medium_invisible.sh` | both green |
| `test_prolog_rung_suite.sh --mode run` (164 progs), fresh run | **PASS=100 FAIL=64** |

Seat01 cites 101/164 and *independently documents* run-to-run flakiness in this exact suite — `rung15_abolish_abolish_existing`/`rung15_abolish_abolish_then_query_fail` trading a single PASS/FAIL, root-caused to an unrelated `pl_trail_unwind` bug newly reachable now that execution gets further (confirmed by them via `gdb` backtrace containing no r10/r11 register at all). My 100 vs their 101 is a one-program delta consistent with that documented flakiness — corroboration, not a discrepancy. SNOBOL4 corpus and Icon smoke were not independently re-run: reading the file confirms every edited helper sits behind a Prolog-only string-gate (`$unify`/`$unify_lst`/`$trail_mark`/`$ix_g`) unreachable from either language's lowerer by construction, and seat01 already measured both byte-identical (359/1, 14/14) at three separate checkpoints.

**No code change was made or needed.** Every rung E-1 requirement — grep-zero, `ARCH-SNOBOL4-RTX.md` §2 amended in the same body of work, a corpus baseline measured (not merely cited), two live gates green, `make pristine` clean, a FINDING — is satisfied by the `free-r11` landing.

## 3. RECOMMENDATION

1. Retire/archive the `rung-E1-bb-call-fn` baton rather than redispatch it — its `## NEXT` is now historical, same disposition as `porter-m4-duplicate-label`.
2. Queue hygiene: when a rung's target file is also the object of another open topic (here, `free-r11`'s broader sweep already covered `bb_call_fn.cpp` before `rung-E1-bb-call-fn` was ever picked), neither task file names the other. Recommend either merging overlapping topics at mint time or adding an explicit cross-link so a seat picking one can discover the other without reading the file's git log first. Not fixed here — flagging for whoever owns queue/dispatch hygiene next (this is the same general territory as `FINDING-2026-08-23-seat08-parked-row-served-as-rank0-free-no-unclaim-verb.md`, a different shape of the same underlying gap: the dispatch layer has no notion of "this row's object overlaps a different row's object").
