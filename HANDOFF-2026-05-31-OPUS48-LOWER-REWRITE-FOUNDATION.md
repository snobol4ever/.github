# HANDOFF 2026-05-31 — Opus 4.8 — LOWER REWRITE: unified four-port foundation + tree-pattern plan

## Context
Continuation of the 2026-05-31 PIVOT (Lon: "start over / do it completely different"). This session Lon
gave the direction concretely: **rip-and-replace `lower.c` with ONE unified AST→IR lowerer**, built on the
Proebsting four-port attribute-grammar model, with an eventual **tree-pattern-matching** dispatch (Icon ?
SNOBOL flavor) and an Icon-bootstrap endgame. Ground zero — we do not care what the old build breaks.

## Survey finding (changes the scope for the better)
There is only ONE real AST→IR lowerer: **`src/lower/lower.c`** (2840 lines, 7 separate TT_ dispatchers).
The other "lower" files are NOT AST→IR and are out of scope for the merge:
- `src/frontend/prolog/prolog_lower.c`, `src/frontend/rebus/rebus_lower.c` — AST→AST normalizers (`Term*`/`tree_t`→`tree_t`).
- `src/lower/lower_sno.c` — a tree→`.sno` SOURCE emitter (`tree_to_sno`), a transpiler.
So "merge" = rewrite `lower.c` only. Alphabet: 156 `TT_*` kinds in, 110 `IR_*` node kinds out.

## The architecture (settled this session)
**Master dispatch: ROLE × kind.** A `TT_` kind has a shared STRUCTURE; its ROLE-CONTEXT picks the rule:
- `ROLE_VALUE` — general expr/statement (Icon/Snocone/Rebus/Raku/SNOBOL value position)
- `ROLE_PATTERN` — SNOBOL pattern element (entered at `subj ? pat`)
- `ROLE_GOAL` — Prolog goal (entered in a clause body)
One funnel `lower2(cx, e, γ_in, ω_in, &α_out, &β_out)` → branch on `cx.role` → ONE `switch(tree_e)` per role.
~2/3 of kinds are role-monomorphic (one arm); only QLIT/VAR/FNC + the arith/rel kinds (shared VALUE↔GOAL)
need the inner role split. This is the "one switch, lang code inside" shape, made precise.

