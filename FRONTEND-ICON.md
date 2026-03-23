# FRONTEND-ICON.md — Tiny-ICON Frontend (L3)

Tiny-ICON is a frontend for snobol4x targeting the x64 ASM backend.
SNOBOL4 and Icon share a bloodline — Griswold invented both.
The Byrd Box IR is the bridge: same four ports (α/β/γ/ω), new Icon frontend
feeding the same TINY pipeline. Goal-directed generators map directly to Byrd boxes.

**Session trigger phrase:** `"I'm playing with ICON"`
**Session prefix:** `I` (e.g. I-1, I-2, I-3)
**Backend:** x64 ASM only — same NASM/ELF64 pipeline as SNOBOL4
**Location:** `src/frontend/icon/` in snobol4x

*Session state → this file §NOW. Backend → BACKEND-X64.md.*

---

## §NOW — Session State

| Session | Sprint | HEAD | Next milestone |
|---------|--------|------|----------------|
| **ICON frontend** | `main` I-0 — plan written, no code yet | — | M-ICON-LEX |

---

## Why Icon fits the Byrd Box model

Icon's goal-directed evaluation: every expression either succeeds (generating
zero or more values) or fails. Expressions suspend and resume like generators.
This maps exactly to α (proceed) / β (resume) / γ (succeed) / ω (fail).

JCON (Townsend + Proebsting, 1999) proved this: Icon → JVM via Byrd Box IR.
Proebsting's 1996 paper gives the exact four-port templates for every Icon
operator. Those templates are our emitter spec.

---

## Design Decisions

### Backend: x64 ASM (not C, not JVM)

The x64 ASM backend already has full arithmetic (`E_ADD/SUB/MPY/DIV`),
string ops (`CAT2_*` macros), function calls (`APPLY_FN_N`), and the
complete Byrd box macro library. Icon's expression evaluation maps directly
onto existing machinery. No new backend needed.

JCON source is kept as structural reference (especially `irgen.icn` for
four-port wiring patterns) but is not built or run.

### Explicit semicolons — no auto-insertion

Icon's standard lexer inserts semicolons automatically on newlines.
We reject this. Every expression sequence requires an explicit `;`.
This is a deliberate deviation: simpler lexer, explicit structure,
no hanging-continuation ambiguity. Icon source in the corpus is patched
to use explicit semicolons.

### Shared IR — reuse everything with exact semantics

| Icon concept | Shared IR node | Notes |
|---|---|---|
| Integer literal | `E_ILIT` | exact reuse |
| Real literal | `E_FLIT` | exact reuse |
| String literal | `E_QLIT` | exact reuse |
| Cset literal | `E_QLIT` + DT_CS tag | cset = typed string |
| Variable | `E_VART` | exact reuse |
| `+` `-` `*` `/` `%` `^` | `E_ADD/SUB/MPY/DIV/EXPOP` | exact reuse |
| Unary `-` | `E_MNS` | exact reuse |
| `\|\|` string concat | `E_CONC` | exact reuse |
| Function call | `E_FNC` | exact reuse |
| `upto(cs)` | `BREAK` Byrd box | semantic match |
| `many(cs)` | `SPAN` Byrd box | semantic match |
| cset membership | `ANY` Byrd box | semantic match |
| `\|` value alternation | new `E_ICN_ALT` | NOT `E_OR` (that is pattern alt) |
| `to` generator | new `E_TO` node | paper §4.4 template |
| `every`/`do` | new `E_EVERY` node | drives generator to exhaustion |
| `if`/`then`/`else` | new `E_ICN_IF` node | paper §4.5 indirect goto |
| `suspend` | new `E_SUSPEND` node | β port of enclosing call |
| `?` string scan | new `E_SCAN` node | explicit cursor threading |

New nodes added to `sno2c.h` `EKind` enum. SNOBOL4 frontend unaffected.

### `bounded` flag — deferred optimization

JCON threads a `bounded` flag through every IR node: when an expression
is in a "value needed" context (assignment RHS, argument), the resume/fail
ports are omitted entirely. This is the highest-value optimization but is
deferred until after correctness. All four ports emitted unconditionally
for now.

---

## Milestone Table

