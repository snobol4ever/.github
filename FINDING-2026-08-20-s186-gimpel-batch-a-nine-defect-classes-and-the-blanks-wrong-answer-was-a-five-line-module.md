# FINDING s186 — gimpel batch A: 25 drivers, NINE defect classes, and the s183 BLANKS wrong answer bottoms out in a FIVE-LINE module

**Session:** 2026-08-20 s186 · seat5 · queue row `gimpel-drivers-A` (rank 4)
**Trees:** corpus `programs/gimpel/` + `probe/gimpel/`, SCRIP **`0b75fa5e`, `make pristine`** (RT_OPT `-O0`, FACT RULE O0-DEV — no codegen touched this session). ⛔ **Every verdict below was re-measured on that pristine build after a first pass on a day-old binary was caught and thrown away — see §7.**
**Oracle:** `x64/bin/sbl -b`, verified alive before any verdict. Every `.ref` in this row is live-oracle output; none hand-authored, none md5-pinned.
**Ruling served:** Lon s183 in-chat — *"You should make tests out of each Gimpel function. Make an entire test suite around it."*

---

## 1. THE BOARD — 25 modules, 25 drivers, m3 AND m4 verdicts

Convention copied exactly from HQ's `BASE10_driver` exemplar: `<NAME>_driver.sno` beside the module, `-INCLUDE "<NAME>.sno"` at the top, cases written from the module's HEADER COMMENT (the contract), `.ref` from the live oracle.

| verdict | n | modules |
|---|---|---|
| **GREEN** (m3 = m4 = oracle) | **10** | AGT · BALREV · BASE10\* · BCD_EBCD · BLEND · BREAKX · BSORT · COMB · INSERTB · LAST |
| **RED** (checked in red, law 0d) | **12** | ASM360 · BASEB · COPYL · DAY · DEXP · DEXTERN · DIFF · FASTBAL · FIND · FLD · INSERT · IP |
| **ORACLE-INCOMPATIBLE** (no `.ref` obtainable) | **3** | BAL · FTRACE · INFINIP |

\* `BASE10_driver` is HQ's s183 exemplar, re-verified green here.

⛔ **The 3 oracle-incompatible modules ship WITHOUT a `.ref`, deliberately.** SPITBOL refuses to run them and hand-authoring a ref is forbidden, so there is nothing honest to pin. Each is named below with the exact oracle error. This is the one place the row's DONE-WHEN ("a `<NAME>_driver.sno` + oracle `.ref`") cannot be met, and the reason is the oracle, not the work.

## 2. ⭐⭐ THE HEADLINE — s183's BLANKS SILENT WRONG ANSWER IS A FIVE-LINE PROGRAM

HQ found BLANKS returning `X = A + B` where the oracle returns `X=A+B`, and reasonably read it as the hard shape: `-INCLUDE`, 2 `DEFINE`s, recursive `ARBNO` through a defer, `FENCE`-in-`ARBNO`, `LEN(*DIFF(N,' '))`. **It is none of those.** BLANKS strips blanks by calling `DIFF(S,' ')`, and `DIFF.sno` is five lines. `DIFF_driver` is red on **all five** of its contract cases — SCRIP removes nothing at all:

| call | oracle | SCRIP m3 = m4 |
|---|---|---|
| `DIFF('ABCDEF','BDF')` | `ACE` | **`ABCDEF`** |
| `DIFF('MISSISSIPPI','S')` | `MIIIPPI` | **`MISSISSIPPI`** |
| `DIFF('ABC','ABC')` | `` (null) | **`ABC`** |

Ablated to **five lines with no function, no recursion, no ARBNO, no defer**:

```
        S  =  'ABCDEF'
        X  =  'BDF'
        X  =  SPAN(X)        <- rebind X to a pattern built over X's OWN former value
        S  X  =
        OUTPUT  =  S         oracle ACDEF · SCRIP ABCDEF
```

