# GOAL-PARSER-REBUS.md — PARSER-REBUS pattern frontend in Snocone

**Repo:** corpus+one4all
**Branch:** `parser` (one4all only — `corpus` and `.github` stay on `main`)
**Sibling ladder:** `GOAL-LANG-REBUS.md`. The existing Rebus frontend
(`src/frontend/rebus/`) is the in-process oracle.

**Done when:** A Snocone program `parser_rebus.sc` reads Rebus source,
runs **one** `Compiland` PATTERN that builds the canonical IR tree on
the shared shift-reduce stack, and for every test program in the rung
corpus `tree_equal(existing_frontend_tree, parser_rebus_tree)` returns
true. Where a `.ref` file exists, executing both trees through the IR
interpreter produces byte-identical output.

⛔ **The deliverable is a PATTERN, not a procedure.** See `## Rubric`
below before writing any code. A line-at-a-time goto-driven state
machine — even one that emits the right tree shapes — is the wrong
deliverable and does not advance any rung.

---

## Status — session #62 attempt was REWORK, not landed

Sessions #62 (Claude Sonnet 4.7, 2026-05-03) wrote `parser_rebus.sc`
as a goto-driven line-at-a-time state machine that achieved tree
equivalence with the existing Rebus frontend on PASS=38 fixtures.

That code is the **wrong shape**. It does not use `Compiland`/`Command`/
`shift`/`reduce`/`nPush`/`nInc`/`nTop`/`nPop` — the canonical SNOBOL4-
family pattern spine the rest of this goal file specifies. The PASS=38
gate flagged tree equivalence but did not flag architectural shape;
that is a hole in the gate, not a clearance.

All seven rungs (RB-0..RB-6) are **REOPENED for rewrite as patterns**.
The 38 fixtures in `corpus/programs/rebus/parser/` are kept verbatim —
they are correct as gate input — but `parser_rebus.sc` itself is to be
rewritten from scratch following the model of `parser_snocone.sc`.

The rewrite does NOT have to be done all at once. The rung structure
below stages it: each rewritten rung lands when its pattern subtree
clears its fixture subset using the shift-reduce idiom.

---

## Rubric — what makes this a pattern parser

Before writing any `.sc` code, confirm every item below. If any
answer is "no", stop and rework.

1. **One root pattern.** The driver does at most: read stdin into
   `Src`, then `Src ? Compiland`. That single match performs the
   entire parse. (The driver may then walk the tree on the stack
   to call `TDump` per top-level child — that is emission, not
   parsing, and is allowed.)

2. **`Compiland` has the canonical spine.** Literally:
   ```
   Compiland = nPush() ARBNO(*Command) reduce("'Parse'", 'nTop()') nPop();
   ```
   `Command` is one big alternation of sub-patterns, one per
   recognized construct.

3. **No goto/label inside parsing patterns or their helpers.**
   Snocone control flow is via patterns and structured
   if/while only. The single legacy exception (the `read_loop`/
   `read_done` stdin-slurp at the top of the driver) is the only
   place `goto` may appear, and it must come AFTER the parse, not
   inside it. (Note: even SN's driver uses while-loop form for
   stdin slurp; new code should too.)

4. **Tree construction is via `shift()` and `reduce()` only.** Never
   call `Push(Tree(...))` from a pattern escape. `shift(p, t)` pushes
   a leaf of type `t` from what `p` matched; `reduce(t, n)` folds the
   top `n` stack entries into a t-node.

5. **No per-line state machine.** No `_rb_state = 0/1` toggle. No
   per-construct `_rb_*_kind` / `_rb_*_txt` global slots feeding hand-
   built `Tree(...)` calls in helper functions. Per-construct binding
   happens via shift's third parameter and reduce's child-count.

