# FINDING — JCON is a demo now: two of its seventeen modules were never in the corpus, and `jtran` does not link

**hq_B · 2026-09-03 · MODE=QUARTET · row `jcon-compiler-is-a-major-demo-with-benchmark-numbers-in-the-readme`, dispatched by ceo (Lon in-chat ~15:32 CDT)**

## Summary

JCON is now a graded demo (`corpus/demos/icon/jcon/`, gate `test_demo_icon_jcon.sh`,
numbers `bench_triangulate_demos_icon.sh`). Two of its four programs are byte-identical
to the Arizona oracle in both modes; two are declared known-differences. Getting there
turned up **five defects and two stale documents**, three of which had been presenting
as something else entirely.

## 1. ⛔ Two of `jtran`'s seventeen modules were never in the corpus — and the absence presented as a lexer bug

JCON's `tran/Makefile` builds `jtran` from **seventeen** modules. Two are *generated*,
exactly as the Makefile generates them:

    do_ops.icn:    ./oplexgen     > do_ops.icn
    interface.icn: ./interfacegen > interface.icn

The corpus carried the 16 hand-written modules **and both generators**, but neither
generated file. The package README's own build order listed **fifteen** modules and
named neither.

⭐ **Why nobody caught it: the 15-module `jtran` builds and runs.** Nothing errors at
build time. But `lexer.icn` reaches into `do_ops` at its very first token, so every
pipeline stage past `preproc` died at `lexer.icn:14` with `procedure or integer
expected, offending value: &null` — a **missing build input presenting as a lexer
defect**, in the one module a reader would most readily believe was broken. The
`preproc`-only path works fine, which is exactly enough to make the program look alive.

**Cured.** Both files regenerated with the *oracle* (never with SCRIP — see below),
passed through the shared `tools/semicolonize_icon.py`, verified two ways (stripping
trailing `;` restores the generator's byte-exact output; `icont -c` gives the same
verdict before and after), and checked in with `#GEN:` headers. New script
`scripts/util_regen_jcon_generated_sources.sh` regenerates and **verifies** them; its
`--check` mode is clean at this HEAD.

⛔ **The generators must stay the oracle's job.** These two files are *inputs* to the
demo that grades SCRIP; generating them with SCRIP would let a SCRIP defect author its
own oracle input. Not hypothetical — SCRIP's own `oplexgen` emits the same lines in a
different order (defect 4 below), so a SCRIP regen would silently re-order `do_ops.icn`.

## 2. ⛔ IR op=21 is `IR_CORET` — and it is **not** a missing template

The task brief named `jtran_main.icn` dying with `FATAL emit_drive: IR op=21 has no
template in the universal driver` as "ONE real gap, name the op". The op is **`IR_CORET`**
(verified by compiling a probe against `src/ir/IR.h`, not by counting enum lines).

But the gap is not a gap. `emit.cpp:1259` plainly has `case IR_CORET:`. The abort comes
from the **guard sink inside that case** — `emit.cpp:1943-1946`, where an `IR_CORET`
whose operand has no slot (`sa < 0`) calls `drive_unowned`. The FATAL message says so
itself, in its own last sentence, and names the backtrace line as the authority; the
backtrace duly reads `emit.cpp:1946`, not `1478`.

**The actual trigger** — minimal witness, one line:

```icon
procedure main(); create foo(); end          # foo UNDECLARED -> compiler SIGABRTs (rc=134)
procedure foo(); return 1; end               # add this, and it compiles clean
```

So `create` of an **undeclared name** aborts the compiler where `icont` reports an
undeclared identifier and produces a runnable binary. ⭐ **And this is why it fires on
`jtran_main.icn` alone**: its `create preproc(...)`, `create yylex(...)` etc. name
procedures that live in *other* modules. Link the modules and every name resolves — the
abort disappears, which it does. **The op=21 failure is a symptom of defect 1, not an
independent blocker**, and grading `jtran_main.icn` in isolation was measuring the wrong
thing. Routed to hq_C as its own row anyway: a compiler must not abort on a program
`icont` accepts.

## 3. ⛔ `jtran` does not link — `icon-scan-resume-through-non-resumable-while-condition`

With all 17 modules linked, `jtran` compiles to 638,965 lines of assembly and then
**stops before a binary exists**, in both modes:

- **m3** — `bb_emit_end: 2 unresolved forward reference(s): label='n47_var_β'`, rc=134.
- **m4** — the `.s` assembles, then `ld` fails: `undefined reference to n6630_var_β`,
  `n6645_var_β`. Exactly two, both in `lexer.icn`'s `yylex`/`lex_yylex0`.

⭐ **The link-directive build and the old concatenated build fail identically** (same
638,965 lines, same two symbols), so this is a property of the program, not of the new
demo shape.

**Minimal witness — two lines. All three ingredients are required; remove any one and it
links:**

```icon
procedure g(); "" ? { while 1 do suspend 1 }; end     # scan + while + suspend
procedure main(); write(g()); end                     # oracle prints 1; SCRIP aborts
```

**Root cause, from `--dump-ir` on that witness.** Node 5 is the `SCAN`, carrying operands
`[enter, ., 7@]` — the third is its *resume* target, the `while`'s loop-back `GOTO` (`7@`).
`GOTO` is pure wiring, so the emitter follows it to node **2** — the loop **condition**,
a `LIT_INTEGER` — and asks for that node's **β** port. A non-resumable node emits only α.
Hence an emitted reference to a label that is never defined.

The condition axis confirms it exactly:

| condition | result | why |
|---|---|---|
| `while 1`, `while "x"`, `while gv`, `while 1 to 2` | ⛔ abort | condition is non-resumable — only α exists |
| `while f()` (generator), `while &fail`, `while not 1` | ✅ links | condition has a β |
| `until 1`, `every … do suspend`, `repeat suspend` | ✅ links | different loop-back shape |

⛔ **Routed to hq_C, deliberately not cured here.** The natural fix is a "resume at α"
marker on the scan's resume operand, and `IR_t` carries only **two** `IR_ref_t` (γ and ω)
— α and β are x86 labels, per the FROZEN LABEL MODEL in `GOAL-JCON-IN-SCRIP.md`. That is
a change to a frozen model and a correctness verdict; it is hq_C's call, not hq_B's.

⭐ **This closes an explicitly-open question from today.**
`FINDING-2026-09-03-seat02-icon-jcon-suite-census-and-level-cure.md` class 4
(`icon-jcon-class-forward-ref-deferred-emit`) says "Not yet root-caused to a specific
construct — needs its own ablation pass." This is that pass. ⚠ Note seat02's two
witnesses have since moved: `proto.icn` now passes m3 (rc=0), and `evalx.icn` now fails
on a *different* op (`op=121`, not a forward reference). `jtran` is the live witness.

## 4. ⚠ `oplexgen`: `key(table)` iteration order differs from the oracle

`oplexgen` emits JCON's operator-lexer decision tree by walking `every i := key(t.t)`
(`oplexgen.icn:235,240,246,254`). Measured: **611 lines on both sides, `sort` of the two
outputs byte-identical, m3 ≡ m4 exactly** — the multiset agrees, only the order differs.
Icon does not specify `key()` order, so the generated source stays valid Icon either way;
this is a byte-identity gap against the oracle, not a wrong answer. Declared in
`corpus/demos/icon/jcon/oplexgen.knowndiff`.

## 5. ⚠ `stop()` exits 0, and `exit()` does not exist

Found via `jlink`, whose stdout/stderr match the oracle byte-for-byte on all three arms
while its **exit status does not**:

```icon
procedure main(); stop("bye"); end     # oracle rc=1, message "bye";  SCRIP rc=0, message "bye"
procedure main(); exit(3);    end      # oracle rc=3;  SCRIP: ** Error 5 -- Undefined function or operation
```

`exit()` is a standard Icon builtin and is absent entirely. Both routed to hq_C.

## 6. ⛔ Two stale documents, both in hq_B's own lane, both now corrected

- **`SCRIP/README.md` claimed a working self-host** — "SCRIP compiles the 17-module JCON
  translator … into one native x86-64 binary (656K lines) … and that binary starts and
  drives its full pipeline." At this HEAD there is no binary (defect 3), and the assembly
  is 638,965 lines, not 656K. Replaced with the measured demo grid.
- **`scripts/bench_icon_rate_3way.sh`'s header still instructs "build SCRIP with `-O2`
  before running (O0-DEV-O2-BENCH)"** — VOID law since Lon's s262 FACT RULE (`RT_OPT` is
  `-O0`; there are no `-O2` builds, ever). Flagged, not edited: it is a one-line header
  fix in a script this row does not otherwise touch, and it belongs with whoever next
  opens that file. **Named here so it cannot go on being invisible.**

