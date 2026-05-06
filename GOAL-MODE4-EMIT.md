# GOAL-MODE4-EMIT.md — Mode 4 x86 backend (`--jit-emit --x64`)

**Repos:** one4all (primary)
**Branch:** TBD (likely `main` once GOAL-CHUNKS M1 is closed)
**Tracker:** brand-new sub-goal carved out of GOAL-CHUNKS.md
(session #62, 2026-05-05). Replaces the placeholder name
`GOAL-MODE4-EMIT-X64-SNO.md` referenced in GOAL-CHUNKS Step 8.

**Done when:** `scrip --jit-emit --x64 file.sno` and `scrip
--jit-emit --x64 file.sc` produce a standalone asm/binary that,
when executed via `./prog < input`, produces output identical to
`scrip --sm-run file.sno < input` (and similarly for `.sc`). The
emitted executable links against `libscrip_rt.so` — a runtime
support library carrying the pattern matcher, NV table, builtins,
and (post-Step 19) the BB broker plus generator/Prolog
backtracking machinery. After Step 19 closes, the same scope
extends to Icon, Raku, Prolog, Rebus.

---

## Why this file exists

GOAL-CHUNKS.md Step 8 (M2) and Step 19 (M5) both target the x86
mode-4 emitter. Step 8 is the SNOBOL4+Snocone-only initial
landing; Step 19 is the extension to all six frontends after the
SM_PUSH_EXPR delete. These belong in one file because:

- They share the same emission pipeline (`sm_codegen.c` →
  asm/binary).
- They share the same `libscrip_rt.so` build/link/package work.
- The SM-opcode coverage grows monotonically — Step 8's emitter
  handles the SNO/Snocone subset; Step 19 extends to the full
  opcode set including `SM_SUSPEND` / `SM_RESUME` / per-frontend
  builtin shims.
- Splitting them would force duplicate "what does an emitted
  binary look like" sections.

GOAL-CHUNKS.md keeps Steps 8 and 19 as pointers — this file owns
the destination.

---

## Architectural target

**Pipeline:**

```
file.sno  ──► [parser] ──► IR ──► [sm_lower] ──► SM_Program
                                                     │
                                                     ▼
                                          [sm_codegen --x64]
                                                     │
                                                     ▼
                                              file.s (asm) or
                                              file.o (object)
                                                     │
                                                     ▼
                                          ld + libscrip_rt.so
                                                     │
                                                     ▼
                                                file (ELF)
```

**Runtime support library — `libscrip_rt.so`.**

The emitted executable contains compiled SM chunks (one per
function/procedure/predicate/deferred body) plus a `main()` that
calls into the runtime to set up the SM dispatch state and drive
the program-level entry chunk. Everything that needs language
semantics — pattern matcher, NV table lookup, &-keyword access,
DATATYPE registration, conversions, I/O, GC, generator BB pump
(post-Step 19), Prolog backtracking (post-Step 19) — lives in
`libscrip_rt.so`. The emitted binary contains **no EXPR_t
walker**. That is the whole point.

**Symbol surface.** The emitter produces calls into a stable C
ABI exported by `libscrip_rt.so`. The full surface is enumerated
in this goal's per-rung table (SCRIP_RT-1 onward). At minimum it
includes:

- `scrip_rt_init` / `scrip_rt_finalize`
- `scrip_rt_push` / `scrip_rt_pop` / `scrip_rt_peek`
- `scrip_rt_call_chunk(int entry_pc, int arity)`
- `scrip_rt_pat_match(...)` — pattern matcher entry
- `scrip_rt_nv_lookup` / `scrip_rt_nv_store`
- `scrip_rt_builtin_<name>` for each SCRIP builtin
- `scrip_rt_bb_drive(int entry_pc)` — added in Step 19 (M5)
- `scrip_rt_pl_unify` / `scrip_rt_pl_choice` — added in Step 19

**Entry chunk.** The top-level program is itself a chunk
(post-CHUNKS Step 17). The emitted `main()` is roughly:

```c
int main(int argc, char **argv) {
    scrip_rt_init(argc, argv);
    scrip_rt_call_chunk(PROGRAM_ENTRY_PC, 0);
    return scrip_rt_finalize();
}
```

`PROGRAM_ENTRY_PC` is a constant baked at emit time, since the
SM_Program is the emitted binary.

---

## Prerequisite

⛔ **Do not start this goal until GOAL-CHUNKS.md M1 (Steps 1–7)
is closed.** The mode-4 emitter cannot exist while any SM-mode
runtime path still walks EXPR_t — there is nowhere for the
emitted binary to call into. Step 8 begins as soon as M1 ships.

For the M5 extension (Step 19 of GOAL-CHUNKS): wait until
GOAL-CHUNKS M4 (Steps 12–18, ending with the `SM_PUSH_EXPR`
delete) is closed. At that point the lowerer produces pure SM
for all frontends, and the mode-4 codegen extends to handle the
full opcode set.

---

## Migration strategy

**Sequential rungs, one per session.** Each rung leaves the
emitter green for everything it claimed in previous rungs, plus
its newly-claimed scope. No long-lived feature flag — the rung
that adds a frontend's coverage also flips the gate to require
that frontend pass.

**M2 phase (initial landing):**

- Scope: SNOBOL4 + Snocone only.
- Opcode coverage: everything `sm_lower` emits for SNOBOL4 +
  Snocone after CHUNKS M1, including `SM_PUSH_CHUNK` /
  `SM_CALL_CHUNK`. **Excludes** `SM_SUSPEND` / `SM_RESUME` (those
  don't exist yet at M1 close — added in CHUNKS Step 14).
- `libscrip_rt.so` v1: pattern matcher, NV table, scan builtins,
  string/numeric builtins, I/O, GC.
- Gate: `--jit-emit --x64 beauty.sno` produces a binary that
  passes the same Beauty oracle as `--sm-run beauty.sno` (the
  byte-identical SPITBOL crosscheck). `--jit-emit --x64 beauty.sc`
  produces a binary whose output matches `--sm-run beauty.sc`.

**M5 phase (extension):**

- Scope: Icon, Raku, Prolog, Rebus.
- Opcode coverage adds: `SM_SUSPEND`, `SM_RESUME`, the per-kind
  generator chunks landed in CHUNKS M4 Step 15, the Prolog
  clause-chunk shapes landed in CHUNKS M4 Step 16.
- `libscrip_rt.so` v2: extends with BB broker (now a runtime
  library, not a driver-time component), Icon coexpression
  machinery, Prolog trail/unify/choice-point, Raku-specific
  builtins, Rebus runtime.
- Gate: emitted binary passes smoke for each frontend and a
  curated corpus subset (smoke_icon 5/5, smoke_prolog 5/5,
  smoke_raku 5/5, smoke_rebus 4/4) plus existing Beauty/Snocone.

**Per-rung gates** (apply to every step unless the step says
otherwise):

```
smoke ×{coverage} (snobol4 7/7, snocone 5/5 from M2; +icon/raku/
                  prolog/rebus once their rungs land)
isolation gate PASS  (unchanged from CHUNKS)
emitted-binary smoke: ./prog < input matches scrip --sm-run prog
                      < input for every program in the rung's
                      coverage set
libscrip_rt.so unit tests PASS
```

---


---

## Architecture — Two Separate Emitters (settled session #67, 2026-05-06)

Archaeology of `.github/archive/` (BB-GEN-X86-TEXT.md, BB-GRAPH.md,
EMITTER-COMMON.md, EMITTER-X86.md, EMITTER-X86-DEEP.md, BB-GEN-LANG.md,
SESSION-snobol4-x64.md, SCRIP-SM.md) established two completely
separate concerns that must NOT be conflated:

### 1. SM opcodes -> straight-line x86 (the SM emitter)

The SM instruction set is the universal IR. Every backend (x86, JVM,
.NET, JS, WASM) walks the same SM_Program array with one switch, one
case per opcode. For text-asm output, each opcode group maps to ONE
named GNU-as macro. The macro expands to actual inline x86 -- NOT a
PLT call into libscrip_rt for every tiny op. Context: a growing text
buffer for the current statement proc body. Three-column SNOBOL4 layout
throughout:

  .LpcN:    SM_MACRO_NAME arg1, arg2    ; goto comment or jmp label

One macro file `sm_macros.s` (parallel to the proven `snobol4_asm.mac`,
151 macros) defines one macro per SM opcode group. `sm_codegen_x64_emit.c`
calls into it. `libscrip_rt.so` is still the right boundary for things
that truly need runtime support: NV table, pattern matcher, GC. Inline
arithmetic, push/pop, and control flow bake directly.

### 2. BB boxes -> one proc per box (the BB box emitter)

The BB graph is NOT a sequence of SM opcodes. It is a directed graph
of box nodes. Each box has exactly four ports:

  alpha (a) -- try (entry: forward attempt)
  beta  (b) -- retry (entry: backtrack)
  gamma (g) -- success exit (drives next box's alpha)
  omega (o) -- failure exit (drives enclosing beta)

**The Law (from BB-GEN-X86-TEXT.md):** One NASM/GNU-as proc per box.
Each named pattern or primitive box = one labeled proc with local labels
`.alpha`, `.beta`, `.gamma`, `.omega`. Sub-box ports become local labels
within the enclosing proc. Emitted ONE BOX AT A TIME.

Three-column law inside every box proc:

  LABEL:              ACTION (macro + params)          GOTO (jmp target)

The proven precedent: `bb_emit.c` TEXT mode + `snobol4_asm.mac` 151 macros,
106/106 vs SPITBOL oracle. The new mode-4 emitter inherits this model
directly. `emit_bb_box()` is a clearly separate function from the SM
straight-line emitter.

### Separation in sm_codegen_x64_emit.c

  emit_sm_instr()    -- straight-line SM opcodes (push/pop/arith/control)
                        one emit_sm_* fn per opcode group
                        writes macro calls in three-column format
                        inline x86 via sm_macros.s, not PLT calls

  emit_bb_box()      -- called once per SM_PAT_* instruction
                        emits one proc with .alpha/.beta/.gamma/.omega
                        macro call per port body
                        jmp gotos connect ports across boxes

### Multi-backend portability

For JVM: SM opcodes -> iload/iadd/etc; BB boxes -> method-per-box.
For .NET: SM opcodes -> ldc/add/etc; BB boxes -> delegate-per-box.
For JS: SM opcodes -> function calls; BB boxes -> closure-per-box.
For WASM: SM opcodes -> i64.add/etc; BB boxes -> function-per-box.
All share the same alpha/beta/gamma/omega four-port protocol.

---

---

## Demo Programs and Tracked Artifacts (settled session #67, 2026-05-06)

Every session that changes the mode-4 emitter regenerates and commits
the x64 artifact set. Git history is the archive -- no session-numbered
copies. `git log -p artifacts/x64/samples/roman.s` shows full evolution.

### Source programs (demo/snobol4/)

These four SNOBOL4 programs are the tracked artifact generators. They
were in one4all before M-G0-CORPUS-AUDIT (commit f9fbf15f) deleted all
source programs. Restored to demo/snobol4/ in session #67.

| File | Purpose | Why tracked |
|------|---------|-------------|
| roman.sno | ROMAN(N) recursive numeral converter | Exercises recursive DEFINE, REPLACE, BREAK, pattern match |
| wordcount.sno | Word tokenizer via BREAK/SPAN | Exercises BREAK/SPAN pattern primitives, INPUT loop |
| claws5.sno | CLAWS5 POS-tag corpus tokenizer | Corpus-scale: exercises ARBNO, complex patterns |
| treebank.sno | Penn Treebank S-expression parser | Exercises nested patterns, stack operations |

Primary artifact: `beauty.sno` from corpus (4700+ SM instructions,
oracle gate at EM-7).

### Artifact locations (artifacts/x64/)

    artifacts/x64/beauty_prog.s     PRIMARY -- changes most; visual overview
    artifacts/x64/samples/roman.s   demo programs -- easy to inspect
    artifacts/x64/samples/wordcount.s
    artifacts/x64/samples/claws5.s
    artifacts/x64/samples/treebank.s
    artifacts/x64/README.md         regen commands + milestone checks

### Regen protocol (run end of every session touching the emitter)

```bash
cd /home/claude/one4all
BEAUTY=/home/claude/corpus/programs/snobol4/demo/beauty.sno
./scrip --jit-emit --x64 $BEAUTY > artifacts/x64/beauty_prog.s
./scrip --jit-emit --x64 demo/snobol4/roman.sno    > artifacts/x64/samples/roman.s
./scrip --jit-emit --x64 demo/snobol4/wordcount.sno > artifacts/x64/samples/wordcount.s
./scrip --jit-emit --x64 demo/snobol4/claws5.sno   > artifacts/x64/samples/claws5.s
./scrip --jit-emit --x64 demo/snobol4/treebank.sno > artifacts/x64/samples/treebank.s
git diff --stat artifacts/x64/
# Commit if changed
git add artifacts/x64/ demo/snobol4/ && git commit -m "x64 artifacts: regen <rung>"
```

### What to look for in the artifacts

Scan `roman.s` after each rung to see emitter progress:
- UNHANDLED_OP lines = opcodes not yet baked
- SM_ADD / SM_MUL macro calls = arithmetic baked (EM-3+)
- BB box proc labels (.alpha/.beta/.gamma/.omega) = pattern boxes baked (EM-6+)
- Zero UNHANDLED_OP = EM-7 gate (beauty oracle)

---
## Steps (in order — execute one per session, sequentially)

### M2 phase — SNOBOL4 + Snocone only

- [x] **Step EM-1 — Driver wiring + `libscrip_rt.so` skeleton.**
  In `scrip.c`, add `--jit-emit --x64` to the mode parser
  (currently lines ~145–148 parse three modes plus
  `--monitor`). New mode: walks IR → SM_Program as in `--sm-run`,
  but instead of calling the SM dispatch loop, hands the
  SM_Program to a new `sm_codegen_x64_emit(SM_Program*, FILE*
  out)` entry. Stub that entry to write a literal-zero asm file
  and exit 0; this rung is wiring only, not codegen.
  Build `libscrip_rt.so` skeleton: empty C file, exports
  `scrip_rt_init` / `scrip_rt_finalize` as no-ops, plus the
  Makefile target `out/libscrip_rt.so`. Link the literal-zero
  asm against it; verify the resulting binary loads and exits
  0. Standard gates green.

- [x] **Step EM-2 — SM_NOP + SM_HALT + SM_PUSH_INT codegen.**
  Smallest non-trivial program (`OUTPUT = 42` in SNOBOL4 is too
  big — pick `&OUTPUT = 0` or a synthetic SM program with three
  ops). Emit x86-64 asm for `SM_PUSH_INT`, `SM_HALT`, `SM_NOP`.
  Add `scrip_rt_push_int(int64_t)` and `scrip_rt_halt(int rc)`
  to `libscrip_rt.so`. Verify emitted binary runs and exits with
  the expected rc. This rung establishes the codegen calling
  convention (which regs hold the SM stack pointer / pc / state
  ptr; how stack frames are laid out for `scrip_rt_*` calls).

- [x] **Step EM-3 — SM stack ops (PUSH/POP/DUP/SWAP) + arithmetic.**
  Cover `SM_PUSH_STR`, `SM_PUSH_VAR`, `SM_POP`, `SM_DUP`,
  `SM_SWAP`, `SM_ADD` / `SM_SUB` / `SM_MUL` / `SM_DIV` /
  `SM_MOD`. `libscrip_rt.so` v0.3 gains the NV table + numeric
  builtins. Gate: a hand-written SM_Program that computes
  `(2 + 3) * 4` and exits with that as rc, run via the
  emitter, returns 20.

- [ ] **Step EM-4 — Control flow: SM_JUMP, SM_JUMPF, SM_JUMPT,
  SM_LABEL.**  Direct x86 jumps to baked-at-emit-time pc values.
  Labels resolve at emit time — no runtime branch table needed.
  Gate: SM program with a forward jump and a conditional
  backward jump runs correctly.

- [ ] **Step EM-5 — SM_PUSH_CHUNK / SM_CALL_CHUNK / SM_RETURN.**
  This is the core of the chunks design. `SM_PUSH_CHUNK` emits
  a constant push of `(entry_pc, arity)`. `SM_CALL_CHUNK` is a
  baked direct call to the chunk's emit-time address (no
  dispatch loop). `SM_RETURN` is a standard ret. The
  `libscrip_rt.so` `scrip_rt_call_chunk` becomes thin — it
  exists for chunks called by descriptor (e.g., from pattern
  matcher), not for direct chunk-to-chunk calls.
  Gate: SM program with two chunks calling each other returns
  the right value.

- [ ] **Step EM-6 — Pattern matcher integration.**  The pattern
  matcher in `libscrip_rt.so` (lifted from
  `src/runtime/interp/scan_builtins.c` and
  `src/frontend/snobol4/snobol4_pattern.c`) is invoked via
  `scrip_rt_pat_match(DESCR_t subject, DESCR_t pattern, ...)`.
  When the matcher needs to invoke a deferred chunk (the
  pattern's `*expr` arg, a CONVE result, etc.), it calls
  through `scrip_rt_call_chunk(entry_pc, arity)`. Since
  emit-time pc and runtime pc are the same in mode 4
  (no dispatch loop), the call lands directly. Gate: a SNOBOL4
  program that uses `SPAN`, `BREAK`, `LEN`, `*expr`, and a
  pattern with `$` capture compiles and runs.

- [ ] **Step EM-7 — `--jit-emit --x64 beauty.sno` passes oracle.**
  The full Beauty crosscheck (md5
  `abfd19a7a834484a96e824851caee159`, 646 lines) on the emitted
  binary. This is the M2-SNOBOL4 milestone gate: emitted binary
  produces byte-identical output to SPITBOL.

- [ ] **Step EM-8 — `--jit-emit --x64 beauty.sc` + smoke_snocone.**
  Snocone rides the SNOBOL4 lowering path. This rung verifies
  that's true at the codegen level too — the same emitter, no
  Snocone-specific work, runs Snocone correctly. Gate:
  smoke_snocone 5/5 on emitted binaries.

- [ ] **Step EM-9 — M2 milestone close: package + docs.**
  Document the `libscrip_rt.so` ABI (every exported symbol, its
  C signature, what it does, what it can fail with). Document
  the emit-time invariants (which SM opcodes are baked-direct
  vs `scrip_rt_*` calls). Add a Makefile target
  `make jit-emit-test` that runs the M2 gate. Update
  GOAL-CHUNKS.md Step 8 to `[x]`. Update PLAN.md current step.
  This is a natural pause: M2 ships before M3 begins (M3 is
  parallelizable) and before CHUNKS M4 begins.

### M5 phase — extends to all six frontends

⛔ Do not begin until CHUNKS M4 (Steps 12–18) is closed.

- [ ] **Step EM-10 — SM_SUSPEND / SM_RESUME codegen + BB broker
  in `libscrip_rt.so`.**  `SM_SUSPEND` saves the chunk's local
  SM state (pc, value-stack snapshot, frame pointer) into a
  coexpression record; `SM_RESUME` restores. The BB broker
  becomes a `libscrip_rt.so` API:
  `scrip_rt_bb_drive(int entry_pc) → DESCR_t`. Each tick
  resumes a suspended chunk to its next SUSPEND or RETURN.
  Gate: hand-written SM program that yields three values via
  SUSPEND, driven by `scrip_rt_bb_drive` from a parent chunk,
  returns the right values.

- [ ] **Step EM-11 — Icon main + smoke_icon.**  CHUNKS M4 Step 12
  has already lowered Icon main() as a chunk. This rung verifies
  the emitter handles it. Gate: smoke_icon 5/5 on emitted
  binaries; emitted Icon corpus subset matches `--sm-run`.

- [ ] **Step EM-12 — Raku CASE + smoke_raku.**  CHUNKS M4 Step 13
  has already lowered CASE as chunk-per-arm. This rung is
  emitter coverage. Gate: smoke_raku 5/5.

- [ ] **Step EM-13 — Icon generators.**  Each generator kind
  migrated in CHUNKS M4 Step 15 needs emitter coverage. Bundle
  per the same kind-bundle the lowering used. Gate: Icon
  corpus subset for the rung's kinds matches `--sm-run`.

- [ ] **Step EM-14 — Prolog clauses.**  CHUNKS M4 Step 16's
  per-kind clause lowerings + trail/unify/choice machinery in
  `libscrip_rt.so` v2. Gate: smoke_prolog 5/5; Prolog corpus
  subset matches.

- [ ] **Step EM-15 — Rebus.**  Rebus uses the Snocone lowering
  path almost entirely; this rung is mostly a gate rerun. Gate:
  smoke_rebus 4/4.

- [ ] **Step EM-16 — M5 milestone close: full-frontend gate.**
  Run the full mode-4 x86 gate set on every frontend. Update
  GOAL-CHUNKS.md Step 19 to `[x]`. Update PLAN.md. The x86 cell
  in PLAN.md's Milestone-3 matrix flips green for all six
  language rows.

---

## Closed steps

**Step EM-2** — SM_NOP + SM_HALT + SM_PUSH_INT codegen.
- Per-instruction dispatch loop in `sm_codegen_x64_emit.c`. Each
  emitted block carries a `.LpcN:` label for future control-flow
  rungs (EM-4) to target. Two opcodes baked: `SM_HALT` (pops int
  from SM stack via `scrip_rt_pop_int`, passes to `scrip_rt_halt`)
  and `SM_PUSH_LIT_I` (movabs literal, calls `scrip_rt_push_int`).
  Every other opcode emits `UNHANDLED_OP` markers + a runtime call
  to `scrip_rt_unhandled_op` — fail-fast rather than silently-wrong.
- Calling-convention block in the emitter file header documents the
  SysV AMD64 contract and reserves `r12` (SM value-stack ptr) and
  `r13` (SM_State ptr) as callee-saved for future baked-direct
  opcodes (EM-3+).  Until EM-3 lands these regs are unused; the
  prologue does not yet save/restore them.
- libscrip_rt.so ABI grew from 2 → 6 symbols: added `scrip_rt_push_int`,
  `scrip_rt_pop_int`, `scrip_rt_halt`, `scrip_rt_unhandled_op`. EM-1's
  `scrip_rt_finalize` extended (backward-compatible) to surface the
  rc most recently passed to halt (or 0 if halt never called).
  Internal SM value stack is fixed-capacity int64 (256 entries; EM-3
  may grow / become typed).
- Two **honest deviations** from the rung text, documented in code:
  - `SM_NOP` is not in the `sm_opcode_t` enum. The rung text was
    aspirational. EM-2 covers `SM_HALT` and `SM_PUSH_LIT_I` only;
    no enum extensions made. Documented in
    `sm_codegen_x64_emit.c` opcode-coverage block.
  - `scrip_rt_pop_int` was originally an EM-3 ABI symbol (full
    PUSH/POP/DUP/SWAP). Pulled forward by one rung because
    `SM_HALT`'s codegen needs it: mode 2's `SM_HALT` returns 0
    unconditionally, so without a stack-pop the EM-2 gate could
    not distinguish a successful run from EM-1's literal-zero
    scaffold. Documented in `scrip_rt.h` and `emit_op_halt()`.
- Test harness `out/sm_codegen_x64_emit_test` (new): C standalone
  that builds an in-memory 3-op SM_Program (`PUSH_LIT_I 42` +
  `HALT`) and emits asm. Used by the gate.
- Gate `scripts/test_smoke_jit_emit_x64.sh` consolidated (EM-1's
  separate gate dropped — its "binary exits 0" check was an
  artifact of the literal-zero scaffold). Four sub-tests:
  PUSH_LIT_I+HALT (rc=42 verified end-to-end),
  UNHANDLED_OP trap (rc=134 + diagnostic on stderr),
  real-frontend emit (`OUTPUT = "hi"` emit ok, asm assembles),
  EM-1 flag-validation (regression guard). PASS=4/4.
- New files warning-clean under `-Wall -Wextra` (verified outside
  the project's `-w` setting).
- Gates: smoke ×6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4); isolation
  gate PASS; csnobol4 Budne PASS=36 (≥34); EM-1+EM-2 gate 4/4.
- one4all @ `b5f8b42a`. Session #66, 2026-05-06.

**Step EM-1** — Driver wiring + `libscrip_rt.so` skeleton.
- `scrip.c` accepts `--jit-emit --x64` as a fourth, mutually-exclusive
  execution mode (alongside `--ir-run`/`--sm-run`/`--jit-run`/`--monitor`).
  The two flags are required together; bare `--jit-emit` and bare `--x64`
  each emit a clear error. Mutex with the other modes is enforced.
- New emit entry `sm_codegen_x64_emit(SM_Program*, FILE*)` in
  `src/runtime/x86/sm_codegen_x64_emit.{c,h}`. EM-1 implementation is a
  literal-zero scaffold: the SM_Program is asserted non-null but unused;
  the function writes a System V AMD64 `main` that calls
  `scrip_rt_init(argc, argv)` then `scrip_rt_finalize()` and returns its
  rc. GNU-as / Intel-syntax dialect, PLT-relative calls, PIC-friendly.
- New runtime support library skeleton at `src/runtime/rt/scrip_rt.{c,h}`.
  Exports `scrip_rt_init` (no-op) and `scrip_rt_finalize` (returns 0).
  Public ABI documented in the header; subsequent EM-N rungs extend
  monotonically. Built via Makefile target `make libscrip_rt` →
  `out/libscrip_rt.so` (gcc -fPIC -shared).
- New gate script `scripts/test_smoke_jit_emit_x64.sh`. Four sub-tests:
  emit (asm produced; main + ABI calls present), link (gcc -no-pie against
  libscrip_rt.so with -rpath), run (binary exits 0), errors (all three
  flag-validation paths fire). PASS=4/4.
- Both new files warning-clean even under `-Wall -Wextra` (verified
  outside the project's `-w` setting).
- Gates: smoke ×6 PASS (snobol4 7/7, snocone 5/5, icon 5/5, prolog 5/5,
  raku 5/5, rebus 4/4); isolation gate PASS; csnobol4 Budne PASS=36
  (≥34); EM-1 gate PASS=4/4.
- one4all @ `2dda60cc`. Session #66, 2026-05-06.

(no other rungs closed yet)

---

## Definitions

- **mode 4 / `--jit-emit`** — the fourth SCRIP execution mode:
  emit a standalone asm/binary linked against `libscrip_rt.so`,
  rather than running in the host process. Modes 1–3 are
  `--ir-run` (IR walker), `--sm-run` (SM dispatch loop in-host),
  `--jit-run` (in-process JIT).

- **`libscrip_rt.so`** — the runtime support library the emitted
  binary links against. Contains all language-semantic code that
  cannot be reasonably baked into the emitted binary itself
  (pattern matcher, NV table, BB broker, builtins).

- **baked-direct opcode** — an SM opcode whose codegen produces
  inline x86 (e.g., `SM_PUSH_INT`, `SM_ADD`, `SM_JUMP`). No
  function call into `libscrip_rt.so`.

- **runtime-call opcode** — an SM opcode whose codegen produces
  a call into `libscrip_rt.so` (e.g., `SM_PAT_MATCH`,
  `SM_BB_DRIVE`, `SM_CALL_CHUNK` when the target is descriptor-
  carried rather than emit-time-known).

---

## Watermark

EM-3 LANDED 2026-05-06 (session #67) -- typed ScripRtVal stack; SM_PUSH_LIT_S,
SM_PUSH_VAR, SM_STORE_VAR, SM_POP, SM_ADD/SUB/MUL/DIV/MOD emitters; (2+3)*4=20
gate PASS. ARCH: sm_macros.s (one GNU-as macro per SM opcode group, three-column
format); emit_bb_box() scaffold (one-proc-per-box, alpha/beta/gamma/omega).
Honest deviations: SM_DUP/SM_SWAP not in opcode enum; nv_get/set stubs; arith
integer-only; SM_JUMP_S/F declared for EM-4. Gate: PASS=5 FAIL=0.
Artifact tracking: corpus/programs/snobol4/demo/*.s side-by-side (roman,
wordcount, claws5, expression, porter, treebank-array, treebank-list, beauty --
all assemble cleanly). one4all artifacts/x64/ mirrors with beauty_prog.s.
one4all @ 64b409a9. corpus @ ac5392f. Next rung: EM-4 (SM_JUMP/SM_JUMP_S/SM_JUMP_F
control flow; gate: forward jump + conditional backward loop).

ARCH PIVOT settled 2026-05-06 (session #67)

ARCH PIVOT settled 2026-05-06 (session #67) -- Two-emitter architecture
documented above. SM straight-line opcodes use one GNU-as macro per opcode
group (sm_macros.s), inline x86, three-column format. BB boxes emitted one
proc at a time via emit_bb_box(), four ports alpha/beta/gamma/omega, from
the proven bb_emit.c / snobol4_asm.mac precedent (106/106 SPITBOL oracle).
libscrip_rt.so is the boundary only for NV table, pattern matcher, GC.

EM-3 IN PROGRESS 2026-05-06 (session #67) -- SM typed value stack
(ScripRtVal) implemented in libscrip_rt.so; emitters for SM_PUSH_LIT_S,
SM_PUSH_VAR, SM_STORE_VAR, SM_POP, SM_ADD/SUB/MUL/DIV/MOD added.
Gate program (2+3)*4=20 ready. Architecture pivot means EM-3 will be
restructured around sm_macros.s before gate is run against final form.
SM_DUP/SM_SWAP not in sm_opcode_t enum (honest deviation). scrip_rt_nv_get/
nv_set are stubs (NV table requires GC+snobol4 runtime linkage). Arithmetic
is integer-only in EM-3 gate (string coercion deferred).

EM-2 LANDED 2026-05-06 (session #66) -- SM_HALT and SM_PUSH_LIT_I
baked. Synthetic PUSH_LIT_I 42 + HALT round-trip emit->link->run
verified end-to-end (rc=42). libscrip_rt ABI at 6 symbols. Per-PC
labels (.LpcN) emitted for future EM-4 jump targets. Honest
deviations: SM_NOP skipped (not in opcode enum); scrip_rt_pop_int
pulled forward from EM-3 ABI to make EM-2 gate distinguishable.

EM-1 LANDED 2026-05-06 (session #66) -- driver wiring + libscrip_rt.so
skeleton in place. End-to-end pipeline proven: scrip --jit-emit --x64
file.sno -> asm -> gcc -no-pie + -lscrip_rt -> ELF binary -> loads and
exits 0.

Goal stub written 2026-05-05 in session #62, lifted from
GOAL-CHUNKS.md Steps 8 and 19.
