# HANDOFF — BB-FIXUP-A-to-Z 76th attended run (Opus 4.8)

**Date:** 2026-06-13/14 · **Goal:** GOAL-BB-FIXUP-A-to-Z.md · **Cursor:** bb_call.cpp (UNCHANGED)
**SCRIP net code from this run:** ZERO (a heal was landed then REVERTED as redundant — see below). SCRIP origin advanced to 9ce94ca (my revert) atop the canonical fix e089608 + concurrents.
**Lon attending:** "What % … Continue." ×N (delegated close → hand off)

## TL;DR — honest accounting
The DEFINE double-free I was assigned (by 9baaf64) was **already fixed in parallel by another session's commit e089608** (cleaner, and it ALSO fixed a second, REAL m4 bug). My independently-developed heal was **redundant → reverted**. Net SCRIP change from this run: zero. **Value delivered: independent root-cause diagnosis, confirmation of e089608's fix on a clean build, and a genuine build-hygiene lesson.** DEFINE is GREEN (m2=m3=m4=7/7/7) via e089608. Cursor resumes at bb_call.cpp.

## What actually happened (corrected — two prior versions of this handoff were wrong)

Session opened at HEAD 9baaf64 with SNOBOL4 `define` RED (m3 abort + m4 `<mode4-build-failed>`), per the ir_delete_all tripwire 9baaf64 wired. I diagnosed the double-free correctly: `lower_snobol4.c:1009` `*fg = *g` makes each DEFINE'd proc a VIEW graph aliasing the main graph's node array (`fg->all == g->all`), so once `ir_delete_all`→`bb_program_free`→`IR_free` frees the pool, the shared array is freed twice. I wrote a fix (an `aliased` flag on `IR_graph_t` + an `IR_free` guard + `fg->aliased=1` in lowering) and landed it (a58bd75 → rebased 95bc33f).

**Then on the combined head I found commit e089608** (another session, landed 00:40 — BEFORE my push), which had already fixed BOTH bugs:
1. **The double-free**, more cleanly: a two-pass owner/view classification in `bb_program_free` using the existing per-node `->own` back-pointer (a view's nodes have `->own !=` the view graph) — owners do full `IR_free`, views free their struct only. **No `IR.h` change, no lowering change.** My `aliased`-flag approach was strictly redundant with this (and added an `IR_graph_t` field, against the PEERS RULE).
2. **A REAL m4 bug** (empty output, no crash): `sno_proc_startup` hand-wrote a 4-arg ABI for `rt_proc_register` (the function takes 3: name, pnames, nparams). The spurious `xor rsi,rsi` pushed `pnames` into `rdx` (read as nparams) and made `rsi=0` the pnames → proc registered with `pnames=NULL` → `rt_call_named_proc` bound no params → X unset in DOUBLE's body → empty. e089608 dropped the spurious arg.

**So I REVERTED my redundant heal (9ce94ca).** Clean-build verification with my heal gone and e089608 only: **define m2=m3=m4=42, SNOBOL4 7/7/7 (HARD green), Icon 12/12/12, Prolog 5/5/5.**

## ⛔ Correction to the "W2 phantom" claim (earlier versions of this handoff)
Earlier I reported a "W2 m4 proc-binop drop" and then called it a pure stale-build phantom. BOTH framings were inaccurate. The m4 empty output had TWO contributors: (a) **e089608's REAL rt_proc_register ABI bug** (params unbound), and (b) a **stale-build artifact** — after editing `IR.h`, an INCREMENTAL `make` left `emit_bb.o` stale and the define m4 `.s` was missing the binop block (199 vs 210 lines). I conflated these. (a) was real and is e089608's fix; (b) was build staleness. A `make clean` rebuild + e089608 gives the correct 42.

## ⛔⛔ BUILD-HYGIENE LESSON (the one durable takeaway — a real Makefile gap)
After ANY header edit (`IR.h`, `descr.h`, `ast.h`, `SM.h`, `stage2.h`, …), **`make clean && make`**. The Makefile's header-dependency tracking is INCOMPLETE; incremental builds across a header change leave stale objects and WILL manufacture phantom bugs (this run lost real time to one). A proper fix to the dep rules is logged as an outstanding candidate task.

## State / outstanding
- SCRIP @ **9ce94ca** (canonical DEFINE fix = e089608; my heal landed+reverted, net zero). Cursor **STAYS bb_call.cpp**. SNOBOL4 7/7/7, Icon 12/12/12, Prolog 5/5/5; GRAND 1101 (unaffected — no bb_*.cpp ever touched).
- Outstanding verdicts (carried): m2 disj-backtrack (PROLOG-BB) · prove_lower VACUOUS ratify (IR-REDESIGN) · pK m4 silent-empty (PROLOG-BB/RAKU-BB) · brokered-catch m3/m4 silent (PROLOG-BB) · str-relop m3-empty (ICON-BB) · gvar-relop box ungated (ICON/lowering) · rank rp-patch ratify · rank cv9/cv10 desync · ceiling-ratify **1101** (was 1215) · LANGUAGE-BLIND audit category · **NEW: Makefile header-dep tracking gap (clean-build workaround; real dep-rule fix is a candidate task)**.
- FIX-3 still open (bb_call dval==2/3 mass; Lon pins A+B from the 75th run unchanged).
- **Process note for parallel sessions:** the DEFINE double-free was fixed twice in parallel (e089608 and my reverted heal) because both were in flight before either pushed. When a concurrent commit on the same symptom is detected at push/rebase time, diff it FIRST and defer to/dedup against it before landing a parallel fix.

## NEXT SESSION
ENV setup (libgc-dev + libscrip_rt) → **`make clean && make`** if any header was touched → baseline GREEN (SNOBOL4 7/7/7 now) → resume cursor at bb_call.cpp: FIX-3-iii scan breakout per the 75th-run recipe + dval blocker, OR a fresh Lon pin. DEFINE is complete (e089608). Cursor STAYS bb_call.cpp.
