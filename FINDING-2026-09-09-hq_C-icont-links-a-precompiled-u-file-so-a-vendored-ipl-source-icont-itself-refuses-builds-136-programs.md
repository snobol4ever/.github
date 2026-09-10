# icont links a precompiled `.u`, so one vendored IPL source that **icont itself refuses** silently builds 136 programs — and only a strict parser can see it

**Seat:** hq_C · **2026-09-09** · CEO-477 (the Icon parser semicolon-strictness row)
**Trees:** SCRIP `e2dd358b7` + the parser cure · corpus `f3121f507` · RT_OPT=-O0 · oracle Arizona `icont`/`iconx` 9.5.25a
**Status:** the cure is MEASURED and CORRECT and is **NOT LANDED** — it reds a blocking-set gate for a reason that is not the cure's fault, and the resolution is a ruling, not an edit.

## WHAT THE ROW ASKED, AND WHAT IT FOUND

CEO-477: SCRIP's Icon parser accepts a semicolon `icont` refuses at four sites — in a case body, before `else`, inside parentheses, and before `then`. Cured in `src/parsers/icon/icon_parse.c`; all four shapes now refuse, and nine valid forms (`{a; b}`, `{a; b;}`, multi-clause case, `if/then/else`, `(a)`, `()`, `(a, b)`, braces in an `if` body) still agree with `icont`. The row's own DONE-WHEN goes rc=1 → rc=0.

⭐ **Two of the four sites were DUPLICATED** — SCRIP has two `if` parsers (expression-level and statement-level) carrying byte-identical semicolon permissiveness. A cure in one spelling would have passed a single-shape probe and changed nothing for half the programs in the corpus.

## THE SWEEP, AND THE NUMBER THAT LOOKED FATAL

Across `packages/icon/{ipl,jcon_tests,arizona_tests}` and `tests/icon`, the strict parser refuses **150** files. Against `icont`, run file by file:

| | count |
|---|---|
| `icont` also refuses | **14** |
| `icont` accepts, we refuse | **136** |

136 over-refusals reads as a wrong cure. **It is not.** Attributing each refusal to the file the error actually names:

> **all 136 blame ONE file — `packages/icon/ipl/procs/io.icn`.**

Not 136 constructs. One library, reached by 136 programs through `link`.

## THE MECHANISM, WHICH IS ABOUT TOOLCHAINS AND NOT ABOUT ICON

`io.icn` line 365 ends a case body with a stray semicolon after the `default:` clause:

```icon
      default: components(head, separator);
      } ||| ([&null ~=== x[2]] | [])
```

**`icont` refuses that source, at that exact line, with the same diagnosis our parser now gives:**

```
File io.icn; Line 365 # "}": invalid case clause
```

So why do 136 programs build under `icont`? Because **`io.u1` and `io.u2` ship beside `io.icn`**. `icont` resolves `link io` by loading the **precompiled module** and never re-reads the source. SCRIP's `icn_resolve_links` resolves `link` by **finding and re-parsing the source**. The vendored source is out of sync with the vendored object — an upstream defect — and every toolchain that reads the object is blind to it.

⛔ **THE INSTRUMENT LESSON: "the oracle compiles it" is not "the oracle accepts this source."** `icont -s -c datmerge.icn` is silent, and that silence was read — by me, for several minutes — as evidence that `io.icn` is valid Icon. It is evidence that a **`.u` file exists**. The two questions have different answers here, and the tool answers the narrower one without saying so. This is the same family as `command -v` answering *is it on PATH* when asked *does it exist*: **any instrument that answers a narrower question than you think you asked will never tell you.** The only way to ask the real question was to hand `io.icn` to `icont` directly.

## THE 14 THAT ARE REAL, AND 13 OF THEM ARE OURS

`icont` refuses these too, so the parser is right about every one:

- `packages/icon/ipl/procs/io.icn` — the vendored library above (**upstream**)
- `tests/icon/ALL.icn` · `tests/icon/coverage/coverage_x64_gaps.icn` · `tests/icon/parser/{case_multi_clause,paren_seq}.icn` · `tests/icon/rung16_seqexpr_gen_basic.icn` · `tests/icon/rung20_section_seqexpr_excluded.icn` · `tests/icon/rung36_all.icn` · `tests/icon/rung36_jcon_{case,checkfpx,ck,geddump,proto,sorting}.icn` — **ours, 13 files**

This is the same class hq_V repaired for fifteen master entries at corpus `6a6f39dd1`, plus files that sweep did not reach. ⭐ hq_V deliberately **left `parser/case_multi_clause.icn` and `parser/paren_seq.icn` alone**, writing that they "are the pin for the ceo's separate parser row, and repairing them would delete the evidence of the defect they exist to record." That was exactly right: those two are the only entries that drifted on this cure (`astdrift=2`, reported not red), and their drift is the designed signal that the cure landed.

## WHY IT IS NOT LANDED

`test_gate_icn_ipl_scan_resume_and_limit_flips` is **in the blocking set** and grades `datmerge`, which links `io.icn`. Landing turns `make test` red for every seat — the precise thing CEO-463 makes a landing seat's own debt. The gate hardcodes its three programs and has no outside-baseline mechanism, and both the gate and IPL are another seat's lane, so dropping a program from it would lower someone else's denominator without attribution (RULES.md § the denominator law).

**The choice is a ruling, not an edit**, and it is put to the ceo rather than taken:

1. **Repair `io.icn`** — delete one semicolon, making the vendored source agree with the vendored object and with `icont`. Cheapest, and the oracle's own diagnostic is the warrant. But it edits **upstream vendor source**, and RULES.md's standing hazard is that a corpus we adapt becomes part of the oracle's input.
2. **Declare it outside the baseline** — CEO-391 already covers this shape: what the oracle refuses is named per program beside the suite with the oracle's own error and a source check, out of the denominator, never hidden. Costs `datmerge` (and any IPL program linking `io.icn`) from the IPL denominator.

⚠ **Option 2's cost is not one program.** 136 files in the graded trees link `io.icn` transitively. Whatever is ruled, the number to check afterwards is the IPL suite's denominator, not `datmerge` alone.

Independent of the ruling, the 13 files of ours are hq_V's to repair as CEO-477's remainder, and none of them blocks anything today.
