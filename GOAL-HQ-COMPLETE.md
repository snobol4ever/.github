# ⛔⭐⭐⭐⭐ GOAL-HQ-COMPLETE — HEADQUARTERS FOR **CORRECTNESS**

**Opened 2026-08-22 s256 by Lon, in-chat, verbatim in substance:** *"we will need to split HQ into TWO parts. One responsible for CORRECTNESS of (SNOBOL4, Icon, and Prolog) with SNOBOL4 being #1, Icon #2, and Prolog #3."*

**Seat root:** `/home/claude_C` · **postoffice identity:** `hq_C` · **twin:** `GOAL-HQ-PERFORM.md` (`/home/claude_P`, `hq_P`)

## THE ONE QUESTION THIS HQ OWNS

**Does it produce the right answer?** Nothing else. Speed belongs to `hq_P` and is not this seat's business even when it is staring at a slow correct program.

| | |
|---|---|
| **priority** | **SNOBOL4 #1 · Icon #2 · Prolog #3** — in that order, always |
| **instrument** | **oracle diff.** `x64/bin/sbl -bf` for SNOBOL4/Snocone (⛔ `-bf` ALWAYS, s189 — folding manufactures phantom duplicate labels); Arizona `icont`/`iconx` for Icon; GNU/SWI-Prolog for Prolog |
| **verdict** | byte-identical to the oracle, or **named RED with a witness**. There is no third state |
| **flagship** | **beauty self-host = the fixed point** — output byte-identical to `beauty.sno` itself (Lon s117; all md5 pins VOID, the checked-in file is its own oracle) |

## ⛔⛔⛔ THE LAW BOTH HQs SHARE: **YOU MEASURE *AND* YOU CURE**

⭐ **Lon s259:** *"… Tag you are it. Did I mention you are in DUO mode. I do not want to here about you not fixing the bugs. You will measure. You will cure."* Build, run, diff, bisect, profile — and when a measurement becomes a **defect, fix it**.

⛔ The s256 delegate-only rule this replaced was written for an HQ commanding 16 seats, and its own test was *"does this end in a brief in a seat's inbox?"* **In DUO there is no inbox to end in** — held literally it guaranteed nothing was ever fixed. ⭐ The bug stops with the seat that finds it. The one-line test: **did this turn change the CODE, or only the record?** See § DUO MODE below.


## ⛔⛔⛔ RUNG C-0 — **PARKED BY LON s258** (was "STILL OPEN"). CURED AT `-O0`, BROKEN AT `-O1` **AND** `-O2` (measured 2026-08-22, hq_C)

⛔ **PARKED, NOT SOLVED, AND NOT TO BE WORKED:** both culprits (`c_rt_cap_open`, `rt_call_proc_descr`) are C runtime slated for ASM replacement. **Reaffirmed by Lon 2026-08-23 s261, verbatim: *"Do NOT fix -O2 bug for BEAUTY. Do not care. Next."*** ⭐ The heading said STILL OPEN for three sessions after it was parked; the body below is kept because its measurements are sound and whoever writes that ASM needs them.

⛔⛔ **LON CALLED THIS FROM MEMORY AND HE WAS RIGHT** — in-chat: *"The problem as I remember was with -O2 and beauty self host did not work."* **MEASURED AT `3f951354`:**

| arm | `-O0` | `-O2` |
|---|---|---|
| m3 | ✅ 40,971 / `6f1671c0` FIXED POINT | ⛔ **278 / `1c75f97d`** |
| m4 | ✅ 40,971 / `6f1671c0` FIXED POINT | ⛔ **278 / `1c75f97d`** |

⭐⭐ **AND IT IS NOT AN `-O2` PROBLEM AT ALL — `-O1` FAILS IDENTICALLY.** Measured immediately after: `RT_OPT="-O1 …"` → **278 bytes, md5 `1c75f97d`**, the same output. So the boundary is `-O0` → `-O1`, not `-O1` → `-O2`, and the culprit lives in the **much smaller `-O1` pass set**. ⛔ Everyone has been calling this "the -O2 problem" — including the row name `161-o2-red` — and that framing is wrong and was narrowing the search to the wrong pass set.

| RT_OPT | m3 | verdict |
|---|---|---|
| `-O0` | 40,971 / `6f1671c0` | ✅ FIXED POINT |
| **`-O1`** | **278 / `1c75f97d`** | ⛔ BROKEN |
| **`-O2`** | **278 / `1c75f97d`** | ⛔ BROKEN |

⭐ **The `-O2` output is BYTE-IDENTICAL to the PRE-CURE `-O0` output** — the same failure, not a similar one. `6ba28e5e` cures the 32-bit-tag-compare class at `-O0` and NOT at `-O2`, matching `161-o2-red`'s note *"asm RT_OPT-independent; wound is runtime C under optimization."* `m3 ≡ m4` still holds **within** each arm: this is an optimisation-level split, not a medium split. **⛔ DO NOT BENCHMARK BEAUTY AT `-O2` — it quits after its header and will time gloriously.**

⛔ **HQ ERROR TO LEARN FROM:** one arm of a two-arm axis was measured and reported without the axis. Every number was true; the SCOPE was missing, and a true number with a missing scope reads as a general claim. Cost and blindness were the same defect — nobody re-ran `-O2` because it cost 9m30 and was discarded on every switch. Now 0–1s (flag-keyed build cache, SCRIP `6c3f081c`).

**The 278-byte stub was real, is reproducible, and is cured at `-O0`.** Measured at HEAD `457dc5d9`, pinned classic source, run from the beauty directory:

| tree | arm | bytes | md5 | verdict |
|---|---|---|---|---|
| `cd13321e^` **and** `cd13321e` | m3 | **278** | `1c75f97d…` | ⛔ Parse Error on START |
| `457dc5d9` (HEAD) | m3 | **40,971** | `6f1671c0757729992ae01a6bdf16f081` | ✅ FIXED POINT |
| `457dc5d9` (HEAD) | m4 | **40,971** | `6f1671c0757729992ae01a6bdf16f081` | ✅ FIXED POINT |

**m3 ≡ m4 holds; the DESIGN-INVARIANT violation is closed.** The live *converted* beauty (41,492 B) also self-hosts to its own fixed point.

**⭐ THE CURE IS `6ba28e5e`** (*"descr-stamp-asm-mints: … **two latent 32-bit-tag-compare defects found and fixed**"*), named by `git bisect run` over the repaired inverted probe. **HQ's hypothesis was right about the MECHANISM, wrong about the COMMIT:** it named mixed-width reads of the split `DESCR_t` tag word, and "32-bit-tag-compare" is exactly that class — but `cd13321e` (narrow three `DT_NOTSTR_MASK` tests) was **necessary and not sufficient**; `6ba28e5e` fixed two *further* latent tag compares and that is where beauty returns. Neither seat knew they had closed Milestone 1.

```bash
bash .github/probes/m1-bisect/check_m1_fixedpoint.sh both     # exit 0 at HEAD — this IS the M1 DONE-WHEN
```

⛔ **HQ'S OWN PRIME SUSPECT IS DISPROVEN, and is recorded rather than deleted so nobody re-derives it.** The mixed-width `DT_NOTSTR_MASK` hypothesis (`62017f8a` split `DTYPE_t v`, bits 8–31 stopped belonging to `v`, a string test reads as not-a-string) made `cd13321e rung-descr-stamp-notstr-mask` the obvious cure. **It is not:** `cd13321e` emits 278 bytes, byte-identical to its parent. The narrowing may still be correct work; what is false is that it cured C-0.

