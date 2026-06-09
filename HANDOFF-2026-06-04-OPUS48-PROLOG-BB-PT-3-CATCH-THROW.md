# HANDOFF 2026-06-04 (Opus 4.8) — Prolog-BB: PT-3 catch/throw on the rail (m4 96→101, EXCISED 19→14)

## TL;DR

Landing commit `f44c20c` (rebased from 1fe43fd over PB-9d/PB-RB-CONV; gates re-verified at merged HEAD). `catch/3` + `throw/1` now **emit and run natively in mode-4**. All 5 rung28_exceptions rungs
(catch_atom_match, no_throw, throw_catch_atom, throw_catch_compound, rethrow) PASS m4 with
m2==m3==m4 byte-identical output. m4 **96 → 101 / 0 / 14**; GATE-3 m2/m3 **115/115 HELD**;
zero FAILs. The remaining 14 EXCISED are all PT-4 (retract×5, abolish×5, aggregate/nb×4).
One commit, 10 files, no new files, Makefile untouched.

## Design — native sub-graph blocks, NOT the meta rail

The goal file's PT-3 sketch said "rt_call_term inside a CP/trail barrier." That route was
**rejected**: the rungs' recovery goals are conjunctions of `write`/`nl` builtins, which the
PT-1b meta resolver does not (and should not yet) carry. Instead, catch's goal and recovery
sub-graphs are emitted as **native callable blocks** — the same `codegen_callee_block`
mechanics that emit `.Lplpred_*` predicate blocks (verdict via `rt_set_last_ok` + `ret`) —
and a new runtime entry `rt_catch_native(goal_fn, rec_fn, catcher)` drives them around the
**existing m2 catch-frame substrate** (`resolve_catch_push`/`resolve_throw_term`'s
setjmp/longjmp stack in `resolution.c`). The substrate is SHARED, not duplicated: the
orchestration twins `rt_catch` (interp-drives `IR_interp_once`) and `rt_catch_native`
(native-calls the blocks) coexist exactly like `rt_findall`/`rt_findall_term`. The blocks
are reached by RIP-relative `lea` — **zero baked pointers**; the `zc_ptr` in-process trap
(HANDOFF-…-FINDALL-M4-INPROC-POINTER-TRAP.md) does not apply.

## Canonical grounding (RULES "CONSULT CANONICAL SOURCES" — both uploaded zips READ)

- **gprolog** `BipsPl/catch.pl` `'$catch_internal1'` — catch saves current **B** as the
  Handler (sys_var 7); `BipsPl/throw.pl` `'$unwind'` → `BipsPl/throw_c.c` `Pl_Throw_2` —
  the throw **cuts back to the handler choice point** (`Pl_Cut(b_word)`; untrailing rides
  the cut) and fails into catch's second clause, which unifies ball×catcher: match → run
  Recovery via `'$call_internal'`; no match → `'$unwind'` again (re-throw outward).
  Uncaught (b == LSSA) → system_error.
- **swipl** `src/pl-vmi.c` `I_CATCH`/`B_THROW`/`I_EXITCATCH` — CHP_CATCH choice point at
  catch entry; B_THROW pre-match walk outward, **cuts all choicepoints created since**;
  the exception term is **copied** (`duplicate_term`/`freezeGlobal`) "to make the
  exception term immune for undo operations."
- **Convergent law implemented:** mark CP at catch entry → throw pre-matches outward →
  unwind = trail-to-mark + **CP-truncate-to-mark** → real unify ball×catcher → recovery
  or re-throw → **ball copied at throw**.

Two canonical behaviors the m2 oracle LACKS were added in the **native path only**
(unobservable in all 5 rungs; m2 untouched → byte-identity preserved):
1. **CP truncate at landing** — `Resolve_CatchFrame` gains `cp_mark` (set in shared
   `resolve_catch_push`, read only by `rt_catch_native`); landing does
   `resolve_cp_truncate(cp_mark)`. Without it, stale CPs would reference longjmp-abandoned
   native frames — a real crash hazard the interp never had.
2. **Ball copy at throw** — `rt_throw_term` does `bb_copy_term(deref(ball))` before
   `resolve_throw_term` (swipl law). m2's `rt_throw` still doesn't copy — **latent oracle
   divergence**, observable only for balls containing variables bound after the catch's
   trail mark; no rung exposes it. Flagged for a future re-baseline audit.

## Touches (10 files, 1 commit)

1. `src/runtime/builtins/resolution.{h,c}` — `cp_mark` field + set in `resolve_catch_push`
   + `resolve_catch_top_cp_mark()` accessor. Additive; m2 landing path never reads it.
