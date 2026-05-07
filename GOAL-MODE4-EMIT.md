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

### 1. SM opcodes -> macros (the SM emitter)

The SM instruction set is the universal IR. Every backend (x86, JVM,
.NET, JS, WASM) walks the same SM_Program array with one switch, one
case per opcode. For text-asm output, each opcode group maps to ONE
named GNU-as macro in `sm_macros.s`. The macro expands to actual inline
x86 -- NOT a PLT call for every tiny op. Flat macro call per opcode,
NO three-column formatting:

  SM_PUSH_INT 42
  SM_ADD
  SM_JUMP_F  .Lpc17

One macro file `sm_macros.s` (parallel to the proven `snobol4_asm.mac`,
151 macros) defines one macro per SM opcode group. `libscrip_rt.so` is
the boundary for: NV table, pattern matcher, GC only.

### 2. BB boxes -> three-column layout (the BB box emitter)

The BB graph is NOT a sequence of SM opcodes. It is a directed graph
of box nodes. Each box has exactly four ports:

  alpha (a) -- try (entry: forward attempt)
  beta  (b) -- retry (entry: backtrack)
  gamma (g) -- success exit (drives next box's alpha)
  omega (o) -- failure exit (drives enclosing beta)

**The Law (from BB-GEN-X86-TEXT.md):** One GNU-as proc per box.
Each named pattern or primitive box = one labeled proc with local labels
`.alpha`, `.beta`, `.gamma`, `.omega`. Emitted ONE BOX AT A TIME.

**THREE-COLUMN LAW** applies here (BB boxes only, not SM opcodes):

  LABEL:              ACTION (macro + params)          GOTO (jmp target)

The proven precedent: `bb_emit.c` TEXT mode + `snobol4_asm.mac` 151 macros,
106/106 vs SPITBOL oracle. The new mode-4 emitter inherits this model
directly. `emit_bb_box()` is a clearly separate function from the SM
straight-line emitter.

### Separation in sm_codegen_x64_emit.c

  emit_sm_instr()    -- SM opcodes (push/pop/arith/control flow)
                        one emit_sm_* fn per opcode group
                        flat macro call per opcode -- NO three-column
                        inline x86 via sm_macros.s, not PLT calls

  emit_bb_box()      -- called once per SM_PAT_* instruction
                        emits one proc with .alpha/.beta/.gamma/.omega
                        THREE-COLUMN layout: label / macro+params / jmp
                        jmp gotos connect ports across boxes

### Multi-backend portability

For JVM: SM opcodes -> iload/iadd/etc; BB boxes -> method-per-box.
For .NET: SM opcodes -> ldc/add/etc; BB boxes -> delegate-per-box.
For JS: SM opcodes -> function calls; BB boxes -> closure-per-box.
For WASM: SM opcodes -> i64.add/etc; BB boxes -> function-per-box.
All share the same alpha/beta/gamma/omega four-port protocol.

---

## Generated-code readability standard (settled session #68, 2026-05-06)

⛔ The mode-4 emitter does NOT spit. Other compilers spit. Ours
documents.

The emitted `.s` file is a deliverable in its own right: it must
read top-to-bottom as an annotated disassembly so a human can audit
the codegen without consulting `--dump-sm` or the SM_Program. This
is binding on every backend (x86, JVM, .NET, JS, WASM) and every
frontend. New rungs that touch emit paths inherit the standard.

### Page-break hierarchy

Major banner — emitted at every statement boundary (`SM_STNO`):

```
# ============================================================================
# stmt N  (line L):  <verbatim source line>
# ============================================================================
```

Minor banner — emitted between conceptual blocks within a statement
(value build vs. store vs. goto), used sparingly:

```
# ----------------------------------------------------------------------------
# <caption>
# ----------------------------------------------------------------------------
```

The comment introducer is `#` (GNU-as line-comment); `;` is the
statement separator on x86 GAS and must NOT be used for comments.
JVM / .NET / JS / WASM textual outputs use their respective
line-comment introducers but the visual shape (== major, -- minor)
is invariant across backends.

### Source-text preservation

The emitter receives the source-file path and slurps it once into
a 1-based `lineno → text` cache. `SM_STNO` carries `stno` in
`a[0].i` and `lineno` in `a[1].i` — the latter is purely
informational and the interpreter ignores it. When `lineno` is
0 (parser-recorded only on labeled statements today) or out of
range, the emitter falls back to `lineno = stno` because the
SNOBOL4 / Snocone / Icon / Prolog / Raku / Rebus convention is
one statement per line. A future rung — one-line .y change in each
frontend — will record `lineno` on every statement and the
fallback can be removed.

### Inline annotations (third column, `# ...`)

Every line whose asm alone does not reveal the source-level
referent MUST carry a third-column annotation naming what the
referent is:

| Asm | Annotation |
|---|---|
| `movabs rdi, <ptr>` for SM_PUSH_LIT_S | `# str="..."` (escape-and-truncate preview) |
| `movabs rdi, <ptr>` for SM_PUSH_VAR | `# var=NAME` |
| `movabs rdi, <ptr>` for SM_STORE_VAR | `# store -> NAME` |
| `mov edi, <op>` for SM_ADD/SUB/MUL/DIV/MOD | `# SM_ADD` etc. (opcode mnemonic) |
| `jmp .LpcN` | `# SM_JUMP -> pc=N` |
| `jz .LpcN` | `# SM_JUMP_F -> pc=N` |
| `jnz .LpcN` | `# SM_JUMP_S -> pc=N` |
| Literal-immediate opcodes (e.g. `movabs rdi, 42`) | no annotation needed; the literal IS the source |

The escape-and-truncate convention for string previews: backslash
quote and backslash; replace bytes < 0x20 and 0x7f with `.`; cap
at 40 chars with trailing `...` if truncated.

### Why this is binding

The output `.s` files (and equivalents on other backends) are
checked in to corpus as tracked artifacts. Each session's
regeneration commit is a diff a human can read. If the readability
properties degrade, the diff makes it visible immediately and the
commit is rejected on review. There is no path to "we'll add the
banners later" — once the standard is in, every emitter touch
preserves it.

---

## Tracked Artifacts — Protocol (settled session #67, 2026-05-06)

### The rule

At the end of every session that touches the mode-4 emitter:

1. Regenerate all tracked `.s` files.
2. If a `.s` file assembles cleanly AND differs from the repo copy, commit it.
3. If it does not assemble, do NOT commit it — leave repo copy unchanged.
4. Git history is the archive. No session-numbered copies. Ever.

`git log -p corpus/programs/snobol4/demo/roman.s` shows full emitter evolution.

### Tracked demo programs (canonical location: corpus/programs/snobol4/demo/)

Five programs. Chosen for coverage (distinct features) and stability (will not be deleted again).

| File | Lines | Size | Features exercised |
|------|-------|------|--------------------|
| `roman.sno` | 36 | 7 KB | Recursive DEFINE, REPLACE, BREAK, pattern match |
| `wordcount.sno` | 13 | 10 KB | BREAK/SPAN, INPUT loop, arithmetic |
| `claws5.sno` | 213 | 90 KB | ARBNO, complex patterns, corpus-scale |
| `treebank-list.sno` | 207 | 101 KB | Nested patterns, stack operations |
| `treebank-array.sno` | 243 | 120 KB | Array operations, nested patterns |

The `.s` files live side-by-side with the `.sno` files in corpus:

    corpus/programs/snobol4/demo/roman.sno           roman.s          (7 KB)
    corpus/programs/snobol4/demo/wordcount.sno        wordcount.s     (10 KB)
    corpus/programs/snobol4/demo/claws5.sno           claws5.s        (90 KB)
    corpus/programs/snobol4/demo/treebank-list.sno    treebank-list.s (101 KB)
    corpus/programs/snobol4/demo/treebank-array.sno   treebank-array.s (120 KB)

Programs NOT tracked here (too large to inspect):
Programs NOT tracked (too large): expression.sno, porter.sno, beauty.sno.

### Regen + commit protocol

Run this at the end of every session that touches sm_codegen_x64_emit.c,
sm_macros.s, or scrip_rt.c:

```bash
cd /home/claude/one4all
DEMO=/home/claude/corpus/programs/snobol4/demo

# Regenerate
./scrip --jit-emit --x64 $DEMO/roman.sno          > $DEMO/roman.s          2>/dev/null
./scrip --jit-emit --x64 $DEMO/wordcount.sno       > $DEMO/wordcount.s      2>/dev/null
./scrip --jit-emit --x64 $DEMO/claws5.sno          > $DEMO/claws5.s         2>/dev/null
./scrip --jit-emit --x64 $DEMO/treebank-list.sno   > $DEMO/treebank-list.s  2>/dev/null
./scrip --jit-emit --x64 $DEMO/treebank-array.sno  > $DEMO/treebank-array.s 2>/dev/null

# Verify all assemble (do not commit if any fail)
for s in $DEMO/roman.s $DEMO/wordcount.s $DEMO/claws5.s \
          $DEMO/treebank-list.s $DEMO/treebank-array.s; do
    gcc -c "$s" -o /dev/null 2>/tmp/as_err.txt         && echo "OK   $(basename $s)"         || { echo "FAIL $(basename $s) -- NOT committing"; cat /tmp/as_err.txt; exit 1; }
done

# Commit corpus if changed
cd /home/claude/corpus
git diff --stat programs/snobol4/demo/roman.s programs/snobol4/demo/wordcount.s
git add programs/snobol4/demo/roman.s programs/snobol4/demo/wordcount.s \
        programs/snobol4/demo/claws5.s programs/snobol4/demo/treebank-list.s \
        programs/snobol4/demo/treebank-array.s
git diff --cached --quiet || git commit -m "x64 artifacts: regen demo/*.s (<rung>)"
```

### What to look for

`roman.s` is the primary inspection target after each rung — small enough
to read, complex enough to be meaningful:

- `# UNHANDLED_OP` comment lines = opcodes not yet baked (shrinks each rung)
- `scrip_rt_arith@PLT` calls = arithmetic baked (EM-3+)
- `.box_N_alpha` / `.box_N_gamma` labels = BB boxes baked (EM-6+)
- Zero UNHANDLED_OP = EM-7 beauty oracle gate

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

- [x] **Step EM-4 — Control flow: SM_JUMP, SM_JUMPF, SM_JUMPT,
  SM_LABEL.**  Direct x86 jumps to baked-at-emit-time pc values.
  Labels resolve at emit time — no runtime branch table needed.
  Gate: SM program with a forward jump and a conditional
  backward jump runs correctly.

- [x] **Step EM-5 — SM_PUSH_CHUNK / SM_CALL_CHUNK / SM_RETURN.**
  This is the core of the chunks design. `SM_PUSH_CHUNK` emits
  a constant push of `(entry_pc, arity)`. `SM_CALL_CHUNK` is a
  baked direct call to the chunk's emit-time address (no
  dispatch loop). `SM_RETURN` is a standard ret. The
  `libscrip_rt.so` `scrip_rt_call_chunk` becomes thin — it
  exists for chunks called by descriptor (e.g., from pattern
  matcher), not for direct chunk-to-chunk calls.
  Gate: SM program with two chunks calling each other returns
  the right value.

