# GOAL-SN4-HOME-LOWER — front-half correctness: LOWER + splice (HOME seat; master = GOAL-SN4-HOME.md)

**CHARTER:** every SNOBOL4 wrong-answer whose owner is `lower_snobol4.c` or the replace/splice arithmetic. **ZERO emitter frame-arm bytes** — that surface is the RBP seat's; this partition is what makes P1 four-way concurrent.

**LAWS THAT BIND HARDEST HERE:** MONITOR-FIRST (RULES §1) · anti-pattern §2 (never guess an offset — instrument) · s29 STANDING INSTRUMENT RULE (state what the defective arm would print; every board carries a known-PASS control row) · judge BY SET vs BOARD's P0 floors.

## RUNGS
- [x] **L-0 · WITNESS FLOOR — LANDED s33.** Board adopted and MECHANISED as `SCRIP/scripts/board_earn0_set.sh` (m3/m4/both; `REPEAT=n` reports a row whose verdict is not constant as **FLAKY**, never as whichever arm came up first — `earn0_stored_capture` is the known member and a single-shot board misleads by design). All four controls PASS at HEAD. Floor table in the LIVE CURSOR; re-RUN the script, never transcribe it (STALENESS LAW).
- [ ] **L-1 · DEFECT A — PRODUCER ELISION (LOWER, convicted by knob `SCRIP_PAT_INLINE=0`).** Why is a use inside a stored composite not an inlining site, and why is the producer elided before that is known? Fix in LOWER. ⛔ **FIXING A ALONE LOOKS LIKE A REGRESSION** — silent rc=0 passes become rc=124 hangs as the mask comes off (measured s29 §2b). Judge BY SET against the FINDING table; EXPECT the hang count to RISE; a seat that reverts on that signal reverts a correct fix. `SCRIP_PAT_INLINE=0` stays a diagnostic discriminator ONLY.
- [ ] **L-2 · DEFECT B — THE CONSUMER HANG A WAS MASKING.** Mint the default-arm witness FIRST (unreachable today until A lands); then MONITOR-FIRST; the s29 bounded probes say match-time, inside one statement, plausibly unbounded allocation (`[ZHP] heap exhausted` sibling arm — plausible, NOT established; cross-check with HOME-RBX X-4).
- [~] **L-3 · C-9 RESIDUALS — CHARACTERISED s34 (FINDING-2026-08-12d), NOT FIXED (from CLIMB s41, mechanism named, fix incomplete).** ⛔ **s41's "the `start` term needs its own displacement" is TRUE ONLY FOR `TAB`/`RTAB`** (Series T, slope +1: `LEN(k) TAB(6) LEN(1)` arrives start=k, want 0). For `ARB`/`SPAN`/`BREAK`/`REM` the splice receives `start`=**constant 3** and `end`=**`slen`** — Series S is FLAT, so no displacement of any sign or slope can fix it; find the WRITER. POS/RPOS never pick up the unanchored scan anchor (`op_zpat`=0 for them, still splice `[0,1)`). `bal` is wrong on BOTH terms (+1/+1) and is its own row. `LEN`/literals are genuinely clean (verified non-terminal). `op_zpat` precedent: one authority, SUBTRACTED, never folded into `op_zdepth` (double-add class). Then re-measure `test_case` (splice customer, expect clear).
- [ ] **L-4 · 061 — VARIABLE-ARG PATTERN-PRIMITIVE CLASS.** The dynamic arm reads a cell the arg never landed in (whole class, not POS-specific). MONITOR bracket exists per s39b — read that cursor first, do not re-spend.
- [ ] **L-5 · `test_string` SECOND COMPONENT.** Capture also wrong (`r=[   hello]`) — NOT the splice signature; alternation-arm / post-SPAN cursor suspect, unconvicted. Own witness, own conviction.

## GATES (every rung)
crosscheck/patterns + probe BY SET vs P0 floors, both modes · monitor divergence must MOVE PAST the fix · regen ×3 iff codegen touched (splice arithmetic counts) · FINDING per land mine · cursor move per handoff.

