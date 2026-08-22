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

## ⛔⛔⛔ RUNG C-0 — MILESTONE 1 MODE-3 IS REGRESSED. THIS IS #1 AND NOTHING OUTRANKS IT

**Measured s256, reproduced independently four times** (seat04, seat06, seat09, HQ):

```
beauty m3 self-host  ->  278 bytes.   The fixed point is 40,971.
                          It prints its own "Parse Error" and stops.
```

- **m4 still reproduces the fixed point** (md5 `6f1671c0757729992ae01a6bdf16f081`). So **m3 ≢ m4, and that is a DESIGN INVARIANT violation** — a BOTH-MEDIUM defect by definition. m3 is BINARY, m4 is TEXT: **start at the medium-split mechanisms, do not bisect blind.**
- **seat04 bisected to `62017f8a`** (`descr-stamp-fields`: split `DESCR_t` tag into `v`/`mod_op`/`src_node`/`slen`), reconfirmed at HEAD.
- ⭐ **HQ HYPOTHESIS, UNMEASURED, FALSIFY FREELY:** `62017f8a` turned `DTYPE_t v` (a 4-byte enum owning bits 0-31) into `uint8 v + uint8 mod_op + uint16 src_node`. Offsets did not move. What changed is that **bits 8-31 stopped being part of `v`** — and the tree reads that word at MIXED WIDTHS. `rtx_match.S:768` byte-compares; `rtx_match.S:946` and `rtx_arith.S:78` DWORD-test against `DT_NOTSTR_MASK`; `rtx_abi.inc:63` states the rule outright (*"STRING tests are 32-BIT ONLY"*); `descr.h:41` asserts an invariant that holds **only while those bits are zero**. Anything dirtying them makes a **string test as not-a-string** — and beauty is pure string work parsing SNOBOL4, so it fails first and loudest.
- **Corroborating witness:** with `SCRIP_DESCR_STAMP=1` the same mask class loses `LGT` and `LEQ` on `060_pred_operand_edge.sno`. Stamping is **default OFF**, so if beauty breaks with it off, something else is dirtying those bits — **find what.**
- Rows: `rung-m1-m3-regression` (seat01) · `rung-descr-stamp-notstr-mask` (seat12). Same class — make them talk.

⛔ **A CORRECTNESS TRAP THIS HQ MUST NOT FALL INTO:** a broken program is FAST. Any beauty timing taken in m3 today looks spectacular while doing almost nothing. **Verify the output before believing any number** — yours or a seat's.

## THE STANDING CORRECTNESS BOARD

| front | state (measured s256) |
|---|---|
| **SNOBOL4 #1** | m3 M1 REGRESSED (C-0). Standing reds: `160_pat_alt_inner_gen_resume`, `demo_treebank` (deliberate), `132_pat_fence_eps_recur_shallow` (compile SKIP). ⛔ Corpus totals in old briefs (`339/341`) are STALE — seat3 measured `320/321` and `319/321+1skip`. **Measure your own baseline and cite it.** |
| **Icon #2** | Oracles **ABSENT** — `icont`/`iconx` are not installed here. ⛔ An Icon board run today grades against nothing and prints plausible red. **Install the oracle before staffing any Icon row.** `GOAL-ICON-100.md` R-0 is default-arm resurrection. |
| **Prolog #3** | Oracles **ABSENT** — no `swipl`, no `gprolog`. Smoke 3/5 pre-existing. Same rule: no oracle, no verdict. |

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

**Opened s256. First action: RUNG C-0.** Verify the M1 m3 regression yourself (do not inherit it), then supervise `rung-m1-m3-regression` to a cure. ⛔ Second action, and it is not optional: **run `bash SCRIP/scripts/s4e_msg.sh fleet` on a cadence.** The old HQ never did, and two table rows sat 115 and 83 minutes with zero output while nobody noticed — a claimed row also HIDES itself from the picker, so a stalled seat blocks everyone else from the row too.
