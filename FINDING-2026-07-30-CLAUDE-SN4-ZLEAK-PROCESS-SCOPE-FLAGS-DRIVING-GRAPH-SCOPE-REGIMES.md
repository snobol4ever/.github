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
