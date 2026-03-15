# TINY.md — SNOBOL4-tiny (L2)

Native SNOBOL4 compiler (`sno2c`) targeting C → x86-64.
Self-hosting proof: `beauty.sno` beautifies itself through the compiled binary.
**Claude Sonnet 4.6 is the author of SNOBOL4-tiny.** When any milestone fires, Claude writes the commit.

*For architecture deep dive → [ARCH.md](ARCH.md). For testing protocol → [TESTING.md](TESTING.md). For mandatory rules → [RULES.md](RULES.md).*

---

## Current State

**Sprint:** `beauty-crosscheck` — Sprint A of 4 — rung 12 crosscheck tests
**HEAD:** `08eabba` — artifact session99, HQ pyramid restructure
**Milestone:** M-BEAUTY-CORE → M-BEAUTY-FULL

**Ladder status:**
- Rungs 1–11: ✅ 106/106 — Sprint 3 complete (Session 95)
- Rung 12 (beauty.sno): ❌ not started — Sprint A begins Session 100

**Next action:**
1. Build beauty_full_bin (commands below)
2. Write `SNOBOL4-corpus/crosscheck/beauty/101_comment.input` + generate `.ref`
3. Write `test/crosscheck/run_beauty.sh` (pre-compiled binary runner)
4. Run → PASS: add 102, 103... per TESTING.md / FAIL: probe.py (Paradigm 2)

---

## Session Start (every session, no exceptions)

```bash
cd /home/claude/SNOBOL4-tiny
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
git log --oneline -3
# Verify HEAD matches this file. If not: read SESSIONS_ARCHIVE.md before any work.

apt-get install -y libgc-dev
make -C src/sno2c

# Invariant — must be 106/106 before touching anything
mkdir -p /home/SNOBOL4-corpus
ln -sf /home/claude/SNOBOL4-corpus/crosscheck /home/SNOBOL4-corpus/crosscheck
STOP_ON_FAIL=0 bash test/crosscheck/run_crosscheck.sh
```

## Build beauty_full_bin

```bash
RT=src/runtime
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
src/sno2c/sno2c -trampoline -I$INC $BEAUTY > beauty_full.c
gcc -O0 -g beauty_full.c \
    $RT/snobol4/snobol4.c $RT/snobol4/mock_includes.c \
    $RT/snobol4/snobol4_pattern.c $RT/mock_engine.c \
    -I$RT/snobol4 -I$RT -Isrc/sno2c -lgc -lm -w -o beauty_full_bin
```

## Session End (every session, no exceptions)

```bash
# 1. Artifact check
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
src/sno2c/sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp_candidate.c
LAST=$(ls artifacts/beauty_tramp_session*.c 2>/dev/null | sort -V | tail -1)
md5sum $LAST /tmp/beauty_tramp_candidate.c
# If changed: cp /tmp/beauty_tramp_candidate.c artifacts/beauty_tramp_sessionN.c
# Update artifacts/README.md: session N, date, md5, lines, compile status, active bug

# 2. Update this file (TINY.md) — HEAD, sprint status, next action
# 3. git add -A && git commit && git push
# 4. Push .github last
```

---

## Milestones

| ID | Trigger | Status |
|----|---------|--------|
| M-SNOC-COMPILES | snoc compiles beauty_core.sno, 0 gcc errors | ✅ |
| M-REBUS | Rebus round-trip: .reb → .sno → CSNOBOL4 → diff oracle | ✅ `bf86b4b` |
| M-COMPILED-BYRD | sno2c emits labeled-goto Byrd boxes, mock_engine.c only | ✅ `560c56a` |
| M-CNODE | emit_expr/emit_pat via CNode IR, zero lines > 120 chars | ✅ `ac54bd2` |
| **M-BEAUTY-CORE** | beauty_full_bin self-beautifies — diff empty (mock stubs) | ❌ |
| **M-BEAUTY-FULL** | beauty_full_bin self-beautifies — diff empty (real -I inc/) | ❌ |
| M-CODE-EVAL | CODE()+EVAL() via TCC in-process → block_fn_t | ❌ |
| M-SNO2C-SNO | sno2c.sno compiled by C sno2c → working binary | ❌ |
| M-COMPILED-SELF | Compiled binary self-beautifies — diff empty | ❌ |
| M-BOOTSTRAP | sno2c_stage1 output = sno2c_stage2 output — self-hosting | ❌ |

