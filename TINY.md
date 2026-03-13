# TINY.md — SNOBOL4-tiny

**Repo:** https://github.com/SNOBOL4-plus/SNOBOL4-tiny  
**What it is:** Native SNOBOL4 compiler (`sno4now`) targeting C → x86-64. Self-hosting proof: `beauty.sno` beautifies itself through the compiled binary. Claude Sonnet 4.6 is the author.

---

## Current State

**Active sprint:** Rebus R3 — `src/rebus/rebus_emit.c` (SNOBOL4 text emitter)  
**Milestone target:** MREBUS  
**Paused sprint:** Sprint 26 — hand-rolled parser → Milestone M0. Resumes after MREBUS.  
**HEAD:** `bceaa24` — chore: untrack generated rebus artifacts  
**Last substantive commit:** `01e5d30` — feat: Rebus lexer/parser — all 3 tests pass

**Next action:** Write `src/rebus/rebus_emit.c`. Start with expressions (R3), then
assignments (R4), then control structures (R5–R8). Model on `rebus_print.c`.

---

## Session Start Checklist

```bash
cd SNOBOL4-tiny
git log --oneline --since="1 hour ago"   # fallback: git log --oneline -5
find src -type f | sort
git show HEAD --stat
# Then read § Current Sprint below
```

---

## Milestones

| ID | Trigger | Status |
|----|---------|--------|
| **M1** | `snoc` compiles `beauty_core.sno`, 0 gcc errors | ✅ Done |
| **M0** | `beauty_full_bin` self-beautifies — diff empty | ⏸ Paused (Sprint 26) |
| **M2** | Compiled binary self-beautifies — diff empty | ❌ |
| **M3** | `snoc` compiles `snoc` (self-hosting) | ❌ Future |
| **MREBUS** | Rebus round-trip: `.reb` → `.sno` → CSNOBOL4 → diff oracle | ❌ **Active** |

**When any milestone triggers:** Claude Sonnet 4.6 writes the commit message. This is the deal. Recorded 2026-03-12.

---

## Sprint Map

### Sprints toward MREBUS (active track)

| Sprint | What | Status |
|--------|------|--------|
| Rebus R1 | Lexer (`rebus.l`) — all control structures, operators, auto-semicolon | ✅ `01e5d30` |
| Rebus R2 | Parser → full AST (`rebus.y`) — all 3 test files parse cleanly | ✅ `01e5d30` |
| **Rebus R3** | **Emitter: expressions → SNOBOL4 text** | **← active** |
| Rebus R4 | Emitter: assignment variants (`:=` `:=:` `+:=` `-:=` `\|\|:=`) | ❌ |
| Rebus R5 | Emitter: if/unless → label/goto | ❌ |
| Rebus R6 | Emitter: while/until/repeat → label/goto | ❌ |
| Rebus R7 | Emitter: for (with/without `by`) | ❌ |
| Rebus R8 | Emitter: case/of/default | ❌ |
| Rebus R9 | Emitter: function/record declarations | ❌ |
| Rebus R10 | Emitter: exit/next/fail/stop/return | ❌ |
| Rebus R11 | Emitter: pattern stmts (`?` `?<-` `?-`) | ❌ |
| Rebus R12 | Round-trip test → **MREBUS triggers** | ❌ |

### Sprints toward M0 (paused — resumes after MREBUS)

| Sprint | What | Status |
|--------|------|--------|
| Sprint 26 | Hand-rolled parser (`lex.c` + `parse.c`) replacing Bison/Flex | ⏸ Paused |
| Sprint 27 | Smoke tests: 0/21 → 21/21 on `test_snoCommand_match.sh` | ❌ |
| Sprint 28 | `beauty_full_bin` diff empty → **M0 triggers** | ❌ |

### Sprints toward M2

| Sprint | What | Status |
|--------|------|--------|
| Sprint 29 | Compiled binary self-beautifies → **M2 triggers** | ❌ |

