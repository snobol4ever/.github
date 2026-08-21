# FINDING s193 (seat3, `/home/claude3`, Claude Opus 5) — queue row `treebank-allocating` (rank 26)

## ⭐⭐⭐ THE HEADLINE: THE ALLOCATING TREEBANK MATCHED AND BUILT **NOTHING**, ITS `.ref` PINNED THAT, AND THE CAUSE IS NOT THE PATTERN ENGINE — **SCRIP HAS NEVER IMPLEMENTED SPITBOL'S ALTERNATIVE EVALUATION `( e1, e2, …, en )`**

`lower_snobol4.c:705` lowered `TT_VLIST` as **`return sx_lower(cx, t->c[0], …)`** — the parser builds every element and **LOWER drops `e2..en` on the floor**. The construct is therefore correct exactly when `e1` succeeds and **silently fails the whole statement the moment `e1` fails**. Silently, because a failed SNOBOL4 statement prints nothing.

**The 4-line witness has no pattern matching in it at all:**
```
        x       = ARRAY('0:3')
        OUTPUT  = 'a[' (IDENT(x) 0, 7) ']'
```
Oracle `sbl -bf`: `a[7]`. SCRIP m3 and m4: **nothing at all.**

**Manual v3.7 p.99 "Alternative Evaluation" (and Appendix note 3, `( e1, e2, e3, …, en )`), verbatim:** *"The elements of the list are evaluated from left to right, until an evaluation succeeds. The value of the successful list element is returned as the value of the parenthesized list. No further list elements are evaluated when an element succeeds. If all elements fail, the entire list signals failure."* Characterised against the live oracle rather than read off the page: `(S1(),F1())` → `S` with F1 **never called**; `(F1(),S1())` → `S` with F1 called once; `(F1(),F1(),S1())` → `S` with F1 called twice. SCRIP got the first of those three right and printed nothing for the other two.

## ⛔ WHY IT REACHES THIS ROW: ONE LINE OF `treebank.sno`'s LIST LIBRARY

`ListInsert4` grows the backing array with

```
ListInsert4     a  =  ARRAY('0:' (IDENT(a(x)) 0, size * 2 - 1))
```

`IDENT(a(x))` succeeds only on the **first** insert (while `a(x)` is still null). On **every growth after the first** it fails, the alternative is not tried, the assignment never happens, `a` stays null, and `ListInsert8` then assigns that **null string** to `a(x)`. Measured directly, no pattern matching involved:

| after | oracle `DATATYPE(a(s))` / proto | SCRIP m3 |
|---|---|---|
| append A | ARRAY `0:0` | ARRAY `0:0` |
| append B | ARRAY `0:1` | **STRING** |
| append C | ARRAY `0:3` | ARRAY `0:0` |

## ⛔⭐⭐ THE `.ref` WAS TRUE OF A PROGRAM THAT DOES NO WORK — 'NON-EMPTY IS NOT ALIVE', PINNED

`corpus/programs/snobol4/demo/treebank.ref` is `matched bytes=327`, and SCRIP m3 prints exactly that. The program's *only* output is `SIZE(src)`, which is a property of the **input**, not of the parse. I added a re-serialiser (`Show(x)`) and asked both engines to print the tree they had just built:

- oracle: `(BANK (ROOT (S (NP (DT The) (NN cat)) (VP (VBZ sits)))) (ROOT (S (NP (DT A) (NN dog)) …)))`
- SCRIP m3: **`tree=`** — empty.

The pin cannot distinguish those. This is the project's own *"non-empty is not alive"* class (s33/s40/s43/s44) arriving as a checked-in reference file.

## ⛔ THE BRIEF WAS WRONG ON ARRIVAL IN BOTH HALVES, AND THE FIRST HALF IS AN ORACLE-FLAG ARTEFACT

The row says *"treebank.sno dead BOTH sides (oracle ERROR 217, m3 Error 5)"*, inherited from `FINDING-…-s168-PT-0-1-2` §1.

