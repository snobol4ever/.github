# HANDOFF 2026-06-03 (Opus 4.8) — Prolog-BB: recursive if-then-else normalization (nested ITE + bare arrow)

## TL;DR
Implementation session. Fixed the **two independent WAM-CP-9 bugs** the prior scoping
handoff (`HANDOFF-2026-06-03-OPUS48-PROLOG-BB-WAM-CP-9-ITE-COMMIT-SCOPED.md`) flagged as
"bonus bugs found while probing" — the **m4 nested-ITE-with-call link gap** and the
**m2 ITE-bare-call no-output** bug. They turned out to be **ONE parse-tree root cause**, fixed
by a single Prolog-parser-only change. SCRIP HEAD `bfabff3` (rebased over peer SNOBOL4 concat
`047dded`). New corpus rung `rung41_ite_nested_ite` (corpus `ebb8c21`). All gates green.

**GATE-3: m2 112/112 · m3 112/112 byte-identical · m4 86→87 / 0 / 25.**

**NOT touched:** the genuinely-open WAM-CP-9 piece — the **m2-oracle-WRONG ITE-commit
*semantics*** (`( a(X),X>=2 -> true ; X=0 )` gives m2 `2 3 0`, m4-correct `2`). That needs
Lon's design sign-off (shared-`lower.c` port wiring, risks byte-identity). This session was
strictly the parser-side `( ->; )`→`TT_IF` desugaring, which is orthogonal to the commit
semantics.

## Root cause
`src/parser/prolog/prolog_lower.c` `pl_maybe_ifthenelse` only rewrote `( Cond -> Then ; Else )`
into a `TT_IF` AST node when the `;` was a **top-level clause-body goal** (the call site looped
over `body_prog->c[i]` and only rewrote direct `;` children). Two shapes were therefore never
converted:
1. A `->` **nested inside a conjunction or disjunction branch** — e.g. the inner
   `( a(X) -> true ; fail )` in `main :- ( ( a(X) -> true ; fail ), write(X), nl, fail ; true ).`
2. A **standalone `( Cond -> Then )`** with no else — e.g. `main :- ( a(X) -> write(X), nl ).`

In both cases the `->`/`;` node fell through `lower_goal` to the generic `IR_GOAL` arm, which
emitted a **call to a predicate with an empty name** → label `.Lplpred____2` (empty name,
arity 2) that the emitter **never defined**. Result: m4 `ld` failure
(`undefined reference to .Lplpred____2` / `_redo`), and m2 produced no output (the bogus call
silently failed).

Confirmed by BB dumps: the working top-level form lowered to `IR_ITE`; the nested/bare forms
lowered to `IR_DISJ` / a bare `IR_GOAL` chain with no `IR_ITE` node at all.

## The fix (SCRIP `bfabff3`, one file: `src/parser/prolog/prolog_lower.c`, +52/-19)
Replaced `pl_maybe_ifthenelse` with a recursive `pl_rewrite_control(tree_t*)` + 3 small
helpers, and applied it to **every** body goal (not just top-level `;` goals):
- `pl_is_arrow` — predicate for a `->` `TT_FNC` node (n≥2).
- `pl_arrow_then_prog` — gathers the **full** then-conjunction `arrow->c[1..]` (the old code
  took only `arrow->c[1]`, a latent then-arm truncation for `( a -> b, c ; d )`), recursing.
- `pl_disj_of_rest` — builds the else from the remaining `;` arms, so a chained
  `( C1->T1 ; C2->T2 ; E )` nests correctly (ISO right-assoc: else = `( C2->T2 ; E )`).
- `pl_rewrite_control` — three cases: (a) standalone `->` → `TT_IF` with implicit `fail` else;
  (b) `;` whose first child is `->` → `TT_IF` with `pl_disj_of_rest` as else; (c) plain `;`/`,`
  → recurse into all children. Mirrors gprolog `Pl2Wam/syn_sugar.pl` `normalize_cuts1`
  (`(IfThen ; R)` and `(P -> Q)` clauses) and swipl `pl-comp.c` `compileBody`'s control
  recursion.

C-style verified: no line >200 chars, zero blank lines, only the 200-char `/*---*/` separator.
The now-dead `pl_maybe_ifthenelse` wrapper was deleted (zero-dead-code rule).

## Canonical grounding (uploaded sources)
- gprolog `4-gprolog-master.zip` → `src/Pl2Wam/syn_sugar.pl` `normalize_cuts1`:
  `(IfThen ; R)` with `IfThen = (P -> Q)` desugars to
  `'$get_cut_level'(V), P, '$cut'(V), Q ; R` — recursive over `P`, `Q`, `R`; and the if-part is
  opaque (`normalize_cuts_in_if`). Standalone `(P -> Q)` desugars to `..., P, '$cut'(V), Q`.
- swipl `5-swipl-devel-master.zip` → `src/pl-comp.c` `compileBody` lines ~2312-2326:
  `A -> B ; C` emits `C_IFTHENELSE` + local cut on the condition ("Cut locally in the
  condition"). [This is the *semantics* layer = the still-open WAM-CP-9 piece; this session
  only consumed it for the recursion-shape confirmation, not the local-cut.]

