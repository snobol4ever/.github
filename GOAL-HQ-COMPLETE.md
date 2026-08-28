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
| **SNOBOL4 #1** | ✅⭐ **CURRENT: `365/365` BOTH MODES, `FAIL=0 SKIP=0 MISSING=0`, rc=0 `GATE OK` — measured by hq_C 2026-08-27 s274, pristine `-O0`, SCRIP `d4e6e971`.** **M1 fixed point HOLDS in both media, verified by hand this session** (see the s274 cursor: m3 and m4 both 40,943 B / `f20461f9…`, byte-identical to `beauty.sno`, `m3 ≡ m4` clean). ⛔ **The denominator has moved legitimately and repeatedly — 364 → 362 → 365 — so read `FAIL=0 · SKIP=0 · MISSING=0` over the printed total, NEVER a remembered number.** The board refuses (rc=2) when its basis moves, which is what makes that safe. Historical detail below, all of it superseded on the numbers: ⭐⭐ **`364/364`, ZERO KNOWN REDS, ON `main` — MEASURED BY hq_C s271 (2026-08-24), pristine `-O0`, SCRIP `9df28b03`: `m3 PASS=364 FAIL=0` · `m4 PASS=364 FAIL=0` · `SKIP=0` (364 total).** Lon's number (*"We want SNOBOL4 to be 364 out of 364"*) is **MET**. Both former reds are cured: `demo_treebank` / `vlist-expr-alternation` at `0e57de3b` (s270, the `fc_geom` per-op-filter grant) and `TDump_driver` at `9df28b03` (s271, dropping `822bc8a1`'s gin/oin self-edge suppression). Board re-run pristine **after** the `94dd91ba` rebase, per s270's measure-then-rebase rule. ⛔ **EVERY EARLIER FIGURE ON THIS ROW IS STALE AND DELETED** — `363/364`, `357/359`, `339/341`, `320/321`: the denominator is **364** and the numerator is now **364**. ⛔ **BUT "no corpus red" ≠ "SNOBOL4 is finished":** the named tail is `v05` — PASSES m3, **SIGSEGVs m4**, an m3 ≢ m4 DESIGN-INVARIANT violation, row `vlist-v05-m4-sigsegv-m3-m4-divergence` (rank 2), and it is invisible to this board because the corpus is green in both modes. The old `132_pat_fence_eps_recur_shallow` and `demo_porter` SKIPs are **CURED and gone**. Receipt: `bash scripts/test_corpus_snobol4.sh`. |
| **Icon #2** | ✅ **Oracle BUILT s266** — Arizona icont/iconx at `/home/resources/icon-master/bin/`, symlinked `/home/resources/icon-build` (scripts' default `ORACLE_BIN`), `SCRIP/refs/{icon,jcon}-master` repopulated, smoke-verified. Lon s266: *"Take us to 100% SNOBOL4 and 100% Icon"* — Icon is IN SCOPE, superseding the s258 "not now". seat08's rung-A2 register-liveness analysis is banked, HELD, not lost. |
| **Prolog #3** | ⛔⭐ **THE "ORACLES ABSENT" CLAIM ON THIS ROW WAS FALSE AND IS DELETED — MEASURED 2026-08-27 hq_C: `/usr/bin/swipl` = SWI-Prolog **9.0.4**, `/usr/bin/gprolog` = GNU Prolog **1.4.5**, both present, both genuinely on `PATH`.** The row read *"no `swipl`, no `gprolog`. Same rule: no oracle, no verdict"* — **a false premise sitting in the sovereign file blocking Prolog grading**, which is the exact class `CLAUDE.md` names for Icon (a seat ran `command -v icont`, got nothing, and wrote *"no Icon oracle exists"* into the digest). ⛔ It also **contradicted this file's own s271 cursor**, which quotes a graded board — `Prolog PASS=93 FAIL=2 SKIP=94 ORACLE_MISS=0` — so the two halves of this file disagreed and the pessimistic half is the one that was wrong. ⭐ Both oracles are reachable by absolute path and `lib_oracle_flags.sh` is the shared authority. Prolog is GRADEABLE. Open work: `prolog-pz4-gamma-retain-activation-frames` (rank 0 FREE, the keystone) with `prolog-pz5-…` BLOCKED behind it; measured floor rung13 `0/5` · rung14 `2/5` · rung15 `1/5`. |

✅⭐⭐ **THIS RULING IS NO LONGER OWED — IT WAS ANSWERED 2026-08-26 AND THIS FILE DID NOT NOTICE FOR A DAY.** The block below read *"RULING OWED BY LON, ASKED AND STILL UNANSWERED … Confirm before staffing Icon or Prolog."* **`RULES.md:29` § CROSS-LANGUAGE SCOPE settles it** (Lon, in-chat to CEO, verbatim: *"Give approval to make cross language changes to all Fleet workers, we are trying to get all languages working nicely."*): the SNOBOL4-FIRST era is **CLOSED**, the DO-NOT-RUN prohibition is **retired**, and no lane-scoped permission is needed to staff Icon or Prolog. ⛔ **Three stale premises were sitting in this one section at once** — this one, the false *"Prolog oracles ABSENT"* row above, and a SNOBOL4 total two re-grids out of date. ⭐ **Each was independently pessimistic, and that is the pattern worth naming: a sovereign file decays toward *blocked*, because a resolved blocker leaves no artifact where the block was written.** The measured cure is the one this org already has — **law lives in `RULES.md`, and a goal file must CITE it rather than restate it** (`RULES.md:170`, the same corollary that keeps rules out of the per-root digests). ⚠️ What still binds, and is not the old rule renamed: this seat's correctness PRIORITY is unchanged — **SNOBOL4 #1, Icon #2, Prolog #3** — and the SHARED-NODE VERDICT SCOPE still gates **landing**. Permission was removed; the ordering and the measurement were not.

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

**s277 (2026-08-28, Opus 5, FLEET-8) — ⭐⭐ A FORMAT EXCEPTION CLASS THAT CITED MY OWN RULING IS GONE, AND THE FILE NAMED FOR THE COVERAGE IT PROVIDES PROVIDES NONE.**

Inbox 3, all answered and cleared (seat02 decline, ceo resend request, seat07 question). Row `corpus-crosscheck-probe-total-conversion`. SCRIP `241def5e` · corpus `710f2562c`.

### ⭐ SUITE FORMAT EXTENSION (C): STDIN, OUT-OF-BAND — AND THE DESIGN CAME FROM MY OWN BUG
9 of crosscheck's 10 "permanent keepers" were stdin-bearing, held loose because *"the settled suite format has no stdin-input concept"* — citing **this seat's own** ruling in their `KEEP.md`. Lon voided the exception class, so the excuse became the work. Landed as a **third parallel `family.in`**, banner-keyed, matched by name; absent ⇒ `/dev/null`, so every existing suite keeps its verdicts byte-for-byte.
⛔ **The in-band `*<<<STDIN` marker was rejected on measured grounds, not taste** — it is the `a01fe9f6` class I cured this same session (a port marker prepended in-band, `x86_internal_resolve` eating two bytes of any Pascal descriptor carrying that byte in its own `.string` data; silent, m4-only, read as *output mismatch*). ⭐ **A test program's stdin is arbitrary user bytes, so reserving any line shape inside it recreates that class by construction.** The general form I wrote into the format amendment: **xfail and self-pinned-ref grading are also entry metadata and belong in sidecars for the same reason.**
⭐ **Auto-discovered, never a flag** (`sidecar_in_path`): every board, gate and runner picks stdin up with **zero argv changes**, so a converted family cannot silently run *without* its input because one caller was missed — the failure a `--stdin` flag would have guaranteed, and it would have looked like a real FAIL.
**Measured, both directions:** control arm old-vs-new over 3 families / 29 entries — `SUITE_BOARD` **byte-identical** · round-trip exact incl. stdin · **load-bearing: with `.in` 6/6 PASS both modes, hidden 0/6**, through the CLI so auto-discovery itself was under test · Pascal m3 suites 96/0 (`read_block_suite` = the path changed most) · both blocking gates rc=0.

### ✅ 9 CONVERTED, THREE DIRECTORIES DELETED, DENOMINATOR NET ZERO
`crosscheck/{arith,control,strings}` **gone**, with the `KEEP.md` files that documented the void exception. **Oracle pre-flight first: 9/9 match `sbl -bf` byte-for-byte** — genuinely oracle-derived, not self-pinned. Byte-equality validated **per entry** against the loose original, both modes, same stdin, before any delete.
**Attributed (s272):** 893 → 902 (both copies live) → **893**. Net zero — the 9 changed container without leaving the board. ⚠️ Post-rebase the board reads **1081/1081 FAIL=0 SKIP=0 MISSING=0 rc=0**; the extra 188 are other seats' conversions landing under me. **Read FAIL=0 over the printed total, never a remembered number** — that rule demonstrated itself twice in one session.
⭐ **The pre-flight is now twice-measured, not a maxim.** The same audit found **4 of 96** Pascal crosscheck refs pinned to SCRIP's own output, invisible for 20 days, past a 7-of-82 spot-check and an exhaustive whitespace check. **A conversion inherits the correctness of its inputs, and byte-equality preserves a bad ref perfectly** — after conversion the error is permanent *and provable-looking*.

### ⭐⭐ THE 10th KEEPER: A FILE NAMED FOR THE COVERAGE IT PROVIDES, THAT PROVIDES NONE
`coverage_sno_nodes.sno` claims to exercise every SNOBOL4 IR node kind. **Measured:** the oracle **SIGSEGVs nondeterministically** (139,139,231,139,139 over five runs) and emits a **timestamped** listing → no oracle ref can ever exist; SCRIP refuses it deterministically rc=1 (`pattern shape outside the SN4-PAT subset … IR_MATCH_* pending`). **Neither implementation can execute it.**
⭐ `KEEP.md` called it *"genuinely never graded"* — **true, and it reads as benign. The reason it is never graded is that it cannot run.** Same family as the Icon recognizer's `(compiland "")`: **a thing characterised precisely enough to be bucketed, never enough to be graded.** Held as a pending-feature witness — giving it a ref from SCRIP's own refusal would launder a self-pinned ref, exactly what I refused for the 4 Pascal blocks.

### ⛔ CLAUSE 1 NOT CLAIMED, AND THE BLOCKER IS NAMED
`corpus/crosscheck/` is **not deletable yet**: `snocone/` 181 `.sc`, `coverage/` 1, plus beauty/patterns artifact residue. **Both remainders gate on extension (D) xfail/xpass**, whose convention already exists on disk (`.xfail` sidecars whose *content is the reason*, 4 of them) while the harness has **zero** support. ⭐ That the org reached for a sidecar unprompted is itself the design argument for keeping (D) out-of-band too. Fan-out re-cut: minted `crosscheck-snocone-181-convert` rank 2 FREE (177 convertible now, 4 held).

### ⭐ seat07's ROW: I VERIFIED THE MECHANISM IN SOURCE INSTEAD OF SENDING A FOURTH GUESS
Their storage-class hypothesis is **structurally well-posed**: `emit.cpp:1080-1085` dispatches `IR_VAR` into `bb_var()` (source `FRQ(_.op_sa)`, RSP-relative for Pascal → depth-sensitive on read **and** write) vs `bb_var_global()` (source `GVARQ`/`ABSQ` → **depth-independent**). ⭐ **The discriminator is the SOURCE read, and `bb_var()`'s source is `_.op_sa` — the PRODUCER's slot, a cross-node quantity** — which is exactly my own open half (`emit.cpp:3170-3173`, `zd_out[i] - zd_out[_k] + _xh` across runs). **Two independent lines met on one mechanism for the first time on this thread.** Checkable with **no rebuild** on the `.s` they already hold. ⛔ Scope stated explicitly: the *arms* are proven, the *polarity* is not — a mixed result kills it for the price of a grep. Killed a fourth candidate before sending it (`XSAQ` looks like a missing rbp arm in `bb_var`; it has exactly 7 users, all `bb_match_*`, so the split is by design), and corrected `x86_asm.h:887`'s blanket *"no rbp arm anywhere"* — there is one, Icon-generator-gated, 0 for Pascal. Banked in the row's baton, **not only in a message** — because the postoffice lost an hq_C→ceo message unread this same session.

### ⭐ THE UNSAYING I OWED, RESENT
ceo cleared my message unread (their own pipe defeated `check`). Resent: I had **routed seat03's bisect attribution upward as correct** — `69a0e1d1` first-bad for the Pascal bool-family truncation. **It is wrong.** The real introducer is `3da1168c`, twenty days earlier, byte-identical at `lower_pascal.c:125` in **both** of that bisect's own anchors — settled by two `git show | grep`, no rebuild. ⭐ **`git bisect` assumes one repository and one oracle; this workspace has neither** — corpus moved under a SCRIP bisect (`32be25c71`, 77 seconds away), so the flip had no SCRIP commit responsible. **Pin the oracle before bisecting the code.** Blast-radius checked: zero occurrences in `GOAL-CEO.md` or any sovereign file, so the false premise never landed. seat03's *observations* were all correct — only the anchor was wrong.

---


**s276 (2026-08-28, Opus 5, FLEET-8) — ⭐⭐ THE RANK-0 SHARED-INFRA ROW IS CLOSED, AND THE OTHER TWO RESULTS BOTH RAN AGAINST ME: I VOIDED A GOOD GRID ON AN ARGUMENT, AND AN ICON BOARD HAD BEEN GRADING ZERO FILES.**

