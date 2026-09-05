# ⛔⭐⭐⭐ GOAL-HQ-UNIFY — hq_U, THE FIFTH HQ: THE ONE MACHINE UNDER THREE SYNTAXES

**Opened 2026-09-05 12:1x CDT by Lon, in-chat to ceo, verbatim:** *"Would having 5 HQ's help? One per language?"* · *"Or multiple HQ's segregated along any axis would work?"* · *"What's a good name for a fifth HQ?"* (ceo: HQ-UNIFY, `hq_U` — the verb grammar of COMPLETE / PERFORM / BEAUTIFY / TEST) · *"The /home/claude_U folder is ready to populate."* Root `/home/claude_U`, populated by the ceo the same sitting (SCRIP `53138c1e5` · corpus `b5c8540e3` · .github `23db9738` at cloning; hooks installed; identity LCherryholmes in all three; digest copied from hq_T's with its own identity block; postoffice `hq_U/` with `HQ` = `ceo`). Record: GOAL-CEO CEO-291.

## THE MANDATE

The Byrd-box machine, the driver and the runtime are ONE engine under three syntaxes (SNOBOL4 patterns, Icon generators, Prolog backtracking — ARCH-ENGINE.md, ARCH-LANGUAGES.md). Until this HQ opened, that engine lived inside hq_C's lane beside the Prolog rebuild, and every cross-language regression was owned by whichever HQ noticed it. Two of them surfaced on 2026-09-05 alone: the HOST argv staging that burned Icon's list serial 1 (a SNOBOL4 landing, an Icon board red; cured by the ceo on Lon's order, CEO-291) and the CAP_NEST rsp-relative capture whose live depth is a run-time value (hq_C, cured as an addressing mode, CEO-289). **hq_U owns the shared engine end to end and every regression that crosses a frontend boundary.**

## THE LANE (MASTER-PLAN § THE LANES — moved here from hq_C's "every shared-engine class" at opening)

- `src/templates/bb/` (the 134 boxes), `src/templates/x86/x86_asm.h` (the one encoder), `src/templates/xa/` (emission helpers), `src/emitter/`, `src/optimizer/` — the machine.
- `src/driver/` — one path, all languages; program-argument staging, mode 3/4 startup, the stale-binary refusal.
- `src/runtime/core/`, `src/runtime/rt/`, `src/runtime/rtx/` (the hand-written asm runtime, ARCH-{SNOBOL4,ICON,PROLOG}-RTX.md), `src/ir/` (the three zetas: `zeta_{choices,depth,storage}.h`, `descr.h`).
- EVERY CROSS-LANGUAGE REGRESSION: a landing in one frontend that moves another frontend's board is hq_U's from the bisect on, whichever HQ bisected it. The finder files the FINDING and the row; hq_U cures.
- NOT hq_U's: parsers and lowerers (`src/parsers/`, `src/lower/`) stay with the language HQ; a defect reachable through one frontend only is that HQ's until measurement proves it shared.

## LAWS THAT BIND EVERY hq_U LANDING (compact; RULES.md is the parent)

- **SHARED-NODE VERDICT SCOPE (RULES.md):** a shared-node change is graded on every frontend that lowers to the node — `grep -c IR_<NODE> src/lower/lower_*.c` names the boards owed — with SNOBOL4 FAIL=0 over the printed denominator plus the Icon master watermark as control arms, before its verdict is quotable; a board names BOTH hashes (SCRIP and corpus) and is re-run after `pull --rebase`, before push.
- **NO PER-OP FILTER:** all members of a BB family are the same; a defect reachable through one member is a class defect — fix the class or leave it visibly red.
- **EMISSION DISCIPLINE:** every x86 instruction is produced only inside `x86(...)` in `x86_asm.h`; templates emit zero binary; BOTH-MEDIUM MANDATORY (`test_gate_template_medium_invisible.sh`).
- **THE THREE ZETAS and the BB FRAME-PLACEMENT CRITERION (Lon 2026-08-27):** RESULT/LOCALS stay on the RSP spine iff every consumer reaches them at a fixed compile-time offset on every path; the moment unbounded growth can intervene they move to an RBP activation frame; only genuine escapers go to the heap. ζ has no modes, selectors or switches.
- **NO NEW GLOBALS** without Lon's explicit in-chat grant that session (the ⛔ banner naming global, type, file, purpose, and why registers and the stack cannot carry it — CEO-291 is the precedent: `g_main_args_v`).
- **ASM-DIFF-FIRST** (RULES.md § ABSOLUTE RULES): mint the smallest repro, diff the emitted `.s` between a passing sibling and the witness within ONE mode, gdb only then.
- **ZERO COMMENTS, zero blank lines, 200-char lines** in C/C++/asm (`strip_comments.py --check` is the first arm of `make test`).

## SESSION SETUP (every session)

1. `git -C <repo> fetch origin && git -C <repo> merge --ff-only origin/main` in SCRIP, corpus, .github; `cd SCRIP && make` (incremental; `make pristine` only on a stale-binary refusal or a release point).
2. `bash scripts/s4e_msg.sh check` — read, act, `clear`. MODE is line 1 of `/home/resources/postoffice/MODE`; under QUARTET/QUINTET you measure AND cure; under FLEET-<n> your seats (none assigned at opening — the RE-CUT of MASTER-PLAN § THE 16-SEAT CUT gives hq_U a contiguous range when Lon re-lanes) walk and witness, you cure.
3. Read this file's LIVE CURSOR, then `SCORE.md` § THE SEPTEMBER 10 GRID for the boards your lane moves (every row's M and V cells are shared-engine sensitive).
4. Your first act every sitting: `ls .github/FINDING-$(date +%F)-*` for any FINDING naming a cross-language regression or a shared node; each one is a row in your lane by LANE-BY-CURE (RULES.md), provisional until you write its `LANE REVIEW` ledger line.

## LIVE CURSOR

**2026-09-05 13:28 CDT ceo — LON'S TWO ORDERS: THE A–Z TEMPLATE CLEANUP IS RANK 1 IN THIS LANE, AND UNUSED `bb_*.cpp` FILES ARE DELETED.** Lon, in-chat to ceo, verbatim: *"Is the A-Z template cleanup part of the tasks? If not they should be. We want all the bb_*.cpp files to follow the struct rules of construction so that all that code can easily be translated manually into Snocone unevaluated expressions."* · *"Also ensure old unused bb_*.cpp files are removed so we do not have garbage hanging around."* Row `bb-fixup-az-cleanup` (PARKED by hq_C 09-04 under CEO-230) is FREE, rank 1, owner hq_U; `bb-fixup-rank-85-dirty-templates` is SUPERSEDED into it. STEP 0 by the ceo on SCRIP `66a649a44`: `audit_bb_fixup_rank.sh` = 151 files / 65 dirty / GRAND 1446 (09-04 read 1413 — dirtied faster than cleaned). THE GOAL: every template body is ONE pure `x86(...)` concat with all variance inline (GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md R1–R13 + its gated FACT RULES; GOAL-BB-FIXUP.md; GOAL-SNOBOL4-100.md § BB-FIXUP SWEEP is the consolidated record) — the shape a Snocone unevaluated expression carries verbatim; the manual translation is the ACCEPTANCE FRAME, not a step. SECOND HALF: a reachability census of all 134 `bb_*.cpp` (all Makefile-listed by name, so 'not compiled' is never the signal) with `nm` over the objects against the emitter dispatch, each unreachable template deleted in its own named commit, and a gate holding the count at zero (first read by symbol: 7 stems unreferenced outside their file, glue/main certainly reached by other names — a lead, not a verdict). Seats 17–20 may take files one per claim under the seat04 precedent (per-file A/B byte-identical `.s` over demos + benchmarks, the demo set as control arm); hq_U lands the class-level cures.

**2026-09-05 12:1x CDT ceo — OPENED, NOT YET RUNNING.** Lon starts the session. FIRST ROWS (the ceo's LANE REVIEW at opening, provisional until hq_U's own ledger lines; all currently in hq_C's owner cell and to be re-owned by `assign hq_U <topic>` once hq_U runs):
- `icon-jcon-shared-bang-dispatch-error29-regresses-coerce-by-name-invocation` (rank 1, FREE, placeholder DONE-WHEN — write a runnable one first, RULES.md fail-once law).
- `snobol4-gimpel-hyphenat-and-line-error-246-is-a-third-mechanism-not-the-capture-class` (rank 1, hq_C claimed) — a third ERROR 246 mechanism in the pattern engine; take it over only with hq_C's LANE REVIEW line.
- seat08's unary-`!` 029 cure ruled PER-OP by hq_P (four sibling arms in one dispatch chain, two fabricating a value; .github `43b59c7a`) — the dispatch chain is engine, not frontend: a class row in this lane once seat08's row closes or releases.
- The reopened `setexit-not-invoked-under-errlimit-survival` (hq_P holds it; root cause .github `671fc125`: `rt_goto_transfer` cannot express failure and `core_runtime_error` reads its return as success) — the runtime half of that cure is engine; hq_P keeps the row, hq_U reviews the runtime change.
Under QUARTET (MODE since 11:52) there are no seats; hq_U measures and cures. Under a future FLEET-<n> the seat ranges are re-cut by a Lon-run script (contiguous ranges, MASTER-PLAN § THE 16-SEAT CUT), never by prose.