- [x] **Step EM-6 — Pattern matcher integration.**  The pattern
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

**Step EM-5** — SM_PUSH_CHUNK / SM_CALL_CHUNK / SM_RETURN.
- Three SM chunk-discipline opcodes baked in `sm_codegen_x64_emit.c`.
  `SM_RETURN` → native `ret`; `SM_CALL_CHUNK` → baked direct
  `call .Lpc<entry_pc>` against the per-PC labels EM-2 already plants;
  `SM_PUSH_CHUNK` → `scrip_rt_push_chunk_descr(entry_pc, arity)` —
  pushes a `ScripRtVal{tag=SCRIP_RT_CHUNK=11, slen=arity, i=entry_pc}`
  whose tag/layout mirrors `DT_E` in `descr.h` (chunk-flag carried in
  `slen`, entry_pc in `.i`).
- libscrip_rt.so ABI grew by one symbol: `scrip_rt_push_chunk_descr`
  plus the `SCRIP_RT_CHUNK = 11` enum addition. `SM_CALL_CHUNK` and
  `SM_RETURN` need no ABI symbols — both are pure inline x86.
- **Honest deviation from interpreter (documented in emitter source):**
  `sm_interp.c`'s `SM_CALL_CHUNK` snapshots the caller's value stack
  to a heap buffer, runs the chunk on an empty stack, then restores
  + appends the result. The mode-4 emitter does NOT snapshot — it
  uses shared-stack `call`/`ret` over the global value stack inside
  `libscrip_rt.so`. Rationale: (1) byte-correct for clean chunk
  bodies; (2) stack-discipline violations would be lowerer bugs, not
  emitter responsibility; (3) the snapshot machinery is needed for
  `SM_SUSPEND/SM_RESUME` in EM-10 anyway and belongs there. If a
  future rung surfaces a real test case that needs snapshot-and-
  restore, we revisit.
