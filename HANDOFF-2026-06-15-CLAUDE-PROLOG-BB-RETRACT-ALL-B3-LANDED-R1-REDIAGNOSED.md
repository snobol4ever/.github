# HANDOFF 2026-06-15 — CLAUDE — PROLOG-BB — retract_all (B3) LANDED + R1 RE-DIAGNOSED

Goal: GOAL-PROLOG-BB. m3/m4 **113 → 114 byte-identical**. SCRIP `f7f37db` (pushed, on `origin/main`).

## RESULT
- GATE-3 m3 **114** / m4 **114** (parity by construction; re-verified post-rebase + clean rebuild).
- GATE-1 m3/m4 5/5. No-new-global ratchet **15/15** (no new global, no new box, no new IR kind).
- Cross-lang unaffected (change is `pl_gz_*` Prolog-only; Icon m3 spot-verified).
- Closed: **`rung14_retract_retract_all`**. Remaining red: **1** — `rung14_retract_retract_mixed`
  (R1, integer-arg retract; FENCED both modes → no regression). All 5 abolish + the other 4 retract green.
- Commit identity: LCherryholmes / lcherryh@yahoo.com.

## WHAT B3 ACTUALLY TOOK — the handoff's 3 retract sites were necessary but NOT the wall

The prior B3 plan (admit/whitelist/codegen `retract/1` in a callee body) was correct and is all landed,
BUT the program was still fenced after it. Tracing localized the real blocker to a **pre-existing guard in
the SHARED multi-clause callee-frame path**, not retract:

`pl_gz_rule_callee_body` (scrip.c) ended with `if (!head && ce->nclauses > 1) return 0;`.
`retract_loop` is a 2-clause predicate whose **second clause is the empty-body base fact `retract_loop.`**
(arity 0, no head-unify, no body goals → `head == NULL`). With `nclauses > 1` the build rejected it.

This gate had never fired before because the only shapes that reach the multi-clause **callee-frame** path
with an empty clause are rare: a predicate mixing a RULE clause with an empty FACT clause, that is CALLED
(not inlined) and is NOT all-facts (so `pl_gz_choice_inline` declines it). All-fact predicates
(`color(red). color(blue).`) take the inline-fact path and never reach `pl_gz_rule_callee_body`.

FIX: synthesize ONE `IR_SUCCEED` sentinel for the empty clause so it has a real entry node —
`if (!head && ce->nclauses > 1) { IR_t *sc = pl_gz_det_node(IR_SUCCEED); ...; head = tail = sc; }`.
`bb_succeed` emits exactly `α: jmp γ` / `def β: jmp ω` (deterministic succeed-once), which is correct for
an empty fact clause and satisfies the emit driver's label machinery (`gz_emit_callee` walks
`gz_clause_head_of`; a zero-node clause breaks its `pgl[cbase[c+1]]` clause-advance indexing).

### The 5 changes (all in src/driver/scrip.c, 26 insertions / 1 deletion, `f7f37db`)
1. `pl_gz_rule_body_goal_ok` — `IR_BUILTIN "retract"/1` admission arm (head LOGICVAR or STRUCT/ATOM;
   **integer-literal-arg fence preserved**: STRUCT head with any `IR_LIT_I` operand → return 0, keeps m3≡m4).
2. `pl_gz_rule_clause` — whitelist `retract`/1 in the structural first-pass filter (beside `throw`).
3. `pl_gz_callee_body_node` — emit `IR_DET_RETRACT` with slot-mapping (mirror of the main-level retract arm:
   LOGICVAR head → slot-map; STRUCT/ATOM head → synth `CELL_UNIFY` into a synth slot).
4. `pl_gz_nsynth_chain` + `pl_gz_clause_nsynth` — count the non-logicvar retract synth slot (frame width).
5. `pl_gz_rule_callee_body` — the empty-clause `IR_SUCCEED` sentinel (the actual wall; **shared path**).

NOTE: #5 touches the shared callee-frame path, so it was gated against the FULL Prolog suite both modes +
GATE-1 + no-new-global + an Icon m3 smoke before commit. No regression anywhere.

## R1 — `retract_mixed` RE-DIAGNOSED (the prior "integer-materialization" theory is WRONG)

I reproduced R1 cleanly (lifted both integer fences locally, uncommitted, then reverted) and chased it by
**static m3-vs-m4 asm diff first, then a runtime trace**. Findings, pinned to evidence:

### (1) The emitted code is NOT the bug — asm is byte-identical
The `fact(2)` retract-head construction (`CELL_UNIFY` → `rt_node_to_term(kind=0,ival=2)` →
`rt_compound_build_n(.S0,1,[2])` → `rt_unify_terms`) is **byte-identical** to the working seed-`assertz`
`fact(2)` head build, modulo the frame slot (`[r12+40]` retract vs `[r12+24]` seed — different synth slots,
both correct). So the prior handoff's "integer operand not materialized in TEXT medium" is DISPROVEN.

### (2) The real divergence is the STORE-POPULATION PATH differing between m3 and m4
Runtime trace of `/tmp/tret.pl` (`:- assertz(fact(1/2/3)). main :- retract(fact(2)), fact(X), write(X), nl, fail. main.`):

```
m3:  [no rt_pl_dyn_assertz_cell calls at all]
     retract fact(2): tries arg0=1, arg0=2, MATCHED+removed
     iter_step: next=NON-NIL → enumerates fact(1), fact(3)   ✓  (store = [1,3] after retract)

m4:  assertz fact(1): row head=A tail=A
     assertz fact(2): row head=A tail=B
     assertz fact(3): row head=A tail=C        → store = [1,2,3]
     retract fact(2): tries arg0=1, arg0=2, MATCHED+removed
     iter_step: next=NIL → store EMPTY          ✗
```

**m4 runs the seed `assertz`es at runtime (the `DET_ASSERTZ` goals prepended to `main`); m3 does NOT call
`rt_pl_dyn_assertz_cell` at all, yet m3's store is still populated and enumerable.** So the two modes
populate the dynamic store by DIFFERENT mechanisms, and after the SAME retract they hold different contents
(m3 `[1,3]`, m4 empty). The retract C code is the same `.so`; the inputs differ.

### (3) Where to look (NOT yet root-caused — handed off)
- Seed path: `prolog_lower.c:771-787` injects each directive-assertz for a MARKED pred as a goal into
  `main`'s clause body → emits `IR_DET_ASSERTZ` → `rt_pl_dyn_assertz_cell` at `main` entry. This is what m4
  runs (3 assertz calls observed). **Why does m3 NOT run these same injected goals?** That asymmetry is the
  bug. Hypotheses to check, cheapest first:
  (a) Does m3 `--run` actually execute the injected seed goals, or does it populate the store via a
      DIFFERENT path (e.g. the directive-fold into the static pred + some m3-only `iter_begin` fallback that
      reads the static `g_pl_pred_table`)? Dump `--dump-ir` is the same for both modes (one IR), so the
      divergence is at EMIT or RUNTIME-INIT, not lowering. Compare what each mode's emitted entry actually
      calls at startup.
  (b) m4 builds `[1,2,3]` then retract→empty. If retract's middle-removal (`prev->next = c->next`) is run
      against a list whose `prev`/`head` linkage was built by the runtime assertz in a way that makes
      `row->head` collapse to NULL on removing a non-head node — inspect `dyn_pred_intern`/`rt_pl_dyn_add`
      tail-linkage when 3 nodes were appended at runtime vs pre-seeded. The m4 assertz trace shows
      head=A stable, tail advancing A→B→C, so the list looks correct PRE-retract; the corruption is at or
      after retract. gdb the m4 binary: break `rt_pl_dyn_retract_cell` return, inspect `row->head`,
      `row->head->next`, `prev`, `c` for the fact(2) removal.
  (c) Atom args work in BOTH modes (handoff-confirmed: `retract(c(b)), c(X)` → a,d). Integer-only failure +
      m4-only + requires the runtime-assertz seed path ⟹ suspect an interaction between
      `copy_term_deep` of an integer `Term` and the list linkage under the m4 runtime-assertz population.
- CURRENT MITIGATION (committed, holds parity): integer-literal retract HEADS are FENCED in BOTH the
  admission arm (`pl_gz_rule_body_goal_ok`, scrip.c ~482) and the main-level build arm
  (`pl_gz_build_goal`, scrip.c ~1736): `if h0 is IR_STRUCT with any IR_LIT_I operand return 0`. Delete BOTH
  fences after the fix → +1 both modes → 115/115.
- REPRO: `/tmp/tret.pl` above. Temporarily comment out both fence lines, `make scrip && make libscrip_rt`,
  then `./scrip --run /tmp/tret.pl` (gives 1,3) vs
  `bash scripts/run_prolog_via_x86_backend.sh /tmp/tret.pl` (gives empty). Revert the fences when done.

## OPEN ITEMS FOR LON (flagged, unchanged from prior sessions)
- Harness `--mode all` still drives the deleted m2 `--run` arm → false FAILs; use `--mode run` /
  `--mode compile` separately. GATE-1 smoke + the m2 lines in the rung suite are false-FAIL (not a regression).
- With m2 gone, several of the 15 doomed globals may now be genuinely dead → floor possibly droppable.
