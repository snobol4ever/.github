# HANDOFF 2026-05-28 — Opus 4.7 — PROLOG LOWER: one-function-per-node PIVOT

**Goal:** GOAL-PROLOG-BB.md — structural refactor (Lon-directed PIVOT). Migrate
`lower_pl.c` from a single ~460-line `lower_pl_goal` mega-switch to the Icon
one-function-per-node style (`lower_icn.c`'s `lower_icn_new_*_ag` builders,
which themselves transcribe JCON `irgen.icn`'s `ir()`-dispatches-to-`ir_a_*`
shape). Behavior-neutral throughout — every commit byte-identical graphs.

## Why this pivot (Lon's call, 2026-05-28)

Lon preferred Icon's named per-node builders over Prolog's mega-switch. Agreed,
and it's structural not cosmetic:
- The port contract `(cfg, e, γ_in, ω_in, &α_out, &β_out)` is invisible when
  buried in 460 lines of `if (strcmp(fn,...))`; named builders force each node
  to declare its α/β/γ/ω wiring. That's where β-wiring bugs hide.
- Aligns the Prolog sister file with Icon so a fix proven in
  `lower_icn_new_Alt_ag` can be lifted mechanically.
- **`lower_pl_new_Call` is now the clean home for CAT-A-3's β-resume work** —
  the real motivation. Fix backtracking in the node that owns it, not at line
  240 of a switch.

## Landed this session (2 commits, both at full watermark)

`7119e41d` — Alt / Ite / Unify / Compare:
- `lower_pl_new_Alt`   (disjunction `;`)   ← twin of `lower_icn_new_Alt_ag`
- `lower_pl_new_Ite`   (if-then-else)        ← twin of `lower_icn_new_If_ag`
- `lower_pl_new_Unify` (`=`)
- `lower_pl_new_Compare` (`>,<,>=,<=,=:=,=\=`)

`4e555954` — Conj / Call:
- `lower_pl_new_Conj` (conjunction `,` → BB_PL_SEQ) ← twin of
  `lower_icn_new_Conjunction_ag`. Back-to-front γ/ω threading + resumable-β
  table + `bb_pl_seq_state_t` publishing.
- `lower_pl_new_Call` (0-arity atom-goal + general N-ary, unified → BB_PL_CALL)
  ← twin of `ir_a_Call` / `bb_pl_call.cpp`. Added a forward decl for
  `flatten_comma` so Conj can call it before its definition.

Trivial leaves (cut, true/fail/nl atom-goals) stay inline — Icon keeps trivial
leaves inline too; not worth a function.

## Gate ledger (held at watermark across BOTH commits)

| Gate | Count |
|---|---|
| GATE-1 smoke | 5/5 |
| GATE-2 crosscheck | 132/0 (5 ORACLE_MISS) |
| GATE-3 mode-2 | 91/107 |
| GATE-4 mode-4 minimal | 4/4 |
| Full mode-4 corpus | 28/107 |
| FACT RULE grep | 0 |
| Sibling smokes | icon 5/5, snocone 5/5, raku 5/5, rebus 4/4 |

one4all HEAD (pushed): `4e555954` (rebased onto upstream `6f41527f`). Prior: `58142007`.

## NEXT — the one remaining piece: `lower_pl_new_Builtin`

Everything genuinely control/relational/structural is now a named builder. What
remains inline in `lower_pl_goal` is the **builtin family** — ~12 arms, banners
"builtins: write…" through "findall/3":

- write / writeln / nl / is / `==` / `\==` / `@<` etc.   (BB_BUILTIN, α/β operands)
- type-tests: var/nonvar/atom/atomic/number/integer/float/compound/callable/is_list/ground (1-arg)
- term-construction: functor/3, arg/3, `=..`/2, atom_length/2, atom_concat/3,
  atom_chars/2, atom_codes/2, upcase_atom/2, downcase_atom/2, term_to_atom/2,
  term_string/2, atom_number/2  (ALL args on nd->α γ-chain)
- DCG phrase/2,3  (rewrites to a direct NT call — NOT a plain builtin; keep its
  own arm or a `lower_pl_new_Phrase`)
- sort/2, msort/2, format/1,2, numbervars/3, writeq/1, write_canonical/1,
  print/1, retract/1, retractall/1, abolish/1  (args on nd->α γ-chain)
- findall/3  (lowers Goal into its OWN self-contained BB graph — special, keep
  separate arm or `lower_pl_new_Findall`)

**Recommended shape** (improves on Icon — Icon has no such builtin repetition):
collapse the ~10 "args-on-α-γ-chain" arms into ONE table-driven
`lower_pl_new_Builtin(cfg, fn, e, γ_in, ω_in, &α_out, &β_out)` reading a small
static functor table `{ name, arity-or-(-1), arg-wiring-style }`. Three
arg-wiring styles seen in the current code:
  1. α/β operands (write/is/compare-likes — 1 or 2 args on nd->α / nd->β)
  2. all-args-on-nd->α-γ-chain (functor/arg/=../sort/format/numbervars/…)
  3. 1-arg type-test (var/atom/…)
Keep phrase/2,3 and findall/3 as their OWN named builders (they're not plain
builtins — phrase rewrites to a call, findall builds a sub-graph).

**This piece is detail-sensitive** — each family has slightly different
arg-wiring (which args land on α vs the γ-chain, whether ival carries arity).
That's exactly why it was deferred to a fresh context rather than rushed at the
end of this session. Verify per-family against the corpus, not just the gate
totals (a mis-wired arg can keep the count at 91 while silently breaking a
specific rung's output).

## Verification protocol (run after EACH extraction — proven this session)

```
bash scripts/build_scrip.sh
bash scripts/test_prolog_rung_suite.sh   | tail -1   # GATE-3 → 91/107
bash scripts/test_prolog_mode4_rung.sh   | tail -1   # GATE-4 → 4/4
bash scripts/test_crosscheck_prolog.sh   | tail -3   # GATE-2 → 132/0
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob' src/ \
  | grep -vE '_templates/|emit_core' | wc -l                # FACT RULE → 0
# sibling smokes: icon/snocone/raku/rebus → 5/5/5/4
```
For the builtin collapse specifically, ALSO diff actual rung outputs (not just
counts) for the affected predicates before/after, since arg-mis-wiring is
count-invisible.

## Setup (this session, reproducible)

```
bash scripts/install_system_packages.sh   # libgc-dev etc — REQUIRED, build fails without gc/gc.h
bash scripts/build_scrip.sh
make libscrip_rt                           # REQUIRED for mode-4 x86 runner
```

## After the builtin collapse — back to CAT-A-3

With `lower_pl_new_Call` clean, CAT-A-3 Steps B–D (the mode-4 backtracking
unlock, +15–25 corpus) have their proper home. See
HANDOFF-2026-05-27-OPUS-PROLOG-BB-CAT-A3-STEPA.md for that design (always-r12
resume-buffer recommended; JCON study confirmed cursor-in-caller-allocated-state
is the right shape — JCON's MoveLabel/IndirectGoto `t` adapted to a call/return
ABI).
