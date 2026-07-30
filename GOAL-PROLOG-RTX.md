# GOAL-PROLOG-RTX.md — The Prolog Runtime in Optimized x86-64 Assembly

**Minted s221-PL (2026-07-30) on Lon's directive:** *"Notice how GOAL-SNOBOL4-RTX and GOAL-ICON-RTX are
proceding with replacing the C runtime with highly optimized register-aware ASM code. You do the same.
Join the coordination that is setup by the two, and y'all will be come three."*

**Ladder name:** `PL-RTX` — the **third** RTX ladder, running CONCURRENTLY with `GOAL-SNOBOL4-RTX.md`
(`SN4-RTX`), `GOAL-ICON-RTX.md` (`ICON-RTX`), and `GOAL-PROLOG-BB.md` (the ζ / PL-SINK ladder).

**Contract:** `ARCH-PROLOG-RTX.md` — read it before any rung. It does NOT restate step 0; it points at
`ARCH-SNOBOL4-RTX.md` §7, which is the shared checklist, and records only Prolog's deltas.

---

## ⛔⛔ SYMBOL OWNERSHIP IS NOT IN THIS FILE — IT IS IN `RTX-CLAIMS.md`

The runtime is SHARED (~20,000 lines, one `.so`, six languages). **Three** RTX ladders now work it.
Check a symbol OUT in that ledger — **and PUSH the claim before the work, not with it** — before writing
code. Run `CUR_SESSION=<n> bash scripts/util_rtx_claims.sh` at session start and session close.

⭐ **Prolog's advantage: its hot surface is almost entirely Prolog-EXCLUSIVE** (`rt_pl_dop_*`), so this
ladder can run for many sessions with **no arbitration against SN4-RTX or ICON-RTX at all.**
⛔ **Prolog's disadvantage, and it is the whole scope problem: its hot surface COLLIDES with its own BB
ladder's PL-SINK rungs.** See §SCOPE below. That collision, not inter-RTX contention, is this ladder's
governing constraint.

---

## ⛔ LIVE CURSOR — s225-PL (2026-07-30) — **ADDENDUM TO s224 BELOW, WHICH IT DOES *NOT* SUPERSEDE: THE s221 BOARD IS A FIFTH DIRECTORY, `benchmarks/prolog/bench/` (22 FILES), AND IT REPRODUCES 2,060,043 / 19-OF-22 TO THE DIGIT. PLCALL KILL-SWITCH GATE NOW PASSES ON PROLOG, BOTH MODES.**

SCRIP `8437c3d7` on origin + s224's local `440f7d6d` (**left untouched — another session's live work in a shared container**). RT_OPT=`-O0`. **Zero source edits s225.** Watermark re-proved at start: **Prolog 164/164 interp + 164/164 compile, FAIL=0.**
FINDING: `FINDING-2026-07-30-CLAUDE-PL-RTX-ITEM-0-VOIDED-THE-BOARD-RUNS-22-OF-22-IN-MODE-3-AND-THE-RANKING-REPRODUCES-TO-THE-DIGIT-THREE-FILES-ARE-NAMED-QUEENS.md`

⛔ **PRIORITY: s224 (below) STRUCK ITEM 0 FIRST, with the better method.** s225 reached it independently and **second**, in the same container, and claims none of s224's results. s225 discharges exactly one of s224's NEXT items — *"re-rank the s221 board with full-path+md5 keys"* — and adds three things:

1. ⭐⭐ **THE BOARD IS `benchmarks/prolog/bench/` — 22 files, 22/22 rc=0 in mode 3.** s224 measured `vanroy/` (**21** files) and *inferred* the match from reach (*"19/21 matches 19/22 exactly"*). No inference needed: census over all 22 of `bench/` gives **ENTRIES 2,060,043 · reach 19/22 · BAILED_C 0** — the s221 figures **to the digit**. ⇒ the board was measured in mode 3 from `bench/`; **item 0 is closed twice over, by two instruments.** ⇒ s224's four-directory census is really **five**. ⇒ **PERF VEHICLE: `bench/queensn.pl` = 1,596,708 arrivals = 78% of board traffic**, one rc=0 program.
2. ⭐ **SMALL CORRECTION TO s224(2)(a) — THREE files are named `queens.pl`, not two.** 430,081 belongs to **`bench/queens.pl`** (measured exactly), not `vanroy/queens.pl` — the latter is the **looped** wrapper s224 itself clocked at rc=124. s224's N=6-vs-N=16 explanation of the 33× **stands**; only the path label moves. ⭐ **The session that discovered basename-keyed measurement was itself off by one directory on a basename** — the sharpest possible case for its own owed FACT RULE (full path + `md5sum`, always).
3. ⭐ **`meta_qsort`'s "real banked defect" is PATH-SPECIFIC.** s224 banked `vanroy/meta_qsort.pl` rc=134 `rt_pl_cterm: island exhausted`. **`bench/meta_qsort.pl` ⇒ rc=0, 3,656 arrivals.** ⛔ Re-bank narrowly as *"exhausts the cterm island under the loop wrapper"* — **fourth consequence of the basename habit.**
4. ✅ **OWED ITEM DISCHARGED — PLCALL KILL-SWITCH GATE PASSES ON PROLOG.** s223 added the `EXT` param but never completed the sweep; it appears in no later cursor. `… PLCALL <bench> 4 both pl` ⇒ **m3 IDENTICAL=22 · m4 IDENTICAL=22 · MOVER=0 · QUARANTINE=0 · SKIP=0 · GATE PASS.** With s223's falsification probe, **RTX-1-PL's correctness case is closed.**

