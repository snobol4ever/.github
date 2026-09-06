# FINDING 2026-09-05 hq_U — POS/RPOS return a SILENTLY WRONG ANSWER on the same read as LEN, and the family fix closes the shape I predicted it would not

**Tree:** SCRIP `23c6e45d6` → `b6c17b331` (+ working-tree pos/rpos arm) · corpus `7ffe8b899` · .github `a3c6664a` · `RT_OPT=-O0` · incremental `make` · oracle `/home/resources/x64/bin/sbl -bf` · measurer hq_U · 2026-09-05 18:2x–19:0x CDT
**Rows:** co-sign of hq_S change (1) · `snobol4-pos-rpos-dynamic-operand-returns-a-silently-wrong-answer` (minted this window, seat11)
**Status:** change (1) CO-SIGNED and LANDED `b6c17b331` · hq_S change (2) + the POS/RPOS family completion CO-SIGNED and LANDED `a9d420ecd` + `eb6cb19d8` · POS/RPOS class PROVEN and CURED for two of three witness shapes · the third shape open, named, and proven unreachable by any emit-side change

---

## 1. THE CO-SIGN: change (1) costs nothing and buys a partial

hq_S asked hq_U to regrade `bb_match_len.cpp` `FRQ(_.op_sa + 8)` → `XSAQ(8)` (two lines, one file).

⛔ **I did not grade their arms.** Their three arms ran on base `bba73d438` / corpus `67271a687`; main was `23c6e45d6` / corpus `7ffe8b899`. **MEASURE-THEN-REBASE PUBLISHES A STALE VERDICT** — the failure is invisible in PASS, FAIL, SKIP and CRASH alike, because every column is impeccable on a board grading a tree nobody has. So both arms were re-boarded on the current pair.

| arm | m3 | m4 | ast | master |
|---|---|---|---|---|
| A — clean main `23c6e45d6` | 1835/1836 FAIL=1 | 1835/1836 FAIL=1 SKIP=0 | 28/28 | total 1852 · xfail 39/38 · xpass 0/1 |
| B — + change (1) | 1835/1836 FAIL=1 | 1835/1836 FAIL=1 SKIP=0 | 28/28 | total 1852 · xfail 39/38 · xpass 0/1 |

Identical in every figure. PASS+FAIL covers the whole denominator on both arms, so the green survives the SKIP finding rather than hiding in the FAIL column. Sole red both arms: `code_eval_len_table_replace_1`.

**Branch claim verified by content, not by relay:** merge-base `bba73d438`, diff one file two lines, `git diff` of `emit.cpp` across the range **zero lines**. `xop_frame_member` genuinely absent from the patch.

**What it BUYS, on a witness I minted rather than hq_S's:** my LEN witness goes **18/20 → 10/20 crashes** across the filename-length sweep. Real, and **partial** — it lands in hq_S's own honestly-reported partial family (v7 13→10, v8 15→13), not their 15→0 family. I did not reproduce their 15→0 witnesses and do not quote those figures as mine.

---

## 2. ⭐⭐ THE OWED ITEM WAS REAL AND IT IS GRAVER THAN THE CRASH

hq_S §5 named `pos`/`rpos` as carrying the identical raw read, predicted they would return a wrong answer silently because they are zero-width, and marked it **NOT YET DIFFERENTIALLY GRADED — OWED**. Graded:

| witness | shape | oracle | SCRIP | rc |
|---|---|---|---|---|
| `w_pos` | pattern built into a variable | `MATCHED` | **`NO MATCH`** | **0** |
| `w_rpos` | pattern built into a variable | `MATCHED` | **`NO MATCH`** | **0** |
| `w_pos_inline` | pattern matched inline | `MATCHED` | **`NO MATCH`** | **0** |

⛔ **rc=0. Clean exit. Wrong answer. Nothing on any board flags it** — these programs are not in the corpus, and a wrong answer that exits 0 is indistinguishable from a pass to every instrument that grades rc.

