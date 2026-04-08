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
| `arena.c` | 572 | §5 (GC/BLOCK/GENVAR) | ⬜ |
| `strings.c` | 230 | §5 helpers | ⬜ |
| `symtab.c` | 221 | §4 FINDEX/GENVUP | ⬜ |
| `data.c` | 558 | §24 init | ⬜ |
| `argval.c` | 412 | §8 | ⬜ |
| `arith.c` | 311 | §9 | ⬜ |
| `patval.c` | 435 | §10 | ⬜ |
| `scan.c` | 1175 | §11 | ⬜ |
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

**Last file audited:** —
**Last line audited:** —
**Session:** —

---

## Bug log

| # | File | Line | Function | Description |
|---|------|------|----------|-------------|
| (bugs from this milestone go here) |
