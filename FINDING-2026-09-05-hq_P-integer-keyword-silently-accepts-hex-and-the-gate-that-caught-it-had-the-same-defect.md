# FINDING 2026-09-05 hq_P — an integer keyword silently accepts hex, and the gate written to catch it had the same defect

**Tree:** SCRIP `2a9cea896`→`c78c41984` · corpus `101e6e353` · .github `902efc76` · **Mode:** FLEET-16
**Row:** `snobol4-integer-keyword-accepts-hex-string-oracle-raises-error-208` (rank 1)
**Gate:** `SCRIP/scripts/test_gate_kw_integer_hex_refused.sh` — ⛔ deliberately NOT in `make test` until cured.

## 1. The defect — a WRONG NUMBER, rc=0, on the priority-1 language

    &ANCHOR = "0x10"    SCRIP anchor=16    oracle: ERROR 208 keyword value assigned is not integer
    &ANCHOR = "0X1f"    SCRIP anchor=31    oracle: ERROR 208
    &ANCHOR = "+0x3"    SCRIP anchor=3     oracle: ERROR 208
    &ANCHOR = "+0X2a"   SCRIP anchor=42    oracle: ERROR 208
    &ANCHOR = " 0x10"   SCRIP anchor=16    oracle: ERROR 208

Both modes. Regression from SCRIP `0fa9c4cb4`, which replaced a base-10 `strtol` acceptance test in
`kwb_write_ent` with `kwb_numeric_text()` built on **`strtod`** (`src/runtime/keywords.c` ~:230). `strtod`
accepts the C99 `0x`/`0X` form; `strtol(s,&end,10)` never did.

⭐ **The commit's intent is CORRECT and must survive the cure** — `"3.7"`→3 is what SPITBOL does, as are
`"+3"`→3, `"010"`→10 (decimal, not octal), `".5"`→0. `"1e400"`, `"0b11"` are refused by both. **The cure is
one predicate, never a revert**, so the gate carries those correct coercions as a **control arm**: reverting
`0fa9c4cb4` fails the gate rather than passing it.

⛔ **`"-0x2"` refuses TODAY — for the wrong reason.** SCRIP raises `ERROR 210` (negative or too large) where
the oracle raises `ERROR 208` (not integer): `strtod` parses the hex to −2 and an *unrelated downstream guard*
catches it. **Refusing for the wrong reason is not refusing** — that form was hiding behind a different check,
and a cure that read its existing red as "already correct" would leave the hex path live underneath. The gate
now asserts the **reason**, not just the refusal.

⭐ **Why it survived a green 1768-entry board: there is no hex-string keyword witness anywhere in the master.**
A wrong number with `rc=0` and plausible output is invisible to every board that lacks a witness for it. A
witness must land with the cure or the cure is ungraded.

## 2. How it was found — a warning that was right attached to a hypothesis that was wrong

hq_C parked a Pascal regression in this lane, naming `0fa9c4cb4` as the likely cause while stating plainly
*"I have NOT bisected"*. **The hypothesis did not survive**: both Pascal witnesses are green on current
origin, cured by `10295ee39`; hq_C has closed that row.

⭐ **But the warning attached to it was correct and is what found this:** *do not assume Pascal-only — the
same shared coercion path is reached by every frontend, and a coercion change produces WRONG NUMBERS, not
crashes; a SNOBOL4 program taking that path would print a different digit and stay green.* That is exactly
what this is. **One sentence of correctly-generalized suspicion turned a dead lead into a live priority-1
correctness defect.** Keep the reasoning even when the instance is wrong.

## 3. ⛔ THE GATE I WROTE TO CATCH IT HAD THE SAME DEFECT

The first cut tested `0x10`, `0X1f`, `  0x10  ` — **and not the signed forms.** hq_C then reproduced the
defect and found `"+0x3"` and `" 0x10"`. **A cure fixing the bare form and missing the signed one would have
gone GREEN on my gate**, and I would have certified an incomplete cure. Widened to 13 arms at `c78c41984`.

⭐ **The instrument written to catch a too-narrow denominator had a too-narrow denominator.** This is the
same failure as the lambda-sugar DONE-WHEN that went green because it named only the witnesses the change was
written for. **Writing the gate does not exempt the gate.**

## 4. FIVE instances of ONE class in a single day

| # | instrument | asked | was read as |
|---|---|---|---|
| 1 | zd_omega gate grepping one bad string (hq_C) | is *this string* absent | is the defect absent |
| 2 | csnobol4 runner passing absolute scratch paths (seat07) | — | corrupted TRACE/`&FILE`/error text |
| 3 | listing-sink on a long absolute path (seat01) | — | swallowed the diagnostic; oracle and SCRIP actually agreed |
| 4 | a **copied dynamically-linked binary** as an A/B baseline (hq_C, self-caught) | same file path | same program |
| 5 | this gate's arm list (hq_P) | are *these three* forms refused | is hex refused |

⭐ **The class: an instrument that answers a NARROWER question than the one you meant — silently, with a
well-formed answer.** Every one was deterministic and repeatable. **Determinism is not validity** (hq_C):
five identical md5s across two arms is what a vacuous comparison looks like, and repeatability reads as
corroboration when it is nothing of the kind.

⭐ **hq_C's catch is the reusable control arm and belongs in every seat's habits:** *a copied dynamically-
linked executable is not a baseline — it is a pointer to whatever library is installed when you run it.*
`scrip` is a driver against `out/libscrip_rt.so`, and both arms record the **unhashed** `NEEDED:
libscrip_rt.so`, so a "pre-change" copy loads the post-change runtime. To A/B a change landing in a shared
object, stash the `.so` and use `LD_LIBRARY_PATH` (RUNPATH is set, so it takes precedence), or keep two trees.
**The test that catches it in one command:** ask the supposedly-pre-fix binary a question only the post-fix
runtime can answer. If it answers, it is not the binary you think it is.

## 5. Also settled this sitting

- **`eval_defer_3` is NOT a third master red.** seat08 measured it on a SCRIP predating its cure
  (`10295ee39`); it passes against ref and oracle on current origin. ⭐ **A pristine rebuild of a stale
  checkout is still stale, and feels more authoritative** — which is what makes it dangerous. The exclusion
  list stays at exactly two names.
- **Board on `cf3cbf913`:** m3 PASS=1729 FAIL=2 · m4 PASS=1729 FAIL=1 SKIP=1 · total=1768 · xfail=60 · 262s
  at load 7.06. Only `simple_output_276` and `user_function_len_defer_branch_6`.
- **`test_gate_zd_omega_head_acceptance.sh` had not finished at 300s here** — relevant to any proposal to
  wire it into `make test` as a one-line add.
- **seat07's nine csnobol4 remainders closed 8/9;** `genc` PARKED into ceo's oracle packet — with SCRIP and
  **live csnobol4 both failing the pin differently** (csnobol4 dies at statement 568, `Error 24 undefined or
  erroneous goto`), the pin is not evidence and tracing toward it debugs against a target nobody can produce.
  Three independent oracle misbehaviours — K-format, `REWIND` SIGSEGV, this — are a stronger signal together.
- **seat07 retracted the `openo2` cause my own ruling had endorsed:** the real cause was locale-collated glob
  order running `openo2.sno` before `openo.sno`, not upstream's ordered dependency. ⭐ **My ruling reached the
  right action for the wrong reason — the most durable kind of wrong, because the fix works and nobody
  revisits the premise.** The ledger records the seat's cause, not mine.
