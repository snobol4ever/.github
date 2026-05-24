# TRACK-PURE-PROJECTION.md — templates → pure CONCAT/IF/FOR

Audit baseline: one4all `3785ffd1` (2026-05-25). Scope: `src/emitter/{SM,BB}_templates/*.cpp`.

## Principle (Lon)
A template is a pure function `state → one string`. Body = ONE expression of three constructs:
- **CONCAT**  `X_lit + Global + Y_lit + …`
- **IF(cond, c1, c2)**  conditional emission; `cond` = global SCALAR
- **FOR(i, lo, hi, …)**  iterate a global COLLECTION

Switches off scalars, iterates collections. Knows only "what switches my output" + "what lists I
iterate." Templates are CALLED by drivers; never drive. No side effects.

## FORBIDDEN in a template body (the exterminate list)
`emit_flat_ir` · `emit_label_define_bb` · `emit_jmp_label` · `emit_label_initf` · `alloca` of
labels · recursion · `pBB->c[i]` deref into sub-templates · `prog->instrs[]` scan ·
returning `std::string()` after doing work via side effects.

================================================================================
## PP-A — DE-DRIVE (severe; FIRST)
================================================================================

### Self-driving x86 templates (recurse + mint labels + patch, return empty string)
- [x] **bb_pat_cat.cpp** ✅ x86 driving lifted to `flat_drive_cat` in emit_bb.c; `emit_flat_ir`
      BB_PAT_CAT case calls it directly; audit reroutes x86 CAT through `emit_flat_ir`. Template
      x86 arm deleted; only pure-CONCAT JVM/NET/JS arms remain. GATE-PK 442/0/612, audit GREEN,
      prolog 124/0/0.                                                                            (PP-A1)
- [x] **bb_pat_alt.cpp** ✅ x86 driving → `flat_drive_alt` (emit_bb.c). Shared predicate
      `bb_kind_is_driver_owned()` added; audit routes driver-owned x86 kinds through `emit_flat_ir`.
      GATE-PK 442/0/612.                                                                        (PP-A2)
- [x] **bb_pat_fence.cpp** ✅ with-children traversal → `flat_drive_fence` (emit_bb.c); zero-child
      delegates back to template via flat_fill_*. Template keeps pure macro/zero-child emission.
      GATE-PK 442/0/612.                                                                        (PP-A3)

### Flat-list self-scans in SM templates
- [x] **sm_returns.cpp:155** ✅ `sm_nreturn` backward scan lifted to SM driver loop (emit_sm.c);
      driver computes `g_emit.enclosing_fname` per pc; template reads the scalar. Also dropped the
      side-effecting `emit_mode_set` in the template + inlined the `.c_str()`. GATE-PK 442/0/612,
      smoke parity 184 / run 186/75.                                                            (PP-A4)
- [x] **sm_defines.cpp:57** ✅ `prog->instrs[pc-1]` neighbor read → driver stamps
      `g_emit.prev_instr_name`; template reads scalar.                                          (PP-A5)
- [x] **sm_exec_bb.cpp:14** ✅ `pc = pSM - prog->instrs` pointer-arith → reads `_.i` (driver
      already sets it). SM audit primes `enclosing_fname`/`prev_instr_name` to avoid stale
      contamination. GATE-PK 442/0/612, audit GREEN, prolog 124/0/0.                            (PP-A5)

### Operand-child derefs (RULING NEEDED — legal FOR/index, or flatten in driver?)
- [x] **bb_pl_arith.cpp:17,33** — RULING: pBB->c[0]/c[1] are sub-records of the DATA struct (Snocone DATA() model). Legal. No-op.  (PP-A6)
- [x] **bb_pl_unify.cpp:30,45** — same ruling.                                                    (PP-A6)
- [x] **bb_pl_builtin.cpp:40,41,90,91** — same ruling.                                            (PP-A6)

### Driver carrier (PP-A0)
- [x] PP-A0 ruling applied. No collection needed — child node records passed through pBB directly.

================================================================================
## PP-B — R4 conversion-locals (`const char *x = x_s.c_str()`) — 33
================================================================================
### SM (7, stub arms — low priority)
- [x] sm_calls.cpp:25,41,61  sm_jumps.cpp:30  sm_returns.cpp:47,102,164
### BB (26, ACTIVE x86 arms)
- [x] bb_arbno:48,77  bb_lit:84  bb_pat_alt:39  bb_pat_cat:66  bb_pat_len:45  bb_pat_arb:57
- [x] bb_pat_pos:60  bb_pat_tab:69
- [x] bb_pat_any:40,41,48,76,77  bb_pat_break:39,40,47,75  bb_pat_notany:39,40,47,75
- [x] bb_pat_span:39,40,47,75
PP-B COMPLETE ✅ `41a04350` — 34 c_str() locals eliminated across 16 files. GATE-PK 442/0/612 NEW=0 GONE=0.

================================================================================
## PP-C — R3 string-globals → std::string
================================================================================
- [ ] `Σ` = `const char *Σ` + `int Σlen` (emit_globals.h:70). → `std::string` for concat; KEEP
      ABI for `&Σ`/`Σlen` baked via `TEMPLATE_ADDR_SIGMA`. RULING PENDING: Σ is never C++-concatenated
      in templates — only address-baked x86 ABI (TEMPLATE_ADDR_SIGMA/SIGLEN). Templates use Σ only
      as an asm-string label ("Σlen", "Σ"). PP-C may be a no-op; awaiting Lon ruling.

================================================================================
## PP-D — R1/R2 scope tighten + final audit
================================================================================
- [x] SM templates read only SM_t-fields + sanctioned globals. ✅ Verified: `_.prog` dead local
      removed from sm_defines.cpp. No BB-lane fields accessed.
- [x] BB templates read only BB_t-fields + sanctioned globals. ✅ Zero SM-lane field reads.
- [x] Cross-lane audit: BB templates → no SM fn-map/sequence fields. SM templates → no BB label fields. CLEAN.
- [x] `lbl_succ/fail/back(+_p)` and SM `_.i/_.n/_.out` confirmed global-class (emission scratch). LEGAL.
PP-D COMPLETE ✅ GATE-PK 442/0/612 NEW=0 GONE=0, AUDIT GREEN, PROLOG 124/0/0.
