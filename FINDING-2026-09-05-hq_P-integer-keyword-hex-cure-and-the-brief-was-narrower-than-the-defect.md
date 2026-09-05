# FINDING — the integer-keyword hex cure, and the BRIEF was narrower than the defect

**Seat:** hq_P (HQ-PERFORMANCE, Opus 5) · **Date:** 2026-09-05 · **Mode:** FLEET-16 (SNOBOL4 only)
**Row:** `snobol4-integer-keyword-accepts-hex-string-oracle-raises-error-208` (rank 1, hq_P lane)
**Tree:** SCRIP `c78c41984`+ · corpus `101e6e353`+ · oracle `/home/resources/x64/bin/sbl -bf`

## 1. The cure

`kwb_numeric_text()` (`src/runtime/keywords.c:233`) decides whether a STRING assigned to an
integer-required keyword is numeric. It delegated the whole question to `strtod()`. **`strtod` accepts
three families SNOBOL4's integer-keyword syntax does not**, and each produced a different wrong answer:

| assigned string | before | oracle | after |
|---|---|---|---|
| `"0x10"`, `"0X1f"`, `"+0x3"` | **stored 16 / 31 / 3, rc=0** | ERROR 208 | Error 208 |
| `"-0x2"` | Error **210** | ERROR 208 | Error 208 |
| `"inf"`, `"INF"`, `"infinity"` | Error **210** | ERROR 208 | Error 208 |
| `"nan"`, `"NAN"`, `"nan(0)"` | Error **210** | ERROR 208 | Error 208 |
| `"1e400"` (overflows to inf) | Error **210** | ERROR 208 | Error 208 |

Two conditions, both in that one predicate: reject a `0x`/`0X` prefix after optional whitespace and
sign, and reject a non-finite `strtod` result. Nothing else moved.

## 2. ⛔ THE BRIEF'S OWN CHARACTERISATION OF THE DEFECT WAS NARROWER THAN THE DEFECT

The row I minted said, in its GOAL: *"The defect is ONLY the unsigned 0x/0X form"*, and listed
`"1e400"` among the forms *"correctly refused by both"*. **Both clauses are wrong**, and I wrote them.

`1e400` was not correctly refused — it was refused with **ERROR 210 (negative or too large)** where the
oracle raises **208 (not integer)**. So were `inf` and `nan`. That is not a second defect; it is the
**same** defect, in the same predicate, wearing the disguise the brief itself had already named for
`-0x2`: **`strtod` parses the value, and an unrelated downstream RANGE guard catches the result.** The
brief spotted that disguise on one form and then, three sentences later, was fooled by it on three more.

⭐ **A cure aimed at the brief's stated extent would have passed its own gate and left most of the class
live.** The reason it did not is that the boundary was **re-measured against the oracle before writing
the predicate**, not read off the row — 32 forms, of which the brief accounted for 6.

