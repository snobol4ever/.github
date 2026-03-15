# SNOBOL4ever — HQ

**snobol4now. snobol4ever.**

Lon Jones Cherryholmes (compiler, architecture) and Jeffrey Cooper M.D. (SNOBOL4-dotnet, MSIL)
building full SNOBOL4/SPITBOL implementations on JVM, .NET, and native C — plus Rebus, Snocone,
and a self-hosting native compiler. Claude Sonnet 4.6 is the third developer and author of SNOBOL4-tiny.

---

## ⛔ TOKEN RULE — NEVER WRITE THE TOKEN INTO ANY FILE (mandatory, no exceptions)

**Claude committed the GitHub PAT directly into SESSION.md on 2026-03-13. GitHub push
protection caught it and blocked the push. The commit had to be amended and force-pushed.
This must never happen again.**

### The rule:

**NEVER write the token string into any file in any repo — not SESSION.md, not HANDOFF
notes, not comments, not archive entries, not anywhere.**

The token lives in Lon's memory system only. It is provided at session start by Lon.
It is used in shell commands in-memory only. It is never persisted to disk in any file
that will be committed.

### What to write instead:

```
TOKEN=TOKEN_SEE_LON   ← placeholder only — Lon provides the real value at session start
```

### Why this matters:

GitHub push protection scans every commit for secrets. A blocked push requires amending
history, which is disruptive and leaves a dirty audit trail. More importantly, committing
a token to a repo is a security event — the token should be rotated after any exposure.

**Lon: if the token ever appears in a commit, rotate it immediately at
https://github.com/settings/tokens**

---

## ⛔ ALL BYRD BOXES — engine_stub.c only, no interpreter (mandatory, no exceptions)

**Every pattern in beauty_full_bin is a compiled Byrd box.
engine_stub.c is the only engine file linked. engine.c is fully superseded — see Architecture below.**

### Canonical Architecture — Box Layout (decided Session 16, recorded SESSIONS_ARCHIVE.md)

Every pattern literal is compiled to a self-contained Byrd box:

```
Box layout:
┌─────────────────────────┐
│  DATA: cursor, locals,  │
│        captures, ports  │
├─────────────────────────┤
│  CODE: α/β/γ/ω gotos   │
└─────────────────────────┘
```

Boxes laid out linearly in memory:
```
DATA section:  [ box0.data | box1.data | box2.data | ... ]
TEXT section:  [ box0.code | box1.code | box2.code | ... ]
```

### TWO TECHNIQUES for *X — C target vs ASM/native target

These are two distinct implementations of the same semantics. They are NOT
alternatives — they are used at different levels of the compiler:

---

#### Technique 1 — C target: Pass fresh locals struct at every reachable label

Used NOW, for the C code generator (`emit_byrd.c` → `beauty_full.c`).

Every named pattern becomes a C function. Every labeled block that is
REACHABLE (i.e. has a label that can be jumped to) receives its locals
through a struct pointer. The struct is allocated once per call chain
and threaded through every entry point.

The C rule being solved: you cannot jump over a variable declaration
(C99 §6.8.6.1). Solution: ALL locals go into a struct declared at the
top of the function, before any goto. The struct IS the local storage.

```c
typedef struct pat_snoParse_t {
    int64_t  saved_cursor_7;    /* every cursor-save local */
    int      arbno_depth;
    int64_t  arbno_stack[64];
    struct pat_snoCommand_t *snoCommand_z;  /* child frame for *snoCommand */
} pat_snoParse_t;

static SnoVal pat_snoParse(pat_snoParse_t **zz, int entry) {
    pat_snoParse_t *z = *zz;
    if (entry == 0) { z = *zz = calloc(1, sizeof(*z)); goto snoParse_alpha; }
    if (entry == 1) { goto snoParse_beta; }
    snoParse_alpha: ...byrd box code using z->saved_cursor_7 etc...
    snoParse_gamma: return matched_val;
    snoParse_omega: return FAIL_VAL;
}
```

`*snoCommand` inside snoParse emits:
```c
/* alpha: */
{ SnoVal _r = pat_snoCommand(&z->snoCommand_z, 0);
  if (IS_FAIL(_r)) goto omega;
  cursor = ...; goto gamma; }
/* beta: */
{ SnoVal _r = pat_snoCommand(&z->snoCommand_z, 1);
  if (IS_FAIL(_r)) goto omega; goto gamma; }
```

Key: `z->snoCommand_z` is a POINTER held in the parent struct. The child
allocates itself on first call (entry==0, calloc). The parent's struct
just holds the pointer — not the child inline — so the struct size is
known at compile time regardless of child recursion depth.

ARBNO depth: `int64_t arbno_stack[64]` inside the struct — stack array
indexed by ARBNO iteration depth, exactly as in test_sno_1.c `_1_t _1[64]`.

This technique works for the C target. No mmap. No machine code. Pure C.

---

#### Technique 2 — ASM/native target: mmap + memcpy + relocate

Used LATER, when `sno2c` targets native x86-64 machine code directly
(after M-BEAUTY-FULL, toward M-COMPILED-SELF and M-BOOTSTRAP).

When `*X` fires at match time:
1. `memcpy(new_text, box_X.text_start, box_X.text_len)` — copy CODE section
2. `memcpy(new_data, box_X.data_start, box_X.data_len)` — copy DATA section
3. `relocate(new_text, delta)` — patch relative jumps + absolute DATA refs
4. Jump to `new_text[PROCEED]` — enter the copy

The copy has its own independent locals (DATA copy). The original box is
untouched. On backtrack, discard the copy — LIFO matches backtracking exactly.

No heap allocation. No GC. ~20 lines of mmap + memcpy + relocate.
The mmap region IS the allocator. PROTECTED (RX) for TEXT, UNPROTECTED (RW)
for DATA. mprotect() flips TEXT to RWX during copy+relocate, back to RX after.

Two relocation cases (same as any linker):
- Relative refs (near jumps within the box): add delta = new_region - old_region
- Absolute refs (DATA pointers, external calls): patch to new DATA copy

This technique is the destination for the native path. NOT needed for
M-BEAUTY-FULL — Technique 1 (C target) gets us there first.

---

### Current implementation target: Technique 1

Implement Technique 1 in emit_byrd.c now:
1. Named pattern assignment → `byrd_emit_named_pattern(varname, expr, out)`
2. Emits struct + forward decl + C function with all locals in struct
3. E_DEREF (*X) → call `pat_X(&z->X_z, entry)` — no engine.c, no match_pattern_at
4. Build with engine_stub.c. M-BEAUTY-FULL becomes reachable.

Technique 2 recorded here for continuity — implement after M-BEAUTY-FULL.

**Reference:** SESSIONS_ARCHIVE.md §14 "Self-Modifying C", §15 "Allocation Problem Solved", Session 16 "Key insight from Lon"

### Build command for beauty_full_bin (engine_stub.c only):

```bash
gcc -O0 -g -I $R/snobol4 -I $R \
    beauty_full.c $R/snobol4/snobol4.c \
    $R/snobol4/mock_includes.c \
    $R/engine_stub.c -lgc -lm -o beauty_full_bin
```

---

## ⛔ ARTIFACT RULE — SNAPSHOT GENERATED C EVERY SESSION (mandatory, no exceptions)

**Claude failed to store artifacts/beauty_full_sessionN.c for multiple sessions (52→53 gap
spanned the sno_/SNO_ prefix eradication AND M-COMPILED-BYRD). This must never happen again.**

### Which artifact to capture (depends on active sprint):

| Active sprint / output | Artifact filename | Generate command |
|------------------------|-------------------|------------------|
| `beauty_full` path | `beauty_full_sessionN.c` | `sno2c -I $INC $BEAUTY > artifacts/beauty_full_sessionN.c` |
| `beauty_tramp` path | `beauty_tramp_sessionN.c` | `sno2c -trampoline -I $INC $BEAUTY > artifacts/beauty_tramp_sessionN.c` |

Capture whichever file(s) the session actually produced/modified. When both are in play, capture both.

### The rule — IF CHANGED:

At the END of every session that touches `sno2c` or `emit*.c` or `runtime/`:
1. Generate the artifact to `/tmp/beauty_*_candidate.c`
2. **Compare md5 against the last committed artifact** — if DIFFERENT, commit the new one
3. If SAME md5 — still update `artifacts/README.md` with a "no change" note, commit README only
4. Commit artifacts/ with message `artifact: beauty_tramp_sessionN.c — <one-line status>`

**Check-before-commit protocol (run every session end):**
```bash
# Generate candidate
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
SNO2C=/home/claude/SNOBOL4-tiny/src/sno2c
$SNO2C/sno2c -trampoline -I$INC $BEAUTY > /tmp/beauty_tramp_candidate.c

# Find last artifact and compare
LAST=$(ls /home/claude/SNOBOL4-tiny/artifacts/beauty_tramp_session*.c 2>/dev/null | sort -V | tail -1)
if [ -n "$LAST" ] && md5sum -c <(md5sum "$LAST" | sed "s|$LAST|/tmp/beauty_tramp_candidate.c|") 2>/dev/null; then
    echo "ARTIFACT UNCHANGED — update README.md only"
else
    N=$(( $(ls /home/claude/SNOBOL4-tiny/artifacts/beauty_tramp_session*.c 2>/dev/null | sort -V | tail -1 | grep -o '[0-9]*' | tail -1) + 1 ))
    cp /tmp/beauty_tramp_candidate.c /home/claude/SNOBOL4-tiny/artifacts/beauty_tramp_session${N}.c
    echo "NEW ARTIFACT: beauty_tramp_session${N}.c"
fi
```