2. `src/interp/IR_interp.c` — `rt_throw_term(ball)` (copy + `resolve_throw_term`) and
   `rt_catch_native(goal_fn, rec_fn, catcher)` beside their interp twins: push frame →
   setjmp → `goal_fn()` → pop → `rt_last_ok()`; landing → trail-unwind + cp-truncate +
   env-restore → pop → take ball → unify (fail → re-throw) → `rec_fn()` → `rt_last_ok()`.
   longjmp out of arbitrarily deep native predicate frames is safe: the setjmp frame
   (rt_catch_native's C frame) is live for the whole goal drive, and longjmp restores
   rsp + callee-saved regs (incl. ζ=r12).
3. `src/emitter/emit_globals.h` — `bb_zn` sidecar appended after `bb_rn` (the
   compound-unify additive precedent; siblings held).
4. `src/emitter/emit_bb.c` — (a) `bb_prepare` IR_CATCH arm deposits the node into
   `g_emit.bb_zn`; (b) `codegen_callee_block` refactored into label-parameterized
   `codegen_graph_block` + thin name/arity wrapper (**byte-identical** for every existing
   block — m4 95-pass set unchanged); (c) catch side table (`g_pl_catch_nodes[64]`,
   `pl_catch_block_index`), recursive collector (`pl_catch_collect_graph`: IR_CATCH →
   register + recurse goal_g/rec_g; IR_CHOICE → recurse clause bodies), and
   `codegen_pl_catch_blocks(main_g, out)` emitting `.Lplcatch_<i>_goal` / `.Lplcatch_<i>_rec`
   blocks for every catch in main + every registry pred graph. Table fully populated
   BEFORE any block emission, so nested catches (rethrow's inner-inside-`inner`) resolve.
5. `src/emitter/emit_core.c` — IR_CATCH dispatch line gains `bb_prepare(nd)`.
6. `src/emitter/BB_templates/bb_catch.cpp` — real MEDIUM_TEXT arm: build catcher term
   (scalar marshal / `emit_build_compound_term` for IR_STRUCT — the bb_goal `build_arg`
   shape, duplicated per-template as RULES requires) → push + pad (net-even qwords) →
   `lea rdi/rsi, [rip + .Lplcatch_<i>_{goal,rec}]` → `call rt_catch_native@PLT` → test →
   γ/ω; β→ω single-shot (m2-parity). Non-admitted fallthrough keeps the x86() stub.
   Raw-byte producers in this file: **0** (TEXT-only arm, the findall/is-lint precedent).
7. `src/emitter/BB_templates/bb_builtin_retract_throw.cpp` — throw MEDIUM_TEXT arm:
   build ball (IR_STRUCT → `emit_build_compound_term`, else scalar marshal) →
   `mov rdi,rax; call rt_throw_term@PLT` (longjmps; trailing `jmp ω` unreachable, keeps shape).
8. `src/emitter/BB_templates/bb_builtin_common.h` — `rt_throw_term` extern (additive).
9. `src/driver/scrip.c` — RICH-gate-only admission (m4-native, m3-interpreted, the
   float-unify/findall precedent; flat gate untouched): `pl_rich_node_emittable` IR_CATCH
   arm (zc + goal_g + rec_g + catcher `pl_findall_term_buildable`); `throw/1` in the
   builtin arm (ball term-buildable); `pl_rich_graph_ok` recurses goal_g/rec_g beside the
   CHOICE-bodies recursion; m4 rich path calls `codegen_pl_catch_blocks` before
   `codegen_clause_dispatch`.

## Gate state (all re-verified at commit)

| Gate | Before | After |
|---|---|---|
| GATE-1 smoke | m2 5/5 · m3 4/5 (known artifact) · m4 5/5 | unchanged |
| GATE-3 rung suite | m2 115 · m3 115 · m4 96/0/19 | m2 **115** · m3 **115** · m4 **101/0/14** |
| FAILs (m4) | 0 | **0** |
| PL-HY-FENCE one-box | PASS | PASS |
| pl-no-value-stack | PASS | PASS |
| seg_byte/SL_B outside templates · g_vstack | 0 · 0 | 0 · 0 |
| bb_catch.cpp raw-byte producers | 0 | 0 (TEXT-only arm) |
| siblings | Icon m2 12 HARD · SNOBOL4 m2 7 HARD | **held** (Icon m3/m4 5/7 stash-proven pre-existing at clean HEAD) |

Remaining 14 EXCISED: retract×5 + abolish×5 (PT-4 dynamic DB) + aggregate/nb×4 (PT-4).
PT-3's catch frame + throw rail is the substrate PT-4's error paths will reuse.

## Still open / flagged

- **m2 oracle divergences (latent, unobservable in corpus):** no CP-truncate and no
  ball-copy in `rt_catch`/`rt_throw`. Aligning m2 to canon risks the 115/115 byte-identity
  → needs its own re-baseline rung with Lon's sign-off (same class as the WAM-CP-9
  ITE-commit oracle bug).
- Cut state across throw (`g_resolve_cut_flag/barrier`) is not saved/restored at the
  catch boundary — m2 parity kept; no rung exercises cut-then-throw. Joint with WAM-CP-9.
- catch/throw **inside meta-calls** still LOUDLY rejected by the PT-1b resolver
  (unchanged, by design until the local-barrier work).

## Build / verify

```bash
cd /home/claude/SCRIP && make -j4 scrip && make libscrip_rt
bash scripts/test_prolog_rung_suite.sh --mode all   # m2 115 · m3 115 · m4 101/0/14
for r in catch_atom_match no_throw throw_catch_atom throw_catch_compound rethrow; do
  bash scripts/run_prolog_via_x86_backend.sh corpus/programs/prolog/rung28_exceptions_$r.pl; done
```
The suite regenerates `corpus/programs/prolog/*.s`; `git checkout HEAD -- 'programs/prolog/*.s'` to re-clean.

Authors: LCherryholmes · Claude Opus 4.8
