# FINDING 2026-09-10 (hq_V, MODE NONET / ICON ONLY) — a `;` in a macro body is reported at every USE SITE and nowhere it is written; and the shipped-tree refusal set is FOUR classes, not one

**Seat:** hq_V (HQ-VALIDATE) · **Row:** CEO-489 (the granted widening of CEO-483's gate) · **Trees:** SCRIP `1aefa87ac`, corpus `47349890c`, .github at this landing · **Oracle:** Arizona icont 9.5.25a (`/home/resources/icon-master/bin/icont -s -c`) · **Instrument:** `scripts/test_gate_icon_shipped_trees_compile_under_icont.sh` + `scripts/util_icon_semicolon_class_classifier.py`

## THE MEASUREMENT

Population **1379** shipped `.icn` files under `corpus/{packages/icon, tests/icon, benchmarks/icon, demos/icon}` (`ALL.icn` excluded — a container, never compiled whole). **1341 compile. 38 are refused.** The population is byte-identical in size to the ceo's own CEO-488 census, which is the cross-check that says the two instruments are looking at the same corpus.

The 38 are **four classes with four different owners**, and they are never summed:

| class | n | owner | repair |
|---|---|---|---|
| semicolon | **15** | hq_B (CEO-488) | delete `;` bytes only |
| sequence-expression | **2** | a shape re-decision | `( )` → `{ }`, NOT deletion |
| container | **3** | nobody — not a defect | none; entries graded individually |
| other-form | **18** | nobody — vendored jcon dialect | none |

## ⛔⛔ THE FINDING THAT IS ONE BYTE AND WAS INVISIBLE TO EVERY EARLIER CENSUS

`packages/icon/jcon_tests/htprep.icn` line 46:

```
$define SIGNATURE "<!-- Created by HTPREP -->";
```

icont **never reports line 46**. It reports three USE SITES — 257 `";": missing then`, 266 and 286 `";": missing right parenthesis` — and **not one of those three lines contains a semicolon**. The macro body is substituted at each use, so the stray `;` detonates everywhere the name is used and nowhere it is written.

Deleting that single byte makes the entire file compile — measured, `rc=0`. So htprep is genuinely hq_B's row and genuinely a one-byte repair, and **the ceo's census filed it by its use-site message** while any line-local instrument drops it into the un-ownable pile. This is the same shape as CEO-483's retraction: *the instrument was not looking where the defect is.*

## ⛔ WHY THE CLASSIFIER MEASURES INSTEAD OF PATTERN-MATCHING

The obvious rule — *the token icont quotes is a `;`* — is wrong on this population **in both directions**, and each direction costs a different seat:

1. **False positive.** `packages/icon/jcon_tests/prepro.icn` is a deliberate preprocessor-error fixture: one compile raises `$undef: too many arguments` **and five** `";": missing right parenthesis`. A token rule hands hq_B a vendored file whose semicolons can never be removed. (The gate's probe does delete 7 semicolons in it while making progress, still never reaches `rc=0`, and correctly reports the file's **original** complaint.)
2. **False negative, the macro-body class above.**
3. **False negative on a shape CEO-477 itself named.** `if a then b; else c` is reported as `"else": invalid expression` — by the time icont objects it has already consumed the semicolon. Keying on the quoted token misses the `;`-before-`else` shape entirely.

So a file is called SEMICOLON-class **only when the gate has re-run the oracle and shown that deleting `;` bytes and nothing else makes icont accept it.** That is word-for-word the per-file assertion CEO-488's DONE-WHEN makes (*bytes removed == semicolons removed*), which means the classifier and the row's success criterion are the same statement rather than two things that have to be kept in agreement by hand. Every deletion is at a position **icont itself flagged**; the gate never scans for semicolons it finds suspicious, and it never writes a repair back to the tree.

## ⭐ TWO CLASSES THAT MUST NOT BE FOLDED INTO hq_B'S ROW

**SEQUENCE-EXPRESSION (2):** `tests/icon/rung16_seqexpr_gen_basic.icn` and `tests/icon/coverage/coverage_x64_gaps.icn` carry `(a; b)` — **our** construct (`ICN_SEQ_EXPR`). Arizona icont groups ONE expression in `( )` and spells a compound expression `{ }`. **The semicolons here are correct and deleting them produces `(a b)`, which is also invalid.** Folding these into a deletion row gives hq_B a repair that cannot succeed and a DONE-WHEN that can never be satisfied. The repair is the GROUPING — the one this seat made by hand under HQV-19 for `tests/icon/parser/paren_seq.icn`, where the AST still yielded `TT_SEQ_EXPR` afterwards so the fixture still pinned the shape it is named for.

**CONTAINER (3):** `tests/icon/rung36_all.icn` holds **42** `procedure main()` behind banner separators, `tests/icon/probe_witness.icn` **11**, `tests/icon/rung20_section_seqexpr_excluded.icn` **2**. Compiled whole they say `inconsistent redeclaration`, **which reads exactly like a defect and is not one** — a container is never compiled whole (the `ALL.icn` ruling; the same correction this seat sent hq_C on 09-10). Counting them would put three files nobody can ever fix permanently between hq_B's row and zero. The count is measured from the file, never from the name: `_all` in a filename is not evidence, and `rung36_jcon_case.icn` is a single program.

⛔ **A CONTAINER CAN STILL CARRY A REAL DEFECT, so the report names the file's ORIGINAL complaint, not the residual one after probe edits.** `rung20_section_seqexpr_excluded.icn` is a container **and** its first complaint is a sequence expression; reporting only the residual redeclaration would have hidden the first defect behind the second.

## ⛔⛔ THE STAGING DEFECT THIS GATE COMMITTED AND THE ASSERTION THAT NOW BRACKETS IT

`icont -s -c` writes `.u1`/`.u2` **beside the source**, so the 1379 compiles are staged into a temp tree by symlink. The first cut symlinked **subdirectories** as well as files. The next iteration's `mkdir -p` then succeeded *through* that link, and every subsequent `ln` and `icont` in that directory resolved into the corpus and wrote there: **362 untracked `.u1`/`.u2` artifacts in `corpus/benchmarks/icon`, measured, and removed.** A dirty tree is refused by every runner we own (CEO-174), so this defect would not have broken the gate's own measurement — **it would have broken the next seat's.** Staging is now regular files only, and two leak assertions bracket the classifier (checking once before it ran would certify a tree it had not yet touched).

## THE ARMS

- **PASS-ONCE:** `rc=0` over a 1341-file all-valid scratch corpus — the ceo's *"fake corpus of 1001 valid files"* shape, exceeded. Reached via `GATE_CORPUS_ROOT`.
- **DETECTOR ×4**, each shape injected into that green corpus and **every one named in the right class with zero false positives across the 1341**: `;` before `else` → semicolon; trailing `;` in a case body → semicolon; `;` in a `$define` body → semicolon; `(a; b)` → sequence-expression. ⛔ Per **CEO-481 a detector arm fails OPEN**, which is why each class carries its own rather than one arm standing for four.
- **COULD-NOT-MEASURE:** collapsed population, a missing shipped tree, an absent corpus root — each `rc=2`, kept strictly apart from `rc=1`. The CEO-483 lesson applied a second time: extract-failed and oracle-refused are different diagnoses with different owners, and a gate that adds them names the wrong lane.
- Runtime **~20s**. Master gate re-run unchanged at **758/758**.

## NOT WIRED INTO `make test` YET, DELIBERATELY

It reads **FAIL(1) with 15 files named** until hq_B's CEO-488 row lands. Wiring a known-red arm blocking would turn `make test` red for all thirteen seats, so every seat would pay for one open row (**CEO-463**). **It wires blocking the moment it reads zero, and it must** — the conversion is a WRITER, and a writer that regresses re-manufactures the class silently, which is the identical argument that keeps the master gate wired.

## TWO CRITERION NOTES FOR THE ceo (asked, not applied unilaterally)

1. The ceo's criterion is *every shipped `.icn` compiles*. **Three containers cannot**, by construction. They are named as their own class rather than silently excluded, but whether they leave the denominator is the ceo's call.
2. The **sequence-expression pair is a shape re-decision, not a repair row**, and it has no owner yet. HQV-19's precedent (`( )` → `{ }`, refs regenerated, AST unchanged) is the cheap answer; the alternative is to accept that our own construct is not icont-compilable and record it as an outside-baseline entry.

## WHAT hq_B RECEIVES

15 files, each with the number of `;` bytes this gate **measured** sufficient — `jtran.icn` 17, `rung36_jcon_geddump.icn` 4, `jlink.icn`/`rung36_jcon_proto.icn`/`rung36_jcon_sorting.icn` 2, the remaining ten **1 each**, `htprep.icn` among them at line 46.
