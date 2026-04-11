# ARCH-SILLY.md — Silly SNOBOL4

Ground-up faithful C rewrite of v311.sil (CSNOBOL4 2.3.3, Phil Budne).
Lives in `one4all/src/silly/`. Self-contained — no dependencies outside that folder
except system headers.

## Source oracles

```
/home/claude/work/snobol4-2.3.3/v311.sil      # SIL spec (12,293 lines)
/home/claude/work/snobol4-2.3.3/snobol4.c     # generated C ground truth (14,293 lines, 383 fns)
/home/claude/work/spitbol-docs-master/         # SPITBOL docs
```

## Platform model

**32-bit on 64-bit platform.** Arena model. No Boehm GC.
- `int_t = int32_t` (SIL integer / address field)
- `real_t = float` (SIL real — 32-bit, matching original)
- One 128 MB `mmap` slab. All DESCR A-fields = 32-bit arena offsets.
- `A2P(off)` = `(void*)(arena_base + (off))` — pointer from offset
- `P2A(ptr)` = `(int32_t)((char*)(ptr) - arena_base)` — offset from pointer
- GC: manual mark-compact matching v311.sil GC/GCM/SPLIT exactly

## Control flow rules

- Zero gotos anywhere. Zero computed BRANCHes.
- `if`/`while`/`for`/`switch` only.
- SIL RCALL → C function call. SIL RRTURN → `return`.
- Multiple SIL exits: `sno_rc_t` enum return or out-params.
- Pattern backtracking: C call stack + `setjmp`/`longjmp` in `sil_scan.c`.

## BLOCKS section

v311.sil lines 7038–10208 — NOT IMPLEMENTED.
BLOCKS is a conditionally-compiled optional feature (.IF BLOCKS / .FI).
Skip entirely in all forward and backward sweep passes.

## Three-way diff method

For every SIL instruction, three columns simultaneously:
1. `v311.sil` — the spec (note: SIL branch convention arg3=FALSE, arg4=TRUE — reversed)
2. `snobol4.c` — generated C (GROUND TRUTH — resolves all branch ambiguity)
3. `src/silly/sil_*.c` — our translation

`snobol4.c` cuts through all SIL ambiguity. Use it as primary reference for logic,
v311.sil for structure and labels.

## Naming conventions

| Origin | Convention | Example |
|--------|-----------|---------|
| SIL label → C function | `NAME_fn` | `APPLY_fn`, `FINDEX_fn` |
| SIL DESCR global → C typedef | verbatim + `_t` | `DESCR_t`, `SPEC_t`, `PATND_t` |
| SIL named global → C global | verbatim UPPERCASE | `XPTR`, `OCICL`, `TRIMCL` |
| SIL EQU constant → C `#define` | verbatim UPPERCASE | `OBSIZ`, `CARDSZ`, `FBLKSZ` |
| SIL flag → C `#define` | verbatim UPPERCASE | `FNC`, `TTL`, `MARK`, `PTR`, `FRZN` |
| SIL data type code → C `#define` | verbatim UPPERCASE | `S_TYPE=1`, `I_TYPE=6`, `DATSTA=100` |
| New C helper struct | `Mixed_case` | `Interp_state`, `Scan_ctx`, `Name_entry` |
| New C helper function | `snake_case` | `arena_init()`, `hash_spec()`, `pat_alloc()` |
| Procedure return typedef | `RESULT_t` | always |

## Oracle exception

CSNOBOL4 is the execution oracle for Silly (not SPITBOL).
Silly is a C rewrite of CSNOBOL4's SIL source — CSNOBOL4 IS the reference by construction.
CSNOBOL4 lacks FENCE — Silly inherits that gap.
