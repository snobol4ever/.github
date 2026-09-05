# FINDING — 2026-09-04 (seat12, hq_T lane; queue row `snobol4-xfail-class-fuzz-crash-and-hang-corpus-19-entries`, rank 1)
# THE 19-ENTRY FUZZ CRASH/HANG CLASS: FRESH CENSUS AT THE POST-ORACLE-SWAP HEAD, SIX ENTRIES' XFAIL REASONS ARE NOW STALE, AND ONE PLAUSIBLE FIX WAS TRIED AND REVERTED — DISPOSITION: CLASSIFICATION + ONE FALSIFIED CURE, NO ROW CLOSED

**Tree at measurement:** SCRIP HEAD after `git pull --rebase` (merge `b35ddccbc`) + local `make` (incremental, RT_OPT `-O0`; the pristine-per-landing requirement is VOID per CLAUDE.md/RULES.md:118). corpus HEAD `ab43c1184`. Oracle: `/home/resources/x64/bin/sbl -bf`, the **18:19 CDT today** swap (fork `c0dc231`, SIGSEGV-on-exit-after-error cured) — every oracle run in this FINDING is against the NEW binary. **No SCRIP source change survives this session** — see §5.

## 0. POPULATION — CONFIRMED 19, NOT MORE, NOT FEWER

The task's own DONE-WHEN (`grep -A1 -E "^\*-+ [0-9]+ .* XFAIL$" corpus/tests/snobol4/ALL.xfail | grep -ciE "fz_|fuzz"`) was run before touching anything: **`n=19`, exact match to the row's name.** The 19 formal entry names (banner form, `corpus/tests/snobol4/ALL.sno`) are listed in §2. Per hq_T's own warning on this baton (a keyword grep can silently widen a row), the count was cross-checked by listing the matched banners directly, not trusted from the arithmetic alone.

## 1. WHY A FRESH CENSUS FIRST: THE SHARED ORACLE CHANGED FOUR HOURS BEFORE THIS ROW WAS MINTED

hq_T's own doorbell said "an xfail reason records what someone BELIEVED when they wrote it... the belief may have expired." Eighteen of nineteen reasons cite `FINDING-2026-08-20-s188/s189` — **fifteen days old** — and those FINDING files were deleted from the tree this afternoon (`f78d8b3f`, Lon's order). So every reason on this row is now a claim with no live citation. All 19 were re-extracted (`lib_master_extract.sh master_extract_name`, `--out-in` honored) and re-run in **both modes** against the **current** binary and the **current** oracle.

## 2. THE FRESH CENSUS

| entry | m3 | m4 | oracle -bf | ref match (m3/m4) |
|---|---|---|---|---|
| `fence_capture_imm_capture_replace_branch_1` | SIG11 | SIG11 | rc=0 match | -/- |
| `fence_rpos_rem_replace_branch_1` | SIG11 | SIG11 | rc=0 | -/- |
| `arbno_fence_rpos_replace_branch_1` | SIG11 | SIG11 | rc=0 | -/- |
| `arbno_arb_rpos_replace_branch_1` | SIG11 | SIG11 | rc=0 | -/- |
| `fence_span_rpos_replace_branch_1` | SIG11 | SIG11 | rc=0 | -/- |
| `arbno_fence_pos_replace_branch_2` | SIG11 | SIG4 | rc=0 | -/- |
| `arbno_fence_tab_replace_branch_1` | HANG | rc=0 | rc=0 | -/N |
| `arbno_bal_tab_replace_branch_1` | HANG | rc=0 | rc=0 | -/N |
| `arbno_arb_rpos_replace_branch_2` | SIG11 | SIG11 | rc=0 | -/- |
| `fence_arb_span_replace_branch_1` | SIG11 | SIG11 | rc=0 | -/- |
| `fence_arb_tab_replace_branch_1` | SIG11 | SIG4 | rc=0 | -/- |
| `fence_arb_tab_replace_branch_2` | SIG11 | SIG4 | rc=0 | -/- |
| `arbno_fence_bal_replace_branch_3` | rc=0 | rc=0 | rc=0 | N/N |
| `arbno_fence_span_replace_branch_1` | rc=0 | rc=0 | rc=0 | N/N |
| `arbno_fence_bal_replace_branch_1` | rc=0 | rc=0 | rc=0 | N/N |
| `arbno_span_break_replace_branch_1` | HANG | HANG | rc=0 | -/- |
| `arbno_span_tab_replace_branch_1` | SIG11 | SIG11 | rc=0 | -/- |
| `arbno_fence_bal_replace_branch_2` | rc=1 | rc=1 | rc=0 | N/N |
| `arbno_fence_span_replace_branch_2` | HANG | HANG | rc=0 | -/- |

