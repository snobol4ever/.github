# PARSER-REBUS.md — Rebus Parser

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Status:** AUTHORITATIVE — ✅ M-REBUS complete (bf86b4b)

Rebus is a structured language that transpiles to SNOBOL4.
Bison-generated parser. File: `src/rebus/rebus.y`

---

## Source Layout

```
src/rebus/
  rebus.h          AST node types ✅
  rebus.l          Flex lexer ✅
  rebus.y          Bison parser ✅
  rebus_print.c    Pretty-printer (model for emitter) ✅
  rebus_emit.c     SNOBOL4 emitter ✅
  rebus_main.c     Driver ✅
test/rebus/
  word_count.reb
  binary_trees.reb
  syntax_exercise.reb ✅
```

---

## Translation Rules (TR 84-9 §5)

```
REBUS                          → SNOBOL4
────────────────────────────────────────────────────────
record R(f1,f2)                → DATA('R(f1,f2)')
function F(p1,p2) ... end      → DEFINE('F(p1,p2)') + body
if E then S                    → [E] :F(rb_else_N)  [S] :(rb_end_N)
if E then S1 else S2           → [E] :F(rb_else_N) [S1] :(rb_end_N) rb_else_N [S2]
unless E then S                → [E] :S(rb_end_N)  [S]  rb_end_N
while E do S                   → rb_top_N [E] :F(rb_end_N) [S] :(rb_top_N)
until E do S                   → rb_top_N [E] :S(rb_end_N) [S] :(rb_top_N)
repeat S                       → rb_top_N [S] :(rb_top_N)
for I from E1 to E2 do S       → rb_I_N = E1 / loop with GT check
case E of V1: S1 default: S0   → IDENT chain + label dispatch
exit                           → :(rb_end_N)    nearest enclosing loop
next                           → :(rb_top_N)    nearest enclosing loop
E1 := E2                       → E1 = E2
E1 || E2  /  E1 & E2           → E1 E2   (blank concat)
E1 | E2                        → (E1 | E2)
E1 ? E2 <- E3                  → E1 ? E2 = E3
```

**Label counter:** `int rb_label = 0;` — increment per control structure.
**Loop stack:** `int rb_loop_top[64], rb_loop_end[64], rb_loop_depth = 0;`

---

## Round-Trip Protocol (M-REBUS ✅)

```bash
src/rebus/rebus word_count.reb > /tmp/word_count.sno
spitbol -b /tmp/word_count.sno < input > /tmp/got.txt
diff /tmp/expected.txt /tmp/got.txt   # empty = pass
```

All three test files pass round-trip at bf86b4b.

## References

- `LEXER-REBUS.md` — token stream input
- `PARSER-SNOBOL4.md` — Rebus transpiles to SNOBOL4 → this parser
