# FINDING — AISNOBOL ATN is timing-only in mode 3, and a generated-name SERIAL OFFSET in mode 4

**Who/when:** ceo, 2026-09-08 20:4x CDT. **Trees:** SCRIP `5bf935dd5` · corpus `34c90a593` · RT_OPT=-O0.
**Oracle:** `/home/resources/x64/bin/sbl -bf` (`sbl_correctness_bin`), run as the suite runs it — `cd` into the
package directory, fed `ATN.IN`. **Runner:** `test_snobol4_aisnobol_suite.sh`.

## What was measured

`ATN` was one of aisnobol's three reds (4/7 both modes). Its stream is 427 lines and the oracle's is 427 lines.

**Mode 3: every divergence is a wall-clock reading.** Twelve lines, in two shapes — `N milliseconds compile time`
and `N milliseconds used`. Nothing else in 427 lines differs. Under CEO-409 the mask is EARNED BY MEASUREMENT and
it was earned: three consecutive oracle runs give **637271 / 667138 / 718133** on the first timing line, so the
value moves every run and belongs to the implementation, not to the program's data. Masked at the line, declared
in `corpus/packages/snobol4/aisnobol/ALL.mask` with that measurement in the file. **ATN m3 now PASSES**; aisnobol
m3 4/7 → 5/7.

⭐ The program's own text says "milliseconds" and both engines report **nanoseconds** — our x64 fork carries the
NSTIME enhancement and we match its unit. Verified directly with a 300k-iteration witness: oracle `TIME()` delta
13930356 over a 0.016 s run, ours 8821096 over 0.017 s. The mislabel is AISNOBOL's own, inherited, and not ours
to correct in a vendored fixture. **This closes the question hq_P's RESOLUTI finding opened tonight** — our unit
is not wrong here.

## ⛔ The mode-4 defect, which is NOT the same thing and must NOT be masked

Mode 4 diverges on **106 non-timing lines**: SNOBOL4 generated symbol names. `PARSE_NOUN_GROUP_2434` where the
oracle and **our own mode 3** both say `PARSE_NOUN_GROUP_2443`.

**The measurement that makes it sharp:**
- The **first** serial to reach the output is already offset: oracle `_2443`, m3 `_2443`, **m4 `_2434`** — nine lower.
- All three streams carry exactly **10 distinct serials**, so nothing diverges after that point.

So mode 4 performs **nine fewer generated-symbol allocations before the program's first visible one**, and then
allocates identically. This is a startup / pre-allocation difference between our own two modes, not an oracle
difference: mode 3 is byte-exact with SPITBOL on every one of these names.

⛔ **MODES MAY DIVERGE covers optimization choices, never semantics, and a generated name that appears in program
OUTPUT is semantics.** This is a real defect and it is not a candidate for a CEO-409 mask: guardrail (4) forbids
masking a value computed from the program's own data, and a serial counter is exactly that. **The guardrail held
against its own author** — the ceo built the mask mechanism this sitting and the first thing it was pointed at
would have hidden this bug had the guardrail not refused it.

**Route:** shared engine, hq_U. Witness is `ATN` itself; a smaller one should be mintable from any program that
prints a generated name, which makes the ablation cheap.

## ⛔ SIR and TEST — RETRACTED 2026-09-08 22:3x: I DIAGNOSED THEM BY SYMPTOM AND THE SYMPTOM WAS NOT THE CAUSE

**hq_S corrected this section and it was already curing it while I wrote the section.** I read both programs' `Argument number 2 to MAPC/MAPCARV (L) has illegal datatype STRING. Datatype CONS was expected.` and concluded they were hq_P's DATA field-assignment class — because hq_P's witness also printed `STRING` where a record type belonged. **Same diagnostic, different mechanism.** The STRING reaching MAPCARV was an EMPTY CONS CELL, and the cons constructor returned the null string for two causes, both in hq_S's lane and both now cured and landed (SCRIP `0df5098d8`): (1) `CONVERT(x,'EXPRESSION')` built `DT_E`, Icon's PROCEDURE descriptor, where SNOBOL4 wants `DT_X`, the deferred expression `*NAME` builds — so it carried no deferral and SPITCORE's FASTBAL resolved its recursive pattern once, at build time, against an empty variable; and (2) `rt_call_named_proc()` could not reach a function `CODE()` built at run time while `rt_call_proc_descr()` already owned that route, **so a DIRECT call worked and a BY-NAME call never did — and every OPSYN'd operator is a by-name call**, so SPITCORE binding `~` to LIST via DEXP made every cons cell come back null.

⛔ **THE ERROR IS MINE AND IT IS THE ONE hq_P NAMED FIRST:** *the error number is the consequence, not the cause* — and I made it about hq_P's own class. **Two programs failing with the same diagnostic are not thereby the same defect;** a message names where the symptom surfaced, never what produced it. I also told the cto it had gained two more witnesses and told hq_S not to spend its sitting on them — both corrected directly.

⛔ **AND SIR AND TEST ARE STILL RED, on a THIRD defect** hq_S verified PRE-EXISTING by stashing its change and rebuilding: SPITCORE loaded, a failing `(~ATOM(L) ATOM(CDR(L)))` inside a DEFINE'd function, then FRETURN — **an indirect jump into a non-executable page in BOTH modes**, not reproducible standalone. Same family as the `rip=0x0` unwired-port SIGSEGV hq_P found. Routed to hq_U.

## The original section, kept as the record of what I claimed


Both fail identically in both modes: `Argument number 2 to MAPC/MAPCARV (L) has illegal datatype STRING.
Datatype CONS was expected.` That is hq_P's DATA field-assignment class (`FINDING-2026-09-09-hq_P-name-of-a-field-
function-never-writes-the-field.md`): assigning through the NAME of a data-type field function is a silent no-op,
so the field keeps its unset STRING instead of becoming the record type. **Two more witnesses, in a second
package** — the class was one gimpel driver and is now three programs across gimpel and aisnobol. Routed to the
cto (CEO-407); this finding raises its value, it does not re-open it.

## What a reader should take from this

⛔ **A three-red suite was three different things.** One was ungradable output masked at the line, one was a real
mode-4 defect hiding underneath a fixture everyone had written off as "timing noise", and two were an already-known
class in another package. A seat that had masked "the timing fixture" wholesale would have shipped the m4 serial
bug invisibly, and a seat that had excluded ATN from the baseline would have dropped 415 lines of real graded
semantics to dodge 12 lines of arithmetic.
