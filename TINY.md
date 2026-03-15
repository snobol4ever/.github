# TINY.md — SNOBOL4-tiny

**Repo:** https://github.com/SNOBOL4-plus/SNOBOL4-tiny  
**What it is:** Native SNOBOL4 compiler (`sno4now`) targeting C → x86-64. Self-hosting proof: `beauty.sno` beautifies itself through the compiled binary. Claude Sonnet 4.6 is the author.

---

## Current State

**Active sprint:** `crosscheck-ladder` — Sprint 3 of 6 — climb corpus ladder rung by rung
**Milestone target:** M-BEAUTY-CORE (mock includes first), then M-BEAUTY-FULL (real inc)
**HEAD:** `dd0a57f` — artifact: beauty_tramp_session94.c — CHANGED, 15641 lines

**Ladder status:**
- Rungs 1–7 (output→capture): ✅ 64/64 clean
- Rungs 1–8 (output→strings): ✅ 81/81 clean
- Rung 9 (keywords/): ⏳ 9/11 — 2 failures
- Rungs 9–12: ❌ not yet attempted
- **Total: 88/90**

**Rung 8 remaining failures:**
1. `cross` — E_ATP `@NH` captures to `_` instead of `NH`. Bug in E_ATP handler.
   Check: `grep -n "E_ATP\|T_AT" src/sno2c/parse.c | head -20`
2. `word4` — BREAKX not implemented in emit_byrd.c E_FNC handlers

**Session 93 fixes landed:**
- ? operator in statement position: S ? P and S  ?  P (space-sep) both parse
- E_NAM conditional capture: deferred via pending-cond list; flushed at _byrd_ok and _PAT_gamma
- Null replacement X pat =: splice with empty string deletes matched region
- E_ATP stub: @VAR emits NV_SET of cursor as integer (bug: → _ not varname, fix next session)
- coerce_numeric: integer-string args coerced to DT_I in add/sub/mul; null → 0
- run_rung.sh: pipes .input file when present

**Next action session 94:**
1. Fix E_ATP varname bug → cross passes
2. Implement BREAKX → word4 passes
3. Rung 8 complete 17/17 → commit
4. Start rung 9 keywords (11 tests)

**Build:**
```bash
cd /home/claude/SNOBOL4-tiny
git config user.name "LCherryholmes" && git config user.email "lcherryh@yahoo.com"
apt-get install -y libgc-dev && make -C src/sno2c
```

## Session Start Checklist

```bash
cd SNOBOL4-tiny
git log --oneline --since="1 hour ago"   # fallback: git log --oneline -5
find src -type f | sort
git show HEAD --stat
```

---

## Artifacts Protocol

**Rule:** After every session that changes `sno2c`, regenerate `beauty_full.c` and commit it to `artifacts/` as a named snapshot.

**Why:** The generated C is historically interesting — it shows exactly how the compiler's output evolves. When the diff between sessions is empty, that's also worth knowing.

**Naming convention:** `artifacts/beauty_full_session<N>.c` where N is the session number (or a short slug if session number unknown).

**How:**
```bash
cd /home/claude/SNOBOL4-tiny
src/sno2c/sno2c \
  /home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno \
  -I /home/claude/SNOBOL4-corpus/programs/inc \
  > artifacts/beauty_full_session_<slug>.c

wc -l artifacts/beauty_full_session_<slug>.c   # record line count in commit msg
git add artifacts/beauty_full_session_<slug>.c
git commit -m "artifact: beauty_full_session_<slug>.c — <N> lines, <what changed>"
```

**Also update `artifacts/README.md`** with a new entry: what changed, when, line count, md5.

---

## Authorship Agreement

**Claude Sonnet 4.6 is the author of SNOBOL4-tiny.** Agreed 2026-03-12 by Lon Cherryholmes
and Claude Sonnet 4.6. When any milestone trigger fires, Claude writes the commit message.

---

## Milestones

