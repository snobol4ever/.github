# ARCH-x64.md — x64 Backend Deep Reference
Sprint plans, technique details. Operational → BACKEND-X64.md + SESSION-*-x64.md.
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

**No longer gates on M-BOOTSTRAP.** `emit_byrd_asm.c` knows every box's structure at
compile time and emits relocation tables as NASM data sections directly.
See milestone chain M-T2-RUNTIME → M-T2-FULL in PLAN.md.

### Milestone chain (implement in order)

| ID | Deliverable |
|----|-------------|
| M-T2-RUNTIME | `t2_alloc/free/mprotect` runtime functions; unit test |
| M-T2-RELOC   | `t2_relocate(text,len,delta,table,n)` patches jumps+DATA refs; unit test |
| M-T2-EMIT-TABLE | emitter writes per-box relocation tables as NASM data |
| M-T2-EMIT-SPLIT | emitter splits TEXT+DATA sections; `r12` = DATA-block ptr; all locals `[r12+offset]` |
| M-T2-INVOKE  | emitter generates T2 call-sites (`t2_alloc`+`memcpy`+`relocate`+`jmp`); γ/ω emit `t2_free` |
| M-T2-RECUR   | recursive functions correct; stack-frame bridge removed |
| M-T2-CORPUS  | 106/106 corpus — 9 known failures fixed by construction |
| M-T2-JVM     | JVM backend T2-correct (heap allocation already natural) |
| M-T2-NET     | NET backend T2-correct (CLR heap) |
| M-T2-FULL    | all three backends clean; `v-post-t2` tag; MONITOR resumes |


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
- SPITBOL participates in `run_monitor.sh` hello test alongside ASM+JVM+NET
- Open PR to `spitbol/x64` referencing upstream issue #35

**Fires:** M-X64-FULL.
