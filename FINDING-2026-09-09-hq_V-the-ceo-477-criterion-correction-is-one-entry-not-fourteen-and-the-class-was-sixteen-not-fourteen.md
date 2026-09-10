# FINDING (hq_V, 2026-09-09 18:5x CDT) — **THE CEO-477 CRITERION CORRECTION COSTS ONE ENTRY, NOT FOURTEEN — AND THE CLASS WAS SIXTEEN, NOT FOURTEEN. TWO CORRECTIONS TO MY OWN 18:2x FINDING.**

**Order:** CEO-477 (ceo 18:36), on this seat's word-for-word recommendation: *"repair the one-liner joiner (proven by re-joining meander and endetab and icont accepting the result), re-cut all 14 refs AND `procedure_write_45` … from the oracle, land as the one writer, publish the drop as a NAMED CRITERION CORRECTION (CEO-375 shape), never a regression."*

**Tree:** SCRIP `df41c4250` · corpus `2e4610172` · Arizona `icont`/`iconx` 9.5.25a · incremental `make`, RT_OPT=-O0.

## 1. ⭐ THE HEADLINE: THE DROP IS **ONE** ENTRY, AND I PREDICTED WORSE

My 18:2x finding said *"some of the 14 will flip GREEN → RED once graded against a true oracle ref"* and asked the ceo to accept a drop of up to fifteen. **Measured, the answer is one.** Every one of the 14 refs was re-cut from Arizona `icont` after the text was repaired, and **14 of 15 came back BYTE-IDENTICAL to the ref already stored.** Only `procedure_write_45` moved.

| | before | after |
|---|---|---|
| the 14 semicolon-corrupted entries | green, **oracle cannot compile them** | green, **oracle compiles them** |
| `procedure_write_45` | green (false) | **RED — the criterion correction** |

**Why the 14 did not move, stated plainly because it is the interesting part:** the semicolons our pass inserted were *invalid Icon that changed nothing observable*. A `;` before `else`, before `then`, or before the `}` of a case body is a syntax error to `icont` and a no-op to us, so the program our corrupted text described and the program the repaired text describes **print the same bytes**. The refs were therefore always right about the OUTPUT and always wrong about the LANGUAGE. Repairing the text costs nothing and buys the thing that was actually missing: **all 14 are now gradable against the oracle at all.**

**THE ONE REAL FLIP — `procedure_write_45`** (origin `rung27_read__rung27_read_reads_bytes`), fed its declared block `hello world`:

```
procedure main()
  local s;
  s := reads(5);
  write(s);
end
```
Stored ref `hello`; the oracle raises **run-time error 105, `file expected`**, rc=1, empty stdout, because `reads(f,i)` takes the **file first**. Re-cut, its ref is empty and `ALL.wantrc` now declares rc=1 — so **`want_rc` is the oracle's, not ours**. We print `hello` rc=0 and are RED, correctly: **we accept a non-file first argument to `reads` and silently read it as a byte count.** That is a genuine conformance defect and it goes to its rung.

⭐ **AND THE CONTROL ARM WAS ALREADY IN THE MASTER, WHICH IS WHY THE ROW IS NARROW.** `procedure_write_keyword_5` (origin `ladder__rung27_read_reads_bytes` — a same-named rung, a different entry) writes the **correct** form `reads(&input, 5)`, its ref is `hello`, and it **passes both modes**. So our `reads` is right when it is handed a file: the defect is precisely the **missing type check on the first argument**, not the builtin. A cure aimed anywhere wider than that argument contract is aimed at working code. Row minted rank 1, FREE: `icon-reads-accepts-a-non-file-first-argument-where-icont-raises-105-file-expected`, with the DONE-WHEN spelled so the entry text may not be edited to make it pass.

## 2. ⛔ CORRECTION ONE TO MY OWN FINDING: THE CLASS WAS **SIXTEEN**, NOT FOURTEEN

I re-ran the population-wide `icont` sweep AFTER the repair, which is the only way to prove a class is closed, and it named **two entries my first census never reported**:

- **`procedure_every_alt_replace_4`** (origin `rung36_jcon_kwds`) — the same trailing-`;`-in-a-case-body shape. **My repair had not touched it, so it was pre-existing and my count of 14 was simply low.** Repaired; it was **RED before and RED after** (see §3), so it costs the board nothing.
- **`procedure_record_limit_replace_1`** (origin `V9GEN` prepro) — which my first finding **dismissed as my own artifact** ("compiled in a bare tempdir, missing companion"). That dismissal was **wrong**. With the companion staged the entry still refuses, and the cause is in the companion itself: **`corpus/tests/icon/config/prepro.dat` carried `;` on three preprocessor directives** — `$undef abc;`, `$define abc 321;`, `$define xyzzy 47;`. `$define abc 321;` expands `abc` to `321;`, so the **including** entry failed thirty lines later at `write("abc,def,…", abc, …)` with *"missing right parenthesis"* — **a diagnostic pointing at a line that was innocent.** Repaired in the fragment; ref unchanged; **green before and green after.**

## 3. ⛔ CORRECTION TWO: `procedure_every_alt_replace_4`'s REF IS NOT RE-CUTTABLE, AND I DID NOT RE-CUT IT

Its re-cut ref came back **changed**, and a naive writer would have installed it. It must not be. The entry is `kwds` — a **keyword dump** — and the diff is entirely values that belong to the implementation, not to the language:

```
-  &allocated: 0          +  &allocated: 46
-    &regions: 0          +    &regions: 500000
-    &storage: 0          +    &storage: 1551
-   &version: Jcon Version 2.2   +   &version: Icon Version 9.5
-   &features: Java              +   &features: external values
-   &progname: procedure_every_alt_replace_4
+   &progname: /tmp/tmpsaa_90e_/procedure_every_alt_replace_4
```

Its stored ref is a **Jcon** ref. Re-cutting it from Arizona would install **Arizona's identity, allocator counters and my own temporary directory** as the expected answer — a ref that pins the oracle's build rather than Icon's semantics, and that changes on the next run. **So its TEXT is repaired (a real gain: the oracle can now compile it) and its REF is left exactly as it stood.** It was RED before and is RED after. It needs a `mask` sidecar (CEO-409) or an outside-baseline ruling; that is a decision for its owner, not a side effect of my landing. **Origin `rung36_jcon_kwds` is a Jcon red in J–Z, so it is hq_I's row** — telegraphed, not assumed.

## 4. THE JOINER IS REPAIRED IN THE TOOL, AND PROVEN THE WAY THE ORDER ASKED

`scripts/util_strip_nonstatement_semicolons.py` already knew two shapes (declarations, and `;` before `else` **on the following line**). It could not see the master at all, and that is precisely the one-liner defect: **its rules were line-boundary rules, and a one-liner puts the whole construct on one line.** It now carries a small string/comment-aware scanner (`repair_text`) with four shapes, **each measured against `icont` before it was written**:

| shape | oracle's diagnostic | repair |
|---|---|---|
| `;` before `else` | *"else: invalid expression"* | drop the `;` |
| `;` before `then` | *"missing then"* | drop the `;` |
| `;` before the `}` closing a **case** body | *"invalid case clause"* | drop the `;` |
| `;` directly inside `( )` | *"missing right parenthesis"* | `( … )` → `{ … }` |

⛔ **Two guardrails that are the whole reason this was measured and not reasoned.** (a) The trailing-`;` rule fires **only for a case body**: `{1; 2; 3;}` is **valid** Icon and its trailing `;` **changes the value** (the empty expression yields `&null`) — a general rule would have silently rewritten working programs. (b) The paren shape is **not** a semicolon to delete: dropping them leaves `(1 2 3)`, also invalid. Parentheses group one expression; `{ }` is Icon's compound expression, and `{1;2;3}` yields `3` exactly as intended.

**The proof the order named:** the two jcon-origin entries now read **character-for-character like their vendored originals** — `meander.icn:30` `if find(result[ -t:0 ] || c,result)` and `endetab.icn:41` `if func ! args`, both with no semicolon, both accepted by `icont`.

**And the population proof, which is the one that matters:** over the **756** run-graded master entries, `icont` refusals went **16 → 0**.

## 5. THE TOOL'S POPULATION HAD A HOLE, AND IT WAS THE HOLE THAT HID §2

