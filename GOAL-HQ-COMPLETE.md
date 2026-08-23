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

## ⛔ THE LAW BOTH HQs SHARE: MEASURE FREELY, CURE NEVER

Lon s256: *"you can build and test and do, but when you find BUGS you delegate."* Build, run, diff, bisect, profile — all of it. **The moment a measurement becomes a DEFECT it becomes a row and a brief, never an edit.** HQ's output is rungs; a fix taken at HQ is a fix the fleet did not learn.

## ⛔⛔⛔ RUNG C-0 — **STILL OPEN.** CURED AT `-O0`, BROKEN AT `-O2` (measured 2026-08-22, hq_C)

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

## ⛔⭐⭐⭐ STANDING ORDER CHANGE — DUO ONLY, NO FLEET (Lon, in-chat, 2026-08-22 s258)

**Lon, verbatim in substance:** *"Just so we are clear we are run only duo here, no FLEET, just 2 HQ's."*

**hq_C and hq_P are the only sessions running. There are no seats.** What this changes, and it is most of the operating model:

1. ⭐ **MEASURE FREELY, CURE NEVER IS SUSPENDED FOR THIS SEAT — HQ CURES NOW.** That law's stated reason was *"a fix taken at HQ is a fix the fleet did not learn."* With no fleet there is no learner, and the law would mean **nothing gets fixed at all**. Lon has already put this seat in a curing role in the same session (*"Fix that BUILD problem"*), which is the reading in practice. ⛔ This is HQ's reading of two Lon statements, not a third Lon statement — it is marked as such, and Lon can overturn it in one line.
2. **The batons are a two-person worklist, not a dispatch queue.** `/home/resources/postoffice/tasks/*.task.md` keep their full value — GOAL, a DONE-WHEN that is a command, QA and an evidence LEDGER — but nobody is coming to pick them up. hq_C works them directly, newest evidence appended as before.
3. **All 7 seat assignments have been RELEASED** (`claims.released.hq_C-s258-duo/`). ⛔ This was not cosmetic: a claimed row **hides itself from the picker**, so leaving work assigned to a seat that is not running would have fenced it off from the only two sessions that exist.
4. ⛔ **CORRECTED BY LON THE SAME SESSION — THE FLEET PROTOCOL IS NOT DORMANT, IT IS THE ENABLER.** hq_C had written the control plane off as "dormant, no further investment" on hearing "duo only". Lon, in-chat: *"I am saying get the FLEET protocol working, or we can not blast development later"* and *"We will be doing massive work on Icon and Prolog etc as we go. We want the system working."* So the duo is the CURRENT staffing, not the destination: the fleet returns for the Icon/Prolog work, and the protocol must be finished and proven BEFORE it does. ⭐ Outstanding, in priority order: **V2-5 gate honesty** (31 of 105 gates cannot say NO — at 16 seats that closes rows on false green at scale, and LAW 1's DONE-WHEN rule depends on it), **V2-2 queue-as-index** (11 of 77 live rows converted to batons; rows still carry multi-KB prose), then V2-6 (Lon's flip; `PROTOCOL-V2-DRAFT.md` is staged and structurally complete).
5. **Escalation is unchanged:** hq_C ↔ hq_P directly, `ceo` for arbitration, Lon overrides anyone.

## LIVE CURSOR — hq_C

**s258 (2026-08-22): C-0 is REOPENED on the `-O2` arm, the control plane is repaired, the build is fixed — and the fleet is gone. The cursor moves to WORK IT MYSELF.**

**Done this session, each with a command behind it:** C-0 measured CURED at HEAD (both media) and HQ's own prime suspect disproven · the M1 probe rescued out of a seat's disposable `/tmp` into `.github/probes/m1-bisect/`, made portable, and its **own** blindness (the `-INCLUDE`/CWD trap) found and fixed · **V2-1 landed and pushed** (SCRIP `93d3ef16`: rank-sorted picker, `assign`-is-the-lock, `sweep`; gate `test_gate_s4e_picker_v2.sh` 18/18, negative-tested three ways) · **queue purged** (113 DONE rows swept to `QUEUE.done.tsv`, blank-line landmine gone, 4 dead locks released, every brief pointer verified) · **hq inbox drained** — all 10 seats with open questions answered · **hq_P's V2-4 cross-verified and signed off** (18/18 live, 15 failures against pre-patch) · **9 task batons minted** in `/home/resources/postoffice/tasks/`, every DONE-WHEN a command and every one demonstrated able to say NO.

**NEXT, in order — ⛔ DUO MODE: these are jobs to DO, not briefs to dispatch. ⭐ AND LON RULED THE SEQUENCE (s258): SNOBOL4 **this minute**; the FLEET PROTOCOL finished so development can be blasted later; Icon and Prolog massively but NOT NOW.**
1. ⛔⛔⛔ **RUNG C-0 ON THE `-O2` ARM. Nothing outranks it and it is now this seat's own hands.** The `-O2` failure is byte-identical to the pre-cure `-O0` failure, so it is the same 32-bit-tag-compare class surviving optimisation. ⭐ **Free narrowing already banked: `RT_OPT` already carries `-fno-strict-aliasing` AND `-fwrapv`, so the two commonest UB-under-optimisation causes are ALREADY EXCLUDED.** ⭐ **`-O1` IS ALREADY DONE AND IT FAILS** (278 / `1c75f97d`, identical), so the boundary is `-O0`→`-O1` and the suspect set is `-O1`'s passes, not `-O2`'s. Next probes, cheapest first: **`-fsanitize=undefined` at `-O0`** (highest yield — UB is exploitable at `-O1` even where `-O0` happens to work, and the two commonest causes are already excluded by the existing flags, so what remains is the interesting kind); then `-O1 -fno-<pass>` bisection over `pattern_match.c`/`rt*.c`; then `-Og` as a sanity point. ⭐ Each arm now costs 0–1s to switch back to, so this is finally affordable — that is what the build fix bought.
2. **`161-o2-red` is almost certainly the same defect** (`161_pat_defer_fn_nested_match` SEGVs both modes at `-O2` only; *"wound is runtime C under optimization"*). Treat them as one investigation until proven otherwise — a second witness for the same bug is worth more than a second bug.
3. **`rtcc-r9-gvarq-collision-bb-define`** — live uncleared r9/GVARQ collision in `bb_define.cpp`, which the rtcc gate reports green over because `--strict` is invoked nowhere.
4. ⛔ **Still owed by Lon:** SNOBOL4-FIRST vs the s255 bootstrap ruling. HQ reads it as a sequence — **a reading, not Lon's word** — and the Icon/Prolog oracles are absent from this box regardless.
5. ⛔ **Every correctness verdict from here names its RT_OPT.** The C-0 misfire was one arm of a two-arm axis reported without the axis.
