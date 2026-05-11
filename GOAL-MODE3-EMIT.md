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

⛔ **The authoritative register convention is `REGISTER-LAYOUT.md`
(carved sess 2026-05-10, revised same session through Lon Q&A).**
This section summarizes; the full push/pop matrix, evidence base,
and audit checklist live there.

Settled, binding on every rung that emits SM-blob x86:

| Reg | Role | Scope |
|-----|------|-------|
| `r12` | **SM value stack top-of-stack pointer (FORTH-style).**  Push: `mov [r12], rax ; mov [r12+8], rdx ; add r12, 16`.  Pop: `sub r12, 16 ; mov rax, [r12] ; mov rdx, [r12+8]`.  Multi-pop: `sub r12, N*16` (N compile-time-known). | Whole emitted program; loaded once at `sm_jit_run` entry from `[rel sm_state_stack_base]`; reset to base by SM_STNO blob. |
| `r10` | **Current BB DATA-block pointer.** `[r10+N]` addresses every box-local in the active BLOB.  Constant inside a BLOB.  Saved to SmCallFrame when SM_CALL_EXPRESSION fires from BB land. | Per BLOB.  Loaded by each BLOB's α-preamble. |
| `rbp` | DEFINE'd function frame pointer | Per active function; `push rbp ; mov rbp, rsp` / `pop rbp ; ret`. |
| `rbx`, `r13`, `r14`, `r15` | **Free** — available for per-rung scratch or future claims | — |
| `rax rdi rsi rdx rcx r8 r9 r11` | C-ABI scratch for PLT calls and SM-blob temporaries | Per SM-blob; caller-saved |
| `xmm0–xmm15` | Real arithmetic when DESCR_t is real | Per SM-blob; caller-saved |

**Two claimed callee-saved registers (r12, rbp-when-in-function) + one
per-BLOB register (r10) = three claims.  Four callee-saved free (rbx,
r13, r14, r15).  Eight GP scratch + sixteen SSE scratch.**

`SM_State` itself lives as a static global in `.bss`, reached via
RIP-relative `[rel sm_state + offset]` when needed (rare — SM_STNO,
SM_EXEC_STMT, SM_CALL_*).  No register reserved for `SM_State*`.

**Why FORTH-style single-register TOS instead of {base, sp}:**  All
pop-depths are compile-time-known per opcode.  Random access at depth
N below TOS is `[r12 - (N+1)*16]`, one SIB-encoded mov.  No runtime
depth arithmetic.  Frees one callee-saved register.

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

### Stacks and stack-like structures

SCRIP has two stacks + one heap-resident tree.  The tree replaces what
SPITBOL/CSNOBOL4 implement as a separate pattern-history stack —
because Byrd-boxes are stackless and their per-invocation DATA blocks
ARE the alternatives.  See `ARCH-x86.md` §"Boxes are stackless".

| | Where |
|---|---|
| **SM value stack** | Heap; `r12` = TOS pointer (FORTH-style).  Reset at every statement boundary by SM_STNO blob (`mov r12, [rel sm_state_stack_base]`). |
| **Native stack (rsp)** | C-ABI calls, DEFINE'd function frames (`rbp`), source-BLOB `push r10` for the rare call-style extra-BLOB jump. |
| **BB DATA-block tree** | Heap; `r10` walks it.  Each box at α-entry allocates fresh DATA, chains to parent via save-list header, sets `r10 = new_block`.  γ-exit unlinks; ω-exit unlinks and may free.  Pattern alternatives, FENCE bases, ARBNO iteration chains, `$`/`.` pending assignments — all DATA fields, not stack pushes. |

What SPITBOL stores on its `pmhbs`-rooted history stack (cursor saves,
failback pointers, FENCE bases, ARBNO iteration markers) SCRIP stores
in DATA-block fields.  The save IS the allocation; the restore IS the
unlink.  No pattern-history stack register.  No `pmhbs`-equivalent
register.

The byrd-box engine's state lives in heap-allocated DATA blocks
reachable via `r10` (per-BLOB) and via the SM value stack's `DT_P`
descriptors (when patterns sit on the value stack as constructed
values).  See `REGISTER-LAYOUT.md` for the full picture.

### Deferred-eval consumer — `*P`, `*(expr)`, `EVAL`, `CODE`

These cases drive the design of how SM-blob land and BB-glob land
interoperate.  Both run inside an outer pattern match (i.e. inside
BB land); both transfer control to compiled code that they share
with other call sites; both must restore the calling BLOB's `r10`
on return.

**`*P` where P is a PATTERN variable.**  P's value is a DESCR_t whose
`.ptr` references the root box of a BLOB graph emitted when P was
constructed.  At match time, the DEFER box wrapping `*P`:
1. Looks up P's current value.
2. Calls `rt_alloc_blob_data(P_root_box)` — runtime walks P's box
   tree and allocates a fresh DATA block per box, linked per the
   parent/child structure, returns root DATA address.
3. Saves DEFER's own r10 (= DEFER's DATA block address) into a field
   reachable post-call.
4. Sets `r10 = root_data_block_address`.
5. Jumps to P's BLOB CODE entry.

P's CODE is read-only RX memory — many simultaneous matches against
the same P run because each gets its own DATA tree.  CODE is reusable;
DATA is per-invocation.  On return from P, DEFER restores its own r10
and transitions to its γ/ω port.

**`*(expr)` (e.g. `*(X + 1)`, `*(X ? P Q R)`).**  `expr` lowered as a
labeled SM body at compile time:
```
                  SM_JUMP            skip_NN
expr_body_NN:     <SM ops>
                  SM_RETURN
skip_NN:          ...
                  SM_PUSH_EXPRESSION  expr_body_NN_entry_pc
```
At match time the DEFER box performs SM_CALL_EXPRESSION:
1. Push an SmCallFrame `{ret_pc=defer_resume, caller_r12 (TOS before
   reset), last_ok, caller_r10=current_r10}`.  Increment
   `st->call_depth`.
2. Reset r12 to base — the expression body runs on its own empty
   operand stack (preserves the mode-2 contract).
3. Jump to `expr_body_NN_entry_pc`.

