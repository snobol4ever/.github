# FRONTEND-REBUS.md — Rebus Language Frontend

Rebus is a structured language that transpiles to SNOBOL4.
M-REBUS ✅ `bf86b4b` — round-trip complete.

*Session state → TINY.md. sno2c compiler → FRONTEND-SNO2C.md.*

---

## Source Layout

```
src/rebus/
  rebus.h          AST node types ✓
  rebus.l          Flex lexer ✓
  rebus.y          Bison parser ✓
  rebus_print.c    Pretty-printer (model for emitter) ✓
  rebus_emit.c     SNOBOL4 emitter ✓
  rebus_main.c     Driver ✓
test/rebus/
  word_count.reb
  binary_trees.reb
  syntax_exercise.reb ✓
```

---

## Translation Rules (TR 84-9 §5)

```
REBUS                          → SNOBOL4
────────────────────────────────────────────────────────
record R(f1,f2)                → DATA('R(f1,f2)')

function F(p1,p2)              → DEFINE('F(p1,p2)l1,l2') :(F_end)
  local l1, l2                 F
  initial { ... }                [flag-guarded initial stmts]
  [body]                         [body]
  return expr                    FRETURN expr
end                            F_end

if E then S                    → [E] :F(rb_else_N)  [S] :(rb_end_N)
                                   rb_else_N  rb_end_N

if E then S1 else S2           → [E] :F(rb_else_N)  [S1] :(rb_end_N)
                                   rb_else_N [S2]  rb_end_N

unless E then S                → [E] :S(rb_end_N)  [S]  rb_end_N

while E do S                   → rb_top_N [E] :F(rb_end_N)
                                   [S] :(rb_top_N)  rb_end_N

until E do S                   → rb_top_N [E] :S(rb_end_N)
                                   [S] :(rb_top_N)  rb_end_N

repeat S                       → rb_top_N [S] :(rb_top_N)  rb_end_N

for I from E1 to E2 do S       → rb_I_N = E1
                                   rb_top_N GT(rb_I_N,E2) :S(rb_end_N)
                                   [S]  rb_I_N = rb_I_N + 1 :(rb_top_N)
                                   rb_end_N

case E of                      → rb_val_N = E
  V1: S1                           IDENT(rb_val_N,V1) :S(rb_c1_N) ...
  default: S0                      :(rb_def_N)
}                                  rb_c1_N [S1] :(rb_end_N)
                                   rb_def_N [S0]  rb_end_N

exit                           → :(rb_end_N)    nearest enclosing loop
next                           → :(rb_top_N)    nearest enclosing loop
return E                       → FRETURN E
E1 := E2                       → E1 = E2
E1 :=: E2                      → E1 :=: E2
E1 +:= E2                      → E1 = E1 + E2
E1 -:= E2                      → E1 = E1 - E2
E1 ||:= E2                     → E1 = E1 E2
E1 || E2  /  E1 & E2           → E1 E2         (blank concat)
E1 | E2                        → (E1 | E2)
E1 ? E2                        → E1 ? E2
E1 ? E2 <- E3                  → E1 ? E2 = E3
```

**Label counter:** `int rb_label = 0;` — increment per control structure.
**Loop stack:** `int rb_loop_top[64], rb_loop_end[64], rb_loop_depth = 0;`
**Initial block guard:** `IDENT(F_init_done):S(F_body)` / `F_init_done=1` / `[stmts]` / `F_body`

---

## Round-Trip Protocol (M-REBUS)

```bash
# .reb → .sno → CSNOBOL4 → diff oracle
src/rebus/rebus word_count.reb > /tmp/word_count.sno
snobol4 -f /tmp/word_count.sno < input > /tmp/got.txt
diff /tmp/expected.txt /tmp/got.txt   # empty = pass
```

M-REBUS fired at `bf86b4b`. All three test files pass round-trip.