- **Honest deviation 2:** Conditional return variants
  (`SM_RETURN_S/F`, `SM_FRETURN[_S/_F]`, `SM_NRETURN[_S/_F]`) still
  trap via `emit_sm_unhandled`. The tracked `.s` files for the demo
  programs assemble cleanly (the unhandled stub is a real call
  instruction); they will not RUN correctly until a near-future rung
  adds the conditional-return shapes. EM-5's gate doesn't exercise
  them. Filed as inline next-rung scope.
- **Honest deviation 3:** `SM_PUSH_CHUNK`'s descriptor sits on the
  value stack but is not yet routed to a downstream `EVAL` /
  `sm_call_chunk` consumer; that path activates when EM-6+ links the
  pattern matcher. EM-5b proves the descriptor-push call path round-
  trips without corrupting the SM stack.
- Test harness extended: `argv[5]=em5.s` (two chunks calling each
  other; chunk_A calls chunk_B which returns 7, A adds 6, returns 13;
  rc=13), `argv[6]=em5b.s` (PUSH_CHUNK 99,2 + POP + PUSH 21 + HALT;
  rc=21). Gate adds two sub-tests (PASS=7 → PASS=9). Argc range
  extended (max 7 args).
- Five tracked artifacts regenerated and assemble cleanly: `roman.s`,
  `wordcount.s`, `claws5.s`, `treebank-list.s`, `treebank-array.s`.
