# HANDOFF — Prolog-BB: compound-unify m4 excision DIAGNOSED + option-(b) plan shovel-ready

**Date:** 2026-06-03 · **Model:** Claude Opus 4.8 · **Track:** GOAL-PROLOG-BB.md
**Status:** Diagnostic + design session. **NO source code changed.** Working tree clean, all gates
re-verified green at SCRIP HEAD `97f807f`. One design fork surfaced; awaiting Lon's one-word sign-off
before the next session implements.

## Baselines re-verified green (HEAD `97f807f`, nothing touched)

| Gate | Result |
|---|---|
| `make -j4 scrip` + `make libscrip_rt` | rc=0 |
| GATE-1 smoke | m2 5/5 · m3 4/5 (unify = known harness artifact) · m4 5/5 |
| GATE-3 rung suite | m2 **111/111** · m3 **111/111** · m4 **75 / 0 / 36** |
| `test_gate_bb_one_box.sh` (PL-HY-FENCE) | PASS |
| FACT greps | `g_vstack` 0 · `seg_byte(SEG_CODE`/`SL_B(` outside templates 0 · `b.size()` ledger 0 |

## What was diagnosed

The m4 `EXCISED=36` set includes **rung03 / rung05 / rung06**, and all three are blocked by **one single
cause: compound (list/struct) unification is deferred.**

- **rung03** `f(X,a) = f(b,Y)` — struct-vs-struct unify.
- **rung05** `member(X,[X|_])` — clause head unifies arg2 against list cell `'.'/2` (a struct).
- **rung06** `append`/`length`/`reverse` — all built on list-cell head unification.

Empirically isolated: a pure-recursion probe (`count(N) :- N>0, write(N), nl, M is N-1, count(M).`) **PASSES
m4 cleanly**; adding any compound-operand `IR_UNIFY` excises. The gate that rejects them is
`src/driver/scrip.c:227-228` (`pl_rich_node_emittable`'s `IR_UNIFY` arm rejects `IR_STRUCT`/`IR_ARITH`/
`IR_LIT_F` operands), mirrored by `bb_unify.cpp`'s `u_deferred()` bomb. This is exactly the
PL-HY-1a-flagged deferred arm ("unify scalar-only, compound/float DEFERRED").

## Semantics grounded in canonical source (RULES "CONSULT CANONICAL SOURCES")

gprolog `src/EnginePl/unify.c:125-145` (the `TAG_STC_MASK` branch): structure×structure unify =
**functor+arity match, then element-wise recursion over args.** That is precisely what `rt_unify_terms`
already does on two built `Term*` trees — so building both operands to ground/partial term trees and
calling `rt_unify_terms` is the correct, complete implementation.

## The substrate ALREADY EXISTS (no new runtime needed)

- `emit_build_compound_term(const IR_t *nd)` (`src/emitter/BB_templates/bb_builtin.cpp:11`) — the
  **sanctioned mode-4 serialized encoder** (PL-HY-1a verdict: NOT a dup; its mode-3 twin is the single
  `rt_node_to_term_ptr` call). It recurses `IR_STRUCT`/`IR_ARITH` children and reads each node **at emit
  time**, baking only literal immediates (`mov edi,<kind>`, `mov rsi,<ival>`) plus `lea rdx,[rip+strlabel]`
  for strings — **zero runtime pointers, fully relocatable.** `bb_goal` already uses it for compound args.
- `rt_unify_terms(void*,void*)` — unifies two built terms (the gprolog-grounded deref/`X==X`-noop/bind law).
- (Runtime-side equivalent for mode-3, already wired at 23 sites: `rt_node_to_term_ptr` →
  `resolve_node_to_term`, `src/interp/IR_interp.c:303,342`.)

`bb_unify.cpp`'s general arm already has the right SHAPE (build left → save on stack → build right →
`rt_unify_terms`); it bombs compounds only because its scalar helper `u_build()` is a single
`rt_node_to_term` call that cannot recurse.

