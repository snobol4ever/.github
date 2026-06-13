# HANDOFF — 2026-06-13 — Opus 4.8 — BB-FIXUP A→Z 74th attended run — FIX-3-ii DEFINE CARVE

## ONE-LINE
Carved SNOBOL4 `DEFINE` out of the `bb_call.cpp` dval-dispatch monster into its own IR kind
`IR_CALL_DEFINE` + a new clean both-medium template `bb_call_define.cpp`; dirty
`bb_call_gvar_define_str` helper deleted. Behavior-neutral, certified. **SCRIP @ 80c8745.**
Cursor STAYS `bb_call.cpp` (partial ring stop — FIX-3-iii still PINNED).

## WHAT LANDED — SCRIP 80c8745 (one TIER-S commit, one IR-split)
10-file change:
- `src/contracts/IR.h` — `IR_CALL_DEFINE` added at END of enum (before `IR_OP_COUNT`; no existing value shifts).
- `src/contracts/scrip_ir.c` — name-table entry `[IR_CALL_DEFINE]="IR_CALL_DEFINE"` (designated-initializer, order-free); argblk-dump guard `bb->op != IR_CALL && != IR_CALL_DEFINE`.
- `src/lower/lower_snobol4.c` — `sno_call_channels` (the SINGLE chokepoint for all 3 DEFINE build sites: stmt / `X=DEFINE(...)` / scan-subject): sets `call->op = IR_CALL_DEFINE` for DEFINE, **keeps dval=5.0** (set by `lc_call_argblks`).
- `src/interp/IR_interp.c` — mode-2 `case IR_CALL_DEFINE:` fall-through into BOTH single-shot test (282) and exec (2329). dval=5 preserved → the `dval==2||dval==5` bodies fire identically (DEFINE in mode-2 ≡ general value-call via `try_call_builtin_by_name`).
- `src/emitter/emit_core.c` — gvar_assign trigger (450) `|| op_a->op==IR_CALL_DEFINE`; dispatch `case IR_CALL_DEFINE: bb_emit_x86(bb_call_define()); return 0;`.
- `src/emitter/emit_bb.c` — `bb_fill_alpha` IR_CALL_DEFINE block (CV10: driver-side IR-walk of `IR_EXEC(nd).counter`→spec→strtab-intern into `op_parts_lbl[0]`, set `op_sval`); `binop_operand_streams` (1457) case fall-through; flat dispatch `case IR_CALL_DEFINE:` → `case IR_CALL` (2638, hits dval==5 FILL at 2747, intermediate dval==2/3 skip); gvar_assign trigger (2918) `|| IR_CALL_DEFINE`; **two chain-walkers (3074, 3310) `|| c->op==IR_CALL_DEFINE`** (MANDATORY — queue DEFINE's ω-successor or the chain after it drops); size (3286) `case IR_CALL_DEFINE: return 0`.
- `src/emitter/BB_templates/bb_call.cpp` — 4 marshal sites (110/139/168/349) kind-keyed to `(IR_CALL && (dval==2||3)) || IR_CALL_DEFINE`; DELETED `bb_call_gvar_define_str` helper + its dispatch arm (596) + the now-unused `rt_proc_define` extern.
- `src/emitter/BB_templates/bb_call_define.cpp` — **NEW**, CV9 parameterless both-medium, modeled on certified-clean `bb_binop_gvar_arith.cpp`: `x86("label",α) + comment "IR_CALL_DEFINE" + x86("lea","rdi","[rip + __]",specptr,op_parts_lbl[0]) + x86("call","rt_proc_define",fptr) + jmp γ / def β / jmp ω`. ZERO violations.
- `src/emitter/BB_templates/bb_templates.h` — registered `std::string bb_call_define();`.
- `Makefile` — compile rule + source-list entry for `bb_call_define.cpp` (link globs `$(OBJ)/*.o`).

## THE DESIGN INSIGHT (why this is neutral)
`dval==5` (DEFINE) lives at **11 sites / 5 files**: bb_call.cpp 4 marshal + 1 dispatch; emit_bb.c 2747 (FILL) + 3286 (size); scrip.c 234; IR_interp.c 2331+2345 (mode-2); scrip_ir.c 459.
**dval==5 is GROUPED with dval==2 at every execution site and appears ALONE only at the emitter dispatch (bb_call.cpp:596).** So: introduce IR_CALL_DEFINE, **keep dval=5 on the node** → every value-call site stays logically identical by construction; only the emitter dispatch reroutes to the clean template. The op-switches that distinguish IR_CALL get a `case IR_CALL_DEFINE` fall-through (or `|| op==IR_CALL_DEFINE`) so the node still reaches the dval-testing bodies. The marshal sites key on `sval` via `marshal_single_call` (NOT op/dval), so a DEFINE-arg is transparent.
**scrip.c's 12 IR_CALL sites were verified ALL `icn_`-prefixed (Icon-admission) → DEFINE is SNOBOL4-only (`g_gvar_flat_chain`), never reaches them → left untouched (neutral by unreachability, not churned).** Likewise emit_bb.c 1794/1812/2560/2678/2756 are Icon-gated or after the dval==5 FILL+break.

## PROOF (certified)
- **C2** on live `define` probe (`DOUBLE('DOUBLE(X)')` → 42): normalized A/B asm-diff = **sanctioned deltas ONLY** — (1) R1 comment terse `BOX IR_CALL DEFINE(spec)...`→`IR_CALL_DEFINE`; (2) inline `.section .rodata / .string "DOUBLE(X)" / .section .text` block relocated to strtab (`.S2`, identical content); (3) label-renumber (`xgvarg12→11`, `.Lprocfn15→14`) from the old template's dropped `g_flat_node_id++`. `lea`/`call`/`jmp`/port lines byte-identical.
- **Behavior m2=m3=m4=42** on the define probe (all three modes, end-to-end).
- **Full battery at floors pre+post** (and re-certified on each rebased combined head): sno m4 7/7 HARD (define passes), pat M2 19 M4 19/0, icon m2 12/12 HARD m3=m4 10/2, prolog 5/5 ×3, prove_lower VACUOUS rc=0, purity 1, bin_t 0, vstack 3, med_inv 75, handencoded 0, sno_pat_reg HARD, emit_blind 0, prolog crosscheck 93→**97** PASS (concurrent-improved, no regress).

## CEILING (inherited by next session)
**131 files / 76 dirty / 55 clean / GRAND 1143.**
- Mine: sole DEFINE mover, bb_call.cpp 337→316 (−21 rank), `bb_call_define.cpp` born CLEAN (0).
- 7 concurrents absorbed (open + 2 push-races, all rebased clean): a430139 PL-GZ-A6 nb_setval/getval (+2 new dirty templates), f6bbabb RAKU user-sub dval=3, 33f7202 RAKU rk_discover dedup, fa4cb1d bb_var_frame 4→0 CLEAN, b3de0be ICON lower_every, 41d2c08 SNOBOL4 unary-minus, fbf4b91 Pascal M3 relop. Net concurrent +6 GRAND / +3 files / dirty+clean shuffle. From session-open 1158, all git-attributable.

## STILL OPEN — PINS FOR LON (unchanged)
- **(A) FIX-3-iii dval==2/3 channel (PINNED):** how `IR_CALL_GEN_SCAN` peels off `IR_CALL_PROC_STAGED`/`NAMED_PROC` so the native fast-path keys on a KIND not `dval==3 + sval`. Co-owned IRD/ICN. **bb_call.cpp CANNOT reach rc=0 without this** — the dval==2/3 mass (marshal_*/byname/userproc/staged: lv/rp/bp/ef/mt bulk) is untouched.
- **(B) LANGUAGE-BLIND audit category (DEFERRED, carried 71st–73rd):** adding it flips ~7 behind-cursor files dirty (incl. bb_call) → cursor-reset cascade. Awaiting Lon's call: extend strip / add category+accept reset / defer to FIX-FENCE.

## NEXT SESSION
Cursor STAYS **bb_call.cpp**. FIX-3-i (write de-walk, 73rd) + FIX-3-ii (DEFINE carve, this run) are both CONSUMED. The ONLY remaining bb_call advance is **FIX-3-iii → take Lon's pin (A)** to start the dval==2/3 mass. If pin not given, bb_call.cpp is BLOCKED and the sweep should be redirected by Lon (the A→Z ring has many other dirty files, but SOP says no skipping — so this needs Lon's word).
Open protocol: clone SCRIP + corpus + x64; git identity; baseline battery GREEN before first edit; print rank table at open AND close.

SCRIP @ 80c8745 verified on origin · .github @ this commit.
