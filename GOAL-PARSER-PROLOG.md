# GOAL-PARSER-PROLOG.md — PARSER-PROLOG pattern-based frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-PROLOG.md` and `GOAL-PROLOG-IR-RUN.md`. The
existing Prolog frontend (`src/frontend/prolog/`) is the in-process oracle.

**Done when:** A Snocone program `parser_prolog.sc` reads Prolog source,
runs one `Compiland` PATTERN that builds the canonical IR tree, and for
every test program in the rung corpus
`tree_equal(existing_frontend_tree, parser_prolog_tree)` returns true.

---

## Cross-pollination

All six PARSER-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` plus the `nPush`/`nInc`/`nTop`/`nPop` counter helpers
from `corpus/programs/scrip/`. Bug fixes there benefit all six.

Prolog is the most syntactically distinct of the six — clauses (`head :-
body.`), facts (`fact.`), terms with arity. The Compiland spine is identical
across all PARSER-*.

---

## Naming policy — anchor on existing frontend

⛔ Non-terminal and token names in `parser_prolog.sc` MUST match the
existing Prolog frontend's vocabulary, not be invented.

- **Tokens** — from `src/frontend/prolog/prolog_lex.h`: `TK_ATOM`, `TK_VAR`,
  `TK_ANON`, `TK_INT`, `TK_FLOAT`, `TK_STRING`, `TK_LPAREN`, `TK_RPAREN`,
  `TK_LBRACKET`, `TK_RBRACKET`, `TK_PIPE`, `TK_COMMA`, `TK_DOT`, `TK_LBRACE`,
  `TK_RBRACE`, `TK_OP`, `TK_NECK`, `TK_QUERY`, `TK_CUT`, `TK_SEMI`.
- **Non-terminals** — from `src/frontend/prolog/prolog_parse.c`: `clause`,
  `term`, `primary`, `args`, `list`.
- **IR node tags** — from `prolog_lower.c::expr_dump`: `E_CHOICE`, `E_CLAUSE`,
  `E_UNIFY`, `E_CUT`, `E_FNC`, `E_QLIT`, `E_ILIT`, `E_FLIT`, `E_VAR`, `E_ADD`,
  `E_SUB`, `E_MUL`, `E_DIV`.

Cross-PARSER spine names (`Compiland`, `Push`/`Pop`/`Top`, `nPush`/`nInc`/
`nTop`/`nPop`) are the only invented names — shared across all six PARSER-*.

See GOAL-PARSER-SNOCONE.md "Naming & Design Principles" for the full writeup.

---

## Session Setup

```bash
( cd /home/claude/one4all && git fetch origin parser 2>/dev/null; git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_prolog.sh         # existing frontend baseline
bash /home/claude/one4all/scripts/test_parser_prolog.sh        # parser gate
```

---

## Architecture

```
scrip --parser-crosscheck parser_prolog.sc tiny.pl
```

SCRIP runs `parser_prolog.sc` (which `-include`s the shared SC library from
`corpus/programs/scrip/`) against `tiny.pl`. PAT produces IR tree t2 via
`Compiland`; the existing frontend produces t1. Compared in memory
(`tree_equal`), executed in memory.

**Shared SC library** (`corpus/programs/scrip/`):
```
tree.sc  stack.sc  counter.sc  ShiftReduce.sc  semantic.sc
```

Compiland spine (uses the counter helpers — `nPush` opens a counter frame,
`nInc` bumps the count, `nTop` reads it, `nPop` closes the frame):
```
Compiland = nPush() ARBNO(*Command) reduce('Parse', 'nTop()') nPop();
```

Prolog-specific: PAT-PR's `Command` reduces to a `Clause` node (fact or
rule); program tree is `(Parse (Clause ...) (Clause ...) ...)`.

---

## Style invariants (parser_prolog.sc)

- **No `goto`/labels** in the driver loop. Use `while`-style structured flow.
- **Names match the existing frontend** (see Naming policy above).
- **No invented non-terminals** — invented names reserved for cross-PARSER spine.

---

## Rung ladder

### PARSER-PR-0 — atom — **LANDED** (PASS=4)
Atoms, vars, ints, quoted strings followed by `.`.

### PARSER-PR-1 — facts — **LANDED** (PASS=11)
Bare facts and compound facts `f(a, b, c).`.

### PARSER-PR-2 — rules — **LANDED** (PASS=18)
Rules `head :- goal.` with single goal in body. Two-phase build
(`snapshot_head` + `mark_body` + `build_clause`); E_CHOICE/E_CLAUSE key
is head arity alone.

### PARSER-PR-3 — conjunction / disjunction (`,` / `;`) — **next**

- [ ] `Command` handles `a, b, c` and `a ; b` in goal position.
- **Sibling LANG rungs:** PR-10..PR-12.
- **Gate:** PASS≥24.

#### Oracle IR shapes (verified via `--dump-ir`)

| Source | IR shape |
|---|---|
| `foo :- a, b.` | `(E_CLAUSE foo/0 (E_FNC a) (E_FNC b))` — top-level `,` flattened |
| `foo :- a ; b.` | `(E_CLAUSE foo/0 (E_FNC ; (E_FNC a) (E_FNC b)))` — `;` wrapped, flat n-ary |
| `foo :- a, b ; c.` | `(E_CLAUSE foo/0 (E_FNC ; (E_FNC , (E_FNC a) (E_FNC b)) (E_FNC c)))` — nested `,` preserved |
| `foo :- a ; b ; c.` | `(E_CLAUSE foo/0 (E_FNC ; (E_FNC a) (E_FNC b) (E_FNC c)))` — flat n-ary `;` |
| `foo :- a, b, c, d.` | `(E_CLAUSE foo/0 (E_FNC a) (E_FNC b) (E_FNC c) (E_FNC d))` |

Three flattening rules (match prolog_parse.c::flatten_conj and
prolog_lower.c right-spine flattening):
1. **Top-level `,` in body**: flattened away into separate E_CLAUSE children.
2. **Inner `,` (nested in `;` or non-top)**: preserved as flat n-ary `(E_FNC ,)`.
3. **`;` always**: preserved as flat n-ary `(E_FNC ;)`.

Precedence: `,` (1000) tighter than `;` (1100). Grammar:
```
body := disj
disj := conj (';' ws_opt conj)*
conj := simple_goal (',' ws_opt simple_goal)*
simple_goal := tk_atom '(' args ')'  |  tk_atom
```

#### Test fixtures committed

`conj_two.pl`, `conj_three.pl`, `disj_two.pl`, `disj_three.pl`,
`conj_in_disj.pl`, `disj_compound.pl` in `corpus/programs/prolog/parser/`.
All have verified oracle output.

#### Critical Snocone gotchas (sessions ending 2026-05-03)

⚠️ **`*func()` immediate evaluations inside ARBNO arms only fire on the
FIRST iteration in `--ir-run` mode.** Verified empirically:
`ARBNO( ws_opt tk_comma ws_opt simple_goal . *inc_body_count() )` — the
ARBNO correctly iterates and `simple_goal` pushes goals to the stack on
every iteration, but `*inc_body_count()` only fires once. The cursor
advances correctly (so the ARBNO loops), but the standalone post-match
side effect is skipped.

This rules out the accumulator-counter pattern that works fine outside
ARBNO. **The fix is to use the cross-PARSER spine's `nPush`/`nInc`/`nTop`/
`nPop` counter helpers** — these are designed specifically for "count what
I just pushed" inside ARBNO, used in `Compiland` itself. The mechanism is
already available; PR-3 just needs to use it. See how `Compiland` uses
`nPush()` / `ARBNO(nInc() ...)` / `reduce('...', 'nTop()')` / `nPop()`:
that is the canonical "count goals in ARBNO and read the count after"
pattern, and the answer for PR-3 conj/disj building.

⚠️ **`if (var)` where `var = 0` is TRUTHY in Snocone** — integer `0`
converts to string `"0"` which is non-null. Use `if (GT(var, 0))` or
`if (IDENT(var, 1))` for explicit comparisons. The `body_present`
flag used `if (body_present)` which silently appended a phantom child
on facts. Fixed via `if (GT(body_present, 0))` in `build_clause`.

⚠️ **Snocone boolean AND in `if (...)` is juxtaposition**, NOT `&` or `&&`.
Use `if (IDENT(t(x), 'E_FNC') IDENT(v(x), ','))`.

⚠️ **Pop() with no parameter** returns the popped value (function return).
`g = Pop()` works as expected. But calling `Pop()` from inside a
`*func()` immediate evaluation in an ARBNO arm runs into the same
"only fires once" problem above.

#### Recommended PR-3 strategy for next session

1. **Use `nPush`/`nInc`/`nTop`/`nPop` counter helpers** — same mechanism
   as `Compiland`. Open a frame for the body before the first `simple_goal`,
   `nInc()` per goal (placed where `simple_goal` is in the spine, NOT as
   a `*func()` after it), `nTop()` to read the count, `nPop()` to close.
   This is the documented spine pattern and avoids the ARBNO-`*func()` bug.
2. **Validate after each `str_replace`** with
   `bash /home/claude/one4all/scripts/test_parser_prolog.sh | tail -3` —
   PR-2 baseline must remain PASS=18 throughout.
3. **`build_clause` already has correct flatten logic** for top-level
   `(E_FNC ,)` — the upgrade landed cleanly during the 2026-05-03 session.
   Re-apply it (was reverted with rest of file). The `if (GT(body_present,
   0))` fix needs re-applying too.
4. **Add `disj` after `conj` works** — same nPush/nInc/nTop/nPop pattern,
   building `(E_FNC ;)` instead of `(E_FNC ,)`.
5. **Defer parenthesized body subterms** (`(a, b) ; c`), nested compound
   args, anon vars, arithmetic to later rungs.

### PARSER-PR-4 — lists (`[H|T]` / `[a,b,c]`)
Gate: PASS≥30.

### PARSER-PR-5 — arithmetic (`is`, builtin operators)
Gate: PASS≥38.

### PARSER-PR-6 — queries / directives
Gate: PASS≥45.

---

## Invariants

- Prolog's LANG ladder is at PR-17 active; PAT-PR does not race ahead.
- Test programs in `corpus/programs/prolog/parser/` are owned by PAT-PR.
- `.ref` files captured at rung-land time.
- Variables vs atoms distinction is first-class in the token classifier.

---

## Watermark

PARSER-PR-2 LANDED (PASS=18). PARSER-PR-3 attempted twice (sessions
ending 2026-05-03 — two emergency handoffs). On-disk and remote state
is clean PR-2; nothing partial pushed. Six PR-3 fixtures committed with
verified oracle output.

**Next session:** re-attempt PARSER-PR-3 using the `nPush`/`nInc`/`nTop`/
`nPop` counter helpers (the canonical spine mechanism for this pattern).
