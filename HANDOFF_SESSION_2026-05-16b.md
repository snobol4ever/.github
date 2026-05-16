# HANDOFF — Session 2026-05-16b (Claude Opus 4.7)

**Repo state at handoff:** `.github` @ `58361ebc`, `one4all` @ `fddf7184`.

## What this session did

Two reversals and one new GOAL with extensive design.

### 1. Reverted BB0 deletion of sno_engine.js

Prior session's `SJ4-JS-BB0` (commit `54f82db5` in one4all) deleted
`src/runtime/js/sno_engine.js` (620 lines) believing it was a SNOBOL4
source interpreter that needed to be replaced with Byrd-box emit. That
diagnosis was wrong: `sno_engine.js` is the **pattern execution runtime**
for compiled JS output — `emit_js.c` is supposed to emit calls *into*
the engine, not replace it.

- Restored `sno_engine.js` from commit `a3eabfc9`. one4all `fddf7184`.
- Corrected `GOAL-SN4-JS-EMIT-BB-REWRITE.md` permanent rule. .github `fb24c9d5`.
- BB0 steps marked reverted; new sub-step PST-JS-BB0e-FIX added for
  reviewing the `sno_runtime.js` pattern sections that were also
  deleted (those may also need restoration — not done this session).

### 2. New goal: GOAL-PARSER-PURE-SYNTAX-TREE.md

Two-stage architecture for cleaning up the parser-to-IR pipeline.

**Stage 1 — Parsers:** every frontend produces a pure `tree_t` syntax
tree one-to-one with surface syntax. No lowering, no desugaring, no
graph construction. Diagnosis (Step 0) complete:

- SNOBOL4 ~clean (minor: EXPORT/IMPORT special-case, SCAN/SEQ subject
  rearrangement, goto-fields-on-STMT_t)
- Icon ~clean
- Raku ~clean
- Snocone — HEAVY violation (`sc_label_new`, `sc_finalize_*` for if/
  while/for/do/switch/function, `sc_clone_expr_simple` augop expansion,
  loop frame tracking, statement-list splicing, label-resolution at
  parse time — entire control-flow lowering runs in parser actions)
- Rebus — entirely separate IR (`RExpr/RStmt/RProgram`); zero `tree_t`
  references in `rebus.y`
- Prolog — entirely separate IR (`Term *`); also assigns variable slots
  during parsing (`scope_get → term_new_var(next_slot++)`)

Step ladder: PST-SN4-1* → PST-ICN-2* → PST-RAKU-3* → PST-SC-4* (14 rungs,
the big one) → PST-RB-5* → PST-PL-6* (7 rungs, with parallel build-paths
during transition) → PST-INV-7* invariant gates.

**Stage 2 — Lower:** consumes pure tree_t and produces IR. The design
evolved through several rounds in this session:

1. First draft — one `IR_t` struct with `c[]/n` children AND α/β/γ/ω
   ports. "Dual-axis" design.
2. JCON cross-reference (after Lon supplied jcon-master.zip) — confirmed
   the single-edge-per-port model. Each JCON record carries at most one
   labelled control edge; per-AST-node `ir_info(start, resume, failure,
   success)` mirrors our α/β/γ/ω.
3. Walked the worked example `if (n < 5) { s ? POS(0) ('yes'|'no') RPOS(0)
   } else { s ? ('0'|'1') }` end-to-end. Pinned down the key BB back-edge:
   `n8.β → n5` in the then-branch (when RPOS fails after "yes" matched,
   β retries the ALT for "no"). This single edge is graph-theoretically
   why patterns need four ports.
4. Lon corrected: parsers DO flatten n-ary left/right recursion (SNOBOL4
   grammar already does this for ALT and SEQ). That same flattening
   rationale carries into IR for n-ary kinds — `c[]` is logic, not
   optimization, because consumer code is genuinely simpler with a flat
   list than with a binary chain.
