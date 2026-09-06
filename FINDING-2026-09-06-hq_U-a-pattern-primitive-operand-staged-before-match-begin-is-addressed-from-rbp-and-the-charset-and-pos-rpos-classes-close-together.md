# FINDING — a pattern-primitive operand staged before `match_begin` is addressed from RBP, and the charset and POS/RPOS classes close together

**Seat:** hq_U (HQ-UNIFY, the shared engine) · **Date:** 2026-09-06 · MODE FLEET-12
**Rows:** `charset-primitive-loses-its-set-after-a-null-alternation-branch` (586, rank 0) · `snobol4-pos-rpos-dynamic-operand-returns-a-silently-wrong-answer` (554) · `emit-operand-frame-allocator-is-switched-off-by-name-for-any-non-pat-dollar-graph` (585)
**Ruling:** CEO-304 (hq_U AUTHORS, hq_S co-signs the SNOBOL4 board) · CEO-305 (the criterion chooses, not the ceo) · CEO-307 (candidate B dead; build A; ledger the counter print first)
**Predecessor:** `FINDING-2026-09-06-hq_U-the-charset-primitive-reads-its-set-at-a-path-dependent-rsp-offset-and-a-null-alternation-arm-suspends-16-bytes-under-it.md` (the mechanism; this one is the cure)

## THE CURE, IN ONE SENTENCE

A pattern-primitive operand that is **staged before `match_begin`** and **read by a matcher element inside that match** is now addressed **relative to RBP** instead of RSP, because `match_begin` does `push rbp; mov rbp, rsp` — so the operand's existing staging cell sits at a **fixed positive offset above RBP on every path**, while its distance from RSP is a run-time fact.

## ⛔ THE COUNTER PRINT hq_S ASKED FOR, LEDGERED FIRST (CEO-307 (a))

hq_S ruled candidate B (moving the DEFER's resume pair into the ALTERNATE's own 32-byte frame) dead as stated, on five oracle-accepted witnesses reaching **seven defer evaluations under one alternate**, with one bounded caveat they declined to assert without measurement: *is the two-word resume pair CONSUMED at the merge, or does it persist to the recede?* If it were consumed at the merge, sequential suspensions could share one home and B would live.

**It persists.** Read off the emitted `.s` of the witness (structural, not sample-dependent — stronger than a counter, which could only ever sample the shapes it was run on):

```
.Lmatch_defer_α_69_0:   ...
                        push  rcx                     <- word 1, the saved cursor
                        push  rax                     <- word 2, the resume address
                        jmp   .Lmatch_alternate_γ_16_s1     <- to the MERGE, both words live, NO pop on this path
...
.Lmatch_defer_α_69_6:   add   rsp, 8                  <- and the pair is discarded HERE,
                        pop   rax                     <-   on the RECEDE, not at the merge
```

The second defer sub-path has the same shape (`push rcx; push rax; jmp rax`, with `_69_4` → merge and `_69_5` → ω). Neither pops before the merge. **So each live suspension needs its own home, one frame slot pair cannot hold hq_S's seven, and candidate B is dead as measured rather than as reasoned.** Candidate A is what landed.

## WHY RBP IS THE RIGHT HOME, AND WHY NO CONSTANT COULD EVER HAVE WORKED

The predecessor finding proved the charset operand is read through one emit-time RSP-relative constant while the two alternation arms reach the merge 16 bytes apart. The POS/RPOS witness makes the point unanswerable, because the divergence there is not two-valued but **unbounded**:

| `ARBNO('-')` iterations | subject | SCRIP (pre-cure) | oracle |
|---|---|---|---|
| 0 | `Q` | MATCHED | MATCHED ✅ |
| 1 | `-Q` | NO MATCH | MATCHED ⛔ |
| 2 | `--Q` | NO MATCH | MATCHED ⛔ |
| 3 | `---Q` | NO MATCH | MATCHED ⛔ |

The error appears at the first iteration and the offset error scales with a **run-time** iteration count. There is no emit-time constant to compute. This is the BB FRAME-PLACEMENT CRITERION's own "unbounded growth can intervene" clause, and its remedy is the criterion's own: a home that does not move — RBP.

