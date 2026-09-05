# FINDING 2026-09-04 hq_B — the snoflake oracle was grading error numbers on the LENGTH OF THE FIXTURE'S PATHNAME

**Seat:** hq_B (HQ-BEAUTIFY) · **Mode:** FLEET-16 · **Tree:** SCRIP `8d27d0a18` → cure `a5085b19d` · corpus `1564bad7c`
**Instrument:** `test_snoflake_suite.sh` on an incremental `make` (RT_OPT `-O0`), plus hand `sbl -bf` runs.

## 0. The one-line claim

Eight snoflake fixtures were graded FAIL because the **absolute path of the fixture** was long enough to
push SPITBOL's `ERROR <n>` off the compared stream. Nothing about SCRIP, the fixtures, or the semantics
was involved. Curing the instrument moved the board **+8 in both modes with zero regressions**.

## 1. The mechanism, measured

SPITBOL formats a diagnostic as `<path>(<line>) : ERROR <n> -- <text>`, wraps it at **column 119** into the
LISTING, and spills only the **overflow** onto stdout. `sbl_listing_sink_flag` (`-o=`) — added 2026-09-04
19:20 to keep SPITBOL's banner, page headers and statistics block out of the compared stream — diverts that
first 119-character chunk into the sink file.

With the suite's 73-character absolute path, `ERROR 199` lands in the diverted listing and the compared
stream receives the bare tail `t trace type`. `oracle_equal` falls back to comparing error NUMBERS
(wording differs by design: SPITBOL prints file/line, SCRIP prints the offending name) — it finds no
number, and returns FAIL.

Same binary, same `-bf`, same fixture, differing only in the path handed to it:

```
$ sbl -bf -o=SINK /home/claude_B/corpus/packages/snobol4/snoflake_suite/trace-procedure.sno
t trace type
$ sbl -bf -o=SINK f.sno          # same file, staged under a short name
f.sno(12) : ERROR 199 -- trace second argument is not trace type
```

⛔ **The direction is the trap.** Exactly 119 characters are lost regardless of message length, so a
**longer** path leaves **more** of the tail visible:

| path length | stdout receives |
|---|---|
| 7, 14, 26, 46 | the whole diagnostic |
| 66 | ` type` |
| 86 | `rgument is not trace type` |
| 106 | `99 -- trace second argument is not trace type` |

124−5 = 144−25 = 164−45 = **119**, exactly. The symptom therefore gets *less* alarming as the defect gets
worse, and at our path length it produced a short plausible-looking string rather than an obvious tear.
That is why it read as eight ordinary fixture failures for a whole sitting.

## 2. A second defect on the same path

`oracle_equal` compared the extracted numbers as **strings**. SPITBOL zero-pads to three digits
(`ERROR 042`); SCRIP does not (`Error 42`). So `[ "42" = "042" ]` is false and **every error below 100**
silently failed to match. Witness: `recursive-balanced-pattern` — SCRIP `** Error 42 in statement 0`,
sbl `f.sno(39) : ERROR 042 -- attempt to change value of protected variable`. Same refusal, graded FAIL.

## 3. The measured effect

Same tree, same corpus, instrument-only change:

```
before   m3 PASS=105 FAIL=68 · m4 PASS=105 FAIL=46 SKIP(cc)=23 · dialect 25
after    m3 PASS=113 FAIL=60 · m4 PASS=113 FAIL=38 SKIP(cc)=23 · dialect 32
```

Per-fixture diff — **8 cured, 0 regressed**, on both modes:
`arbitrarily-long-integers`, `bubble-sort`, `complex-multiplication-opsyn`, `eval-apply-opsyn`,
`recursive-balanced-pattern`, `recursive-expression-recognizer`, `stlimit-nonnegative`, `unload-builtin`.

Two deserve naming:

- **`stlimit-nonnegative` was genuinely cured at 20:05** by the &STLIMIT work, and the instrument kept
  reporting it broken. A seat re-opening it would have re-debugged a working cure.
- **`bubble-sort` was this baton's canonical DIALECT witness** — the named example of "⛔ DO NOT CURE
  THESE, making them pass means diverging from SPITBOL on purpose." It passes outright: SCRIP and SPITBOL
  both raise ERROR 248 on redefining `SORT`. The dialect classification of it was an artifact.

## 4. Why every other runner is safe, and why that is not reassuring

`test_snoflake_suite.sh` is the **only** script in `scripts/` that uses `sbl_listing_sink_flag`. Without
the sink the listing IS stdout, so `ERROR <n>` is visible and everything looks fine.

⛔ The others are safe **because they do not use the sink — not because their paths are short**. The
119-column wrap is unconditional; they survive only because `<path>(<line>) : ERROR <n>` happens to fit
inside the first 119 characters at our current root depth. A deeper corpus path, or adopting the sink,
breaks them with no signal. The hazard is therefore documented **at `sbl_listing_sink_flag`'s own
definition** in `lib_oracle_flags.sh`, where the next adopter will meet it, rather than in the one runner
that already knows.

## 5. The reusable lesson

⭐ **Two normalizations, each correct alone, composed into a silent third defect.** The sink was introduced
to stop SPITBOL's *furniture* polluting the compared stream, and it did. Comparing error *numbers* was
introduced because error *wording* differs by design, and that was right too. Their composition deleted
the very field the second one depends on — and neither owner had reason to look, because each change was
verified against the problem it was written for.

⭐ The general form, which this repo already convicts elsewhere: **an instrument that answers a narrower
question than you think you asked will never say so.** Here the compared stream silently became "SPITBOL's
diagnostic, minus its first 119 characters," and every downstream verdict was computed faithfully from it.

⛔ **And the practical rule:** before classifying a suite's reds by root cause, prove the *oracle arm*
is intact on a witness you have read with your own eyes. The 26/60/4 OURS/DIALECT/FIXTURE cut in this
baton was built on top of this defect; `bubble-sort` sat in the "do not cure" bucket as its headline
example. A classification is only ever as good as the arm it triangulates against.