⛔ **The entry basenames (`*_replace_branch_N`) are a batch-mint artifact, not a semantic description** — none of the 19 programs calls SNOBOL4 `REPLACE()`; do not route anyone to `bb_match_replace.cpp` on the strength of the name (a keyword-collision trap the naming itself sets).

## 3. MECHANISM MAP, RECOVERED AGAINST THE DELETED FINDINGS (`git show f78d8b3f^:<name>`) AND VERIFIED BY EXACT CONTENT MATCH, NOT NAME GUESSING

Each of these 19 is a **corpus-consolidation rename** of a witness minted at s188/s189/s183. Content, not name, is the join key:

| entry | = prior witness | mechanism (s188/s189 taxonomy) | prior disposition |
|---|---|---|---|
| `fence_capture_imm_capture_replace_branch_1` | `fz_abort_fence1_stackcap` (byte-identical) | FENCE1-stacked-capture: `cap_in_repeat_body` (emit.cpp) under-covers the inner SAVE/COND of a stacked pair inside a FENCE1 body | root-caused to the predicate, not cured |
| `arbno_fence_rpos_replace_branch_1` | `fz_red_m1a_arbno_defer_fencenull` (byte-identical) | **M1** — ARBNO re-enters a deferred element, inline road needs `FENCE(<null-matching>)` | classified, NOT cured (10 killswitches swept, all inert) |
| `arbno_fence_tab_replace_branch_1` | reduction of `fz_segv_24` | **M1**, blob road (no FENCE needed) | classified only |
| `arbno_arb_rpos_replace_branch_1` | `fz_red_m3_arbno_nullalt_gen` (byte-identical) | **M3** — `ARBNO(<null-first-arm ALT> <generator>)` | classified only |
| `fence_arb_span_replace_branch_1` | reduction of `fz_segv_23` | **M2** — sealed captured generator + forcing right neighbour | classified only (dropping the capture cures all M2 witnesses, per ablation — not yet turned into a code fix) |
| `fence_arb_tab_replace_branch_1` | reduction of `fz_segv_18` | **M2** | classified only |
| `fence_rpos_rem_replace_branch_1` | ⛔ **= `fz_red_m2_breach_m4only`** | **M2 1:1-BREACH** — documented in 2026-08-20 as m3 correct / m4-only SIGSEGV | **DRIFT, see §4** |
| `fence_span_rpos_replace_branch_1` | ⛔ **= `fz_red_m2_breach_m3only`** | **M2 1:1-BREACH** — documented as m3-only SIGSEGV / m4 correct | **DRIFT, see §4** |
| `arbno_fence_bal_replace_branch_3` | ⛔ **= `fzr_13_alt_of_arbno`** (= reduction of `fz_diff_13`) | **s189 Class D-1** — an `ALTERNATE`'s "try next arm" β-motion has no seam tier (`zdp_seam_tier`, `zeta_depth.c:38`); root named at s183, candidate cure `SCRIP_RSEAL_OFF` **already measured inert** | do not re-try that killswitch |
| `arbno_fence_span_replace_branch_2` | s189 "class C" reduction | **s189 Class C** — nested `(A\|(B\|C))` alternation livelocks; `emit.cpp:1192`'s `_altnest` guard already refuses this for the ARBNO carrier but the shape reaches livelock by another road | classified, still red |
| `arbno_fence_pos_replace_branch_2`, `arbno_bal_tab_replace_branch_1`, `arbno_arb_rpos_replace_branch_2`, `fence_arb_tab_replace_branch_2`, `arbno_fence_span_replace_branch_1`, `arbno_fence_bal_replace_branch_1`, `arbno_span_break_replace_branch_1`, `arbno_span_tab_replace_branch_1`, `arbno_fence_bal_replace_branch_2` | s183 systematic-fuzzer witnesses (`util_pattern_fuzz.py --seed 11 --depth 4`) | **not in the s188/s189 manual taxonomy at all** — a later, separate fuzzing campaign; no prior root-cause work exists for these 9 | **unclassified against M1–M4/D-1/D-2/A-C; open** |