## ⭐ LIVE CURSOR — 2026-08-12 s35 (Opus 5). **L-3 ROOT CAUSE FOUND, NOT YET FIXED. NEXT RUNG: L-3 fix — un-guard the C-9 REPL-ZDEPTH correction (emit.cpp:841, currently inside `if (g_zd_arm)`).** ZERO compiler bytes, zero script bytes. FINDING-2026-08-12f.

**⛔ "FIND THE WRITER" IS DISCHARGED — THERE WAS NEVER A MISSING WRITER.** `IR_MATCH_BEGIN` writes `head.cursor` (ZLS **+48**) and `IR_MATCH_END` writes `head.end` (ZLS **+72**) correctly in BOTH the passing and failing shapes. **`IR_MATCH_REPLACE`'s reach-back is aimed exactly 16 bytes LOW**, landing on:

| intended | actually read (−16) | value seen |
|---|---|---|
| ZLS +48 `head.cursor` | ZLS +32 `result` DESCR of MATCH_BEGIN | its dword **type tag `DT_I` = 0x03** ⇒ the flat `3` |
| ZLS +72 `head.end` | ZLS +56 `head.zeta_mark` (GC pointer) | ≫ slen ⇒ **clamped to `slen`** by `c_rt_match_replace` |

So `(3, slen)` was never a cursor at all — that is why Series S read FLAT and why no displacement appeared to fix it. **Board-wide split, all 12 probes, no exceptions:** start_off **64** (=ZLS+48, correct) = `len_nonterm` `len_pure` `lit_len` `pos` — the only 3 PASSes live here; start_off **48** = the other 8 — **8 of 8 FAIL**.

**THE MECHANISM WAS ALREADY IN-TREE AND FIXED ON ONE PATH ONLY.** `emit.cpp:841`'s s35 C-9 REPL-ZDEPTH comment describes this defect verbatim ("all four frame reads … short by exactly the subtree footprint … +16 for a literal replacement, +80 for `A '-' B`"), but the correction sits inside `if (g_zd_arm)` (`zd_on[i]`, emit.cpp:2656). Shapes that decline the ZD arm never get it. L-3's own rung text — *"mechanism named, fix incomplete"* — was literally true.

⛔ **DO NOT HARDCODE 16.** The in-tree comment names the gate: *"any fix hardcoding 16 passes the literal case and FAILS the concat case"* — witness **`P8_concat_repl`**. The correct term is the planner's under-cells quantity **`g_zd_wpop`**. ⛔ **Every probe on the l3 board uses a single-literal replacement, so THIS BOARD IS STRUCTURALLY VACUOUS ON THAT DISTINCTION** — a hardcoded 16 goes 12/12 green here and is still wrong. Judge on `P8_concat_repl` too.

⛔ **INSTRUMENT IS LYING — FIX IT FIRST.** The `SCRIP_REPL_TRACE` fprintf (`gen_runtime.c:161`) prints **after** `if (end > slen) end = slen;`. Every recorded "`end` arrives as `slen`" in this goal actually means "`end` arrived ≥ slen," pointer included. One-line move above the clamp, zero risk, precedes the next measurement.

