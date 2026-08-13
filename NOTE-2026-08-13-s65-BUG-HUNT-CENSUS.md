# NOTE — s65b BUG-HUNT CENSUS (Lon directive: "We are on a BUG hunt and CLASSIFY")

**THE THREE LEDGERS** (regenerate: `bash SCRIP/scripts/test_bug_hunt_census.sh [out.tsv]`; per-site lists in `/tmp/bug_hunt_diag/<md5>.diag`; compiler tags gated `SCRIP_CLASS_DIAG=1`, stderr-only, byte-inert off — proven ON==OFF md5-identical):

1. **NOFIX** — compile-time NO-FIXED-OFFSET: `[CLS:NOFIX]` at the bb_prepare choke, predicate `emit_rec_pin() || op_stmt_dyn` — the s52/s53 dyn-offset knowledge whose `[rsp + -1]` sentinel arm was deleted; the knowledge now reports without changing emission.
2. **NOWHACK** — compile-time NO-WHACK-for-unbounded-growth: `[CLS:NOWHACK]`, predicate `frame_need_of(nd)==1` minus FENCE1 (its keeper mechanism IS whack power — EARN-2 exclusion precedent).
3. **RESULT** — runtime failure classification via `classify_one` (test_rsp_descent_sweep.sh, ONE AUTHORITY, reused via SWEEP_LIST).

**SNAPSHOT 2026-08-13, SCRIP HEAD 39d5f17d + s65b diag, mode SCRIP_FN_RBP=1 (default), set = 188 BB probes + 6 SCRIP demos + 32 corpus demos = 226 programs:**

| Ledger 3 result | count |
|---|---|
| PASS | 164 |
| SIG11 | 33 |
| DIFF | 20 |
| SIG6 | 5 |
| TIMEOUT | 2 |
| COMPILE_FAIL | 1 |
| ASM_FAIL | 1 |

Ledger 1: **157 programs / 3235 sites** (dominated by pinned pattern-blob graphs — emit_rec_pin is graph-scoped).
Ledger 2: **110 programs / 285 sites** — op breakdown: IR_MATCH_ARBNO 145 · IR_MATCH_ASSIGN_COND 118 · IR_MATCH_ASSIGN_IMM 22.

**CORRELATION:** 62 red total; **46 of 62 carry NOWHACK>0** (predicted by ledger 2); 13 more carry NOFIX>0 only; **exactly 3 are invisible to both ledgers**: probes A05, A06 (SIG11) + demo expression.sno (COMPILE_FAIL).

**⛔ THE CAVEAT, STATED SO NOBODY OVER-TRUSTS THE CORRELATION:** NOWHACK>0 ∧ red does NOT mean NOWHACK caused the red. The minimal witness proves it: a one-DEFINE program with a match in the body (SHIFT: `S LEN(N) . FRONT REM . REST` — the Class-A match-inside-DEFINE-body shape) SIG11s with BOTH ledgers EMPTY (bb_prepare fired 7×, zero tags). **The Class-A condition — body statements running at the shim's dynamic depth — is compile-time INVISIBLE BY DESIGN**: the s62 ruling ("You do NOT know where the begin of a FUNCTION is", no lexical scoping, statements one at a time in source order) means the compiler cannot know which statements execute at shim depth. Class A lives on ledger 3 only. A05/A06 are the probe-suite members of the invisible set — first fix targets alongside the SHIFT witness.

**FIX/LEAVE (awaiting Lon rulings, per "some of which we will fix and some we will leave"):**

| Class | Members (this set) | Proposed |
|---|---|---|
| A — match-inside-DEFINE-body dynamic depth | demo claws5/roman-class SIG11s, treebank TIMEOUT, SHIFT witness | FIX (dominant) |
| Invisible probes | A05, A06 | FIX (root-cause first — may be Class A) |
| expression.sno COMPILE_FAIL | 1 | FIX (compiler crash = quality floor) |
| porter ASM_FAIL dup-label | 1 | pre-existing s60 OWED 3 |
| D/X/H probe families (NOWHACK-carrying SIG11/DIFF) | ~40 | classify per family next session |
| beauty.sno SIG11 | 1 | known ONE root (op_sa re-home, s63 NOTE) |
