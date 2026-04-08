# PLAN-SN4-X86.md — SNOBOL4 × x86 Home-Stretch Milestones

**Goal:** `scrip` binary — SNOBOL4 for x86 — all command-line switches working,
all tests passing.

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Updated:** 2026-04-08j
**Current baseline:** PASS=168 `--sm-run` · PASS=168 `--ir-run` · HEAD `c30de4ca`

---

## Switch Map — Target State

```
scrip --ir-run        ✅ WIRED   tree-walk IR executor
scrip --sm-run        ✅ WIRED   SM_Program interpreter
scrip --jit-run       ✅ WIRED   threaded-call JIT
scrip --jit-emit --x64   ⬜ GAP   SM → x86 .s emitter
scrip --jit-emit --jvm   ⬜ GAP   SM → Jasmin .j emitter
scrip --jit-emit --net   ⬜ GAP   SM → IL .il emitter
scrip --jit-emit --js    ⬜ GAP   SM → JS emitter
scrip --jit-emit --c     ⬜ GAP   SM → C emitter
scrip --jit-emit --wasm  ⬜ GAP   SM → WAT emitter
scrip --bb-driver     ✅ WIRED
scrip --bb-live       ✅ WIRED
scrip --dump-ir       ✅ WIRED
scrip --dump-sm       ✅ WIRED
scrip --dump-bb       ✅ WIRED
scrip --trace         ✅ WIRED
scrip --bench         ✅ WIRED
scrip --dump-parse    ✅ WIRED
```

---

## Milestones — Priority Order

### SN4-X86-1-BOX-UNIFY: Box unification — clean linker, single-source box architecture
**Status:** 🟡 Planned (DYN-24 done 11/14 boxes)
**File:** MILESTONE-BOX-UNIFY.md

#### What is a Byrd box?

Every SNOBOL4 pattern primitive — `ANY`, `SPAN`, `BREAK`, `LEN`, `ARB`, `ARBNO`,
captures, alternation, sequence — is implemented as a **Byrd box**: a small C
function with four ports (α enter, β backtrack, γ succeed, ω fail). Boxes are
wired into a graph at match time; `exec_stmt` drives the graph by calling α and
following γ/ω/β transitions until the whole pattern succeeds or fails. There are
about 25 box types. This architecture is what makes SNOBOL4 pattern matching
efficient and composable.

#### The current problem: three representations, two of them duplicated

Each box currently exists in up to three forms:

| Form | Location | Used by |
|------|----------|---------| 
| C source (canonical logic) | `src/runtime/boxes/bb_*.c` | `scrip --sm-run`, `--ir-run`, `--jit-run` |
| NASM text (hand-written asm) | `src/runtime/boxes/bb_*.s` | old `snobol4_x86` runtime (legacy) |
| asm binary (mmap'd machine code) | not yet implemented | planned JIT path |

DYN-24 session de-duplicated 11 of the 14 simple boxes — `bb_box.h` now owns the
shared typedefs and `bb_*.c` is canonical for those 11. But 3 complex boxes
(`bb_atp`, `bb_capture`, `bb_deferred_var`) are still duplicated:

- Their **live implementations** are `static` functions buried inside `stmt_exec.c`
  (because they need `bb_node_t`, `DESCR_t`, and `bb_build` which are all defined
  there, and extracting them without a shared header was deferred).
- Stub files `bb_atp.c`, `bb_capture.c`, `bb_dvar.c` exist but don't compile cleanly
  — they reference symbols they can't see. The Makefile excludes them from the build,
  so they're dead weight that causes confusion.

This creates a latent linker hazard: if anyone tries to include the stubs, the build
breaks with undefined symbol errors. It also makes the codebase misleading — three
files that look like canonical box implementations but aren't.

#### Phase 1 — Quick fix (one session)

Delete the three broken stub files. Keep the working `static` implementations in
`stmt_exec.c` exactly where they are. This is option A from MILESTONE-BOX-UNIFY.md:
no new architecture, just remove the confusion.

Gate: `make scrip` links clean, zero undefined-symbol warnings.

#### Phase 2 — Full single-source architecture (future)

Extract `bb_node_t` + `bb_build` prototype into a new `runtime/dyn/bb_build.h`.
Include that header in `bb_atp.c`, `bb_capture.c`, `bb_dvar.c` — now they can
compile on their own. Remove the `static` copies from `stmt_exec.c`. Every box has
exactly one `.c` file as its canonical home.

Long-term goal (post-JIT): each box also gets a `bb_*_emit.c` — a function that
writes the box's machine code directly into the mmap pool. One English description
of the box's matching logic → three mechanical derivations: C source, NASM text,
binary emitter.

Gate Phase 2: 25/25 C boxes pass unit harness; C/asm parity verified.

---

### SN4-X86-2-CORPUS-GAPS: Close corpus gaps — PASS=178 on `--sm-run`
**Status:** 🟡 Active (PASS=168, gap=10)
**File:** MILESTONE-SN4PARSE-VALIDATE.md (P1b/P1c), MILESTONE-P2F-SEMI.md,
         MILESTONE-RT-RUNTIME.md (RT-9), MILESTONE-SILLY-SNOBOL4.md (M-SS-BLOCK)

The 10 failing tests break into:
- **expr_eval, test_stack** — NRETURN lvalue semantics in call_user_function; DEFINE arity
- **1012_func_locals** — semicolon multi-statement (P2F-SEMI fix via git bisect)
- **1112_array_multi, 1113_table, 1114_item, 1116_data_overlap** — array/table edge cases
- **212_indirect_array** — indirect array reference
- **word1, wordcount** — PAT-value storage / spurious OUTPUT (SJ-15 class bug)
- **cross, triplet, fileinfo** — parser or pattern edge cases

Gate: `INTERP="./scrip --sm-run" CORPUS=/home/claude/corpus bash test/run_interp_broad.sh | grep "^PASS"`
Target: **PASS=178**

---

### SN4-X86-3-BB-BENCH: Benchmark `--bb-live` vs `--bb-driver`
**Status:** ⬜ Not started
**File:** (new section in MILESTONE-SCRIP-X86-COMPLETION.md)

Fill the M-DYN-BENCH-X86 results table. Run the standard corpus with `--bench`
under both modes; record ops/sec and wall time.

Gate: Results table filled in MILESTONE-SCRIP-X86-COMPLETION.md.
Quick win — one session.

---

### SN4-X86-4-EMIT-X64: `--jit-emit --x64` — SM-based x86 text emitter
**Status:** ⬜ Not started (old `emit_x64.c` is LEGACY stopgap)
**File:** MILESTONE-SCRIP-X86-COMPLETION.md § M-JITEM-X64

New file `src/backend/emit_sm_x64.c`. Walk SM_Program; for each instruction
emit corresponding x86 blobs in 3-column format (label / instruction / comment).

Gate: `scrip --jit-emit --x64 corpus/001.sno` produces correct `.s`; `nasm` + `ld` + run passes.

---

### SN4-X86-5-EMIT-JVM: `--jit-emit --jvm` — SM-based Jasmin emitter
**Status:** ⬜ Not started
**File:** MILESTONE-SCRIP-X86-COMPLETION.md § M-JITEM-JVM

New file `src/backend/emit_sm_jvm.c`.
Gate: PASS=165 via `scrip --jit-emit --jvm`.

---

### SN4-X86-6-EMIT-NET: `--jit-emit --net` — SM-based IL emitter
**Status:** ⬜ Not started
**File:** MILESTONE-SCRIP-X86-COMPLETION.md § M-JITEM-NET

New file `src/backend/emit_sm_net.c`.
Gate: PASS=170 via `scrip --jit-emit --net`.

---

### SN4-X86-7-EMIT-JS: `--jit-emit --js` — SM-based JS emitter
**Status:** ⬜ Not started
**File:** MILESTONE-SCRIP-X86-COMPLETION.md § M-JITEM-JS

New file `src/backend/emit_sm_js.c`.
Gate: PASS=174 via `scrip --jit-emit --js`.

---

### SN4-X86-8-EMIT-C: `--jit-emit --c` — SM-based C emitter
**Status:** ⬜ Not started
**File:** MILESTONE-SCRIP-X86-COMPLETION.md § M-JITEM-C

New file `src/backend/emit_sm_c.c`.
Gate: `scrip --jit-emit --c corpus/001.sno` produces C that compiles and runs.

---

### SN4-X86-9-EMIT-WASM: `--jit-emit --wasm` — SM-based WAT emitter
**Status:** ⬜ Not started
**File:** MILESTONE-SCRIP-X86-COMPLETION.md § M-JITEM-WASM

New file `src/backend/emit_sm_wasm.c`.
Gate: existing WASM corpus tests pass via new emitter.

---

### SN4-X86-10-PARSER-GAPS: Parser gaps — postfix subscript, multiple assignment
**Status:** ⬜ Sprint 91 target
**File:** MILESTONE-SN4PARSE-VALIDATE.md

- P1b: `f(g(x)[i])` postfix subscript on call result — 6 failing files
- P2D: multiple assignment `A = B = C + 1`

Gate: 84/84 standard SNOBOL4 sweep clean.

---

### SN4-X86-11-DEAD-CODE: Dead code archive + LEGACY labels
**Status:** ⬜ Immediate housekeeping (no milestone needed per COMPLETION doc)
**File:** MILESTONE-SCRIP-X86-COMPLETION.md § Archive Actions

```bash
git mv src/runtime/asm/bb_poc.c          archive/backend/
git mv src/runtime/asm/bb_emit_test.c    archive/backend/
git mv src/runtime/asm/bb_pool_test.c    archive/backend/
git mv src/runtime/asm/snobol4_asm.mac   archive/backend/
git mv src/runtime/asm/snobol4_asm_harness.c archive/backend/
git mv src/runtime/asm/x86_stubs_interp.c    archive/backend/
```
Add `/* LEGACY */` comment to top of each old emitter in `src/backend/`.

Gate: `make scrip` still builds; dead files gone from working tree.

## Out-of-Scope for This Track (other session tracks)

These milestones are active but belong to other parallel tracks — not the
SNOBOL4 × x86 home-stretch:

| Milestone | Track |
|-----------|-------|
| MILESTONE-SILLY-SNOBOL4.md (M-SS-BLOCK) | Silly / v311.sil faithful rewrite |
| MILESTONE-SS-AUDIT.md | Silly deep audit |
| MILESTONE-SS-MONITOR.md | Silly sync-step monitor |
| MILESTONE-V311-C.md | Ground-up faithful C rewrite |
| MILESTONE-RT-SIL-MACROS.md | SIL macro design reference |
| MILESTONE-NET-SNOBOL4.md | .NET track (Jeff Cooper + D-session) |
| MILESTONE-NET-INTERP.md | .NET annex |
| MILESTONE-JVM-SNOBOL4.md | JVM track |
| MILESTONE-JS-SNOBOL4.md | JS track |
| MILESTONE-JS-ICON.md | Icon × JS |
| MILESTONE-JS-PROLOG.md | Prolog × JS |
| MILESTONE-JS-BENCH.md | JS bench |
| MILESTONE-DYN-INTERP.md | DYN-session tree-walk interp |
| MILESTONE-FAST-EMIT-CHECK.md | Emit-diff speed |
| MILESTONE-FAST-INVARIANTS.md | Invariant harness speed |
| MILESTONE-SNO2SC.md | SNOBOL4→Snocone conversion |
| MILESTONE-SN4PARSE.md | sn4parse standalone parser |
| MILESTONE-SN4PARSE-VALIDATE.md (P3 UTF-8) | Unicode extensions |
| MILESTONE-SCRIP-UNIFY-X86.md | Binary rename/unify (post-correctness cleanup) |

---

## Done (this track — preserved here for continuity)

| Milestone | Completed |
|-----------|-----------|
| M-DIAG | 2026-04-07 |
| M-BB-LIVE-WIRE | 2026-04-07 |
| M-DYN-B13 | 2026-04-07 |
| M-JIT-RUN | 2026-04-07 |
| RT-1 INVOKE | 2026-04-04 |
| RT-2 VARVAL/INTVAL/PATVAL | 2026-04-04 |
| RT-3 NAME/ASGNIC | 2026-04-04 |
| RT-4 NMD naming list | 2026-04-04 |
| RT-5 NV_SET_fn void→DESCR_t | 2026-04-08i |
| RT-6/7/8 EXPVAL/CONVE/EVAL | 2026-04-08i |
| RT-CAP-FN SM_PAT_CAPTURE_FN | 2026-04-08j |

---

*Written 2026-04-08j — Lon Jones Cherryholmes + Claude Sonnet 4.6*
*Replaces scattered MILESTONE-* files for the x86 track.*
*Other-track milestones remain in their own files.*