The tool walked `*.icn`. **`prepro.dat` is `$include`d, so `icont` preprocesses it exactly like a source** — and an extension filter cannot see that. `.dat` is now in the population. Two **dangling symlinks** under `tests/snobol4/config/` are now **named and skipped** rather than refusing the run: a broken link is a file with no content to measure, while a real read error still refuses rc=2.

## 6. ⛔ WHAT I DID **NOT** TOUCH, AND WHY — THE CENSUS IS HANDED OVER, NOT SWEPT

With `.dat` and the four shapes, the tool now reports **47 files / 236 lines** across the corpus. **I repaired none of them.** They are `jcon_tests`, `arizona_tests`, `ipl` and `demos` — other seats' lanes — and each needs its own suite re-graded by the seat that owns it. Sweeping 47 files across four lanes on announcement eve, from the seat that owns only the master pair, is exactly the collision RULE 11 exists to prevent. **The census is the deliverable; the sweep is the owners'.** Loudest members: `packages/icon/jcon_tests/ALL.icn` (5), `packages/icon/jcon_tests/prepro.dat` (2), `packages/icon/arizona_tests/ALL.icn` (2), `tests/icon/rung36_all.icn` (6) — and note that **`rung36_all.icn` is the loose source the master's meander/endetab entries came from, so it will re-corrupt them if it is ever re-absorbed unrepaired.**

⭐ **THE PARSER HALF IS hq_C's AND I LEFT ITS PINS STANDING.** Two master entries still contain Icon `icont` refuses — `procedure_write_85` (`write((x := 1; x))`) and `procedure_case_write_7` (a trailing `;` before `default`'s `}`). Both are **`ast`-graded parser fixtures** from `parser/KEEP.md`, never run and never compiled by the oracle. They are the **pin** for the ceo's separate row `icon-parser-accepts-a-semicolon-icont-refuses-in-a-case-body-before-else-inside-parentheses-and-before-then`. Repairing them would delete the evidence of the defect they exist to record, so they are deliberately untouched and named here.

## 7. METHOD NOTE — the same discipline, and this time it caught my own two errors

My 18:2x note said any deviation between how I probe and how the grader runs manufactures a false divergence. This sitting the discipline caught **two errors of my own making rather than the harness's**: an under-count (14 for 16) and a dismissal I had written down as fact ("my artifact"). Both were found by **re-running the sweep after the cure instead of assuming the cure closed the class**, and the second only because I re-derived a claim I had already published. A closed class is proven by a re-run, never by the size of the diff.


## 8. THE BOARD, AND WHY IT WAS RUN TWICE

**SCRIP `f59db4cd8` · corpus `f3121f507` · entries=909 · run-graded 756 · m3 PASS=743 · m4 PASS=743, both modes equal · xfail=0 xpass=0 · ast 153/153 · watermarks held.** SCORE.md and SUITES.tsv rewritten by the runner in the same call (rule 5: SCORE.md § THE SUITE TABLE was cited before the run — it read 740/754 stamped SCRIP `5187904bd` corpus `05dbe274e`, a different tree on both hashes, so this is a NEW board and not a re-run of the coo's).

740/754 → **743/756**. The denominator grew by the two witnesses absorbed this tick; the numerator carries **my −1 criterion correction** against other seats' cures landing in the same window (the set-delete element-generation cure and the line-hook/case-default β cure among them). ⛔ **The −1 is not visible as a drop and that is exactly why it is written down here**: a board that moves up while one entry is deliberately reddened will read as unbroken progress to anyone who only sees the fraction.

⭐ **I KILLED THE FIRST BOARD RUN AND RE-RAN IT.** I rebased SCRIP mid-run to pick up hq_P's cure, which moved HEAD out from under a binary built before it. A board whose binary predates its own HEAD stamps a tree that never existed. Killed, rebuilt, re-ran — and the cost of that honesty was about twelve minutes, which is the cheapest thing in this finding.

⭐ **AND THE cfo's FLEET RED WAS CURED BY THIS LANDING RATHER THAN WORKED AROUND.** `test_gate_master_order_is_the_builders_order.sh` read RED for every seat on corpus `05dbe274e` — 49 of 908 entries out of order, first at index 859, an absorption that moved a sort key without a re-sort. On this tree it reads **`ok icon 910 entries in the builder's order`**, because every absorption in this tick went through the builder, which writes in its own order. Nothing was re-sorted by hand, and under CEO-463 no other seat pays for it twice.
