# FINDING s192 (seat3) — THE `FAIL` RETREAT WAS WIRED ALL ALONG. A **STATEMENT-TERMINAL POP** WAS STAMPED IN FRONT OF IT, AND IT FREED THE RETRY CURSOR THE RETREAT WAS ON ITS WAY TO READ

**Date:** 2026-08-20 · **SCRIP:** `ed61196c` (`make pristine`, RT_OPT `-O0`) · **corpus:** `a90b5aeb` · oracle live `sbl -bf`.
**Row:** `rty-fail-inline-retry` (rank 1) — Class A of `FINDING-2026-08-20-s189-two-retry-classes-on-opposite-roads.md`. ⭐ **Class B (`rty-fence-arbno-stored`) LANDED IN PARALLEL** as seat2's FENCE-RTAIL (`56842aab`) while this rung was measuring. Its three witnesses were red on my measurement tree and are **green at the merged HEAD**; that is seat2's cure, not mine, and the two are independent — **all ten `probe/retry/` witnesses are green in BOTH modes at merged `ed61196c`, pristine**, so neither patch disturbs the other. The two classes were on opposite roads exactly as s189 paired them, and each took its own line.

## 1 · ⛔ THE BRIEF'S MECHANISM WAS WRONG, AND THE WRONG WORD IS "WIRING"

s189 read the defect as: *"on the inline statement-graph road, `IR_MATCH_FAIL`'s failure exits as a wholesale concede instead of a retreat (β) into the left element."* Two corrections, both from the brief's own prescribed first step (diff the two roads' emission), and neither of them blocking — the witnesses, the split, the controls and the DONE-WHEN were all exactly right.

**(a) There is no `IR_MATCH_FAIL`.** `FAIL` lowers to a **bare `IR_GOTO`** whose BOTH ports are φ-tagged (`lower_snobol4.c:1365`), and `sno_seq_nary`'s global fixup repoints both at the left neighbour carrying a **β** tag. The opcode census that would have found this is one grep: `grep -rn IR_MATCH_FAIL src/` returns nothing. (`TT_ABORT`, the case immediately beside it, was minted into a real `IR_MATCH_ABORT` for the adjacent reason at SCRIP `83114981` — *"was a bare `IR_GOTO` — classifier-invisible"* — and that commit's own comment cites `TT_FAIL` as its precedent. The precedent was never converted, so `FAIL` is the last bare-`IR_GOTO` pattern element.)

**(b) THE RETREAT EDGE WAS CORRECT.** The emitted asm jumps to `n6_match_assign_imm_β` — the left element's β, exactly as the stored road does. What is wrong is the instruction **in front of** it. `--compile`, `rty_fail_arb_inline` vs its one-token green twin `rty_deadlit_arb_ctl`, whole diff minus label renumbering:

```
control:   .Lx22_1:   add rsp, 48;    jmp n6_match_assign_imm_β
patched:   .Lx22_1:                   jmp n6_match_assign_imm_β
```

`add rsp,48` is the **statement-terminal ζ release**. `n5_match_arb_β` reads its retry cursor at `[rsp+0]`/`[rsp+4]` — cells the release has just freed — so the extension arithmetic runs on garbage, exhausts immediately, and the whole match dies after ONE instance. Oracle `A/AB/ABC`, SCRIP `A`.

## 2 · THE ONE LINE, AND THE ω SIDE HAD ALREADY FIXED IT ONCE

`zd_plan`'s release planner (`src/emitter/emit.cpp`) decides per node whether a γ arc leaves the statement. Its membership test was **forward-only**:

```c
else for (int k = 0; k < rl; k++) { if (nodes[run[k]] == gt && k > r) gin = 1;  ... }
```

A β-tagged γ arc is a **retreat**: it lands at or BEHIND its own run position (the FAIL relay chases straight back to the node itself, `k == r`). `k > r` is false, `gin` stays 0, and `zgpop[i] = 48` is stamped on an arc that never leaves the match. The `[ZD]` planner diagnostic is a one-row diff between the two witnesses:

```
RED    i=6 IR_MATCH_ASSIGN_IMM K=0 zout=48 gpop=48 wpop=0
GREEN  i=6 IR_MATCH_ASSIGN_IMM K=0 zout=48 gpop=0  wpop=0
```