⭐ **THE INGREDIENT IS THE SELF-REFERENCE, AND THE CONTROL PROVES IT.** Bind the same `SPAN` to a *different* variable (`P = SPAN(X)`) and SCRIP is **correct**. Pattern-valued variables are fine; `SPAN` over a variable is fine; `SPAN` inline is fine. Only `X = SPAN(X)` goes inert — consistent with SCRIP binding SPAN's argument by name and reading it back after the target has already become the pattern. Both witnesses are committed as a red/green pair: `probe/gimpel/gim_span_self_rebind_wrong.sno` and `gim_span_self_rebind_control.sno`.

**Why this matters beyond BLANKS:** `X = SPAN(X)` is not exotic 1970s style, it is the ordinary SNOBOL4 idiom for "turn this argument into a matcher in place," and it fails **silently**. Nothing crashes, nothing is declared unlanded, the answer is just wrong.

## 3. THE NINE DEFECT CLASSES, EACH WITH A MINIMAL WITNESS

Seven are distilled to ≤6-line witnesses in `corpus/probe/gimpel/`, each with a live-oracle `.ref`. Two are named but not yet minimized. ⛔ **Cite the CONSTRUCT, never the op number** — `54b6c478` made the IR opcode enum alphabetical, so the numbers below are valid at `0b75fa5e` and nowhere else.

| # | class | from | witness | how it fails |
|---|---|---|---|---|
| 1 | `X = SPAN(X)` self-rebind is an inert pattern | DIFF, **BLANKS** | `gim_span_self_rebind_wrong` (+ green control) | **silent wrong answer** |
| 2 | `SPAN` over a PARAMETER, matched against the function's return variable | DIFF | `gim_span_param_pattern_wrong` | **silent wrong answer** — oracle `ACDEF`, SCRIP `CDEF`: the leading `A` is eaten along with the `B` |
| 3 | omitted **LEADING** argument shifts the rest left — `F(, 'y')` puts `y` in `A` | INSERT | `gim_omitted_arg_shift` | **silent wrong answer** (trailing omission `F('x', )` is correct) |
| 4 | `~` negation reaches the emitter as **IR op=3, no template** | IP | `gim_not_op_no_template` | **compiler FATAL**, m3 + m4 |
| 5 | deferred `TAB(*R)` reaches the emitter as **IR op=82, no template** | BASEB | `gim_tab_defer_no_template` | **compiler FATAL**, m3 + m4 |
| 6 | trailing-dot real literal `25.` rejected by the parser | DAY | `gim_real_literal_parse` | **parse error, no code generated at all** |
| 7 | `EVAL` of a `CONVERT`ed EXPRESSION **always succeeds** | FIND | `gim_eval_silent_success` | **silent wrong answer** — FIND returns 1 for every array and every predicate |
| 8 | the ASM360 field-splitting pattern mis-splits its fields | ASM360 | *(not minimized)* | **silent wrong answer** — `OPERAND` comes back empty and its text spills into `COMMENT` |
| 9 | runtime re-`DEFINE` of a function to a second entry label | COPYL | *(not minimized)* | **runaway → `[ZHP] heap exhausted (512 MB)`** |

⛔ **CLASS 7 IS THE DANGEROUS ONE AND IT IS A CONTRADICTION IN THE TREE.** `FLD_driver` and `DEXP_driver` get an honest refusal — *"EVAL and CODE are outside the landed subset (IR_MATCH_\* family pending)"*. But `FIND` routes through `EVAL(CONVERT(PRED '(MAX,TEST)','EXPRESSION'))` and gets no refusal at all: `EVAL` **answers, and always answers success**, so `FIND(A,'GE')`, `FIND(A,'LE')`, `FIND(B,'~LGT')` and `FIND(B,'LGT')` all return `1` against oracle `2/3/2/3`. The same unlanded feature is loud on one path and silently wrong on another. A feature declared unlanded must fail on **every** path that reaches it.