**NEXT (s224's three rulings still govern and are unchanged — see its NEXT below).** s225 adds only: re-key the board table by full path + `md5sum` now that the board directory is known; and if `bench/queensn.pl` is used for a 3-arm measurement, note it needs a PRISTINE rebuild (the `.so` in the tree is s224's).

**WATERMARK (s225):** `.github` = this addendum + FINDING + ledger inbox note. SCRIP/corpus = **untouched.** Per `RULES.md`, INCOMPLETE until `handoff_status.sh` prints HANDOFF COMPLETE.

---

## ⛔ LIVE CURSOR — s224-PL (2026-07-30): **⭐⭐⭐ ITEM 0 IS FALSE AND STRUCK. THE VAN ROY CORPUS RUNS 19/21 IN MODE 3. TWO LEDGER VERDICTS ARE FALSIFIED BY 5–6 ORDERS OF MAGNITUDE. THE LADDER'S REAL DEFECT IS BASENAME-KEYED MEASUREMENT, AND IT HAS NOW PRODUCED FOUR SEPARATE FALSE CLAIMS.**

SCRIP `440f7d6d` (local; PUSH OWED — see WATERMARK). RT_OPT=`-O0`. Watermark re-proven at session
start: **Prolog 164/164 interp + 164/164 compile, FAIL=0.**