⭐ **The ω port already carries this exact relaxation, and its comment predicted this bug in so many words:** *"ZD-5b-SAVE-OIN (s14): drop k>r on oin — scan-retry back-edge (ω→MATCH_BEGIN, k<r) is intra-match; **forward-only guard was correct for gin but wrong for oin**."* It was correct for gin only for as long as no γ arc carried a β tag. `lc_γ_to_β`/`lc_γ_tag_β` exist and are used by four lowerers; the SN4 seq fixup is the one that reaches an armed run.

**CURE — one derived predicate + one conjunct, keyed on the PORT TAG and never on an op:**

```c
int gib = port_sz_beta(nodes[i]->γ.sz); { …GOTO chase, inherit the tag… } gib = gib && !beta_is_stmt_land(gt);
…  if (nodes[run[k]] == gt && (k > r || gib)) gin = 1;
```

The chase is mandatory and is why a naive `port_sz_beta(nodes[i]->γ.sz)` finds nothing: **the tag lives on the intervening relay, never on the producer.** ASSIGN_IMM's own `γ.sz` is CLEAR; only the FAIL `IR_GOTO` says retreat. Same chase the drive loop already runs for `gamma_is_beta` (~3163); same `!beta_is_stmt_land` split as `omega_is_retry` (~3165) — a β-edge into `STATEMENT_BEGIN` is a pure landing pad, not an in-match back-edge.

⭐⭐ **AND THIS IS WHY THE STORED ROAD WAS GREEN — the brief's "the blob road IS the specification" lands on the line one above.** The `nblob > 0` arm carries **no positional test at all**; it asks membership and nothing else. The two roads disagreed because one of them had a forward-only guard bolted to its membership test and the other did not.

**⛔ NO-PER-OP-FILTER SATISFIED BY CONSTRUCTION:** the conjunct names a port tag. BAL and ARB are one class here and neither is spelled. **NO NEW GLOBAL** (one block-local `int`), **NO NEW KILLSWITCH** (`getenv` count unchanged), **NO NEW OPCODE**, **NO TEMPLATE TOUCHED**.

## 3 · ⭐ THE DEFECT WAS LIVE IN EIGHT PROGRAMS AND VISIBLE IN ONE

The compile-time md5 blast radius (below) found the pop firing in 8 programs; only `175`/`rty_fail_*` were red. **In the other seven the retreat cascades straight into an ABSOLUTE unwind** — `n2_match_begin_β`'s `lea rsp,[rbp-56]` retry_whack, or the frame whack — which re-establishes RSP before anything reads it, so the over-pop is healed in flight. The cells only get read when the retreat lands on an **EXTENDING generator**, one that keeps its retry cursor on the ζ-spine at a static offset.

That is exactly the manual's class and exactly the guard control's class. v3.7 p.208: *"patterns such as ARB and BAL have **implicit alternatives** which are tried before your explicit ones. ARB behaves as if it were `(LEN(0) | LEN(1) | LEN(2) | …)` … and fails only when further extensions would make it larger than the subject."* SPAN is not in it — p.126 *"SPAN … will match the longest subject string possible"*, one instance. So `rty_fail_span_ctl` firing once is correct, and it stays correct: **its emission moves (the same one instruction is deleted) and its output does not.** The witnesses whose FAIL sits right of `ANY`/`NOTANY`/`LEN`/`*P` are all in the healed seven.

Manual on `FAIL` itself, p.125: *"FAIL tells the pattern matcher to try again… Forced failure and retries continue until the subject is exhausted"*, and p.204: *"causing the scanner to backtrack and try alternatives."* SCRIP now does.

## 4 · MEASUREMENT

**Witnesses** — all ten of `corpus/probe/retry/`, both modes, patched:

| witness | m3 | m4 | |
|---|---|---|---|
| `rty_fail_bal_inline` | PASS | PASS | ⭐ was RED |
| `rty_fail_arb_inline` | PASS | PASS | ⭐ was RED |
| `rty_deadlit_arb_ctl` · `rty_fail_bal_stored_ctl` · `rty_fail_span_ctl` | PASS | PASS | the three controls, unmoved |
| `rty_fence_arbno_*` (3) | red | red | Class B, other row, untouched |