**Three reds are honest unlanded-subset refusals, not defects:** DEXP and DEXTERN (`DEFINE` with a non-literal prototype string — runtime `DEFINE` pending) and FLD (name operator over this form). They are red because the driver produces no oracle-matching output, and they are named here so the suite does not read them as bugs.

## 4. THE THREE MODULES THE ORACLE ITSELF CANNOT RUN

Tried `-b` **and** `-bf` on each; both spellings fail identically.

- **BAL** — `BAL.sno(11) : ERROR 042 -- attempt to change value of protected variable`. The module's function is named `BAL`, which collides with SPITBOL's **built-in protected `BAL` pattern**; `BAL = GBAL ARBNO(GBAL)` cannot execute. (Confirmed from the other side: `DEXP.sno` uses the built-in `BAL . ARGS` and runs green.) The driver is committed so the module is covered the moment an oracle that tolerates it exists.
- **FTRACE** — `FTRACE.sno(4) : ERROR 248 -- attempted redefinition of system function`. Line 4 is `OPSYN('DEFINE','FTRACE')`; SPITBOL protects `DEFINE`. The module's whole mechanism is redefining `DEFINE`, so this is unfixable from the driver side.
- **INFINIP** — `REDEFINE.sno(17) : ERROR 156 -- opsyn first arg is not correct operator name`, reached through `INFINIP_lib.sno`. A SNOBOL4+ program, not a SPITBOL one.

⭐ **The INFINIP driver still earned its keep.** Run bare, `INFINIP.sno` dies at `No END statement found in source file(s)` — it carries a lowercase `end` **label** and no `END` **statement**. The driver supplies the `END`, which advanced the failure past the front door to the real (deeper) incompatibility above. That is the driver convention working exactly as intended on a module nobody could previously run at all.

## 5. ⛔ TWO CORRECTIONS FOR HQ

**(a) The manifest misclassifies exactly ONE module, and it is in batch A.** `DRIVER-MANIFEST.tsv` classes `INFINIP` as `n_include=0` (self-contained), but it carries `-include "INFINIP_lib.sno"` in **lowercase**, which the census regex missed. Census run this session: exactly **1** module uses the lowercase spelling (INFINIP); the other 77 include-bearing modules use `-INCLUDE` and are classed correctly. So batch A is "24 self-contained + 1 mislabelled", and batches B–F need no reclassification.

**(b) The row's quoted corpus baseline is EXACT — retracted correction, kept visible.** The brief cites `m3 332/5 m4 325/11`. Measured on the pristine `0b75fa5e` build: **m3 PASS=332 FAIL=5 · m4 PASS=325 FAIL=11 SKIP=1 (337 total)** — the brief's number to the digit. **The fail-set is unchanged by this row and structurally cannot be changed by it:** `test_corpus_snobol4.sh` enumerates `crosscheck/`, `beauty_suite/*_driver.sno` and four named demos, and never touches `programs/gimpel/` or `probe/`. Every file this row adds is new.

⛔ **This session first reported the brief's baseline as STALE, against a measured `326/11 · 323/13`. That was wrong and the cause is §7.** The retraction is left in rather than quietly edited out, because the failure mode it demonstrates is the whole point of HQ-27: a stale binary does not announce itself — it produces a clean, plausible, fully-formatted board, and the first instinct on a mismatch is to doubt the DOC rather than the BUILD.

## 6. ⭐ THE METHOD NOTE THAT WILL SAVE BATCHES B–F A FALSE RED

**A driver can be contaminated by a defect in a construct it uses only incidentally.** The first `LAST_driver` and `COPYL_driver` built their test lists with `LINK(, 'B')` — an omitted leading argument — and both came back red. That red was **class 3, not LAST's and not COPYL's**. Rewritten with an explicit null variable (`LINK(NIL, 'B')`), **LAST went green** and COPYL's own genuine runaway was finally visible underneath.

