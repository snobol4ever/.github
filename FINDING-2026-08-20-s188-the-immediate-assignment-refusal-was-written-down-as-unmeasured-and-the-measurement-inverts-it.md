# FINDING s188 (seat2 `/home/claude2`, Claude Opus 5; queue row `arb-immed-assign-retry`, rank 1)
# ⛔ THE `$` BLOB-RESUME REFUSAL WAS WRITTEN DOWN AS "UNMEASURED" AND THE MEASUREMENT INVERTS ITS REASONING. THE BRIEF'S CLASS NAME IS FALSIFIED: IT IS NOT `$` ON A RETRYING GENERATOR.

**WATERMARK (SCRIP `zeta_depth.c` one line, `make pristine`, tree clean, RT_OPT `-O0`):** corpus board **m3 332/5 · m4 325/11 · SKIP 1** — the brief's baseline TO THE DIGIT, fail-set identical **by name**. Smoke **7/7 both modes** (m4 hard gate) · medium-invisible **0** (ceiling 0) · emit_no_lang **LANG-BLIND OK**. RULES step-4 regen: benchmark/feature/demo all **`changed=0`**.

## ⭐ THE HEADLINE — THE BRIEF NAMED THE WRONG INGREDIENT, AND THE CONTROLS IT SHIPPED COULD NOT HAVE CAUGHT IT

The brief's class was *"an IMMEDIATE ASSIGNMENT **ON** A RETRYING GENERATOR"*, isolated by two controls: `ARB . v` green (so not ARB alone) and `SPAN('a') $ v` green (so not `$` alone). Both controls are real. **The conjunction they name is still wrong**, because neither control varies the axis that actually matters.

**One probe falsifies it.** The witness's own pattern, written INLINE instead of stored:

```
'a+aa' POS(0) ARB $ v RPOS(0)      → oracle matcha+aa · SCRIP matcha+aa   GREEN
E = ARB $ v ; 'a+aa' POS(0) *E RPOS(0)  → oracle matcha+aa · SCRIP nomatch   RED   (the witness)
```

`$` on a retrying generator, retry forced by the same `RPOS(0)`, **has always worked**. The ingredient is that the pattern is **BUILT AS A VALUE** — assigned to a variable and matched through the compiled `PAT$n` blob.

**And the deferral is not the ingredient either.** `*E` is a red herring the witness inherits from its neighbours: reference `E` **BARE** and it is equally red (`ptw_min_arb_immed_stored`). Deferred, bare, and `*(…)` on a parenthesised inline pattern all fail identically; every inline spelling passes.

**⛔ THE SECOND CONTROL PROVES LESS THAN IT APPEARS TO.** `ptw_min_span_immed_ctl`'s `.ref` is **`nomatch`** — oracle and SCRIP agree only in *refusing*, and `v` is never printed, so the control never demonstrates that `$` assigns anything at all. A positive control was minted (`SPAN('a+') $ v` over the same subject → `matcha+aa`) and it is green. The conclusion "not `$` alone" survives; the evidence offered for it did not carry that weight.

## ⭐⭐ THE ROOT CAUSE, AND IT WAS DOCUMENTED RATHER THAN HIDDEN — THE SAME SHAPE AS s187

`src/contracts/zeta_depth.c:38`, `zdp_seam_tier()`:

```c
case IR_MATCH_ASSIGN_COND: case IR_MATCH_ASSIGN_SAVE: return zdp_cap_seamtier() ? 2 : 0;
default: return 0;                                  /* IR_MATCH_ASSIGN_IMM fell to here */
```

`IR_MATCH_ASSIGN_IMM` was untiered, so `resume_carrier_ok()` (`emit.cpp:2451`) refused it as a resume carrier and the blob published a **wholesale concede**. s180 cured exactly this for `.` and **said in the same comment why it left `$` behind**, verbatim:

> *"ASSIGN_IMM stays 0: unmeasured, and its side effect fires DURING the match (undo is not a pure record pop)."*

**⛔ That sentence is the defect, and it is s187's shape one file over: a limitation frozen into a contract by being written down.** s187 found `pattern_match.c:911` capping the `DT_X` chain at one link and justifying it as *"mirrors the old body EXACTLY"*; here a refusal is justified as *"unmeasured"* — and stays refused for eight sessions because the note reads as a ruling.

## ⭐⭐⭐ THE MEASUREMENT INVERTS THE STATED REASONING

Emitted asm, the two inline witnesses (`--compile`, TEXT):

