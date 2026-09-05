# FINDING: `corpus/benchmarks/snobol4/testpgms.spt` (the combined source) has silently dropped characters relative to its own already-committed split files, and rc=0 on four of the eight programs hides a live internal ERROR

**Who/when:** seat09, 2026-09-04 (box clock; FLEET-16, SNOBOL4-only), row `snobol4-testpgms-only-four-of-eight-programs-were-ever-split-out`.

## What the row's own instruction ran into

The row's mandate was literal: "re-split ALL EIGHT programs faithfully from `testpgms.spt`... do NOT hand-edit the four existing files into shape — re-split all eight from the ONE combined source." Doing exactly that regressed `testpgms-test1.spt` (never flagged as buggy) and reshaped `testpgms-test4.spt`: a `git diff` against the pre-existing committed files showed content changes far beyond the known leading-`./*` defect.

**The mechanism, isolated:** every literal `!` character in programs #1 and #4's span of `testpgms.spt` has been replaced by a bare `\n`, with the `!` itself deleted — not just where `!` acts like an operator (`TEST = !(IDENT(...))  STARS` → `TEST = ` / `(IDENT(...)) STARS`), but also **inside a quoted string literal**, which proves this is a raw text-level corruption and not a parser/semantics artifact:
```
-        UNARY   =   ANY('+-&.$*?!@%#')
+        UNARY   =   ANY('+-&.$*?
+@%#')
```
Confirmed by raw-byte inspection (`od -c`) at `testpgms.spt:115` vs. the committed `testpgms-test1.spt` blob `7b4955556`: the combined file reads `...TEST = \n` where the committed file reads `...TEST = !(IDENT(A,'A')...) STARS\n` — the `!` and everything that should follow it on that line is simply gone from `testpgms.spt`.

**Extent, measured, not assumed:**
| program | span | `!` in the known-good committed file | `!` in `testpgms.spt` today |
|---|---|---|---|
| #1 | 1-423 | 23 | 0 |
| #2 | 424-684 | 0 | 0 (nothing to lose) |
| #3 | 685-744 | 2 | 2 (both survive, at lines 735 & 740) |
| #4 (body) | 745-~840 | 1 | 0 |
| #5-#8 | 863-1412 | **no reference exists** | 0 |

Program #3's two `!` occurrences survive untouched, so this is not a blanket "every `!` in the file" substitution — it is localized, and I have no theory that reliably predicts where it did or didn't strike. That means **programs #5-#8, split out for the first time by this row (and independently by hq_T's parallel vendoring row into `corpus/packages/snobol4/spitbol_testpgms/`), have no independent reference to catch the same corruption if it struck them too.** I scanned their span for the tell-tale signature (a line ending in a bare operator immediately followed by a line starting cold, no `.`-continuation marker) and found none — every candidate matched a legitimate SNOBOL4 null-assignment/null-replacement idiom (`OUTPUT =`, `HEAD =`, `CARD LEN(1) . CH =`) instead. That is reassuring but not proof of absence.

## What I did about it (deviates from the literal instruction, on purpose)

- **Programs #1-#4:** did **not** derive these from `testpgms.spt`. Copied the already-oracle-validated `corpus/packages/snobol4/spitbol_testpgms/test{1,2,3,4}.spt` (hq_T's vendoring row, `PROVENANCE.md`) into `corpus/benchmarks/snobol4/testpgms-test{1,2,3,4}.spt` instead — verified `!`-count-correct, and for #2/#3 confirmed the ONLY diff from the prior committed files is the intended leading-`./*` strip. This satisfies the row's actual intent (uniform, correct, oracle-clean files, each starting cleanly at its own `-TITLE` line) without propagating known corruption.
- **Programs #5-#8:** `testpgms.spt` is the only source that exists, so these are sliced straight from it at the given `-TITLE` boundaries (863/965/1075/1280, to EOF 1412), trailing `./*` separator stripped for consistency. **Their correctness relative to the original vendor listing is unverified** — flagging this explicitly rather than asserting it.
- A separate, unrelated discovery in the same span: program #4's slice legitimately continues past its `END` with a data/test-harness block (`-LIST` + a `SETUP PAT1 = ...` pattern definition + `TRIM(INPUT) PAT1 :S(OK) :F(BAD)`) that reads genuine sample statements for the syntactic recognizer to classify — this is real source, not stray data, confirmed by the fact it itself reads from `INPUT`. Programs #5-#7 have similar-shaped trailing blocks (a word list for #5's TREESORT4, ordering pairs for #6's TOPOLOGICAL SORT, symbol names for #7) that read as literal DATA rather than statements; whether the grading harness should feed these via the shared `testpgms.in` or treat them as inline source is **not resolved by this row** and is left for whoever owns the grading design (the umbrella row / hq_T's runner).