⚠️ This is the SAME lesson as my previous commit (`c78c41984`, *"the hex arms were narrower than the
defect"*), one turn further out: there the **gate's arms** were narrower than the defect; here the
**brief's prose** was. ⭐ **The transferable rule: a brief's account of a defect's EXTENT is a
measurement someone took once, and it decays exactly like a count in a digest.** Re-measure the
boundary; do not implement the sentence.

## 3. The gate, widened and negative-tested in both directions

`scripts/test_gate_kw_integer_hex_refused.sh` — now 26 arms × 2 modes, wired into `make test`
**in this same commit, never before** (a red in the blocking set stops every seat's landing).

- **6 acceptance arms** (hex silently stored) and **9 wrong-reason arms** (`-0x2` inf INF infinity nan
  NAN `nan(0)` 1e400 `"  inf  "`) — each asserts the oracle's own 208, re-read from a live `sbl -bf`
  run every execution, and REFUSES rc=2 if the oracle ever stops raising it.
- **Control arm A (coercion):** `3.7`→3, `+3`→3, `010`→10, `.5`→0, `1.5e3`→1500, `3.`→3, `1e7`→10000000.
  Fails if someone "cures" this by reverting `0fa9c4cb4`, whose intent is **correct**.
- **⭐ Control arm B (the 210 guard), added because the cure could over-reject:** `1e30`, `99999999`,
  `16777217`, `-3` must **keep** raising 210. A finite-but-too-large number is *too large*, not *not
  integer*; collapsing it into 208 would trade one wrong code for another and match no oracle.

⛔ **Both new arm families were negative-tested by injection, not merely asserted** — an arm that cannot
fail prints the same string as one that passed:

- Neutering the non-finite guard (`if (0 && …)`) → **rc=1, 16 failures naming inf/INF/infinity/nan/NAN/
  nan(0)/1e400/`"  inf  "`**, while the hex arms stayed green (proving the two guards are independent).
- Deliberately over-rejecting (`|| d > 16777216.0`) → **rc=1, control arm B fires** on 1e30, 99999999,
  16777217.

## 4. ⛔ THE MASTER CANNOT CARRY AN ERROR-PATH WITNESS — A STRUCTURAL GAP, NOT A CHOICE

The row required a witness in the SNOBOL4 master *"or the cure is ungraded"*. **Half of that is
landed and half is blocked, and the blocked half is a gap that reaches far past this row.**

✅ **Landed:** entry **1815 `kw_integer_string_coercion_preserved`** (`ALL.sno`/`ALL.ref`/`ALL.csv`),
seven coercion forms, **byte-identical to `sbl -bf` in m3 AND m4**, verified by extracting it back out
through `corpus_suite_harness.py extract` and running both modes against its own ref. Master 1814→1815.

⛔ **Blocked — the refusal half.** An error-raising entry cannot be graded in this master today:

1. **The diagnostic format differs entirely.** SCRIP prints `** Error 208 in statement 0` + an indented
   message; SPITBOL prints `<abs-path>(1) : ERROR 208 -- keyword value assigned is not integer`, twice,
   **embedding the absolute source path** — which is not even stable across runs.
2. **The exit code differs**: oracle rc=0, SCRIP rc=1. `want_rc` is DECLARED per family via an
   `ALL.wantrc` sidecar, and **snobol4 has no `ALL.wantrc`**, so every entry is want_rc=0.
3. **Measured consequence: `grep -c '^\*\* Error' ALL.ref` is ZERO across all 1815 entries.** No
   error-path witness exists in the SNOBOL4 master at all — which is *why* a wrong number with rc=0
   survived on a green board, and why the next error-path cure will be ungraded for the same reason.

The sanctioned mechanism for a SCRIP-ruled ref (`pin-ref` + `ALL.refpins.tsv`, `REF-PINS.md`) exists and
is the right tool for (1), but (2) needs a new sidecar this family has never had. ⭐ **That is a row, not
an improvisation** — hand-adding an rc=1 entry would have put a permanent red in the board 16 seats
grade against. Minted rather than forced; see § 6.

## 5. The ceo's umbrella re-pin (`re-pin-your-umbrella-done-whens-to-the-board-line`)

Audited both hq_P umbrellas the ceo named:

- **csnobol4 — already compliant, no edit.** `snobol4-csnobol4-suite-non-pass-censused-by-class-and-cured`
  and `…-thirty-regen-candidate-refs-…` both already anchor `^CSNOBOL4_SUITE_BOARD total=…` with the
  tokens in the case the runner prints (`m3_PASS=`, uppercase there).
- **testpgms — RE-PINNED.** `snobol4-spitbol-testpgms-four-programs-to-100-percent-both-modes` did not
  call the runner at all: it **re-implemented the entire grading inline** — its own oracle loop, its own
  `cmp`, its own hand-printed `SPITBOL_TESTPGMS total=` line. A second, hand-maintained copy of the
  suite's semantics that could drift from the runner with neither side able to notice. Now one
  `grep -E '^SPITBOL_TESTPGMS_BOARD total=[0-9]+ '` with the tokens **as the runner prints them**
  (lowercase `m3_pass=`/`m3_fail=`/`m4_pass=`/`m4_fail=`), the graded line echoed, and the runner's rc=2
  honoured as REFUSE rather than read as red.
  ⭐ **`unscored=0` is now REQUIRED** — the old criterion could go green while the oracle died on
  programs it never counted, the exact denominator hole the runner's own header warns about.
  ⭐ The ceo's 18:53 **eight-program** correction is preserved: `total<8` still REFUSES and still names
  #5 TREESORT4 / #6 TOPOLOGICAL SORT / #7 SYMBOL TABLE GENERATOR / #8 BRIDGE DEALER as hq_T's row.
  ⚠️ Verified **offline in both directions** (`bash -n` clean; green line matches; `unscored=1` and
  `m3_fail=1` each go red) rather than by a live run — a full board was already running in this
  checkout, and two runs in one checkout collide. The next seat on that row gets the first live receipt.

## 6. Routed, not silently absorbed

- ⚠️ **`snobol4-bb-emit-end-unresolved-forward-reference-return-aborts-six-of-seven-testpgms` carries TWO
  `DONE-WHEN:` lines** — a real one and the `mint --stdin` hard-refusing placeholder beneath it. **It is
  mechanically harmless**: `s4e_msg.sh` extracts with `sed … | head -1` (`:608`), so the real one wins
  and the ⛔-placeholder check at `:611` never sees the dead line. Recorded because a *reader* of that
  baton sees a scary "can never pass" placeholder that does not apply, and because the claims
  `done-when-line-is-executed-whole-…` and `fifty-seven-batons-are-unclosable-…` are already held by
  other seats — this is evidence for them, not a new row.