## 7. New instruments

- **`scripts/test_demo_icon_jcon.sh`** — the demo gate. Builds its own `icont` oracle
  from the same sources every run (so an oracle/SCRIP difference can never be source
  drift). **Refuses `rc=2` rather than skipping.** A declared known-difference that starts
  *passing* is reported `XPASS` and **fails**, so a cure cannot land silently behind a
  stale marker. Three defects were found in the gate itself while building it, each fixed
  and commented at the site: program args need `--` in m3 or the driver reads them as
  flags (and an unrecognised flag is not diagnosed — it is treated as a *filename*); the
  answer is on **stderr** for `jlink`, so the oracle picks the stream once for all arms;
  and a `BUILD-ERR` must outrank an empty-oracle void, which the first cut got backwards
  and duly printed `VOID-EMPTY-ORACLE` over `jtran`'s real blocker.
- **`scripts/bench_triangulate_demos_icon.sh`** — three-angle triangulation for Icon
  *demos*, modelled on `bench_triangulate_demos_snobol4.sh`. Icon previously had no
  triangulator at all (only `bench_icon_rate_3way.sh`, a kernel harness implementing
  angle 1 alone), which is why RULES.md § THE TWO-NUMBER BENCHMARK BASIS still says "Raku
  and Icon lack triangulation scripts". **Raku no longer does, and now neither does Icon** —
  that clause is ready to retire.
- **`scripts/util_regen_jcon_generated_sources.sh`** — regenerates and verifies the two
  generated modules.

## 8. The numbers, and one ruling I need from ceo

Angles 1 and 2 agreed within 4% on every row, two independent runs. `RT_OPT=-O0`.
⛔ Basis: **one iteration = one whole program run** — a TOTAL carrying process startup
(and, for m3, the compile). Never to share a column with a kernel slope.

| demo | m3 vs `iconx` | m4 vs `iconx` |
|---|:---:|:---:|
| `interfacegen` | 0.19–0.21x | **1.28–1.40x** |
| `jlink` | 0.03x | 0.77x |

Ranges are the spread across two runs, not error bars. `oplexgen` and `jtran` get
timings but **no multiple**, because their output does not match the oracle.

⚠ **ASK (non-blocking, proceeding as described).** The law computes multiples on **WORK**
(total − overhead), with empty-program subtraction as the marked interim where an engine
has no clock hook. These are unmodified upstream JCON sources with no `wall_ms` hook, and
on a 4–5 ms program against a 2–4 ms process startup **the subtraction is dominated by its
own error bars, and it inverts**: on totals m4 (3.93 ms) beats iconx (4.99 ms), while the
same run on the work basis reports m4 at **0.465x**, i.e. slower. Both cannot be true and
neither belongs in a README. So the harness **detects overhead ≥ 50% of either arm and
refuses the work multiple**, printing the total-basis multiple in its place, labelled —
never both, never the work number with a quiet asterisk. I believe that is the right
reading of the law's intent (the law's own reason for the split is that startup is
irrelevant to a process server — it is not a licence to publish a number that is mostly
subtraction noise), but the law's letter says multiples are computed on WORK. **Ruling
requested; the README ships the labelled total-basis grid meanwhile.**

## Verification

- `test_demo_icon_jcon.sh` — **PASS(0)**: `interfacegen` and `jlink` byte-identical both
  modes; `oplexgen` and `jtran` declared, still-differing known-differences.
- `util_regen_jcon_generated_sources.sh --check` — clean.
- Both generated modules: semicolonization verified byte-exact by strip-back, and
  `icont -c` identical before and after.
- ⭐ **No `src/` file was touched by this row** — the work is corpus, scripts and docs — so
  the shared-node grading obligation does not arise. Control arms run anyway and reported
  in the LEDGER.

## Routed

- **hq_C** — defect 2 (`create` of an undeclared name aborts the compiler), defect 3
  (`icon-scan-resume-through-non-resumable-while-condition`, the `jtran` blocker, with the
  frozen-label-model design question), defect 5 (`stop()` exit code, missing `exit()`).
- **ceo** — the WORK-vs-TOTAL basis ruling above; the VOID `-O2` header in
  `bench_icon_rate_3way.sh`; and RULES.md's "Raku and Icon lack triangulation scripts"
  clause, now false in both halves.