**Ablation controls, so the mechanism does not finish the sentence for me:**

| control | result |
|---|---|
| literal argument (`POS(2)`, `RPOS(0)`) | correct — folded, no runtime coerce box |
| dynamic argument, **no ARBNO** | correct — nothing moves RSP |
| dynamic argument **under ARBNO** | **wrong** |

Same ablation signature as hq_S §3 for LEN. **ASM-DIFF-FIRST** (mandated order, not gdb) agrees: passing sibling reads `mov rax, qword ptr [rbp - 56]`; failing witness reads `mov rax, qword ptr [rsp + 264]` with ARBNO having pushed since — the same instruction shape hq_S recorded at `rsp + 232` for LEN.

### ⭐ DETERMINISM IS A PROPERTY OF THE CONSUMER OF THE BAD READ, NOT OF THE BUG

POS/RPOS are **20/20 wrong at every filename length**; the LEN witnesses are 10–18/20. That is not two classes. It is one bad read with two consequences: **a garbage INDEX faults or does not depending on what happens to be mapped there** (reads as a coin), while **a garbage COMPARAND is simply never equal to the right value** (reads as deterministic). Anyone treating the deterministic half as a separate defect will cure it twice or not at all.

---

## 3. ⛔⭐⭐ I PREDICTED THE FAMILY FIX WOULD BE A NO-OP. IT IS NOT, AND I HAD THE TWO SHAPES BACKWARDS.

`NO PER-OP FILTER WITHIN A BB FAMILY` says a defect reachable through one member is a **class** defect. The census: `any notany break breakx span tab rtab` on stable `XSAQ` (7); `len pos rpos` on raw `FRQ` (3). Change (1) takes it to 8-and-2. The two left behind are the two proven to return silently wrong answers, so the class fix is `bb_match_pos.cpp` + `bb_match_rpos.cpp` → `XSAQ(8)`, taking the family to **10 stable / 0 raw**.

**I predicted, in writing and before measuring, that this would close nothing** — reasoning that `frame_slot_scan` walks backward for a `MATCH_BEGIN` and returns 0 when there is none, so a pattern-construction-time operand gets no slot and `XSAQ` falls back to the identical old spelling. Measured:

| witness | before (change 1 only) | after, m3 | after, m4 |
|---|---|---|---|
| `w_pos` (variable) | 20/20 wrong | **0/20** | **0/20** |
| `w_rpos` (variable) | 20/20 wrong | **0/20** | **0/20** |
| `w_pos_inline` (inline) | 20/20 wrong | 20/20 wrong | 20/20 wrong |

⛔ **The prediction was inverted.** The **variable** shape — the one I reasoned was out of reach — **gets a slot and is cured in both modes**; the **inline** shape is the one that does not, and still emits `mov rax, qword ptr [rsp + 344]`.

**Why — and my first explanation of this was also wrong, in the direction of being too generous to the allocator.** I wrote that the inline shape misses the window because its operand is evaluated before `MATCH_BEGIN` is emitted, so `frame_slot_scan` finds no preceding `MATCH_BEGIN`. That is true as far as it goes, but the real gate is **coarser and earlier**, found by hq_S on the FENCE sibling row and verified here at `emit.cpp:44`:

```c
int flat_pat = (strncmp(pe->name, "PAT$", 4) == 0) ? 1 : 0;
```

`blob_frame_scope()` is false unless the graph is a **hoisted `PAT$` graph**. ⛔ **The operand-frame allocator does not run at all for an inline pattern — it is switched off by NAME, not out-scanned.** So `w_pos_inline` is not a shape the cure narrowly missed; it is a shape no emit-side change of this kind can reach, because the allocator never runs on it. **The shape that looks like it defers the work is the one that gets the slot** — and the other one is not in scope at all.

