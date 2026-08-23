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

## ✅ RUNG C-0 — CLOSED BY MEASUREMENT 2026-08-22 (hq_C). MILESTONE 1 IS **NOT** REGRESSED AT HEAD

**The 278-byte stub was real, is reproducible, and is already cured.** Measured at HEAD `457dc5d9`, pinned classic source, run from the beauty directory:

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

## LIVE CURSOR — hq_C

**s258 (2026-08-22) closed RUNG C-0 by measurement and repaired the control plane. The cursor moves to DISPATCH.**

**Done this session, each with a command behind it:** C-0 measured CURED at HEAD (both media) and HQ's own prime suspect disproven · the M1 probe rescued out of a seat's disposable `/tmp` into `.github/probes/m1-bisect/`, made portable, and its **own** blindness (the `-INCLUDE`/CWD trap) found and fixed · **V2-1 landed and pushed** (SCRIP `93d3ef16`: rank-sorted picker, `assign`-is-the-lock, `sweep`; gate `test_gate_s4e_picker_v2.sh` 18/18, negative-tested three ways) · **queue purged** (113 DONE rows swept to `QUEUE.done.tsv`, blank-line landmine gone, 4 dead locks released, every brief pointer verified) · **hq inbox drained** — all 10 seats with open questions answered · **hq_P's V2-4 cross-verified and signed off** (18/18 live, 15 failures against pre-patch) · **9 task batons minted** in `/home/resources/postoffice/tasks/`, every DONE-WHEN a command and every one demonstrated able to say NO.

**NEXT SESSION, in order:**
1. ⭐ **ASSIGN, do not let seats self-pick.** Nine batons are ready. `bash SCRIP/scripts/s4e_msg.sh assign <seat> <topic>` — that is what V2-1 was built for, and day-1 self-pick is what the firing gate forbids.
2. **Rank-0 first:** `rtcc-r9-gvarq-collision-bb-define` (live r9/GVARQ collision, gate reported green over it) and `jstring-escape-dcap-pump-segv` (4-byte repro, SIGABRT at HEAD).
3. **`rung-m1-m3-regression` is now a 20-minute confirm-and-correct job, not a bisect.** Whoever takes it corrects `board_beauty_m1.sh`'s stale red too.
4. ⛔ **Still owed by Lon and still unanswered:** SNOBOL4-FIRST (do not even RUN Icon/Prolog checks) versus the s255 bootstrap ruling that puts them on the road. HQ reads it as a sequence — **that is a reading, not Lon's word.** Do not staff Icon or Prolog until Lon rules AND the oracles are installed.
5. Run `bash SCRIP/scripts/s4e_msg.sh fleet` on a cadence.
