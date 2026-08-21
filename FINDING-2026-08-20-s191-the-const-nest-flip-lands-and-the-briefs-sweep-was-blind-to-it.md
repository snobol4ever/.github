# FINDING s191 (2026-08-20, seat6 `/home/claude6`, Claude Opus 5) — **THE `SCRIP_CONST_NEST` FLIP LANDS, AND ITS REAL BLAST RADIUS IS TWO PROGRAMS OUT OF 2136 — BUT THE BRIEF'S 527-PROGRAM SWEEP WOULD HAVE SHOWN ZERO AND CALLED IT PROVEN.**

**Brief executed:** queue row `const-nest-flip` (rank 2) — *"re-verify the arming precondition at THEN-current HEAD … then the full treatment before any default flip: 527-artifact .s sweep + the 6-suite board, both arms self-diffed twice as the control. DONE-WHEN: flip landed with killswitch and =0 reverting VERBATIM; .s blast radius named line by line; 6-suite board movers each traced to a mechanism; corpus fail-set no worse; FINDING."*

## ⛔ THE ONE SENTENCE

The arming precondition holds and is now *measured* rather than read — `SCRIP_SPAN_FRAME=0` still reproduces the s130/s131 leaf-suspension SIG11 under `CONST_NEST=1` on three witnesses, and at the shipped default it is gone — but the brief's named instrument is **blind to this rung**: the 527-program list contains not one `&`-constant program, so it reports **0 movers** for a flip that changes two programs and cures a silent wrong answer.

## 1. THE ARMING PRECONDITION — RE-VERIFIED, AND MEASURED NOT READ

`sn4_span_frame()` (`src/emitter/emit.cpp:2342`) reads `(e && *e == '0') ? 0 : 1` — **default ON** since `d3251f23`. That is the source half. The measured half, at pristine HEAD `28e2122a`, RT_OPT `-O0`, on the witness family the CN-15 comment names:

| witness | OFF | `CONST_NEST=1` | `CONST_NEST=1 SPAN_FRAME=0` |
|---|---|---|---|
| `cn_nest_alt_defer` | PASS/PASS | PASS/PASS | PASS/**SIG11** |
| `cn_alt_leaf_flat_red` | PASS/PASS | PASS/PASS | PASS/**SIG11** |
| `cn_alt_leaf_lit_red` | PASS/PASS | PASS/PASS | PASS/**SIG11** |
| `cn_alt_leaf_flat_grn` | PASS/PASS | PASS/PASS | PASS/PASS |
| `cn_const_compose_all` | **DIFF/DIFF** | **PASS/PASS** | PASS/PASS |

The third column is the blocker, alive and reproduced on demand. The precondition is not a historical note — it is a live dependency, and this table is the receipt that the flip rides on `d3251f23` and would be wrong without it.

## 2. ⛔ THE BRIEF'S INSTRUMENT IS BLIND TO THIS RUNG — 0 MOVERS / 527, AND THAT NUMBER MEANS NOTHING HERE

`util_s_md5_sweep.sh`'s default list is *demo (maxdepth 1) + crosscheck + probe/bb*. Run at both arms it reports **0 movers / 527 comparable**, both arms self-diffed twice = **0 rows**. That is a true statement and a worthless one: **not one program on that list declares a `&` user constant**, so the list cannot express the flip. The 527 is the right denominator for a *codegen* rung (its origin: ARBNO-TAIL-BETA byte-identity) and the wrong one for a *lowerer* rung whose reach is a source construct. Taking `0/527` as the flip's blast radius would have been a plausible, fully-documented, entirely empty proof.

**So the sweep was re-aimed at the construct, not at the habit.** Every program in the tree that the switch can reach — which is more than `.sno`, because `.sc` (Snocone) and `.reb` (Rebus) lower through the same `lower_snobol4.c` — with `corpus/programs/lon/` excluded **by construction** (RULES: off limits, never compiled; the list is built by a `find` that cannot name it):

| list | comparable | movers | control (self-diff) |
|---|---|---|---|
| brief's default 527 | 527 | **0** | 0, 0 |
| all `.sno` (`corpus/**`, lon excluded) | 1648 | **2** | 1 — see §4 |
| all `.sc` + `.reb` | 488 | **0** | 0 |
| **total** | **2136** | **2** | — |

## 3. THE BLAST RADIUS, NAMED LINE BY LINE — TWO PROGRAMS, ONE MECHANISM, AND BOTH SHRINK

Both movers are `corpus/probe/cn/`. In both, the emitted `.s` gets **smaller**, and the box sequence says exactly why: the dynamic keyword-read + assign scaffolding that built the pattern at run time disappears, and each `match_defer` standing in for a nested `&` member is replaced by the member's **staged tree**.

### `cn_const_compose_all` — 526 → 461 lines, first diff at line 26
`&A = ARBNO('a')` · `&B = ''` · `&P2 = &A &B` · `'aa' POS(0) *&P2 RPOS(0)`

* **deleted:** `n20_keyword_snobol` `n21_assign_` — the run-time read of the nested member and its store into the composed pattern.
* **replaced:** `n24_match_defer_` → `n22_match_arbno_{α,as,af}` — `&A`'s ARBNO staged inline as a real box.
* **renumber:** everything from the old `n22` down shifts by −2. Boxes `n0..n19` are identical and identically numbered.
* `PATV$`/defer symbols **6 → 0**.

### `cn_nest_alt_defer` — 732 → 608 lines, first diff at line 16
`&W2 = SPAN("ab")` · `&N2 = SPAN("09")` · `&P = &W2 | &N2` · `"ab" POS(0) *&P RPOS(0)`

* **deleted:** `n27_keyword_snobol` `n28_assign_` `n29_keyword_snobol` `n30_assign_` — one read+store pair per nested member.
* **replaced:** `n37_match_defer_` `n38_match_defer_` → `n33_match_span_` `n34_match_span_` — both SPANs staged inline.
* **renumber:** old `n31..n36` → `n27..n32` (−4). Boxes `n0..n26` identical and identically numbered.
* `PATV$`/defer symbols **12 → 0**.

⭐ **This witness predicted its own cure in its header comment**, written at s161: *"When that emission defect is root-caused, the depth limit deletes and this witness's defer count drops — output stays exactly this either way."* The defer count dropped 2 → 0 and the output stayed `match`. The prophecy is the receipt.

## 4. THE CORRECTNESS HALF — THE OFF ARM IS A SILENT WRONG ANSWER

`cn_const_compose_all` is not a byte-shuffle. It is **`nomatch` at the default arm and `match` at the flipped arm**, in both media, against a pinned `.ref` of `match`:

* OFF: `DIFF/DIFF` — prints `nomatch`.
* ON: `PASS/PASS` — prints `match`.

`'aa'` anchored `POS(0) … RPOS(0)` against `ARBNO('a')` concatenated with `''` must match. The defer road answers no. The staged-tree road answers yes. **The flip's second mover is a cure and its first mover is a proof the cure is mechanical, not incidental.**

## 5. WHY THE FLIPPED ARM IS THE SEMANTICALLY FAITHFUL ONE (manual, not taste)

SPITBOL manual v3.7, *Recursive Patterns*: a pattern-valued variable composes **by value** at the moment the composing statement executes — `LIST = "(" ITEM ARBNO("," ITEM) ")"` incorporates `ITEM`'s value then and there — and the unevaluated-expression operator `*X` is the **sole** form that defers, and the sole form recursion is built from. Substituting a nested `&` member's staged tree at compile time is therefore the faithful reading of `&P2 = &A &B`: `&A`'s value is what belongs in the composition. The top-level-only limit was never a semantic position; it was a s161 containment measure around the s130/s131 emission defect, and that defect is cured. Genuine self-reference still refuses and still bottoms out in the dynamic defer — `sno_kw_chase(nm, 0)` is the honest cycle test the stack was built for — which is exactly the manual's `*X` recursion, preserved.

## 6. TWO THINGS THE SWEEP FOUND THAT ARE NOT THIS ROW'S — BOTH ARM-INDEPENDENT, NEITHER A FLIP BLOCKER

### (a) ⛔ `unary_not.sno` BAKES UNINITIALISED MEMORY INTO `.rodata` — A DIFFERENT BINARY EVERY COMPILE
`corpus/programs/snobol4/parser/unary_not.sno` is **one line**: `x = ~BREAK(nl)`. Its emitted `.s` differs on **every single compile**, in **both arms**, and the entire difference is one `.rodata` string:

```
n5_assign_α:   lea rdi, [rip + .S0]
.S0:           .string "FK\001"      <-- compile 1
.S0:           .string "\262\313"    <-- compile 2   (also: "\3427\001", "\226\017", ...)
```

Four consecutive compiles gave four different md5s at each arm. This is a compiler reading uninitialised memory and **emitting it into the program**. It is arm-independent, so it is not a flip mover — it is the **noise floor of the `.sno` sweep**, and it is the reason that sweep's control shows 1 row instead of 0. ⛔ It also means any future byte-identity gate that includes this program is one row noisy forever, and a real one-row regression there would be invisible. **Not fixed here (out of row scope) — proposed as its own queue row via the QUESTION BOX.**

### (b) THE MIXED CONSTANT/ORDINARY COMPOSE SEAM — STILL RED, AND MY FLIP CANNOT REACH IT
A three-way discriminator is already checked in, and only the middle case is mine:

| witness | shape | OFF | ON |
|---|---|---|---|
| `cn_const_compose_ctl` | all ordinary: `P2 = A B` | PASS/PASS | PASS/PASS |
| `cn_const_compose_all` | all constant: `&P2 = &A &B` | **DIFF/DIFF** | **PASS/PASS** ⬅ this row |
| `cn_const_compose_leaf` | **mixed**: `P2 = &A &B` | **DIFF/DIFF** | **DIFF/DIFF** |

The mechanism is visible in the emitted head-blob and is the *same wrong-answer road*, reached through a different gate: in the all-ordinary control the blob opens `n0_match_arbno_{α,as,af} n1_match_lit_` — the ARBNO **staged**; in the mixed case it opens `n0_match_defer_ n1_match_lit_` — the ARBNO **deferred**, and the defer answers `nomatch`. `sno_kw_nest_ok` gates substitution of a keyword member inside a **keyword** tree; `P2` is an ordinary variable, so this seam never reaches the switch. Correctly untouched by this rung, and a clean one-rung follow-up. **Proposed as its own queue row.**

## 7. THE m3 (BINARY) HALF — 2360 PROGRAMS, ONE REAL MOVER, AND IT IS THE CURE

The `.s` sweep is a TEXT-medium instrument; it says nothing about mode-3. So the BINARY medium was measured directly and behaviourally: mode-3 stdout+rc hashed per program, every `.sno`/`.sc`/`.reb` in the tree (`programs/lon` excluded by construction), **no oracle and no gcc in the loop** — because arm-vs-arm delta is the question, and grading against ground truth is a different one.

| | rows | movers |
|---|---|---|
| OFF vs ON | 2360 | 36 raw |
| **OFF vs OFF (same arm, re-run) — the noise floor** | 2360 | **38** |
| **OFF vs ON, minus the noise floor** | 2360 | **1** |

The single surviving mover is `probe/cn/cn_const_compose_all.sno` — the cure. **Zero regressions in mode 3.** `cn_nest_alt_defer`, a `.s` mover, is *not* an m3 mover: its output is unchanged, exactly as its box-level analysis predicts (a defer replaced by the staged tree it was deferring to answers the same).

**The noise floor is stated, not assumed**, and it is a known class: 27 of the 38 are `benchmarks/snobol4*` programs that print wall-clock `ms:`/`iters:` lines (the scorecard carries a `norm=ms` rule for exactly this), 4 are `csnobol4-suite` file-I/O programs (`openi`, `openo2`), 5 are `gimpel` drivers, 1 is the `unary_not` program of §6(a), and 1 is a Rebus parser probe. A raw "36 movers" would have been a scary and entirely false number; the control is what makes the 1 real.

## 8. THE FLIP IS PROVEN TO BE THE ARM THAT WAS MEASURED

One character of behaviour at `src/lower/lower_snobol4.c:1327` — `(e && *e == '1') ? 1 : 0` → `(e && *e == '0') ? 0 : 1`, the house idiom already carried by `sn4_span_frame`, `sn4_pt_frame` and `sn4_xh_frame_extra`. **The killswitch stays: `SCRIP_CONST_NEST=0` reverts VERBATIM.** After the flip + `make pristine`, both directions were re-swept and joined row-for-row against the pre-flip pair:

| claim | list | movers |
|---|---|---|
| post-flip **DEFAULT** ≡ pre-flip **ARMED** | 1648 `.sno` | 0 (+`unary_not`, §6a) |
| post-flip **`=0`** ≡ pre-flip **DEFAULT** | 1648 `.sno` | 0 (+`unary_not`, §6a) |
| post-flip **DEFAULT** ≡ pre-flip **ARMED** | 488 `.sc`/`.reb` | **0** |
| post-flip **`=0`** ≡ pre-flip **DEFAULT** | 488 `.sc`/`.reb` | **0** |

and on the shipped binary the witness table is the arm table, in both media:

| witness | DEFAULT | `=0` |
|---|---|---|
| `cn_const_compose_all` | **PASS/PASS** | DIFF/DIFF |
| `cn_nest_alt_defer` · `cn_alt_leaf_flat_red` · `cn_alt_leaf_lit_red` · `cn_const_compose_ctl` | PASS/PASS | PASS/PASS |

**4 gates green** on the flipped build: `emit_no_lang` · `template_medium_invisible` (ceiling 0) · `icn_no_stack` · `icn_one_reg_frame`.

## 9. CORPUS NON-REGRESSION + RULES STEP-4 AS AN INDEPENDENT SECOND PATH

`test_corpus_snobol4.sh` at the flipped default **and** at `=0`:

```
mode-3 (--run):     PASS=332 FAIL=5
mode-4 (--compile): PASS=325 FAIL=11 SKIP=1  (337 total)
```

— the standing s183/s184/s185/s188 watermark **to the digit**, at both arms, with the **fail-set identical BY NAME** (`diff` of the two FAIL lists is empty). The cn probes are not members of this runner, which is why the cure shows in §7 and not here.

`lower_snobol4.c` is a named RULES step-4 codegen trigger, so all five regens ran in order. Every one reports **`changed=0`**: benchmark · feature · demo · programs (`emitted=623 changed=0 unchanged=623`) · prolog-bench (`emitted=22 changed=0`). A second, independently-implemented path to the same conclusion the `.s` sweep reached: outside the two `probe/cn` witnesses, this flip moves nothing.

## VERDICT

**CLEAN. FLIPPED.** `SCRIP_CONST_NEST` is default ON. One line of behaviour, killswitch intact and proven verbatim in both directions, 4 gates green, corpus watermark unchanged at both arms with the fail-set identical by name, and a total measured blast radius of **two programs** — one of which is a **silent wrong answer cured** and the other a defer-to-staged-tree substitution that shrinks the emission and changes no output.

**The methodological carry-forward, and it is the reason this row was worth a session:** the brief named an instrument (`0 movers / 527`) that could not see the rung, and the number it produced was clean, documented, and meaningless. A byte-identity sweep proves only what its *list* can express. For a rung whose reach is a **source construct** rather than a code path, the list must be built from the construct — here, every frontend that lowers through `lower_snobol4.c`, which is `.sc` and `.reb` as well as `.sno`, 2136 comparable programs instead of 527. **Sweep the construct, not the habit.**

## 10. RE-PROVEN AFTER THE REBASE — AND THE REBASE MOVED THE WATERMARK, BUT NOT BY MY HAND

The push rebased onto two commits that landed mid-session, one of them **codegen**: seat1's `408aab34` (scorecard/`util_ref_mint.sh`) and seat3's `ed61196c` **RTY-GAMMA-RETREAT, which edits `src/emitter/emit.cpp`**. RULES: re-prove the gate after a rebase — so `make pristine` ran again and every verdict number was re-earned on the shipped tree (`c512089a`).

| re-proof on the rebased tree | result |
|---|---|
| `.s` arm delta, 1648 `.sno` | **the same 2 movers** (`cn_const_compose_all`, `cn_nest_alt_defer`) + `unary_not` (§6a) |
| `.s` arm delta, 488 `.sc`/`.reb` | **0** |
| witnesses, both media | `cn_const_compose_all` DEFAULT **PASS/PASS** vs `=0` DIFF/DIFF; other three PASS/PASS at both arms |
| 4 gates | **green** |
| corpus, DEFAULT **and** `=0` | `m3 334/3 · m4 327/9 SKIP 1 (337)`, **fail-set identical BY NAME** |

⭐ **The corpus watermark IMPROVED — from `m3 332/5 · m4 325/11` to `m3 334/3 · m4 327/9` — and that is seat3's `ed61196c` cure, not this rung's.** It is recorded here because this is the tree the flip ships on, and stated plainly because a rung that quietly banked a neighbour's +2/+2 would be lying. **This flip is watermark-neutral:** its two arms are identical to each other in both modes with the fail-set identical by name, before and after the rebase. Step-4 regens re-ran on the final tree; the only artifacts that moved (`demo/calculator-1.s`, `demo/json.s`) are seat3's emit.cpp change and were already upstream when corpus rebased.
