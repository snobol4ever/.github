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

---

## ⭐ MEASURED: the surviving defect, quantified (added same session)

I said above that no count would be quoted until I ran it. Here it is. Every `.sno`/`.ref` pair in `corpus/programs/csnobol4-suite` run against **both** oracles — csnobol4 (native) and `sbl -bf` (what the scorecard actually uses) — 120 gradeable pairs:

| class | count | meaning |
|---|---|---|
| **`SPITBOL_WRONG_ORACLE`** | **30** | **csnobol4 reproduces the `.ref` exactly; SPITBOL does not** — graded false-RED today |
| `both_agree` | 47 | both oracles reproduce the `.ref` — graded correctly |
| `neither_matches` | 41 | see the honesty note below |

⛔ **The 30 are the exposure**, and the program names carry the story — they are CSNOBOL4 extensions SPITBOL does not have:

`8bit2 alis case1 conv2 digits err float func2 function include labelcode label line loaderr maxint openi openo ord popen2 popen pow scanerr setexit2 setexit4 setexit5 setexit7 sleep space update vdiffer`

`include`, `popen`/`popen2`, `setexit2/4/5/7`, `openi`/`openo`, `loaderr`, `maxint`, `labelcode`, `vdiffer` — a suite of dialect features, graded by an oracle that does not speak the dialect.

⚠️ **Honesty note on the 41**, because inflating a bucket is how the original error happened: my sweep is **cruder than the scorecard** — it fed `/dev/null` to stdin and set no `SETL4PATH` include path, where `scorecard_snobol4.sh` uses `stdin_for` and `sc_libpath`. Of the 41: **1** has an input file I did not supply, **9** use `-INCLUDE` against the absent `corpus/programs/modules/`, and **31** are unexplained by this sweep's limitations. ⛔ **The 31 are NOT claimed as defects** — they are unexplained by *this measurement*, which is a statement about my sweep, not about the corpus.

### The cure, and the blocker that stops it being a one-line edit

**Cure:** grade `csnobol4-suite` against csnobol4, not SPITBOL.

⛔ **Blocked, and named rather than worked around:**
1. `scripts/lib_oracle_flags.sh` — the single authority for oracle selection — has **zero csnobol4 awareness**. It exposes `sbl_lang_flags`, `sbl_clean_bin`, `sbl_correctness_bin`; there is no `csnobol4_bin()` to call.
2. **csnobol4 is not in this root.** It lives at `/home/claude/csnobol4/snobol4` (the retired root) and is not on `PATH`. This root is deliberately slim (SCRIP, corpus, .github). Wiring the board to a binary outside the root re-opens the **absent-oracle false-FAIL class** that CLAUDE.md warns about in three separate sessions — trading 30 false reds for a whole-suite false red is not a cure.

⭐ So the real shape is: add a `csnobol4_bin()` resolver to `lib_oracle_flags.sh` with the same `assert`-and-refuse-loudly discipline the SPITBOL resolvers already have, decide where the shared csnobol4 oracle lives (`/home/resources/`, beside the other shared oracles, matching the s255 two-oracle ruling's pattern), and only then point the `csnobol4_suite` row at it. That is an oracle-topology decision, not a scorecard tweak, which is why it is written down here rather than committed.
