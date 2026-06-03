# HANDOFF — Prolog-BB: compound (list/struct) unify LANDED in mode-4 — m4 75→86

**Date:** 2026-06-03 · **Model:** Claude Opus 4.8 · **Track:** GOAL-PROLOG-BB.md
**Status:** Implementation session. The PL-HY-1a/1c compound-unify arm diagnosed last
session is now LANDED. SCRIP HEAD `374c2ff`. All gates green, GATE-3 m2/m3
byte-identical. m4 **75 → 86** (+11).

## What landed

The previous session (`HANDOFF-2026-06-03-OPUS48-PROLOG-BB-COMPOUND-UNIFY-DIAGNOSIS.md`)
diagnosed `bb_unify`'s deferred compound arm as shovel-ready and recommended option (b)
(a `g_emit` node-ptr sidecar, the `bb_arith` mechanism). This session implemented exactly
that — the 3-touch edit (plus the `emit_globals.h` field declaration = 4 files).

### The 4 touches (all as planned)

1. **`src/emitter/emit_globals.h`** — appended two fields to `sm_emit_t` after `bb_ri`:
   ```c
   void *  bb_ln;   /* left  operand IR node ptr (compound unify) */
   void *  bb_rn;   /* right operand IR node ptr (compound unify) */
   ```
   Appended at the end of the existing `bb_*` block → existing offsets undisturbed →
   Icon (12/12) and SNOBOL4 (7/7) sibling m2 gates held.

2. **`src/emitter/emit_bb.c`** `bb_prepare` IR_UNIFY arm — deposits the two operand node
   pointers into the sidecar (one added line):
   ```c
   g_emit.bb_ln = (void *)nd->α; g_emit.bb_rn = (void *)nd->β;
   ```

3. **`src/emitter/BB_templates/bb_unify.cpp`** — the substantive change:
   - `u_deferred()` (which bombed compound AND float) → `u_deferred_float()` (floats only).
   - The general arm's `u_build()` scalar-only builder split into `u_build_scalar()` (the
     old single `rt_node_to_term` call, for scalars) and, for compound operands, a call to
     `emit_build_compound_term(ln/rn)` — the **sanctioned mode-4 serialized encoder**
     (PL-HY-1a verdict: NOT a dup) that recurses IR_STRUCT/IR_ARITH children and bakes only
     literal immediates + `[rip+strlabel]` (zero runtime pointers, fully relocatable).
   - The var-var / var-const / self-unify scalar arms are **unchanged**.
   - Box stays `(void)` / `pBB`-free and **x86()-pure** (0 raw-byte producers;
     medium-invisible count = 0 for this file).

4. **`src/driver/scrip.c`** `pl_rich_node_emittable` IR_UNIFY arm — removed `IR_STRUCT`
   from the rejection list (kept `IR_ARITH` and `IR_LIT_F` rejected). This admits
   struct-operand unify graphs to the mode-4 emitter.

### Semantics grounded in canonical source

gprolog `src/EnginePl/unify.c` `TAG_STC_MASK` branch (lines ~124-145, in the uploaded
`4-gprolog-master.zip`): structure×structure unify = **functor+arity match, then
element-wise recursion over args.** That is exactly what `rt_unify_terms` does on two
built `Term*` trees, so building both operands and calling `rt_unify_terms` is the correct
and complete implementation. (The mode-2 interpreter already does this:
`IR_interp.c:4255-4256` calls `resolve_node_to_term(bb->α/β)` which recurses IR_STRUCT,
then `unify(...)`.)

## Result — m4 75 → 86 (+11, not the predicted +3)

The diagnosis predicted +3 (rung03/05/06). The actual gain was **+11** because compound
(list-cell `'.'/2`) head unification is the substrate for ALL list-manipulation rungs, not
just the three named probes. Verified end-to-end through the real x86 pipeline
(`run_prolog_via_x86_backend.sh` — scrip→as→gcc→run):

