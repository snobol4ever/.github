# SESSION-silly-snobol4.md — Silly SNOBOL4 Faithful C Rewrite

**Repo:** one4all (subfolder `silly-snobol4/`) · **Track:** standalone rewrite
**Trigger:** any message containing "Silly SNOBOL4" starts this session
**Milestone doc:** `MILESTONE-SILLY-SNOBOL4.md`

---

## ⛔ §INFO — session invariants (append-only, read every session)

### What this is (2026-04-06)

A ground-up faithful C rewrite of `v311.sil` (CSNOBOL4 2.3.3, Phil Budne).
Lives in `one4all/silly-snobol4/` — self-contained, references nothing outside
that folder except system headers.

**Source oracle:** `/home/claude/work/snobol4-2.3.3/v311.sil` (12,293 lines)
**Generated C reference:** `/home/claude/work/snobol4-2.3.3/snobol4.c` (14,293 lines, 383 fns)
**SPITBOL docs:** `/home/claude/work/spitbol-docs-master/`

### Naming conventions (2026-04-06)

| Thing | Convention | Example |
|-------|-----------|---------|
| SIL label → C function | `NAME_fn` | `APPLY_fn`, `GENVAR_fn`, `FINDEX_fn` |
| SIL DESCR global → C typedef | `NAME_t` | `DESCR_t`, `SPEC_t`, `PATND_t` |
| SIL named global → C global | verbatim | `XPTR`, `OCICL`, `TRIMCL`, `MSG1` |
| SIL EQU constant → C #define | verbatim | `OBSIZ`, `CARDSZ`, `ATTRIB`, `LNKFLD` |
| SIL flag → C #define | verbatim | `FNC`, `TTL`, `STTL`, `MARK`, `PTR`, `FRZN` |
| SIL data type code → C #define | verbatim | `S_TYPE=1`, `I_TYPE=6`, `DATSTA=100` |
| New C helper struct (no SIL origin) | CamelCase | `ScanCtx`, `NamFrame`, `InterpState` |
| New C helper function (no SIL origin) | snake_case | `arena_init()`, `hash_spec()`, `pat_alloc()` |
| SIL return result enum | CamelCase | `SilResult` (FAIL=0, OK=1) |
| New C table entry struct | CamelCase | `InvokeEntry`, `NamEntry` |

### Architecture (2026-04-06)

**32-bit on 64-bit platform.**
- `int_t  = int32_t`  (SIL integer / address field)
- `real_t = float`    (SIL real — 32-bit, matching original)
- Arena model: one 128 MB `mmap` slab. All DESCR A-fields hold 32-bit arena offsets.
- `A2P(off)` = `(void*)(arena_base + (off))` — raw pointer from offset
- `P2A(ptr)` = `(int32_t)((char*)(ptr) - arena_base)` — offset from pointer
- Boehm GC: NOT used. Arena is manual mark-compact matching v311.sil GC/GCM/SPLIT exactly.

**Control flow rules:**
- Zero gotos anywhere. Zero computed BRANCHes.
- `if`/`while`/`for`/`switch` only.
- SIL RCALL → C function call with typed params and return.
- SIL RRTURN → `return` (with value or `sno_rc_t` code).
- Multiple SIL exits: either `sno_rc_t` enum return or out-params.
- Pattern backtracking: C call stack + `setjmp`/`longjmp` in `sil_scan.c`.

**BLOCKS section:** v311.sil lines 7038–10208 — skipped entirely.

### Cherry-picks from one4all (2026-04-06)

These files from `one4all/src/runtime/snobol4/` contain well-tested logic
that can be adapted. Adapt, don't copy verbatim — the type system differs
(one4all uses Boehm GC + 64-bit; silly-snobol4 uses arena + 32-bit).