### Completed sprints (engine + pipeline foundation)

| Sprint | What | Status |
|--------|------|--------|
| Sprint 0 | α/β/γ/ω skeleton + runtime — null program | ✅ `test/sprint0` |
| Sprint 1 | LIT, POS, RPOS — single token patterns | ✅ `test/sprint1` |
| Sprint 2 | CAT (concatenation) — P_γ→Q_α wiring | ✅ `test/sprint2` |
| Sprint 3 | ALT (alternation) | ✅ `test/sprint3` |
| Sprint 4 | ASSIGN (`$`, `.`) — immediate and deferred capture | ✅ `test/sprint4` |
| Sprint 5 | SPAN β — backtracking | ✅ `test/sprint5` |
| Sprint 6 | BREAK, ANY, NOTANY | ✅ `test/sprint6` |
| Sprint 7 | LEN, TAB, RTAB, REM, ARB | ✅ `test/sprint7` |
| Sprint 8 | ARBNO — `(a\|b)*abb` | ✅ `test/sprint8` |
| Sprint 9 | REF (ζ) simple — `{a^n b^n}` | ✅ `test/sprint9` |
| Sprint 10 | Mutual REF — palindrome | ✅ `test/sprint10` |
| Sprint 11 | Shift/Reduce + nPush — balanced parens | ✅ `test/sprint11` |
| Sprint 12 | @cursor + -INCLUDE — `{a^n b^n c^n}` | ✅ `test/sprint12` |
| Sprint 13 | cstack — Turing `{w#w}` | ✅ `test/sprint13` |
| Sprint 14 | Python front-end, Stage B runtime | ✅ `test/sprint14` |
| Sprint 15 | DEFINE/APPLY, expression parser | ✅ `test/sprint15` |
| Sprint 16 | EVAL/OPSYN | ✅ `test/sprint16` |
| Sprint 17 | (folded into Sprint 18) | — |
| Sprint 18 | Three-way Byrd Box port — C + JVM + MSIL | ✅ `test/sprint18` |
| Sprint 19 | End-to-end pipeline wired | ✅ `test/sprint19` |
| Sprint 20 | T_CAPTURE — deferred assignment in compiled C | ✅ `test/sprint20` |
| Sprint 21 | Three-way port complete (21A + 21B) | ✅ `test/sprint21` |
| Sprint 22 | Full pipeline green — 22/22 oracle PASS | ✅ `test/sprint22` `2f98238` |
| Sprint 23 | `snoc_runtime.h` shim + emit.c symbol collection + hello world | ✅ `6d3d1fa` |
| Sprint 24 | Function-per-DEFINE in emit.c | ✅ |
| Sprint 25 | SIL execution model + body boundary + 0 gcc errors | ✅ |

---

## Rebus: Translation Rules (TR 84-9 §5)

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
                                 [S] rb_I_N = rb_I_N + 1 :(rb_top_N)
                                 rb_end_N

case E of                      → rb_val_N = E
  V1: S1                         IDENT(rb_val_N,V1) :S(rb_c1_N)
  default: S0                    :(rb_def_N)
}                                rb_c1_N [S1] :(rb_end_N)
                                 rb_def_N [S0]  rb_end_N