6. **Counter helpers (`nPush`/`nInc`/`nTop`/`nPop`) appear at every
   variadic-fold site.** `ARBNO(*X)` rungs that build a list use
   `nPush()` before, `nInc()` inside the body, `reduce(t, 'nTop()')`
   after, then `nPop()`. This is how the parser knows how many items
   to fold. Hard-coded child counts (e.g. `reduce(r_ALT, 2)`) are fine
   only for fixed-arity productions.

7. **Sub-pattern names mirror `rebus.y`.** Use `function_decl`,
   `record_decl`, `pat_expr`, `expr`, `alt_expr`, etc. — the
   non-terminal names from `src/frontend/rebus/rebus.y`. Where a name
   conflicts with Snocone reserved syntax, suffix with `_pat`. Do not
   invent names like `MatchLine` / `BodyAltLine` / `IfLine` — those
   are line-fragments, not grammar non-terminals.

8. **One alternation in `Command` covers all top-level constructs.**
   In Rebus that is `function_decl | record_decl`. Statement-level
   forms (assign, match, alt, if, while, call, atom) live under a
   `stmt`-rooted sub-tree fired by `function_decl`'s body, not as
   peers of `function_decl`.

A grep that should produce zero hits in the rewritten parser:
```
grep -nE 'goto |^[a-z_]+:|_rb_state|_rb_atom_kind|emit_[a-z]' parser_rebus.sc
```
(Hits in commented-out scaffolding are fine; hits in active code are
the wrong shape.)

---

## Reference — `parser_snocone.sc` as the model

Read `corpus/programs/scrip/parser_snocone.sc` end-to-end before
starting. It is the closest sibling: same shared SC blob, same
`Compiland`/`Command` spine, hand-rolled expression-precedence ladder
(`Expr17` atoms → `Expr9` mul/div → `Expr6` add/sub → `Expr4` concat
→ `Expr3` alt → ...), and same shift/reduce idiom. Rebus's ladder
is shorter (no concat operator at this stage; alternation is at
statement level, not expression level — see `rebus.y`) but the
overall shape is identical.

Counter-helper hits per parser, for orientation (Rebus is the outlier):

| Parser | nPush/nInc/nTop/nPop hits |
|---|---|
| parser_snocone.sc | 9 |
| parser_snobol4.sc | 8 |
| parser_icon.sc | 5 |
| parser_prolog.sc | 4 |
| parser_raku.sc | 4 |
| **parser_rebus.sc (current, wrong shape)** | **0** |
| **parser_rebus.sc (target)** | **8+** |

---

## Cross-pollination

All six PARSER-* parsers share `Compiland`/`Shift`/`Reduce`/`Push`/`Pop`/`Top`/
`tree`/`TDump`/`stack` from `corpus/programs/snocone/demo/beauty/`. Bug
fixes there benefit all six. Rebus shares lowering with SNOBOL4, so PAT-RB's
`expr ? pat` and `expr | expr` lift directly from PARSER-SN. The existing
Rebus frontend is younger than SNOBOL4's; PAT-RB does not silently match
divergences — report upstream.

Naming follows the canonical writeup in `GOAL-PARSER-SNOCONE.md` (use BNF
names, `beauty.sc` names, `shift()`/`reduce()` over manual `Push(Tree(...))`,
no new labels/goto).

---

## Session Setup

```bash
( cd /home/claude/one4all && git fetch origin parser 2>/dev/null; \
  git checkout parser 2>/dev/null || git checkout -b parser origin/parser 2>/dev/null || git checkout -b parser )

bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
```

Gate after setup:
```bash
bash /home/claude/one4all/scripts/test_smoke_rebus.sh     # existing frontend baseline
bash /home/claude/one4all/scripts/test_parser_rebus.sh    # PAT-RB
```

---

## Architecture reminder

```
scrip --parser-crosscheck parser_rebus.sc tiny.reb
```

SCRIP runs `parser_rebus.sc` (which `-include`s the shared SC library from
`corpus/programs/scrip/`) against `tiny.reb`. PAT produces tree t2 via
`Compiland`; the existing frontend produces t1. Compared in memory
(`tree_equal`), executed in memory. No subprocesses, no temp files.

