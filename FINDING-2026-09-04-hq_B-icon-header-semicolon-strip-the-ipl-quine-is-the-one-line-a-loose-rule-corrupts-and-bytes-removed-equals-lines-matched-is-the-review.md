# FINDING — the Icon header-semicolon strip: the IPL quine is the one line a loose end-of-line rule corrupts, and `bytes-removed == lines-matched` is the review

**Seat:** hq_B · **Date:** 2026-09-04 · **Row:** `icon-no-semicolon-after-procedure-header-corpus-stripped-everywhere` · **Landed:** corpus `5e921aa3a` (the strip), SCRIP `5f31265f9` (LOCK 4 brace arms out) · **Law:** Lon 2026-09-04 ~13:55 via ceo, RULES.md § ABSOLUTE RULES ICON SEMICOLON-REQUIRED as amended

## The claim

A mechanical "one byte per matching line" rewrite over 1,150 Icon files has exactly one line in this corpus that a loose rule gets wrong, and it is a self-reproducing program. The strip was made unable to match it rather than told to skip it by name. The rewrite was reviewed by counting identities, not by eye — and the one time the count disagreed with the plan, it was the count that was right. Then, today, the row's own acceptance criterion turned out to carry the loose rule the strip had refused, and read RED on the landed tree for that same line. Three facts, each measured.

## What landed (for the record — the chat is not the record)