Prior, explicitly-recorded NON-CURES worth not repeating: **ten killswitches swept on M1's minimal witness, all inert** (`SCRIP_FENCE_IGNORE`, `SCRIP_FENCE0_WHACK`, `SCRIP_SPAN_FRAME`, `SCRIP_OPT`, `SCRIP_SEQ_TAIL`, `SCRIP_ARBNO_ALTSIB`, `SCRIP_PAT_INLINE`, `SCRIP_CAP_SEAMTIER`, `SCRIP_DEFER_XPAT`, `SCRIP_RTSEQ_RESUME`); the `alt-arm-resume-surface` fix (`lower_snobol4.c:1800`) cures a different standing board row and **moves zero of M1–M4**; `SCRIP_RSEAL_OFF` is inert for D-1.

## 4. STALE-REASON FINDINGS — SIX OF NINETEEN NOW BEHAVE DIFFERENTLY THAN THEIR RECORD SAYS

Per this row's own law ("an entry that behaves differently than its reason says is a FINDING, not a failure of this row"):

1. **`fence_capture_imm_capture_replace_branch_1`** — documented **SIGABRT rc=134** (a deliberate, honest internal bomb, `bb_match_capture.cpp` "no home"), both modes. **Now SIG11/SIG11.** The compiled `.s` contains **zero** occurrences of the bomb string (`grep -c 'no home'` = 0) — the classifier defect the 2026-08-20 FINDING named is confirmed **unchanged** (fresh `SCRIP_EARN_DIAG`/`SCRIP_CLASS_DIAG` trace: outer capture pair `need=1`, inner pair's SAVE **and** COND both `need=0`, identical to the FINDING's table), but something downstream now routes the misclassified node to a data-write branch instead of the safe refusal. See §5 — this is now a wild SIGSEGV with **RSP itself corrupted to 0** at the fault (`gdb`: `rip=0x7fffe9c00256` inside the JIT slab, `rsp=0x0`, `rbp` a plausible frame address), which is strictly worse than the documented abort: a controlled, honestly-labeled refusal became a wild control-flow/stack corruption.
2. **`fence_rpos_rem_replace_branch_1`** (`fz_red_m2_breach_m4only`) — documented as a **1:1 mode-breach**: m3 correct (`match`), m4-only SIGSEGV. **Now both modes SIGSEGV.** m3 has regressed since 2026-08-20.
3. **`fence_span_rpos_replace_branch_1`** (`fz_red_m2_breach_m3only`) — documented as the breach in the other direction: m3-only SIGSEGV, m4 correct. **Now both modes SIGSEGV.** Same drift, opposite original arm.
4. **`arbno_fence_span_replace_branch_1`** — documented **rc=134** (SIGABRT). **Now rc=0/rc=0, wrong output (N/N), no crash at all.** The abort is gone; a silent correctness bug remains in its place.
5. **`arbno_fence_bal_replace_branch_2`** — documented **SEGV**. **Now rc=1/rc=1** (a clean nonzero exit, no crash), oracle `rc=0 match`. The crash is gone; scrip now refuses or errors where the oracle succeeds — not yet triaged which.
6. **`arbno_fence_tab_replace_branch_1`** / **`arbno_bal_tab_replace_branch_1`** — both are reductions/witnesses whose 2026-08-20/s183 record implies SEGV-class behavior; both now show **m3 HANG, m4 rc=0-but-wrong-output**. Neither mode crashes any more; the population moved from "crash" to "hang + silent wrong answer," which is a different pair of bugs to cure, not the same one.

None of these six were re-classified, deleted, or had their `.ref` touched — they are reported here exactly as instructed and left exactly as found in `ALL.xfail`/`ALL.sno`/`ALL.ref`.

## 5. ONE FIX ATTEMPTED, DISPROVEN AGAINST A CONTROL, REVERTED BEFORE COMMIT — RECORDED SO THE NEXT ATTEMPT DOES NOT REPEAT IT

