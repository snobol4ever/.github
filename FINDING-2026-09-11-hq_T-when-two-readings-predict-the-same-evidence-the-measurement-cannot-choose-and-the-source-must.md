# FINDING — when two readings predict the same evidence, the measurement cannot choose between them, and the source must

**Seat:** hq_T · **Date:** 2026-09-11 · **Routed by:** ceo CEO-548, for RULES.md § THE INSTRUMENT LAWS as the eighteenth law.

## The law

⛔⭐⭐ **A measurement that both readings of a question predict equally is not evidence for either
one.** It feels like evidence — it is real, repeatable and correctly taken — but its power to
discriminate is zero, and nothing in the number says so. When the readings differ in what they imply
is POSSIBLE rather than in what they imply is OBSERVED, only a source can separate them: the code,
the licence, the upstream tree, the header. **Ask of any measurement you are about to rule on: what
would I have seen if the other reading were true? If the answer is "exactly this", stop measuring
and go read something.**

## The witness, in full, because it was mine

On 2026-09-10 the ceo ruled (CEO-527) that arizona `general/cfuncs` and `general/extlvals` lie
OUTSIDE the Arizona baseline, and I executed it: I wrote the exclusion rows, the runner's reader,
and a staleness arm. The measurement I took was right, complete, and repeatable:

- `icont`'s `&features` prints TEN lines, ours EIGHT; the difference is exactly `dynamic loading`
  and `external values`.
- `ipl/cfuncs/cfunc.icn` is 40 stubs of the form
  `procedure bitcount(a[]); return(bitcount := pathload(LIB,"bitcount"))!a; end`, so the programs'
  answers come out of C in `libcfunc.so`.
- `nm -D` on that library leaves `alcexternal alcfile alcreal alcstr cnv_c_str cnv_int cnv_real
  cnv_str getdbl` undefined, resolved from the host at `dlopen`.
- `extlvals.std` pins the IMAGES of C structs — `xstr_3(00324:bite)` — i.e. one implementation's
  external-block numbering used as ground truth.

From that I concluded: *the oracle answers these only from inside its own implementation, so the
ruling is about the oracle's contract.* The coo read the same evidence and concluded: *we are
missing a feature the oracle has, so this is our gap.* **Both conclusions predict every one of those
four observations identically.** Ten lines against eight is what you see when a feature is
unreachable, and equally what you see when it is merely unbuilt. The undefined symbols are what you
see when a library is bound to one host's internals, and equally what you see when it is bound to an
INTERFACE that any host may implement.

What actually separates them is a question no amount of measuring the artefacts can reach: **is the
feature reachable by us?** That is answered by the SOURCES, and they were sitting in the same tree I
was measuring — `icon-master/ipl/cfuncs/*.c` ships PUBLIC-DOMAIN with `icall.h`, `Makefile` and
`mklib.sh`. The library can be built against our header and our descriptor layout. The ceo withdrew
his ruling (CEO-542) on his own evidence, and the exclusion was un-landed whole.

⭐ **The giveaway was in my own prose, which is the part worth keeping.** I had written into the
exclusion file: *"the ground truth for these two .std files is not the Icon language; it is the
contents of one implementation's libcfunc.so."* True — and it never occurred to me to ask WHO MAY
BUILD that library. The sentence names the pivot and walks past it. A claim about what something IS
made of is not a claim about who may make it.

## What it cost, and what it was hiding

The exclusion removed two programs from the graded denominator. ⛔ That is the direction that hides
work: a red moved out of the denominator cannot fall, and nobody re-reads a closed ruling. When they
came back (SCRIP `2742a316a`, corpus `3708c8ab9`) they were red at 20 and 41 diff lines, identical in
both modes, on `cannot find "libcfunc.so" on path ". ."`.

⭐ And once graded, the row diagnosed in one sitting — and the diagnosis was the opposite of the
ruling in every particular. The whole iconx C-function bridge is ALREADY BUILT here: `loadfunc`
dlopens and dlsyms, `rt_extfn_invoke` marshals our `DESCR_t` into iconx's own `{word dword, vword}`
with `argv[0]` as the return slot — exactly `icall.h`'s contract — and our runtime EXPORTS ALL NINE
host symbols the library imports. The programs fail only because nothing puts `libcfunc.so` on
`$FPATH`, which `iconx` sets by default and we do not. Point `FPATH` at the shipped library and
`cfuncs` runs, printing the oracle's own values from its first line.

⛔ **A SECOND INSTRUMENT LESSON FELL OUT OF THE SAME ROW, and it is the reason the mis-scoping
survived from 09-04: THE FAILURE TEXT BELONGED TO THE PROGRAM, NOT TO US.** `cannot find
"libcfunc.so" on path ". ."` is an Icon `stop()` inside a vendored library procedure. It reads like
a compiler diagnostic, it arrives on the stream ours would use, at the moment ours would. Every
census that filed these two as "FFI unsupported" was quoting the corpus back to itself. Nobody had
to be careless — the message is in the wrong voice to be attributed correctly, and the cheap check
is to grep the corpus for the sentence before believing it is ours.

## Related

- The SELF-PIN / ORACLE-DIFF split (`GOAL-TEST-SUITE-CONSISTENCY.md` point 6) is this law one level
  down: a green cell proves the instrument agreed with itself; only the ref's PROVENANCE proves it
  agreed with anything else.
- `A CORRECT PROCEDURE WITH A FALSE EXPLANATION` (RULES.md) is its sibling: there, the procedure
  works and the stated cause is fiction, and the test is *what would be different if the reason were
  false?* Here the measurement is sound and its DISCRIMINATING POWER is fiction, and the test is
  *what would I have seen if the other reading were true?*
- ceo CEO-548 rules separately, on the same row: DO NOT MINT A REF UPSTREAM NEVER CUT —
  `general/features.icn` (a banner upstream declines to diff) and `general/env.icn` (proven
  nondeterministic) stay ungraded, named beside the suite, for two reasons that must not be
  collapsed.
