# SESSION-silly-snobol4.md — Silly SNOBOL4 Faithful C Rewrite

**Repo:** one4all (subfolder `silly-snobol4/`) · **Track:** standalone rewrite
**Trigger:** any message containing "Silly SNOBOL4" starts this session
**Milestone doc:** `MILESTONE-SILLY-SNOBOL4.md`

---

## ⛔ §INFO — session invariants (append-only, read every session)

### What this is (2026-04-06)

⚠️ **ORACLE EXCEPTION — this session only:** CSNOBOL4 (instrumented executable) IS the
sync-step oracle for Silly SNOBOL4, by construction. All other sessions use SPITBOL x64
(`/home/claude/x64/bin/sbl`) as the sole execution oracle (D-005). This session is the
one legitimate exception: Silly is a C rewrite of CSNOBOL4's own SIL source, so CSNOBOL4
is the reference. CSNOBOL4 still lacks FENCE — Silly inherits that gap until M-CSNOBOL4-FENCE.

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
| New C helper struct (no SIL origin) | Mixed_case | `Interp_state`, `Scan_ctx`, `Name_entry`, `Invoke_entry` |
| New C helper function (no SIL origin) | snake_case | `arena_init()`, `hash_spec()`, `pat_alloc()` |
| SIL return result enum | CamelCase | `SilResult` (FAIL=0, OK=1) |
| New C error enum (no SIL origin) | UPPER_CASE | `SNOBOL4_error` |

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
| `nmd.c` | NAM_save/NAM_push/NAM_commit/NAM_discard design | remove GC_MALLOC, use arena; Name_entry → `nam_entry_t` |
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

⚠️ BWD session: update only the BWD row. FWD session: update only the FWD row. Never touch the other.

| Sprint | HEAD | Next milestone |
|--------|------|----------------|
| SS-39 BWD | one4all `09107beb` | **M-SS-BLOCK-BACKWARD** — watermark 10600 (EXN2CL clean). Next: DIGSVL (line 10596). |
| SS-47 FWD | one4all `43ac7934` | **M-SS-BLOCK-FORWARD** — watermark 2606 (GOTLC done). Next: NAM (line 3223). |

### MONITOR func-hook proposal (2026-04-08g)

**The idea:** Retool MONITOR sync-step protocol for C function enter/exit hooks on both
CSNOBOL4 (compiled C via snobol4.c) and Silly (our C rewrite). Instead of SNOBOL4
TRACE() hooks, instrument at the C level:
- CSNOBOL4: wrap each function in `snobol4.c` with `mon_enter(name)` / `mon_exit(name, result)` calls
- Silly: same wrappers on each `*_fn()` function
- Sync-step barrier: both write to named FIFO, block on ACK
- Controller: read one event from each, compare, send G or S
- First diverging function name/result = exact bug location

**Why it would work brilliantly:**
- Both are C — no SNOBOL4 LOAD() plumbing needed, just `#include "mon_hooks.h"`
- snobol4.c has 383 functions, our silly has ~60 — manageable
- AC_GOTO table transitions show up as STREAM_fn calls — would catch the IBLKTB loop instantly
- Sync-step means first divergence stops both — no bisecting, no guessing
- CSNOBOL4 is the oracle by construction — it IS the reference for Silly

**Readiness assessment:**
- CSNOBOL4 available and builds ✅ (in /home/claude/work/snobol4-2.3.3/)
- Silly builds clean ✅
- MONITOR sync-step protocol fully designed in MONITOR.md ✅ (two FIFOs per participant)
- The adaptation from SNOBOL4 TRACE() hooks to C function hooks is straightforward
- **Gap:** The sync-step implementation (monitor_ipc_sync.c + monitor_sync.py) exists in
  design doc but may not be built yet — check test/monitor/ before starting
- **Gap:** snobol4.c has 383 functions — a code-gen script to wrap them all is needed,
  not hand-editing
- **Scope:** This is a 1-session infrastructure build + 1-session first-run payoff

