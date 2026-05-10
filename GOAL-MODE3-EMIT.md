# GOAL-MODE3-EMIT.md — Mode 3 becomes a real per-instruction native x86 emitter

⛔ **REQUIRED READING — read these BEFORE opening any source file or running any
code under this Goal:**
1. `ARCH-x86.md` (whole file) — defines the x86 backend, the four execution
   modes, the BINARY/TEXT dual-emitter principle, the byrd-box ABI, and the
   SM_Program / native-code relationship.
2. `ARCH-SCRIP.md` (whole file) — defines mode-1/2/3/4 in the table at
   §"Execution modes (RS-15)" and the mode-specific notes section.

**Repo:** one4all (primary) + corpus + .github.

**Premier-goal status.**  This Goal pauses most other active work until it
closes.  The only sibling Goal that remains active in parallel is
`GOAL-ICON-BB-COMPLETE`.  Everything else stops at its current rung and waits.
The reason: mode 3 today is not what `ARCH-x86.md` says it is, and almost every
downstream piece of work (mode 4 emission, EXPRESSION lowering for `*P`/`*(X+1)`,
Icon/Prolog full SM dispatch, the four-mode isolation property for all
frontends) is structurally blocked behind a real mode 3.  Land mode 3 properly
once and the rest unblocks together.

**Done when:** `scrip --jit-run file.{sno,sc,icn,pl}` runs every program in the
`--sm-run` (mode 2) PASS set with byte-identical output, going through a real
native-x86 emitter that produces per-`SM_Instr` blobs of inline x86 in
`SEG_CODE`, dispatched by an entry jump from `sm_jit_run` and threaded through
the program by native `jmp`/`call`/`ret`.  No C dispatch loop.  No per-opcode
tail-call thunks.  No `uint8_t**` pointer array.  Pattern construction
(`SM_PAT_*`) operates on the same value stack as everything else — no separate
pat-stack.  Glob-emitted invariant pattern fragments (live via `bb_flat.c`
EMIT_BINARY in `bb_pool` at runtime) continue to work unchanged; their
per-glob `r10`-anchored data block is the design that mode-3 SM-blob land
adopts for its own register convention.

**Once this Goal closes**, `GOAL-MODE4-EMIT`'s `EM-MODE4-IS-MODE3-DUMP` becomes
trivially achievable: mode 4 = mode 3 with `SEG_CODE` bytes serialized to
`.s` plus auxiliary sections.  We do not dump dynamically-built things — variant
pattern globs allocated in `bb_pool` at execution time are not part of mode 4
output.  A future `EXIT(3)`-style memory-image dump is dreamed about but not
in scope here.

---

## Architectural target

### One value stack

Today's `sm_interp.c` and `sm_codegen.c` both carry a separate `g_pat_stack` /
`g_jit_pat_stack` for `SM_PAT_*` opcodes.  This is vestigial.  Every
`SM_PAT_*` opcode pushes or pops `DESCR_t` values whose type is `DT_P` — they
are values, the same shape as every other SM stack push/pop.  `SM_PAT_BOXVAL`
is literally `pat_pop()` then `sm_push()` — it exists only to bridge the two
stacks.  The SIL precedent (PATBCL/PATICL) does not apply here: in SCRIP,
patterns are first-class `DT_P` values whose `ζ` is a byrd-box state struct,
and the byrd-box engine — not the SM dispatch loop — is the executor of
patterns at match time.  Construction is just value arithmetic.

**Decision:** the pat-stack collapses into `SM_State.stack`.  `SM_PAT_*`
opcodes are value-stack opcodes.  `SM_PAT_BOXVAL` is deleted.  `g_pat_stack`,
`g_pat_sp`, `g_pat_cap`, `pat_push`, `pat_pop` are deleted from `sm_interp.c`.
`g_jit_pat_stack`, `g_jit_pat_sp`, `g_jit_pat_cap`, `jit_pat_push`,
`jit_pat_pop` are deleted from `sm_codegen.c`.  `sm_lower` stops emitting
`SM_PAT_BOXVAL`.  `SM_EXEC_STMT` pops the pattern from the value stack along
with subject and replacement.  This is ME-1, the opening rung.

### Register convention (mode-3 SM-blob land)

Settled, binding on every rung that emits SM-blob x86:

| Reg | Role | Scope |
|-----|------|-------|
| `r12` | `SM_State*` — anchor for value stack, `last_ok`, `pc` | Whole emitted program; loaded once at `sm_jit_run` entry, never reloaded inside emitted code |
| `r10` | per-glob data-region pointer; `[r10+N]` addresses every local in the currently-active flat-glob | Per BB-glob, loaded once at glob entry preamble; glob-private (caller does not use `r10`, so glob boundary is implicitly save-free) |
| `rbp` | chunk frame pointer for DEFINE'd chunks | Per DEFINE'd chunk; established via `push rbp ; mov rbp, rsp` at entry, torn down via `pop rbp ; ret` at exit |
| `rbx, r13, r14, r15` | callee-saved working registers, used per-box per `bb_boxes.s` convention | Per byrd-box; boxes save/restore their own |
| `rax rdi rsi rdx rcx r8 r9 r11` | C-ABI scratch for PLT calls and SM-blob temporaries | Per SM-blob; caller-saved |

**Why `r12 = SM_State*`.**  Every SM stack op today is a PLT call to
`rt_push_int@PLT` / `rt_pop_void@PLT` / etc.  With `r12` anchored, the hot
ops inline as `mov [r12+sp_offset], rax ; inc dword [r12+sp_byte_offset]` —
three instructions instead of a PLT round-trip.  This is the speedup mode 3
is supposed to deliver, and currently does not.

**Why `r10` for the glob data region.**  This is the proven convention from
`bb_flat.c` (see `EM-FORMAT-BB-DATA-CONSOLIDATE` in `GOAL-MODE4-EMIT.md`'s
closed rungs, sess 2026-05-10).  Every flat-glob invariant pattern blob today
emits `lea r10, [rip + Δ]` as the first instruction of its preamble, then
addresses every box's local state as `[r10+N]` for the rest of the blob.  The
data blocks for every box in the glob are consolidated into one
`.section .data` block at the end of the blob — one contiguous region of
`.quad 0` slots, addressed by baked offsets.  This is exactly the "GLOB BB's
linked in their graph; concat all local storage; one register addresses every
local; save/restore at glob boundary" design.  It already ships; mode-3 just
adopts the same `r10` convention so SM-blob land and BB-glob land coexist
without register conflict.