- rung03 `f(X,a)=f(b,Y)` → `b a` ✅
- rung05 `member(X,[a,b,c])` → `a b c` ✅ (backtracking + list-cell head unify)
- rung06 `append`/`length`/`reverse` → `[a,b,c,d]` / `4` / `[d,c,b,a]` ✅
- …plus 8 more list-unify rungs through rung40.

### Remaining 25 EXCISED (none compound-unify-blocked)

findall (5), retract (5), abolish (5), aggregate/nb_setval (4), catch/throw (5),
dcg_generate (1). All need a real runtime substrate (PLG-9g dynamic-DB + exception
families). **Float-unify** (`X = 3.14`, `IR_LIT_F`) also remains deferred (CAT-D float
substrate) — confirmed still correctly excising in m4 while m2 handles it.

## Gates (all green, pre-commit verified)

| Gate | Mode-2 | Mode-3 | Mode-4 |
|---|---|---|---|
| GATE-1 smoke | 5/5 ✅ | 4/5 (unify harness artifact) | 5/5 |
| GATE-3 rung suite | **111/111** ✅ | **111/111** ✅ | **86 / 0 / 25** |
| siblings (HARD m2) | Prolog 111 · Icon 12 · SNOBOL4 7 | — | — |

- `test_gate_bb_one_box.sh` (PL-HY-FENCE) PASS
- `test_gate_no_bb_bin_t.sh` 0 · `test_gate_pl_no_value_stack.sh` PASS · `prove_lower2.sh` PASS
- `test_gate_no_handencoded_bytes.sh` 0 · `test_gate_template_medium_invisible.sh` 343
  (unchanged — `bb_unify.cpp` contributes 0)
- FACT greps: `g_vstack` 0 · `seg_byte(SEG_CODE`/`SL_B(` outside templates 0
- `util_template_purity_audit.sh`: 2 pre-existing non-Prolog side-effects
  (`bb_call_write_slot.cpp`, `bb_every.cpp`) — unchanged baseline, not touched.

GATE-3 m2/m3 byte-identity is structurally guaranteed: compound-unify in m2/m3 runs the
interpreter (`bb_exec_once` → `resolve_node_to_term` + `unify`), which this change does not
touch; only the m4 emitter path changed.

## Note on a transient observed (resolved)

The very first full-suite run this session reported m4 75/0/36 (unchanged), then 86/0/25
after a rebuild. The only code delta between those builds was a temporary stderr trace
(since removed). Root cause was a `make -j4 scrip` parallel-build race: the suite ran
against a `scrip` binary linked before the `scrip.c` driver object finished recompiling.
A forced `touch src/driver/scrip.c && make scrip` reproduced 86/0/25 deterministically.
**Lesson for next session:** after editing `scrip.c`, confirm the driver object is fresh
(or run `make scrip` to completion) before trusting the first suite run.

## Setup note

`refs/` was dropped from the fresh-start repo; the gprolog grounding came from the uploaded
`4-gprolog-master.zip` (extracted to `/home/claude/gprolog-src/gprolog-master`). Per RULES
"CONSULT CANONICAL SOURCES," restore `refs/gprolog` / `refs/swipl` when canonical grounding
is needed (`git clone https://github.com/didoudiaz/gprolog`).

## Repos state

| Repo | HEAD |
|---|---|
| SCRIP | `374c2ff` |
| .github | this doc + GOAL-PROLOG-BB.md watermark/Gate-table/PL-HY-1c update |
| corpus | unchanged |

## Suggested next steps

- **PLG-9g / WAM-CP-13** — the 25 remaining EXCISED families all want the m4 dynamic-DB +
  exception runtime substrate. findall sub-graph + assert/retract store + catch/throw on an
  explicit indexed deferred-frame array (`test_sno_1.c` `_1[64]`), NOT snapshot/C-recursion.
- **CAT-D float substrate** — would clear the float-unify deferral (`rt_pl_arith_d` →
  `double`, `rt_pl_is_d` → `TERM_FLOAT`). No corpus float-unify rung yet; defer until one
  surfaces.
- **WAM-CP-9-rest** — the ITE-commit m2-oracle bug (swipl-proven) scoped last session; still
  needs Lon's design sign-off (touches shared `lower.c` + risks 111/111 byte-identity).