The discipline: when a driver goes red, ablate the *driver's* scaffolding before naming the *module* red. A module's verdict is only trustworthy once the driver's own constructs are known-green. The corollary is cheap and worth doing every time — build the scaffolding out of constructs already proven green elsewhere in the batch.

Two smaller notes from the same pass: `DUMP` is a SPITBOL **system function** (`ERROR 248` on redefinition) — do not name a driver helper `DUMP`. And a driver case must stay inside the module's stated contract: `BLEND('','')` raises `ERROR 171` in the oracle because `BLEND.sno`'s `GT(L1,128)` guard routes length-0 past its own `EQ(L1,0) :S(RETURN)` early exit — a module bug, out of contract ("equi-length strings"), and an error dump is not a `.ref`. Case dropped. Worth recording separately: on that same input **SPITBOL raises `ERROR 171 -- null or unequally long 2nd, 3rd args to replace` where SCRIP silently returns null** — a divergence in `REPLACE`'s argument validation, found incidentally, not yet minimized.

## 7. ⛔⭐ THE MISS THAT ALMOST SHIPPED — HQ-27 IS NOT CEREMONY

The first full pass of this row ran against the `scrip` in the tree, which looked fine and ran fine. **It was built 2026-08-19 21:18. `git log --since` that timestamp: 52 commits** — including the s183 M1 RT-CARRIER cure (`0b7b8d29`, `943e404a`), which is precisely the pattern-machinery class these witnesses land in, and `54b6c478`, which renumbered every IR opcode.

Nothing failed. The stale binary produced a complete, internally consistent, entirely plausible board. It was caught only because a **number disagreed with a document** — the brief's corpus baseline — and the disagreement was chased to the build instead of being written off as documentation drift.

**What `make pristine` at `0b75fa5e` then changed:**

| | stale binary | pristine `0b75fa5e` |
|---|---|---|
| corpus baseline | m3 326/11 · m4 323/13 | **m3 332/5 · m4 325/11** (= the brief) |
| class 2 (`SPAN` over a parameter) | core dump | **silent wrong answer** `CDEF` |
| class 8 (ASM360) | core dump | **silent wrong answer**, fields mis-split |
| class 5 (deferred `TAB`) | IR op=**90** | IR op=**82** |

**The board itself did not move** — 10 GREEN / 12 RED / 3 ORACLE-INCOMPATIBLE, same modules, same verdicts, re-proven end to end. But two of the nine classes were **mis-described as crashes when they are silent wrong answers**, which inverts their priority: a crash is self-reporting, a wrong answer is not. And an op number cited from a stale enum is worse than no number, because it points a reader at the wrong template.

⭐ **The transferable rule, and it is stronger than "run pristine before a gate":** a stale build is indistinguishable from a current one by inspection of its OUTPUT. The only cheap detector is a number that a document also knows — so when a measurement disagrees with a checked-in figure, **suspect the build before the document**. Here the document was right twice: RULES.md's s172 figure matched the stale build and the brief's figure matched the current one, and reading that as "RULES is current, the brief is stale" was exactly backwards.

## 8. WHAT THIS CONFIRMS ABOUT THE STRATEGIC CLAIM

HQ predicted gimpel would be a second, independent witness source for the M1 class — code written in the 1970s by people with no knowledge of SCRIP, with a live oracle for every module. Batch A returns **nine defect classes from 25 modules**, seven of them minimized to ≤6 lines, and it **shrank** an existing M1-adjacent finding from a 30-line module with recursive `ARBNO` through a defer to a **five-line program with no function in it**. **Five of the nine are silent wrong answers** — the class that no crash, no gate and no FATAL would ever have surfaced. Two of those five were only *visible* as wrong answers on the current build: on the day-old binary they were crashes, i.e. the tree has been converting loud failures into quiet ones, which is exactly the direction that makes a driver suite worth more than a gate.
