# REGISTER-LAYOUT.md — SCRIP mode-3 x86-64 register convention

> ⛔ **RETIREMENT NOTICE (r10 / BBREG_DATA is OUT).** The consolidated **per-BLOB DATA-block pointer in `r10`** described throughout this document is **RETIRED**. The live flat boxes address **RW box-locals at `[r12+off]`** (the ζ frame, established by the glob preamble `push r12; mov r12, rdi`) and **RO box-constants at `[rip+disp]`** (sealed adjacent, RIP-relative). There is no data-block register and no `lea r10,[rip+Δ]` preamble. Everything below that loads `r10`, addresses `[r10+N]`, or `push`/`pop`s `r10` for a DATA block is **superseded history retained for reference only** — see **R10-OUT** in `GOAL-SNOBOL4-BB.md` for the eliminating ladder. (This is in addition to the earlier SM-era supersession already noted: r12 is the ζ RW frame, NOT an SM value-stack TOS.)

⛔⛔ **SUPERSEDED FOR BB-NATIVE EMISSION (2026-05-31, Lon-ratified).** The
register roles below describe the **SMX-4-era SM-blob** convention (r12 =
SM value-stack TOS; r13/r14/r15 = free). SMX-4 deleted the SM engine, so
that value-stack and SM-state no longer exist. The **live** convention for
the ground-zero BB-native x86 emission is the GOAL-*-BB FACT RULE
"X86-64 REGISTER / SUBJECT-MODEL CONVENTION". ⛔ **CORRECTED 2026-06-30
(Claude Sonnet 4.6): this section originally pointed to `src/emitter/
bb_regs.h` as "the single source" — that file DOES NOT EXIST (confirmed:
no `bb_regs.h` anywhere under `src/`; `emit.h`'s own header comment says
"bb_regs.h + emit_defs.h were dead and dropped"). The roles in the table
below are independently re-verified CORRECT against the actual current
source, `src/templates/x86_asm.h`** (the `FR`/`FRQ` frame helpers,
`x86_r12_modrm`, and the bare `"r12"`/`"r13"`/`"r14"`/`"r15"` string
literals each template's `x86(...)` calls pass) — only the file pointer
was wrong, not the convention itself:

| Reg | Live role (verified against `src/templates/x86_asm.h`, NOT `bb_regs.h` — that file is gone) |
|-----|-----------------------------------------|
| **r13** | Σ — subject BASE ptr |
| **r14** | δ — CURSOR |
| **r15** | Δ — subject LENGTH/END (folds retired Ω/Σlen) |
| **r12** | ζ — BB-local RW FRAME base (`[r12+off]`); **NOT** a value stack |
| **r10** | per-BLOB DATA-block ptr (flat); broker current-node ptr (brokered) — fork TBD |
| **rbx** | DESCR BASE POINTER — dual-width: 8-byte DESCR (32-bit) / 16-byte DESCR (64-bit) (Lon 2026-05-31) |
| **rbp** | variable NAME/HASH-table base (RESERVED) — GET/SET are C calls for now; inlining is a future optimization (Lon 2026-05-31) |

The mode-3 SM detail below is retained as historical reference only.

⛔ **This is the locked register convention for mode-3 SM-blob emission
and for flat-BB glob emission.**  Every blob, every glob, every PLT
call signature in mode 3 obeys this.  Changes require an explicit goal
rung and Lon sign-off.

**Sources of truth referenced in this doc:**
- `archive/backend/bb_boxes.s` — proven 25-box library, 106/106 oracle. (Verified 2026-06-30: still present at this path.)
- `/home/claude/x64/int.h`, `int.asm`, `sbl.min` — SPITBOL x64
  MINIMAL register map and save/restore discipline.
- `/home/claude/csnobol4/v311.sil`, `snobol4.c`, `res.h`,
  `include/macros.h` — CSNOBOL4 cstack discipline and PDLPTR pattern
  history list.
- `src/runtime/x86/bb_flat.c` — **DOES NOT EXIST** (corrected 2026-06-30, Claude Sonnet 4.6: confirmed
  by `find`, neither `bb_flat.c` nor a `src/runtime/x86/` directory exist anywhere in the current tree).
  The live flat-glob register convention this doc locks (`"r12"`/`"r13"`/`"r14"`/`"r15"` literals, the
  `FR`/`FRQ` frame helpers) actually ships in `src/templates/x86_asm.h`, included per-template by the
  current `src/templates/*.cpp` family — not in any `src/runtime/x86/` file.
- `ARCH-x86.md` — defines the flat-BB ABI, the stackless-box discipline,
  and the intra-/extra-BLOB jump rules this doc operates against. **`ARCH-x86.md` is itself flagged
  stale on file-layout claims as of 2026-06-30 — see its own correction banner.**

---

## TL;DR — register assignments

| Reg | Class | Role | When loaded / saved |
|-----|-------|------|----------------------|
| **r12** | callee-saved | *(SM-era)* SM value stack TOS — **retired by SMX-4**; now ζ BB-local RW frame base (see bb_regs.h) | *(SM-era)* loaded at `sm_jit_run` entry; the SM engine no longer exists |
| **r10** | caller-saved | **Current BB DATA-block pointer** — `[r10+N]` addresses every box-local in the active BLOB | Loaded by each BLOB's α-preamble as `lea r10, [rip + Δ_data]` (static globs) or as the result of an `rt_alloc_blob_data()` call (variant globs and re-entries); constant inside a BLOB; saved in SmCallFrame when SM_CALL_EXPRESSION fires from inside BB land |
| **rbp** | callee-saved | DEFINE'd function frame pointer (when active) | `push rbp; mov rbp, rsp` at function α-entry; `pop rbp; ret` at exit |
| **r13, r14, r15** | callee-saved | *(SM-era: "free")* — **now the subject model: r13=Σ base, r14=δ cursor, r15=Δ length/end** (bb_regs.h / GOAL FACT RULE) | loaded at pattern/scan-graph entry; rbx remains free scratch |
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

## (superseded body deleted 2026-07-01)
Everything the banners above mark superseded — SM value stack, r10 DATA-block walking, `*P`/DEFER SM machinery, push/pop matrices, the SM-era rationale, EVAL/CODE re-entrancy, ME-4 checklist — deleted per Lon's prune directive; recover from git if ever needed. **Live convention = the corrected table at top; source of truth = `src/templates/x86_asm.h`.** The two oracle maps below are kept for MONITOR/gdb cross-debugging.

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

