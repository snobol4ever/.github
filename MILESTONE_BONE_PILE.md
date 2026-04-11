# MILESTONE_BONE_PILE.md — Archived Milestone Reference

**Status:** Parked — cleared 2026-04-08 to focus on SNOBOL4 × x86 home stretch.
**Active sessions:** Silly SNOBOL4 (MILESTONE-SS-*, MILESTONE-SILLY-*, MILESTONE-V311-*) and snobol4dotnet (MILESTONE-NET-*) are NOT here — they remain active in their own files.
**Purpose:** Preserve milestone content for future use when x86 track is complete and other tracks reopen.

---


---

<!-- SOURCE: MILESTONE-BOX-UNIFY.md -->

# MILESTONE-BOX-UNIFY — Single-Source Box Definitions

**Session:** DYN- · **Sprint:** DYN-25 onward
**Status:** PLANNED — DYN-24 did the 11 easy boxes; this finishes the job.

---

## Problem Statement

Every Byrd box currently has up to three representations:

| Form | Location | Owner |
|------|----------|-------|
| C text (canonical) | `src/runtime/boxes/bb_*.c` | Linked by scrip-interp + test harness |
| asm text (NASM) | `src/runtime/boxes/bb_*.s` | Linked by snobol4_x86 runtime |
| asm binary | (not yet implemented) | Planned for JIT path |

**Current duplication after DYN-24:**
- 11 simple boxes ✅ de-duplicated — `bb_box.h` owns typedefs, `bb_*.c` is canonical
- 3 complex boxes (`bb_atp`, `bb_capture`, `bb_deferred_var`) still duplicated:
  - Live in `stmt_exec.c` as `static` (need `bb_node_t`, `DESCR_t`, `bb_build`)
  - Also have stub `bb_atp.c`, `bb_capture.c`, `bb_dvar.c` that don't compile cleanly

---

## Phase 1 — Fix DYN-24 linker error (DYN-25 first task)

`bb_build()` in `stmt_exec.c` references `bb_atp`, `bb_capture`, `bb_deferred_var`
as function-pointer targets. When `bb_atp.c`/`bb_capture.c`/`bb_dvar.c` are
excluded from the build, these symbols are undefined.

**Fix options (pick one):**
A. Keep complex boxes as `static` in `stmt_exec.c`; delete `bb_atp.c`,
   `bb_capture.c`, `bb_dvar.c` stub files entirely. Cleanest for now.
B. Extract `bb_node_t` + `bb_build` prototype into `runtime/dyn/bb_build.h`,
   include in `bb_dvar.c` / `bb_atp.c` / `bb_capture.c`. More work, cleaner long-term.

**Recommendation:** Option A for DYN-25 (delete stubs), Option B as part of
the full unification below.

---

## Phase 2 — Full single-source architecture (future milestone)

### Target layout

```
src/runtime/boxes/
  bb_box.h          — spec_t, ports (α/β/γ/ω), ALL state typedefs, bb_box_fn
  bb_build.h        — bb_node_t, bb_build() prototype (extracted from stmt_exec.c)
  bb_lit.c          — C implementation (canonical logic)
  bb_lit.s          — asm-text implementation (hand-written NASM, matches C)
  bb_lit_emit.c     — asm-binary emitter: writes bb_lit machine code into mmap pool
  ... (25 boxes × 3 files)
```

### Port wiring diagram (top level — same for all three forms)

```
         ┌─────────────────────────────┐
         │       bb_NAME(ζ, entry)     │
         │                             │
  α ────►│  α port: match forward      │────► γ (success, spec_t)
  β ────►│  β port: backtrack          │────► ω (failure, spec_empty)
         │                             │
         │  state: NAME_t *ζ           │
         └─────────────────────────────┘
```

C form: `spec_t bb_NAME(void *zeta, int entry)` — three-column goto style
asm-text form: NASM with `bb_NAME:` global, same port logic as C
asm-binary form: `void bb_NAME_emit(uint8_t *buf, size_t *len, NAME_t *ζ)` —
  writes machine code for one box invocation into mmap pool

### Single logic rule

**One English description of the box's matching logic → three mechanical
derivations.** Any change to box semantics touches `bb_NAME.c` first;
`bb_NAME.s` and `bb_NAME_emit.c` are then derived/updated to match.

### Macro-formatted C source

All `bb_*.c` files use the three-column macro style already established:

```c
spec_t bb_lit(void *zeta, int entry)
{
    lit_t *ζ = zeta;
    spec_t LIT;
    if (entry==α)                                                               goto LIT_α;
    if (entry==β)                                                               goto LIT_β;
    LIT_α:  if (Δ + ζ->len > Ω)                                                goto LIT_ω;
            if (memcmp(Σ+Δ, ζ->lit, (size_t)ζ->len) != 0)                      goto LIT_ω;
            LIT = spec(Σ+Δ, ζ->len); Δ += ζ->len;                              goto LIT_γ;
    LIT_β:  Δ -= ζ->len;                                                        goto LIT_ω;
    LIT_γ:                                                                      return LIT;
    LIT_ω:                                                                      return spec_empty;
}
```

No mixing of styles. All 25 boxes look identical in structure.

---

## Gate

- snobol4_x86 **142/142** maintained throughout
- `scrip-interp` links and passes M-INTERP-A01 smoke tests (20 corpus programs)
- `bb_test` harness: 25/25 C boxes pass, 25/25 S boxes match

---

## Files to create/modify

```
src/runtime/dyn/bb_build.h          — extract bb_node_t + bb_build prototype
src/runtime/boxes/bb_box.h          — already updated (DYN-24); add bb_build.h include
src/runtime/boxes/bb_atp.c          — rewrite to use bb_build.h (or delete if Option A)
src/runtime/boxes/bb_capture.c      — rewrite (or delete if Option A)
src/runtime/boxes/bb_dvar.c         — rewrite (or delete if Option A)
src/runtime/dyn/stmt_exec.c         — remove remaining static bb_* bodies
```

---

*Written DYN-24 2026-04-02. Supersedes ad-hoc box notes in SESSIONS_ARCHIVE.*


---

<!-- SOURCE: MILESTONE-DYN-INTERP.md -->

# MILESTONE-DYN-INTERP — scrip-interp: SNOBOL4 Tree-Walk Interpreter

**Session prefix:** DYN- · **Repo:** one4all · **Frontend:** SNOBOL4 · **Backend:** interp

---

## What it is

`scrip-interp` is a SNOBOL4 interpreter that reuses the existing frontend
(lex + parse → `Program*` IR) and executes statements by tree-walking the IR.
It serves two purposes:

1. **Fast corpus runner** — no compile/assemble/link overhead per test
2. **Debug tool** — run `.sno` programs directly, diff vs SPITBOL oracle

**Architecture (per GENERAL-BYRD-DYNAMIC.md):**

- Non-pattern statements (assignment, arithmetic, I/O): evaluated directly
  by `interp_eval()` tree-walking the `EXPR_t` IR.
- **Pattern statements**: `interp_eval()` evaluates subject and pattern
  expressions using `snobol4_pattern.c` constructors (`pat_lit`, `pat_cat`,
  `pat_arb`, etc.) which return `DT_P` descriptors (live `PATND_t` trees).
  These are handed to **`stmt_exec_dyn()`** which calls **`bb_build()`** to
  assemble a Byrd box graph, then runs it through the five-phase executor
  (subject → build pattern → match → replacement → S/F branch).

This means `scrip-interp` DOES use Byrd boxes for pattern execution —
it just builds them at interpretation time rather than emitting static NASM.
The `interp_eval` pattern-expression path must NOT attempt to match patterns
directly; it must always route through `stmt_exec_dyn`.

---

## What already exists (reuse)

| Component | File | Status |
|-----------|------|--------|
| Lexer | `src/frontend/snobol4/lex.c` | ✅ shared |
| Parser | `src/frontend/snobol4/parse.c` | ✅ shared |
| Pattern constructors | `src/runtime/snobol4/snobol4_pattern.c` | ✅ shared |
| NV store (variables) | `src/runtime/snobol4/snobol4.c` | ✅ shared |
| Statement executor | `src/runtime/dyn/stmt_exec.c` | ✅ shared |
| bb_*.c boxes (25+) | `src/runtime/boxes/*/bb_*.c` | ✅ |
| Driver | `src/driver/scrip-interp.c` | ✅ 1090 lines |

---

## Milestone chain

| Milestone | Description | Gate | Status |
|-----------|-------------|------|--------|
| **M-INTERP-A01** | `scrip-interp` binary: parse + execute trivial programs | 20 corpus smoke tests pass | ✅ `200543f` DYN-25 |
| **M-INTERP-A02** | Pattern matching: E_ALT / E_CAPT_* wired | 60 corpus pattern tests pass | ✅ `61639ca` DYN-26 |
| **M-INTERP-A03** | DEFINE / call-stack / user functions | ≥130/142 match | ✅ `1ebaa02` DYN-27 |
| **M-INTERP-A04** | Broad corpus: 169p/9f — OPSYN alias, INDIRECT, ITEM, NRETURN 001/002 | 169/178 broad | ✅ `d411c48` DYN-41 |
| **M-INTERP-A05** | Fix remaining 9 failures → ≥175p broad | ≥175p broad · 142/142 gate | ⬜ DYN-42 next |
| **M-INTERP-B01** | `bb_test.c` per-box unit harness — 25/25 C boxes | 25/25 unit tests pass | ⬜ not started |
| **M-INTERP-B02** | Same harness vs `bb_*.s` objects — C/ASM parity | 25/25 `.s` boxes match `.c` | ⬜ not started |
| **M-INTERP-B03** | Same harness vs `bb_*.java` — Java/C parity | 25/25 Java boxes match `.c` | ⬜ not started — bb_*.java landed J-217 (`7c35456`) |

---

## M-INTERP-A05 — Remaining 9 failures

| Test | Root cause | Fix |
|------|-----------|-----|
| `1013_func_nreturn` 003 | NRETURN lvalue-assign: `ref_a() = 26` — parser doesn't see `(` after IDENT at NRETURN site | Option A: `skip_ws(lx)` in `parse_expr17` before `T_LPAREN` check |
| `1015_opsyn` | OPSYN operator interaction | Trace vs ref |
| `1016_eval` | EVAL edge cases | Trace vs ref |
| `cross`, `expr_eval` | DEFINE/named-pattern interaction | Trace vs ref |
| `test_case`, `test_math`, `test_stack`, `test_string` | scrip harness failures | Trace vs ref |

**DYN-42 approach for 1013/003:** Try Option A first (2-line parser change in
`parse_expr17` — `skip_ws(lx)` after consuming IDENT, before `T_LPAREN` check).
If it breaks anything, fall back to Option B (runtime guard in statement executor).

---

## Build command

```bash
cd /home/claude/one4all
gcc -O0 -g -I src -I src/frontend/snobol4 -I src/runtime/snobol4 \
    -I src/runtime/boxes/shared \
    src/driver/scrip-interp.c \
    src/frontend/snobol4/lex.c src/frontend/snobol4/parse.c \
    src/runtime/snobol4/snobol4.c src/runtime/snobol4/snobol4_pattern.c \
    src/runtime/dyn/stmt_exec.c src/runtime/dyn/eval_code.c \
    $(find src/runtime/boxes -name "bb_*.c") \
    -lgc -lm -o scrip-interp
```

(See `SESSION-dynamic-byrd-box.md §scrip-interp build command` for the
current exact flags — they may have evolved.)

---

## Routing

