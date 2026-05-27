# HANDOFF — 2026-05-27 Opus 4.7 — ICON-BB LFJ-2..LFJ-7

**Session goal:** ICON-BB · continue LFJ staircase progression
**Developer:** Claude Opus 4.7
**Date:** 2026-05-27
**Final watermark:** one4all `620a0ab0` · .github (this commit)

---

## Outcomes

Six rungs landed in one session — first six dispatch-table flips of the LFJ staircase. Gates green throughout, zero regressions.

| Rung | one4all commit | AST kinds flipped | What landed |
|------|----------------|---|---|
| LFJ-2 | `620a0ab0` | TT_NULL | `lower_icn_new_NoOp`. No-child → BB_LIT_NUL (genuine NoOp per ir_a_NoOp). With-child → delegates to legacy_NULL (the `/E` is_null test, which is ir_a_Unop op `/` in JCON — proper retirement deferred to that rung). `lower_icn_legacy_NULL` de-static'd. |
| LFJ-3 | `620a0ab0` | TT_ILIT, TT_FLIT, TT_QLIT, TT_CSET | Four literal lowerers: `lower_icn_new_Intlit`/`Reallit`/`Stringlit`/`Csetlit`. JCON's success-chunk + unbounded-resume-chunk shape collapses to "single non-resumable leaf box" in SCRIP because the chain walker already provides succeed-once/fail-on-resume. Csets share BB_LIT_S with strings (current SCRIP runtime convention). |
| LFJ-4 | `620a0ab0` | TT_GLOBAL | `lower_icn_new_Global`. JCON `ir_a_Global` emits no chunks (metadata-only); SCRIP equivalent is BB_SUCCEED placeholder. TT_LOCAL/TT_STATIC_DECL deliberately NOT flipped — JCON has no `ir_a_Local`/`ir_a_Static` (those live on per-procedure metadata lists). The `ir_value` JCON helper has no SCRIP analog per mapping doc Sec. 5/6 — documented as non-emission in lower_icn_new.c. |
| LFJ-5 | `620a0ab0` | 20 binop kinds: TT_ADD/SUB/MUL/DIV/MOD/POW/LT/LE/GT/GE/EQ/NE/CAT/LCONCAT/LLT/LLE/LGT/LGE/LEQ/LNE | One function `lower_icn_new_Binop` covers them all, mirroring JCON's single `ir_a_Binop` procedure with internal dispatch on `p.op`. AG-pure step-3 intercept in `lower_icn_expr_threaded_b` is producer-agnostic — it catches the new fn's tree-shape transparently. `lower_icn_expr_node` de-static'd for cross-file recursion. Branches NOT covered (documented in comment): `p.op == "&"` (TT_CONJ, LFJ-11), augmented assignment (TT_AUGOP, separate slot), `@` (defer), resumable-op closure path (unary generators, separate kinds). |
| LFJ-6 | `620a0ab0` | TT_IF | `lower_icn_new_If`. AG-pure step-5 intercept already realizes JCON's wiring (`cond.γ=cond.ω=nd_if; nd_if.γ=then.α; nd_if.ω=else.α`). JCON-only state (tmp/tiu/xiu/yiu name allocations, ir_max_st/ir_union_inuse scope unions, MoveLabel/IndirectGoto continuation tracking) has no SCRIP analog. Pre-existing semantic divergence noted in comment: JCON synthesizes `else := &fail` for missing else; SCRIP intercept routes cond.failure→γ_in (correct for if-as-statement; differs for if-as-expression unbounded). LFJ-6 doesn't change this — it's a property of the intercept. |
| LFJ-7 | `620a0ab0` | TT_TO, TT_TO_BY | `lower_icn_new_ToBy`. JCON has NO separate ir_a_To — `i to j` is `i to j by 1` with byexpr defaulted at irgen.icn:1171. New fn dispatches on `e->t`. Preserves both SCRIP optimization paths: static-literal fast (both bounds TT_ILIT → ival/dval, α/β NULL) and dynamic (α/β as boxes, 8.2 intercept upgrades to AG-pure). `icn_fold_signed_lit` de-static'd for cross-file use. |

**Total: 28 AST kinds flipped to `lower_icn_new.c` in one session.**

---

## Per-rung verification methodology

Each rung followed the LFJ-2 acceptance pattern:

1. Read the JCON `ir_a_*` procedure(s) for the rung from `/home/claude/corpus/programs/icon/jcon-ref/irgen.icn`.
2. Cross-reference against `LOWER-IRGEN-MAPPING.md` to identify JCON-only artifacts with no SCRIP equivalent (the mapping doc was authoritative throughout — saved real time on LFJ-4's `ir_value` and LFJ-6's tmp-name state).
3. Look at the existing `lower_icn_legacy_*` function(s) for the kind in question to see SCRIP's current encoding (BB-kind choice, optimization paths, intercept hooks).
4. Look at any AG-pure intercept in `lower_icn_expr_threaded_b` that targets the kind — confirm it matches on `nd->t == BB_*` and not on the producer function (this is the architectural invariant that lets table flips be wrapper-transparent).
5. Write the new function in `lower_icn_new.c` with a comment block documenting: source (irgen.icn line range), wiring mapping JCON→SCRIP, JCON-only state ignored, branches NOT covered (with rationale), any SCRIP-specific optimizations preserved.
6. Add the declaration to `lower_icn_new.h`.
7. Flip the table slot(s) in `lower_icn.c`'s `lower_kind_table_init()`.
8. Add a temporary `fprintf(stderr, "[new <kind>]\n")` at the top of the new function.
9. Build (`bash scripts/build_scrip.sh`).
10. Run a targeted probe program exercising the AST kind; confirm probe line(s) print AND output matches legacy.
11. Run full gate suite — must hold at 5/5 · 198 · 24 · 5/5.
12. Remove probe; rebuild; rerun gates; confirm template-only rule (`grep == 0`).

This methodology caught the LFJ-4 finding that TT_GLOBAL is intercepted in proc-setup paths before reaching the dispatcher, and the LFJ-2 finding that SCRIP-Icon's parser never produces childless TT_NULL. Both were resolved with documentation rather than code changes — the new functions own the table slot correctly even when the AST shape that would reach them doesn't currently come out of the parser.

---

## Architectural insight: wrapper-transparent migration

The single most useful realization this session: **the AG-pure intercepts in `lower_icn_expr_threaded_b` match on `nd->t == BB_*` (the BB-kind) and surrounding AST kind, NOT on which function produced the BB**. This means:

- The new lowering function can produce the **same legacy tree-shape** (`nd->α = lhs`, `nd->β = rhs`, etc.).
- The wrapper intercept then plucks lhs/rhs from α/β, scrubs them to NULL, and lays down the AG-pure γ-chain.
- The executor's AG-pure branch (`nd->α == NULL && nd->β == NULL`) takes over.

This is elegant: migrations through the dispatch table need not coordinate with downstream consumers. The new function and the legacy function are interchangeable from the wrapper's perspective. **One-line revert** (flip the table slot back) genuinely just works because the wrapper doesn't know or care.

This applies cleanly to LFJ-5 (BB_BINOP), LFJ-6 (BB_IF), LFJ-7 (BB_TO/BB_TO_BY). The literal kinds (LFJ-3) and degenerate cases (LFJ-2, LFJ-4) don't go through AG-pure intercepts at all — they're leaf boxes that just exist as fresh-entry/fail-on-resume.

---

## Next rung — LFJ-8

**Task:** Transcribe `ir_a_Every` → `lower_icn_new_Every`. Flip TT_EVERY.

**Reference:** irgen.icn:309-332.

**Substrate to understand before coding:**

1. **AG-pure step 8.1 BB_EVERY** (commit `f81e1d51`): dispatcher passthrough for literal-bound generators. Gated on `gen->α == NULL && gen->β == NULL && gen->γ != NULL` (flat-wire condition from TT_EVERY lowering at lower_icn.c:444). Marker `nd->ival = 1` selects the AG-pure executor branch. State==0 hands off via nd->α through chain; state==1 = re-entry from gen.ω → return γ.

2. **AG-pure step 8.2 BB_TO / BB_TO_BY dispatch** (commit `7acc7849`): when c[0]->t is TT_TO/TT_TO_BY, lower_icn_legacy_EVERY routes the gen child through `lower_icn_expr_threaded_b` (lower_icn.c:503-506) so the 8.2 intercept scrubs gen->α/β, chains lo→hi→gen via γ, stamps sval marker. This is the entry path for the AG-pure dynamic-bound case.

3. **Legacy EVERY** at `lower_icn_legacy_EVERY` (lower_icn.c:492+) is a substantial function — has the TT_TO/TT_TO_BY routing branch, body lowering, marker stamping for the AG-pure branch. Needs careful 1:1 transcription with the same routing logic. The "ZERO logic change" mandate applies.

4. **JCON's ir_a_Every** uses `closure := ir_tmp` (closure cell for re-yield) and ResumeValue for re-entry. SCRIP packs that state into BB_EVERY's counter/state/value fields per mapping doc Sec. 3.