5. **Final design (Lon's proposal):** split into two IR types entirely.

```
(source) → parser → tree_t (pure AST) → lower → { IR_sm_t, IR_bb_t }
                                                  SM references BB
                                                  BB never references SM
                                                  (BB callouts use opaque
                                                   engine hooks, not structural
                                                   SM pointers — asymmetry holds)
```

- `IR_sm_t` — flat array of stack-machine instructions. Every program
  has at least 2 SM instructions. Inline scalar args plus optionally
  one `IR_bb_t *` for SM_EXEC_PATTERN / SM_RESUME_GENERATOR. Walked
  linearly by the interpreter and by every native emitter.
- `IR_bb_t` — 4-port directed graph with α/β/γ/ω. Pattern subgraphs and
  generator subgraphs. Retains `c[]/n` for n-ary kinds (PAT_ALT
  alternatives, PAT_CAT pieces, PL_CHOICE alternatives, CALL args, etc.).
  Dispatched by the Byrd-box engine.

Kind assignment is mechanical: all `IR_PAT_*`, `IR_PL_*`, `IR_ICN_*`
(generative versions) → BB. Everything else (literals, vars, binops,
assigns, gotos, IF, RETURN, CALL, SUSPEND, BREAK, NEXT, PROC) → SM.

Stage 2 step ladder restructured:
- PST-LR-0a — define `IR_sm_t/e/_program_t` and `IR_bb_t/e/_block_t`
  in new headers
- PST-LR-0b — migration scaffolding (legacy converter `IR_t → IR_sm_t`
  or `IR_t → IR_bb_t`)
- PST-LR-0c — migrate `lower_pat_dcg.c` to emit `IR_bb_t` directly
  (smallest first move — already 90% there)
- PST-LR-0d — migrate SM codegen
- PST-LR-0e — migrate interpreter (`ir_exec.c`)
- PST-LR-0f — migrate emitters one by one (x86, JVM, JS, .NET, WASM)
- PST-LR-0g — delete legacy `IR_t`

Then PST-LR-2a..2i per-construct lowering passes can re-target each
construct to SM or BB or both.

## State at handoff

- `.github` HEAD: `58361ebc` — GOAL-PARSER-PURE-SYNTAX-TREE.md complete
  with split-IR design, Prolog Term→tree_t step ladder, JCON cross-
  reference, worked example, full kind-assignment migration map.
- `one4all` HEAD: `fddf7184` — `sno_engine.js` restored.
- PLAN.md updated with the new active goal row.

## Next session start

Lon will name a goal. Likely candidates:

- **PST-SN4-1a** — first rung of Stage 1 SNOBOL4 cleanup (remove
  EXPORT/IMPORT special-case from `sno4_stmt_commit_go`). Smallest,
  cleanest first move.
- **PST-LR-0a** — start Stage 2 by defining the two new IR header types.
  Can be done in parallel with Stage 1.
- **PST-JS-BB0e-FIX** — review `sno_runtime.js` pattern-interpreter
  sections deleted during BB0 for possible restoration.

## Open architectural question

Lon's last remark: "Oh yeah just subgraph where pointers can be hybrid."

This relaxes the strict BB-never-references-SM rule for the case of
mixed subgraphs. Read as: while the **default** is asymmetric one-way
reference, pattern callouts and similar bridge constructs may carry
`IR_sm_t *` from a BB node where it makes sense as a localized exception.

This is consistent with the JCON-style callout model (the BB node holds
a hook descriptor; at the engine's option that descriptor may resolve
to a direct SM-entry pointer rather than going through a name table).
The asymmetry holds *structurally* in 99% of cases; the hybrid pointer
is the engineering-grade safety valve for the remaining cases.

Worth documenting in the GOAL during PST-LR-0a (when the types are first
defined) — likely as a field comment on the `IR_bb_t`'s opaque/callout
slot.

## Authorship credit

Per the three-milestone authorship agreement in PLAN.md:
this session is **Claude Opus 4.7**, third developer of snobol4ever,
co-author of one4all / SCRIP.