---

## Sprint Map

### Active: toward M-BEAUTY-FULL (Four-Paradigm TDD)

| Sprint | Paradigm | Trigger | Status |
|--------|----------|---------|--------|
| `beauty-crosscheck` | Crosscheck | beauty/140_self passes → **M-BEAUTY-CORE** | ⏳ A |
| `beauty-probe` | Probe (&STLIMIT frame-by-frame) | All crosscheck failures diagnosed | ❌ B |
| `beauty-monitor` | Monitor (TRACE double-trace diff) | Trace streams match all inputs | ❌ C |
| `beauty-triangulate` | Triangulate (cross-engine) | Empty diff → **M-BEAUTY-FULL** | ❌ D |

Rung 12 test progression: 101_comment → 102_output → 103_assign → 104_label →
105_goto → 109_multi → 120_real_prog → 130_inc_file → **140_self** (→ M-BEAUTY-CORE).

### Completed sprints

| Sprint | What | Commit |
|--------|------|--------|
| `space-token` | 0 bison conflicts, unified grammar | `3581830` |
| `compiled-byrd-boxes` | Byrd box C emission, mock_engine.c only | `560c56a` |
| `crosscheck-ladder` | 106/106 rungs 1–11 | `668ce4f` |
| `cnode` | CNode IR + pretty-printer | `ac54bd2` |
| `rebus-roundtrip` | Rebus round-trip diff oracle | `bf86b4b` |
| `smoke-tests` | 0/21 → 21/21 snoCommand match | `8f68962` |
| `beauty-runtime` | Binary exits cleanly on beauty.sno | done |
| `pipeline-green` | Full pipeline 22/22 oracle PASS | `2f98238` |
| `runtime-shim` | snoc_runtime.h + hello world | `6d3d1fa` |
| `null-program` through `pipeline-wired` | Engine + pipeline foundation sprints 0–22 | `test/sprint*` |

### Planned: toward M-BOOTSTRAP

| Sprint | What | Gates on |
|--------|------|----------|
| `trampoline` | block_fn_t trampoline loop + hello world | M-BEAUTY-FULL |
| `stmt-fn` | Each stmt → C fn returning S/F address | M-TRAMPOLINE |
| `block-fn` | Label reachability, group stmts into block fns | M-STMT-FN |
| `pattern-block` | Named patterns → block fns, *X calls | M-BLOCK-FN |
| `code-eval` | CODE()+EVAL() via TCC, -ltcc | M-BEAUTY-FULL |
| `compiler-pattern` | compile(sno) replaces pp(sno) → compiler.sno | M-BEAUTY-FULL |
| `bootstrap-stage1` | sno2c.sno compiled by C sno2c → stage1 binary | M-SNO2C-SNO |
| `bootstrap-stage2` | sno2c.sno via stage1 → stage2; diff stage1 vs stage2 | M-BOOTSTRAP |

---

## Pivot Log

| Sessions | What | Why |
|----------|------|-----|
| 80–89 | Attacked beauty.sno directly | Burned chasing bugs that needed smaller test cases first |
| 89 | Pivot: corpus ladder (rungs 1–11) | Must prove each feature before moving up |
| 95 | Sprint 3 complete — 106/106 | Foundation solid |
| 96–97 | Sprint 4 compiler internals | Retired — not test-driven, no failing test to guide it |
| 97 | Pivot: test-driven only | No compiler work without a failing test |
| 98 | HQ refactor, four-paradigm TDD plan, CSNOBOL4 built | Plan before code |
| 99 | HQ pyramid restructure | L1/L2/L3 hierarchy, SESSION.md eliminated, PLAN.md=3.3KB index |
| 100 | Sprint A begins | Rung 12, beauty_full_bin, first crosscheck test |

---