| ID | Trigger | Depends on | Status |
|----|---------|-----------|--------|
| **M-ICON-LEX** | `icon_lex.c` tokenizes all Tier 0 tokens; `icon_lex_test.c` 100% pass | — | ❌ |
| **M-ICON-PARSE-LIT** | Parser produces correct AST for all Proebsting §2 paper examples | M-ICON-LEX | ❌ |
| **M-ICON-EMIT-LIT** | Byrd box for `ICN_INT` matches paper §4.1 exactly | M-ICON-PARSE-LIT | ❌ |
| **M-ICON-EMIT-TO** | `to` generator; `every write(1 to 5);` → `1..5` | M-ICON-EMIT-LIT | ❌ |
| **M-ICON-EMIT-ARITH** | `+` `*` `-` `/` binary ops via existing `E_ADD/MPY/SUB/DIV` | M-ICON-EMIT-TO | ❌ |
| **M-ICON-EMIT-REL** | `<` `>` `=` `~=` relational with goal-directed retry | M-ICON-EMIT-ARITH | ❌ |
| **M-ICON-EMIT-IF** | `if`/`then`/`else` with indirect goto `gate` temp (paper §4.5) | M-ICON-EMIT-REL | ❌ |
| **M-ICON-EMIT-EVERY** | `every E do E` drives generator to exhaustion | M-ICON-EMIT-IF | ❌ |
| **M-ICON-CORPUS-R1** | Rung 1: all paper examples pass; oracle = `icont`+`iconx` from icon-master | M-ICON-EMIT-EVERY | ❌ |
| **M-ICON-PROC** | `procedure`/`end`, `local`, `return`, `fail`, call expressions | M-ICON-CORPUS-R1 | ❌ |
| **M-ICON-SUSPEND** | `suspend E` inside procedure = user-defined generator | M-ICON-PROC | ❌ |
| **M-ICON-CORPUS-R2** | Rung 2: arithmetic generators, relational filtering | M-ICON-SUSPEND | ❌ |
| **M-ICON-CORPUS-R3** | Rung 3: user procedures with return; user-defined generators | M-ICON-CORPUS-R2 | ❌ |
| **M-ICON-STRING** | `ICN_STR`, `\|\|` concat via `CAT2_*` macros | M-ICON-CORPUS-R3 | ❌ |
| **M-ICON-SCAN** | `E ? E` string scanning; explicit cursor threading | M-ICON-STRING | ❌ |
| **M-ICON-CSET** | Cset literals; `upto`→`BREAK`, `many`→`SPAN`, membership→`ANY` | M-ICON-SCAN | ❌ |
| **M-ICON-CORPUS-R4** | Rung 4: string operations and scanning | M-ICON-CSET | ❌ |

---

## Sprint I-1 Plan: Lexer + Parser

### Files to create

```
src/frontend/icon/
  icon_lex.h         — token kinds, Token, Lexer structs
  icon_lex.c         — hand-rolled lexer (no flex; no auto-semicolon)
  icon_lex_test.c    — unit tests: tokenize all paper examples
  icon_ast.h         — IcnKind enum + IcnNode struct
  icon_parse.h       — parser API
  icon_parse.c       — recursive-descent parser
  icon_parse_test.c  — unit tests: parse paper examples, verify AST shape
```

### Token set

```c
typedef enum {
    TK_EOF = 0,
    TK_INT, TK_REAL, TK_STRING, TK_CSET, TK_IDENT,
    TK_PLUS, TK_MINUS, TK_STAR, TK_SLASH, TK_MOD, TK_CARET,
    TK_LT, TK_LE, TK_GT, TK_GE, TK_EQ, TK_NEQ,
    TK_SLT, TK_SLE, TK_SGT, TK_SGE, TK_SEQ, TK_SNE,
    TK_CONCAT,      /* || */
    TK_LCONCAT,     /* ||| */
    TK_ASSIGN,      /* := */
    TK_SWAP,        /* :=: */
    TK_REVASSIGN,   /* <- */
    TK_AUGPLUS, TK_AUGMINUS, TK_AUGSTAR, TK_AUGSLASH, TK_AUGCONCAT,
    TK_AND,         /* & */
    TK_BAR,         /* | */
    TK_BACKSLASH,   /* \ */
    TK_BANG,        /* ! */
    TK_QMARK,       /* ? */
    TK_AT,          /* @ */
    TK_TILDE,       /* ~ */
    TK_DOT,
    TK_TO, TK_BY, TK_EVERY, TK_DO,
    TK_IF, TK_THEN, TK_ELSE,
    TK_WHILE, TK_UNTIL, TK_REPEAT,
    TK_RETURN, TK_SUSPEND, TK_FAIL, TK_BREAK, TK_NEXT,
    TK_PROCEDURE, TK_END,
    TK_GLOBAL, TK_LOCAL, TK_STATIC,
    TK_RECORD, TK_LINK, TK_INVOCABLE,
    TK_CASE, TK_OF, TK_DEFAULT,
    TK_CREATE, TK_NOT,
    TK_LPAREN, TK_RPAREN, TK_LBRACE, TK_RBRACE, TK_LBRACK, TK_RBRACK,
    TK_COMMA, TK_SEMICOL, TK_COLON,
    TK_ERROR
} IcnTkKind;
```

### AST node kinds

