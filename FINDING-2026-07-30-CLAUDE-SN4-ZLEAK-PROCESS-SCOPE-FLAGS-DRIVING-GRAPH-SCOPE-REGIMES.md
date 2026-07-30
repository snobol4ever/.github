# FINDING 2026-07-30 (s21x-r) — THE STF "DEFECT" WAS A PROCESS-SCOPE PLANNER FLAG, NOT A BOX TEMPLATE; AND THE ARMED PATH WAS NEVER BROKEN

**Session:** s21x-r · **Goal:** GOAL-SNOBOL4-BB.md · **Lon directive:** "Complete ZETA CELLS on the RSP FORTH-style STACK." / "All your choices."
**SCRIP:** `efb72d69` (ZLEAK-1) · `ed9ea588` (ZLEAK-2) — **corpus:** `8cfe632c` (D2 probe + ref)

---

## 1. THE HEADLINE

`SCRIP_STMT_FRAME=1` cost 41 m4 programs. Every prior session read that as a defect in the code the gate EMITS. It was not. It was one `static int` in the PLANNER, read once from `getenv`, applied to all 316 programs while the emit-time verdict armed only 31.

**The armed path was correct the whole time.** s21x-q's NEXT(1) — "find the real STF defect in the ARMED path; the armed set is arithmetic, so bisect there" — would have sent a session to bisect 31 programs that all pass.

---

## 2. THE MEASUREMENT THAT DECIDED IT (the step s21x-q named as cheap+decisive and did not run)

Both sets re-derived this session per CENSUS SHELF LIFE, not cited:

| set | size | composition |
|---|---|---|
| ARMED (`-> live=1`) | **31 programs / 31 live graphs** | output · assign · concat · arith · goto. ZERO pattern programs. |
| m4 REGRESSION under STF=1 | **41 programs** | pattern · capture · BAL · W06/W07. ZERO arithmetic. |
| **INTERSECTION** | **0** | **DISJOINT, not merely proper.** |

All 31 armed programs **PASS** under STF=1. 31 live graphs across 31 programs = one each, so the census does **not** undercount — s21x-q's hypothesis (b) is dead and hypothesis (a) holds in its strongest form.

---

## 3. ROOT CAUSE — TWO AUTHORITIES, ONE LEVEL OUT FROM s21x-o

`zls_build` takes a per-graph `g`. Its elide switch did not:

```c
{ static int eon = -1; if (eon < 0) { ... if (sf && *sf == '1') eon = 0; } }   /* zeta_storage.c:507 */
```

`static` ⇒ computed ONCE per process. So s21x-e's forced elide-off applied to **all 316 programs**, while `g_emit.flat_stmt_frame` (emit.cpp:2536) armed **31**. The 285 DECLINED graphs got `zls_grant` instead of `zls_grant_elide` and a skipped `zls_mark_value_refs` — **plan-side damage with no emit-side regime to justify it.**

This is **ALL-OR-NOTHING PER GRAPH violated from the planner side**, and it is exactly the s21x-o root cause one level out: *the ELIDE authority is process-scoped, the REGIME authority is graph-scoped, and neither can see the other.*

Ordering is why it was structurally invisible: `ir_drive_slot_assign` → `zls_build` runs at drive-slots time, **before any proc emits** (scrip.c:357, lower_snobol4.c:2411). The planner cannot consult a verdict that does not exist yet, so it consulted the env instead — and the env has no graph in it.

---

## 4. THE INSTRUMENT (the reusable part — this is how the class gets caught)

> **After the regime is honest, EVERY graph reporting `live=0` MUST be BYTE-IDENTICAL between regimes. Any declined graph whose `.s` differs is BY DEFINITION a process-scope leak.**

Per program: count `-> live=1` under `SCRIP_STF_DEBUG=1`; diff default `.s` against gated `.s`. It needs **no theory of the mechanism** and **cannot miss one**. It found ZLEAK-2 immediately after ZLEAK-1 closed, and it is what should be run before any future default-flip.

Sweep progression:

| state | declined | leaking |
|---|---|---|
| before ZLEAK-1 | 285 | **285** |
| after ZLEAK-1 | 285 | **24** |
| after ZLEAK-2 | 285 | **0** ← ALL-OR-NOTHING PER GRAPH now provably holds corpus-wide |