Shared SC library: `tree.sc  stack.sc  counter.sc  ShiftReduce.sc  semantic.sc`.

Compiland spine:
```
Compiland = nPush() ARBNO(*Command) reduce("'Parse'", 'nTop()') nPop();
```

---

## Rebus tree shapes (existing frontend, taken as oracle)

| Construct | Oracle `--dump-ir` (single-line form) |
|-----------|---------------------------------------|
| `function f() ... end` | `(STMT :subj (E_FNC DEFINE (E_QLIT "F()")))` then per-body STMTs, then `:go RETURN` `:lbl rb_N` |
| `record R(f1, f2)` | `(STMT :subj (E_FNC DATA (E_QLIT "R(F1,F2)")))` |
| `x` (bare atom) | `(STMT :subj (E_VAR X))` |
| `42` | `(STMT :subj (E_ILIT 42))` |
| `"hi"` | `(STMT :subj (E_QLIT "hi"))` |
| `x := y` | `(STMT :eq :subj (E_VAR X) :repl (E_VAR Y))` |
| `if c then s` | `(STMT :subj <c> :goS L_then :goF L_else)` then s, then merge label |
| `while c do s` | label, then `(STMT :subj <c> :goS body :goF after)` then s, loop back |
| `f()` | `(STMT :subj (E_FNC F))` |
| `x ? y` | `(STMT :subj (E_VAR X) :pat (E_VAR Y))` |
| `a \| b \| c` | left-assoc `(E_ALT (E_ALT a b) c)` per `rebus.y` `alt_expr` |

(The 38 fixtures in `corpus/programs/rebus/parser/` cover every shape
above; oracle outputs are stable.)

---

## Worked atom example — the smallest correct rung

This is the shape RB-0 must take in the rewrite. Read it, follow it.

```snocone
// Lex tokens — drop into the file once, used by every rung.
ws_run = SPAN(' ' tab);
ws_opt = (ws_run | epsilon);
nl_one = (LEN(1) . _nl *IDENT(_nl, nl));

Id      = ((ANY(&UCASE &LCASE '_'))
           (SPAN(&UCASE &LCASE digits '_') | epsilon))
          . _id_raw
          epsilon . *assign('_id', uc(_id_raw));

Integer = SPAN(digits)               . _int_lit;
String  = ('"' BREAK('"') . _str_body '"' | "'" BREAK("'") . _str_body "'");

s_VAR   = "'E_VAR'";   r_VAR   = "'E_VAR'";    // shift wants bare, reduce wants quoted
s_ILIT  = "'E_ILIT'";  r_ILIT  = "'E_ILIT'";
r_QLIT  = "'E_QLIT'";  // QLIT goes through a custom shift helper for sval

// Atom — Rebus's `expr17` slice (id | integer | string).
function rb_push_qlit() {
    Push(tree('E_QLIT', _str_body));
    rb_push_qlit = .dummy;
    nreturn;
}

atom = FENCE(
           *String epsilon . *rb_push_qlit()
         | shift(*Integer, s_ILIT)
         | shift(*Id,      s_VAR)
       );

// At RB-0, a "command" is just an atom-as-statement: wrap it in STMT.
// reduce('STMT', 1) folds the one atom on the stack into (STMT atom).
// (Real STMT shape uses a :subj wrapper — see RB-0 step below for the
// exact reduce target string. Add it once, reuse across rungs.)

Command = ws_opt *atom ws_opt nl_one reduce("'STMT'", 1);

Compiland = nPush() ARBNO(*Command) reduce("'Parse'", 'nTop()') nPop();

// Driver: slurp stdin, fire the one match, walk the result.
InitCounter();  InitStack();
Src = '';
Line = INPUT;
while (DIFFER(Line)) {  Src = Src Line nl;  Line = INPUT;  }

if (~(Src ? Compiland)) {  OUTPUT = 'PARSER-RB: parse failed';  goto die;  }

// Emission: walk Top(), TDump each child STMT.
parse_root = Top();
i = 0;
while (i = LT(i, n(parse_root)) i + 1)  TDump(c(parse_root)[i]);
die:
```