**Recommendation:** YES, do it — but in a dedicated M-SS-MONITOR sprint:
1. Check test/monitor/ for existing sync-step code
2. Write mon_hooks.h (FIFO open, atomic write, ACK read — ~50 lines)
3. Write wrap_snobol4.py: parse snobol4.c function signatures → emit wrapped version
4. Hand-annotate the ~60 Silly functions (manageable) OR write a similar wrapper script
5. Write monitor_sync.py controller (2-participant version — simpler than 5-way)
6. Run on hello.sno → first diverging function = bug name
Then fix, re-run, next divergence, repeat. Each iteration is near-instant.

## ⛔ §INFO additions (2026-04-06)

### Build command — NO -m32
```bash
cd /home/claude/one4all
gcc -Wall -Wextra -std=c99 -g -O0 src/silly/sil_*.c -lm -o /tmp/silly-snobol4 -I src/silly
```
Do NOT use `-m32`. The arena uses `int32_t` offsets explicitly; 64-bit build is correct and runs natively.

### Platform layer (SS-19)
`src/silly/sil_platform.c` is written and linked. It provides:
- 30 scan tables + `STREAM_fn`/`clertb_fn`/`plugtb_fn` with registry dispatch
- All 34 operator-fn DESCRs (ADDFN…STRFN)
- All XCALLs, STREAD_fn, STPRNT_fn, helper stubs
- `CONTIN`/`STOPSH` as `DESCR_t` globals with `.a.i = AC_CONTIN/AC_STOPSH`
- `init_syntab()` fills operator-fn put values after arena_init

### Milestone sequence (2026-04-06)
```
M-SS-DIFF   → section-by-section diff pass: each of 22 TUs vs v311.sil oracle
              Goal: find wrong translations before we run anything.
              Method: for each §, read v311.sil SIL and compare to our C side-by-side.
              Output: a punch-list of corrections per file.

M-SS-HARNESS → two-way harness: Silly SNOBOL4 vs CSNOBOL4 (snobol4ever/harness)
               Run same corpus through both; diff outputs.
               Gate: binary exists, reads stdin, produces stdout, terminates.
               sil_data_init() must be correct enough to get through BEGIN.
```

### sil_data_init() status
Currently a partial stub — computed constants filled, stacks allocated, but the
2000+ DESCR globals from v311.sil §24 (function descriptors, keyword tables,
pattern primitives, OBLIST, etc.) are NOT populated from the SIL source.
The diff pass (M-SS-DIFF) will surface which globals are wrong/missing.
A generator script (parse §24, emit C) is the right approach for M-SS-HARNESS prep.

### Naming conventions — C translation rules (2026-04-06)
See full table in `GENERAL-RULES.md` under `## ⛔ NAMING CONVENTIONS`.
Summary:
- SIL label → `NAME_fn` (`FINDEX_fn`, `CODSKP_fn`)
- SIL global → verbatim UPPERCASE (`XPTR`, `FNCPL`, `NEXFCL`)
- SIL EQU/#define → verbatim UPPERCASE (`FBLKSZ`, `CNODSZ`, `DATSTA`)
- SIL type → verbatim + `_t` (`DESCR_t`, `SPEC_t`)
- New C struct/enum → `Xxxx_yyy` one-cap-first (`RESULT_t`, `Invoke_entry`, `Scan_ctx`)
- New C function/variable → `snake_case` (`arena_init`, `genvar_from_descr`, `locapt_fn`)
- **Never CamelCase. Never ALL_CAPS for new C types.**

### M-SS-DIFF punch-list (SS-19, 2026-04-06)
Fixed this session:
- `SIL_result` → `RESULT_t` everywhere (41 files)
- `CNODSZS` → `CNODSZ` (SIL verbatim)
- Added `#define FBLKSZ (10*DESCR)` to `sil_types.h`
- `FBKLSZ` typo (×2) → `FBLKSZ` in `sil_symtab.c` FINDEX_fn
- `BLOCK_fn(FBLKSZ, 0)` → `BLOCK_fn(FBLKSZ, B)` (FATBLK, oracle type=B)
- Dropped `FNCPL_off` shadow — use `D_A(FNCPL)` directly everywhere
- `GENVAR_fn_from_descr` → `genvar_from_descr` in `sil_main.c`
- Build confirmed clean (one pre-existing format-truncation warning only)

