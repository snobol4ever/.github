# FINDING s187 (seat8 `/home/claude8`, Claude Opus 5; queue row 0 `arbno-tail-false-accept`) — THE CAMPAIGN'S ONLY FALSE ACCEPT IS ONE MIS-AIMED EDGE: AN ELEMENT'S RESUME SURFACE WAS ITS **FIRST** BOX, NOT ITS **LAST**

**WATERMARK:** `make pristine` at SCRIP `213771e2` + this patch, RT_OPT `-O0`, corpus `66259281`, oracle verified alive before every verdict.
**LANDED:** one line + one killswitch in `src/lower/lower_snobol4.c` (`sno_seq_tail()` / `SCRIP_SEQ_TAIL`, default ON). **BOTH reds oracle-identical in BOTH modes.** Pass-thru board **m3 147→151 · m4 133→137**, zero movers the other way, movers identical by name in both modes.

## 1. THE MANUAL IS THE AUTHORITY — WHAT SPITBOL REQUIRES

**SPITBOL manual v3.7, Tutorial, "The ARBNO Function", p.121, verbatim:**
> *"Like the ARB pattern, ARBNO is shy, and tries to match the shortest possible string. Initially, it simply matches the null string. If a subsequent pattern component fails to match, SPITBOL backs up, and asks ARBNO to try again. Each time ARBNO is retried, it supplies another instance of its argument pattern. In other words, ARBNO(PAT) behaves like ( "" | PAT | PAT PAT | PAT PAT PAT | … )"*

and the reference entry, p.212:
> *"ARBNO matches the shortest string possible—initially the null string—and only tries to match pattern if other pattern components in the statement require it."*

**The law this states, and the one the defect breaks:** the alternation is over **instance COUNT**, and every alternative starts at **the same cursor** — instance k+1 begins where instance k began, because `PAT PAT` is one alternative of the disjunction, not a continuation of another. A retry is therefore only legal after the subsequent components that ran on the previous alternative have **reversed their own cursor advance**. Exhaustion (no further alternative) is a plain match failure: ARBNO concedes and the statement fails. There is no arm on which exhaustion reports success.

## 2. ROOT CAUSE — ONE LINE, `sno_seq_nary` (`src/lower/lower_snobol4.c`)

`sno_seq_nary` wires a concatenation: *σ (rightward success) → next element's α; φ (leftward fail) → previous element's β.* It records each element's **resume surface** in `res[i]`, and `res[i-1]` is what element *i*'s ω/β edge aims at. That surface was computed as:

```c
IR_t * ri = (_rb < g->n) ? g->all[_rb] : ei;    /* first-allocated node of the element */
```

— the element's **HEAD**. The correct surface is the element's **rightmost box**: the box that ran last, that holds the most recent choice point, and whose β owes the cursor undo. `sno_seq_nary` already knows this about its own *callers* — `out_rtail` exists precisely to hand a run's `res[ne-1]` (its LAST element) to a righter fence — but inside its own loop it took the head of every element.

**Latent until PAT-INLINE.** While every element was a single box, head == tail and the aim was accidentally right. **PAT-INLINE (Lon 2026-08-09, `SCRIP_PAT_INLINE`)** made a bare stored-pattern reference lower its whole stored tree **inline as ONE element** (`case TT_VAR` / `case TT_DEFER` → `return sno_pat_node(cx, p, succ, fail)`), which is exactly a multi-box element. From that day, **every element to the right of a stored pattern reference receded into that pattern's FIRST box and skipped the β of every interior box with it** — both the interior CHOICE POINTS and, for the class-0 leaves whose β *"reverses arithmetically"* (`ARCH-PASSTHRU` RESULT GRID), the interior CURSOR UNDO.

**THE FIX (one line):** the element's tail is already computed by the loop that follows — it is the node whose γ this very loop tags **σ** (rightward success exits the element). Take the last such node:
```c
if (sno_seq_tail() && ti) ri = ti;
```
A single-box element has `ti` == the head, so the entire pre-PAT-INLINE corpus is byte-identical by construction. `SCRIP_SEQ_TAIL=0` restores the head aim verbatim.

## 3. THE MEASUREMENT THAT NAMED IT — AND WHY IT LOOKED LIKE AN "ARBNO EXHAUSTION" BUG

`E = ARBNO('a') LEN(1)` / `POS(0) E RPOS(0)`; subject = *k* `a`'s then one `X`, so the oracle **matches every row** at exactly *k* instances:

