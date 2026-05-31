# HANDOFF — LANG-INDEP-RENAME Slice 3 (Prolog)

**Date:** 2026-05-30 · **Author:** Claude Opus 4.8 · **Goal:** `GOAL-LANG-INDEPENDENT-RENAME.md`
**Repos:** SCRIP `42886970` (pushed) · .github (this commit)

---

## What shipped (both green, both pushed)

- **Slice 3a — Prolog BB box layer** (`ddfc8f81`). 13 box templates `git mv` + functions + `*_state_t`
  + `*_str` + g_emit scratch fields + 7 enums. `bb_pl_*→cultural` (collisions `bb_disj/bb_conj/bb_goal/
  bb_logicvar`; free strip the other 8). `BB_PL_*→BB_{GOAL,LOGICVAR,STRUCT,DISJ,GCONJ,ITE,CATCH}`. Makefile
  RT_PIC_SRCS + scrip recipe paths/.o. No `#include` churn (templates are standalone TUs).
- **Slice 3b — Prolog runtime symbols** (`42886970`). `pl_→resolve_` for **174 post-AST-INTERNAL**
  identifiers (`pl_*→resolve_*`, `Pl_*→Resolve_*`, `PL_*→RESOLVE_*`, `g_pl_*→g_resolve_*`). Files
  `lower_pl.{c,h}→lower_clause.{c,h}`, `pl_runtime.{c,h}→resolve_runtime.{c,h}`.

**Gate after each commit:** `make scrip` rc=0 · `make libscrip_rt` rc=0 · **Icon m2 6/6 (HARD)** ·
sm_dead 1/1 · FACT 0. Baseline held exactly.

---

## The one real decision (VETOABLE) — `BB_PL_SEQ → BB_GCONJ`

The goal flagged "investigate the enum collision before renaming." Done. `BB_CONJ` (BB.h:42) is **Icon's**
`&`-evaluation conjunction (built in `lower_graph.c`, run by `bb_exec.c case BB_CONJ`); Prolog's `BB_PL_SEQ`
is a **different** executor (clause-body `,`). Genuine two-executor clash → two names required. I kept
Icon's bare `BB_CONJ` (didn't reopen Icon → protected its gate) and gave Prolog **`BB_GCONJ`** ("goal
conjunction"), box fn `bb_conj`. The already-bare `BB_CHOICE/UNIFY/CUT/BUILTIN/ATOM/ARITH` were Prolog's
own, de-prefixed earlier — no clash. **To flip:** rename Icon's `BB_CONJ→BB_EVAL_CONJ` (3 files) and let
Prolog take bare `BB_CONJ`. Say the word. (Full rationale in the goal file's VETOABLE DECISION callout.)

---

## What's deferred (precisely scoped)

- **Slice 3c — 29 Prolog cross-boundary symbols** (exempted in 3b to keep the commit green). They split:
  - **(a) frontend-DEFINED → leave as-is (correct):** the Prolog parser/builtin API — `prolog_atom*`,
    `prolog_parse`, `prolog_compile`, `prolog_driver`, `prolog_builtin`, `prolog_atom_name`, and the
    Prolog-builtin impls (`pl_write*`, `pl_univ`, `pl_functor`, `pl_arg`, `pl_term_to_string`) IF their
    def-site is `prolog_builtin.c`.
  - **(b) post-AST-DEFINED but frontend-USED → SHOULD rename + fix frontend bridge:** `pl_box_*`,
    `g_pl_trail`, `g_pl_cut_flag`, `pl_env_new`, `pl_pred_table_lookup_global`,
    `pl_unified_term_from_expr`, `pl_assert_term`, `pl_throw_existence_error_procedure`. Bridge call sites:
    `prolog_lower.c`, `prolog_driver.c`, `pl_broker.{c,h}`, `pl_interp.h`.
  - My def-site heuristic was ambiguous (regex couldn't cleanly separate def from call) — do a careful
    per-symbol pass: a *definition* is a function body / `typedef` / non-`extern` global, NOT a call or a
    header `extern` decl. Use `grep -oh` (multi-file `grep -o` prefixes `filename:` and breaks set math).
  - Also `SM_BB_PL_INVOKE` (SM.h) — vestigial SMX-4-excised opcode still carrying `PL`; fold/rename when
    the SM execution surface is finally driven from 1 → 0.
- **Slice 4 — Raku** (`raku_`/`rk_` + ~300 syms). Peek `raku_builtins*` and name by feature before mv.
- **Slice 5 — backend output libs** (`.il/.j/.wat/.cs/.java/.js`, `Sno*`). Off the live X86 path. The
  Prolog `.js`/`.wat` libs (`sno_runtime.js`, `prolog_runtime.wat`) still hold `pl_*`/`PL_*` — that's
  Slice 5, not a 3b miss (my sed targeted only `*.c/*.h/*.cpp`).

---

## Mechanics that worked / gotchas confirmed

- **Dispatch is `switch(enum)→fn`**, so enum names and box-fn names are independent. Box/enum spelling skew
  is already normal (`bb_pl_choice`↔`BB_CHOICE`). The `emit_core.c:844` range check `k>=BB_CHOICE &&
  k<=BB_PL_CALL` survives a pure rename (auto-updated to `<=BB_GOAL`; values unchanged — never reorder).
- **Do NOT blanket `s/pl_/resolve_/`** — `pl_` sits mid-word (`bb_pl_*`, and `\bpl_` won't even match after
  `_`). 3b used an **explicit per-identifier `\bsym\b` sed program** generated from the audited universe,
  longest-first, applied via `sed -f` to every post-AST `*.c/*.h/*.cpp` **unconditionally** (binary-safe vs
  the α/β/γ/ω files — no `grep -I` skip risk). Sets at `/tmp/b_all.txt` (203), `/tmp/b_xbound.txt` (29),
  `/tmp/b_rename.txt` (174), `/tmp/b_sed.sed` (174 rules). (These are in /tmp — regenerate if the box is
  recycled: see the goal file for the exact `grep -arhoE` patterns.)
- **Safe-subset rule for cross-boundary:** the rename set = (post-AST universe − frontend-appearing set), so
  every renamed symbol is provably absent from frontend → renaming it in post-AST cannot break frontend.
  Exempting the intersection is always link-safe regardless of def-site; it only postpones completeness.

## Next concrete step
Slice 3c (b)-set first (the genuine post-AST broker/interp bridge — that's the real remaining
de-prefixing); then Raku (Slice 4). Gate + commit + push (code repo first, .github last) after each.
