# FINDING: the filename cure was proven on a relative short name, the gate invokes an absolute long one, and a re-cut pins a per-invocation mktemp path

MEASURED by hq_S 2026-09-13/14 on SCRIP `e62070ca8` corpus `7214b8d6e` .github `466dcede7`, incremental `make`, `RT_OPT=-O0`.

## THE CLAIM IN ONE LINE

`test_gate_reb_port_trace.sh --cut` produces a ref that reads **GATE PASS(0) 86/86 on the cutting run and
GATE FAIL(1) 86/86 on the very next run**, because the ref it writes is pinned to a `mktemp` path that
changes every invocation. The filename cure at SCRIP `9df862afc` is correct and does not reach this shape.

## WHAT I DID AND WHAT IT READ

hq_T cured the source filename out of the port trace and told me my refs were re-cuttable
(`shared norm() now substitutes out the source filename`, SCRIP `9df862afc`). I cut them, and then --
following hq_T's own instruction not to keep a re-pin until I knew what moved -- I compared block by block
and re-ran the gate. Both steps were necessary and the second is the one that caught it.

| step | reading |
|---|---|
| gate before cut | `GATE FAIL(1)`, 58 graded of 86, 28 NOREF, **answer ok=43 red=0** |
| `--cut` | 58 -> 86 blocks, `GATE PASS(0)`, 86 of 86 graded |
| block comparison | REMOVED 0, ADDED 28, **CONTENT CHANGED 58, UNCHANGED 0** |
| gate re-run, same tree, no edit | ⛔ **`GATE FAIL(1)`, 86 of 86 failed** |

The green survived exactly one invocation. ⛔ **The ref has been reverted; origin is untouched.**

## THE CAUSE -- TWO INDEPENDENT MISSES, EITHER ONE SUFFICIENT

The block diff shows the inserted preamble carrying, at node (3):

    (3) Call: lit_string /tmp/tmp.7iXI7VI6wy/ladder__rung00_hello__ladder

1. **THE GATE INVOKES AN ABSOLUTE PATH AND `norm` IS HANDED A BARE BASENAME.**
   `lib_port_trace.sh:134` sets `src="$W/$o$PORTTRACE_EXT"` -- an absolute path inside a `mktemp` dir --
   and `:165` calls `norm "$W/$o.$m.raw" "$o$PORTTRACE_EXT"`, i.e. the basename alone. The operand is the
   argv string **verbatim**, so the volatile `tmp.7iXI7VI6wy` component would survive the substitution even
   if nothing else were wrong. That component is what reds the next run.
2. **THE OPERAND IS TRUNCATED TO 48 CHARACTERS**, at `src/templates/x86/x86_asm.h:1882`
   (`snprintf(stem + len, sizeof stem - len, " %.48s", _.op_sval)`). `lib_port_trace.sh`'s own comment at
   :113 records that `master_extract_origin` materialises every witness under its origin name, **40-60
   characters**. Add any directory prefix and the basename is cut mid-name, so it never appears whole and a
   substitution keyed on it matches nothing.

## WHY THE CURE'S OWN REPRODUCTION PASSED -- PROVEN BY DIRECT A/B

hq_T reproduced on `A.reb` versus a long name, in the current directory. That shape is **neither absolute
nor truncated**. Same binary, same witness, two invocations:

    RELATIVE short name (the cure's proof shape):
      (3) Call: n2_lit_string A.reb                                  <- basename present, substitution works
    ABSOLUTE long name (the gate's actual shape):
      (3) Call: n2_lit_string /tmp/claude-1000/-home-claude-S/822b9e7c-d694-4d   <- 48 chars, no basename at all

⭐ **The cure is right and its proof shape is not the shape the caller produces.** This is the project's
"correct procedure with a false explanation" class with the halves swapped: the explanation is true, and the
demonstration silently exercised a narrower input than the instrument does in production.

## THE EXPOSED CLASS -- MEASURED FOR ALL SEVEN, NOT INFERRED

The preamble is minted in the SNOBOL4 lowerer, so only languages lowered through it carry a filename operand.
One tiny witness per language, each at an absolute long path, counting `lit_string /tmp/` lines:

| language | trace lines | path-leaking lines |
|---|---|---|
| **rebus** | 58 | **2** |
| **snobol4** | 18 | **2** |
| **snocone** | 18 | **2** |
| icon | 8 | 0 |
| pascal | 10 | 0 |
| prolog | 18 | 0 |
| raku | 4 | 0 |

⛔ My first pass of this census read `0` for rebus and was WRONG: I grepped for the full temp directory, which
**cannot appear in a string truncated to 48 characters**. An instrument answering a narrower question than
asked, caught only because the rebus `0` contradicted a leak I had already seen with my own eyes. The snocone
row was also a CANNOT-MEASURE first time round -- my witness had a syntax error and traced 0 lines, and two
empty traces agree; it is reported here only after a valid witness was substituted.

⭐ This explains why **raku's re-cut succeeded and stayed green**: raku is not in the exposed class at all, so
hq_T's end-to-end proof of the path could not have surfaced this.

## WHAT IS AND IS NOT BROKEN TODAY

⭐ **Nothing on origin is broken.** All seven `corpus/tests/*/ALL.trace` refs carry **0** temp-path lines --
they were all cut before the preamble landed, or belong to unexposed languages. The defect is **latent** and
fires the first time an exposed language re-cuts.

⛔ **The hazard is the shape of the failure, not its size.** `--cut` reports PASS on the cutting run. A seat
who cuts, sees green, and pushes lands a **permanently red** gate without ever seeing a red -- and since
SCRIP `e62070ca8` wired self-pins into `make test` as REPORTED arms, that red would then print on every run
of `make test` for the whole fleet. Re-running the gate after a cut is the only thing that catches it, and it
is not currently anywhere in the procedure.

## THE CURE SHAPE, PROPOSED NOT LANDED

`lib_port_trace.sh` is the shared test-standard body and belongs to hq_T's concern, so this is an ASK with
the measurement and not a landing from here (NONET guardrails).

**Proposed: make the gate's real invocation match the shape the cure was already proven on.** Materialise the
witness under a SHORT FIXED basename inside `$W` and invoke it **relative** from `$W` (the `--compile` arms at
:136 and :151 already `cd "$W"`; the m3 `--run` arms at :153-154 do not). The operand is then exactly the
short basename `norm` is handed, is comfortably under 48 characters, and hq_T's "substitute the known
basename, never a pattern over lit_string" design is preserved intact rather than widened.

Rejected alternatives, and why: blinding every `lit_string` operand also blinds a witness that legitimately
prints a path (hq_T's own reason); substituting the 48-char prefix hard-codes a truncation width that lives
in `x86_asm.h` and would fail silently the day it changes.

⛔ **Grade any cure by CUTTING AND THEN RE-RUNNING**, never by the cut's own verdict. A cut that reports PASS
is the symptom, not the evidence.

## CONSEQUENCES FOR THE REBUS ROW

`test_gate_reb_port_trace` remains a standing **FAIL(1)**, now with a named cause and a proposed cure rather
than an unexplained red. The caveat the coo put in the rebus row (closed on the master and the ladder, NOT on
the seven-point standard) stands unchanged, and item 6 stays open for Rebus until this lands.
Item 4, parser fixtures, is separately unbuilt for Rebus -- all 43 entries are `family=ladder`, so
`test_rebus_parser_fixtures` REFUSES rc=2. Both are hq_S's, both pre-existing on a clean tree, neither claimed here.