**(a) The oracle was never dead.** The `ERROR 217 -- duplicate label ×5` at lines 70/75/80/83/86 is the **s189 case-folding phantom**: SPITBOL folds names by default, and `treebank.sno` defines exactly five case-differing label pairs — `Init_list`/`init_list`, `Push_list`/`push_list`, `Push_item`/`push_item`, `Pop_list`/`pop_list`, `Pop_final`/`pop_final`. Five pairs, five errors, and the five lines named are exactly the lowercase halves. Under the **ruled** arm `sbl -bf` (RULES.md: `-f` is the oracle's LANGUAGE switch, the only correct arm for a case-sensitive SCRIP) it parses and runs: `matched bytes=327`.

**(b) m3's `Error 5` is downstream of the same defect.** With the alternatives dropped, `bank` is never assigned, so any statement that touches it dies in `a(bank)` — *"Undefined function or operation"*. At this HEAD `treebank.sno` itself no longer prints it only because its single output line never touches `bank`.

## ⭐ THE MEASUREMENT THE ROW ASKED FOR — AND THE WITNESS THAT COULD CARRY IT

`treebank.sno` cannot be the timed allocating row even with the flag fixed: on the benchmark tape input (`VBGinTASA.dat`, 100 KB) the **oracle** dies with `ERROR 246 -- stack overflow`, with or without the `EVAL` wrappers. The manual's Ch.9 p.136 action-routine ploy — `pattern . *fn()`, conditional assignment used to call at the right moment — is also the exact shape my own s190 row `dcap-alpha-cell-m4` kills in mode 4 (`rt_dcap_pump` → `rt_call_proc_descr` → an `alpha$<FN>` cell only the compiler process ever fills; backtrace confirms `rip=0xb`).

I therefore **minted** `corpus/programs/snobol4/demo/treebank-alloc.sno`: the same grammar, the same tape, the same input, with action routines that allocate an `ARRAY` per node and retain it in a `TABLE`, ridden on the **non-capture** deferred call `*fn()` with immediate `$` capture (manual p.87). Its identity gate is an **allocation-sequence checksum**, not `matched bytes` — a run that matches while allocating nothing cannot pass it.

⛔ **It is deliberately NOT the treebank parse, and the reason is measured, not assumed.** I first tried to keep the parse by rewriting the conditional-assignment actions to immediate ones. Re-serialising the result proves that road is a dead end: the oracle itself builds `(ROOT (S) (NP) (DT) The …)` — flat and wrong — because `ARBNO` tries its **empty** match first, so the trailing `*pop_list()` fires on every abandoned length. **The action-routine idiom genuinely requires conditional assignment**; that is what the manual's ploy is buying.

## ⭐ THE ALLOCATING ROW IS GREEN IN ALL THREE ENGINES, AND IT INVERTS THE NON-ALLOCATING RESULT

`bash scripts/bench_pt0_3way.sh --progs treebank-alloc --reps 40 --samples 7` · **RT_OPT `-O0`** (O0-DEV-O2-BENCH: this number is not comparable to an `-O2` one) · ratios are the deliverable, absolute ms are not (LAW 2):

| program | m3/sbl | m4/sbl | identity |
|---|---|---|---|
| `treebank-alloc` (allocating) | **0.53×** | **0.47×** | OK (3-way) |
| `treebank-match` (s168, non-allocating) | 1.14× | 1.19× | OK (3-way) |

**SCRIP is ~2× FASTER than the oracle once the match allocates, having been ~1.2× slower when it did not.** Same grammar, same input, same tape: the only variable is the allocation.

## ⭐ THE GC SPLIT — s168's H1 IS FALSIFIED FOR ALLOCATING MATCHING TOO, AT THE SHIPPED DEFAULT

Storage regenerations counted with `SCRIP_ZETA_TELEM=1`, one pass over the 100 KB input; arena via `SCRIP_HEAP_MB` (`ZC_HEAP_MB` default **512**):

| arena (`SCRIP_HEAP_MB`) | `treebank-alloc` (allocating) | `treebank-match` (non-allocating) |
|---|---|---|
| **512 MB — the shipped `ZC_HEAP_MB` default** | **0** | 0 |
| 64 MB | 0 | not measured |
| 32 MB | 0 | not measured |
| 16 MB | 0 | not measured |
| 12 MB | 0 | not measured |
| 8 MB | **6 372** | **0** |

*(`treebank-match` measured at 256 MB and 8 MB — zero at both; the intermediate arenas were not run for it because the endpoints already bracket it.)* The **40-rep bench tape** at the 512 MB default also does **0** regenerations.

**The allocating row is the first member of this family that can drive the collector at all** — the non-allocating twin does **zero** regenerations at every arena down to 8 MB, where the allocating one does thousands. **But at the shipped 512 MB default the allocating match still does ZERO**, so its GC share is **0 %**, exactly as s168 measured for the non-allocating half. H1 (*"the GC tax follows the match"*) is falsified for allocating matching too — not because the workload does not allocate, but because the arena is large enough that it never has to collect.

## LANDED

- **`src/lower/lower_snobol4.c`** — the `TT_VLIST` lowering, **DEFAULT OFF** (opt-in `SCRIP_VLIST_ALT=1`), the `SCRIP_B1C_LAND` precedent in `runtime_eval.c:232`: half a cure, shipped ahead of its partner because the default arm is byte-identical **by construction** (the same one-line `return`). The IR is provably right — element *i*'s **ω** is element *i+1*'s **α**, the last element's ω is the caller's, so *"all fail ⇒ the list fails"* falls out of the wiring rather than a test.
⛔ **AND IT IS PROVEN, NOT ASSERTED: A/B ON ONE TREE, 400 PROGRAMS** (`programs/snobol4/demo` + `crosscheck` + `probe`, `programs/lon/` excluded by construction), same tree with and without the patch, `--compile` md5 both arms: **0 movers / 400**. Gates green: `emit_no_lang` · `template_medium_invisible` · `icn_no_stack` · `icn_one_reg_frame`.
- **`scripts/bench_pt0_3way.sh`** — `sbl -b` → `sbl -bf` (one of the 19 unconverted call sites RULES.md names) plus `treebank-alloc` in `input_of`. ⛔ **The conversion is MEASURED INERT for the two rows that predate it:** `treebank-match` and `treebank-match-fence` are **byte-identical** under `-b` and `-bf` on `VBGinTASA.dat`, so s168's baseline numbers are not invalidated by this change.
- **`corpus/programs/snobol4/demo/treebank-alloc.{sno,ref}`** — `.ref` minted through `scorecard_snobol4.sh oracle` (the door the board grades through), classified **LIVE**, and read before commit. **PASS/PASS on the board, both modes.**
- **`corpus/probe/vlist/`** — three witnesses, `.ref`s all minted LIVE from the oracle and read: `vl_alt_first_ok` (**green**, the `e1`-succeeds half that always worked, so the reds cannot be misread as "the construct is unparsed"), `vl_alt_second` (**red**, and **green armed** — the lowering half), `vl_alt_nested_cat` (**red, and RED ARMED** — the ζ half). Two intended reds, declared.

## ⛔⭐⭐ WHY THE SWITCH IS OFF — THE OTHER HALF IS A ζ RUNG AND I DID NOT TAKE IT UNASKED

Armed, the lowering is correct and a **bare two-element** list works (`z = (IDENT(x) 0, 7)` → `7`). Everything else still breaks, and the asm says exactly why. The ζ-spine addresses every operand at a **static RSP depth**, and the retreat contract reads every **ω** as *"leave the statement"*:

```
n24_var_β:   add rsp, 16
             add rsp, 16;   jmp n29_lit_integer_α
```

The β chain unwinds the **enclosing expression's live cells** before jumping to the next element, and the out-of-line element is then planned at a depth that fits no frame — it writes `[rsp+320]` inside an 80-byte statement frame. So a VLIST nested in a concatenation yields `7]` where the oracle yields `A[7]`, and a three-element or all-fail bare list **SIGSEGVs**. This is the **s192 `zd_plan` family**: an arc that lands *inside* the statement read as a statement exit. **A guard that is correct only because no input has ever exercised it is not correct — it is unexercised**, and `TT_VLIST` had never delivered an ω that stayed inside the statement, because it had never delivered one at all.

## ⭐ THE GENERALISABLE MOVE

**A reference file is one half of a disagreement, and a program that prints a property of its INPUT has pinned nothing about its OUTPUT.** `matched bytes=327` is true of the correct parse, of an empty parse, and of a program that only measures the string it was handed. The defect had been sitting under a green pin since the file was checked in; it took **one added line that prints what the program built** to see it. Same family as s191's *"a lookup that prints is not a lookup that checks"* and s189's `default: return 0`.

## ROWS ASKED, NOT TAKEN

1. **`vlist-alt-zeta-depth`** — arm `SCRIP_VLIST_ALT` by teaching the release planner that this arc lands inside the statement. `vl_alt_nested_cat` is the ready-made witness; `vl_alt_second` is the already-green control.
2. ~~**`dcap-alpha-cell-m4`**~~ — ⭐ **ALREADY LANDED, THIS SESSION, BY SOMEONE ELSE, AND THE REBASE IS HOW I FOUND OUT.** seat4's row **`apply-snodef-m4`** (SCRIP `99cd7ede`, *"the m4 image was never told where `<FN>_α` lives"*) is the cure I asked for at s190. **Re-measured on the merged pristine tree, not assumed:** the faithful capture-target twin's **m4 SIGSEGV is GONE** — m3 and m4 now produce the **same** answer, and that answer is the empty tree, i.e. the VLIST defect. So the m4 half of this row is closed and **the only thing between a faithful allocating treebank and green-in-both-modes is `vlist-alt-zeta-depth`**. ⛔ One residual, recorded not chased: `treebank.sno` (the EVAL wrapper form) in m4 has moved from `Error 22` to `** Error 5 — Undefined function or operation` where m3 prints `matched bytes=327`; still an m3/m4 divergence, still out of this row's scope.
3. **`treebank-ref-is-blind`** — `treebank.sno`'s pin cannot fail; it should assert the tree, not the input size. Left alone here because touching it is a corpus ruling, not a compiler fix.

## RECEIPTS

SCRIP `c512089a` + this rung (`src/lower/lower_snobol4.c`, `scripts/bench_pt0_3way.sh`) · corpus `f7ce61c3` + this rung (`programs/snobol4/demo/treebank-alloc.{sno,ref}`, `probe/vlist/`) · **RT_OPT `-O0`** on every number (O0-DEV-O2-BENCH; label any comparison with its RT_OPT) · oracle **live** `sbl -bf` from `/home/claude/x64/bin/sbl`, invoked through `scorecard_snobol4.sh` for every `.ref` and every grade · m4 built `--compile` → `gcc -no-pie … -lscrip_rt`.
**⛔ RE-PROVED AFTER THE REBASE (RULES: re-prove the gate after a rebase), AND IT WAS NOT A FORMALITY — seat6's `DCAP-FRETURN-FALSE-ACCEPT` (`af1b9d64`) and seat4's `apply-snodef-m4` (`99cd7ede`) both landed on the same road while I was measuring.** `make pristine` at merged SCRIP `40a5b01a` (driver + `out/libscrip_rt.so` from ONE build, same minute; **zero** `-O1`/`-O2` in the build log): `treebank-alloc` **PASS/PASS** on the board · `vl_alt_first_ok` PASS/PASS · `vl_alt_second` red default / **green armed** · `vl_alt_nested_cat` red default / red armed · all four gates green.
**⛔ WHAT IS *NOT* CLAIMED:** no corpus watermark — the compiler change is **default off**, so the emitted tree is unchanged by construction and RULES step-4 regen is **N/A**; I did not run a full board and do not report one. The bench ratios are median-of-7 on one box and are **ratios**, not transferable absolute ms (LAW 2). The 512 MB / 8 MB regeneration counts are **counts**, which are timing-immune; the small-arena wall-clock sweep was abandoned as impractical (6 372 collections per pass) and no wall number is quoted for it.