**Self-check before committing RB-0:**
- `grep -c 'goto ' parser_rebus.sc` → 1 (only the `die:` label, used to skip emission on parse failure; remove it if you can).
- `grep -cE 'nPush|nInc|nTop|nPop' parser_rebus.sc` → at least 2 (one `nPush`, one `nTop`, one `nPop`).
- `grep -cE 'shift\(|reduce\(' parser_rebus.sc` → at least 3 (two shifts in atom, one reduce in Command).
- `grep -c '_rb_state' parser_rebus.sc` → 0.
- `grep -c '^[a-z_]\+:' parser_rebus.sc` → ≤1 (only `die:` if kept; ideally 0).

---

## Rung ladder — REWRITES (all reopened)

The 38 fixtures in `corpus/programs/rebus/parser/` already exist and are
correct. Each rung's job is to bring `parser_rebus.sc`'s **shape** up to
spec for that fixture subset.

### PARSER-RB-0 — atom (rewrite) — **next**

- [ ] Delete current `parser_rebus.sc` (or move to `parser_rebus.sc.gotoboard`
      backup at top of branch, then delete after RB-3 lands).
- [ ] Write new `parser_rebus.sc` following the worked example above.
      `Compiland = nPush() ARBNO(*Command) reduce("'Parse'", 'nTop()') nPop();`,
      `Command = ws_opt *atom ws_opt nl_one reduce(<STMT shape>, 1);`,
      `atom = FENCE(*String ... | shift(*Integer, s_ILIT) | shift(*Id, s_VAR));`.
- [ ] Driver slurps stdin into `Src`, runs `Src ? Compiland`, walks the
      tree on the stack, calls `TDump` per top-level STMT.
- [ ] Self-check greps from the worked example all pass.
- [ ] PASS=3 on `atom_id`, `atom_int`, `atom_str` fixtures.
- **Sibling LANG rung:** RB-1.
- **Gate:** PASS=3 AND rubric self-checks all pass.

### PARSER-RB-1 — assignment `x := expr` (rewrite)

- [ ] Add `assign_stmt` sub-pattern:
      `assign_stmt = *Id . _lhs ws_opt ':=' ws_opt *atom reduce("'STMT_ASSIGN'", 2);`
      where reduce target is the STMT shape that lowers to
      `(STMT :eq :subj (E_VAR X) :repl <atom>)` — see `semantic.sc`
      for the canonical reduce-target string.
- [ ] Add `assign_stmt` to `Command`'s alternation BEFORE bare `*atom`.
- [ ] PASS=8 on the assignment fixtures.
- **Sibling LANG rungs:** RB-1.
- **Gate:** PASS=8 AND rubric self-checks all pass.

### PARSER-RB-2 — control flow `if/then`, `while/do` (rewrite)

- [ ] Add `if_stmt` and `while_stmt` sub-patterns. The :goS/:goF/merge
      label generation that the existing frontend does at lower-time
      should be deferred to a `lower_if`/`lower_while` step that walks
      the parsed tree post-Compiland. The PATTERN itself just produces
      `(IF cond body)` / `(WHILE cond body)` — closer to the
      surface-syntax shape — and the lowering pass adds the labels.
      (This matches how `rebus_lower.c` separates concerns; mirror it.)
- [ ] Alternative if scope-creep: keep label generation in the parser
      via a counter helper `next_rb_label()` called from a pattern
      escape, but build the label-bearing STMTs via shift/reduce, not
      via hand-built Tree(...) calls.
- [ ] PASS=12.
- **Sibling LANG rungs:** RB-2.
- **Gate:** PASS=12 AND rubric self-checks.

### PARSER-RB-3 — function decls + call sites (rewrite)

