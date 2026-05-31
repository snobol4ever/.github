# HANDOFF 2026-05-31 — Opus 4.8 — ICON-BB mode-2 foundation correctness fixes

## TL;DR
Picked GZ-7 (`x := 42; write(x)`), found its mode-2 oracle already passing, and while grounding it
discovered and fixed **four** real mode-2 oracle correctness bugs in the Icon foundation. All grounded in
canonical Icon sources per the CONSULT-CANONICAL-SOURCES rule, all gated, all non-regressive, locked in by a
new 27-case regression gate. Build GREEN throughout. **No mode-3 / emitter work** (the larger fork-gated unit
was deliberately not started).

## SCRIP commits (all on `origin/main`, pushed)
- `8615c04` **`IR_UNOP` exec arm** (`bb_exec.c`). The unified lowerer emits `IR_UNOP` (tree kind in `ival`),
  but `bb_exec.c` had no `IR_UNOP` arm — only the dead per-kind `IR_NEG/IR_POS/IR_SIZE/IR_NONNULL/IR_CSET_COMPL`
  arms (no live lower path emits those). So every unary op fell to the loud default and FAILED
  (`write(-7)` printed nothing — the UNOP failed → write never ran). Added `IR_UNOP` mirroring `IR_BINOP`'s
  dual structure (postfix `ag_ring_peek` when `α` NULL, tree `bb_exec_node` otherwise), dispatching on
  `(tree_e)bb->ival`: `-` negate, `+` numeric-coerce, `*` size, `\` nonnull, `~` cset-complement.
  Generator-ish ops (RANDOM/ITERATE/INTERROGATE) stay at the loud default (unchanged). Cross-language win:
  SNOBOL4 `X = -5` → `-5`.
- `de0ce21` **integer `BINOP_POW`** (`lower_program.c`). Canonical `oarith.r` `^`/`bigpowii`: int^int (exp≥0)
  is INTEGER, not real. `binop_apply` always returned `REALVAL(pow(...))` → `2^10` printed `1024.0`. Added the
  integer fast-path for `exp>=0` (matches the existing `^` fn-string guard `ri>=0`; negative-exponent stays
  real — unchanged). Shared Icon+SNOBOL4 `BinopKind` path (Prolog uses separate `resolve_arith_eval`); correct
  for Icon `^` and SPITBOL `**`. Now `2^10→1024`, `2.0^10→1024.0`, `2^0.5→1.414…`.
- `16e28db` **regression gate** `scripts/test_icon_arith_unary_mode2.sh` (additive; existing smoke baseline
  untouched). Locks in the fixes + verified-correct foundation.
- `7dc77be` **`v_to` captures the `TO_BY` step** (`lower.c`). Canonical `ir_a_ToBy` threads from/to/BY
  (default 1); the `IR_TO_BY` exec arm reads the step from `node->ival`, but `v_to` dropped `c[2]` entirely —
  so every `to by` ran with step 1: `1 to 5 by 2 → 1 2 3 4 5` (want `1 3 5`), and negative steps failed
  outright (`3 to 1 by -1 → ∅`). Added `to_by_const_step()` capturing a CONSTANT step into `node->ival`: int
  (`TT_ILIT`), real (`TT_FLIT` → reinterpreted bits + `"ar"`), and signed wrappers (`TT_MNS`/`TT_PLS`, since
  `by -1` parses as `TT_MNS(TT_ILIT 1)`). Variable/expression steps NOT yet threaded (stay default 1 — known
  limitation). Plain `TT_TO` unaffected (never sets `ival`; exec uses `counter++`). Now `1 to 5 by 2→1 3 5`,
  `3 to 1 by -1→3 2 1`, `10 to 2 by -2→10 8 6 4 2`.
- `aabf060` **`v_assign` Icon `:=` generator-transparent** (`lower.c`). Canonical `ir_binary`: `:=` is a
  `funcs` member, so when NOT bounded the assign's resume threads to the RHS resume — `every i := (1 to 3) do
  write(i)` must yield `1 2 3`. `v_assign` returned a hard bounded resume (→`ω_in`) → produced only `i=1`.
  Thread resume→`rβ` (rhs resume) when **Icon AND `!cx.bounded` AND `rβ` is a real generator resume**;
  `rhs.γ` already →`as` so each resumed value re-stores. Icon-gated + guarded: SNOBOL4/Rebus and bounded/
  non-generator rhs (`x := 42` where `rβ==ω_in`) keep `resume→ω_in`, provably unchanged. Now
  `every i := 1 to 3 do write(i)→1 2 3`, `every i := 1 to 5 by 2→1 3 5`, `every j := (10|20|30)→10 20 30`.

(`af6c8ae` SNOBOL4 SBL-EXEC-4 and a `descr8-macro-funnel` branch landed from parallel sessions; my pushes
rebased onto them conflict-free — FACT-rule isolation held.)

## Gates (green + UNMOVED across all five commits)
Icon m2 **6/6 HARD** · Icon m3 **5/6** (only `if_expr` fork-blocked, unchanged) · SNOBOL4 m2 **7/7** ·
Prolog m2 **5/5** · regression gate **27/27** · no-stack **113** · one-reg-frame **20** · FACT **0**.
Each fix is Icon-gated or `rβ`/`cx.lang`-guarded; SNOBOL4/Prolog and bounded cases verified unchanged every time.

## Verified-correct (no fix needed)
div/mod sign conventions, real division, string relops (`<<` `>>` `~==` `<<=`), comparison chains, concat
coercion, real formatting, mixed int/real comparison, generator cross-products (`(1 to 2)*(3 to 4)` etc.),
compound `{}` blocks, nested `if`, `if`/`else` value forms, alternation-into-`write`, `every…do`,
`*(1 to 3)` (unary passes through the generator resume).

## OPEN BUGS found this session (root-caused, NOT fixed — for a fresh-budget session)

### 1. `if`-as-arithmetic-operand → empty
`(if C then E) + 1` yields nothing (e.g. `write((if 1<2 then 7) + 1)` → ∅, want `8`). `if`-as-value works
alone (`write(if 1<2 then 7)`→7) and `if…else` works; only composition into an operator breaks.
**Root cause:** `v_binop` forward-patches the IF *node's* `γ` (the deferred-operand patch
`if (!c1->γ) c1->γ = e2α`), but `v_if` already lowered the THEN/ELSE branches against the original `γ_in`
(NULL when the IF is an operand), so the branch leaf keeps `γ=NULL` and the chain dead-ends before `+1`/`write`
(BB dump: the "then" `LIT_I` has `γ=.`). **Fix direction:** route THEN/ELSE branch success through the IF
NODE as a single success funnel (jcon `ir_a_If` `p.ir.success` chunk model), so patching `IF.γ` propagates;
the `IR_IF` exec arm conflates condition-dispatch with branch-value and likely also needs care. `v_if` is
SHARED and the gated `if_expr` (statement form) passes — do not regress it. Same "continuation/resume
threading through a node" CLASS as the two fixes that DID land (`v_to` step, `v_assign` resume).

### 2. Relational filtering only works for `<bounded> > <generator-on-right>`
`every write(2 < (1 to 5))` → ∅ (want `3 4 5`); `every write(3 < (1 to 5))` → ∅; `every write((1 to 5) > 3)`
→ ∅ (generator on LEFT). But the GZ-6 shape works: `every write(3 > (1 to 5))` → `1 2`,
`every write(5 > (1 to 4))` → `1 2 3 4`. So relational backtracking is wired ONLY for the exact GZ-6 shape
(bounded left, generator right, `>`); **`<` and generator-on-left both fail.** Likely an asymmetry in the
`IR_BINOP` relational re-pump arm (`bb_exec.c`, the `r_gen`/`l_gen` logic) — it re-pumps the RIGHT operand but
not the LEFT, and/or the relop's fail→resume edge is only built for one operand order. Ground any fix in jcon
`ir_a_Binop` (the relop is generator-transparent in BOTH operands) before touching the shared arm.

## State / environment notes
- `origin/main` HEAD before session: `5645017` (3 commits past this GOAL file's old `81d721b` watermark —
  parallel Prolog PLG-3/4 + test-harness). After session + parallel interleave: `aabf060`.
- The comment-purge commit `a0bb9be4` (prior handoff) is **NOT** in `main`'s history — consistent with Lon's
  PIVOT backing it out; these sources still carry comments.
- `refs/` is **local-only** (not tracked) — populate from the uploaded `1-icon-master.zip` / `2-jcon-master.zip`
  into `SCRIP/refs/{icon-master,jcon-master}` at session start.
- Clone is a healthy full checkout on `/home/claude/SCRIP` (not the flaky FUSE mount).

## Recommended next steps
1. **Mode-2 (low-risk, high-value):** fix OPEN BUG #2 (relational filtering symmetry — both operand orders +
   `<`) then OPEN BUG #1 (`if`-as-value funnel). Both are the same threading class as this session's wins.
2. **Mode-3 (large, fork-gated):** GZ-7 `x := 42; write(x)` stackless — needs new no-stack runtime helpers
   (`rt_nv_set`/`rt_nv_get` returning to registers, replacing `rt_pop_nv_set`/`rt_nv_get`-push), `bb_assign`/
   `bb_var` rewritten to the `[r12+off]` one-register frame, `icn_ring_to_tree` taught `IR_ASSIGN` (arity 1),
   and `bb_call`'s var-arg slot read. Still gated on Lon's Path-1/Path-2 fork.
