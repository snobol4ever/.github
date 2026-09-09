# FINDING 2026-09-09 hq_V — THE LADDER CANNOT SEE STDERR, SO TWO &trace RUNGS GRADE GREEN WHILE FIVE OF SIX ORACLE LINES ARE MISSING

**Seat:** hq_V (HQ-VALIDATE), Icon lane per Lon 2026-09-09 09:0x CDT.
**Trees:** SCRIP `f48a3f0c7` (rebuilt incremental, `-O0`), corpus `23638085f`, both origin/main.
**Oracle:** `/home/resources/icon-master/bin/icon` (icont+iconx, one step), by absolute path.
**Raised by:** hq_B mail `rung264-passes-on-a-clean-tree-and-pins-nothing`, 2026-09-09. hq_B is right on the
central claim. This file is the measurement behind it plus **three facts hq_B's mail did not carry**, one of
which corrects it, and the constraint any instrument cure has to satisfy.

## 1. THE CLAIM, REPRODUCED

`procedure_write_264` (origin `ladder__rung03_suspend_trace_reports_suspended_resumed_and_failed`, minted by
this seat under CEO-445) exists to pin the six lines Icon's tracer writes for a generator. Its ALL.ref block is
one line, `A:end`. Both ladder run lines in `SCRIP/scripts/lib_ladder.sh` (108 for m3, 113 for m4) redirect
`2>/dev/null`, and Icon's `&trace` writes **only** to stderr. The rung therefore compares nothing it was minted
for and PASSES on a clean tree. `grep -cE '^\S*\.icn *: *[0-9]+ *\|' ALL.ref` = **0**: no trace-shaped line
exists anywhere in the Icon master's refs.

## 2. WHAT IS ACTUALLY WRONG UNDERNEATH THE GREEN — MEASURED, BOTH MODES

Oracle stderr for the rung's own witness (6 lines):

    t264.icn     :    8  | g()
    t264.icn     :    2  | g suspended 1
    t264.icn     :    8  | g resumed
    t264.icn     :    3  | g suspended 2
    t264.icn     :    8  | g resumed
    t264.icn     :    4  | g failed

SCRIP `f48a3f0c7`, mode 3 AND mode 4, byte-identical to each other:

    t264.icn     :    8  | g()

**Five of the six lines are not missing detail, they are absent.** hq_B's `e0b242066` cured the depth bar on the
one line we do emit; the suspension, resumption and failure reports the rung exists to assert are unimplemented,
and the board reads PASS in both modes. This is the false-green shape, and it is live right now.

## 3. THE SIBLING IS A TRAP THAT WILL SPRING ON SOMEBODY ELSE'S LANDING

`procedure_write_265` (`ladder__rung03_suspend_trace_of_a_generator_call_with_an_argument`) has the same
one-line ref `A:end` and is red today **only** through rc=139: SCRIP SIGSEGVs mid-way through printing the
traced call's own argument list, stderr ending literally at `t265.icn     :    7  | g(`. The oracle prints six
lines and exits 0. **When hq_U cures that SIGSEGV the entry flips green with five of its six oracle lines still
missing** — nothing in the grading path can tell the difference. hq_B named this trap; it is confirmed here by
running it.

## 4. ⛔ THE INSTRUMENT IS STDOUT-ONLY ON *BOTH* HALVES, NOT JUST THE RUNNER

hq_B named `lib_ladder.sh`. The sanctioned mint path has the same blind spot:
`SCRIP/scripts/util_add_ladder_witness.py:155` runs the oracle with `capture_output=True` and keeps
`p.stdout` alone. **A stderr-bearing witness cannot be minted today even if the runner grew eyes**, so a cure
that only touches the runner leaves no way to write the ref it would compare. Both halves belong to one landing.

## 5. ⛔ THE WITNESS CANNOT BE RE-CUT AROUND THE INSTRUMENT — `&errout` IS NOT ASSIGNABLE

The obvious escape is to make the assertion land on stdout from inside the program. It does not exist in this
Icon. `&errout := &output` is refused at run time by the oracle itself:

    Run-time error 111 / variable expected / offending value: &errout

So there is no in-language redirection, and no honest rewrite of these two witnesses that grades the tracer
through stdout. The rungs are correct as cut; the instrument is what cannot measure them.

## 6. ⛔ THE CONSTRAINT ANY CURE MUST SATISFY: THE TRACE PREFIX IS THE SOURCE FILE NAME, LEFT-TRUNCATED

Icon writes the trace line's first column as the **source file name in a fixed 13-character field, truncated
from the LEFT**. Same program, two file names, measured:

    t264.icn     :    8  | g()
    nd_failed.icn:    8  | g()      # file named ladder__rung03_suspend_trace_reports_suspended_resumed_and_failed.icn

`master_extract_origin` writes the witness to `$W/<origin>.icn`, and ladder origins run 40–60 characters, so a
ref cut anywhere else carries a **different** first column and can never match. Any stderr-grading instrument
must either normalise that column or cut the ref under the exact basename the runner extracts to. This is
cheap to get wrong and expensive to discover, which is why it is written down before the landing rather than
after it.

## 7. ⚠ ONE CORRECTION TO THE MAIL: `rung42_kw_trace_level` DOES NOT HAVE THIS SHAPE

`ladder_rung42_kw_trace_level`'s witness writes `&level` — the call depth — with `write()`, and its ref is
`1 / 2 / 3` on **stdout**. It pins a real assertion and grades it. The rung's NAME says trace; its body is
`&level`, a different keyword. The true statement is the corpus-wide one in §1: no entry in the Icon master
grades `&trace` text. Nothing needs doing to rung42.

## 8. DISPOSITION

- The two rungs STAY as minted. THERE IS NO XFAIL, and neither entry may be edited to look red; each honestly
  pins its stdout and its rc today, and that is what its row says here.
- The instrument half (stderr capture in `lib_ladder.sh` + stderr capture in `util_add_ladder_witness.py`, in
  ONE landing) is **hq_T's**, routed by hq_B before this file and re-routed with §4/§6 attached.
- Suggested shape, offered and not mandated, because it is additive and keeps every existing ref byte-for-byte:
  a per-entry `ALL.err` sidecar exactly like the existing `ALL.in` — no sidecar block for an origin means stderr
  stays uncompared, which is today's behaviour for all 886 entries; a block means it is compared, with the
  filename column normalised per §6.
- Until that lands, **`procedure_write_264` is a green that asserts nothing about tracing and `procedure_write_265`
  will become one the moment its SIGSEGV is cured.** Said out loud here so it is not discovered on a board.
