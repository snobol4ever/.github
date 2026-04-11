# MISC-SPITBOL-LOAD.md — SPITBOL LOAD/UNLOAD as Second Oracle Sprint

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