- Gates: smoke ×6 PASS (snobol4 7/7, snocone 5/5, icon 5/5, prolog
  5/5, raku 5/5, rebus 4/4); isolation gate PASS; EM-1..EM-5 gate
  PASS=9 FAIL=0.
- one4all @ d5800b58. corpus @ 9ef362e. .github @ b033d1c.
  Session #69, 2026-05-06.

**Step EM-4** — Control flow + generated-code readability standard.
- Three SM control-flow opcodes baked direct in
  `sm_codegen_x64_emit.c`. `SM_JUMP` → `jmp .Lpc<target>`;
  `SM_JUMP_S` → `call scrip_rt_last_ok / test eax,eax / jnz
  .Lpc<target>`; `SM_JUMP_F` → same shape with `jz`. Targets
  resolve at emit time against the per-PC `.LpcN:` labels EM-2
  already plants. `SM_LABEL` is a no-op emitter-side because the
  per-PC label already serves as the jump target — kept as a
  documented switch case so it never falls through to
  `emit_sm_unhandled`.
- libscrip_rt.so ABI grew by one symbol: `scrip_rt_set_last_ok(int)`.
  Backs a real `g_last_ok` flag (was a hard-coded `return 1` stub
  in EM-3). Default is 1 at process start; future rungs (EM-6
  pattern matcher) will toggle it implicitly. EM-4b gate
  demonstrates an external override pattern that drives a backward
  loop — proving the JUMP_F shape executes correctly when the
  flag is 0.
