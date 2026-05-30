# REGISTER-LAYOUT.md — SCRIP mode-3 x86-64 register convention

⛔ **This is the locked register convention for mode-3 SM-blob emission
and for flat-BB glob emission.**  Every blob, every glob, every PLT
call signature in mode 3 obeys this.  Changes require an explicit goal
rung and Lon sign-off.

**Sources of truth referenced in this doc:**
- `archive/backend/bb_boxes.s` — proven 25-box library, 106/106 oracle.
- `/home/claude/x64/int.h`, `int.asm`, `sbl.min` — SPITBOL x64
  MINIMAL register map and save/restore discipline.
- `/home/claude/csnobol4/v311.sil`, `snobol4.c`, `res.h`,
  `include/macros.h` — CSNOBOL4 cstack discipline and PDLPTR pattern
  history list.
- `src/runtime/x86/bb_flat.c` — live flat-glob emitter; the `r10`
  convention this doc locks already ships there.
- `ARCH-x86.md` — defines the flat-BB ABI, the stackless-box discipline,
  and the intra-/extra-BLOB jump rules this doc operates against.

---

## TL;DR — register assignments

| Reg | Class | Role | When loaded / saved |
|-----|-------|------|----------------------|
| **r12** | callee-saved | **SM value stack top-of-stack pointer** (FORTH-style) | Loaded once at `sm_jit_run` entry from `[rel sm_state_stack_base]`; reset to stack base by SM_STNO blob; preserved by every PLT call via SysV |
| **r10** | caller-saved | **Current BB DATA-block pointer** — `[r10+N]` addresses every box-local in the active BLOB | Loaded by each BLOB's α-preamble as `lea r10, [rip + Δ_data]` (static globs) or as the result of an `rt_alloc_blob_data()` call (variant globs and re-entries); constant inside a BLOB; saved in SmCallFrame when SM_CALL_EXPRESSION fires from inside BB land |
| **rbp** | callee-saved | DEFINE'd function frame pointer (when active) | `push rbp; mov rbp, rsp` at function α-entry; `pop rbp; ret` at exit |
| **rbx, r13, r14, r15** | callee-saved | **Free.** Available for per-rung scratch / future claims | — |
| **rax, rdi, rsi, rdx, rcx, r8, r9, r11** | scratch | C-ABI scratch for PLT arg shuffle and SM-blob temporaries | Caller-saved per SysV |
| **xmm0–xmm15** | scratch | Real arithmetic when DESCR_t is real | Caller-saved per SysV |

**Two claimed callee-saved registers in mode 3:** `r12` (SM value stack
TOS) and `rbp` (function frame when active).  One per-BLOB register:
`r10` (BB LOCAL).  Four callee-saved registers genuinely free for
future use.  Eight GP scratch registers plus sixteen SSE scratch
registers for per-blob computation.

`SM_State` itself lives as a static global in `.bss`, reached via
RIP-relative `[rel sm_state + offset]` when needed (which is rare —
SM_STNO blob to reload the stack-base pointer; SM_EXEC_STMT entry to
spill canonical state).  No register is reserved for `SM_State*`.

---

## Stacks and stack-like structures