**The canonical signature IS the attribute grammar** (Proebsting; jcon `ir_a_X(p,st,inuse,target,bounded,rval)`):
```
IR_t * lower_X(IR_graph_t *bbg, const tree_t *e, IR_t *γ_in, IR_t *ω_in, IR_t **α_out, IR_t **β_out);
```
- γ (succeed) / ω (fail) are INHERITED → in as two pointers.
- α (start) / β (resume) are SYNTHESIZED → out as two pointers-to-pointers.
SCRIP `IR_t` carries α/β/γ/ω as POINTER PORTS (not jcon `ir_Goto` chunk-lists), so "goto L" = a pointer
assignment; chains of unconditional gotos COLLAPSE (= the paper's Fig-2 optimization, for free).

**Two template classes** (= the "linear-forward-fail vs forward-backtrack-abort" distinction; jcon `bounded`):
1. BOUNDED LEAF (paper §4.1): single value. α→γ; β→ω (resume fails). `emit_leaf` honors `cx.bounded`
   (jcon's `/bounded` guard) — a generator collapses its resume port to ω when only one value is wanted.
2. RESUMABLE GENERATOR: α starts; γ per value; β re-pumps; ω on exhaustion.

**Wiring is local:** each rule wires 4–12 ports among {node + 2–3 children}, exactly the port equations in
the paper/irgen. Children are lowered with the caller threading their γ/ω; forward refs (E1.succeed→E2.start)
are patched after both children exist. Three primitives encode the whole discipline: `nalloc`, `set_succ_fail`
(jcon default-only `/x:=y` idiom — never clobber a threaded port), `ret` (write the two synthesized ports).

## What landed (NEW files in SCRIP, NOT wired into the build/Makefile/driver — deliberate)
- **`src/lower/lower2.c`** (358 lines, compiles clean, 0 errors as a standalone TU). The foundation:
  - canonical signature on every box; `nalloc`/`set_succ_fail`/`ret`/`emit_leaf` primitives.
  - 5 FOUNDATION BOXES wired + PROVEN faithful to the paper: `v_literal` (§4.1 / ir_a_Intlit),
    `v_unop` (§4.2 uminus), `v_binop` (§4.3 plus AND LessThan — relational flag `dval=1.0`),
    `v_to`/`v_to_by` (§4.4 / ir_a_ToBy), `v_if` (§4.5 / ir_a_If — the one runtime-gated box; E1 lowered
    `bounded=1`).
  - PATTERN leaves wired (LIT/ARB/REM + SPAN/ANY/NOTANY/BREAK/BREAKX via `pat_cset_arg`, the cset trichotomy
    centralized — was copy-pasted 5× in legacy `build_node`). GOAL leaves wired (cut/true/fail).
  - 118/156 kinds armed; the rest are LABELLED extension stubs, each annotated with its source `ir_a_*`
    procedure, routing LOUDLY to `lower_unhandled` (never a silent fallthrough).
- **`src/lower/prove_lower2.c`** — proof harness. Links lower2.c + scrip_ir.c ONLY (provides local
  `kind_is_resumable` + `cset_try_fold` stub so the old lowerer is NOT linked). Builds an AST by hand, lowers
  via a thin `lower2_value_entry` shim, prints each IR node's idx + α/β/γ/ω to diff against the paper figures.
  (Re-add the shim to lower2.c to re-run; it was stripped to keep lower2.c pure.)
- **`src/lower/tmatch_proto.c`** — PROTOTYPE of the tree-pattern matcher (compiles). `tm(e,KIND,nargs,&c0,…)`
  and `tm_g(e,KIND,"tag",nargs,…)` match a shallow shape + capture children; an `#if 0` exhibit shows 3
  foundation arms + the nested `EVERY(ASSIGN(VAR,TO(lo,hi)))` + the Prolog ladder rewritten in pattern form.

## PROOF result (the reason this is a SOLID foundation, not a guess)
Lowered the paper's own examples through `lower2()` and diffed port topology:
- `5 > ((1 to 2)*(3 to 4))` → exactly **9 IR nodes** (paper's "nine expanded templates"). **14/17 control
  edges matched Figure 1 immediately;** the 3 "mismatches" are FAITHFUL collapses — with constant bounds the
  pointer-port form equals **Figure 2 (optimized)**, the better result.
- The proof CAUGHT A REAL BUG in `v_to`: it wired both children's fail to outer `ω_in`. Canonical `ir_a_ToBy`
  requires **`to.fail → from.resume`** (to-child exhaustion resumes the from-child). FIXED, then RE-PROVEN with
  `(1 to 2) to (3 to 4)` (the paper's §2 "initiated four times" case): the critical edge now reads
  `to2.fail → to1` where before it was the outer fail. Faithful.
- Proven = TOPOLOGY only. NOT yet executed (no executor wired to lower2 output). Value-level proof is the next
  level and depends on `bb_exec.c` honoring the relational flag (`dval=1.0`) and the if-gate (`node.β` runtime
  dispatch) the way lower2 encodes them — VERIFY against the executor, do not assume (RULES: consult canonical).

## The tree-pattern-matching idea (Lon's "two shots"; STEP 2, after the foundation is complete)
MEASURED on legacy lower.c: the DECISION at each node is SHALLOW — 120 decision-peeks, but only **12 sites
peek two levels** (ASSIGN(IDX(a,k),rhs); EVERY(ASSIGN(VAR,TO))) and **ZERO peek three.** The WIRING is uniform
recursion (78 lower-calls — one per child subexpression). So lowering = MATCH shallow shape + CAPTURE immediate
children + RECURSIVELY lower each + WIRE. That is exactly what `tm`/`tm_g` serve.
- Shot 1: `tm`/`tm_g` (match + capture). Shot 2: per-role switch where each arm is `if (pattern matches) →
  produce wiring`. The nested 2-level peeks read top-down as the AST shape (`EVERY(ASSIGN(VAR,TO(lo,hi)))`).
- LOC shrink is modest (~30%); the WIN is uniformity (every `e->n<k`/null guard vanishes into the match; the
  Prolog if-ladder becomes a table of `shape ? builder`).
- **Sequencing decision:** do step 2 AFTER the hand-coded foundation boxes are all in and proven — refactor
  proven code into pattern form, don't design two things at once.

## Design threads (recorded for the endgame)
- **Parsing symmetry.** Parsers are bison/flex-generated (never hand-edited). The parse is an LALR pattern
  match tokens→tree; `tm`/`tm_g` add the SYMMETRIC match tree→IR on the way down. Same shape, two directions.
- **Deferred eval ↔ capture.** `IR_PAT_DEFER` (bb_pat_defer.cpp, 3 arms; `rt_defer_match(var,flag,Δ)`) binds a
  pattern-valued var and matches it AT RUNTIME. A tree-pattern CAPTURE is the compile-time analog: `tm` binds a
  subtree but defers lowering until the arm decides. Same deferral discipline, one level up — why it composes.
- **Icon-bootstrap endgame.** The lowerer IS a tree-pattern matcher with uniform recursion = an Icon program
  over `tree_t`, each rule a SNOBOL pattern over `node.kind ++ node.sval` with children captured. Dependency
  ordering: (1) finish C foundation + prove; (2) refactor into `tm`/`tm_g` pattern form; (3) once Icon-BB
  executes enough, the pattern-form C transliterates to Icon almost mechanically. Pattern-form C is the bridge.

## Next steps (suggested order)
1. **Extend the proven core**: add `Every` (ir_a_Every), `Alt` (ir_a_Alt — FIRST box where β re-enters a
   SIBLING, the real backtracking test), conjunction `&`. Prove each through `prove_lower2.c`.
2. **Close the topology↔semantics gap**: wire `lower2` output through `bb_exec` on `1 to 5`; confirm values,
   confirm the relational flag + if-gate encodings are honored (or adjust to what the executor wants).
3. **Rebuild the program/proc walkers** (`lower()`, `lower_proc_body`, `lower_pl_predicate`, `IR_lower_pat`)
   that drive the per-node engine over a whole program and populate `stage2_t`.
4. Continue filling VALUE/PATTERN/GOAL arms box-by-box, each grounded in its `ir_a_*` and proven.
5. THEN step 2 (tmatch refactor), THEN (much later) the Icon bootstrap.

## Environment notes (carried from prior handoff)
- Work git in a FULL clone on local disk (this session used `/home/claude/SCRIP`, a fresh full clone — safe).
- Use `grep -a` on post-AST source (UTF-8 α/β/γ/ω trips binary detection). Shell is `/bin/sh` for some tools.

**Build state:** old `lower.c` UNTOUCHED — `make scrip` still builds the legacy path (SNOBOL still aborts
`[SMX] FATAL` by design; Icon m2 6/6). The three new files are standalone, not in the Makefile, so nothing
regressed. No gates were run this session (foundation is pre-execution).