- **Generated-code readability standard** landed in this rung —
  see the `## Generated-code readability standard` section above
  for the binding spec. Concretely: `SM_STNO` now emits a major
  page-break banner showing `# stmt N (line L): <verbatim source>`
  above each statement's asm block; `SM_PUSH_LIT_S` annotates the
  string-pointer immediate with `# str="..."`; `SM_PUSH_VAR` /
  `SM_STORE_VAR` annotate with `# var=NAME` / `# store -> NAME`.
  The emitter signature changed to
  `sm_codegen_x64_emit(SM_Program*, FILE*, const char *src_path)` —
  pass `NULL` for synthetic test programs; pass the input path for
  real-frontend emit (scrip.c does this). The source file is slurped
  once and indexed 1-based.
- **`sm_lower.c` change (one line):** `SM_STNO` now uses
  `sm_emit_ii(p, SM_STNO, stno, lineno)` so the emitter has the
  source-line number on every statement boundary. Safe for
  `sm_interp.c` because it reads only `a[0].i` for STNO. Visible in
  `--dump-sm` output as `stmt=N line=L`.
- **Honest deviations from the rung text, documented in code:**
  - The rung names "SM_JUMPT" but the enum is `SM_JUMP_S` (success).
    Same opcode under a different name. Ditto JUMPF / JUMP_F.
  - Parser records `s->lineno` only on labeled statements today
    (`commit_go: s->lineno=lbl.lineno`). Unlabeled statements arrive
    with `lineno=0`. Emitter handles this with a
    `lineno==0 → fallback to stno` rule, valid because SNOBOL4 source
    convention is one statement per line. A one-line .y change in
    each frontend will make the fallback unnecessary; deferred.
  - END statement's recorded `lineno` is sometimes past EOF (lexer
    advanced after parsing END). Emitter detects out-of-range and
    falls back identically.
- **Backward-compatible `scrip_rt_last_ok` ABI:** the old EM-3 stub
  always returned 1; EM-4 makes it back a real flag with a
  default-1 initializer. Programs that linked against the EM-3
  library and never called `set_last_ok` continue to work
  identically.
- Test harness extended: `argv[3]=em4a.s` (forward jump + JUMP_F
  not-taken + JUMP_S taken; rc=42), `argv[4]=em4b.s` (backward
  loop body driven by override; rc=0). Gate adds two sub-tests
  (PASS=5 → PASS=7).
- Five tracked artifacts regenerated and assemble cleanly:
  `roman.s` (177 lines, was 164), `wordcount.s` (242, was 211),
  `claws5.s` (2024, was 1786), `treebank-list.s` (2318),
  `treebank-array.s` (2748). Line growth is the readability work
  — page-break banners + verbatim source + inline annotations.
- Gates: smoke ×6 PASS (snobol4 7/7, snocone 5/5, icon 5/5, prolog
  5/5, raku 5/5, rebus 4/4); isolation gate PASS; EM-1..EM-4 gate
  PASS=7 FAIL=0; csnobol4 Budne PASS=36 (≥34, run pre-readability
  edits — no runtime change since).
- one4all @ 86d9c707. corpus @ 7ba9eea. .github @ HEAD. Session #68, 2026-05-06.

**Step EM-3** — SM stack ops + arithmetic.
(See watermark below — EM-3 was watermark-only; promoted to a
formal closed entry in a future cleanup pass.)

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