## Verification
Reproducers (all now m2==m3==m4):
- `( ( a(X) -> true ; fail ), write(X), nl, fail ; true )` → `1` (was: m2 empty, m4 link-fail)
- `( a(X) -> write(X), nl )` (bare, no else) → `1` (was: m2 empty, m4 link-fail)
- `( fail -> write(t) ; write(e) )` → `e`
- `( fail->a ; fail->b ; c )` → `c`
Regressions held: bare top-level ITE `1`; disjunction-of-calls `1 2 3`.

New corpus rung `rung41_ite_nested_ite` (`.pl` + `.expected` + `.s`): all four shapes in one
program, output `1 1 e c`, identical across interp/run/compile. The committed `.s` assembles,
links against `libscrip_rt.so`, and runs to `1 1 e c`.

Gate sweep (final, post-rebase):
- GATE-1 smoke: m2 5/5, m3 4/5 (known unify harness artifact), m4 5/5.
- GATE-3 rung suite: **m2 112/112 · m3 112/112 · m4 87/0/25** (was 111/111/86-0-25).
- PL-HY-FENCE PASS; pl-value-stack PASS; `seg_byte`/`SL_B` 0; `g_vstack` 0.
- Siblings: Icon m2 12/12, SNOBOL4 m2 7/7.
- FACT-RULE NO-VALUE-STACK block md5 `cba1c10d…` byte-identical across PROLOG/SNOBOL4/ICON.

## Why m2/m3 byte-identity is safe
The change is **parser-side AST desugaring in `prolog_lower.c`** — it produces a `TT_IF` node
that the existing, unchanged `g_ite` lowerer + `IR_ITE` interpreter/emitter already handle
(top-level ITE has worked for many rungs). It is Prolog-only and touches no shared `lower.c`,
no emitter template, no runtime. The 112/112 byte-identity is the proof.

## Concurrency note
SCRIP push was rejected once (peer landed SNOBOL4 mode-4 concat `047dded`, a `lower.c`
value-side change). `git pull --rebase` applied cleanly with **zero conflicts** (disjoint
files); rebuilt + re-ran all gates green before pushing `bfabff3`. Corpus pushed `ebb8c21`.

## What changed on disk
- **SCRIP** `bfabff3`: `src/parser/prolog/prolog_lower.c` only.
- **corpus** `ebb8c21`: `programs/prolog/rung41_ite_nested_ite.{pl,expected,s}` (3 new files).
  Pre-existing `.s` drift on the other 110 rungs (emitter got leaner between when they were
  committed and now — same drift the HY-LADDER-AUDIT handoff identified) was **reverted**, not
  folded in — it belongs to whoever lands the emitter change that caused it.
- **.github**: `GOAL-PROLOG-BB.md` (STATE line, WAM-CP-9 ladder item annotated, gate-table
  caption + rows) + this handoff. FACT-RULE blocks untouched (verified byte-identical).

## NEXT (unblocked) vs (needs Lon)
**Unblocked forward engineering:**
- **WAM-CP-11** — deep-backtracking arg restore (`saved_args`) + nested choices.
- **WAM-CP-12** — determinism detection → CP elision (lower-time).
- **PL-INDEX-L2-1** — Level-2 hash dispatch for first-arg indexing (>8 clauses).

**Needs Lon's design sign-off:**
- **WAM-CP-9 (rest) ITE-commit semantics** — the m2-oracle-WRONG case. Now isolated cleanly:
  the parser desugaring is done, so the remaining work is purely the local-cut barrier on the
  ITE condition in shared `lower.c` `IR_ITE` arm + m2 port wiring + m4 emit, with a re-baseline
  audit (some rungs may PASS *because* they match the buggy m2). Risks the now-112/112
  byte-identity gate.
- **PL-HY-1c** design (`g_pl_flat_chain` lowerer prereq); reclassify PL-HY-2/3/4/5.

m4 87→ further remains gated on a runtime substrate for the 25 EXCISED rungs (findall /
retract / abolish / assertz / aggregate / catch-throw / dcg_generate / float-unify) —
PLG-9g / PLG-10 / WAM-CP-13.

## Build / verify recipe
```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh            # GATE-1 m2 5/5
bash scripts/test_prolog_rung_suite.sh       # GATE-3 m2 112/112, m3 112/112, m4 87/0/25
bash scripts/test_gate_bb_one_box.sh         # PL-HY-FENCE PASS
# reproduce the (now-fixed) bugs:
printf ':- initialization(main).\na(1). a(2). a(3).\nmain :- ( ( a(X) -> true ; fail ), write(X), nl, fail ; true ).\n' > /tmp/nite.pl
./scrip --interp /tmp/nite.pl </dev/null                                   # 1
bash scripts/run_prolog_via_x86_backend.sh "$(realpath /tmp/nite.pl)" </dev/null   # 1
```