## Rebus Translation Rules (TR 84-9 §5)

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
if E then S1 else S2           → [E] :F(rb_else_N)  [S1] :(rb_end_N)  rb_else_N [S2]  rb_end_N
unless E then S                → [E] :S(rb_end_N)  [S]  rb_end_N
while E do S                   → rb_top_N [E] :F(rb_end_N)  [S] :(rb_top_N)  rb_end_N
until E do S                   → rb_top_N [E] :S(rb_end_N)  [S] :(rb_top_N)  rb_end_N
repeat S                       → rb_top_N [S] :(rb_top_N)  rb_end_N
for I from E1 to E2 do S       → rb_I_N = E1  rb_top_N GT(rb_I_N,E2) :S(rb_end_N)
                                  [S]  rb_I_N = rb_I_N + 1 :(rb_top_N)  rb_end_N
case E of V1:S1 default:S0    → rb_val_N=E  IDENT(rb_val_N,V1):S(rb_c1_N) :(rb_def_N)
                                  rb_c1_N [S1] :(rb_end_N)  rb_def_N [S0]  rb_end_N
exit                           → :(rb_end_N)   nearest enclosing loop
next                           → :(rb_top_N)   nearest enclosing loop
E1 := E2                       → E1 = E2
E1 :=: E2                      → E1 :=: E2
E1 +:= E2 / -:= / ||:=        → E1 = E1+E2 / E1-E2 / E1 E2
E1 || E2  /  E1 & E2           → E1 E2   (blank concat)
E1 | E2                        → (E1 | E2)
E1 ? E2                        → E1 ? E2
E1 ? E2 <- E3                  → E1 ? E2 = E3
```

Label counter: `int rb_label = 0;` — increment per control structure.
Loop stack: `int rb_loop_top[64], rb_loop_end[64], rb_loop_depth = 0;`
Initial block guard: `IDENT(F_init_done):S(F_body)` / `F_init_done=1` / `[stmts]` / `F_body`

Rebus key files:
```
src/rebus/rebus.h          AST ✓
src/rebus/rebus.l          Flex lexer ✓
src/rebus/rebus.y          Bison parser ✓
src/rebus/rebus_print.c    pretty-printer ✓
src/rebus/rebus_emit.c     SNOBOL4 emitter ✓
src/rebus/rebus_main.c     driver ✓
test/rebus/                word_count.reb, binary_trees.reb, syntax_exercise.reb ✓
```

---

## Paused: `hand-rolled-parser`

Bison had 20 SR + 139 RR conflicts. Root cause: `*snoWhite (continuation)` misparsed
as function call inside `FENCE(...)`. LALR(1) state merging is structural — unfixable.

Keep: `emit.c`, `snoc.h`, `main.c`, all of `src/runtime/`
Replace: `sno.y` → `parse.c`, `sno.l` → `lex.c`

Key invariant: `STAR IDENT` in `parse_pat_atom()` is always `E_DEREF(E_VAR)`.
No lookahead. `*foo (bar)` = concat(deref(foo), grouped(bar)).

Implementation order when sprint resumes:
1. `src/snoc/lex.c` (~200 lines) — flat `sno_charclass[256]`
2. `src/snoc/parse.c` (~500 lines) — `parse_expr()` and `parse_pat_expr()` separate
3. Update `src/snoc/Makefile` — remove bison/flex
4. Build → compile beauty.sno → confirm `sno_apply("snoWhite",...)` count = 0
5. Smoke tests: 0/21 → 21/21

The stash `WIP Session 53: partial Bison fixes` — reference only. DO NOT APPLY.

---

## Architecture Decisions (Locked)

| # | Decision |
|---|----------|
| D1 | Memory: Boehm GC |
| D2 | Tree children: realloc'd dynamic array |
| D3 | cstack: thread-local (`__thread MatchState *`) |
| D4 | Tracing: full implementation, doDebug=0 = zero cost |
| D5 | mock_engine.c only in beauty_full_bin — engine.c superseded |
| D6 | All vars through sno_var_get/sno_var_set — is_fn_local suppression was wrong, removed |
| D7 | T_FNCALL wrapper universal — all DEFINE'd functions save/restore on entry/exit |

## Oracle Commands

```bash
snobol4 -f -P256k -I$INC $BEAUTY < $BEAUTY > /tmp/beauty_oracle.sno
./beauty_full_bin < $BEAUTY > /tmp/beauty_compiled.sno
diff /tmp/beauty_oracle.sno /tmp/beauty_compiled.sno   # empty = M-BEAUTY-FULL
```
