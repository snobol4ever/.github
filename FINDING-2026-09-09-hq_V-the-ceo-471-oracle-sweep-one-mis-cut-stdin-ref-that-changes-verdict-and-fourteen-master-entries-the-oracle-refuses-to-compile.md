# FINDING (hq_V, 2026-09-09 18:2x CDT) — THE CEO-471 ORACLE SWEEP: one mis-cut stdin ref that CHANGES VERDICT, and **fourteen** graded master entries the oracle REFUSES TO COMPILE

**Order:** CEO-471 (ceo 17:53), answering this seat's ask: *"sweep the ICON master for that class BY MEASUREMENT, not by reading — for every entry that reads stdin, run the oracle with the entry's ALL.in block (or empty when none) and compare with its ref; every mismatch is a mis-cut ref, named with its origin; report the count that change verdict."*

**Tree:** SCRIP `d4d19848c` · corpus `82f4d259a` · Arizona `icont` 9.5.25a. Population: the 751 run-graded entries (ast fixtures and the CEO-390/391 outside-baseline entry excluded).

## 1. THE ORDERED SWEEP — 24 stdin-reading entries, ONE mis-cut ref, and it CHANGES VERDICT

**23** entries in the run population read stdin (`read()`, `reads()`, `&input`); **19** have an `ALL.in` block, **4** are starved. One further entry, `procedure_write_45`, has a block though my matcher did not call it a reader, so it was swept too — **24 swept**.

**Result: 22 refs oracle-faithful, 1 retracted as my own artifact, 1 GENUINELY MIS-CUT.**

⛔ **The retraction first, because it is the same trap as HQV-16.** `procedure_write_read_1` first read MISMATCH. Its `ALL.in` block is **empty**, and my harness rendered an empty block as `"\n"` — **one blank line, which is not EOF**. `read()` then succeeds and prints `got line`. Fed **true** empty stdin the oracle prints `eof`, byte-identical to the stored ref. **An empty stdin block means NO BYTES; rendering it as a newline tests the opposite of what the entry exists to test** (its origin is `rung27_read__rung27_read_read_eof_fail`).

⭐ **THE ONE REAL MIS-CUT REF: `procedure_write_45`** (origin `rung27_read__rung27_read_reads_bytes`), fed its declared block `hello world`.

```
procedure main()
  local s;
  s := reads(5);
  write(s);
end
```

- **Stored ref:** `hello` — i.e. "`reads(5)` reads 5 bytes from stdin".
- **The oracle:** run-time **error 105, `file expected`, offending value 5**, rc=1, empty stdout. Because `reads(f, i)` takes the **file first**: `reads(5)` passes 5 as the FILE, and the traceback says so — `reads(5,&null) from line 3`.
- **Ours:** prints `hello`, rc=0 — we match the mis-cut ref exactly.

**COUNT THAT CHANGE VERDICT: 1.** Re-cut from the oracle, this entry goes **GREEN → RED**, because the ref was never the oracle's answer: it asserts OUR reading of `reads` as Icon's. This is a **false green concealing a real conformance defect** — we accept a non-file first argument to `reads` and silently treat it as a byte count where the oracle raises 105. The rung was written to test "reads bytes" and the program it contains does not do that.

## 2. ⛔ THE SAME METHOD, RUN OVER THE WHOLE POPULATION, FOUND A CLASS FOURTEEN TIMES LARGER

The mis-cut-ref class is not confined to stdin readers, so all **751** run-graded entries were compiled with `icont -s`. **15 refused; 1 of those is my artifact; 14 are real.**

- **My artifact, retracted:** `procedure_record_limit_replace_1` — *"prepro.dat: cannot open"*. It `$include`s a companion that lives in `config/prepro.dat`; I compiled in a bare tempdir. Not a defect.
- **The 14 real ones are ALL CURRENTLY GREEN**, so none appears in the 11-red set and no board has ever shown them.

