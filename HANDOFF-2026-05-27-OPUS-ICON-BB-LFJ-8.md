# HANDOFF — 2026-05-27 Opus 4.7 — ICON-BB LFJ-8

**Session goal:** ICON-BB · LFJ-8 (`ir_a_Every` → `lower_icn_new_Every`, flip TT_EVERY)
**Developer:** Claude Opus 4.7
**Date:** 2026-05-27
**Final watermark:** SCRIP `3d8aae8c` · .github (this commit)

---

## Outcome

LFJ-8 landed. TT_EVERY is now owned by `lower_icn_new.c`. Gates green, FACT RULE clean.

| Rung | SCRIP commit | AST kinds flipped | What landed |
|------|----------------|---|---|
| LFJ-8 | `3d8aae8c` | TT_EVERY | `lower_icn_new_Every` — 1:1 transcription of legacy_EVERY (which already encoded JCON's flat-wire generator topology with inline mapping comments). Preserves AG-pure step 8.1 literal-bound gating (`gen->α==NULL && gen->β==NULL`) and step 8.2 TT_TO/TT_TO_BY dynamic-bound routing through `lower_icn_expr_threaded_b`. JCON's 6 Goto chunks collapse onto 4 CFG port assignments per the SCRIP encoding. |

**Gates:** smoke_icon 5/5 · broker 25 · rungs 198 · smoke_prolog 5/5. FACT RULE: 0.

---

## Verification

Followed the LFJ-2..LFJ-7 methodology exactly:

1. Read `ir_a_Every` from irgen.icn:309-332.
2. Cross-referenced LOWER-IRGEN-MAPPING.md sec. 3 for JCON-only artifacts with no SCRIP analog.
3. Read existing `lower_icn_legacy_EVERY` (lower_icn.c:492-541) for SCRIP's current encoding — the inline comments there already documented the flat-wire convention from AG-pure step 8.1 commit `f81e1d51`.
4. Confirmed the 8.2 intercept in `lower_icn_expr_threaded_b` matches on `nd->t == BB_TO/BB_TO_BY` (BB-kind), not on producer function — so the new lowering remains wrapper-transparent.
5. Wrote `lower_icn_new_Every` with a 50-line comment block documenting: JCON shape, SCRIP shape, port-wiring mapping, AG-pure 8.1 / 8.2 interactions, "do B" optional case, JCON-only state with no SCRIP analog (ir_init_loop, ir_loop_stack, label allocations, bounded-suspend chunks, ir_coord).
6. Added `extern BB_t *lower_icn_expr_threaded_b(...)` to lower_icn_new.c.
7. Added declaration to lower_icn_new.h.
8. Flipped `lower_kind_table[TT_EVERY]` in lower_icn.c:1056 from `lower_icn_legacy_EVERY` to `lower_icn_new_Every`.
9. Added temporary `fprintf(stderr, "[new Every]\n")` probe at top of new function.
10. Built (`bash scripts/build_scrip.sh`).
11. Ran targeted probe:
    ```icn
    procedure main()
       every i := 1 to 5 do
          write(i)
       every write(1 | 2 | 3)
    end
    ```
    `./scrip --run` output: `[new Every]` printed twice (once per every form), then `1\n2\n3\n4\n5\n1\n2\n3\n`. Matches expected.
12. Removed probe + #include <stdio.h>, rebuilt, reran gates. All green.

---

## Architectural notes

**Code is structurally identical to legacy_EVERY.** legacy_EVERY's inline comments already documented the JCON→SCRIP mapping for ir_a_Every — those comments were authored when AG-pure step 8.1 added the flat-wire convention. The new function's comment block captures the SAME mapping in the LFJ-style "documentation-as-contract" format used by LFJ-2..LFJ-7, but the C statements are 1:1.

**Why this is fine:** the LFJ method's value is the dispatch-table flip and the documentation-as-contract — not necessarily new code generation. Where legacy already implemented the JCON semantics faithfully, the transcription is a verbatim copy. The LFJ-15 cleanup will delete the legacy version; the new function is the canonical residence.

**Where legacy was non-faithful** (e.g. LFJ-5 BINOP missing branches, LFJ-6 IF's missing-else divergence), the new function still copies legacy 1:1 with comments flagging the divergence — the LFJ contract is "zero logic change, document everything." Fixes ride on later passes.

---

## Files touched

| Repo | File | Δ |
|------|------|---|
| SCRIP | `src/lower/lower_icn_new.c` | +77 (new function + 50-line comment block + 1-line extern) |
| SCRIP | `src/lower/lower_icn_new.h` | +1 (declaration) |
| SCRIP | `src/lower/lower_icn.c` | 1 line (table slot flip) |
| .github | `PLAN.md` | ICON-BB row updated |
| .github | `GOAL-ICON-BB.md` | LFJ-8 row updated · watermark `3d8aae8c` |
| .github | `HANDOFF-2026-05-27-OPUS-ICON-BB-LFJ-8.md` | new (this file) |

---

## Next — LFJ-9

**Task:** Transcribe `ir_a_Compound` + `ir_a_ProcBody`. Flip the relevant slots.

**Reference:** irgen.icn — search for `procedure ir_a_Compound` and `procedure ir_a_ProcBody`.

**Caveats to investigate:**
- SCRIP's parser may not produce a distinct AST kind for Compound (it's likely TT_SEQ or part of the proc-setup path which short-circuits the dispatcher).
- ProcBody is procedure-level and lives in proc-setup, not the per-expression dispatcher — may be a "no-flip" rung (document non-emission like LFJ-4's TT_LOCAL/TT_STATIC_DECL).
- If both kinds turn out to be no-ops at the dispatcher level, write the new functions anyway with proper documentation, register declarations, but skip the table flip — and document the rationale.

**Method:** identical to LFJ-2..LFJ-8. The "wrapper-transparent migration" insight from LFJ-2..LFJ-7 continues to hold.

---

## Status — LFJ staircase

| Rung | Status | Commit |
|------|--------|--------|
| LFJ-0  | ✅ | `bc7dae2a` |
| LFJ-1a-i..vi | ✅ | `f79ea9ba` `013703ff` `b252409f` `320f1eea` `092f7862` `0ed7ace3` |
| LFJ-1b | ✅ | `e5eb34b0` |
| LFJ-1c | ✅ | `5cd9003d` |
| LFJ-2..LFJ-7 | ✅ | `620a0ab0` (one session) |
| **LFJ-8** | **✅** | **`3d8aae8c` (this session)** |
| LFJ-9..LFJ-14 | open | — |
| LFJ-15 | open (delete legacy file) | — |

7/15 rungs remain. Pace is steady; current cadence suggests LFJ-9..LFJ-14 in 2-3 sessions if rungs continue grouping cleanly.