```c
typedef enum {
    ICN_INT, ICN_REAL, ICN_STR, ICN_CSET, ICN_VAR,
    ICN_TO, ICN_TO_BY,
    ICN_ADD, ICN_SUB, ICN_MUL, ICN_DIV, ICN_MOD, ICN_POW, ICN_NEG,
    ICN_LT, ICN_LE, ICN_GT, ICN_GE, ICN_EQ, ICN_NE,
    ICN_SLT, ICN_SLE, ICN_SGT, ICN_SGE, ICN_SEQ, ICN_SNE,
    ICN_CONCAT, ICN_LCONCAT,
    ICN_ALT,        /* E1 | E2 — value alternation */
    ICN_BANG,       /* !E — generate elements */
    ICN_LIMIT,      /* E \ N */
    ICN_NOT,        /* \E — succeed if E fails */
    ICN_SEQ_EXPR,   /* E1 ; E2 */
    ICN_EVERY, ICN_WHILE, ICN_UNTIL, ICN_REPEAT,
    ICN_IF,         /* indirect goto gate — paper §4.5 */
    ICN_CASE,
    ICN_ASSIGN, ICN_AUGOP, ICN_SWAP,
    ICN_SCAN, ICN_SCAN_AUGOP,
    ICN_CALL, ICN_RETURN, ICN_SUSPEND, ICN_FAIL, ICN_BREAK, ICN_NEXT,
    ICN_FIELD, ICN_SUBSCRIPT,
    ICN_PROC, ICN_RECORD, ICN_GLOBAL,
} IcnKind;
```

### Test corpus — Rung 1

```
test/frontend/icon/corpus/rung01_paper/
  t01_to5.icn          every write(1 to 5);
  t02_mult.icn         every write((1 to 3) * (1 to 2));
  t03_nested_to.icn    every write((1 to 2) to (2 to 3));
  t04_lt.icn           every write(2 < (1 to 4));
  t05_compound.icn     every write(3 < ((1 to 3) * (1 to 2)));
  t06_paper_expr.icn   full optimized paper example
```

Oracle: `icont` + `iconx` from `icon-master`.

---

## Sprint I-2 Plan: Emitter

### Files to create

```
src/frontend/icon/
  icon_emit.h        — emitter API
  icon_emit.c        — IcnNode → four-port x64 ASM chunks
  icon_driver.c      — main(): lex → parse → emit
icon-asm             — driver shell script (top-level, mirrors snobol4-asm)
```

### Port threading model

```c
typedef struct {
    char start[64];    /* α — initial entry (synthesized) */
    char resume[64];   /* β — re-entry for next value (synthesized) */
    char fail[64];     /* ω — where to go on failure (inherited) */
    char succeed[64];  /* γ — where to go on success (inherited) */
} PortSet;
```

Labels: `icon_N_a` (α), `icon_N_b` (β), `icon_N_g` (γ), `icon_N_w` (ω)
where N is a unique node ID. Matches existing α/β/γ/ω naming in ASM backend.

### Four-port templates (from Proebsting paper)

**ICN_INT** (§4.1):
- α: `value ← N; goto γ`
- β: `goto ω`

**ICN_ADD/MUL/etc** (§4.3): E1 outer loop, E2 restarted per E1 value.
Reuses `E_ADD/MPY` emission path from `emit_byrd_asm.c` — just call it.

**ICN_LT/GT/etc** (§4.3 variant): E2 resumed on comparison failure (goal-directed).

**ICN_TO** (§4.4): `I` temp; increment on β; check `I > E2.value` → E2.β.

**ICN_IF** (§4.5): `gate` temp holds address of E2.β or E3.β; resume = indirect goto.

**ICN_EVERY**:
- α: goto E.α
- β: goto body.β
- E.ω → every.ω (exhausted)
- E.γ → body.α
- body.ω → E.β (get next)
- body.γ → every.γ

---

## Session Bootstrap (every I-session)

```bash
git clone https://github.com/snobol4ever/snobol4x
git clone https://github.com/snobol4ever/.github
bash /home/claude/snobol4x/setup.sh
# Reference material already present from session planning:
# /home/claude/jcon-master/   — JCON source (irgen.icn, ir.icn)
# /home/claude/icon-master/   — Icon reference impl (icont oracle)
```

Read FRONTEND-ICON.md §NOW for current milestone. Start at first ❌.

---

## Reference

- Proebsting 1996 paper: "Simple Translation of Goal-Directed Evaluation" — four-port templates §4.1–4.5
- JCON source: `jcon-master/tran/` — `ir.icn` (IR vocab), `irgen.icn` (wiring patterns)
- Icon reference impl: `icon-master/src/icont/` — `tparse.c`, `tcode.c`
- Prolog frontend (structural template): `src/frontend/prolog/`
- ASM macro library: `src/runtime/asm/snobol4_asm.mac`
- MISC.md §JCON — lessons learned from JCON study
