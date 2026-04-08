# MILESTONE-SS-AUDIT — Silly SNOBOL4 Deep Variable/Logic Audit

**Goal:** Line-by-line audit of every C function in `src/silly/` against the three-way oracle
(v311.sil + snobol4.c + ours). Look for bugs of omission AND commission:
- Wrong variable used (XPTR vs YPTR, EXOPND vs EXPRND, etc.)
- Wrong operation (INCRA vs DECRA, > vs >=, + vs -)
- Wrong order (operand sequence, field offsets)
- Missing steps (omitted PUSH/POP, missing SETAC, skipped assignment)
- Extra steps (spurious resets, wrong path taken)
- Wrong field offset (T_CODE vs T_FATHER vs T_LSON vs T_RSIB)
- Wrong return path (FAIL vs OK, RTN1 vs RTN2 vs RTN3)

**Method:** Three-way diff per function. For each variable: check usage, operations, order.

**Watermark rule:** After each session, record the last file + line number audited.

---

## Audit order (by §, matching SIL structure)

| File | Lines | § | Status |
|------|-------|---|--------|
| `arena.c` | 572 | §5 (GC/BLOCK/GENVAR) | ✅ SS-29d (4 bugs) |
| `strings.c` | 230 | §5 helpers | ✅ SS-29d (2 bugs) |
| `symtab.c` | 221 | §4 FINDEX/GENVUP | ✅ SS-29d (4 bugs) |
| `data.c` | 558 | §24 init | ✅ SS-29d (0 bugs) |
| `argval.c` | 412 | §8 | ⬜ |
| `arith.c` | 311 | §9 | ✅ SS-30c (1 bug) |
| `patval.c` | 435 | §10 | ✅ SS-30d (3 bugs) |
| `scan.c` | 1175 | §11 | ✅ SS-30e (31 bugs) |
| `define.c` | 167 | §12 | ⬜ |
| `extern.c` | 164 | §13 | ⬜ |
| `arrays.c` | 360 | §14 | ⬜ |
| `io.c` | 234 | §15 | ⬜ |
| `trace.c` | 470 | §16 | ⬜ |
| `asgn.c` | 386 | §17 | ⬜ |
| `nmd.c` | 127 | §17 NMD | ⬜ |
| `pred.c` | 283 | §18 | ⬜ |
| `func.c` | 379 | §19 | ⬜ |
| `interp.c` | 275 | §7 | ⬜ |
| `cmpile.c` | 273 | §6 | ⬜ |
| `expr.c` | 469 | §6 | ✅ SS-29 (4 bugs) |
| `forwrd.c` | 355 | §6 | ✅ SS-29 (1 bug) |
| `trepub.c` | 112 | §6 | ⬜ |
| `errors.c` | 212 | §22-23 | ✅ SS-29b (2 bugs) |
| `main.c` | 268 | §2-3 | ✅ SS-29b (3 bugs) |
| `platform.c` | 1706 | tables | ⬜ (tables verified SS-28) |

---

## Watermark

**Last file audited:** `scan.c` (line 1175 — complete)
**Previous files complete:** `arena.c`, `strings.c`, `symtab.c`, `data.c`, `argval.c`, `arith.c`, `patval.c`
**Next file:** `define.c` (line 1)
**Session:** SS-30e (2026-04-07g)

---

## Bug log

