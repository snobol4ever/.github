# FINDING s169 (seat5, Opus 5, queue row `b1c-flip`) — THE B1c PARITY DEFAULT IS FLIPPED ON: 1024 PROGRAMS × 2 MODES × 2 ARMS, NINE MOVERS, EVERY ONE CRASH→BETTER, ZERO REGRESSIONS — AND MODE-4 `.s` IS BYTE-IDENTICAL BY MEASUREMENT

**Front:** GOAL-SNOBOL4-100 · beauty self-host M1 · wall **B1c**. Queue row 3 `b1c-flip`, DONE-WHEN: *"A/B table in a FINDING, default flipped + pushed, e_plain/b1c_cross_medium_concat_seam green m3 at default."* All three met.
**Trees:** SCRIP `f44be5f1` (the commit the brief names — it was origin HEAD on arrival), corpus `a3604cc9`, .github `12355307`. Oracle `x64/bin/sbl` cloned and smoke-verified before any verdict. **Both measurement arms and the post-flip re-measure ran on `make pristine` builds — driver AND `out/libscrip_rt.so` from one commit** (HQ-27 PRISTINE-BUILD-BEFORE-VERDICT; this is the exact contamination class that manufactured the retracted HQ-21 numbers).

## What was inherited
HQ's `f44be5f1` landed B1c fragment emit-context parity behind `SCRIP_B1C_PARITY`, **default OFF**, explicitly deferring the A/B and the flip to this seat. Three getenv sites: `src/runtime/runtime_eval.c:231` (the fragment proc loop's parity block — `rt_proc_set_jmpentry` / SN4-FLAT-PROC floor / PL-DC arming / frame-bytes / zstatic / patzeta / DC seal) and `src/templates/bb_call_proc_staged.cpp:322,593` (the two TINY-refuse gates, `!g_rt_fragment_emit || _b1c*`).

## THE A/B — 6 suites, 1024 programs, both modes, both arms
Suites (the `--suites` set, sizes as measured): `crosscheck` 196 · `patterns` 122 · `bb_probes` 188 · `feature_test` 161 · `probes_misc` 334 · `demos` 23 = **1024 rows/arm**, each row graded in m3 AND m4 against the live oracle or its pinned `.ref`.

| | m3 PASS | m4 PASS |
|---|---|---|
| default (OFF) | 956 | 944 |
| `SCRIP_B1C_PARITY=1` | **962** | 944 |

**Movers: 9. Regressions: 0** — not one program that passed in either mode stopped passing. Every mover starts from SIG11.

| suite | program | OFF → ON |
|---|---|---|
| patterns | `crosscheck/patterns/141_pat_eval_double_fn_arbno.sno` | SIG11/SIG11 → **PASS**/SIG11 |
| probes_misc | `probe/b1/b1c_cross_medium_concat_seam.sno` | SIG11/SIG11 → **PASS**/SIG11 |
| probes_misc | `probe/b1/b1c_e_plain.sno` | SIG11/SIG11 → **PASS**/SIG11 |
| probes_misc | `probe/eval/ev_beauty_shape.sno` | SIG11/SIG11 → **PASS**/SIG11 |
| probes_misc | `probe/nret/nr_eval_direct_CONTROL.sno` | SIG11/SIG11 → **PASS**/SIG11 |
| probes_misc | `probe/nret/nr_eval_opsyn_CRASH.sno` | SIG11/SIG11 → **PASS**/SIG11 |
| probes_misc | `probe/b1/b1c_eval_fn_pattern_retreat.sno` | SIG11/SIG11 → DIFF/SIG11 |
| probes_misc | `probe/b1/b1c_patvalued_formal_retreat.sno` | SIG11/SIG11 → DIFF/SIG11 |
| probes_misc | `probe/b1_eval_pattern_defer_call.sno` (`probe/b1/`) | SIG11/SIG11 → DIFF/SIG11 |

Three of the nine are corroboration from OUTSIDE the b1 probe set that HQ built the fix against — `141_pat_eval_double_fn_arbno` (shared crosscheck corpus), `nr_eval_direct_CONTROL` and `nr_eval_opsyn_CRASH` (the NRETURN probe family). `ev_beauty_shape` is a beauty-shaped EVAL witness and sits directly on the M1 critical path.