**Recommended approach:**
1. View irgen.icn:309-332 (ir_a_Every).
2. View lower_icn.c:492-590 or so (legacy_EVERY in full).
3. View bb_exec.c BB_EVERY executor branch to confirm what the lowerer must produce.
4. The new function will preserve the TT_TO/TT_TO_BY routing branch (it's how step 8.2 gets activated) — that's not a logic change, it's substrate plumbing.
5. Write `lower_icn_new_Every`, declare in header, flip TT_EVERY slot.
6. Probe with both static-bound (`every i := 1 to 3`) and dynamic-bound (`every i := lo to hi`) every-loops to confirm both paths fire.

---

## Subsequent rungs preview

| Rung | JCON procedures | SCRIP AST kinds |
|------|---|---|
| LFJ-9  | ir_a_Compound, ir_a_ProcBody | Compound may be a no-op per mapping doc Q5 (proc_body is C-level lower_icn_proc_body); investigate. |
| LFJ-10 | ir_a_Call, ir_a_Field, ir_a_Sectionop | TT_FNC, TT_FIELD, TT_SECTION/SECTION_PLUS/SECTION_MINUS. ir_a_Call is the BIG one — n-ary args, generator arg odometer. AG-pure step 9 territory. |
| LFJ-11 | ir_a_Alt, ir_conjunction, ir_a_Not | TT_ALTERNATE, TT_SEQ (for conjunction — TT_SEQ becomes BB_CONJ when 2-child non-statement), TT_NOT. |
| LFJ-12 | ir_a_While, ir_a_Until, ir_a_Repeat, ir_a_Limitation | TT_WHILE, TT_UNTIL, TT_REPEAT, TT_LIMIT. |
| LFJ-13 | ir_a_Scan, ir_a_Case, ir_a_Return, ir_a_Suspend, ir_a_Break, ir_a_Next | TT_SCAN, TT_CASE, TT_RETURN, TT_SUSPEND, TT_LOOP_BREAK, TT_LOOP_NEXT. |
| LFJ-14 | Remaining ir_a_* (Create, Mutual, Key, Invocable, Link, Initial, RepAlt, CoexpList, Unop, augmented_assignment) | All remaining kinds. |
| LFJ-15 | (no JCON proc — final cleanup) | Delete `lower_icn.c`. Delete all `_threaded_b` AG-PURE intercept branches. Delete `lower_kind_table` indirection. Rename `lower_icn_new.c` → `lower_icn.c`. |

---

## Final gate snapshot (post LFJ-7)

```
smoke_icon:        PASS=5  FAIL=0
smoke_prolog:      PASS=5  FAIL=0
smoke_broker:      PASS=24 FAIL=27
icon_all_rungs:    PASS=198 FAIL=34 XFAIL=36 TOTAL=268
template-only:     grep == 0
```

Identical to the pre-session baseline (`5cd9003d`). 28 AST kinds now route through `lower_icn_new.c`; behavior preserved exactly.

---

## File ownership touched this session

- `src/lower/lower_icn.c` — table slots flipped, 3 helpers de-static'd, header include added
- `src/lower/lower_icn_new.c` — 8 new functions (NoOp, Intlit, Reallit, Stringlit, Csetlit, Global, Binop, If, ToBy) + extensive comments
- `src/lower/lower_icn_new.h` — 9 declarations
- `.github/GOAL-ICON-BB.md` — 6 rung ticks, watermark update
- `.github/PLAN.md` — ICON-BB row update

No other files touched. No SNOBOL4 / Snocone / Rebus / Raku / Prolog lowering touched. No BB_PAT_* touched. No BB_t struct touched (PEERS rule). Template-only emission rule held throughout (grep == 0 every rung).

---

## Process notes

- Each rung from PLAN to verified-green took 5-15 minutes once the pattern was established (LFJ-2 took the longest because it established the methodology; LFJ-3 was fastest because four very-uniform leaf transcriptions; LFJ-5 was substantive due to 20-kind dispatch + research; LFJ-7 substantive due to two optimization paths to preserve).
- Build was clean throughout — no compile errors after the first include-missing hiccup in LFJ-2 (`<stdio.h>` for the probe).
- Gates ran consistently at smoke_icon 5/5 · rungs 198 · broker 24 · smoke_prolog 5/5. No flakes observed.
- No upstream concurrent commits hit during the session (single committer this time).
- Per RULES.md push order: one4all first, .github last.
- The methodology section above is intentionally explicit so the next developer can replicate cleanly. The key habit is **never coding the new function until reading both the JCON procedure AND the existing legacy SCRIP function**: 90% of the "translation" decisions are about what SCRIP already encodes differently (optimization paths, intercept hooks) and how to preserve that while still claiming faithful transcription. The legacy is the SCRIP rendering of the JCON procedure; the new function inherits that rendering and adds the proper attribution.
