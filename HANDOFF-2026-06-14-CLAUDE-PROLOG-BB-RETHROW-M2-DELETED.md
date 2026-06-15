# HANDOFF 2026-06-14 — Claude — PROLOG-BB: rung28 rethrow LANDED + mode-2 (`--interp`) DELETION discovered

**Author:** Claude (Opus 4.8) · **Track:** GOAL-PROLOG-BB (PL-GZ) · **SCRIP:** `2c38d15`→`70b7bd9` · **.github:** docs

## TL;DR
- Landed **rung28 `rethrow`** — `catch/3` inside a CALLED predicate body. **GATE-3 m3 104→105, m4 104→105, byte-identical parity intact.** Commit `70b7bd9`, one file (`src/driver/scrip.c`).
- Discovered the working tree had advanced past this goal file's `81b63f1` watermark to HEAD `2c38d15`, and that **mode-2 (`--interp`) was physically DELETED in between** (`a2440f4`). The "m2 114/115 HARD gate" premise is now VOID; the gate scripts still drive `--interp` and report silent false FAILs.
- Remaining 10 m3≡m4 fails (**retract ×5 + abolish ×5**) are UNCHANGED — still parked on Lon's two dynamic-rail forks. Nothing decided, no global added.
- Wired the two design docs into the GOAL's MANDATORY-READ as **required reading** (Lon's request): `ARCH-PROLOG.md` (BB design) + `DESIGN-PROLOG-BB-ALL.md` (GDE inventory + merged build order + §10 globals/structures-NOT-used).

## What landed — rung28 rethrow (`70b7bd9`)
Test: `corpus/programs/prolog/rung28_exceptions_rethrow.pl`
```prolog
main  :- catch(inner, E, (write(outer), write(' '), write(E), nl)).
inner :- catch(throw(mine), other, write(wrong)).
```
Expected `outer mine`: `inner`'s catcher `other` does NOT unify with ball `mine`, so the ball propagates to `main`'s catcher `E` (a var, matches). Before: `[PL-GZ FENCE]` — a predicate whose body contains `catch/3` was not admitted on the GZ callee path. The 4 passing rung28 cases all catch at MAIN level (handled by `pl_gz_build_goal`'s IR_CATCH arm); only `rethrow` puts the catch inside a *called* predicate.

**Pure build-side fix in `src/driver/scrip.c`. Emit + runtime UNTOUCHED.** Verified the runtime already supports propagation: `rt_pl_throw_match` (unification.c:768) clears `g_pl_throw_ball` ONLY on a successful unify (line 774); on mismatch the ball stays pending (comment line 766). `gz_emit_cell`→`gz_emit_catch` (emit_bb.c:615) already routes `IR_CELL_CATCH` inside callee bodies, and `gz_collect_callees` (emit_bb.c:530) already recurses into catch sub-chains.

**The REAL gate** was NOT the missing admission arm — it was the FIRST-PASS structural filter in `pl_gz_rule_clause` (scrip.c), which rejected `IR_CATCH` alongside `IR_CHOICE`/`IR_DISJ`/`IR_ITE` *before* the semantic check at the bottom of the function ran. Four sites:
1. **`pl_gz_rule_clause`** — removed `IR_CATCH` from the structural rejection (kept CHOICE/DISJ/ITE rejected). Safe: catch `goal_g`/`rec_g` are SEPARATE `IR_alloc` graphs (lower_prolog.c:190,203); only the IR_CATCH node + its catcher (built in the parent context, line 200) live in the parent `all[]`, so the single-GCONJ uniqueness check still holds, and the catch is then validated semantically.
2. **`pl_gz_rule_body_goal_ok`** — IR_CATCH admission arm: validates the catch state, recurses both sub-chains, and checks the catcher shape (ATOM/LIT_I/LIT_F/LOGICVAR/STRUCT).
3. **`pl_gz_callee_body_node`** (NEW) — extracted the entire per-goal builder out of `pl_gz_rule_callee_body` (verbatim, via a head/tail/synth_next pointer-aliasing wrapper) so a catch's γ-linked sub-chains reuse the identical slot-mapping builder. Added an IR_CATCH case: builds the goal/recovery sub-chains by walking each sub-graph's γ-chain and recursing, slot-maps the catcher via `pl_gz_struct_slot_map`, draws the mark slot from `synth_next++`, emits the `IR_CELL_CATCH` node.
4. **`pl_gz_nsynth_chain`** (NEW) + IR_CATCH case in **`pl_gz_clause_nsynth`** — reserve the catch mark slot (+1) plus any sub-chain synth temporaries in the callee frame, so the frame is sized correctly.

No new global (NO-NEW-GLOBAL ratchet 15/15 unchanged), no new box, no new IR kind, no value stack. The catch mark lives in a frame cell `[ζ+off]`; propagation rides the pre-existing single-slot `g_pl_throw_ball` register (a one-Term* pending-exception slot, used already by the 4 passing catch cases — not a value stack).

## The big finding — mode-2 (`--interp`) is DELETED at HEAD
`git log -S '"--interp"'` shows **`a2440f4` "DELETE the IR-graph interpreter — only BBs run, no interpreter accessible"** removed the `--interp` CLI arm. It is an ancestor of HEAD `2c38d15` and NEWER than this goal file's `81b63f1` watermark. `94c94f4` then trimmed the CLI to `--run/--compile/--target/--dump-ast/--dump-ir/--transpile/--bench`. `./scrip --interp X` now errors `cannot open '--interp'`.

This is the recurring STALE-MAP pattern, now compounded: the goal file claimed HEAD `81b63f1` with "GATE-3 m2 114", but the real tip is `2c38d15` with m2 gone. Consequences (each UNHANDLED — flagged for Lon, not acted on without his word):
- **Gate scripts still drive `--interp`** (`test_smoke_prolog.sh`; `test_prolog_rung_suite.sh:51`). m2 now reports 0/5 + 0/115 = SILENT FALSE FAIL (not a regression). The smoke gate's "exit 0 iff mode-2 all-PASS" condition means it now ALWAYS exits non-zero.
- The **"m2 HARD gate"** language throughout this goal file + handoffs is void.
- The **catch-residue demolition gate** ("don't delete `g_resolve_catch_*`/`rt_catch_native` — m2 rung28 routes through them") and the **NO-NEW-GLOBAL doomed-floor 15** rationale ("each doomed `g_*` still reached by m2") are now STALE — several doomed globals may be genuinely dead and droppable.
- The goal file's MANDATORY-READ + Architecture-reference sections still describe m2 `--interp` as the reference oracle.

**LIVE TRUTH: only m3 `--run` (BINARY→RX slab) and m4 `--compile --target=x86` (TEXT→as+gcc) exist; m3 105 ≡ m4 105.**

**DECISION FOR LON:** (a) re-baseline the gate scripts — drop or replace the m2 path, reset the smoke pass-condition to m3/m4; (b) re-audit the catch-residue (`g_resolve_catch_*`) and the doomed-floor now that m2 cannot reach them. Neither done here (gate-harness re-baselining + a demolition pass were not authorized).

## Remaining 10 — retract ×5 + abolish ×5 (Lon's forks, UNCHANGED)
These need a runtime DYNAMIC-CLAUSE STORE that does not exist on the GZ path. Lon's ⭐ KEY FINDING (verified, in the PRIOR STATE block of the goal file): `assert*` IS the Prolog `CODE()`/`EVAL()` — a clause is a Byrd box, like a SNOBOL4 pattern is code — so `assert*`/`retract`/`CODE`/pattern-construction belong on ONE DYNAMIC-BB-BUILDING rail. The runtime BB-compiler `pl_gz_build` (emit_bb.c) already exists and is already used by the m3 driver (compile→free IR→jump in); `bb_pool.c`/`pat_pool.c` are general runtime code arenas. Building this rail ALSO unblocks the SNOBOL4 B-ladder.

**OPEN FORKS PUT TO LON (still unanswered):** (1) minimal Prolog-only dynamic rail vs the shared EVAL/CODE/pattern rail from the start; (2) the new SANCTIONED global's name/home (proposed `g_pl_dyn_pred_*`, must be added to `test_gate_pl_no_new_global.sh`'s allowlist). NOTHING decided — no global added, no FACT RULE written, no allowlist edit.