```
n6_match_assign_imm_β:                        jmp   n5_match_arb_β      ← $  : BARE leftward jump
n6_match_assign_cond_β:  sub  r12, 24;        jmp   n5_match_arb_β      ← .  : pend-record pop, then the same jump
```

**IMM's β is a STRICT SUBSET of the shape s180 blessed** — the identical leftward fail-through with the record pop *omitted*. Tier 2 is defined in this file as *"deterministic elements whose beta is a self-undo fail-through jumping LEFTWARD"*; IMM qualifies more cleanly than COND, not less.

The reasoning is backwards because the manual makes it so. **SPITBOL manual p.87, "Immediate Assignment"** (the row's required citation): *"Immediate assignment occurs whenever a subpattern matches, **even if the entire pattern match ultimately fails**."* The side effect being committed is precisely why there is **no undo to get wrong**. s180 read "fires during the match" as a hazard; the manual makes it the safety argument.

**The manual also settles the retry question directly — its own worked example is this pattern.** p.87:

```
S = 'ABCDEFG' ;  S ? 'A' ARB $ OUTPUT 'E'   →   (null) / B / BC / BCD / Success
```

ARB **extends** under `$` and **re-fires** the assignment on every retry. Checked in as `ptw_min_man_p87_stored`: stored in a pattern variable, SCRIP printed the null string and then `Failure` — **one firing, zero retries**, i.e. the retreat died at the `$` node and never reached ARB. **p.123–124 "Quickscan and Fullscan"** closes the only escape hatch: the heuristics that once let a `$` suppress match attempts were **removed from SPITBOL** — *"pattern matching is done exhaustively and no heuristics are applied"* — and `&FULLSCAN` may only be set non-zero. There is no reading of the manual under which the witness may fail.

## ⭐ ASM-DIFF-FIRST, AND IT NAMED THE MECHANISM WITHOUT gdb

Per RULES the opening move was the `.s` diff between the passing sibling (`ARB . v` stored) and the failing witness (`ARB $ v` stored). One line differs in the blob's β port:

```
PAT$0_β:   jmp  n2_match_assign_cond_β     ← .  GREEN : re-enters the capture, which resumes ARB
PAT$0_β:   jmp  PAT$0_ω                    ← $  RED   : the wholesale refusal
```

This is verbatim the shape s180's own comment describes as the pre-s180 state (*"the blob β-dispatch REFUSED any stored pattern whose rightmost element was a capture (`PAT$N_β: jmp PAT$N_ω`)"*) — s180 cured it for one member of the family and left its twin refusing. `SCRIP_RESUME_WHY=1` prints the lattice verdict directly and was the confirming instrument: witness `body_root_op=59 tier=0`, sibling `body_root_op=58 tier=2`. (⛔ Cite the CONSTRUCT: 58/59 are ASSIGN_COND/ASSIGN_IMM at this commit — the enum is alphabetical since `54b6c478`.)

## THE CURE — ONE CASE LABEL, AND IT IS A FACT-RULE REPAIR

`IR_MATCH_ASSIGN_IMM` joins the arm its two family-mates already sat in. `bb_match_capture.cpp` owns **COND, IMM and SAVE** — "one mechanism, two phases" in `emit.cpp`'s own words — so admitting COND while refusing IMM was exactly the **FACT RULE NO-PER-OP-FILTER** shape: a family member refused by op identity. The family is now uniform, rides the existing `SCRIP_CAP_SEAMTIER` killswitch, and **adds no state** (no new global, no new env knob, no new file-scope).

## THE BOUNDARY, MEASURED ON 18 PROBES × 2 MODES — ALL GREEN, 1:1 THROUGHOUT

Every red in the axis sweep fell to the one line, and **m3 ≡ m4 on all 18** before and after (a lower/lattice defect both media inherit from one codegen — no mode-4 row is owed):

| axis | probe | before | after |
|---|---|---|---|
| manual p.87, inline | `'A' ARB $ OUTPUT 'E'` | GREEN | GREEN |
| manual p.87, **stored** | same, via `E` | **RED** | GREEN |
| inline `$` + retry | `ARB $ v` inline | GREEN | GREEN |
| stored, **bare** ref | `E = ARB $ v`; `E` | **RED** | GREEN |
| stored, deferred | `*E` (the witness) | **RED** | GREEN |
| stored, `*(inline)` | `*(ARB $ v)` | **RED** | GREEN |
| stored + ARBNO | `ARBNO(LEN(1)) $ v` | **RED** | GREEN |
| stored + BAL | `BAL $ v` | **RED** | GREEN |
| stored + ALT arms | `('a'\|'a+'\|'a+aa') $ v` | **RED** | GREEN |
| `$` **off** the generator | `ARB ('a' $ v)` | **RED** | GREEN |
| literal forcing tail | `*E 'aa'` | **RED** | GREEN |
| no retry required | `E RTAB(0)` | GREEN | GREEN |
| `$` at the **use** site | `E = ARB`; `E $ v` | GREEN | GREEN |

**⭐ The two greens are the load-bearing ones.** `E RTAB(0)` is tier 0 *and green* — because nothing forces a retry, which is what proves tier 0 only manifests as a retreat refusal. `E = ARB` + `E $ v` is green because the `$` is compiled into the statement graph, not into the blob — the single cleanest statement of where the boundary ran.

## ⛔ ONE HONEST NON-CLOSURE, MEASURED AND ROUTED, NOT FOLDED IN

**`IR_MATCH_ATP` (the `@` cursor operator) is untiered in the same switch and is red by the same symptom.** `E = ARB @v` → `PAT$0_β: jmp PAT$0_ω`, oracle `match4`, SCRIP `nomatch`; the **inline twin is green**. Checked in red per law 0d as `ptw_min_atp_stored_red` + `ptw_min_atp_inline_ctl` with live-oracle refs.

**It is NOT this row's family and was deliberately not folded into this landing:** ATP owns `bb_match_atp.cpp`, a separate template, so it is a separate box family — the FACT RULE closes the family that shares a mechanism, and `bb_match_capture` is now closed (COND + IMM + SAVE all tier 2). **The measurement is done so the next seat inherits it rather than re-deriving it:** ATP's inline β is `add rsp,16; jmp n4_match_arb_β` — a self-undo fail-through jumping LEFTWARD, the tier-2 definition verbatim and the *same shape as ASSIGN_SAVE's β* that s180 already blessed. **The cure is one case label.** Wanted: its own row, its own board A/B.

**Also seen and NOT mine:** `IR_MATCH_ALTERNATE` is untiered too (`E = ARB ('x'|'a')` stored → red, `body_root_op=54 tier=0`). That is the **s183 `blob-resume-refusals` untiered disjunction**, already routed; the standing board reds `160_pat_alt_inner_gen_resume` and `175_pat_bal_generator_retry` sit in that lane. Recorded here only so the next seat does not mint a third witness for it.

## ⛔ THE GENERALISABLE MOVE, FOR THE NEXT SEAT THAT MEETS THIS SHAPE

**A refusal that documents itself as "unmeasured" is a TODO, not a ruling — and it decays into a ruling by being read.** Two sessions running (s187's `dtx_used`, this row's `ASSIGN_IMM stays 0`) the blocker was a candid comment explaining why one half of a mechanism was left out, which every subsequent reader took as a validated boundary. **When a comment justifies a limitation by anything other than a measurement — "mirrors the old body", "unmeasured", "the obvious risk is" — the sentence is a lead, not a wall: go measure it.** Both times the measurement took minutes and inverted the stated reasoning.

**Corollary on controls:** a control whose expected output is a *failure* proves only agreement in refusing. Where a mechanism's job is to produce a value, at least one control must show the value being produced.

**⭐ RE-PROVED AFTER THE REBASE, NOT ASSUMED:** the push brought in two pattern-machinery commits beneath this one — seat4's `cecb7d11` ARBNO-ALTSIB and seat3's `213771e2` ONE AUTHORITY (the duplicate `DT_X` chain drain, s187's own file) — so every number was re-measured after a second `make pristine` at merged SCRIP **`9d811427`**: board **m3 332/5 · m4 325/11 · SKIP 1** fail-set identical **by name**, smoke **7/7 both modes**, medium-invisible **0**, emit_no_lang **LANG-BLIND OK**, and all 8 checked-in probe pairs verdict-identical (the `atp` pair red as checked in, its inline control green), `m3 ≡ m4` on every one.

## FILES

- **SCRIP** — `src/contracts/zeta_depth.c` (one case label; the stale s180 comment corrected in place rather than left contradicting the code).
- **corpus** — `probe/passthru/ptw_min_arb_immed_inline_ctl` · `ptw_min_arb_immed_stored` · `ptw_min_man_p87_stored` (green, this row) · `ptw_min_atp_stored_red` + `ptw_min_atp_inline_ctl` (red, routed), all with **live-oracle** `.ref`s checked for the s186 `sbl`-exits-0-after-a-fatal-error trap.