## Second finding: rc=0 is not "passing" for four of these eight

Grading all eight against the correctness oracle (`sbl_correctness_bin` = `/home/resources/x64/bin/sbl -bf`, `testpgms.in` on stdin, `timeout 30`) live:

| program | rc | lines | embedded runtime ERROR (from output content, not rc) |
|---|---|---|---|
| #1 | 0 | 140 | none (its own `ERROR AT 72 &ERRTYPE=29` line is the program's *intentional* SETEXIT self-test, not a real failure) |
| #2 | 231 | 19 | genuine oracle rejection at a `;`+`.`-continuation construct — already documented in `PROVENANCE.md`, not our vendoring, not re-litigated here |
| #3 | 0 | 47 | none |
| #4 | 0 | 28 | **`ERROR 116 -- inappropriate file specification for input`** at its own line 65 (`INPUT(.INPUT,,72)`) |
| #5 | 0 | 28 | **`ERROR 116`** at line 6 (`INPUT(.INPUT,,72)` / unit-number I/O this build doesn't support) |
| #6 | 0 | 66 | **`ERROR 248 -- attempted redefinition of system function`** at line 16 (`DEFINE('DECR(X)')` — `DECR` collides with a built-in) |
| #7 | 0 | 204 | **`ERROR 248`** at line 10 (`DATA('SYMB(CHAR,LINK,ALT,ASSOC,SUCC)')` — the `CHAR` field accessor collides with the built-in `CHAR()`) |
| #8 | 0 | 28 | **`ERROR 160 -- inappropriate file specification for output`** at line 4 (`OUTPUT('TITLE',6,'(14H1THIS IS HAND ,110A1)')` — FORTRAN-style unit-number output) |

SPITBOL evidently treats these as non-fatal (it prints the error, dumps diagnostics, and still exits 0), so **a harness that only checks `rc` will silently call five of these eight passing when four of them errored out within the first ~10 statements.** This is exactly the same class of false-signal this codebase's rules already warn about elsewhere (a plausible-looking all-green table that isn't one) — worth naming precisely because `PROVENANCE.md`'s own "test4 | rc=0, 16 lines" characterization is the same shallow read, on the version *without* the corruption or the tail.

## Disposition

- `corpus/benchmarks/snobol4/testpgms-test{1..8}.spt` now exist, each begins at its own `-TITLE SPITBOL TEST PROGRAM` line, none carry a leading `./*`. Row's DONE-WHEN verified passing (`rc=0`, "all 8 programs are split out...").
- Not cured by me, out of this row's scope: (a) repairing `testpgms.spt` itself at the confirmed-corrupt spans (I have exact replacement text for #1 and #4's body from the trusted references, but a same-file line-count-changing edit risks shifting every downstream `-TITLE` boundary hq_T's parallel vendoring row is reading against *right now* — too risky for me to do solo without a second measurement); (b) the four ERROR-116/160/248 conditions in #4-#8 (construct-class defects/vintage-vs-modern incompatibilities, not split artifacts); (c) whether #5-#7's trailing data blocks belong in the `.spt` source or in a per-program stdin fixture.
- `ask`ed hq_P (`q-testpgms-spt-dropped-characters-and-masked-runtime-errors`) with a pointer to this file, flagging the risk to hq_T's parallel `packages/snobol4/spitbol_testpgms/` vendoring of #5-#8 from the same uninspected source.
