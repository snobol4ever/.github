# FINDING — ⛔ RETRACTION: the "four false-green .ref files" were MY oracle mistake, not a corpus defect

**Seat:** hq_C (HQ-CORRECTNESS) · **Date:** 2026-08-23 · **Status:** the original claim is WITHDRAWN.

## What I claimed, and why it was wrong

I reported that four `.ref` files in `corpus/programs/csnobol4-suite/` — `noexec`, `openo`, `sleep`, `space2` — were **false greens**: empty files asserting "prints nothing" while the oracle printed real output, so that any harness diffing them would pass a program that could print anything. hq_P accepted it and called it the best find of the day.

**It does not survive measurement.** Three of the four `.ref` files are correct exactly as they stand.

⭐ **Root of the error: I graded a CSNOBOL4-dialect suite against the SPITBOL oracle.** `corpus/programs/csnobol4-suite/` is Phil Budne's CSNOBOL4 test suite (124 `.sno`).

Measured against the suite's **native** oracle, `/home/claude/csnobol4/snobol4`:

| program | csnobol4 stdout | rc | `.ref` | verdict |
|---|---|---|---|---|
| `noexec.sno` | *(empty)* | 0 | empty | ✅ correct |
| `openo.sno` | *(empty)* | 0 | empty | ✅ correct |
| `space2.sno` | *(empty)* | 0 | empty | ✅ correct |
| `openo2.sno` | `hello` / `world` | 0 | `hello` / `world` | ✅ correct |
| `sleep.sno` | *(empty)* | **1** | empty | ⚠️ see below |

And the emptiness is correct for reasons plainly visible in sources I should have read before claiming:

- **`noexec.sno`** is `-NOEXECUTE`. It compiles and never runs. Printing nothing is the whole point of the test.
- **`openo.sno`** does `OUTPUT(.FOO,10,,"openo.tst")` — it writes to a **file**, not stdout. **`openo2.sno` is its partner**, reading `openo.tst` back and printing `hello`/`world`. The pair only makes sense with `openo.ref` empty.
- **`space2.sno`** does `convert(" ", .integer)` and `convert(" ", .real)`. **Both FAIL**, and a failed conditional assignment prints nothing.

## ⛔ What I mistook for "the oracle prints real output"

Under `sbl -bf`, the same programs emit **error text**:

- `noexec`, `space2` → `No END statement found in source file(s)`, rc=1 — they end with lowercase `end`, and `-f` turns case folding **off**.
- `openo` → `ERROR 160 -- inappropriate file specification for output` (twice), rc=141.

That is SPITBOL refusing a dialect it does not speak. **I read a wrong-oracle error stream as oracle output and inverted the verdict.**

⭐ The irony worth recording: `-bf` is mandated precisely *because* it is the case-sensitive arm that matches SCRIP (s189). The same flag that makes SPITBOL the correct SNOBOL4 oracle is what makes it reject these lowercase-`end` CSNOBOL4 programs.

## The fourth file: `sleep.sno` — a real gap, but not the claimed one

`sleep.sno` opens `-INCLUDE "../modules/time/time.sno"`, and **`corpus/programs/modules/` does not exist in this root**. csnobol4 gives rc=1, `Cannot open INCLUDE file`. So it is an empty `.ref` beside a program that **cannot run here at all** — untestable, not falsely green.

## ⭐ The one thing that survives — and it is the OPPOSITE polarity

`scorecard_snobol4.sh` **does** grade this suite against SPITBOL: row `csnobol4_suite` (line 47), `SBL="${SBL:-$S4A/x64/bin/sbl}"` (line 32), `sbl_flags()` → `sbl_lang_flags()` = `-bf` (line 92). Pointing SPITBOL at CSNOBOL4-dialect programs is a genuine oracle mismatch.

⛔ But it manufactures **FALSE RED, not false green** — far less dangerous than what I claimed, and a *scorecard* defect rather than a *corpus* defect. **No count is quoted here because I have not run the row.** Measuring before quoting is the discipline whose absence produced this retraction in the first place.

## The lesson, stated plainly

**Check which dialect the oracle speaks before grading a corpus with it.** A wrong-oracle error stream is not evidence about the program under test. The failure was mine twice over: I inverted a verdict, and I shipped it to a peer who banked it without re-deriving it — which is the reasonable thing for a peer to do, and is exactly why shipping an unverified claim is expensive.

Related: `FINDING-2026-08-20-s188-the-oracle-flag-is-a-language-switch-and-b-manufactures-the-crashes-it-is-blamed-for.md` — the same class, and it already said the flag is a *language switch*. I had the answer on disk and did not apply it.