Inbox 2 (seat07 park, ceo rulings), both drained. Pristine `-O0` at SCRIP `43fa94a0`.

### ✅ `bb-label-prefix-pascal-suite-regression` — DONE, full SHARED-NODE control set re-proven
Cure `840d05f7`: `a01fe9f6` signalled ports **in band** (`\x01`+port prepended to a label line) and `x86_internal_resolve` consumed **any** `\x01` plus the byte after it — but Pascal record-layout descriptors legitimately emit `\x01` inside `.string` data, so **two bytes of the program's own data were silently deleted.** One mechanism explains every symptom seat12 saw: m4-only (the resolver runs in TEXT medium, never BINARY), record/variant-record families worst hit (they emit `\x01` in data), and `output mismatch` rather than crash (nothing malformed — the data is simply wrong).
**Verdict set at HEAD:** Pascal m4 suites **96/96, 0 fail** (the DONE-WHEN) · loose PASS=142 FAIL=12 · SNOBOL4 **m3 893/893 · m4 893/893 · FAIL=0 SKIP=0 MISSING=0** rc=0 · Icon **PASS=251 FAIL=15 BADEXIT=1 MISSING=0** = the control in `840d05f7` · both blocking gates rc=0. ⛔ **SNOBOL4 denominator moved 615 → 893 since s275** — read `FAIL=0 · SKIP=0 · MISSING=0` over the printed total, never a remembered number.
⛔ **Recorded as a NARROWING, not a redesign.** In-band signalling over a channel that does not reserve its signal byte stays fragile by construction; today's line-start discriminator rests on the empirical claim that a data `\x01` never lands at line-start, which **nothing enforces and no gate checks**. Minted `label-port-marker-out-of-band` rank 2 per ceo's ruling, with a DONE-WHEN that demands the adversarial witness today's HEAD would fail. **Closing the correctness row must not close the design risk.**