| # | File | Line | Function | Description |
|---|------|------|----------|-------------|
| A4  | arena.c  | ~120 | GENVAR_fn | Missing CONVSW=0 at entry |
| A10 | arena.c  | ~280 | GC_fn GCBA | GCM pseudo-block forced f=PTR instead of D(ST1PTR) |
| A13 | arena.c  | ~370 | GC_fn GCLAP | off-by-one: off>=0 should be !=0 (title slot) |
| A14 | arena.c  | ~420 | GC_fn GCLAT | same off-by-one in permanent-block pass |
| S1  | strings.c | ~113 | SPCINT_fn | Always stripped whitespace; oracle only when SPITCL!=0 |
| S2  | strings.c | ~80  | TRIMSP_fn | Used ==' ' only; oracle uses isspace() |
| Y1  | symtab.c | ~25  | locapt_fn | Returned type-slot not pair-base; AUGATL wrote wrong offsets |
| Y2  | symtab.c | ~50  | locapv_fn | Returned value-slot not pair-base; FINDEX read wrong offset |
| Y3  | symtab.c | ~110 | AUGATL_fn | New-block type/value one DESCR too high |
| Y4  | symtab.c | ~155 | DTREP_fn  | Searched DTLIST instead of DTATL |
| AR-1 | arith.c | ~95 | ARITH_fn | SCL not saved/restored around XYARGS — XYARGS clobbers SCL (op selector) |
| PV-1 | patval.c | ~273 | ATOP_fn | INVOKE exit 2 (name returned) mapped to NRETURN; should be OK |
| PV-2 | patval.c | ~300 | nam_dol | Same INVOKE exit 2 mapping error (NRETURN→OK) |
| PV-3 | patval.c | ~210 | lprtnd | DEQL YCL,LNTHCL sense inverted: LEN should skip MOVA (ZCL=0); others should set ZCL=N |
| SC-1  | scan.c | SCAN_fn | ANCCL inverted in SCANVB: AEQLC(ANCCL,0)→FAIL; oracle D_A(ANCCL)!=0→FAIL |
| SC-2  | scan.c | SCAN_fn | REMSP else-branch dead: SIL LCOMP both exits→SCANV1; else picks wrong operand order |
| SC-3  | scan.c | SCNR_fn | ANCCL inverted — anchored/unanchored paths (SCFLCL vs SCONCL) swapped |
| SC-4  | scan.c | SCNR_fn | FULLCL min-length check inverted (runs when ON, should skip) |
| SC-5  | scan.c | SJSR_fn | ANCCL inverted in SJVVON (same as SC-1) |
| SC-6  | scan.c | SJSR_fn | INVOKE missing case 2→SJSR1 and case 3→NEMO |
| SC-7  | scan.c | do_SCIN2 | FULLCL length-check guard inverted |
| SC-8  | scan.c | do_SCIN1A | UNSCCL≠0 falls through to do_SCIN2(); should backtrack (SALT3) |
| SC-9  | scan.c | do_ABNS | FULLCL guard inverted in ANYC3 |
| SC-10 | scan.c | do_ABNS | +1 guard: TXSP.l < MAXLEN; oracle uses XSP.l + 0 <= MAXLEN |
| SC-11 | scan.c | do_LPRRT POS | n>TXSP.l→TSALT (oracle→TSALF); n<TXSP.l→TSALF (oracle→SALT) |
| SC-12 | scan.c | do_LPRRT RTAB | FULLCL guard inverted — residual check runs when ON |
| SC-13 | scan.c | do_ONAR | FULLCL inverted — ON should TSCOK immediately |
| SC-14 | scan.c | do_FARB | FULLCL inverted — FULLCL==0 should give nval=YCL |
| SC-15 | scan.c | do_FARB | PUTDC cursor: slot DESCR(1) vs oracle slot 2*DESCR(2) |
| SC-16 | scan.c | do_ATP | TRAPCL check inverted — runs trap when ≤0 |
| SC-17 | scan.c | do_ATP | Missing scan-state push/pop (12 regs + 4 specs) around TRPHND |
| SC-18 | scan.c | do_BAL_inner | FULLCL inverted — FULLCL==0 should give nval=YCL |
| SC-19 | scan.c | do_BAL/BALF | BAL and BALF share function but have different entry logic |
| SC-20 | scan.c | do_BAL_inner | PUTDC cursor: slot DESCR(1) vs oracle slot 2*DESCR(2) |
| SC-21 | scan.c | do_BAL_inner | BAL1 exit missing PDL underflow check (PDLPTR<PDLHED→INTR13) |
| SC-22 | scan.c | do_BRKXF | LENFCL inverted — LENFCL==0→SALT; oracle LENFCL!=0→SALT |
| SC-23 | scan.c | do_STAR STARP | FULLCL inverted — FULLCL==0 should give nval=YCL |
| SC-24 | scan.c | do_STAR STARP | Missing second FULLCL check to skip size check when ON |
| SC-25 | scan.c | do_STAR | SCIN case 3 (→RTNUL3) not handled |
| SC-26 | scan.c | do_STAR | SCIN success → GOTO_TSCOK; oracle → GOTO_SCOK |
| SC-27 | scan.c | do_DSAR | LENFCL inverted in non-P path |
| SC-28 | scan.c | do_DSAR DSARP | FULLCL inverted (same class) |
| SC-29 | scan.c | do_DSAR | SCIN1 case 1 (fail) vs case 2 (success) not distinguished |
| SC-30 | scan.c | do_FNCE/NME/ENME3 | PDL push slot 0; oracle slot DESCR(1) |
| SC-31 | scan.c | do_SUCF | XCL read from slot 0; oracle slot DESCR(1) |
