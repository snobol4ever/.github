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

---

## ⛔⭐ CORRECTION, SAME SITTING, SAME SEAT — THE ATTRIBUTION ABOVE IS WRONG AND THE RULING IT ASKED FOR IS VOID

Everything above about the **mechanism** holds and was re-verified. **The blame does not.** I wrote that `io.icn` is an *upstream* defect and that the vendored source is *out of sync with the vendored object*. It is neither.

**The stray semicolon is OURS.** `corpus` carries three commits that rewrote the Icon corpus into SCRIP's semicolon-required dialect — `ba07c0350` (explicit semicolons in every checked-in Icon program), `f8fe5b83d` (**convert packages/icon/ipl to semicolon-required style, 826 files**), `5e921aa3a` (strip the trailing semicolon from 6181 procedure header lines). Upstream `/home/resources/icon-master/ipl/procs/io.icn` has **no semicolons in that case body at all** and `icont` compiles it without complaint:

```icon
   return case head := x[1] of {
      separator: [separator]
      "": []
```

⭐ **This is the exact hazard RULES.md names and that I had already written into my own memory: adapting a corpus for the tool makes the edit part of the oracle's input.** I then spent the investigation treating our edit as the vendor's code, and wrote a FINDING blaming upstream for it. The `.u` files were a real and interesting red herring — they *do* explain why `icont -s -c datmerge.icn` is silent — but they let me stop one step short of asking **who wrote the line**. `git log` on the file answers in one command, and I ran it only after the FINDING was already pushed.

## THE ACTUAL SCOPE, MEASURED — IT IS ONE CHARACTER

Every `.icn` in `packages/icon/ipl/procs` handed to `icont` individually: **1 of 251 refused**, and it is `io.icn`. Our 826-file conversion produced exactly one casualty. Removing that single trailing semicolon:

- `icont` **accepts** our `io.icn` outright (the further errors it reported at lines 439 and 458 were cascades of the first, not separate defects);
- of the **136** files the strict parser refused that `icont` accepts, **0 remain**;
- `test_gate_icn_ipl_scan_resume_and_limit_flips` goes **GREEN on all three programs in both modes** — `datmerge`, `ibrow`, `miu`.

**So there is nothing to rule on.** Neither option I put to the ceo applies: no vendored source is edited (ours is restored toward upstream), and nothing goes outside the baseline. The parser cure is unblocked and lands with the one-character corpus repair beside it.

## ⚠ AND A MISTAKE OF MINE TO RECORD, NOT ONLY A MISREADING

Cleaning up after my own sweep, I ran `git clean -f -- '*.u1' '*.u2'` in `corpus` on the belief that the 284 `.u` files were artifacts my `icont` runs had just created. **I checked that vendor `.u` files were tracked, found they were not, and cleaned anyway** — the check fired correctly and I read its answer backwards. `io.u1`/`io.u2` predate this session, are **not** in git, and are therefore **not restorable from origin**.

What that does and does not cost, stated precisely rather than reassuringly:
- Untracked files exist **per clone**, so no other seat's tree is touched and nothing origin defines was lost.
- SCRIP never reads `.u` files at all; only `icont` does.
- With `io.icn` now valid, `icont` can regenerate them, which it could not do while our semicolon stood.

⭐ The lesson is narrower than "be careful with `git clean`": **`git clean` deletes by tracked-ness, and I reasoned about provenance** — *I made these files a minute ago* — which is a different property that git was never asked about and never reported on. The same shape as the two instrument errors already recorded above.
