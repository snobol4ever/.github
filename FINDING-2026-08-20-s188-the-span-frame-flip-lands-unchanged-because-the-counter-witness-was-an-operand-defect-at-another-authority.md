# FINDING s188 (2026-08-20, seat7 `/home/claude7`, Claude Opus 5) — **THE `SCRIP_SPAN_FRAME` FLIP LANDS, AND THE ARM IS THE SAME ARM s173 REVERTED. THE COUNTER-WITNESS WAS NEVER THE ARM'S DEFECT — IT WAS AN OPERAND DEFECT AT A DIFFERENT AUTHORITY, AND CURING THAT AUTHORITY LEFT THE ARM WITH NO COUNTER-WITNESS AT ALL.**

**Brief executed:** queue row 7 `span-frame-flip` — *"HQ-59 ruling (fz3-flip precedent, Lon desk delegation 2026-08-20): flip `SCRIP_SPAN_FRAME` default ON … Run the owed 527-program artifact sweep + 6-suite A/B at armed default at HEAD; flip if clean, own commit"*, under **⛔ HQ-60 (Lon in-chat 2026-08-20): SPINE-RESIDENT LEAVES KEEP RSP** — the flip may not re-home any leaf outside an ALT arm, and *any spine-resident SPAN spelling change = STOP + ask hq*.
**Verdict: CLEAN. FLIPPED AND PUSHED.** SCRIP `d3251f23` (the flip) + `23d2b914` (RULES step-4 feature regen), corpus `42530cb0` (demo regen). One line of behaviour: `(e && *e == '1') ? 1 : 0` → `(e && *e == '0') ? 0 : 1` at `emit.cpp:sn4_span_frame` — the house idiom already carried by `sn4_pt_frame` and `sn4_xh_frame_extra`. **The killswitch stays: `SCRIP_SPAN_FRAME=0` reverts VERBATIM.**
**Tree:** every number below from a **`make pristine`** build (HQ-27), RT_OPT **`-O0`** (FACT RULE O0-DEV), live `x64/bin/sbl` oracle verified alive before measuring. Measured twice: once at `0b75fa5e` before the flip, and **re-proven in full after the rebase** onto seat2's `9d811427` + seat3's `213771e2` (RULES: re-prove your gate after a rebase — those commits touch `emit.cpp`, `zeta_depth.c`, `pattern_match.c`, so the re-proof was not a formality).

## ⛔ THE ONE SENTENCE

s173 measured this arm as **13 cures and one silent wrong answer** and reverted the flip; s184 proved that one wrong answer was **not the arm's** — the cross-`MATCH_BEGIN` correction hardcoded `64` for the head's RSP motion while the true motion is `64 + emit_match_begin_frame_extra()`, a skew **latent at the default arm all along** — and cured it at its own authority (`XH-FRAME-EXTRA`, `0b75fa5e`); with that landed the identical arm now measures **4 cures and zero regressions**, and the flip that was blocked twice goes in with **no edit to the arm itself**.

## THE LEDGER

### 1. `.s` artifact sweep — the owed 527 (`util_s_md5_sweep.sh`, mode-4 TEXT)

**13 movers / 527 comparable** (529 rows; the 2 non-md5 rows are the stable `COMPILE_RC_1` pair the sweep's own header documents from s149). **Both arms self-diffed twice = 0 rows**, so the sweep is not load-flaky and the 13 are real.

| | mover |
|---|---|
| crosscheck | `library/test_string` · `patterns/063_pat_fence_fn_optional` · `064_pat_fence_fn_capture` · `065_pat_fence_fn_decimal` · `121_pat_calc_op_dispatch` · `160_pat_alt_inner_gen_resume` |
| probe/bb | `c5` · `probes/fence_probe` · `probes/H29` · `probes/N12` · `probes/t6m` |
| demo | `claws5-match` · `json` |

### 2. ⛔ HQ-60 ACCEPTANCE — MET, AND CHECKED LINE BY LINE, NOT ASSERTED

Every changed line in all 13 movers falls in exactly four classes, with **zero `OTHER`** (mechanical classification, both measurements):

* **CARVE** — `sub rsp,N` at `MATCH_BEGIN` widening by 16 per new registry candidate.
* **WHACK** — the `lea rsp,[rbp-N]` `retry_whack` following the carve by the same delta.
* **RE-HOME** — an ALT-arm scratch-cell leaf's ζ cell moving from a flat `[rsp+N]` to `[rbp-M]`, plus registry renumbering of already-rbp-homed slots whose index shifted (`121`: `[rbp-64]`→`[rbp-96]` — a renumber, not a new re-home).
* **SPINE REBASE** — `json`'s `n675_match_break_α` charset read `[rsp+136]`→`[rsp+152]`, i.e. **exactly the carve delta**. This is the s184 cure working: the flat spine operand now follows the moved `rsp`. It is a *displacement* change, not a *spelling* change — no spine operand became rbp-relative.

**Every re-homed box was verified to be ALT-arm interior**, by its own wires and not by trusting the predicate: entered from `*_match_alternate_α`'s arm dispatch (directly or through a concatenation chain) and failing back to `*_match_alternate_af`. The four that do not name an alternate on their own line were chased by hand: `H29 n18_match_tab` (entered via `n17_match_assign_save_α` from `n15_match_alternate_α`, fails to `n15_match_alternate_af`), `json n675_match_break` (arm of `n664`), `claws5-match n69_match_break`/`n72_match_span` (interior of the `n68_match_notany` concatenation inside `n65`'s arm), `160 n11_match_arb` (via `n10_match_assign_save_α` ← `n9_match_lit_α`, arm 1 of `n3`). **ZERO spine-resident re-homes. `leaf_frame_member()`'s `alt_arm_member` conjunct was NOT widened** — the flip changes one default and nothing else.