## Mode-4 `.s` blast radius = 0, measured twice
`util_s_md5_sweep.sh` over 529 programs (demo + crosscheck + probe/bb): **OFF vs ON = 0 movers / 527 comparable**; the 2 non-md5 rows are the same stable `COMPILE_RC_1` pair the sweep's own header documents from s149 (`crosscheck/coverage/coverage_sno_nodes.sno`, `demo/expression.sno`) — identical labels in both arms, so they are not byte-identity claims either way. After the flip, re-swept on the pristine rebuild: **new default vs pre-flip default = 0 movers / 529 rows, byte-identical.** The template-side gates are `!g_rt_fragment_emit || _b1c*` and `g_rt_fragment_emit` is 0 at m4 compile time, so the disjunct is structurally unreachable there — the measurement confirms the structure rather than merely trusting it. Independently corroborated: **all three RULES step-4 regens report "No changes"** (`util_regen_{benchmark,feature,demo}_s_artifacts.sh`).

## The flip, and the proof it IS the arm that was measured
Three sites flipped to the house idiom `(e && *e == '0') ? 0 : 1` (the KW-6 precedent at `keywords.c:137`); `SCRIP_B1C_PARITY=0` restores pre-flip behaviour verbatim, preserving the BASELINE-ARM law. Pristine rebuild, then the whole 6-suite board re-run **at the flipped default** and joined row-for-row against the measured `=1` arm: **1024 of 1024 identical, with one exception that is proven noise** — `probe/m1/m1_arbno_capture_call_bracket.sno` read SIG4/PASS where the `=1` run read SIG11/PASS. It is nondeterministic in BOTH arms: 16 runs (8 at default, 8 at `=0`) gave 6×SIG11 + 2×SIG4 each. It is the already-red s145 arbno-capture-bracket blocker changing crash FLAVOUR, in a program that crashes identically before and after; it is not a mover and not caused by the flip. Witnesses at the flipped default, m3: `b1c_e_plain` **PASS**, `b1c_cross_medium_concat_seam` **PASS** — the DONE-WHEN pair. Both read SIG11 under `=0`.

## Two witnesses minted (corpus `probe/b1/`)
`e_plain` was named in the DONE-WHEN but existed only as prose in FINDING s164 — it is now checked in as **`b1c_e_plain.sno`** with its oracle `.ref`, together with its passing control **`b1c_m_plain.sno`** (the same pattern main-built). Oracle output for both is `PC ran / match`, which reproduces the s164 table exactly. The pair is the sharpest B1c discriminator in the corpus: identical semantics, one EVAL-built and one main-built, and at the pre-flip default the EVAL-built one was the only member that crashed.

## ⛔ What this flip does NOT fix — both already own queue rows, neither is a regression
- **R1 / row `b1c-m4-seam`:** every m4 column above is unchanged. m4 still SEGVs at the seam in both arms; the parity work is m3-only in effect.
- **R2 / row `b1c-retreat`:** the three DIFF rows are the routed retreat family — they stop crashing and start answering `match` where the oracle retreats to `nomatch`. **A crash became a silent wrong answer on those three.** That is a real change in failure MODE and is called out here rather than buried in the mover table: it is not a board regression (SIG11 and DIFF are both FAIL, and no passing program moved), but a silent wrong answer is the more dangerous shape, so row `b1c-retreat` should be read as raised in priority by this flip, not merely inherited.

## Gates
`test_gate_emit_no_lang.sh` **green** (LANG-BLIND). BOTH-MEDIUM ratchet: **29 guard sites, ceiling 29, delta 0** (measured at `f44be5f1`; queue row 13 `medium-retire` landed under me mid-session and retired 22 of those sites, so the live ceiling is now lower — my diff adds zero `MEDIUM_`, so delta 0 holds on either baseline) — my diff adds zero `MEDIUM_`; `bb_*.cpp` count is identical at HEAD and worktree. `test_gate_template_medium_invisible.sh --strict` prints its pre-existing WIP baseline (12 raw-byte producers in `bb_glue_flat.cpp`/`xa_flat.cpp`) — neither file is touched here, and the ratchet the RULES banner governs is at its ceiling, not above it. Regens ×3 clean. Oracle verified alive before the first verdict (the `x64` clone was ABSENT on arrival at this seat root — the false-all-FAIL trap CLAUDE.md names; cloned and smoke-tested first).
