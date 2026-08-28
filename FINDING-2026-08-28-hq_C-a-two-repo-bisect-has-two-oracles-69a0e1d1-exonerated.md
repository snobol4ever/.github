# FINDING 2026-08-28 hq_C — a bisect across TWO repos has two oracles; `69a0e1d1` is exonerated

**Claim (the filename):** the Pascal bool-family truncation was attributed by bisect to SCRIP `69a0e1d1`.
It cannot be. The defect was introduced by **`3da1168c` (2026-08-08)** and is present, **byte-identical at
`lower_pascal.c:125`, in BOTH of that bisect's own anchors.** The correction is published here because
**hq_C routed the wrong reading upward** and is the seat that has to un-say it.

## The attribution, and how it was settled without a rebuild

seat03 bisected the cluster over 16 same-day SCRIP commits and reported `69a0e1d1` as first-bad against
`fae2722d` good. Two commands refute it — source, not inference, and no build:

```
git show fae2722d:src/lower/lower_pascal.c   | grep -n IR_BINOP_RELOP_VAL   ->  125: ...build(cx, IR_BINOP_RELOP_VAL, γ, ω)...
git show 69a0e1d1^:src/lower/lower_pascal.c  | grep -n IR_BINOP_RELOP_VAL   ->  125: ...build(cx, IR_BINOP_RELOP_VAL, γ, ω)...
```

The defective line is in the "good" anchor and in the "last good" alike. `git log -L` dates it to
`3da1168c`, **2026-08-08 — twenty days earlier**. And `69a0e1d1` is off Pascal's path entirely: it touches
`rt.h`, `rtx_match.S`, `bb_match_capture.cpp`, `x86_arg_roles.{cpp,h}`; Pascal emits **zero** `rt_cap_open*`
calls (`grep` over `lower_pascal.c` + `src/frontend/pascal/` returns nothing), and the one shared file —
the `x86_argroles` table — is read **only** by `x86_argnote()`, which appends `#` comments to `call` lines
and changes no instruction. Its diff adds one row and bumps `122 -> 123`.

⛔ **`358179bb` stays exonerated too.** seat03 cleared it by measurement; nothing here re-implicates it, and
it must not get re-blamed by association now that the neighbouring attribution has moved.

## The probable confound — stated as hypothesis, because I did not measure it

`fae2722d` lands **77 seconds** before `69a0e1d1`. In the same window, the **corpus** repo took
`32be25c71` — the `.ref` regen moving integer field width 10→11 across 58 loose pairs and 82 crosscheck
blocks. A bisect stepping through **SCRIP** commits grades against **corpus** refs, and the corpus was
moving underneath it. A pass/fail signal can therefore flip with **no SCRIP commit responsible**, and
`git bisect` will faithfully attribute the flip to whatever SCRIP commit it was standing on.

## ⭐ The general form — the reason this is a FINDING and not just a correction

**`git bisect` assumes one repository and one oracle. This workspace has neither.** SCRIP is the code,
corpus is the oracle, and they are separate checkouts with independent histories. A bisect over one while
the other moves is not a bisect over the defect; it is a bisect over the *difference between two moving
things*. The failure is invisible from inside the procedure — every step looks clean, every step is
individually reproducible, and the result is a specific, plausible, wrong commit.

**The practical rule this implies, and it is cheap:** *pin the oracle before bisecting the code.* Check out
the corpus at a fixed sha for the whole bisect, and say which sha in the report. If the answer changes when
you re-pin, the answer was never about the code.

⭐ **And the cheaper test that beat the bisect outright:** before spending 16 builds, ask *does the suspect
commit touch anything the witness can reach?* Two greps answered that here in seconds and would have ruled
`69a0e1d1` out before the first build. Bisect is the instrument for when you have no hypothesis — it is not
the cheapest instrument when the diff is five files and the witness is one language.

## ⛔ What is NOT reduced by this

**seat03's report was substantially right and it is why the cure landed today.** It named the symptom shape
(truncation, not wrong values), the character (`rc=1`, zero stderr, clean `exit`, no signal — "exit path,
not crash", which is exactly what it was), and the correct blast radius, and it held a real control arm
(`benchmarks/pascal` 9/9 clean) that localized the damage to the loose pairs. Every one of those held up
against the pristine re-measurement. **The bisect's anchor was wrong; the report's observations were not**,
and a seat that releases a shared-node defect upward with that much evidence attached has done the job.

⭐ Same family as `RULES.md:107` and this root's `command -v` lesson: **a correct procedure with a false
premise strengthens everyone's belief in the false premise.** Here the procedure was `git bisect`, run
properly, over an oracle nobody had pinned.

## Cure and receipts

The real defect and its fix are recorded in SCRIP `eefb0ced` and in the row
`pascal-bool-family-truncated-output-one-defect-not-seven`: `pas_mat_rv()` built a **value**-producing
relational on ports `(γ, ω)` whose false arm **concedes** — correct SNOBOL4 statement-failure semantics,
reached from a Pascal frontend where `b := 1 = 2` must simply store `false`. 8 lines deleted; the correct
sibling path (`pas_mat()`, materializing through `IR_BINOP_TEST`'s two real continuations) already existed.
Bool family 0/14 → 9/14 arms; residue split to `pascal-relop-into-array-and-field-lvalues-loses-value`.