**Glob boundary save/restore.**  Trivial in this register layout: glob entry
loads `r10` via `lea r10, [rip + Δ_glob]`; SM-blob land never reads or writes
`r10`; on glob `ret` the caller's `r10` is irrelevant because the caller does
not use it.  No active save/restore code at the boundary — the convention is
the discipline.  If glob-to-glob chaining is added later (one glob's `γ` port
jumping directly into another glob's `α`), the receiving glob's entry
preamble's `lea r10, ...` overwrites the previous glob's `r10` — that is the
save/restore, performed unconditionally at every glob entry.

### Two-stack design retired; one stack remains

After ME-1, the only stacks in mode 3 are:
- The `SM_State.stack` (value stack) — `DESCR_t[]` realloc'd, anchored at `r12`.
- The native x86 stack (`rsp`) — used by `call`/`ret`/`push`/`pop` for chunk
  prologues, PLT-call alignment, and byrd-box callee-save spill.

No pat-stack.  No third region.  The byrd-box engine's state lives in
heap-allocated `ζ` structs reachable via the value stack's `DT_P` descriptors,
not in any third stack.

### Deferred-eval consumer (`*P`, `*(X+1)`, `EVAL`, `CODE`)

These are produced by `GOAL-CHUNKS`'s active work: `SM_PUSH_EXPR` is being
replaced with `SM_PUSH_CHUNK <entry_pc>, <arity>`, and the deferred body
lowers in place as

```
   SM_JUMP    skip_chunk_NN
chunk_NN:
   <recursively lowered SM ops for the deferred body>
   SM_RETURN
skip_chunk_NN:
   SM_PUSH_CHUNK  chunk_NN, arity
```

Mode 3's job is to *consume* these opcodes correctly.  `SM_PUSH_CHUNK` pushes
a `DT_E` descriptor whose payload is `{ entry_pc, arity }`.  `SM_CALL_CHUNK`
pops the descriptor, pushes a return frame, sets pc to `entry_pc`, runs until
`SM_RETURN`, leaves the result on the value stack.  No IR walker.  No
`EXPR_t*` field access anywhere in mode 3.

`GOAL-MODE3-EMIT` does not own the producer side (sm_lower's
`SM_PUSH_EXPR → SM_PUSH_CHUNK` migration) — that is `GOAL-CHUNKS-STEP17`'s
work, currently in progress.  This Goal owns the consumer side.  ME-8 lands
**after** GOAL-CHUNKS-STEP17 closes (or at least after a per-frontend SM
sub-program migration completes for the SNOBOL4 frontend), so we are consuming
a stable opcode shape, not a moving target.

### Variant patterns (dynamic) stay dynamic

`bb_flat.c` EMIT_BINARY emits glob bytes into `bb_pool` slots at runtime —
this is the existing variant-pattern path and it stays.  Mode 4 (future)
will not dump these dynamically-built things; they continue to be allocated
fresh per statement.  The SM-blob side of mode 3 is what becomes statically
emittable, not the variant-pattern side.  The architectural rule for mode 4
when it returns: only emit what `sm_codegen` placed in `SEG_CODE` at codegen
time; everything that materializes in `bb_pool` at execution time stays
behind in `libscrip_rt.so`.

### Byrd-box ABI unchanged

Per `bb_boxes.s` (the proven 25-box library, archive 106/106 oracle):
- Entry: `rdi = ζ` (zeta — box state struct), `esi` = entry port (0 = α, 1 = β).
- Exit: `rax:rdx = σ:δ` (success), or `eax=99, edx=0` (failure / `DT_FAIL`).
- Callee-saved: `rbx, r12, r13, r14, r15` — boxes save and restore their own.

Note `r12` is callee-saved per the C-ABI, so the mode-3 SM-blob convention
(`r12 = SM_State*`) is preserved across byrd-box calls automatically.
Boxes that need a callee-saved working register save and restore `r12` like
any other callee-saved reg; they never observe its SM-blob meaning.

---

## Reuse, do not rewrite

| Component | Status | Source |
|-----------|--------|--------|
| `bb_emit.c` dual-mode (TEXT/BINARY) | proven 106/106 | `src/runtime/x86/bb_emit.c` |
| `bb_flat.c` flat-glob invariant emit, `r10`-anchored data | live (mode 3 + mode 4) | `src/runtime/x86/bb_flat.c` |
| `bb_boxes.s` 25-box library | archive | `archive/backend/bb_boxes.s` |
| `bb_pool.c` RW→RX slab | proven | `src/runtime/x86/bb_pool.c` |
| `stmt_exec.c` Phase-3 driver | live | `src/runtime/x86/stmt_exec.c` |
| `SM_State` value stack | live | `src/runtime/x86/sm_interp.c` |
| `sm_codegen.c` segment infrastructure (SEG_CODE, SEG_DISPATCH, seg_alloc, seg_seal) | live but misused | `src/runtime/x86/sm_codegen.c` |
| `sm_lower.c` SM_Program lowering | live | `src/runtime/x86/sm_lower.c` |

Mode 4 stays frozen during this Goal — `sm_codegen_x64_emit.c` text emitter
code is preserved but the mode-4 gate is suspended (per Lon sess 2026-05-10:
mode 4 will be mode 3 + SEG_CODE serializer after ME-14 closes).  When
ME-14 closes, GOAL-MODE4-EMIT's `EM-MODE4-IS-MODE3-DUMP` reopens.

---

## Session Setup

```bash
bash /home/claude/one4all/scripts/install_system_packages.sh
bash /home/claude/one4all/scripts/build_scrip.sh
bash /home/claude/one4all/scripts/build_spitbol_oracle.sh
cd /home/claude/one4all && make libscrip_rt
```

---

## Gates

Every rung holds the following invariants unless explicitly noted:

- `test_smoke_snobol4.sh`: PASS=7 FAIL=0.
- `test_smoke_unified_broker.sh`: PASS=49 FAIL=0.
- `test_gate_em_beauty_subsystems_mode4.sh`: **SUSPENDED** — mode 4 is not yet
  implemented; it will be mode 3 + SEG_CODE serializer after ME-14 closes.
  Code preserved; gate not run during ME-* rungs.  Original baseline was
  PASS=4 FAIL=13 (env-specific; not a hard target).

Rung-specific gates as listed per rung below.

---

## Steps

> Closed-rung details (implementation notes, samples, gate counts, file lists)
> are in this file's git log.  Each closed bullet shows landed-date and the
> one4all commit that landed it; `git log -p .github/GOAL-MODE3-EMIT.md`
> recovers the full prose for any rung.

### Phase A — Foundation (one-stack discipline + r12 reservation)

- [x] **ME-1 — Pat-stack unification.**  Delete `g_pat_stack`/`g_jit_pat_stack`
      and their helpers from `sm_interp.c` and `sm_codegen.c`.  Reroute every
      `SM_PAT_*` opcode to push/pop the value stack.  Delete `SM_PAT_BOXVAL`
      (it becomes a no-op; remove the case and stop emitting it from
      `sm_lower.c`).  Update `SM_EXEC_STMT` to pop pattern from the value
      stack alongside subject and replacement.  ✅ 2026-05-10 one4all `cc3cd475`.
      Gate: smoke 7/7, unified_broker 49/49 (mode-4 gate suspended — see
      Gates section).

- [x] **ME-2 — `r12 = SM_State*` reservation.**  `sm_jit_run` sets
      `r12 = &state` before transferring control to `SEG_CODE`.  No emitted
      code uses `r12` yet — pure infrastructure that establishes the
      convention.  Document the convention in `sm_codegen.c` header comment.
      Gate: smoke 7/7 holds; nothing changes in emitted code.
      ✅ 2026-05-10 one4all `babf76be`.  Implementation: `asm volatile
      ("mov %0, %%r12" : : "r"(st) : "r12")` inside the dispatch loop body,
      just before the stub call.  Today's C-function stubs ignore r12;
      ME-3's per-instruction native blobs will consume it as `[r12 + offset]`
      for value-stack ops.  Verified via `gcc -S`: `mov %rax, %r12` appears
      inside `#APP/#NO_APP` in `sm_jit_run`'s emitted asm.  Header comment
      now documents the full mode-3 register convention (r12 / r10 / rbp /
      callee-saved set / scratch set).  Gate: smoke 7/7, unified_broker 49/49.

### Phase B — Native SM-blob emission (replace threaded-call JIT)

- [x] **ME-3 — Minimal native blob set.**  Rewrite `sm_codegen.c` so each
      `SM_Instr` lowers to its own contiguous native-x86 blob in `SEG_CODE`,
      not a pointer into `SEG_DISPATCH`.  Opcodes covered: `SM_HALT`,
      `SM_PUSH_LIT_I`, `SM_PUSH_LIT_S`, `SM_POP`, `SM_JUMP`.  Build a
      per-PC side-table (`{pc, seg_code_offset, byte_count}`) populated as
      bytes are laid down — needed for jump patching (this rung) and for
      mode 4's future `seg_code_dump_as_s()` (much later).  SM_JUMP uses
      32-bit displacements, patched in a second pass after all blobs are
      emitted.  `sm_jit_run` becomes `mov r12, state ; jmp [SEG_CODE_entry]`.
      Tear out the per-opcode tail-call thunk (`mov rax, imm64 ; jmp rax`)
      mechanism in `SEG_DISPATCH`.  `SEG_CODE` no longer holds a `uint8_t**`
      pointer array; it holds real instructions.  Gate: tiny hello-world
      SNOBOL4 program runs end-to-end via `--jit-run` with byte-identical
      output to `--sm-run`.
      ✅ 2026-05-10 one4all `aca47e6c`.  Per-instruction 30-byte fixed-size
      blob shape:
         Standard: `inc dword [r12+20] ; mov rax,handler ; sub rsp,8 ;
                    call rax ; add rsp,8 ; jmp rel32 trampoline`
         SM_HALT:  `inc dword [r12+20] ; ret ; 24×nop`
         SM_JUMP:  `mov dword [r12+20],target_pc ; jmp rel32 blob[target] ;
                    16×nop`
      Trampoline (~32B at head of SEG_CODE): reads pc from `[r12+20]`,
      bound-checks vs prog->count, then `jmp blobs_base + pc*30`.  Stride
      is encoded as `imul rax, rax, 30` (imm8).  Per-PC side table
      `g_blob_offsets[]` built during emit; used now for SM_JUMP rel32
      patching in pass 2 (`seg_patch_u32` to `blob[target_pc] - rel32_end`),
      will be reused by mode-4 SEG_CODE serializer.  `sm_jit_run` becomes
      a six-line C function: `mov r12,state` (asm volatile) + `entry()`
      (called as `void(*)(void)` to trampoline) + `return 0`.  SM_HALT's
      `ret` returns to `entry()`'s call site — no C dispatch loop.
      16-byte stack alignment: pre-fix the 22-byte blob without `sub rsp,8`
      / `add rsp,8` segfaulted on arith and goto_s because `entry()` left
      `rsp ≡ 8 (mod 16)` and naive `call rax` would enter handlers at
      `rsp ≡ 0`, faulting on the first `movaps` in printf/vsnprintf/GC
      alloc.  The `sub/add rsp, 8` pair restores the ABI's `rsp ≡ 8`
      invariant on callee entry.  Header comment documents the discipline.
      Gates: smoke 7/7, unified_broker 49/49, SN-7 beauty 26/25 unchanged.
      Extended verification: arith, concat, goto_s, unconditional jump,
      vars+arith, 100k-iter loop, pattern replacement, DEFINE'd function
      — all byte-identical `--sm-run` vs `--jit-run`.  Perf microbench
      (100k counter loop): sm-run 110ms, jit-run 82ms (~26% faster);
      modest because handlers still do most work via `call rax`.  ME-4
      inlines arithmetic/stack ops and the gap widens.  Mode-4 gates
      (`test_smoke_jit_emit_x64.sh`, `test_gate_em_beauty_*`) SUSPENDED
      per Gates section; verified pre-existing FAIL state is unchanged.
      SEG_DISPATCH slab still mmap'd by `sm_image_init` but no longer
      written or sealed — sits unused; harmless until a future cleanup
      removes it from `sm_image.c`.

- [ ] **ME-4-pre — Register layout study + design (Lon-directed sess 2026-05-10).**
      Before further inline-native blobs land, lock down the SM-blob
      register convention by reading the existing self-hosting SNOBOL4
      implementations' register-allocation decisions and writing a
      single-page proposal Lon signs off on.  Reason: ME-4 (partial,
      shipped this session at one4all `e7ac6f77`) was emitted without
      a coherent register convention beyond what ME-2/ME-3 already
      locked — each blob reloads `[r12]`-stack-base into a fresh
      scratch and picks ABI scratch regs ad-hoc.  The four C-ABI
      callee-saved regs (`rbx`, `r13`, `r14`, `r15`) are unclaimed in
      SM-blob land — wasted design space.  The right move per Lon:
      do not invent a register layout unilaterally; read what
      CSNOBOL4 and SPITBOL already chose on real evidence.

      Sources to read, in order:
      1. **CSNOBOL4 `v311.sil` → `snobol4.c`** — the generated C
         encodes the SIL VM's register-vs-memory partition.  Look
         for which DESCR_t slots are kept "hot" (in C locals that
         the C compiler will register-allocate) vs. which sit in
         globals.  The set of "hot" slots names the de-facto
         register-budget the original VM design considered minimal.
         Cross-check against `archive/snobol4-csnobol4-internals.md`
         if present, and CSNOBOL4's `descr.c` for DESCR_t layout.
      2. **SPITBOL `sbl.min` → `bootstrap/sbl.asm`** — the hand-
         tuned x86-32 / x86-64 register assignments.  `sbl.min`
         declares SIL globals as named registers via SBL declaratives;
         the bootstrap asm preserves those.  Note which SIL globals
         map to dedicated machine registers vs. `[rel SYM]` global
         memory, and the rationale embedded in macro definitions
         (`asm.sbl`, `lex.sbl`, `err.sbl`).
      3. **`bb_boxes.s`** — the proven 25-box byrd-box library.  Per-
         box callee-save discipline is documented in
         `GOAL-MODE3-EMIT.md` "Prior art" section; cross-check
         which callee-saved regs each box uses as evidence of
         which roles are "important enough to spill."

      Deliverable: a `REGISTER-LAYOUT.md` (in `.github`) covering:
      - The SIL-VM-level register set (named SIL globals →
        machine reg, per CSNOBOL4 + SPITBOL).
      - The SCRIP SM-blob register-set proposal (per-reg role +
        scope + load/save discipline), tracking the prior-art
        choices unless there is a documented reason to diverge.
      - The interaction with the existing fixed assignments
        (`r12 = SM_State*`, `r10 = BB-glob data`, `rbp = chunk
        frame`, byrd-box callee-save discipline from `bb_boxes.s`).
      - Explicit decision for each of `r13`, `r14`, `r15`, `rbx`.
      - The realloc-invalidation question (when does `r13 =
        SM_State.stack` need reload?  Which C calls can grow the
        stack?  What's the marker for "this call may grow"?).
      - The inter-statement sp-reset contract that mode-2
        enforces at `sm_interp.c:295` — and how mode-3 will match
        it (this is the proximate cause of the live realloc bug,
        see ME-4 PARTIAL note).
      Lon signs off on REGISTER-LAYOUT.md.  Then ME-4-post fixes
      the realloc bug against the locked convention.  Then ME-5+
      lands against the locked convention from the start.

      Closure criterion: REGISTER-LAYOUT.md committed in `.github`
      with Lon's sign-off line in its watermark.  No code changes
      land under ME-4-pre.

- [ ] **ME-4-post — Fix realloc bug + re-emit ME-4 blobs against
      locked convention.**  After ME-4-pre lands.  Implements the
      sp-reset-at-statement-boundary contract (per
      REGISTER-LAYOUT.md's decision — likely Option (a): emit a
      per-statement sp-reset blob at SM_STNO).  Re-emits the ten
      ME-4 inline-native blobs against the locked register
      convention, expecting ~25 bytes saved per blob from
      eliminated base-reloads and an additional perf measurement.
      Gate: smoke 7/7 + unified_broker 49/49 hold, the canonical
      multi-statement reproducer (see ME-4 PARTIAL note) runs
      byte-identical between `--jit-run` and `--sm-run`.  When
      ME-4-post closes, ME-4 is closed.

- [ ] **ME-5 — Control flow.**  `SM_JUMP_S`, `SM_JUMP_F`, `SM_LABEL`,
      `SM_STNO`.  SM_LABEL records SEG_CODE offset for the next instruction;
      SM_STNO is no-op at runtime (statement number is used by mode 4 banner
      emission, irrelevant in mode 3).  `SM_JUMP_S` and `SM_JUMP_F` lower
      as `call rt_last_ok@PLT ; test eax, eax ; jnz/jz <rel32>`.  Gate:
      `goto_s` and `goto_f` smoke tests pass under `--jit-run`.

- [ ] **ME-6 — Function calls and returns.**  `SM_CALL_FN`, `SM_RETURN`,
      `SM_NRETURN`, `SM_FRETURN`.  Bridge via existing `rt_call@PLT` for
      builtin dispatch.  DEFINE'd chunks get a real prologue/epilogue:
      `push rbp ; mov rbp, rsp` at entry, `pop rbp ; ret` at exit.  This
      fixes the alignment problem currently failing 13 mode-4 drivers
      (latent in mode 3 today: any chunk that PLT-calls `vsnprintf` via
      `bb_label_initf` faults on `rsp%16==8`).  Gate: `define` smoke
      passes; recursive `roman.sno` runs under `--jit-run`.

- [ ] **ME-7 — Chunk dispatch fix in `sm_lower.c`.**  Distinguish DEFINE'd
      function entries from internal labels (the `:S(label)` / `:F(label)`
      targets).  Add a flag on `SM_LABEL` (e.g. `a[1].i = 1` for DEFINE'd
      entries, 0 otherwise) set by the lowerer when it emits the label
      associated with a `DEFINE('fn(args)')` body.  `emit_expression_registry`
      (in mode 4's emitter, untouched in this Goal — but the same flag is
      consumed by the mode-3 ME-6 prologue emission) filters by the new
      flag.  Internal labels remain addressable for intra-chunk jumps but
      do not enter the registry and do not receive prologues.  Gate:
      `test_gate_sn7_beauty_self_host.sh` measured via `--jit-run` lifts
      from the current 26/51 baseline (exact target tbd; we expect ≥27).

### Phase C — Deferred-eval consumer (post-GOAL-CHUNKS)

- [ ] **ME-8 — `SM_CALL_CHUNK` / `SM_PUSH_CHUNK` consumer.**  Lands **after**
      GOAL-CHUNKS-STEP17 closes (or after the per-frontend SM sub-program
      migration completes for the SNOBOL4 frontend, at minimum, so we
      consume a stable opcode shape).  `SM_PUSH_CHUNK <entry_pc>, <arity>`
      lowers to push a `DT_E` descriptor `{v=DT_E, .ptr=<packed
      entry_pc:arity>}` on the value stack.  `SM_CALL_CHUNK` pops the
      descriptor, pushes a return frame (capturing the post-call SM-PC),
      transfers control via a 32-bit relative jump to `entry_pc`'s
      SEG_CODE offset.  `SM_RETURN` inside a chunk pops the return frame
      and jumps back.  No `EXPR_t*` access.  Coordinated with GOAL-CHUNKS:
      we provide the mode-3 consumer; GOAL-CHUNKS provides the producer
      (sm_lower emitting `SM_PUSH_CHUNK` in place of `SM_PUSH_EXPR`).
      Gate: corpus programs using `*P`, `*(X+1)`, `EVAL(str)`, `CODE(str)`
      run identically under `--jit-run` vs `--sm-run`.  Same pass-set as
      `--ir-run` for those programs.

### Phase D — Pattern construction on the value stack

- [ ] **ME-9 — Pattern primitives.**  `SM_PUSH_PAT_LIT`, `SM_PAT_ANY`,
      `SM_PAT_SPAN`, `SM_PAT_BREAK`, `SM_PAT_NOTANY`, `SM_PAT_LEN`,
      `SM_PAT_POS`, `SM_PAT_RPOS`, `SM_PAT_TAB`, `SM_PAT_RTAB`,
      `SM_PAT_ARB`, `SM_PAT_REM`, `SM_PAT_FAIL`, `SM_PAT_SUCCEED`,
      `SM_PAT_EPS`, `SM_PAT_FENCE`, `SM_PAT_FENCE1`, `SM_PAT_ABORT`,
      `SM_PAT_BAL`, `SM_PAT_CAT`, `SM_PAT_ALT`, `SM_PAT_ARBNO`.  Each
      lowers to a value-stack push of a `DT_P` descriptor — typically
      `<load args from r12 stack>`, `mov rdi, <arg>`, `call rt_pat_<kind>@PLT`,
      `<store rax:rdx as DT_P on r12 stack>`.  Combinators (`SM_PAT_CAT`,
      `SM_PAT_ALT`, `SM_PAT_ARBNO`) pop their input patterns from the
      value stack, call the combinator runtime, push the result.  Gate:
      pattern smoke programs byte-identical between `--jit-run` and
      `--sm-run`.

- [ ] **ME-10 — Capture and user-call.**  `SM_PAT_CAPTURE`,
      `SM_PAT_CAPTURE_FN`, `SM_PAT_CAPTURE_FN_ARGS`, `SM_PAT_USERCALL`,
      `SM_PAT_USERCALL_ARGS`, `SM_PAT_DEREF`, `SM_PAT_REFNAME`.  Bridge via
      libscrip_rt.  Captures pop the inner pattern and capture-spec, push
      the wrapped pattern.  User-call captures register a callback that
      Phase 3 invokes from the byrd-box engine.  Gate: assign-driver,
      capture-bearing patterns from beauty subsystems run under
      `--jit-run`.

### Phase E — Statement execution boundary and Icon/Prolog

- [ ] **ME-11 — `SM_EXEC_STMT` — statement execution boundary.**  Pops
      replacement, subject, pattern from the value stack (one stack — the
      ME-1 unification).  Calls `rt_exec_stmt@PLT` with subject-name (from
      the instruction's `a[0].s`), the popped descriptors, and the
      `has_repl` flag.  The runtime side hands off to the byrd-box engine
      for Phase 3, which may invoke flat-glob invariant blobs via
      `bb_flat.c` EMIT_BINARY into `bb_pool` (the live, proven variant-
      pattern path).  Mode 3 itself emits no inline byrd-box code here;
      Phase 3 stays inside libscrip_rt and bb_pool slots.  Gate: pattern
      smoke programs in `test_smoke_snobol4.sh` and the
      `unified_broker.sh` 49-program set byte-identical between
      `--jit-run` and `--sm-run`.

- [ ] **ME-12 — `SM_BB_PUMP`, `SM_BB_ONCE`, `SM_SUSPEND_VALUE`.**
      Icon/Prolog/Raku support.  Each lowers to a `call rt_bb_<op>@PLT`
      with the appropriate descriptor on `r12` stack.  Gate: Icon and
      Prolog smoke programs (smoke_icon, smoke_prolog) run under
      `--jit-run` byte-identical to `--sm-run`.

### Phase F — Audit and corpus pass

- [ ] **ME-13 — Glob integration audit.**  Verify that when mode 3's
      SM-blob land calls into libscrip_rt's `rt_exec_stmt`, and from there
      Phase 3 jumps into a `bb_pool`-resident flat-glob blob (emitted at
      runtime via `bb_flat.c` EMIT_BINARY), the `r10` discipline is
      preserved end-to-end: SM-blob land does not corrupt `r10` (it never
      writes it), glob entry preamble loads `r10` correctly, glob `ret`
      returns control with the C-ABI honoring `r10`'s caller-saved status
      (the SM-blob caller does not depend on `r10` afterward).  This is
      verification, not new code — a documented audit run, with
      instrumentation if useful, confirming the register convention holds
      across the SM-blob / BB-glob interface.  Gate: full corpus (706
      programs) `--jit-run` byte-identical to `--sm-run`, no `r10`
      clobber observed in any trace.

- [ ] **ME-14 — Full corpus pass.**  `--jit-run` runs every program in the
      `--sm-run` PASS set with byte-identical output across all six
      frontends (SNOBOL4, Snocone, Icon, Raku, Prolog, Rebus).  This is the
      premier-goal completion criterion.  Once it closes, GOAL-MODE4-EMIT's
      `EM-MODE4-IS-MODE3-DUMP` rung reopens.  Gate: corpus PASS counts for
      `--jit-run` ≥ `--sm-run` PASS counts, frontend by frontend.

---

## Prior art / research basis

This section captures the evidence base for the architectural decisions above.
A future agent who finds a decision puzzling should look here before
re-deriving from source.  All material is from the carve-session research
(2026-05-10) reading `archive/backend/bb_boxes.s`, `archive/backend/snobol4_asm.mac`,
`archive/backend/emit_emitters/emit_x64.c`, `.github/archive/GENERAL-SCRIP-ABI.md`,
`.github/archive/EMITTER-X86.md`, `.github/archive/EMITTER-X86-DEEP.md`,
`.github/archive/INTERP-X86.md`, `.github/archive/MILESTONE_BONE_PILE.md`,
`.github/archive/BB-GEN-X86-BIN.md`, and the live `src/runtime/x86/bb_flat.c`.

### Per-box callee-save discipline in `bb_boxes.s` (proven 106/106 oracle)

Every box in the archive's 25-box library obeys one ABI but pushes only the
callee-saved registers it actually uses.  Recognising the size of a box's
prologue is part of recognising what kind of box you are reading:

| Box | Pushes | Why that many |
|-----|--------|---------------|
| `bb_lit`, `bb_any`, `bb_notany` | `rbx, r12` | ζ + one σ holding slot |
| `bb_arb`, `bb_len`, `bb_pos`, `bb_tab`, `bb_rem` | `rbx` | ζ only; result computed direct |
| `bb_alt` | `rbx, r12, r13` | ζ + (σ, δ) of current child |
| `bb_span`, `bb_brk`, `bb_breakx` | `rbx, r12, r13` | ζ + scan state |
| `bb_seq` | `rbx, r12, r13, r14, r15` | ζ + (σ, δ) of left + (σ, δ) of right |
| `bb_arbno`, `bb_dvar` | `rbx, r12, r13, r14, r15` | ζ + frame walker + child result |

Plus `sub rsp, 8` (or 16) for stack alignment + per-call σ/δ holding slots.
The pattern is consistent: `rbx` is always the ζ pointer; `r12..r15` carry
per-call intermediate values that must survive across child-box `call`
sequences.  This is the discipline mode-3 SM-blob emission must preserve
when its blobs `call` into byrd-boxes — the boxes save what they touch; the
SM-blob caller's r12 (= `SM_State*` in our convention) survives because the
box restores it like any other callee-saved register.

### The `Σ Δ Ω` global-subject ABI

Subject text and cursor are not passed as arguments to boxes.  They live in
`.bss` globals:

```
extern Σ          ; uint8_t *Σ      — subject text base pointer
extern Δ          ; int      Δ      — current cursor position
extern Ω          ; int      Ω      — subject length (the right wall)
```

Every box reads `Σ`, `Δ`, and `Ω` directly via `[rel Σ]`, `[rel Δ]`, `[rel Ω]`.
On match success a box advances `Δ`; on backtrack it restores the saved value.
`bb_flat.c` flat-globs load `Δ`'s address into `r10` at glob entry not
because the glob owns `Δ` (it doesn't — `Δ` is one global), but because
inside a flat-glob the *per-box local state* (saved cursors, frame stacks)
sits in a consolidated `.data` block addressed via `r10`, and the boxes'
direct `[rel Δ]` access continues to reach the one true cursor.  Two
separate addressing modes coexist: globals via `[rel SYM]`, locals via
`[r10+N]`.  Mode-3 SM-blob land is unaffected — it neither reads `Σ/Δ/Ω`
nor writes them; that is byrd-box-engine business.

### Box return ABI: success via value, not via continuation-jump

`GENERAL-SCRIP-ABI.md` (the cross-language ABI design, 2026-03-27) proposed
γ-jump-address and ω-jump-address in `rdx`/`rcx` at call time, with the
callee `jmp [rdx]` on success and `jmp [rcx]` on failure.  `bb_boxes.s`
shipped a simpler convention: the caller does a normal `call`, and the
callee returns with `rax:rdx = σ:δ` (success) or `eax=99, edx=0` (failure,
`DT_FAIL`); the caller `test r12, r12 ; jz <ω-label>` (or `cmp eax, 99 ; je
<ω-label>`) right after the call.  Both are valid Byrd-box realizations;
the simpler one is what the 106/106 oracle ran on, and it is what mode-3
SM-blob land calls into.  We do not change this.

Cross-language implication (for future GOAL-MODE3-EMIT-JVM /
GOAL-MODE3-EMIT-NET work, not in scope here): on JVM/.NET, return-by-value
maps naturally to a return-tuple; the continuation-jump version cannot be
expressed without trampolines.  Sticking with return-by-value on x86 keeps
the cross-backend translation straight.

### `DESCR_t = 16 bytes, returned in rax:rdx` via C-ABI struct-return

`DESCR_t` is 16 bytes (an enum tag + variant union with a string pointer + a
size, or an int, or a real, or a pointer).  The C-ABI passes 16-byte structs
in registers when returning from a function — specifically in `rax:rdx`.
That is why `NV_GET_fn`, `pat_lit`, every box, every constructor in
`snobol4_pattern.c` "naturally" returns `rax:rdx` without us having to
arrange it: the C compiler does so.  The SM-blob convention inherits this:
every PLT call from emitted code yields its `DESCR_t` result in `rax:rdx`,
and the blob's job is to store both halves onto the value stack at
`[r12+sp]` and `[r12+sp+8]`.  If a future bug shows up where only half a
`DESCR_t` is being stored, this paragraph is the reminder of which half is
which.

### Why we re-purpose `r12` from its legacy role

`archive/backend/emit_emitters/emit_x64.c` used `r12` as the per-invocation
DATA-block pointer.  The legacy comments are explicit (`r12 points to this
invocation's DATA block`, `mov r12, rax ; r12 = new DATA ptr`).  Mode-3 does
not preserve that role for `r12`.  Instead, mode-3 splits the legacy
`r12=DATA` into two: SM-blob land uses `r12 = SM_State*` for the value
stack; BB-glob land uses `r10 = data-region pointer` for box locals
(precisely what the legacy `r12` did, but renamed to free `r12` for the SM
side).  Both registers are callee-saved in the SM context (we never write
them inside emitted PLT call sequences expect at the boundaries we define).
A future agent reading `emit_x64.c` and finding `r12 = DATA` should
recognise this as legacy and look here for the new role assignment.

### Why `r10` for the glob data region (C-ABI consequence)

`r10` is *caller-saved* in the System V x86-64 C-ABI.  This means: any C
function we PLT-call may clobber `r10` without saving it.  Two consequences
follow that are not obvious until stated:

1. **SM-blob land must not depend on `r10` surviving a PLT call.**  SM-blob
   land does not use `r10` at all — neither read nor write — and so this is
   a non-issue *for SM-blob land*.
2. **BB-glob land must reload `r10` at every glob entry.**  If a glob makes
   any external call (e.g. a capture function callback that re-enters the
   broker), the callee may clobber `r10`; on return, the glob must not
   assume `r10` is still pointing at its data region.  The current
   `bb_flat.c` convention loads `r10` *once at glob entry* on the
   assumption that flat-globs do not make external calls inside themselves
   — which is part of what makes a sub-tree "invariant" and eligible for
   flat-glob emission in the first place (`flat_is_eligible_node(p)`).
   Variant nodes that need external calls do not get flat-globbed.

The implicit save-free boundary works *because* of (1) — the SM caller
doesn't care what the glob did to `r10`, and the glob doesn't care what the
SM caller had in `r10` before.  This is a benefit of `r10`'s caller-saved
status, not in spite of it.

### Two-stack reconciliation (fuller version of the ME-1 rationale)

SIL's `PATBCL/PATICL` (pattern code list / pattern instruction list) and
`PDLPTR/PDLHED` (push-down list — the value stack) are separate because in
SIL they serve different *executors*: PATBCL is walked by SCNR (the
scanner); PDLPTR is walked by INTRP (the interpreter).  Two stacks for two
machines.

In SCRIP the equivalent split exists, but it is not between two value
stacks — it is between the value stack (built by the SM dispatch loop or by
mode-3 native code) and the byrd-box graph (executed by the byrd-box
engine).  The byrd-box graph is the data: it is a tree of `ζ` state structs
linked by `bb_child_t.fn` function pointers.  Construction of that tree is
plain value arithmetic done by `SM_PAT_*` opcodes, and value arithmetic
belongs on the value stack — not on a third stack that exists only to be
moved into the value stack by `SM_PAT_BOXVAL`.

The proof: every `SM_PAT_*` constructor (`pat_lit`, `pat_cat`, `pat_arbno`,
…) returns a `DESCR_t` whose `v` field is `DT_P` and whose `.ptr` is the
allocated ζ struct.  These descriptors are first-class.  `sm_pop()` and
`sm_push()` already handle them — the type tag is in the descriptor, not in
the stack's identity.  Once `SM_PAT_*` opcodes simply push their results to
the value stack, `SM_EXEC_STMT` pops the pattern descriptor the same way it
pops subject and replacement, and the SIL-style two-machine split is
preserved at the right boundary (Phase 2 vs Phase 3, not pat-stack vs
value-stack).

This is why ME-1 is the opening rung: until the pat-stack is gone, mode-3
SM-blob emission has to deal with two distinct stack-anchoring registers
(one for value-stack, one for pat-stack) and lose the "`r12` is *the*
stack" simplicity that makes everything below tractable.

### EXPVAL re-entrancy (relevant to ME-8)

`MILESTONE_BONE_PILE.md`'s RUNTIME-6 section spells out the SIL ground
truth for `EXPVAL`: when evaluating an EXPRESSION-typed descriptor, SIL
saves the entire interpreter state on a save stack before invoking the
expression body, and restores it on exit (success or failure).  The state
saved includes `OCBSCL/OCICL` (current code block + offset), `PATBCL/PATICL`
(pattern code state), `WPTR/XCL/YCL/TCL` (work pointers, three temp
descriptors), `MAXLEN/LENFCL` (string length bookkeeping), `PDLPTR/PDLHED`
(value stack head), `NAMICL/NHEDCL` (naming stack head), and specifier
slots (`HEADSP/TSP/TXSP/XSP`).

The correctness property: EXPVAL must be fully re-entrant — an EXPRESSION
can contain a call to `EVAL()` which calls EXPVAL again.  The save/restore
must handle arbitrary nesting.

For mode-3 ME-8 (`SM_CALL_CHUNK` consumer): the SM-blob land equivalent of
EXPVAL's save/restore is the return-frame push that `SM_CALL_CHUNK` does
before transferring control to the chunk's entry_pc.  The return frame
needs to capture exactly the state that a re-entered EVAL/CODE could
clobber: the value-stack depth at call time (so `SM_RETURN` can detect
balance violations), the SM-PC to return to, and — critically — anything
in `SM_State` that is mutated by sub-expressions (currently just
`last_ok`; verify against `sm_interp.c` at ME-8 entry).

If sub-expressions can mutate the pat-stack (after ME-1 there is no
pat-stack, so this concern dissolves), or any global like `g_jit_halted`,
those mutations either need to be captured in the return frame or proven
to be already-correct under nesting.  This is the audit ME-8 must do
before its first byte of code is written.

The SIL "save the universe" approach is the safe default; SCRIP can be
narrower because most of SIL's saved state has no SCRIP equivalent (we do
not have OCBSCL/OCICL — the SM_Program is a single flat array; we do not
have PATBCL/PATICL — the pat-stack is gone after ME-1; we do not have
specifier slots — `DESCR_t` is the universal value).  The minimum viable
return frame is `{ return_sm_pc, value_stack_sp_at_call, last_ok }`.

### `PROG_INIT` vs `sm_jit_run` entry: why no callee-save spill

`snobol4_asm.mac`'s `PROG_INIT` macro (program entry in the legacy
asm-emitted binary) pushes all five callee-saved registers
(`r15, r14, r13, r12, rbx`) plus `rbp` before sub-rsp'ing for local
descriptors:

```nasm
PROG_INIT:
    push r15 ; push r14 ; push r13 ; push r12 ; push rbx
    push rbp ; mov rbp, rsp ; sub rsp, 56 ; call stmt_init
```

The legacy did this because the emitted code *used* `r12..r15` and `rbx` as
implicit working registers across the whole program — they needed to be
preserved on return to `crt0`'s `main()` caller.

Mode-3's `sm_jit_run` does not need this spill at entry.  Reason: SM-blob
land uses only `r12` as a fixed register, set once at sm_jit_run entry, and
the C-ABI considers `r12` callee-saved — meaning *`sm_jit_run` itself*
(which is a C function) is responsible for saving/restoring it.  The
compiler-generated prologue/epilogue of `sm_jit_run` already does this.
The SM-blob code that runs inside the `jmp SEG_CODE_entry` does not need
its own additional spill; it inherits the safety of the surrounding C
frame.

Byrd-boxes called from SM-blob land do their own per-box callee-save spill
(per the table at the top of this section), so `r12 = SM_State*` survives
those calls.  Boxes that touch `r12` save it like any other callee-saved
register; boxes that do not touch it leave it alone.

The conclusion: mode-3 SM-blob entry is `mov r12, &state ; jmp
SEG_CODE_entry`, not `push r12 ; … ; mov r12, &state ; … ; pop r12`.
The C surrounding context provides the spill.

---

## Definitions

- **mode 3 / `--jit-run` / `--sm-native`** — third SCRIP execution mode: emit
  native x86 into `SEG_CODE`, jump in, run in-process.  No emit to disk.  ARCH-x86's "Stack machine (SM_Program)" + "Dual-mode emitter" requires this
  to be a real per-instruction native emitter; today it is a threaded-call
  C dispatch loop.  This Goal fixes that.
- **SM-blob** — the native x86 bytes emitted for a single `SM_Instr` in
  `SEG_CODE`.  Together the SM-blobs form a flat native program threaded
  by `jmp`/`call`/`ret`, walked by `r12`-anchored stack ops.
- **BB-glob** — a contiguous run of flat-globbed invariant byrd-boxes
  emitted as one self-contained x86 blob with one shared `r10`-anchored
  data region.  Today emitted into `bb_pool` slots at runtime by
  `bb_flat.c` EMIT_BINARY.  Mode 3 does not statically emit globs — they
  remain dynamic per statement.
- **glob boundary** — the entry preamble of a BB-glob, where `r10` is
  loaded.  The save/restore discipline is "every entry loads `r10`;
  callers do not use `r10` and so need no explicit save."
- **`libscrip_rt.so` / `rt_*@PLT`** — runtime support library carrying NV
  table, pattern matcher, GC, BB broker, generator/Prolog backtracking,
  arithmetic helpers, string builtins.  Mode-3 emitted code reaches all
  language semantics through PLT calls into this library.

---

## Watermark

**GOAL-MODE3-EMIT carved sess 2026-05-10 (Claude latest).**  Premier-goal
status declared by Lon: most other work pauses until this Goal closes;
`GOAL-ICON-BB-COMPLETE` is the only sibling that stays active.  Architecture
locked in this session through close reading of `ARCH-x86.md`, `ARCH-SCRIP.md`,
`archive/backend/bb_boxes.s` (proven 106/106 25-box library), the
`GENERAL-SCRIP-ABI.md` ABI in `.github/archive/`, the live `bb_flat.c`
flat-glob discipline (sess 2026-05-10 `EM-FORMAT-BB-DATA-CONSOLIDATE`),
and the `g_pat_stack` audit confirming SM_PAT_BOXVAL is a no-op move
between two stacks that should be one.  Decisions: (1) one value stack, no
pat-stack; (2) `r12 = SM_State*`, `r10` = per-glob data region (matches
existing convention), `rbp` = chunk frame for DEFINE'd chunks; (3) variant
patterns stay dynamic, no static dump of `bb_pool` contents in mode 3 or
mode 4; (4) deferred-eval consumer (ME-8) lands after GOAL-CHUNKS-STEP17
closes so the opcode shape is stable; (5) byrd-box ABI from `bb_boxes.s`
preserved verbatim (rdi=ζ, esi=entry, rax:rdx=σ:δ, callee-saved
rbx/r12/r13/r14/r15).

No code landed this session — Goal-file authorship only.  Baseline gates
at session start: smoke 7/7 PASS, unified_broker 49/49 PASS,
em_beauty_subsystems_mode4 PASS=4 FAIL=13 (frozen as tripwire — mode 4 is
not touched during this Goal).  one4all @ `f78d366c`.

**Addendum sess 2026-05-10 (same session, second commit):** added
`## Prior art / research basis` section (~230 lines) capturing the evidence
base for the architectural decisions above — per-box callee-save discipline
from `bb_boxes.s`, the `Σ Δ Ω` global-subject ABI, the box-return ABI
(value-via-rax:rdx vs the GENERAL-SCRIP-ABI's continuation-jump proposal),
`DESCR_t` 16-byte C-ABI struct-return convention, the `r12` re-purposing
from its legacy `emit_x64.c` "DATA block ptr" role, why `r10`'s
caller-saved C-ABI status makes the glob save-free boundary work, the
fuller SIL/SCRIP two-stack reconciliation, EXPVAL re-entrancy detail
relevant to ME-8's return-frame design, and why `sm_jit_run` entry needs
no explicit callee-save spill.  A future agent puzzled by any decision in
the Architectural target section should consult this before re-deriving
from source.

**Addendum sess 2026-05-10 (third commit, this session):** ME-2 ✅ landed
at one4all `babf76be`.  `sm_jit_run` now establishes `r12 = SM_State*`
via `asm volatile` inside the dispatch loop, just before transferring
control to the SEG_CODE stub.  Header comment in `sm_codegen.c` documents
the full mode-3 register convention.  No emitted code reads or writes
`r12` yet — today's threaded-call stubs are C functions that reach
`SM_State` via `g_jit_state`.  ME-3 is the consumer: per-instruction
native blobs that address the value stack as `[r12 + offset]` and never
reload `r12`.  Gates clean: smoke 7/7, unified_broker 49/49.  one4all
@ `babf76be`.

**Addendum sess 2026-05-10 (fourth commit, same session as ME-2):** ME-3 ✅
landed at one4all `aca47e6c`.  Per-instruction native blob emitter
replaces the threaded-call C dispatch loop; `SEG_CODE` now holds 30-byte
native blobs (one per `SM_Instr`) threaded by `jmp`/`call`/`ret`, not a
`uint8_t**` pointer array.  `sm_jit_run` is a six-line C function:
load `r12 = SM_State*`, `entry()` into the shared trampoline at the head
of `SEG_CODE`, return when `SM_HALT`'s blob `ret`s out.  Per-PC side
table `g_blob_offsets[]` built during emit; used now for `SM_JUMP` rel32
patching in pass 2, reusable by mode-4's SEG_CODE serializer.

Stack-alignment correctness: the initial 22-byte standard blob (no
`sub rsp,8` / `add rsp,8` around `call rax`) segfaulted on arith and
goto_s because `sm_jit_run`'s `entry()` C call leaves `rsp ≡ 8 (mod 16)`
and a naive `call rax` would enter the handler at `rsp ≡ 0`, faulting on
the first `movaps` in printf/vsnprintf/GC alloc.  Fix: pad with
`sub rsp,8` / `call rax` / `add rsp,8` around the call, restoring the
ABI's `rsp ≡ 8` invariant on callee entry.  Blob grew 22→30 bytes;
header comment in `sm_codegen.c` documents the discipline.

Verification: smoke 7/7, unified_broker 49/49, SN-7 beauty 26/25
unchanged baseline.  Extended byte-identity (`--sm-run` vs `--jit-run`)
on arith, concat, goto_s, unconditional jump, vars+arith, 100k-iter
loop, pattern replacement, DEFINE'd function — all pass.  Perf
microbench 100k counter loop: ~26% faster (sm-run 110ms → jit-run 82ms);
modest because handlers still do most work via `call rax`.  ME-4
inlines arithmetic/stack ops and the gap widens.  Mode-4 gates
SUSPENDED per Gates section; pre-existing FAIL state unchanged.
SEG_DISPATCH slab still mmap'd but no longer written/sealed — sits
unused; harmless.  one4all @ `aca47e6c`.

**Next:** ME-4 — Stack-machine arithmetic and string ops.  `SM_ADD`,
`SM_SUB`, `SM_MUL`, `SM_DIV`, `SM_MOD`, `SM_CONCAT`, `SM_COERCE_NUM`,
`SM_PUSH_NULL`, `SM_PUSH_VAR`, `SM_STORE_VAR`.  Each opcode lowers to
its inline native sequence — typically `<load args from r12 stack>`,
`mov edi, kind`, `call rt_<name>@PLT`, `<store result back through r12
stack>`.  Same shapes as today's `sm_macros.s` but inline bytes per
instruction, not pointer-array indirection.  Gate: arithmetic smoke
programs (`arith_sm` etc. in `test_smoke_snobol4.sh`) byte-identical
between `--jit-run` and `--sm-run`.  Note: now that ME-3's per-
instruction blob model is proven, ME-4's job is to swap selected blobs'
"call C handler" middle for direct inline native — same blob shape,
same alignment discipline, different bytes in the middle.

**⚠ Emergency handoff sess 2026-05-10 (Claude latest): ME-4 PARTIAL,
gates clean but a downstream bug is live.**  Work done this session,
not yet committed to a closed-rung pointer:

1. **Architecture pivot:** the goal-file's literal recipe `call rt_<name>@PLT`
   is unworkable because `scrip` does not link against `libscrip_rt.so` —
   `rt_*` symbols don't exist in the scrip process.  Three options were
   surveyed with Lon: (A) refactor scrip to dynamic-link libscrip_rt
   (multi-session reshape, ~381 symbol-set deduplication), (B) static-link
   rt.c into scrip (~10 lines of ifdef stubs to break duplicate-symbol
   chain), (C) keep using scrip-side handlers but unify via a backend
   abstraction inside rt.c and inline the stack-pop/push around new
   value-in/value-out helpers (`me4_*` family).  Lon picked **Option C**.

2. **rt.c backend abstraction landed.**  Added `rt_vstack_ops_t` public
   ABI in `rt.h` (pointer-form, DESCR_t-opaque) and the matching plumbing
   in `rt.c`: default backend = static `g_vstack[]` / `g_last_ok` (mode-4
   unchanged by construction); `rt_set_vstack_backend(ops)` /
   `rt_get_default_vstack_backend()` exposed.  All 25 `rt_*` function
   bodies' direct `g_vstack` / `g_vtop` / `g_last_ok` references swept
   through `g_ops` (auto-script + manual fixes; one false-positive fixed
   in `rt_set_last_ok`).  libscrip_rt.so builds clean; mode-3 + mode-4
   baseline gates unchanged (smoke 7/7, unified_broker 49/49,
   mode-4 FAIL=13 frozen).  Note: `g_pat_stack[]` inside rt.c is NOT
   in the backend abstraction this rung; it's libscrip_rt-internal
   variant-pattern scratch and never seen by mode-3 (mode-3 builds
   patterns on the value stack since ME-1).  Future rung may extend
   the backend to cover it.

3. **Variable-size blobs landed.**  The fixed 30-byte ME3_BLOB_SIZE
   stride is gone.  Per-PC dispatch table changed from `g_blob_offsets[]`
   (size_t byte-offsets) to `g_blob_addrs[]` (uint8_t* absolute
   addresses).  Trampoline updated: indirect-jump through
   `g_blob_addrs[pc]` instead of `imul rax, rax, 30 + add base`.
   Stride encoding via imm8 imul is gone.  Trampoline now 23 bytes
   (was 32).  No NOP padding in any blob.  emit_halt_blob = 6 bytes
   (was 30), emit_jump_blob_skeleton = 14 bytes (was 30),
   emit_standard_blob = 28 bytes (was 30).  Mode-4-future serialization
   benefits: each blob is exactly the bytes it needs; no padding to
   strip.  SM_JUMP rel32 patching updated to compute relative offset
   from absolute addresses (was offset-based).

4. **ME-4 helpers + blobs landed.**  Added `me4_arith` / `me4_concat`
   / `me4_coerce_num` / `me4_push_var` / `me4_store_var` / `me4_push_null`
   value-in/value-out helpers in `sm_codegen.c` (DESCR_t in / DESCR_t
   out via SysV ABI; side effect on `g_jit_state->last_ok` only).
   Emitted inline-native blobs for all 10 named opcodes
   (SM_ADD/SUB/MUL/DIV/MOD/CONCAT/COERCE_NUM/PUSH_NULL/PUSH_VAR/STORE_VAR)
   that load args from `[r12]`-anchored stack into ABI arg regs, call
   the matching me4_* via imm64 (SEG_CODE↔scrip-text rel32 unreachable
   by mmap distance, confirmed empirically), store result back through
   `[r12]`-anchored stack.  All blobs defensively reload stack base
   after the C call (most helpers can't realloc; cheap insurance).
   Wired in `sm_codegen` dispatch loop.

5. **Gates: smoke 7/7, unified_broker 49/49 PASS.**  Mode-4 gate
   suspended (per ME-3 Gates section).  Microbench: 100k counter
   loop sm-run 116ms → jit-run 79ms (~32% faster, vs ME-3's ~26%).

6. **🐛 BUG diagnosed but unfixed: multi-statement arithmetic
   programs abort with `realloc(): invalid next size`.**  Reproducer:
   any program with multiple expressions per loop iteration involving
   PUSH_VAR.  Root cause partially identified late in session:
   `sm_interp.c:295` resets `st->sp = 0` between statements
   (`/* reset value stack at each statement boundary */`) — mode-2
   contract.  Mode-3's ME-3 blobs did not replicate this discipline;
   the latent bug was hidden because handler-side `sm_push` does
   bounds-check + realloc.  ME-4's inline-native PUSH_NULL and
   PUSH_VAR blobs write to `stack[sp]` directly without the
   bounds check; sp creeps past the initial `stack_cap=16` and
   corrupts the heap.  Same gates pass because they don't exercise
   the multi-expression-per-statement pattern.

   **Fix candidates (next session):** (a) emit a per-statement
   sp-reset blob at SM_STNO (replicates mode-2 contract); (b) add
   inline bounds-check + slow-path call to sm_push in PUSH_NULL /
   PUSH_VAR blobs; (c) pre-grow `SM_State.stack` to a safe bound
   at sm_jit_run entry (compute high-water mark in sm_lower).
   Option (a) is architecturally honest — mode-3 should match the
   inter-statement contract mode-2 enforces.

7. **Register layout was NOT redesigned this session — significant
   regret.**  When Lon picked Option C ("variable-size blobs"), I
   should have stopped and proposed a unified register convention
   first: `r12` = SM_State header (locked, per ME-2 already), `r13`
   = SM_State.stack base (the value-stack pointer, locked across all
   blobs except after potentially-realloc'ing calls), with r14/r15
   reserved for locals / heap-frame / chunk-frame respectively.
   Instead I emitted blobs ad-hoc, each one reloading `[r12]` (stack
   base) into a temporary every time.  Each blob wastes ~25 bytes on
   redundant base-loads and sp-arithmetic that a register convention
   would put in a once-loaded register.  This regression-tolerant but
   sub-optimal shape is now the live mode-3 emitter.  A future rung
   ("ME-4b" or similar) should re-emit with the locked register
   convention, expecting blob sizes to shrink ~30% and another
   measurable perf win.  See full discussion in session log.

**State at handoff:** one4all working tree dirty; no commit pushed.
`src/runtime/rt/rt.c` +178/-65, `src/runtime/rt/rt.h` +46/-0,
`src/runtime/x86/sm_codegen.c` +620/-134.  ME-4 marked PARTIAL below
(stays `- [ ]`).  Sibling Goals (esp. GOAL-CHUNKS) untouched; mode-4
frozen as tripwire untouched.  Gates: smoke 7/7, unified_broker 49/49,
mode-4 PASS=4 FAIL=13 frozen.  Continuation reads this addendum, fixes
the realloc bug per the Fix candidates above, runs the failing
reproducer (multi-statement arith — see commit body for canonical
input), and then closes ME-4 only after that passes byte-identical.
The register-layout redesign is the recommended **first** rung after
ME-4 closes — call it ME-4b — so the rest of the rungs land against
the locked convention rather than inherit the ad-hoc one.