Working the FENCE1-stacked-capture mechanism (item 1 above): `emit.cpp`'s three capture dispatch cases (`IR_MATCH_ASSIGN_SAVE` line 1209, `_COND` 1207, `_IMM` 1208) call `bb_prepare(nd)`, which resets `bb_ls/bb_rs/bb_op_lbl/bb_lk` but **not `op_off`**. `bb_match_capture.cpp`'s `havehome()` macro (`_.op_zres || _.op_cap_anchor || _.op_off >= 0`) treats any non-negative `op_off` as "has a home." Empirically (`gdb`, breaking on `bb_match_capture`, printing `g_emit.op_off`): **`op_off` reads `0` at every one of the four capture-node visits in the red witness — identical to the green one-capture control.** For the misclassified inner SAVE (`op_frame_need=0`, `op_cap_frame_off=-1`, `op_cap_anchor=0`), this stray `0` satisfies `havehome()` by accident and the template writes `r14d` to `FR(0)` instead of reaching the "no home" bomb — a plausible account of how a classifier bug that used to abort safely now corrupts the stack.

**Candidate fix tried:** explicitly set `g_emit.op_off = -1` at the end of each of the three capture dispatch cases (after any legitimate consumption of the incoming value, e.g. `SAVE`'s `op_fc_base` derivation), so a node with no real slot reads `op_off < 0` at `havehome()` time.

**Result: FALSIFIED against the green control.** `bb_match_capture()` has an *earlier*, unconditional gate — `(_.op_off < 0) ? bomb("capture stack slot not promoted") : ...` — at the very top of the function, ahead of every phase/frame_need/anchor branch. The one-capture control (which never reaches `havehome()` at all — it takes the `op_cap_frame_off != -1` activation-frame branch) **also** depends on `op_off` reading non-negative at entry, for this unrelated, earlier gate. Resetting `op_off` to `-1` made the previously-green control bomb too (`rc=134`, "capture stack slot not promoted"). **Reverted; `git status`/`git diff` confirm the SCRIP tree is byte-identical to the pulled HEAD — nothing was committed or pushed.**

**Why this matters for the next attempt:** `op_off` is overloaded across at least two unrelated purposes inside one template — a blanket "has this capture been through slot-promotion at all" precondition, and (separately) one of three ways `havehome()` decides a *specific* node has a writable home. A correct fix needs to give the capture template a signal for "do I, this node, actually have a home" that is independent of `op_off`'s incidental leftover value, or make the line-36 gate consult the same corrected signal — either way it touches all three phases and needs the **full corpus board (m3+m4, `corpus_suite_harness.py run`) run clean**, not just the one red witness and one control, before it can land. That full-board proof was not attempted this sitting; the two-point falsification above was enough to disqualify the candidate.

## 6. WHAT THIS ROW HAS NOT DONE

DONE-WHEN is **still RED, `n=19`** — nothing here is a cure. No entry was reclassified, deleted, or had its `.ref` re-cut. No `.s` regen applies (no committed source change). This is a classification + one falsified-and-reverted fix, the same disposition the original s188 FINDING for this exact ABORT mechanism reached two weeks ago ("classification row, no fix attempted"); this sitting adds a fix *attempt* and its falsification on top of that, plus the fresh census and the six drift findings.

## 7. FOR THE NEXT SEAT (prioritized)

1. **The 9 s183-only entries (no s188/s189 lineage) are the least-investigated ground** — nobody has ablated them yet. Start there before re-opening M1–M4, which two prior dedicated sessions already carried to "investigation-only."
2. **FENCE1-stacked-capture (item 1, §4):** the classifier defect (`cap_in_repeat_body`'s FENCE1 bracket under-covering a stacked inner pair, `emit.cpp:706-717`) is confirmed still live and is the more promising target than the `op_off`/`havehome()` symptom this sitting chased — fixing the classifier so the inner SAVE/COND correctly get `need=1` (matching the outer pair) is more likely to produce a real `match` than patching how the "no home" fallback is reached.
3. **D-1 (`arbno_fence_bal_replace_branch_3`) is not a fresh problem** — it is `zdp_seam_tier` needing a third β-motion for `IR_MATCH_ALTERNATE`'s "try next arm," named at s183/s189 and un-cured since. `SCRIP_RSEAL_OFF` is proven inert; do not re-spend time confirming that.
4. Any fix touching `emit.cpp`'s capture dispatch or `cap_in_repeat_body` needs the full SNOBOL4 master-suite board (m3 **and** m4) clean before landing — this template is on the path of every capture in the corpus, not just these 19.

**WITNESSES/ARTIFACTS:** none checked into corpus (no `.sno`/`.ref` changes, per law 0d — nothing here is a new reduction, all 19 already exist in the master). Working extractions + raw run logs live under this session's scratch dir, not the repo.