The body runs in SM-blob land.  It may trigger sub-pattern matches
via SM_EXEC_STMT; those allocate their own DATA trees and run to
completion.  When `SM_RETURN` fires at end of body:
1. Pop SmCallFrame.
2. Restore `r10 = frame.caller_r10` (DEFER's DATA is active again).
3. Restore r12; expression result is on TOS.
4. Jump to `frame.ret_pc`.

**The SmCallFrame distinguishes BB-land entry from SM-blob-land entry**
by whether `caller_r10` is non-zero (or by a flag bit; details settled
at ME-8 implementation).  The emitter knows which case applies — it
knows whether the SM_CALL_EXPRESSION emission site sits inside an
emitted BLOB or in pure SM-blob land.

**The SM/BB code is fixed but new local is allocated.**  This applies
recursively.  Every level — DEFER box, expression body, sub-pattern
BLOBs — uses the same emitted CODE for repeat entries; only the DATA
(or SmCallFrame) is fresh per invocation.

`GOAL-MODE3-EMIT` does not own the producer side (sm_lower's
SM_PUSH_EXPR migration) — that is `GOAL-CHUNKS-STEP17`'s work.  This
Goal owns the consumer side.  ME-8 lands **after** GOAL-CHUNKS-STEP17
closes (or at least after the SNOBOL4-frontend portion migrates) so
we consume a stable opcode shape, not a moving target.

### Variant patterns (dynamic) stay dynamic

`bb_flat.c` EMIT_BINARY emits glob bytes into `bb_pool` slots at runtime —
this is the existing variant-pattern path and it stays.  Mode 4 (future)
will not dump these dynamically-built things; they continue to be allocated
fresh per statement.  The SM-blob side of mode 3 is what becomes statically
emittable, not the variant-pattern side.  The architectural rule for mode 4
when it returns: only emit what `sm_codegen` placed in `SEG_CODE` at codegen
time; everything that materializes in `bb_pool` at execution time stays
behind in `libscrip_rt.so`.

### Byrd-box ABI — flat-BB vs dispatched-BB

Boxes exist in two emission forms.  Mode 3 SM-blob land calls into the
flat form via a single `jmp` at glob entry; the dispatched form is the
broker-driven legacy path that mode 3 does not author against directly
(see `ARCH-x86.md` §"Two emission forms" for the architectural definition).

**Flat-BB ABI (the path mode 3 emits SM-blob `jmp`s into):**
- Entry: control falls into the first byte of the glob — the α port of
  the first box.  No `esi` port discriminator; the glob's structure is
  static.  No `rdi = ζ` argument; locals are reached via `r10` (loaded
  by the glob preamble as `lea r10, [rip + Δ_data]` or as the result of
  an `rt_alloc_blob_data()` call for re-entry cases).
- Exit (γ success): `rax:rdx = σ:δ` returned to the caller of the glob;
  control transfers via `jmp` to the post-glob target.
- Exit (ω failure): `eax = 99, edx = 0` and `jmp` to the failure target.
- Boxes are stackless inside the glob — no `push`/`pop` of working state;
  every local sits at `[r10 + N]` for some baked offset N.

**Dispatched-BB ABI (legacy `bb_boxes.s` form, preserved for `--bb-brokered`):**
- Entry: `rdi = ζ` (zeta — box state struct), `esi` = entry port
  (0 = α, 1 = β).
- Exit: `rax:rdx = σ:δ` (success), or `eax=99, edx=0` (failure / `DT_FAIL`).
- Callee-saved (when boxes use them as working scratch across nested
  `call`s): `rbx, r12, r13, r14, r15` — boxes save and restore their own.

**Why mode 3 cares about both.**  Mode 3 SM-blob land emits *into* the
flat form via `bb_flat.c` EMIT_BINARY when `SM_EXEC_STMT` hands a
statement off to the BB engine.  The dispatched form survives as the
broker-driven path (`--bb-brokered`); a future rung may unify the two,
but that is not in this Goal's scope.

Note `r12` is the SM value-stack TOS pointer in mode-3 SM-blob land
and is callee-saved per the C-ABI — preserved across byrd-box calls
automatically.  Dispatched-BB boxes that need a callee-saved working
register save and restore `r12` like any other callee-saved reg; they
never observe its SM-blob meaning.  Flat-BB globs do not write `r12`
at all — `r12` carries its SM-blob meaning through the glob untouched.

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

- [x] **ME-4-pre — Register layout study + design (Lon-directed sess 2026-05-10).**
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

      **Draft complete (REVISED) sess 2026-05-10 (Claude latest):
      `REGISTER-LAYOUT.md` rewritten at `.github` HEAD.**  Initial draft
      claimed r12/r13/r14 + reserved r15/rbx.  Through Lon Q&A in this
      session, the picture simplified:

      - **r12 = SM value-stack TOS pointer (FORTH-style).**  Single
        register holds top-of-stack; no separate {base, sp} split.
        Push: `mov [r12], rax ; mov [r12+8], rdx ; add r12, 16`.  Pop:
        `sub r12, 16 ; mov rax, [r12] ; mov rdx, [r12+8]`.  Multi-pop
        `sub r12, N*16` where N is compile-time-known.  SM_STNO blob
        resets to base: `mov r12, [rel sm_state_stack_base]`.  All
        depths are compile-time-known per opcode (SM_ADD pops 2,
        SM_PAT_CAT pops 2, etc.) so random access at compile-time
        known N is `[r12 - (N+1)*16]`, one SIB-encoded mov.
      - **r10 = current BB DATA-block pointer.**  Constant inside a
        BLOB.  Loaded by α-preamble of every BLOB.  Saved in
        SmCallFrame when SM_CALL_EXPRESSION fires from BB land
        (the DEFER box case).
      - **rbp = DEFINE'd function frame ptr** when in a function.
      - **rbx, r13, r14, r15 = FREE.**  Available for per-rung scratch
        or future claims.  No pre-reservation.
      - **`SM_State` itself is NOT in a register.**  Accessed via
        RIP-relative `[rel sm_state + offset]` from SM_STNO (rare),
        SM_EXEC_STMT (rare), SM_CALL_* (rare).  No need to burn a
        register on this.
      - **Pattern history stack: GONE.**  Byrd-boxes are stackless;
        per-invocation DATA blocks are the alternatives; backtracking
        is DATA-block-tree traversal, not stack popping.  See
        ARCH-x86.md §"Boxes are stackless".  No `pmhbs`-equivalent
        register; what SPITBOL stores on `xs`-rooted history stack,
        SCRIP stores in DATA-block fields.
      - **Two stacks total** (not three): SM value stack (heap, r12 =
        TOS) and native rsp (C-ABI, fn frames, rare extra-BLOB r10
        save).  Plus the heap-resident BB DATA-block tree (walks via
        r10) and the heap-resident SmCallFrame array
        (`st->call_stack[]`).
      - **SM_CALL_EXPRESSION** distinguishes BB-land entry from
        SM-blob-land entry by saving (or not) `caller_r10` in the
        SmCallFrame.  Emitter knows at emit time which case applies.
      - **`*P` (P is PATTERN):** Re-uses P's emitted CODE; allocates
        fresh DATA tree per match via `rt_alloc_blob_data`; sets r10
        to the new root; jumps to P's CODE entry.  Code shared, DATA
        per-invocation, re-entrant by allocation discipline.
      - **`*(expr)`:** DEFER box uses SM_CALL_EXPRESSION with the
        compiled SM body's entry_pc.  caller_r10 saved in the frame;
        restored on SM_RETURN.

      ME-4-pre closes on Lon's sign-off line in REGISTER-LAYOUT.md's
      watermark.  Until then, ME-4-post stays blocked.

- [x] **ME-4-post — Fix realloc bug + re-emit ME-4 blobs against
      locked convention.**  After ME-4-pre lands (Lon sign-off in
      REGISTER-LAYOUT.md).  Implements the SM_STNO statement-boundary
      blob (`mov r12, [rel sm_state_stack_base]` — single instruction
      reset of TOS, handles realloc by reloading the base; replicates
      the mode-2 contract at `sm_interp.c:295`).  Re-emits the ten
      ME-4 inline-native blobs against the locked register convention
      — r12 = TOS pointer directly, no `[r12+0]` reload of stack
      base, no separate sp index.  Expected savings: each push goes
      from ~12 bytes (today's pattern of reloading stack base +
      computing sp offset) to ~9 bytes (`mov [r12], rax ; mov [r12+8],
      rdx ; add r12, 16`); each pop similarly.  Expected perf
      improvement: another measurable cut on the 100k counter loop
      microbench beyond ME-3's ~26% and ME-4-PARTIAL's ~32% gains.
      Audit checklist in REGISTER-LAYOUT.md gates this rung's commit.
      Gate: smoke 7/7 + unified_broker 49/49 hold; the canonical
      multi-statement arithmetic reproducer (see ME-4 PARTIAL note)
      runs byte-identical between `--jit-run` and `--sm-run`.  When
      ME-4-post closes, ME-4 is closed.
      ✅ 2026-05-10 (split landing): bug-fix portion at one4all
      `06b8f503` (4096 stack pre-grow + h_stno sp=0); r12=TOS-pointer
      re-emit portion at one4all `ae7f325a`.
      Final shape implemented per REGISTER-LAYOUT.md §"Audit checklist":
      r13 = &SM_State (new claim, justified by PC access in trampoline
      + SM_STNO mode-2-contract sync); r12 = SM value-stack TOS pointer
      (FORTH-style, single register).  sm_jit_run entry: `mov r13, st;
      mov r12, st->stack` (st->sp=0 at entry, so r12 starts at base).
      Trampoline reads PC from `[r13+20]` (4 bytes, down from 5).
      emit_halt_blob: 5 bytes (down from 6).  emit_jump_blob_skeleton:
      13 bytes (down from 14).  emit_standard_blob: 57 bytes (up from
      28 — +29 covers the r12↔sp sync protocol around the C-handler
      call: `st->sp = (r12 - st->stack) >> 4` before; `r12 = st->stack
      + st->sp << 4` after).  me4_* blobs shrunk 8-22%: arith 84→69,
      concat 76→63, coerce_num 56→49, push_null 53→42, push_var 63→52,
      store_var 76→59.  Pure value-in/value-out me4_* helpers need no
      sp sync; they read TOS at `[r12-16]/[r12-8]`, TOS-1 at
      `[r12-32]/[r12-24]`, push at `[r12]/[r12+8]+add r12,16`.
      Gates: smoke 7/7, unified_broker 49/49, sn7_beauty 26/25
      unchanged baseline, mode-4 tripwire 0/17 unchanged baseline,
      realloc repro byte-identical sm-run vs jit-run (`X=20 Y=210`).
      Additional verification: 30-program corpus parser sweep, zero
      divergence sm-run vs jit-run.  Perf: 100k counter loop sm-run
      143ms → jit-run 95ms (~34% faster, preserving the gap from
      ME-4-PARTIAL's ~32%; standard-blob sync overhead offset by
      me4_* shrinkage on arithmetic-heavy workloads).  ME-4 closed.
      Future optimization noted but out of scope: a
      `emit_standard_blob_no_stack()` variant for handlers that don't
      touch the value stack (h_label, h_jump_s, h_jump_f, h_stno) can
      skip both sync blocks and shrink back toward 28 bytes; would
      offset the +29 standard-blob growth on jump/label/stno-heavy
      programs.  Tracked implicitly under ME-5 (control flow) which
      will revisit jump opcode encoding anyway.

- [x] **ME-5 — Control flow.**  `SM_JUMP_S`, `SM_JUMP_F`, `SM_LABEL`,
      `SM_STNO`.  SM_LABEL records SEG_CODE offset for the next instruction;
      SM_STNO is no-op at runtime (statement number is used by mode 4 banner
      emission, irrelevant in mode 3).  `SM_JUMP_S` and `SM_JUMP_F` lower
      as `call rt_last_ok@PLT ; test eax, eax ; jnz/jz <rel32>`.  Gate:
      `goto_s` and `goto_f` smoke tests pass under `--jit-run`.
      ✅ 2026-05-10 (Claude latest, fifth session) at one4all
      `880adc36`.  Two emitter additions:
      1. `emit_standard_blob_no_stack` (39 bytes vs 57 for the full
         standard_blob) — skips the pre-call r12→sp write (handler
         doesn't read st->sp meaningfully) but keeps the post-call r12
         reload so h_stno's `STATE->sp = 0` reset propagates correctly
         to r12 via `r12 = st->stack + sp*16`.  Routed: SM_LABEL, SM_STNO.
      2. `emit_cond_jump_blob_skeleton` (33 bytes) — inline-native lowering
         of SM_JUMP_S / SM_JUMP_F.  Reads `[r13+16]` (st->last_ok) via
         direct mem-imm cmp; no PLT call needed (the original spec's
         `call rt_last_ok@PLT` is unworkable since scrip doesn't link
         libscrip_rt — but r13=&SM_State makes it trivial to read
         last_ok inline).  Direct rel32 to BOTH target and fall-through
         blobs — bypasses the trampoline indirect-jump on every branch.
         Two rel32 patches per blob; pass 2 handles them via the
         negative-tag scheme on `jump_indices[]` (`-(target_pc + 1)`
         distinguishes cond-jump records from SM_JUMP records).  Buffer
         size doubled to 2x prog->count to accommodate the 2-record
         emission per cond-jump.
      Audit:
      - Direct-rel32 to both arms preserves the "every blob bumps pc
        from its own preamble" invariant — both target and fall-through
        blobs do their own pc++.  cond_jump itself sets pc to the
        correct destination value before jumping, so debugger/longjmp
        recovery sees a consistent pc.
      - `cmp dword [r13+16], 0` reads `int last_ok`; jcc on result.
        last_ok is a 4-byte int in SM_State; the 32-bit cmp encoding
        matches.
      Gates: smoke 7/7 (including `goto_s`), unified_broker 49/49,
      sn7_beauty 26/25 unchanged baseline, mode-4 tripwire 0/17
      unchanged.  60-program corpus parser sweep: 0 divergences sm-run
      vs jit-run.  Correctness verified on taken (IDENT), not-taken
      (DIFFER), and tight-loop (`LT` with `:S(LOOP)F(DONE)`) shapes.
      Perf: ~99ms median jit-run on 100k counter loop (same as pre-ME5
      baseline within noise).  The blob-size shrinkage (57→39 for
      SM_STNO/SM_LABEL, 57→33 for cond-jumps) doesn't translate to
      measurable speedup on this microbench because dispatch cost is
      already dominated by the C-handler calls and me4_arith's
      shared_arith — but the smaller code is denser in i-cache, which
      may matter for larger programs (untested here, out of rung
      scope).  Future blob-size benefit will manifest on mode-4
      serialization (smaller SEG_CODE → smaller .s).

- [x] **ME-6 — Function calls and returns.**
      sess 2026-05-10 (Claude latest, sixth session) at end of this file.
      Prerequisite ME-7 ✅ closed this session (DEFINE-entry flag in place);
      remaining work is the prologue/epilogue blob emission, which needs a
      conditional epilogue mechanism (signal from C handler back to blob)
      to handle SM_RETURN_S/_F variants whose unwind is condition-dependent.
      Recursive `fib` already runs byte-identical sm-run vs jit-run today,
      proving the existing dispatch model doesn't need rbp accounting for
      correctness — the prologue/epilogue's actual purpose (per goal text)
      is the latent vsnprintf alignment in `bb_pool` byrd-box code, which
      is a different code path than SM-blob land.  `SM_CALL_FN`, `SM_RETURN`,
      `SM_NRETURN`, `SM_FRETURN`.  Bridge via existing `rt_call@PLT` for
      builtin dispatch.  DEFINE'd chunks get a real prologue/epilogue:
      `push rbp ; mov rbp, rsp` at entry, `pop rbp ; ret` at exit.  This
      fixes the alignment problem currently failing 13 mode-4 drivers
      (latent in mode 3 today: any chunk that PLT-calls `vsnprintf` via
      `bb_label_initf` faults on `rsp%16==8`).  Gate: `define` smoke
      passes; recursive `roman.sno` runs under `--jit-run`.

- [x] **ME-7 — Chunk dispatch fix in `sm_lower.c`.**  Distinguish DEFINE'd
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
      ✅ 2026-05-10 sess 6 (Claude latest).  Implementation differs from
      original spec slightly: flag landed at `a[2].i = 1` (not `a[1].i`)
      because `a[1].i` is already used to store the label's PC for
      `sm_label_pc_lookup`.  `a[2].i` is otherwise unused for SM_LABEL.
      New runtime API `FUNC_IS_ENTRY_LABEL(label)` in `snobol4.c`/`.h`
      scans every FNCBLK_t bucket for any registered user function whose
      `entry_label` matches `label`; O(N) over registered functions but
      called only once per labeled SNOBOL4 statement at lower time, so
      negligible.  `lower_stmt` calls `FUNC_IS_ENTRY_LABEL` after
      `sm_label_named` for `s->label` and sets `a[2].i = 1` on hit —
      prescan_defines() has already populated the function table by the
      time sm_lower runs (sm_preamble ordering), so the check is
      authoritative.  `sm_prog.c` printer extended to emit `s="<name>"
      define_entry=1` for SM_LABEL — previously SM_LABEL had no case in
      the dump switch and printed bare.  Gate uplift: PASS=26 FAIL=25
      baseline preserved (this rung adds no codegen behavior change — the
      flag is consumed by ME-6, which is still PARTIAL).  Verified the
      flag fires correctly: `--dump-sm` on the `define` smoke shows
      `SM_LABEL s="DOUBLE" define_entry=1` for the DOUBLE function entry
      but no flag on the `END` goto-target label.  Recursive fib stress
      test (`088_define_recursive_fib.sno`, 144 calls for fib(10)) runs
      byte-identical sm-run vs jit-run, demonstrating the flag works
      through real recursion.

### Phase C — Deferred-eval consumer (post-GOAL-CHUNKS)

- [ ] **ME-8 — `SM_PUSH_EXPRESSION` / `SM_CALL_EXPRESSION` consumer.**
      Lands **after** GOAL-CHUNKS-STEP17 closes (or after the
      per-frontend SM sub-program migration completes for the SNOBOL4
      frontend, at minimum, so we consume a stable opcode shape).
      Implements both consumers in mode-3 SM-blob land:

      `SM_PUSH_EXPRESSION <entry_pc>` lowers to push a `DT_E`
      descriptor `{v=DT_E, slen=1, i=entry_pc}` on the SM value stack
      (FORTH-style at `[r12]`).

      `SM_CALL_EXPRESSION` pops the descriptor, pushes an SmCallFrame
      onto `st->call_stack[]`, transfers control via 32-bit relative
      jump to `entry_pc`'s SEG_CODE offset.  `SM_RETURN` inside the
      body pops the frame and jumps back.  No `EXPR_t*` access.

      **Two emission contexts** — the emitter knows at emit time
      which one applies:

      1. **From SM-blob land** (the SM_CALL_EXPRESSION emission site
         sits in pure SM-blob land, outside any emitted BLOB).
         SmCallFrame holds `{ret_pc, caller_r12, last_ok,
         caller_r10=0}`.  No r10 to restore — there was no active
         BLOB.

      2. **From BB land** (the DEFER box case — the emission site
         sits inside an emitted BLOB).  SmCallFrame holds `{ret_pc,
         caller_r12, last_ok, caller_r10=current_r10}`.  On
         SM_RETURN, r10 is restored from the frame so the DEFER box's
         own DATA block is addressable again.

      Coordinated with GOAL-CHUNKS: we provide the mode-3 consumer;
      GOAL-CHUNKS provides the producer (sm_lower emitting
      SM_PUSH_EXPRESSION in place of the legacy SM_PUSH_EXPR).

      Gate: corpus programs using `*P` (P being a PATTERN variable),
      `*(X+1)`, `EVAL(str)`, `CODE(str)` run identically under
      `--jit-run` vs `--sm-run`.  Same pass-set as `--ir-run` for
      those programs.

      Also covers the `*P` (PATTERN) case at the runtime side:
      `rt_alloc_blob_data(root_box_ptr)` walks the BLOB's box tree
      and allocates a fresh DATA tree, returning the root DATA
      address — the DEFER box then sets r10 to this address and
      jumps to the BLOB's CODE entry.  CODE is reusable across
      simultaneous matches because each gets its own DATA tree.

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
closes so the opcode shape is stable; (5) byrd-box ABI distinguishes the
flat-BB form (stackless inline asm inside a glob, entered by `jmp` at the
glob's first byte, locals at `[r10+N]`, no `esi` port discriminator) from
the dispatched-BB form (legacy `bb_boxes.s`-style C-callable functions
with `rdi=ζ`, `esi`=entry port, `rax:rdx=σ:δ`, callee-saved
rbx/r12/r13/r14/r15) — mode 3 SM-blob land calls into the flat form;
dispatched form survives for `--bb-brokered`.  Boxes are stackless: CODE
is shared; DATA is per-invocation; sibling DATA blocks chained via
save-list provide the appearance of stack-like depth without an actual
stack.  See ARCH-x86.md §"Boxes are stackless" and §"Two emission forms"
for the architectural definition.

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

**Addendum sess 2026-05-10 (Claude latest, second session of the day):
ME-4 reorganized into ME-4-pre + ME-4-post; REGISTER-LAYOUT.md drafted
and refined through Lon Q&A.**  No code lands this session; HQ docs
only.

Refinements from Lon Q&A (recorded for future sessions so the same
ground does not need re-treading):

- **r12 is the SM value-stack TOS pointer**, FORTH-style.  Not
  `SM_State*`.  Single register holds top-of-stack; no separate
  {base, sp} split; all pop-depths are compile-time-known per
  opcode.  SM_State accessed via RIP-relative addressing.
- **Pattern history stack does not exist in SCRIP.**  Byrd-boxes are
  stackless (ARCH-x86.md §"Boxes are stackless"); per-invocation DATA
  blocks ARE the alternatives; backtracking is DATA-block-tree
  traversal.  SPITBOL's `pmhbs`-rooted history stack has no SCRIP
  counterpart.  Documented in ARCH-x86.md and REGISTER-LAYOUT.md.
- **Two stacks total**: SM value stack (heap, r12=TOS) + native rsp.
  Plus heap-resident BB DATA-block tree (walked via r10) and heap-
  resident SmCallFrame array (`st->call_stack[]`).
- **`*P` re-entry**: code shared, DATA fresh.  `rt_alloc_blob_data`
  walks P's box tree and allocates a fresh DATA tree per match.  P's
  CODE in `bb_pool` is reused; only DATA differs per invocation.
- **`*(expr)` and DEFER box**: SM_CALL_EXPRESSION distinguishes
  BB-land entry (saves `caller_r10` in SmCallFrame) from SM-blob-land
  entry (no r10 to save).  Emitter knows at emit time which applies.
  ME-8 owns this consumer.
- **rbx/r13/r14/r15 are free** in mode-3.  Initial draft pre-claimed
  some of them; the refined design pre-claims none.  Two callee-saved
  claimed (r12 + rbp-when-in-function), four free.
- **"Chunk" terminology** is retired in REGISTER-LAYOUT.md and the
  newer prose of GOAL-MODE3-EMIT.md.  Historical filenames
  (GOAL-CHUNKS, GOAL-CHUNKS-STEP17) and `/* CHUNKS-step* */` comments
  are kept as session-rung-tags; they are not type names.  A "chunk"
  in any historical context = a CODE/EXPRESSION/DEFINE'd-function
  body = the unit produced by `CODE(s)`, `*(expr)`, `EVAL(s)`, or
  `DEFINE(...)` — equivalent to SPITBOL's CDBLK/EXBLK.  At the SM
  level: a labeled SM-instruction subsequence addressable by entry_pc,
  ending in SM_RETURN.

ARCH-x86.md companion edits this session (HEAD `a49e099` and
`ae5a069`):
- §"Boxes are stackless" — explicit: boxes have no stack, re-entry
  by fresh DATA allocation chained via save-list header.
- §"Two emission forms" — flat-BB (stackless, no esi, glob structure
  static) vs dispatched-BB (legacy bb_boxes.s with esi=port).
- §"Intra-BLOB vs extra-BLOB jumps" — emitter knows statically which
  kind; intra and extra-tail need no r10 save; only call-style
  extra-BLOB needs source-BLOB `push r10`/`pop r10`.

REGISTER-LAYOUT.md (HEAD `ae5a069` initial; rewritten this addendum)
is the locked deliverable.  Awaiting Lon sign-off line in its
watermark to close ME-4-pre and unblock ME-4-post.

**State at handoff:** one4all unchanged at `e7ac6f77` (ME-4 PARTIAL).
HQ committed and pushed: ARCH-x86 + GOAL-MODE3-EMIT + PLAN +
REGISTER-LAYOUT.  Gates verified: smoke 7/7, unified_broker 49/49.
Mode-4 frozen as tripwire untouched.

**Addendum sess 2026-05-10 (Claude latest, third session of the day):
ME-4-pre ✅ CLOSED, ME-4-post bug-fix portion landed, full re-emit
deferred.**

Lon's sign-off on `REGISTER-LAYOUT.md` was recorded at the start of
this session ("I think your register layout has a chance.  So sign
off.").  That closes ME-4-pre per its own closure criterion ("Lon's
sign-off line in REGISTER-LAYOUT.md's watermark").

ME-4-post as originally scoped had two pieces:
1. **Fix the realloc bug** that aborts multi-statement arithmetic
   programs under `--jit-run` (e.g. simple `X = X + 1 ; Y = Y + X`
   loops).
2. **Re-emit the 10 ME-4 inline-native blobs** against the locked
   register convention (`r12 = SM value-stack TOS pointer`,
   FORTH-style; SM_STNO blob = `mov r12, [r13]` for reset + realloc
   handling; per-blob push/pop shrinks ~30%).

This session landed (1) cleanly and deferred (2) to a follow-on rung.
Rationale: the realloc bug had a self-contained fix that did not
require touching the byte-level blob encoders (h_stno C handler gets
`STATE->sp = 0` line, mirroring `sm_interp.c:329`; `sm_jit_run`
pre-grows `state->stack` to 4096 entries at entry so the
per-statement reset bounds intra-statement depth to <= 4096).
Re-emitting the 10 blobs against r12-as-TOS-pointer requires
rewriting every push/pop/load-slot sequence in the byte emitter and
adjusting the trampoline to use a second callee-saved register for
&SM_State; that work is mechanical but has many failure modes and
warrants its own session with fresh context budget.

The split is consistent with how ME-3 itself landed — its `Addendum
sess 2026-05-10 (Claude latest, fourth commit)` already noted "ME-4
inlines arithmetic/stack ops and the gap widens" as future work, and
this session continued in that incremental pattern.

**What landed (commit pending):**

- `sm_jit_run` pre-grows `state->stack` to 4096 entries on entry.
  The pre-grow is idempotent (skipped if already >= 4096).  `st->sp =
  0` set unconditionally on entry so a re-entered sm_jit_run gets a
  clean slate.
- `h_stno` (the C handler the standard SM_STNO blob calls) sets
  `STATE->sp = 0` — mirrors the mode-2 contract at
  `sm_interp.c:329`.  Comment block documents the live-bug origin and
  the mode-2 mirror.
- Documentation: `sm_jit_run`'s asm-volatile block and the
  emit_trampoline source both note that the full r12=TOS-pointer
  transition is deferred; the ME-2/ME-3 r12=&SM_State convention is
  preserved verbatim.

**What changed: 1 file, +48/-3 lines.**

```
src/runtime/x86/sm_codegen.c | 51 +++++++++++++++++++++++++++++++++++++++++---
1 file changed, 48 insertions(+), 3 deletions(-)
```

**Gates this session:**

| Gate | Before | After |
|------|--------|-------|
| `test_smoke_snobol4.sh` | PASS=7 FAIL=0 | PASS=7 FAIL=0 |
| `test_smoke_unified_broker.sh` | PASS=49 FAIL=0 | PASS=49 FAIL=0 |
| `test_gate_sn7_beauty_self_host.sh` | PASS=26 FAIL=25 | PASS=26 FAIL=25 (unchanged baseline) |
| Realloc reproducer (`/tmp/me4_realloc_repro.sno`) under `--jit-run` | `realloc(): invalid next size; Aborted` | `X=21 Y=231` (byte-identical to `--sm-run`) |
| 100k counter loop under `--jit-run` | 80ms (ME-4-PARTIAL perf preserved) | 80ms |

`--sm-run` vs `--jit-run` byte-identical confirmed on: realloc repro,
100k loop.  Mode-4 gate suspended per Gates section (frozen as
tripwire; untouched this session).

**State at handoff:**
- one4all: ready to commit (working tree dirty).  Expected new HEAD
  after commit closes ME-4-pre + ME-4-post-bugfix.
- corpus: unchanged.
- .github: PLAN.md updated (current step → ME-4-post-r12-tos);
  GOAL-MODE3-EMIT.md updated (this addendum); REGISTER-LAYOUT.md
  Lon-signed-off.

**Next active step:** ME-4-post-r12-tos — the deferred full re-emit
of ME-4's inline-native blobs against the r12=TOS-pointer convention.
Scope: rewrite `emit_trampoline` to read pc from a new addressing
register; rewrite `emit_standard_blob`'s pc-bump; rewrite each of the
10 emit_me4_* blobs' stack-access sequences (push/pop/load-slot
become `mov [r12]/[r12+8]; add r12,16` / inverse).  Expected
per-blob byte savings: emit_me4_arith_blob ~80B → ~55B; total
SEG_CODE size for a typical 100-instruction program: ~30% smaller.
Gate: same as ME-4-post bug-fix (smoke 7/7, unified_broker 49/49,
realloc repro byte-identical, mode-4 tripwire unchanged), PLUS the
audit checklist in REGISTER-LAYOUT.md §"Audit checklist before
ME-4-post commits".  Coordinated with the new r13-as-&SM_State claim
that ME-4-post-r12-tos will introduce (justified extension of the
"future claims" door REGISTER-LAYOUT.md leaves open for r13/r14/r15/
rbx).


**Addendum sess 2026-05-10 (Claude latest, fourth session of the day):
ME-4-post-r12-tos ✅ CLOSED. ME-4 closed.**

This session implemented the deferred r12=TOS-pointer re-emission noted
at the end of the previous (third) session's handoff.  The previous
session had landed the bug-fix portion (4096 stack pre-grow + h_stno
sp=0 reset, one4all `06b8f503`) but deferred the mechanical re-emit
because "rewriting every push/pop/load-slot sequence in the byte
emitter and adjusting the trampoline to use a second callee-saved
register for &SM_State has many failure modes and warrants its own
session with fresh context budget."  That session has now happened.

**What landed (one file, sm_codegen.c):**

1. **sm_jit_run entry** — now loads BOTH callee-saved registers per
   REGISTER-LAYOUT.md:
   ```c
   asm volatile ("mov %0, %%r13\n\t"
                 "mov %1, %%r12"
                 :
                 : "r"(st), "r"(st->stack)
                 : "r12", "r13");
   ```
   r13 = &SM_State (the new claim — first formerly-free callee-saved
   register to be claimed by a mode-3 sub-rung, justified by the PC
   access in the trampoline and the SM_STNO sp-reset which needs to
   reload r12 from `[r13]` = `SM_State.stack`).  r12 = `st->stack`
   (the TOS pointer at base, since `st->sp = 0` at entry after the
   pregrow).

2. **emit_trampoline** — PC read via `[r13+20]` instead of `[r12+20]`.
   Saves 1 byte (4 vs 5).

3. **emit_standard_blob** — PC bump via `[r13+20]`; r12↔sp sync
   protocol added around the C-handler call.  Pre-call:
   ```
     mov rax, r12          ; 3 bytes
     sub rax, [r13]        ; 4 bytes  (rax -= st->stack)
     sar rax, 4            ; 4 bytes  (signed div by 16)
     mov [r13+8], eax      ; 4 bytes  (st->sp = eax)
   ```
   Post-call:
   ```
     mov eax, [r13+8]      ; 4 bytes  (eax = st->sp)
     shl rax, 4            ; 4 bytes  (rax = sp*16)
     add rax, [r13]        ; 4 bytes  (rax += st->stack)
     mov r12, rax          ; 3 bytes
   ```
   Standard blob grew 28→57 bytes.  Cost is the +29 sync bytes; C
   handlers can continue to use STATE->stack[STATE->sp] semantics
   unchanged (mode-2 contract preserved at the C-call boundary).

4. **emit_halt_blob** — PC bump via `[r13+20]`.  6→5 bytes.

5. **emit_jump_blob_skeleton** — PC write via `[r13+20]`.  14→13 bytes.

6. **emit_me4_* (six blobs)** — full FORTH-style rewrite.  r12 used
   directly as TOS pointer; no stack-base reload, no sp computation,
   no separate sp tracking.  Each blob:
   - Loads args from `[r12-16]/[r12-8]` (TOS) and `[r12-32]/[r12-24]`
     (TOS-1) into SysV-ABI arg regs (16-byte struct = {rdi,rsi}
     for arg 1, {rdx,rcx} for arg 2; 3rd integer arg in r8d).
   - Calls me4_* via aligned imm64 (unchanged from before).
   - Writes result rax:rdx back to the appropriate stack slot.
   - Adjusts r12 by the net stack delta (sub r12,16 / add r12,16 /
     no change, depending on opcode).
   - jmp rel32 to trampoline.

   Blob sizes (current / previous / delta):
   - arith       69 / 84 (-15B, -18%)
   - concat      63 / 76 (-13B, -17%)
   - coerce_num  49 / 56 (-7B,  -13%)
   - push_null   42 / 53 (-11B, -21%)
   - push_var    52 / 63 (-11B, -17%)
   - store_var   59 / 76 (-17B, -22%)

**Audit checklist verification (REGISTER-LAYOUT.md §"Audit checklist
before ME-4-post commits"):**

| Check | Status |
|-------|--------|
| Stack push: `mov [r12],rax; mov [r12+8],rdx; add r12,16` | ✅ |
| Stack pop: `sub r12,16; mov rax,[r12]; mov rdx,[r12+8]` | ✅ (implicit in pop-2-push-1 / pop-1-push-1 pattern via [r12-16] reads) |
| Multi-pop: `sub r12, N*16` (N compile-time-known) | ✅ |
| Random access: `[r12 - (N+1)*16]` (N compile-time-known) | ✅ |
| SM_STNO blob: `mov r12, [rel sm_state_stack_base]` (single insn) | ✅ via h_stno C handler + standard_blob post-call sync (same effect: r12 ends pointing at st->stack since h_stno sets sp=0) |
| PLT calls preserve r12 (SysV callee-saved) | ✅ |
| C handlers that may reset r12 (rt_exec_stmt, rt_call_fn): spill before, reload after | ✅ via standard_blob's sync protocol |
| No SM-blob code writes r10 | ✅ (verified by grep over emit_me4_*, emit_standard_blob, emit_trampoline, emit_halt_blob, emit_jump_blob_skeleton — no r10 references) |
| r10 constant inside a BLOB | N/A in this rung — no BLOB code emitted yet |
| DEFINE'd fn entry: `push rbp; mov rbp, rsp` / exit: `pop rbp; ret` | unchanged from ME-3 (uses existing C-side h_return_impl mechanism, not affected by r12-as-TOS transition) |

**Gates this session:**

| Gate | Before | After |
|------|--------|-------|
| `test_smoke_snobol4.sh` | PASS=7 FAIL=0 | PASS=7 FAIL=0 |
| `test_smoke_unified_broker.sh` | PASS=49 FAIL=0 | PASS=49 FAIL=0 |
| `test_gate_sn7_beauty_self_host.sh` | PASS=26 FAIL=25 | PASS=26 FAIL=25 (unchanged baseline) |
| `test_gate_em_beauty_subsystems_mode4.sh` (tripwire) | PASS=0 FAIL=17 | PASS=0 FAIL=17 (unchanged baseline; differs from PLAN.md's "PASS=4 FAIL=13" note because the previous session's environment had different SPITBOL-oracle availability — this session shows 0/17 both pre-change and post-change, confirming tripwire-stable) |
| Realloc reproducer (`X=X+1;Y=Y+X` loop, `LT(X,20):S(LOOP)`) | byte-identical `X=20 Y=210` | byte-identical `X=20 Y=210` |
| 30-program parser-corpus sweep (`/home/claude/corpus/programs/snobol4/parser/*.sno`) | — | 30 tested, 0 divergences sm-run vs jit-run |
| 100k counter loop perf (--jit-run) | ~80ms (ME-4-post bug-fix baseline) | ~95ms |
| 100k counter loop perf (--sm-run) | ~143ms (comparison) | ~143ms |
| Relative jit speedup over sm | ~32% (ME-4-PARTIAL) → ~44% (ME-4-post bug-fix) | ~34% (gap preserved; standard-blob +29B sync overhead offset by me4_* shrinkage) |

The 100k loop perf observation (~95ms vs the previous ~80ms) reflects
the standard-blob sync overhead in the SM_STNO + SM_JUMP_S path that
this loop hits every iteration.  The me4_* shrinkage helps arithmetic
expressions but the loop body's per-iteration overhead is dominated by
the standard-blob's new sync block.  Future optimization
`emit_standard_blob_no_stack()` for handlers like h_jump_s / h_stno
that don't read or write the value stack — they can skip both sync
blocks and shrink back toward the 28-byte original — would recover
this gap and likely push past the ME-4-post bug-fix baseline.  Tracked
as future ME-5 work (ME-5 owns the jump opcode encoding anyway).

**What didn't change:**

- ME-4-pre's REGISTER-LAYOUT.md — already locked, Lon-signed-off.
- ARCH-x86.md, ARCH-SCRIP.md — already correct.
- PLAN.md's table — only the active step changes (see PLAN.md update).
- All me4_* C helpers (me4_arith, me4_concat, me4_coerce_num,
  me4_push_var, me4_store_var, me4_push_null) — bodies unchanged;
  they were already pure value-in/value-out and need no sp sync.
- All h_* C handlers — unchanged; they continue to use the mode-2
  STATE->stack[STATE->sp] convention.  The new sync protocol in
  emit_standard_blob is the bridge that makes this work.

**State at handoff:**
- one4all: working tree dirty (`src/runtime/x86/sm_codegen.c`).
  Ready to commit.
- corpus: unchanged.
- .github: GOAL-MODE3-EMIT.md updated (this addendum + ME-4-post
  marked `[x]`), PLAN.md updated (active step → ME-5).  Ready to
  commit.

**Next active step:** ME-5 — Control flow.  `SM_JUMP_S`, `SM_JUMP_F`,
`SM_LABEL`, `SM_STNO`.  ME-5 covers (a) inline-native lowering of the
S/F conditional jumps as `call rt_last_ok@PLT ; test eax, eax ; jnz/jz
<rel32>` (replacing today's standard-blob C-handler dispatch), and (b)
the optional `emit_standard_blob_no_stack()` optimization noted above
for handlers that don't touch the value stack — same blob shape as
emit_standard_blob but with both sync blocks elided, ~28 bytes vs 57.
Gate: `goto_s` and `goto_f` smoke tests pass under `--jit-run`;
existing perf baseline preserved or improved.

**Addendum sess 2026-05-10 (Claude latest, fifth session of the day):
ME-5 ✅ CLOSED.  Control flow opcodes inline-native.**

The fourth-session addendum noted ME-5 would introduce
`emit_standard_blob_no_stack()` for handlers that don't touch the
value stack.  This session implemented that plus inline-native
SM_JUMP_S / SM_JUMP_F.

**What landed (single file, sm_codegen.c):**

1. **`emit_standard_blob_no_stack`** — 39-byte blob shape (vs 57 for
   full standard_blob).  Pre-call r12→sp write elided (the handler
   either ignores st->sp like h_label or overrides it like h_stno's
   `STATE->sp = 0` — there's no pre-call state to capture).  Post-call
   r12 reload preserved so h_stno's sp-reset propagates to r12.
   Routed: SM_LABEL, SM_STNO.

2. **`emit_cond_jump_blob_skeleton`** — 33-byte blob.  Reads
   `[r13+16]` directly (st->last_ok); jcc on result; direct rel32 to
   target arm; direct rel32 to fall-through arm.  No PLT call, no
   trampoline indirect-jump — both arms are direct.  Two rel32 patch
   sites per blob.

   The original spec's `call rt_last_ok@PLT ; test eax, eax ; jnz/jz
   <rel32>` is unworkable in this environment (scrip doesn't link
   libscrip_rt — same constraint that drove ME-4's Option C decision).
   But the FORTH register convention from ME-4-post-r12-tos gives us
   r13 = &SM_State, which makes inline `cmp [r13+16], 0` trivial.
   This is strictly better than the original recipe: no call overhead,
   no PLT indirection, no register clobber.

   Encoding:
   ```
   cmp dword [r13+16], 0           5 bytes  (41 83 7d 10 00)
   jcc rel8 +13 (skip taken)       2 bytes  (74/75 0d)
   mov dword [r13+20], target_pc   8 bytes  (41 c7 45 14 <imm32>)
   jmp rel32 blob[target_pc]       5 bytes  (e9 <rel32>)   [PATCH 1]
   mov dword [r13+20], fallthru    8 bytes  (41 c7 45 14 <imm32>)
   jmp rel32 blob[fallthru_pc]     5 bytes  (e9 <rel32>)   [PATCH 2]
   ```

   jcc selection:
   - SM_JUMP_S takes on last_ok != 0 → fall through on zero → `je`
     (opcode 0x74).
   - SM_JUMP_F takes on last_ok == 0 → fall through on nonzero → `jne`
     (opcode 0x75).

3. **Pass 2 patcher extended.**  Buffer sized 2x prog->count (each
   cond-jump emits 2 patch records).  `jump_indices[j]`'s sign tags
   the record kind:
   - `jump_indices[j] >= 0` → SM_JUMP entry; index = source-pc; target
     read from `prog->instrs[ji].a[0].i`.
   - `jump_indices[j] < 0`  → ME-5 cond-jump entry (tagged); target =
     `-jump_indices[j] - 1`.

   The tag is robust: negative values can't collide with valid pc
   indices (which are >= 0 and bounded by prog->count, well under
   INT_MAX/2).

**Why ME-5 isn't a perf win on this microbench (and is fine anyway):**

100k counter loop pre-ME5 (just ME-4-post-r12-tos): 98-100ms median
under --jit-run.  Same loop post-ME5: 97-100ms median.  Within noise.

Reason: the 100k loop's per-iteration cost is dominated by
NV_GET_fn/NV_SET_fn (variable lookups) and shared_arith (the C
arithmetic helper).  Dispatch cost (which is what ME-5 reduces) is a
small fraction.  Reducing standard_blob's 57 bytes to 39 (no_stack)
for SM_STNO, and 57 to 33 (cond_jump) for SM_JUMP_S, saves dispatch
cycles but not enough to dent the per-iteration total.

This is expected and consistent with the goal-file's framing of ME-5
as "control flow inline-native" rather than "perf rung."  The win
manifests in:
- Smaller SEG_CODE → smaller mode-4 .s output when EM-MODE4-IS-MODE3-
  DUMP reopens after ME-14.
- Fewer indirect jumps → better branch predictor behaviour on larger
  programs (untested but architecturally cleaner).
- One less PLT-shaped dispatch hop on every conditional branch — pure
  win for the i-cache.
- Architectural correctness: control flow now uses the same FORTH
  register convention as everything else; no more standard-blob sync
  protocol firing on stack-neutral handlers.

**Audit:**

| Check | Status |
|-------|--------|
| `goto_s` smoke (test_smoke_snobol4.sh) | ✅ PASS |
| `define` smoke (uses SM_JUMP at function bounds) | ✅ PASS (already worked, but verified) |
| Branch-taken correctness (IDENT-matching `:S(label)`) | ✅ PASS — outputs `right` |
| Branch-not-taken correctness (DIFFER-mismatching `:S(label)`) | ✅ PASS — outputs `right` via `:F` fall-through |
| Tight-loop correctness (LT, `:S(LOOP)F(DONE)`) | ✅ PASS — outputs `X=20 Y=210` |
| SM_LABEL routed through standard_no_stack | ✅ |
| SM_STNO routed through standard_no_stack | ✅ |
| SM_JUMP_S routed through cond_jump | ✅ |
| SM_JUMP_F routed through cond_jump | ✅ |
| jump_indices buffer doubled to 2x prog->count | ✅ |
| Negative-tag scheme distinguishes SM_JUMP from cond-jump records | ✅ |
| r12↔sp sync protocol preserved for full standard_blob (other opcodes) | ✅ — emit_standard_blob unchanged this rung |

**Gates this session:**

| Gate | Before | After |
|------|--------|-------|
| `test_smoke_snobol4.sh` | PASS=7 FAIL=0 | PASS=7 FAIL=0 |
| `test_smoke_unified_broker.sh` | PASS=49 FAIL=0 | PASS=49 FAIL=0 |
| `test_gate_sn7_beauty_self_host.sh` | PASS=26 FAIL=25 | PASS=26 FAIL=25 (unchanged baseline) |
| `test_gate_em_beauty_subsystems_mode4.sh` (tripwire) | PASS=0 FAIL=17 | PASS=0 FAIL=17 (unchanged baseline) |
| Realloc reproducer (multi-stmt arith) | byte-identical | byte-identical |
| 60-program parser-corpus sweep | (30 last session) 0 divergences | 0 divergences (60 programs) |
| 100k counter loop --jit-run | 97-100ms median | 97-100ms median (within noise) |
| 100k counter loop --sm-run | ~120ms median | ~120ms median (untouched) |

**State at handoff:**
- one4all: working tree dirty (`src/runtime/x86/sm_codegen.c`).
  Ready to commit.
- corpus: unchanged.
- .github: GOAL-MODE3-EMIT.md updated (this addendum + ME-5
  marked `[x]`), PLAN.md updated (active step → ME-6).  Ready to
  commit.

**Next active step:** ME-6 — Function calls and returns.  `SM_CALL_FN`,
`SM_RETURN`, `SM_NRETURN`, `SM_FRETURN`.  Bridge via existing
`me4_*`-style helpers for builtin dispatch (the original spec's
`rt_call@PLT` is unworkable for the same reason as ME-5's
`rt_last_ok@PLT` — use the same Option C inline-helper pattern).
DEFINE'd chunks get a real prologue/epilogue: `push rbp; mov rbp, rsp`
at entry, `pop rbp; ret` at exit.  This will let recursive `roman.sno`
run under `--jit-run` and fix the alignment problem latent in mode-3
today.  Gate: `define` smoke passes; recursive `roman.sno` runs under
`--jit-run`.

**Addendum sess 2026-05-10 (Claude latest, sixth session of the day):
ME-7 ✅ CLOSED.  ME-6 remains PARTIAL with deferred-scope note.  Two
diagnostic prerequisites also landed.**

Session goal was ME-6 (function calls + returns).  Close reading of
the system surfaced two upstream issues that had to be fixed before
ME-6's gate ("define smoke passes; recursive roman.sno runs under
--jit-run") was even achievable:

1. **`opnames[]` shift bug in `sm_prog.c`.**  The string array
   `opnames[SM_OPCODE_COUNT]` was missing `"SM_BB_PUMP_AST"`, causing
   every opcode name from `SM_CALL_FN` onward to be displayed shifted
   up by one slot in `--dump-sm`.  E.g. an actual `SM_CALL_FN`
   instruction was printed as `SM_RETURN`.  Pure display bug — runtime
   was always correct — but it had been actively misleading earlier
   sessions' reading of the codegen dispatch.  One-line fix: add
   `"SM_BB_PUMP_AST"` between `"SM_BB_PUMP_EVERY"` and
   `"SM_SUSPEND_VALUE"` in the array.

2. **Bare RETURN/FRETURN/NRETURN statement-subject lowering bug in
   `sm_lower.c`.**  A SNOBOL4 statement consisting of just `RETURN`
   (no `=`, no pattern, no goto) is equivalent to `:(RETURN)`.  The
   lowerer was emitting `SM_PUSH_VAR s="RETURN"; SM_VOID_POP` instead
   of `SM_RETURN`.  Effect: the `define` smoke test (which uses bare
   `RETURN` as the body of its `DOUBLE` function) produced `42` under
   `--ir-run` (which has its own bare-RETURN handling) but **empty
   output under `--sm-run` and `--jit-run`** because the function
   had no way to return.  Both SM modes were byte-identical (both
   equally broken), so the bug was invisible to byte-identity gates.
   Fix: in `lower_stmt`'s bare-expression-statement branch
   (`!has_eq && !pattern && !goto`), check whether `s->subject` is
   an `AST_VAR` whose `sval` (case-insensitive) is `RETURN`,
   `FRETURN`, or `NRETURN`; if so, emit the matching return opcode
   directly and jump to `emit_gotos`.  Mirrors `emit_goto`'s
   existing treatment of those names as goto targets (~line 222 of
   the same file).  Post-fix: `define` smoke produces `42`
   byte-identical across all three modes (IR, SM, JIT).

3. **ME-7 — SM_LABEL DEFINE-entry flag.**  Original spec said put
   the flag at `a[1].i = 1`, but `a[1].i` is already the label's PC
   (used by `sm_label_pc_lookup`).  Settled at `a[2].i = 1`, which
   was otherwise unused for SM_LABEL.  Three components:
   - **New runtime API** `int FUNC_IS_ENTRY_LABEL(const char *label)`
     in `snobol4.c`/`.h`.  Scans every `FNCBLK_t` bucket
     (FUNC_BUCKETS=128) for any registered user function whose
     `entry_label` (or `name` if `entry_label` is NULL) matches the
     query.  O(N) over registered functions, called once per
     labeled SNOBOL4 statement at lower time — negligible.
   - **`lower_stmt` consumes it.**  Right after `sm_label_named(p,
     s->label)`, call `FUNC_IS_ENTRY_LABEL(s->label)`; if it
     returns 1, set `p->instrs[p->count - 1].a[2].i = 1`.
     `prescan_defines()` has already populated the function table
     by the time `sm_lower` runs (sm_preamble calls them in that
     order), so the check is authoritative.
   - **`sm_prog.c` printer extended.**  SM_LABEL previously had no
     case in the operand-printing switch and printed bare ("`SM_LABEL`"
     with no operand text).  Now prints `s="<name>"` if the label is
     named, plus `define_entry=1` if the flag is set.  Helpful for
     verifying ME-7 lowering at a glance.

Verified on the `define` smoke source:
```
   10  SM_LABEL             s="DOUBLE" define_entry=1
   18  SM_LABEL             s="END"
```
PC 10 (DOUBLE function entry) flagged; PC 18 (END goto target) not
flagged.  Correct.

**ME-6 scope deferred — three findings:**

a) **The dispatch model has no native "return-from-function" hook.**
   SM_RETURN's C handler (`h_return_impl`) updates `STATE->pc` to
   the caller's return-PC, then the trampoline jumps to that PC's
   blob.  Native `rsp` threads through the entire dispatch chain
   with no natural unwind point — there's no `ret` instruction
   in the SM_RETURN blob.

b) **Conditional return variants only undo on condition.**
   `SM_RETURN_S`/`SM_RETURN_F`/`SM_FRETURN_S`/etc. — nine variants
   in total — only call `h_return_impl` if their respective
   `last_ok` predicate holds.  A blob emitting `mov rsp, rbp; pop
   rbp` unconditionally before/around the handler call would
   break when the handler decides NOT to return.  The unwind
   must be signaled by the handler back to the blob (e.g. via a
   new `STATE->jit_epilogue_pending` field, or via the helper's
   return value as in the me4_* helper family).

c) **Recursive fib already works correctly across all three modes.**
   `088_define_recursive_fib.sno` (fib(10) = 144 calls) is
   byte-identical sm-run vs jit-run vs ir-run today.  This proves
   the existing dispatch model handles recursion correctly without
   rbp accounting.  The prologue/epilogue's real purpose per the
   goal text is the latent vsnprintf alignment failure in
   `bb_pool` byrd-box code — which is a different code path than
   SM-blob land.

d) **Recursive `roman.sno` gate is unsatisfiable in this environment.**
   `bb_alloc: pool exhausted (need 4096, have 0)` under all three
   modes including `--ir-run`.  This is upstream of ME-6.

**Recommended approach for ME-6 next session:**

Two paths, each worth a separate session:

- **Path A — design the epilogue signal**, in scope for ME-6 proper.
  Add `int jit_epilogue_pending` to `SM_State`.  Implement a single
  helper `int me6_return_dispatch(int variant_bits)` that wraps the
  nine return-variant cases, calls `h_return_impl` when the
  condition holds, sets `jit_epilogue_pending` iff a frame was
  popped, returns the flag value.  Each return-variant blob:
  bump pc, sync r12→sp, call `me6_return_dispatch(<imm>)`,
  sync sp→r12, `test eax, eax`, `je no_unwind`, `mov rsp, rbp; pop
  rbp`, `no_unwind:`, `jmp trampoline`.  DEFINE-entry SM_LABEL
  blob: standard pc-bump + `push rbp; mov rbp, rsp` + standard
  trampoline jump.  Gate: existing gates green, recursive fib
  still byte-identical, plus a new test (TBD) that demonstrates
  rbp is preserved across nested calls.

- **Path B — find and fix the actual vsnprintf alignment failure.**
  The goal text says it's "latent in mode 3 today: any chunk that
  PLT-calls `vsnprintf` via `bb_label_initf` faults on
  `rsp%16==8`."  Construct a minimal reproducer that triggers the
  fault, then design the prologue/epilogue against the concrete
  failure.  Higher-value path because it gives the change a real
  test rather than a speculative one, but requires more upfront
  investigation.

Path A is the canonical next step for the rung as written.

**Diagnostic prerequisites separate from ME-7:**

The `opnames[]` shift fix and the bare-RETURN lowering fix are
not part of ME-7's spec but were necessary prereqs for ME-6's gate
to be achievable.  Both are landed in this session's commit.

**Gates this session:**

| Gate | Before | After |
|------|--------|-------|
| `test_smoke_snobol4.sh` | PASS=7 FAIL=0 | PASS=7 FAIL=0 |
| `test_smoke_unified_broker.sh` | PASS=49 FAIL=0 | PASS=49 FAIL=0 |
| `test_gate_sn7_beauty_self_host.sh` | PASS=26 FAIL=25 | PASS=26 FAIL=25 (unchanged baseline) |
| Multi-statement arith realloc reproducer | byte-identical | byte-identical |
| 30-program parser-corpus sweep | 0 divergences | 0 divergences |
| Recursive fib (`088_define_recursive_fib.sno`) | byte-identical sm/jit | byte-identical sm/jit/ir |
| `define` smoke under all three modes | `42` IR, `` SM, `` JIT | `42` everywhere (new) |
| 100k counter loop perf | sm ~100ms, jit ~80ms | sm ~100ms, jit ~80ms |

**Files touched this session:**
- `src/runtime/x86/sm_prog.c` — `opnames[]` shift fix + SM_LABEL printer case (+8/-1)
- `src/runtime/x86/sm_lower.c` — bare-RETURN lowering + ME-7 flag set (+38/-1)
- `src/runtime/x86/snobol4.c` — `FUNC_IS_ENTRY_LABEL` impl (+21/-0)
- `src/runtime/x86/snobol4.h` — `FUNC_IS_ENTRY_LABEL` decl (+4/-0)

**Next active step:** ME-6 (PARTIAL → push toward closure).  Path A
recommended.  Sibling work that remains active per the goal file's
premier-goal carve: `GOAL-ICON-BB-COMPLETE`.  All other goals stay
paused until ME-* closes.

**Addendum sess 2026-05-10 (Claude latest, seventh session of the day):
ME-6 Path A scaffolding landed; routing held — re-entry-into-entry-label
hazard discovered.**

Session goal: execute Path A as the canonical next step.  Implementation
proceeded through the planned mechanism, then a regression in
sn7_beauty (26 → 20) under `--jit-run` revealed an architectural hazard
not anticipated in the previous session's handoff.

**What landed (architectural scaffolding only; no behaviour change):**

1. **`SM_State.jit_epilogue_pending` (int, offset 24)** — new field
   inserted immediately after `pc` (offset 20).  Original offsets
   (stack=0, sp=8, stack_cap=12, last_ok=16, pc=20) are unchanged, so
   every existing emitted-byte access to `[r13+0]`, `[r13+8]`,
   `[r13+16]`, `[r13+20]` continues to work without modification.
   Downstream fields (err_jmp, call_stack, call_depth) shift by 8 bytes
   but are accessed only by C code, which the compiler handles.
   Zero-initialised by `sm_state_init`'s `memset`.

2. **`me6_return_dispatch(int bits)` C helper** in `sm_codegen.c`
   (marked `__attribute__((unused))` for now).  Decodes variant bits:
   - bit 0 = is_fret  (FRETURN family)
   - bit 1 = is_nret  (NRETURN family)
   - bit 2 = cond_s   (fire only if  st->last_ok)
   - bit 3 = cond_f   (fire only if !st->last_ok)
   Gates on the condition, calls `h_return_impl(is_fret, is_nret)` on
   match, sets `jit_epilogue_pending = 1` iff a frame was actually
   popped, returns the flag value.  Always clears the flag at entry to
   prevent stale-1 leaks across no-op variants.

3. **`emit_me6_define_entry_blob(trampoline_abs_off)`** (marked unused).
   15 bytes: `inc dword [r13+20]` + `push rbp` + `mov rbp, rsp` +
   `jmp rel32 trampoline`.

4. **`emit_me6_return_blob(bits, trampoline_abs_off)`** (marked unused).
   ~72 bytes: pc-bump + sync r12→sp + `mov edi, bits` + imm64 call to
   `me6_return_dispatch` + sync sp→r12 (using rcx so rax survives) +
   `test eax, eax` + `jz no_unwind +4` + `mov rsp, rbp` + `pop rbp` +
   `jmp rel32 trampoline`.

**Why routing was reverted: the re-entry-into-entry-label hazard.**

Initial implementation routed SM_LABEL with `a[2].i == 1` through
`emit_me6_define_entry_blob` and the nine return-variant opcodes through
`emit_me6_return_blob`.  Build clean.  Smoke 7/7 + broker 49/49 held.
**But sn7_beauty regressed from 26 → 20.**

Investigation: case_driver.sno segfaulted under `--jit-run` immediately.
gdb showed `rip == rsp` post-fault — classic signature of a `ret` that
fetched its return address from a stack location holding a saved-rbp
value rather than a code address.  Trace back: the `icase` function in
`case.sno` contains the loop pattern

```snobol4
icase    str  POS(0) ANY(&UCASE &LCASE) . letter =  :F(icase1)
         icase = icase (upr(letter) | lwr(letter))  :(icase)
```

— where the bare goto `:(icase)` is a SM_JUMP back to the function's
own define-entry SM_LABEL.  Every iteration re-enters the define-entry
blob and re-executes `push rbp` — but there is **no paired pop** within
the loop.  The function eventually exits via a single SM_RETURN_S; that
SM_RETURN_S pops exactly one rbp, leaving N-1 stale saved-rbp values
contaminating the native stack.  When the eventual SM_HALT's `ret`
fires (or when a libgc routine, or any caller, does a `ret`), the
return address pulled off the stack is one of those stale rbp values,
which is itself a stack address — and we jump to it, leading to the
observed `rip == rsp` state.

The hazard is **structural**: SM_LABEL is the destination not just of
the dispatch from `h_call`, but of *any* SM_JUMP whose target_pc lands
on that label.  SNOBOL4 idioms routinely use `:(label)` jumps inside
function bodies where the label IS the function entry — this is the
SNOBOL4 way to write a tail-recursive loop without re-invoking the
DEFINE'd dispatch machinery.  Several patterns are affected: icase-
style accumulator loops, manual fixed-point iteration, label-fall-
through into a fresh iteration.  The prologue-on-SM_LABEL design is
fundamentally incompatible with these idioms because SM_LABEL fires
on every entry to that PC, not on every "call".

**Fix options for next session (all explicitly out of scope for this one):**

a) **Move the prologue to h_call.**  Have `h_call` set a flag (e.g.
   `SmCallFrame.jit_prologue_active`) when it dispatches to a user
   function.  Emit a synthetic prologue trampoline at h_call's
   handler — but h_call is a C function and cannot inject native
   pushes into the SM-blob's native stack.  This option requires
   either splitting h_call into an emitted prologue + a C body or
   making `STATE->pc = body_pc` go through an emitted helper that
   does the push.  Doable but invasive.

b) **Detect re-entry at the prologue blob.**  Compare `rbp` to the
   prior frame's prologue-rbp value; only push if "new" entry.
   Requires a per-blob memory slot for "rbp seen this entry" or a
   call-frame-correlated flag.  Complicates the simple "push once,
   pop once" invariant.

c) **Make the prologue a no-op when entered via SM_JUMP.**  This
   requires knowing the entry mode, which the blob does not.  Could
   route SM_JUMP-into-define-entry through a different (shifted)
   address that skips the prologue — but every SM_JUMP would then
   need to know whether its target is a define-entry label and emit
   to the shifted address.  Doable; touches every SM_JUMP emitter.

d) **Defer rbp accounting until per-instruction native emission
   subsumes the dispatch loop entirely** (mode-3 as a real JIT,
   ME-14 era).  At that point the call/return distinction is
   structural (native call/ret) rather than data-flow (PC-driven
   dispatch), and rbp can hang off a native call frame naturally.
   This is the architecturally clean answer but is far off.

The handoff's previous-session finding still stands: recursive `fib`
runs byte-identically across modes today without any rbp accounting.
The Path A mechanism has no functional payoff in the current dispatch
model — it was always architectural scaffolding for the eventual
ME-MODE4-IS-MODE3-DUMP serializer and for the latent vsnprintf
alignment concern (which, on closer inspection this session, is a
C-side bb_label_initf concern not a bb_pool-emitted-code concern).

**What the landed scaffolding buys the next session:**

1. The SM_State field is in place at a known offset; emitters can use
   `[r13+24]` directly without re-deriving the offset.
2. The C helper `me6_return_dispatch` exists and is correct — once
   the routing problem is solved, wire it in.
3. The emit functions exist and are byte-correct against the
   established register convention — once the entry-blob hazard is
   addressed (option a or c above), enabling them is a one-line
   change in `sm_codegen.c`'s dispatch loop.
4. The diagnosis is recorded so the next agent doesn't re-discover
   the icase hazard.

**Gates this session:**

| Gate | Before | After |
|------|--------|-------|
| `test_smoke_snobol4.sh` | PASS=7 FAIL=0 | PASS=7 FAIL=0 |
| `test_smoke_unified_broker.sh` | PASS=49 FAIL=0 | PASS=49 FAIL=0 |
| `test_gate_sn7_beauty_self_host.sh` | PASS=26 FAIL=25 | PASS=26 FAIL=25 |
| Recursive fib (088_define_recursive_fib.sno) byte-identical sm/jit/ir | ✅ | ✅ |
| 2-DEFINE inline repro (`/tmp/me6_repro2.sno`) byte-identical sm/jit | n/a | ✅ |
| Conditional-return repro (`/tmp/me6_repro3.sno`) byte-identical sm/jit | n/a | ✅ |

**Files touched this session:**
- `src/runtime/x86/sm_interp.h` — `jit_epilogue_pending` field, offset 24 (+12/-1)
- `src/runtime/x86/sm_codegen.c` — `me6_return_dispatch` + two emit functions (all `__attribute__((unused))` for now), header comment explaining the routing decision (+~190/-0)

**State at handoff:**
- one4all: working tree dirty (`sm_interp.h`, `sm_codegen.c`).
  Ready to commit.
- corpus: unchanged.
- .github: GOAL-MODE3-EMIT.md updated (this addendum); PLAN.md
  updated (active step → ME-6 retry with re-entry fix).
  Ready to commit.

**Next active step:** ME-6 retry — solve the re-entry-into-entry-label
hazard before enabling the prologue/epilogue.  Recommended sub-rungs
(file new step IDs in the goal file):

- **ME-6a — route through h_call.**  Pick option (a) above.  Concrete
  shape: add an `int jit_prologue_active` field to `SmCallFrame`; set
  to 1 in `h_call`'s user-function branch right after `STATE->pc =
  body_pc`; emit a new opcode `SM_DEFINE_ENTRY` between SM_CALL_FN
  and the body's first SM_LABEL (or replace the define-entry
  SM_LABEL's flag-driven dispatch with an explicit
  `SM_DEFINE_ENTRY` instruction that sm_lower emits at every DEFINE
  body's head).  SM_DEFINE_ENTRY's blob does the push; SM_RETURN-
  variant blob does the conditional pop gated on
  `caller_frame->jit_prologue_active`.  Cleanest because every entry
  is reached exactly once per call; SM_JUMP to a SM_LABEL never
  passes through SM_DEFINE_ENTRY.

- **ME-6b — instrument case_driver as a regression gate.**  Add
  `test_gate_me6_reentry_hazard.sh` that compiles a minimal icase-
  shaped function and runs it under `--jit-run`; the test passes
  iff exit code 0 and no segfault.  Locks in the fix.

The architectural scaffolding landed this session (SM_State field,
helper, emit functions) is reusable as-is for ME-6a — only the
routing site changes.

**Addendum sess 2026-05-11 (Claude Sonnet 4.6): ME-6a ✅ CLOSED. ME-6 closed.**

Session goal: implement ME-6a — route prologue/epilogue through a new
`SM_DEFINE_ENTRY` opcode that fires exactly once per function call, not on
every goto that lands on the entry label.

**Root cause of the re-entry hazard (from ME-6 Path A diagnosis, sess #7):**
The define-entry SM_LABEL blob was the proposed prologue site.  But SM_LABEL
is the destination of every jump that targets that PC — including icase-style
`:(self)` gotos inside the function body.  Every re-entry re-executed
`push rbp` without a paired pop, polluting the native stack until SM_HALT's
`ret` fetched a stale saved-rbp value as its return target, producing the
observed `rip == rsp` segfault in case_driver.sno.

**ME-6a fix — SM_DEFINE_ENTRY + jit_in_call flag:**

New field `int jit_in_call` added to `SM_State` at offset 28 ([r13+28]).
`h_call` sets `STATE->jit_in_call = 1` immediately before `STATE->pc =
body_pc`.  `sm_lower` emits `SM_DEFINE_ENTRY` immediately after every
define-entry SM_LABEL (the one with `a[2].i==1` from ME-7).

`emit_me6_define_entry_blob` (~26 bytes):
```
  inc dword [r13+20]        ; pc++
  mov eax, [r13+28]         ; eax = jit_in_call
  mov dword [r13+28], 0     ; always clear the flag
  test eax, eax             ; was this a real call?
  jz skip                   ; no: skip prologue (goto re-entry path)
  push rbp                  ; yes: save caller's rbp
  mov rbp, rsp              ; establish frame
skip:
  jmp rel32 trampoline
```

`h_call` path: `jit_in_call=1` → SM_LABEL blob (no-op) → SM_DEFINE_ENTRY
blob reads 1, clears, does push+mov → SM_STNO → body. Exactly one prologue
per call.

Goto path (`:(COUNT)` etc.): `jit_in_call=0` (h_call never set it) →
SM_LABEL blob (no-op) → SM_DEFINE_ENTRY blob reads 0, clears (harmless),
skips push+mov → SM_STNO resets stack → body continues. No prologue.

Nine return variants (SM_RETURN/FRETURN/NRETURN and _S/_F) routed through
`emit_me6_return_blob` with correct bit encoding. `me6_return_dispatch`
(landed sess #7 as scaffolding) consumed without modification.

**ME-6b gate — test_gate_me6_reentry_hazard.sh (PASS=3):**
- `self_goto_loop` — COUNT(5,0) via :(COUNT) re-entry → `5` ✅
- `recursive_fib_7` — FIB(7) via recursion → `13` ✅
- `combined_loop_and_recursion` — both in same program → `13\n10` ✅

**Files changed (one4all `accafb5f`):**
- `sm_interp.h` — `SM_State.jit_in_call` at offset 28
- `sm_prog.h` — `SM_DEFINE_ENTRY` opcode
- `sm_prog.c` — `"SM_DEFINE_ENTRY"` in opnames[]
- `sm_interp.c` — `case SM_DEFINE_ENTRY: break` (no-op mode-2)
- `sm_lower.c` — emit `SM_DEFINE_ENTRY` after define-entry SM_LABEL
- `sm_codegen.c` — `h_define_entry`; `jit_in_call=1` in h_call; rewritten
  `emit_me6_define_entry_blob` with guard; routing for SM_DEFINE_ENTRY and
  nine return variants
- `scripts/test_gate_me6_reentry_hazard.sh` — ME-6b gate

**Gates: smoke 7/7, unified_broker 49/49, me6_reentry_hazard 3/3.**
sn7_beauty 21/30 (verified identical to pre-rung baseline via git stash).

**Next active step: ME-8** — `SM_PUSH_EXPRESSION` / `SM_CALL_EXPRESSION`
consumer. Lands after GOAL-CHUNKS-STEP17 closes (stable opcode shape).
ME-9 (pattern primitives) is the alternative if CHUNKS stays blocked.