Armed graphs still differ 31/31 throughout — **the null is not vacuous, the regime genuinely fires.**

---

## 5. ZLEAK-2 — SEQ-CELL, AND IT WAS 100% LEAK

Same shape one line down (`zeta_storage.c:737`), aggravated by polarity: `on = (a=='1' && !(z=='0'))` made SEQ-CELL **ACTIVE BY DEFAULT** under `SCRIP_STMT_FRAME=1` — contradicting s21x-l's own record ("SEQ-CELL dormant"). **Code and doc disagreed; the doc was right.**

All 24 residual leaks attributed by killswitch (`SCRIP_SEQ_CELL=0` → all 24 byte-identical). Diffs came in units of 7 lines = one flat `[rbp+N]` slot becoming `sub rsp,16` / `[rsp+0]` / `add rsp,16`, N occurrences per program.

**SEQ-CELL affects ZERO of the 31 armed graphs** — it fired ONLY where the regime declined. Pure leak, no armed customer to protect. Fix = explicit opt-in `SCRIP_SEQ_CELL=1`; feature NOT deleted (opt-in still emits the cell).

---

## 6. WHAT THIS RETIRES

- **s21x-q NEXT(1) is RETIRED.** No defect in the armed path.
- **s21x-p's D2 root cause is RETIRED (both halves, on top of s21x-q retiring the first half by dormancy).** s21x-p: *"the probe HEAP-EXHAUSTS with STF alone"* → the probe returns `A` in ALL FOUR regimes at HEAD. The heap exhaustion was the elide leak.
- **"roman-under-gates segv" is RETIRED.** Recursive roman returns `MDCCLXXVI` under default, STF, CALL2BB, and STF+CALL2BB.
- **"Any combo including `SCRIP_STMT_FRAME=1` remains OFF-LIMITS" is FALSIFIED** for all three measured combos (§7).
- **The 31-vs-44 "unreconciled units" note is RESOLVED.** 44 is **not** armed *statements*. It is armed *programs* measured with `SCRIP_SUBJ_CELL=1` also on — same unit, different env, matching s21x-k's own "31→44" line. Denominator 316 both times.

---

## 7. WATERMARK — ALL REGIMES, RE-DERIVED AT CLOSE (317 programs, incl. the new D2 probe)

| regime | m3 | m4 | DIVERGE | armed |
|---|---|---|---|---|
| **DEFAULT** | 266/51 | **265/50/2** | 3 {140,141,W04} | — |
| `SCRIP_STMT_FRAME=1` | 265/52 | **265/50/2 fail set IDENTICAL** | 3 (same members) | 31 |
| `+SCRIP_SUBJ_CELL=1` | 265/52 | **265/50/2 fail set IDENTICAL** | 3 (same members) | 44 |
| `+SCRIP_CALL2BB=1` | **268/49 (+2)** | **265/50/2 fail set IDENTICAL** | **1 {W04}** | 58 |
| `SCRIP_BB_ALLOC=0` killswitch | 312/4 | 312/2/2 | 2 {140,141} | — |

*(pre-fix, for contrast: STF=1 was m3 230/86 · m4 223/91/2 · DIV=6.)*

⭐ **CALL2BB FIXES 140 AND 141 IN MODE-3** — the two divergences s21x-q recorded as surviving into the killswitch baseline, i.e. believed allocator-independent and immutable. They are neither. The two-BB constant-folded DEFINE world resolves them, and DIVERGE drops 3 → 1 with only `W04_arbno_basic` (the known allocator-induced one) left. **This is direct evidence for NEXT(3), the FLIP + DELETE.**

---

## 8. STILL OPEN IN THE CLASS (audited, NOT fixed — they are the next rung)

Same `static`-from-`getenv` shape, same missing per-graph verdict, currently gated behind a second env so they are dormant by default. Under their own env combinations the instrument reports:

| site | env combo | armed | declined | **leaks** |
|---|---|---|---|---|
| SUBJECT-CELL registration loop (`zeta_storage.c` ~445) | `STMT_FRAME+SUBJ_CELL` | 44 | 272 | **149** |
| `fc_call_ok` (`zeta_storage.c` ~409) | `STMT_FRAME+CALL2BB+CALL2BB_FC` | 58 | 258 | **77** |

Both are currently **benign** (fail sets identical to baseline) but both are latent, and SUBJ_CELL sits directly on the match-family admission path the ladder is heading for. **Any measurement previously taken under these envs conflated regime effects with leak effects** — which is the most likely reason the D2 autopsy chased a match-release weld that was never the fault.

⚠ **These two are NOT the same easy shape as ZLEAK-1/2.** SEQ-CELL had zero armed customers, so opt-in cost nothing. SUBJ_CELL and CALL2BB **do** have armed customers (they arm 44 and 58 graphs respectively, all differing), so the fix is not a polarity flip — it needs the verdict plumbed to the planner, or the grants deferred to the existing PS-3 s153 **late pass** (`zls_build` already has one, invoked from `emit_chain` at each graph's emission entry — that is the natural home, and it is where a per-graph verdict IS available).

---

## 9. LAW PROPOSED

**NO PROCESS-SCOPE FLAG MAY DRIVE A GRAPH-SCOPE REGIME.** If a planner decision must agree with an emit-time per-graph verdict, it is computed per graph or deferred to the late pass — never cached in a `static` from `getenv`. A `static int on = getenv(...)` inside a function taking an `IR_graph_t * g` is the greppable signature of the defect class. Completion test = the §4 sweep reporting 0 leaking declined graphs under every gate combination the session touches.

---

## 10. ZLEAK-3 SPECIFIED (SUBJ_CELL + fc_call_ok) — measured, de-risked, deliberately NOT implemented this session

**Why it is not the ZLEAK-1/2 shape.** SEQ-CELL had zero armed customers, so opt-in cost nothing. SUBJ_CELL and `fc_call_ok` arm 44 and 58 graphs respectively and **all of them differ** — a polarity flip would delete a live feature.

**Why a blanket consumption gate is wrong.** The ASSIGN value-spine loop is **not** env-gated: it populates the same `fvr` registry on the DEFAULT path (12 cell refs in default `039_pat_any`, 5 in `023_arith_add`). The SUBJECT loop calls the **same** `fc_vlit_register` / `fc_vread_register`. Nothing at emit time distinguishes a subject-registered node from an assign-registered one, so gating `fc_vread_fp`'s consumers on `g_emit.flat_stmt_frame` would break the default path.

**The circularity, named.** `emit_stmt_frame_scan` queries `fc_vread_fp` to DECIDE arming — under SUBJ-ARM-1 a head carrying a subject-cell registration is precisely what licenses the match statement to arm. The registration would need the arming verdict to avoid leaking. **Registry ⇄ verdict.** This is why the leak survived: it cannot be removed by moving a flag.

**The resolution: plan-time fixpoint — register → scan → unregister on decline.**
`emit_stmt_frame_scan(g, entry)` is a pure function of (graph, entry, registry): a BFS over the closed kind whitelist consulting the registry, with no emit-time globals in its body. It is therefore callable at plan time. Unregistration is already an established mechanism (the PS-3 s153 late pass declines wholesale and unregisters SEQ). The registry becomes a **proposal**; the verdict remains the **authority**.

⭐ **MEASURED — the fixpoint is complete, not partial.** Across the leaking declined graphs: **150 declined by the SCAN, 0 declined by a conjunct.** So the plan-time scan reproduces the emit-time verdict for 100% of the leaking population; there is no residue for the emit-only conjuncts (`flat_pat`/`flat_gen`/`flat_jmp_entry`/`gp`/`rc`/`np`) to mop up.

**⛔ PROVE THIS BEFORE CODING (the one blocking premise).** *Plan-time entry ≡ emit-time entry, and one graph gets at most ONE choke decision.* `emit_chain` runs per graph EMISSION and is called from several places (driver loops, `runtime_eval.c`, `bb_pat_build.cpp` — emit.cpp ~2531 names them); the census counted ~592 choke decisions across 316 programs. If a single graph is ever emitted twice, or entered at a different node, one plan-time decision cannot match every emission and the fixpoint mis-decides — which is precisely the s188 "mixed regimes inside one graph" disease. **Instrument the choke with a graph id and count decisions per graph first.**

**Fallback if the premise fails:** a tagged registry — mark subject-registered nodes at registration, gate only those at emit.cpp:889 (`op_fc_disp`) and emit.cpp:1281 (`op_subj_cell`). ⚠ Gating consumption alone is not sufficient by itself: the cell lifecycle has claim/pop touch points (`fc_vwpop_register` and the pop hooks), and gating reads without gating pops desynchronizes rsp. Enumerate every touch point before choosing this arm.

**Premise already proven this session (it is what makes an emitter-side fix possible at all):** under SUBJ_CELL a declined graph's prologue carve is **unchanged** (232 both regimes on `039_pat_any`) and the subject producer's flat slot is merely **orphaned** (`[rsp+176]` refs 2 → 0). The storage form changes; the allocation does not. So a declined graph can be returned to the flat slot without re-planning its frame.

---

## 11. ZLEAK-3 PREMISE RESOLVED — and the guard caught what the measurement missed (SCRIP `30c96e72`)

**Instrument:** `g=%p entry=%p` added to the `[STF]` choke line, inside the existing `SCRIP_STF_DEBUG` gate (zero default-path cost). Everything below follows from it.

**Measured: 317 programs · 595 choke decisions · 527 distinct (program,graph) pairs.**

| premise | result |
|---|---|
| plan-time entry ≡ emit-time entry (**the strong form §10 asked for**) | ⛔ **FALSE** — 32 graphs emitted from MULTIPLE entries, up to **11** (`test_string`); all DEFINE / indirect-goto / EVAL shapes |
| **verdict stability** per graph | ✅ **0 violations / 32** |
| **arming implies single entry** | ✅ **44 armed decisions / 44 distinct armed graphs, 1:1**; ZERO multi-entry graphs armed |

**So §10 asked for the wrong premise.** The fixpoint does not need entry equality. It needs (a) the verdict to be stable per graph and (b) arming to imply a single entry — and both hold. One plan-time decision then matches every emission: scan from `g->entry` (IR.h:232); for a graph the planner would arm that is the only entry, and a graph it declines is declined at all of them.

**The guard.** Rather than trust an empirical regularity, it is now enforced: a per-graph verdict/entry table checked at the choke, regime-gated on `_stf` so the default path never executes it. **Warn-only by default** — a currently-benign violation must not become a hard failure — with `SCRIP_STF_STRICT=1` aborting for anyone working the rung.

### ⭐ It earned its keep immediately

Under `SCRIP_CALL2BB=1` the guard fires on **`1014_func_freturn`: VERDICT STABILITY VIOLATED, verdict 0 then 1.** The same graph declines at one emission and arms at another — latent **s188 mixed-regime disease**. It is invisible by every other signal: 1014 still matches its ref, and the CALL2BB m4 fail set is still identical to baseline.

**I had proven the premise under `SUBJ_CELL` and was one step from assuming it for `CALL2BB`.** It does not carry.

**Consequences:**
1. ZLEAK-3's fixpoint is **scoped to STF + SUBJ_CELL**. Do not extend it to CALL2BB until the instability is fixed.
2. **`1014_func_freturn` is the named reproducer** — `SCRIP_STMT_FRAME=1 SCRIP_CALL2BB=1 SCRIP_STF_STRICT=1 ./scrip --compile <it>` aborts on demand.
3. There is a **real latent ALL-OR-NOTHING PER GRAPH violation at the EMISSION level** (not just the planner level) sitting under CALL2BB, benign today. It should be fixed before the FLIP + DELETE defaults the two-BB world — which is otherwise the best-evidenced next rung (§7: CALL2BB fixes 140/141, DIVERGE 3→1).

**LAW (companion to §9):** a premise measured under one gate combination is not proven for another. Enforce premises with a guard at the choke rather than a census in a session log — the census cannot fire six months later, and the guard can. Watermarks unchanged by the guard: DEFAULT m3 265/52 · m4 265/50/2 · DIV=3; STF+CALL2BB m3 268/49 · m4 265/50/2 · DIV=1.