- [ ] Add `function_decl` sub-pattern matching `'function' Id '(' arglist ')'
      ARBNO(*body_stmt) 'end'`. Use `nPush()`/`nInc()`/`nTop()`/`nPop()`
      around the ARBNO of body statements so the function STMT folds the
      correct child count.
- [ ] Add `call_stmt` for bare `f()` no-arg calls.
- [ ] PASS=18.
- **Sibling LANG rungs:** RB-3.
- **Gate:** PASS=18 AND rubric self-checks.

### PARSER-RB-4 — pattern match `expr ? pat` (rewrite)

- [ ] Add `match_stmt = *expr ws_opt '?' ws_opt *pat_expr reduce("'STMT_MATCH'", 2);`.
      `pat_expr` is `expr` per `rebus.y` line 678 (no distinction yet).
- [ ] Lift directly from `parser_snobol4.sc`'s pattern handling once
      PARSER-SN-4 lands (currently in flight).
- [ ] PASS=25.
- **Sibling LANG rung:** RB-4.
- **Gate:** PASS=25 AND rubric self-checks.

### PARSER-RB-5 — alternation generators `a | b | c` (rewrite)

- [ ] Add `alt_expr` sub-pattern using `nPush()`/`*X3`/`reduce(r_ALT,
      'nTop()')`/`nPop()` for n-ary alt — the canonical idiom from
      `parser_snocone.sc:175 Expr3 = nPush() *X3 reduce(r_ALT, r_nTop) nPop();`.
- [ ] Verify left-associativity matches `rebus.y` `alt_expr`. (n-ary
      reduce produces a flat E_ALT with n children; if oracle expects
      strict left-fold `(E_ALT (E_ALT a b) c)` instead, switch to the
      explicit binary fold pattern from `parser_snocone.sc:155-162`.)
- [ ] PASS=32.
- **Sibling LANG rung:** RB-5.
- **Gate:** PASS=32 AND rubric self-checks.

### PARSER-RB-6 — record decls (rewrite)

- [ ] Add `record_decl` to `Command`'s top-level alternation alongside
      `function_decl`. Shape:
      `record_decl = 'record' ws_run *Id '(' opt_idlist ')' reduce("'STMT_RECORD'", k);`
      where k is the field count via `nPush()`/`nInc()`/`nTop()`/`nPop()`.
- [ ] Field-list joining (raw text → `"NAME(F1,F2)"` E_QLIT) lives in a
      named reduce-target string, not in a hand-rolled helper.
- [ ] PASS=38.
- **Sibling LANG rung:** RB-6.
- **Gate:** PASS=38 AND rubric self-checks.

---

## Invariants

- Rebus's existing frontend is younger; tree divergences may surface bugs in
  EITHER frontend. PAT-RB does not silently conform.
- Test programs in `corpus/programs/rebus/parser/` are owned by PAT-RB.
- `.ref` files captured at rung-land time.
- **A rung is not landed until the rubric self-checks pass AND the
  fixture gate passes.** Tree equivalence alone is not sufficient.

---

## Watermark

PARSER-RB-0..RB-6 wrong-shape attempt landed sessions #62 (Claude
Sonnet 4.7, 2026-05-03) — PASS=38 FAIL=0 against 38 fixtures, but the
parser is a goto-driven line-at-a-time state machine, not a Snocone
pattern. Rungs reopened for rewrite.

Current-tree heads: corpus `f2d3077`, one4all/parser `dd6ad80d`,
.github (this commit) — all on remote. The wrong-shape
`parser_rebus.sc` is in corpus at `f2d3077`; the rewrite starts by
deleting it and writing a fresh one following the worked atom
example above.

`test_parser_rebus.sh` carries the `normalize()` whitespace-collapse
upgrade from session #62 — keep that, it is correct.

The 38 fixtures in `corpus/programs/rebus/parser/` are correct — keep
them. The whole rewrite gates against the same 38.

PARSER-RB-0 — next.