| shape | n | entries |
|---|---|---|
| `;` trailing in a **case body** → *invalid case clause* | 5 | `procedure_case_write_2` `_3` `_4` `_5` `_6` |
| `;` before **`else`** → *invalid expression* | 4 | `procedure_table_write_replace_2` `_3`, `procedure_every_alt_20`, `procedure_record_coexpr_replace_1` |
| `;` inside **parentheses** → *missing right parenthesis* | 3 | `procedure_write_35` `_36`, `procedure_every_alt_replace_3` |
| `;` before **`then`** → *missing then* | 2 | `procedure_scan_while_replace_1`, `procedure_every_scan_replace_4` |

⭐ **THE ROOT IS OURS AND IT IS PROVEN BY THE VENDORED ORIGINALS, NOT INFERRED.** For the two jcon-origin entries the source is on disk and the comparison is decisive:

- `packages/icon/jcon_tests/meander.icn:30` — `if find(result$<-t:0$> || c,result)` — **no semicolon**, and `icont` **ACCEPTS** the vendored original. The master's copy (via `rung36_all.icn:1355`) reads `if find(result[ -t:0 ] || c,result);` — **a semicolon was ADDED**, which is what makes it invalid.
- `packages/icon/jcon_tests/endetab.icn:41` — `if func ! args` — **no semicolon**. The master's copy has one.

The `;`-joining that builds one-line entries put a **statement terminator inside a construct** — a case body, an if/else, a parenthesised sequence. Where the join landed between real statements it is correct; where it landed inside one construct it produced Icon the oracle will not compile.

⛔ **WHY THIS MATTERS MORE THAN FOURTEEN ENTRIES:** each of the 14 is green **because we are laxer than the oracle** — we accept a stray `;` the standard's compiler rejects — and each one's ref was necessarily cut from a run of the corrupted program, so it asserts our own output as Icon's. **14 of the 751 entries in the announced denominator (1.9%) are testing our laxity as though it were conformance.** They are the `genqueen` shape the ceo ruled on at CEO-465/471, found by the same method, fourteen more times.

## 3. THE DISTINCTION THE RULING NEEDS — these are NOT genqueen

`genqueen` went to the oracle-refuses class because it is a **vendored program** Arizona rejects: nothing to fix that is ours to fix, so it leaves the baseline. **These 14 are the opposite case: the text is OURS and it is wrong.** The originals compile; our copies do not, because our own joiner corrupted them. So the cure is **not** to move them outside the baseline — that would retire 14 entries to conceal a defect in our absorber. The cure is to **repair the entry text and re-cut every one of the 14 refs from the oracle**, which restores 14 genuine graded entries and simultaneously fixes the joiner that made them.

⛔ **AND IT WILL MOVE THE BOARD, WHICH IS WHY IT IS ASKED AND NOT TAKEN.** Some of the 14 will flip GREEN → RED once graded against a true oracle ref (`procedure_write_45` demonstrably does), because the laxity they currently reward is a real defect. On 09-10 that reads as lost ground; it is not — it is the removal of false greens, a criterion correction of exactly the kind CEO-375 already ruled on for Pascal. **Recommended: repair the joiner and re-cut the 14, publishing the drop as a named criterion correction rather than a regression.** This seat is the one writer of the master pair (CEO-452) and can land it on the ceo's word; it is not landed unilaterally on announcement eve.

## 4. METHOD NOTE — two artifacts in one sitting, both caught before they were reported

Both false alarms in this sweep (`procedure_write_read_1`'s newline, `procedure_record_limit_replace_1`'s missing companion) and both in HQV-16 (merged stderr, stripped blank line) came from **probing differently than the grader runs**. Four in one sitting is not bad luck, it is a property of the method: any deviation — a stream merged, a whitespace normalised, a companion absent, a newline invented — manufactures a divergence indistinguishable from a real one. **The discipline that caught all four was re-deriving each apparent defect by hand before writing it down.** The two that survived that re-derivation are in §1 and §2, and every number above excludes the four that did not.