EM-7-pre LANDED 2026-05-07 (session #71) -- beauty.sno emits, assembles, links;
runs until SM_PAT_CAPTURE_FN trap. Substantial groundwork for EM-7 closure.

Five SM opcode groups baked in sm_codegen_x64_emit.c:
(1) SM_CALL -- general function dispatch via scrip_rt_call(name, nargs).
    Pseudo-calls (INDIR_GET, NAME_PUSH, ASGN_INDIR, IDX, IDX_SET) handled
    inline in libscrip_rt.so mirroring sm_interp.c's SM_CALL switch.
    Builtin/user-fn fall-through to INVOKE_fn -> APPLY_fn -> g_user_call_hook.
    SN-6 FAIL-arg short-circuit preserved.
(2) SM_CONCAT, SM_PUSH_NULL, SM_COERCE_NUM -- thin PLT calls.
(3) Conditional return variants: SM_RETURN_S/F, SM_FRETURN[_S/_F],
    SM_NRETURN[_S/_F] -- emit_sm_return_variant emits a kind/cond pair,
    calls scrip_rt_do_return; if fires, native ret; else jz to .Lretskip_<pc>.
    Plain unconditional SM_RETURN unchanged (still pure native ret).
(4) SM_PAT_CAPTURE_FN_ARGS, SM_PAT_USERCALL_ARGS -- args-on-stack pattern
    capture variants (.fn(args) / $fn(args) / *fn(args)).
(5) Test 2 in test_smoke_jit_emit_x64.sh changed from SM_CONCAT (now baked)
    to SM_INCR (still unhandled) to keep the unhandled-op trap test live.

libscrip_rt.so capacity bumps:
- STRTAB_CAP   512 -> 8192   (beauty.sno has 749 unique strings)
- VSTACK_CAP   256 -> 65536  (beauty.sno self-hosting needs deep stack)

New libscrip_rt.so ABI (7 entries):
- scrip_rt_concat() / scrip_rt_push_null() / scrip_rt_coerce_num()
- scrip_rt_call(const char *name, int nargs)
- scrip_rt_do_return(int kind, int cond) -> int
- scrip_rt_pat_capture_fn_args(const char *fname, int is_imm, int nargs)
- scrip_rt_pat_usercall_args(const char *fname, int nargs)

Tracked .s artifacts: zero UNHANDLED_OP markers across all five demo
programs (roman/wordcount/claws5/treebank-list/treebank-array) -- a
visible diff-review marker that EM-7's emit-side coverage is essentially
complete.  Line counts shrank as PLT calls replaced UNHANDLED stubs:
roman 177->146, wordcount 242->222, claws5 2024->1815, treebank-list
2318->2190, treebank-array 2748->2610.

beauty.sno end-to-end status:
- emit:    34102 lines of asm, exit 0
- assemble: 415 KB .o, no errors
- link:    128 KB ELF binary, no errors
- run:     starts; halts at first SM_PAT_CAPTURE_FN (opcode 51)
           via scrip_rt_unhandled_op trap.

Honest deviations remaining for EM-7 closure (deferred to EM-7-final):
(1) SM_PAT_CAPTURE_FN and SM_PAT_USERCALL (no-args forms) still trap.
    emit_bb_box's switch needs cases for these; the libscrip_rt.so
    helpers (pat_assign_callcap_named_imm, pat_user_call) already exist.
(2) User-defined SNOBOL4 function dispatch in mode-4 not yet wired:
    scrip_rt_call falls through to INVOKE_fn for unknown names, which
    misses user functions whose bodies are emitted as native chunks at
    .Lpc<N>.  Needs name->entry_pc table emitted in .s + a hook into
    g_user_call_hook that invokes scrip_rt_call_chunk.  Sketch in
    session #71 chat history.
(3) NRETURN's name-tracking is approximate: scrip_rt_do_return reads TOS
    and synthesizes a NAMEVAL from a string value; doesn't track the
    body's retval-slot name.  Sufficient for the dot-star idiom
    (push_list = .dummy) where the body explicitly NAMEVAL'd.

Gate: PASS=10 FAIL=0 (test 2 updated SM_CONCAT->SM_INCR).
Smoke x6 PASS (7/7, 5/5, 5/5, 5/5, 5/5, 4/4).  Isolation gate PASS.
Five tracked .s artifacts regen'd, assemble cleanly, zero UNHANDLED_OP.

Next rung: EM-7-final (close the EM-7 milestone).
- EM-7a: Bake SM_PAT_CAPTURE_FN + SM_PAT_USERCALL in emit_bb_box.
- EM-7b: User-defined function dispatch table (name -> entry_pc).
- EM-7c: --jit-emit --x64 beauty.sno passes SPITBOL oracle gate
         (md5 abfd19a7a834484a96e824851caee159, 646 lines).

EM-6 LANDED 2026-05-06 (session #70) -- pattern matcher integration.

ScripRtVal/ScripRtTag removed; DESCR_t is the one type throughout.
libscrip_rt.so now links the full SNOBOL4 runtime (16 objects + parser,
-fPIC): bb_pool_init() + SNO_INIT_fn() in scrip_rt_init(); real
nv_get/nv_set via NV_GET_fn/NV_SET_fn; scrip_rt_arith with string
coercion; scrip_rt_halt_tos (safe-pop TOS as rc else 0).

New EM-6 ABI surface: 26 scrip_rt_pat_*() functions mirroring the
SM_PAT_* dispatcher in sm_interp.c, plus scrip_rt_exec_stmt().
Pat-stack (g_pat_stack[], g_pat_sp) in libscrip_rt.so.

String table (strtab_*) in sm_codegen_x64_emit.c: first pass collects
unique strings; .section .rodata emitted before .text; all string
references use RIP-relative LEA not process-pointer movabs. emit_bb_box()
fully implemented (PLT calls per SM_PAT_*). SM_EXEC_STMT baked.
SM_STNO is a true no-op. SM_HALT uses scrip_rt_halt_tos.

Honest deviations: (1) SM_RETURN_S/F, SM_FRETURN[_S/_F],
SM_NRETURN[_S/_F] still trap via emit_sm_unhandled. (2) SM_PAT_CAPTURE_FN
and SM_PAT_USERCALL unhandled -- trap. (3) DT_E chunk dispatch in eval
path stubs out (sm_call_chunk aborts -- not exercised by EM-6 gate).

Gate: PASS=10 FAIL=0 (new test 10: LEN(3).W on "abcdef", output
matches --sm-run oracle: start/abc/end). Smoke x6 PASS
(7/7,5/5,5/5,5/5,5/5,4/4). Isolation gate PASS.
Five tracked .s artifacts regen'd and assemble cleanly.

one4all @ 5452a9a6. corpus @ cfe5886. Session #70, 2026-05-06.

Next rung: EM-7 (--jit-emit --x64 beauty.sno passes SPITBOL oracle,
md5 abfd19a7a834484a96e824851caee159, 646 lines).

EM-5 LANDED 2026-05-06 (session #69) -- chunk discipline. Three SM opcodes
baked: SM_PUSH_CHUNK (call scrip_rt_push_chunk_descr@PLT), SM_CALL_CHUNK
(baked direct `call .Lpc<entry_pc>`, no PLT, no dispatch loop), SM_RETURN
(native `ret`). libscrip_rt.so ABI grew by one symbol
(scrip_rt_push_chunk_descr) and one enum (SCRIP_RT_CHUNK=11, mirrors DT_E).
EM-5 gate PASS=9 FAIL=0 (was 7 -- added 7a two-chunks-calling-each-other
rc=13, 7b PUSH_CHUNK descriptor round-trip rc=21).

Honest deviations: (1) emitter uses shared-stack call/ret instead of the
interpreter's snapshot-and-restore -- byte-correct for clean chunk bodies;
snapshot moves to EM-10 with SUSPEND/RESUME. (2) Conditional return
variants (SM_RETURN_S/F, SM_FRETURN[_S/_F], SM_NRETURN[_S/_F]) still trap
via emit_sm_unhandled -- tracked .s files assemble but won't run end-to-
end on real frontends until a near-future rung. (3) PUSH_CHUNK descriptor
sits on stack but isn't yet consumed by EVAL/sm_call_chunk -- that path
activates when EM-6+ links the pattern matcher.

Tracked artifacts regenerated and assemble cleanly:
roman.s, wordcount.s, claws5.s, treebank-list.s, treebank-array.s.

Gates: smoke x6 PASS (7/7,5/5,5/5,5/5,5/5,4/4); isolation gate PASS;
EM-1..EM-5 gate PASS=9 FAIL=0.

Next rung: EM-6 (pattern matcher integration -- libscrip_rt.so v1
gains the matcher lifted from snobol4_pattern.c + scan_builtins.c;
emit_bb_box() flips on for SM_PAT_* opcodes; gate: a SNOBOL4 program
using SPAN/BREAK/LEN/*expr/$ capture compiles and runs).

EM-4 LANDED 2026-05-06 (session #68) -- control flow + readability standard.
Three SM opcodes baked: SM_JUMP (direct jmp .LpcN), SM_JUMP_S (call last_ok +
test + jnz), SM_JUMP_F (same shape, jz). SM_LABEL is a no-op (per-PC label
suffices). libscrip_rt.so ABI grew by one symbol: scrip_rt_set_last_ok backs
a real g_last_ok flag (was a return-1 stub). EM-4 gate PASS=7 FAIL=0
(was 5 -- added 6a forward-jump+conditional-shapes rc=42, 6b backward-loop
override rc=0).

GENERATED-CODE READABILITY STANDARD landed this rung -- now binding on every
backend. Major page-break banner ('====') over each statement showing
verbatim source text + stno + lineno. Inline annotations on the right column
(# str="...", # var=NAME, # store -> NAME, # SM_JUMP -> pc=N, etc.).
Emitter signature is now sm_codegen_x64_emit(SM_Program*, FILE*, const char
*src_path). sm_lower.c emits SM_STNO via sm_emit_ii so a[1].i carries
lineno; visible in --dump-sm as "stmt=N line=L". sm_interp.c reads only
a[0].i so the change is interp-safe.

Tracked artifacts regenerated and assemble cleanly: roman.s 177 (was 164),
wordcount.s 242 (was 211), claws5.s 2024 (was 1786), treebank-list.s 2318,
treebank-array.s 2748. Line growth = readability work (banners + verbatim
source + inline annotations).

Honest deviations: parser records s->lineno only on labeled statements
today; emitter falls back to lineno=stno when lineno is 0 or out of range
(SNOBOL4 convention is one stmt per line so this hits in practice). One-line
.y change in each frontend will remove the fallback; deferred.

Gates: smoke x6 PASS (7/7,5/5,5/5,5/5,5/5,4/4); isolation gate PASS;
EM-1..EM-4 gate PASS=7 FAIL=0; csnobol4 Budne PASS=36 (run pre-readability
edits; no runtime change since).

one4all @ 86d9c707. corpus @ 7ba9eea. Next rung: EM-5
(SM_PUSH_CHUNK / SM_CALL_CHUNK / SM_RETURN; gate: two chunks calling
each other).

EM-3 LANDED 2026-05-06 (session #67) -- typed ScripRtVal stack; SM_PUSH_LIT_S,
SM_PUSH_VAR, SM_STORE_VAR, SM_POP, SM_ADD/SUB/MUL/DIV/MOD emitters; (2+3)*4=20
gate PASS. ARCH: sm_macros.s (one GNU-as macro per SM opcode group, three-column
format); emit_bb_box() scaffold (one-proc-per-box, alpha/beta/gamma/omega).
Honest deviations: SM_DUP/SM_SWAP not in opcode enum; nv_get/set stubs; arith
integer-only; SM_JUMP_S/F declared for EM-4. Gate: PASS=5 FAIL=0.
Artifact tracking: corpus/programs/snobol4/demo/*.s side-by-side (roman,
wordcount, claws5, expression, porter, treebank-array, treebank-list, beauty --
all assemble cleanly). one4all artifacts/x64/ mirrors with beauty_prog.s.
one4all @ 64b409a9. corpus @ ac5392f. Next rung: EM-4 (SM_JUMP/SM_JUMP_S/SM_JUMP_F control flow;
gate: forward jump + conditional backward loop).

Artifact tracking settled session #67 (handoff session):
  Five tracked .s files in corpus/programs/snobol4/demo/:
    roman.s (7KB) wordcount.s (10KB) claws5.s (90KB)
    treebank-list.s (101KB) treebank-array.s (120KB)
  Protocol: regen each session; commit if assembles AND changed.
  corpus @ 006a437. .github @ 8918c23. one4all @ 204321ae.

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
