# FINDING 2026-08-28 hq_P — exact α/β execution counts need NO emitted counter, and `match_begin` carries the recede pressure

**Row:** `perf-symbol-attribution-tooling` slice 4 (Lon, via ceo: *"SCRIP can instrument alpha and beta to produce
execution counts."*). **Instrument:** `SCRIP/scripts/util_port_counts.py` (new). **Tree:** SCRIP `8f35de3a` (measured at `f63d5cbd`; the rebase pulled in only a postoffice-doc commit, zero `src/` change),
corpus `d28835341`, `RT_OPT=-O0`, mode-4, callgrind 3.22.0.

## ⭐⭐ THE DESIGN RESULT: THE COUNTS WERE ALREADY THERE, BEHIND A SYMBOL TABLE

The addendum scoped slice 4 as an **emitted counter** — `SCRIP_PORT_COUNTS=1` emitting an increment at each α/β
port, with the dead `SCRIP_BBPROF` bones revived as the reporting half. That is buildable, but it was not necessary,
and the necessary version is strictly better:

**Every α and every β port is ALREADY a symbol in a mode-4 binary** (porter: **1,959 α + 1,138 β** local `t`
symbols), and callgrind's `--dump-instr=yes` reports an exact Ir count **per instruction address**. The count of the
instruction at an α label's address *is* the number of times that port was entered. So the counts come out with:

- **no emitted-code change** — the measured binary is byte-identical to the shipped one;
- **no new global variable** — there is no counter cell to store anywhere, so `RULES.md` NO-NEW-GLOBALS is not
  engaged and no in-chat grant is needed;
- **no overhead to measure and subtract** — clause 6's "the overhead arm is the real risk" simply does not arise.

⭐ **That last point is Instrument Law 6 satisfied STRUCTURALLY rather than by apology.** The law says an instrument
sharing a mechanism with what it measures is a participant; an emitted `inc` in the α port of a hot match box is the
definition of a participant, and it would have owed a measured perturbation beside every number it produced. A
simulator outside the process owes none. ⛔ **The cheaper instrument is also the more honest one, and the row's own
conditions are what said so** — the addendum's clause-6 requirement was the clue that the emitted-counter design was
the expensive branch, not a detail to satisfy.

⚠️ **NOT CLAIMED — and this is the emitted-counter route's remaining reason to exist (scope, per Law 13):** this is
**MODE-4 ONLY**. Mode 3 runs flat-wired blobs in an anonymous sealed slab with no symbols for callgrind to resolve;
slice 3's `SCRIP_PERF_MAP` names m3 boxes to `perf` but is **per-graph, not per-box**, and callgrind does not read a
perf map at all. **m3 port counts remain UNBUILT, not broken.** The addendum's "both modes must count AND dump"
condition is therefore **met for m4 and open for m3** — see § FOR ceo.

## ✅ THE INSTRUMENT WAS PROVEN BEFORE IT WAS TRUSTED — THREE HAND-DERIVABLE WITNESSES

Not self-consistency: three numbers predictable from the program text *before* running it.

1. **`loop1000` (purpose-built, 1000 iterations).** The `LT` test must run **1001** times (1000 passes + the final
   failure) and the increment **1000**. Measured: `statement_begin` / `cmp_test` / `coerce_numeric` / the test-side
   `var` and `lit_integer` α = **1001**; `binop` / `assign` / the increment-side operands α = **1000**; β = **1**,
   the single final recede. Exactly the semantics, split on the right boundary.
2. **`porter` external anchor.** `assign_var`, `subscript`, `deref` α = **23,531** each — and porter emits
   **23,531 output lines**. One entry per line, from an instrument that knows nothing about lines.
3. **`pattern_bt` B/A = 10.000, derivable from the subject string.** `&ANCHOR = 0`, subject
   `'xxxxxxxxxx bbb…'` — **ten leading `x`** before the first position where an arm can match, so unanchored
   scanning recedes exactly 10 times per match attempt. 1,000 attempts → **α = 1,000, β = 10,000, B/A = 10.000**,
   to the unit.

Selftest (`--selftest`): positive arm + **4 negative arms all rc=2** + a **POISON arm** proving the assertions can
fail + two object-context arms (below). Refuses rc=2 on: no input, missing file, unparseable profile, zero port
symbols, zero cost attributed to the object, and every-α-zero.

## ⛔⭐ TWO PARSER DEFECTS THE INSTRUMENT CAUGHT ON ITSELF — BOTH WOULD HAVE UNDER-REPORTED SILENTLY

Both are recorded because both are the *same* shape as the bugs these laws exist for, and both are now selftest arms.

- **The main object may have NO `ob=` line at all — it is the DEFAULT context.** Measured on the 1,000-iteration
  witness: the profile's only `ob=` is libstdc++, every main-object cost line sitting in the default context.
  Requiring an explicit `ob=` match dropped **100% of the program's own cost**.
  ⭐ **It surfaced as a REFUSAL, not as a plausible empty table, only because refusing is this script's default when
  nothing is attributed.** That is Instrument Law 2 paying for itself on its own author, within an hour of being
  written. A `PASS`-shaped empty table would have been believed.
- **`ob=` and `cob=` share ONE name-compression namespace.** In porter's profile the id in a bare `ob=(1)` is defined
  **50,000 lines earlier** by `cob=(1) ld-linux-x86-64.so.2`. Absorbing only `ob=` definitions leaves it unresolved —
  which happened to be **harmless here** (ld-linux is not ours) and would not be harmless for an id that is.
  ⛔ A defect whose damage depends on which library got which id is exactly the kind that survives a green run.

Also handled, each a way the parser could have been silently wrong: the cost line after a `calls=` line is the call's
**inclusive** cost, never self cost (charging it would give a recursive pattern box a number larger than the whole
program); `calls=` target positions live in the **callee's** position context and must not clobber the caller's
tracker; `+N`/`*` subposition compression tracks **per column**.

## ⭐⭐ THE MEASUREMENT: WHERE THE RECEDES ACTUALLY ARE

**porter** (mode-4, `-O0`, `porter.dat`; coverage: 1,959 boxes, **1,891 α-entered (96.5%)**, α-total 15,342,550,
β-total 4,765,160, object-Ir 253,137,981 of program-Ir 840,385,143). ⛔ `B/A` is **recedes per proceed**, a
dimensionless pressure — **not** a speed multiple, never written with an `x` (RULES.md FACT RULE reserves `x` for
reference/ours).

| family | α | β | B/A | boxes |
|---|---|---|---|---|
| `match_begin` | 293,858 | **1,398,610** | **4.759** | 13 |
| `match_assign_imm` | 1,151,998 | 1,133,955 | **0.984** | 57 |
| `match_rtab` | 1,319,489 | 1,148,441 | **0.870** | 58 |
| `coerce_numeric` | 388,758 | 290,458 | 0.747 | 32 |
| `assign` | 921,036 | 172,237 | 0.187 | 245 |
| `var` | 1,670,582 | 265,593 | 0.159 | 187 |
| `statement_begin` | 1,444,040 | 186,946 | 0.129 | 269 |
| `match_pos` | 1,260,523 | 104,060 | 0.083 | 8 |
| `match_lit` | 1,195,691 | 4,096 | 0.003 | 60 |
| `match_defer` | 1,320,572 | 1,100 | 0.001 | 119 |
| `match_assign_save` | 1,316,385 | 0 | 0.000 | 111 |
| `statement_end` | 1,017,275 | 0 | 0.000 | 267 |

⭐ **`match_begin` has the highest pressure by a factor of ~5 over the next family, and is the single largest β
source in the program: 1,398,610 of 4,765,160 recedes = 29.4%.** With `match_rtab` (24.1%) and `match_assign_imm`
(23.8%) the three carry **77.2% of every recede porter executes**.

⭐⭐ **THIS INDEPENDENTLY CORROBORATES SLICE 1, BY A DISJOINT MECHANISM.** Slice 1's *sampled* rollup put
`match_begin` at **24.84% of porter cycles with 18.18 points on the β port alone** and was explicitly logged as "ONE
unqualified sample on a shared box … a lever ranking, not a share anyone should quote." The exact counts, from
simulation rather than sampling, land on the same box and the same port. **Two instruments, two mechanisms, one
lever** — which is the standard this project sets before a number is trusted.

⚠️ **`match_assign_imm` at B/A = 0.984 is worth hq_C's attention specifically.** Nearly **every** immediate-capture
assign that proceeds is later receded — the work is done and then undone. Instrument Law 9's own witness is that
SNOBOL4 has two capture operators and the slice-captures cure reached `.` (deferred) while leaving `$` (immediate)
paying the full pre-cure copy ceremony, *~30% of porter*. ⛔ **NOT CLAIMED: I measured COUNTS, not COST** — that
these 1,133,955 recedes are expensive is hq_C's finding, not a new measurement of mine. What is new is that the
count says the undo is near-universal, not occasional.

**Cross-program (Law 13 — the all-clear is scoped to the list actually run: porter, pattern_bt, string_pattern,
loop1000):** in every program measured, the recede pressure concentrates on `match_begin` and the classic pattern
families barely recede at all — `pattern_bt` records `match_lit` 42,000 α / **0** β, `match_alternate` 11,000 α /
**0** β, `match_defer` 11,000 α / **0** β, with **all 10,000 of its recedes on `match_begin`**. ⭐ So the recede path
is **centralized at `match_begin`, not distributed across the pattern boxes** — a structural fact the sampled
profile could not have shown, because sampling attributes cycles, not transitions.

⚠️ **`string_pattern` records β-total = 4 over 30,054 α** — it does not exercise the recede path at all. That is a
statement about the benchmark, not the compiler: **a pattern benchmark that never backtracks cannot grade a
backtracking cure** (Instrument Law 7). Anyone grading a recede-path cure should use porter or pattern_bt and not
string_pattern.

## FOR ceo

1. **Slice 4's m4 half is DELIVERED and needs no globals grant.** The banner ask the emitted-counter design would
   have required is **not being made**, because the design that required it was not the one that shipped.
2. ⛔ **The m3 half is OPEN and it is the one that still needs a ruling.** Exact per-box counts inside mode-3's
   sealed slab genuinely do need either a counter cell (→ NO-NEW-GLOBALS, → an in-chat banner ask to Lon) or a
   per-box extension of slice 3's perf-map plus a sampling profiler (→ samples, not exact counts, i.e. not what Lon
   asked for). **I did not choose between those** — it is an architecture call, and the cheap m4 result should be in
   hand before anyone spends a globals grant on the expensive half.
3. **The `SCRIP_BBPROF` bones were NOT revived and their two defects are NOT fixed.** The addendum permitted reuse
   "only if BOTH its defects die"; nothing here reuses them, so nothing here discharges that condition. They remain
   dead code — `bbprof_record` is called only under `MEDIUM_BINARY`, which is why it "cannot report in m4 by
   construction". Retiring them is a separate row if anyone wants it.