Still open:
- `EXDTSP` as `const char[]` → should be `SPEC_t` (§4 DTREP)
- Continue diff pass §6–§23

### §11 diff findings — PDL slot conventions (2026-04-07q)

Our `pdl_push3(d0, d1, d2)` stores at offsets `0 / DESCR / 2*DESCR` (0-based).
Oracle stores at `DESCR / 2*DESCR / 3*DESCR` (1-based, after `INCRA PDLPTR,3*DESCR`).
Mapping: our slot 0 = oracle slot DESCR (function code), our slot 1 = oracle slot 2*DESCR (cursor), our slot 2 = oracle slot 3*DESCR (lenfcl).
This is **internally consistent** throughout sil_scan.c. Do NOT change to 1-based.

### §11 diff findings — fullscan nval pattern (2026-04-07q)

Recurring pattern in FARB, BAL, STAR, DSAR:
- Oracle: `AEQLC FULLCL,0,,PROC1` means fullscan OFF → use nval=0; fullscan ON → use YCL.
- C: `if (AEQLC(FULLCL, 0)) { nval = 0; } else { nval = D_A(YCL); }`
- `AEQLC(x,0)` returns true when `x.a.i == 0` (i.e. OFF). The `,,PROC1` means fall-through when OFF — so OFF path sets nval=0. Always verify this pattern when reading oracle `AEQLC FULLCL,0`.

### M-SS-DIFF progress (2026-04-07q)

| § | TU | Status |
|---|----|--------|
| §1–§9 | sil_types/data/arith/argval/etc. | ✅ complete (prior sessions) |
| §10 | sil_patval.c | ✅ complete (2026-04-07o) |
| §11 | sil_scan.c | ✅ complete (2026-04-07q) |
| §12 | sil_define.c | ✅ complete (2026-04-07r) — 1 bug: block-fill off-by-one |
| §13 | sil_extern.c | ✅ complete (2026-04-07s) — 1 bug: LNKFNC entry addr slot 0 not 1 |
| §14 | sil_arrays.c | ✅ complete (2026-04-07s) — 2 bugs: ARRAY elem slot off-by-one; ITEM multi-dim Horner |
| §15 | sil_io.c | ✅ complete (2026-04-07t) — 3 bugs: READ opts lost; DETACH wrong arena base; PUTIN XCL not saved |
| §16 | sil_trace.c | ✅ complete (2026-04-07w) — 9 bugs |
| §17 | sil_asgn.c + sil_nmd.c + sil_scan.c | ✅ complete (2026-04-07x) — 8 bugs |
| §18 | sil_pred.c | ✅ complete (2026-04-07x) — 1 bug |
| §19 | sil_func.c | ✅ complete (2026-04-07y) — 1 bug |
| §4 | symtab.c | ✅ complete (2026-04-08a) — 2 bugs |
| §7 | interp.c | ✅ gaps noted (2026-04-08a) — 0 code fixes |
| §6 | cmpile.c | ✅ complete (2026-04-08b) — 4 bugs |
| §6 | expr.c + forwrd.c (CARDTB bug) | ✅ complete (SS-29 / 2026-04-07d) — 4 bugs |
| §8 | argval.c | ✅ complete (2026-04-08b) — 4 bugs total |
| §20–§23 | remaining TUs | ✅ complete (SS-30) — 1 bug: END_fn XITHND return path |

---

## ⛔ §INFO addition — M-SS-DIFF-RECHECK method (2026-04-07w)

### Three-way diff method

M-SS-DIFF-RECHECK is a **complete scan of all §1–§23** (not limited to any section range).
It is NOT a re-scan of §16–§19 only. Every TU gets reviewed.

**Method: three-way oracle + generated C + ours**

