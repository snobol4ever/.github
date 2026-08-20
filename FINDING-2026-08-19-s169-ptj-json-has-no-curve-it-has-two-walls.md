# FINDING s169 — PT-J: json HAS NO PERFORMANCE CURVE, IT HAS TWO WALLS — AND ">60 s" WAS NEVER THE PROBLEM

**Seat:** local `/home/claude3` (seat3), Claude Opus 5, PT front. **Picked up:** queue row 6 `pt-json` —
*"GOAL-SNOBOL4-100.md s166 PT, rung PT-J ONLY. json input bisect 631K→64K→8K→1K, linearity verdict."*
**SCRIP** `a78b39fb` · **corpus** `a3604cc9` · **.github** this commit. **All numbers RT_OPT=`-O0`** (FACT RULE O0-DEV).
**Instrument-only, per the PT front's own charter — NO fixes this seat.**

## 1. THE VERDICT THE BRIEF ASKED FOR: **NEITHER LINEAR NOR SUPERLINEAR — THERE IS NO CURVE**

PT-J asked for a linearity verdict across 631 KB → 64 KB → 8 KB → 1 KB. **That bisect cannot be run, and the reason
is the finding.** json's cost is not a function of input *size* at all. It is a **step function of input SHAPE**, and
both steps are cliffs at inputs three orders of magnitude below the smallest rung the brief names:

| input | ARBNO iterations | SCRIP m3 | oracle |
|---|---|---|---|
| `[]` | 0 | ok, ~1.15 s | 0 ms |
| `["s"]` | 0 | ok, ~1.13 s | 0 ms |
| `{"a":["s"]}` | 0 | ok, ~1.18 s | 0 ms |
| **`["s","s"]`** | **1** | **NO COMPLETION** | 0 ms |
| **`{"a":"s","b":"s"}`** | **1** | **NO COMPLETION** | 0 ms |
| **`{"a":["s","s"]}`** | **1** | **NO COMPLETION** | 0 ms |

**IN `json.sno`'S GRAMMAR, THE FIRST `ARBNO` ITERATION OVER A DEFERRED (`*`) BODY DOES NOT TERMINATE.** Zero
iterations: fine, ~1.1 s, **and the answer is correct**. One iteration: never returns. Every row above is **5 of 5
clean runs**, no concurrent load. ⛔ **Scope it to that grammar:** the pure-grammar sibling `json-match.sno` does
**not** hang on `["s","s"]` — it matches it — so the hang needs the *capturing* grammar. Reduction to a small
witness FAILED this seat; `ptj1` therefore carries the whole grammar, and it shows both halves in one run:
`one-element 0/1/1/0/0/0/0/1` printed correctly, then no return. The controlled ladder `{"a":["s" × n]}` puts the wall between **n=1 (12 B, 1 ms)** and
**n=2 (17 B, no completion)** — the same wall in the smallest form it can take.

**It is a control-flow loop, not allocation growth:** at n=2 (17 bytes) the process was still spinning after
**4 min 11 s** with **RSS flat at 28 MB**. A budget of 420 s produced no completion.

Since every real JSON document has two or more members somewhere, **the benchmark never runs at any size.** The
s154 cursor item *"json >60 s"* records a symptom of non-termination, not slowness — and no profile was ever
possible, which is exactly why PT-J's charter says *characterize, don't profile, until it terminates.*

## 2. THE SECOND WALL: **ANY NUMBER WITH A LEADING DIGIT 1–9 SIGSEGVs**

Independent of the first, and reachable on inputs the first wall lets through:

| value | result | | value | result |
|---|---|---|---|---|
| `0` | ok | | `1` `2` `9` | **SIGSEGV** |
| `0.5` | ok | | `12` `123` `10` `100` | **SIGSEGV** |
| `0.087` | ok | | `-1` `1.5` `1e5` `1.5e-3` | **SIGSEGV** |

Read against the grammar, the split is exact:

```
jnumber = ('-' | '') ('0' | ANY('123456789') (SPAN('0123456789') | '')) ...
                      ^^^ this arm is fine    ^^^ every input that takes THIS arm faults
```

Construct probe, `json.sno`: `{}`, `{"a":{}}`, `{"a":[]}`, `{"a":"s"}`, `{"a":true}`, `{"a":null}`, `{"a":["s"]}`,
`{"a":[[]]}` all produce the **correct check**; `{"a":1}`, `{"a":[1]}`, `{"a":{"b":1}}`, `{"a":[1,2]}` all **SIGSEGV**.

⛔ **BUT THE ARM DOES NOT FAULT IN ISOLATION, AND I COULD NOT REDUCE IT.** The obvious reading — "that alternation
is the bug" — is NOT what I measured. Lifted out on its own, `num = ('0' | ANY('123456789') (SPAN('0123456789') |
''))` matches `0` and `123` correctly on SCRIP. Three further reductions that kept the deferred recursion around it
also failed to fault. **So the input split is exact and it lines up with that arm, but the fault is
CONTEXT-DEPENDENT inside the full grammar** — witness `ptj2` therefore carries the whole grammar deliberately
rather than pretending to a minimal repro I do not have.

## 3. THE SIBLING IS WORSE — `json-match.sno` FAULTS ON THE FIRST NON-EMPTY OBJECT

`json-match.sno` is the *pure-match* variant (no captures, no actions) — the one PT would most want for engine
throughput. It is the more broken of the two: `{}` → ok (`check: 2`), but `{"a": []}`, `{"a": "s"}`, `{"a": 1}` and
`{"a": [1]}` **all SIGSEGV**. Across the full 631 KB→409 B ladder it SIGSEGVs at **every single rung**, so the
"631 KB is slow" reading of this benchmark was never right either. **The two siblings fail differently and must not
be conflated:** `json.sno` hangs on a second array element and SIGSEGVs on a leading-1-9 number; `json-match.sno`
SIGSEGVs on any non-empty object but matches `["s","s"]` fine.

## 4. ⛔ ALL OF IT PREDATES THIS SEAT'S FZ-3 COMMIT — PROVEN, NOT ASSUMED

Every result above reproduces **identically** on a pristine worktree build of `f0ae498d`, the parent of this seat's
own `a78b39fb`: `["s"]` ok · `["s","s"]` no completion · `{"a": 1}` SIGSEGV · `json-match` SIGSEGV at 409 B and at
631 KB. `json-match.sno` contains **zero** FENCE constructs, and FZ-3 ships disarmed (`fence0_release_bytes()`
returns 0), so it cannot reach this code. **Not mine, and now recorded so no future seat re-derives it.**

**The oracle is correct and instantaneous on every one of these:** `["s","s"]` → `check: 0/1/2/0/0/0/0/1` in `ms: 0`;
`{"a":["s","s"]}` → `check: 1/1/2/0/0/0/0/2` in `ms: 0`. SPITBOL x64 stack-overflows (ERROR 246) only at the full
631 KB with plain `-b`, on the stock program and on the probe alike — a stack setting, not a defect class.

## 5. A THIRD, SMALLER OBSERVATION — AND ONE MEASUREMENT I HAD TO THROW AWAY

`{"a":"s"}` under the stock harness exhausts the 512 MB arena (`[ZHP] heap exhausted`, ~850 K blocks) on **4 of 5
clean runs**, completing normally on the 5th; `["s"]`, `[]` and `{"a":["s"]}` complete 5 of 5. So it is real,
**intermittent, and shape-sensitive** — but it is NOT simple per-iteration leakage: a probe doing 400 separate
`ZBODY(1)` calls, and one doing a single `ZBODY(10000)` with the loop inside one activation, both complete cleanly
on the same input. Whatever accumulates is in the harness's calibrate/measure path, not in the match repeat itself.

⛔ **AN EARLIER VERSION OF THAT TABLE WAS CONTAMINATED AND IS RETRACTED.** My first construct sweep ran while a
420-second background job held a core, and it reported `HEAP` for `{"a":"s"}` and `{"a":"s"}`-shaped rows that the
clean re-run does not reproduce the same way. **Every number in this FINDING is from a re-run with zero concurrent
load** (`ps` confirmed no straggler `scrip` processes). Recording the mistake because the next seat will otherwise
trust the first table: *a benchmark measured under concurrent load is a measurement of the load.*

## 6. THE ONE MINIMAL WITNESS I DID GET — A WRONG ANSWER, NOT A HANG

The hang needs more of the real grammar than I could reduce it to this seat. What DID minimize is a sibling defect
in the same construct family — **forward reference through a deferred pattern**:

```snobol
	elem = *val
	val  = ('"s"' | '[' elem ARBNO(',' elem) ']')
	S = '["s","s"]'
	S ? POS(0) elem RPOS(0)	:F(NO)     * SCRIP prints FAIL; SPITBOL prints MATCH