⭐⭐ **(0) ITEM 0 (s223's #1 NEXT) IS FALSE — STRUCK.** *"The van Roy corpus does not execute in mode 3"*
is wrong. Measured with `scrip`'s OWN exit status: **19 of 21 `benchmarks/prolog/vanroy/*.pl` return
rc=0** with correct output. The two non-zero are `meta_qsort.pl` (rc=134 `rt_pl_cterm: island exhausted`
— ⛔ **CORRECTED BY s225: this is PATH-SPECIFIC, not a general defect — `bench/meta_qsort.pl` runs rc=0
with 3,656 arrivals. Bank it narrowly.**) and `queens.pl` (rc=**124** = my own 60 s `timeout`, *after* it printed the
correct 16-queens answer). **19/21 matches the s221 board's 19/22 reach exactly** ⇒ the ranking and the
grading instrument WERE always in the same mode. ⚠ **MY FIRST PASS AT THIS MEASUREMENT WAS ALSO WRONG**
and I caught it: I read `$?` after a pipeline, so `rc` was `tail`'s status and every program read rc=0.
**A pipeline destroys the exit status you are trying to measure.**

⭐⭐⭐ **(1) ROOT CAUSE OF ITEM 0, AND OF THREE OTHER FALSE CLAIMS: MEASUREMENT KEYED ON BASENAME.**
s223 ran `chat_parser`/`boyer`/`browse`/`crypt`/`derive` and reported rc=134 as a property of *"the van
Roy corpus."* Those files live in **`benchmarks/prolog/src/{swi-vanroy,gnu-examplespl}/`** — the
**PRISTINE UPSTREAM IMPORTS**, which carry **no entry-point harness** — not the adapted, runnable
`benchmarks/prolog/vanroy/` set. `chat_parser`/`boyer`/`browse` exist ONLY under `src/`. **PROVED with
the SAME basename:** `src/swi-vanroy/crypt.pl` ⇒ rc=134 `[IBB] FATAL: mode-3 driver: main BB graph not
found`, **0** harness directives; `vanroy/crypt.pl` ⇒ **rc=0**, correct output, **3** harness directives.
⛔ **`crypt.pl` and `derive.pl` each exist in FOUR directories.**
⇒ **FACT RULE OWED: A MEASUREMENT RECORDS THE FULL PATH + `md5sum`, NEVER THE BASENAME.** Four false
claims so far trace to this one habit: item 0; the 33× queens gap; and the two ledger verdicts in (2).

⭐⭐ **(2) ITEM (2) SOLVED, AND TWO SHARED-LEDGER VERDICTS FALSIFIED.**
**(a) The 12,957 vs 430,081 "33× disagreement" is two different files**, as s223 guessed — now proved:
`programs/prolog/queens.pl` md5 `c77a63aa…` is **N=6** (44 lines, the rung test, = 12,957);
**N=16 ⇒ 430,081 is `benchmarks/prolog/bench/queens.pl`.** N=6 vs N=16 backtracking search fully accounts
for 33×, and **no instrument was broken** — but ⛔⛔ **s225 CAUGHT ME COMMITTING THE EXACT DISEASE I WAS
DIAGNOSING: I attributed 430,081 to `vanroy/queens.pl`, which is the LOOPED wrapper I had myself clocked
at rc=124. THREE distinct files are named `queens.pl`. My N=6-vs-N=16 explanation stands; only the path
label moves. Writing the rule did not make me follow it.**
**(b) ⛔⛔ `RTX-CLAIMS.md` row `rt_call_arr_gen` reads `0` arrivals, `0/22` reach,
`NOT-A-TARGET:PHANTOM-BY-EXECUTION`. MEASURED THIS SESSION: 2,815,800 arrivals** on a validated rc=0
workload. **(c) ⛔ row `rt_arg_stage` reads `8` arrivals / `1/22` and `BLOCKED:MEASURED-ZERO`
(OUT: ICON-RTX). MEASURED: 812,824.** Both are **other ladders' rows — NOT EDITED**, filed to the
ledger inbox per discipline.

⭐⭐ **(3) THE SINK-FREE HOT SURFACE IS EMPTY — MEASURED, AND THAT IS THIS LADDER'S REAL BLOCKER.**
Full dynamic sweep on `rung10_programs_puzzle_19.pl` (rc=0, ~2.8 s): `rt_gen_spine_resume_enter`
**18,132,718** (already asm — ICON-RTX s214) · `rt_proc_call_open_det` **13,850,337** (RTX-1-PL ✅) ·
`rt_jmp_frame_lexprep2` **13,850,337** · `rt_pl_dop_trail_unwind` **13,702,135** (SINK-9 ⏳) ·
`rt_pl_dop_unwind_nothrow` **13,609,578** (SINK-9 ⏳) · `rt_call_arr_gen` **2,815,800** ·
`rt_pl_dop_unify` **1,775,371** · `rt_arg_stage` **812,824** · `rt_proc_set_*` **0–20** (startup only)
· `rt_pl_dop_trail_mark` **1** (confirms VESTIGIAL). ⇒ **every hot Prolog symbol is now ported,
SINK-claimed, or ledger-blocked.** ⛔ `rt_jmp_frame_lexprep2` is **13.85 M and exactly 1:1 with
`open_det`** but sits in the **DUAL-ENTRY cluster — "the highest-risk area on either ladder"** (it broke
Icon at HEAD for four sessions) and a port there is a **three-language event** ⇒ **I did NOT take it
unilaterally. It needs a ruling.**

⭐⭐⭐ **(4) THE RUNG I DID LAND IS NOT ASM, AND THAT IS THE FINDING.** `rt_call_arr_gen` is a **14-arm
`strcmp` chain with NO fast path** — 2,815,800 arrivals, and `rt_pl_between_gen` takes **2,815,800 =
100.0% of them, on the arm sitting 11th in the chain** ⇒ ~28 M failing `strcmp`s per run to reach one
destination. **`ARCH-PROLOG-RTX.md` hazard (a) does NOT apply, and the reason is measured, not argued:**
that hazard holds for the `dop` family because `rt_pl_dop_ax_*` **fast-path int×int and return BEFORE
the dispatch is entered**; here **the dispatch IS the entry.** Hoisting the hot arm to the head =
**one line of C**: warmed interleaved 5 rounds, medians, two `.so` arms swapped per round, base **2844**
→ hoist **2716** ⇒ **1.047×**, faster in **4/5**, and independently bracketed (28 M × ~5 ns ≈ 140 ms
predicted vs **128 ms** measured — the estimate and the stopwatch agree). ⇒ **THE DISPATCH COST WAS
REMOVABLE IN C. An asm port of this symbol would have claimed a win a one-line reorder already took;
its residual prize is call overhead only.** ⛔ **Generalized: on this ladder, MEASURE WHETHER C CAN TAKE
THE WIN BEFORE WRITING ASM — "replace C with asm" is a means, not the goal.**

⭐⭐⭐ **(5) THE SUCCESSOR RUNG IS EMITTER-SIDE AND DOMINATES ANY ASM PORT HERE.** `bb_call.cpp` **bakes
the callee name as a `.string` literal into the emitted code** (`.LbynamegenfnNN: .string "$between"`)
and passes `lea rdi, [rip + …]`. **The name is a COMPILE-TIME CONSTANT.** So 2.8 M crossings per program
run a by-name string dispatch to re-derive a fact the emitter already had; it could emit
`call rt_pl_between_gen` **directly**, deleting the dispatch AND one crossing rather than making it
cheaper. That is SINK-shaped, and it is the real prize.

⛔⛔ **(6) CONCURRENCY — TWO SESSIONS ARE ON THIS ONE GOAL FILE, AND I DUPLICATED WORK BECAUSE OF IT.**
`.github` HEAD advanced mid-session to **`4b1dd1b0` — `PL-RTX s225`** (parallel session, same ladder).
`RULES.md` sanctions parallel sessions **on DIFFERENT goal files**; two on `PL-RTX` is outside that.
**s225 had ALREADY struck item 0, already found the basename root cause, already identified the real
s221 board as `benchmarks/prolog/bench/` (22 files, 22/22 rc=0, reproducing 2,060,043 / 19-of-22 TO THE
DIGIT), and already completed the kill-switch sweep at m3 IDENTICAL=22 / m4 IDENTICAL=22.**
⇒ ✅ **My 6-program subset sweep is SUPERSEDED — cite s225's 22/22, not mine.**
⛔ **MY ERROR, AND IT COST MOST OF THIS SESSION'S BUDGET: I trusted this file's `LIVE CURSOR` (s223) and
never read `RTX-CLAIMS.md`'s MESSAGE BOARD, even though §SYMBOL OWNERSHIP tells me to check the ledger.
I ran `util_rtx_claims.sh` (the GATE) and mistook that for reading the LEDGER.** ⇒ **FACT RULE OWED:
ORIENTATION READS THE MESSAGE BOARD, NOT JUST THE GATE'S EXIT CODE. The gate reports rot; the board
reports WHAT OTHER SESSIONS ALREADY DID.**
⚠ **AND s225 DID NOT MOVE THIS CURSOR** — it committed a FINDING + one board line and left the header at
s223, which is `RULES.md` FACT RULE (b) firing **again**, in the very session that correctly lectured
three ladders about measurement discipline. **That omission is what routed me into duplicate work.**

**GATES (s224):** Prolog **164/164 interp + 164/164 compile** at the hoist. **No-regression proven
against a MEASURED baseline, not assumed:** Icon **251/12/30 identical** across all three modes base vs
hoist; SNOBOL4 identical, same single **pre-existing** `zb_arena_collection_grow` FAIL in both arms.
⛔ Ledger gate reports **BLOCKED — 3 fatal**, ALL PRE-EXISTING AND NONE PROLOG'S: `rt_defer_open` /
`rt_defer_close` (SN4-RTX, asm in `rtx_match.S`, rows not DONE — **now reported for the sixth session**)
and `rt_frame` (ICON-RTX ledger rot). Not my rows; not edited.

⚠ **s223's "PUSH BLOCKED, credential needed" BANNER WAS FALSE AT HEAD** — `ff6947e5` (RTX-1-PL) is on
origin, verified by `git log origin/main`. That is `RULES.md` FACT RULE (a) firing **again**, one session
after it was written. **VOIDED.**

**WATERMARK:** SCRIP `440f7d6d` **local, PUSH OWED (credential needed)** / corpus `<none>` / `.github`
this cursor + ledger inbox — **PUSH OWED.** Per RULES.md this handoff is **INCOMPLETE until
`handoff_status.sh` prints HANDOFF COMPLETE.**

**NEXT:** ⭐ **Three rulings are needed and this ladder cannot legally proceed on hot symbols without
them: (i) the §SCOPE ruling (unblocks `trail_unwind` 13.7 M + `unwind_nothrow` 13.6 M, the two biggest
remaining prizes, both SINK-9 ⏳); (ii) DUAL-ENTRY — may PL-RTX take `rt_jmp_frame_lexprep2` (13.85 M,
1:1 with `open_det`, three-language, highest-risk cluster)?; (iii) arbitration with ICON-RTX over
`rt_arg_stage`, whose `BLOCKED:MEASURED-ZERO` this session falsified at 812,824.** Unblocked meanwhile:
**(5) the emitter-side direct-call rung** (no ruling needed, dominates the asm port); **RTX-0d-PL** is
now substantially advanced (workload set validated: 19/21 van Roy + `puzzle_19` known-good);
**re-rank the s221 board with full-path+md5 keys** and re-audit every verdict derived from it.

---

## ⛔ SUPERSEDED — s223-PL CURSOR (retained for the corrections it recorded; items 0/6/7 now amended by s224 above)

SCRIP `b1ca896e` + this session. RT_OPT=`-O0`.
FINDING: `FINDING-2026-07-30-CLAUDE-PL-RTX-1-LANDED-GREEN-AND-VACUOUS-BY-VOLUME-AND-ALL-THREE-SHARED-RTX-INSTRUMENTS-FAIL-ON-PROLOG.md`

⛔⛔ **SAME-SESSION CORRECTION (supersedes items 6 and 7 below — newest at top):**
**(a) THE ARM CENSUS WAS NEVER BROKEN.** `chat_parser`/`boyer`/`browse`/`crypt`/`derive` exit **rc=134 with NO `LD_PRELOAD` at all** — `[IBB] FATAL: mode-3 driver: main BB graph not found`, **5 of 5 van Roy programs.** The census's own message *"check that the program runs at all"* was exactly right; I promoted a true report about the PROGRAM into a false accusation against the TOOL, for want of one command. **Item 7(c) is STRUCK; 7(a) and 7(b) stand.**
**(b) ITEM 6's PERF TABLE IS VOID — IT TIMED A CRASHING PROGRAM**, i.e. ~100% compile phase, so all three arms agreed to 1% by construction. ⭐⭐ **This is the ICON-RTX s220 compile-phase confound, on the exact family `ARCH-PROLOG-RTX.md` §2 warns is NOT covered by the `dop` zero-floor result** (*"Non-`dop` targets (`rt_proc_*`…) are not covered — re-measure per family"*) — **I wrote that caveat at s221 and walked into it at s223.** ⛔ And I shipped it INSIDE a correction of the cold-cache artifact: **fixing one confound is not evidence the number is clean.** ⇒ **verify rc==0 AND that the workload reaches the symbol BEFORE timing.**
**(c) ⭐⭐ THE REAL NUMBER — RTX-1-PL IS A WIN, NOT A NULL.** On `corpus/programs/prolog/rung10_programs_puzzle_19.pl` (rc=0, ~2.5 s): census **ENTRIES 13,850,337 / BAILED_C 0 / COMMITS 13,850,337** (≈1000× `queens.pl`); warmed interleaved 5 rounds, medians, `-O0`: PRISTINE **2557** · OFF **2536** · ON **2424** ⇒ **ON/PRISTINE ≈ 1.055×**, gate tax **1.008× ≈ nil**, ON fastest in **5/5 rounds**. ⚠ Under the ~1.10× trust floor, so it rests on four weak agreements not one strong claim: three arms, 5/5 direction, ~0 tax, and an arithmetic bracket (~10 instr × 13.85 M ≈ 139 M instr ≈ 2–4% of a 2.5 s `-O0` run). **"VACUOUS-BY-VOLUME" is WITHDRAWN.**
**(d) ⛔⛔ THE FINDING THAT OUTLIVES THE RUNG: THE VAN ROY CORPUS THIS LADDER'S WHOLE RANKING RESTS ON DOES NOT EXECUTE IN MODE 3.** s221 reports 2,060,043 arrivals across 19/22 of those programs, yet every RTX rung is graded through `--run` — **the ranking and the grading instrument are not in the same mode.** That is a defect one level above any rung and it is now item 0.

1. ⭐⭐ **RTX-1-PL IS ASSEMBLY.** `src/runtime/rtx/rtx_plcall.S`, family gate `PLCALL`, C body → `c_rt_proc_call_open_det`. **Three of four C levels absorbed ⇒ the success path has NO CALL:** `prologue_lex`'s `fbytes` is discarded by every caller on this path so its computation is ELIDED entirely; `rt_pcall_grow` inlined as a capacity compare with a cold out-of-line arm (hot path frameless); `rt_value_trail_mark` inlined as one load. `rt_pcall_grow` de-static'd → `visibility("hidden")` (the s187 `rt_nret_fix` precedent). Linkage split read from `rt.o`, never the `.so` (s209): 7 hidden globals rip-direct, 4 exported via `@GOTPCREL`. Every baked offset anchored by `_Static_assert` in the owning TU ⇒ **a struct move breaks the COMPILE, not the runtime.**
2. **GATES ALL GREEN.** Prolog watermark **164/164 interp + 164/164 compile at PRISTINE *and* at ON**. SNOBOL4 **7/0**, Icon **14/14 m3 + 14/14 m4** (cited as no-regression for the C-side de-static ONLY). Arm census `queens.pl`: ENTRIES **12,957** / BAILED_C **0** / COMMITS **12,957**.
3. ⭐⭐ **THE FALSIFICATION PROBE IS THE EVIDENCE, NOT THE GREENNESS** (§7 step 2b). Deliberately broken asm moves the Prolog battery **164/0 → 111/53 in BOTH modes** ⇒ the asm executes, coverage is **53/164 = 32 percent**, and **m4 is real evidence** — the s214 "never close on m3 alone" trap is discharged by measurement rather than assumed.
4. ⭐⭐ **s221 ITEM 8 / PROPOSED RTX-13-PL IS SETTLED AND WAS MISCONCEIVED.** `_det0…_det4` measure zero **not** because a `det_fuse` conjunct fails but because the hot sites **never evaluate `det_fuse` at all**: `bcps_spine_gen_arm` — whose own in-tree comment says every nondet Prolog predicate is dispatched there — has **no fused family and no fuse test**, only `gi_idx >= 0 ? rt_proc_call_open_det : rt_proc_call_open`. ⇒ the arity, `"$call/N"`-name and frame-regime hypotheses all have no referent. ⭐ **And it RAISES this rung: the generator arm calls the ported symbol directly BY INDEX, so RTX-1-PL is the live hot arm and cannot be mooted by any det-arm eligibility fix.** The real successor rung is "extend the fused family to the generator arm."
5. ⛔⛔ **I NEARLY REPORTED 3.4×.** `queens.pl` first read PRISTINE 204 ms → ON 60 ms. That was **entirely cold page-cache on whichever arm ran first.** Warmed and interleaved, the same program reads 53 / 51 / 52 ms. **Nothing but re-measuring caught it.** ⇒ never report a number from a non-interleaved loop; this is why the contract mandates the harness.
6. **THE HONEST NUMBER** (`chat_parser.pl` ~576 ms, 7 warmed interleaved rounds, medians, `RT_OPT=-O0`): PRISTINE **576** · OFF **583** · ON **569** ⇒ **ON/PRISTINE 1.01× = NULL**; kill-switch tax **0.99× ≈ 0**, so the port is **FREE TO KEEP**. Census reports only **12,957** arrivals on the `queens.pl` it can grade vs the board's **430,081** — a **33× disagreement**, most likely two different files both named `queens`. At ~13 k arrivals × ~10 instructions saved the port is invisible **by construction**.
7. ⛔⛔ **THE REAL BLOCKER — ALL THREE SHARED RTX INSTRUMENTS FAIL ON PROLOG, THREE DIFFERENT WAYS.** (a) `test_gate_rtx_killswitch_sets.sh` was hardcoded `*.sno` ⇒ **no Prolog and no Icon arm at all** — ✅ FIXED, added an `EXT` parameter (default `sno`, every existing invocation byte-unmoved); ⚠ the Prolog sweep was launched and **NOT COMPLETED**, still owed. (b) `bench_rtx_3arm.sh` requires a self-timed `ms:` window and **no Prolog program emits one** ⇒ it prints `NOT GRADED` for every program; item 6's table is hand-rolled wall clock and is labelled as such rather than dressed up as the harness's output. (c) `util_rtx_arm_census.sh` **SIGABRTs (rc=134) under `LD_PRELOAD` on the van Roy corpus** (`chat_parser`, `boyer` — 2 of 2 tried; it works on `corpus/programs/prolog/queens.pl`) ⇒ **the census cannot grade the corpus the s221 ranking was built from**, so the 2,060,043 board figure is single-instrument and item 6's 33× gap is unresolvable until this is fixed. ⇒ **RTX-1-PL's PERF claim is UNFALSIFIABLE; its CORRECTNESS claim is fully discharged. ⛔ Do NOT read the null as "the port does not help" — read it as "this tree cannot yet measure whether it helps."**

**WATERMARK:** SCRIP local commit (6 files) / corpus `<none>` / `.github` FINDING + this file + `RTX-CLAIMS.md` — **PUSH BLOCKED, credential needed.**

**NEXT:** ⭐ **(0) Establish which mode the s221 van Roy ranking was measured in — those 22 programs ABORT under `--run`, so the ranking and the grading instrument are not in the same mode. Re-rank on programs that execute if the counts do not transfer; `rung10_programs_puzzle_19.pl` is the first known-good member.** Then (1) complete `test_gate_rtx_killswitch_sets.sh PLCALL <prolog corpus> 4 both pl`; (2) name the exact file behind each of 12,957 and 430,081; (3) give `bench_rtx_3arm.sh` a Prolog timing arm (or self-time the Prolog benchmarks); (4) then rule on whether RTX-1-PL stays — note it is FREE to keep at a 0.99× tax; (5) the §SCOPE ruling is still open and still not blocking.

**BANKED (inherited from `GOAL-PROLOG-BB.md`, all still live):** `unary_not.sno` emits a `.string` from
uninitialised memory (poisons every `.s` byte-identity sweep); engine-wide silent-fail on undefined
predicates; int/float standard-order conflation; lexer escape three-site/two-behaviour; NO-LCO segfault;
nested-`\+` binding leak; `retractall/1` gaps.

---

## ⛔⛔ SCOPE — THE RULING THIS LADDER NEEDS FROM LON

Nine of the top eleven Prolog symbols are already-SINK'd or claimed by an **OPEN** PL-SINK rung in
`GOAL-PROLOG-BB.md`, which is a **concurrently running session**:

| RTX rank | symbol | corpus calls | reach | PL-SINK rung | SINK status | PL-RTX |
|---:|---|---:|---|---|---|---|
| 1 | `rt_pl_dop_trail_unwind` | 2,114,931 | 10/22 | **SINK-9** | ⏳ OPEN | ⛔ COLLISION |
| 2 | `rt_proc_call_open_det` | 2,060,043 | **19/22** | **none** | — | ✅ **CLEAR** |
| 3 | `rt_pl_dop_unify` | 1,108,786 | **22/22** | SINK-1 | ✅ s142 | ⚠ reduced |
| 4 | `rt_pl_dop_mkc` | 1,018,100 | 19/22 | SINK-3 | ✅ s145 | ⚠ reduced |
| 5 | `rt_pl_dop_cmp_ne` | 880,792 | 5/22 | **SINK-7** | ⏳ OPEN | ⛔ COLLISION |
| 6 | `rt_pl_dop_unwind_nothrow` | 873,060 | 16/22 | **SINK-9** | ⏳ OPEN | ⛔ COLLISION |
| 7 | `rt_pl_dop_is_v` | 735,898 | 14/22 | **SINK-5** | ⏳ OPEN | ⛔ COLLISION |
| 8 | `rt_pl_dop_ax_sub` | 731,498 | 12/22 | **SINK-6** | ⏳ OPEN | ⛔ COLLISION |
| 9 | `rt_pl_dop_unify_cs` | 622,812 | 12/22 | SINK-1 fam | ✅ | ⚠ reduced |
| 10 | `rt_pl_dop_ax_add` | 573,678 | 6/22 | **SINK-6** | ⏳ OPEN | ⛔ COLLISION |
| 11 | `rt_pl_dop_ix_g` | 289,004 | 15/22 | SINK-4 | ✅ s148, **kk==4 deferred** | ✅ deferred arm CLEAR |
| — | `rt_pl_dop_trail_mark` | **22** | 22/22 | SINK-8 | ✅ s146 | ⛔ **VESTIGIAL** |

**THE QUESTION.** When a Prolog symbol is hot and has an open SINK rung, does it get
**(a)** SINK (emitter inline fast path), **(b)** RTX (runtime body in asm), or
**(c)** SINK for the guarded fast arm **+ RTX for the arm SINK deliberately defers to C**?

⭐ **RECOMMENDED: (c)** — the only option under which both ladders keep working. SINK's inline path takes
the arrivals it guards, so **RTX's honest scope is the residue SINK refuses**, which is already
enumerated in `GOAL-PROLOG-BB.md`: SINK-4's `kk==4` per-site intern cache, SINK-7's out-of-2⁵³ range
arm, SINK-6's `div`/`idiv`/`mod` guard arms (`b==0`, `b==−1`) and any `DT_R`, SINK-5's non-`{I,R}` tags —
**plus every symbol with no SINK rung at all**, which is where rung 1 lives.
Under (a) this ladder has ~2 live rungs. Under (b) two concurrent sessions fight over one
emitter/runtime boundary per symbol, and per RULES.md concurrency that is safe for FILES and **not** safe
for a shared performance claim.

⛔ **UNTIL RULED: this ladder works ONLY symbols with no SINK rung, or SINK-deferred arms.** Rung 1
satisfies both.

---

## THE LADDER

### - [x] ✅ RUNG RTX-1-PL — `rt_proc_call_open_det` — **LANDED s223-PL. Green both modes, 12,957 commits / 0 bails, **~1.055× measured on 13.85 M arrivals / 0 bails** (see the SAME-SESSION CORRECTION atop the cursor; items 6-7 are superseded).**
**WHY IT IS FIRST, AND IT IS FIRST UNDER EVERY SCOPE OPTION:** rank **2** by execution (2,060,043),
rank **1 by REACH (19/22 programs — the broadest of any Prolog symbol)**, **no PL-SINK rung**, **not a
`dop`** so structurally outside SINK's `$op` territory, **Prolog-dominant** (5,291 static sites),
**absent from `RTX-CLAIMS.md` entirely**, and in the CALL family where SN4-RTX has already paid for the
lessons (`rt_proc_call_epilogue_γ/ω` are `DONE:SN4-RTX:881ea03d`).
⭐ **Its sibling `rt_proc_call_open` measures ZERO calls in 22/22 programs** despite 5,626 static sites —
**the `_det` variant takes the entire path, and only the dynamic sweep could show that.**

**STEP 0 STATUS — PARTIALLY DONE s221; THE REST IS OWED BEFORE ANY ASM:**
- [x] **0(a) live definition exists** — exported `T` in `out/libscrip_rt.so`.
- [x] **0(b) spelling round-trips** — taken from `nm -D --defined-only`, not from prose. ⚠ Note the
  neighbouring `rt_proc_call_epilogue_γ/ω` carry literal UTF-8 GREEK; **this symbol does not**, but any
  new sibling in the family must be taken as the tree spells it (RTX-4 s165 truncation class).
- [x] **0(d) executed + scales** — 13,226 → 52,901 at nrev N=25→100 (**4.00× exact**); 2,060,043
  corpus-wide across 19/22 programs. ⚠ **ZERO on `fib`** — per cursor item 5, that is a statement about
  `fib`, not about the symbol.
- [x] **0(e) not already assembly** — grep run **with `--include=*.S`** (the load-bearing flag, s200).
- [x] ✅ **0(c) DONE — AND IT FIRED. SLICE 0 LANDED (SCRIP `1f91a433`).** `nm out/rt_pic/rt.o` showed **three of the five things the port needs were `static` and unreferenceable from `.S`**: `g_rt_gen_procs` `b`, `g_rt_gen_proc_count` `b`, `g_pcall_cap` `b` — plus TWO `static` FUNCTIONS, `rt_proc_call_prologue_lex` `t` and `rt_pcall_grow` `t`. **The `.so` reported all of them fine**, exactly as s209 said it structurally must. Promoted the three globals to `visibility("hidden")` after checking **s214 axis 2 first** (zero template/emitter refs ⇒ not named in emitted mode-4 TEXT ⇒ `hidden` is safe); verified **absent from the dynamic table** after ⇒ direct `[rip+sym]`. Now all nine cluster globals are `B`/`D`. Gates: **Prolog 164/164 + 164/164 · SNOBOL4 7/0 · Icon 14/14 m3 + 14/14 m4**, all green, visibility-only change.
- [x] ✅ **0(f-pre) DONE — NOT straight-line, so 0(f) is NOT discharged in advance.** All six family members share one shape: two decline guards (`idx` range; `!p->fn || p->dyn_scope`) → optional `g_call_args` copies → **a call to `rt_proc_call_prologue_lex`** → `return p->fn`. ⭐ **COST DECOMPOSITION, and it is FAVOURABLE — the opposite of the RTX-4/`rt_make_list` shape:** the callee chain bottoms out in cheap, inlinable work. `rt_proc_call_prologue_lex` is ~12 stores + 2 increments + `fbytes` arithmetic **whose result every caller DISCARDS via `(void)`** ⇒ dead work on this path. Its one call, `rt_pcall_grow`, is **`if (g_pcall_top < g_pcall_cap) return;`** — a capacity guard whose common case returns immediately ⇒ the ideal inline-with-bail arm. Its other call, `rt_value_trail_mark`, is **`{ return g_pl_trail.top; }`** — one global load. ⇒ **the entire cluster can be absorbed with NO call remaining in the success path.** Absorbing a `static` callee into a gated wrapper's asm is precedented TWICE (s211 `rt_parse_num_d`, s216 `data_field_ptr`) and needs no contract amendment.
- [x] ✅ **0(g) DONE — THE LIVE ARM IS THE GENERIC FORM, AND THE "OPTIMIZED" ARMS ARE DEAD.** `bb_call_proc_staged.cpp` emits a THREE-TIER ladder: (1) **PL-DC** direct `call proc_X_dcα` (no open crossing at all, gated `rt_pl_dc_ok`), (2) **fused `rt_proc_call_open_detN`** (≤4 args, `ZC_FRAME_RSP`), (3) **classic generic `rt_proc_call_open_det`**. ⭐⭐ **MEASURED on `queens.pl`: generic `_det` = 430,081 · `_det0`…`_det4` = ZERO, all five.** ⇒ **porting the generic form ports the live arm.** ⛔ **AND THE WHOLE PL-REGAIN-4 FUSED FAMILY IS DEAD ON THE HOTTEST PROLOG PROGRAM** — it exists to collapse `{rt_arg_stage × nargs + open_det}` into one crossing, and `rt_arg_stage` independently measures **8 calls across 22 programs**. Since `dc` requires `det_fuse`, **PL-DC is dead here too.** ⇒ **an entire shipped two-rung optimization pair is bypassed on the hot path, and only the dynamic sweep could show it.** ⚠ **OWED: WHY `det_fuse` is false for Prolog's hot sites** (`det_idx < 0` / frame regime / `nargs > 4`) — Prolog carries 5,291 static `_det` sites, so if the fused arm can be made to fire that may outrank the asm port entirely. **Measure before porting: this is a possible RTX-13-PL (fix the eligibility) that would beat RTX-1-PL.**
- [ ] ⛔ **REMAINING 0(c) for the port itself:** `rt.o`, not
  `libscrip_rt.so`: `B`/`D` = linkable, `b`/`d` = `static` and **unreferenceable from `.S`** (s209 —
  the `.so` is structurally incapable of separating `static` from `visibility("hidden")`).
  ⛔ **AND s214's second axis:** if any such global is ALSO named by a template in emitted mode-4 TEXT it
  must stay **DYNAMICALLY EXPORTED**, and then every `.so`-internal access must become `@GOTPCREL` or a
  `-no-pie` copy relocation silently makes it a DIFFERENT VARIABLE.
- [ ] ⛔ **0(f-pre) READ THE C BODY AND ENUMERATE ITS ARMS.** If it is straight-line (no arm, no call, no
  early return) then entries==commits by construction and 0(f) is discharged before the asm exists
  (s217). Otherwise the ported arm's liveness must be established.
- [ ] ⛔ **0(g) READ THE EMITTING TEMPLATE FIRST (s211-ICN, and Prolog is the language where this bites
  hardest).** Grep the `bb_*.cpp` that emits the call for an inline `cmp`/`je` tag guard. **PL-SINK is
  an entire ladder of exactly such guards** — cursor item 1 is what happens when one lands. If a guard
  steers arrivals away from the arm I intend to port, **port the arm the guard REJECTS**, or refuse.
- [ ] Then, and only then: port behind gate `SCRIP_RTX_PLCALL`, C body → `c_rt_proc_call_open_det`.

**GATES OWED AT LANDING:** Prolog `test_prolog_rung_suite.sh` **164/164 + 164/164** (the watermark
established this session) · SNOBOL4 + Icon batteries as **no-regression only** (⛔ per
`ARCH-SNOBOL4-RTX.md` §7 step 2b, **an unmoved battery may NOT be cited as evidence the asm executes**) ·
`util_rtx_arm_census.sh` with `COMMITS > 0` · `test_gate_rtx_killswitch_sets.sh PLCALL` (N≥4 per arm,
hash SETS — the s217/s219 correction) · 3-arm `bench_rtx_3arm.sh` reporting **ON/PRISTINE** as the answer.

### - [ ] RUNG RTX-2-PL — the SINK-deferred arms (scope option (c) only)
Enumerated residue the SINK ladder explicitly leaves in C: SINK-4 `kk==4` (per-site intern cache),
SINK-7 out-of-2⁵³ range (the double-compare trap — `cvtsi2sd`/`comisd`, and `x86_asm.h` has only ~12 xmm
hits so **verify the encoder forms exist for BOTH media before choosing**), SINK-6 `div`/`idiv`/`mod`
guards (`b==0`, `b==−1` — `INT_MIN/−1` traps on x86) and any `DT_R`, SINK-5 non-`{I,R}` tags.
⛔ **Do not open before the §SCOPE ruling.**

### - [ ] RUNG RTX-0d-PL — extend the workload set beyond two backtracking programs
Cursor item 6: `queensn`+`queens` are ~78% of arrivals. The ranking needs list/arith/IO-shaped run-phase
workloads before any rung is prioritised **on rank alone**. ⚠ Mirrors ICON-RTX's RTX-21-ICN exactly.

### - [ ] RUNG RTX-12-PL — eradication (LAST)
Delete gate + `c_*` body. ⛔ Cross-language per ledger hard rule 4: requires **all three** watermarks
green and every beneficiary row `DONE`.

---

## ARCHITECTURE NOTE — WHY PROLOG'S SURFACE LOOKS DIFFERENT

Prolog's hot symbols are `rt_pl_dop_*`: the runtime sinks for lowered `$op` nodes emitted by
`lower_prolog.c` through the four-port (α/β/γ/ω, δ/ε) BB machine documented in `GOAL-PROLOG-BB.md`.
They are **emitted-code-only** — the compile phase never calls them (cursor item 4) — which is why
Prolog's absolute dynamic counts are already run-phase counts and why its surface is the largest of the
three languages (**112 distinct symbols** vs Icon's 90 and SNOBOL4's 54) while being almost entirely
uncontested.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
