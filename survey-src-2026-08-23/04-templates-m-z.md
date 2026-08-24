# Survey 04 — src/templates/bb_[m-z]*.cpp (agent report, condensed verbatim)

Scope: 66 files, 4,569 LOC. All 66 in Makefile build list (131 bb_ total repo-wide, 0 missing either direction) — **no unbuilt files in this range.**

## 1. INVENTORY (by family)
| Family | Files | LOC | Purpose | Verdict |
|---|---|---|---|---|
| match (IR_MATCH_*) | 29 | 2541 | SNOBOL4/Snocone pattern primitives (ARB, ARBNO, BAL, ANY, NOTANY, BREAK/X, SPAN, TAB/RTAB/POS/RPOS, LEN, FENCE0/1, ALTERNATE, CAPTURE, DEFER, BEGIN, END, ATP, LIT, REM, REPLACE, VALUE, ABORT) | Live, central; heaviest env-flag experimentation |
| scan (IR_SCAN_*) | 12 | 688 | Icon `s ? expr` string-scanning generators | Live, distinct feature from match |
| var | 5 | 186 | local slot / N-hop lexical frame walk / global-table GVA / name-cell | Live |
| swap/rev | 5 | 184 | :=:, <->, reversible assigns (do/undo on β) | Live |
| to/to_by | 2 | 206 | Icon TO/BY generators, int/real arms | Live |
| unop / unop_gvar_slot | 2 | 147 | unary ops; gvar_slot = narrow fast-path duplicate | Live, overlapping |
| subscript/section/subject | 3 | 161 | x[i], x[i1:i2], SUBJECT load | Live |
| misc singles (main, make_list, move_label, proc_value, random, ref_invariant, repalt, return, statement, succeed, suspend) | 11 | 393 | one IR op each; main/repalt not full boxes | Live |
| zdp_anchor | 1 | 63 | diagnostic probe scaffolding, not a Byrd box | Live non-box |

## 2. DEAD PARTS
- **bb_match_arbno.cpp ~72% dead**: `bb_match_arbno_DELETED_ARMS()` (L229, 198 lines to EOF) called nowhere; transitively sole keeper of bb_match_arbno_tail (L120-174), bb_match_arbno_rbp (L176-206), helpers zv/arbno_zero_window/nofill/poison/fill_cells/fill_window (L14-28), trd/trq/tail_zero/tail_cap_zero8/tail_cap_copy (L30-34). Live dispatcher (L210-227) reaches only frameless_k/frame/frameless. ~306 of 426 lines unreachable.
- Orphaned static helpers: `apin()` + `stmt_has_proc_invoke()` bb_match_begin.cpp:20-21; `fence_whack_on()` bb_match_fence1.cpp:12.
- No #if 0.

## 3. VIOLATIONS
- MEDIUM_*: **zero**. Raw-byte producers outside x86_asm.h: **zero**. Blank lines: **zero**. C Byrd-box fns: **zero**. Language-name branches: **zero**.
- 200-char: 14 files, all long `x86("comment", ...)` narrative lines: bb_match_defer (13), bb_match_capture (7), bb_match_any/break/end/notany (4 each), arbno/span (4-5), begin (2), arb/breakx/fence0/statement (1 each).
- Per-op filter (borderline): `has_replace_l()` in bb_match_end.cpp:24 AND bb_match_begin.cpp:24 (duplicated verbatim) — CFG hazard census over ops (REPLACE|FENCE0|FENCE1|ABORT|ARBNO) gating stfh() storage optimization. Likely not letter-violation (hazard census, not family admit/refuse) but the kind of list the rule warns about.

## 4. STRUCTURE
- Canonical skeleton: x86_alpha…x86_gamma…x86_beta…x86_omega (stateful) or alpha…gamma…beta_trampoline (single-shot). Vast majority conform.
- Deviants (not real 4-port boxes): bb_main.cpp (driver glue), bb_zdp_anchor.cpp (probes), bb_repalt.cpp (3 splice fragments), bb_statement.cpp (single-entry trailer, no beta), bb_ref_invariant.cpp (alpha+gamma only).
- **match vs scan: NOT two generations — two different language features** sharing the r13/r14/r15 subject/cursor/length convention. match = SNOBOL4 pattern statement (THREE-ZETAS frame taxonomy). scan = Icon `s ? expr` (flatter, ports Icon's fstranl.r/fscan.r). Disjoint IR ops, never share a dispatch site. Reorg: keep as two families/subdirs.

## 5. DEPENDENCIES
- Universal: emit.h, bb_template_common.h, x86_asm.h, <string> (all 66); bb_templates.h (22); descr.h (30). ast.h/SM.h narrowly (bb_unop*, TT_* constants).
- Boundary inconsistency: bb_to.cpp, bb_to_by.cpp, bb_unop_gvar_slot.cpp include ../runtime/builtins/gen.h for BINOP_* enums; all others use local extern "C" prototypes.

## 6. NAMING / DRY
- **Major DRY: cset-dispatch block (~13 functions) copy-pasted ×5** with different 2-letter prefixes: bb_match_any (an_*), notany (na_*), break (bk_*), breakx (bx_*), span (sp_*) — factor to shared bb_cset_dispatch.
- 6 of 12 scan files repeat the same runtime-var-arm vs baked-literal-arm ternary shape.
- `has_replace_l()` duplicated (begin/end). `frame_reach()` duplicated verbatim bb_var_frame.cpp:10 + bb_var_frame_ref.cpp:10.