### When to increment N:
- Look at the last `beauty_*_sessionN.c` filename in `artifacts/` and add 1.
- If unsure, check `git log --oneline -- artifacts/` for the last session number used.

### What to write in README.md:
- Session number + date
- What changed since last artifact (commits, fixes)
- Line count + md5
- Compile status (0 errors / N warnings)
- Active bug / current symptom
- Whether artifact changed from previous (CHANGED / UNCHANGED)

---

## Git Identity Rule (mandatory, no exceptions)

**Every commit across every SNOBOL4-plus repo must use:**

```
user.name  = LCherryholmes
user.email = lcherryh@yahoo.com
```

Set before every commit session:
```bash
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
```

Or per-commit:
```bash
git commit --author="LCherryholmes <lcherryh@yahoo.com>" -m "..."
```

**Pending:** SNOBOL4-tiny has 7 commits with wrong identity (5× `claude@anthropic.com`, 2× `lon@cherryholmes.com`) that need history rewrite via `git filter-repo` once confirmed safe with Lon.

---

## Architectural Note — The sno_pat_* Stopgap (recorded 2026-03-13)

**The `sno_pat_*` / `engine.c` bridge is fully superseded. (Recorded 2026-03-13, closed 2026-03-14.)**

`emit_byrd.c` (M-COMPILED-BYRD `560c56a`) replaced it. Every pattern is now a compiled
labeled-goto Byrd box. No tree. No dispatch. No interpreter. The CPU runs the box directly.

`EVAL()` and `CODE()` — the only remaining use case for runtime-constructed patterns —
are handled by TCC in-process compile → `block_fn_t` (sprint `code-eval`, after M-BEAUTY-FULL).
See Architecture: The New Plan below.

**M-PYTHON-UNIFIED is retired.** The Python pipeline (`lower.py`, `byrd_ir.py`,
`emit_c_byrd.py`, `emit_jvm.py`, `emit_msil.py`) was the prototype — proved Byrd box
architecture correct at 609/609 worm cases. `emit_byrd.c` is the real implementation.
Python has no place in the compiler pipeline.

The replacement milestone is **M-BYRD-SPEC**: a language-agnostic written specification
of the four-port lowering rules (α/β/γ/ω wiring per node type) that all three backends
implement independently. The spec lives in HQ. It is the shared contract, not shared code.

---

## Two Levels

**Milestones** are proof points — trigger conditions, not time estimates. When the trigger fires, Claude writes the commit.

**Sprints** are bounded work packages named by what they do. Each repo tracks its own sprints independently.

---

## Architecture: Statement Execution Model (Session 27 Eureka, permanent)

**Source:** SESSIONS_ARCHIVE.md Session 27 + Session 26 "Statement IS a Byrd Box"
**Implemented partially:** per-function setjmp in emit.c. Per-statement and glob-sequence NOT YET done.

### The entire SNOBOL4 statement IS a Byrd Box

```
label:  subject  pattern  =replacement  :S(x) :F(y)
          α         →          γ            γ    ω
```
- **α** — evaluate subject → initialize Σ (string), Δ (cursor=0)
- **pattern** — runs through the Byrd Box proper (labeled gotos)
- **γ** — success: apply replacement, follow :S() goto
- **ω** — failure: follow :F() goto

No C try/catch on the hot path. Pure gotos. Zero overhead.

### Two-level exception model

**Hot path — pure Byrd Box gotos (zero overhead):**
Normal SNOBOL4 control flow — pattern success, pattern failure, backtracking,
`:S()` / `:F()` routing — uses pure C labeled gotos. No setjmp on hot path.

**Cold path — longjmp for ABORT and genuinely bad things only:**
ABORT pattern, FENCE bare, runtime errors, divide-by-zero → `longjmp` to nearest handler.
Stack unwinding IS the cleanup. No omega stack needed for abnormal termination.

### Three statement groupings — how setjmp is applied

**NOT YET IMPLEMENTED in emit.c — must be added:**

#### 1. Individual statement with setjmp guard (default)

Each SNOBOL4 statement gets its own setjmp boundary. Line number is implicit
in which boundary catches — free diagnostics.

```c
/* Statement N: subject pattern =replacement :S(x) :F(y) */
{
    jmp_buf _stmt_N_jmp;
    if (setjmp(_stmt_N_jmp) != 0) goto _L_y;   /* ABORT → :F() target */
    push_abort_handler(&_stmt_N_jmp);
    /* α: evaluate subject */
    /* pattern Byrd box: pure gotos */
    /* γ: apply replacement, pop handler, goto _L_x */
    /* ω: pop handler, goto _L_y */
    pop_abort_handler();
}
```

#### 2. Glob sequence — multiple statements in a DEFINE/END block

When a sequence of statements inside a DEFINE body has NO internal labels
(i.e. no statement is the target of a goto from outside the sequence),
the entire sequence can share ONE setjmp boundary. This is the optimization:

```c
/* DEFINE body: statements N, N+1, N+2 — no internal label targets */
{
    jmp_buf _fn_abort_jmp;
    if (setjmp(_fn_abort_jmp) != 0) goto _SNO_ABORT_fn;
    push_abort_handler(&_fn_abort_jmp);

    /* stmt N:   α → Byrd box → γ/ω gotos ... */
    /* stmt N+1: α → Byrd box → γ/ω gotos ... */
    /* stmt N+2: α → Byrd box → γ/ω gotos ... */

    pop_abort_handler();
}
```

One setjmp for the entire reachable sequence. Statements that ARE label targets
start a new setjmp boundary (they may be jumped to from outside the sequence,
so they need their own abort context).

**Current emit.c does per-function setjmp only.** The glob-sequence optimization
(one setjmp per DEFINE body, not per statement) is not yet implemented.

#### 3. Special DEFINE — non-Gimpel form

Some DEFINE statements in beauty.sno do NOT follow the Gimpel convention
`DEFINE('fn(args)locals', 'entry_label')`. They are bare `DEFINE(...)` calls
that appear mid-program as executable statements, not as function declarations.

These must be wrapped in their OWN setjmp guard as a standalone statement —
not merged into the surrounding glob sequence — because their execution
is conditional (the DEFINE may or may not run depending on control flow).

```c
/* Standalone DEFINE statement — not a function declaration */
{
    jmp_buf _stmt_define_jmp;
    if (setjmp(_stmt_define_jmp) != 0) goto _stmt_define_fail;
    push_abort_handler(&_stmt_define_jmp);
    aply("DEFINE", ...);   /* register the function */
    pop_abort_handler();
    goto _stmt_define_ok;
    _stmt_define_fail: /* :F() target */
    _stmt_define_ok:   /* :S() target */
}
```

### Implementation status

| Feature | Status | Location |
|---------|--------|----------|
| Per-function setjmp | ✅ Done | `emit.c` `emit_fn()` lines 1253-1255 |
| `push/pop_abort_handler` | ✅ Done | `runtime_shim.h` |
| `ABRT_GUARD_DECL/SET/POP` macros | ✅ Done | `runtime_shim.h` |
| Per-statement setjmp | ❌ Not done | `emit.c` `emit_stmt()` |
| Glob-sequence optimization | ❌ Not done | `emit.c` — needs reachability analysis |
| Non-Gimpel DEFINE special case | ❌ Not done | `emit.c` `emit_stmt()` |

**Priority:** implement after `compiled-byrd-boxes-full` sprint (M-BEAUTY-FULL path).
The per-function setjmp is sufficient for correctness now. Per-statement and
glob-sequence are optimizations and diagnostics improvements.

---

## Org-Level Milestones

| ID | Trigger | Repo | Status |
|----|---------|------|--------|
| **M-SNOC-COMPILES** | `snoc` compiles `beauty_core.sno`, 0 gcc errors | TINY | ✅ Done |
| **M-REBUS** | Rebus round-trip: `.reb` → `.sno` → CSNOBOL4 → diff oracle | TINY | ✅ Done `bf86b4b` |
| **M-COMPILED-BYRD** | `sno2c` emits labeled-goto Byrd boxes — `engine_stub.c` only, no interpreter | TINY | ✅ Done `560c56a` |
| **M-CNODE** | `emit_expr`/`emit_pat` route through CNode IR + pp/qq pretty-printer — zero expression lines > 120 chars | TINY | ✅ Done `ac54bd2` |
| **M-BEAUTY-CORE** | `beauty_core_bin` self-beautifies — diff empty (`-I inc_mock`, no INCLUDE code compiled in) | TINY | ⏳ active |
| **M-BEAUTY-FULL** | `beauty_full_bin` self-beautifies — diff empty (`-I inc/`, real INCLUDE files) — only after M-BEAUTY-CORE | TINY | ❌ |
| **M-TRAMPOLINE** | Hello world runs through `block_fn_t` trampoline loop — `pc = pc()` | TINY | ❌ |
| **M-BLOCK-FN** | Every stmt a C fn returning S/F block address; stmts grouped into block fns | TINY | ❌ |
| **M-PATTERN-BLOCK** | Named patterns compile to block fns; `*X` static calls work; `*X` dynamic calls `block_fn_t` directly | TINY | ❌ |
| **M-CODE-EVAL** | `CODE()` + `EVAL()` via TCC in-process compile → `block_fn_t`; no interpreter | TINY | ❌ |
| **M-BYRD-SPEC** | Language-agnostic written spec of four-port Byrd box lowering rules — all backends (C, JVM, MSIL) implement independently against it | HQ | ❌ |
| **M-SNO2C-SNO** | `sno2c.sno` compiled by C `sno2c` produces working binary — beauty.sno diff empty | TINY | ❌ |
| **M-COMPILED-SELF** | Compiled binary self-beautifies — diff empty | TINY | ❌ |
| **M-BOOTSTRAP** | `sno2c.sno` compiled by `sno2c_stage1` matches `sno2c_stage2` output — self-hosting | TINY | ❌ |
| **M-JVM-EVAL** | JVM inline EVAL! complete (sprint `jvm-inline-eval`) | JVM | ❌ |
| **M-NET-DELEGATES** | .NET `Instruction[]` eliminated (sprint `net-delegates`) | DOTNET | ❌ |