exit                           → :(rb_end_N)   nearest enclosing loop
next                           → :(rb_top_N)   nearest enclosing loop
return E                       → FRETURN E
E1 := E2                       → E1 = E2
E1 :=: E2                      → E1 :=: E2
E1 +:= E2                      → E1 = E1 + E2
E1 -:= E2                      → E1 = E1 - E2
E1 ||:= E2                     → E1 = E1 E2
E1 || E2  /  E1 & E2           → E1 E2        (blank concat)
E1 | E2                        → (E1 | E2)
E1 ? E2                        → E1 ? E2
E1 ? E2 <- E3                  → E1 ? E2 = E3
```

**Label counter:** `int rb_label = 0;` — increment per control structure.  
**Loop stack:** `int rb_loop_top[64], rb_loop_end[64], rb_loop_depth = 0;`  
**Initial block guard:** `IDENT(F_init_done) :S(F_body)` / `F_init_done = 1` / `[stmts]` / `F_body`

**File layout:**
```
src/rebus/rebus.h          AST ✓
src/rebus/rebus.l          Flex lexer ✓
src/rebus/rebus.y          Bison parser ✓
src/rebus/rebus_print.c    pretty-printer (model for emitter) ✓
src/rebus/rebus_emit.c     SNOBOL4 emitter  ← NEXT
src/rebus/rebus_main.c     driver ✓
test/rebus/                word_count.reb, binary_trees.reb, syntax_exercise.reb ✓
```

---

## Paused: Sprint 26 — Hand-Rolled Parser

### Why (Session 53 root cause)

Bison/Flex LALR(1) parser: 20 SR + 139 RR conflicts. Root cause: `*snoWhite (continuation)`
misparsed as function call inside `FENCE(...)`. State merging is structural — unfixable in
LALR(1). Decision: replace `sno.y` + `sno.l` with hand-rolled recursive-descent parser.

**Keep unchanged:** `emit.c`, `snoc.h`, `main.c`, all of `src/runtime/`  
**Replace:** `sno.y` → `parse.c`, `sno.l` → `lex.c`

### Key invariant

`STAR IDENT` in `parse_pat_atom()` is **always** `E_DEREF(E_VAR)`. No lookahead check. Period.
`*foo (bar)` = concat(deref(foo), grouped(bar)). Two sequential calls to `parse_pat_atom()`.

### Implementation order (when Sprint 26 resumes)

1. `src/snoc/lex.c` (~200 lines) — flat `sno_charclass[256]`, VARTB rule: `IDENT(` → FNCTYP
2. `src/snoc/parse.c` (~500 lines) — `parse_expr()` and `parse_pat_expr()` are separate functions
3. Update `src/snoc/Makefile` — remove bison/flex
4. Build → compile beauty.sno → confirm `sno_apply("snoWhite",...)` count = 0
5. Run smoke tests: target 0/21 → 21/21

**The stash** `WIP Session 53: partial Bison fixes` — reference only. DO NOT APPLY.

---

## Architecture: Two Worlds

| World | Type | Failure | Entry |
|-------|------|---------|-------|
| **Byrd Box** | Pattern nodes (α/β/γ/ω) | Structured backtrack | `_alpha` |
| **DEFINE functions** | Regular C functions | `goto _SNO_FRETURN` | Normal call |

`T_FNCALL` wrapper is universal — any function call in CONCAT context must be wrapped.
All DEFINE'd functions must save/restore on entry/exit. `is_fn_local` suppression was wrong — removed.
All vars (params, locals, globals) go through `sno_var_get`/`sno_var_set`.

## Architecture Decisions (Locked)

| # | Decision |
|---|----------|
| D1 | Memory: Boehm GC |
| D2 | Tree children: realloc'd dynamic array |
| D3 | cstack: thread-local (`__thread MatchState *`) |
| D4 | Tracing: full implementation, doDebug=0 = zero cost |
| D6 | ByrdBox struct reconciliation: after Sprint 20 |

## Build / Oracle Commands

```bash
# Build snoc
cd SNOBOL4-tiny && make -C src/snoc

# Oracle (primary)
snobol4 -f -P256k -I $INC $BEAUTY < $BEAUTY > /tmp/beauty_oracle.sno

# M0/M2 trigger test
beauty_full_bin < $BEAUTY > /tmp/beauty_compiled.sno
diff /tmp/beauty_oracle.sno /tmp/beauty_compiled.sno   # must be empty

# Smoke tests
bash test/smoke/test_snoCommand_match.sh    # target: 21/21
```