⛔⛔ **AND THE INSTRUMENT BUILT TO CHASE C-0 WAS ITSELF BLIND — this is the transferable half.** `beauty.sno` pulls **16 `-INCLUDE` files resolved against the working directory**. Run the pinned source anywhere but the beauty dir and every arm emits **zero bytes** (`cannot open include 'global.inc'`). seat01 caught a first corruption in the HQ-spec probe and fixed it correctly; the corrected probe kept the same defect through a different door, and its own smoke test recorded *"reads BAD as expected (rc=1, empty output)"* — when the real symptom is **278 bytes**, not 0. A `git bisect run` over it would have marked **every** commit BAD and converged, fast and confidently, on nothing. ⭐ **"BAD as expected" is not a measurement — it is a prediction that matched a number nobody compared. A probe must assert the SHAPE of the failure it expects, not merely its polarity.**

Full receipts: `FINDING-2026-08-22-hq_C-rung-C-0-milestone-1-is-not-regressed-at-head-the-board-is-stale.md`. Instruments (rescued from a seat's `/tmp`, made portable, negative-tested): `.github/probes/m1-bisect/`.

## THE STANDING CORRECTNESS BOARD

| front | state (measured by hq_C at HEAD `457dc5d9`, 2026-08-22) |
|---|---|
| **SNOBOL4 #1** | ✅ **M1 fixed point HOLDS in both media** (C-0 closed above). **Corpus baseline, measured here — cite this or measure your own:** `m3 PASS=357 FAIL=2` · `m4 PASS=355 FAIL=2 SKIP=2` (**359 total**). ⛔ The old `339/341` AND seat3's `320/321` are both stale — the denominator is 359. Reds: `160_pat_alt_inner_gen_resume` (standing, both modes, now a row) · `demo_treebank` (deliberate) · `132_pat_fence_eps_recur_shallow` (compile SKIP) · **`demo_porter` (compile SKIP — seat13's m4 duplicate-label defect, corpus-visible, now a row)**. Receipt: `bash scripts/test_corpus_snobol4.sh`. |
| **Icon #2** | Oracles **ABSENT** — `command -v icont iconx` returns nothing. ⛔ An Icon board run here grades against nothing and prints plausible red. seat08's rung-A2 register-liveness analysis is complete and banked, and is HELD, not lost. |
| **Prolog #3** | Oracles **ABSENT** — no `swipl`, no `gprolog`. Same rule: no oracle, no verdict. |

⛔ **RULING OWED BY LON, ASKED AND STILL UNANSWERED:** SNOBOL4-FIRST says *do not even run* the Icon/Prolog checks, while the s255 bootstrap ruling puts them on the road. HQ reads that as a SEQUENCE, not a contradiction — **that is HQ's reading, not Lon's word. Confirm before staffing Icon or Prolog.**

## OPEN CORRECTNESS ROWS ALREADY ROOT-CAUSED (landing jobs, not investigations)

- **`rung-arbno-selfloop`** (seat11) — `lower_snobol4.c:1463` takes `g->all[before_i]` as a resume target unconditionally; for a parenthesised group that first node is `sno_seq_nary`'s own sentinel GOTO, and the scan closes with `S->γ = succ` where `succ` **is** the assign node. Cycle closed by construction. **Two-site class** — `TT_CAPT_COND_ASGN` has byte-identical lines at `:1439-1442`, and no probe covers `.` .
- **`json-alternate-af-spin`** (seat13) — seat04 root-caused it to FLAT-mode choice-record rsp drift; HQ answered the `blob_choice_rbp_scan` FENCE question (the exclusion is **empirical, not load-bearing**: measured `fn=1` on both cures, so the choice-node COUNT alone separates cure from crash). ⛔ But an explicit warning applies: the two ALT admissions answer different questions and **must not be merged**.
- **`breakx-no-extend-runaway`** — checked in RED, ⛔ run only under `timeout` with stdout redirected (9.5M lines).

## ⛔ THE THREE TRAPS THAT FIRED ON THE OLD HQ TODAY

1. **A DONE-WHEN that can never say YES** (`free-r10`/`free-r11` — read the rung it FEEDS before judging a rung).
2. **Wall clock on a loaded machine** (belongs to `hq_P`, but the discipline is shared: verify before quoting).
3. **Measuring a broken program** (C-0 above).

⭐ Generalise: **if doing nothing passes, it is not a check; if nothing can make it pass, it is not a criterion either.**

## SESSION SETUP

```bash
cd /home/claude_C && for r in SCRIP corpus .github; do git -C $r fetch -q origin && git -C $r merge --ff-only origin/main; done
bash SCRIP/scripts/s4e_msg.sh check          # hq_C inbox
ls x64/bin/sbl /home/resources/spitbol-clean/sbl; command -v icont iconx swipl gprolog   # ORACLE PREFLIGHT — absent oracle = false red
cd SCRIP && make pristine                    # HQ-27: required before any gate verdict
```

## ⛔⭐⭐⭐⭐ TWO MODES. **DEFAULT = DUO.** MEASURE **AND** CURE. (Lon s259)

**Lon, verbatim:** *"There are two modes and you better know which mode you are in. And the DEFAULT is DUO mode. You know why. We'll probably NEVER be in FLEET mode because you can barely handle yourself much less 16 FLEET worker."*

| | **DUO — THE DEFAULT** | **FLEET — exceptional** |
|---|---|---|
| who exists | Lon watching · `hq_C` · `hq_P` · `ceo` | + 16 seat workers |
| who does the work | ⭐ **the two HQs, themselves** | HQs dispatch, seats execute |
| a bug you find | ⭐ **you fix it** | a row + a brief |
| entered by | **assume it** | only when Lon says so explicitly |

### ⛔⛔⛔ YOU MEASURE **AND** YOU CURE

**Lon:** *"… Tag you are it. Did I mention you are in DUO mode. I do not want to here about you not fixing the bugs. You will measure. You will cure."*

⭐ **"Tag you are it": the bug stops with the seat that finds it.** Earlier this file recorded the revocation as *"HQ's reading, marked as such"* — that hedge is now void. Lon has said it outright, twice. Mirrored into `CLAUDE.md`'s MODES section (which is UNVERSIONED — this root is not a git repo — so **this file is the durable copy**).

## ⛔⛔⛔ DUO MODE — THE OPERATING RULE FOR THIS SEAT. READ IT BEFORE ANYTHING ELSE.

**There are exactly TWO sessions: `hq_C` (me, correctness) and `hq_P` (performance). No seats. No fleet. No CEO running.**

⛔ **I DO THE WORK MYSELF. The deliverable is a FIX, not an artifact about a fix.**

**The failure mode this seat keeps repeating, named so it can be caught:** converting work into *reports* — a row, a FINDING, a message, a measurement — and calling that progress. That is HQ behaviour and there is no fleet to receive it. Lon, s258, after the fourth instance: *"You asked permission to do your job that I asked you."* and *"All day to just use another scratch register?"*

**The five rules, each inverting a mistake made today:**
1. **A question from Lon IS an assignment.** He asked "did we rid ourselves of r10/r11" twice; I answered twice with a measurement and moved on. Asking again is not curiosity, it is escalation.
2. **NEVER ask permission for work already asked for.** I found `free-r11` held by a seat that does not exist and said *"say the word and I'll reclaim it."* There is no word coming. Reclaim it.
3. **I CURE.** The delegate-only rule's whole basis was a fleet that learns from briefs. There is no learner.
4. **A row is a note to my future self, not a handoff.** Minting a baton and moving on = the work did not happen.
5. **Never block on CEO.** It has never run this session. Route decisions there and *keep going*.

⭐ **The test, one line: did this turn change the CODE, or only the record?** If only the record, it was not work.

## ⛔⭐⭐⭐ STANDING ORDER CHANGE — DUO ONLY, NO FLEET (Lon, in-chat, 2026-08-22 s258)

**Lon, verbatim in substance:** *"Just so we are clear we are run only duo here, no FLEET, just 2 HQ's."*

**hq_C and hq_P are the only sessions running. There are no seats.** What this changes, and it is most of the operating model:

1. ⭐ **HQ CURES NOW.** The delegate-only rule's stated reason was *"a fix taken at HQ is a fix the fleet did not learn."* With no fleet there is no learner, and the law would mean **nothing gets fixed at all**. Lon has already put this seat in a curing role in the same session (*"Fix that BUILD problem"*), which is the reading in practice. ⛔ This is HQ's reading of two Lon statements, not a third Lon statement — it is marked as such, and Lon can overturn it in one line.
2. **The batons are a two-person worklist, not a dispatch queue.** `/home/resources/postoffice/tasks/*.task.md` keep their full value — GOAL, a DONE-WHEN that is a command, QA and an evidence LEDGER — but nobody is coming to pick them up. hq_C works them directly, newest evidence appended as before.
3. **All 7 seat assignments have been RELEASED** (`claims.released.hq_C-s258-duo/`). ⛔ This was not cosmetic: a claimed row **hides itself from the picker**, so leaving work assigned to a seat that is not running would have fenced it off from the only two sessions that exist.
4. ⛔ **CORRECTED BY LON THE SAME SESSION — THE FLEET PROTOCOL IS NOT DORMANT, IT IS THE ENABLER.** hq_C had written the control plane off as "dormant, no further investment" on hearing "duo only". Lon, in-chat: *"I am saying get the FLEET protocol working, or we can not blast development later"* and *"We will be doing massive work on Icon and Prolog etc as we go. We want the system working."* So the duo is the CURRENT staffing, not the destination: the fleet returns for the Icon/Prolog work, and the protocol must be finished and proven BEFORE it does. ⭐ Outstanding, in priority order: **V2-5 gate honesty** (31 of 105 gates cannot say NO — at 16 seats that closes rows on false green at scale, and LAW 1's DONE-WHEN rule depends on it), **V2-2 queue-as-index** (11 of 77 live rows converted to batons; rows still carry multi-KB prose), then V2-6 (Lon's flip; `PROTOCOL-V2-DRAFT.md` is staged and structurally complete).
5. **Escalation is unchanged:** hq_C ↔ hq_P directly, `ceo` for arbitration, Lon overrides anyone.

## LIVE CURSOR — hq_C

**s265 (2026-08-23) — LON ORDERED THE BENCHMARK HARNESS INVERTED, AND IT IS INVERTED. DUO.**

### ⭐ THE ORDER, VERBATIM IN SUBSTANCE

*"the system does NOT have the stand alone program and has all that WRAPPER actually in the SOURCE CODE. And there is NO REF files. So REVAMP the benchmark harness to have the `*.sno` file look like and BE the REAL program application that can be run stand alone, and you can make temporary versions you build on the fly with WHATEVER WRAPPERs you need."* · *"Do not use the HUGE files for the REF files. Use the INPUT versions which are small for that reason."* · *"we should have three options I would think."*

### DONE — SCRIP `a0ebc660`, corpus `90dbbb895`, both pushed

| | before | **after** |
|---|---|---|
| benchmark `.sno` | the wrapper: `ZBODY(ZKN)` + `-INCLUDE 'harness.inc'`, **no `END`**, not runnable standalone | the **application**: own `END`, own real output, no include, runs under `scrip` / `sbl -bf` / csnobol4 |
| `.ref` | 16 pinned `check: <n>` (a harness artifact) · **2 had none at all** | **33/33** minted from `sbl -bf` on the SMALL `.input`, verified m3 **and** m4 |
| the wrapper | baked into the source, one shape | `scripts/bench_wrap.sh` builds it on the fly, **three modes** |
| scorecard `benchmarks` | 17/17 on `check:` lines, `norm=ms` | **18/18 m3 · 18/18 m4 · 100.0%** on real output, norm dropped |

**Three options, as ruled: STANDALONE** (no wrapper — `perf`/`time`/callgrind the real app, graded while timed) · **`--mode=time`** (budget, count iterations) · **`--mode=iter --n=N`** (exact count, no deadline).

⭐ **MODE 3 WAS UNREACHABLE FOR EVERY DATA-DRIVEN BENCHMARK AND NOBODY HAD SAID SO.** The fixed-work gate was `fixed_n = INPUT`, a stdin read — but porter/json/claws5/calculator/treebank read their *corpus* from stdin, so it could never see a count. They were time-based-only by construction. `bench_wrap.sh` **bakes** `fixed_n`, which is what makes instruction-counting reachable on exactly the two rows hq_P is profiling. Told hq_P; they had hit it independently and hand-built the same workaround.

### ⛔ THE CORRECTNESS DEFECT IT UNCOVERED — CURED

**`DATATYPE()` upper-cased programmer-defined type names.** `DATATYPE(jobj(...))` → `JOBJ` where the `-bf` oracle says `jobj`; `MiXeD` → `MIXED`. Root cause `by_name_dispatch.c:5202`: the fold was applied to the WHOLE result — right for the built-in spellings the function stores lowercase internally, wrong for a name the user declared in a `DATA` prototype. It also truncated names past 31 chars through a `static char ub[32]`. Cured at the single site; m3 and m4 byte-identical to the oracle.

### ⭐⭐ THE RUNG THAT OUTLIVES THIS SESSION — **A `.ref` MINTED AGAINST THE WRONG ORACLE ARM AGREES WITH THE BUG FOREVER**

`corpus/programs/snobol4/demo/json.ref` pinned `root=JOBJ` — minted against `sbl -b` (folding ON), the arm **s189 outlawed**. So the pin agreed with SCRIP's bug, the demos suite graded green, and every instrument aimed at it was blind. It was not found by grading. It was found by **re-deriving the pin from the correct authority and diffing.** ⛔ **Any pin older than s189 is suspect by construction** — sweep unminted, needs a row. hq_P recorded the identical rung independently and, against their own interest, that the two values sat side by side in their own transcript unread: *"printing two things is not diffing them."*

### GATES, PRISTINE, ON THE MERGED TREE (after rebasing onto seat02's `3e4591fe`)

corpus **m3 359/360 · m4 359/360 SKIP=0** — only `demo_treebank` (seat03, deliberate). ⭐ The m4 SKIP is **gone**: seat02's `132_pat_fence_eps_recur_shallow` link fix landed. Both emit gates rc=0.

### OPEN, WITH OWNERS

- ✅ **`deferred-indirect-capture-target` — CURED s265. `P . *(...)` WORKS.** Lon's word for it is the right one: an **enhancement**, not a regression — it never worked, so there was nothing to bisect. Both arms now byte-identical to `sbl -bf` in m3 AND m4, including the `$` immediate arm that was **silently dropping the assignment**. ⭐ The cure is a compile-time carrier, not a runtime test: a name string and an ordinary string are the same bytes at run time, so the strict gate must stay strict (it is what correctly fails `. *("dum" "my")`) and the LOWERER carries the fact instead — an `EXPRNM$` thunk that lowers the INNER expression and returns the name string. ⛔ Chosen over the `"*$"` prefix this FINDING originally proposed: three OTHER sites decode that same `*` for deferred PATTERN evaluation and would have broken; a distinct thunk NAME changed **one** site instead of six. ⛔ A regression was caught in flight — the first dedup guard excluded every `want_name` entry and cost `140`/`141_pat_eval_double_fn` (−2); only `EXPRNM$` thunks lower differently. **The broad guard looks more conservative and is the one that breaks things.** This unblocks the Λ/λ INLINE arm. *(superseded, kept for the two reverted attempts:)* `p = "HELLO" . *$("dummy")`: oracle matches and assigns, SCRIP fails the match. ⭐ **And the arm nobody reported is worse** — with `$` instead of `.` SCRIP *succeeds and silently drops the assignment.* Mechanism confirmed by trace to four hops: `lower_snobol4.c:1494/1518` route only `TT_FNC`-with-args to the name-wanting collector, and — the root — `sx_lower`'s `TT_INDIRECT` arm (`:377`) emits `IR_DEREF` **unconditionally**, so the thunk can never yield a name no matter what `want_name` says. Two cures were built, measured and **REVERTED** (the compiler is untouched): marking `want_name` alone changes nothing; routing the thunk through `SNO$NRET` dangles on a `RETURN` landing thunk graphs do not have. ⛔ The right design — a `"*$"` prefix carrying the compile-time fact — must teach **4 sites in `pattern_match.c` + 2 templates**, so it is its own session, not a tail-end edit. Witnesses committed with oracle refs at `corpus/probe/deferred_indirect_target/`. Evidence: `FINDING-2026-08-23-hq_C-deferred-indirect-capture-target-never-yields-a-name.md`. ⭐ The NRETURN-function arm PASSES today, so a lambda lowered that way is not blocked.
- `json-match-capture-free-hang` — FREE. Still the only benchmark red: 31/33 pass both modes, these 2 TIMEOUT. Untouched by this work.
- ✅ **`&CASE` defaulted to the FOLDING oracle arm — CURED s265.** `keywords.c:102` gave `&CASE` a default of **1**; `sbl -bf` says **0** and `sbl -b` says 1. SCRIP was matching the arm s189 outlawed — and contradicting itself, because `core.c:2451` already refuses writes with the words *"&CASE is read-only; SCRIP is case-sensitive only"*. Announcing folding on read, denying it on write. Zero behavioural risk (`kwb_own[0]` is read by nothing); all six keyword defaults now byte-identical, and the WRITE path already matched the oracle exactly. ⭐ **Found by seat03 in the `other-diff` bucket the sweep's first version dismissed by name** — same class as the DATATYPE fold but a **digit, not a letter**, so a case-only detector structurally cannot see it. It needed someone to read the diffs. `probe/kw/kw_defaults.ref` and `kw_direct_read.ref` re-minted (they pinned 1, and SCRIP emitted 1 live — the pin agreed with the runtime defect, exactly the `json.ref` shape again).
- ✅ **the fleet dispatcher had two missing mechanisms — BOTH LANDED s265.** Three seats filed three symptoms in one day. (a) **No way to release an unworked claim** — `done` is COMPUTED, so closing a row you never worked would have to defeat the DONE-WHEN gate; seats correctly sat on locks instead, and a claimed row **hides itself from the picker**, so one stale clone silently removed a row from the whole fleet's reach. New `unclaim`. (b) **The state column was decorative** — 94 of 94 rows read FREE and nothing consulted it, which is how `161-o2-red`, *parked by Lon at s258 and saying so in its own baton*, kept being served as the fleet's topmost rank-0 row. ⭐ **A ruling only a human enforces is not a ruling.** New `park`; PASS 3 obeys it; negative-tested both directions. (c) **A stale clone silently reverted to pre-V2 dispatch** — `next()` now refuses on a `PROTOCOL-VERSION` mismatch. ⛔ Note why the obvious check is wrong: *"git fetch and compare"* cannot work, because a seat that never pulled has a stale `origin/main` too — that test passes exactly when it must fail. The shared postoffice is the only authority no clone can be behind.
- ⛔ **pre-s189 ref sweep — REOPENED s265. seat03 swept 1625 pairs and reported ZERO; I negative-tested the instrument and IT CANNOT DETECT ITS OWN POSITIVE CONTROL.** Restoring the known-contaminated pin (`root=JOBJ` in `programs/snobol4/demo/json.ref`) and re-running `util_sweep_fold_arm_refs.sh` still reports `CASE-ONLY-DIVERGENCE: 0` — it buckets `json.sno` into `other-diff`, which the script drops by name as *"NOT this sweep's bug class"*. Cause is one token: line 51 captures with `2>&1`, and `json`/`calculator-1`/`calculator-2` write `match_ms=` to **TERMINAL** precisely so stdout stays byte-comparable; the merge destroys the case-only signature before it is tested. ⭐ **That is the row's own defect class wearing different clothes — a measurement carrying something it never declared it was carrying.** Also: `other-diff` took **14 of 25 in one directory** and is where the signal hides, and stdin resolution misses the `<family>.input` fallback the `-match` variants need (`util_mint_bench_refs.sh:ref_stdin()` already does it right). ⛔ **DONE-WHEN is now both-directions and mechanical: the script must DETECT the restored positive control AND report 0 on the corrected corpus.** A sweep never shown to find anything has not been shown to work. Ref restored; corpus clean.
- ⛔ **`always_inline` on the `core/core.h` tag predicates is a `hq_C` row now** (hq_P handed it over with a reproducer). Folding a one-line tag test cannot change what it computes, yet it breaks THREE deferred-capture tests and costs **100x wall time** — that is a live descriptor the collector stops seeing once it is no longer spilled to memory. Precise-roots territory. hq_P dropped it rather than committing it.
- ⛔ **`ce48e3bb` (hq_P's landed `descr.h` `always_inline` sweep) is UNDER SUSPICION but KEPT** — same mechanism, gated green twice, no evidence against it, worth 2.6% on claws5. **If any capture or GC red appears near it, revert it FIRST and re-measure.** Ruled jointly with hq_P; they will not defend the 2.6%.
- `demo_treebank` / `vlist-expr-alternation` (seat03) — staying red on purpose, unchanged.
- The 15 `benchmarks/snobol4/demo/` programs are graded by `util_mint_bench_refs.sh` but are **not** in the scorecard (`-maxdepth 1`). Adding them moves the denominator and the weights, and ⛔ **the weights are Lon's knob.**

**Evidence:** `FINDING-2026-08-23-hq_C-benchmark-corpus-was-a-harness-not-a-program.md`

## LIVE CURSOR — hq_C (s264, superseded by s265 above)

**s264 (2026-08-23) — FLEET OF 4, HANDOFF. Lon in-chat: *"You are running concurrently with a FLEET of 4 workers."* — that invoked FLEET for this run; DUO remains the default between runs (routed by ceo onto ARCH-FLEET-CEO.md's mode line).**

### ⭐ THE BOARD MOVED. MEASURED PRISTINE AT SCRIP `540e3a00`, BOTH EMIT GATES rc=0

| | start of s264 | **end of s264** |
|---|---|---|
| corpus m3 | 357/359 FAIL=2 | ✅ **359/360 FAIL=1** |
| corpus m4 | 355/359 FAIL=2 SKIP=2 | ✅ **358/360 FAIL=1 SKIP=1** |

**The only survivor is `demo_treebank`** (deliberate, seat03, and it is staying red on purpose — see below). ⛔ The denominator is **360**, not 359 (`a0859f7e` added a test).

### CURED THIS SESSION

1. **hq_C — the counted-string cset family** (`1f281ace`). Lon's ruling (*"any C function to manipulate strings is INVALID since the NUL character problem"*). `rt_coerce_str_d` carried **two defects on one line**: it tested `v.s[0]` for emptiness, so a NUL-leading string read as empty and raised *"argument is not a string"* (Error 69/59/151); and it overwrote a correct `slen` with `strlen()`, which is why `SPAN` failed **silently** instead. One line, two defects, four symptoms. BREAK/ANY/SPAN/NOTANY now all oracle-identical. `cset_resolve` had the same truncation and is fixed with it.
2. **hq_C — a measurement instrument that was lying** (`540e3a00`). `probes_misc` had no `norm=ms`, so 12 programs scored DIFF on **timing noise alone**. ⛔ This is the IDENTICAL defect that scored the benchmark suite 0/17 at s261 — s261 fixed the symptom in one suite and nobody asked which other suites fed the same harness. **They were the same bug in two places and only one was closed.**
3. **seat01 — generator resume under alternation** (`3342581a`). Cured `160_pat_alt_inner_gen_resume` AND the `json` demo. ⛔⛔ **AND THE REAL FINDING IS ORGANISATIONAL: the fix already existed, at s190, behind `SCRIP_ALT_TAIL` default OFF, and was never flipped** — while its sibling `sno_seq_tail()` (same mechanism) has been default-on the whole time. hq_C re-derived the defect from scratch at s264 not knowing it was solved. ⭐ **"Cured but not landed" is a state this org does not track, and it cost a full re-derivation.**
4. **seat02 — `porter-m4-duplicate-label`**: already cured at `b7d88465`; verified independently anyway, then **swept the class** (all 1971 non-lon programs compiled to m4 and `as`-checked, 0 hits).
5. **seat04 — `132_pat_fence_eps_recur_shallow`** (`4aec6e9f`). A bodiless `DEFINE` made mode-4 fabricate `FN__makeP`, a symbol nothing emits. Fixed to the `rt_ab_undef_fn_stub` idiom already used one function up. The last m4 SKIP is gone.

### ⛔ WHERE hq_C WAS WRONG, RECORDED RATHER THAN QUIETLY DROPPED

hq_C proved `160` + the json hang + `json-match-fence` were **one class** and predicted all three would fall to one cure. **Only two did.** Measured at HEAD: `json` **PASS/PASS** · `json-match` **TIMEOUT** · `json-match-fence` **TIMEOUT** (it moved DIFF→TIMEOUT, which is a *change of symptom*, not obviously an improvement). ⭐ The narrowing is sharp and is the row's value: `[1,2]` hangs, `[1]` completes, and **json.sno passes the same witness on the same grammar — the only structural difference is captures.** So the residual lives in the **capture-FREE** path, which is the opposite of where anyone would look. Row minted: `json-match-capture-free-hang`.

### OPEN, WITH OWNERS

- `json-match-capture-free-hang` — FREE, briefed with the bisection above.
- `demo_treebank` / `vlist-expr-alternation` (seat03) — ⭐ **STAYING RED ON PURPOSE, and hq_C ruled it so.** The TT_VLIST lowering was NOT missing (it landed at `b7d88465` behind `SCRIP_VLIST_ALT`, default off); the true blocker is `zd_plan` (`emit.cpp:2388`), whose run-walker follows only γ edges, so a node reachable only by an ω edge is never claimed and its address collides. seat03's prototype makes the SIGSEGV **probabilistic instead of certain** (crash vs silent wrong write depending on environment layout) — **a worse safety profile than the status quo**, correctly gated default-off and written up rather than shipped. A named red beats a silent wrong answer.
- `x64-execfile-writer` — ⛔ **BLOCKED** pending Lon on scope (routed via ceo). Not a config flip: `main.c:86` calls `malloc_empty()`, declared at `sproto.h:92`, **defined nowhere in either SPITBOL tree**. ceo verified by recompute and landed hq_C's four-condition ORACLE-SWAP PROCEDURE into RULES.md § Oracles as law.
- `nul-in-counted-strings-class-defect` (hq_C) — one rung left: `n11`, `CONVERT(table,'ARRAY')` on a NUL-bearing key raises **Error 235** where the oracle answers `3`.
- seat04's census: **META 90.0** over 1952 rows. Weakest suites are `gimpel 40.5%` and `csnobol4_suite 47.5%`; `beauty_self` (weight **20**) is structurally UNSCR, so the score is over 93/113 effective weight — ⛔ **the flagship is not in the number.**

### ⛔⭐ THE DOMINANT FAILURE MODE OF s264 — **THREE SEATS, THREE INSTRUMENTS, ONE TRAP: MEASURING ACROSS A MOVING TREE**

With four workers and two HQs all pushing, the tree changed under everyone, and **three independent seats produced a wrong measurement the same way in one session.** None of them was careless; all three caught it themselves.

1. **hq_P** ran a before/after where the two arms were **different trees** — `git pull --rebase` landed *between* the two corpus runs, so corpus1 (pre-rebase) was correctly RED and corpus2 (post-rebase) GREEN, and the delta got attributed to the only change they were conscious of, an `ARRAY(n)` edit. hq_C settled it in one command (`git merge-base --is-ancestor 3342581a a0859f7e` → NO; `3342581a` is `ce48e3bb`'s parent). ⛔ **RULES.md already said *re-prove your gate after a rebase*, and hq_P DID re-run the gate — and still subtracted a pre-rebase baseline from it. The rule as written closes only half the trap.**
2. **seat04** scored `160_pat_alt_inner_gen_resume` RED after the cure. hq_C guessed "stale pin"; **hq_C was wrong** — seat04 checked and the `.ref` was oracle-minted 2026-07-11 and always correct. It was a build/commit race: the recheck ran against objects that had not yet picked up `3342581a`.
3. **seat03** threw out an entire corpus board run for contamination by their own concurrent rebuild — caught before reporting.

⭐ **THE RULE, hq_P's wording, adopted: a before/after pair is only a measurement if both arms are the SAME TREE plus the ONE change. Re-baseline after every pull.** Re-proving the gate tells you the *tree* is good; it does not stop you subtracting a stale *baseline* from it. Those are two different disciplines and the org only has a rule for one.

⛔ **AND THE META-POINT: this is the cost of parallelism, and it is not free.** Four seats produced five cures today; they also produced three false measurements, every one of which took an HQ command to settle. Budget for that when sizing a fleet — the coordination is real work, not overhead.

### ⭐ THE METHOD NOTE, WORTH MORE THAN ANY SINGLE CURE

**A class defined by a CODE IDIOM is searched with a grep; a class defined by a VALUE is searched with a LADDER.** The NUL brief named an idiom that does not exist in the tree (`grep -c` = 0) and a 1,286-call census whose top files contained neither real site. A 14-rung witness ladder plus one gdb backtrace found both in two files. Both ladders are banked and reusable: `corpus/probe/altgen` (7 rungs, 2 controls) and `corpus/probe/nul` (14 rungs). ⭐ **Every ladder carries PASSING CONTROLS** — that is what proves the instrument discriminates rather than merely reporting red.


**s264 (2026-08-23) — FLEET MODE, 4 WORKERS. Lon in-chat, verbatim: *"You are running concurrently with a FLEET of 4 workers."* ⛔ This OVERRIDES the DUO default recorded below and in CLAUDE.md; it is Lon's word, this session, and it is why seats exist again.**

**CURED AND PUSHED HERE (SCRIP `1f281ace`):** the **cset-argument family** was wrong for `CHAR(0)`. `rt_coerce_str_d` — the coercion every pattern primitive funnels through — tested `v.s[0]` for emptiness, so a NUL-leading string read as empty and raised *"argument is not a string"* (Error 69 BREAK · 59 ANY · 151 NOTANY); the same line then overwrote a correct `slen` with `strlen()`, which is why `SPAN` returned a **silent** no-match instead. One line, two defects, four symptoms. `cset_resolve` had the same truncation and is fixed with it. Corpus **m3 358/360 · m4 357/360 +1 SKIP**, fail set unchanged by name, both emit gates rc=0. ⛔ **The denominator is 360, not 359** (`a0859f7e` added a test). Receipts: FINDING-2026-08-23-hq_C-counted-strings-cset-family-cured-at-two-funnels.md.

**PROVEN HERE, AND IT COLLAPSED THREE ROWS INTO ONE:** `160_pat_alt_inner_gen_resume`, the **json/json-match HANG**, and `json-match-fence` DIFF are **ONE defect** — a generator (ARB *or* ARBNO) in the FIRST arm of an alternation is never resumed when the continuation after the alternation fails. 7-rung ladder banked at `corpus/probe/altgen` (corpus `4e6eab8bc`), refs oracle-minted: **g01/g02 controls PASS, g03–g07 RED**, and the red rungs give a WRONG ANSWER in milliseconds rather than hanging — a far better instrument than the 5s timeout. FINDING-2026-08-23-hq_C-three-reds-are-one-class-generator-resume-under-alternation.md.

**FLEET DISPATCH s264 (claims on disk, assignment IS the lock):** seat01 `160-pat-alt-inner-gen-resume` (the class above, with the pre-minted ASM-DIFF pair g02-passes/g03-fails) · seat02 `porter-m4-duplicate-label` · seat03 `vlist-expr-alternation` · seat04 `snobol4-full-board-census` (newly minted — nobody had the denominator for Lon's "ALL SNOBOL4 programs at 100%"). hq_C holds `nul-in-counted-strings-class-defect`.

**NEXT:** `n11_array_key` — `CONVERT(table,'ARRAY')` with a NUL-bearing key raises **Error 235** where the oracle answers `3`. It is the one red left in the NUL ladder and it is hq_C's.

⭐ **METHOD NOTE WORTH MORE THAN EITHER CURE:** a class defined by a CODE IDIOM is searched with a grep; a class defined by a VALUE is searched with a LADDER. The inbound NUL brief named an idiom that **does not exist in the tree** (`grep -c` = 0) and a 1,286-call census whose top files contained neither real site. A 14-rung witness ladder plus one gdb backtrace found both in two files.


**s263 (2026-08-23) — NO-PIN ROOTED GC LANDED AND PUSHED (SCRIP `c61c5610`+`927d0521`+`1257d56c`).** Lon's rulings executed: (block,offset) slot registry replaces both interior-address fixup registries; PZ — which had been DEAD ON EVERY RUN since rtcc became mandatory (its constructor's pin/range registration disqualified the predicate; this was the "slow as a dog") — is resurrected and now covers tables/arrays/records (aggregates slide, repaired by the registry); collection moved to safepoints via an adaptive high-water line; `rt_gc_point_arr` and `rt_gc_collect` are asm veneers parking all six callee-saved registers above the repairing scan's floor (⛔ 16B alignment pad or libc movaps faults — measured); **ALL pin code physically deleted** (HBF_PIN, rt_gc_pin_ptr, gc_cons_scan/_t, rpin registry, pin telemetry, setjmp snapshot) — every formerly-pinned span is repair-scanned by gc_zeta_frame; zh bump blocks left the arena for rt_slab_region. Merged over hq_P's s262 TABLE rewrite. **Pristine: corpus m3 357/2 m4 356/2+1SKIP (standing reds only) · gc stress 15/15 × {plain,S25,S7,S1} × {m3,m4} ALL GREEN (204/213/214 cured — red since s131) · beauty 34/34 · both emit gates rc=0 · table_variety check 381880 even at SCRIP_HEAP_MB=4.** Open rungs routed in FINDING-2026-08-23-hq_C-no-pin-rooted-gc-slot-registry-pz-resurrection.md: coexpr stacks must leave the arena (Icon-gated), PLJ repair verification (Prolog-gated), rrng (block,offset) form. NEXT: the two standing corpus reds (160_pat_alt_inner_gen_resume is the front red).

**s263 addendum, at handoff — JSON-HANG ROW OPEN (from hq_P, blocks the JSON workhorse benchmark): bisected to a 5-byte witness.** `[1,2]` hangs and `{"a":1,"b":2}` hangs while `1`, `[1]`, `[[1]]`, `{"a":1}`, `{"a":[1]}` all complete against the oracle — so `ARBNO(sep item)` fails to TERMINATE after its first real iteration, in both jarray and jobject; nesting and single elements are innocent. Same family smell as front red 160_pat_alt_inner_gen_resume. Full table + the next-session ablation ladder: FINDING-2026-08-23-hq_C-json-hang-bisected-arbno-second-iteration.md. ⭐ NEXT SESSION STARTS THERE, not at 160 blind — the 5-byte witness is the sharper instrument.

## LIVE CURSOR — hq_C (s261, superseded by s263 above)

**s261 (2026-08-23) — TWO WRONG ANSWERS CURED, THE BENCHMARK SUITE UNBLOCKED. All numbers below measured on a `make pristine` tree (HQ-27); an earlier board self-reported ⛔ STALE BINARY and those numbers were discarded, not quoted.**

### ⭐ CURED THIS SESSION

1. **`calculator-2` — ARBNO extension double-fired a deferred capture** (SCRIP `ba628703`). An ARBNO that EXTENDS after an enclosing `. *FN()` capture's first success fired the action TWICE; the abandoned attempt's pend entry was never retracted and `rt_dcap_pump` replayed it. Cure is three instructions on the **ARBNO-FRAME** arm: bank `r12` at α, **RE-BANK at PAIR(2) when an instance commits**, restore at β. ⛔ The re-bank is the subtlety — rolling back to the α mark on every recede wipes instances that legitimately completed. Slot ownership **proven**: `frame_slot_off()` strides 16B/index, the arm uses bytes 0–7, so `AFCQ(8)` is the node's own memory. No new global, no grant. **1944 diff lines → 0.** FINDING-2026-08-23-hq_C-arbno-extension-double-fires-deferred-captures.md.
2. **Protected pattern names were silently assignable** (SCRIP `d40c1d8c`, lead from hq_P). `ARB = 1` landed and the program ran on. A GVA-eligible name stores via a direct cell write that never calls `NV_SET_fn`, bypassing its guard. Cured in **`gva_name_eligible()`** — the single admission funnel, beside the exclusion list that already exists for the same reason. ⛔ NOT the three call sites; that is the per-call-site filter RULES.md forbids. Oracle says the refusal is **RUN time** (statement 2, after earlier output), which is what routing back through `NV_SET_fn` gives. All seven names verified.
3. **The benchmark suite was grading 0 of 17** (SCRIP `1c0d2aad`). `harness.inc` grew a full-resolution `ns:` line; the `norm=ms` filter deletes measurement lines BY NAME and never learned it, so every pin mismatched. **0.0% → 100.0%.**

### BOARD, MEASURED PRISTINE

| suite | before | after |
|---|---|---|
| benchmarks | 0/17 · 0.0% | **17/17 · 17/17 · 100.0%** |
| demos | 18/23 · 17/23 · 76.1% · UNSCR 1 | **19/23 · 18/23 · 80.4% · UNSCR 0** |
| corpus (`-O0`) | m3 357/359 · m4 355/359+2SKIP | **unchanged, identical fail set** |

### NEXT, IN ORDER
1. **`json` + `json-match` — TIMEOUT/TIMEOUT at 90s.** Two of the four remaining demo reds. Likely the open `json-alternate-af-spin` row. **Unexamined by me — no depth estimate.**
2. **`json-match-fence` — DIFF.** Unexamined.
3. **`porter` — m4-only ASM_FAIL** (duplicate-label). The single row separating m4's 18 from m3's 19.
4. **`160_pat_alt_inner_gen_resume`** — the only non-deliberate crosscheck red.
5. ⛔ **The NV_SET_fn guard-bypass CLASS is OPEN.** Protected-names was one instance; nobody has audited what other name-based guards live there and are bypassed for GVA-eligible variables.
6. ⛔ **`expression.sno` moved** to `programs/snobol4/oracle-unrunnable/` (Lon) — 15 absent includes, `sbl rc=139`, ungradeable.
7. ⛔ **NO `-O2` BUILDS is a fact rule (Lon s262).** The `-O2`-only reds are unreachable by construction; `FINDING-...-calculator-1-is-an-O2-split...` keeps its verdict (**53819b4a CLEARED, do not revert**) but its defect is moot.


**s258 → s259 (2026-08-22/23) HANDOFF. Every line carries the command behind it.**

### ⭐ r10/r11 ARE NOW USABLE FOR stmt#/BB-node# — VIA THE VENEER, NOT ERADICATION

**Lon ruled the method:** *"Just add R10 and R11 to the RTCC VENEER."* Correct, and far cheaper than what this seat was doing.

- **RTCC veneer extended** (SCRIP `53819b4a`): `RTCC_C_R10`/`RTCC_C_R11` added to the mask and to `RTCC_C_ALL`; save+restore emitted in **both media** at the slots `rtcc.h` had already reserved (`rtccb+56`, `+64`; `RTCC_GPR_COUNT` was already 9). **Measured: 71 save/restore pairs each on roman.**
- **Mask table updated** for the five symbols that clobber them — `rt_cmp_d` (r10+r11), `rt_cap_match_begin`/`rt_cap_pop`/`rt_cap_top`/`rt_match_ctx_restore` (r10). `test_gate_rtcc_callee_class` PASSES.
- **Emitted code is clear of r10/r11 as scratch**: templates went 20/48 sites → **0/0** (the one remaining "r10" is a comment string). Targets chosen by measured liveness, not convenience — `rcx` would have produced `mov [rcx+0], rcx` because `creg` is passed as rcx; `rdi` overlapped 0 of 17 r11 sequences where `rdx` overlapped 4.
- ⛔ **Runtime `.S` still uses them as scratch** (r10 ≈ 97 instruction lines, r11 ≈ 56) — **and that is now FINE**, because the veneer saves across the call. Eradicating them there is no longer required and the ABI working set stays nine registers.
- ⛔ **A bug I introduced and the gate caught:** substituting r10→r8 at four `rtx_match.S` sites made three declared non-clobbering leaves write r8 without declaring it, which would have had the veneer drop a live slot. **Reverted.** Do not sed hand-written asm.

### CORRECTNESS STATE, MEASURED AT SCRIP `53819b4a`

- **Corpus (`-O0`, the dev arm): m3 357/359 · m4 355/359 + 2 SKIP.** Reds: `160_pat_alt_inner_gen_resume`, `demo_treebank` (deliberate), `132_pat_fence_eps_recur_shallow` + `demo_porter` (compile SKIP). **Unmoved across every change tonight.**
- **Milestone 1 holds at `-O0` in both media**; ⛔ **BROKEN at `-O1`/`-O2` — PARKED by Lon** (both culprits are C runtime slated for ASM replacement). `161-o2-red` is PARKED, not discarded; the storage-assumption note in its baton matters for whoever writes that ASM.
- All 17 benchmark kernels correct at `-O0` **and** `-O2`, zero arm delta.

### NEXT, IN ORDER
1. **`jstring-escape-dcap-pump-segv` (rank 0)** — ⭐ diagnosed further tonight and it is NOT the reported plain SEGV: a 4-byte input `"\t"` gives **heap exhaustion (512 MB) then abort**, because after the deferred `*estr` re-enters and pushes a second dcf frame, the outer frame's entry is read with **`len=480251808`**. Line 650 guards `len < 0` but not absurd positive. ⛔ The heap death MASKS a 458 MB out-of-bounds `memcpy` at line 652. Fix: bound `len` against the subject (`Σlen`) — line 912 already does exactly that check elsewhere, so the invariant exists and is simply not applied here.
2. **`rtcc-r9-gvarq-collision-bb-define` (rank 0)** — live uncleared r9/GVARQ collision; `test_gate_rtcc_claimed_regs --strict` is RED and was red before tonight.
3. **`160_pat_alt_inner_gen_resume`** — the only non-deliberate standing corpus red.
4. ⛔ **Icon and Prolog are NOT now** (Lon s258); their oracles are absent from this box regardless.
## ⛔ SUPERSEDED CURSOR — s258 (kept for its measurements, NOT the live cursor)

⛔ **THIS IS NOT THE LIVE CURSOR.** The live one is above, at s259/SCRIP `53819b4a`. This file carried **two** sections both titled `LIVE CURSOR — hq_C`, in a file whose whole premise is *trust the LIVE CURSOR at the top* — so a reader scrolling to the last one got the older state. Demoted 2026-08-23 s261. Its `161-o2-red` content is retained because RUNG C-0 is PARKED, not solved, and the ddmin result is the map for the ASM rewrite.

**s258 (2026-08-22) — HANDOFF. Every claim below carries the command that produced it.**

### THE CORRECTNESS STATE, MEASURED AT SCRIP `751557a9`

| | `-O0` (dev arm) | `-O1` | `-O2` (bench arm) |
|---|---|---|---|
| beauty M1 self-host, m3 **and** m4 | ✅ 40,971 / `6f1671c0` | ⛔ 278 | ⛔ 278 |
| `161_pat_defer_fn_nested_match` (17 lines) | ✅ oracle | ⛔ **SEGV** | ⛔ wrong answer, rc=0 |
| corpus | m3 357/359 · m4 355/359+2SKIP | — | m3 355/359 · m4 354/359+2SKIP |
| 15 benchmark programs | ✅ 15/15 | — | ✅ 15/15 (zero arm delta) |

⭐ **THE WHOLE OPTIMISATION DEFECT IS TWO FILES OF 261** — `src/runtime/rt/rt.c` and `src/runtime/pattern_match.c`, found by two automated file-level bisections with bounds confirmed first. De-optimise exactly those two and beauty self-hosts in both media at `-O2` and the corpus returns to the `-O0` baseline **exactly**: `bash scripts/build_o2_working_snobol4.sh`. ⛔ **That is a WORKAROUND — it hides UB, it does not remove it.** Non-additive: `rt.c` alone leaves beauty at 614 bytes; `pattern_match.c` alone fixes neither. One defect class, two doors. Row: **`161-o2-red`, rank 0**, baton `tasks/161-o2-red.task.md`. Next probe: `-fsanitize=undefined` on exactly those two files. ⭐⭐ **ROOT CAUSE CONFIRMED FOR THE WITNESS — `rt.c` compiled with ANY optimisation allocates the BLOB-PIN registers and breaks the pinned ABI.** `rtx_abi.inc` pins **rbx · r13 (Σ) · r14 (δ) · r15 (Δ)**. Denying gcc the full set in `rt.c` cures the witness at `-O1` **and** `-O2`; **r13 is necessary in every cure** (`rbx+r13` ✅, `r13+r14+r15` ✅, `rbx+r14+r15` ⛔, any single pin ⛔). At `-O0` gcc never allocates them, so the pins survive by accident — which is exactly why `-O0` works and `-O1` does not. ⛔ `-ffixed` is a DIAGNOSTIC, not the fix: it costs four GPRs everywhere.
⛔ **AND A RETRACTION I OWE, IN MY OWN CURSOR:** I earlier wrote *"REFUTED, do not re-run"* against this hypothesis. **I had tested only two of the four pins.** A hypothesis tested on a subset of its own terms and reported as refuted is worse than an untested one, because it carries a "do not look here" sign.
⛔⭐ **TWO INDEPENDENT MECHANISMS — PROVEN, not suspected.** All 261 runtime objects built at `-O2` with all four pins reserved: **witness PASSES, beauty still 278 bytes in both media.** Pin reservation cures the witness class and is **not sufficient for Milestone 1**. Mechanism 2 lives in `rt.c` + `pattern_match.c`, and is not the pins, not UB (UBSan silent), not a single pass, and not the directly-called functions. ⛔ Chase it with the pins already reserved so the pin noise is gone. ⛔⛔ **AND NOT WITH A BINARY SEARCH — that was tried and it SELF-REFUTED.** A by-function bisect over 289 symbol-table-derived functions (instrument pre-verified, bounds asserted) converged on `rt_gvar_assign_pat_sz`, and the confirmation step then showed that function alone does NOT cure it. **The property is not monotone** — round 3 returned FAIL(**614**), a third distinct byte count, the fingerprint of interacting contributors. If the cure needs two functions together, a half holding only one fails and the search discards the half holding the other. ⭐⭐⭐ **MECHANISM 2 IS NOW LOCALISED TO TWO FUNCTIONS — `c_rt_cap_open` (pattern_match.c) and `rt_call_proc_descr` (rt.c)** — found by **ddmin** and verified two-sided: each alone leaves beauty broken (278 and **614** respectively), both together give the exact fixed point. ⭐ That **explains the 614** that has puzzled every arm of this hunt: it is `rt_call_proc_descr` cured with `c_rt_cap_open` still live. They are the two halves of the deferred-call-in-a-pattern path — a capture open and a procedure call by descriptor — which is exactly what hq_P's independent perf finding pointed at from the other side. FINDING-2026-08-22-hq_C-mechanism-2-is-two-functions-*.md. ⛔ Still a workaround; next step is to diff each function's -O0 vs -O2 disassembly, which is now tractable.
⭐ (Superseded note, kept for method: mechanism 2 was earlier believed DISTRIBUTED — matching the file-level signature (`rt.c` alone → 614, `pattern_match.c` alone → nothing, both → pass). Next method: **delta debugging (ddmin)** or additive accumulation from the empty set; and whatever runs must verify each candidate ALONE before accepting it, which is the only reason this did not become a confident wrong answer. ⛔ And do NOT ship the `-ffixed` contract as "fixing -O2" — it fixes one of two things.
⭐ Negatives recorded so nobody repeats them: UBSan on both files reports **nothing**; no single `-fno-<pass>` cures it; `rt.c`'s 6 file-scope asm blocks are ABI-clean (the coroutine entry's unrestored callee-saved registers are correct — it `jmp`s, never returns); de-optimising only the 7 rt.c functions the witness calls does not cure it.

### WHAT LANDED THIS SESSION

- **Milestone 1 finally has a gate.** `grep '40971\|6f1671c0' scripts/*.sh` returned NOTHING — the property the project is measured by was undefended, which is why C-0 needed a hand bisect. `test_gate_m1_self_host_fixed_point.sh`, negative-tested three ways (fails at `-O2`, passes at `-O0`, fails on an absent binary instead of skipping green).
- **`done` now computes the verdict.** It appended the DONE marker unconditionally and never ran the DONE-WHEN — LAW 1 violated inside the tool written to enforce it. Now it runs the baton's criterion and refuses on non-zero. Override is loud and recorded.
- **`test_gate_fleet_protocol_e2e.sh`** — the first test of the whole seat LOOP (α→β→γ→ω) rather than one subcommand. The picker gate and the identity gate were both green over the `done` hole all session because neither ran a lifecycle.
- **V2-1** (rank-sorted picker, `assign`-is-the-lock, `sweep`) + **queue purge** (113 rows swept, 4 dead locks freed, dups deduped) — cross-verified and signed off by hq_P; I cross-verified and signed off their V2-3/V2-4.
- **The build.** `RT_OBJDIR`/`.so` are keyed by a hash of `RT_OPT`+`ZCFLAGS`, so arms coexist and switching costs **0–1s instead of 9m30** — and a silent wrong build (no flag stamp: `RT_OPT="-O2" make` after `-O0` did nothing and returned `-O0`) is now structurally impossible. `make buildinfo` prints what you are actually linking. `pristine` also removes `./scrip`, which it never did.
- **hq inbox drained** — 10 seats answered, `fleet` shows **Q=0 on every row**.

### NEXT, IN ORDER

1. ⛔⛔ **`161-o2-red` (rank 0).** `-fsanitize=undefined` on `rt.c` + `pattern_match.c`. The 17-line witness replaces the 40KB one — three behaviours at three optimisation levels.
2. **V2-5 gate honesty — the last protocol blocker.** seat16's **31 injection-proven** can't-say-no gates is the authoritative number; my syntactic scan finds only 4, and injection is the stronger test. Two are confirmed hiding live defects.
3. **V2-2 is partial** — 11 batons of 77 live rows; QUEUE.tsv still carries multi-KB prose.
4. **`rtcc-r9-gvarq-collision-bb-define` (rank 0)** — live uncleared r9/GVARQ collision in `bb_define.cpp`; `--strict` is invoked nowhere in the repo.
5. ⛔ **Every correctness verdict names its RT_OPT.** The C-0 misfire was one arm of a two-arm axis reported without the axis.
6. **Icon and Prolog are coming and are NOT now** (Lon s258). Their oracles are absent from this box; install before staffing either front.