- **No parser change.** SCRIP already ran `procedure main()` + `end` with no semicolon (rc=0, correct output) — the ceo measured it before minting and hq_B re-measured it before touching anything. The row was corpus-only.
- **corpus `5e921aa3a`:** 1,150 files, **6,181 insertions, 6,181 deletions** — the diffstat is symmetric by construction, because every change is one `;` byte off one line. Packages included, deliberately: those header semicolons were our own 2026-09-02/03 addition (`ba07c0350`, `f8fe5b83d`), so stripping them RESTORES upstream form.
- **SCRIP `5f31265f9`:** `test_gate_icn_semicolon_required.sh` LOCK 4 (seat02's brace-dialect probes) removed and named, LOCKs 1–3 still hold: Icon does no newline processing and `;` stays mandatory BETWEEN statements. `end;` is rejected by icont and SCRIP alike; the corpus carried zero of them.
- **Boards identical before and after**, checked against numbers written down BEFORE the freeze rather than reconstructed after: Icon ladder `--to 37` = 420/420 over 210 witnesses; Icon master entries 749, run-graded m3 595/596 · m4 595/596, FAIL=0 XPASS=0 XFAIL=1, ast 153/153. A strip of a character the parser never needed moves no verdict; a moved verdict would have been a converter defect.
- **Freeze:** declared explicitly with a start time (14:0x CDT) because hq_P had earlier *inferred* one from a law telegram and stopped work on nothing; unfrozen on push, minutes later.

## Fact 1 — the quine: `packages/icon/ipl/progs/repro.icn` is spliced through a hard-coded index

Its whole program is two lines (26–27 of the file, after the IPL header comment):

```
procedure main();x:="procedure main();x:= \nx[21]:=image(x);write(x);end";
x[21]:=image(x);write(x);end
```

`x` is a string literal quoting the program's own text; `x[21]:=image(x)` splices the quoted-and-escaped image of the string back into itself at **column 21**, the position just after `x:=`; `write(x)` then prints the program. Re-verified today with the real oracle (`icont -s`, `iconx`, rc=0): output line 2 is byte-identical to source line 27, and output line 1 is source line 26 minus the trailing `;` — the statement terminator that OUR 09-02 semicolonization appended, which the quine's own string cannot know about. (That residual byte is the semicolon-required dialect's cost on this one program and is not this row's business; it was there before the strip and it is there after.)

**Why a loose rule corrupts it.** The natural strip pattern is *"a line that starts with `procedure` and ends with `;`"* — `^\s*procedure\b.*;\s*$`. Line 26 matches it. Stripping its last byte removes the **assignment's** terminator, not a header semicolon. And the header semicolon it *does* contain (`procedure main();`) cannot be touched either: it is inside the text the string literal quotes, and editing the header without editing the literal desynchronises the program from its own image and invalidates the index 21. **The program would still compile and still run — it would just stop printing its own source.** No board would catch it: the IPL suite is compile-graded (upstream ships no `.std` oracle), so a silently-wrong quine is exactly the shape of defect that survives a green board.

**Measured, not argued:** the strict header-only pattern — *`procedure` NAME `(` params `)` `;` end-of-line, nothing else on the line* — matches **1,150 files / 6,181 lines**; the loose end-of-line rule matches **1,151 / 6,182**; the single line in the difference IS `repro.icn:26`. The reusable artifact is the pattern itself:

```
^[[:space:]]*procedure[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]*\([^)]*\)[[:space:]]*;[[:space:]]*$
```

**Why strictness and not a name-skip.** A skip-list entry (`repro.icn`) stops protecting the moment the file is copied, renamed, or a second quine is vendored. A pattern that *cannot* match the dangerous shape protects every file that has that shape, including ones nobody has looked at. The general form: when a transformation has a known counterexample, encode the counterexample's *shape* in the matcher, not its *name* in an exclusion.

## Fact 2 — `bytes-removed == lines-matched` is the review, and it caught the one over-reach

A 6,181-line diff is not reviewable by eye, so the strip carried three counting identities, asserted per file and again in aggregate:

- lines changed **==** lines matched
- bytes removed **==** lines changed (one byte per line, exactly)
- diffstat insertions **==** deletions

The first attempt failed the second identity on one file: **23 bytes removed for 22 lines matched**. The cause was a header with a trailing space after its semicolon — the pattern's trailing `\s*$` had let the removal eat the whitespace along with the `;`. Nobody would have seen one extra byte of trailing whitespace in a 6,181-line diff. The assertion saw it before the diff existed. 191 already-rewritten files were reverted and the removal was made surgical — exactly the one `;` byte, the trailing whitespace left as found — after which every identity held on every file.

⭐ The lesson is not "check your work"; it is **that for a mechanical rewrite the counting identities ARE the review, and they must be stated as equalities the tool asserts, not as expectations a human holds.** An expectation held by the author is exactly as reliable as the author's attention on the 4,000th file.

## Fact 3 — the acceptance criterion carried the loose rule, and read RED on the correct tree

The row's DONE-WHEN (ceo, 14:01) censused *"zero header-semicolon lines across every tracked `.icn`"* with:

```
grep -lE "^[[:space:]]*procedure[[:space:]].*;[[:space:]]*$"
```

— the loose end-of-line rule. On the landed tree it reads **1 file: `repro.icn`**, so the row's own gate was RED for the one line the strip was *right* not to touch, and `s4e_msg.sh done` would have refused a landed, correct, board-identical row forever. Re-cut today to the strict pattern above (reads 0), with the ledger line naming this FINDING as the reason.

⭐ **The general form is the one worth keeping:** a rule stated loosely in a brief ("strip the `;` from lines ending in `;` after `procedure`") gets transcribed loosely into the gate that certifies it, and the gate then contradicts the correct implementation *precisely where the implementation was careful*. The strictness has to be written down once, as a pattern, and both the tool and the gate must cite that pattern — never paraphrase it. This is `RULES.md` § TRANSCRIPTION IS WHERE PROVENANCE DIES applied to a regex.

## Kin

- `FINDING-2026-09-04-seat01-icon-source-rewriter-three-bugs-retired-brace-converter.md` — the paren-depth reset, the `\^X` escape width, and comment loss in the retired brace converter. Same family: **Icon source is full of string literals and escapes, and a rewriter that does not parse them will be wrong on some line.** The counting identities above are how you find *which* line before the diff lands.
- `FINDING-2026-09-03-seat08-icon-ipl-semicolon-conversion-two-real-bugs-found-and-fixed-in-the-shared-transform.md` and seat16's companion — the 09-02/03 conversion that ADDED the semicolons this row removed; the quine survived that pass too, by luck rather than by pattern.

## Not claimed

The strip tool itself was a scratch script and is not committed; the artifacts that outlive it are the strict pattern, the three identities, and the measurements quoted here. The 24 rung36 STRICT `.xfail` markers and the master's former XFAIL entry are a different row and a different FINDING.
