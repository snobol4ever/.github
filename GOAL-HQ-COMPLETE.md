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
⛔⭐ **TWO INDEPENDENT MECHANISMS — PROVEN, not suspected.** All 261 runtime objects built at `-O2` with all four pins reserved: **witness PASSES, beauty still 278 bytes in both media.** Pin reservation cures the witness class and is **not sufficient for Milestone 1**. Mechanism 2 lives in `rt.c` + `pattern_match.c`, and is not the pins, not UB (UBSan silent), not a single pass, and not the directly-called functions. ⛔ Chase it with the pins already reserved so the pin noise is gone. ⛔ And do NOT ship the `-ffixed` contract as "fixing -O2" — it fixes one of two things.
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