- **Session doc:** `SESSION-dynamic-byrd-box.md` (DYN- session)
- **Deep ref:** `GENERAL-BYRD-DYNAMIC.md`
- **Related:** `MILESTONE-NET-INTERP.md` — .NET analogue (Pidgin + C# bb boxes)

---

*MILESTONE-DYN-INTERP.md — updated D-166, 2026-04-02, Claude Sonnet 4.6.*
*A01/A02/A03/A04 complete. A05 = DYN-42 next (9 remaining failures). B01/B02 not started.*


---

<!-- SOURCE: MILESTONE-FAST-EMIT-CHECK.md -->

# MILESTONE-FAST-EMIT-CHECK.md — M-G-EMIT-FAST: Fast Emit-Diff Gate

*Authored DYN-13 session, 2026-04-01, Claude Sonnet 4.6*

---

## Problem — root cause measured

`run_emit_check.sh` took **224s** on a 2-core machine for 1286 checks.

Profiled breakdown per `check_one()` invocation:

| Source | Cost | Count | Total |
|--------|------|-------|-------|
| `bash -c` subprocess spawn (xargs) | ~17ms | 1286 | ~22s |
| `mktemp` + `rm` (temp file I/O) | ~18ms | 1286 | ~23s |
| `scrip-cc` compile | ~2ms | 1286 | ~3s |
| `diff` subprocess | ~3ms | 1286 | ~4s |
| **Parallelism headroom (2 cores)** | ÷2 | — | — |
| **Observed wall time** | — | — | **224s** |

**Root causes:**
1. `xargs -P N -I{} bash -c 'check_one ...'` spawns one **bash subprocess per file** — even with `-P N`, each subprocess starts fresh, re-parses the exported function, and pays full bash startup cost (~17ms).
2. `mktemp` creates a real temp file on disk per invocation; `diff` and `rm` each add a syscall round-trip. On a slow container FS this inflates to ~18ms/call.
3. scrip-cc is **called once per file per backend** — 3 separate processes for the same source. The binary already supports multiple input files internally (loops over `files[]`), but the script never uses this.
4. No output reuse: `-o /dev/stdout` pipes per-call then re-reads; the `.s`/`.j`/`.il` oracle files are stat'd + opened per comparison.

**Result:** ~35ms overhead per invocation × 1286 = ~45s overhead alone, magnified by 2-core serialization.

---

## Goal

`run_emit_check.sh` gate time: **< 15s** on a 2-core machine (15× speedup).

---

## Solution: three-level optimization

### Level 1 — Batch scrip-cc per backend (implemented)

Instead of 1286 separate scrip-cc invocations, run **3 invocations total** — one per backend (`-asm`, `-jvm`, `-net`) — each receiving all source files at once. scrip-cc's existing multi-file loop handles this; output goes to `$WORK/out/{asm,jvm,net}/` via derived filenames.

```bash
# Before: 1286 invocations
xargs -P2 -I{} bash -c 'check_one "$1" -asm s' _ {}

# After: 3 invocations total
scrip-cc -asm "${SNO_FILES[@]}"   # all files, derived output names
scrip-cc -jvm "${SNO_FILES[@]}"
scrip-cc -net "${SNO_FILES[@]}"
```

scrip-cc derives output as `$(basename src .sno).{s,j,il}` next to source. We redirect via a WORK dir by symlinking or using `-o` per-file in a prebuilt manifest. See implementation note below.

### Level 2 — Eliminate mktemp: compare directly in memory

scrip-cc multi-file mode writes output next to source (`.s`, `.j`, `.il`). For diff-gate purposes, use `--update` to write into `$WORK/generated/` then diff the whole directory tree with `diff -rq`. No per-file temp files needed.

### Level 3 — Single bash process for result scanning

Replace `xargs ... bash -c 'check_one'` with a single bash loop in the main process. With batch compilation already done, the inner loop is pure diff — no subprocesses needed.

```bash
# After batch compile, all in one bash process:
for src in "${SNO_FILES[@]}"; do
  base="${src%.sno}"
  for be_ext in "asm s" "jvm j" "net il"; do
    backend="${be_ext% *}"; ext="${be_ext#* }"
    got="$WORK/generated/$(basename $base).$ext"
    expected="$(dirname $src)/$(basename $base).$ext"
    diff -q "$got" "$expected" >/dev/null 2>&1 && PASS=$((PASS+1)) || FAIL=$((FAIL+1))
  done
done
```

Zero subprocess spawns in the diff loop. Zero mktemp calls.

---

## Implementation note: WORK dir output from scrip-cc

scrip-cc's multi-file mode derives output filenames next to source, which we cannot redirect. Two options:

**Option A (simpler):** Copy all corpus source files into `$WORK/src/` first, run scrip-cc there, diff against originals. One `cp -r` per run (~2s) but no source pollution.

**Option B (preferred):** Add `--outdir DIR` flag to scrip-cc `main.c` (trivial: ~10 lines). All derived outputs go to `DIR/` with original basename. No source copying needed.

Option B is the permanent fix. Option A is the interim fallback until scrip-cc gets `--outdir`.

---

## Files

| File | Change |
|------|--------|
| `test/run_emit_check.sh` | Rewrite inner loop — batch compile + in-process diff |
| `src/driver/main.c` | Add `--outdir DIR` option (Option B) |
| `.github/MILESTONE-FAST-EMIT-CHECK.md` | This doc |

---

## Gate

```bash
# Before:  Emit-diff 1286/0 — 224s
# After:   Emit-diff 1286/0 — <15s
CORPUS=/home/claude/corpus bash test/run_emit_check.sh
# Must still show: 1286 pass / 0 fail
```

The pass/fail count must not change. This is a pure performance milestone.

---

## Sprint

`DYN-13` — authors: Lon Jones Cherryholmes · Claude Sonnet 4.6


---

<!-- SOURCE: MILESTONE-FAST-INVARIANTS.md -->

# MILESTONE-FAST-INVARIANTS.md — M-G-INV: Fast 3×3 Invariant Harness

*Authored G-7 session, 2026-03-28, Claude Sonnet 4.6*

---

## Problem

The Grand Master Reorg touches all emitters. Every change must be gated by
the full 3×3 invariant matrix (SNOBOL4/Icon/Prolog × x86/JVM/.NET — 7 active
checks). The current runners:

- Recompile all runtime `.o` files **inside every test** (run_rung*.sh each rebuild)
- Run all 7 suites **serially** — wall time ~5–10 min
- Spawn `gcc` hundreds of times for link steps
- No shared runtime archive — link cost paid per test

Running this on every commit or after every emitter edit is prohibitively slow.

## Goal

A single script `test/run_invariants.sh` that:

1. **Builds runtime archives once** at startup — one `.a` per runtime family
2. **Runs all 7 active suites in parallel** — one background job per suite
3. **Reports pass/fail per cell** of the 3×3 matrix, with total wall time
4. **Exits 0** if all active cells pass, **1** if any fail
5. **Target wall time: < 60 seconds** on a 2-core machine

## Optimizations

| Optimization | Mechanism | Savings |
|---|---|---|
| Runtime pre-build | `ar rcs libsno4rt_asm.a *.o` once | Eliminates N×7 gcc -c calls |
| Parallel suites | `suite_fn &` + `wait` for all 7 | Serial→parallel on all cores |
| Per-test link uses archive | `gcc prog.o libsno4rt_asm.a` | Single link command, no .o list |
| Prolog runtime archive | `libsno4rt_pl.a` (atom+unify+builtin) | Same for Prolog x64 |
| No verbose per-test output | Only FAIL lines + final matrix | Less I/O contention |
| TIMEOUT tuned | 5s x86, 10s JVM (JVM startup cost) | No wasted wait |
| scrip-cc pipe | `scrip-cc ... | nasm -f elf64 /dev/stdin` | Skip temp .s file for x86 |

## Script location

`one4all/test/run_invariants.sh`

Called from `SESSION_BOOTSTRAP.sh` HOW block in place of the current
per-suite inline code.

## Success criteria

- All 7 active invariant cells pass (Icon .NET / Prolog .NET: SKIP — not impl)
- Wall time < 60s on 2-core CI container
- Single exit code (0 = all pass)
- Output: concise 3×3 matrix with per-cell status + wall time

## 3×3 output format

```
Invariants (Xs = wall time):
              x86          JVM          .NET
  SNOBOL4   106/106 ✓   106/106 ✓   110/110 ✓
  Icon       38-rung ✓   38-rung ✓      SKIP
  Prolog    30/30   ✓    31/31  ✓      SKIP
────────────────────────────────────────────
  ALL PASS  [12.4s]
```

## Status

| Step | Action | Done |
|------|--------|------|
| M-G-INV-DESIGN | This doc | ✅ G-7 |
| M-G-INV-BUILD | Write `test/run_invariants.sh` with all optimizations | ✅ G-7 |
| M-G-INV-WIRE | Replace SESSION_BOOTSTRAP.sh HOW block with call to `run_invariants.sh` | ✅ G-7 |
| M-G-INV-VERIFY | Run it, confirm all 7 cells report, wall time measured | pending |


---

<!-- SOURCE: MILESTONE-JS-BENCH.md -->

# MILESTONE-JS-BENCH.md — JS Engine Benchmark: one4all vs spipatjs

**Session:** SJ · **Created:** SJ-5, 2026-04-01 · **Author:** Claude Sonnet 4.6

---

## Goal

Measure and compare pattern matching throughput between:
- **one4all engine** (`src/runtime/js/sno_engine.js`) — 532-line iterative
  frame engine (Clojure match.clj model, immutable frames, GC-owned Ω stack)
- **spipatjs** (`github.com/philbudne/spipatjs`) — 3090-line PE node-graph
  engine (GNAT model, pthen-linked nodes, explicit match classes)

Run both **at the same time** in the same Node.js process on the same corpus
of patterns, so JIT warmup and GC conditions are equivalent.

---

## Line counts (as of SJ-5)

| Engine | File | Lines | Model |
|--------|------|-------|-------|
| one4all JS | `sno_engine.js` | 532 | Iterative frame, tagged-union tree |
| spipatjs | `spipat.mjs` | 3090 | PE node graph, pthen links |

Ratio: **~6× smaller**. Architectural difference: spipatjs pre-compiles pattern
graphs at build time (pthen links = O(1) next-node); one4all climbs Ψ parent
stack on every success (O(depth) per node). Hypothesis: spipatjs faster on
simple/linear patterns; one4all competitive on deep-backtrack patterns (ARBNO,
BAL) where the Ω stack allocation advantage matters.

---

## Benchmark suite

Run each pattern × subject pair N=10000 times; report ops/sec.

| ID | Pattern | Subject | Notes |
|----|---------|---------|-------|
| B01 | `'HELLO'` (literal) | `'HELLO WORLD'` | Baseline literal |
| B02 | `BREAK(' ') SPAN(alpha)` | `'the quick brown fox'` | Classic word scan |
| B03 | `ARB 'x'` | `'aaaaaaaaaaax'` | ARB backtrack depth 12 |
| B04 | `ARBNO(SPAN(alpha))` | `'hello world foo'` | ARBNO multi-rep |
| B05 | `BAL` | `'(a(b(c)d)e)rest'` | Balanced parens |
| B06 | `ALT('foo','bar','baz','qux') SPAN(alpha)` | 100-char mixed string | Wide ALT |
| B07 | Nested SEQ 10-deep | 50-char string | Deep sequence |
| B08 | `SPAN(alpha) . WORD` (capture) | `'hello world'` | Capture overhead |

---

## Benchmark harness location

`test/js/bench_engine.js` — standalone Node.js script, no external deps.

Output format (one line per benchmark × engine):
```
B01  one4all   9823456 ops/sec
B01  spipatjs  11234567 ops/sec
```

---

## Gate

- All 8 benchmarks run to completion (no crash, no wrong output)
- Results committed to `test/js/bench_engine_results.txt`
- Summary table added to this file under `## Results`

---

## Implementation notes

- spipatjs is GPL-3 + GCC Runtime Exception — **do not copy code into one4all**
- Import spipatjs as an ES module (`await import(...)`) alongside our CJS engine
- Wrap both in a thin adapter so benchmark loop is identical for both
- Use `performance.now()` for timing; warm up 1000 iterations before measuring

---

## Results

*(to be filled in at milestone completion)*


---

## Results — SJ-6, 2026-04-01

**Node:** v22.22.0  **WARMUP:** 2000  **MEASURE:** 20000

| ID  | one4all (ops/sec) | spipatjs (ops/sec) | ratio | desc |
|-----|------------------:|-------------------:|------:|------|
| B01 | 207,510 | 6,354 | 32.7x | Literal match |
| B02 | 23,578 | 6,072 | 3.9x | BREAK+SPAN word scan |
| B03 | 28,602 | 6,418 | 4.5x | ARB backtrack depth 12 |
| B04 | 232,160 | 6,875 | 33.8x | ARBNO multi-rep |
| B05 | 179,353 | 6,457 | 27.8x | BAL balanced parens |
| B06 | 9,196 | 6,379 | 1.4x | Wide ALT (4 alternatives) |
| B07 | 163,845 | 6,268 | 26.1x | Deep SEQ (10 literals) |
| B08 | 415,434 | 6,406 | 64.9x | CAPT_IMM capture overhead |

**one4all wins all 8 benchmarks.** Range: 1.4x–64.9x faster.

### Analysis

spipatjs throughput is nearly flat (~6,000–6,900 ops/sec) across all patterns
regardless of complexity. Root cause: `Pattern.umatch()` calls `Object.freeze(m)`
on the Match result object on every successful match — this is an O(n) GC write-
barrier operation that dominates the timing. The PE node-graph pthen advantage
is completely masked by this per-call freeze cost.

one4all's advantage is largest on:
- **B08 CAPT_IMM (64.9x)**: short fast path, no freeze overhead
- **B04 ARBNO (33.8x)**: lazy expansion via GC-owned frame tree is cheaper
  than spipatjs's stack management inside freeze-gated match objects
- **B01 Literal (32.7x)**: pure allocation/startup cost dominates spipatjs

**B06 Wide ALT (1.4x)** is the closest: our string-concatenated switch key
`(λ + '/' + action)` pays for itself vs spipatjs's class dispatch only when
pattern complexity is high enough to amortize the freeze cost.

### Conclusion

The Clojure-model engine (immutable frame arrays, GC-owned Ω stack, zero
post-match allocation) is decisively faster in Node.js v22 than the GNAT PE
node-graph model with result freezing. For production use: one4all engine.

Gate: ✅ All 8 benchmarks ran, results committed.


---

<!-- SOURCE: MILESTONE-JS-ICON.md -->

# MILESTONE-JS-ICON.md — Icon × JavaScript Milestone Ladder

**Session:** IJJ · **Oracle:** `emit_wasm_icon.c` (IR switch) + `emit_jvm_icon.c` (Byrd wiring)
**Invariant cell:** `icon_js` (added at M-IJJ-A01)
**Emit-diff gate:** 981/4 throughout

---

## Dependency answer: SNOBOL4 JS runtime first

Icon JS **depends on** M-SJ-A01 (scaffold + runtime). The `sno_runtime.js`
provides the trampoline engine and base types that Icon JS extends.
Icon-specific: generators via `function*` OR trampoline continuations.
Recommendation: use trampoline (consistent with other backends, no
generator frame overhead for deeply nested expressions).

---

## Phase A — Foundation

### M-IJJ-A01 — Scaffold + hello/arith parity

**Depends on:** M-SJ-A01 (shared trampoline engine)
**Scope:**
- Create `src/backend/emit_js_icon.c` — mirrors `emit_wasm_icon.c` IR switch
- `icon_runtime.js` extending `sno_runtime.js`: `_icon_fail`, `_icon_succ`
- Handle: literals, arithmetic, string ops, `E_ASSIGN`, `E_VAR`
- OUTPUT: `write()` procedure

**Gate:** `icon_js` cell: hello/arith pass · emit-diff 981/4 ✅

---

### M-IJJ-A02 — Goal-directed: E_TO, E_GENALT, numeric relational

**Depends on:** M-IJJ-A01
**Scope:**
- `E_TO`: `i to j` — trampoline state machine with `_to_i` counter
  (Proebsting §4.4 template directly)
- `E_GENALT` (`|` alternation): `_alt_i` counter routing
- `E_LT/E_LE/E_GT/E_GE/E_EQ/E_NE` — numeric relational (goal-directed:
  succeed yielding rhs if condition holds, else ω)
- `E_EVERY` drive-to-exhaustion loop

**Gate:** `(1 to 5)` · `(1 to 3) * (1 to 2)` · `5 > ((1 to 2)*(3 to 4))`
match Proebsting Figure 2 optimized output · emit-diff 981/4 ✅

---

### M-IJJ-A03 — Suspension: E_SUSPEND, co-expressions

**Depends on:** M-IJJ-A02
**Scope:**
- `E_SUSPEND` (`@` — suspend/yield from procedure)
- `create expr` co-expression constructor
- `@coexpr` activation — swap continuation

**Gate:** rung03_suspend tests pass · emit-diff 981/4 ✅

---

## Phase B — String Scanning and Structures

### M-IJJ-B01 — String scanning: E_MATCH / E_SCAN_AUGOP

**Depends on:** M-IJJ-A03
**Scope:**
- `E_MATCH` (`subject ? pattern`) — Icon scanning
- `E_SCAN_AUGOP` augmented scan
- String positional functions: `pos()`, `move()`, `tab()`, `many()`, `upto()`

**Gate:** icon string scanning tests pass · emit-diff 981/4 ✅

---

### M-IJJ-B02 — Structures: lists, records, E_MAKELIST, E_FIELD

**Depends on:** M-IJJ-B01
**Scope:**
- `E_MAKELIST` `[e1,e2,...]` → JS array
- `E_RECORD` declaration → JS class
- `E_FIELD` `.name` → property access
- `E_ITER` `!E` — iterate list/string elements
- `E_SECTION` `E[i:j]` string/list section

**Gate:** icon structure tests pass · emit-diff 981/4 ✅

---

### M-IJJ-PARITY — Full corpus parity

**Depends on:** M-IJJ-B02
**Gate:** `icon_js` ≥ `icon_x86` pass count · emit-diff 981/4 ✅

---

*MILESTONE-JS-ICON.md — created IJJ-1, 2026-03-31, Claude Sonnet 4.6.*


---

<!-- SOURCE: MILESTONE-JS-PROLOG.md -->

# MILESTONE-JS-PROLOG.md — Prolog × JavaScript Milestone Ladder

**Session:** PJJ · **Oracle:** `emit_wasm_prolog.c` (IR switch) + `emit_jvm_prolog.c` (Byrd wiring)
**Invariant cell:** `prolog_js` (added at M-PJJ-A01)
**Emit-diff gate:** 981/4 throughout

---

## Dependency answer: SNOBOL4 JS runtime first, then Icon JS optional

Prolog JS **depends on** M-SJ-A01 (trampoline engine). It does NOT depend
on Icon JS. Prolog uses continuation-passing style for unification and
backtracking — different from Icon's generator model, same trampoline engine.

Each Prolog clause becomes a trampoline block. The choice point (E_CHOICE)
becomes a chain of α/β functions — try first clause on α, second clause on
β, etc. E_CUT seals the β chain.

---

## Phase A — Foundation

### M-PJJ-A01 — Scaffold + hello/facts/unify parity

**Depends on:** M-SJ-A01 (shared trampoline engine)
**Scope:**
- Create `src/backend/emit_js_prolog.c` — mirrors `emit_wasm_prolog.c` IR switch
- `prolog_runtime.js`: term representation, `_unify(t1,t2,trail)`,
  trail stack, undo trail on backtrack
- Handle: atoms, integers, `E_UNIFY`, `E_CLAUSE`, `E_CHOICE` (single clause)
- Simple facts: `foo(a). foo(b).` → two block functions chained via `E_CHOICE`

**Gate:** `prolog_js` cell: hello/atom/fact pass · emit-diff 981/4 ✅

---

### M-PJJ-A02 — Multi-clause predicates + backtracking

**Depends on:** M-PJJ-A01
**Scope:**
- `E_CHOICE` α/β chain across N clauses
- Trail unwind on β: `_trail_unwind(mark)` restores variable bindings
- `E_TRAIL_MARK` / `E_TRAIL_UNWIND` wiring
- Variable terms: unbound var → JS object `{ref: null}`, bound → `{ref: term}`
- Tests: `member/2`, `append/3`

**Gate:** rung multi-clause backtrack tests pass · emit-diff 981/4 ✅

---

### M-PJJ-A03 — Arithmetic: E_FNC(is), comparison

**Depends on:** M-PJJ-A02
**Scope:**
- `is/2` — evaluate arithmetic expression, unify with lhs
- Numeric comparison: `</2`, `>/2`, `=:=/2`, `=\=/2`
- `E_FNC` dispatch for Prolog builtins

**Gate:** Prolog arithmetic tests pass · emit-diff 981/4 ✅

---

## Phase B — Lists and Control

### M-PJJ-B01 — Lists: `[H|T]` unification, list builtins

**Depends on:** M-PJJ-A03
**Scope:**
- List term: `[H|T]` → JS `{head, tail}` cons cell
- Unification over cons cells (recursive)
- `length/2`, `member/2`, `append/3` corpus tests

**Gate:** Prolog list tests pass · emit-diff 981/4 ✅

---

### M-PJJ-B02 — Cut, negation-as-failure

**Depends on:** M-PJJ-B01
**Scope:**
- `E_CUT` — seal β of enclosing `E_CHOICE` (trampoline: null out retry fn)
- `\+` negation-as-failure — try goal, succeed if it fails, fail if it succeeds
- `once/1`

**Gate:** cut/negation tests pass · emit-diff 981/4 ✅

---

### M-PJJ-B03 — assert/retract (dynamic predicates)

**Depends on:** M-PJJ-B02
**Scope:**
- `assert(Clause)` → add to JS predicate table at runtime
- `retract(Clause)` → remove from table
- Predicate table: JS `Map` from functor/arity to clause list
- This is Prolog's analog of SNOBOL4's `CODE()` — runtime clause addition

**Gate:** assert/retract tests pass · emit-diff 981/4 ✅

---

### M-PJJ-PARITY — Full corpus parity

**Depends on:** M-PJJ-B03
**Gate:** `prolog_js` ≥ `prolog_x86` pass count · emit-diff 981/4 ✅

---

*MILESTONE-JS-PROLOG.md — created PJJ-1, 2026-03-31, Claude Sonnet 4.6.*


---

<!-- SOURCE: MILESTONE-JS-SNOBOL4.md -->

# MILESTONE-JS-SNOBOL4.md — SNOBOL4 × JavaScript Milestone Ladder

**Session:** SJ · **Oracle:** `scrip-interp.c` (interpreter) · `emit_byrd_c.c` (emitter, Phase D)
**Architecture:** Interpreter first → Emitter after (interpreter proven)
**Gate (Phases A–C):** Interpreter regression only — no emit-diff, no snobol4_x86 invariants
**Gate (Phase D+):** emit-diff + snobol4_js invariants added when emitter work begins

---

## Organizing principle

One track, two sequential phases of work:

1. **Interpreter (Phases A–C):** Lex → Parse → IR → execute via stack machine +
   JS Byrd-box sequencer. Oracle: `scrip-interp.c`. IR is identical to what
   `scrip-cc` builds. The two execution engines are:
   - **Stack machine** — evaluates expressions, drives Phases 1, 4, 5
   - **Byrd-box sequencer** — drives pattern match, Phases 2, 3

   JS Byrd boxes live in `one4all/src/runtime/boxes/*/bb_*.js`.
   The interpreter does NOT walk the IR tree the way `scrip-interp.c` does —
   it executes via the stack machine + sequencer instead.

2. **Emitter (Phase D+):** `emit_js.c` static code generation, built on the
   proven interpreter. Oracle: `emit_byrd_c.c`. Added after Phase C complete.

---

## 5-Phase statement execution

Every SNOBOL4 statement runs through 5 phases (oracle: `stmt_exec.c`):

```
Phase 1: build_subject  — resolve subject variable or expression → Σ/Δ/Ω
Phase 2: build_pattern  — IR pattern node → live {α,β} JS Byrd box graph
Phase 3: run_match      — drive root.α() via trampoline, collect captures
Phase 4: build_repl     — evaluate replacement expression → value
Phase 5: perform_repl   — splice into subject, assign, take :S/:F branch
```

Pattern-free statements skip Phases 2+3.

---

## Key files

| File | Role |
|------|------|
| `src/runtime/js/sno-interp.js` | **Main interpreter** — stack machine + BB sequencer |
| `src/runtime/boxes/*/bb_*.js` | **JS Byrd boxes** — one per box type |
| `src/runtime/js/sno_runtime.js` | Value types, builtins, I/O |
| `src/driver/scrip-interp.c` | **Oracle** — C tree-walk interpreter (reference only) |
| `src/runtime/dyn/stmt_exec.c` | **Oracle** — 5-phase executor |
| `src/backend/c/emit_byrd_c.c` | Oracle for Phase D emitter (future) |

---

## Phase A — Lexer, Parser, IR, Scaffold

### M-SJ-A01 — Lexer: tokenize SNOBOL4 source

**Depends on:** nothing (first milestone)
**Oracle:** `src/frontend/snobol4/lex.c`
**Scope:**
- `src/runtime/js/lex.js` — tokenize SNOBOL4 source file
- Token types: label, subject, pattern, replacement, goto, continuation
- Output: token stream consumable by parser
- Corpus `rungJS00/`: lex smoke tests

**Gate:** rungJS00 lex tests pass ✅

---

### M-SJ-A02 — Parser: token stream → IR tree

**Depends on:** M-SJ-A01
**Oracle:** `src/frontend/snobol4/parse.c` · `src/frontend/snobol4/scrip_cc.h`
**Scope:**
- `src/runtime/js/parse.js` — produce IR identical to `scrip-cc`
- `Program` → linked list of `STMT_t`
- `STMT_t` fields: label, subject `EXPR_t*`, pattern `EXPR_t*`, replacement `EXPR_t*`, goto
- `EXPR_t` node kinds: all E_* from `ir.h`
- Corpus `rungJS01/`: parse smoke (round-trip label/subject/goto)

**Gate:** rungJS01 parse tests pass ✅

---

### M-SJ-A03 — Stack machine: Phase 1 + Phase 5 (no pattern)

**Depends on:** M-SJ-A02
**Oracle:** `scrip-interp.c` `interp_eval()` · `stmt_exec.c` Phase 1 + Phase 5
**Scope:**
- `sno-interp.js`: `eval_expr(node)` stack machine — `E_QLIT`, `E_ILIT`, `E_VAR`,
  `E_ASSIGN`, `E_CONCAT`, arithmetic ops
- `exec_stmt()` Phase 1: resolve subject
- `exec_stmt()` Phase 5 (no-pattern path): assign + `:S/:F` dispatch
- Label table + goto dispatch loop
- `OUTPUT` variable → stdout
- Corpus `rungJS02/`: hello, assignment, goto, label

**Gate:** rungJS02 pass ✅

---

### M-SJ-A04 — Stack machine: full value layer (Phase 4 complete)

**Depends on:** M-SJ-A03
**Oracle:** `scrip-interp.c` `interp_eval()` full switch
**Scope:**
- All arithmetic: `E_ADD`, `E_SUB`, `E_MPY`, `E_DIV`, `E_MOD`, `E_POW`, `E_NEG`
- String builtins: `SIZE`, `REPLACE`, `DUPL`, `REVERSE`, `TRIM`, `SUBSTR`, `LPAD`, `RPAD`
- Conversion: `INTEGER`, `REAL`, `CONVERT`
- `E_INDR` indirect reference (`$expr`)
- `E_KEYWORD` (`&ANCHOR`, `&TRIM`, etc.)
- Corpus `rungJS03/`: arithmetic, string ops, keywords

**Gate:** rungJS03 pass ✅

---

## Phase B — Pattern Matching (Phases 2 + 3)

### M-SJ-B01 — BB sequencer bootstrap: E_QLIT + scan loop

**Depends on:** M-SJ-A04
**Oracle:** `stmt_exec.c` Phase 2+3 · `bb_lit.js` (already written)
**Scope:**
- `sno-interp.js`: `build_pattern(node)` dispatcher → `{α,β}` root box
- Wire `bb_lit.js` for `E_QLIT`
- Scan loop: `for (cursor=0; cursor<=Σ.length; cursor++)`
- `&ANCHOR`: position-0 only when non-zero
- Phase 5 (match path): splice matched portion from subject
- Corpus `rungJS04/`: literal match, literal replace

**Gate:** rungJS04 pass ✅

---

### M-SJ-B02 — E_SEQ wiring

**Depends on:** M-SJ-B01
**Oracle:** `bb_seq.js` · `emit_byrd_c.c` `emit_seq()`
**Scope:**
- `build_pattern()`: `E_SEQ` → wire `seq_α→left_α`, `left_γ→right_α`,
  `right_ω→left_β`, `right_γ→seq_γ`
- n-ary SEQ: right-fold children
- Corpus `rungJS05/`: concatenated patterns

**Gate:** rungJS05 pass ✅

---

### M-SJ-B03 — E_ALT alternation

**Depends on:** M-SJ-B02
**Scope:**
- `build_pattern()`: `E_ALT` → `alt_α→left_α`, `left_ω→right_α`, `right_ω→alt_ω`
- Corpus `rungJS06/`: alternation tests

**Gate:** rungJS06 pass ✅

---

### M-SJ-B04 — E_ARBNO / E_ARB

**Depends on:** M-SJ-B03
**Scope:**
- `E_ARBNO`: zero-or-more; zero-advance guard
- `E_ARB`: try empty first, β tries longer
- Corpus `rungJS07/`

**Gate:** rungJS07 pass ✅

---

### M-SJ-B05 — All pattern primitives

**Depends on:** M-SJ-B04
**Scope:**
- All remaining E_* pattern nodes: `E_LEN`, `E_POS`, `E_RPOS`, `E_TAB`,
  `E_RTAB`, `E_REM`, `E_ANY`, `E_NOTANY`, `E_SPAN`, `E_BREAK`, `E_BREAKX`,
  `E_FENCE`, `E_FAIL`, `E_SUCCEED`, `E_ABORT`, `E_BAL`
- Each wires its `bb_*.js` box into `build_pattern()`
- Corpus `rungJS08/`

**Gate:** rungJS08 pass ✅

---

### M-SJ-B06 — Captures: COND / IMM / CUR + Phase 5 commit

**Depends on:** M-SJ-B05
**Oracle:** `stmt_exec.c` capture-flush logic
**Scope:**
- `.var` conditional capture: buffer on γ, flush in Phase 5
- `$var` immediate capture: write on each advance
- `@var` cursor position capture
- Phase 5: commit pending capture list after overall match success
- Corpus `rungJS09/`

**Gate:** rungJS09 pass ✅

---


### M-SJ-B07 — PAT-VALUE STORAGE: retire E_SEQ/E_CAT dual-use ambiguity at runtime

**Depends on:** M-SJ-B06
**Sprint:** SJ-14
**Oracle:** `scrip-interp.c` — C interpreter stores pattern values as opaque DESCR_t pattern pointers; assignment of a pattern expression stores the pattern, not a string.
**Scope:**
- `sno-interp.js` — `_expr_is_pat(e)`: module-level predicate mirroring parser._is_pat()
- `interp_eval(E_SEQ)`: if `_expr_is_pat(e)` → route to `_build_pat(e)` returning a `{__pat}` object; else fall through to string concat
- Result: `PAT = " the " ARB . OUTPUT ("..." | "...")` stores a live pattern object in `_vars['PAT']`; subsequent `LINE ? PAT` retrieves it via `_build_pat E_VAR __pat` fast path — no stringify
- Secondary bug (NOT yet fixed): spurious intermediate OUTPUT writes during ARB backtracking — traced to a second OUTPUT-writing path outside the engine's `_pending_cond` deferral; see SJ-15 first actions

**Gate:** word1–word4 / wordcount / cross passing ✅ *(secondary OUTPUT bug must also be fixed)*

---

## Phase C — Functions, Data Structures, EVAL

### M-SJ-C01 — Arrays / Tables / DATA types

**Depends on:** M-SJ-B06
**Scope:**
- `ARRAY()` → JS array · `TABLE()` → JS `Map`
- `DATA()` → JS class · `FIELD()` → property access
- `E_IDX` subscript (read + lvalue)
- Corpus `rungJS10/`

**Gate:** rungJS10 pass ✅

---

### M-SJ-C02 — User-defined functions / DEFINE

**Depends on:** M-SJ-C01
**Oracle:** `scrip-interp.c` `call_user_function()` · `prescan_defines()`
**Scope:**
- `DEFINE('fname(p1,p2,...)')` registration
- `E_FNC` call: save/restore local scope
- `RETURN` / `FRETURN` / `NRETURN`
- Recursion: fresh local scope per call
- Corpus `rungJS11/`

**Gate:** rungJS11 pass ✅

---

### M-SJ-C03 — EVAL() / CODE()

**Depends on:** M-SJ-C02
**Scope:**
- `sno_eval(str)` — compile + execute SNOBOL4 expression string
- `sno_code(str)` — compile + execute SNOBOL4 statement block
- Reuses the lexer/parser/interpreter pipeline recursively
- Corpus `rungJS12/`

**Gate:** rungJS12 pass ✅

---

### M-SJ-INTERP — Interpreter parity

**Depends on:** M-SJ-C03
**Scope:** All rungJS00–JS12 + rung2–rung11 passing through interpreter.
Interpreter at parity with `scrip-interp.c` on full corpus.

**Gate:** interpreter pass count ≥ `scrip-interp.c` on same corpus ✅

---

## Phase D — Emitter (after interpreter proven)

### M-SJ-D01 — emit_js.c scaffold + hello

*(Unlocked after M-SJ-INTERP)*
**Oracle:** `emit_byrd_c.c` · proven interpreter as reference
**Scope:** `emit_js.c` emitter scaffold, `sno_engine.js` static fast path.
Gates reintroduce emit-diff + `snobol4_js` invariants.

*(Milestones D02+ to be specified at M-SJ-INTERP time.)*

---

## Sprint Sequence

| Sprint | Milestone | Key work |
|--------|-----------|----------|
| SJ-6 | M-SJ-A01 | Lexer (`lex.js`) |
| SJ-7 | M-SJ-A02 | Parser (`parse.js`) → IR |
| SJ-8 | M-SJ-A03 | Stack machine Phase 1+5 · goto · label · OUTPUT |
| SJ-9 | M-SJ-A04 | Full value layer — arithmetic, builtins, keywords |
| SJ-10 | M-SJ-B01 | BB sequencer bootstrap · E_QLIT · scan loop |
| SJ-11 | M-SJ-B02–B03 | E_SEQ · E_ALT |
| SJ-12 | M-SJ-B04–B05 | ARBNO/ARB + all 16 primitives |
| SJ-13 | M-SJ-B06 | Captures + Phase 5 commit flush |
| SJ-14 | M-SJ-B07 | PAT-value storage — _expr_is_pat + E_SEQ routing (partial) |
| SJ-15 | M-SJ-B07 (complete) + M-SJ-C01 | Fix spurious OUTPUT + ARRAY/TABLE/DATA |
| SJ-15 | M-SJ-C02 | DEFINE/user-fns |
| SJ-16 | M-SJ-C03 | EVAL()/CODE() |
| SJ-17 | M-SJ-INTERP | Interpreter parity sweep |
| SJ-18+ | M-SJ-D01+ | Emitter phase begins |

---

*MILESTONE-JS-SNOBOL4.md — rewritten SJ-6, 2026-04-02, Claude Sonnet 4.6.*
*Interpreter-first architecture. Emitter (Phase D) follows after interpreter proven.*
*Oracle for interpreter: scrip-interp.c. Oracle for emitter: emit_byrd_c.c.*


---

<!-- SOURCE: MILESTONE-JVM-SNOBOL4.md -->

# MILESTONE-JVM-SNOBOL4.md — SNOBOL4 × JVM Milestone Ladder

**Session:** J · **Work file:** `src/backend/emit_jvm.c` (one4all)
**Milestone ladder:** this file · **Baseline:** `94p/32f` (J-216, `a74ccd8`)

---

## The architectural distinction that drives everything

`snobol4jvm` (Clojure) and `one4all` JVM backend (`emit_jvm.c`) both target
the JVM — but they implement pattern matching in fundamentally different ways:

**snobol4jvm** — interpreted frame walker:
`match.clj` `engine` takes a pattern tree as *data* and walks it at runtime
using a 7-element frame vector `[Σ Δ σ δ Π φ Ψ]`, dispatching on
`:proceed/:succeed/:recede/:fail` actions.  The pattern tree is data; the
engine loop is code.  One engine handles all patterns.

**one4all emit_jvm.c** — compiled pure Byrd boxes:
`emit_jvm_pat_node()` compiles each pattern AST node to *Jasmin labels*
at compile time.  α/γ/ω are literal JVM goto targets baked into the `.class`
file.  There is no interpreter loop at runtime — the compiled class IS the
Byrd box graph.  This is the same model as `emit_byrd_asm.c` targeting x86:
same IR, same labeled-goto structure, different instruction set.

**Consequence for oracles:**

| What | Oracle | Why |
|------|--------|-----|
| 5-phase semantics — what each phase must produce | `snobol4jvm/runtime.clj` + `match.clj` | Proven at 1,896 tests / 4,120 assertions / 0 failures |
| Phase 2+3 implementation — how to emit compiled Byrd boxes | `emit_byrd_asm.c` | Same compiled-label model, same IR, same corpus |
| Inline expression strategy | `snobol4jvm/jvm_codegen.clj` Stage 23E | IFn inlining maps to Jasmin inline bytecode |
| EVAL/CODE dynamic compilation | `snobol4jvm/compiler.clj` CODE | re-entrant parse→emit→load pipeline |

`snobol4jvm` is the **semantic oracle**.
`emit_byrd_asm.c` is the **structural oracle** for pattern emission.
Both must be read before writing any new pattern or EVAL/CODE code.

---

## The 5-phase statement executor

Every SNOBOL4 statement executes in exactly five phases:

```
Phase 1: build_subject  — resolve subject variable or expr → String (local L6)
Phase 2: build_pattern  — pattern AST → compiled Byrd box label graph
Phase 3: run_match      — scan loop drives root box α labels; captures collected
Phase 4: build_repl     — replacement expression → value already on stack
Phase 5: perform_repl   — splice into subject, sno_var_put, take :S/:F branch
```

The compiled class for a pattern statement IS Phases 2+3 — the label graph
runs directly, no dispatch overhead.  `snobol4jvm/runtime.clj` RUN loop
defines what must happen in each phase; `emit_byrd_asm.c` defines how it
compiles to labeled gotos.

---

## Oracle Read Order (before writing any pattern or EVAL/CODE code)

```bash
# Semantic oracle — what phases must produce
sed -n '35,110p' snobol4jvm/src/SNOBOL4clojure/runtime.clj     # RUN loop: Phase 1+5
sed -n '1,30p'   snobol4jvm/src/SNOBOL4clojure/match.clj        # engine API + frame model
grep -n "CAPTURE\|pending-cond\|commit" snobol4jvm/src/SNOBOL4clojure/match.clj  # Phase 5 captures

# Structural oracle — how to compile Byrd boxes to labeled gotos
grep -n "case E_QLIT\|case E_SEQ\|case E_ALT\|case E_ARBNO\|emit_asm_pat" \
    src/backend/emit_byrd_asm.c | head -20                       # x86 pattern node emitter
sed -n '2990,3070p' src/backend/emit_jvm.c                       # JVM scan loop + local layout

# Inline-emit oracle — expression strategy
sed -n '170,250p' snobol4jvm/src/SNOBOL4clojure/jvm_codegen.clj # inline-emit! patterns

# EVAL/CODE oracle
sed -n '119,188p' snobol4jvm/src/SNOBOL4clojure/compiler.clj    # CODE! + CODE
sed -n '465,490p' snobol4jvm/src/SNOBOL4clojure/operators.clj   # EVAL dispatch
```

---

## M-JVM-INTERP — Dynamic JVM Byrd Box Interpreter (Phase 0)

**Rationale:** Build a JVM equivalent of `scrip-interp.c` (DYN- session) in Java, using `src/runtime/boxes/bb_*.jasmin` (assembled to `boxes.jar`) as the Byrd box execution layer. The interpreter exercises the **exact same Jasmin bytecode** that `emit_jvm.c` generates — no proxy, no translation gap. `bb_*.java` is human-readable reference only, never loaded at runtime.

**Box execution layer: Jasmin only.** `bb_*.jasmin` → `jasmin.jar` → `bb/bb_*.class` → `boxes.jar`. Package `bb`. Java source compiles against `bb_*.java` stubs for type-checking; at runtime only `boxes.jar` is on the classpath.

**Architecture: Java frontend + Jasmin Byrd box sequencer**

```
NON-PATTERN execution (Phases 1, 4, 5):
  Java interpreter — NV store, eval(), builtin dispatch
  Lexer.java → Parser.java → Interpreter.java

PATTERN execution (Phases 2 + 3):
  PatternBuilder.java  — ExprNode IR → bb_*.jasmin box graph
  bb_executor (Jasmin) — scan loop, updates ms.delta, commits deferred captures on :S
  Boxes share single bb_box$MatchState; exec() 7-arg canonical form passes ms
```

**Oracles:**
- `src/frontend/snobol4/lex.c` + `parse.c` — lexer/parser structure
- `scrip-interp.c` + `stmt_exec.c` — eval loop oracle
- `bb_*.java` — readable reference for each box's α/β logic (NOT the execution artifact)
- `src/backend/emit_jvm.c` + `emit_byrd_asm.c` — emitter structural oracle

**Status (J-228):** Interpreter operational at **121p/57f** (178 total) against `boxes.jar`.
Remaining Jasmin-specific regressions vs 136p Java-stub baseline:
- `bb_arbno.jasmin` VerifyError in `tryBody` — stack type mismatch
- `bb_any`/`bb_rpos` logic regression — val() transform hit wrong boxes
Pre-existing failures (42): ARRAY/TABLE/DATA, rung10 recursion, expr_eval, stcount.

**M-JVM-INTERP breakdown:**

### M-JVM-INTERP-A00: Jasmin Boxes
- Write `bb_*.jasmin` for all 25 boxes + `BbBox.jasmin` base + `BbExecutor.jasmin`
- **Oracle:** `bb_*.java` (human-readable reference, same logic, same α/β/γ/ω structure)
- Assemble: `jasmin.jar` → `bb_*.class` → `boxes.jar`
- **Gate:** All 25 boxes assemble clean; `BbExecutor` instantiates `BbLit` and runs a trivial α/ω smoke test

### M-JVM-INTERP-A01: Lexer
- `src/driver/jvm/Lexer.java` — tokenize SNOBOL4 source
- Token types mirror `src/frontend/snobol4/lex.c` token enum
- **Oracle:** `src/frontend/snobol4/lex.c`
- **Gate:** All 19 NET-INTERP parse test inputs tokenize without error

### M-JVM-INTERP-A02: Parser
- `src/driver/jvm/Parser.java` — recursive descent, produces `StmtNode[]`
- Typed Java AST nodes: `StmtNode`, `ExprNode`, `PatNode` (mirror C AST structs)
- **Oracle:** `src/frontend/snobol4/parse.c` + `MILESTONE-NET-INTERP.md §Pidgin parser`
- **Gate:** 19/19 parse test cases produce correct AST (pretty-print matches reference)

### M-JVM-INTERP-A03: IR Tree
- `src/driver/jvm/IrBuilder.java` — lowers typed AST → IR instruction list + PatNode subtrees
- **Stack machine IR:** typed opcode nodes (`PUSH_VAR`, `PUSH_LIT`, `CALL`, `ASSIGN`, `BRANCH_S`, `BRANCH_F`, etc.) — one opcode per future JVM bytecode sequence
- **Pattern IR:** `PatNode` tree with same node kinds as `PATND_t` in scrip-cc — consumed by PatternBuilder
- IR node design must have 1:1 correspondence to emit_jvm.c operations (design invariant)
- **Oracle:** `src/runtime/dyn/stmt_exec.c bb_build()` (lines 407–640) + `src/backend/emit_jvm.c`
- **Gate:** IR pretty-prints cleanly for all 19 parse test inputs; each opcode maps to a named emit_jvm.c operation

### M-JVM-INTERP-A04: Interpreter + Byrd Box Sequencer + Test Harness
- `src/driver/jvm/Interpreter.java` — dispatches stack machine IR opcodes (Phases 1, 4, 5)
- `src/driver/jvm/PatternBuilder.java` — walks PatNode IR → instantiates Jasmin-assembled `bb_*.class` graph (Phase 2)
- `BbExecutor` (Jasmin) sequences α/β/γ/ω signals through box graph (Phase 3) ✅ (from A00)
- `SnobolEnv.java` — variable store (`Map<String, SnobolValue>`)
- Corpus runner: `test/run_interp_jvm.sh` — diff vs SPITBOL oracle
- **Oracle:** `stmt_exec.c` 5-phase loop + `bb_executor.java` + `MILESTONE-DYN-INTERP.md`
- **Gate:** ≥ 20 corpus smoke tests pass (rung1); ready for M-JVM-INTERP-A05

### M-JVM-INTERP-A05: Baseline Verification
- Target: match `scrip-interp.c` behavior across full corpus
- Establish interpreter as rapid testbed for M-JVM-A02+ compiled path
- **Gate:** ≥ 94p broad corpus (matches DYN- baseline); ready to proceed to M-JVM-A02

---

## Jasmin Byrd Box runtime — `src/runtime/boxes/*/bb_*.jasmin` + `boxes.jar`

**Assembled J-220, packaged J-227/J-228. one4all `src/runtime/boxes/jasmin/boxes.jar`.**

Every box exists in Jasmin source alongside the other language siblings:

```
bb_lit.c    bb_lit.s    bb_lit.cs    bb_lit.java    bb_lit.jasmin  ← EXECUTION
bb_seq.c    bb_seq.s    bb_seq.cs    bb_seq.java    bb_seq.jasmin
... (all 25+ boxes)
shared/bb_box.java      shared/bb_box.jasmin
shared/bb_executor.java shared/bb_executor.jasmin
```

**`bb_*.jasmin` is the execution layer. `bb_*.java` is a human-readable reference only — never loaded at runtime.**

Jasmin sources live in each box's per-box subdirectory (e.g. `lit/bb_lit.jasmin`)
and are mirrored to `jasmin/` flat dir for bulk assembly. Package: `bb` (all classes
in `bb/bb_*.class` inside `boxes.jar`).

**Key API facts (from assembled bytecode — authoritative):**
- All box constructors: `(bb/bb_box$MatchState, <args>)V`
- `bb_executor.exec()` 7-arg canonical: `(String, String, bb/bb_box$MatchState, bb/bb_box, boolean, String, boolean)Z` — boxes share the ms passed here; exec updates ms.delta each scan step
- `bb_len/pos/rpos/tab/rtab`: two constructors — `(ms, int)` and `(ms, IntSupplier)` for dynamic var args
- Inner class names: camelCase (`bb_box$MatchState`, `bb_box$Spec`, `bb_executor$VarStore`, etc.)
- Interfaces in package bb: `bb_executor$VarStore`, `bb_dvar$BoxResolver`, `bb_capture$VarSetter`, `bb_atp$IntSetter`

**Rebuild command:**
```bash
cd src/runtime/boxes/jasmin
java -jar ../../backend/jasmin.jar -d /tmp/jasmin_out *.jasmin
cd /tmp/jasmin_out && jar cf .../boxes.jar bb/*.class
```

**Compile driver against bb_*.java stubs (compile-time type-checking only):**
```bash
BB_STUBS=/tmp/bb_stubs
javac -d $BB_STUBS $(find src/runtime/boxes -name "*.java")
javac -cp $BB_STUBS -d /tmp/jvm_jasmin src/driver/jvm/*.java
# Run: java -cp /tmp/jvm_jasmin:src/runtime/boxes/jasmin/boxes.jar driver.jvm.Interpreter <file.sno>
```

---

## Current state of `emit_jvm_pat_node()`

Already implemented (pre-pivot work):
- `E_QLIT` — `regionMatches` + cursor advance + γ/ω
- `E_SEQ` — right-fold, ARB+backtrack greedy loop, deferred capture commit
- `E_ALT` — cursor-save, try left, restore, try right
- `E_CAPT_COND_ASGN` (`.var`) — deferred capture with temp local
- `E_CAPT_IMMED_ASGN` (`$var`) — immediate `sno_var_put` on γ
- `E_CAPT_CURSOR` (`@var`) — cursor position capture
- `ARBNO(child)` — greedy loop with zero-advance guard
- `ANY(charset)`, `NOTANY(charset)` — `charAt` + `contains`
- Scan loop with `&ANCHOR` check and cursor retry

**The Byrd box compilation infrastructure is substantially built.**
The 32 failures at 94p/32f are not pattern-engine gaps — they are value-layer
and DATA/function gaps in the non-pattern paths (rung8 strings, rung10
functions, rung11 DATA, 2D subscript).

---

## Phase 1 — Value Layer Completion

### M-JVM-A01 — Scaffold through goto/branching ✅

**Status:** Done (J0–J3, pre-pivot). 94p/32f baseline.

---

### M-JVM-A02 — Value layer complete + 2D subscript fix

**Depends on:** M-JVM-A01
**Oracle:** `snobol4jvm/runtime.clj` + `jvm_codegen.clj` inline-emit patterns
**Scope:**
- **2D subscript bug**: `E_IDX` write path (`emit_jvm_stmt` lines ~2658–2700) —
  fix `nchildren>=3` case to build `"row,col"` composite key.
  Read `emit_byrd_asm.c` lines ~3530–3570 first (structural co-oracle).
- String builtins: `REPLACE`, `DUPL`, `REVERSE`, `TRIM`, `SUBSTR`, `LPAD`, `RPAD`
- `E_INDR` (`$expr` indirect reference) full round-trip
- `&STLIMIT`/`&STCOUNT` ✅ already landed J-216

**Gate:** rung8 (strings) all pass · global driver diff clean · ≥ 100p

---

### M-JVM-A03 — DATA + functions + RETURN/NRETURN

**Depends on:** M-JVM-A02
**Oracle:** `snobol4jvm/runtime.clj` + `operators.clj` INVOKE dispatch
**Scope:**
- `DATA` constructor calls → `sno_array_new` + field stores
- `DATA` field accessor calls → `sno_array_get(instance, fieldname)`
- `DATATYPE(N)` for DATA instances → check `__type__` key
- `DEFINE` / user-defined functions / `RETURN` / `FRETURN` / `NRETURN`
- Recursive functions: per-invocation stack frame (Near-Term Bridge model
  from `GENERAL-OVERVIEW.md` — same as x86 `emit_byrd_asm.c`)

**Gate:** rung10 (functions) · rung11 (DATA) all pass · ≥ 120p

---

## Phase 2 — Pattern Completion (Byrd Box Gaps)

The compiled Byrd box infrastructure already exists.
These milestones fill the remaining pattern primitive gaps.

### M-JVM-B01 — Remaining pattern primitives

**Depends on:** M-JVM-A03
**Oracle:** `emit_byrd_asm.c` pattern node cases (structural) + `match.clj` primitives (semantic)
**Scope:**
- `SPAN(cs)`, `BREAK(cs)`, `BREAKX(cs)` — cursor-advance loops
- `LEN(n)` — advance cursor by n chars
- `POS(n)`, `RPOS(n)` — absolute/relative position assert
- `TAB(n)`, `RTAB(n)` — advance-to-column
- `REM` — match everything to end
- `BAL` — balanced parentheses match
- `FENCE` — one-way door (blocks β backtrack)
- `FAIL`, `SUCCEED`, `ABORT` — control primitives
- `E_REF` (`*X`) — pattern-valued variable dereference

**Gate:** rung6 (all patterns) · rung7 (captures) all pass · ≥ 136p

---

### M-JVM-B02 — Full backtracking (β port)

**Depends on:** M-JVM-B01
**Rationale:** Current `emit_jvm_pat_node` ALT uses cursor-save/restore but
does not implement true β (resume) backtracking for nodes that can produce
multiple matches (SPAN, BREAK, BREAKX in backtrack context).
**Oracle:** `emit_byrd_asm.c` β label emission for SPAN/BREAK/ARBNO
**Scope:**
- β labels for SPAN, BREAK, BREAKX: on β, shrink match by 1 and re-offer
- β for ARBNO: already has greedy loop; add proper backtrack shrink path
- Verify: `SPAN('abc') . X` correctly captures shrinking spans on backtrack

**Gate:** rung6 backtrack-dependent tests pass · ≥ 140p

---

## Phase 3 — EVAL / CODE

### M-JVM-C01 — EVAL() / CODE()

**Depends on:** M-JVM-B02
**Oracle:** `snobol4jvm/compiler.clj` CODE function — parse→IR→inject into live table.
On JVM: re-enter `scrip-cc -jvm`, emit `.j` snippet, assemble via `jasmin.jar`
(already on path), load with a new `ClassLoader`, wire goto target.
**Scope:**
- `sno_eval(str)` — re-entrant parse + emit expression → class → invoke → String
- `sno_code(str)` — re-entrant parse + emit statement block → class → jump
- Wire into `jvm_emit_builtin()` dispatch for EVAL/CODE names

**Gate:** rung9 EVAL/CODE tests pass · ≥ 142p (x86 gate parity)

---

### M-JVM-PARITY — Full corpus parity

**Depends on:** M-JVM-C01
**Gate:** `snobol4_jvm` = 126/126 (all non-xfail tests) ✅

---

## Sprint Sequence

| Sprint | Milestone | Key work |
|--------|-----------|----------|
| J-220 | M-JVM-INTERP-A00 | `bb_*.jasmin` — 25 boxes + BbBox + BbExecutor · oracle: `bb_*.java` · assemble → `boxes.jar` |
| J-221 | M-JVM-INTERP-A01 | `Lexer.java` — tokenize SNOBOL4 source · oracle: `lex.c` |
| J-222 | M-JVM-INTERP-A02 | `Parser.java` — recursive descent → `StmtNode[]` · oracle: `parse.c` |
| J-223 | M-JVM-INTERP-A03 | `IrBuilder.java` — AST → IR nodes · PatternBuilder → Jasmin box classes |
| J-224 | M-JVM-INTERP-A04 | `Interpreter.java` 5-phase loop · `SnobolEnv` · corpus runner |
| J-225 | M-JVM-INTERP-A05 | Baseline verification vs `scrip-interp.c` · ≥94p broad |
| J-226 | M-JVM-A02 | 2D subscript fix · rung8 strings · global driver clean |
| J-227 | M-JVM-A03 pt1 | DATA constructor/field/DATATYPE · rung11 |
| J-228 | M-JVM-A03 pt2 | DEFINE/functions/RETURN/FRETURN/NRETURN · rung10 |
| J-229 | M-JVM-B01 | SPAN/BREAK/LEN/POS/TAB/REM/BAL/FENCE/FAIL/REF |
| J-230 | M-JVM-B02 | β backtrack for SPAN/BREAK/BREAKX/ARBNO |
| J-231 | M-JVM-C01 | EVAL()/CODE() re-entrant pipeline |
| J-232 | M-JVM-PARITY | Full corpus sweep + xfail audit |

---

## How snobol4jvm and emit_byrd_asm.c relate to emit_jvm.c

```
snobol4jvm/runtime.clj  ─── semantic oracle ──→  emit_jvm.c
  "what Phase N must produce"                     (Jasmin text)
                                                       ↑
emit_byrd_asm.c  ─────── structural oracle ──→  emit_jvm.c
  "how compiled Byrd boxes                    same labeled-goto
   look as labeled gotos"                      model, JVM opcodes
```

`snobol4jvm` proves the semantics are right.
`emit_byrd_asm.c` proves the compilation strategy is right.
`emit_jvm.c` applies both to produce Jasmin.

---

*MILESTONE-JVM-SNOBOL4.md — written J-217 pivot, 2026-04-02, Claude Sonnet 4.6.*
*Key insight: one4all JVM emits pure compiled Byrd boxes (labeled gotos), not*
*an interpreted frame walker. emit_byrd_asm.c is the structural oracle.*
*snobol4jvm is the semantic oracle only.*


---

<!-- SOURCE: MILESTONE-P2F-SEMI.md -->

# MILESTONE-P2F-SEMI — Semicolon Statement Separator

**Status:** ⬜ deferred  
**Blocks:** 1012_func_locals (1 test, currently FAIL in PASS=178 baseline)  
**Track:** SNOBOL4 × x86 / CMPILE parser

---

## The bug in one line

```snobol4
        a = 'aa' ; b = 'bb' ; d = 'dd'
```

Only `a = 'aa'` is compiled. `b = 'bb'` and `d = 'dd'` are dropped.

## Root cause (RT-139, 2026-04-06)

`FORWRD()` inside `CMPFRM` calls `forrun()` which reads the **next physical
card** into `g_io_linebuf`, clobbering the `; b='bb' ; d='dd'` remainder that
`TEXTSP.ptr` still points into.  The outer P2F loop in `cmpile_file_internal`
correctly checks `BRTYPE==EOSTYP && TEXTSP.len>0` after `compile_one_stmt()`
returns, but always sees `TEXTSP.len=0` because the buffer was overwritten.

## v311.sil mechanism (authoritative)

```
XLATNX  STREAM XSP,TEXTSP,CARDTB   ← re-classify remaining TEXTSP
        RCALL  ,NEWCRD              ← process card type
        RCALL  ,CMPILE,,(COMP3,,XLATNX)  ← compile; RTN3 → XLATNX again
```

After CMPILE parses `a='aa'` and FORBLK consumes `;`, TEXTSP = ` b='bb' ; d='dd'`.
RTN3 goes back to XLATNX → CARDTB sees leading space → NEWTYP → NEWCRD → CMPILE.
**No semicolon logic inside CMPILE itself.**

## Fix

In `cmpile_file_internal`, **snapshot TEXTSP before calling `compile_one_stmt()`**:

```c
/* XLATNX mirror: snapshot remainder so forrun() clobber can be detected */
const char *semi_saved_ptr = NULL;
int         semi_saved_len = 0;
```

Inside `compile_one_stmt()` (or via a wrapper), before `FORWRD()`/`EXPR()` inside
`CMPFRM`, save `TEXTSP` to a buffer that `forrun()` cannot touch (not `g_io_linebuf`).
After CMPILE returns, restore that snapshot as TEXTSP if `BRTYPE==EOSTYP`.

Alternatively: **find the exact `return s` path** inside CMPILE() that handles
`a='aa'` — add `SNO_SEMI=1` probes at every `return s` on a one-line test file:

```bash
printf "        a = 'aa' ; b = 'bb' ; d = 'dd'\nend\n" > /tmp/semi1.sno
SNO_SEMI=1 ./scrip --dump-parse /tmp/semi1.sno 2>&1
```

Fix that one path to not drain TEXTSP past `;`.

## Test monitor note

The CMPILE stream trace (`SNO_TRACE=1`) already runs against all 500+ corpus
sources via `one4all/csnobol4/dyn89_sweep.sh`.  Once the fix is in, strap
`--dump-parse` against the full corpus sweep to catch regressions:

```bash
# Gate: all 500+ files parse without error; stmt count matches reference
CORPUS=/home/claude/corpus bash one4all/csnobol4/dyn89_sweep.sh 2>/dev/null | grep FAIL
```

## Gate

```bash
cd /home/claude/one4all
./scrip --dump-parse corpus/crosscheck/rung10/1012_func_locals.sno | grep "stmt 1[012]"
# Must show: stmt 10 = a='aa', stmt 11 = b='bb', stmt 12 = d='dd'
./scrip --interp corpus/crosscheck/rung10/1012_func_locals.sno   # → PASS
CORPUS=/home/claude/corpus bash test/run_interp_broad.sh 2>/dev/null | grep "^PASS"
# PASS=179 (was 178)
```

## Regression note (RT-139b)

**`sno4parse.c` was renamed to `CMPILE.c`** — same file, same P2F loop (commit
`174d77eb`, sprint 93, 84/84 sweep confirmed).  A later commit broke `TEXTSP.len`.
**Fix: `git bisect run` against the 1012 test — one command.**

```bash
git bisect start HEAD 174d77eb
git bisect run bash -c 'make scrip -C /home/claude/one4all -s && \
  /home/claude/one4all/scrip --dump-parse \
  /home/claude/corpus/crosscheck/rung10/1012_func_locals.sno 2>/dev/null | \
  grep -q "stmt 11.*b.*bb" && echo good || echo bad'
```


---

<!-- SOURCE: MILESTONE-RT-RUNTIME.md -->

# MILESTONE-RT-RUNTIME.md — SIL-Faithful Runtime Subsystems

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Session:** SNOBOL4 × x86, sprint 95+
**Status:** ACTIVE — RUNTIME-1 through RUNTIME-9 queued

---

## Governing Principle

Everything outside lex, parse, and pattern match (Byrd boxes) must
be **named and behave identically to the SIL** (`v311.sil`, CSNOBOL4 3.3.3).
The SIL procedure names become C function names. The SIL logic
becomes the C logic. No invention — faithful translation.

Covered by this milestone chain:
- `ARGVAL`, `VARVAL`, `INTVAL`, `PATVAL`, `EXPVAL` — typed argument eval
- `INVOKE` — universal function dispatch
- `NAME` / `ASGN` — NAME type and assignment with all hooks
- `NMD` / naming list — conditional assignment stack
- `EXPVAL` / `EXPEVL` — EXPRESSION type execution (save/restore system state)
- `CONVE` / `CODER` / `CNVRT` — compile-to-EXPRESSION, CODE(), CONVERT()
- `EVAL` builtin — string → expression evaluation
- `INTERP` / `INIT` / `GOTO` / `GOTL` / `GOTG` — SM_Program dispatch loop

## Invariant — Green Throughout

**Baseline (sprint 95, one4all `5c1a1d8`):**
```
PASS=177  FAIL=1  (178 total)   [expr_eval — needs EVAL+NRETURN]
```

Every RT commit must hold PASS ≥ 177. The floor never drops.
Run after every change:
```bash
cd /home/claude/one4all && bash test/run_interp_broad.sh
```

---

## Strategy — Additive Shim Replacement

`scrip-interp.c` stays buildable and passing after every commit.
Each milestone replaces exactly one internal dispatch point with
the SIL-faithful version. No big-bang rewrites.

| What gets replaced | Where in code | RT milestone |
|--------------------|--------------|-------------|
| `call_user_function()` if/else dispatch | scrip-interp.c | RUNTIME-1 |
| Type coercions inside `interp_eval()` | scrip-interp.c | RUNTIME-2 |
| `interp_eval_ref()` + K-type in NV_SET | scrip-interp.c + snobol4.c | RUNTIME-3 |
| `capture_t` array in stmt_exec.c | stmt_exec.c | RUNTIME-4 |
| `NV_SET_fn` — add output/trace hooks | snobol4.c | RUNTIME-5 |
| `eval_expr()` stub in eval_code.c | eval_code.c | RUNTIME-6 |
| `CODE()` / `CONVERT()` builtins | snobol4.c | RUNTIME-7 |
| `EVAL_fn` stub | snobol4.c | RUNTIME-8 |
| tree-walk `execute_program()` | scrip-interp.c → sm_interp.c | RUNTIME-9 |

---

## RUNTIME-1 — INVOKE Dispatch Table

**SIL procs:** `INVOKE`, `INVK1`, `INVK2`, `ARGVAL`
**File:** `src/runtime/snobol4/invoke.c` (new) + hook into `snobol4.c`
**Gate:** PASS ≥ 177, all existing tests unaffected

### What SIL does

```
INVOKE: pop function index (INCL)
        get procedure descriptor XPTR from INCL[0]
        if arg count matches FNC flag → BRANIC (branch indirect)
        else if FNC flag set → variable-arg: branch anyway
```

`ARGVAL`: fetch next descriptor from object code array (OCBSCL+OCICL),
check FNC bit → if set call INVOKE, else get value from name slot,
handle &INPUT association.

### What we have

`call_user_function()` in scrip-interp.c: a linear if/else over
hardcoded builtin names, then a search through a user-function list.
No FNC-bit model. No descriptor-keyed dispatch table.

### What to build

```c
/* invoke.c */

/* Function descriptor — mirrors SIL FBLKSZ block */
typedef struct {
    const char *name;
    int         nargs;       /* -1 = variable */
    DESCR_t   (*fn)(DESCR_t *args, int nargs);
} FuncDesc_t;

/* Global function table (builtins + user-defined) */
DESCR_t INVOKE_fn(const char *name, DESCR_t *args, int nargs);

/* ARGVAL: evaluate next argument off IR (tree-walk phase) */
DESCR_t ARGVAL_fn(EXPR_t *arg);
```

Replace the body of `call_user_function()` with a call to `INVOKE_fn`.
All builtin registrations move into `invoke.c`'s init table.
User `DEFINE` registers into the same table.

### Corpus gate

expr_eval needs NRETURN+EVAL (RUNTIME-6/RUNTIME-8), not RUNTIME-1.
Gate: no regressions. PASS stays 177.

---

## RUNTIME-2 — VARVAL / INTVAL / PATVAL Typed Argument Evaluators

**SIL procs:** `VARVAL`, `INTVAL`, `PATVAL`, `VARVUP`, `XYARGS`
**File:** `src/runtime/snobol4/argval.c` (new)
**Gate:** PASS ≥ 177

### What SIL does

Each evaluator: fetch descriptor → check FNC (call INVOKE if so) →
check &INPUT association → get value from name slot → coerce to
required type (STRING / INTEGER / PATTERN).

```
VARVAL: → STRING (coerce INTEGER via GENVIX, reject others)
INTVAL: → INTEGER (coerce STRING via SPCINT, coerce REAL via RLINT)
PATVAL: → PATTERN (coerce STRING→bb_lit, EXPRESSION→EXPVAL, REAL→STRING→bb_lit)
VARVUP: → uppercase STRING (VARVAL + case-fold if &CASE set)
```

### What we have

Ad-hoc coercions scattered through `interp_eval()` cases. No unified
typed-evaluator pattern. `_expr_is_pat()` heuristic instead of type-dispatch.

### What to build

```c
/* argval.c */
DESCR_t VARVAL_fn(DESCR_t d);   /* → STRING or FAIL */
DESCR_t INTVAL_fn(DESCR_t d);   /* → INTEGER or FAIL */
DESCR_t PATVAL_fn(DESCR_t d);   /* → PATTERN (DT_P) or FAIL */
DESCR_t VARVUP_fn(DESCR_t d);   /* → uppercase STRING or FAIL */
```

Thread these through `interp_eval()` at the points where type coercion
currently happens ad-hoc. The tree-walker stays; coercion logic moves
into named functions matching SIL names.

---

## RUNTIME-3 — NAME Type + Keyword Names (K)

**SIL procs:** `NAME` (`.X`), `ASGNV`, `ASGNIC`, type K dispatch
**Files:** `src/runtime/snobol4/snobol4.c`, `scrip-interp.c`
**Gate:** PASS ≥ 177, NAME tests added to corpus

### What SIL does

`.X` → `NAME` proc: fetch descriptor, test FNC bit, call INVOKE
if so, return N-typed descriptor pointing at variable's storage slot.

Type K (keyword): `ASGNIC` routes keyword assignment through `INTVAL`
(keyword values are always INTEGER). `NV_GET`/`NV_SET` for K-type
variables reads/writes the keyword global directly (e.g. `&TRIM`,
`&ANCHOR`, `&STLIMIT`).

### What we have

`interp_eval_ref()` returns a raw `DESCR_t*` C pointer. Works for
simple E_VAR cases. Completely ignores K (keyword) type. No DT_N
descriptor returned — just a pointer that leaks through the abstraction.

`NAMEPTR(dp_)` macro exists in snobol4.h but is not used by the
name-return path.

### What to build

```c
/* In snobol4.c */

/* NAME_fn: .X — return DT_N descriptor for variable name */
/* Mirrors SIL NAME proc */
DESCR_t NAME_fn(const char *varname);

/* ASGNIC_fn: keyword assignment — route through INTVAL */
int ASGNIC_fn(const char *kw_name, DESCR_t val);

/* Extend NV_GET_fn / NV_SET_fn to handle DT_K slot dispatch */
/* K-type names map to keyword globals: &TRIM, &ANCHOR, etc. */
```

Replace `interp_eval_ref()` with calls to `NAME_fn` where `.X` is
needed. Replace raw pointer returns with `DT_N` descriptors.
`ASGN` (RUNTIME-5) then dereferences DT_N via `NAMEPTR`.

---

## RUNTIME-4 — Conditional Assignment Stack (NMD / Naming List)

**SIL procs:** `NMD`, `NMD1`–`NMD5`, `NMDIC`, `NAMEXN`
**SIL globals:** `NAMICL`, `NHEDCL`, `PDLPTR`, `PDLHED`, `NBSPTR`
**File:** `src/runtime/dyn/stmt_exec.c`, new `src/runtime/snobol4/nmd.c`
**Gate:** PASS ≥ 177, `.VAR` capture tests pass

### What SIL does

The naming list is a LIFO buffer (`NBSPTR` + `NAMICL` offset).
Each `.VAR` conditional assignment during a pattern match pushes
`(specifier, variable_descriptor)` pairs onto this list.

On **pattern success**: `NMD` walks the list from `NHEDCL` to `NAMICL`,
assigns each captured substring to its variable. Handles:
- Normal variable (DT_S target): `GENVAR` + `PUTDC`
- Keyword variable (DT_K target): `NMDIC` → `SPCINT` (integer coerce)
- EXPRESSION variable (DT_E target): `NAMEXN` → `EXPEVL`

On **pattern failure**: the naming list is discarded by restoring
`NAMICL` to `NHEDCL` (nothing was committed).

`PDLPTR` / `PDLHED` is the **pattern history list** — backtrack state
for `ARBNO`, `BAL`, etc. Separate from the naming list.

### What we have

`capture_t` array in `stmt_exec.c` collects `(varname, substring)`
pairs. On success, iterates and calls `NV_SET_fn`. This is the right
shape but:
- No LIFO framing per-statement (no NHEDCL save/restore)
- No keyword coercion path (NMDIC)
- No EXPRESSION variable path (NAMEXN)
- Not re-entrant (EXPVAL inside NMD can recurse)

### What to build

```c
/* nmd.c — naming list (SIL §NMD) */

/* Thread-local (or global) naming list state */
typedef struct {
    const char *varname;   /* target variable */
    int         dt;        /* DT_S / DT_K / DT_E */
    const char *substr;    /* matched substring */
    int         slen;
} NamEntry_t;

#define NAM_MAX 256
static NamEntry_t nam_buf[NAM_MAX];
static int        nam_head = 0;   /* NHEDCL */
static int        nam_top  = 0;   /* NAMICL */

void  NAM_push(const char *var, int dt, const char *s, int len); /* .VAR hit */
int   NAM_save(void);                    /* save NHEDCL → returns cookie */
void  NAM_commit(int cookie);            /* NMD: assign all since cookie */
void  NAM_discard(int cookie);           /* on failure: restore to cookie */
```

Wire `NAM_push` into the bb_capture box (replaces current `capture_t`).
Wire `NAM_commit` / `NAM_discard` into `stmt_exec_dyn` at the S/F branch.

---

## RUNTIME-5 — ASGN with &OUTPUT Association + TRACE + Keyword Assignment

**SIL procs:** `ASGN`, `ASGNV`, `ASGNVV`, `ASGNVP`, `ASGNC`, `ASGNIC`
**File:** `src/runtime/snobol4/snobol4.c` — extend `NV_SET_fn`
**Gate:** PASS ≥ 177, OUTPUT-association test added

### What SIL does

```
ASGN:
  1. fetch subject descriptor (may be FNC → INVOKE)
  2. check K type → route to ASGNIC (keyword assignment via INTVAL)
  3. fetch value descriptor (may be FNC → INVOKE)
  4. check &INPUT association on value variable
  5. PUTDC: write value into subject's DESCR slot
  6. check &OUTPUT → if association exists, call PUTOUT
  7. check &TRACE → if VALUE trace on subject, call TRPHND
  8. return value (for embedded assignment X = (A = B) )
```

### What we have

`NV_SET_fn(name, val)`: plain hash-table store. No output association,
no trace, no keyword routing, no embedded-assignment return value.

### What to build

Extend `NV_SET_fn` signature to return `DESCR_t` (the assigned value,
for embedded assignment). Add hook points:

```c
/* snobol4.c — extend NV_SET_fn */
DESCR_t NV_SET_fn(const char *name, DESCR_t val);
/*  → checks OUTPUT assoc table (outatl)
    → checks TRACE value table (tvall)  [&TRACE]
    → keyword names routed to kw_set()
    → returns val (for embedded assignment)
*/
```

Output association table (`outatl`) and trace association table (`tvall`)
are initially empty. The hooks are wired but inert until
`OUTPUT` and `TRACE` builtins populate them (later milestone).

---

## RUNTIME-6 — EXPVAL / EXPEVL — EXPRESSION Type Execution

**SIL procs:** `EXPVAL`, `EXPEVL`, `EXPVC`, `EXPV1`–`EXPV11`
**File:** `src/runtime/dyn/eval_code.c` — replace stub `eval_expr()`
**Gate:** PASS ≥ 177, EXPRESSION type tests added

### What SIL does

`EXPVAL` saves the **entire system state** before evaluating an
EXPRESSION-typed value:
```
Push: OCBSCL, OCICL, PATBCL, PATICL, WPTR, XCL, YCL, TCL
      MAXLEN, LENFCL, PDLPTR, PDLHED, NAMICL, NHEDCL
      specifiers: HEADSP, TSP, TXSP, XSP
```
Sets new `OCBSCL` = the EXPRESSION's code block.
Calls `INVOKE` to execute each instruction.
On exit (success or failure): restores all saved state.

`EXPEVL` is the entry for evaluating an EXPRESSION and returning
**by name** (the variable reference, not the value). Used by `NMD`
when target is DT_E (NAMEXN path).

`EXPVC`: when the code block's first descriptor has FNC bit set,
call INVOKE (function call within expression evaluation).

### What we have

`eval_expr(const char *src)` in eval_code.c: re-parses a string,
tree-walks the result. No save/restore of system state. No DT_E
descriptor execution. Returns a value but not re-entrant.

### What to build

```c
/* eval_code.c — replace eval_expr() */

/* System state snapshot for EXPVAL save/restore */
typedef struct {
    /* interpreter registers */
    int   ocbscl_base;   /* OCBSCL */
    int   ocicl_off;     /* OCICL */
    int   nam_head;      /* NHEDCL */
    int   nam_top;       /* NAMICL */
    int   pdl_head;      /* PDLHED */
    int   pdl_ptr;       /* PDLPTR */
    /* ... other saved state ... */
} SysState_t;

/* EXPVAL: execute a DT_E EXPRESSION, return value or FAIL */
DESCR_t EXPVAL_fn(DESCR_t expr_d);

/* EXPEVL: execute DT_E EXPRESSION, return by name */
DESCR_t EXPEVL_fn(DESCR_t expr_d);
```

The key correctness property: EXPVAL must be **fully re-entrant** —
an EXPRESSION can contain a call to EVAL() which calls EXPVAL again.
The save/restore stack must handle arbitrary nesting.

---

## RUNTIME-7 — CONVE / CODER / CNVRT — Compile to EXPRESSION and CODE

**SIL procs:** `CONVE`, `CONVEX`, `CODER`, `CNVRT` (= `CONVERT()`),
              `RECOM*` (recompile loop), `CONVR`, `CONVRI`, `CNVIV`,
              `CNVVI`, `CNVTA`, `ICNVTA`
**File:** `src/runtime/snobol4/snobol4.c` — `CODE_fn`, `CONVERT_fn`
**Gate:** PASS ≥ 177, CODE() + CONVERT() corpus tests pass

### What SIL does

`CODER` (= `CODE(S)`):
1. Evaluate arg as string via `VARVAL`
2. Set up compiler with string as input (`TEXTSP`)
3. Compile statements via `CMPILE` loop until string exhausted
4. Set type to C (CODE) on resulting block
5. Return CODE descriptor

`CONVE` (convert to EXPRESSION):
1. Same as CODE but compile a single expression via `EXPR`
2. Set type to E (EXPRESSION) on result
3. Return EXPRESSION descriptor

`CNVRT` (= `CONVERT(X, T)`):
Full type-conversion matrix:
```
S→I, S→R, I→S, I→R, R→S, R→I   (numeric conversions)
S→E  (string → expression via CONVE)
T→A  (table → array via CNVTA)
any→S  (via DTREP — data type representation string)
```

### What we have

`CODE()` stub returns NULVCL.
`CONVERT()` does only numeric conversions.
No `CONVE` — no compile-string-to-EXPRESSION path.
No table→array conversion.

### What to build

```c
/* snobol4.c */
DESCR_t CODE_fn(DESCR_t *args, int nargs);     /* CODE(S) → DT_C */
DESCR_t CONVE_fn(DESCR_t str_d);               /* string → DT_E */
DESCR_t CONVERT_fn(DESCR_t *args, int nargs);  /* CONVERT(X,T) full matrix */
```

`CODE_fn` and `CONVE_fn` call `sno_parse()` (existing) on the string,
wrap the resulting `Program*` in the appropriate DT_C / DT_E descriptor.

---

## RUNTIME-8 — EVAL() Builtin

**SIL proc:** `EVAL`, `EVAL1`
**File:** `src/runtime/snobol4/snobol4.c` — replace `EVAL_fn` stub
**Gate:** PASS = 178 (expr_eval finally passes), EVAL corpus tests pass

### What SIL does

```
EVAL(X):
  ARGVAL → get X
  if X is DT_E (EXPRESSION) → go directly to EXPVAL (EVAL1)
  if X is DT_I → return X (idempotent)
  if X is DT_R → return X (idempotent)
  if X is DT_S:
    if empty string → return X (idempotent)
    try SPCINT → return integer if succeeds
    try SPREAL → return real if succeeds
    CONVE: compile string to EXPRESSION
    → EXPVAL: execute it
```

### What we have

`EVAL_fn`: stub that calls `eval_expr(src)` — re-parses string,
tree-walks result. Misses idempotent cases, misses DT_E path,
misses numeric-string shortcuts.

### What to build

```c
/* snobol4.c — replace EVAL_fn body */
DESCR_t EVAL_fn(DESCR_t *args, int nargs) {
    DESCR_t x = ARGVAL_fn(args[0]);
    if (x.v == DT_E) return EXPVAL_fn(x);       /* EVAL1 */
    if (x.v == DT_I || x.v == DT_R) return x;   /* idempotent */
    if (x.v == DT_S) {
        if (IS_NULL_fn(x)) return x;             /* empty → idempotent */
        DESCR_t n = try_int(x);   if (n.v == DT_I) return n;
        DESCR_t r = try_real(x);  if (r.v == DT_R) return r;
        DESCR_t e = CONVE_fn(x);                 /* compile → DT_E */
        if (e.v == DT_FAIL) return FAILDESCR;
        return EXPVAL_fn(e);                     /* execute */
    }
    return FAILDESCR;
}
```

This is the milestone that makes `expr_eval` pass (PASS → 178).

---

## RUNTIME-9 — INTERP / INIT / GOTO / GOTL / GOTG — SM_Program Dispatch Loop

**SIL procs:** `INTERP`, `INTRP0`, `INIT`, `GOTO`, `GOTL`, `GOTG`, `BASE`
**File:** `src/driver/sm_interp.c` (new — does NOT modify scrip-interp.c)
**Gate:** SM_Program test suite passes; scrip-interp.c tree-walker untouched

### What SIL does

```
INTERP (core loop):
  INTRP0: OCICL += DESCR                 ; advance to next instruction
           XPTR = code[OCICL]            ; fetch descriptor
           if FNC bit set → INVOKE       ; dispatch function
           on INVOKE failure: OCICL = FRTNCL (failure offset)
                              FALCL++  (&STFCOUNT)
                              check &TRACE → TRPHND

INIT (statement header):
  update &LASTNO, &LASTFILE, &LASTLINE
  OCICL += DESCR × 3 (skip stmtno, lineno, filename)
  update &STNO, &LINE, &FILE, &STCOUNT
  check &STLIMIT → EXEX if exceeded
  check &TRACE → STNO/STCOUNT trace handlers

GOTO: fetch offset from code, set OCICL
GOTL: fetch label string, look up in label table,
      handle RETURN/FRETURN/NRETURN/ABORT/CONTINUE/SCONTINUE
GOTG: :<VAR> — get CODE descriptor, set OCBSCL+OCICL=0
```

### What we have

`execute_program()` in scrip-interp.c: tree-walks `STMT_t` linked list.
No `&STNO`/`&LINE` update. No `&STLIMIT` check. No `NRETURN` from
nested function calls (partial — known bug). No `ABORT`/`CONTINUE`
goto targets.

### What to build

`sm_interp.c`: a fresh file implementing the SM_Program dispatch loop
over `SM_Instr[]` (from SCRIP-SM.md). This is the component that
connects the RUNTIME-1 through RUNTIME-8 subsystems to the SM_Program instruction
set and retires the tree-walker permanently.

`scrip-interp.c` continues running on the tree-walker during this milestone.
`sm_interp.c` runs in parallel against the same corpus.
When `sm_interp` PASS ≥ scrip-interp PASS, the tree-walker is retired.

**This milestone is the architecture reset target from PLAN.md** —
SM_Program execution replaces tree-walking IR.

---

## Milestone Summary Table

| Milestone | SIL procs | File(s) | Gate |
|-----------|-----------|---------|------|
| ~~**RUNTIME-1**~~ ✅ | `INVOKE`, `INVK1/2`, `ARGVAL` | `snobol4_invoke.c` | done |
| ~~**RUNTIME-2**~~ ✅ | `VARVAL`, `INTVAL`, `PATVAL`, `VARVUP` | `snobol4_invoke.c` | done |
| ~~**RUNTIME-3**~~ ✅ | `NAME`, `ASGNIC`, type K dispatch | `snobol4_invoke.c` + `sil_macros.h` | done |
| ~~**RUNTIME-4**~~ ✅ | `NMD`, `NMD1-5`, `NMDIC`, `NAMEXN` | `snobol4_nmd.c` | done |
| **RUNTIME-5** ⚠️ **CURRENT** | `ASGN`, `ASGNV`, `ASGNVV`, `ASGNVP` | `snobol4_invoke.c` — `NV_SET_fn` → `DESCR_t` + OUTPUT/TRACE hooks | PASS ≥ 163 |
| **RUNTIME-6** ⚠️ **CURRENT** | `EXPVAL`, `EXPEVL`, `EXPVC` | `eval_code.c` — implement `EXPVAL_fn`/`EXPEVL_fn` (declared, not implemented) | PASS ≥ 163 |
| **RUNTIME-7** ⚠️ **CURRENT** | `CONVE`, `CODER`, `CNVRT` | `snobol4_invoke.c` — `CONVE_fn` + `CODE_fn` + full `CONVERT_fn` matrix | PASS ≥ 163 |
| **RUNTIME-8** ⚠️ **CURRENT** | `EVAL`, `EVAL1` | `snobol4_invoke.c` — replace stub: full DT_E/DT_S/DT_I/DT_R dispatch | **PASS = 178** |
| **RUNTIME-9** | `INTERP`, `INIT`, `GOTO`, `GOTL`, `GOTG` | `sm_interp.c` (exists, extend) — depends RT-5–8 | PASS ≥ 178 via SM |

Dependencies: RT-5 → RT-6 → RT-7 → RT-8 in order. RT-9 depends on all prior.

---

## SIL Reference Quick Index

All procedures in `/home/claude/snobol4-2.3.3/v311.sil`:

| Proc | Line | Description |
|------|------|-------------|
| `INVOKE` | 2669 | Universal function dispatcher |
| `ARGVAL` | 2683 | Evaluate one argument (untyped) |
| `EXPVAL` | 2702 | Execute EXPRESSION, save/restore state |
| `EXPEVL` | 2750 | Execute EXPRESSION, return by name |
| `EVAL` | 2754 | EVAL() builtin |
| `INTVAL` | 2769 | Evaluate argument as INTEGER |
| `PATVAL` | 2800 | Evaluate argument as PATTERN |
| `VARVAL` | 2836 | Evaluate argument as STRING |
| `VARVUP` | 2867 | Evaluate argument as uppercase STRING |
| `XYARGS` | 2890 | Evaluate argument pair |
| `INTERP` | 2651 | Core interpreter loop |
| `INIT` | 2608 | Statement initialization |
| `GOTO` | 2641 | Interpreter goto |
| `GOTL` | 2575 | Label goto (RETURN/FRETURN/etc.) |
| `GOTG` | 2559 | Direct goto :<VAR> |
| `BASE` | 2544 | Code basing |
| `NAME` | 6043 | .X — return NAME descriptor |
| `NMD` | 6055 | Commit conditional assignments |
| `ASGN` | 5832 | X = Y with all hooks |
| `CONVE` | 6534 | String → EXPRESSION |
| `CODER` | 6530 | String → CODE |
| `CNVRT` | 6457 | CONVERT(X,T) |

---

*MILESTONE-RT-RUNTIME.md — created sprint 95, 2026-04-04*
*Baseline: PASS=177 FAIL=1. Target: PASS=178 at RUNTIME-8, then SM_Program at RUNTIME-9.*


---

<!-- SOURCE: MILESTONE-RT-SIL-MACROS.md -->

# MILESTONE-RT-SIL-MACROS.md — SIL Macro Classification for SM + scrip-interp

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-05 (revised — dual-axis classification)
**Status:** DESIGN — feeds RT milestones and SM_Program instruction set
**Source:** `v311.sil` (CSNOBOL4 2.3.3, Phil Budne) + `include/macros.h` (C translations)

---

## The Question (Sharpened)

SIL defines ~130 macro instructions and ~211 named procedures.
For each, we need to know **both**:

1. **scrip-interp axis** — does it become a C function / C macro in the RT layer?
   Used by: `snobol4.c`, `argval.c`, `invoke.c`, `nmd.c`, `eval_code.c`, `stmt_exec.c`
2. **SM_Program axis** — does it become a named SM_Program instruction?
   Used by: `sm_interp.c` dispatch loop (RUNTIME-9) + all emitters (x86, JVM, .NET, JS)

These are **independent axes**. A macro can be:
- RT only (too low-level for the SM — e.g. field access macros)
- SM only (pure control flow with no C-level helper needed)
- BOTH (the SM instruction dispatches to a C RT function — most common)
- SKIP (GC/compiler/IO internal — irrelevant to our runtime)

---

## Classification Tags

| Tag | Meaning |
|-----|---------|
| **RT** | C macro/inline/function in `sil_macros.h` or RT source file |
| **SM** | SM_Program instruction in `SM_Op` enum + dispatch case in `sm_interp.c` |
| **BOTH** | SM instruction whose dispatch calls a C RT function by the same name |
| **SKIP** | GC/compiler/IO internal — not useful |
| **DONE** | Already implemented |

---

## Group 1 — Descriptor Access (GETD / PUTD family)

**Axis: RT only.** These are C field accesses on `DESCR_t`.
Too low-level to be SM instructions — the SM operates on typed values,
not raw memory offsets. Every RT function uses these.
C translations are in `include/macros.h` (`D()`, `D_A()`, `D_V()`, `D_F()`).

| SIL Macro | SIL Semantics | C Translation | scrip-interp | SM_Program |
|-----------|---------------|---------------|:---:|:---:|
| `GETD d,base,off` | d = *(base+off) | `d = *(DESCR_t*)((char*)base+off)` | RT macro | — |
| `PUTD base,off,d` | *(base+off) = d | `*(DESCR_t*)((char*)base+off) = d` | RT macro | — |
| `GETDC d,base,off` | d = base->field[off] | struct field access | RT macro | — |
| `PUTDC base,off,d` | base->field[off] = d | struct field assign | RT macro | — |
| `GETAC d,base,off` | d = (ptr)base[off] | pointer load | RT macro | — |
| `PUTAC base,off,d` | base[off] = (ptr)d | pointer store | RT macro | — |
| `SETAC base,val` | base.a = constant | `d.ptr = (void*)val` | RT macro | — |
| `SETAV d,src` | d.a = src.v | `d.ptr = (void*)(intptr_t)src.v` | RT macro | — |
| `MOVD dst,src` | dst = src (full descr) | `dst = src` | RT macro | — |
| `MOVDIC d,doff,s,soff` | d[doff] = s[soff] | indirect struct copy | RT macro | — |
| `MOVV dst,src` | dst.v = src.v | `dst.v = src.v` | RT macro | — |
| `MOVA dst,src` | dst.a = src.a | `dst.ptr = src.ptr` | RT macro | — |
| `MOVBLK dst,src,sz` | memcpy block | `memmove(dst+DESCR, src+DESCR, sz)` | RT macro | — |

**sil_macros.h action:** `#define GETDC(d,base,off)`, `#define PUTDC(base,off,d)`, etc.
Mirror `macros.h` D_A/D_V/D_F field accessors with our `DESCR_t` layout.

---

## Group 2 — Type Test and Comparison

**Axis: RT (all); SM (ACOMP, RCOMP, LCOMP only).**
Type tests are C conditionals in RT functions. Only the three
compare ops that replace common `SM_CALL` paths earn SM status.

| SIL Macro | SIL Semantics | scrip-interp | SM_Program |
|-----------|---------------|:---:|:---:|
| `TESTF d,type,eq,ne` | if (d.f & type) goto eq else ne | **RT** `IS_FNC(d)` | — |
| `TESTFI d,type,off,eq,ne` | indirect type test | **RT** | — |
| `VEQLC d,T,t,f` | if (d.v == T) goto t else f | **RT** `IS_TYPE(d,T)` | — |
| `VEQL d1,d2,t,f` | if (d1.v == d2.v) | **RT** `SAME_TYPE(a,b)` | — |
| `DEQL d1,d2,t,f` | if (d1==d2) full descr equal | **RT** `DEQL(a,b)` | — |
| `AEQLC d,val,t,f` | if (d.a == constant) | **RT** `AEQLC(d,v)` | — |
| `AEQL d1,d2,t,f` | if (d1.a == d2.a) | **RT** `AEQL(a,b)` | — |
| `ACOMP d1,d2,lt,eq,gt` | compare integers/addresses | **RT** `ACOMP(a,b)` | **SM** `SM_ACOMP` |
| `ACOMPC d,val,lt,eq,gt` | compare address vs constant | **RT** `ACOMPC(d,v)` | — |
| `RCOMP d1,d2,lt,eq,gt` | compare reals | **RT** `RCOMP(a,b)` | **SM** `SM_RCOMP` |
| `LEQLC sp,n,t,f` | if (sp.len == n) | **RT** `SP_LEN_EQ(sp,n)` | — |
| `LCMP sp1,sp2,lt,eq,gt` | compare string lengths | **RT** `LCMP(a,b)` | — |
| `LCOMP sp1,sp2,lt,eq,gt` | lexicographic compare | **RT** `LCOMP_fn(a,b)` → `lexcmp()` | **SM** `SM_LCOMP` |
| `VCMPIC d,T,off,t,f` | type compare indirect | **RT** | — |
| `VCOMPC d,T,t,f` | value compare constant | **RT** | — |
| `PCOMP d,val,lt,eq,gt` | compare as pointer (unsigned) | **RT** `PCOMP(a,b)` | — |

**SM rationale:** `SM_ACOMP` replaces `SM_CALL "EQ"/"GT"/"LT"` for integer predicates.
`SM_RCOMP` replaces `SM_CALL "GE"/"LE"` for real predicates.
`SM_LCOMP` replaces `SM_CALL "LGT"/"LLT"/"LGE"/"LLE"` for string predicates.
All three are hot paths; making them native SM ops eliminates INVOKE overhead.

**sil_macros.h action:** `IS_INT`, `IS_REAL`, `IS_STR`, `IS_PAT`, `IS_NAME`, `IS_KW`,
`IS_EXPR`, `IS_CODE`, `IS_FNC`, `TESTF`, `VEQLC`, `DEQL`, `AEQLC`.

---

## Group 3 — Arithmetic on Addresses/Integers

**Axis: RT (all inline ops); SM (INCR, DECR only as dedicated ops; ADD/SUB/MUL/DIV already DONE).**

| SIL Macro | SIL Semantics | scrip-interp | SM_Program |
|-----------|---------------|:---:|:---:|
| `INCRA d,n` | d.a += n | **RT** `INCRA(d,n)` → `d += n` | **SM** `SM_INCR n` |
| `DECRA d,n` | d.a -= n | **RT** `DECRA(d,n)` → `d -= n` | **SM** `SM_DECR n` |
| `SUM d,a,b` | d = a + b (integer) | **RT** | SM `SM_ADD` (**DONE**) |
| `MULT d,a,b` | d = a * b | **RT** | SM `SM_MUL` (**DONE**) |
| `MULTC d,a,c` | d = a * constant | **RT** | — |
| `DIVIDE d,a,b` | d = a / b | **RT** | SM `SM_DIV` (**DONE**) |
| `SUBTRT d,a,b` | d = a - b | **RT** | SM `SM_SUB` (**DONE**) |
| `ADDLG d,sp` | d += sp.len | **RT** `ADDLG(d,sp)` | — |
| `ADREAL d,x,y` | d = x + y (real) | **RT** | — (covered by SM_ADD with type dispatch) |
| `MPREAL d,x,y` | d = x * y (real) | **RT** | — |
| `DVREAL d,x,y` | d = x / y (real) | **RT** | — |
| `SBREAL d,x,y` | d = x - y (real) | **RT** | — |
| `MNSINT d,x` | d = -x (integer, overflow check) | **RT** `NEG_I_fn(d)` | — (SM_NEG handles) |
| `MNREAL d,x` | d = -x (real) | **RT** `NEG_R_fn(d)` | — |
| `INTRL d,x` | d = (real)x int→real | **RT** `INT_TO_REAL_fn(d)` | — |
| `RLINT d,x,f,ok` | d = (int)x real→int, fail→f | **RT** `REAL_TO_INT_fn(d)` | — |
| `EXREAL d,x,y,err` | d = x**y (reals) | **RT** `EXP_R_fn(d,e)` | — (SM_EXP handles) |

**SM rationale:** `SM_INCR`/`SM_DECR` model SIL's ubiquitous `INCRA OCICL,DESCR` / `DECRA XCL,2*DESCR` — advancing/retreating the instruction pointer and loop counters. These appear literally hundreds of times in v311.sil. As SM ops they let `sm_interp.c` advance its own PC without a full INVOKE.

---

## Group 4 — String / Specifier Operations

**Axis: RT (all C function calls); SM (TRIM, SPCINT, SPREAL only).**
The specifier ops (LOCSP, GETLG, etc.) are C inline helpers.
Only the three that appear in hot SM-level paths earn SM status.

| SIL Macro | SIL Semantics | C Translation | scrip-interp | SM_Program |
|-----------|---------------|---------------|:---:|:---:|
| `LOCSP sp,d` | sp = specifier from descriptor | `X_LOCSP(sp,d)` in macros.h | **RT** | — |
| `GETSPC d,base,off` | sp = *(base+off) | struct access | **RT** | — |
| `PUTSPC base,off,sp` | *(base+off) = sp | struct assign | **RT** | — |
| `GETLG d,sp` | d = sp.len | `S_L(sp)` | **RT** | — |
| `PUTLG sp,d` | sp.len = d | `S_L(sp) = d` | **RT** | — |
| `GETSIZ d,base` | d = block.title.v | `D_V(base)` | **RT** | — |
| `SETSIZ base,d` | block.title.v = d | `D_V(base) = d` | **RT** | — |
| `SETLC sp,n` | sp.len = constant | `S_L(sp) = n` | **RT** | — |
| `SETSP sp1,sp2` | sp1 = sp2 (copy) | `_SPEC(sp1) = _SPEC(sp2)` | **RT** | — |
| `SHORTN sp,n` | sp.len -= n | `S_L(sp) -= n` | **RT** | — |
| `FSHRTN sp,n` | sp.off += n; sp.len -= n | `S_O(sp)+=n; S_L(sp)-=n` | **RT** | — |
| `TRIMSP sp1,sp2` | trim trailing blanks | `trimsp(sp1,sp2)` in macros.h | **RT** `TRIM_fn` | **SM** `SM_TRIM` |
| `REMSP sp1,sp2` | sp1 = sp2 minus leading sp | `X_REMSP(sp1,sp2,sp)` | **RT** | — |
| `SUBSP sp,d,n` | substring | `substr(sp,sp2,descr)` | **RT** `SUBSTR_fn` | — |
| `APDSP sp1,sp2` | append sp2 to sp1 | `APDSP(sp1,sp2)` in macros.h | **RT** | — |
| `LEXCMP sp1,sp2` | lexicographic compare → int | `lexcmp(sp1,sp2)` | **RT** → `SM_LCOMP` | via SM_LCOMP |
| `SPCINT d,sp,f,ok` | parse integer from string | `spcint(d,sp)` | **RT** `SPCINT_fn` | **SM** `SM_SPCINT` |
| `SPREAL d,sp,f,ok` | parse real from string | `spreal(d,sp)` | **RT** `SPREAL_fn` | **SM** `SM_SPREAL` |
| `REALST sp,d` | format real → string | `realst(sp,d)` | **RT** `REALST_fn` | — |
| `INTSP sp,d` | format integer → string | `intspc(sp,d)` | **RT** `INTSP_fn` | — |
| `LVALUE sp,d` | get l-value specifier | `lvalue(sp,d)` | **RT** | — |
| `LEQLC sp,n,t,f` | sp.len == n? | `S_L(sp) == n` | **RT** | — |

**SM rationale for TRIM/SPCINT/SPREAL:**
- `SM_TRIM` — appears in VARVAL (string cleanup before use). Very common in pattern matching setup.
- `SM_SPCINT`/`SM_SPREAL` — appear in INTVAL and EVAL's numeric coercion path. Making them SM ops eliminates a `SM_CALL "spcint"` round-trip. EVAL uses both in sequence; an SM instruction can branch on parse failure directly (the `f_label` operand in SCRIP-SM.md).

---

## Group 5 — Control Flow

**Axis: mostly SM (already DONE); key additions are JUMP_INDIR, SELBRA, STATE_PUSH/POP.**

| SIL Macro | SIL Semantics | scrip-interp | SM_Program |
|-----------|---------------|:---:|:---:|
| `BRANCH label` | unconditional goto | goto | SM `SM_JUMP` (**DONE**) |
| `RCALL ret,proc,args,exits` | call procedure with exit table | call dispatch | SM `SM_CALL` (**DONE**) |
| `RRTURN ret,n` | return via exit n | return/longjmp | SM `SM_RETURN`/`SM_FRETURN` (**DONE**) |
| `BRANIC d,off` | branch indirect via descriptor | `((FnPtr)d.ptr)()` | SM **`SM_JUMP_INDIR`** |
| `SELBRA d,table` | select branch by integer index | switch(d.v){table[i]} | SM **`SM_SELBRA`** |
| `PUSH d` | push descriptor onto stack | cstack++ | SM `SM_PUSH_VAR`/lit (**DONE**) |
| `POP d` | pop descriptor from stack | cstack-- | SM `SM_POP` (**DONE**) |
| `SPUSH sp` | push specifier (2 descriptors) | cstack += SPEC/DESCR | **RT** (used in EXPVAL save) |
| `SPOP sp` | pop specifier | cstack -= SPEC/DESCR | **RT** (used in EXPVAL restore) |
| `ISTACKPUSH` | push 14 descriptors + 4 specs | full state save | SM **`SM_STATE_PUSH`** |
| `PSTACK x` | save pattern stack ptr | `x.a = cstack-1` | **RT** (bb_pool context) |
| `ISTACK` | init stack pointer | cstack = stack base | **RT** (init only) |

**SM_JUMP_INDIR use:** `GOTG` (`:(<VAR>)` computed goto) — pops a CODE descriptor,
jumps to its code block. Also `INVK1` `BRANIC INCL,0` — indirect dispatch to function.
In `sm_interp.c` this is: `pc = (SM_Instr*)descr.ptr; continue;`

**SM_SELBRA use:** `EXPVAL`'s `SELBRA SCL,(FAIL,RTXNAM,RTZPTR)` — selects exit
based on integer index. In `sm_interp.c`: `goto *exit_table[instr.u.table[d.ival]]`
or equivalent computed goto. Also used in `INTERP`'s `INVOKE` exit dispatch.

**SM_STATE_PUSH/POP use:** `EXPVAL` saves 14 descriptors + 4 specifiers before
executing a nested EXPRESSION, restores them after. In `sm_interp.c` this becomes
a memcpy of the interpreter's register file to a save stack.

---

## Group 6 — Pattern Building (SM — DONE)

All `SM_PAT_*` instructions are already designed in SCRIP-SM.md.

`SM_PAT_LIT`, `SM_PAT_ANY`, `SM_PAT_NOTANY`, `SM_PAT_SPAN`, `SM_PAT_BREAK`,
`SM_PAT_LEN`, `SM_PAT_POS`, `SM_PAT_RPOS`, `SM_PAT_TAB`, `SM_PAT_RTAB`,
`SM_PAT_ARB`, `SM_PAT_REM`, `SM_PAT_BAL`, `SM_PAT_FENCE`, `SM_PAT_ABORT`,
`SM_PAT_FAIL`, `SM_PAT_SUCCEED`, `SM_PAT_ALT`, `SM_PAT_CAT`, `SM_PAT_DEREF`,
`SM_PAT_CAPTURE`.

SIL equivalents: `ANY`, `BREAK`, `BREAKX`, `NOTANY`, `SPAN`, `LEN`, `POS`,
`RPOS`, `RTAB`, `TAB`, `ARBNO`.

---

## Group 7 — Byrd Box Construction (RT — DONE)

| SIL Proc | Our BB box | scrip-interp | SM_Program |
|----------|-----------|:---:|:---:|
| `NAM` (.VAR conditional assign) | `bb_capture.c` | **DONE** | — |
| `DOL` ($VAR immediate assign) | `bb_capture.c` (immed) | **DONE** | — |
| `SCAN`/`SJSR`/`SCNR` (scan loop) | `BB-DRIVER` | **DONE** | via `SM_EXEC_STMT` |
| `ATOP` (@ cursor assign) | `bb_capture.c` (cursor) | **DONE** | — |
| `ANY`/`BREAK`/`BREAKX`/`NOTANY`/`SPAN` | `bb_*.c` | **DONE** | — |
| `LEN`/`POS`/`RPOS`/`RTAB`/`TAB` | `bb_*.c` | **DONE** | — |
| `ARBNO` | `bb_arbno.c` | **DONE** | — |

---

## Group 8 — Named Builtins (RT via INVOKE table)

All become C functions registered via `register_fn()`.
None are SM instructions — they are called through `SM_CALL name, nargs`.
SM instruction `SM_CALL` dispatches to the INVOKE table.

| SIL Proc | Builtin | scrip-interp | SM_Program | RT milestone |
|----------|---------|:---:|:---:|------|
| `INVOKE`/`INVK1`/`INVK2` | dispatch core | **RT** `INVOKE_fn` | via `SM_CALL` | RUNTIME-1 |
| `ARGVAL` | arg evaluator (untyped) | **RT** `ARGVAL_fn` | via SM dispatch | RUNTIME-1 |
| `VARVAL` | arg → STRING | **RT** `VARVAL_fn` | via SM dispatch | RUNTIME-2 |
| `INTVAL` | arg → INTEGER | **RT** `INTVAL_fn` | via SM dispatch | RUNTIME-2 |
| `PATVAL` | arg → PATTERN | **RT** `PATVAL_fn` | via SM dispatch | RUNTIME-2 |
| `VARVUP` | arg → uppercase STRING | **RT** `VARVUP_fn` | via SM dispatch | RUNTIME-2 |
| `NAME` | .X → DT_N descriptor | **RT** `NAME_fn` | via SM dispatch | RUNTIME-3 |
| `ASGN`/`ASGNV`/`ASGNIC` | assignment with hooks | **RT** `ASGN_fn` | via SM dispatch | RUNTIME-5 |
| `NMD`/`NMD1`–`NMD5`/`NMDIC` | naming list commit | **RT** `NMD_fn` | via SM dispatch | RUNTIME-4 |
| `EXPVAL`/`EXPEVL` | EXPRESSION execute | **RT** `EXPVAL_fn` | `SM_STATE_PUSH/POP` | RUNTIME-6 |
| `CONVE`/`CODER` | string→EXPRESSION/CODE | **RT** `CONVE_fn` | via SM dispatch | RUNTIME-7 |
| `CNVRT` | CONVERT(X,T) | **RT** `CONVERT_fn` | via SM dispatch | RUNTIME-7 |
| `EVAL`/`EVAL1` | EVAL() builtin | **RT** `EVAL_fn` | via SM dispatch | RUNTIME-8 |
| `INTERP`/`INTRP0` | interpreter core | `execute_program()` | `sm_interp.c` loop | RUNTIME-9 |
| `INIT` | statement header | per-stmt setup | SM header decode | RUNTIME-9 |
| `GOTO` | offset goto | goto dispatch | `SM_JUMP` target | RUNTIME-9 |
| `GOTL` | label goto + special labels | label lookup | `SM_JUMP` + INVOKE | RUNTIME-9 |
| `GOTG` | `:(<VAR>)` computed goto | — | `SM_JUMP_INDIR` | RUNTIME-9 |
| `BASE` | code basing | — | `SM_CALL` setup | RUNTIME-9 |
| `PLS` | unary +X (NOT identity) | ⚠️ missing | via SM dispatch | RUNTIME-2 fix |
| `INTGER` | INTEGER(X) | ✅ | via SM dispatch | — |
| `EQ`/`NE`/`GT`/`LT`/`GE`/`LE` | numeric predicates | ✅ | via `SM_ACOMP` | — |
| `LEQ`/`LNE`/`LGT`/`LLT`/`LGE`/`LLE` | string predicates | ✅ | via `SM_LCOMP` | — |
| `DIFFER`/`IDENT` | identity tests | ✅ | via SM dispatch | — |
| `SIZE`/`TRIM`/`DUPL` | string ops | ✅ | via SM dispatch | — |
| `SUBSTR`/`RPLACE`/`REVERS` | string ops | ✅ | via SM dispatch | — |
| `LPAD`/`RPAD`/`CHAR` | string ops | ✅ | via SM dispatch | — |
| `ARRAY`/`ASSOC`/`ITEM` | array/table ops | ✅ | via SM dispatch | — |
| `COPY`/`APPLY`/`DEFINE`/`OPSYN` | control | ✅ | via SM dispatch | — |
| `TRACE`/`STOPTR` | trace hooks | ⬜ stub | via SM dispatch | RUNTIME-5 |
| `LABEL` | LABEL(X) | partial | via SM dispatch | RUNTIME-3 |
| `IND` | $X indirect | ✅ | via SM dispatch | — |
| `KEYWRD` | &KW access | partial | via SM dispatch | RUNTIME-3 |
| `ARG`/`LOCAL`/`FIELD`/`FIELDS` | introspection | ✅ | via SM dispatch | — |
| `DATDEF`/`FUNCTN`/`SORT`/`RSORT` | meta | ✅ | via SM dispatch | — |
| `EVAL` stub→full | EVAL() | ⚠️ | via SM dispatch | RUNTIME-8 |
| `DATE`/`TIME` | system | ✅ | via SM dispatch | — |

---

## Group 9 — BLOCK-mode Operations (SKIP)

Lines 7160–10211 of v311.sil: BLAND, BOX, BOXIN, AFRAME, etc.
**Decision: SKIP.** No corpus tests use SNOBOL4B blocks.

---

## Group 10 — Compiler Internals (SKIP)

`CMPILE`, `ELEMNT`, `EXPR`, `FORWRD`, `FORRUN`, `FORBLK`, `NEWCRD`,
`CTLADV`, `BLOCK` (allocator), `GC`, `GCM`, `SPLIT`, `BINOP`, etc.
**Decision: SKIP.** We have `CMPILE.c`.

---

## The Two-Axis Master Table — SM Instructions

These are the SM_Program instructions that exist or are added.

**Two completely different backends — different languages:**
- `scrip-interp (C)` column: what `sm_interp.c` does in C when it dispatches
  this op. Calls C RT functions from `sil_macros.h` / `snobol4.c` / `argval.c`.
- `x86 emitter` column: the **x86 assembly instructions** that `emit_x64.c`
  writes into the code buffer when it sees this SM op. `call lexcmp` here means
  the emitter writes the bytes for an x86 `call` instruction targeting the
  `lexcmp` runtime symbol — not a C function call. `jmp [rax]` means the emitter
  writes an indirect-jump encoding. These are assembly mnemonics, not C.

| SM Instruction | SIL Origin | scrip-interp (C) | x86 emitter (asm) | Status |
|----------------|------------|------------------|-------------|--------|
| `SM_PUSH_LIT_S` | `PUSH` literal | push string descr | `mov`+`call push_str` | DONE |
| `SM_PUSH_LIT_I` | `PUSH` integer | push int descr | `mov`+`call push_int` | DONE |
| `SM_PUSH_LIT_F` | `PUSH` real | push real descr | `mov`+`call push_real` | DONE |
| `SM_PUSH_NULL` | `MOVD d,NULVCL` | push null descr | `call push_null` | DONE |
| `SM_PUSH_VAR` | `ARGVAL`/`GETDC` | `NV_GET_fn(name)` | `call NV_GET_fn` | DONE |
| `SM_STORE_VAR` | `PUTDC`/`ASGN` | `NV_SET_fn(name,val)` | `call NV_SET_fn` | DONE |
| `SM_POP` | `POP` | discard top | `sub rsp,DESCR` | DONE |
| `SM_ADD` | `SUM` | `add_fn(a,b)` | `call add_fn` | DONE |
| `SM_SUB` | `SUBTRT` | `sub_fn(a,b)` | `call sub_fn` | DONE |
| `SM_MUL` | `MULT` | `mul_fn(a,b)` | `call mul_fn` | DONE |
| `SM_DIV` | `DIVIDE` | `div_fn(a,b)` | `call div_fn` | DONE |
| `SM_EXP` | `EXREAL` | `exp_fn(a,b)` | `call exp_fn` | DONE |
| `SM_NEG` | `MNSINT`/`MNREAL` | `neg_fn(a)` | `call neg_fn` | DONE |
| `SM_CONCAT` | `APDSP` | `concat_fn(a,b)` | `call concat_fn` | DONE |
| `SM_JUMP` | `BRANCH` | `pc = target` | `jmp target` | DONE |
| `SM_JUMP_S` | `BRANCH` on success | `if(ok) pc=target` | `test/jnz` | DONE |
| `SM_JUMP_F` | `BRANCH` on failure | `if(!ok) pc=target` | `test/jz` | DONE |
| `SM_LABEL` | label def | label table entry | label: | DONE |
| `SM_HALT` | `BRANCH END` | `return` | `ret` | DONE |
| `SM_CALL` | `RCALL`/`INVOKE` | `INVOKE_fn(name,args)` | `call invoke_fn` | DONE |
| `SM_RETURN` | `RRTURN ,6` | longjmp RETURN | `ret`+exit6 | DONE |
| `SM_FRETURN` | `RRTURN ,4` | longjmp FRETURN | `ret`+exit4 | DONE |
| `SM_DEFINE` | `DEFINE` call | `register_fn()` | `call register_fn` | DONE |
| `SM_PAT_*` (21 ops) | pattern procs | `bb_build()` | `call bb_build_*` | DONE |
| `SM_EXEC_STMT` | `SCAN`/BB-DRIVER | `stmt_exec_dyn()` | `call stmt_exec_dyn` | DONE |
| **`SM_JUMP_INDIR`** | `BRANIC d,0` | `pc=(SM_Instr*)d.ptr` | `jmp [rax]` | **ADD** |
| **`SM_SELBRA`** | `SELBRA d,table` | `goto table[d.ival]` | `jmp [table+rax*8]` | **ADD** |
| **`SM_STATE_PUSH`** | `PUSH (OCBSCL…)` + `SPUSH` | memcpy regs to save-stack | `call state_push` | **ADD** |
| **`SM_STATE_POP`** | `POP (…)` + `SPOP` | memcpy from save-stack | `call state_pop` | **ADD** |
| **`SM_INCR`** | `INCRA d,n` | `d += n` (inline) | `add rax,n` | **ADD** |
| **`SM_DECR`** | `DECRA d,n` | `d -= n` (inline) | `sub rax,n` | **ADD** |
| **`SM_ACOMP`** | `ACOMP d1,d2` | `cmp_int(a,b)→-1/0/1` | `cmp rax,rbx` | **ADD** |
| **`SM_RCOMP`** | `RCOMP d1,d2` | `cmp_real(a,b)→-1/0/1` | `ucomisd` | **ADD** |
| **`SM_LCOMP`** | `LEXCMP sp1,sp2` | `lexcmp(a,b)→-1/0/1` | `call lexcmp` | **ADD** |
| **`SM_TRIM`** | `TRIMSP sp1,sp2` | `trimsp(sp1,sp2)` | `call trimsp` | **ADD** |
| **`SM_SPCINT`** | `SPCINT d,sp,f` | `spcint(d,sp)` + branch | `call spcint`+`jz f` | **ADD** |
| **`SM_SPREAL`** | `SPREAL d,sp,f` | `spreal(d,sp)` + branch | `call spreal`+`jz f` | **ADD** |

**12 new SM instructions. Additive — no existing SM_Instr layout change.**

---

## The Two-Axis Master Table — RT Functions (sil_macros.h + RT files)

Functions that exist only in C, called from scrip-interp and SM dispatch — not SM instructions.

| C Function | SIL Origin | File | Used by SM? | RT milestone |
|-----------|-----------|------|:---:|------|
| `TESTF(d,T)` macro | `TESTF` | `sil_macros.h` | dispatch only | now |
| `VEQLC(d,T)` macro | `VEQLC` | `sil_macros.h` | dispatch only | now |
| `DEQL(a,b)` macro | `DEQL` | `sil_macros.h` | dispatch only | now |
| `AEQLC(d,v)` macro | `AEQLC` | `sil_macros.h` | dispatch only | now |
| `IS_INT/REAL/STR/PAT/…` | type shorthands | `sil_macros.h` | dispatch only | now |
| `INCRA(d,n)` / `DECRA(d,n)` | `INCRA`/`DECRA` | `sil_macros.h` | `SM_INCR`/`SM_DECR` | now |
| `SPCINT_fn(d,sp)` | `SPCINT` | `argval.c` | `SM_SPCINT` dispatch | RUNTIME-2 |
| `SPREAL_fn(d,sp)` | `SPREAL` | `argval.c` | `SM_SPREAL` dispatch | RUNTIME-2 |
| `REALST_fn(sp,d)` | `REALST` | `argval.c` | via `SM_CALL` | RUNTIME-2 |
| `INTSP_fn(sp,d)` | `INTSP` / `INTSPC` | `argval.c` | via `SM_CALL` | RUNTIME-2 |
| `TRIM_fn(sp,sp)` | `TRIMSP` | `snobol4.c` | `SM_TRIM` dispatch | now |
| `LCOMP_fn(sp,sp)` | `LEXCMP` | `snobol4.c` | `SM_LCOMP` dispatch | now |
| `INVOKE_fn(name,args,n)` | `INVOKE` | `invoke.c` | `SM_CALL` dispatch | RUNTIME-1 |
| `ARGVAL_fn(d)` | `ARGVAL` | `argval.c` | SM arg fetch | RUNTIME-1 |
| `VARVAL_fn(d)` | `VARVAL` | `argval.c` | `SM_PUSH_VAR` coerce | RUNTIME-2 |
| `INTVAL_fn(d)` | `INTVAL` | `argval.c` | `SM_PUSH_VAR`→INT | RUNTIME-2 |
| `PATVAL_fn(d)` | `PATVAL` | `argval.c` | `SM_PAT_DEREF` | RUNTIME-2 |
| `VARVUP_fn(d)` | `VARVUP` | `argval.c` | `SM_CALL "VARVUP"` | RUNTIME-2 |
| `NAME_fn(varname)` | `NAME` | `snobol4.c` | `SM_CALL ".X"` | RUNTIME-3 |
| `ASGNIC_fn(kw,val)` | `ASGNIC` | `snobol4.c` | `SM_STORE_VAR` DT_K | RUNTIME-3 |
| `NAM_push/commit/discard` | `NMD` | `nmd.c` | `SM_EXEC_STMT` | RUNTIME-4 |
| `ASGN_fn(name,val)` | `ASGN` | `snobol4.c` | `SM_STORE_VAR` hook | RUNTIME-5 |
| `EXPVAL_fn(d)` | `EXPVAL` | `eval_code.c` | `SM_STATE_PUSH/POP` | RUNTIME-6 |
| `EXPEVL_fn(d)` | `EXPEVL` | `eval_code.c` | via `SM_CALL` | RUNTIME-6 |
| `CONVE_fn(str_d)` | `CONVE` | `snobol4.c` | via `SM_CALL` | RUNTIME-7 |
| `CODE_fn(args,n)` | `CODER` | `snobol4.c` | via `SM_CALL "CODE"` | RUNTIME-7 |
| `CONVERT_fn(args,n)` | `CNVRT` | `snobol4.c` | via `SM_CALL "CONVERT"` | RUNTIME-7 |
| `EVAL_fn(args,n)` | `EVAL` | `snobol4.c` | via `SM_CALL "EVAL"` | RUNTIME-8 |
| `state_push()`/`state_pop()` | `ISTACKPUSH` | `eval_code.c` | `SM_STATE_PUSH/POP` | RUNTIME-6 |

---

## sil_macros.h — Complete Design

Create `src/runtime/snobol4/sil_macros.h`. This is the **RT axis** header.
The **SM axis** changes are in `sm_interp.c` enum + dispatch (RUNTIME-9).

```c
/*
 * sil_macros.h — C translations of SIL macro instructions
 *
 * Axis 1 (scrip-interp / RT functions):
 *   Used by snobol4.c, argval.c, invoke.c, nmd.c, eval_code.c, stmt_exec.c
 *
 * Axis 2 (SM_Program dispatch):
 *   SM_INCR/SM_DECR dispatch calls INCRA/DECRA defined here.
 *   SM_ACOMP/SM_RCOMP/SM_LCOMP dispatch calls ACOMP/RCOMP/LCOMP.
 *   SM_TRIM/SM_SPCINT/SM_SPREAL dispatch calls TRIM_fn/SPCINT_fn/SPREAL_fn.
 *   SM_STATE_PUSH/POP dispatch calls state_push()/state_pop().
 *
 * Authors: Lon Jones Cherryholmes · Claude Sonnet 4.6
 * Date: 2026-04-05
 */
#ifndef SIL_MACROS_H
#define SIL_MACROS_H

#include "snobol4.h"   /* DESCR_t, DT_* constants */

/* ── Group 1: Descriptor field access ── */
#define GETDC(d, base, off)    ((d) = *((DESCR_t*)(base) + (off)/sizeof(DESCR_t)))
#define PUTDC(base, off, d)    (*((DESCR_t*)(base) + (off)/sizeof(DESCR_t)) = (d))
#define MOVD(dst, src)         ((dst) = (src))
#define MOVV(dst, src)         ((dst).v = (src).v)
#define MOVA(dst, src)         ((dst).ptr = (src).ptr)
#define SETAC(d, val)          ((d).ptr = (void*)(intptr_t)(val))
#define SETAV(d, src)          ((d).ptr = (void*)(intptr_t)(src).v)

/* ── Group 2: Type tests — scrip-interp RT axis ── */
#define TESTF(d, T)            ((d).f & (T))
#define IS_FNC(d)              TESTF((d), FNC)
#define VEQLC(d, T)            ((d).v == (T))
#define DEQL(a, b)             ((a).v == (b).v && (a).ptr == (b).ptr)
#define AEQLC(d, val)          ((intptr_t)(d).ptr == (intptr_t)(val))
#define AEQL(a, b)             ((a).ptr == (b).ptr)
#define SAME_TYPE(a, b)        ((a).v == (b).v)

/* Type shorthands — use DT_* constants from snobol4.h */
#define IS_INT(d)    ((d).v == DT_I)
#define IS_REAL(d)   ((d).v == DT_R)
#define IS_STR(d)    ((d).v == DT_S || (d).v == DT_SNUL)
#define IS_PAT(d)    ((d).v == DT_P)
#define IS_NAME(d)   ((d).v == DT_N)
#define IS_KW(d)     ((d).v == DT_K)
#define IS_EXPR(d)   ((d).v == DT_E)
#define IS_CODE(d)   ((d).v == DT_C)
#define IS_ARR(d)    ((d).v == DT_A)
#define IS_TBL(d)    ((d).v == DT_T)

/* ── Group 2: Comparison — both RT and SM dispatch axis ── */
/* ACOMP: returns -1/0/1 like strcmp; SM_ACOMP dispatches to this */
static inline int ACOMP(DESCR_t a, DESCR_t b) {
    intptr_t la = (intptr_t)a.ptr, lb = (intptr_t)b.ptr;
    return (la > lb) - (la < lb);
}
/* ACOMPC: compare descriptor address vs constant */
#define ACOMPC(d, val) \
    (((intptr_t)(d).ptr > (intptr_t)(val)) - ((intptr_t)(d).ptr < (intptr_t)(val)))

/* RCOMP: real compare; SM_RCOMP dispatches to this */
static inline int RCOMP(DESCR_t a, DESCR_t b) {
    return (a.dval > b.dval) - (a.dval < b.dval);
}

/* LCOMP: lexicographic string compare; SM_LCOMP dispatches to lexcmp() */
/* Declaration — defined in snobol4.c or string RT */
int LCOMP_fn(const char *sp1, int len1, const char *sp2, int len2);

/* ── Group 3: Address arithmetic — SM_INCR/SM_DECR dispatch here ── */
#define INCRA(d, n)   ((d) += (n))
#define DECRA(d, n)   ((d) -= (n))

/* ── Group 4: String/specifier coercions — SM_SPCINT/SPREAL dispatch here ── */
/* Returns 1 on success, 0 on failure (SM_SPCINT branches on 0) */
int SPCINT_fn(DESCR_t *out, const char *sp, int len);
int SPREAL_fn(DESCR_t *out, const char *sp, int len);
/* Format functions */
int REALST_fn(char *out, int maxlen, DESCR_t d);
int INTSP_fn(char *out, int maxlen, DESCR_t d);
/* SM_TRIM dispatches to TRIM_fn */
void TRIM_fn(const char *in, int inlen, const char **out, int *outlen);

/* ── Group 5: State save/restore — SM_STATE_PUSH/POP dispatch here ── */
/* For EXPVAL (RUNTIME-6): save/restore full interpreter register file */
void state_push(void);   /* ISTACKPUSH — push OCBSCL,OCICL,… */
void state_pop(void);    /* restore from state stack */

/* ── Descriptor null/fail sentinels ── */
/* FAILDESCR: the canonical failure descriptor (DT_FAIL type) */
extern DESCR_t FAILDESCR;
extern DESCR_t NULLDESCR;

#endif /* SIL_MACROS_H */
```

---

## Relationship to RT Milestones (updated)

| RT Milestone | Uses (scrip-interp axis) | Uses (SM axis) |
|-------------|--------------------------|----------------|
| RUNTIME-1 INVOKE | `TESTF`, `VEQLC`, `BRANIC`→`INVOKE_fn` | `SM_CALL` dispatches `INVOKE_fn` |
| RUNTIME-2 VARVAL/INTVAL/PATVAL | `SPCINT_fn`, `SPREAL_fn`, `INTRL`, `RLINT`, `LOCSP`, `GETLG` | `SM_SPCINT`, `SM_SPREAL`, `SM_PUSH_VAR` coerce |
| RUNTIME-3 NAME/KEYWORD | `VEQLC` DT_K, `GETDC`/`PUTDC`, `NAME_fn` | `SM_STORE_VAR` DT_K path, `SM_CALL ".X"` |
| RUNTIME-4 NMD | `GETLG`, `ACOMP`, `GETSPC`, `PUTDC`, `SPCINT_fn` | `SM_EXEC_STMT` calls `NAM_commit`/`NAM_discard` |
| RUNTIME-5 ASGN | `TESTF`, `VEQLC`, `PUTDC`, `AEQLC` trace check | `SM_STORE_VAR` extended with output/trace hooks |
| RUNTIME-6 EXPVAL | `SM_STATE_PUSH/POP`, `SPUSH`/`SPOP` | `SM_STATE_PUSH` + `SM_STATE_POP` instructions |
| RUNTIME-7 CONVE/CODER | `SPCINT_fn`, `SPREAL_fn`, `LOCSP`, `GETLG` | `SM_CALL "CODE"`, `SM_CALL "CONVERT"` |
| RUNTIME-8 EVAL | `VEQLC` dispatch, `SPCINT_fn`, `SPREAL_fn`, `CONVE_fn`, `EXPVAL_fn` | `SM_CALL "EVAL"` → `SM_SPCINT`/`SM_SPREAL` inline |
| RUNTIME-9 INTERP | `INCRA`/`DECRA`, `TESTF`, `BRANIC`, `SELBRA`, `ACOMP`/`RCOMP` | ALL SM instructions — `sm_interp.c` dispatch loop |

---

## Actions Required (Priority Order)

### Now (this session)
1. **Create `sil_macros.h`** — the header above. Verified against `macros.h`.
2. **Update SCRIP-SM.md** — add 12 new SM ops to the instruction table.
3. **Fix PLS** — `register_fn("PLS", _b_pls, 1, 1)` — unary `+X` is NOT identity.

### Per RT Milestone
Each RT-N reads the corresponding SIL proc from `v311.sil`, implements in C
using `sil_macros.h` type tests and field accessors, registers in INVOKE table.

### RUNTIME-9 — sm_interp.c (The Architecture Target)
When `sm_interp.c` is written, every SM instruction in the master table above
gets a dispatch case. The 12 new SM ops each call the corresponding RT function
defined in `sil_macros.h`. The emitter maps each SM op to native code.

---

## Summary — Counts by Axis

| Group | Count | scrip-interp axis | SM_Program axis |
|-------|-------|:-:|:-:|
| Descriptor access macros | 13 | `sil_macros.h` C macros | — |
| Type test / compare | 16 | `sil_macros.h` + 3 SM ops | `SM_ACOMP`, `SM_RCOMP`, `SM_LCOMP` |
| Address arithmetic | 2 inline + rest RT | `sil_macros.h` INCRA/DECRA | `SM_INCR`, `SM_DECR` |
| String / specifier | 21 RT functions | `argval.c`, `snobol4.c` | `SM_TRIM`, `SM_SPCINT`, `SM_SPREAL` |
| Control flow | 12 | goto/longjmp/call | `SM_JUMP_INDIR`, `SM_SELBRA`, `SM_STATE_PUSH/POP` |
| Pattern building | 21 | bb_build() | `SM_PAT_*` (DONE) |
| Byrd box construction | 15 | bb_*.c (DONE) | via `SM_EXEC_STMT` |
| Named builtins | ~50 | RT functions via INVOKE | via `SM_CALL` |
| SNOBOL4B blocks | ~50 | SKIP | SKIP |
| Compiler internals | ~25 | SKIP | SKIP |

**Total useful: ~120 of 211 procedures**
**SM_Program instructions: 12 new + 36 existing = 48 total**
**RT-only functions: ~70 (sil_macros.h + argval.c + invoke.c + nmd.c + snobol4.c extensions)**

---

*MILESTONE-RT-SIL-MACROS.md — revised sprint 99, 2026-04-05*
*Key addition: dual-axis table (scrip-interp vs SM_Program) for every macro.*
*C translations verified against csnobol4 `include/macros.h` and generated `snobol4.c`.*


---

<!-- SOURCE: MILESTONE-SCRIP-UNIFY-X86.md -->

# MILESTONE-SCRIP-UNIFY-X86.md — Unify x86 Executable

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-07
**Status:** ⬜ not started
**Depends on:** SCRIP-UNIFIED.md (design), current PASS=178

---

## Goal

Replace the `scrip-interp` / `scrip-cc` split with a **single `scrip` binary** for
the x86 platform. One executable, three execution modes, zero disk round-trips for
native code.

This is the x86 instance of a per-platform pattern. The JVM and JS platforms will
produce `scrip-jvm` and `scrip-js` respectively — each a self-contained interpreter
for their target. The x86 `scrip` is the primary development focus and the
correctness/performance reference.

---

## Binary Inventory — Before and After

| Before | After | Disposition |
|--------|-------|-------------|
| `scrip-interp` (pre-built, 647KB) | removed | replaced by `scrip --interp` |
| `scrip-interp-dbg` (pre-built) | removed | replaced by `scrip --interp` + debug flags |
| `scrip-interp-s` (pre-built) | removed | replaced by `scrip --interp` stripped |
| `scrip-cc` (Makefile target) | removed | replaced by `scrip --jit-run` / `--jit-emit` |
| *(none)* | **`scrip`** | new unified binary |
| *(future)* | `scrip-jvm` | JVM interpreter (separate milestone) |
| *(future)* | `scrip-js` | JS interpreter (separate milestone) |

---

## Execution Modes (from SCRIP-UNIFIED.md RT-128 addendum)

```
scrip --interp      Mode I:  C tree-walk over IR. Correctness reference.
scrip --hybrid      Mode GS2: SM dispatch (phases 1/2/4/5) + BB-DRIVER (phase 3). [default]
scrip --gen         alias for --hybrid
scrip --stackless   Mode GS1: 100% stackless x86 blob chain, no SM dispatch overhead.
```

---

## Milestone Steps

### U0 — Remove pre-built binaries and rename driver ✅ partial
- [x] Remove `sno4parse` pre-built binary (done 2026-04-07, commit `7186f29c`)
- [ ] Remove `scrip-interp`, `scrip-interp-dbg`, `scrip-interp-s` pre-built binaries
- [ ] Rename `src/driver/scrip.c` entry point to unify `--interp` / `--gen` flags
- [ ] Root `Makefile`: rename target `scrip-interp` → `scrip`; remove `scrip-cc` target
- [ ] `src/Makefile`: change `BIN = ../scrip-cc` → `BIN = ../scrip`
- **Gate:** `make` produces `scrip`; `scrip --interp corpus/001.sno` passes

### U1 — Harness switchover
- [ ] Update all test scripts in `test/` that reference `scrip-interp` or `scrip-cc` → `scrip`
- [ ] Update `snobol4-asm.sh`, `snobol4-jvm.sh`, `snobol4-net.sh` wrapper scripts
- [ ] Update `harness/` repo references
- **Gate:** `run_invariants.sh` and `run_emit_check.sh` pass at PASS=178 with `scrip`

### U2 — Scrip image / segment allocator
- [ ] Create `src/runtime/asm/scrip_image.c` + `.h` — mmap slab allocator for 5 segments
  - segment 0: runtime stubs (RX)
  - segment 1: SM dispatch table (RX)
  - segment 2: program body (RX, variable)
  - segment 3: Byrd box pool (RW/RX, per-statement)
  - segment 4: data / constants (RW)
- [ ] Wire into `scrip --gen` path (replaces disk .s emission)
- **Gate:** `scrip_image_test` allocates all segments, mprotects, writes+calls a stub

### U3 — SM-LOWER (IR → SM_Program)
- [ ] Create `src/runtime/sm/sm_lower.c` + `.h`
- [ ] IR STMT_t/EXPR_t nodes → flat SM_Program (array of SM instructions)
- [ ] SM_PAT_* instructions for pattern phases; SM_EXEC_STMT for BB-DRIVER handoff
- **Gate:** `sm_interp_test` runs all 178 passing corpus programs via SM_Program

### U4 — Pattern integration (--hybrid default)
- [ ] Wire SM_PAT_* → BB-GRAPH build; SM_EXEC_STMT → BB-DRIVER call
- [ ] `scrip --hybrid` executes SM_Program via SM dispatch + BB-DRIVER for phase 3
- **Gate:** PASS=178 via `scrip --hybrid`; diff of `--interp` vs `--hybrid` trace is empty

### U5 — Stackless path (--stackless)
- [ ] Inline blob chain: each SM instruction → self-contained x86 blob, direct jmp wiring
- [ ] r13 = stmt frame ptr; BB-DRIVER inline; C stack only at static helper boundaries
- **Gate:** PASS=178 via `scrip --stackless`; M-DYN-BENCH-X86 filled (all 3 mode columns)

---

## Test Command Reference

```sh
# Smoke — all three modes must agree
scrip --interp   corpus/001.sno
scrip --hybrid   corpus/001.sno
scrip --stackless corpus/001.sno

# Full corpus
./test/run_invariants.sh

# Mode diff (must be empty after U4)
SNO_TRACE=1 scrip --interp  /tmp/x.sno 2>/tmp/interp.trace
SNO_TRACE=1 scrip --hybrid  /tmp/x.sno 2>/tmp/hybrid.trace
diff /tmp/interp.trace /tmp/hybrid.trace

# vs oracle
SNO_TRACE=1 scrip --interp /tmp/x.sno 2>/tmp/interp.trace
SNO_TRACE=1 /home/claude/x64/bin/spitbol /tmp/x.sno 2>/tmp/spitbol.trace
diff /tmp/interp.trace /tmp/spitbol.trace | head -30
```

---

## What Does NOT Change

- Frontend (CMPILE.c, IR) — unchanged
- Runtime (stmt_exec.c, bb_*.c boxes) — unchanged
- Corpus — unchanged
- BB-GRAPH, BB-DRIVER, BB-GEN-X86-BIN docs — unchanged (blob ABI unchanged)
- M-DYN-B* milestone chain — continues as-is; blobs slot into segment 3

---

*Written: 2026-04-07, Lon Jones Cherryholmes + Claude Sonnet 4.6*
*Design basis: SCRIP-UNIFIED.md (RT-125 + RT-128 addendum)*


---

<!-- SOURCE: MILESTONE-SCRIP-X86-COMPLETION.md -->

# MILESTONE-SCRIP-X86-COMPLETION.md — Dead Code Audit + Gap Analysis

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-07
**Status:** ⬜ active planning

---

## The Single-Binary Principle

`scrip` is the one and only x86 executable. Every switch must route to real
code. Dead code is archived. Gaps are milestoned.

---

## Switch Coverage Map — What Is and Is Not Wired

### Execution modes

| Switch | Status | Notes |
|--------|--------|-------|
| `--ir-run` | ✅ **WIRED** | `execute_program()` in scrip.c — full, PASS=178 |
| `--sm-run` | ✅ **WIRED** | `sm_lower()` + `sm_interp_run()` — full, PASS=178 |
| `--jit-run` | ✅ **WIRED** | `sm_codegen()` + `sm_jit_run()` — threaded-call JIT, PASS=178 |
| `--jit-emit` | ⬜ **STUB** | flag parsed, `(void)` suppressed — no codegen |

### Byrd Box pattern mode

| Switch | Status | Notes |
|--------|--------|-------|
| `--bb-driver` | ✅ **WIRED** | `exec_stmt()` → BB-DRIVER → BB-GRAPH — works with all exec modes |
| `--bb-live` | ✅ **WIRED** | `g_bb_mode = BB_MODE_LIVE` → `bb_build_binary_node()` with PATND cache |

### Targets (for `--jit-emit`)

| Switch | Status | Emitter file | Notes |
|--------|--------|-------------|-------|
| `--x64` | ⚠️ **OLD EMITTER** | `emit_x64.c` (5827 lines) | Sub-box text emitter; emits `.s` → disk → nasm → ld. Not SM-based. Keep linked, archive-label. |
| `--jvm` | ⚠️ **OLD EMITTER** | `emit_jvm.c` (4953 lines) + `emit_jvm_icon.c` + `emit_jvm_prolog.c` | Jasmin text emitter. Not SM-based. Keep linked, archive-label. |
| `--net` | ⚠️ **OLD EMITTER** | `emit_net.c` (2841 lines) | IL text emitter. Not SM-based. Keep linked, archive-label. |
| `--js` | ⚠️ **OLD EMITTER** | `emit_js.c` (1125 lines) | JS text emitter. Not SM-based. Keep linked, archive-label. |
| `--c` | ⚠️ **OLD EMITTER** | `emit_byrd_c.c` (4820 lines) + `emit_cnode.c` (476 lines) | C text emitter. Not SM-based. Keep linked, archive-label. |
| `--wasm` | ⚠️ **OLD EMITTER** | `emit_wasm.c` (2118 lines) + icon/prolog variants | WAT text emitter. Not SM-based. Keep linked, archive-label. |

### Diagnostic options

| Switch | Status | Notes |
|--------|--------|-------|
| `--dump-ir` | ✅ **WIRED** | `ir_dump_program()` — works |
| `--dump-sm` | ✅ **WIRED** | `sm_prog_print(sm, stdout)` after `sm_lower()` |
| `--dump-bb` | ✅ **WIRED** | `g_opt_dump_bb` — prints PATND tree before each match |
| `--trace` | ✅ **WIRED** | `g_opt_trace` — prints statement number to stderr |
| `--bench` | ✅ **WIRED** | `clock_gettime(CLOCK_MONOTONIC)` wraps execution dispatch |
| `--dump-parse` | ✅ **WIRED** | `cmpile_print()` — works |
| `--dump-parse-flat` | ✅ **WIRED** | works |
| `--dump-ir-bison` | ✅ **WIRED** | old Bison/Flex path — works |

---

## Dead Code Inventory

### Archive immediately — replaced by scrip.c

| File | Reason | Destination |
|------|--------|-------------|
| `archive/driver/main.c` | old `scrip-cc` driver | already in archive — add README note |
| `archive/driver/scrip-interp.c` | old standalone interpreter | already in archive — add README note |
| `src/runtime/asm/bb_poc.c` | proof-of-concept mmap, superseded by scrip_image.c | `archive/backend/` |
| `src/runtime/asm/bb_emit_test.c` | standalone test, not built by Makefile | `archive/backend/` |
| `src/runtime/asm/bb_pool_test.c` | standalone test, not built by Makefile | `archive/backend/` |
| `src/runtime/asm/snobol4_asm.mac` | NASM macro file for old text emitter path | `archive/backend/` |
| `src/runtime/asm/snobol4_asm_harness.c` | harness for asm path | `archive/backend/` |
| `src/runtime/asm/x86_stubs_interp.c` | satisfies asm externs for scrip-interp — no longer needed | `archive/backend/` |

### Archive-label (keep linked, mark as reference)

These are the **old sub-box emitters**. They still compile and produce correct
output via the old pipeline (`--jit-emit` dispatches to them as a stopgap until
new SM-based emitters are written). They are **not dead yet** — they are the
stopgap implementation of `--jit-emit`. But they are superseded by design and
will be replaced milestone by milestone.

| File | Label |
|------|-------|
| `src/backend/emit_x64.c` | `/* LEGACY: sub-box text emitter; superseded by M-JITEM-X64 */` |
| `src/backend/emit_x64_icon.c` | same |
| `src/backend/emit_x64_prolog.c` | same |
| `src/backend/emit_x64_snocone.c` | same |
| `src/backend/emit_jvm.c` | `/* LEGACY: Jasmin text emitter; superseded by M-JITEM-JVM */` |
| `src/backend/emit_jvm_icon.c` | same |
| `src/backend/emit_jvm_prolog.c` | same |
| `src/backend/emit_net.c` | `/* LEGACY: IL text emitter; superseded by M-JITEM-NET */` |
| `src/backend/emit_js.c` | `/* LEGACY: JS text emitter; superseded by M-JITEM-JS */` |
| `src/backend/emit_byrd_c.c` | `/* LEGACY: C text emitter; superseded by M-JITEM-C */` |
| `src/backend/emit_cnode.c` | `/* LEGACY: C node emitter; superseded by M-JITEM-C */` |
| `src/backend/emit_wasm.c` | `/* LEGACY: WAT text emitter; superseded by M-JITEM-WASM */` |
| `src/backend/emit_wasm_icon.c` | same |
| `src/backend/emit_wasm_prolog.c` | same |
| `src/backend/trampoline.h` | `/* LEGACY: trampoline infrastructure for old x64 text path */` |

---

## Gap Milestones


### M-JITEM-X64 — New SM-based `--jit-emit --x64` emitter
**Switch:** `--jit-emit --x64`

Replace `emit_x64.c` (sub-box text emitter) with SM_Program → x86 `.s` walker.
One box emitted at a time (3-column output: label / instruction / comment).
This is the new architecture: SM instruction → blob description → text.

- New file: `src/backend/emit_sm_x64.c`
- Walk `SM_Program`; for each instruction emit corresponding x86 text blobs
- 3-column output format (supersedes old flat emit style)
- **Gate:** `scrip --jit-emit --x64 corpus/001.sno` produces correct `.s`; assemble+run passes

---

### M-JITEM-JVM — New SM-based `--jit-emit --jvm` emitter
**Switch:** `--jit-emit --jvm`

Replace `emit_jvm.c` with SM_Program → Jasmin `.j` walker.

- New file: `src/backend/emit_sm_jvm.c`
- **Gate:** PASS=165 via `scrip --jit-emit --jvm` (current JVM baseline)

---

### M-JITEM-NET — New SM-based `--jit-emit --net` emitter
**Switch:** `--jit-emit --net`

Replace `emit_net.c` with SM_Program → IL `.il` walker.

- New file: `src/backend/emit_sm_net.c`
- **Gate:** PASS=170 via `scrip --jit-emit --net` (current .NET baseline)

---

### M-JITEM-JS — New SM-based `--jit-emit --js` emitter
**Switch:** `--jit-emit --js`

Replace `emit_js.c` with SM_Program → JavaScript walker.

- New file: `src/backend/emit_sm_js.c`
- **Gate:** PASS=174 via `scrip --jit-emit --js` (current JS baseline)

---

### M-JITEM-C — New SM-based `--jit-emit --c` emitter
**Switch:** `--jit-emit --c`

Replace `emit_byrd_c.c` + `emit_cnode.c` with SM_Program → C walker.

- New file: `src/backend/emit_sm_c.c`
- **Gate:** `scrip --jit-emit --c corpus/001.sno` produces C that compiles and runs correctly

---

### M-JITEM-WASM — New SM-based `--jit-emit --wasm` emitter
**Switch:** `--jit-emit --wasm`

Replace `emit_wasm.c` with SM_Program → WAT walker.

- New file: `src/backend/emit_sm_wasm.c`
- **Gate:** existing WASM corpus tests pass via new emitter

---

## Recommended Execution Order

1. ~~**M-DIAG**~~ ✅ done 2026-04-07
2. ~~**M-BB-LIVE-WIRE**~~ ✅ done 2026-04-07
3. ~~**M-DYN-B13**~~ ✅ done 2026-04-07
4. ~~**M-JIT-RUN**~~ ✅ done 2026-04-07
5. **M-DYN-BENCH-X86** — benchmark `--bb-live` vs `--bb-driver`; fill results table
6. **M-JITEM-X64** — new 3-column SM-based text emitter replaces emit_x64.c
7. **M-JITEM-JVM / NET / JS / C / WASM** — parallel, lower priority

---

## Archive Actions (immediate, no milestone needed)

```bash
# Move truly dead files to archive
git mv src/runtime/asm/bb_poc.c          archive/backend/
git mv src/runtime/asm/bb_emit_test.c    archive/backend/
git mv src/runtime/asm/bb_pool_test.c    archive/backend/
git mv src/runtime/asm/snobol4_asm.mac   archive/backend/
git mv src/runtime/asm/snobol4_asm_harness.c archive/backend/
git mv src/runtime/asm/x86_stubs_interp.c    archive/backend/
```

Add `/* LEGACY */` comment to top of each old emitter in `src/backend/`.

---

*Written: 2026-04-07, Lon Jones Cherryholmes + Claude Sonnet 4.6*


---

<!-- SOURCE: MILESTONE-SN4PARSE-VALIDATE.md -->

# MILESTONE-SN4PARSE-VALIDATE.md — sno4parse Parser Validation & Extension Milestones

**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6
**Date:** 2026-04-04
**Session:** SNOBOL4 × x86, sprint 89
**Status:** ACTIVE — Phase 1 in progress

---

## Context

`sno4parse` is the SNOBOL4 frontend parser for the SCRIP stack. It must parse
the full SPITBOL-extended dialect used in the corpus, not just standard SNOBOL4.
The parser replicates CSNOBOL4's `stream()`/syntab mechanism exactly — **the
256-byte chrs[] table values are authoritative from CSNOBOL4 and must never be
changed**. All fixes are in code logic, not table bytes.

The two-way STREAM trace oracle (SNO_TRACE=1) compares sno4parse vs patched
CSNOBOL4 stream-by-stream. Sweep script: `one4all/csnobol4/dyn89_sweep.sh`.

---

## DYN-89 Baseline (session start)

| Status | Count |
|--------|-------|
| OK     | 14    |
| ERR    | 71    |
| HANG   | 0     |
| Total  | 84    |

---

## Phase 1 — Standard SNOBOL4 Parse Correctness (DYN-89)

**Target: 84/84 OK on corpus/programs/snobol4/**

### Fixes applied this session (DYN-89)

| Fix | Root Cause | Result |
|-----|-----------|--------|
| ELEFNC: FORWRD before arg loop | Missing first FORWRD past `(` | arg-whitespace class fixed |
| ELEFNC: second FORWRD after comma | `F(a, b)` space-after-comma | `, b` now positioned correctly |
| ELEFNC: empty arg `F(a,,b)` and `F(a, ,b)` | loop entered EXPR on `,` | NULL node emitted |
| ELEARY: mirror of ELEFNC fixes | `A[i, j]` subscript with space | subscript-whitespace fixed |
| CMPFRM/CMPASP: FORBLK→FORWRD | `=` already consumed separator | replacement value parsed |
| EQTYP at statement start | unindented `OUTPUT = 'x'` → label+EQTYP | CMPFRM routed correctly |
| NSTTYP: FORWRD after `(` | `( SPAN('x') )` space after paren | inner expr positioned correctly |
| Unary+space: FORWRD after unary chain | `? X` space between op and operand | NBLKTB root cause (see below) |

### Fixes applied this session (DYN-90)

| Fix | Root Cause | Result |
|-----|-----------|--------|
| CMPGO UTOTYP/STOTYP/FTOTYP: FORWRD before/after EXPR | Space after `<` hit ELEMTB before token | `:< C >` direct goto fixed |

### DYN-90 end state

| Status | Count |
|--------|-------|
| OK     | 76    |
| ERR    | 8     |
| HANG   | 0     |

### Remaining bugs (sprint 91 priority order)

**1. BRTYPE=1 postfix subscript on call result `f(g(x)[i])`** (6 files)
- In ELEFNC arg loop, after parsing `g(x)`, `[1]` hits BRTYPE=1 (`[`) → error
- Fix: in `expr_prec_continue`, detect `[` as postfix subscript on any expression
- Same fix as M-SN4PARSE-P2C ([] alias for <>)
- Files: beauty_ShiftReduce_driver, beauty_tree_driver, demo/beauty.sno, claws5, TDump, beauty_oracle

**2. Phantom "illegal character" — Qize.sno, io.sno** (2 files)
- SNO_TRACE shows full parse completing with no ST_ERROR
- `sil_error()` fires but parse output looks correct
- Hypothesis: `g_error` not cleared between statements, OR sweep grep picks up error from earlier statement in same file
- Action: check `g_error` lifecycle; verify with `grep -c "ELEMNT: illegal" <output>`

---

## Phase 2 — SPITBOL Extensions (new syn tables)

### Extensions identified from SPITBOL manual (Appendix C + Chapter 15)

**RULE: All 256-byte chrs[] arrays are authoritative from CSNOBOL4/SPITBOL syn.c.
New tables get their own fresh chrs[] matching SPITBOL semantics. Never modify
existing table bytes.**

#### 2A. `?` as binary pattern-match operator (priority 1, left-associative)

From SPITBOL manual §AppC p275-276:
> The question mark symbol (?) is defined to be an explicit binary pattern-matching
> operator. It is left associative and has priority lower than all operators except
> assignment (=). It returns as its value the substring matched from its left argument
> (a string) by its right argument (a pattern).

```
ABCD ? LEN(3) $ OUTPUT ? LEN(1) REM $ OUTPUT
→ prints ABC then BC
```

- **Current:** `?` is unary only (QUESFN — interrogation, returns null if operand succeeds)
- **SPITBOL adds:** `?` as BINARY op at priority 1 (between `=`=0 and `|`=3)
- **Required:**
  - Add `BISNFN` (already defined as 215 in CMPILE.c) to BIOPTB at priority 1
  - Disambiguate: unary `?` (prefix) vs binary `?` (infix after an expression)
  - The parser already distinguishes unary/binary by context — BIOPTB handles binary
  - Check BIOPTB chrs[63]('?') — currently not in BIOPTB → add if missing
- **New table needed:** None — modify BIOPTB entry (but chrs[] bytes are authoritative!)
  - Alternative: BIOPTB is from CSNOBOL4 which does NOT have binary `?`
  - Therefore a NEW table `BIOPTB_SPITBOL` or an extension mechanism is needed
  - Or: post-processing in `expr_prec_continue` to recognize `?` as binary op

#### 2B. Alternative evaluation `(e1, e2, e3)` — comma-list in parens

From SPITBOL manual §AppC p275:
> A selection or alternative construction: (e1, e2, e3, ..., en)
> Evaluate left to right until one succeeds; failure if all fail.

```snobol4
A = ( EQ(B,3), GT(B,20) ) B+1
NEXT = ( INPUT , %EOF )
```

- **Current:** NSTTYP `(expr)` parses one EXPR. Comma inside parens is only
  valid inside function arg lists (ELEFNC).
- **Required:** When ELEMNT sees NSTTYP `(`, parse a comma-separated list of EXPR.
  Each comma-separated item is an alternative. Build E_ALT node (or new E_SELECT).
- **IR node:** `E_SELECT` (new EKind) — n-ary, children = alternatives
- **Execution:** SM_SELECT instruction — try each child, return first success
- **No new syn table needed** — parsing is code logic in NSTTYP branch of ELEMNT

#### 2C. `[]` square-bracket subscripts as alias for `<>`

From SPITBOL manual §AppC p275:
> The array brackets [] may be used instead of <> if desired.
> Thus X[I,J] and X<I,J> are equivalent.

- **Current:** VARTB fires ARYTYP on `<`, nothing on `[`
- **VARTB chrs[] is authoritative** — cannot add `[` to it
- **Required:** New `VARTB_SPITBOL` table OR post-processing:
  - After ELEMTB, if next char is `[`, treat as array subscript
  - Cleanest: in `expr_prec_continue`, recognize `[` as postfix subscript operator
  - This also fixes bug #2 (postfix subscript on call result)

#### 2D. Multiple assignment `A = B = C + 1`

From SPITBOL manual §AppC p275:
> = is treated as a right-associative operator of lowest priority (0).
> Multiple assignments: A[J=J+1] = INPUT

- **Current:** `=` is handled structurally by CMPILE, not as an expression operator
- **Required:** In `expr_prec_continue`, treat `=` as right-assoc binary op at priority 0
- **No new syn table needed** — code logic in BINOP/expr_prec_continue

#### 2E. Embedded pattern match `A = (B ? C = D) + 1`

- Binary `?` inside an expression triggers an embedded match+replace
- Depends on 2A (binary `?`)

#### 2F. Semicolon `;` as statement separator (multiple statements per line)

From SPITBOL manual §Ch15 p188:
> The semicolon character may be used to place several statements on one line.
> Each semicolon terminates the current statement and behaves like a new column one.

- **Current:** `;` is EOSTYP in FRWDTB — treated as end-of-statement
- **Required:** At the top-level read loop, after a `;` is seen, continue parsing
  the same line buffer as a new statement
- **No new syn table needed** — loop logic in `parse_program()`

---

## Phase 2 Validation — crosscheck/ suite — 2026-04-05 (sprint 101)

**Result: 181/181 OK · 0 ERR · 0 HANG** ✅

All 181 `.sno` files in `corpus/crosscheck/` parse cleanly with zero errors.
This is the Phase 2 validation gate per MILESTONE plan. **PASSED.**

Broader sweeps:
- `corpus/programs/snobol4/` — 84/84 OK (baseline)
- `corpus/programs/gimpel/` — 143/145 OK, 2 ERR (both CSNOBOL4-confirmed), 0 HANG
  - PHRASES.sno: grammar data file, not SNOBOL4 source
  - TR.sno: unresolved `-INCLUDE "push.sno"` — CSNOBOL4 Error 30

---

## Phase 3 — UTF-8 / Unicode Support

### Design

SNOBOL4's string model is byte-oriented (each `stream()` call operates on bytes).
UTF-8 adds multi-byte code points. The syntab mechanism (256-byte chrs[] arrays)
operates on individual bytes — which is exactly right for UTF-8 prefix bytes.

**Key insight:** UTF-8 byte ranges are disjoint and well-defined:
- `0x00–0x7F`: ASCII (single-byte, handled by existing tables unchanged)
- `0xC0–0xDF`: 2-byte sequence lead byte
- `0xE0–0xEF`: 3-byte sequence lead byte
- `0xF0–0xF7`: 4-byte sequence lead byte
- `0x80–0xBF`: continuation bytes

**Strategy: Extension tables, not modification of existing tables.**

### Milestone 3A — UTF8TB: UTF-8 lead-byte dispatcher

New 256-byte table `UTF8TB`:
- `0x00–0x7F` → ACT_CONTIN (fast path, ASCII unchanged)
- `0x80–0xBF` → ACT_ERROR (bare continuation byte — malformed)
- `0xC0–0xDF` → ACT_GOTO → UTF8_2TB (2-byte sequence)
- `0xE0–0xEF` → ACT_GOTO → UTF8_3TB (3-byte sequence)
- `0xF0–0xF7` → ACT_GOTO → UTF8_4TB (4-byte sequence)
- `0xF8–0xFF` → ACT_ERROR (invalid in modern UTF-8)

### Milestone 3B — VARTB_U / ELEMTB_U: Unicode identifiers

SPITBOL identifiers are `[A-Za-z][A-Za-z0-9_]*`. For Unicode:
- Lead bytes of Unicode letters (U+0080+) should be VARTYP in ELEMTB_U
- Continuation bytes absorbed by VARTB_U
- New tables ELEMTB_U and VARTB_U extend the ASCII tables with UTF-8 awareness

### Milestone 3C — String primitives: SIZE, SUBSTR, REPLACE in UTF-8

- `SIZE(s)` → character count (not byte count)
- `SUBSTR(s,i,n)` → substring by character position
- Pattern primitives: `LEN(n)` matches n characters (not bytes)
- Implementation: runtime functions become UTF-8 aware; parser is unaffected

### Milestone 3D — QLITB_U: UTF-8 in quoted string literals

- Quoted strings `'...'` and `"..."` already pass bytes through unchanged
- SQLITB/DQLITB need no change for parsing
- Runtime storage: strings are byte arrays; UTF-8 is transparent
- Only SIZE/SUBSTR/pattern primitives need character-vs-byte awareness

---

## Milestone Summary Table

| Milestone | Description | Deps | Status |
|-----------|-------------|------|--------|
| **M-SN4PARSE-P1** | 84/84 standard SNOBOL4 parse | — | ⚠️ 76/84 |
| M-SN4PARSE-P1a | Unary+space fix (NBLKTB logic) | — | ✅ already works — was phantom |
| M-SN4PARSE-P1b | Postfix subscript `f()[i]` | — | ⬜ sprint 91 |
| M-SN4PARSE-P1c | Qize/io g_error lifecycle | — | ⬜ sprint 91 |
| **M-SN4PARSE-P2A** | Binary `?` pattern-match operator | P1 | ✅ sprint 94 |
| **M-SN4PARSE-P2B** | Alternative eval `(e1,e2,en)` | P1 | ✅ sprint 98-ext |
| **M-SN4PARSE-P2C** | `[]` subscript = `<>` + postfix subscript | P1 | ✅ sprint 96 |
| **M-SN4PARSE-P2D** | Multiple assignment `A=B=C+1` | P1 | ⬜ |
| M-SN4PARSE-P2E | Embedded match `(B?C=D)` | P2A+P2D | ⬜ |
| **M-SN4PARSE-P2F** | Semicolon multi-statement | P1 | ✅ sprint 92 |
| **M-SN4PARSE-P3A** | UTF8TB dispatch table | P2 | ⬜ |
| **M-SN4PARSE-P3B** | VARTB_U / ELEMTB_U Unicode idents | P3A | ⬜ |
| M-SN4PARSE-P3C | UTF-8 string primitives (runtime) | P3A | ⬜ |
| M-SN4PARSE-P3D | QLITB_U (transparent, low risk) | P3A | ⬜ |

---

## Implementation Notes

### Table authority rule
> **The 256-byte chrs[] array of every table that exists in CSNOBOL4 syn.c is
> authoritative and must not be modified.** All SPITBOL and Unicode extensions
> use NEW tables with their own chrs[] arrays. Linkage (`.go` pointers) from
> existing tables to new tables is permitted via `init_tables()` patching.

### BIOPTB extension for binary `?`
CSNOBOL4's BIOPTB does not include `?`. SPITBOL adds it at priority 1.
Since we cannot modify BIOPTB chrs[], the approach is:
- In `BINOP()`, after BIOPTB returns ST_ERROR for `?`, check if current char is `?`
  and return `BISNFN` (215) with priority 1 as a special case.
- Or: build `BIOPTB_EXT` that starts from BIOPTB and adds `?`.

### Sweep script
`one4all/csnobol4/dyn89_sweep.sh` — run against corpus/programs/snobol4/.
Output: one line per file, OK/ERR/HANG + first error message.

### Session start for next DYN session
```bash
cd /home/claude
cat .github/SCRIP-SM.md
tail -120 .github/SESSIONS_ARCHIVE.md
cat .github/MILESTONE-SN4PARSE-VALIDATE.md
gcc -O0 -g -Wall -o one4all/sno4parse one4all/src/frontend/snobol4/CMPILE.c
bash one4all/csnobol4/dyn89_sweep.sh   # baseline: ~73 OK / 11 ERR / 0 HANG
```


---

<!-- SOURCE: MILESTONE-SN4PARSE.md -->

# MILESTONE-SN4PARSE — SIL-Faithful SNOBOL4 Lexer/Parser

**Milestone ID:** M-SN4PARSE  
**Session:** DYN-84 · 2026-04-04  
**Authors:** Lon Jones Cherryholmes · Claude Sonnet 4.6  
**Gate:** `./sn4parse corpus/programs/gimpel/SQRT.sno` → zero errors, correct IR tree for all 13 statements  

---

## Why This Exists

scrip-interp's parser (`lex.c` / `parse.c`) has known fragility — the E_SEQ vs
E_CAT ambiguity, the label/subject confusion, deferred patterns not handled as
first-class EXPRESSION type. Before writing SM-LOWER we need a correct parser as
oracle.

SIL v311.sil IS the oracle. Its lexer/parser is a 3-layer 256-byte syntax table
system with `stream()` as the only scanner primitive. This milestone extracts that
system faithfully into a standalone C program that produces our IR tree.

When this milestone passes, we have:
1. A correct standalone parser usable as oracle against SPITBOL
2. A basis for replacing scrip-interp's lex.c/parse.c
3. Confirmed understanding of the 5 missing runtime types (EXPRESSION, CODE, NAME, + captures)

---

## Architecture — How SIL Streams

### The Three Scanning Layers

```
Layer 1 — Card type (CARDTB)
  stream(CARDTB): classifies entire line as NEW / CMT / CTL / CNT
  NEWTYP=1  → new statement (body follows)
  CMTTYP=2  → comment (* in col 1) → skip
  CTLTYP=3  → control card (- directive) → skip
  CNTTYP=4  → continuation (+ in col 1) → NEWCRD called; strips +, TEXTSP set to remainder; FORWRD restarts on new line (TRUE STREAMING — no pre-joining)

Layer 2 — Inter-field scanning (IBLKTB → FRWDTB)
  FORBLK: stream(IBLKTB) — skips leading blanks, stops at field boundary
  FORWRD: stream(FRWDTB) — finds next non-blank token boundary
  BRTYPE set after each call — the delimiter that ended the field:
    EQTYP=4  → = (assignment/replacement separator, consumed by AC_STOP)
    CLNTYP=5 → : (goto field, consumed)
    EOSTYP=6 → end of statement
    RPTYP    → ) consumed
    CMATYP   → , consumed
    NBTYP    → non-blank, NOT consumed (next char is start of token)

Layer 3 — Token content
  LBLTB → LBLXTB : label field (col 1, alphanumeric run)
  ELEMTB → VARTB / INTGTB → FLITB / SQLITB / DQLITB : element type
  BIOPTB → TBLKTB / STARTB : binary operator (STARTB disambiguates * vs **)
  UNOPTB : unary prefix operators
  GOTOTB → GOTSTB / GOTFTB : goto field type
```

### The stream() Function (verbatim from lib/stream.c)

```c
// Consumes chars from sp2, sets sp1=prefix, sp2=remainder, STYPE=put.
// AC_CONTIN: keep going (fast path: index==0)
// AC_STOP:   cp++; len--; then STOPSH (consume current char)
// AC_STOPSH: stop WITHOUT consuming (next char stays in sp2)
// AC_ERROR:  STYPE=0; return ST_ERROR immediately
// AC_GOTO:   tp = ap->go; continue in new table
```

**Critical:** AC_STOP consumes the delimiter. AC_STOPSH does not.
- `=`, `)`, `,`, `:` → AC_STOP (consumed — field separator gone before next ELEMNT)
- Non-blank token start → AC_STOPSH (not consumed — ELEMNT sees the char)
- EOS → AC_STOP (consumed)

### FRWDTB Action Ordering (verified from syn_init.h)

```
actions[0] = {EQTYP,  AC_STOP}    chrs['='=61] = 1
actions[1] = {RPTYP,  AC_STOP}    chrs[')'=41] = 2
actions[2] = {RBTYP,  AC_STOP}    chrs['>'=62] = 3
actions[3] = {CMATYP, AC_STOP}    chrs[','=44] = 4
actions[4] = {CLNTYP, AC_STOP}    chrs[':'=58] = 5
actions[5] = {EOSTYP, AC_STOP}    chrs[';'=59] = 6
actions[6] = {NBTYP,  AC_STOPSH}  chrs[other]  = 7
```

**Key trap:** chrs[] values are 1-based indices into actions[]. chrs[x]=N means
actions[N-1]. When rewriting actions[], the chrs[] values must remain verbatim
from syn.c — only the actions[] ordering changes.

### CMPILE — Statement Compiler (v311.sil line 1608)

```
stream(LBLTB)          → label (col 1 alphanumeric; STOPSH on blank/EOS)
FORBLK()               → skip to body; sets BRTYPE
if BRTYPE==EOSTYP      → label-only line
if BRTYPE==CLNTYP      → goto field only (no subject)
ELEMNT() → subject     
FORBLK()               → BRTYPE after subject
if BRTYPE==EQTYP       → CMPFRM: FORBLK(); replacement=EXPR()
if BRTYPE==CLNTYP      → CMPGO
if BRTYPE==EOSTYP      → bare invoke (done)
else                   → pattern=EXPR()
  FORBLK()
  if BRTYPE==EQTYP     → CMPASP: FORBLK(); replacement=EXPR()
  if BRTYPE==CLNTYP    → CMPGO
CMPGO:
  stream(GOTOTB)       → :S/:F/: type
  EXPR() for each label
```

### ELEMNT — Element Analysis (v311.sil line 1924)

```
loop: stream(UNOPTB)   → collect unary prefix operators
stream(ELEMTB)         → classify atom; GOTO chains to VARTB/INTGTB/SQLITB/DQLITB
dispatch on first char of XSP (not STYPE — GOTO chains change STYPE):
  digit  → ILITYP: text=XSP, ival=atoll; or FLITYP if INTGTB→FLITB
  letter → VARTYP/FNCTYP/ARYTYP from VARTB final STYPE
           FNCTYP: loop { arg=EXPR(); FORWRD(); break on RPTYP, cont on CMATYP }
           ARYTYP: loop { sub=EXPR(); FORWRD(); break on RBTYP, cont on CMATYP }
  quote  → QLITYP: strip delimiters from XSP
  '('    → NSTTYP: atom=EXPR() (recursive)
wrap atom in unary chain (innermost last)
BRTYPE = STYPE at end
```

### EXPR — Expression Compiler (v311.sil line 2093)

```
left = ELEMNT()
loop:
  op = BINOP() via stream(BIOPTB)
  if no op → break
  prec = op_prec(op); next_min = right_assoc ? prec : prec+1
  right = expr_prec(next_min)
  left = binop_node(op, left, right)
Juxtaposition (blank-separated elements):
  BINOP returns 0 on blank; need separate detection
  blank + element-start → E_CAT (value ctx) or E_SEQ (pattern ctx)
```

**Operator precedences (from SIL function descriptor CODE+2*DESCR field):**
```
&  BIAMFN  prec=1   (lowest)
|  ORFN    prec=2
+- ADDFN/SUBFN prec=3
*/ MPYFN/DIVFN prec=4
** EXPFN   prec=5   right-assoc
@  BIATFN  prec=6   right-assoc
.$ NAMFN/DOLFN prec=7 right-assoc (highest explicit binary)
   juxtaposition prec=10 (highest of all)
```

---

## What SIL Builds vs What We Build

SIL builds **object code** (a flat descriptor array for its interpreter).
We build an **IR tree** (EXPR_t / STMT_t for SM-LOWER).
The grammar is identical — only the output differs.

---

## Missing Runtime Types (found in DYN-84)

These must be added to DESCR_t / ir.h before SM-LOWER is correct:

| SIL Type | Code | Meaning | Status |
|----------|------|---------|--------|
| EXPRESSION | E=11 | Unevaluated expr (`*X`) — CODE pointer with type tag | ❌ missing |
| CODE | C=8 | Compiled code block (DEFINE/EVAL result) | ❌ missing |
| NAME | N=9 | Name descriptor (`.X` — pointer to variable cell) | ❌ missing |
| Conditional capture | XNME | Buffer on name list, commit at Phase 5 | ⚠️ partial |
| Immediate capture | XFNME | Assign live, push unravel entry | ⚠️ conflated with XNME |

**EXPVAL protocol (re-entrant eval for EXPRESSION type):**
```
save: OCBSCL, OCICL, PATBCL, PATICL, WPTR, XCL, YCL, TCL
      MAXLEN, LENFCL, PDLPTR, PDLHED, NAMICL, NHEDCL
      HEADSP, TSP, TXSP, XSP (specifiers)
set:  OCBSCL = expression code block; OCICL = DESCR (first slot)
run:  inner interpreter loop
restore: all saved state
```
SM dispatch loop must support this as a proper C stack frame (sm_interp() called
recursively with new SM_Program* and ip=0).

---

## sn4parse.c Current State

**File:** `one4all/src/frontend/snobol4/sn4parse.c`  
**Commit:** `59ada3d`  

**Working:**
- Card type dispatch (CARDTB): comments, directives, continuations skipped
- Label field (LBLTB): column-1 alphanumeric labels
- FORBLK/FORWRD: inter-field blank scanning
- ELEMNT: variables, integer/float literals, quoted strings, function calls with args, subscripts, unary operators
- EXPR: binary operators with precedence, right-associativity
- CMPILE: assignment (X=Y), bare invoke, :S/:F/: goto fields
- Corpus test: `LT(Y,0) :S(FRETURN)` → correct tree

**Remaining bugs (fix in order):**

**Bug 1: `**` exponent not parsed**
- BIOPTB `*` → STARTB → `*` → EXPFN/TBLKTB
- BINOP() saves/restores TEXTSP on ST_ERROR but STARTB succeeds
- Likely expr_prec_continue exits after first element before looping
- Fix: trace why BINOP returns 0 on `**`

**Bug 2: FORBLK error after `)` before tab+`:`**
- After `LT(Y,0)`, TEXTSP=`\t:S(RETURN)`
- FORBLK→IBLKTB: tab(9)→1→GOTO FRWDTB→`:`→CLNTYP AC_STOP → should work
- Actual: "FORBLK: scan error" — IBLKTB sees something unexpected
- Fix: add debug print inside FORBLK to see what char IBLKTB errors on

**Bug 3: Pattern field not reached**
- `SUBJECT PATTERN :S/:F` form (most SNOBOL4 statements)
- After subject ELEMNT, FORBLK returns NBTYP for non-blank
- CMPILE should call EXPR() for pattern — check branch condition

**Bug 4: Juxtaposition (blank-separated CAT/SEQ)**
- `'HELLO' LEN(5)` → should produce E_CAT (value) or E_SEQ (pattern)
- BINOP() returns 0 on blank; expr_prec_continue exits loop
- Fix: after BINOP fails, peek at TEXTSP — if non-blank element follows,
  build CAT/SEQ node in_pattern_ctx flag

---

## Gate Criteria

```bash
cd /home/claude
./sn4parse corpus/programs/gimpel/SQRT.sno 2>&1
# Expected: 13 statements, 0 errors
# Every statement shows correct subject/pattern/replacement/goto tree
# SQRT = Y ** 0.5 → replace: (EXPFN(**) (VAR Y) (FLIT 0.5))
# LT(Y,0) :S(FRETURN) → subject: (FNC LT (VAR Y) (ILIT 0)) :S(FRETURN)
```

Secondary gate — run full Gimpel suite:
```bash
for f in corpus/programs/gimpel/*.sno; do
  echo "=== $f ===" && timeout 5 ./sn4parse "$f" 2>&1 | grep "error\|=== [0-9]"
done
```

---

## Relationship to DYN-82 (SM_Program)

sn4parse.c is NOT a replacement for scrip-interp's parser. It is:
1. **Oracle** — run both parsers on same input, diff IR trees
2. **Documentation** — the grammar is now executable
3. **Precursor** — when sn4parse passes corpus, port its ELEMNT/EXPR/CMPILE
   into scrip-interp replacing lex.c/parse.c, then SM-LOWER can be written
   on a correct foundation

**DYN-82 sequence (unchanged):**
```
M-SN4PARSE (this) → correct parser
  → SM_Instr + SM_Program structs
  → SM-LOWER (IR → SM_Program)
  → sm_interp dispatch loop
  → replace tree-walker in scrip-interp.c
  → corpus ≥177p/0f → M-DYN-SM-INTERP
```

---

*Written: DYN-84 session 2026-04-04*  
*File: MILESTONE-SN4PARSE.md*


---

<!-- SOURCE: MILESTONE-SNO2SC.md -->

# MILESTONE-SNO2SC.md — SNOBOL4 → Snocone Conversion Program

**Owner:** SC session · **Prefix:** `SNO2SC` · **Trigger:** "sno2sc" or "snobol4 to snocone"

---

## §GOAL

Build a library of idiomatic Snocone programs converted from:
1. **Gimpel** — classic SNOBOL4 programs from Gimpel's *Algorithms in SNOBOL4*
2. **AI-SNOBOL** — AI/NLP programs from the AI-SNOBOL corpus
3. **beauty.sno** — the full beauty compiler (final milestone, depends on all beauty-sc subsystems)

Flagship programs:
- **claws5.sc** — CLAWS part-of-speech tagger (corpus linguistic tool)
- **treebank.sc** — Penn Treebank-style parser (wholesale POS(0)...RPOS(0) pattern approach)

**Final target:** `beauty.sc` compiles itself via `scrip-cc -sc -asm`.

---

## §CONVERSION PHILOSOPHY

Snocone is NOT a line-for-line transliteration of SNOBOL4.
Write idiomatic Snocone — use `while`, `if`, `procedure`, `struct`.

| SNOBOL4 idiom | Snocone idiom |
|---------------|---------------|
| Goto-based loops | `while (1) { ...; if (cond) break; }` |
| `DEFINE + label + :(RETURN)` | `procedure f(a,b) { ... return; }` |
| `DATA('t(f1,f2)')` | `struct t { f1, f2 }` |
| `val = COND(x,y) expr` | `if (COND(x,y)) { val = expr; }` |
| `str POS(0) PAT . cap =` (subject replace) | `SUBSTR` index walk — see NOTE below |
| `+expr` (numeric coerce) | drop it — integers are integers |
| `~(strval)` empty check | `GT(i, SIZE(arr))` or `IDENT(x,'')` carefully |
| `fn = .dummy; nreturn` | keep — correct SPITBOL idiom (deref to '' on call) |
| `epsilon . *fn()` | same in Snocone — works natively |

**NOTE on wholesale pattern approach for treebank.sc:**
SNOBOL4's `str POS(0) PAT RPOS(0) . result` — match full string.
In Snocone: `if (str ? (POS(0) && PAT && RPOS(0) . result)) { ... }`
The `.` capture in pattern context works. `&&` = sequence concat.
Avoid subject replacement (`= rhs`) — use SUBSTR + SIZE walk instead.

---

## §MILESTONE LADDER — M-SNO2SC-*

| ID | Program | Source | Difficulty | Status |
|----|---------|--------|------------|--------|
| **M-SNO2SC-STRINGS** | strings.sc — string utility library | new | easy | ❌ |
| **M-SNO2SC-ARITH** | arith.sc — number utilities | Gimpel | easy | ❌ |
| **M-SNO2SC-ROMAN** | roman.sc — Roman numeral converter | corpus/roman.sno | easy | ❌ |
| **M-SNO2SC-WCOUNT** | wordcount.sc — word counter | corpus/wordcount.sno | trivial | ❌ |
| **M-SNO2SC-TREEBANK** | treebank.sc — Penn Treebank parser (position threading) | corpus/treebank.sno | medium | ❌ |
| **M-SNO2SC-CLAWS5** | claws5.sc — CLAWS5 POS tagger (ARBNO wholesale) | corpus/claws5.sno | medium | ❌ |
| **M-SNO2SC-IO** | io.sc — INPUT/OUTPUT OPSYN | inc/io.sno | hard | ❌ |
| **M-SNO2SC-GEN** | Gen.sc — code generation output | inc/Gen.sno | hard | ❌ |
| **M-SNO2SC-QIZE** | Qize.sc — quoting (needs subj replacement) | inc/Qize.sno | hard | ❌ |
| **M-SNO2SC-TDUMP** | TDump.sc — tree pretty-printer | inc/TDump.sno | hard | ❌ |
| **M-SNO2SC-BEAUTY** | beauty.sc — full port | demo/beauty.sno | very hard | ❌ |

**Tier 1 (no blockers):** STRINGS → ARITH → ROMAN → WCOUNT
**Tier 2 (one non-trivial conversion):** TREEBANK → CLAWS5
**Tier 3 (needs dynamic / io / Gen infrastructure):** IO → GEN → QIZE → TDUMP → BEAUTY

---

## §TIER 1 DETAILS

### strings.sc — 8 utility functions
All pure value operations, no subject replacement needed:
```snocone
procedure Reverse(s, i, n, out)   // SUBSTR walk backwards
procedure Trim(s)                 // strip leading/trailing spaces
procedure TrimLeft(s, i, n)
procedure TrimRight(s, i, n)
procedure Split(s, sep, arr, i, n, start, pos)  // → ARRAY
procedure Join(arr, sep, i, n, out)              // ← ARRAY
procedure StartsWith(s, prefix)   // IDENT(SUBSTR(s,1,SIZE(prefix)), prefix)
procedure EndsWith(s, suffix, n, sn)
```

### arith.sc — 5 number utilities
All iterative (while loops), no SNOBOL4 idioms needed:
```snocone
procedure Fibonacci(n, a, b, t, i)   // iterative
procedure Sieve(n, arr, i, j)        // TABLE as bit array
procedure GCD(a, b, t)               // Euclidean: while DIFFER(b) { t=b; b=REMDR(a,b); a=t; }
procedure Factorial(n, acc, i)       // iterative
procedure IsPrime(n, i)              // trial division to SQRT(n)
```

### roman.sc
Original uses `N RPOS(1) LEN(1) . T =` (subject replacement to strip last digit).
Snocone rewrite: pass index, extract with SUBSTR:
```snocone
procedure Roman(n, i, len, digit, t)
    // walk digits right-to-left: i from SIZE(n) down to 1
    // for each SUBSTR(n, i, 1) look up in '0,1I,2II,...,9IX,'
    // prefix the roman numeral, shift place (I→X→C→M via REPLACE)
```

### wordcount.sc
Original: `LINE ? WPAT =` (consumes match from LINE via subject replacement).
Snocone rewrite: scan by index looking for word boundaries:
```snocone
// Walk line char by char, detect SPAN(WORD) runs
// Increment counter per run
```

---

## §TIER 2 DETAILS

### treebank.sc — Position Threading Pattern
**Key insight:** Instead of mutating `buf` with subject replacement, thread an explicit
position index through all recursive calls. This is MORE idiomatic Snocone and shows
the design difference clearly.

SNOBOL4 `group()` mutates `buf` globally (`:S(RETURN)` after `buf POS(0) ... =`).
Snocone `group(pos)` returns the NEW position — pure functional threading.

```snocone
procedure group(pos, tag, wrd, newpos) {
    // match '(' at pos → pos+1
    if (~(SUBSTR(buf, pos, 1) :: '(')) { freturn; }
    pos = pos + 1;
    // skip whitespace
    while (pos <= SIZE(buf) && SUBSTR(buf,pos,1) ? SPAN(' ' && nl)) { pos = pos + 1; }
    // match word (tag)
    // ... recursive descent, return updated pos
    group = pos;
    return;
}
```

### claws5.sc — Wholesale ARBNO Pattern
The original pattern compiles to one giant ARBNO expression.
In Snocone this translates almost 1:1:
```snocone
claws_info = POS(0) && *do_mem_init() &&
    ARBNO(
        (SPAN(digits) . num && '_CRD :_PUN' && *do_new_sent()
        | (NOTANY('_') && BREAK('_')) . wrd && '_' &&
          (ANY(UCASE) && SPAN(digits && UCASE)) . tag &&
          *do_add_tok())
        && ' ')
    && RPOS(0);
```
Risk: nested alternation through `ARBNO` — test progressively.

---

## §CLAWS5 NOTES

CLAWS5 is a rule-based POS tagger using:
- Suffix rules: `word POS(0) BREAK('') RPOS(N) . suffix` → tag lookup
- Bigram/trigram context rules
- Disambiguation tables

Snocone approach:
- Suffix patterns: `word ? (RTAB(N) . suffix)` — capture last N chars
- Tables as `TABLE()` — same as SNOBOL4
- Procedure per rule class: `procedure ApplySuffixRules(word, tag) { ... }`
- Context window: pass prev/next tokens as args

---

## §TREEBANK NOTES

The **wholesale pattern** approach in treebank.sno:
```snobol4
line  POS(0) '(' tag ' ' word ')' RPOS(0)
```
This matches the entire string at once — no loops, no subject replacement.
In Snocone:
```snocone
if (line ? (POS(0) && '(' && ANY(alpha) . tag && ' ' && REM . word_and_rest)) {
    // process
}
```
Key: `&&` for pattern sequence, `|` for alternation, `.` for capture.
Avoid nested alternation through function args (known stack underflow — SC-16 open issue).

---

## §LIBRARY LAYOUT

```
corpus/programs/snocone/library/
  gimpel/
    fibonacci.sc
    sieve.sc
    quicksort.sc
    bst.sc
    expr_eval.sc
  ai/
    tokenizer.sc
    ner.sc
    rd_parser.sc
  nlp/
    claws5.sc
    treebank.sc
one4all/test/sno2sc/
  gimpel/   ← driver.sc + driver.ref per program
  ai/
  nlp/
```

---

## §BUILD

```bash
FRONTEND=snocone BACKEND=x64 TOKEN=TOKEN_SEE_LON bash /home/claude/.github/SESSION_SETUP.sh
cd /home/claude/one4all
# Run a conversion test:
CORPUS=/home/claude/corpus bash test/sno2sc/run_sno2sc_suite.sh gimpel/fibonacci
# Gate:
CORPUS=/home/claude/corpus bash test/run_invariants.sh snobol4_x86 snocone_x86
```

---

## §FIRST ACTION — SC-17

**Before anything else:** fix `uses_nreturn` in `emit_x64.c`.

Root cause: second-pass scanner resets `cur_np = NULL` on ANY non-function label,
so NRETURN gotos inside `if(){}/while(){}` blocks are missed.
Fix: only reset `cur_np` when hitting `fname.END` (snocone proc terminator) or
a new function-entry label. Internal labels keep `cur_np`.
See SESSIONS_ARCHIVE SC-16 for full analysis and the two-line fix location.

Then:
1. Verify `assign` beauty-sc driver test 4 passes
2. Run full beauty-sc suite → 11/11
3. Commit `emit_x64.c` fix + `emit_x64_snocone.c` unary PERIOD fix
4. Start M-SNO2SC-GIMPEL01 (fibonacci.sc — trivial warm-up)