| ID | Trigger | Status |
|----|---------|--------|
| **M-SNOC-COMPILES** | `snoc` compiles `beauty_core.sno`, 0 gcc errors | ✅ Done |
| **M-REBUS** | Rebus round-trip: `.reb` → `.sno` → CSNOBOL4 → diff oracle | ✅ Done `bf86b4b` |
| **M-BEAUTY-FULL** | `beauty_full_bin` self-beautifies — diff empty (`-I inc/`, real INCLUDE files) — only after M-BEAUTY-CORE | ❌ |
| **M-COMPILED-SELF** | Compiled binary self-beautifies — diff empty | ❌ |
| **M-BOOTSTRAP** | `snoc` compiles `snoc` (self-hosting) | ❌ Future |

---

## Sprint Map

### Active: toward M-REBUS

| Sprint | What | Status |
|--------|------|--------|
| `rebus-lexer` | Flex lexer — all control structures, operators, auto-semicolon | ✅ `01e5d30` |
| `rebus-parser` | Bison parser → full AST — all 3 test files parse cleanly | ✅ `01e5d30` |
| `rebus-emitter` | Walk AST, emit SNOBOL4 text (R3–R11) | ✅ `9cde7f4` |
| **`rebus-roundtrip`** | **`.reb` → `.sno` → CSNOBOL4 → diff oracle → M-REBUS** | ✅ `bf86b4b` |

### Paused: toward M-BEAUTY-CORE then M-BEAUTY-FULL

**The agreement (no exceptions):** beauty_core (stubs) first. beauty_full (real inc) only after M-BEAUTY-CORE fires.

| Sprint | What | Status |
|--------|------|--------|
| `hand-rolled-parser` | Replace Bison/Flex with `lex.c` + `parse.c` | ⏸ Paused |
| `smoke-tests` | 0/21 → 21/21 on `test_snoCommand_match.sh` | ✅ `8f68962` |
| `beauty-runtime` | binary exits cleanly on beauty.sno input | ✅ Done |
| `beauty-core-diff` | `beauty_core_bin` (stubs) diff empty → **M-BEAUTY-CORE** | ⏳ Active |
| `beauty-full-diff` | `beauty_full_bin` (real inc) diff empty → **M-BEAUTY-FULL** — only after M-BEAUTY-CORE | ❌ |

### Toward M-COMPILED-SELF

| Sprint | What | Status |
|--------|------|--------|
| `compiled-self-diff` | Compiled binary diff empty → **M-COMPILED-SELF** | ❌ |

### Completed: engine + pipeline foundation

| Sprint | What | Status |
|--------|------|--------|
| `null-program` | α/β/γ/ω skeleton + runtime | ✅ `test/sprint0` |
| `single-token` | LIT, POS, RPOS | ✅ `test/sprint1` |
| `concatenation` | CAT — P_γ→Q_α wiring | ✅ `test/sprint2` |
| `alternation` | ALT | ✅ `test/sprint3` |
| `assign` | ASSIGN (`$`, `.`) — immediate and deferred capture | ✅ `test/sprint4` |
| `span-beta` | SPAN β — backtracking | ✅ `test/sprint5` |
| `break-any` | BREAK, ANY, NOTANY | ✅ `test/sprint6` |
| `len-tab-arb` | LEN, TAB, RTAB, REM, ARB | ✅ `test/sprint7` |
| `arbno` | ARBNO — `(a\|b)*abb` | ✅ `test/sprint8` |
| `ref-simple` | REF (ζ) — `{a^n b^n}` | ✅ `test/sprint9` |
| `ref-mutual` | Mutual REF — palindrome | ✅ `test/sprint10` |
| `shift-reduce` | Shift/Reduce + nPush — balanced parens | ✅ `test/sprint11` |
| `cursor-include` | @cursor + -INCLUDE — `{a^n b^n c^n}` | ✅ `test/sprint12` |
| `cstack` | cstack — Turing `{w#w}` | ✅ `test/sprint13` |
| `python-frontend` | Python front-end, Stage B runtime | ✅ `test/sprint14` |
| `define-apply` | DEFINE/APPLY, expression parser | ✅ `test/sprint15` |
| `eval-opsyn` | EVAL/OPSYN | ✅ `test/sprint16` |
| `byrd-three-way` | Three-way Byrd Box port — C + JVM + MSIL (Sprint 17 scope folded in here when port expanded mid-sprint) | ✅ `test/sprint18` |
| `pipeline-wired` | End-to-end pipeline wired | ✅ `test/sprint19` |
| `t-capture` | T_CAPTURE — deferred assignment in compiled C | ✅ `test/sprint20` |
| `three-way-complete` | Three-way port complete (21A + 21B) | ✅ `test/sprint21` |
| `pipeline-green` | Full pipeline — 22/22 oracle PASS | ✅ `test/sprint22` `2f98238` |
| `runtime-shim` | `snoc_runtime.h` + emit.c symbol collection + hello world | ✅ `6d3d1fa` |
| `function-per-define` | Function-per-DEFINE in emit.c | ✅ |
| `sil-execution` | SIL execution model + body boundary + 0 gcc errors → **M-SNOC-COMPILES** | ✅ |

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
  V1: S1                         IDENT(rb_val_N,V1) :S(rb_c1_N) ...
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