> ⛔ **CORRECTION (2026-05-30, GROUND ZERO 3).** The "SM value stack" described
> below was a WRONG premise for Icon (and is being removed from Icon BB emission).
> Icon Byrd boxes are stackless per `ARCH-x86.md` §"Boxes are stackless": values
> live in **flat per-box DATA slots** and flow by static `jmp` wiring (consumer
> reads its operand boxes' slots directly); unbounded-depth backtrack state lives
> in **per-box .bss arenas** (ARBNO / recursion), not on any value stack. The
> stackless emitter that benchmarked faster than SPITBOL is archived at
> `one4all/archive/backend/emit_emitters/emit_x64.c`; references in
> `one4all/refs/bb/`. The SM value stack (`r12` TOS, `rt_push_*`/`rt_pop_*`) must
> NOT be used by the Icon path. See `GOAL-ICON-BB.md` → "GROUND ZERO 3".

SCRIP has **two stacks** and one **tree of heap-resident DATA blocks**.
The tree replaces what SPITBOL/CSNOBOL4 implement as a third stack
(the pattern history stack).

### Stack 1 — SM value stack (heap, `r12 = TOS pointer`)

Allocated and realloc-grown by the runtime; anchored at `r12` as a
FORTH-style top-of-stack pointer.  Holds DESCR_t values (16 bytes
each).

**Push:**
```asm
mov   [r12],     rax    ; descr.v (8 bytes)
mov   [r12 + 8], rdx    ; descr.data (8 bytes)
add   r12, 16
```

**Pop:**
```asm
sub   r12, 16
mov   rax, [r12]
mov   rdx, [r12 + 8]
```

**Multi-pop (compile-time-known depth N):**
```asm
sub   r12, N*16         ; discard N entries; reads at [r12], [r12+16] etc.
```

Random access at compile-time-known depth N below TOS:
`[r12 - (N+1)*16]`.  Depths are always known at emit time because each
opcode consumes a fixed-by-opcode number of operands (SM_ADD pops 2,
SM_PAT_CAT pops 2, SM_EXEC_STMT pops 2 or 3 depending on `has_repl`,
etc.).  No runtime depth computation needed.

**Reset at every statement boundary** by the SM_STNO blob (the mode-2
contract at `sm_interp.c:295`):
```asm
mov   r12, [rel sm_state_stack_base]   ; reset TOS to base
```

This is the fix for the live ME-4 realloc bug — mode-2 enforces
`st->sp = 0` at every statement; mode-3 must replicate this discipline.

Used by:
- All SM_PUSH_* / SM_POP / arithmetic / string opcodes.
- Pattern construction (after ME-1 — pat-stack collapsed in).
- SM_EXEC_STMT operands (subject, pattern, replacement).
- SM_CALL_EXPRESSION argument and return-value handoff.

### Stack 2 — Native stack (`rsp`)

Used by:
- C-ABI `call`/`ret` for PLT calls into libscrip_rt.
- DEFINE'd function prologue (`push rbp; mov rbp, rsp`) / epilogue
  (`pop rbp; ret`).
- Source-BLOB save of `r10` when emitting a call-style extra-BLOB
  jump (rare; capture-callback case).

Pattern-engine state does **not** live on `rsp`.

### Tree — BB DATA blocks (heap; `r10` walks it)

**This is where pattern-match backtracking state lives in SCRIP.  Not
on any stack.  Per `ARCH-x86.md` §"Boxes are stackless":**

Each Byrd box, when its α-port is entered, allocates a **fresh DATA
block**, writes the previously-active DATA block's address into the
new block's save-list header field, and sets `r10` to point at the
new block.  The box's body addresses every local as `[r10 + N]`.  On
γ-exit (success), the box returns `rax:rdx = σ:δ` to the parent; the
parent box's CODE has its own DATA block already, addressed by the
parent's own r10 (restored by the parent BLOB's α-preamble when
control returns to it).  On ω-exit (failure), the box's DATA block is
unlinked from the chain (parent's r10 becomes active again) and freed
or pooled.

DATA blocks form a **tree** rooted at the outermost match's root box.
ARBNO's iterations form a sibling chain inside ARBNO's DATA.  FENCE
records its "outer base" as a pointer to the DATA block of the box
that was active when FENCE was α-entered — failures inside the FENCE
argument cannot unwind past that pointer.  Pattern alternatives are
simply child boxes of an ALT node, each with its own DATA block when
α-entered, each holding the cursor it would resume scanning from on
retry.

What SPITBOL stores on its `pmhbs`-rooted history stack (cursor saves,
failback pointers, FENCE bases, ARBNO iteration markers) SCRIP stores
in DATA block fields.  The save IS the allocation; the restore IS the
unlink.

**Re-entry safety:**  Box CODE is reusable but not necessarily
re-entrant.  Two simultaneous matches against the same box CODE (e.g.
when `*P` fires twice nested) are safe only because each match gets
its own DATA tree — fresh allocation per α-entry.

---

## `*P` and `*(expr)` — the deferred-evaluation cases

These two cases drive the design of how SM-blob land and BB-glob land
interoperate.  Both run inside an outer pattern match (i.e. inside BB
land); both transfer control to compiled code that they share with
other call sites; both must restore the calling BLOB's `r10` on
return.

### `*P` where P holds a PATTERN value

P's value is a DESCR_t whose `.ptr` references the root box of a BLOB
graph emitted when that pattern was constructed.  **The BLOB's CODE is
emitted once and shared by all matches against P.**  Every time `*P`
fires at match time, the DEFER box that wraps `*P`:

1. Looks up P's current value via NV table.
2. Calls `rt_alloc_blob_data(P_root_box)` to allocate fresh DATA
   blocks for every box in P's BLOB graph.  The runtime walks P's box
   tree, allocates a DATA block for each, chains them per the
   parent/child structure, returns the root DATA block's address.
3. Loads `r10 = root_data_block_address`.
4. Jumps to P's BLOB CODE entry.

When P's BLOB γ/ω-exits, control returns to the DEFER box's logic.
The DEFER box's own DATA block (allocated by its own α-preamble) was
addressable via the DEFER box's own r10, which the parent BLOB's
preamble had set.  When P's BLOB jumped in, P's α-preamble overwrote
r10 with P's root DATA.  **On return from P, the DEFER box must
restore its own r10** — which means the DEFER box, before jumping into
P, has to save its own r10 somewhere.  The natural place is in a
field of the DEFER box's own DATA block:

```asm
;; DEFER box α-entry sequence (inside the parent BLOB, after r10 has
;; been set to the DEFER box's DATA)
mov   rdi, [rel P_descr_address]    ; load P's DESCR_t
call  rt_alloc_blob_data            ; rdi → root DATA addr in rax
mov   [r10 + DEFER_SAVED_R10], r10  ; save DEFER's own r10 (= our DATA)
                                    ; — actually we need this BEFORE
                                    ; the call clobbers r10; see below
mov   r10, rax                      ; switch to P's BLOB's root DATA
jmp   [rax + ROOT_BOX_CODE_PTR]     ; jump into P's CODE
;; P γ/ω-exits via jmp back to the address stored in its root DATA's
;; γ_ret or ω_ret field — which the DEFER box wrote before jumping in.
;; On return, r10 is *not* automatically restored; the resume code
;; below does it.
.defer_resume_gamma:
mov   r10, [DEFER_OWN_DATA_FIELD_REACHABLE_FROM_PARENT]
                                    ; restore DEFER's own r10
;; ...read P's result, transition to γ port of DEFER box
```

The order of operations matters: r10-save must precede the call that
clobbers r10.  Practical fix: save r10 first, *then* call
`rt_alloc_blob_data`, *then* mov r10 = rax.  Or pass DEFER's DATA
address to `rt_alloc_blob_data` so it links DEFER's DATA into the new
tree's parent slot.

### `*(expr)` — the DEFER box wrapping an SM EXPRESSION body

`expr` here is an arbitrary expression — could be `*(X + 1)`, could be
`*(X ? P Q R)` involving sub-patterns.  At lower time, `sm_lower`
emitted a labeled SM body for `expr`:

```
                SM_JUMP   skip_expr_NN
expr_body_NN:   <SM ops to evaluate expr>
                SM_RETURN
skip_expr_NN:   ...
                SM_PUSH_EXPRESSION  expr_body_NN_entry_pc
```

The DEFER box's α-entry, instead of jumping into another BLOB's CODE
like `*P` does, performs **SM_CALL_EXPRESSION** with the entry_pc to
the expression body:

1. Spill r10 (DEFER's own DATA) into the SmCallFrame's `caller_r10`
   field.
2. Push the SmCallFrame: `{ret_pc=defer_resume, caller_r12, last_ok,
   caller_r10}`.  Increment `st->call_depth`.
3. Reset r12 to the saved-aside SM stack base so the expression body
   runs on its own empty operand stack (this preserves the mode-2
   contract).
4. Jump to `expr_body_NN_entry_pc`.

The expression body runs in SM-blob land.  It may itself trigger a
sub-pattern match via SM_EXEC_STMT (for `X ? P Q R`, the `?` operator
becomes an SM_EXEC_STMT call) — that call hands a fresh BB tree to
the runtime, which allocates its own DATA blocks, runs to completion,
and returns.  When SM_RETURN finally fires at the end of
`expr_body_NN`:

1. Pop the SmCallFrame.
2. Restore r10 = `frame.caller_r10` (now back inside the DEFER box's
   DATA).
3. Restore r12 to the caller's TOS; result of expression is on top.
4. Jump to `frame.ret_pc` (= the DEFER box's resume point inside the
   parent BLOB).

**Why the SmCallFrame needs `caller_r10` and not just for this case:**
`SM_CALL_EXPRESSION` can be invoked from either SM-blob land (no
active BLOB, r10 is dead) or from BB land (the DEFER box case, r10
holds the DEFER box's DATA).  The emitter knows which case applies at
emit time — it knows whether the SM_CALL_EXPRESSION emission site is
inside an emitted BLOB or not.  When from SM-blob land, the
`caller_r10` field is written as 0 (or undefined; ignored) and
restoration is skipped.  When from BB land, the field is loaded with
`r10` before the call and restored on return.

### "The SM/BB code is fixed but new local is allocated"

Captures the essence: **code is shared, DATA is per-invocation**.  This
applies recursively.  When `*(X ? P Q R)` fires, the DEFER box gets
fresh DATA, then the expression body (SM code) gets a fresh
SmCallFrame, then if X ? matches against `P Q R` and P has its own
sub-patterns, each sub-pattern's BLOBs get fresh DATA trees, etc.  At
every level the CODE is the address emitted once at `sm_lower` time;
the LOCAL is freshly allocated at every entry.

This is also why P being a pattern value works for `*P`: P's BLOB CODE
sits in a `bb_pool` slot at one address forever; P's BLOB DATA is
ephemeral, allocated per `*P` invocation.  Re-entering the same P
recursively is fine because each entry gets its own DATA tree.

---

## Push/pop matrix — every boundary

| Boundary | Pushed | Popped | Where |
|----------|--------|--------|-------|
| `sm_jit_run` entry | (nothing) | (nothing) | C compiler's prologue saves r12/r13/r14/r15/rbx/rbp per SysV.  `sm_jit_run` is the C frame holding them. |
| **SM_STNO** (statement boundary) | (nothing) | (nothing) | Inline blob: `mov r12, [rel sm_state_stack_base]` — reset TOS, handle realloc by reloading the base. |
| **Intra-BLOB jump** | (nothing) | (nothing) | Plain `jmp rel32 target`.  r10 unchanged. |
| **Extra-BLOB tail-jump** | (nothing) | (nothing) | Plain `jmp rel32 target`.  Destination BLOB's α-preamble loads its own r10; source BLOB's r10 dies. |
| **Extra-BLOB call-style jump** (rare) | `push r10` before outbound `jmp`/`call` | `pop r10` at resume point inside source BLOB | Source BLOB's responsibility. |
| **α-entry of any BLOB** | (DATA allocation is the save) | — | First action of every BLOB: allocate DATA (or use the pre-allocated address passed in), chain to parent, set `r10 = new_block`. |
| **γ-exit of a BLOB** (success) | — | (DATA chain unlink IS the restore) | Parent's r10 becomes the active LOCAL again; success result in `rax:rdx`. |
| **ω-exit of a BLOB** (failure) | — | (DATA unlink + parent's β retry) | Parent's r10 becomes active; parent's β-port fires; current BLOB's DATA may be freed or pooled. |
| **PLT call from SM-blob land** | (nothing extra) | (nothing extra) | r12 preserved by SysV; r10 not used in SM-blob land. |
| **PLT call from inside a BLOB** | `mov [r10 + SAVED_R12], r12` ; (caller-saved scratch is the caller's problem) | `mov r12, [r10 + SAVED_R12]` after call | r12 is callee-saved by SysV — the saving is needed only when the called function may itself reset r12 (e.g. `rt_exec_stmt` does, because the sub-statement runs on a fresh operand stack); for read-only helpers no save is needed. |
| **SM_PUSH_EXPRESSION** | DESCR_t with `{v=DT_E, slen=1, i=entry_pc}` onto value stack | — | Plain SM stack push. |
| **SM_CALL_EXPRESSION from SM-blob land** | `SmCallFrame{ret_pc, caller_sp=r12_value_before_reset, last_ok, caller_r10=0}` on `st->call_stack[]` | mirror restore at SM_RETURN | Heap-resident frame array. |
| **SM_CALL_EXPRESSION from BB land** | `SmCallFrame{ret_pc, caller_sp=r12_value_before_reset, last_ok, caller_r10=current_r10}` on `st->call_stack[]` | restore `r10` from frame at SM_RETURN | The emitter knows it's from BB land because the emission site is inside an emitted BLOB. |
| **DEFINE'd fn call (SM_CALL_FN)** | SmCallFrame + N saved NV slots + frame.retval_name | mirror restore + retval write at SM_RETURN | Existing `st->call_stack[]` mechanism with `nsaved` NV-slot saves. |
| **Pattern alternatives** (during match) | DATA-block allocation (the save) | DATA-block unlink (the restore) | Allocation is on the heap-backed DATA-block pool.  No `rsp` push. |
| **FENCE** | FENCE box's DATA records pointer to outer-active DATA block as `fence_base` | FENCE box ω-exits to its parent; failures inside FENCE-arg cannot escape past `fence_base` | DATA field, not a stack push. |
| **ARBNO** | Per-iteration DATA blocks form a sibling chain inside ARBNO's DATA | Failure pops the chain head; commit on body-failure when zero iterations is acceptable | DATA chain, not a stack push. |
| **`$` / `.`** (pattern assignment) | Assignment node's DATA records the assignment target and cursor at activation; defers actual assignment to end-of-match if alternatives exist behind | End-of-match scan walks DATA chain looking for pending assignments | DATA fields, not a stack push. |
| **EVAL / `*expr` re-entry mid-pattern** | (subsumed by SM_CALL_EXPRESSION from BB land — same mechanism) | (subsumed) | The BB engine's per-box DATA chain survives the call automatically; only the SmCallFrame mechanism needs to act. |

Most boundaries cost nothing on rsp.  The only rsp interactions are
the standard C-ABI for PLT calls, the DEFINE'd function frame, and
the rare call-style extra-BLOB jump's `push r10`.  The expensive
boundaries (function calls, EXPRESSION calls) use the heap-resident
SmCallFrame array — already present in `SM_State`, no new mechanism.

---

## Stacks in SPITBOL, CSNOBOL4, and SCRIP

| | Operand stack | Pattern history | Function frames | C/native stack |
|---|---|---|---|---|
| **SPITBOL** | (in registers wa/wb/wc — no operand stack) | folded into `xs = rsp` | folded into `xs = rsp` (PROC/EXI discipline) | `xs = rsp` (one stack, three uses) |
| **CSNOBOL4** | `cstack` (heap) — descriptors and specifiers | `PDLPTR`/`PDLEND` (separate heap area) | folded into `cstack` (EXPVAL pushes state) | C stack used implicitly by gcc-translated SIL handlers |
| **SCRIP** | SM value stack — heap, `r12` = TOS | **DATA-block tree per BB** — heap, no stack at all | `SmCallFrame` array — heap, indexed by `st->call_depth` | `rsp` — C-ABI calls, DEFINE'd fn frames (`rbp`), rare extra-BLOB r10 saves |

**SCRIP has fewer stacks than CSNOBOL4 because the BB engine
replaces the pattern history stack with a heap-allocated DATA-block
tree.**  This is not an optimization; it is the consequence of the
Byrd-box model.  Boxes are stackless; their DATA blocks are the
alternatives; backtracking is tree traversal, not stack popping.

---

## Why this layout — evidence base

### r12 = SM value stack TOS (FORTH-style, single register)

FORTH idiom: one register holds the data-stack pointer, post-incremented
on push.  Mirrors SPITBOL's `xs = rsp` discipline (one register
addresses the stack; everything else is `[xs + N]`) but applied to the
operand stack, not the history stack.

Why single register (TOS) rather than {base, sp}?  All pop-depths are
compile-time-known per opcode — `SM_ADD` pops 2, `SM_PAT_CAT` pops 2,
`SM_EXEC_STMT` pops 2 or 3.  Random access at depth N is `[r12 -
(N+1)*16]`, one SIB-encoded mov.  No runtime depth computation.  Single
register is sufficient and frees one more register for future use.

Mode-2's `SM_State.stack` array is the underlying memory; mode-3
treats `r12` as the moving pointer into that array.  The
`sm_state_stack_base` global lets SM_STNO reset TOS without reading
the SM_State struct.

### r10 = BB DATA-block pointer (already in `bb_flat.c`)

Convention pre-dates this doc: `bb_flat.c` already loads `r10` at
glob entry as `lea r10, [rip + Δ_data]` and accesses every box-local
as `[r10 + N]`.  This doc promotes it from "what bb_flat happens to
do" to "the locked convention" and formalizes:

1. Re-entries to the same BLOB CODE (e.g. `*P` firing twice) allocate
   **fresh DATA** per entry — the CODE is reusable, the DATA is per-
   invocation.  Variant pattern globs (today) and static globs (after
   mode-4 emit) both follow this discipline.
2. Intra-BLOB jumps never touch r10.  Extra-BLOB tail-jumps don't
   touch it either (destination's α-preamble loads its own).  Only
   call-style extra-BLOB jumps (rare; capture callbacks) need source-
   BLOB `push r10` / `pop r10`.
3. PLT calls from inside a BLOB don't preserve r10 (caller-saved per
   SysV), so flat-globs forbid PLT calls inside themselves
   (`flat_is_eligible_node` enforces).  Variant globs that need PLT
   calls handle the r10 save themselves at the call sites.

Why caller-saved (not callee-saved)?  C-ABI assignment in System V.
Cannot be changed without breaking interop with libscrip_rt.so.

### rbx, r13, r14, r15 — held free

No current need; reserving them now would either lock in a design
without evidence or waste them.  Mode-3 inline blobs use the SysV
scratch set (rax/rdi/rsi/rdx/rcx/r8/r9/r11) for short-lived per-blob
computation — eight registers, far more than any single blob needs.
Future rungs (SM_CALL_FN's NV-slot saving, more complex pattern
operators, optimization passes) may claim one or more of these; that
claim happens with a new HQ rung that justifies it.

### SM_State* not in any register

`SM_State` is a single global.  Accessing it via `[rel sm_state +
offset]` costs 6–7 bytes per access vs 4 bytes via a register pin.
The accesses are rare (SM_STNO, SM_EXEC_STMT, SM_CALL_*) — not in the
hot push/pop path.  Pinning a register here would burn a callee-saved
register for marginal gain.

### rbp = DEFINE'd function frame ptr

Standard SysV-compatible discipline.  `push rbp ; mov rbp, rsp` at
function α-entry; `pop rbp ; ret` at ω-exit.  Required to preserve
16-byte alignment for PLT calls inside function bodies (which can hit
`vsnprintf` etc.).  When not in a function, rbp is treated as
callee-saved scratch.

---

## SPITBOL register map (for reference)

| MINIMAL | x86-64 | Class | Role |
|---------|--------|-------|------|
| IA | r12 | callee-saved | Integer accumulator |
| W0 | rax | scratch | Wide-zero / temp |
| WA | rcx | scratch | Working register A |
| WB | rbx | callee-saved | Working register B (cursor in match) |
| WC | rdx | scratch | Working register C |
| XL | rsi | scratch | Index-left (source) |
| XR | rdi | scratch | Index-right (current node ptr) |
| XS | rsp | (special) | History stack = native stack |
| XT | rsi (alias) | scratch | Temporary (aliased to XL) |
| CP | r13 | callee-saved | Code pointer (current opcode-stream PC) |
| RA | xmm12 | (preserved) | Real accumulator |

SPITBOL's `save_regs` / `restore_regs` (`int.asm:351`/`365`) save these
to a fixed `reg_block` in `.bss` whenever MINIMAL calls into C OSINT.
SCRIP needs no equivalent: SysV callee-saved discipline plus the
sm_jit_run C-frame's prologue/epilogue handle re-entry safety for
free.

---

## CSNOBOL4 stack realization (for reference)

```c
// include/macros.h:132
S4_EXTERN VAR struct descr *cstack;

// include/macros.h:152
#define PUSH(x)   D(cstack+1) = D(x);          cstack++;          OFCHK()
#define POP(x)    cstack--; UFCHK();           D(x) = D(cstack+1)
#define SPUSH(x)  _SPEC(cstack+1) = _SPEC(x);  cstack += SPEC/DESCR; OFCHK()
#define SPOP(x)   cstack -= SPEC/DESCR;        UFCHK(); _SPEC(x) = _SPEC(cstack+1)
```

Both PUSH and SPUSH operate on the same `cstack` — descriptor and
specifier are stored on one stack.  Separately, `PDLPTR`/`PDLHED`/
`PDLEND` manage the pattern history stack in its own heap area.  So
CSNOBOL4 has **two stacks**: `cstack` (operands + frames) and PDL
(pattern history).

SCRIP folds those further: SM value stack (= `cstack` minus the
specifier merge, since DESCR_t is uniform width) + DATA-block tree
(replaces PDL because Byrd-boxes own their alternatives).

---

## EVAL/CODE/EXPRESSION re-entrancy

SPITBOL's `evalp` (`sbl.min:20767–20825`) saves 6 words on `xs` per
nested EVAL:

```
push xr     ; node pointer
push wb     ; cursor
push r_pms  ; subject string pointer
push pmssl  ; subject string length
push pmdfl  ; dot flag
push pmhbs  ; history stack base
```

CSNOBOL4's `EXPVAL` (`v311.sil:2707–`) saves 14 descriptors + 4
specifiers = 18 fields per nested EVAL — but most of those are
SIL-machine state (OCBSCL/OCICL = code base + offset; PATBCL/PATICL =
pattern code base + offset; WPTR/XCL/YCL/TCL = working slots) that
SCRIP does not have because SM_Program is a flat array and DESCR_t is
the universal value.

The SCRIP equivalent — SM_CALL_EXPRESSION — saves just:
- `ret_pc` — SM-PC to resume at.
- `caller_sp` (effectively the r12 value before reset).
- `last_ok` — currently the only SM_State field sub-expressions mutate.
- `caller_r10` — only when the call originates from BB land
  (the DEFER box case).

That's 3 or 4 words.  The cursor/subject/length equivalents live in
the SM_State struct already and survive across the call by virtue of
sitting in `SM_State` (which is not mutated by sub-expression code).
The `pmhbs`/`pmdfl` equivalents are not state to save — they are
pointers into the DATA-block tree, and the tree itself survives the
SM call because DATA blocks are heap-allocated and reachable from the
outer pattern's root box.

---

## Audit checklist before ME-4-post commits

When ME-4-post (the inline-native blob re-emission against this
locked convention) lands, every emitted blob must satisfy:

- [ ] **Stack push:** `mov [r12], rax ; mov [r12+8], rdx ; add r12, 16`.
- [ ] **Stack pop:** `sub r12, 16 ; mov rax, [r12] ; mov rdx, [r12+8]`.
- [ ] **Multi-pop:** `sub r12, N*16` where N is compile-time-known.
- [ ] **Random access:** `[r12 - (N+1)*16]` where N is compile-time-known.
- [ ] **SM_STNO blob:** `mov r12, [rel sm_state_stack_base]`.  Single
      instruction, ~7 bytes.
- [ ] **PLT calls** that don't reset r12 (most read-only helpers):
      no save needed (SysV preserves it).
- [ ] **PLT calls** that may reset r12 (`rt_exec_stmt`, `rt_call_fn`):
      spill r12 to `[rel sm_state.sp_or_top]` before; reload after.
- [ ] **No emitted code writes r10** in SM-blob land.  Only BB-glob
      α-preambles write r10.
- [ ] **Inside a BLOB, r10 is constant** for the entire body.  Intra-
      BLOB jumps don't touch it.  PLT calls inside a BLOB save/reload
      r10 themselves (or — preferred — flat-globs forbid PLT calls
      via `flat_is_eligible_node`).
- [ ] **DEFINE'd function entry:** `push rbp ; mov rbp, rsp ; ...`.
      Exit: `pop rbp ; ret`.

Pass criteria: smoke 7/7, unified_broker 49/49 hold; the canonical
multi-statement arithmetic reproducer (from ME-4 emergency handoff)
runs byte-identical `--run` vs `--interp`; per-blob size shrinks
measurably from current ad-hoc emission.

---

## Watermark

**Carved sess 2026-05-10 (Claude latest), Lon-directed.**  Architecture
based on close reading of SPITBOL x64 (`int.h`/`int.asm`/`sbl.min`,
EVALP/EVALX/EVALS, pmhbs / FENCE / ARBNO / `$`/`.` saves), CSNOBOL4
(`v311.sil`/`snobol4.c`/`include/macros.h`, cstack / PDLPTR / EXPVAL),
`bb_boxes.s` 106/106 oracle, live `bb_flat.c` flat-glob discipline,
and the existing ME-1/ME-2/ME-3 locked decisions.

**Design refinements through Lon Q&A in this session:**
1. r12 is the SM value-stack TOS pointer (FORTH-style single
   register), not `SM_State*`.  `SM_State` is reached via RIP-relative
   addressing when needed.
2. r13/r14/r15/rbx are NOT pre-claimed — they stay free.
3. The pattern engine uses heap-allocated DATA-block trees, not a
   pattern-history stack.  SCRIP has two stacks (SM value stack +
   native rsp) rather than CSNOBOL4's two-plus or SPITBOL's one-
   serving-three-roles.
4. SM_CALL_EXPRESSION distinguishes BB-land entry (saves `caller_r10`
   in SmCallFrame) from SM-blob-land entry (no r10 to save).  The
   emitter knows at emit time which case applies.
5. `*P` and `*(expr)` both reuse shared CODE with fresh DATA per
   entry — CODE is reusable; DATA is per-invocation; re-entry safety
   is guaranteed by the fresh-DATA discipline.

No code lands under ME-4-pre.  ME-4-post is gated on Lon's sign-off
line below.

**Lon sign-off:** [x] Lon Jones Cherryholmes, sess 2026-05-10 — "I think your register layout has a chance. So sign off."