⭐ **The cure is the criterion satisfied, not a new mechanism.** `ZOPQ`/`ZOPD`/`XSAQ`/`XSAD` already carry an RBP arm keyed on `op_zread_xf[k]`; `capture_frame_slot` already hands out match-scoped RBP homes on `emit_match_rbp()` alone. What was missing was only a *correct displacement* for an operand whose home is **above** RBP.

**No spill is emitted, and that is deliberate.** The ruled design said "spill at `match_begin`". A spill would have to copy from `[rbp + K]` into `[rbp - X]` — it needs the same `K`, then pays a copy and frame bytes to relocate a value that is already at a fixed RBP-relative address and already immune to everything inside the match. So the landing computes `K` and stops. Same criterion, same RBP arm, one fewer instruction; the deviation from the ruled letter is recorded here rather than left to be discovered in the diff.

## THE DISPLACEMENT, DERIVED AND THEN CHECKED AGAINST THE EMITTED CODE

```
K = 8 + (zd_out[match_begin] - zd_out[producer]) + xh(producer, match_begin)
```

The `8` is `match_begin`'s own `push rbp`, which is unconditional under `emit_match_rbp()` (`bb_match_begin.cpp`, `push rbp` / `mov rbp, rsp` inside `if (emit_match_rbp())`). The walked range lies **before the match opens**, so it provably contains no `ALTERNATE` and no `DEFER` — **path-independent by construction**, which is the whole point.

Checked, not assumed: for the charset witness `K = 8`, and `ZOPQ(0,8)` therefore emits `[rbp + 16]`. The pre-cure read was `[rsp + 152]`; the instrumented pieces (`read=144`, `zout_i=96 zout_k=64 zout_mb=64 xh=112` split `32` above / `80` below the `match_begin`) reconcile to `read = D + K` with `D = 136`, and `D` is independently confirmed by `match_begin`'s own `lea rsp, [rbp + -72]` retry line plus the pushes below it. **Three independent routes to the same number before a line of cure was written.**

## THE ADMISSION TEST, AND WHY THE FIRST VERSION WAS TOO NARROW

The anchor fires when: `emit_match_rbp()`, the consumer satisfies `ir_is_matcher_element()`, the operand is not itself a matcher node (which excludes capture wiring operands), and **exactly one `IR_MATCH_BEGIN`** lies between producer and consumer.

⭐ **My first version also required zero `IR_MATCH_END` in the linear range, and that guard silently excluded the entire POS/RPOS class.** In `pos_dyn_inline` the consumers are `MATCH_POS` nodes at indices 45 and 49 — *arm bodies, laid out after the statement chain and after `MATCH_END`*, though they execute **inside** the match. The conservative guard read the linear order and concluded "outside the match".

That is the third arrival this week at one sentence, and it is now mine as well as the org's: **ζ liveness follows NESTING; the walk follows linear ORDER.** It cost the `capture_alt_branch_7` cure a wrong hypothesis, it is why `xop_frame_member`'s γ-chase cannot see a DEFER that is an *arm*, and here it nearly shipped a cure that closed one of two rows the ceo had explicitly said were one cure. The fix was to stop asking "is the consumer between these two linear indices" and start asking "**is the consumer a thing that only ever executes inside a match**" — `ir_is_matcher_element`, a behavioural question with an existing answer in `IR.h`.

⭐ Also worth its own line: the two rows were **not** cured by two changes. `op_zread_xf[k]` is the RBP arm of *both* addressing paths — `ZOPQ`/`ZOPD` (the charset consumer, `op_zres=1`) and `XSAQ`/`XSAD` (the POS consumer, `op_zres=0`, base `op_sa`). One displacement, computed once, fed to one field, cured both. The ceo's "rows 554/585/586 are ONE cure" was structurally right before anyone could see why.

## MEASURED — every number below produced on this tree, none quoted

**Tree:** SCRIP `44f9e17ce` + this change · corpus `3cbc7ec5f` · `.github` `cfc093ca` · `RT_OPT=-O0` · incremental build.

