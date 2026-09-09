# FINDING 2026-09-08 hq_P — 213 correct witness pairs are in NO denominator; grading the 40 SNOBOL4 ones found 5 reds, including a SEGFAULT

## Claim

`corpus/tests/<lang>/` holds **213 `<name>.<ext>` + `<name>.ref` pairs that appear in no `ALL.csv`,
no `ALL.xfail` and no `ALL.excluded.txt`.** They are not passing, not expected-failing, and not
excluded — **no denominator contains them**, so no board has ever run them.

I ran the 40 SNOBOL4 ones. **35 pass; 5 are RED**, and one of the reds **segfaults in both modes**.

## The census

| language | orphaned pairs | of loose sources |
|---|---|---|
| **icon** | **172** | 239 |
| **snobol4** | **40** | 142 |
| snocone | 1 | 70 |
| prolog | 0 | 44 |
| raku | 0 | 98 |
| pascal | 0 | 6 |
| rebus | 0 | 4 |
| **total** | **213** | |

⛔ **The two announcement languages are exactly the two with the problem**, and Icon carries 172 of
the 213. I have **not** graded the Icon 172 and make no claim about them beyond this: nothing runs them.

⭐ Instrument control-armed in **both** directions before I believed any of it — names reported
orphaned score 0 hits in `ALL.csv`, and a name reported present (`ladder__rung14_…`) scores 1. An
"is it in the file" probe that silently under-reports is this project's signature failure, so it was
tested for exactly that.

## The 5 SNOBOL4 reds

| witness | oracle | SCRIP m3 |
|---|---|---|
| `define_redef_three_way` | `one` / `two` / `three` | `three` / `three` / `three` |
| `define_redef_alt_entry` | `first` / `second-via-alt-entry` | `second-via-alt-entry` ×2 |
| `nested_alt_span_breakx_rpos` | `match` | **prints nothing at all** |
| `nested_arbno_rpos` | `match` | **SIGSEGV (rc=139), both modes** |
| `probe_loose_fwctx_fwctx_suite_malformed` | — | (not characterised here) |

The first two belong to the compile-time-`DEFINE` class already filed and routed to the cto
(`FINDING-2026-09-08-hq_P-define-is-applied-at-compile-time-…`). The next two are **new** and are
pattern-engine defects.

## ⛔ `nested_arbno_rpos` — nesting ARBNO segfaults, and the ablation is one token wide

```
          'aa' (ARBNO(ARBNO(BREAKX('a'))) | '') RPOS(0)     :S(OK)F(NO)
OK        OUTPUT = 'match'                                  :(END)
NO        OUTPUT = 'nomatch'
END
```

| pattern | oracle | SCRIP |
|---|---|---|
| `ARBNO(BREAKX('a'))` | `match` | `match` |
| `ARBNO(ARBNO(BREAKX('a')))` | `match` | **SIGSEGV** |

**One added `ARBNO` is the entire difference.**

⭐ **It is NOT stack exhaustion**, which is the natural guess for a nested repetition operator over a
pattern that can match empty. Under gdb:

```
Program received signal SIGSEGV
0x0000000000000000 in ?? ()
#0  0x0000000000000000 in ?? ()
rip = 0x0; saved rip = 0x0
```

**`rip = 0x0` — the generated code jumps to address zero.** That is an **unwired Byrd-box port**
(a α/β/γ/ω wire left NULL at compile time), not runaway recursion. The distinction matters: the
recursion theory sends you to the runtime and to `&STLIMIT`; the real defect is in port wiring when
`ARBNO` nests, and it is a compile-time bug with a runtime symptom.

⛔ It is also **not classified by our own SIGSEGV handler** — `rt_stack_overflow.c` exists to report
stack-guard faults as ERROR 246 and this produces a bare signal 139, which is correct (it is not a
stack fault) and is worth knowing: a raw 139 from a pattern is a wiring bug, an ERROR 246 is depth.

## `nested_alt_span_breakx_rpos` — a silent wrong answer

```
          'a+a+a' (SPAN('ab') | (BREAKX('ab') | '')) RPOS(0)     :S(OK)F(NO)
```

Oracle prints `match`. SCRIP prints **nothing** — neither `match` nor `nomatch`, so both the S and F
branches were skipped. ⛔ A statement whose success and failure gotos are *both* unreached is the
same wiring smell as the segfault above and the two should be looked at together.

## Why this class is worse than xfail, and why it is a new shape

This project has catalogued the vacuous test (an instrument that cannot fail) and the stale
denominator (a count that moved). This is neither. It is a **correct, failing, committed test that
no denominator contains** — and it is strictly worse than an `xfail`, because an `xfail` at least
appears in a census and `test_gate_no_xfail_survives.sh` counts it. These appear nowhere. Every
count we keep starts from `ALL.csv`.

⭐ The SNOBOL4 master read **1894/1894 FAIL=0 both modes, ast 28/28, MISSING=0** on SCRIP `0567aba18`
/ corpus `34c90a593` tonight — a genuinely green board, with a segfaulting witness sitting in the
tree beside it.

## What I did NOT do, and why

⛔ **I did not add these to any master.** Five known-reds would take the blocking arm from `FAIL=0`
to `FAIL=5` for every seat 34 hours before the announcement. Whether they enter before or after the
cures is a `ceo` decision. The honest state is: they are red, they are real, and the board does not
know about them.

## Routing

- nested-ARBNO SIGSEGV + the silent nested-ALT answer → pattern engine / port wiring (`hq_U`).
- the 172 Icon orphans → `hq_C`'s lane to grade; **ungraded, not alleged red**.
- the denominator decision → `ceo`.

## Provenance

SCRIP `0567aba18`, corpus `34c90a593`, `RT_OPT=-O0`, oracle `/home/resources/x64/bin/sbl -bf`,
master board re-run to green on this same tree.