For each function, compare ALL THREE simultaneously:
1. `v311.sil` — SIL source oracle (confusing branch convention: arg3=FALSE, arg4=TRUE — reversed)
2. `snobol4.c` — generated C from CSNOBOL4's own SIL compiler — **THIS IS GROUND TRUTH**
   - Location: `/home/claude/work/snobol4-2.3.3/snobol4.c` (14,293 lines, 383 fns)
   - Already resolves all SIL branch ambiguity into plain C if/goto
   - Use `grep -A N "^FUNCNAME\b" snobol4.c` to pull each function
3. `src/silly/sil_*.c` — our translation

**Why three-way catches more bugs:**
- SIL branch convention trips up first-pass reading (arg3=false, arg4=true)
- Generated C cuts through all ambiguity — DCMP/DCMP in generated = deql() in ours
- Structural omissions (missing PUTDC, missing appends) visible by line-count comparison
- Off-by-one (> vs >=) visible by direct comparison

**Bug classes found in §16 recheck that first pass missed:**
- Structural omissions: TRAC3 link-back, fentr prefix, FNEXT1 return value
- Wrong register: valtr4 FRETCL ZPTR→XPTR, STOPTR YPTR path
- Inverted branch: valtr4 VEQLC(S) 
- Off-by-one: `>` vs `>=` on BUFLEN overflow guards (affects ALL trace functions)

### Future: in-process diff driver

The right approach is a driver that walks snobol4.c and sil_*.c in lockstep, function by function.
Options:
- **Static structural diff**: normalize both to (register-touched, branch-taken, global-written) sequences; diff the sequences
- **Runtime trace diff**: run same input through both, compare register state after each SIL op
- **Callback/step approach**: both interpreters step through same IR, fire callback on divergence

M-SS-HARNESS (two-way vs CSNOBOL4) catches runtime divergence but requires working inputs.
Static diff catches structural bugs before any code runs.

### M-SS-DIFF-RECHECK watermark (update each session)
- §16 sil_trace.c: ✅ 9 bugs fixed
- §17 sil_asgn.c + sil_nmd.c + sil_scan.c: ✅ 8 bugs fixed
- §18 sil_pred.c: ✅ 1 bug fixed
- §19 sil_func.c: ✅ 1 bug fixed (APPLY_fn INVOKE return path)
- §22+§23 sil_errors.c: ✅ 7 bugs fixed (FTLTST/FTLERR/FTERST, PROTER/SIZERR/UNDFFE, missing handlers)
- §20–§21 (sil_main.c common stubs): ⬜ next
- §1–§15 (sil_support, sil_arith, sil_interp, sil_cmpile, etc.): ⬜ pending

### M-SS-BLOCK method clarification (2026-04-08b, corrected 2026-04-09)

**One block at a time. Watermark = SIL line number of last completed block.**

⛔ **WHAT A LABELED BLOCK IS (critical — Claude got this wrong repeatedly):**
- A labeled block starts on a line that has a label in column 1.
- It continues up to but NOT INCLUDING the next line that has a label in column 1.
- `*_` is NOT the boundary. `*_` is inside a PROC — it marks a fall-through arm end within a block.
- Each label in SIL is its own block to verify independently.
- Example: GOTL PROC contains internal labels GOTLV, GOTLV1, GOTL1, GOTL2, GOTL3, GOTL4,
  GOTL5, GOTL5B, GOTL6, GOTLC — each is a SEPARATE block to verify one at a time.
- Do NOT bundle multiple labels into one verification pass. One label = one verification = one commit.

**Method:**
- Extract the single labeled block from v311.sil (from label line up to but not including next label line)
- Find the exact same block in snobol4.c (generated C)
- Find our equivalent in silly/*.c
- Compare **logic** instruction by instruction — not just presence
- Record any divergence as a bug; fix small ones immediately
- Advance watermark to that SIL line, push one commit per block

### M-SS-BLOCK watermark (FORWARD)
**Watermark: v311.sil line 2606** (GOTLC verified ✅ — per SESSIONS_ARCHIVE session SS-47 2026-04-09e).
**Next block: GOTO (v311.sil line 2607)**.
