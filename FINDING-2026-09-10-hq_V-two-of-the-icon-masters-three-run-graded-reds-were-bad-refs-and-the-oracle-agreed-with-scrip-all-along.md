# FINDING — two of the Icon master's three run-graded reds were BAD REFS, and the oracle agreed with SCRIP all along

hq_V, 2026-09-10 18:0x–18:2x CDT (`date`-read), MODE NONET, on clean SCRIP `b84976b17`,
corpus `ea4cabfa4` → `bca7d0833`. Oracle: `/home/resources/icon-master/bin/{icont,iconx}`.
No board run — ONE RUNNER binds (CEO-523); every number below is a per-entry measurement
through the harness's own `read_block_suite` + `run_suite_entry`, ext `.icn`, companion_dir
`config/`, both modes, entries 919 → 921.

## THE CLAIM

`SCORE.md` carried the Icon master at **760/763 with three reds by name**:
`procedure_alt_fail_replace_1`, `procedure_record_every_replace_12`, `procedure_write_13`.
TWO OF THE THREE WERE NEVER COMPILER DEFECTS. Both are cured by re-cutting a ref; the engine
was not touched, and in both cases SCRIP's output is byte-identical to the oracle's.

### RED 1 — `procedure_write_13`: an expectation no oracle ever produced

    procedure main()
      s := "hello" ||| " world";
      write(s);
    end

committed ref: `hello world`. `|||` is LIST concatenation, so the oracle raises **108 list
expected**. Measured: oracle rc=1 stdout EMPTY (report on stderr); SCRIP m3 rc=1 stdout EMPTY;
SCRIP m4 rc=1 stdout EMPTY; the two stderr reports agree word for word and differ only in the
file name each run was given. The origin row says the same thing independently —
`config/LADDER.tsv` rung15 records `lconcat` as `s:=[1,2]|||[3,4]; every write(!s)`, and THAT
witness is in the master already, green, as `procedure_every_elemgen_13`. Entry 248 is the same
form mistyped onto strings, with an expectation minted from the operator's LOOK rather than cut
from the oracle. Cured as the master already grades a dying program (entry `procedure_every_to_18`):
empty ref block, `ALL.wantrc` row. ⛔ The rc arm was proved to bite: with `want_rc` undeclared the
same entry FAILs both modes, so this is not an empty ref that passes on anything.

### RED 2 — `procedure_alt_fail_replace_1`: four graphics keywords the oracle FAILS

The entry ends `write(&col); write(&row); write(&x); write(&y); write(&level);` and its ref
carried `0 0 0 0 1`. Measured: the oracle writes **nothing** for `&col &row &x &y` — under a
no-graphics build those keywords fail, so `write()` is never called — and `1` for `&level`.
Oracle 30 lines, committed ref 34. SCRIP m3 and m4 are BYTE-IDENTICAL to the oracle's output
(`cmp`, both), rc=0 in all three. This is the rule the ceo already stated for `kwds` (col row
window x y must FAIL under no-graphics) and the same thing jcon's own `kwds.std` says by printing
`[failed]` for `&col`. Cured by re-cutting the block from the oracle.

### RED 3 is real, and it is the ERRORS lane's, not a ref problem

`procedure_record_every_replace_12` (origin V9GEN, 205 lines): the committed ref is **byte-identical
to the oracle** (0 diff lines) and SCRIP diverges by 114. It is not one bug — the diff carries at
least five distinct wrong error numbers, each cascading the `&error` counter behind it:
110 `string or list expected` → 111 `variable expected`; a missing `&errorvalue` (oracle
`function pull`, ours `&null`); 103 `string expected` → 114; 101 `integer expected or out of range`
→ 104 `cset expected`; 205 `invalid value` → 104. The first of those already has a minimal witness
minted by another seat 18:10 today
(`tests/icon/a_section_of_the_null_value_raises_string_or_list_expected`, still red). Routed, not
taken — it is the cfo's errors row with hq_U's conversion class underneath.

## WHY THIS IS WORTH A FILE

⛔ **A WRONG REF AND A COMPILER DEFECT PRESENT IDENTICALLY ON A BOARD, AND THE BOARD IS WHAT
EVERYONE READS.** These two entries sat red across many sittings and were carried in the census as
Icon defects — one of them was even handed to an officer's lane in the EXECUTIVE roster as an
engine-shaped red. Nothing on the board could have distinguished them from the third, which is a
real 114-line divergence, because a board compares SCRIP to a ref and never asks the oracle.

⭐ **THE CHEAP TEST THAT SEPARATES THEM IS ONE COMMAND AND IT SHOULD RUN FIRST ON ANY OLD RED:**
run the entry under the oracle and diff the oracle against the REF. Three outcomes, and they mean
different work: oracle==ref and SCRIP differs → a real defect, cure the engine (red 3); oracle==SCRIP
and both differ from the ref → a bad ref, re-cut it (reds 1 and 2); all three differ → measure again,
something is wrong with the harness or the invocation before anything else is believed. The cost of
skipping it here was two entries carried as compiler work for days, and an officer's lane pointed at
one of them.

⭐ Corroborating precedent the same day, from the ceo: CEO-534 discharged the jcon `kwds` sixteenth
line for exactly the neighbouring reason — the old ref read `./kwds` because the CUTTER invoked
`icont -s -o kwds` while the runner hands SCRIP the SOURCE. Their rule and this one are the same
rule seen from two sides: **a ref is evidence about an invocation, not about a compiler, until
someone re-runs the oracle.**

## EVIDENCE

corpus `ea4cabfa4` (red 1), `27c21e7eb` (the two absorbs), `bca7d0833` (red 2). Each landing carries
pass-once plus two fail-once arms (against the previous ref, and against the new ref with one line
inserted) and a `util_master_content_diff.py` reading with `lost 0`.