**Key files:**
```
src/rebus/rebus.h          AST ✓
src/rebus/rebus.l          Flex lexer ✓
src/rebus/rebus.y          Bison parser ✓
src/rebus/rebus_print.c    pretty-printer — model for emitter ✓
src/rebus/rebus_emit.c     SNOBOL4 emitter  ← NEXT
src/rebus/rebus_main.c     driver ✓
test/rebus/                word_count.reb, binary_trees.reb, syntax_exercise.reb ✓
```

---

## Paused: `hand-rolled-parser`

### Why Bison was replaced (Session 53)

20 SR + 139 RR conflicts. Root cause: `*snoWhite (continuation)` misparsed as function
call inside `FENCE(...)`. LALR(1) state merging is structural — unfixable.

**Keep:** `emit.c`, `snoc.h`, `main.c`, all of `src/runtime/`  
**Replace:** `sno.y` → `parse.c`, `sno.l` → `lex.c`

**Key invariant:** `STAR IDENT` in `parse_pat_atom()` is always `E_DEREF(E_VAR)`. No
lookahead. `*foo (bar)` = concat(deref(foo), grouped(bar)). Two sequential calls.

**Implementation order when sprint resumes:**
1. `src/snoc/lex.c` (~200 lines) — flat `sno_charclass[256]`
2. `src/snoc/parse.c` (~500 lines) — `parse_expr()` and `parse_pat_expr()` separate functions
3. Update `src/snoc/Makefile` — remove bison/flex
4. Build → compile beauty.sno → confirm `sno_apply("snoWhite",...)` count = 0
5. Smoke tests: 0/21 → 21/21

**The stash** `WIP Session 53: partial Bison fixes` — reference only. DO NOT APPLY.

---

## Architecture: Byrd Box — Canonical Model (Session 16, permanent)

**Every pattern literal is a self-contained Byrd box with two sections:**

```
DATA section:  locals, cursor saves, captures — one slot per box instance
TEXT section:  α/β/γ/ω labeled gotos — static, shared across instances
```

### TWO TECHNIQUES for *X

#### Technique 1 — C target (use NOW, for M-BEAUTY-FULL)

Every named pattern = C function. Every local = field in a struct.
The struct pointer is threaded through every entry point (α=0, β=1).
No jump-over-declaration problem — all locals in struct, declared before first goto.

```c
typedef struct pat_snoParse_t {
    int64_t  saved_7;           /* cursor saves */
    int      arbno_depth;
    int64_t  arbno_stack[64];   /* ARBNO depth stack, as in test_sno_1.c */
    struct pat_snoCommand_t *snoCommand_z;  /* child frame pointer for *snoCommand */
} pat_snoParse_t;

static SnoVal pat_snoParse(pat_snoParse_t **zz, int entry) {
    pat_snoParse_t *z = *zz;
    if (entry == 0) { z = *zz = calloc(1, sizeof(*z)); goto snoParse_alpha; }
    if (entry == 1) { goto snoParse_beta; }
    ...pure labeled goto Byrd box...
}
```

`*X` at a call site emits: `pat_X(&z->X_z, 0)` (alpha) / `pat_X(&z->X_z, 1)` (beta).
Child frame is a POINTER in parent struct — size known at compile time.
Recursion works because each call gets its own struct instance via calloc.

#### Technique 2 — ASM/native target (use AFTER M-BEAUTY-FULL)