### 3. The 6-suite board — 1222 rows/arm × 2 modes

Suites `crosscheck · patterns · bb_probes · feature_test · probes_misc · demos`, every row graded m3 AND m4 against the live oracle or its pinned `.ref`.

| | m3 PASS | m4 PASS |
|---|---|---|
| `SCRIP_SPAN_FRAME=0` | 1172 | 1113 |
| flipped default (ON) | **1173** | **1117** |

**4 movers. ALL CURES. ZERO REGRESSIONS** — not one program that passed in either mode stopped passing.

| suite | program | OFF → ON |
|---|---|---|
| demos | `programs/snobol4/demo/claws5-match.sno` | SIG11/SIG11 → **PASS/PASS** |
| probes_misc | `probe/cn/cn_alt_leaf_lit_red.sno` | PASS/SIG11 → PASS/**PASS** |
| probes_misc | `probe/cn/cn_alt_leaf_flat_red.sno` | PASS/SIG11 → PASS/**PASS** |
| probes_misc | `probe/claws5/claws5_dcap_call_green.sno` | PASS/SIG11 → PASS/**PASS** |

**Noise floor stated, not assumed:** the default arm re-run against itself moved **1** row — `160_pat_alt_inner_gen_resume` `SIG11/SIG11 → SIG11/SIG4`, an already-red row crashing differently, the documented class where a dead run's status is not stable. All 4 movers above are red→green state changes, none of that shape.

### 4. Corpus non-regression + the standing watermark

`test_corpus_snobol4.sh`: **m3 332/5 · m4 325/11 SKIP 1** — the s183/s184/s185 watermark — at the flipped default, at `=0`, and pre-flip, with the **fail-set identical BY NAME across all three**. (`claws5-match` is not a member of this runner, which is why the cure shows on the board and not here.)

### 5. Gates + the blocker, re-verified

4 gates green: `emit_no_lang` · `template_medium_invisible` (ceiling 0) · `icn_no_stack` · `icn_one_reg_frame`. **`TDump_driver` — the s173/s184 blocker — is PASS in BOTH arms and BOTH modes** (`ulimit -s unlimited`, as its m3 requires). The `probe/leafwide` witness family is PASS in both arms; `ctl_spanvar_alt_inline` stays **DIFF in both arms**, arm-independent, exactly as the s184 cursor recorded it — **not a flip blocker, still wants its own row.**

### 6. THE FLIP IS PROVEN TO BE THE ARM THAT WAS MEASURED

After the flip + pristine rebuild, joined row-for-row against the pre-flip pair:

* flipped default vs pre-flip **ARMED**: **0 movers / 527** `.s`, **0 movers / 1222** board rows.
* `SCRIP_SPAN_FRAME=0` vs pre-flip **DEFAULT**: **0 movers / 527** `.s`.
* flipped default vs `=0` on the shipped build: **13** `.s` movers — the same 13, same program set, same line classification, post-rebase.

## ⛔ WHAT THE DONE-WHEN ASKED, ANSWERED LITERALLY

* **flip pushed** — SCRIP `d3251f23`.
* **probe/cn witnesses green m3 at default** — `cn_alt_leaf_lit_red` and `cn_alt_leaf_flat_red` were already m3-green and were **m4 SIG11**; at the flipped default both are **green in BOTH modes**. `cn_nest_alt_defer` (the witness the `lower_snobol4.c` CN-15 comment names) is PASS/PASS.
* **`demo_claws5` green m3 at default** — ⛔ **and this is two programs, so say which.** `demo/claws5-match.sno` was **m3 SIG11 and is now PASS in both modes** — that is the m3 cure HQ-59 priced. `demo/claws5.sno` (the corpus runner's `demo_claws5`) was **already m3-green** and its **m4 SIG11 is unmoved by this flip** — that residue is queue row 23 `claws5-m4-sig11`'s scope, which HQ already narrowed to the m4 half. Nothing here closes row 23.
* **corpus non-regression** — §4.

## ⭐ FOR THE NEXT SEAT — OWED-2 IS NOW UNBLOCKED, AND THE FIRST READING IS A CURE

`lower_snobol4.c:sno_kw_nest_ok`'s comment states the CN-15 arming is **blocked on `SCRIP_SPAN_FRAME`, not on its own switch** — lifting the top-level-only limit turns an ALT arm's `IR_MATCH_DEFER` into a scratch-cell leaf and re-arms exactly the class this flip cures. **That block is now gone by default.** One suite measured (not a flip, not landed): `SCRIP_CONST_NEST=1` over `probes_misc` (612 rows × 2 modes) at the flipped default = **1 mover, a cure** — `probe/cn/cn_const_compose_all` DIFF/DIFF → **PASS/PASS** — and zero regressions. A real OWED-2 flip still owes the full 527 + 6-suite treatment this row just ran; this is one suite and is reported as a pointer, not a verdict.

## THE GENERALISABLE MOVE

**A counter-witness that survives a killswitch A/B is not automatically the arm's defect.** s173's `TDump_driver` was red *only* under the armed arm, which reads as arm-caused and cost the flip two sessions — yet the mechanism was a constant `64` in a *different* authority that was wrong the whole time and merely invisible while `emit_match_begin_frame_extra()` returned 0. The arm did not break it; the arm **made an existing skew reachable**. When an A/B produces a single counter-witness against many cures, ablate to the smallest witness and **diff the two arms' `.s`** before pricing the arm: an operand byte-identical across both arms while `rsp` moved under it is the tell, and it names the second authority instead of the switch.