| one4all file | Useful for | Adaptation needed |
|---|---|---|
| `argval.c` | VARVAL_fn, INTVAL_fn, PATVAL_fn logic | remove GC_strdup, use arena; int32_t not int64_t |
| `nmd.c` | NAM_save/NAM_push/NAM_commit/NAM_discard design | remove GC_MALLOC, use arena; NamEntry_t → `nam_entry_t` |
| `invoke.c` | INVOKE_fn / APPLY_fn dispatch pattern | adapt to fn_entry_t table with arena ptrs |
| `sil_macros.h` | MOVD, SETAC, type-test macros | verify against our DESCR_t layout |
| `snobol4.c` | arithmetic, string ops, keyword logic | heavy adaptation — different DESCR layout |

### Build (2026-04-06)

```bash
cd /home/claude/one4all/silly-snobol4
gcc -Wall -Wextra -std=c99 -m32 -g -O0 -c sil_types.h   # M0 gate
gcc -Wall -Wextra -std=c99 -m32 -g -O0 -c sil_data.c    # M1 gate
# etc. — each milestone gates on its file compiling clean
```

Prereq for -m32: `apt-get install -y gcc-multilib`

### SIL source line ranges by section (2026-04-06)

| Section | Lines | Content |
|---------|-------|---------|
| §1 Linkage/Equates | 829–953 | EQU constants, type codes, flags |
| §2 Program Init | 954–1023 | BEGIN |
| §3 Compile/Interp | 1024–1087 | XLATRD..XLATSC |
| §4 Support | 1088–1218 | AUGATL CODSKP DTREP FINDEX |
| §5 Storage/GC | 1219–1553 | BLOCK GENVAR GC GCM SPLIT |
| §6 Compiler | 1554–2519 | BINOP CMPILE ELEMNT EXPR FORWRD NEWCRD TREPUB UNOP |
| §7 Interp Exec | 2520–2678 | BASE GOTG GOTL GOTO INIT INTERP INVOKE |
| §8 Arg Eval | 2679–2922 | ARGVAL EXPVAL EXPEVL EVAL INTVAL PATVAL VARVAL VARVUP VPXPTR XYARGS |
| §9 Arithmetic | 2923–3118 | ADD DIV EXPOP MPY SUB EQ GE GT LE LT NE REMDR INTGER MNS PLS |
| §10 Pattern-valued | 3119–3322 | ANY BREAKX BREAK NOTANY SPAN LEN POS RPOS RTAB TAB ARBNO ATOP NAM DOL OR |
| §11 Pattern Match | 3323–4239 | SCAN SJSR SCNR + 27 sub-procedures |
| §12 Defined Fns | 4240–4470 | DEFINE DEFFNC |
| §13 External Fns | 4471–4643 | LOAD UNLOAD LNKFNC |
| §14 Arrays/Tables | 4644–5267 | ARRAY ASSOC DATDEF ITEM DEFDAT FIELD RSORT SSORT |
| §15 I/O | 5268–5465 | READ PRINT BKSPCE ENDFIL REWIND SET DETACH PUTIN PUTOUT |
| §16 Tracing | 5466–5827 | TRACE STOPTR FENTR FENTR2 KEYTR TRPHND VALTR FNEXT2 |
| §17 Other Ops | 5828–6101 | ASGN CONCAT IND KEYWRD LIT NAME NMD STR |
| §18 Predicates | 6102–6321 | DIFFER FUNCTN IDENT LABEL LEQ-LNE NEG QUES CHAR LPAD RPAD |
| §19 Other Fns | 6322–7037 | APPLY ARG LOCAL FIELDS CLEAR CMA COLECT COPY CNVRT DATE DT DMP DUMP DUPL OPSYN RPLACE REVERS SIZE TIME TRIM VDIFFR |
| §20 BLOCKS | 7038–10208 | **SKIP** |
| §21 Common Code | 10209–10241 | RTN1 FAIL RETNUL RTN2 RTN3 etc. |
| §22 Termination | 10242–10336 | END FTLEND SYSCUT |
| §23 Errors | 10337–10480 | all error handlers |
| §24 Data | 10481–12293 | all static data |

---

## §NOW

| Sprint | HEAD | Next milestone |
|--------|------|----------------|
| SS-1 | (not started) | M0: sil_types.h — EQUs, DESCR_t, SPEC_t, flags, type codes |