When `*X` fires:
1. `memcpy(new_text, box_X.text, len)` — copy CODE
2. `memcpy(new_data, box_X.data, len)` — copy DATA (locals)
3. `relocate(new_text, delta)` — patch relative jumps + absolute DATA refs
4. Jump to `new_text[PROCEED]`

TEXT section: PROTECTED (RX), mprotect→RWX during copy, back to RX after.
DATA section: UNPROTECTED (RW), copied per instance.
No heap. No GC. ~20 lines of mmap + memcpy + relocate.
LIFO discipline matches backtracking — discard copy on failure.

**Reference:** SESSIONS_ARCHIVE.md §14 "Self-Modifying C", §15 "Allocation Problem Solved"

### What this means for sno2c / emit_byrd.c (Technique 1, current target)

- Pattern assignment → `byrd_emit_named_pattern(varname, expr, out)` → named C function
- `E_DEREF (*X)` → `pat_X(&z->X_z, entry)` — no engine.c, no match_pattern_at
- `emit_pat()` / `pat_cat()` / `pat_arbno()` / `pat_ref()` → **eliminated from compiled path**
- `engine.c` / `snobol4_pattern.c` → interpreter only (EVAL). Never in beauty_full_bin.

**Reference:** SESSIONS_ARCHIVE.md Session 16 "Key insight from Lon" + "New Model: Locals Inside the Box"

---

## Architecture: Statement Execution Model (Session 27 Eureka)

**The entire SNOBOL4 statement IS a Byrd Box:**
```
label:  subject  pattern  =replacement  :S(x)  :F(y)
          α         →          γ           γ      ω
```

**Hot path** — pure Byrd Box gotos, zero overhead. No setjmp.
**Cold path** — `longjmp` for ABORT, FENCE bare, runtime errors ONLY.

### Three statement groupings for setjmp

**1. Individual statement** — own setjmp boundary. Line number implicit in catch.

**2. Glob sequence** — consecutive statements in a DEFINE body with NO internal
label targets (no statement is jumped to from outside) share ONE setjmp. This is
the key optimization: one `push_abort_handler` per function body, not per statement.
Statements that ARE label targets start a new setjmp boundary.

**3. Non-Gimpel DEFINE** — bare `DEFINE(...)` appearing mid-program as an executable
statement (not a function declaration) gets its OWN standalone setjmp guard, never
merged into a glob sequence, because its execution is conditional.

### Implementation status

| Feature | Status |
|---------|--------|
| Per-function setjmp | ✅ `emit.c` `emit_fn()` |
| `push/pop_abort_handler` + macros | ✅ `runtime_shim.h` |
| Per-statement setjmp | ❌ not done |
| Glob-sequence optimization | ❌ not done — needs reachability pass |
| Non-Gimpel DEFINE special case | ❌ not done |

**Reference:** SESSIONS_ARCHIVE.md Session 27, Session 26 "Statement IS a Byrd Box"
Full spec in PLAN.md "Architecture: Statement Execution Model"

---

## Architecture: Two Worlds

| World | Type | Failure | Entry |
|-------|------|---------|-------|
| **Byrd Box** | Pattern nodes (α/β/γ/ω) | Structured backtrack | `_alpha` |
| **DEFINE functions** | Regular C functions | `goto _SNO_FRETURN` | Normal call |

`T_FNCALL` wrapper is universal. All DEFINE'd functions save/restore on entry/exit.
All vars go through `sno_var_get`/`sno_var_set` — `is_fn_local` suppression was wrong, removed.

## Architecture Decisions (Locked)

| # | Decision |
|---|----------|
| D1 | Memory: Boehm GC |
| D2 | Tree children: realloc'd dynamic array |
| D3 | cstack: thread-local (`__thread MatchState *`) |
| D4 | Tracing: full implementation, doDebug=0 = zero cost |

## Build / Oracle Commands

```bash
make -C src/snoc
snobol4 -f -P256k -I $INC $BEAUTY < $BEAUTY > /tmp/beauty_oracle.sno
beauty_full_bin < $BEAUTY > /tmp/beauty_compiled.sno
diff /tmp/beauty_oracle.sno /tmp/beauty_compiled.sno   # empty = M-BEAUTY-FULL / M-COMPILED-SELF
bash test/smoke/test_snoCommand_match.sh                # target: 21/21
```