### ⛔ I VOIDED seat07's MEASURED GRID ON AN ANCESTRY ARGUMENT, AND RE-MEASURING PUT EVERY NUMBER BACK UNCHANGED
seat07 parked `pascal-m4-for-spine-leak-64b-per-iter` with a 9-kernel grid taken at `79873cc3`. `git merge-base --is-ancestor a01fe9f6 79873cc3` = **YES**, so their base carried my rank-0 regression. I ruled the grid unusable, set the row BLOCKED, and **published a mechanism** — that the regression explained an anomaly they had flagged (failing set changed *membership* while holding *count*). Then I measured: **byte-identical grid on the cured base, 10/10 deterministic both directions.** Their numbers were right as published.
⭐ **Ancestry establishes that a variable was UNCONTROLLED; it never establishes that it was OPERATIVE.** I had the first and asserted the second. Refusing an uncontrolled baseline was correct and I would do it again; publishing an unmeasured cause was not. ⛔ **The tell: the hypothesis was load-bearing twice over** — it excused the grid *and* resolved the one anomaly I couldn't otherwise explain. **A story that closes your open question as a free side effect is being selected for closure, not for truth.**
**Consequences, all against my ruling:** the membership shuffle is *still* unexplained and `a01fe9f6` is now eliminated as its cause (seat07's two-unrelated-events reading stands); seat07's fix (b) is **not** rehabilitated — the grid's invariance is evidence their original judgement was right and my second-guess wrong. Row BLOCKED → **FREE** with the re-measured grid as its verified baseline. Receipt: `FINDING-2026-08-28-hq_C-an-ancestry-argument-voided-a-good-grid-and-measurement-put-it-back.md`.

### ⭐ AN ICON BOARD HAD **THREE** INDEPENDENT REASONS IT COULD NOT MEASURE — 0 FILES GRADED, NOW 476
`test_corpus_icon_parser.sh` exited rc=2 `icon_parser compile failed`. Refusing was correct; it had been refusing *instead of grading*, for unknown duration, in this seat's **#2** language. Three faults, each alone fatal and all producing that one line: bare **`icont`** (not on PATH; `icont_bin()` exists precisely so nobody re-derives it); **`$REPO_ROOT/../corpus`** with `REPO_ROOT` already the seat root → `/home/corpus`, a path that **could never have matched on any tree, ever**; and the sources **relocated** by the 2026-08-24 re-grid.
⭐⭐ **Fault 2 means the board was broken BEFORE the re-grid that broke it again** — so the obvious, correctly-diagnosed re-grid repair alone would have left it printing the same rc=2 and looking like one unfixed bug. **A refusal is a scalar; the thing behind it need not be.** The natural loop (fix, re-run, still red, conclude the fix was wrong) misreads *correct and incomplete* as *incorrect*. Same shape as the `-O2` framing on RUNG C-0, where `-O1` fails identically and the boundary was never where the row name said.
Cured at `43fa94a0`: resolve by search, refuse on unresolvable, go through the shared accessor. **0 → 476 files** (parser 476/476, recognizer 268 pass / 208 empty, 0 crashes, rc=0). **Negative-tested both arms** — sources absent rc=2, oracle absent rc=2 with no bare-`icont` fallback. ⚠️ **Still owed:** the recognizer's **208 empty** results are counted but ungraded — nothing says whether an empty parse is a defect there. Surfaced by this cure, not answered by it.


**s276b addendum — THE 208 WAS MINTED, NOT FOLDED, AND THE TWO-MINUTE CHECK IS WHY.** ceo left the recognizer's 208 ungraded-empties to my discretion. Witness found in two minutes — `corpus/tests/icon/parser/augop_add.icn`, three lines (`procedure main(); x +:= 1; end`): parser emits `(proc main () () ((expr (id x)) (expr (int 1))))`, **recognizer emits `(compiland "")`**. The recognizer recognizes *nothing* on a valid program, so "empty is legitimate here" is false and folding would have buried a real gap under a count. Row `icon-recognizer-vacuous-compiland-ungraded` minted rank 2 FREE; DONE-WHEN demands all 476 in a graded class with **zero ungraded**, and rc=2 refusal rather than a green count where legitimacy cannot be established.
⭐⭐ **The shape, and it is the sharpest thing I found this session: the recognizer emits SUCCESS-SHAPED OUTPUT THAT CONTAINS NOTHING** — `crash/timeout=0` across all 476, every loud channel clean — **and the board's own classifier already special-cased the exact string `(compiland "")` to bucket it.** The vacuous result was known well enough to **pattern-match** and never well enough to **grade**. ⭐ **A value recognised precisely enough to be counted is not thereby a value anyone decided was correct.** Bucketing reads as handling; it is the step *before* handling, and it leaves a named bucket and a stable count that look exactly like a resolved question. ⚠️ Recorded and explicitly NOT claimed: the parser drops the `+:=` on that same witness, so its `476/476` says the parser is **non-empty**, not **right** — a verdict I have not taken and will not let a green number stand in for.

### ✅ RANK-0 `pascal-refs-regen-refs-half` — DONE, AND THE ROW'S REAL QUESTION ANSWERED **NO**
⛔ Scope correction I am recording rather than closing over: **the refs half was already landed by seat04 (`32be25c7`) before ceo minted this row** — our messages crossed, and the board was at 96/0 when I picked it up, not 14/82. What remained was my own caveat, so I did that instead of re-running a regen.
⭐ **I validated seat04's regen against `fpc -Miso` DIRECTLY, never against SCRIP** — a SCRIP-vs-ref check cannot tell a correct ref from one pinned to SCRIP's own output. Over the 58 loose pairs: **MATCH=56 · MISMATCH=1 · FPC-WON'T-COMPILE=1.** The regen is genuinely oracle-correct; measured, not assumed. seat04 separately confirmed they sourced every ref from fresh fpc runs, never from old-ref.
**The one mismatch is the finding.** `read3.ref` carried width 10 while everything else moved to 11 — because **fpc cannot run `read3` at all** (Runtime error 106 on the ISO `while not eof do read(i)` idiom with its own `.in`). So it sits on the exception list for a legitimate reason (*the oracle cannot produce this ref*) and was **thereby also, silently, exempted from the width correction — an unrelated concern.** ⭐⭐ **AN EXCEPTION GRANTED FOR ONE REASON IS INHERITED BY EVERY MECHANICAL PASS THAT FOLLOWS; an exception list is a set of files that quietly stop receiving corrections.** From outside, an exempted file and a correct file look identical — both are simply not in the diff. Fixed (`16e2677c9`): value from the pre-existing ref (right, unreproducible by fpc), width from the oracle (verified 56×), **neither half from SCRIP**. m4 loose 141→**143**, FAIL 13→**11**; suites **96/0** both modes; benchmarks 9/9.
⭐ **And the classification bought a second result: an aggregate failure count hides structure.** By signature, `FAIL=13` is one whitespace artefact, **one cluster of seven**, and four singletons. The cluster — `boolarg boolassign boolchain boolidx boolmix boolnot boolptr` — emits **truncated** output with the values it *does* emit **correct**: early termination, **one defect not seven**, and the first-value-correct is evidence *against* a boolean-arithmetic reading. Minted `pascal-bool-family-truncated-output-one-defect-not-seven` with a do-not-file-as-seven instruction.

### ⛔ seat07's ROW: THREE OF MY HYPOTHESES REFUTED, AND I STOPPED HANDING OUT CANDIDATES
seat07 built the approved three-pass split and proved with `SCRIP_ZD_OMEGA_HEAD=0` that the relocation is **byte-for-byte a no-op** for every already-resolving node — then: intmm/queens/perm FAIL→PASS, **sieve PASS→FAIL**, `quick` crash→**silent wrong answer**, bubble unchanged. Two different release-computation mechanisms hit the identical sieve regression, which points away from pop arithmetic entirely.
⛔ **My `g_zd_read` lead was structurally impossible and I retracted it before it cost them a day:** `emit.cpp:2537-2538` refuses a run outright (`why="opnd"`) unless every operand's producer is already in `run[]` at an earlier position, and that check is **unconditional** — not bypassed by `nblob`, which only feeds gin/oin. So an accepted run has in-run operands by construction and the subtraction is always within one coordinate system. That is my **third** refuted hypothesis on this thread (`flat_all_zd`, then `g_zd_read`).
⭐ **Grounded candidate, matching their "treated differently BY SHAPE":** the three **ω-pop STEAL paths** (`emit.cpp:3146` `_uw`, `:3157` `_ej`, `:3165` `_zw5`), each firing on `zd_on[i] && zd_wp[i] > 0`. A never-armed node can never enter them; arming makes nodes newly eligible, and a steal **redirects `node_ω` to a pooled target** rather than adjusting arithmetic — which predicts `quick`'s crash→**silent wrong answer** exactly, the one result they called unexplained. It also explains why two different pop mechanisms give the identical sieve regression: **neither is the cause; the arming is.**
⭐ **Having been wrong three times, I sent an INSTRUMENT instead of a fourth guess:** env-gated one-line prints at the three steal sites (node index, op, `zd_wp[i]`, which steal fired), then build sieve at `SCRIP_ZD_OMEGA_HEAD=0` and default and **diff the steal sets**. A node present armed and absent baseline names the mechanism with a witness; identical sets clear all three at once. Built as a keeper, not scaffolding.

### ⛔⛔ THE PASCAL BOARD WENT RED BOX-WIDE AND THE OBVIOUS READING WAS BACKWARDS — CAUGHT ONLY BY THE POST-REBASE RE-PROOF
My push rebased onto `358179bb` (*"pascal: write/writeln default integer field width 10→11, match fpc -Miso"*), and the REBASE-BASELINE COROLLARY re-run caught Pascal m4 suites at **14 pass / 82 fail** (from 96/0) and loose at **PASS=19 FAIL=135** (from 142/12). ⛔ **The compiler was RIGHT and the `.ref` corpus was STALE.** I asked the oracle instead of inferring: `fpc -Miso` on `writeln` of integer 7 prints `          7` — **width 11**, exactly what SCRIP now emits, while the refs carried width 10. `358179bb` landed the codegen half of `pascal-refs-regen-from-fpc-oracle` without the refs half.
⭐ **The danger was misdiagnosis, not the bug.** An 82-failure board reads as catastrophic regression, and the natural first move — revert the suspect commit — restores a compiler that disagrees with its own oracle. Routed to ceo as urgent with *"do not revert 358179bb"*, warned seat07 (mid-cure, with my approval) that the Pascal arm was unusable that day and that their **rc=139 signal was immune** to a width shift so their grid stayed readable, and told seat04 to **regenerate from fpc, never from SCRIP output** (self-referential oracle — the trap I already have a FINDING on). seat04 landed it (corpus `32be25c7`); I re-verified: **suites back to 96/0.**
⭐ **seat04 returned two corrections to me and both were right:** my ruling's `{$mode objfpc}` claim was wrong (they measured `fpc 3.2.2`: `sizeof(integer)=4` already), and my ruling's evidence had scoped to the 58 loose pairs and **never covered `crosscheck/`** — which is where 82 of the failures were. They caught it before landing.

### ⭐ THE CLASS THAT SHOWED UP THREE TIMES IN ONE SESSION, ONCE AS MINE
**A defect is reported at the width of the lane it was found in, and nothing in the finding says so.** seat04 reported `scoreboard.sh`'s dead corpus path as a *Pascal* defect; I measured all seven arms and **six of seven are dead** (every `$REPO/test/<lang>` is a fossil path, `$CORPUS/pascal` predates the re-grid; only the snocone crosscheck arm resolves) — reported at one-seventh its width, through no error, because the reporter checked the arm they stood in and `find … 2>/dev/null` silences the rest. Same class: `a01fe9f6` titled as "broke Pascal record suites" when it was shared label infra eating `\x01` for every frontend; hq_P's *"all three guards are decidable at emit time"* holding at every site they enumerated; **and mine** — I cleared `\x01` on json-match and string_pattern and called it an all-clear, and hq_P pointed out **porter, the witness the campaign is about, was not on my list.** ⭐ **The reader-side defence is the half that scales: when a finding names one language, check whether the MECHANISM is per-language before believing the count.** Two minutes multiplied that finding by six. Rows minted: `scoreboard-all-language-paths-dead-total-zero`, `corpus-suite-harness-extract-valueerror` (the latter flagged unverified-by-hq_C so its taker reproduces rather than trusts).

### ⛔ THE FLEET-BLOCKING COVERAGE GATE WAS ALREADY CURED, AND UNDERNEATH IT THE GATE WAS GREEN IN THE WRONG DIRECTION
ceo routed hq_P's box-wide `make test` blocker. It was **already cured** by `fa1d2b8f` landing under me — but by a **repoint** of a stale ROWD pointer, which is a treadmill. ⭐ **A ROWD coverage claim is satisfied by the row being OPEN**, so a *completed* row red-gates `make test` for every seat while an *undispatchable* row satisfies it **forever**. Measured witness for the worse half: `tests/prolog` (261 files) was covered solely by `prolog-parser-corpus-vacuous-gate-422-files`, which had a task file and **zero rows in `QUEUE.tsv`** — unpickable — and whose work had **already landed** at `b362f2a3`. It stayed "open" only because nobody could close it, and that is exactly what kept the gate green. Cured in the order that does not red-gate the fleet: reclassify `tests/prolog` ROWD→**GATED** first (GATED 21→22, ROWD 6→5), **then** close the row; and the gate now **fails on a ROWD row with no queue row**, negative-tested by removing one from a copied `QUEUE.tsv`. `make test` rc=0. ⚠️ Residue named: that Prolog harness tolerates `TOTAL*5/100+1` = **14 crashes** before failing, and passes today with 4.

### ⭐ seat07's ROW: CO-OWNERSHIP TAKEN AFTER FOUR ATTEMPTS, AND A DEAD END I KILLED BEFORE SENDING IT
seat07 got **+4/−1** (intmm/queens/quick/perm fixed, `sieve` regressed) and bisected the regression to *arming alone* — `zon[i]` flipping 0→1 — not to their new pop math. My first answer was `g_emit.flat_all_zd` (`emit.cpp:2802`), TRUE only when **every** node is armed: a whole-graph mode switch that fits their evidence exactly. ⛔ **I checked its consumers before sending and it is wrong** — both (`:2827`, `:3166`) are gated on `pl_cells_graph`, **Prolog only**, so it cannot touch Pascal. ⭐ The real candidate is **their own bug one level up**: `emit.cpp:3170-3173` computes `g_zd_read[_zj] = zd_out[i] - zd_out[_k] + _xh` — operand addressing as a **difference of `zout` between a consumer and a producer that may live in a different run** — and `_xh` carries MATCH_BEGIN/DEFER/frame terms and **zero** references to `run[]`/`claim[]`/`rpos[]`. They fixed the POP math; the READ math has the identical hole, and a pass-2 ω-discovered run creates cross-run producer/consumer pairs **for the first time**. Split: `zd_plan` stays theirs, the downstream cross-run `zout` question is mine.

### ✅ BUCKET A CUT AND PUSHED (SCRIP `69a0e1d1`) — AND hq_P's 7 Ir WAS ONE TOO MANY
`rt_cap_open_plain`: a second entry planted **past** the three guards. `rt_cap_open` keeps all of them and **falls through** into it; `cap_name_plain()` picks the callee at emit time, case-aligned with the bytes the adjacent `lea` bakes — NULL → guarded (guard 2 handles it), `""` → guarded, `"*X"` → guarded (guard 3 routes to ARM B), `"V"` → plain. **Guards deleted: zero.** ⛔ **Honest number, correcting hq_P's downward, disassembled rather than counted by eye:** `rt_cap_open` @`5d700` is `endbr64` + 6 guard insns = 7, body starts `5d71f`; the specialized entry must **re-pay `endbr64`** (an indirect target in BINARY medium — required, not decorative), so recovery is **6 Ir/call, not 7** → 6 × 1,151,998 = **6,911,988 Ir = 0.83%** of porter, not 0.96%. ⛔ And a cost in the other direction, disclosed rather than netted away: the guarded path now falls through the new entry's `endbr64`, so computed-name captures pay **+1 Ir**. −6 on the common path, +1 on the rare one. Unit: **instructions**, no speed claim.
⭐ **Guard 3 now has a PRODUCTION SITE, not just the bomb condition I argued from:** `lower_snobol4.c:1653` mints computed capture names as `snprintf(pb, "*%s", bn)` whenever a deferred target is not a simple variable. It was never theoretical.
**Verdict set, pristine `-O0`, and RE-PROVEN AFTER A REBASE** that replayed my commit onto four upstream commits including a `lower_pascal.c` change — every arm byte-identical across both runs: SNOBOL4 m3 893/893 · m4 893/893 FAIL=0 SKIP=0 MISSING=0 rc=0 · Icon PASS=251 FAIL=15 BADEXIT=1 MISSING=0 · Icon parser 476/476 · Pascal m4 suites 96/96 · both blocking gates rc=0.
⭐ **Green board necessary, never sufficient — both directions witnessed by hand:** `$ V` → `rt_cap_open_plain`, prints `HE` in m3 and m4; `$ *($N)` → **guarded** entry, output **byte-identical to `sbl -bf`**; `$ *F()` and `$ *(N "X")` also guarded. ⚠️ **A result that looks like a leak and is not:** `$ *N` with N a simple variable routes to `_plain`, because `sno_cap_name_strict()` resolves it to the plain name *before* `op_sval` is set — chased down rather than shipped past. Three regen scripts run in the RULES order, all reporting no changes, and **verified genuine rather than silent**: zero of the 20 benchmark `.s` and zero demo `.s` reference `rt_cap_open` at all.

### ⭐ CO-REVIEW GIVEN, ROW NOT TAKEN — `pascal-m4-for-spine-leak` (ceo re-dispatched to seat07, who flagged before touching `emit.cpp`)
Not mid-attempt and never claimed it; I had set it FREE with a verified baseline precisely so it could be picked up. Gave seat07 the shared-emitter read instead of the row. **Root cause of why their attempt (a) was inert, in the code's own terms:** `emit.cpp:2542` resets each run's depth accumulator to **zero at its own head**, while the back-edge correction at `2554-2555` searches `gback`/`oback` across **all** `n` nodes with `zon[]` set and then computes `zgpop[i] = _wzdepth - _gbpre` — **subtracting two depths measured from two different runs' zeros.** ⭐ It is correct for SNOBOL4 **by construction, not by design**: `bb_src_note` makes every *statement* a head, and a statement boundary is a *real* zero of spine depth, so all runs genuinely share a baseline. ⛔ A pass-2 ω-discovered head is **mid-statement** — its zero is fictional, which is exactly seat07's observed `gpop=-288`. Extending `zd_omega_head` (`:2478`, returns int-as-boolean) arms the run and leaves the baseline wrong; to seed one it must return **which predecessor discovered the node**. ⛔ **Guardrail I asked for explicitly: their opcode-inertness argument (no other frontend builds `IR_BINOP_TEST`) does NOT extend to a baseline change** — SNOBOL4's safety here is structural, so a change to how baselines are established can move SNOBOL4 without ever touching that opcode. Full blocking set owed, not just the Pascal arm.

---


**s275b (2026-08-27, Opus 5, FLEET-16) — ⛔⭐ I MOVED A LIVE THRESHOLD BY LANDING TWO ORACLE FILES, AND IT CLOSED A ROW.**

seat09 closed `icon-n3-scan-one-depth-authority` by correct procedure — pulled first, ran the row's literal DONE-WHEN (`P >= 249`), exit 0, and **flagged it to me unprompted** because it sat near a ruling of mine. That flag is the only reason this was found.

**Measured, same pristine binary at SCRIP `77a80557`, corpus the only variable:** corpus as is → `PASS=249 FAIL=15 MISSING=0 TOTAL=296`; with my two `.expected` moved aside → `PASS=247 FAIL=15 MISSING=2 TOTAL=294`. The whole `+2` is my own earlier landing — oracle files for two programs **already producing correct output**. Zero compiler change. Before my landing the criterion read NOT MET; after it, MET. seat09's attribution (`06a2ed7e` tab/move β-wiring becoming measurable) is **refuted by one grep — neither program contains `tab(` or `move(`.**

⭐ **`P >= N` IS NOT A MEASURE OF THE COMPILER. It measures the compiler PLUS the corpus size, and only one of those is the work** — and the two are correlated by workflow, since giving an ungraded program its oracle is exactly what a seat does while working a row. **`FAIL` is the growth-invariant quantity** (identical at 15 across both arms: adding a passing test cannot raise it).

⛔ **THE SAME TEMPLATE FAILED THE OPPOSITE WAY ON THE SIBLING.** `icon-n4` extracted P with `tail -1 | sed`, but `tail -1` on that runner is trailing explanatory prose — so `P` became an English sentence and the compare died `integer expression expected`, **rc=2 on every tree since it was written.** ⭐ **One criterion passed for free, its sibling could never pass, same shape and same runner** — and the two look nothing alike from outside, so finding one says nothing about the other.

**Census: 15 count-only DONE-WHENs**, including four import rows (the most inflatable shape there is — the deliverable *is* adding files) and the whole `icon-n1/n2/n3/n4` ladder keyed on the one PASS count I moved.

**Landed:** n3/n4 repaired to `FAIL<=15 && BADEXIT<=1 && MISSING==0`, REFUSING rc=2 on an unparseable summary. **n3 re-run: rc=0 — seat09's close survives its own repaired criterion, so it stands and I did NOT reopen it** (reopening would penalise a seat for my edit). n4: rc=1 for the right reason (`SCRIP_ZD_ICN_CPS` still in `emit.cpp`). `icon-n2` untouched — hq_P's, warned directly. Rule proposed to ceo. Receipt: `FINDING-2026-08-27-hq_C-a-pass-count-threshold-measures-the-corpus-not-the-compiler.md`.

⛔ **MINE TO OWN:** I added to a graded set without checking who counted it — **while writing about instruments that answer a narrower question than you think you asked.** ⭐ Third instance of that one class in a single session (a `</dev/null` Pascal board, a 16-bit `fpc` peer, now a PASS count read as a compiler measure).

### ⭐ PZ-4 OWNERSHIP ACCEPTED — hq_P OWNS THE MECHANISM, hq_C OWNS THE ROW

Lon raised Prolog-on-Byrd-Boxes with ceo directly; PZ-4 was rank-0 **ownerless** with two rank-0 crash rows and PZ-5 wedged behind it. hq_P settled it with a reversible default (owner=hq_C) rather than trading messages; ratified. The mechanism is `icon-n2` items 3–4 (generator α uses the host's reserved region; the landing stops `lea rsp,[rax+32]`) — hq_P's. The row is structural Prolog — mine, beside `prolog-term-to-descr-eradication`, whose sequencing I confirm as **PZ-4 first, then Term→DESCR rides the retained frames** (the other order rewrites Term handling twice, once against frames that do not survive resume).

⛔ **The park is honest, and the baton's own line ~344 says otherwise — it is STALE.** That line ruled *"seat05 does NOT wait — real work nobody else holds"*, correct when written; the release notes **below it** refute it (seat05 18:57, GC seam-scan hypothesis REFUTED 9/9 both directions; seat14 19:40, ADDENDUM 3 FCC hypothesis RETIRED). Both independent threads were worked to exhaustion the same day, and two seats picked the row up after that line and released "worked not done". ⭐ **Sovereign files decay toward BLOCKED; batons decay toward GO — same cause, because finishing work never edits the sentence that authorised it. Cite the condition, not the conclusion.** Un-park trigger named explicitly: hq_P's message that items 3–4 landed, **with the D2 witness at REPS=20** — never a REPS=5 delta (hq_P measured a vanished crash *and* a restored design invariant at 5; both evaporated at 20). ⭐ *"One crash condemns the row" is a sound RELEASE gate and a useless COMPARISON gate.*

**Prolog floor re-measured at the new HEAD, UNCHANGED: rung13 `0/5` · rung14 `2/5` · rung15 `1/5`** — identical to the floor recorded at `d4e6e971`, i.e. stable across every commit between, independently corroborating seat14's "unchanged since FLEET-8". A floor measured on two distant trees means future movement is signal, not drift.

---


**s275 (2026-08-27, Opus 5, FLEET-16) — THREE ROUTED ITEMS, ALL THREE ANSWERED BY MEASUREMENT. ⭐⭐ AND THE CHEAP, AUTOMATABLE METHOD I HAD FOR THE BIGGEST OF THEM IS RIGHT 15 TIMES OUT OF 16 WITH ITS ONE WRONG ANSWER INVISIBLE FROM INSIDE IT.**

Inbox was 3: ceo's ruling batch, seat09's Icon wrong-answer routing, ceo's stale-tree correction. Pristine `-O0` at SCRIP `4ddea506`; control arm re-run and green — **SNOBOL4 `m3 PASS=615 FAIL=0 · m4 PASS=615 FAIL=0 · SKIP=0 · MISSING=0`, rc=0 `GATE OK`.** ⛔ Note the denominator moved again, **365 → 615**, from the suite consolidations landing this session. Read `FAIL=0 · SKIP=0 · MISSING=0` over the printed total, never a remembered number.

### ⭐ ceo WAS RIGHT AND I WAS GRADING A STALE TREE — CONFIRMED THREE WAYS, MY ERROR

I had reported `pascal-uplevel-nested-proc-hang` un-landed. ceo measured otherwise and named my pull state as the fault. After `merge --ff-only` + pristine: **uplevel2 and uplevel3 both rc=0 and BYTE-MATCH their `.ref`s.** PULL-BOTH-REPOS-FIRST — the same stale-tree false-red class the census hit last week, this time from my side.

⭐ **The half of my T4 point ceo honored was the real one, and it is now cured:** `corpus/benchmarks/pascal/` was reached by **no gate at all**, so T4 could not distinguish *DONE+landed+ungated* from *DONE+not-landed*. Interim witness-pair arm landed in `test_gate_pascal_m3.sh` (SCRIP `a90b684a`), grading all **9** `.pas`/`.ref` pairs, negative-tested four ways, retiring when `pascal-refs-regen-from-fpc-oracle` lands.

### ⛔⛔ BUILDING THAT GATE, MY FIRST TWO MEASUREMENTS WERE BOTH FALSE — AND BOTH FALSE TOWARD RED

I measured **"7 of 9 Pascal benchmarks give WRONG ANSWERS"** and nearly wrote it up. **7 of the 9 open with `readln(reps)`**; under `</dev/null` reps is 0, every loop is skipped, and the all-zero board is real, plausible and meaningless. Cross-checking against `fpc` I then measured **"fpc disagrees with all 9 refs"** — also false: `fpc`'s default `integer` is 16-bit and overflows the RNG multiply, so the peer needs `{$mode objfpc}`. Both requirements are in that directory's `README.md`, which I had not read.

⭐ **The transferable half is not "read the README."** It is that **both wrong arms were confidently, symmetrically wrong in the same direction — toward a red board — which is the shape a correctness seat is primed to believe.** Same family as this file's own s274 retraction (*a number that confirms a known pattern gets re-quoted, not re-measured*). Corrected: **8 of 9 match; `quick.pas` is a genuine wrong answer** — SCRIP `biggest=10414`, `fpc` 3.2.2 **and** the `.ref` both `15505`, while sibling `bubble.pas` (same RNG, same seed, differing only in the sort) is **right** in SCRIP. Row `pascal-bench-quick-wrong-biggest` minted with `bubble` named as the ASM-DIFF-FIRST passing sibling. Also: m4 SIGSEGVs 5 of the 9 (already-tracked class, fresh evidence, and why the arm is m3-only), and the README's `perm` PAS-FOR-RECURSE frontier note is **STALE — perm is cured at 43300.**

### ⭐ seat09'S ICON ROUTING — VERIFIED INDEPENDENTLY, NOT ACCEPTED ON REPORT

`every EXPR` in **expression** context must FAIL. Oracle `icont`/`iconx`: `y`/`none`. SCRIP: `y`/**empty line**, in **both modes** — so `m3 ≡ m4` holds and this is a pure wrong answer, not a design-invariant violation. Confirmed seat09's statement-vs-expression split by measurement (`rung37_every_do_hello` statement-level matches the oracle exactly), which is what makes `lower_every`'s `(void) γ;` at `lower_icon.c:1112` the right suspect and not merely a plausible one. Row `icn-every-expr-context-discards-gamma` minted **rank 0** (Icon #2, wrong answer, root cause localized, and it gates seat09's `icon-n3-scan-one-depth-authority` from converging). Blast radius **measured**: 12 files under `corpus/tests/`, **21** corpus-wide.

⛔ The pre-existing `rung37_every_in_arg.icn` **does not reproduce it** (its `1|2|3` argument is resumable and takes a different path) **and had no `.expected` at all** — MISSING, counted in nothing, board green. Landed corpus `1f126166a`: oracle `.expected` for it and for `every_do_hello` (both PASS), plus `rung37_every_expr_nonresumable_arg.{icn,expected,xfail}` as the real witness. rung37 arm **PASS=13 MISSING=2 → PASS=15 MISSING=0 XFAIL=1**.

### ⛔⛔⛔ THE RECLASSIFICATION — AND THE TRAP INSIDE THE OBVIOUS METHOD

ceo routed seat04's 38 held-back conformance witnesses to me. The obvious method — **run each cited row's own DONE-WHEN** — is cheap, automatable, and not a matter of opinion. Over the **28** cited `conform-*` rows: **16 pass, 12 fail.**

⛔ **`conform-line-lastline-crash` passes its own DONE-WHEN and IS NOT CURED.** That criterion graded **two** witnesses, both green; `KEEP.md` cites **four**, and the other two still diverge in both modes. ⭐ **A DONE-WHEN that never looks at a witness cannot report that the witness is red — a row's own DONE-WHEN is evidence about its WITNESSES, never about the ROW.** The criterion did not lie; it answered a narrower question than I was asking it, which is this file's recurring class (`command -v icont`; my own s274 state-column count).

⭐ **What caught it was a SECOND, INDEPENDENTLY-BUILT witness list.** Had I derived the witness set *from* the DONE-WHENs — the tidier implementation — the two instruments would have been one and a live bug would have closed silently. **Agreement is evidence only when the instruments differ.** `f09_apply.sno` is the same shape a second time against `conform-local-opsyn-m4-empty`.

**Ruled: release requires BOTH halves** — witness green today (both modes, text and rc) **and** citing row passing its own DONE-WHEN. **38 released for conversion, 3 stay held, 17 Category-A unchanged.** `conform-line-lastline-crash`'s DONE-WHEN **widened** to all four witnesses and verified to say NO. It was the only one of the 16 still holding a live `QUEUE.tsv` row — the other 15 were already swept (LAW 4). ⭐ **The dispatch cost of the whole class was one row, and it was the one the method got wrong.**

Receipts: `FINDING-2026-08-27-hq_C-a-rows-own-done-when-is-evidence-about-its-witnesses-not-about-the-row.md` · `FINDING-2026-08-27-hq_C-nine-pascal-benchmark-witness-pairs-were-ungated-and-one-is-a-live-wrong-answer.md`.

⚠️ **Reported, not fixed:** `test_icon_all_rungs.sh:89` returns XFAIL **without running the program**, so a cured `.xfail` rots silently — the same defect class as an exception list that only permits failing. Both rows I minted therefore assert the DELETION of their own suppression in the DONE-WHEN. V2-5 gate-honesty bucket.

---


**s274 (2026-08-27, Opus 5, FLEET-12 → DUO mid-session) — ⭐⭐⭐ C-0 / MILESTONE 1 VERIFIED GREEN IN BOTH MEDIA BY HAND. AND THE PROBE THIS FILE NAMES AS THE M1 DONE-WHEN COULD NOT SAY YES ON ANY TREE FOR THREE DAYS.**

### ⭐⭐ C-0 IS GREEN — VERIFIED INDEPENDENTLY, NOT ACCEPTED ON REPORT

seat05 messaged that beauty's fixed point was restored by their `table-int-keys-and-nd-subscript` landing (SCRIP `a1d8cb02`) and explicitly asked me to verify before closing anything. **I did not re-run their gate.** Own hand measurement, `make pristine` `-O0`, SCRIP `d4e6e971`, run from the beauty directory:

| arm | bytes | md5 | verdict |
|---|---|---|---|
| m3 | **40,943** | `f20461f9114d50414fc925df1482c9b9` | ✅ byte-identical to `beauty.sno` itself |
| m4 | **40,943** | `f20461f9114d50414fc925df1482c9b9` | ✅ identical to the byte |

`cmp m3 m4` clean — **the `m3 ≡ m4` DESIGN INVARIANT holds.** Control arm, same tree: **SNOBOL4 `m3 PASS=365 FAIL=0 · m4 PASS=365 FAIL=0 · SKIP=0 · MISSING=0`, rc=0 `GATE OK`.**

⛔ **THE PIN MOVED AND THAT IS LEGITIMATE — DO NOT "RESTORE" IT.** Every figure above this section reads `40,971 / 6f1671c0`. That is the **pinned classic** (`.github/probes/m1-bisect/beauty_classic_fixedpoint.sno`), which still self-hosts to exactly those numbers — I measured it. The **live** `corpus/demo/snobol4/beauty/beauty.sno` is now 40,943 / `f20461f9` because Lon hand-edited it. ⭐ Both are fixed points; the flagship criterion is *output byte-identical to its own input* (Lon s117, all md5 pins VOID), so **the file is its own oracle and a changed file legitimately changes the number.**

### ⛔⛔ THE M1 DONE-WHEN COULD NOT SAY YES — REPAIRED, `.github` `7fd19a01`

This file says of `.github/probes/m1-bisect/check_m1_fixedpoint.sh`: *"exit 0 at HEAD — this IS the M1 DONE-WHEN."* It hardcoded `corpus/programs/snobol4/demo/beauty`, a path that **died in the 2026-08-24 corpus re-grid**; the 16 `.inc` files moved to `corpus/include/`. So it exited **2 on every tree, cured or broken**, from 08-24 to 08-27.

⭐ **THE PROBE WAS NOT DISHONEST, AND THE NARROW POINT IS THE TRANSFERABLE ONE.** It refused with **rc=2** and named the missing directory — exactly what REFUSE-NEVER-SKIP requires, and the opposite of the `make test` trap. **But honest refusal BOUNDS the damage; it does not REPAIR the gate.** A criterion that cannot say YES is trap #1 in this file's own § THE THREE TRAPS — *if nothing can make it pass, it is not a criterion* — and it sat there for three days while C-0 read red at the top of the sovereign file.

⛔⛔ **THE GUARD IS WHAT MISSED IT, AND IT IS s272 VERBATIM.** The check was `[ -d "$BEAUTY" ]` — **the container**. The container survived the re-grid while the **contents re-nested**, which is precisely the shape I wrote up at s272 (*"the subtree existing while the files inside it re-nested"*) and precisely why *a guard written against the last outage checks for the last outage*. ⭐ **Both probes now discover the directory BY THE FILE IT MUST CONTAIN** (`global.inc` — prefer `corpus/include`, then `corpus/probe/fwctx`, then a `find`), and assert `-f global.inc`, **never `-d`** on a container.

⭐ **MECHANISM, MEASURED NOT ASSUMED** (`src/driver/scrip.c:938-951`): the driver walks **up** from the source path and registers any `<ancestor>/include`, adding `"."` **last**. The live `beauty.sno` therefore self-hosts **from any cwd** — its ancestor `corpus/` has `include/`. The pinned classic lives under `.github/`, whose ancestors have none, so **CWD is its only resolver**. That is why the `cd` is still load-bearing for the probe, and why its cwd comment needed its **scope corrected, not deleted** — I first measured "cwd no longer matters" from the live file and that generalisation was **wrong**.

**NEGATIVE-TESTED THREE WAYS** (the honesty contract, all three arms): **rc=0** both arms FIXED POINT · **rc=1** says NO on a mangled source · **rc=2** refuses when no directory holding `global.inc` exists.

### ⭐ PROLOG — RULED ON seat07'S CONVERGENCE QUESTION: THE WALL IS PARKED, THE CURE IS MINTED

Three independent same-day passes (2× seat07, 1× seat01) converged, without contradiction, on one root shape: **retry/resume state at a fixed offset or in a shared global, unprotected across a γ-suspend↔β-resume window** — the BB FRAME-PLACEMENT CRITERION. seat07 asked for a sequencing ruling rather than taking it unilaterally.

⛔ **THE GAP WAS NOT THE PARKING — IT WAS THAT THE CURE HAD NO ROW AT ALL.** Three seats converged on PZ-4/PZ-5 while **neither rung existed in the queue**, so the only pickable row was the wall itself. Parking alone would have stalled Lon's s273 *"take this row and fix it."* Minted both, then parked:

- `prolog-pz4-gamma-retain-activation-frames` — **rank 0 FREE**, the keystone; carries all three FINDINGs as required reading, names the **retired** leads (448-vs-480 `resume_off`, the RTCC-veneer `rcx` clobber) so nobody re-walks them.
- `prolog-pz5-in-frame-resume-delete-pending-mailbox` — **rank 0 BLOCKED on PZ-4 by construction** (PZ-5 writes into the *retained* frame; it is not expressible before PZ-4). ⭐ Its DONE-WHEN asserts the **ABSENCE** of `g_pl_zf_pending_` (measured census: **29 refs across 4 files**) — a deletion row that only asserts passing tests lets the machine survive behind a green board.
- `prolog-multiclause-uninit-lexprep-frame` → `PARKED-AWAITING:prolog-pz4-…`, parked **around** seat07's preserved claim (s266 rule: a park is a verdict on a ROW, never an eviction).

**Re-measured seat07's floor myself** — pristine `-O0`: **rung13 `PASS=0 FAIL=5` · rung14 `PASS=2 FAIL=3` · rung15 `PASS=1 FAIL=4`**, name-for-name what they reported.

### ⛔⛔ RETRACTED SAME SESSION — "RANK 0 HAS STOPPED DISCRIMINATING" WAS **MY OWN BAD NUMBER**

⛔ **THE PARAGRAPH BELOW IS FALSE. It is kept, struck in place, as the record of how a wrong number passed three tellings.** **TRUE, verified two ways: rank 0 held ONE genuinely pickable row, not 33** (rank 1: 30 · rank 2: 55).

⛔ **THE ERROR, NAMED EXACTLY: I counted `QUEUE.tsv`'s STATE COLUMN and published it as what the picker SERVES.** The picker's rule is that **any claim file hides a row, DONE or not** — and **32 of my 33 carried DONE-marked claims**. ⭐ **The rule was printed in the `fleet` output I had already read the same session** (*"a row with ANY claim file, DONE or not, is hidden"*). This is the `command -v icont` class in my own hands, and this file warns about it in its own words: **an instrument that answers a narrower question than you think you asked will never say so.** I asked *what does the state column say* and published *what will be served next*.

⭐⭐ **WHY IT SURVIVED: IT AGREED WITH A STORY WE ALL LIKED** — s272's genuine rank-3 finding, hq_P's independent park, my own cursor. **A number that confirms a known pattern gets re-quoted, not re-measured.** And two seats "confirming" each other is worth nothing when both read the same column: **agreement is evidence only when the instruments differ.**

⛔ **ceo had APPROVED a rank-0 amnesty on this number and told me to execute it as my next act. IT WAS NOT EXECUTED** — it would have demoted rows out of an already-empty rank 0. Retraction routed to ceo and hq_P.

✅ **THE REAL DEFECT NEEDED NO RANK CHANGE:** 64 rows sat in the dispatch buffer carrying DONE claims, so every by-eye census over-counted. Cured with the instrument that already existed — `s4e_msg.sh sweep`, **248 → 184 rows**, nothing deleted, buffer backed up (LAW 4: the queue is a **dispatch buffer, not a memory**). ⭐ Then **the opposite of an amnesty**: rank 0 held one pickable row against four arming seats, so three correctness rows were **PROMOTED** — `conform-opsyn-operator-rebind-gz5-fatal` (SNOBOL4 #1, fatal) · `snocone-relop-parse-regression` (a regression) · `prolog-multiclause-fail-backtrack-segv` (Prolog live SEGV). ⛔ `pascal-m4-alpha-undefined-link` and `raku-recursive-sub-segv` deliberately **NOT** promoted: ceo ratified **one shape-test on one witness before any of the four point-fixes**, and promoting both would invite exactly the four separate fixes that ruling forbids.

~~*(false original, retained:)* ceo minted eight rows "rank 1" (5 arch-consolidation + 3 rivals) believing that was the top. Measured: 33 FREE rank-0 rows, 60 FREE rank-1 — they sit behind 33 pickable rows. ⭐ Same correction I routed at s272 (`corpus-suites-consolidation` minted "rank 1", actually rank 3 behind ~25), and hq_P hit it independently today from the perf side (`PARKED-UMBRELLA:hq_P-2026-08-27-rank0-picker-livelock`). Rank 0 has been used to mean *important* rather than *served next*, and has inflated to 53 rows. Costs nothing in DUO; mis-serves the moment a fleet re-fires. Re-ranks applied as custodian: arch engine 1 (dependency — it carries THE METHOD the other four inherit), languages 1, runtime 2, backends 2, build 3; iso7185pat 1, roast 2, bench-rivals 2.~~

⚠️ **A CORRECTION I OWED ceo THE SAME SESSION:** I quoted two of those deltas from memory of an earlier grep instead of re-reading the fields, and got two wrong (`languages` was already 1; `runtime` was 1, not 2). End state unchanged and applied; correction routed. **`RULES.md:105` — transcription is where provenance dies — and a rank is exactly the small field that moves under you.**

---

## LIVE CURSOR — hq_C (s272, superseded by s274 above)

**s272 (2026-08-24, Opus 5, FLEET-8) — ⭐⭐⭐ THE BOARD THAT CERTIFIES SNOBOL4 COULD NOT SAY NO. IT CAN NOW: rc=0 GREEN · rc=1 REAL FAILURE · rc=2 REFUSED. AND THE QUEUE IS SHAPED FOR 8 SEATS.**

### ⛔⛔ THE CORRECTNESS BOARD HAD TWO FALSE-GREENS AT ONCE — CURED, SCRIP `9873fe6e`

`test_corpus_snobol4.sh` is the primary SNOBOL4 correctness instrument and a member of the blocking set.
**(1)** `run_test()` returned **silently** when a `.sno` or `.ref` did not resolve, so any of ~40 **hardcoded** demo
rows could leave the board with no signal at all — not PASS, not FAIL, not SKIP. **(2)** The script's last
statement was a `printf`, so it **exited 0 with any number of mode-4 failures**, though `CLAUDE.md` has always
said mode-4 is the hard gate — the `make test` trap's exact shape, inside the blocking set.

⭐ **NEGATIVE-TESTED IN BOTH DIRECTIONS**, pristine `-O0`, SCRIP `9873fe6e`, corpus `e6c0d6b72`, re-proven after
the rebase that landed it: green **rc=0** (m3 362/362 · m4 362/362 · SKIP=0 · MISSING=0) · broken `$DEMO`
**rc=2** with all 22 rows named · one wrong `.ref` **rc=1**, denominator held at 362.
⛔⛔ **THE WHOLE BUG IN ONE ROW: the OLD script, on that same broken `$DEMO`, printed `PASS=340 FAIL=0` AND
EXITED 0.** Reported by **seat04** (`q-corpus-demo-path-mismatch`); measured, cured and tested here.

⛔ **THE FREQUENCY IS THE FINDING.** The demo paths were repointed **five times in one day** (`6ce46ebc`
`dac73079` `843cacfb` `1177e66e` `50923f55`), and **every break was caught only because a human noticed the
printed total had shrunk.** That is a person doing an instrument's job from memory — and it is why three
different SNOBOL4 totals (360, 362, 364) were each measured green on 2026-08-24 as the corpus moved.
⛔ **MY OWN s271 GUARD MISSED IT, AND THAT IS THE TRANSFERABLE PART:** it refuses when `$DEMO`/`$BEAUTY` is not a
directory — written against the outage I had just seen. The next one was the subtree existing while the **files
inside it** re-nested. **A guard written against the last outage checks for the last outage.**

⭐ **THE RULE, and hq_P reached it the same day from the perf side** (a watermark re-pinned as a 2.20x "win" that
was a two-day campaign plus a hand-edited workload): **an instrument must REFUSE or re-label when its basis moves
— never quietly report a better number.** `FAIL=0` is not a verdict; `FAIL=0` over the expected denominator, with
`MISSING=0`, is. Full receipts:
`FINDING-2026-08-24-hq_C-the-snobol4-board-could-not-say-no-and-a-moved-file-was-invisible.md`.

### ⭐ MEASURED BOARD — AND WHY IT IS **362**, NOT THE 364 THIS CURSOR CLAIMED AT s271

**m3 PASS=362 FAIL=0 · m4 PASS=362 FAIL=0 · SKIP=0 · MISSING=0 · rc=0.** This **agrees with hq_P** (362 at corpus
`e63689fae`). The s271 figure of 364 was true of the tree that produced it; the corpus has since shrunk
legitimately. ⛔ **Do not treat 362 as a regression from 364, and do not "restore" the difference.**
⭐ **hq_P's recommendation to ceo — that `CLAUDE.md` stop pinning a total at all and read `FAIL=0`/`SKIP=0` — is
now MECHANICALLY SUPPORTED, and this seat endorses it**: with rc=2 in place, the board itself refuses when its
denominator moves, so the pinned number is no longer the only thing standing between us and a silent shrink.
⛔ ceo owns the denominator pin; this is a routed recommendation, not a change made here.

### ⭐ QUEUE SHAPED FOR THE 8-SEAT FLEET (ceo `queue-shape-for-new-seats` + `mint-restoration-rows`)

Four lanes are now the **top four served** (the picker is rank-sorted with a stable tie-break, so file order
decides within a rank): `corpus-suites-consolidation` · `icon-corpus-semicolonize` · `strip-mechanical-carve` ·
`instrument-repair-bundle`. Restoration rows minted at rank 2 — `snocone-` / `raku-` / `pascal-restore-prezeta`
(Rebus rides on snocone) — and `beauty-comment-bug-witness` at rank 5. Six new batons written, two amended;
every DONE-WHEN is `bash -n` clean, and every top-four baton carries ceo's **STEP 0** (fix your own root's
`CLAUDE.md` digest — the permission-clean way to land the propagation that a cross-root write was refused for).
⛔ **CORRECTION ROUTED TO ceo:** `corpus-suites-consolidation` was **rank 3**, not the rank 1 ceo believed —
it sat behind ~25 rank-0 rows, so the picker would never have served it. ceo asked for it to be verified rather
than trusted; it was, and it was wrong.

### ⛔ THE OPEN TAIL — NAMED, NOT BURIED

`vlist-v05-m4-sigsegv-m3-m4-divergence` (seat03 holds it) is **no longer where its brief pointed, twice over**.
Both the disjunction-depth and the EVAL-JIT hypotheses were refuted by direct test; seat03 then **confirmed** by
gdb watchpoint that a disjunction box writes a **statically-computed rsp-relative offset that overshoots into
`environ[]`**, but only when reached via a deferred pattern-call pumped at match-end (`rt_dcap_pump`) rather than
a direct call. ⭐ That reconciles with this row's own earlier v01 exoneration instead of contradicting it — v01's
direct invocation never reaches the path. Witness minimised to 49 lines at `corpus/probe/vlist_select/v06`.
**Still unlocated: which fixed-offset computation is wrong.** The lead is the AOT `--compile` analog in
`emit.cpp`/`codegen_flat_chain_body`.

---

**s271 (2026-08-24, Opus 5, FLEET-4) — ⭐⭐⭐ SNOBOL4 IS `364/364` IN BOTH MODES **ON `main`**, ZERO KNOWN REDS. THE LAST STANDING RED (`TDump_driver` r12 SIGSEGV) IS CURED AT SCRIP `9df28b03`.** *(superseded by s272 above — that 364 described a corpus that has since legitimately shrunk to 362.)*

### ⭐⭐ LON'S NUMBER IS NOW MET ON `main`, NOT ONLY ON A CLEAN TREE

s270 measured 364/364 on a *clean tree* and 363/364 on `main`, the gap being `TDump_driver` — bisected then to another seat's `822bc8a1` and routed to `ceo`. **hq_C took the row back and cured it this session.** Measured at SCRIP `9df28b03`, `make pristine`, `RT_OPT=-O0`: **m3 PASS=364 FAIL=0 · m4 PASS=364 FAIL=0 · SKIP=0**; `TDump_driver` byte-equal to its `.ref` in both modes; gates `emit_no_lang`, `template_medium_invisible`, `bb_one_box`, `rtx_unit`, `no_handencoded_bytes`, `audit_m3_native_binary_arms` all rc=0; vlist ladder `v01`–`v05` + `c01`/`c02` PASS in m3.

⛔⛔ **THE CURE IS ONE LINE, AND THE BUG WAS A SAFETY ARGUMENT THAT INVERTED ITSELF.** `822bc8a1` landed two `zarm[]`-gated hunks in `zd_plan()` claiming they were *"inert for all current callers"* because `zarm[]` is populated ONLY by the `IR_MATCH_ALTERNATE` admission path (`emit.cpp:2479`). **The premise is true; the conclusion is backwards.** Because ALTERNATE is the *only* populator, the new conditions fire **exclusively** on ALTERNATE — inert for nobody. Asm diff across the boundary (`69449f94` vs `822bc8a1`, same program) is **30 lines in two `match_alternate` nodes**: a spurious `add rsp, 176` / `add rsp, 192` on edges landing at `_af`/`_s0`, which are ALTERNATE's own **retry wiring, not a scope exit**. RSP walks into the caller's frame; a later `match_begin` builds `rbp` over corrupted ground; the r12 restore `mov r12,[rbp-8]` (the only absolute r12 write besides the single pinned-VA load at `main`) reads a slot that never held r12 → **r12=0 with the pinned VA still valid** — clobbered, not uninitialised, exactly as the row's brief predicted.

⭐ **NOT A BLIND REVERT** (the brief forbade one): hunk 2 (`_wzdepth` arm-relative depth) is **KEPT** — it repaired a measured pred-disagreement WALL and is not implicated. Only hunk 1 is dropped, and dropping it alone cures the crash. Its intended beneficiary was the `IR_DISJUNCTION` arm path, which landed **separately** at `0e57de3b` via the `fc_geom` grant and does not populate `zarm[]` — **no current beneficiary, one measured victim.**

⭐⭐ **THE TRANSFERABLE RULE — "INERT" IS A CLAIM ABOUT THE CALLER SET.** `822bc8a1` certified itself on *"SNOBOL4 crosscheck 325/325"*; its victim `TDump_driver` lives in `beauty_suite`, **outside crosscheck**. An inertness claim verified on a corpus that excludes the affected program is not verified — and here **the gate's sole populator was the sole victim**: the very fact that made the change look safe (only one op reaches it) is what made it dangerous (that one op is the only one it can break). ⛔ Compounding blind spot: `beauty_suite` carries **zero checked-in `.s` artifacts**, so the drift sweep could not have caught it either.

⛔ **THE s270 REBASE TRAP FIRED AGAIN AND WAS CAUGHT THIS TIME.** First board was measured at `0e57de3b`+revert; `pull --rebase` then brought in `94dd91ba` (corpus path-flatten, `programs/` level removed, 200+ path refs rewritten). **The whole board was re-run pristine at the merged HEAD before anything was written down** — identical either side. s270's rule held under test: *re-run the board AFTER the rebase and BEFORE the push.*

⭐ **AND MEASURE THE SPLIT BEFORE BLAMING YOUR OWN CHANGE FOR ARTIFACT CHURN.** RULES.md step-4 regen churned many Icon `.s` files; emitting 5 of them under a purpose-built `0e57de3b` worktree vs the cured build gave **0 of 5 different** — the churn is **pre-existing drift** from three un-regenerated codegen commits, not this cure. Without that check the regen commits would have read as "the cure rewrote Icon codegen."

### ⭐⭐ AND ICON IS BACK AT ITS BASELINE — THE s270 CURE HAD BEEN GRADED ON ONE FRONTEND OUT OF THREE

⛔ hq_P bisected and **revert-proved** that s270's vlist cure `0e57de3b` cost **47 Icon programs** (232 → 185). Cured at `50997871`. **Icon `PASS=232 FAIL=31 XFAIL=30 TOTAL=293` — exactly hq_P's `15738e4a` baseline in all three columns, so that one commit accounted for the entire gap with no residue — while SNOBOL4 held 364/364.**

⭐ **THE PREDICATE WAS NOT WRONG — IT WAS TRUE, AND THAT IS THE DEFECT.** `IR_LIT(nd).ival > 0 && nd->n_operands > 2*ival` is equally true of Icon: `lower_icon.c:944-945` push 2N port operands, `:948` pushes N arm-results on top, `:949` sets `ival=n`; `lower_if` at `:954` builds the same shape, which is why the blast radius was **every Icon conditional**, not just the `|` programs. `IR_DISJUNCTION` is the one host three frontends converge on, so a language-blind predicate over it grants all three — re-routing `FRQ()` to the spine for Icon's producer while Icon's consumers still addressed the frame. **The exact producer/consumer split s270 cured for SNOBOL4, mirrored onto Icon.** ⭐ Cure = hq_P's axis: key the grant on **which ζ plane the consumers address**, which only the lowerer knows. `fc_geom` now also requires `fc_vdj_active(nd)`; `lower_snobol4.c` registers its disjunction through the **same mechanism `fc_vlit`/`fc_save` already use**. ⭐ **Not a per-op filter:** every `IR_DISJUNCTION` stays eligible, nothing is refused by op identity, and Icon's own become eligible by registering — no change to `fc_geom` needed.

⭐⭐ **THE RULE: A SHARED-NODE CURE IS GRADED ON EVERY FRONTEND THAT LOWERS TO THAT NODE.** `grep -l IR_DISJUNCTION src/lower/*.c` names the graders in one command. `0e57de3b` said *"364/364"* with no Icon line, and that reads as *"nothing regressed"* — **the verdict was sound, the SCOPE was dropped.** Same shape as measure-then-rebase, and same shape as `822bc8a1`'s *"inert for all current callers"*: **three defects in two sessions, all true statements missing their scope.**

⛔ **ON THE FC-MISS INSTRUMENT, SO NOBODY MISREADS IT:** `SCRIP_FC_AUDIT=1 | grep -c FC-MISS` took the Icon witnesses 10/5/5/15/5 → **0/0/0/0/0**. But the SNOBOL4 vlist ladder reads **nonzero** (10/15/10/5) on the *cured* tree, and that is **pre-existing** — identical at `0e57de3b`, which measured 364/364. **FC-MISS is only readable against a control run of the same program on a known-good tree.** hq_P's "negative filter, not sufficient" caveat was the load-bearing part of their message.

### ⛔⛔ A BOARD SHRANK 364 → 342 AND STILL READ `FAIL=0` — REPAIRED AT `dac73079`

`6ce46ebc` swept `snobol4/demo -> demo` **in the wrong direction**: the flatten created `corpus/snobol4/demo`, never `corpus/demo`, and `test_corpus_snobol4.sh` was **already correct** when it got rewritten. The runner then discovered **342 programs instead of 364 and reported `PASS=342 FAIL=0`**. 40 scripts repaired.

⭐⭐ **A CLEAN NUMERATOR OVER A SHRUNKEN DENOMINATOR IS THE MOST DANGEROUS SHAPE A BOARD HAS.** Every visible signal said green and the 22 losses were invisible unless someone compared the **TOTAL** to a remembered one. **`FAIL=0` is not a verdict; `FAIL=0` over the expected denominator is.** Caught only by re-running the board after a rebase — the measure-then-rebase rule's **third firing today and the first against another seat's push**. ⛔ Not fixed by reverse-sweeping, because *the obvious fix is the bug again*: one spelling (`$CORPUS_ROOT/demo`) matched no grep pattern and was found only by **re-running the gate**. ⭐ **Credit where due — three gates went red and ALL THREE FAILED LOUDLY**, naming the missing file; that is why this cost minutes, and it is worth recording the express-your-own-failure rule *succeeding* and not only being violated.

### ⛔⭐ CORRECTION, SAME SESSION: THE NUMBER IS **360/360**, AND MY OWN RULE IS WHAT CAUGHT ME

**A BOARD VERDICT NAMES BOTH HASHES.** Every figure below and above that reads `364/364` was measured at **SCRIP `9df28b03`…`1177e66e` with corpus at `b7ace5fe3`**, and quoted the SCRIP hash alone. The corpus then moved. **Re-measured pristine on BOTH trees current — SCRIP `1177e66e` / corpus `7291f5ead`: `m3 PASS=360 FAIL=0` · `m4 PASS=360 FAIL=0 SKIP=0` (360 total).**

⭐ **`FAIL=0` still holds; only the DENOMINATOR moved, and this time legitimately:** 364 − 4 = 360, the `crosscheck/library` quartet (`test_case`, `test_math`, `test_stack`, `test_string`) **deleted WITH its subject** when Lon made `library/` the Snocone import home. Verified directly — all four are absent at `7291f5ead`. ⛔ seat01 reported those same four as *live-red from the `lib/`→`library/` rename*; that report is **stale, not wrong** — they saw them before the deletion. **Expected SNOBOL4 totals are 360 now, not 364.** Icon is unmoved at `232/31/30/293`.

⛔⛔ **THE POINT, AND IT IS THE SHARPEST FORM OF THIS SESSION'S ONE LESSON:** I wrote *"a clean numerator over a shrunken denominator is the most dangerous shape a board has"*, ceo made it law — **and then I published a denominator that had already moved, because I named the tree I changed and not the tree I graded.** A SNOBOL4 board is a verdict on TWO trees; quoting one hash makes the number unreproducible the moment the other moves. ⭐ This is also why the shrink guard is worth more than any path sweep: it fires on a *missing subtree*, which is the illegitimate case, and stays silent for a *deliberate deletion*, which is this one. **The guard did the right thing by not firing.**

### ⭐ ALL THREE FRONTENDS GRADED ON THE SHARED-NODE CURE (RULES.md 6138860c), AND THE REGISTER CAPS ARE NOW LOUD

**SNOBOL4 `m3 364/364 · m4 364/364 SKIP=0` · Icon `232/31/30/293` · Prolog `PASS=93 FAIL=2 SKIP=94 ORACLE_MISS=0`** — pristine `-O0`, SCRIP `1177e66e`. Prolog is included because it lowers `IR_DISJUNCTION` too; ceo ruled a Prolog board rides the Icon cure's acceptance. hq_P independently re-measured SNOBOL4 **and** Icon on their own tree and agrees in every column, so both pins rest on two instruments rather than on one seat's word.

⭐ **hq_P's cap flag was right, and the measurement is sharper than the flag.** All seven `fc_*_register` tables silently dropped registrations at their cap; for `fvdj` — added this session — that withholds a grant the consumer still reads from the spine, i.e. **the producer/consumer split returning as a SIZE-DEPENDENT miscompile a corpus of small programs can never catch.** Now reported once per table, to stderr, **never env-gated**, plus `SCRIP_FC_REG_HIGHWATER=1` for peak occupancy. **Fixed as a CLASS, not one of seven.** ⛔⛔ **MEASURED: `beauty.sno` reaches `vlit = 256` against a cap of `256` — the flagship program runs at 100% occupancy with ZERO headroom.** Nothing overflows today (0 TABLE FULL corpus-wide) so it is not yet a bug — it is one literal away, on the program Milestone 1 is defined on. ⛔ Caps deliberately **NOT raised here**: `fc_vcap()` guards registration with its own hardcoded literals, so raising the arrays alone merely relocates the silent refusal, and raising both changes which nodes get cells — a codegen change owing its own graded board. Row `fc-register-caps-sized-by-guess` (rank 1 FREE) carries the trap, the figures and the three-frontend requirement.

### ⛔⛔ THE BOARD NOW **REFUSES** INSTEAD OF SHRINKING — THE MOST REUSABLE THING THIS SESSION BUILT

The `364 → 342` shrink happened **twice**, from two different causes, and the second time it defeated my own fix: `dac73079` repointed 40 scripts to `snobol4/demo` **correctly and verified** (that path existed, `demo` did not), and then the tree moved again within the hour — `snobol4/demo` ceased to exist and `demo` returned at top level. **Corpus paths have moved three times in two days.** ⭐ Chasing them with sweeps is a losing game and every sweep is another chance to shrink a board silently, so the board now **exits 2 naming the missing subtree** rather than discovering fewer programs. `DEMO`/`BEAUTY`/`INC` became `${VAR:-default}` so the guard is testable; negative-tested **both** ways (rc=2) and positive (364/364).

⛔ **MY FIRST NEGATIVE TEST OF THAT GUARD WAS WORTHLESS AND I NEARLY SHIPPED IT.** The script assigned `DEMO=` unconditionally, so my env override was ignored: it printed `364/364`, `rc=0`, and I had "tested" a nonexistent path. **A test that cannot influence the thing it tests reports the tree's health as the test's verdict.** Sixth instance of *an instrument must express its own failure* — and the first one I committed myself, which is the reason it is written here rather than filed against someone else.

### OPEN / NEXT FOR THIS SEAT

⛔ **`364/364` DOES NOT MEAN SELECTION EXPRESSIONS ARE FINISHED.** The named tail is `v05`: PASSES m3, **SIGSEGVs m4** — an **m3 ≢ m4 DESIGN-INVARIANT violation**, unchanged by this session, row `vlist-v05-m4-sigsegv-m3-m4-divergence` (rank 2). That is the next SNOBOL4 correctness item, and it is a *divergence*, not a corpus failure.

Also swept this session (row `sweep-free-rows-are-real`, pass 4): true-free 138→**142**, all 4 new rows verified LIVE by direct repro, 0 dead. ⭐ Found that the sweep's own documented method is broken — passes 1–3 persisted a **count**, never a **set**, so its STEP 4 reports **85** new rows against a true delta of **4**. Landed `/home/resources/postoffice/SWEEP-CLASSIFIED.tsv` so pass 5 does an exact `comm -13`. Receipt: `FINDING-2026-08-24-hq_C-sweep-free-rows-pass-4-a-count-is-not-a-baseline.md`.

Receipts: `FINDING-2026-08-24-hq_C-tdump-cured-an-inertness-claim-verified-on-a-corpus-that-excluded-its-victim.md`.

## LIVE CURSOR — hq_C (s270, superseded by s271 above)

**s270 (2026-08-24, Fable, FLEET-4) — ⭐⭐ RANK-0 DONE: `(A , B)` SELECTION IS CURED, `demo_treebank` PASSES, AND A CLEAN TREE MEASURES **364/364 IN BOTH MODES, ZERO FAILURES** (`0e57de3b`). PLUS STRIP WAVES 1, 2, 3a, 3b, 4a LANDED: THE PLATFORM AXIS IS GONE AND THE ζ SELECTOR IS ONE CONFIG.**

### ⭐⭐ LON'S NUMBER IS MET ON A CLEAN TREE — AND `main` IS ONE FOREIGN REGRESSION AWAY FROM IT

Lon s269 via CEO-13, rank 0: *"We want SNOBOL4 to be 364 out of 364, so get treebank fixed as a priority."* **Done.** Pristine `-O0`, clean tree (`69449f94` + cure): **m3 364/364 · m4 364/364 · SKIP=0**, ladder `v01`–`v05` PASS, controls `c01`/`c02` PASS. On today's `main`: **363/364**, the single red being `TDump_driver` — ⛔ **NOT this change** (bisected below).

⛔⛔ **THE ROOT CAUSE WAS NOT WHERE THE ROW'S OWN BRIEF POINTED, FOR THREE SESSIONS.** The s266 framing said *failure path* (arm 1 fails, spine not restored). Wrong: with multi-arm on, the selection yielded **NULL even when ARM 1 SUCCEEDED** — control `c01` was red too — so the value never reached the enclosing expression **in any case** and the backtracking story was a red herring. ⭐ The asm named it: the consumer reads its operand from the ζ-**spine**, but `bb_disjunction` never pushed a spine cell and wrote to a **frame** slot; `FRQ()` addresses the spine only inside a *granted flat cell*. Producer and consumer addressed different memory.

⛔⛔⛔ **AND THE GRANT WAS MISSING BECAUSE OF A PER-OP FILTER — the structure RULES.md already outlaws.** `fc_geom()` is a ladder of `if (nd->op == IR_MATCH_ARB) …`, and `emit.cpp` additionally requires every `case IR_*` to call `fc_geom` itself. `IR_DISJUNCTION` was in **neither** list, so a whole value-producing family was **silently denied storage, with no error anywhere.** ⭐ **Second instance beside `zd_wants()`** — the per-op-structure row must cover `fc_geom` too. The class: *a family member denied a resource by omission from a list, failing as wrong data rather than as an error.* ⭐ **The fix keys on STRUCTURE, not the op, deliberately** — `IR_DISJUNCTION` is shared by SNOBOL4 selection, pattern alternation **and** Prolog, so a blanket grant changes pattern codegen tree-wide; a *value* disjunction is the one carrying N arm-result operands past its 2N port pairs. `SCRIP_VLIST_ALT` retired in the correct direction (multi-arm unconditional, ON arm survives) — which mattered on a deadline, since a strip wave would otherwise have inlined the **broken** default permanently.

⛔ **TAIL NAMED, NOT BURIED:** probe `v05` passes m3 and **SIGSEGVs in m4** — an **m3 ≢ m4 divergence**. Corpus is green in both modes, so it is the family's tail, not its body. **Do not read 364/364 as "selection expressions are finished."** Row `vlist-v05-m4-sigsegv-m3-m4-divergence`.

⛔⛔ **`TDump_driver` IS ANOTHER SEAT'S REGRESSION, BISECTED** (3 runs/commit, pristine each, run from the program's own directory): `15738e4a` PASS 3/3 · `f2347178` PASS 2/2 · `69449f94` PASS 2/2 · **`822bc8a1` CRASH 3/3** · `ad56bb88` CRASH 12/12. Enters at `822bc8a1` *"zd_plan: fix arm-relative depth (_wzdepth) and gin/oin self-edge suppression"*. `r12` (the `cas_mark` GVA pointer) reads **0** inside a match while the pinned VA still holds a valid pointer — clobbered, not uninitialised. **The strip waves are clean.** Row `tdump-driver-r12-cas-mark-sigsegv` (rank 0), routed to `ceo`.

⛔⛔⛔ **PROCESS FINDING THAT COST HOURS — MEASURE-THEN-REBASE PUBLISHES A STALE VERDICT.** I measured wave 4a's board, **then** `pull --rebase`, **then** pushed. The rebase brought `822bc8a1` in **after** the measurement, so **wave 4a's commit message certifies a board for a tree that never existed on origin.** ⭐ **Re-run the board AFTER the rebase and BEFORE the push**, or the verdict names a tree nobody can check out. ⛔ It also produced two false conclusions of my own — I briefly believed my own `fc_geom` grant had broken pattern disjunctions tree-wide; the crash had arrived from outside my tree between two of my measurements. Same family as hq_P's *"one false suite voids the whole run"*, except **the falsifier came from another seat's push, not from a concurrent build** — a case the existing rule does not name.

Receipts: `FINDING-2026-08-24-hq_C-vlist-cured-by-a-per-op-filter-and-a-rebase-published-a-stale-board.md`.

hq_P pinned the six-language baseline (`ab1c6b16`) and released this seat's hold; CEO ruled the two flags. Four waves landed, each its own commit with its own proof. Tree: SCRIP `69449f94`.

| wave | commit | what | proof |
|---|---|---|---|
| 1 | `84b07d2d` | grep-provable dead code, 6 sites, −131 lines | board unchanged |
| 2 | `5354dc0c` | 2 rt.c `ZC_FRAME` tautology guards | ⭐ **rt.o BYTE-IDENTICAL** |
| 3a | `f2347178` | 95 never-taken `!PLATFORM_X86` guards, 74 files | 25/25 `.s` identical |
| 3b | `69449f94` | remaining 102 sites + `g_platform`/`bb_platform_t`/all 5 macros deleted | ⭐ **325/325 `.s` identical** |
| 4a | `ad56bb88` | ⭐ **ζ selector collapsed to ONE config**; CLI trio retired as hard errors | ⭐ **325/325 `.s` identical** + negative test rc=2 ×3 |

**`PLATFORM_X86` in `src/`: 197 → 0.** ⭐ **The board did not move once across all four waves:** corpus **m3 363/364 · m4 363/364 · SKIP=0**, `demo_treebank` only — equal to hq_P's independent pin. Gates rc=0 throughout (`emit_no_lang`, `template_medium_invisible`, `bb_one_box`, `rtx_unit`, `no_handencoded_bytes`, `audit_m3_native_binary_arms`).

⛔⛔ **WAVE 1's OWN "ZERO-RISK, GREP-PROVABLE" LIST WAS NOT.** The survey lists the `#error`-blocked ZC arms (`PROMOTE_ON`, `FRAME_DEAD5`, `STORAGE_FRAME_R12`) as wave-1 deletes. **They are TRIPWIRES, and `ZC_STORAGE_FRAME_R12` was never dead at all** (live read at `x86_asm.h:860`). `ZC_FRAME_DEAD5`'s guard protects a **measured 9-net-new-crash** config with **45 live `ZC_FRAME` refs** still standing — deleting the label while the arms remain *is* `ZR-RSPFB5-1`, the mistake that created the trap. **HELD to waves 4–5, where they collapse with their axes.** ⭐ A switch that is unreachable and a switch that GUARDS an unreachable config look identical to grep and are opposite facts.

⭐ **Two more transferable rules banked this session:** (a) *"nothing calls it" ≠ "nothing depends on it"* — `bomb_bytes` was uncalled but a live gate **prescribed it as the remedy**; both scripts retargeted, logic untouched, rc=0. (b) *a clean build is not evidence that a mechanical source transform preserved meaning* — the brace-matching sweep **crashed** on `{`/`}` inside string literals, so the verdict was taken on OUTPUT (325/325 `.s` byte-identical), not on compilation. Fourth instance of *an instrument must express its own failure*.

Receipts: `FINDING-2026-08-24-hq_C-strip-waves-1-3-landed-the-platform-axis-is-gone.md`.

⛔⛔ **WAVE 4a's TRAP IS THE MOST TRANSFERABLE THING THIS SESSION PRODUCED — AND IT WOULD HAVE BEEN A RUNTIME FAULT, NOT A COMPILE ERROR.** `g_zeta_mode` looks exactly like dead residue of the deleted `rt_zeta_set_mode`, and **no compiler source reads it**. But `bb_call_fn.cpp:363` emits `lea r12, [rip + &g_zeta_mode]` — **generated code takes its ADDRESS and loads it at run time.** It is KEPT deliberately. ⭐ **A global read only by EMITTED code is invisible to every grep of the compiler's own sources: deleting it compiles perfectly and dies later, inside someone else's program.** The strip's core hazard, stated generally: *the compiler's sources are not the only reader of the compiler's symbols.* ⛔ Do not let a later sweep "finish the job".

### OPEN / NEXT
1. **WAVE 4b:** the ~90 call sites whose `ZC_STORAGE`/`ZC_PORT` branches are now provably one-sided — harmless dead branches, so deferring them half-lands nothing. Then wave 5 (batched ZC), waves 6–7, then the `00-INDEX` dead-code carve. ⛔ Waves 4–5 are also where the three HELD tripwires (`ZC_FRAME_DEAD5`, `ZC_PROMOTE_ON`, `ZC_COL_GC`) finally collapse **with** their axes. ⛔ Also deferred with a reason: the emitted `g_zeta_mode != 2` comparison is now a one-sided branch **in generated code**; simplifying it changes emitted asm and forces a corpus-wide `.s` regen, so it needs its own byte-diff budget.
1b. ⭐ **`CLAUDE.md`'s ζ-selector section was REWRITTEN this session** — it documented the retired flags as live A/B surface and would have sent the next session straight into a hard error.
2. **Rows minted this session:** `icon-247-to-232-fifteen-program-gap` (rank 4) — a REAL, unattributed 15-program Icon regression between s247 and s267; the s247 number was **measured** (two agreeing runs), so the "old watermark was wrong" escape is closed. Surfaced by seat01 refusing to quietly re-baseline a stale DONE-WHEN.
3. **Ruled for seat01, routed to `GOAL-ICON-100.md`:** N-1 ACCEPTED on no-regression-by-name; ⛔ **no DONE-WHEN may carry a bare absolute score** as its gate (it names the instrument and demands no-regression against a baseline the executing session measures itself); the Prolog wire-stack crossing is **attributed PZ-ladder progress**, callee side explicitly not done.
4. **Flagged, not taken:** wave 3b consumed the JVM/JS/NET/WASM prologue/epilogue template bodies (backend content, but the same constant-false class wave 3 is defined by — raised to CEO rather than done silently) · `wasm_emit_data_segments_str` now unreferenced, left for Phase 2's `g_wasm_strtab` axis · `--target=jvm/js/wasm` never assigned `g_platform` even before this strip, a **pre-existing** CLI lie · `crosscheck/coverage/coverage_sno_nodes.s` is a checked-in golden for a program that **no longer compiles** (`FATAL lower_snobol4` GZ#5) — worth a row.

## LIVE CURSOR — hq_C (s269, superseded by s270 above)

**s269 (2026-08-23, Fable, FLEET-4) — PRE-STRIP REPAIRS DONE + THE SWITCH KEEP-LIST CERTIFIED. STRIP STILL HELD at the wave gate (hq_P's six-language scoreboard is the acceptance oracle and is not pinned). NOTHING DELETED.**

### BOARD, PRISTINE AT SCRIP `b7c044aa`: corpus **m3 363/364 · m4 363/364 SKIP=0** (`demo_treebank` only — the vlist red, seat03's row) · `emit_no_lang` rc=0 · `template_medium_invisible` rc=0 · `bb_one_box` rc=0 (**was 36/36 FAIL**) · `rtx_unit` rc=0 (**was FAIL**). Matches hq_P's pinned corpus number exactly.

### ⭐ CEO-11c STEP 1 DELIVERED — THE CERTIFIED SET-TODAY LIST IS **48**, NOT ~8 (`scripts/util_switch_census.sh`, reproducible)

| | |
|---|---|
| read by `src/` (`getenv`) | **350** |
| **certified SET-today (KEEP)** | **48** |
| **UNSET (die, before keep-classes)** | **302** |
| assigned ONLY in `.github`/`corpus` | **131 — PROSE, certifies nothing** |

⛔ **The 6x error was in the deleting direction.** Report 13's ~8 was substring-level. ⛔ **Two traps, both hit on the first honest pass:** *prose is not a setting* (131 names appear only in FINDINGs/READMEs quoting a command line — grepping the org brain certifies documentation as configuration); *a comment is not a setting, but ARGV is* (3 of 50 were comment-only; `SCRIP_ZONE` is genuinely set through `test_gate_zdp_on_null.sh`'s `ENVS=("$@")` door, which no assignment regex can see). Both are defended against by construction in the census script.

### ⭐⭐ CEO'S NAMED BORDERLINE IS ANSWERED WITHOUT ASKING LON — AND HALF THE FAMILY IS ALREADY ILLEGAL

CEO asked whether the ~36 `SCRIP_ZD*` flags are one instrument or 36 leftovers. **They are not dump flags at all** — `ZD` is ζ-**depth planning**, not ζ-dump. Measured polarity of all 37 consumers: **26 kill-switches default-ON** (`e && *e=='0'` — can only ever *disable*, emit nothing) · **7 opt-in observers** (instruments) · **4 raw-value**. And the 26 live inside `zd_wants()` (`emit.cpp:2095–2140`) as `if (op == IR_CUT) { getenv("SCRIP_ZD_PL_CUT") … }` — **twenty-six per-op admission gates, which is Lon's NO-PER-OP-FILTER law broken verbatim** (`SCRIP_ZD_ONLY`/`SCRIP_ZD_SKIP` take op *lists*). The strip is removing a violation, not making a judgement call. **KEEP 9** (`ZD_CENSUS/DEPTH/DIAG/GAP/TOTAL`, `ZDLOCAL`, `ZDP_TEARDOWN`, `ZDP`, `ZDP_BOMB`) · **DELETE 28**. Whether the per-op *structure* survives the switches is a follow-on row.

### ⭐ BOTH PRE-STRIP REPAIRS WERE THE SAME DEFECT CLASS: AN INSTRUMENT THAT CANNOT EXPRESS ITS OWN FAILURE

- **`test_gate_bb_one_box.sh` — 36/36 FAIL for the whole template architecture's life.** Matcher tested `extern "C" void bb_*(`; every box now returns `std::string` (144 of them), so it scored 0 on every box file and its only hit was the one place it should have scored zero. Repaired to the discriminator its own header always named (`_str` = helper). Five listed files absent — **all five deliberately deleted by named commits, none a regression**. ⭐ Once it could see, it found a real violation: `bb_binop_relop.cpp` held **two** dispatched boxes → split to `bb_binop_relop_val.cpp` rather than an exception (RULES.md forbids exception lists). **Negative-tested 4 ways.**
- **`test_rtx_unit` faildescr — a STALE GOLDEN, not an asm defect.** It printed asm and golden as **identical** and still said MISMATCH: `memcmp` compares 16 bytes, the report showed 3 fields. Byte-level printing named it in one run — offset 1, `mod_op`. `rtx_misc.S` stamps `MOD_OP_RT_FAILDESCR` (130) **deliberately**, landed by `descr-stamp-asm-mints` in **`6ba28e5e`, the same commit that cured Milestone 1**. An intentional feature was standing as an asm-vs-C differential red, behind which any genuine rtx regression would have been invisible. **Negative-tested 2 ways.**

⭐ **Both are the M1-probe class again** — *"BAD as expected" is not a measurement; a check must assert the SHAPE of the failure it expects, not merely its polarity.* Third and fourth instances now on the record.

### OPEN / NEXT
1. ⛔ **HELD:** strip waves 1–7, pending hq_P's six-language scoreboard pin. Certified list is ready; `bomb_bytes`/`bomb_text` deletion is scoped to wave 1 (CEO ruled; ping CEO with the deleting commit hash so the RULES.md exception clause retires in the same window).
2. `SCRIP_OPT` — DELETE-CANDIDATE **flagged, not taken**: row `opt0-residual-two-defects` is open against it; its only harness mention is a comment recording that `SCRIP_OPT=0` breaks the link.
3. **CLI-flag twins are not switches** — `SCRIP_ZETA_STORAGE` is the env twin of the documented `--zeta-storage=`. Deleting the twin is correct; deleting the flag would remove product surface. Flagged to CEO.
4. `sm_eval_subexpr` weak-abort landmine — minted as its own row per CEO, **not** to be fixed mid-strip.
5. `vlist-expr-alternation` (seat03) — redirected this session to the `disj_sigma_copy` arm-result addressing gap; my old-mechanism fix correctly does not transplant to the new `IR_DISJUNCTION` lowering.

## LIVE CURSOR — hq_C (s266, superseded by s269 above)

**s266 (2026-08-23, Fable) — LON: "Tag you are it. Take us to 100% SNOBOL4 and 100% Icon." DUO. BENCHMARKS 33/33 BOTH MODES — THE SUITE'S FIRST ALL-GREEN.**

### ⭐ CURED: one class, three symptoms — pattern blobs with ≥2 choice nodes had no safe records and no resume (SCRIP `d6eafac3`, corpus `0ac12b122`)

- **`json-match` + `json-match-fence` TIMEOUT** (the last 2 benchmark reds, row `json-match-capture-free-hang`) — CURED, byte-identical to `sbl -bf` on the real input.
- **Static stored patterns silently wrong at nc≥2** (`SCRIP_PAT_INLINE=0`, witness c03) — a class NOBODY had reported, found by generalizing the witness.
- Root: `blob_choice_rbp_scan` admits rbp records only at `nc==1` (one shared slot), so ≥2-choice blobs fell to the FLAT `[rsp+N]` record seat04 proved drift-broken; AND the blob's β entry resumed only nc==1 fence-free graphs — everything else answered total failure to re-entry. ⭐ The runtime tree conversion MANUFACTURES the second choice node: `dtp_rcp_tree` rewrites `ARBNO(X)` → `ALT('', SEQ(X, *ARB$n))`. ⭐ And the trigger discriminator was ONE TOKEN: `$name` in pattern position reroutes the whole pattern through the runtime builders — json-match's `$' '` vs json.sno's named variables is the entire difference.
- Cure: per-node 2-cell frame slots for every unsealed MATCH_ALTERNATE in a ≥2-choice blob (`choice_frame_candidate`, `sn4_choice_rbp_off_nd`; nc==1 legacy path byte-identical; killswitch `SCRIP_CHOICE_RBP_MULTI=0`) + blob β resumes at the TAIL (unique γ-exit node — body_root is the ENTRY, the wrong end), fence-tolerant except a fence AT the tail (β→ω IS commit semantics). ⛔ The "two ALT admissions must not be merged" ruling respected; seat04's measured-broken fence-relax untouched.
- Witness ladder banked: `corpus/probe/choice_records/c01..c08`, oracle-minted refs, controls included. Evidence: FINDING-2026-08-23-hq_C-multi-choice-blob-records-and-tail-resume-cure-json-match-family.md.

### BOARD, PRISTINE AT `d6eafac3`: corpus m3 360/361 · m4 360/361 SKIP=0 (`demo_treebank` only, deliberate) · benchmarks **33/33 m3 · 33/33 m4** · M1 fixed point both media · both emit gates rc=0. ⛔ Denominator is now 361.

### ALSO THIS SESSION
- **Lon's sys-perf ruling executed** (SCRIP `f8fac73d`): `scripts/util_perf_context.sh` — CPU-vs-wall attribution (`run`/`watch`/`stamp`), WAIT-BOUND numbers refused; hq_P notified (their bench lane). A TIMEOUT verdict now carries user≈wall proof (a starved false TIMEOUT is user≪wall).
- **Icon oracle BUILT and wired**: `/home/resources/icon-master/bin/{icont,iconx}` (Arizona 9.5, built s266), symlinked at `/home/resources/icon-build` (the scripts' default `ORACLE_BIN`) and `SCRIP/refs/{icon,jcon}-master` repopulated. The Icon front's "oracles ABSENT" line in the standing board is STALE as of s266.
- Queue hygiene: 7 rung-E/A rows parked SUPERSEDED (r10/r11 veneer ruling s259 made them moot — seat13's 3-for-3 pattern confirmed); `opt0-residual-two-defects` minted at rank 4 from seat06's report (SCRIP_OPT=0 is emergency-only, not on the 100% path).

### ⭐⭐ SNOBOL4 NEAR-100 BOARD — MEASURED s266 (Lon asked which suites are "a couple away"). SCRIP `205c6aca`, provenance-stamped, 4 jobs / 16 cores, peak load 7.66 (NOISY, not contended)

| suite | w | N | m3 | m4 | away from X/X |
|---|---|---|---|---|---|
| **beauty_suite** | 15 | 17 | **17** | **17** | ✅ **100%** |
| **bb_probes** | 10 | 188 | **188** | **188** | ✅ **100%** |
| **patterns** | 10 | 124 | **124** | **124** | ✅ **100%** |
| **crosscheck** | 10 | 201 | **201** | **201** | ✅ **100%** |
| **demos** | 15 | 23 | 22 | 22 | ⭐ **ONE** — `treebank`, root-caused below |

⭐ **AND THE CORPUS DENOMINATOR WAS UNDERSTATED — UN-SKIPPED s266 (SCRIP `a9f87275`): `demo/json`, `demo/json-match`, `demo/json-match-fence` all PASS in BOTH modes.** The runner excluded them on a comment reading *"HANGS (m3 AND m4) … needs >30s (currently: forever)"*; both cures landed today (`d6eafac3` tail-resume, hq_P's `a42571b7` fence0). **Corpus board is now `m3 363/364 · m4 363/364 SKIP=0`** — `demo_treebank` still the only red. ⛔ **A skip is a SILENT SUBTRACTION FROM THE DENOMINATOR:** these three were green for hours and no board could say so. Found by seat04 questioning a comment, not by any instrument. ⛔ **And the verification trap, re-committed by the seat that documented it:** json/calculator write `match_ms=` to **stderr** precisely so stdout stays byte-comparable — verifying with `2>&1` merges a timing line into the graded stream and manufactures a DIFF. hq_C hit it, and caught it only by diffing against the LIVE oracle, which agreed with scrip byte-for-byte while the `.ref` appeared not to. Same defect as `util_sweep_fold_arm_refs.sh`'s, one hour after writing that one up.
| **feature_test** | 5 | 157 | 156 | 156 | ⭐ **ONE** — `treebank-prepend` TIMEOUT (same class) |
| misc | 3 | 93 | 87 | 86 | 6–7 |
| probes_misc | 5 | 809 | 738 | 734 | 71–75 |
| **META** | **73** | | | | **98.2** |

⛔ `beauty_self` (w=20) scores 0.0 with N=0 — the ORACLE cannot run beauty (`sbl rc=139`), so the flagship is UNSCR and outside the number, exactly as seat04's census warned. ⭐ **Answer to Lon: FOUR suites are already X/X, and TWO more are ONE program away — and both of those are the SAME defect.**

### ⭐⭐ THE LAST CORPUS RED IS NOT A TREEBANK BUG — IT IS `(A , B)` SELECTION (root-caused s266, corpus `718139e70`)

`demo_treebank` and `feature_test/treebank-prepend` both die on the SPITBOL **selection expression** `(A , B)` (value of A if A succeeds, else B). SCRIP's default lowering (`lower_snobol4.c:727`) lowers **arm 1 only**, so a failing A yields **null**. treebank's `ListInsert4` does `ARRAY('0:' (IDENT(a(x)) 0, size*2-1))` → `ARRAY('0:')` → Error 164, then 235 one call later. **4-line witness:** `x = 'nn'; OUTPUT = 'a=' (IDENT(x) 0, 5)` — oracle `a=5`, scrip prints nothing.
- ⭐ **`SCRIP_VLIST_ALT=1 SCRIP_ZETA_STORAGE=frame-rsp` is BYTE-CORRECT on every rung** — the defect is cell-stack-specific, and frame-rsp is the working reference. ⛔ **cell-heap is ALSO wrong now**; the in-tree comment claiming it was fine is STALE.
- ⭐ **The asm names the mechanism, so the `zd_plan` framing can be retired as incomplete:** arm-1's recede runs through `n6_lit_string_β` — the enclosing CONCAT's left operand, *outside* the vlist — and pops its cell. **The failure path pops a cell belonging to an expression that already succeeded.** `SCRIP_ZD_VLIST_OMEGA=1` fires (it deletes exactly those pops) and is STILL wrong. Fix shape: catch the arm-failure edge AT THE VLIST BOUNDARY and restore the spine there; sound because the value rides the named `VLIST$n` variable.
- Ladder banked `corpus/probe/vlist_select/` — 5 rungs + **2 passing controls**. Row re-briefed, assigned seat03. Evidence: FINDING-2026-08-23-hq_C-treebank-is-really-the-comma-selection-expression.md.

### ICON BASELINE — FIRST MEASUREMENT SINCE THE ORACLE EXISTED (s266)

| suite | | | vs s247 watermark |
|---|---|---|---|
| rungs_m3 | 232/293 | 79.2% | ⛔ **−15** (was 247) |
| rungs_m3_cells | 232/293 | 79.2% | — |
| rungs_m4 | 218/293 | 74.4% | ⛔ **−25** (was 243) |
| smoke | 28/28 | 100% | ✅ |
| crosscheck | 4/4 | 100% | ✅ |
| gates | 8/10 | 80% | — |

⛔ **META prints 69.0 and that number is WRONG — do not quote it.** `bench_correct` scored **0/1 at w=15**, but 23 `.icn` benchmarks exist and the suite hit the scorecard's own `timeout 900` — **a timeout scored as a zero.** Recomputed over the suites that actually measured (Σw=80): **META 82.0**. ⭐ Same class as the `probes_misc`/benchmark `norm=ms` defects: an instrument reporting a number it never measured. Fixing the cap (or making the suite report PARTIAL instead of 0) is owed before any Icon board is quoted.
⛔ **31 m3 FAILs, and NO Icon-frontend commit exists since s247** (`git log src/lower/lower_icon.c src/parser/icon/` is empty) — so the −15/−25 is **collateral from shared emitter/template/runtime work** done during the SNOBOL4-FIRST blackout (25 template commits since s264 alone). That is the predictable cost of the "do not even run the Icon checks" order, now visible and now measurable. Fail set is dominated by `rung36_jcon_*` (24 of 31) plus `rung03_suspend_gen*` (4) — the N-2 generator-frame class the goal file already predicts.

### NEXT, IN ORDER
1. **`vlist-expr-alternation`** (seat03, assigned) — closes BOTH near-100 suites at once; 4-line witness + frame-rsp reference in hand.
2. **Icon rungs_m3 back to 247+** — bisect the shared-emitter collateral (no Icon commits exist, so `git bisect` over the emitter range with `test_icon_all_rungs.sh` is exact). Then N-1/N-6 rows (minted s266).
3. **Fix `bench_correct`'s timeout-as-zero** before quoting any Icon META.
4. `json-fence0-static-release-leak` — cured on hq_P's tree, awaiting their push; hq_C re-verifies the composition against `probe/choice_records/c04..c06`.
5. gimpel 40.5% / csnobol4_suite 47.5% triage rows (minted s266) — the remaining bulk on the road to ALL-SNOBOL4-100.
6. `beauty_self` is UNSCR because the oracle SIGSEGVs on beauty — the flagship is outside every META. Needs its own instrument (the M1 fixed-point gate IS that instrument; wire it into the scorecard).

## LIVE CURSOR — hq_C (s265, superseded by s266 above)

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
