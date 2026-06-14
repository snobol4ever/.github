# HANDOFF — BB-FIXUP-A-to-Z 76th attended run (Opus 4.8)

**Date:** 2026-06-13 · **Goal:** GOAL-BB-FIXUP-A-to-Z.md · **Cursor:** bb_call.cpp (UNCHANGED — cross-cutting heal, not a cursor stop)
**SCRIP landed:** a58bd75 → rebased to **95bc33f** on push (absorbed concurrent a6f9d65, clean)
**Lon attending:** "What % … Continue." ×N → "Continue." (delegated close → option 1 hand off)

## TL;DR
ONE HEAL LANDED — fully fixes SNOBOL4 DEFINE m2=m3=m4 (7/7/7, HARD gate green). An apparent second bug ("W2", m4 proc-binop drop) was a **PHANTOM — a stale-object build artifact, not a real regression**. Corrected here; next session must NOT chase it. DEFINE family is DONE; cursor resumes at bb_call.cpp.

## W1 — DEFINE single-ownership heal (LANDED, clean-build verified)

`9baaf64` (concurrent, IR-IMMUTABLE session under Lon's "each language session heals its own breakage") wired `ir_delete_all` (→ `bb_program_free` → `IR_free`) to free the entire IR pool before m3 run / after m4 emit. Its message assigned the SNOBOL4 heal: *"DEFINE now aborts (free(): invalid pointer during ir_delete_all) … HEAL: SNOBOL4 session fixes DEFINE lowering single-ownership."*

**Root cause (precise):** `lower_snobol4.c:1009` `*fg = *g` carves each DEFINE'd proc as a **view graph** that aliases the main graph's node array — after the struct copy `fg->all == g->all`, `fg->n == g->n` (also lit/exec/operand_aux aliased), with only `fg->entry` repointed to the proc body. Harmless for codegen (proc nodes live in the main pool; `fg` is a view selecting a different entry). But `bb_program_free` assumes every pooled graph OWNS its `all`, so `IR_free(g)` then `IR_free(fg)` double-freed the shared array. Never exposed before because `--run`/`--compile` never freed the pool (at 1f9f595 `ir_delete_all` wasn't yet wired for SNOBOL4).

**Fix (free-time only, codegen-neutral by construction — leaves the aliased `all` intact for emission, changes only `IR_free`):**
- `IR.h`: `int aliased;` appended to `IR_graph_t` (calloc-zeroed via `IR_alloc` → 0 for ALL owning graphs; only the proc view sets it).
- `scrip_ir.c` `IR_free`: `if (!bbg->aliased) { free nodes; free all; }` — still `free(bbg)` (the view struct is its own calloc).
- `lower_snobol4.c`: `fg->aliased = 1;` immediately after `*fg = *g;`.
- Future-proof: if sidecar frees (lit/exec/operand_aux, reverted by 9baaf64 from f0c3e29) ever return, they go inside the same `!aliased` guard.

**Result (CLEAN-BUILD verified on 95bc33f):** SNOBOL4 **m2=m3=m4 = 7/7/7** (HARD gate GREEN; both m3 and the m4 smoke went 6→7 — the abort had broken m3 exec AND the m4 smoke's rc-gated `&&` build-chain). Icon 12/12/12, Prolog 5/5/5 UNREGRESSED (only DEFINE does `*fg=*g`; all other graphs aliased=0 → IR_free unchanged). db2ad0e arith probes unregressed (2**8=256, (-2)**3=-8, 3.4**2=11.56). BB rank GRAND **1101 UNCHANGED** (no bb_*.cpp touched). Floor: 9baaf64's "SNOBOL4 m4 unchanged (HARD ok)" WAS wrong (m4 aborted rc=134 → `<mode4-build-failed>`); the heal RESTORES sno m4 7/7.

## ⛔⛔ The "W2" phantom + BUILD-HYGIENE LESSON (read this)

After the IR.h edit, an **incremental** `make -j4 scrip` did NOT rebuild `emit_bb.o` against the new header. That stale object made define **m4** emit an empty proc binop. I mis-diagnosed this for several steps as a real, separate concurrent regression — "proc-body m4 binop drop, traced to c0253bc/db2ad0e gvar-operand rework" — and even ground-truthed against a 1f9f595 worktree (which, built fresh, showed 42, reinforcing the false belief in a regression). A subsequent **`make clean` full rebuild produced define m4=42**, proving the binop was never dropped — it was build staleness.

**RULE for next session (and a candidate task):** after ANY header edit (`IR.h`, `descr.h`, `ast.h`, `SM.h`, `stage2.h`, …), `make clean && make`. The Makefile's header-dependency tracking is INCOMPLETE; incremental builds across a header change are untrustworthy and will manufacture phantom bugs. A real fix to the dep rules is logged as an outstanding candidate.

(The 95bc33f commit MESSAGE still carries a "KNOWN: define m4 still red" line written under the phantom. That line is VOID — m4 is green. Not force-amended; the goal watermark + this handoff are the authoritative record.)

## State / outstanding
- SCRIP @ **95bc33f** (W1 heal + concurrent a6f9d65). Cursor **STAYS bb_call.cpp**. SNOBOL4 7/7/7, Icon 12/12/12, Prolog 5/5/5; structural floors green; GRAND **1101**.
- Outstanding verdicts (carried): m2 disj-backtrack (PROLOG-BB) · prove_lower VACUOUS ratify (IR-REDESIGN) · pK m4 silent-empty (PROLOG-BB/RAKU-BB) · brokered-catch m3/m4 silent (PROLOG-BB) · str-relop m3-empty (ICON-BB) · gvar-relop box ungated (ICON/lowering) · rank rp-patch ratify · rank cv9/cv10 desync · ceiling-ratify **1101** (was 1215) · LANGUAGE-BLIND audit category · **NEW: Makefile header-dep tracking gap (clean-build workaround in place; real dep-rule fix is a candidate task)**.
- FIX-3 still open (bb_call dval==2/3 mass; Lon pins A+B from the 75th run unchanged).

## NEXT SESSION
ENV setup (libgc-dev + libscrip_rt) → baseline GREEN (SNOBOL4 7/7/7 now) → resume cursor at bb_call.cpp: FIX-3-iii scan breakout per the 75th-run recipe + dval blocker, OR a fresh Lon pin. DEFINE family is complete. Cursor STAYS bb_call.cpp.
