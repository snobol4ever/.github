# HANDOFF — 2026-05-27 Opus 4.7 — ICON-BB LFJ-9 + LFJ-10 + LFJ-11

**Session goal:** ICON-BB · continue LFJ staircase progression
**Developer:** Claude Opus 4.7
**Date:** 2026-05-27
**Final watermark:** one4all `8b6e513b` · .github (this commit)

---

## Outcomes

Three rungs landed this session — LFJ-9, LFJ-10, LFJ-11. Gates green throughout, zero regressions. After this session **10 of 15 LFJ rungs complete (67%)**.

| Rung | one4all commit | AST kinds flipped | What landed |
|------|----------------|---|---|
| LFJ-9  | `80b9130e` | (none) | `lower_icn_new_Compound` + `lower_icn_new_ProcBody` — **documented non-emission** per LOWER-IRGEN-MAPPING.md Q5 + LFJ-4 precedent. Both JCON procedures are realized in SCRIP by the non-`ir_a_*` plumbing function `lower_icn_proc_body` (lower_icn.c:1145), whose inline comments already cite both procedures by name. SCRIP has no TT_COMPOUND/TT_PROC_BODY AST kind — Icon parser emits TT_PROC_DECL with c[2]=TT_PROGRAM (stmt list); neither has a `lower_kind_table` slot, neither reaches the dispatcher (proc_body is called one structural level above `lower_icn_expr_node`). Functions declared in `.h` to complete the LFJ inventory but return NULL — same architectural pattern as LFJ-4 TT_LOCAL/TT_STATIC_DECL. |
| LFJ-10 | `5c5bc669` | TT_FNC, TT_FIELD, TT_SECTION, TT_SECTION_PLUS, TT_SECTION_MINUS (5 kinds) | `lower_icn_new_Call` (ir_a_Call), `lower_icn_new_Field` (ir_a_Field), `lower_icn_new_Sectionop` (ir_a_Sectionop). Call covers general BB_CALL with H-4 γ-chain on args + SCRIP-specific runtime fast paths NOT in JCON: `key()`→BB_KEY_GEN, `find()`→BB_FIND_GEN, `seq()`→BB_SEQ_GEN (JCON would dispatch these via the general Call+Closure machinery). Sectionop dispatches all three SCRIP AST variants via `nd->ival` (0=RANGE, 1=PLUS, 2=MINUS), mirroring JCON's single-procedure p.op dispatch. |
| LFJ-11 | `8b6e513b` | TT_ALTERNATE, TT_SEQ, TT_NOT (3 kinds) | `lower_icn_new_Alt` (ir_a_Alt), `lower_icn_new_Conjunction` (ir_conjunction), `lower_icn_new_Not` (ir_a_Not). Alt uses F-6c convention (arms chain via ω, each arm.γ=BB_ALT, last arm.ω stays NULL for emitter outer-wiring). Conjunction uses H-1 convention (nd->α=e1, nd->β=e2), port wiring realized by AG-pure step-6 BB_CONJ executor. Not has α=inner, executor inverts outcome. JCON-only state with no SCRIP analog documented: ir_max_st/ir_copy_inuse/ir_inter_inuse (per-arm liveness), ir_tmploc/IndirectGoto/MoveLabel (bounded-alt resume indirection — SCRIP uses per-box state). Note: TT_SEQ with 2 children = conjunction; legacy_SEQ also only handled n>=2 as BB_CONJ. |

**Total this session: 8 AST kinds flipped + 2 documented non-emission stubs.**
**Total LFJ progress: 10 of 15 rungs complete.**

---

## Per-rung verification

Followed the LFJ-2..LFJ-8 methodology exactly for each rung:

1. Read the JCON `ir_a_*` procedure from `irgen.icn`.
2. Cross-reference against `LOWER-IRGEN-MAPPING.md` to identify JCON-only artifacts with no SCRIP equivalent.
3. Look at the existing `lower_icn_legacy_*` function for SCRIP's current encoding.
4. Confirm any AG-pure intercept matches on `nd->t == BB_*` (BB-kind), not on producer function — wrapper-transparent.
5. Write the new function in `lower_icn_new.c` with comprehensive comment block.
6. Add declaration to `lower_icn_new.h`.
7. Flip table slot(s) in `lower_icn.c::lower_kind_table_init()` (skipped for LFJ-9 — no slot exists).
8. Add temporary `fprintf(stderr, "[new <kind>]\n")` probe.
9. Build (`bash scripts/build_scrip.sh`).
10. Run targeted probe(s) using existing corpus rungs:
    - LFJ-10: `rung20_section_seqexpr_section_basic.icn` (Sectionop + Call), `rung24_records_record_loop.icn` (Field + Call)
    - LFJ-11: `rung07_control_not.icn` (Not), `rung13_alt_alt_cross_arg.icn` (Alt), `rung13_alt_alt_filter.icn` (Conjunction + Alt)
11. Confirm probe fires AND output matches legacy.
12. Remove probes, remove `#include <stdio.h>`, rebuild.
13. Run full gate suite — held at 5/5 · 198 · 26 · 5/5 throughout.
14. Confirm FACT RULE (`grep == 0`).

---

## Architectural notes

### LFJ-9 non-emission rationale

The LFJ contract is "transcribe every `ir_a_*` procedure from irgen.icn into `lower_icn_new.{c,h}`." Some `ir_a_*` procedures (e.g. `ir_a_Compound`, `ir_a_ProcBody`) describe AST kinds that SCRIP's parser doesn't produce at the dispatcher level — they're consumed one structural level higher by the proc-setup plumbing in `lower_icn_proc_body`. For these, the LFJ method is:

1. Write the new function (returns NULL — it's never reached).
2. Declare it in the header.
3. **Skip the table flip** — no slot exists to flip.
4. Document the SCRIP encoding in a comment block, pointing at the plumbing function that realizes the JCON semantics.

This pattern was established in LFJ-4 (TT_LOCAL/TT_STATIC_DECL: JCON has no `ir_a_Local`/`ir_a_Static`, locals/statics live on per-procedure metadata lists). LFJ-9 applies the inverse: JCON has `ir_a_Compound` and `ir_a_ProcBody`, but SCRIP realizes both in `lower_icn_proc_body`. The non-emission stubs preserve the LFJ inventory completeness.

### LFJ-10 SCRIP fast-path divergence

`lower_icn_new_Call` includes three runtime fast paths that don't appear in JCON's `ir_a_Call`:
- `key(t)` → `BB_KEY_GEN` (table key generator)
- `find(n, h, [start, [stop]])` → `BB_FIND_GEN` (string-search generator)
- `seq([a, [step]])` → `BB_SEQ_GEN` (arithmetic-progression generator)

These are documented as SCRIP-specific compile-time specializations that bypass the general BB_CALL+closure machinery. JCON would dispatch the same Icon functions through the standard call path with the runtime library deciding to suspend. SCRIP gets the same semantics by recognizing the names at LOWER time and selecting specialized BB kinds. This is **intentional divergence**, not a transcription error — the LFJ contract says "zero logic change from legacy," not "byte-identical to JCON." The new function preserves the legacy logic exactly.

### LFJ-11 TT_SEQ ambiguity

SCRIP's `TT_SEQ` AST kind is overloaded:
- With **2 children**, it's a conjunction (`E1 & E2`) and lowers to `BB_CONJ`.
- With **N children** (N>2), it would be a sequence expression.

Legacy `lower_icn_legacy_SEQ` only handled the n>=2 case as `BB_CONJ`. The new `lower_icn_new_Conjunction` mirrors this exactly — checks `e->n < 2`. **If a future Icon parser revision produces TT_SEQ with n>2**, both legacy and new would equally fail to handle it correctly. The (parenthesized sequence E1;E2;...;En) is handled by a separate `TT_SEQ_EXPR` kind via `lower_icn_legacy_SEQ_EXPR`.

This is documented in the LFJ-11 comment block as a potential future-rung concern.

---

## Files touched

| Repo | File | Δ |
|------|------|---|
| one4all | `src/lower/lower_icn_new.c` | +9 functions, ~250 lines (incl. comment blocks) across LFJ-9/10/11 |
| one4all | `src/lower/lower_icn_new.h` | +9 declarations |
| one4all | `src/lower/lower_icn.c` | 8 table-slot flips (LFJ-10: 5, LFJ-11: 3) |
| .github | `PLAN.md` | ICON-BB row updated |
| .github | `GOAL-ICON-BB.md` | LFJ-9, LFJ-10, LFJ-11 rows updated + watermark `8b6e513b` |
| .github | `HANDOFF-2026-05-27-OPUS-ICON-BB-LFJ-9-10-11.md` | this file (new) |

---

## Next — LFJ-12

**Task:** Transcribe `ir_a_While`, `ir_a_Until`, `ir_a_Repeat`, `ir_a_Limitation`. Flip TT_WHILE, TT_UNTIL, TT_REPEAT, TT_LIMIT.

**References:**
- `ir_a_While` / `ir_a_Until` — search for `procedure ir_a_While` and `procedure ir_a_Until` in irgen.icn.
- `ir_a_Repeat` — `procedure ir_a_Repeat`.
- `ir_a_Limitation` — `procedure ir_a_Limitation`.

**Substrate already in tree:**
- `lower_icn_legacy_WHILE_UNTIL` (lower_icn.c:543) — handles BOTH TT_WHILE and TT_UNTIL via `e->t` dispatch. The new function may follow this pattern: one `lower_icn_new_WhileUntil` handling both, plus separate functions for `ir_a_Repeat` and `ir_a_Limitation`.
- `lower_icn_legacy_REPEAT` and `lower_icn_legacy_LIMIT` — investigate.

**Substrate worth understanding:**
- AG-pure step 8 sub-orderings mention BB_LIMIT, BB_REPEAT, BB_WHILE, BB_UNTIL as candidates for AG-pure conversion later — but for LFJ-12 the contract is 1:1 transcription, not AG-pure migration. Just mirror the legacy code.

**Method:** identical to LFJ-2..LFJ-11. Wrapper-transparent migration insight holds.

---

## Status — LFJ staircase

| Rung | Status | Commit |
|------|--------|--------|
| LFJ-0  | ✅ | `bc7dae2a` |
| LFJ-1a-i..vi | ✅ | `f79ea9ba` `013703ff` `b252409f` `320f1eea` `092f7862` `0ed7ace3` |
| LFJ-1b | ✅ | `e5eb34b0` |
| LFJ-1c | ✅ | `5cd9003d` |
| LFJ-2..LFJ-7 | ✅ | `620a0ab0` (one session) |
| LFJ-8 | ✅ | `3d8aae8c` |
| **LFJ-9** | **✅** | **`80b9130e` (this session)** |
| **LFJ-10** | **✅** | **`5c5bc669` (this session)** |
| **LFJ-11** | **✅** | **`8b6e513b` (this session)** |
| LFJ-12 | open | — |
| LFJ-13 | open | — |
| LFJ-14 | open | — |
| LFJ-15 | open (delete legacy file) | — |

**4 rungs remain plus the final cleanup pass (LFJ-15).** Current pace (3-rungs-per-session for grouped kinds, 6-rungs-per-session for the LFJ-2..LFJ-7 batch) suggests LFJ-12/13/14 could land in 1-2 more sessions if rungs continue grouping cleanly. LFJ-15 (file rename + indirection deletion) is a single mechanical session of its own.