```

SCRIP answers **FAIL** where the oracle answers **MATCH** — silently wrong, no crash, in 9 ms. Writing the same
grammar *self*-recursively (`elem = ('"s"' | '[' *elem ARBNO(',' *elem) ']')`) matches correctly, as does the
non-recursive form. **This is json's exact shape:** `json-match.sno` defines `jmember`/`jarray` referencing
`*jelement` while `jelement` is assigned *last*, after `jvalue`.

⛔ **AND IT IS BROADER THAN "FORWARD REFERENCE" — DO NOT INHERIT THAT NAME UNCHECKED.** The same wrong answer
appears with the definitions in the *correct* order (`val` assigned first, then `elem = *val`, matching `'1'`).
What distinguishes the passing spellings from the failing ones is that the failures defer to a **different**
variable while the passes defer to themselves — but two data points is not a law, and I am naming it as an
observation, not a mechanism.

## 6b. THE WITNESSES — `corpus/probe/ptj/`, ORACLE-REF'D, AND EVERY ONE VERIFIED TO ACTUALLY REPRODUCE

`ptj1_arbno_defer_nonterminating` (prints the one-element answer, then never returns) ·
`ptj2_number_leading_digit_segv` (SIGSEGV) · `ptj3_forward_defer_wrong_answer` (prints `FAIL`, oracle `MATCH`).
Every `.ref` is from live `sbl`. ⛔ **`ptj1` has no timeout of its own — never wire it into a gate without one.**

⛔ **I SHIPPED TWO OF THESE WRONG ON THE FIRST CUT AND CAUGHT IT ONLY BY RUNNING THEM.** My first `ptj1` used the
*self*-recursive spelling and my first `ptj2` used the lifted-out `jnumber` — **both matched correctly**, i.e. both
were witnesses that witnessed nothing. They were rebuilt against the real grammars and re-verified. Recorded
because a probe directory whose files do not reproduce is worse than an empty one: it retires a defect on paper.

## 7. WHAT PT-J CONCLUDES, AND WHAT IT HANDS THE NEXT SEAT

1. **json is not a performance workload today; it is three correctness defects wearing a stopwatch.** It should be
   struck from PT's measurement set until they land — treebank remains the workhorse (PT-0..PT-3 unaffected).
2. **Rank order for repair, by blast radius:** (a) ARBNO-first-iteration-over-deferred-body non-termination — this
   is the one that makes the benchmark unrunnable and is the likeliest to be hurting the *real* grammar corpus;
   (b) the leading-digit SIGSEGV — **start by reducing it; this seat could not**; (c) the deferred-reference wrong
   answer in §6. **(a) and (c) may well be one defect — both live in ARBNO-over-deferred-body — so do not assume
   they are two and do not assume they are one.**
3. **PT-J's stated deliverable is discharged with a negative result:** the linearity question has no answer because
   the curve does not exist. That is a stronger outcome than a slope would have been — a slope measured on a program
   that faults would have been fiction.
