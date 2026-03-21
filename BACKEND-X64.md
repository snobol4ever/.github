# BACKEND-X64.md — x64 Assembly Backend (L3)

x64 ASM backend for snobol4x.
Current: near-term stack-frame bridge (M-ASM-RECUR).
Target: Technique 2 (mmap+memcpy+relocate), post-M-BOOTSTRAP.

*Session state → TINY.md. C backend → BACKEND-C.md. Architecture → ARCH.md §Technique 2.*

---

## The Core Insight — CODE shared, DATA per-invocation

Byrd boxes are naturally reentrant. The CODE (α/β/γ/ω goto sequence) never changes.
Only the DATA (locals: cursor, captures, params) differs between simultaneous invocations.

```
┌──────────────────────────────┐  ┌──────────────────────────────┐
│  CODE (RX, shared)           │  │  CODE (RX, shared)           │
│  P_ROMAN_α:                  │  │  P_ROMAN_α:        ← same    │
│    mov rax, [r12+OFFSET_N]   │  │    mov rax, [r12+OFFSET_N]   │
│    ...                       │  │    ...                       │
├──────────────────────────────┤  ├──────────────────────────────┤
│  DATA₁ (RW, invocation 1)   │  │  DATA₂ (RW, invocation 2)   │
│  r12 → N='12', T='', cur=0  │  │  r12 → N='1',  T='', cur=0  │
└──────────────────────────────┘  └──────────────────────────────┘
     ROMAN('12') call                  ROMAN('1') recursive call
```

Same instruction `mov rax, [r12+OFFSET_N]` reads different data in each invocation.
No save/restore needed. No stack. The mechanism IS the architecture:
- α allocates a DATA copy  → that IS the save
- γ/ω discards the copy   → that IS the restore
- Byrd boxes running forward and backward ARE save and restore

**Lon's note:** This is stackless by nature. Each SNO BLOCK is a Byrd-box sequence.
It runs correctly if you give it ONE REGISTER pointing to its locals. Two simultaneous
invocations = two DATA blocks, one CODE block. EVAL/CODE build these sequences at
runtime. The initial compile builds them statically. All run at full speed.

---

## Status

| Phase | What | Gate |
|-------|------|------|
| **Now** | Near-term bridge: per-invocation C stack frames | M-ASM-RECUR |
| **Next** | roman.sno + wordcount.sno PASS | M-ASM-SAMPLES |
| **Future** | Technique 2: mmap+memcpy+relocate | M-BOOTSTRAP |

---

## M-ASM-RECUR — Near-Term Bridge (implement now)

**Problem:** current ASM backend has ONE `rbp` frame for the entire program. All
`[rbp-8/16/32/48]` temporaries are shared globals. Recursive calls corrupt them.

**Fix:** Each user-defined function's α port establishes its own stack frame.
Each invocation gets private `[rbp-8/16/32/48]` slots. Hardware stack acts as
a cheap per-invocation DATA allocator. Same isolation as Technique 2, simpler.

```c
/* emit_asm_named_def(), is_fn branch, α label: */
asmL(np->alpha_lbl);
A("    push    rbp\n");
A("    mov     rbp, rsp\n");
A("    sub     rsp, 56\n");
/* ... load args, jmp body ... */

/* γ label: */
asmL(gamma_lbl);
A("    add     rsp, 56\n");
A("    pop     rbp\n");
A("    jmp     [%s]\n", np->ret_gamma);

/* ω label: */
asmL(omega_lbl);
A("    add     rsp, 56\n");
A("    pop     rbp\n");
A("    jmp     [%s]\n", np->ret_omega);
```

Call sites: **no change** — stack push/pop for param save/restore already correct (session197).

**Optimization note (Lon):** Do NOT skip to Technique 2 now. Optimization hurts when done
too early. Debugging static generated `.s` is hard enough. The stack bridge is correct and
fully inspectable. Prove correctness first, then optimize post-M-BOOTSTRAP.

**Acceptance test:** `roman.sno` runs correctly (recursive Roman numeral conversion).
roman.sno exercises self-recursion; max depth ~2 for '12'. Should not overflow.

**Milestone trigger:** M-ASM-RECUR fires when roman.sno produces correct output AND
26/26 ASM crosscheck + 106/106 C crosscheck both hold.

---

## Technique 2 — mmap + memcpy + relocate (post-M-BOOTSTRAP)

When `*X` fires or a function is called:
1. `memcpy(new_text, box_X.text_start, len)` — copy CODE section
2. `memcpy(new_data, box_X.data_start, len)` — copy DATA section (locals)
3. `relocate(new_text, delta)` — patch relative jumps + absolute DATA refs
   - Relative refs: add `delta = new_addr - orig_addr`
   - Absolute DATA refs: patch to point at `new_data`
4. Load `r12 = new_data`
5. Jump to `new_text[α]`

