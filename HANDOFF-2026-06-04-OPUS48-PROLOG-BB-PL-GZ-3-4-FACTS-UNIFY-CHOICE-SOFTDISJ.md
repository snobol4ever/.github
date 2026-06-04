# HANDOFF — 2026-06-04 — Opus 4.8 — PROLOG-BB — PL-GZ-3 + PL-GZ-4 LANDED (facts+unify, choice+backtracking, soft-tail disjunction)

## What landed (SCRIP main, four commits, all pushed; HEAD `84fee42`)
- **PL-GZ-3a `b7bb399`** — frame-cell logic vars + explicit `=/2` on the GZ path.
- **PL-GZ-3b `6f69e3f`** — single-clause ground-fact head-unify inlined at admit. **PL-GZ-3 rung [x].**
- **PL-GZ-4a `20f15db`** — multi-clause ground-fact CHOICE + backtracking — THE seed transcription
  (`test_pl_1.c` edge/2 shape).
- **PL-GZ-4b `84fee42`** — query-tail `(G ; true)` soft-fail promotion. **PL-GZ-4 rung [x].**

Every probe class m2 == m3 == m4 stdout byte-identical AND rc-identical; m3 native (no INTERP-FALLBACK
banner) and m4 carrying `gzq` labels for the admitted set; every decline identical in BOTH branches
through the ONE `pl_gz_admit`.

## Architecture the next rungs inherit
- **IR kinds appended** (end of Prolog block, `IR.h` + names in `scrip_ir.c`): `IR_CELL_UNIFY` (3a),
  `IR_CELL_CHOICE` (4a). m2 never sees them — they exist only in the admit's rewritten root.
- **Frame layout** (the seed ABI, single query activation `ζ=r12` from `rt_frame()`): `[ζ+0]` query trail
  mark; logic-var cells `[ζ+8+8i]` via `GZ_CELL_OFF(slot)` (`bb_template_common.h` — offsets single-sited
  there; admit deals ONLY in slots); choice boxes take 2 slots each (mark, cursor) AFTER the var cells,
  watermarked by admit (`cslot`, cap 62). `QUERY_FRAME` cells-init covers `nvars` only; choice slots are
  raw ints the box writes at α before any read.
- **`bb_cell_unify.cpp` arms**: self-unify vacuous (compile-time) · cell↔cell `rt_unify_terms` ·
  cell↔const `rt_pl_unify_cell_const` (atom RO sealed in-box) · **const↔const emit-time fold** (equal →
  `jmp γ`, unequal → `jmp ω` — WAM-CP-7 specialization family).
- **`bb_cell_choice.cpp` = edge/2 verbatim**: α: `rt_trail_mark`→mark cell, cursor:=1, fall into clause 1;
  clause-k var-arg unifies short-circuit `je L(k)`; dead const-const clause (emit-time mismatch) = whole
  clause `jmp L(k)`; `def L(k)`: k<N−1 → cursor:=k+2, `rt_trail_unwind(mark)`, FALL into clause k+1; last
  → unwind, `jmp ω`; `def β`: cmp-chain on cursor `je L(k)`, default `jmp L(N−1)`. Internal-label ids
  0..N−1, RO atom seals from id N — the SHARED 16-id space is safe under the admit caps (N≤4, arity≤2 →
  worst 12). ZERO `resolve_cp_current` refetches; mark/unwind classified VALUE (coupling gate: others 0).
- **Conjunction = the Byrd-Box backward redo chain** (`flat_drive_gz_query`): goal β labels pre-allocated;
  `FILL(g, next_γ, (i==0 ? land_ω : gb[i-1]), gb[i])`. Det boxes' `def β → jmp ω` propagates redo
  leftward, so the pure-wiring `bb_fail` leaf (reused as the lowered `fail` goal — `IR_FAIL` admitted in
  the goal loop) IS the backtracking driver. Stacked choices give the full cross product (verified).
- **`pl_gz_admit` validators (scrip.c)**, shared 3b/4a: `pl_gz_fact_clause_units` (clause graph =
  GCONJ of `UNIFY(LOGICVAR i, const)`, `ngoals==arity`, forbidden-kind scan; arity-0 = bare SUCCEED) ·
  `pl_gz_call_args_ok` (args LOGICVAR slot<64 or ATOM/LIT_I) · `pl_gz_goal_callee` (registry key
  `"name/arity"` → `resolve_bb_lookup` → `bb_graph_of_pred`). Single-clause callee = clause graph direct;
  multi-clause = entry `IR_CHOICE` over `bb_choice_state_t.bodies[]`, each body shape-checked, consts
  collected into `pl_gz_choice_state_t` (`IR_interp_state.h`: nclauses/arity/mark_slot/args[2]/consts[4][2],
  node→template via `bb_prepare` `bb_zn`, CATCH precedent). assertz-class mutation is impossible inside the
  admitted goal set, so static inlining is sound.
- **4b soft tail**: admit detects exactly one `IR_DISJ` whose `bb_operand_aux_get` arms are
  `[the one inner GCONJ (or a single goal), IR_SUCCEED]` AND which is the OUTER clause-conj's ONLY goal
  (disjunctive bodies nest TWO GCONJs — outer ngoals==1 goals[0]==disj; this was the one mid-flight bug:
  the original single-GCONJ scan declined everything). Flag rides the rewritten `QUERY_FRAME`'s `dval` →
  driver `op_sb` on the sa=1 landing FILL → `bb_query_frame` ω landing emits `mov32 eax,1` after the
  unwind (comment says PROMOTED). Semantically exact for one-shot main: redo exhausting past goal[0] IS
  entering the `true` arm with bindings undone. Non-`true` right arms, 3+ arms, goals after the disj all
  decline.

