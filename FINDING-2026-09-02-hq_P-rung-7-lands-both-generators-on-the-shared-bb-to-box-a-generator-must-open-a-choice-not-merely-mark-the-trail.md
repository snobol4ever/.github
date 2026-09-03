# FINDING 2026-09-02 hq_P — rung 7 LANDS: both generators ride the shared `bb_to` box, and the lesson is that a generator must OPEN A CHOICE, not merely mark the trail

✅ **`test_prolog_ladder.sh --only 7` PASS 4/4 both modes** — the gate ceo named. SCRIP `84e02570` (+ `d03e51d1` re-pin),
corpus `778827ae7`. `between/3` and `sub_atom/5` land as generators.

## ⭐ NO NEW TEMPLATE — BOTH GENERATORS ARE A BOX WE ALREADY SHIPPED

ARCH § B.13 (ii) is literally right: `between(L,H,X)` **is** Proebsting's `to(E1,E2)`, so it lowers to the shared `IR_TO`
box Icon uses for `i to j`, with the per-value bind going through the same `$is_v` sink `is/2` already uses.

`sub_atom/5` looks like it needs a nested (Before, then Length) generator. It does not: **the pair space linearises** —
block `B` holds lengths `0..n-B` — so one `IR_TO` over `0..count-1` drives it and a decode-and-unify sink does the rest.
⛔ **No mode dispatch anywhere, deliberately.** Every instantiation pattern falls out of unification: a bound argument
filters, an unbound one is written. Slower than a mode-specialised search, and correct for all modes with no per-mode
path to get wrong. Verified against swipl on five modes (all-unbound, `B`/`L` bound, `Sub` bound, `B` bound): identical.

`ir_is_generator_kind()` is the resumable predicate in `pl_lower_conj`, so this covers the rest of § B.13, not just these two.

## ⛔⛔ THE LESSON: MARKING THE TRAIL IS NOT OPENING A CHOICE

The obvious cure for "redo returns the same binding" is a trail mark at α and an unwind at β. **I implemented exactly
that, it emitted, and it changed nothing** — the witness still printed `1` and stopped.

⭐ **Because Prolog trails CONDITIONALLY.** The rung-2 clause step re-seeds locals with `rep stosb` precisely because
they are *younger than any live choice and so were never logged*. A box that only banks `r12` registers **no choice at
all**: every local stays younger than everything, nothing is trailed, and the unwind walks an empty suffix. The
instrument was correct and the precondition was absent.

✅ **The cure is hq_C's rung-3 mechanism REUSED, not a second one** (ceo ruling, superseding § B.13 (i)'s bare
`F.B := rbp`): α banks `r12` in the box pad **and** calls `rt_pl_disj_open(H, rbp)`, which lowers this frame's log
threshold `F.HI` so the activation's cells become loggable, and raises `B` to `H` only when the live choice is older or
absent. β unwinds to the mark before the cursor advances. **ω deliberately restores nothing**, as `bb_disjunction` does;
cut's `B` lifecycle stays rung 4's.

## Shared-box discipline — proven, not assumed

`grep -c IR_TO src/lower/lower_*.c`: prolog 3, raku 3, **icon 2**. All three arms sit under `x86_fb_pinned()`, never a
language name. ✅ **The same `.icn` compiled before and after is BYTE-IDENTICAL**, and the Icon master board holds its
watermark (398/398). That is the s272 lesson — a language-blind grant over a shared node cost 47 Icon programs — paid
forward rather than relearned.

## ⚠️ hq_C's review caught a real defect, and I took the other fix

**Review point 2:** `op_off+24` is `to.limit` in the zd arm and the real arm, and free only in the integer-static arm
the generators take — and **nothing enforced which arm was reached**. A selector change would have aliased the trail
mark onto the loop bound: a **wrong answer, not a crash**.

hq_C recommended granting `IR_TO` a fourth word so the map reserves the mark. That is the better long-term shape and
should be taken when a rung will pay for it — but ⛔ **the grant is language-blind, so it moves every Icon and Raku
frame holding a `to`, and ceo's ruling requires those graphs to stay byte-identical.** So a pinned graph reaching
either other arm now **BOMBS** instead. Refusing keeps both properties; the fourth word remains the right follow-up.

Review point 3 accepted verbatim: the missing ω arm is correct and is now **commented so nobody "fixes" it**.

## ⚠️ THE PIN WENT STALE BETWEEN MEASUREMENT AND PUSH — LIVE, AND NOBODY ERRED

`84e02570` pinned the master board floor 198 → 202 against a board measured before corpus `2b71e9a21` landed seven
marker promotions. Re-measured on the merged tree: **213**. Re-pinned in `d03e51d1`, with the attribution stated
because the number is otherwise misleading: **2 of the +15 over 198 are rung 7's two witnesses leaving XFAIL; the other
13 are corpus-side promotions that arrived while I was pushing.**

⭐ This is precisely the class `optbypass-pin-stable-subset` exists to cure, reproduced in one evening by accident: the
pin lives in SCRIP, the population lives in corpus, the two cannot be made atomic, and a pin keyed on a population that
any promotion moves is **stale by construction**.

## Measured

`--only 7` 4/4 · `--to 2` 6/6 · SNOBOL4 **1679/1679 FAIL=0** both modes · Icon master board 398/398 watermarks held ·
Icon smoke 14/14 · Icon `to` byte-identical · quad gate PASS(0) 38 witnesses · no-new-global PASS · `emit_no_lang` and
`template_medium_invisible` PASS · `nm -D` 0 § C symbols · xfail-marker gate PASS (all three places agree) · board floor
failed once at 214 and passed at 213 · artifact chain clean.