| k | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| oracle | match | match | match | match | match | match | match | match |
| SCRIP (stored) | match | **NO** | match | **NO** | match | **NO** | match | **NO** |
| SCRIP (**inline**, same pattern) | match | match | match | match | match | match | match | match |

⭐ **The "even instance counts only" reading is WRONG and would have sent a seat into `bb_match_arbno.cpp`.** ARBNO is not skipping alternatives: `LEN(1)`'s β never runs, so its one consumed character is never given back, and ARBNO's β resumes **one character past its own yield**. Each retry advances **two** — one un-undone tail char plus one new body instance. Every row above follows arithmetically, and so does the false accept: on `'aa+aa'` the reachable cursors are 0→1→2→3→4→5, so ARBNO "matches" the `a` at index 1 and the `a` at index 3 while `LEN(1)` eats indices 0, 2 and 4 — `RPOS(0)` is reached and **SCRIP declares a match the oracle refuses**. ⛔ **Nothing in `bb_match_arbno.cpp` is implicated. The IR arrives at the emitter already mis-wired**; `SCRIP_OPT=0` reproduces it identically, so it is the LOWERER, not the optimizer.

**The IR, measured, with the aligned inline sibling as the control** (`--dump-ir`, γ/ω columns):

| | inline (GREEN) | stored (RED) |
|---|---|---|
| MATCH_ARBNO | γ=LEN ω=POS | γ=LEN ω=POS |
| MATCH_LEN | γ=RPOS ω=ARBNO | γ=RPOS ω=ARBNO |
| **MATCH_RPOS** | γ=END **ω=LEN** ✅ | γ=END **ω=ARBNO** ⛔ |

Scaled, it is unmistakable — for **every** stored pattern the following element's ω lands on slot 12, the splice HEAD, however many boxes the pattern has: `ARBNO LEN` → 12 (want 13) · `LEN LEN` → 12 (want 13) · `ARBNO LEN LEN` → 12 (want 14) · `LEN ARBNO` → 12 (want 13) · `LEN LEN LEN` → 12 (want 14) · `ARBNO` alone → 12 (**want 12 — correct only because head == tail**). The inline control aims at the tail in every one of those shapes.

## 4. ⛔ THE TWO REDS ARE **ONE** MECHANISM — AND SO ARE TWO OF THE FOUR "CONTROLS"