TEXT: PROTECTED (RX). `mprotect→RWX` during copy+relocate, back to RX after.
DATA: UNPROTECTED (RW). One copy per live invocation.
Reclamation: LIFO discipline — discard `new_data` on γ/ω return. No GC needed.
~20 lines of runtime. No heap. No explicit save/restore. No stack.

**Gates on:** M-BOOTSTRAP (need self-hosting sno2c to emit relocation tables).


---

## M-X64-FULL — SPITBOL LOAD/UNLOAD as Second Oracle (Sprint Plan)

**Goal:** Make `snobol4ever/x64` SPITBOL a fully working LOAD/UNLOAD host so it can:
1. Load `monitor_ipc.so` and participate in the 5-way monitor as second oracle
2. Pass the LOAD/UNLOAD test suite derived from `snobol4dotnet/TestSnobol4/Function/FunctionControl/`

**Test oracle:** `snobol4dotnet` `LoadSpecTests.cs` + `LoadTests.cs` + `LoadXnTests.cs` —
these cover prototype parsing, marshal (INTEGER/REAL/STRING), UNLOAD lifecycle,
double-unload safety, reload-after-unload, SNOLIB search, errors 139/140/141,
xn1st/xnsave/xncbp callbacks, and XNBLK object lifecycle. All cases must pass on x64 SPITBOL.

### Sprint S1 — syslinux.c compiles clean; `make bootsbl` succeeds

**Problem:** `syslinux.c` was written for x32 MINIMAL interface. Five categories of errors:
1. `xnhand`/`xnpfn` missing from `struct ef` → **fixed in B-230**: use `xndta[0]`/`xndta[1]`
2. `MINIMAL_ALOST`, `MINIMAL_ALOCS`, `MINIMAL_ALLOC` — MINIMAL opcode macros undefined in x64 build
3. `TYPET`, `MINFRAME`, `ARGPUSHSIZE` — x32 symbols not present in x64 port.h
4. `mword` declared as `int` in some paths, used as pointer-sized `long` — size mismatch
5. `MP_OFF` macro called with wrong arity in `sysex.c`

**Fix strategy:** Audit `make bootsbl 2>&1 | grep error:` exhaustively. For MINIMAL opcodes
that allocate GC memory (`MINIMAL_ALOST`), replace with direct `malloc`/`GC_malloc` calls —
x64 SPITBOL already uses Boehm GC. For missing symbols, define stubs or use the x64 equivalents.

**Fires:** M-X64-S1 — `make bootsbl` exits 0.

### Sprint S2 — LOAD end-to-end; spl_add(3,4) = 7

**Deliverable:** Minimal `SpitbolCLib` shared library (`libspl.so`) with:
```c
lret_t spl_add(LA_ALIST)   // INTEGER,INTEGER → INTEGER  returns a+b
lret_t spl_strlen(LA_ALIST) // STRING → INTEGER  returns string length
lret_t spl_scale(LA_ALIST)  // REAL,REAL → REAL  returns a*b
lret_t spl_negate(LA_ALIST) // REAL → REAL  returns -a
```
Matches the fixture used in `snobol4dotnet/CustomFunction/SpitbolCLib/`.

Test script:
```snobol4
        LOAD('spl_add(INTEGER,INTEGER)INTEGER', './libspl.so')   :F(FAIL)
        r = spl_add(3, 4)
        OUTPUT = EQ(r, 7) 'PASS' 'FAIL'
END
```

**Fires:** M-X64-S2.

### Sprint S3 — UNLOAD lifecycle

Tests (from `LoadSpecTests`):
- `UNLOAD('spl_add')` → `:S` branch taken
- Double `UNLOAD` → safe (no crash)
- `UNLOAD` then re-`LOAD` → works correctly
- `UNLOAD` then call → `:F` branch (function gone)

**Fires:** M-X64-S3.

### Sprint S4 — SNOLIB, error conditions, monitor_ipc.so

- SNOLIB env var search: `LOAD('spl_add(INTEGER,INTEGER)INTEGER', 'libspl')` with `SNOLIB=/path/to/dir`
- Error 139 (missing `(`), 140 (empty fname), 141 (missing `)`) fire correctly
- `LOAD('MON_OPEN(STRING)STRING', './monitor_ipc.so')` works end-to-end in SPITBOL
- `MON_OPEN` / `MON_SEND` / `MON_CLOSE` callable from SPITBOL SNOBOL4 program

**Fires:** M-X64-S4 → immediately enables M-MONITOR-IPC-5WAY SPITBOL participant.

### Sprint S5 — M-X64-FULL: test suite + PR

- Run SPITBOL's own test suite: all tests pass
- SPITBOL participates in `run_monitor.sh` hello test alongside CSNOBOL4+ASM+JVM+NET
- Open PR to `spitbol/x64` referencing upstream issue #35

**Fires:** M-X64-FULL.