## The ONE open design fork (why this awaits Lon)

`bb_unify` has signature `extern "C" void bb_unify(void)` and reads only **promoted scalars** (`_.bb_lk`,
`_.bb_li`, `_.bb_ls`, …) per the no-`pBB`/no-`_.node` FACT rule. To call `emit_build_compound_term` it needs
the operand **IR node**. Two ways to give it one:

- **(a)** give `bb_unify` a `pBB` arg, like `bb_goal` has. → REJECTED rec: grows the very `pBB` debt the
  x86() revamp is paying down (`bb_goal`'s `pBB` is one of the 13 still-open conversion sites).
- **(b)** promote the two operand node-pointers into a `g_emit` sidecar (the `bb_arith` mechanism: the
  driver `bb_prepare` deposits them), and `bb_unify` passes them to `emit_build_compound_term`.

This sub-decision is entangled with the **global direction of the revamp** (end-state = boxes never touch
IR nodes), which is why GOAL-PROLOG-BB reserves it for Lon. A session resolving it unilaterally by picking
the reading that unblocks it is the exact failure mode RULES.md's NO-C-BYRD-BOX history warns against.

### Recommendation: option (b)

Reuses the sanctioned shared encoder (no new walker → NO-DUP-clean), keeps `bb_unify` `pBB`-free (no new
debt), emit-time walk stays fully relocatable. **Gate-safe by construction:** m2/m3 route compound-unify
through the interpreter (`bb_exec_once`), so the 111/111 byte-identity cannot move; rung03/05/06 are
currently EXCISED, so the worst case is they stay EXCISED — **zero regression surface** on the 75 passing
m4 rungs. Expected payoff: m4 **75 → 78**.

### Correction to a prior framing

An earlier "bake the operand node pointer as a `movabs` immediate" idea is **struck**: it is forbidden
(mode-3-in-process-only, breaks mode-4 relocatability per PER-BOX-LOCAL-STORAGE) **and** vacuous (mode-3
compound-unify runs the interpreter, so the emitted bytes would never execute). The real choice is only
(a)-vs-(b) above.

## Shovel-ready edit (3 small touches) for the next session — pending "do option b"

1. **`src/emitter/emit_bb.c`** `bb_prepare` IR_UNIFY arm — promote `nd->α` and `nd->β` node-pointers into two
   new `g_emit` sidecar fields (mirror the additive `bb_lk`/`bb_li` promotion; appended → existing offsets
   undisturbed → Icon/SNOBOL4 baselines unchanged).
2. **`src/emitter/BB_templates/bb_unify.cpp`** general arm — swap the two scalar `u_build(...)` calls for
   `emit_build_compound_term(<promoted node>)`; drop the `IR_STRUCT` half of `u_deferred()` (keep the
   float-unify bomb until CAT-D float substrate lands). The var-var / var-const / self-unify scalar arms are
   unchanged.
3. **`src/driver/scrip.c:227-228`** — admit `IR_STRUCT` operands to `pl_rich_node_emittable`'s `IR_UNIFY`
   arm (keep `IR_LIT_F` rejected).

**Verification plan:** GATE-3 m2/m3 must stay byte-identical (interpreter-routed → guaranteed); m4 →
**78 / 0 / 33** (rung03/05/06 flip EXCISED→PASS); smoke 5/5/5; FACT greps 0; `test_gate_bb_one_box.sh` PASS;
template-purity unchanged. Prove each rung 3-mode AGREE before commit.

## Setup note

`refs/` was dropped from the fresh-start repo; the gprolog grounding used this session came from the
uploaded `4-gprolog-master.zip` (extracted to `/home/claude/gprolog-master`). Per RULES "CONSULT CANONICAL
SOURCES," restore `refs/gprolog` / `refs/swipl` symlinks when canonical grounding is needed.

## Repos state

| Repo | HEAD |
|---|---|
| SCRIP | `97f807f` (+ this doc) |
| .github | `a2d0f983` (+ goal-state note) |
| corpus | unchanged |