## Bugs killed (hard-won, do not re-learn)
1. **Interned-label seal aliasing (3a)**: `_.bb_ls/_.bb_rs` are interned LABELS in shared mutable buffers —
   sealing them as RO string literals emitted garbage. Templates must read raw text via the NODE pointers
   (`((IR_t*)_.bb_ln)->sval`), which is why `bb_lk/li/ln + bb_rk/ri/rn` exist.
2. **Trail zero-cap `GC_realloc` segfault (3a, m4 standalone)**: zero-init Trail with `cap*=2` from 0 →
   `GC_realloc(p, 0)` FREES the stack → second `trail_push` wrote NULL. Fix: `rt_trail_mark` lazy-inits
   (`if (!stack||cap<=0) trail_init`) — `prolog_unify.c:19`.
3. **Two-GCONJ disjunctive nesting (4b)** — see above; the admit's body discovery must resolve
   outer-vs-inner, never assume "one GCONJ".

## Gates & ratchets (all green at `84fee42`)
- GATE-1 smoke: m2 **5/5** HARD · m3 **4/0/1** (hello, write, unify, clause native; only `recursion`
  EXCISED = GZ-5's flip) · m4 **5/5**.
- GATE-3 suite: m2 **115/115** HARD · m3 **18/0/97-EXC** (was 12 at session start) · m4 **105/0/10-EXC**.
- `test_gate_pl_gz2.sh` PASS (neg ratcheted earlier to `X = f(a)`); `test_gate_pl_gz3.sh` PASS (3a+3b
  probes; neg2 ratcheted multi-clause→rule-clause when 4a admitted multi-clause); `test_gate_pl_gz4.sh`
  PASS (enum3/mixarg/midfail/nested/nosol + softenum/softbind/softsemi incl. a PROMOTED `.s` assertion;
  negatives: 5-clause and non-true right arm). ALL negative-proven via sed-corrupt → exit 1 (run corrupt
  copies from `scripts/`).
- Coupling gate at the reset baseline: choice 19 · goal 10 · others 0 · rung05 `.s` 39.
- Ratchet rule held throughout: each rung's admission obsoletes some older gate's negative exemplar —
  expect it, move the exemplar UP the decline boundary, don't weaken the gate.

## PL-GZ-5 recon (DONE — no code; start at 5a)
Seed `path/2` + driver (`test_pl_1.c:141-250`) fix the architecture:
- Predicates emit as functions with **two entry labels** `pred_α`/`pred_β` (the seed's C `(ζζ, int entry)`
  is print convention ONLY — the `int entry` dispatch does not exist in emitted code; RULES unchanged).
- **ζ-tree**: child activations are pointer slots in the caller's frame; `enter` = reuse-(memset)-or-calloc
  → needs an `rt_enter(void **slot, size)` VALUE helper. Recursion depth rides the calloc chain.
- **Args are cell POINTERS**; α saves them into the callee frame (β re-entry needs only the ζ slot);
  caller CONST args materialize as caller-local cells (cells_init + unify-const covers it, no new rt).
- **Conj-with-calls = the pair-loop**: `call pred_α` / `test rax` / λ-branch; redo re-enters `call pred_β`
  (seed c2: edge–path ping-pong).
- **Feasibility verified**: the J-record patch machinery is OPCODE-GENERIC (`x86_asm.h` ~lines 188-221,
  534) — `'J'` resolves rel32 against whatever Lrec bytes precede it, so a direct call encoder is
  `Lrec(0xE8)+Jrec(id)` binary / `call name` text, ~6 lines, same family as jmp-to-port. **The one design
  decision**: how the CALLEE-entry target reaches the call box — a δ-port-style fill alongside γ/ω/β is
  the principled shape (the seed's call IS a port edge to another box's α). Decide this first in 5a.
- Sub-ladder: **5a** call encoder + δ-target fill + single-clause var-head rule callee (non-recursive;
  "head vars ARE the params" — var-only heads need no head-unify boxes) · **5b** `rt_enter` ζ-tree +
  recursion (flips the smoke `recursion` probe) · **5c** multi-clause rule predicates (full `path/2`).
  GZ-5 also owes the deferred general 2-arm disjunction (redo-into-right-arm) — or split it out as 4c.

## Flags / pre-existing
- `test_smoke_compile_hello_all_langs.sh`: `rebus ROW-DRIFT FAIL-compile` is PRE-EXISTING
  (stash-bisected before PL-GZ-3 work; not ours; untouched).
- PL-GZ-1b checkbox in the ladder still shows `[ ]` while STATE says LANDED — pre-existing inconsistency,
  left for Lon to reconcile.

## Resume
Repos: `~/SCRIP` (HEAD `84fee42`, clean) · `~/.github` (this handoff) · `~/corpus` (untouched this
session — all probes were /tmp synthetics; the gates carry them). Suites:
`scripts/test_smoke_prolog.sh`, `scripts/test_prolog_rung_suite.sh`, `scripts/test_gate_pl_gz{2,3,4}.sh`,
`scripts/test_gate_pl_coupling.sh`. m2 `--interp` · m3 `--run` (banner on stderr when declining) ·
m4 `scripts/run_prolog_via_x86_backend.sh`. Next session opens PL-GZ-5a.