⛔ **RULE EARNED (7th conviction): on the RSP FORTH spine, never compare two `[rsp+N]` displacements taken at different program points without first proving rsp is unchanged between them.** I convicted the PATCTX save block on exactly that error (`.s` shows `[rsp+48] # outer_Σ`, matching SPAN's read) and it is FALSE — rsp moves repeatedly in between, and in ZLS terms `sigma_save` is at **+96**. The `.s` `#` annotations are per-site labels, NOT a frame map; **`--dump-zeta` is the frame map** and is what killed it.

**`l3_spl_pos` reads the CORRECT slot (64) and still fails** ⇒ POS/RPOS confirmed a genuinely separate defect, by a mechanism the s34 table did not use. **`tab_nonterm` reads at 48 like the class but its `end` arrives CORRECT** ⇒ TAB is plausibly this same 16 on `start` only; **re-measure TAB after the 16 lands before spending anything on s41's Series-T displacement theory — it may fall out entirely.**

### NEXT SEAT, IN ORDER
1. Move the `SCRIP_REPL_TRACE` fprintf above the clamp.
2. Find why the replace node declines the ZD arm in var-length pattern graphs (`zd_on[i]`, emit.cpp:2656) — the single guard separating the 64-group from the 48-group.
3. Land the subtree-footprint correction on the unarmed path via `g_zd_wpop`; gate on `P8_concat_repl` AND the l3 board AND probe/bb BY SET.
4. Re-measure TAB/RTAB (see above), then `bal` (own row, wrong on both terms).
5. Only then L-1 (Defect A), honouring its ⛔ (fixing A alone RAISES the hang count).

**UNBLOCKS:** LOWER L-3 (root cause closed to a named guard + a named correct term). **m3 only — this board's m4 arm is UNMEASURED, not green; BOARD B-0 still owns it.**

---
### s34 record (retained — the four-class table and the l3 board stand; its "find the writer" instruction is now discharged, see above)

**L-3 is THREE classes, not the two s41 recorded, and the third is not a displacement.** Measured at the `SCRIP_REPL_TRACE=1` C boundary (already committed in `gen_runtime.c` — no rebuild, no gdb):

| class | members | `start` arriving | `end` arriving |
|---|---|---|---|
| fixed-length | `LEN(n)`, literals | **CORRECT** ✅ | **CORRECT** ✅ |
| carving | `TAB` `RTAB` | cursor **at the carve site** (Series T: slope exactly +1) | **CORRECT** (s41's `op_zpat` genuinely works) |
| **non-carving var-length** | `ARB` `SPAN` `BREAK` `REM` | **constant `3`** | **`slen`** |
| zero-width | `POS` `RPOS` | `0` | `1` (s41's collapse, reproduced) |

⛔ **NO DISPLACEMENT CAN FIX THE THIRD CLASS.** Series S (`LEN(k) SPAN('ef') 'g'`, k=0..3) has `want start` 5→4→3→2 and `arrived start` **3,3,3,3** — flat. A displacement of any sign or slope must move when want moves. `(3, slen)` is a read of cells nobody wrote for this shape, the same disease as POS/RPOS's `(0,1)`: **find the writer, not an offset.** Anti-pattern §2 applies with force — three of my hypotheses died here (FINDING §4).

**⭐ NEW BOARD — `corpus/probe/l3/` (12 probes, oracle-baked refs), run with the EXISTING generic runner:**
`EARN0=/home/claude/corpus/probe/l3 REPEAT=2 bash scripts/board_earn0_set.sh m3` → **m3 @ `900060c7`: 3 PASS / 9 FAIL-silent.** The 3 PASS are the fixed-length controls. Landed in `probe/l3/`, deliberately **NOT** `probe/bb/` (red rows register as REGRESSION there — s41 left its set in `/tmp` for that reason and **it was lost**, which is why this ground was re-walked).

**⛔ THE VACUOUS-`end` TRAP (new anti-vacuity rule, sixth conviction in this goal):** *a splice witness whose match reaches the end of the subject cannot discriminate `end` from `slen`.* Every splice probe must leave characters to the RIGHT of the match. This is a **second, independent tell** from FINDING-2026-08-12 §3's "success-expecting witness" — that one does not fire here, which is why the rule as written did not catch it. `l3_spl_VACUOUS_terminal_trap.sno` is retained as the documented member.

**⛔ CORRECTION — s33's ORDERING RATIONALE IS FALSIFIED (the rung order survives; the reason does not).** s33 put L-3 first because `cap_after_bal`/`cap_after_varlen` were "L-3's named mechanism verbatim." **Capture and splice are two defects:** BREAK/SPAN/REM/TAB/RTAB **capture correctly** and **splice incorrectly** — one shared `start` authority cannot produce that split. Fixing the splice will NOT clear those two rows; they are L-5-adjacent, owner still open. Also: `earn0_cap_after_varlen.sno`'s stated 9-template blast radius is **over-broad by seven** — only ARB and BAL fail capture (BREAKX and ARBNO PASS, killing the retry-extension hypothesis). The `[n, p+n)` capture formula gained a third witness by advance prediction (`'abcdefg' ? ARB . R 'g'` binds null) and **survives**.

### NEXT SEAT, IN ORDER
1. **Locate the writer feeding the non-carving class** — the prize, and separable from everything else on this board.
2. `TAB`/`RTAB` `start` IS a genuine displacement (Series T) — the one component s41's framing describes correctly.
3. `bal` is its own row: wrong on **both** `start` (+1) and `end` (+1), and the only capture-failing member that also splices wrong. Own witness before folding it anywhere.
4. Only then L-1 (Defect A), honouring its ⛔ (fixing A alone RAISES the hang count).

**UNBLOCKS:** LOWER L-3 (three classes separated, board + reproducers now PERSISTED rather than container-local). BOARD B-0 still owns the m4 arm — **both LOWER boards are m3-only; their m4 arms are UNMEASURED, not green.**


### ⭐ CONCURRENT SEAT NOTE (s34) — ⛔ TWO SESSIONS WERE LIVE IN THIS FILE AT 14:31 (the s38b race; the plan's ONE INVARIANT).
s33b landed `eb735a3f` + corpus `7045b2ea` mid-session while s34 was measuring. **VERIFIED: no work was lost** — all 8 of
s33b's cursor lines survive above, and its FINDING (…CAPTURE-DELTA0-BLAST-RADIUS-IS-TWO-OF-NINE…) is untouched.
The two halves are COMPLEMENTARY: s33b = CAPTURE (ARB/BAL, implicit-alternative class), s34 = SPLICE (non-carving class, constant `(3,slen)`). Both independently measured 2-of-9 blast radius — duplicated spend, which is exactly what the invariant prevents.
⛔ **Lon: LOWER has two live seats. Retire one before re-firing.** The surviving seat owns the full rung sequence above.
⚠️ Both sessions minted a file named `FINDING-2026-08-12d`; the two differ by title and both are kept — the CAPTURE finding is `…BLAST-RADIUS-IS-TWO-OF-NINE…`, the SPLICE finding is `…THE-SPLICE-START-IS-A-CONSTANT…`.

---
### s33 record (retained — L-0's floor and its instrument stand unchanged)

**Seat opened without BOARD's P0 floors** — BOARD's cursor is still UNOPENED, and RULES 2026-08-10 forbids parking on that. L-0 needs no BOARD number: it is this seat's OWN open-state, measured at this seat's HEAD, which is what the STALENESS LAW says a per-rung control must always be.

**FLOOR — earn0 board, m3, SCRIP `52545cbf` · corpus `c91d1adf` (`REPEAT=3`). Judge BY SET.**
| verdict | n | members |
|---|---|---|
| PASS | 12 | `inline_control` · `varref_strvar_control` · `pend_alt_ctl_nopend` · `disc_arbno_star_fence_poisoned` (**the four controls — all green**) · `pend_alt_{first,second}_arm` · `pend_blocked_fencefn` · `pend_dies_on_backtrack` · `pend_fire_order` · `pend_group_noalt` · `pend_survives_{fence1,fencefn}` |
| FAIL-silent | 5 | `cap_after_bal` · `cap_after_varlen` · `disc_arbno_star_fence_positive` · `varref_bare_dropped` · `varref_cat_dropped` |
| FAIL-hang (124) | 2 | `stored_varref` · `varref_blob_hang` |
| FLAKY | 1 | `stored_capture` — all three arms live at this HEAD (measured 8×: 3× rc=0 wrong-bind `V=[]`, 5× rc=134; a later 3× run opened with rc=139) |

**FINDING-2026-08-12 §7 REPRODUCES ROW-FOR-ROW at a HEAD four commits past its own** (`fc5b0754`→`52545cbf`), so its characterisation is live, not stale. **Three rows it never covered are now on the board:** `cap_after_bal`, `cap_after_varlen`, `disc_arbno_star_fence_positive`.

### ⭐ WHY L-3 FIRST (ordering claim, not a re-plan — L-1/L-2 remain owned and unstarted)
The two *new* silent rows are a **capture-start displacement pair**, and their arithmetic points in OPPOSITE directions — which is what makes them discriminating rather than merely broken:
- `cap_after_bal` — expect `R=[(cd)]`, got `R=[cd)]` → start **1 too far RIGHT** (dropped the leading `(`)
- `cap_after_varlen` — expect `R=[ef]`, got `R=[cd+ef]` → start **3 too far LEFT**
Both sit immediately after a **variable-length predecessor** (BAL; a var-length item). That is L-3's named mechanism verbatim: *"the `start` term needs its own displacement (relative advance PRECEDING the carve overshoots)."* A signed pair beats L-3's single recorded datum (`LEN(2) TAB(6) LEN(1)` start 2 want 0), because a fix that merely shifts a constant must fail one of the two.
⛔ **HYPOTHESIS, UNCONVICTED:** L-5's `test_string` signature `r=[   hello]` is *extra leading characters* — the `cap_after_varlen` shape. L-5's text says "NOT the splice signature." **Do not fold L-5 into L-3 on this resemblance**; the correct use of it is to re-measure `test_string` the moment L-3 moves and let it fall out or stay. Owner still L-5.

### NEXT SEAT, IN ORDER
1. **MONITOR-FIRST on `cap_after_bal`** (RULES §1) — 2-way sync-step, not code-reading. It is short, exits 0, and diverges by a WRONG ANSWER, the class the monitor is good at. ⛔ Not the hang rows: gdb is dark on that class (s20) and a non-terminating program has no second trace to align.
2. Sign-check any candidate fix against **both** `cap_after_bal` and `cap_after_varlen` before running anything broader.
3. `disc_arbno_star_fence_positive` is **RBP/EARN's** MONITOR-FIRST target (HOME P1), not this seat's — it is on this board as a *shared* row. If it flips while LOWER works, that is RBP landing, not LOWER regressing. **Set-diff, never count.**
4. Only then L-1 (Defect A) — and honour its ⛔: fixing A alone RAISES the hang count. A seat that reverts on that signal reverts a correct fix.

### s33b — L-3 OPENED (not closed). Board now 28 rows: **18 PASS · 7 FAIL-silent · 3 FAIL-hang.**
- **Blast radius MEASURED: 2 of s27's 9, not 9.** ARB + BAL defective; BREAK/BREAKX/REM/RTAB/TAB/SPAN **clean** and minted as `l3_*_clean` controls — a fix that moves any of them is over-broad and one run detects it. Formula `[n,p+n)` confirmed **predictively** on fresh numbers (ARB) and **falsified** on SPAN, so this is per-template, not a class of "captures after variable-length primitives".
- ⭐ The two defective members are exactly the manual's IMPLICIT-ALTERNATIVE primitives (Ch.18 p.207–8) — the two that carry state across the γ yield because they are re-entered on retry. Better predictor than "writes `FR(x86_scratch_off)`", which all nine do.
- ⛔ **RETRACTED, DO NOT INHERIT:** I hypothesised ARB's counter aliases the capture's saved-δ slot (it predicts the arithmetic exactly) and nearly confirmed it off `# start_δ` in the emitted asm. The raw block shows that slot is **MATCH_BEGIN's unanchored scan anchor** (manual Ch.18 step 6: `add start,1` · `cmp` vs subject end · `rt_anchor_g` = `&ANCHOR` · retry). **Root cause OPEN.** An annotation string is not an instrument.
- **L-4 gift:** `SPAN(V)` hangs rc=124 — 4 lines, plain variable, no defer; the star is NOT the discriminator. Minted `l4_span_varg_hang`. Smaller reproducer than 061 itself.
- **NEXT:** MONITOR-FIRST on `cap_after_bal` (still unrun — §3 of the FINDING is why code-reading first was the wrong order), then locate the COND read / SAVE store addresses **by instrument, not by slot name**, sign-checking against both displacement directions.

**UNBLOCKS:** LOWER L-3 (measured radius + 6 clean controls + signed pair) · LOWER L-4 (smaller 061 witness) · BOARD B-0 still owns the m4 arm — **this board is m3-only; its m4 arm is UNMEASURED, not green.** Full detail: `FINDING-2026-08-12d-…-BLAST-RADIUS-IS-TWO-OF-NINE-…`.
