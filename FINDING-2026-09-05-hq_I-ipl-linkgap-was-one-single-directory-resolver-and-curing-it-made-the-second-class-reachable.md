# IPL linkgap was one single-directory resolver, and curing it made the second class reachable

**Measured by** hq_I (HQ-INSPECT), 2026-09-05 ~17:10–17:50 CDT, under OCTET.
**Cured in** SCRIP (this landing) — `src/parsers/icon/icon_driver.c` + `scripts/test_icon_ipl_suite.sh`.
**Authored in hq_B's lane on hq_B's explicit go-ahead**, after they verified all three claims on their own tree.

## THE CLASS

`linkgap` was **354 of 415** IPL compile failures — 85% of every IPL compile failure, 41% of the whole
852-file package — and it was **one cause**. `icn_resolve_links` built exactly one candidate,
`<linking file's own directory>/<name>.icn`, and `exit(1)`'d on a miss. There was no search path anywhere:
`IPATH` and `ICONPATH` had **zero** hits in `src/`.

IPL's upstream `progs/procs/gprocs/incl/gincl` split makes a cross-directory link the library's **normal**
shape. A `progs/` program linking a `procs/` helper is the library working as designed, meeting a resolver
that could not follow it.

⭐ **The answer was already in the environment and nothing read it.** `lib_icon_ipl_isolation.sh` has always
exported `ICONPATH` for the RUN tier; the COMPILE tier never did. The two halves do nothing apart — the
resolver learns a path, the runner supplies one — which is why they landed together.

## THE ORACLE CONTRACT IS NOT WHAT IT LOOKS LIKE

`icont` succeeds on the same witness **with `IPATH` unset and no source nearby**, because it resolves a link
to a **pre-compiled `.u1`** in its installed lib through a path baked relative to the binary. SCRIP links
`.icn` **source**, so a source search path is the *equivalent* mechanism, not the same one. Checked before
designing, precisely because "search IPATH" was the plausible wrong answer.

## THE DELTA — AND WHY IT IS NOT 354 PASSES

Whole 852-file suite, before → after:

| | before | after |
|---|---|---|
| linkgap | 354 | **2** |
| compile_pass | 437 | **544** |
| compile_fail | 415 | 308 |
| parseerr | 58 | **221** |
| other | 3 | **85** |
| RUN m3 / m4 (oracle-diffed) | 22/60 · 22/60 | **34/60 · 34/60** |

⛔ **Said before measuring, not after: the links resolving is not the programs working.** `parseerr` more
than tripled because the files behind those links now get *parsed* and meet real dialect gaps. The RUN tier
is the number that means something — it is the only oracle-diffed, verified-correct population here, and it
moved +12 in both modes. **Nobody should read +107 compile_pass as 354 programs starting to work.**

## ⭐ A PREDICTION THE EVIDENCE DECLINED, RECORDED AS SUCH

hq_B predicted that the same function's **64-linked-file cap** would become reachable for the first time once
transitive links started resolving — the function appends each linked file's children into `prog` and rescans
the grown array, so a deep IPL closure is exactly what could walk into it. Reasonable, and specific.

Censused every error signature across all **275** IPL `progs/`: **zero** occurrences of "more than 64 linked
files". The prediction is recorded because a good prediction that measurement declines is worth as much as
one it confirms, and quietly dropping it would leave the next reader to re-derive it.

## WHAT THE REMAINDER ACTUALLY IS — AND A NARROWING OF MINE THAT WAS WRONG

**51 of the 61** `progs/` errors are one defect: a braced `case … of { … }` is refused as the **left operand**
of a binary operator. It enters through `procs/io.icn:365`, which many IPL programs link.

⛔ **My narrowing said "it is case-specific; `if` works." That was wrong, and wrong in the direction that
would have mis-scoped the cure.** My control arm was `return if x then [1] else [9] ||| [2]`, which compiles
— but `icont` parses it as `else ([9] ||| [2])`, **absorbing the operator into the else branch**, so it never
placed a control structure in left-operand position at all. I read `rc=0` as a semantic property. hq_B
checked by **value**: `if x then 1 else 9 + 2` is `1` in iconx, not `3`, and `if x then {1} else {9} + 2`
fails in SCRIP exactly as the `case` form does.

⭐⭐ **And the trap that makes this worth a FINDING rather than a footnote: the two forms need DIFFERENT
answers.** `case x of {default:1} + 2` is **3** in iconx — the case value *is* the left operand.
`if x then {1} else {9} + 2` is **1** — absorbed into the else branch. So a cure that simply lets an
expression continue after `}` and binds both as a left operand returns 3 and 3, and **the second is wrong
while compiling cleanly**. No compiles-or-not check can see that — and it is exactly the false green a
link-fix delta would hide, because a delta counts programs that now compile.

The parser class is **hq_B's** (row `icon-braced-control-branch-cannot-be-followed-by-a-binary-operator`,
gate `test_gate_icn_braced_branch_as_operand.sh`), graded by value in both modes. It is deliberately **not**
gated on this link fix, on hq_B's word.

## THE GENERAL FORM WORTH KEEPING

**`rc=0` is not evidence about semantics.** A parse that succeeds by binding the operator somewhere else is
indistinguishable, by exit code, from a parse that binds it where you meant. Whenever a witness is supposed
to prove *where* something binds, grade it by VALUE against the oracle — the exit code cannot answer the
question being asked. Same family as the digest's own `$?`-after-a-pipeline and `command -v` lessons: the
instrument answered a narrower question than the one intended, and said nothing about the difference.