**Board A/B, both arms ON ONE TREE, at the shipped HEAD:** corpus **m3 334/3 → 335/2 · m4 327/9 → 328/8 · SKIP 1 (337)**. Δ = `175_pat_bal_generator_retry` FAIL→PASS **both modes**; every remaining failure identical **by name** (145, 160 m3; + expr_eval, 140, 141, semantic_driver, demo_treebank, demo_claws5 m4). ⛔ **RE-MEASURED HERE, NOT CARRIED OVER, AND THAT CAUGHT A MISATTRIBUTION.** The first A/B ran pre-rebase at `021e2b65` (m3 333/4 → 334/3 · m4 326/10 → 327/9, same Δ). The rebase pulled corpus `6913c6e8`, seat5's `prototype-array-dim`, which EDITS `crosscheck/rung11/1110_array_1d.sno` itself — so `1110` turns green across the rebase and **is not mine**. Quoting the post-rebase board against the pre-rebase control would have claimed two cures for a one-line patch. The patched binary is byte-identical to the `make pristine` build (`md5sum -c` on `scrip` + `out/libscrip_rt.so`, both OK), so the pristine verdict covers the shipped artifacts.

**⭐ COMPILE-TIME MD5 BLAST RADIUS — ALL 4982 CORPUS PROGRAMS, ALL SEVEN LANGUAGES** (`corpus/programs/lon/` excluded **by construction**, `find … -prune`, per the absolute rule — never run, never compiled, never read):

- **9 rows differ. 8 are the cure. 1 is the instrument.**
- ⛔ **THE NOISE FLOOR WAS MEASURED FIRST AND IT IS NOT ZERO.** Control arm self-diffed against itself, SAME binary: **1 row** — `programs/snobol4/parser/unary_not.sno`, whose `.S0` rodata string is nondeterministic (three runs of one binary, three md5s: `7216f0a2…`/`db4306d5…`/`d596537b…`). That is s147's already-named class, it appears in the mover list, and quoting 9 without the self-diff would have published a phantom. **True blast radius: 8.**
- All 8 are **ONE MECHANISM**: a single `add rsp,N` deleted in front of a `jmp nX_match_{assign_imm,lit}_β`. Nothing else moves in any of the eight files.
- **ZERO Icon, Prolog, Raku, Pascal, Rebus movers.** This matters: the planner's `ZK-2 GEN-BACK-GIN SCOPE BOUNDARY` comment records that setting `gin=1` for the Icon `every` back-edge (`IR_ASSIGN.γ → IR_TO.β`, also a β-tagged γ arc) was **measured wrong** and refused. The sweep proves that topology is not reached — the cells-arm runs never present it to this test — so the conjunct did not need scoping and none was invented. **If a future rung arms that topology, this is the line that will meet it, and the honest scope is ZK-2's own hazard: a retreat that re-executes CARVING nodes.**
- 8 movers behaviourally: all 8 **ORACLE-IDENTICAL** at `sbl -bf`. Five already had `.ref`s and pass both modes (`057_pat_fail_builtin`, `172_pat_fail_forces_retry`, `175_pat_bal_generator_retry`, `csnobol4-suite/any`, `csnobol4-suite/unsc`).

**Re-proved at merged `ed61196c`, its own `make pristine`** (seat2's FENCE-RTAIL, seat4's REAL-FN-FAMILY and the beauty PRE-CHAIN commit all landed between the A/B and the push — FENCE-RTAIL touches the same seq/resume-carrier machinery, so this was an interaction check, not a formality): board **m3 335/2 · m4 328/8 SKIP 1**, all ten retry witnesses green both modes.

**Gates:** `emit_no_lang` · `template_medium_invisible` (ceiling 0) · `icn_no_stack` · `icn_one_reg_frame` — all green.

## 5 · WHAT THIS RETIRES

`175_pat_bal_generator_retry` — the Class A board red, FAIL→PASS both modes. Queue row `rty-fail-inline-retry` closed. Class B (`145_pat_left_assoc_via_arbno_fence`, row `rty-fence-arbno-stored`) is **not** touched and stays red; s189's pairing of the two classes held up — opposite roads, and only one of them was this line.

## 6 · ⭐ THE GENERALISABLE MOVE

**A guard that is correct only because no input has ever exercised it is not correct — it is unexercised.** `k > r` was written when every γ arc went forward, and stayed load-bearing for the years in which that remained accidentally true. The ω twin was fixed at s14 and the fix's own comment said the γ side was "correct"; it was correct about the inputs of that day. Same family as s189's `default: return 0` (an unlisted op inherits "unsafe" without anyone deciding) and s191's lookup-that-prints-is-not-a-lookup-that-checks: **ask what a test does with the case that has not arrived yet, and whether anything would tell you when it does.**

And the second, cheaper one: **the retreat was right and the instruction in front of it was wrong.** A one-token-apart asm diff said so in one line, before any debugger. ASM-DIFF-FIRST paid for itself in a single step here — the brief's proposed mechanism ("β not wired") would have sent a seat into the lowerer to re-wire an edge that was already correct.