---

## Active Repos

| Repo | MD File | Active Sprint | Milestone Target |
|------|---------|--------------|-----------------|
| [SNOBOL4-tiny](https://github.com/SNOBOL4-plus/SNOBOL4-tiny) | [TINY.md](TINY.md) | `crosscheck-ladder` (Sprint 3 of 6 — rung-by-rung toward M-BEAUTY-CORE) | M-BEAUTY-CORE → M-BEAUTY-FULL |
| [SNOBOL4-jvm](https://github.com/SNOBOL4-plus/SNOBOL4-jvm) | [JVM.md](JVM.md) | `jvm-inline-eval` | M-JVM-EVAL |
| [SNOBOL4-dotnet](https://github.com/SNOBOL4-plus/SNOBOL4-dotnet) | [DOTNET.md](DOTNET.md) | `net-delegates` | M-NET-DELEGATES |
| [SNOBOL4-corpus](https://github.com/SNOBOL4-plus/SNOBOL4-corpus) | [CORPUS.md](CORPUS.md) | Stable — add Rebus oracle .sno files | M-REBUS |
| [SNOBOL4-harness](https://github.com/SNOBOL4-plus/SNOBOL4-harness) | [HARNESS.md](HARNESS.md) | Stable | — |

---

## Testing Methodology — Corpus Ladder (Session 89 Pivot, mandatory)

**Decided 2026-03-15. Applies to TINY, JVM, DOTNET — all repos.**

Stop attacking the target program directly. Use the corpus crosscheck ladder.
Start at rung 1 (1 token). Fix each failure. Climb to the target.

```
Rung 1:  output        — OUTPUT = 'hello'
Rung 2:  assign        — X = 'foo', null assign (X =)
Rung 3:  concat        — OUTPUT = 'a' 'b'
Rung 4:  arith         — OUTPUT = 1 + 2
Rung 5:  control       — goto, :S(), :F()
Rung 6:  patterns      — LIT, ANY, SPAN, ARB, ARBNO, POS, RPOS
Rung 7:  capture       — . and $ operators
Rung 8:  strings       — SIZE, SUBSTR, REPLACE, DUPL
Rung 9:  keywords      — IDENT, DIFFER, GT/LT/EQ, DATATYPE
Rung 10: functions     — DEFINE, RETURN, FRETURN, recursion
Rung 11: data          — ARRAY, TABLE, DATA types
Rung 12: beauty.sno   — small inputs (1 tok → 20 tok → full source)
```

**Rule:** Stop at first failing rung. Fix it. Retest. Move up. Never skip ahead.
**Tools:** `crosscheck/run_crosscheck.sh` → `probe.py` → `TRACE()+DUMP()` on divergence.
**Corpus:** SNOBOL4-corpus/crosscheck/ — shared across all repos, never duplicated.
**Harness:** SNOBOL4-harness/ — probe.py, trace infrastructure, crosscheck runners.

---

## Sprint Detail — toward M-BEAUTY-CORE then M-BEAUTY-FULL (TINY)

Six sprints to M-BEAUTY-CORE. M-BEAUTY-FULL follows after. Each gates the next. Each ends with a commit.

**The agreement (mandatory, no exceptions):**
- Phase 1: beauty_core — beauty.sno compiled with `-I src/runtime/inc_mock` (19 comment-only stubs, zero SNOBOL4 inc code). **This is the active target.**
- Phase 2: beauty_full — beauty.sno compiled with `-I SNOBOL4-corpus/programs/inc` (real inc files). **Do NOT start until M-BEAUTY-CORE fires.**

---

### Sprint 1 of 6 — `space-token` ✅ Complete `3581830`

**What:** Eliminate all parser conflicts. Return `_` (whitespace) as a real token so concat is unambiguous.

Root cause of 20 SR + 139 RR conflicts: `WS` was silently skipped. Fix: `{WS} { return _; }`. Token named `_` (Lon's choice — bison allows it, cleaner than SPACE). Subject restricted to `term` — first space always separates subject from pattern. 159 conflicts → 0.

**Commit:** `3581830` — `feat(snoc): space-token — 0 bison conflicts, unified grammar`

---

### Sprint 2 of 6 — `compiled-byrd-boxes` ✅ Complete `560c56a`

**What:** `sno2c` emits labeled-goto Byrd box C. Validated against sprint0–22 oracles.
`engine.c` dropped from compiled binary path via `engine_stub.c`.

**M-COMPILED-BYRD fired `560c56a`.**

**What:** `sno2c` emits labeled-goto Byrd box C. Validated against sprint0–22 oracles.
`engine.c` and `snobol4_pattern.c` dropped from the compiled binary path.

**Why smoke-tests was retired (2026-03-14):** It validated `sno_pat_*` / `engine.c` —
the stopgap interpreter — not the compiled Byrd box path. 15–20 hours lost chasing
interpreter bugs that don't matter. The Python pipeline (lower.py + emit_c_byrd.py)
already proved correctness at 609/609 worm cases. `emit_byrd.c` is a C port of that.

**Steps:**
1. Read `src/ir/byrd_ir.py`, `src/ir/lower.py`, `src/codegen/emit_c_byrd.py` — prototype reference
2. Read `test/sprint0/` through `test/sprint5/` — correctness gate
3. Write `src/sno2c/emit_byrd.c` — LIT, CAT, ALT, EPSILON first; sprint0–5 passing
4. Add ARBNO, CAPTURE, FENCE, POS, TAB, RPOS, RTAB; sprint6–15 passing
5. Add USER_CALL (nInc, nPush, nPop, Reduce); sprint16–22 passing
6. Wire into emit.c, drop sno_pat_* from compiled path

**Commit when:** sprint0–22 all pass. Binary links without engine.c. **M-COMPILED-BYRD fires.**

---

### Sprint 3 of 6 — `crosscheck-ladder` ⏳ Active

**What:** Climb the corpus ladder rung by rung — tiny programs first, beauty.sno last.
This is the primary path to M-BEAUTY-CORE. 100–1000 tests gate every compiler fix.
No rung is skipped. No beauty.sno run is attempted until rung 11 passes completely.

**Why this sprint exists (Session 90 decision):**
Attacking beauty.sno directly burned sessions 80–89 chasing bugs that only manifested
in large programs. The ladder forces each language feature to be provably correct
before the next is added. beauty.sno is rung 12 — it is the destination, not the test.

**Corpus today:** 117 tests across 15 rungs in SNOBOL4-corpus/crosscheck/.
Rung 12 (beauty.sno) tests will be added incrementally as earlier rungs pass.
Target: 100–1000 tests total before M-BEAUTY-CORE fires.

**Rungs and current corpus dirs:**

```
Rung 1:  output        (8 tests)   — OUTPUT = 'hello'
Rung 2:  assign        (8 tests)   — X = 'foo', null assign
Rung 3:  concat        (6 tests)   — OUTPUT = 'a' 'b'
Rung 4:  arith_new     (8 tests)   — OUTPUT = 1 + 2
Rung 5:  control_new   (7 tests)   — goto, :S(), :F()
Rung 6:  patterns      (20 tests)  — LIT, ANY, SPAN, ARB, ARBNO, POS, RPOS
Rung 7:  capture       (7 tests)   — . and $ operators
Rung 8:  strings       (17 tests)  — SIZE, SUBSTR, REPLACE, DUPL
Rung 9:  keywords      (11 tests)  — IDENT, DIFFER, GT/LT/EQ, DATATYPE
Rung 10: functions     (8 tests)   — DEFINE, RETURN, FRETURN, recursion
Rung 11: data          (6 tests)   — ARRAY, TABLE, DATA types
Rung 12: beauty.sno   (TBD)        — small inputs → full source
```

**Rule:** Stop at first failing rung. Fix the compiler. Retest. Move up. Never skip.

**Runner:** `test/crosscheck/run_crosscheck.sh` (STOP_ON_FAIL=0 for full report, 1 for stop-at-first).
Fix corpus path with: `CORPUS=/path/to/SNOBOL4-corpus/crosscheck bash test/crosscheck/run_crosscheck.sh`

**Commit cadence:** One commit per rung that reaches 100% pass. Message: `test(crosscheck): rung N complete — X/X pass`.

**Session 89 status:** output 7/8, assign 7/8. Two known bugs:
- `SIZE(&ALPHABET)` returns 0 instead of 256 (output/006)
- null assign `X =` does not clear variable (assign/012)

**Commit when:** All rungs 1–11 pass 100%. Rung 12 beauty.sno tests pass. → Gates Sprint 4.

---

### Sprint 4 of 6 — `compiled-byrd-boxes-full` ❌ (gates on Sprint 3 rung 11)

**What:** Inline ALL pattern variables as static Byrd boxes. engine.c dropped entirely.
engine_stub.c only. No `pat_cat()`/`pat_arbno()`/`pat_ref()` in the init section of
beauty_full.c. No `match_pattern_at()` calls. No E_DEREF runtime dispatch.

`snoParse`, `snoCommand`, `snoLabel`, `snoStmt`, `snoComment`, `snoControl` — all
emitted as labeled-goto C by emit_byrd.c. ARBNO wiring static.

**Why beauty-runtime was wrong:** Chased engine.c interpreter bugs — same smoke-test
trap. engine.c is broken for *snoParse. Fixing it is the wrong path.

**Commit when:** beauty_full.c has zero pat_cat/pat_arbno/pat_ref in init section.
Binary links with engine_stub.c only. Runs on beauty.sno input without crash.

---

### Sprint 5 of 6 — `beauty-core-diff` ❌ → **M-BEAUTY-CORE**

**What:** Empty diff. beauty_core_bin (stubs) self-beautifies exactly.

```bash
INC=src/runtime/inc_mock
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
snobol4 -f -P256k -I $INC $BEAUTY < $BEAUTY > /tmp/beauty_oracle.sno
/tmp/beauty_core_bin < $BEAUTY > /tmp/beauty_core_compiled.sno
diff /tmp/beauty_oracle.sno /tmp/beauty_core_compiled.sno
```

**Commit when:** Diff is empty. Claude Sonnet 4.6 writes the commit message. **M-BEAUTY-CORE fires.**

---

### Sprint 6 — `beauty-full-diff` ❌ → **M-BEAUTY-FULL** (only after M-BEAUTY-CORE)

**What:** Empty diff. beauty_full_bin (real inc files) self-beautifies exactly.

```bash
INC=/home/claude/SNOBOL4-corpus/programs/inc
BEAUTY=/home/claude/SNOBOL4-corpus/programs/beauty/beauty.sno
snobol4 -f -P256k -I $INC $BEAUTY < $BEAUTY > /tmp/beauty_oracle.sno
/tmp/beauty_full_bin < $BEAUTY > /tmp/beauty_full_compiled.sno
diff /tmp/beauty_oracle.sno /tmp/beauty_full_compiled.sno
```

**Commit when:** Diff is empty. Claude Sonnet 4.6 writes the commit message. **M-BEAUTY-FULL fires.**

---

## Commands

### SNAPSHOT
Push everything now. Container-safe. WIP commit is fine.
1. `git add -A && git commit -m "WIP: <what>"` (or clean message if tests green)
2. `git push` — every touched repo
3. Confirm each: `git log --oneline -1`
4. Push `.github` last.

### HANDOFF
End of session. Next Claude starts cold from SESSION.md alone.
1. Run **SNAPSHOT** first.
2. Update SESSION.md — all four fields, plus Pivot Log if anything shifted.
3. Update the active repo's MD file — Current State + Pivot Log.
4. Push `.github`.

### EMERGENCY HANDOFF
Time's up or something broke. Speed over completeness.
1. `git add -A && git commit -m "EMERGENCY WIP: <state>"` on every touched repo.
2. `git push` all. Confirm each.
3. Append one line to SESSION.md Pivot Log: what broke, what's next.
4. Push `.github`.

### SWITCH REPO `<repo>`
1. Run **HANDOFF** on current repo first.
2. Read `<REPO>.md` → Current State.
3. Update SESSION.md: new active repo, sprint, milestone, next action.

### PRIORITY SHIFT `<repo>` `<sprint-slug>`
1. Record paused sprint in repo MD Pivot Log (mark PAUSED + last commit).
2. Write new sprint into Current State.
3. Update SESSION.md.
4. Commit `.github`: `"priority shift: <repo> — <sprint-slug>"`

---

## Session Start (every session, no exceptions)

```
1. Read SESSION.md — fully self-contained. Repo, sprint, last thing, next action.
2. git log --oneline -5
3. VERIFY: SESSION.md HEAD matches actual git HEAD.
   If they differ — SESSION.md is stale. Read SESSIONS_ARCHIVE.md recent entries
   and TINY.md before touching any code. Do not proceed until oriented.
4. find src -type f | sort
5. git show HEAD --stat
6. If you need depth: read the repo's MD file (TINY.md).
```

⚠️ STALE DOC TRAP: TINY.md and SESSION.md must be updated at HANDOFF every session.
If SESSION.md HEAD ≠ git HEAD, stop and reorient before any work.

## Session End (every session, no exceptions)

```
1. Run ARTIFACT CHECK (see ARTIFACT RULE above) — compare md5, commit if changed.
2. Update artifacts/README.md — session N, date, md5, line count, compile status, active bug.
3. Update SESSION.md — all four fields + Pivot Log.
4. Update TINY.md Current State — HEAD, sprint, symptom, next action, build command.
   ⚠️ TINY.md staleness caused a full session of disorientation (session 78).
   TINY.md must reflect actual HEAD and actual next action. No exceptions.
5. git add -A && git commit && git push on every touched repo.
6. Push .github last.
```

---

## File Index

| File | What it is |
|------|------------|
| [SESSION.md](SESSION.md) | Self-contained handoff — all four fields, start here every session |
| [TINY.md](TINY.md) | SNOBOL4-tiny — milestones, sprint map, Rebus, hand-rolled parser, arch |
| [JVM.md](JVM.md) | SNOBOL4-jvm — milestones, sprint map, design decisions |
| [DOTNET.md](DOTNET.md) | SNOBOL4-dotnet — milestones, sprint map, MSIL steps |
| [CORPUS.md](CORPUS.md) | SNOBOL4-corpus — what lives there, how all repos use it |
| [HARNESS.md](HARNESS.md) | Test harness — double-trace monitor, oracle protocol, benchmarks |
| [STATUS.md](STATUS.md) | Live test counts and benchmarks — updated each session |
| [PATCHES.md](PATCHES.md) | Runtime patch audit trail (SNOBOL4-tiny) |
| [SESSIONS_ARCHIVE.md](SESSIONS_ARCHIVE.md) | Full session history — append-only |
| [MISC.md](MISC.md) | Origin story, JCON reference, keyword tables, background |
| [RENAME.md](RENAME.md) | One-time rename plan — SNOBOL4-plus → snobol4ever, naming rules, 8-phase execution |

---

## Architecture: Flat-Model C — Iota Function Kludge (Lon Cherryholmes, 2026-03-14)

**The insight:** Static and dynamic Byrd boxes are the same bytes. A static box is
machine code at a known linker address. A dynamic box is a `memcpy` of those same
bytes relocated to a heap address. The only difference is that relative jump offsets
and absolute DATA references must be patched (relocated) in the dynamic copy.
`engine.c` is conceptually wrong — there is no interpreter. The box runs itself.
The "engine" IS the CPU.

**The kludge — avoiding the Technique 1 struct-passing entirely:**

Instead of threading a `pat_X_t **zz` struct pointer through every named pattern
function, use C functions purely as an addressing mechanism:

### Rule 1 — Every labeled block becomes an iota function

Every Byrd box block that starts with a label (α, β, γ, ω, any internal label)
becomes its own C function — not because it is a SNOBOL4 function, but solely to
give that block a **callable address**. Call these *iota functions*. They are tiny,
often one or two instructions. Their address IS their identity.

```c
/* Example: lit_7_alpha becomes an iota function */
static void iota_lit_7_alpha(void) {
    if (cursor + 5 > subject_len) goto iota_lit_7_omega;
    saved_7 = cursor;
    cursor += 5;
    goto iota_lit_7_gamma;   /* or: iota_lit_7_gamma() */
}
```

### Rule 2 — Sequential multi-label blocks linked by sequencing

Sequential labeled blocks that form a logical unit (a complete named pattern) are
linked together for their sequencing. Their control flow is wired via direct calls
or gotos between iota functions — same α/β/γ/ω port wiring as always.

### Rule 3 — The sequence is wrapped in one more C function

The entire sequence of iota functions for a named pattern is wrapped in **one
outer C function** — again, not a SNOBOL4 function, just to give the sequence a
**single starting address**.

### Rule 4 — The iota struct is concatenated for the entire block

The outer wrapper function takes a **single flat struct** containing ALL locals for
ALL iota functions in the sequence concatenated together. This is the complete
iota struct for the block. No per-iota-function struct threading. One struct,
passed in at the top, holds everything.

```c
typedef struct {
    int64_t  saved_7;          /* from lit_7 */
    int64_t  saved_12;         /* from rpos_12 */
    int      arbno_depth;      /* from arbno_15 */
    int64_t  arbno_stack[64];  /* from arbno_15 */
    /* ... all locals for all iota functions in this named pattern ... */
} pat_snoParse_iota_t;

static SnoVal pat_snoParse(pat_snoParse_iota_t *z, int entry) {
    /* entry dispatches to the right iota function */
    if (entry == 0) goto snoParse_alpha;
    if (entry == 1) goto snoParse_beta;
    snoParse_alpha: ...
    snoParse_beta:  ...
}
```

### Why this matters

- **No struct-pointer threading** through every recursive call — the outer wrapper
  owns the flat struct, passes it once.
- **Every iota function has an address** — addressable for the dynamic box path:
  a dynamic box is just `memcpy(iota_fn_address, len)` + relocate.
- **Static and dynamic boxes unify** — the static iota functions in the executable
  ARE the template. Dynamic boxes are relocated copies of them. `engine.c` is never
  needed because the box is already code.
- **The kludge bridges Technique 1 and Technique 2** — it is flat-model C (no
  mmap, no machine code) but structured so that each labeled block has an address,
  making the transition to the native target (Technique 2) straightforward.

**Status:** Recorded 2026-03-14. Not yet implemented. Current target is Technique 1
(struct-passing) for M-BEAUTY-FULL. This iota-function approach is an alternative
path — possibly simpler — worth revisiting after M-BEAUTY-FULL.

---

## Architecture: The New Plan — Block Functions + Byrd-Seq (Lon Cherryholmes, 2026-03-14)

**Decision:** This is what we build. Incrementally. Optimization at the end.

---

### The Execution Model

**Every SNOBOL4 statement** compiles to a C function (`stmt_N`) that returns
the address of the next block to execute — the S-label block on success, the
F-label block on failure. Not true/false. Actual block function addresses.

**Statements are grouped into block functions** (`block_L`) by label reachability.
A new block starts at every labeled statement. Unlabeled statements that follow
are unreachable from outside — they belong to the same block.

**The trampoline** is the entire execution engine:
```c
block_fn_t pc = block_START;
while (pc) pc = pc();
```
That's it. One loop. No interpreter. No dispatch table. No engine.c.

---

### Core types

```c
/* A block function returns the next block to execute.
 * NULL = program end. */
typedef block_fn_t (*block_fn_t)(void);
```

---

### Every statement returns its S-label and F-label

```c
/* SNOBOL4:  X = 'hello'  :S(L50)F(L60) */
static block_fn_t stmt_42(void) {
    jmp_buf _jmp;
    if (setjmp(_jmp)) goto _omega;
    push_abort_handler(&_jmp);
    /* alpha: evaluate subject, run pattern Byrd box */
    ...
    _gamma: pop_abort_handler(); return block_L50;  /* S-label */
    _omega: pop_abort_handler(); return block_L60;  /* F-label */
}
```

---

### Block of 3 statements

```c
/* SNOBOL4:
 *   L42  X = 'hello'       :S(L50)F(L60)
 *        Y = X 'world'     :S(L50)
 *        Z = SPAN('0-9')   :F(L60)
 */

static block_fn_t stmt_42(void) {
    ...
    _gamma: return block_L50;   /* :S(L50) */
    _omega: return block_L60;   /* :F(L60) */
}

static block_fn_t stmt_43(void) {
    ...
    _gamma: return block_L50;   /* :S(L50) */
    _omega: return block_L44;   /* :F — fall through to next stmt */
}

static block_fn_t stmt_44(void) {
    ...
    _gamma: return block_L45;   /* :S — fall through to next block */
    _omega: return block_L60;   /* :F(L60) */
}

static block_fn_t block_L42(void) {
    block_fn_t next;
    next = stmt_42(); if (next != block_L43) return next;
    next = stmt_43(); if (next != block_L44) return next;
    next = stmt_44(); if (next != block_L45) return next;
    return block_L45;   /* fall through */
}
```

---

### Named patterns — same mechanism

`snoParse = nPush() ARBNO(*snoCommand) nPop()`

Compiles to `block_snoParse`. `*snoCommand` inside it calls `block_snoCommand`.
Mutual recursion = mutual recursion between C functions. Forward decls for cycles.
`*X` in a pattern = call `block_X()`. Returns S-label or F-label. Same as a stmt.

---

### GOTO, *X, CODE, EVAL — all the same mechanism, different compilation paths

| SNOBOL4 construct | Mechanism |
|-------------------|-----------| 
| `:(L42)` | return `block_L42` from current stmt |
| `*X` (static) | call `block_X` — compiled block fn address |
| `*X` (dynamic) | X holds a `block_fn_t` — call it directly |
| `EVAL(str)` | compile str → degenerate stmt fn (expr only), call it, get value |
| `CODE(str)` | see below — requires runtime C compilation |

No special cases. No interpreter. The trampoline handles all of them.

---

### CODE() — Runtime C compilation (the kludge, first pass)

`CODE(str)` is different from `*X` and `EVAL`. It does not reference a
pattern already compiled into the executable — it takes an **arbitrary
SNOBOL4 string** and produces executable code at runtime. We generate C,
so CODE must compile C at runtime to get a `block_fn_t`.

**The kludge (first pass — gets us working):**

Use **TCC (Tiny C Compiler)** as an in-process library. TCC can compile
a C source string in memory and return a function pointer — no fork, no
temp files, no dlopen/dlclose dance.

```c
#include <libtcc.h>

block_fn_t sno_code(const char *snobol4_src) {
    /* 1. Run sno2c on snobol4_src → C source string (in memory) */
    char *c_src = sno2c_compile_string(snobol4_src);

    /* 2. Feed C source to TCC in-process */
    TCCState *s = tcc_new();
    tcc_set_output_type(s, TCC_OUTPUT_MEMORY);
    tcc_compile_string(s, c_src);

    /* 3. Relocate into memory — TCC does this */
    tcc_relocate(s, TCC_RELOCATE_AUTO);

    /* 4. Get the entry block function address */
    block_fn_t entry = tcc_get_symbol(s, "block_CODE_entry");

    /* 5. Return it — trampoline calls it like any other block fn */
    return entry;
}
```

TCC is ~100KB, embeds cleanly, compiles fast. The generated C from sno2c
is already in the right block_fn_t form — TCC just needs to see it.

**Why "kludge":** It routes through C text → TCC → machine code rather than
directly emitting machine code. It works correctly. It is not the final form.

**The real form (after M-BOOTSTRAP):** Once sno2c is self-hosting, CODE()
calls the compiler directly on the Byrd IR — no C text, no TCC, straight
to block_fn_t via the native code generator. TCC is scaffolding.

**Sprint:** `code-eval` — depends on M-BEAUTY-FULL. TCC must be available
as a linked library (`libtcc`). Add to build: `-ltcc`.

---

### EVAL() — Unifies with CODE (Lon Cherryholmes, 2026-03-14)

**Key insight: EVAL can eval a PATTERN.**

`EVAL('SPAN(''0-9'') . X')` does not produce a value — it produces a
**block function**. A pattern IS a block function. EVAL returns a
`block_fn_t` that the caller uses as `*X`.

This means EVAL and CODE are **the same mechanism**:

| Call | String contains | Compile produces | Returns |
|------|----------------|-----------------|---------|
| `EVAL(str)` | expression | degenerate stmt fn | value via γ |
| `EVAL(str)` | pattern | pattern block fn | `block_fn_t` for use as `*X` |
| `CODE(str)` | statements | block fn sequence | entry `block_fn_t` |

All three paths: compile str via TCC → get address → return it.
The **type of what comes back** tells you what it is.
The **mechanism** is identical in all three cases.

EVAL is not simpler than CODE — it IS CODE. The distinction is only
in what the string contains, not in how it is compiled or executed.

```c
/* EVAL/CODE unified implementation */
block_fn_t sno_eval_or_code(const char *snobol4_src) {
    char *c_src = sno2c_compile_string(snobol4_src);  /* any snobol4 */
    TCCState *s = tcc_new();
    tcc_set_output_type(s, TCC_OUTPUT_MEMORY);
    tcc_compile_string(s, c_src);
    tcc_relocate(s, TCC_RELOCATE_AUTO);
    /* What comes back depends on what src contained:
     *   expression → block_EVAL_value (degenerate stmt)
     *   pattern    → block_EVAL_pattern (pattern block fn)
     *   statements → block_CODE_entry (stmt sequence)   */
    return tcc_get_symbol(s, "block_EVAL_entry");
}
```

The trampoline calls it like any other `block_fn_t`. No special cases.
No interpreter. The same one loop handles everything.

---

### DEFINE functions

`DEFINE('fn(args)locals', 'entry')` compiles to a C function containing the
block functions for its body. The outer C function saves/restores locals on
entry/exit. Its entry block is `block_entry`.

---

### Flat locals struct per block

All locals for all stmts in a block are concatenated into one flat struct.
Allocated once per block invocation. Threaded through stmt calls.

```c
typedef struct {
    int64_t  _saved_cursor_42;
    int64_t  _saved_cursor_43;
    int      _arbno_depth_44;
    int64_t  _arbno_stack_44[64];
} block_L42_locals_t;
```

---

### Milestones

| ID | Trigger | Status |
|----|---------|--------|
| **M-TRAMPOLINE** | Hello world runs through trampoline loop — `pc = pc()` | ❌ |
| **M-STMT-FN** | Every stmt a C function returning S/F block address | ❌ |
| **M-BLOCK-FN** | Stmts grouped into block functions, gotos resolve | ❌ |
| **M-PATTERN-BLOCK** | Named patterns compile to block fns; `*X` static → direct call; `*X` dynamic → `block_fn_t` stored in var, called directly — no interpreter | ❌ |
| **M-LOCALS-STRUCT** | Flat concatenated locals struct per block, all locals correct | ❌ |
| **M-BEAUTY-CORE** | `beauty_core_bin` self-beautifies — diff empty (`-I inc_mock`) | ❌ |
| **M-BEAUTY-FULL** | `beauty_full_bin` self-beautifies — diff empty (`-I inc/`) — only after M-BEAUTY-CORE | ❌ |
| **M-CODE-EVAL** | `CODE()` + `EVAL()` via TCC in-process compile → `block_fn_t`; same trampoline loop; no interpreter | ❌ |
| **M-COMPILED-SELF** | Compiled binary self-beautifies — diff empty | ❌ |
| **M-BOOTSTRAP** | `sno2c` compiles `sno2c` — self-hosting | ❌ |

---

### Sprint Map

| Sprint | What | Gates |
|--------|------|-------|
| `trampoline` | Core types + `block_fn_t` + trampoline loop + hello world | M-TRAMPOLINE |
| `stmt-fn` | Each stmt → C fn returning S/F address, setjmp guard | M-STMT-FN |
| `block-fn` | Label reachability analysis, group stmts into block fns | M-BLOCK-FN |
| `pattern-block` | Named pattern assignments → block fns, `*X` calls | M-PATTERN-BLOCK |
| `locals-struct` | Flat concatenated locals struct per block | M-LOCALS-STRUCT |
| `beauty-full-diff` | beauty.sno self-beautifies through compiled binary | M-BEAUTY-FULL |
| `code-eval` | `CODE()` + `EVAL()` via TCC in-process compile, `-ltcc` | M-CODE-EVAL |
| `compiled-self-diff` | Compiled binary self-beautifies | M-COMPILED-SELF |
| ~~`sno2c-sno-lex`~~ | ~~Write SNOBOL4 lexer~~ | **beauty.sno already has it** |
| ~~`sno2c-sno-parse`~~ | ~~Write SNOBOL4 parser~~ | **beauty.sno already has it** |
| `compiler-pattern` | Weave emit actions into beauty.sno grammar → `compiler.sno`. ONE PATTERN compiles SNOBOL4 → C. | M-SNO2C-SNO |
| `sno2c-sno-compiles` | `sno2c.sno` compiled by C `sno2c` produces working binary — runs on `beauty.sno`, diff empty vs oracle | M-SNO2C-SNO |
| `bootstrap-stage1` | Compile `sno2c.sno` using C `sno2c` → `sno2c_stage1` binary | — |
| `bootstrap-stage2` | Compile `sno2c.sno` using `sno2c_stage1` → `sno2c_stage2` binary | — |
| `bootstrap-verify` | Compare `sno2c_stage1` vs `sno2c_stage2` output on `beauty.sno` — if identical: **M-BOOTSTRAP fires** | **M-BOOTSTRAP** |

---

## Bootstrap Architecture — M-BOOTSTRAP (decided session 78)

**Strategy:** Classic two-stage bootstrap. `sno2c` front-end rewritten in SNOBOL4.
C runtime stays in C permanently — correct and expected (GCC's runtime is also C).

**Stage 0 — already exists:** C `sno2c` compiles SNOBOL4 → C. This is the bootstrap compiler.

**Stage 1:** Compile `sno2c.sno` using C `sno2c` → `sno2c_stage1` binary.

**Stage 2:** Compile `sno2c.sno` using `sno2c_stage1` → `sno2c_stage2` binary.

**Verification:** Compare C output of `sno2c_stage1` vs `sno2c_stage2` on `beauty.sno`. If identical → **M-BOOTSTRAP fires.**

**What stays in C forever:** `snobol4.c`, `mock_includes.c`, `snobol4_pattern.c`, `engine_stub.c`, `trampoline.h`

**What moves to SNOBOL4 (`sno2c.sno`):** Lexer (`lex.c`), Parser (`parse.c`), Emitter (`emit.c` + `emit_byrd.c` + `emit_cnode.c`)

**`CODE()`/`EVAL()` via TCC:** Not required for M-BOOTSTRAP. Separate sprint after.

**No input from Lon required** — architecture fully specified. Each sprint has a clear trigger. Validation is output diff vs oracle at every stage.


### Optimization (deferred — after M-BEAUTY-FULL)

- Inline small stmt functions into their block function
- Merge setjmp guards for unlabeled stmt sequences (glob-sequence optimization)
- `bounded` flag: suppress unused beta/omega ports for non-resumable expressions
- Struct field reuse across non-overlapping temp lifetimes
- Tail-call optimization for the trampoline (already natural in this model)

---

**Status:** Decided 2026-03-14. Supersedes all previous emit.c / emit_byrd.c
struct-passing work. Begin with sprint `trampoline`.

## Architecture: Four Techniques for Byrd Box Implementation (2026-03-14)

**Unifying insight:** A static Byrd box (machine code at a linker address) and a
dynamic Byrd box (malloc'd copy of those same bytes) are identical — same instruction
bytes, same data layout. The only difference is that relative jump offsets and
absolute DATA references must be patched (relocated) in the dynamic copy. There is
no interpreter. The box runs itself. The CPU IS the engine.

### Technique 1 — Struct-passing (CURRENT, C target, for M-BEAUTY-FULL)

Each named pattern becomes a C function `pat_X(pat_X_t **zz, int entry)`.
All locals live in a typed struct `pat_X_t`. Child frame for `*Y` is a pointer
field `pat_Y_t *Y_z` inside the parent struct. `calloc` on first entry (entry==0),
`memset` on re-entry. `entry==1` dispatches to beta.

```c
typedef struct pat_snoParse_t {
    int64_t  saved_7;
    int      arbno_depth;
    int64_t  arbno_stack[64];
    struct pat_snoCommand_t *snoCommand_z;
} pat_snoParse_t;

static SnoVal pat_snoParse(pat_snoParse_t **zz, int entry) {
    pat_snoParse_t *z = *zz;
    if (entry == 0) { z = *zz = calloc(1, sizeof(*z)); goto snoParse_alpha; }
    if (entry == 1) { goto snoParse_beta; }
    ...labeled goto Byrd box using z->field...
}
```

**Status:** In progress. `byrd_emit_named_pattern()` being implemented.

---

### Technique 2 — mmap + memcpy + relocate (ASM/native target, AFTER M-BEAUTY-FULL)

When `*X` fires at match time, the static box for X is already in memory (compiled
into the executable). To create a dynamic instance:

1. `memcpy(new_text, box_X.text_start, box_X.text_len)` — copy CODE section
2. `memcpy(new_data, box_X.data_start, box_X.data_len)` — copy DATA section
3. `relocate(new_text, delta)` — patch two relocation cases:
   - Relative refs (near jumps within box): add `delta = new_addr - orig_addr`
   - Absolute refs (DATA pointers, external calls): patch to new DATA copy
4. Jump to `new_text[PROCEED]` — enter the copy

TEXT section: PROTECTED (RX). mprotect → RWX during copy+relocate, back to RX after.
DATA section: UNPROTECTED (RW), one copy per dynamic instance.
No heap allocator. No GC. ~20 lines. The mmap region IS the allocator.
LIFO discipline of backtracking = discard copy on failure.

**Status:** Not yet implemented. Target: after M-BEAUTY-FULL.

---

### Technique 3 — Iota functions (flat-model C, intermediate concept)

Named after the structs in `test_sno_2.c`. Every labeled Byrd box block that starts
with a label becomes its own tiny C function — not a SNOBOL4 function, purely to
give that block a **callable address**. Sequential blocks are linked by port wiring
(α→γ→next_α etc.) as direct calls or gotos between iota functions.

The entire sequence of iota functions for a named pattern is wrapped in one outer
C function (again, not a SNOBOL4 function — just for a single starting address).
The outer wrapper takes a **single flat concatenated struct** containing ALL locals
for ALL iota functions in the sequence. One struct, passed once, holds everything.

```c
typedef struct {
    int64_t saved_7;        /* from lit_7 iota */
    int     arbno_depth;    /* from arbno_15 iota */
    int64_t arbno_stack[64];
    /* ... all locals for all iota functions in this pattern ... */
} pat_snoParse_iota_t;

static SnoVal pat_snoParse(pat_snoParse_iota_t *z, int entry) {
    if (entry == 0) goto snoParse_alpha;
    if (entry == 1) goto snoParse_beta;
    snoParse_alpha: ...  /* formerly a separate iota function */
    snoParse_beta:  ...
}
```

**Key property:** Every iota function has an address → addressable for the dynamic
box path. Static iota functions in the executable are the template; dynamic boxes
are relocated copies. Bridges Technique 1 and Technique 2.

**Status:** Concept only. Not implemented. Worth revisiting after M-BEAUTY-FULL.

---

### Technique 4 — Flat single function + GCC label-as-value port table

The entire named pattern stays flat in ONE C function — no struct threading,
no iota wrappers. GCC's `&&label` extension gives the address of any label as
a `void*`. A port table is built at startup:

```c
void *pat_snoParse_ports[2];  /* [0]=alpha, [1]=beta */

static SnoVal pat_snoParse_flat(pat_snoParse_iota_t *z) {
    /* Initialize port table once */
    pat_snoParse_ports[0] = &&snoParse_alpha;
    pat_snoParse_ports[1] = &&snoParse_beta;
    ...
    snoParse_alpha:  ...labeled goto Byrd box...
    snoParse_beta:   ...
}

/* Caller dispatches via: goto *pat_snoParse_ports[entry]; */
```

A dynamic copy or any caller jumps in via `goto *pat_snoParse_ports[entry]`.
The port table IS the interface. `&&label` addresses are interior pointers to
the function's code — stable for process lifetime since the function never
truly returns (it runs forever via gotos).

**Weirdness:** `&&label` is a GCC extension (also Clang). Not standard C.
The addresses are only valid within the function — fine here since the box
never returns normally. Linking visibility: expose the port table as a global
`void*` array; the linked object sees it as a normal symbol.

**Status:** Concept only. Not implemented. Hmm — interesting but nonstandard.

---

---

## M-CNODE — C Expression IR + Pretty-Printer (Session 75, 2026-03-15)

**The problem:** `emit_expr` and `emit_pat` are streaming printers — they make
irrevocable formatting decisions as they recurse, with no lookahead. Every long-line
fix (emit_chain_pretty etc.) is a local heuristic. A depth-2 `concat_sv(A, B)` where
A and B are each long `aply(...)` calls stays on one line because the chain depth is
only 2 — the printer doesn't know how wide the whole expression is.

**The solution:** Same model as beauty.sno's pp/qq split.
- **Build phase** (`build_expr`/`build_pat`): walks Expr* tree, produces CNode IR. No output.
- **Measure phase** (`cn_flat_width`): measures flat width of any subtree. This is the "qq" lookahead.
- **Print phase** (`pp_cnode`): walks CNode tree. At each CALL node, measures flat width. If it fits on the current line → inline. Otherwise → multiline with indent. This is "pp".

**Scope boundary:** CNode covers expression trees only. Structural lines (PLG/PS/PG,
labels, gotos) stay as-is. Seam: `E("SnoVal _v%d = ", u)` then `pp_cnode(build_expr(e))`
then `E(";\n")`. Clean cut.

### CNode IR definition

```c
typedef enum {
    CN_RAW,    // literal text atom: "NULL_VAL", "strv(", "," etc.
    CN_CALL,   // fn(arg, arg, ...): fn_name + CNode*[] args
    CN_SEQ,    // two adjacent nodes: left then right
} CNodeKind;

typedef struct CNode {
    CNodeKind    kind;
    const char  *text;      // CN_RAW: literal; CN_CALL: function name
    struct CNode **args;    // CN_CALL: argument subtrees
    int           nargs;
    struct CNode *left, *right; // CN_SEQ: left then right
} CNode;
```

### pp/qq rules

```c
// "qq" — flat width of subtree, or INT_MAX if > limit (early exit)
int cn_flat_width(CNode *n, int limit);

// "pp" — pretty-print to FILE*, returns column after last char written
// col     = current column (chars already on this line)
// indent  = additional indent for wrapped args (4)
// maxcol  = line width budget (120)
int pp_cnode(CNode *n, FILE *fp, int col, int indent, int maxcol);
```

`pp_cnode` rule for CN_CALL:
- Compute `w = cn_flat_width(n, maxcol - col)`
- If `col + w <= maxcol`: emit flat — `fn(arg0,arg1,...)`
- Else: emit multiline — `fn(\n` + each arg indented on its own line + `)`
- Args that are themselves CN_CALL recurse with `col = indent_col`

### Sprint map

| Sprint | What | Gates |
|--------|------|-------|
| `cnode-build` | `build_expr` + `build_pat` — CNode tree from Expr* | ✅ `160f69b` — 0 mismatches |
| `cnode-measure` | `cn_flat_width(n, limit)` with early exit | ✅ `160f69b` |
| `cnode-pp` | `pp_cnode` — inline if fits, multiline if not | ✅ `160f69b` |
| `cnode-wire` | Replace `emit_expr`/`emit_pat` calls with `pp_cnode(build_expr(...))` | ✅ `ac54bd2` — **M-CNODE fired** |

### Implementation notes

- CNode arena allocator (bump allocator, freed after each statement) — no GC pressure
- `flat_print` helper for sprint 1 validation: writes CNode to char buffer, compared against old `emit_expr` output
- `cn_flat_width` prunes at `limit` — returns `INT_MAX` once exceeded, no wasted work
- `pp_cnode` tracks `col` through CN_SEQ nodes, passes updated col to siblings
- File: `src/sno2c/emit_cnode.c` + `src/sno2c/emit_cnode.h`

### What this fixes

Before: `SnoVal _v34 = concat_sv(aply("REPLACE",...,3),aply("REPLACE",...,3));` — 340 chars

After:
```c
SnoVal _v34 =
    concat_sv(
        aply("REPLACE", (SnoVal[]){
            aply("SUBSTR", (SnoVal[]){get(_cap), vint(1), vint(1)}, 3),
            kw("LCASE"), kw("UCASE")}, 3),
        aply("REPLACE", (SnoVal[]){
            aply("SUBSTR", (SnoVal[]){get(_cap), vint(2)}, 2),
            kw("UCASE"), kw("LCASE")}, 3));
```

**Status:** Planned. Begin with sprint `cnode-build` next session.

---

## Three-Column Format — ALL Generated Code (Session 73, 2026-03-15)

**Lon's requirement:** The entire generated C file must use the 3-column Byrd box layout —
not just pattern blocks. The current `emit.c` uses raw `E(...)` fprintf for all statement
code (label setup, trampoline blocks, function bodies). This must be replaced.

### Column layout (same as emit_byrd.c patterns):

```
Col 1  Label   display  0..17   (4-space indent + label + ":" + pad)
Col 2  Stmt    display 18..59   (C statement body)
Col 3  Goto    display 60+      (goto target)
```

### Mapping from current emit.c output to 3-column:

| Current emit.c output | 3-column form |
|------------------------|---------------|
| `_L_pp:;` + `goto _SNO_NEXT_794;` | `PLG("_L_pp", "_SNO_NEXT_794")` |
| `SnoVal _v795 = ...;` + `goto _SNO_NEXT_794;` | `PL("", "_SNO_NEXT_794", "SnoVal _v795 = ...;")` |
| `_L_pp_Parse:;` + `goto _L_pp_0;` | `PLG("_L_pp_Parse", "_L_pp_0")` |
| label + no stmt + goto | `PLG(col1, col3)` — two-section, skip middle |
| `if(_ok) goto X; if(!_ok) goto Y;` | `PS("X", "if(_ok)")` + `PS("Y", "if(!_ok)")` |

### Two-section emits (label + goto, no middle):

These are valid 3-column lines — col 1 has the label, col 2 is blank, col 3 has the goto.
Example: `_L_pp_Parse:` dispatches immediately to `:(pp_0)` with no action.
Use `PLG(label, goto_target)` — exactly like pattern alpha/beta port wires.

### Implementation plan:

1. Move `pretty_line()` + `COL_*` constants + `PLG`/`PL`/`PS`/`PG` macros to a shared
   header `emit_pretty.h` — included by both `emit.c` and `emit_byrd.c`.
2. Replace all `E("label:;\n")` + `E("goto X;\n")` pairs in `emit.c` with `PLG`/`PL`/`PS`.
3. The `_ok%d`/`!_ok%d` conditional blocks become PS lines with goto in col 3.
4. The `trampoline_stno(N)` call folds into col 2 or drops entirely (it's a debug hook).

**Priority:** After M-BEAUTY-FULL (START bug fix first). This is a cosmetic/readability
improvement — correct output matters more. But Lon wants it before M-COMPILED-SELF.

---

## Save/Restore via Byrd Box for DEFINE Functions (Session 73, 2026-03-15)

**Lon's requirement:** The save/restore of caller locals when entering/exiting a SNOBOL4
DEFINE'd function must be structured as a Byrd box — not as ad-hoc C preamble/postamble.

### Current (wrong) pattern in emit.c:

```c
static SnoVal _sno_fn_pp(SnoVal *_args, int _nargs) {
    SnoVal _saved__x = var_get("x");   /* save */
    SnoVal _saved__t = var_get("t");   /* save */
    ...
    /* function body as flat gotos */
    ...
_SNO_RETURN_pp:
    var_set("x", _saved__x);           /* restore */
    var_set("t", _saved__t);           /* restore */
    return _pp;
}
```

### Required (correct) pattern — save/restore AS Byrd box ports:

The function entry (α) saves caller locals. The function exit (γ/ω) restores them.
This is the natural Byrd box structure:

```
fn_pp_α:   save caller x,t,n,c,i,v into fn_pp_saved_*    goto fn_body_α
fn_body_α: ... function body labeled gotos ...
fn_pp_γ:   restore caller x,t,n,c,i,v from fn_pp_saved_* goto caller_γ
fn_pp_ω:   restore caller x,t,n,c,i,v from fn_pp_saved_* goto caller_ω
```

The save/restore lives in the α and γ/ω ports — not in C function preamble.
This makes the control flow uniform with all other Byrd boxes and makes the
generated code readable in 3-column format like everything else.

**Why it matters:** With C-local shadowing (current approach), recursive calls work
correctly at the C level but the save/restore is invisible in the generated code —
it looks like magic C-scope behavior rather than explicit SNOBOL4 semantics.
The Byrd box form makes the α/γ/ω ports explicit and readable.

**Implementation:** In `emit.c` `emit_fn()`, replace the preamble/postamble save/restore
with PLG/PL lines for α (save) and γ/ω (restore). The saved values go into a struct
(same as Technique 1 in PLAN.md) rather than C locals with var_get/var_set.

**Priority:** Sprint after 3-column format. Prerequisite for M-COMPILED-SELF.

---

## Active Bug: `c` field of tree node returns SSTR not ARRAY (Session 73)

**Symptom:** `indx(get(_c), {vint(1)}, 1)` inside `pp_Parse` returns SFAIL (type=10).
`c.type=1` (SSTR) — the `c` field accessor on a UDEF tree node returns a string, not
the array of children.

**Root cause traced:**
- `Reduce("Stmt", 7)` correctly calls `tree("Stmt", NULL, 7, c_array)`
- The `c` field is stored as an ARRAY in the UDEF node
- But `aply("c", {node}, 1)` → `field_get(node, "c")` returns SSTR

**Next session — Step 1:** Check `field_get` for UDEF nodes — does it serialize the
array to string? Check `_b_tree_c` in snobol4.c and `field_get` for ARRAY-valued fields.

**Next session — Step 2:** Check `indx()` — it's called as `aply("indx", {c, vint(1)}, 2)`
in generated code. But `indx` may not be registered as a builtin. Verify:
```bash
grep -n "register_fn.*indx\|\"indx\"" src/runtime/snobol4/snobol4.c
```

**Next session — Step 3:** The correct access pattern for a DATA-defined array field
may be `aply("c", {node}, 1)` followed by `aply("indx", {c_array, idx}, 2)` — or
it may need direct UDEF field indexing `c[i]` which compiles differently. Check how
beauty.sno's `c[i]` (subscript notation on a UDEF field) compiles in the generated C.

**Commit when fixed:** `fix(runtime): UDEF array field access — c[i] on tree nodes`


---

## Architecture: Two Pattern-Based Compiler Strategies (Session 78, Lon Cherryholmes)

**Reference model:** `SNOBOL4-corpus/programs/inc/ini.sno` — `iniParse` builds a full
INI table structure as a side effect of the match using `epsilon . *assign(...)` primitives
woven into alternation branches. Zero post-processing. The match IS the result.

**Reference demo:** `assignment3.py` (ENG 685, Lon Cherryholmes) — `treebank` pattern
builds a full nested tuple tree inside one pattern via push_list/pop_list lambdas.
`claws_info` does full corpus tagging inside one pattern. Proves complex data structures
can be built entirely within a match — no post-processing pass needed.

---

### Architecture A — Reformed beauty.sno (the sprinkle approach)

**Goal:** Eliminate `pp()`/`qq()` as separate post-processing functions. Sprinkle beautifier
output actions directly into pattern alternations using `epsilon . *action(...)` — exactly
as `iniParse` assigns table entries inline. Each grammar alternative immediately writes its
beautified output as it matches. No tree walk.

**This is hard.** Threading output actions through every sub-pattern level — the way
`treebank` builds a list by wiring push/pop into every nested alternative — requires
deep intricate changes throughout the full pattern hierarchy.

**Status:** Architectural option. Not the current path. Worth pursuing after M-BOOTSTRAP
as the "pure" form of beauty.sno. `ini.sno` is the reference model.

---

### Architecture B — compiler.sno with final primitive (the clean path, current target)

**Goal:** `compiler.sno` reuses `Compiland`/`Parse`/`Stmt`/`Expr`/`Command` patterns
**unchanged**. They already build the Shift/Reduce tree via `nPush`/`nPop`/`~`/`&`.

Replace the `pp()` call with one big **final primitive** — a SNOBOL4 function that reads
the completed tree and emits C Byrd box code.

```
*  beauty.sno:   Src POS(0) *Parse *Space RPOS(0)  →  pp(sno)
*  compiler.sno: Src POS(0) *Parse *Space RPOS(0)  →  compile(sno)
```

`compile(sno)` walks the same tree that `pp(sno)` walks, emits C instead of pretty-printed
SNOBOL4. Grammar patterns identical. Tree identical. Final action is the only difference.

**This is clean and achievable.** Tree machinery proven by M-BEAUTY-FULL.
The compiler is: proven grammar + proven tree + new `compile()` function.

**Status:** This IS the `compiler-pattern` sprint. The bootstrap path.

---

### Sprint map (updated)

| Sprint | What | Gates |
|--------|------|-------|
| ~~`sno2c-sno-lex`~~ | beauty.sno already has it | — |
| ~~`sno2c-sno-parse`~~ | beauty.sno already has it | — |
| `compiler-pattern` | Write `compile(sno)` — final primitive reads Shift/Reduce tree, emits C Byrd boxes. Wire into beauty.sno grammar → `compiler.sno`. Validate: diff empty vs oracle. | M-SNO2C-SNO |

### Why Architecture B first

1. **Proven foundation** — M-BEAUTY-FULL proves parse+tree machinery works. `compile()` gets a correct tree.
2. **Minimal delta** — `compiler.sno` = `beauty.sno` + replace `pp()` with `compile()`. One new function.
3. **Architecture A later** — once bootstrap achieved, reform beauty.sno to eliminate pp/qq via sprinkled inline actions. `ini.sno` is the reference. `treebank` in assignment3.py is the proof of concept.


---

## Session 85 Rename Audit — Full Accounting (2026-03-14)

Complete word-for-word verification of the Session 84 SIL naming rename.
Source of truth: `git show eec84e7` diff on `snobol4.h` + all `.c`/`.h` files.

### Rename Table — Verified Clean ✅

| Old name | New name | Status |
|----------|----------|--------|
| `SnoVal` (struct) | `DESCR_t` | ✅ Gone everywhere |
| `SnoType` (enum) | `DTYPE_t` | ✅ Gone everywhere |
| `.type` field | `.v` field | ✅ Gone everywhere |
| `SNULL` | `DT_SNUL` | ✅ Gone everywhere |
| `SSTR` | `DT_S` | ✅ Gone everywhere |
| `SINT` | `DT_I` | ✅ Gone everywhere |
| `SREAL` | `DT_R` | ✅ Gone everywhere |
| `STREE` | (removed — was struct _Tree, now TREEBLK_t) | ✅ Gone everywhere |
| `SPATTERN` | `DT_P` | ✅ Gone everywhere |
| `UDEF` | `DT_DATA` | ✅ Gone everywhere |
| `SFAIL` | `DT_FAIL` | ✅ Gone everywhere |
| `NULL_VAL` | `NULVCL` | ✅ Gone everywhere |
| `STR_VAL(s)` | `STRVAL(s)` | ✅ Gone everywhere |
| `INT_VAL(i)` | `INTVAL(i)` | ✅ Gone everywhere |
| `FAIL_VAL` | `FAILDESCR` | ✅ Gone everywhere |
| `is_fail()` | `IS_FAIL_fn()` | ✅ Gone everywhere |
| `is_null/is_str/is_int/is_real/is_tree/is_udef` | `IS_NULL_fn/IS_STR_fn/IS_INT_fn/IS_REAL_fn/IS_DATA_fn` | ✅ Gone everywhere |
| `to_str()` | `VARVAL_fn()` | ✅ Gone everywhere |
| `concat_sv()` | `CONC_fn()` | ✅ Gone everywhere |
| `runtime_init()` | `SNO_INIT_fn()` | ✅ Gone everywhere |
| `var_get/var_set` | `NV_GET_fn/NV_SET_fn` | ✅ Gone everywhere |
| `aply()` | `APLY_fn()` | ✅ Gone everywhere |
| `define()` | `DEFINE_fn()` | ✅ Gone everywhere |
| `func_exists()` | `FNCEX_fn()` | ✅ Gone everywhere |
| `make_tree()` | `MAKE_TREE_fn()` | ✅ Gone everywhere |
| `npush/npop/ninc/ndec` | `NPUSH_fn/NPOP_fn/NINC_fn/NDEC_fn` | ✅ Gone everywhere |
| `push/pop/top/stack_depth` | `PUSH_fn/POP_fn/TOP_fn/STACK_DEPTH_fn` | ✅ Gone everywhere |
| `SnoFunc` typedef | `FNCPTR_t` | ✅ Gone everywhere |
| `SPAT_LIT` | `XCHR` | ✅ Gone everywhere |
| `SPAT_ARBNO` | `XARBN` | ✅ Gone everywhere |
| `SPAT_ASSIGN_COND` | `XNME` | ✅ Gone everywhere |
| All other `SPAT_*` | `X*` (SIL codes) | ✅ Gone everywhere |
| `E_MUL` | `E_MPY` | ✅ Gone in sno2c.h |
| `E_ALT` | `E_OR` | ✅ Gone in sno2c.h |
| `E_COND` | `E_NAM` | ✅ Gone in sno2c.h |
| `E_IMM` | `E_DOL` | ✅ Gone in sno2c.h |
| `E_CALL` | `E_FNC` | ✅ Gone in sno2c.h |
| union member `.a` (array) | `.arr` | ✅ Gone in code — see bug below |

---

### Bugs Found by Audit

#### BUG 1 — `ARRAY_VAL` macro uses `.a` (must be `.arr`) ⚠️

**File:** `src/runtime/snobol4/snobol4.h` line 399  
**Current (wrong):**
```c
#define ARRAY_VAL(a_)   ((DESCR_t){ .v = DT_A, .a   = (a_)   })
```
**Correct:**
```c
#define ARRAY_VAL(a_)   ((DESCR_t){ .v = DT_A, .arr = (a_)   })
```
The union member was renamed `.a` → `.arr` in the struct definition (line 56), but the macro was not updated.  
**Severity:** Dormant — `ARRAY_VAL` is currently defined but never called anywhere. Would be a compile error the moment it is used.  
**Fix:** One character change. Fix now before it bites.

---

### Intentional Partial Renames (not bugs — by design)

These functions take `DESCR_t` arguments (updated) but kept lowercase names — they are internal C helpers or math ops where ALLCAPS would be jarring:

| Function | Pattern | Verdict |
|----------|---------|---------|
| `lpad_fn / rpad_fn` | lowercase — inconsistent with ALLCAPS_fn | ⚠️ Minor — should be `LPAD_fn/RPAD_fn` |
| `real_fn / string_fn` | lowercase — inconsistent | ⚠️ Minor — should be `REAL_fn/STRING_fn` |
| `eq/ne/lt/le/gt/ge` | no `_fn` suffix | ✅ Intentional — SIL comparison primitives, short names OK |
| `add/sub/mul/divyde/powr/neg` | no `_fn` suffix | ✅ Intentional — arithmetic primitives |
| `ident/differ` | no `_fn` suffix | ✅ Intentional — SNOBOL4 keyword names |
| `to_int/to_real` | no `_fn` suffix | ✅ Intentional — type coercion helpers |
| `output_val/input_read/comm_var` | mixed | ✅ Acceptable — I/O primitives |
| `pat_lit/pat_span/pat_arbno` etc. | `pat_` prefix, no `_fn` | ✅ Intentional — pattern constructors keep their domain prefix |

---

### Emitter Consistency (sno2c → generated C)

All names emitted by `emit.c`, `emit_byrd.c`, `emit_cnode.c` verified consistent with new names:
- Emits `APLY_fn(...)` ✅
- Emits `CONC_fn(...)` ✅  
- Emits `NULVCL` ✅
- Emits `STRVAL/INTVAL` ✅
- Emits `IS_FAIL_fn(...)` ✅
- Emits `NV_GET_fn/NV_SET_fn(...)` ✅
- Emits `DESCR_t` ✅
- Emits `SNO_INIT_fn()` ✅

No crossover or mismatch in generated code.

---

### Action Required

1. **Fix `ARRAY_VAL` macro** — `.a` → `.arr` in `snobol4.h:399` (one character, fix now)
2. **Consider renaming `lpad_fn/rpad_fn/real_fn/string_fn`** → `LPAD_fn/RPAD_fn/REAL_fn/STRING_fn` for consistency — low priority, not a bug
