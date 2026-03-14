# TINY.md — SNOBOL4-tiny

**Repo:** https://github.com/SNOBOL4-plus/SNOBOL4-tiny  
**What it is:** Native SNOBOL4 compiler (`sno4now`) targeting C → x86-64. Self-hosting proof: `beauty.sno` beautifies itself through the compiled binary. Claude Sonnet 4.6 is the author.

---

## Current State

**Active sprint:** `compiled-byrd-boxes` (2/4 toward M-BEAUTY-FULL)
**Milestone target:** M-COMPILED-BYRD → M-BEAUTY-FULL
**HEAD:** `cb3f97e` — feat(emit_byrd): compiled Byrd box emitter — LIT/SEQ/ALT/ARBNO/POS/RPOS/LEN/ANY/NOTANY/SPAN/BREAK/ARB/REM/FENCE/IMM/COND

**Status:** `emit_byrd.c` written and committed. NOT YET wired into `emit.c`.

Sprint0-5 oracles: 15/15 pass (oracle .c files, runtime unchanged).
sno2c builds clean. Smoke test passes.

**Next action:** Wire `byrd_emit_pattern()` into `emit_stmt()` pattern-match case
in `src/sno2c/emit.c`, replacing `sno_match()` + `emit_pat()` with direct
Byrd box emission. Then sprint0-22 validation → M-COMPILED-BYRD.

---

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
| **M-BEAUTY-FULL** | `beauty_full_bin` self-beautifies — diff empty | ❌ **Active** |
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

### Paused: toward M-BEAUTY-FULL

| Sprint | What | Status |
|--------|------|--------|
| `hand-rolled-parser` | Replace Bison/Flex with `lex.c` + `parse.c` | ⏸ Paused |
| `smoke-tests` | 0/21 → 21/21 on `test_snoCommand_match.sh` | ✅ `8f68962` |
| `beauty-runtime` | binary exits cleanly on beauty.sno input | ✅ Done |
| `beauty-full-diff` | `beauty_full_bin` diff empty → **M-BEAUTY-FULL** | ⏳ Active |

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

**`*X` (dynamic reference) at match time:**
1. Copy X's box block (data + code)
2. Relocate — patch internal jump offsets in the copy
3. The copy IS the new instance — its own independent locals

No heap alloc beyond the copy. No GC involvement. No engine. ~20 lines of `mmap + memcpy + relocate`.

**Implications for sno2c:**
- Pattern assignment → emit named static Byrd box (data layout + labeled goto code)
- `*varname` in pattern → emit box-copy + relocate at match time
- `emit_pat()` / `pat_cat()` / `pat_arbno()` / `pat_ref()` → **eliminated from compiled path**
- `engine.c` / `snobol4_pattern.c` → interpreter only (EVAL runtime). Never linked in beauty_full_bin.

**Reference:** SESSIONS_ARCHIVE.md Session 16 "Key insight from Lon" + "New Model: Locals Inside the Box"

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