The row asked: *fix together or explain why they are two mechanisms.* **One mechanism, one line, both directions.**
- **False ACCEPT** — a skipped **cursor undo** (`LEN`'s β): the retry resumes at the wrong cursor and reaches a position the pattern cannot legally reach.
- **False REJECT** — a skipped **choice point** (`ptw_min_nullalt_retreat_falsereject`, `E = ANY('ab') (LEN(1) | '')` matched `*E 'b'`): the ALTERNATE is the element **TAIL**, so the following literal's ω lands on `ANY` (the head) and the ALT's β — the untried null arm — is never entered.

⛔ **AND THE CONTROL SET DOES NOT ISOLATE WHAT IT CLAIMS TO.** Measured at the IR, **three of the four "green controls" carry the identical mis-wire and are green only by luck**:
- `ptw_min_arbno_tail_ctl_span` (`SPAN('ab') LEN(1)`): RPOS ω = SPAN (head), want LEN ⛔ **mis-wired**; green because SPAN never retries, so both aims concede.
- `ptw_min_nullalt_retreat_ctl` (`LEN(1) | 'z'`): literal's ω = ANY (head), want ALT ⛔ **mis-wired**; green because the answer is `nomatch` on either aim.
- `ptw_min_arbno_tail_ctl_notail` (`ARBNO(ANY('ab'))`): a **single-box** splice, head == tail — the only one **structurally immune**.

So the row's stated trigger — *"ARBNO must EXHAUST its alternatives against a FOLLOWING element"* — is a faithful description of the **symptom** and a false description of the **mechanism**: it names ARBNO, and ARBNO is not load-bearing (`LEN(1) LEN(1)` and `ANY('ab') (LEN|'')` are mis-wired with no ARBNO anywhere). **A control that is green for the wrong reason licenses exactly the wrong hunt.**

## 5. BISECT AND KILLSWITCH

`SCRIP_PAT_INLINE=0` turns **both reds green and leaves all four controls green** — the defect lives entirely on the PAT-INLINE road. That is a bisect, **not the fix**: it buys correctness by giving up the inline pass-thru and routing back through `IR_MATCH_DEFER`. The fix keeps PAT-INLINE and aims the edge correctly.

## 6. BOARDS — MEASURED, NOT ASSERTED (pristine, RT_OPT `-O0`, every arm A/B'd against `SCRIP_SEQ_TAIL=0` on the SAME binary)

| board | `=0` (legacy) | default (fix) | movers |
|---|---|---|---|
| **pass-thru combo m3** | 147/164 | **151/164** | **+4, none the other way** |
| **pass-thru combo m4** | 133/164 | **137/164** | **+4, none the other way** |
| corpus `test_corpus_snobol4.sh` | m3 332/5 · m4 325/11 SKIP 1 (337) | **identical** | fail-set identical **by name** |
| crosscheck `test_crosscheck_snobol4.sh` | m3 312/5 · m4 308/8 SKIP 1 DIVERGE 3 | **identical** | fail-set identical **by name** |
| `board_patterns_2mode` | 122 · AGREE 116 · m4-only 3 · both-fail 3 | **identical** | — |
| `board_earn0_set` | — | **identical** | — |

The four repaired rows are the same four in **both** modes (m3 ≡ m4 preserved): `ptw_min_arbno_tail_falseaccept` · `ptw_min_arbno_tail_falseaccept_nodefer` · `ptw_min_nullalt_retreat_falsereject` · ⭐ **`ptw_min_arbno_nullalt_falseaccept`** — the row's own ANCESTOR witness, HQ's original `arbno-nullalt-false-accept` filing, which the brief no longer named. It falls to the same line.

**⛔ KILLSWITCH INERTNESS, PROVEN NOT ASSERTED — and the first proof was INVALID.** `SCRIP_SEQ_TAIL=0` vs the **pre-patch binary** over the same 1549 programs: **0 real movers** (raw 1, the `unary_not` bomb stub above, exonerated by the control arm's own self-diff). ⛔ The first run of this proof reported 14 movers and was **wrong**: `scrip` carries `DT_RUNPATH /home/claude8/SCRIP/out`, and `lower_snobol4.c` is compiled into `libscrip_rt.so` as well as the driver — so the saved pre-patch binary silently loaded the **patched** `.so` and the "base" arm was the fix. Cured by pairing each binary with its own `.so` under `LD_LIBRARY_PATH` (the `bench_rtx_3arm.sh` precedent) and **smoke-testing the pairing first**: the base pair must print the OLD wrong answer `match` on the witness before its numbers mean anything. ⭐ **A saved binary is not a saved compiler in this tree.** Recorded because it would have shipped a false "the killswitch is not inert" verdict.

**Regression set held:** all four controls green both modes; **61/61** minted probes green (the full 0–7 instance ladder, 14 subject variants, 9 tail variants, and the inline / stored-`E` / deferred-`*E` roads); all six `.ref` files re-verified against the live oracle before and after, **zero drift**.

**⭐ BLAST RADIUS, SWEPT NOT ESTIMATED — 13 real movers / 1549 comparable `.s` (0.8%).** 8 are the `probe/passthru` witness family itself. ⛔ The raw sweep said 14; the 14th, `programs/snobol4/parser/unary_not.sno`, is **NOT a mover** — the same binary self-diffs to a different md5 on every run (the differing line is one bomb-stub `.string` carrying raw address bytes), proven by self-diffing the control arm alone: 3 runs, 3 md5s. The other four named movers self-diff **STABLE** across repeated runs, so they are real. Each was verified by hand: `benchmarks/.../porter.sno` (`check: 139812` — **identical to its `.ref` and to the live oracle on both arms**; only its `.s` moved) · `crosscheck/strings/word3.sno` + `word4.sno` (**MATCH vs `.ref` on both arms, both modes, and the oracle agrees** — and `word3` is the very witness `sno_seq_nary`'s own s8 GROUP-TRANSPARENT-SEQ comment cites) · `probe/cn/cn_const_compose_all.sno` and `programs/snobol4/parser/unary_not.sno` (**pre-existing reds, byte-identical stdout on both arms** — unmoved; `unary_not` is s186 batch A's `~`-has-no-template class, `cn_const_compose_all` the live oracle cannot even load, `ERROR 251`).
⛔ `corpus/programs/lon/` was **excluded from every sweep by an explicit path guard** (99 programs), per RULES.md — never compiled, never run.

## 6b. ⛔ STEP-4 REGEN — RUN IN FULL, AND ONE OF ITS TWO RESULTS IS **NOT MINE**

All five RULES step-4 regens ran in order. ⛔ **None of them can reach `corpus/programs/lon/`** — checked before running, not assumed: benchmark→`benchmarks/snobol*`, feature→`lib`, demo→`programs/snobol4/demo` (a fixed DEMOS list), programs→`icon prolog rebus` only, prolog-bench→prolog.
**MINE:** the FEATURE tree — `test/snobol4/strings/word3.s` + `word4.s` (SCRIP `0b47b175`), both still matching their `.ref` against the live oracle in both modes.
⛔ **NOT MINE, and it would have been credited to this rung:** the DEMO regen moved `claws5-match.s` and `json.s`, which are **byte-identical between `SCRIP_SEQ_TAIL=1` and `=0` on the same binary** — accumulated, un-regenerated drift from the s188 landings this seat rebased onto (seat7 `d3251f23` SPAN-FRAME FLIP, seat2 `9d811427` ARB-IMMED-ASSIGN-RETRY). ⭐ **A regen commits whatever moved since the LAST regen, not what your rung moved — so A/B every regen output against your own killswitch before letting your rung's name sit on it.** (The corpus commit carrying this note was dropped as a duplicate cherry-pick — another seat pushed the identical bytes as `42530cb0` — so the attribution lives here.)
**INDEPENDENT CONFIRMATION the change is SNOBOL4-lowerer-local:** the icon/prolog/rebus regen reports `emitted=623 changed=0`, and the prolog bench regen `emitted=22 changed=0`.

## 6c. RE-PROVED AFTER THE HANDOFF REBASE, NOT ASSUMED

The pull brought in two live compiler landings (seat7 `d3251f23`, seat2 `9d811427` — the latter in this very neighbourhood: *"a stored pattern carrying `$` published a wholesale blob concede"*), so every number was re-measured after a second `make pristine` at SCRIP `a2979dc6`: corpus **m3 332/5 · m4 325/11 SKIP 1** and crosscheck **m3 312/5 · m4 308/8 DIVERGE 3** unchanged; pass-thru **m3 148→152 · m4 134→138** — still exactly **+4 in each mode attributable to this line** at the rebased HEAD (the absolute totals rose by one because the other seats' landings repaired a row of their own).

## 7. ⛔ THE SAME SHAPE AT A SECOND SITE — NAMED, MEASURED, **NOT** FIXED HERE (routing, with its price)

`case TT_ALT` (same file, ~line 1797) computes each **arm's** resume surface the identical way — `IR_t * ri = (before < g->n) ? g->all[before] : ei;` — and pushes it as the ALT's per-arm operand. A **multi-box arm** therefore publishes its HEAD as its resume surface, exactly as the SEQ site did. **The standing witness is already on the board: `160_pat_alt_inner_gen_resume`, `'aXb' ? ('a' ARB . V | 'q') 'b'`** — an ALT whose first arm is a multi-box sequence with a generator inside it; oracle `V=[X]`, SCRIP **SIGSEGV**, unmoved by this rung. Likely siblings from the same board: `145_pat_left_assoc_via_arbno_fence`, `ptx_shift_alt_arms{,_2layer}`, `ptw_min_fence_left_altresume`.
**Why it is not in this rung:** different site, **different consumer** (the ALT template's per-arm dispatch, not the SEQ φ→β edge), and its witness is a **crash**, not a wrong answer — so it needs its own witness ladder and its own A/B against a 137-row pass-thru board rather than a drive-by widening of a rung whose two reds are already closed. Routed as `alt-arm-resume-surface`; the price is one line plus that board.

## 8. FOR THE NEXT SEAT

⭐ **A resume/β edge that aims at a construct's HEAD is a defect the moment any element stops being one box.** The head-vs-tail question is now live at every site that publishes a "resume surface"; this rung fixed the SEQ site, §7 names the ALT site, and both were written the same way by the same reflex (`g->all[before]`). Grep for `g->all[before]` before trusting any other one.
⭐ **A green control is not evidence until its wiring is read.** Three of this row's four controls carry the defect and pass anyway; had the trigger been inferred from the control table alone, the hunt goes to `bb_match_arbno.cpp` and finds nothing there, because there is nothing there.
⭐ **`$` immediate assignment is NOT a safe instrument on this class** — inserting `ARBNO('a') $ A LEN(1) $ B` changes the verdict on subjects that were previously right (`aaX` goes from correct-match to nomatch, `lastA` empty on every subject). It perturbs the very wiring under test; the ablation ladder + `--dump-ir` γ/ω columns are the honest instruments, and they are what named this in minutes.