## Gates run (before commit)
- **GATE-3** `test_prolog_rung_suite.sh --mode run` → **105/115**; `--mode compile` → **105/115**. The 10 fails are exactly retract ×5 + abolish ×5. (The `--mode all` / m2 path reports false FAIL — see the m2-deletion finding.)
- **NO-NEW-GLOBAL** `test_gate_pl_no_new_global.sh` → PASS (no new globals; doomed-ratchet 15/floor 15).
- **no-value-stack** `test_gate_pl_no_value_stack.sh` → PASS.
- **bb_one_box** `test_gate_bb_one_box.sh` → rc=0 (the `bb_binop_*` FAIL lines are pre-existing SNOBOL4 template noise; byte-identical with the change stashed).
- Spot-checked the 4 main-level catch cases + rung01–09 (callee-body-heavy) → all PASS, confirming the `pl_gz_callee_body_node` extraction was behavior-preserving.

## GOAL doc changes (this handoff)
- Added **📖 REQUIRED DESIGN READING** to the MANDATORY-READ section: directs every session to read `ARCH-PROLOG.md` + `DESIGN-PROLOG-BB-ALL.md` before touching Prolog BB code (with a one-line map of what each provides, incl. §10 globals-NOT-used).
- New top STATE block (m3≡m4 @ 105; rethrow landed; m2-deletion finding); prior block demoted to PRIOR STATE; rung28 bullet marked ✅ LANDED. Watermark → `70b7bd9`.

## NEXT (recommended)
1. **Lon's call on the m2-deletion fallout:** re-baseline the gate scripts off `--interp` and re-audit catch-residue + doomed-floor (likely several `g_*` now droppable → ratchet 15↓). This is the highest-leverage cleanup and removes a permanently-red smoke gate.
2. **The dynamic-BB-building rail** (foundational — unblocks retract ×5 + abolish_then_reassert + the SNOBOL4 B-ladder), pending Lon's fork answers.
3. The 4 non-reassert abolish cases — do them ON the new table, not a throwaway gate.