**The three DONE-WHENs, run verbatim and unmodified:**

| gate | before | after |
|---|---|---|
| `test_gate_sno_charset_dynamic_operand_null_alt.sh` (row 586) | **FAIL(1)** — 4 witnesses RED, `break_dyn_nullalt` SIGSEGV 20/20 both modes | **PASS(0)**, 7/7, examined 7 |
| `test_gate_sno_pos_rpos_dynamic_operand.sh` (rows 554, 585) | **FAIL(1)** — `pos_dyn_inline` RED 0/20 both modes | **PASS(0)**, 7/7, examined 7 |

Both gates sweep basename lengths 1..20 in both modes, because argv length shifts the initial stack and therefore every RSP-relative address (hq_S's own reason, inherited).

**SHARED-NODE VERDICT SCOPE — the control arms:**

- **SNOBOL4 master:** `total=1854 · m3_pass=1819 m3_fail=0 · m4_pass=1819 m4_fail=0 · crash=0 hang=0 unproven=0 skip=0 · m3_xfail=35 m4_xfail=34 m4_xpass=1`. **FAIL=0 over the printed denominator in both modes**, and PASS+FAIL+XFAIL covers the whole denominator — no verdict hiding in a SKIP column (the trap that once let a 22-program regression read as a green board).
- **Icon ladder:** baseline 540 graded PASS=510 FAIL=30 → with cure **PASS=510 FAIL=30, identical**.
- **Prolog ladder:** baseline 568 graded PASS=472 FAIL=96 → with cure **PASS=472 FAIL=96, identical**.
- **Icon master:** `entries=808 · run-graded m3 PASS=640 m4 PASS=640 / 655 · ast-shape 153/153` — **watermarks held**, rc=0.

**Blast radius, measured rather than argued.** The owed-artifact check over every benchmark, demo and prolog-bench artifact reports **one** owed file, and its whole diff is four lines in one program:

```
- mov rsi, qword ptr [rsp + 200]   # coerce_string
- mov edx, dword ptr [rsp + 196]
+ mov rsi, qword ptr [rbp + 32]    # coerce_string
+ mov edx, dword ptr [rbp + 28]
```

Icon bench (`total=23 updated=0 unchanged=20`) and Prolog bench (`emitted=23 changed=0`) are **byte-identical across the change**. ⭐ hq_B's point from this morning generalises and is worth keeping: **an owed-artifact count is a blast-radius instrument, not a handoff chore** — it told me the reach of a graph-general emitter change before any board could, and it is what turns "graph-general" from a worry into a number.

## WHAT THIS CLOSES, AND ONE THING IT DOES NOT

This closes the inner half of the last SNOBOL4 master red (`code_eval_len_table_replace_1`, whose `XDump.inc` array enumeration needs exactly this pattern to bind), and the SNOBOL4 floor now reads **FAIL=0**. Every seat grading a shared-node landing against "SNOBOL4 FAIL=0 over the printed denominator" was, until this landed, grading against a bar that could not be reached — that constraint is lifted.

⚠️ **`m4_xpass=1` — `fence_capture_imm_capture_replace_branch_1` now passes with a stale XFAIL marker.** THERE IS NO XFAIL, so that marker is a promotion owed. I have **not** established whether this cure is what turned it green, and I am not claiming it; it is named here so it is not inherited as either cured or unrelated.

## ⭐ TRANSFERABLE

**A guard written for safety can silently narrow a cure past its own row.** The `_nme == 0` term was added defensively, cost nothing to write, broke no test, and quietly excluded one of the two rows the change existed to close. It would have shipped as a complete cure with a green gate beside it. The tell was not a failing test — both gates were the DONE-WHENs and one simply stayed red — it was that **the ceo had already said the two rows were one cure**, so a change that closed one and not the other was a claim contradicting the ruling, and had to be explained rather than shipped.

**A conservative predicate is still a claim about the world, and it decays the same way an aggressive one does.** "No `MATCH_END` between them" reads like caution and is in fact an assertion — that linear position implies execution scope — which is exactly the assertion this engine keeps punishing.
