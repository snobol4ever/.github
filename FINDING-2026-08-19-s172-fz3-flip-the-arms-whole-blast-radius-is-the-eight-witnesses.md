# FINDING s172 (seat3, Opus 5, queue row `fz3-flip`) — `SCRIP_FENCE0_WHACK` IS **DEFAULT ON**. THE "ZERO CORPUS COVERAGE" OBJECTION IS NOW A MEASURED NUMBER, AND THE NUMBER IS: THE ARM'S ENTIRE BLAST RADIUS OVER 1034 PROGRAMS IS THE 8 `probe/fz` WITNESSES AND NOTHING ELSE

**Front:** GOAL-SNOBOL4-100 · FENCE front · FZ ladder. Queue row 27 `fz3-flip`. DONE-WHEN: *"flip pushed; 8 witnesses + 5-lock `test_gate_fz_release.sh` green at armed default; corpus non-regression; FINDING."* All four met.
**Trees:** SCRIP `1ac779ad` (this commit) · corpus `534e2c9c` · .github (this commit). Oracles smoke-verified alive BEFORE any verdict (`sbl -b` and `snobol4 -f` both round-tripped a hello). Every number below was taken on a `make pristine` build — driver AND `out/libscrip_rt.so` from one commit (HQ-27; the emitter lives in the `.so`, so a driver-only swap measures nothing).

## 0. PROVENANCE — THE FLIP IS A RULING, NOT A SEAT TALKING ITSELF INTO IT
This seat **refused to arm at s168** and escalated as `q-fz3-arming`. HQ's first reply *held the default OFF* and affirmed the refusal as the record. The second, superseding message is what is executed here:

> *"FZ-3 FLIP RULING (Lon delegated the desk to HQ): FLIP `SCRIP_FENCE0_WHACK` DEFAULT ON — your witnesses are live-oracle-refs and SPITBOL is the authority (Lon: 'Use SPITBOL as an Oracle... we will be fine tuning'); the killswitch stays for instant retreat. Own attributable commit, 5-lock gate green at armed-default, corpus non-regression."*

Both messages are quoted so the record shows the sequence. The commit is its own, attributable, and folds in nothing.

## 1. THE THING THAT WAS ACTUALLY OWED
The s168 cursor stated the case AGAINST arming in one sentence, and it was an **assertion with no measurement behind it**:

> *"the corpus contributes exactly nothing — armed ≡ disarmed on all 510 programs because the arm emits no release anywhere in it"*

That is a blast-radius claim, and the whole flip stands or falls on it. It had never been measured. It is measured here, over **1034 programs** (crosscheck 318 · probe 534 · demo/feat/smoke/beauty_suite/parser 182), in **both media**, on **pristine builds**.

## 2. THE A/B — THREE DIFFERENTIALS, NOT ONE

| differential | medium | result |
|---|---|---|
| DEFAULT vs `SCRIP_FENCE0_WHACK=0` | m4 TEXT `.s` md5 | **9 movers / 1019 comparable** — 8 are the 8 `probe/fz` witnesses; the 9th is proven noise (§3) |
| DEFAULT vs `SCRIP_FENCE0_WHACK=1` | m4 TEXT `.s` md5 | **1018 / 1019 IDENTICAL** |
| DEFAULT vs `=0` **and** DEFAULT vs `=1` | m3 BINARY behaviour | **0 real movers / 1034**, both |

15 rows are `NOCOMP` — `--compile` returns rc 1 in **both** arms identically, so they are not a byte-identity claim in either direction. They are listed rather than dropped: `crosscheck/coverage/coverage_sno_nodes` · `probe/ab_nret_lvalue` · `probe/define/dyn_define_1` · `probe/m1/m1_nret_cap` · `probe/nret/nret_cond_nondeferred` · `probe/opsyn/{d_unary,opsyn_builtin_target,opsyn_unary_target}` · `beauty_suite/ShiftReduce` · `demo/expression` · `feat/f13_eval_code` · `smoke/{empty_string,hello,multi,null}`.

**The second row is the one that makes this a flip and not a hope.** The shipped default is not merely *believed* to be the arm that was measured — it is proven to BE it, program for program, on a rebuilt tree.

## 3. EVERY APPARENT MOVER DISPROVEN BY HOLDING THE ARM FIXED — NOT BY ARGUMENT
The honest hazard in a differential sweep is a flaky program masquerading as a mover. The test used here changes **nothing**: run the same program 10 times at the **same** arm, env var never touched. Seven programs vary anyway.

| program | 10 runs, DEFAULT arm, env untouched |
|---|---|
| `probe/leafsib/leafsib_rem` | 8×rc139 + 2×rc134 |
| `probe/leafsib/leafsib_tab` | 9×rc139 + 1×rc134 |
| `probe/leafsib/leafsib_break` | 9×rc139 + 1×rc134 |
| `probe/m1/m1_arbno_capture_call_bracket` | 9×rc139 + 1×rc132 — the row s169 already characterised |
| `programs/snobol4/demo/calculator-1` | two distinct outputs, 6/4 |
| `programs/snobol4/demo/calculator-2` | two distinct outputs, 5/5 |
| `programs/snobol4/demo/json` | two distinct outputs, 8/2 |

The sweeps convicted themselves independently: `m1_arbno_capture_call_bracket` read `132→139` in one differential and `139→132` in the other, which can only mean the **default** arm moved.

