# HANDOFF — 2026-06-13 · Claude · Prolog BB — PLAN VERIFIED + ladder reframed as a CORRECTION ladder

## Watermark
SCRIP `1b71e43` (Prolog code UNCHANGED — no code touched this session; tree advanced past the goal-file's `4e54908` watermark via a prior Icon-only commit) · .github `(this commit)`.
**m2 114/115 · m3 91/115 · m4 91/115.** Gates verified GATE-1 5/5/5 HARD; floors m3 91 / m4 91 hold. m3≡m4 by construction.

## Gates (re-verified this session)
GATE-1 `test_smoke_prolog.sh` 5/5/5 ✓. GATE-3 `test_prolog_rung_suite.sh` m2=114, m3=91, m4=91 ✓.

---

## Docs only. No code. Two deliverables.

### 1 · PLAN VERIFICATION (the four design-establishing prompts re-run against primary sources)
Lon asked to COMPLETELY verify the plan. Re-ran all four prior-session prompts against the ACTUAL
sources (Proebsting PDF read in full; JCON `tran/ir.icn`+`irgen.icn`+`jcon/vClosure.java`;
gprolog-master; swipl-devel-master) and checked every load-bearing `DESIGN-PROLOG-BB-ALL.md` claim
against the source line it cites. **The plan is sound and source-faithful.** Highlights, line-checked:
- **PDF:** four ports start/resume/fail/succeed = α/β/ω/γ; start+resume synthesized, fail+succeed
  inherited; `ifstmt` runtime gate (indirect goto on a temp); "nothing more powerful than conditional,
  direct, and indirect jumps" (§6, vs GG86's generator-frame STACK).
- **JCON `ir.icn`:** the complete IR vocabulary == DESIGN §9 (Goto/IndirectGoto/Move/MoveLabel/Call/
  ResumeValue/Succeed/Fail + Create/CoRet/CoFail).
- **JCON `irgen.icn`:** `ir_a_Call`(360) builds a closure + re-drives via `ir_ResumeValue` from the
  call's OWN resume (closure-as-value, not a port); `ir_a_If`(577) = Proebsting `ifstmt` gate exactly;
  `ir_conjunction`(405) threads left.success→right.start; `/bounded` gates EVERY resume chunk.
- **`vClosure.java`:** `retval` (suspended value) + abstract `Resume()`. The closure = (value, Resume).
- **ARBNO (`bench/test_sno_1.c`):** `_1_t _1[64]` + cursor ζ + index `ARBNO_i`; push=`&_1[++i]`,
  pop=`i--`. The value stack frozen into the box as a pure-functional indexed frame. The 4th prompt's
  claim is exactly right.
- **GDE × structure grid (gprolog vs swipl, by file + C symbols):** GNU has in-core CLP(FD) (`EngineFD/`)
  but ZERO tabling/attvar/engine/delimited-control; SWI has all four — `pl-tabling.c` (236 KB) → trie +
  `worklist_set` + `tbl_component`/SCC; `pl-attvar.c` → `registerWakeup`/`ALERT_WAKEUP`; `shift`/`reset`
  in `pl-wam.c`; engines via `PL_create_engine`. 100% coverage that eclipses both = SWI frontier on our
  trail+closure spine + GNU in-core CLP(FD). Nothing in the CORE needs a structure outside {trail, heap,
  frame cells, C call stack}; FRONTIER features add HEAP structures with frame-cell handles, never an
  engine stack. The 10-item "structures NOT used" list survives. (Full grids: scratch file
  /home/claude/verify/PLAN-VERIFICATION.md — not committed.)

### 2 · KEY CORRECTION — the starting state is NOT greenfield (Lon's question)
Lon asked: does the plan handle that we already have many Prolog BBs done WRONG? It did NOT — PL-BB-0..6
read like a fresh build. Measured the actual wrong state in-tree and reframed PL-BB as a CORRECTION /
MIGRATION ladder. New section `## ⛔ STARTING STATE IS NOT GREENFIELD` enumerates:
- **WRONG-1 (headline):** δ/ε are STILL live 5th/6th ports. 4 emitters emit `call δ`/`call ε`
  (`bb_cell_call`, `bb_cell_findall`, `bb_query_frame`, `bb_callee_frame`); `bb_cell_ite`+`x86_asm.h`
  carry `PORT_DELTA/PORT_EPSILON`. Spine to delete: `emit_bb.c` 13, `emit_globals.h` 4, `x86_asm.h` 9.
  → PL-BB-1.
- **WRONG-2:** determinacy not first-class. `grep bounded` over `bb_cell_*`+`lower_prolog.c` == 0; every
  cell box has an UNCONDITIONAL `def β`. A det call still retains a closure+CP it can't use. → PL-BB-0
  (must land BEFORE PL-BB-1).
- **WRONG-3:** `bb_cell_choice/cut/ite` ALREADY EXIST — the "CLAUSE CHOICE"/"CUT"/"ITE" rungs are REWORK
  of live files, not greenfield.
- **WRONG-4:** a parallel legacy set still LINKS (`bb_goal/bb_choice/bb_catch/bb_findall/bb_retract_throw`,
  8× `resolve_bb_env_*`) — unreachable (GZ-only dispatch) but editable by mistake. → PL-BB-DEMOLITION.

Added the **MIGRATION RULE** (one box one version; edit in place, never fork; a box's green rungs are a
HARD floor across its migration; subsume-then-DELETE legacy with linker-as-guide; GATE-1 5/5/5 HARD) and
a new **PL-BB-DEMOLITION** track. Every rung in the corrected ladder now tags which WRONG-n it fixes and
whether it MIGRATES a live box, REWORKS one, or creates a NEW one.

---

## NEXT SESSION (build-heavy, first actual code on this track)
**PL-BB-0** first (fixes WRONG-2): add a `bounded` bit per goal node in `lower_prolog.c`; bounded goals
stop synthesizing β; every `bb_cell_*`/`bb_det_*` consults it and omits the now-unconditional `def β`
tail. Pure refactor — smoke 5/5/5, floor 91, m3≡m4, no new rung. THEN **PL-BB-1** (fixes WRONG-1):
closure-resume call β + physically delete δ/ε. Build: `make -j4 scrip && make libscrip_rt`; smoke
`scripts/test_smoke_prolog.sh`; suite `scripts/test_prolog_rung_suite.sh`.

**Cleanest standalone win if a small green commit is wanted instead:** PL-BB-5's aggregate sum/max/min
(rung27 ×2) — same `IR_CELL_FINDALL` box, add `agg_mode` 2/3/4 + `rt_pl_agg_{sum,max,min}_finish` in
unification.c. Does NOT depend on PL-BB-0/1. (But the WRONG-1/2 corrections are the higher-leverage work.)

## Discipline followed
No code touched (SCRIP stays `4e54908`, all gates green). Docs-only change to `.github`. GOAL STATE block
updated; PL-BB ladder reframed; PLAN.md goals table NOT touched (routine handoff). The four FACT RULES and
the byte-identical-across-GOAL-files bodies were NOT edited.
