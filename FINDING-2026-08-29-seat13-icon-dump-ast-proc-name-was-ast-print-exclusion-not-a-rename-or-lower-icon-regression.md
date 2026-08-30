# FINDING 2026-08-29 seat13 — TT_PROC_DECL's dropped name was a shared `ast_print.c` exclusion, not the task's suspected parser-dir rename or lower_icon churn; fix lands, icon/parser goes 0→123 of 153, and 4 unrelated pre-existing defect classes surface behind it

## Context
Row `icon-dump-ast-drops-tt-proc-decl-name` (rank 0), locked via THE LOOP `next`.

Two things in the task baton did not check out against the live tree, worth recording so nobody
re-chases them:
- **AUTHORITY** cited `FINDING-2026-08-29-hq_P-icon-dump-ast-drops-proc-name-invalidating-153-parser-fixtures.md`.
  It does not exist anywhere under `.github/` (checked by exact name and by `*icon-dump-ast*` /
  `*proc-decl-name*` globs). What *does* exist and covers the identical symptom two days earlier is
  `FINDING-2026-08-27-seat08-parser-fixture-ast-oracles-drifted-snocone-59of67-icon-153of153-plus-a-masking-set-e-bug.md`.
- **SUSPECTS** named "the parser-dir rename era (`src/parser` -> `src/frontend`, `cf2961`)". Neither
  half matches the live tree: `find src -maxdepth 1 -type d` shows `src/parsers/` (plural) — there is
  no `src/frontend/` anywhere — and `git show cf2961` reports "unknown revision", i.e. no such commit
  exists in this repo's history.

Also, apparent "declared tomorrow" timestamps (MODE file, this task's own mint line) are not an
inconsistency — this host's shell is CDT (UTC-5) while postoffice timestamps are UTC `Z`; both
describe the same moment.

## Root cause
`src/ir/ast_print.c` carries three identical guards (`flat_length`, and both branches of
`print_node`) that print a node's `v.sval` inline unless its kind is one of `{TT_QLIT, TT_CSET,
TT_CLAUSE, TT_SUB_DECL, TT_PROC_DECL, TT_REGEX_DECL, TT_AUGOP}`. `TT_PROC_DECL` was in that list. But
`src/parsers/icon/icon_parse.c:838` (`proc->v.sval = procname;`) stores the procedure's own interned
name in exactly that field, the same convention every other named node uses — so the exclusion
silently dropped it on every dump.

`git blame` traces the current line content to `479ae8890` (2026-07-05, "Prolog GROUND ZERO #6" — an
unrelated Prolog commit whose diff evidently swept this file along; the file's own lineage runs back
to the repo's `713c581b` "Initial commit"). There is no recent rename or lower_icon churn behind
this: the exclusion has read this way since at least July 5, roughly two months before anything
exercised it. What's actually new is the *measurement*, not the code — per seat08's Aug-27 finding,
`corpus/tests/icon/parser/` had **no runner at all** before that day, so a printer bug that (per a
corpus-wide sweep, below) has never matched any of this project's committed name-bearing `.ref`
files sat invisible until something finally graded it.

## Fix
Removed `&& e->t != TT_PROC_DECL` from all three guards in `src/ir/ast_print.c`. Pascal's parser
(`src/parsers/pascal/pascal.y:231`, `pascal.tab.c:303`) constructs `TT_PROC_DECL` the same way and
gets the same fix for free — verified: `corpus/tests/pascal/nestvar.pas` now prints `inner`/`outer`/
`main` where it silently dropped them before.

## Verification
- `alt_arith.icn` --dump-ast output is now byte-identical to its committed `.ref` (previously missing
  `main`).
- Independent sweep of all 153 `corpus/tests/icon/parser/*.icn`/`.ref` pairs (no gate script exists
  for this directory yet — seat08's finding already flagged that gap — so swept by hand, same
  technique seat08 used): **PASS=123, FAIL=30**, up from **PASS=0** before this fix.
- Corpus-wide regression check performed *before* touching anything: `grep -rlP '\(TT_PROC_DECL \('`
  (the buggy no-name shape) across every `.ref` under `corpus/` → **0 hits**; the name-bearing shape
  → **131 hits**. No committed oracle anywhere depended on the buggy shape, so this fix cannot
  regress anything already green.

## The 30 residual failures are NOT this defect — decomposed into 4 independent, pre-existing classes
1. **22 files** (`augop_add`, `_concat`, `_cset_diff`, `_cset_inter`, `_cset_union`, `_ge`, `_gt`,
   `_le`, `_lt`, `_mod`, `_ne`, `_numeq`, `_pow`, `_scan`, `_sge`, `_sgt`, `_sle`, `_slt`, `_sne`,
   `_str_concat`, `_streq`, `_sub`): every one of these `.ref` files is **genuinely 0 bytes** — never
   captured, not a shape mismatch. `TT_AUGOP` is (still, correctly, out of this row's scope) in the
   same `ast_print.c` exclusion list this row just trimmed.
2. **6 files** (`conj_two`, `conj_three`, `conj_stmts`, `conj_assign`, `conj_scan`,
   `seq_in_expr`): uniform `TT_CONJ` (actual) vs `TT_SEQ` (expected) node-kind mismatch on all 6 —
   looks like one wrong constant somewhere in Icon's sequence-expression construction.
3. **1 file** (`match_expr`): expects `TT_MATCH_UNARY`, compiler emits a desugared
   `TT_FNC(tab, TT_FNC(match, ...))` chain instead.
4. **1 file** (`special_notident`): expects `TT_NOT(TT_IDENTICAL ...)`, compiler emits
   `TT_NIDENTICAL(...)` directly.

None of these four touch `TT_PROC_DECL` — verified by direct diff per class, not inferred from
filename alone.

## Minted (new work, not this row's to fix)
- `icon-augop-parser-refs-empty` (rank 2)
- `icon-conj-vs-seq-node-mismatch` (rank 2)
- `icon-parser-residual-shape-diffs` (rank 2)

## Not done (deliberately, out of this row's scope)
- No `corpus/tests/icon/parser/` fixtures touched (seat02 holds `tests-consolidate-icon`; the task
  baton explicitly forbids it).
- No permanent gate script authored for `corpus/tests/icon/parser/` — seat08 already flagged that as
  real, separate work; not a byproduct of a single-defect compiler-regression row.
- The 4 residual defect classes above were not fixed — minted as separate rows instead.