**The m4 outlier is sharper still.** `programs/snobol4/parser/unary_not.sno` — the whole program is `x = ~BREAK(nl)` — gives **6 DISTINCT `.s` md5s in 6 compiles at a FIXED arm**, and the variance is one line: `.S0: .string "\035J\003"` vs `"\201v\002"` vs `"#N"` … It contains **no FENCE** and its `.s` emits **no `match_fence0` box at all**, so the release is *structurally absent* from it. It cannot be an FZ mover under any reading. Routed in §6 as its own defect.

## 4. GATES AT THE ARMED DEFAULT
- **`test_gate_fz_release.sh` GREEN, all 5 locks, rc 0.** LOCK 1 (killswitch retreat) 8/8 · LOCK 2 no over-release, re-derived from the emitted asm with no golden pinned · LOCK 3 (the FZ-3 tripwire) 8/8 ARMED, m3 **and** m4, oracle-identical · LOCK 4 the cut rebases staged offsets and moves nothing else (16–80B released, 1–5 cut lines, 0–2 offsets rebased per witness) · LOCK 5 the `op_zpat` road 7 PASS + 1 SKIP (`fz8`'s road is red DISARMED too, which is not an FZ fact).
- `test_gate_emit_no_lang.sh` **green** (LANG-BLIND).
- BOTH-MEDIUM ratchet **3, ceiling 3, delta 0** — this diff adds zero `MEDIUM_`.
- **⭐ RE-PROVEN AFTER THE PUSH, per HQ-27.** The commit rebased onto two arrivals (`418778eb` medium-retire rung 4, `376ecf24` M1-R3 beauty-m3-zls), so every gate above was re-run on a FRESH `make pristine` at the pushed HEAD `1ac779ad`: **FZ gate GREEN rc 0, 16 `m3=PASS m4=PASS` pairs** (8 witnesses × LOCK 1 disarmed + LOCK 3 armed, zero FAIL/MISS/OVER-RELEASE lines), LANG-BLIND green, ratchet 3/3 delta 0. The numbers in §2/§3 were taken on the pre-push pristine build of the same diff.  **Then re-proven a THIRD time at the true HEAD `aaf9d96b`** (M1-R4b landed on top of the flip and touches `emit.cpp` too): fresh `make pristine` rc 0, **FZ gate GREEN rc 0, 16/16 PASS pairs, zero FAIL/MISS/OVER-RELEASE lines**.  The armed default is green on the tree as shipped, not merely on the commit that introduced it.
- **All 5 `.s` regens report `changed=0`**: crosscheck `emitted=484 changed=0`, programs `emitted=623 changed=0`, demo/feature/benchmark "already current". This corroborates the blast radius from a completely different direction — no tracked artifact in those sets contains a live FENCE release.

## 5. WHAT THE FLIP DID *NOT* DO
- **The killswitch stays, and it stays a VERDICT.** `SCRIP_FENCE0_WHACK=0` restores the pre-flip box byte-for-byte, and LOCK 1 keeps testing it every run. An escape hatch nobody tests is not an escape hatch. LOCK 1's header no longer calls the disarmed arm "the shipped default" — it now says it is the retreat path and why it still holds a verdict.
- **Two banners in `bb_match_fence0.cpp` are stamped as HISTORY, not deleted:** *"DEFAULT OFF — and s166 found the SECOND reason it must stay off"* and *"⛔⛔ FZ-3 IS THE REAL WALL, AND IT IS WHY ARMING BY DEFAULT IS STILL REFUSED"*. FZ-3 landed at s168. Left alone they would have told the next seat the arm is still refused.
- **No new global, no `IR_t`/`BB_t` field, no template-side arm.** The flip is one expression, moved to the house idiom `(e && *e == '0') ? 0 : 1` (KW-6 precedent).

## 6. ⛔ ROUTED — A DEFECT CLASS THIS SWEEP SURFACED THAT IS NOT ABOUT FZ AT ALL
**SEVEN CORPUS PROGRAMS ARE NONDETERMINISTIC AT A FIXED ARM, AND ONE IS NONDETERMINISTIC AT COMPILE TIME.** This matters far beyond this rung: **any board that grades these rows is reading noise**, and any future A/B that does not hold-the-arm-fixed first will manufacture movers out of them. Two shapes:
1. **Runtime (6 programs):** the `leafsib_*` family flips SIG11↔SIGABRT, and `calculator-1`/`calculator-2`/`json` produce two different *successful* outputs (rc 0 both times) — the more dangerous shape, since a board scores it PASS or FAIL by coin flip.
2. **⛔ Compile time (1 program):** `parser/unary_not.sno` emits a **different `.s` on every compile** — a garbage string literal in `.S0`. Mode 4 is not reproducible for `x = ~BREAK(nl)` (unary `~` applied to an unassigned variable). This one is worth a rung: a compiler whose output is not a function of its input breaks every md5 sweep, every `.s` artifact, and the whole KILLSWITCH-BYTE-IDENTITY law that governs codegen changes.

**Recommend HQ mint a row for (2) and treat (1) as a standing measurement hazard** — the fleet's A/B protocol should require the hold-the-arm-fixed control before any mover is reported.

## 7. WHAT A SEAT INHERITING THE FENCE FRONT SHOULD KNOW
The release is now ON in every build. If a FENCE-bearing program ever answers wrong, **the first move is one env var, not a bisect**: `SCRIP_FENCE0_WHACK=0` reproduces the pre-flip compiler exactly. If that fixes it, the defect is in the release plan (`fence0_release_bytes()` in `emit.cpp`) or in the depth threading (`zd_plan`), and LOCK 4 is the lock that will name which. If it does *not* fix it, the fence is innocent and the arm is a red herring.