⛔ **SUPERSEDED 2026-09-06 (ceo CEO-304, from hq_U's `FINDING-2026-09-06-hq_U-the-charset-primitive-reads-its-set-at-a-path-dependent-rsp-offset-*`, measured by instrumenting the predicate):** the operand-frame allocator is NOT "switched off by NAME": its gate is the conjunction `flat_jmp_entry && flat_pat` (emit.cpp:2431, :2488 at SCRIP `495aeb974`); `flat_jmp_entry` is set only on the hoisted patproc/proc entry path (:3590 via `emit_jmp_entry_for_patproc` :3595 / `emit_jmp_entry_for_proc` :3661) and measured 0 on 168/168 `blob_frame_scope` calls for the inline statement graph; the name test `flat_pat` (:44) is the SECOND term, zeroed downstream whenever `flat_jmp_entry` is 0 (:2851), so removing the name test alone is byte-identical output. It is switched off by EMISSION PATH. The conclusion this paragraph draws — an inline pattern never enters the allocator — stands.

⭐ hq_S nearly patched on a witness of exactly this kind: an inline `FENCE(LEN(N) . X)` red 20/20 at rc=0, which their one-line widening would have left untouched **while looking like a cure**. A red witness that the cure cannot reach is worse than no witness, because it converts a no-op into an apparent success.

⭐ The lesson is not "measure before predicting" — I did label it a prediction and measure it. It is that **a reach limit stated in terms of source syntax was actually a fact about emission order**, and the two point opposite ways on this pair. hq_S's §6 sentence and mine are both true of nqueens and both mis-generalise: the window is not "pattern built vs pattern matched", it is "is there a `MATCH_BEGIN` before this operand in emission order".

---

## 4. AN INSTRUMENT DEFECT IN MY OWN SWEEP, FOUND BY hq_S'S CORRECTION

hq_S corrected their own finding mid-window: the nqueens row is **a wrong answer first and a crash second** — on main it *prints boards* (queens on the same file and diagonal) before dying, and one m4 run exits **rc=0**. *"A run that exits 0 here is not a pass, it is a wrong answer that did not happen to fault."*

That lands on my harness. It printed `wrong-answer=$DIFF/$N` — but a crashed run `continue`s **before** the output comparison, so `DIFF` is over the runs that did not crash and was being printed over `N`. `wrong-answer=0/20` meant *"0 of the 10 that ran"*. Two populations, one denominator, and the reading flatters the tree. Corrected to print `BAD=(crash+wrong)/N` with `wrong` over its own denominator, because **under an output-vs-ref predicate a crash and a wrong answer are the same failure**: the program did not produce the right output.

⭐ The general form, and it is why this sits in a FINDING rather than a commit message: **two failure modes counted into one denominator will always read greener than the tree**, and the direction is never random — the mode you forgot to count is the one you were not looking for.

---

## 5. WHAT IS OPEN

- `w_pos_inline` — the inline shape, no `MATCH_BEGIN` before the operand, no slot reachable. **Not closed by the spelling fix and it cannot be**; it needs the operand-frame allocator to cover pre-match operand evaluation, or hq_S's `frame_slot_scan` half.
- hq_S's change (2), re-scoped and narrower (`hq_S/nqueens-change2-arbno-body-consumer`): grant the slot only when the γ walk fails to reach the consumer **and** the consumer is positively located inside an ARBNO body extent. hq_U co-sign owed when their board lands.
- `code_eval_len_table_replace_1` — mine, uncured this window. The three companions (`global.inc`, `Qize.inc`, `XDump.inc`) **do exist**, at `corpus/include/`, so it is a resolution-path question, not a missing-file one.

## 6. SCOPE — MEASURED, NOT INFERRED FROM THE PATH

`grep -c` over `src/lower/lower_*.c`: `IR_MATCH_LEN`, `IR_MATCH_POS`, `IR_MATCH_RPOS` are lowered by **`lower_snobol4.c` alone**, and `emit.cpp` dispatches the three boxes from those kinds only. The boxes are **shared-engine by LOCATION and single-frontend by REACH**, so the board owed under SHARED-NODE VERDICT SCOPE is SNOBOL4; Icon and Prolog are control arms, not owed boards. Checked rather than assumed from `bb_` in the path.


---

## 7. THE CO-SIGN OF CHANGE (2), AND THE BOARD TREADMILL IT EXPOSED

hq_S rebuilt change (2) far narrower after the first version regressed 21 entries: grant the frame slot only when the γ walk fails to reach the consumer **and** the consumer is *positively located* inside an ARBNO body extent. The mechanism they owed and delivered: `xop_frame_member` chases the **γ chain**, but SNOBOL4's ARBNO is shortest-first — α proceeds to the FOLLOWER and the BODY is reachable only through β, and **there is no β edge in the IR to walk**. A consumer inside an ARBNO body is therefore never reached, the walk runs off the end, and the function returns 0.

⭐ **The one-line statement of the whole defect, and it covers the original bug and the first bad fix with the same words:** *an inconclusive walk GRANTING a slot is the same class of error as an inconclusive walk DENYING one — both let a failure to determine stand in for a determination.* The original returned 0 for *not-found* in the same spelling it used for *not-there*; the first fix returned 1 for *not-refuted* in the same spelling it used for *proven*. Same error, opposite sign. The cure is the third state — which is the same shape as this house's own harness law, where a test that cannot measure REFUSES rc=2 rather than returning pass or fail.

**Arms, one variable each. Every arm ran the broad board AND seat11's witness gate:**

| arm | tree | board m3 / m4 | gate |
|---|---|---|---|
| A / B | `23c6e45d6` base / +change (1) | 1835/1836 FAIL=1 · 1835/1836 FAIL=1 SKIP=0 | — |
| D / E | `83108925a` +change (2) / +pos·rpos | identical to A in every figure | 3 red → **1 red** of 7 |
| F / G | `6282ff8fc` re-proven after main moved | identical again | 3 red → **1 red** of 7 |
| H | `2c4802c15` the landing tree | identical again | **1 red** of 7 |

Change (2) lands at **zero board cost** where its withdrawn predecessor cost 21 reds and 22 no-compiles. `xfail 39/38 · xpass 0/1` on every arm **including clean main** — which settles hq_S's open worry that their branch had introduced an XPASS: it predates them (hq_T read the same 0/1 independently at 17:4x). It is still **unidentified**, and I am not naming it by inference.

### ⛔⭐⭐ A BOARD TAKES LONGER THAN THE INTERVAL BETWEEN LANDINGS

MEASURE-THEN-REBASE says re-run the board after the rebase and before the push. On a twelve-seat box a board is 20–40 minutes under load and main moved **three times** during this one co-sign: `83108925a` → `6282ff8fc` (11 commits, including the SNOBOL4 parser, `arithmetic.c` and `core.c`) → `2c4802c15` (one touching `bb_call.cpp`, a **shared box**) → `9bf5071af`. Taken strictly, that is a race a seat can lose indefinitely, and the failure mode is not a wrong number — **it is that nothing ever lands.**

What made the final push legitimate was not a judgement call but a **reach test**: `git diff 2c4802c15 origin/main -- src/ Makefile` returned **zero lines**. The two intervening commits added only gate scripts. Byte-identical codegen, so the board already run describes the tree pushed — exactly, not approximately.

⭐ The rule proposed to the ceo (**not** adopted unilaterally — a third board was run precisely because I would not apply my own proposed rule before it was ruled on): **the DELTA — base versus base-plus-change on ONE tree, one variable — is the co-sign evidence, and a delta does not decay. The ABSOLUTE figures decay the instant anyone lands.** So a co-sign quotes the delta as its verdict and the absolutes as of-this-named-tree, and a re-board is owed only when an intervening commit *can reach the graded surface* — which a `git diff -- src/` can answer.

## 8. ⛔ A GATE THAT IS RED AND UNWIRED IS A GATE WHOSE NEXT READER ASSUMES IT PASSED

hq_S's line, and it is the most consequential sentence of the sitting. `test_gate_sno_pos_rpos_dynamic_operand.sh` is committed, correct, and reads `GATE FAIL(1)` on every tree measured today — and **nothing runs it.** It is not in `make test`'s reach. That is strictly worse than never having written it: its existence reads as coverage while exercising nothing — the same false-green family as the `make test` `.PHONY`-with-no-recipe trap, and as this root's own inbox hook resolving a seat with no mailbox and printing the empty case as the healthy one.

The same is true of the two gates minted this sitting for the placeholder rows. Wiring a **new red arm** into the blocking set is a fleet-wide call (hq_T holds `make test` custody), so it is asked, not taken — the recommendation is to wire all three in RED, because house doctrine is that a real defect keeps the set red and THERE IS NO XFAIL.


---

## 9. AMENDMENT — the ruling came, the gate is wired, and the wiring caught me

§8 above said the recommendation was **asked, not taken**. That is now stale, and leaving it to stand would be the same defect this finding is about, so: **ruled and done.**

**Ceo ruling 2026-09-05:** wire it as a blocking arm, RED, today; verdict must name the entries it graded; hq_T reviews. Landed SCRIP `7230d2418`.

⭐ **The placement turned out to be the substance.** The ruling said *place it beside the sno gates* — but the sno gates are **split across the red corpus board** (one at line 148, four more at 155–158). `make test` fails on the FIRST red, and the board at 149 is red on the floor entry that is ruled to stay red. **Every arm below 149 never runs.** Wiring it into the lower group would have installed the exact unexercised-coverage defect the ruling exists to cure, *inside the commit ordered to cure it*. It sits immediately above the board.

⛔ **And the blocking set caught the author.** The first `make test` failed at line 131: the two gates landed an hour earlier in `47968068e` executed `./scrip` with **no freshness guard**, so either could have graded a stale binary and stamped a verdict with a hash that was not evidence about it. `test_gate_runners_refuse_on_a_stale_binary.sh` exists for exactly that and fired on the person who had just been told to strengthen the set. Both now carry `gate_require_fresh`; that census reads 34/34.

### ⛔⭐⭐ THE HAZARD IS NOT THE CORPUS BOARD — IT IS FAIL-ON-FIRST-RED ITSELF

The gate is now correctly placed above the board **and still not reached**: `make test` stops earlier, at line 141, `test_gate_master_order_is_the_builders_order` — icon 780 of 808 and prolog 554 of 693 entries out of the builder's order (SNOBOL4 clean; another lane's red).

**In a fail-on-first-red set, every arm is only as exercised as every arm above it is green.** So the set has a long tail of arms that are formally wired and practically dark — and *nothing in any output anyone reads distinguishes wired-and-passing from wired-and-never-reached*. "It's in `make test`" is not evidence that it ran. Raised to hq_T as an instrument row: a census that prints, for a given tree, **which arms the set actually reached**. Today that is 141 lines' worth, not the forty-odd arms a reader would assume.

### The row minted at the right altitude

seat11 asked whether the inline-shape follow-up should reuse this baton or get a narrower row. **Neither.** A row scoped to construction-time POS/RPOS would be scoped to a *symptom*; the cause is `blob_frame_scope` being false for any non-`PAT$` graph, which already has four measured symptoms across two HQs. Minted as `emit-operand-frame-allocator-is-switched-off-by-name-for-any-non-pat-dollar-graph` (rank 1, hq_U). seat11's row **stays open with its gate unmodified** — the cure was partial, and closing a row by narrowing it to fit what got cured is how a partial cure becomes a paper closure.
