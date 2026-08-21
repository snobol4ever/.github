# FINDING 2026-08-21 (seat2, Claude Opus 5, PZ-0) — PROLOG HAS **ZERO** ζ SPINE AT HEAD, ONE DELIBERATE TAUTOLOGY GATES 86% OF ITS RUNS, AND ITS KILLSWITCH IS VACUOUS

Measured at SCRIP `d2ade229`, `make pristine` rc=0, RT_OPT `-O0`, corpus `f34388fd`. New instrument: `scripts/util_pl_zd_arm_census.sh`. New witnesses: `corpus/probe/plz/` (9 programs) with `.ref` oracles minted from a **live GNU Prolog 1.6.0** built this session from `/home/resources/gprolog-master` — the first live Prolog oracle this campaign has had.

## 1. ⛔ THE INSTRUMENT TRAP, CAUGHT BY INJECTION BEFORE IT WAS PUBLISHED
`SCRIP_ZD_DIAG=1` prints **only** the refusal line (`[ZD] run … REFUSED at i=N (KIND op=K)`, emit.cpp:2438). An ARMED run prints **no `run` line at all** — it prints one `[ZD] h=.. r=.. i=..` line PER NODE (emit.cpp:2434). A census that counts `^\[ZD\] run` and calls the remainder ARMED therefore yields **ARMED=0 for every language, always** — a structural zero that reads exactly like a measurement. My first census did this. It was caught by the mandated injection (RULES/goal law: falsify every zero) and the counter now reads armed runs at their first node (`r=0`). Falsified BOTH directions before any number below was believed: SNOBOL4 `m1_alt_arm2_cap.sno` → ARMED=2 REFUSED=0; Prolog `plz_p2` → ARMED=0 REFUSED=2. **The trap is now documented in the script's own header so the next seat cannot re-spend it.**

## 2. THE CENSUS (214 programs = `corpus/programs/prolog/*.pl` + `corpus/benchmarks/prolog/bench/*.pl`, compile-only)
| arm | ARMED | REFUSED | refusal attribution | position |
|---|---|---|---|---|
| **default (shipped)** | **0** | **736** | `IR_CALL_BUILTIN_PROLOG` 695 · `IR_VAR_REF` 22 · `IR_LIT_STRING` 19 | **736 of 736 at i=0** |
| cells (`SCRIP_PL_CELLS=1`) | 100 | 636 | **`IR_VAR_REF` 635** · `IR_CALL_BUILTIN_GEN` 1 | i=1 ×494, i=2 ×52, i=0 ×22, i≥3 ×68 |

**⭐ THE HEADLINE: at the SHIPPED default, Prolog has NO ζ SPINE AT ALL — zero armed runs out of 736, every one refused at its FIRST node.** The eight PL-ZK admission arms (emit.cpp:2237-2245) are each gated on `g_emit_cfg->pl_cells_graph`, which only `pl_cells_stamp` sets and only under opt-in `SCRIP_PL_CELLS=1`. The default (zframe) arm never sets it, so every PL-ZK arm is unreachable in the shipped compiler. **The "twin-arm" framing in every Prolog doc is therefore misleading: it is not two storage embodiments competing — it is one embodiment (zframe/FRQ) plus an opt-in that almost nothing reaches.**

## 3. ⭐⭐⭐ THE GATE IS ONE KIND, AND ITS GUARD IS A DELIBERATE TAUTOLOGY
`emit.cpp:2064`, Prolog half of the `IR_VAR_REF` arm, verbatim:
```c
return (_plvr && g_emit_cfg && g_emit_cfg->pl_cells_graph && !g_emit_cfg->pl_cells_graph) ? 1 : 0;
```
`X && !X` — **the arm can never return 1.** Provenance is honest and documented: `069c2fd8` (PL-ZK-5B s13, 2026-08-09) says so in its own message — *"VAR_REF Prolog admission gated off via tautology (!pl_cells_graph && pl_cells_graph = always 0) pending correct TERM_VAR materialization in a follow-on sub-rung"* — with the architectural reason: **Prolog variables are heap `Term*` cells requiring unification and trailing; a frame-slot copy yields NULVCL for fresh vars and an Icon NAMETRAP is rejected outright.** Not a typo. A placeholder that has stood 12 days.
**THREE CONSEQUENCES, AND THE THIRD IS NEW:**
(a) **The killswitch `SCRIP_ZD_PL_VR` IS VACUOUS** — it reads the env into `_plvr` and the expression is false regardless. A seat A/B-ing it measures nothing and would read "no effect" as "the arm is inert", the s68 vacuous-gate class exactly. Any doc calling it a live knob is wrong.
(b) **The cost was never measured until now: this one conjunct gates 635 of 736 runs = 86%.** The ladder called ZK-5B "the live blocked rung" and scheduled it as a late cleanup; the measurement says it is *the* gate. Its own commit predicted the mechanism (*"predicates with variable args get flat_all_zd=0 → FRQ fallback"*) — in Prolog that is nearly every predicate, which is why the number is 86% and not 10%.
(c) **VAR_REF admission and γ-RETAIN are ONE PROBLEM, not two.** A logic variable must survive binding, backtracking and trail-unwind; a spine cell that the γ-exit RELEASES (`add rsp,kt`, xa_flat.cpp) cannot hold one — which is precisely why the s13 seat could find no correct materialization and reached for the tautology. **Under the SN4 law (α carves, ω tears down, γ RETAINS) a retained spine cell IS a WAM environment slot**, and conditional trailing (`Word_Needs_Trailing`: trail only bindings older than the newest CP — gprolog `wam_inst.h`; SWI `GTrail`) is what makes it sound. So PZ-4 (γ-retain) is not merely the smoke-test fix: **it is the enabling precondition for the 86% gate**, and the two must be planned as one pair. The banked PL-TRAIL-COND feature rung is its third member.

