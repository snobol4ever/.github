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

---

## ⛔⭐⭐⭐ s65c — THE INVISIBLE-RED SET IS ROOT-CAUSED, AND MY OWN s65b CLAIM IS CORRECTED

**⛔ CORRECTION FIRST (this seat's error, recorded because the wrong grouping would have sent the next seat to the wrong mechanism).** s65b's cursor said all three invisible-red programs were "Class A, compile-time invisible by the s62 no-lexical-scoping design." **That is TRUE of the SHIFT witness and FALSE of A05/A06.** A05/A06 contain NO DEFINE at all. Measured: `SCRIP_EARN_DIAG=1` on A05 prints `op=100 (IR_MATCH_ASSIGN_COND) need=0 haz=0` and `op=101 (IR_MATCH_ASSIGN_SAVE) need=0 haz=0` — **the capture nodes ARE there and ledger 2 reported them as safe.** ⇒ **LEDGER 2 HAS A KNOWN FALSE-NEGATIVE CLASS, and A05/A06 are its witnesses:** `earn_hazard_in` is still EARN-1 SLICE 1's **operand-walk PLACEHOLDER**, and s47 wrote the caveat verbatim — *"γ/ω-wired spans are INVISIBLE to an operand walk, so conditional rows UNDER-DETECT toward 0; the real span authority is EARN-5's."* The ledger did not fail; it reported exactly what its placeholder predicate knows. **EARN-5 (capture-span hazard authority) is therefore not just a ladder rung — it is the fix for ledger 2's blind spot, and closing it converts ~40 of the D/X/H probe reds from unpredicted to predicted.** Only `expression.sno` (COMPILE_FAIL) remains genuinely unattributed.

**ROOT CAUSE, isolated by swap experiment (RULES cheapest-discriminating-experiment, four minted variants, oracle-checked):**

| variant | pattern | result |
|---|---|---|
| v1 | `POS(0) ('ab' \| 'xy' \| 'pq')` — 3 arms, NO capture | **PASS** |
| v2 | `POS(0) ('ab' \| 'xy' . W)` — 2 arms, capture INSIDE arm 2 | **SIGSEGV** |
| v3 | `POS(0) ('ab' \| 'xy') . W` — capture OUTSIDE the alternation | **PASS** |
| v4 | `POS(0) ('xy' . W \| 'pq')` — capture INSIDE arm 1 | **SIGSEGV** |

⇒ **ARITY IS IRRELEVANT (v1 exonerates it). CAPTURE POSITION IS THE WHOLE DISCRIMINATOR: inside an alternation arm dies, outside passes.** Minimal reproducer is v2 — two arms, one capture, no DEFINE, 6 lines — **strictly smaller than A05** (which adds a third arm and an unset-sentinel print), so future work should use v2.

**MECHANISM (gdb, `SCRIP_NO_SEGV_HANDLER=1`, clean backtrace):** `#0 rt_cap_push (slot=0x7fffffffe9e0) at pattern_match.c:771 — if (s->sp == s->buf[0])` reading garbage; `#1 n15_match_assign_save_α`. **The two variants take DIFFERENT ASSIGN_SAVE ARMS — that is the finding:**
- **v3 (PASS) = the STATIC SPINE ARM:** `sub rsp,16; mov dword ptr [rsp+0], r14d` — δ0 banked on the spine, **`rt_cap_push` never called at all**.
- **v2 (CRASH) = the DYNAMIC CAPTURE-STACK ARM:** `lea rdi,[rsp+208]` + RTCC block save + `call rt_cap_push` — and **`[rsp+208]` is not backed by the live claim on the alternation arm's execution path**, so `rt_cap_push` receives a slot pointing at unclaimed stack and dereferences uninitialized `s->buf[0]`.

**THIS IS A NAMED, PREVIOUSLY-CONVICTED FAMILY — do not re-derive it:** `x86_frame_off`'s own s23a comment records the identical shape (*"assign_save cap slot at 384 against a 176B claim ... handed rt_cap_push a slot INSIDE environ — the s22r envp-corruption class"*), and s43's caveat named the alternation-specific reason the offset drifts (*"at L(4)/L(5) rsp is 32B deeper than at the save ... an rsp-arm FRQ would misread by exactly that. Verify per-site, don't assume."*). **The alternation arm is exactly such a site: each arm enters at its own carve depth (`n13_match_alternate_α: sub rsp,32`), so one statically-computed cap-slot offset cannot be right for the arm-interior and the pre-alternation depth simultaneously.**

**NEXT RUNG (do not start without runway — this is a real fix, not an instrument):** decide per the EARN law whether the arm-interior capture (a) earns the frame the RBP-FUNCTION debug mode is meant to expose, or (b) gets its slot resolved through the alternation's own claim base (the `zvo_resolve` owner-table path `x86_frame_off` already provides). Gate: v2/v4 + A05/A06 oracle-green, `board_patterns_set.sh` BY SET, then re-run `test_bug_hunt_census.sh` — **ledger 2's NOWHACK count should MOVE when EARN-5 lands, and that movement is the instrument's own self-test.**