## 4. WATERMARK AT `d2ade229` (pristine, all boards run live this session; the conversion's floor)
smoke **3/5** (clause, recursion FAIL all 3 columns) · honest **PASS=107 FAIL=0 ABORT=0 ORACLE_CRASH=78** · rung **interp 110/164 · compile 109/164** · bench-22 not re-run this rung.
⚠ **INTERP REGRESSED 113 → 110 since s166** (`c2ce75b1`, 28 sessions of sibling shared-emitter landings); compile unchanged at 109. Not chased this rung (PZ-0 is a census); recorded as the floor and as a bisect candidate against sibling landings, canary-style.

## 5. THE NINE WITNESSES vs LIVE gprolog 1.6.0 (`corpus/probe/plz/`, both modes)
| witness | m3 | m4 | oracle |
|---|---|---|---|
| p1 single clause | PASS | PASS | `a` |
| p2 two-clause first solution | FAIL rc=0 **blank** | FAIL rc=0 blank | `a` |
| p3 fail-driven 3 clauses | FAIL **rc=139** | FAIL rc=139 | `a b c` |
| p4 recursion+cut | FAIL rc=0 blank | FAIL rc=0 blank | `3 2 1` |
| p5 inline disjunction, fail-driven | FAIL **rc=139** | FAIL **rc=132** | `a b` |
| p6 member/2 backtrack | FAIL rc=139 | FAIL rc=139 | `1 2 3` |
| p7 cut commits first clause | FAIL rc=0 blank | FAIL rc=0 blank | `a` |
| p8 cut-then-fail barrier | FAIL **rc=132** | FAIL rc=0 **`yes`** | **`no`** |
| p9 guard then cut | FAIL rc=139 | FAIL rc=0 blank | `2` |
**⭐ p8 IS AN m3≢m4 DIVERGENCE *AND* A WRONG ANSWER:** m3 SIGILLs; m4 exits 0 printing `yes` where the oracle prints `no` — i.e. `t(X), !, X > 2` committed to the wrong clause and then reported success. A silent wrong answer on cut is worse than either crash and it is invisible to any board that only counts crashes. p5 also splits the modes (139 vs 132). **The cut/barrier class has no correct arm in either mode** — consistent with §3(c): cut cannot truncate choice points that live in C-heap stacks the emitted code never owns.

## 6. WHAT PZ-0 CHANGES IN THE LADDER
The census was supposed to name the next rung and it named a different one than the charter guessed. **PZ-1 becomes TERM_VAR MATERIALIZATION + γ-RETAIN AS ONE PAIR** (the 86% gate and its precondition), planned together, seeded by hand per the C5 discipline and ruled on by Lon before lowering changes; the clause-dispatcher re-lower moves behind it. ZK-5B's s14 falsification ("Option A as implemented, green 6→0") stands as a falsification **of the old substrate only** — it was measured against a γ-releasing frame, i.e. against the condition §3(c) now names as the reason no materialization could work. Re-derive, never re-apply from memory; discriminating witness first (`plz_p2`/`plz_p6` discriminate; `app/3`/`two.pl` do NOT — s14 correction of record).

## 7. PZ-0(d) — THE BUG FINDER IS BLIND TO PROLOG, AND THE BLINDNESS IS THE SAME FACT AS §2
Under `SCRIP_ZSM=1 SCRIP_ZSM_ALL=1 SCRIP_ZSM_BSKEW=1`, m3: `plz_p1` **0 ZSM events**, `plz_p2` **0 events**; control `m1_alt_arm2_cap.sno` **11 events** on the identical flags. The instrument works; Prolog is invisible to it. So Lon's s196 P2/P3 tooling — the four-port state machine, the RSP expected-value check, the β-skew exceptions list, and the automatic bug finder built on the ZSM ring — **cannot see a single Prolog box today**, and no Prolog defect can be hunted the way the pattern defects were.
The master gate `x86_zdp_rbp_on()` (x86_asm.h:2003) is an env read only — NOT gated on ζ arming — so the blindness is in the emission PATH Prolog's boxes take (they are not going through the `x86_zdp_rbp_at(port)` port hooks that GLUE-3 `785e3a41` made the sole rsp road), not in the gate. ⛔ The exact mechanism is NOT chased here (END-OF-CONTEXT LAW: mint the fact, route it, stop) — it is PZ-7's opening question. **The likely shape, stated as a hypothesis to be measured and not as a finding: no ζ ⇒ no port hooks ⇒ no ZSM, in which case the instrument gap closes as a SIDE EFFECT of PZ-1 rather than needing its own cure.** Measure it at PZ-1's first armed run: if armed Prolog runs start emitting ZSM events with no instrument edit, the hypothesis is confirmed and PZ-7(d) shrinks to an exceptions-list census.
