# HANDOFF — BB-FIXUP 78th attended run (Opus 4.8) — 2026-06-14
## Scan gate lit (cross-goal one-token fix landed) · 77th-run retag premise FALSIFIED · retag held for a concrete reason

**Attendance:** Lon, `"What % … Continue."` ×N → `"It matters not that you make the decision. You are covered by many angles."` → `"Perform hand off."`

**Net SCRIP code:** ONE commit — a one-token **test-harness** fix to GOAL-ICON-BB's scan gate. **Zero** `bb_*.cpp`, zero emitter, zero runtime, zero IR.h. GRAND dirty **unchanged at 992**.

**Cursor:** STAYS `bb_call.cpp` (the FIX-3-iii retag is its only remaining work; this run found a *concrete* reason it cannot land yet, replacing the 77th run's vaguer pin).

**Repo tips:** SCRIP origin **`9902031`** · `.github` @ this commit.

---

## Session open / baseline

- SCRIP @ `89fc357` at open. Concurrents past the 77th's `7880ef1`: Pascal frame-var fix · Prolog NO-NEW-GLOBAL gate · Icon real-arith constant-fold. During the run, **`f3b1837`** (Raku grammar `.parse` end-to-end — `lower_raku.c` + `by_name_dispatch.c`, orthogonal to Icon scan) landed upstream and was rebased under → origin tip `9902031`.
- ENV: `install_system_packages.sh` (libgc-dev, nasm, bison, flex, libgmp-dev, m4, wabt) → `build_scrip.sh` → `make libscrip_rt` (builds to `out/libscrip_rt.so`).
- ⛔ **corpus ABSENT by default** in a fresh container — re-cloned `snobol4ever/corpus` (293 icon programs). The scan gate needs it.
- Baseline **GREEN**, matching the 77th ceiling exactly: SNOBOL4 7/7/7 · Icon 12/12/12 · Prolog 5/5/5; floors bin_t 0 / vstack 0 / icn_no_stack 0 / purity 1 (bb_call_write_slot); emit-blind 0; **GRAND 992 (136/96/40)**. The three orientation-time concurrents did not disturb the BB count.
- FIX-3-iii **inert prep** (`7880ef1`) intact at HEAD: `ir_is_scan_kind` (emit_bb.c:1848); `IR_SCAN_*` case-stacked onto `IR_CALL` at emit_bb.c 1514/2628/3309 + IR_interp.c 283/2383. Behavior-neutral by construction (the lowerer emits zero `IR_SCAN_*`).

---

## (1) LANDED — scan-gate token fix `9902031` (cross-goal)

`scripts/test_gate_icn_scan.sh:233`
```
- case "$dump" in *IR_GEN_SCAN*) ;; *) continue ;; esac
+ case "$dump" in *GEN_SCAN*) ;; *) continue ;; esac
```
`--dump-bb` strips the `IR_` prefix on **all** kinds (probe-confirmed: a scan program dumps `GEN_SCAN`, never `IR_GEN_SCAN`), so the corpus bucket filter matched nothing → N=0 → the gate's floors were unmeetable and it was **dark/red on bogus grounds**. The 77th run flagged this as GOAL-ICON-BB's to fix and named it the *precondition* for the retag. Lon's "you are covered by many angles, make the call" authorized the cross-goal correction — it is a pure test-harness fix, the gate is **not** in the BB-FIXUP commit battery, and nothing in the emitter/runtime/templates was touched.

---

## (2) ⛔⛔ 77th-RUN RETAG PREMISE FALSIFIED — the gate is RED even when lit

With the bucket live, the gate buckets **N=70** (37 corpus programs carrying `GEN_SCAN` + the rung-suite) and reports the TRUE baseline:

```
bucket: N=70 | m2 PASS=44 FAIL=26 | m3 PASS=9 FAIL=2 EXCISED=59 | m4 PASS=9 FAIL=2 EXCISED=59
FLOOR FAIL m3 9 < 11
FLOOR FAIL m4 9 < 11
```

- **84% of scan programs LOUD-EXCISE in m3/m4** (59/70 print `[SMX]` rc=0 — a *deliberate, tracked* bail-out: the scan mode-3/4 boxes aren't built yet; the ratchet expects "EXCISED→PASS deltas as future boxes light up").
- Only **9** scan programs emit working native code; the floor wants **11**.
- The 2 genuine non-excise FAILs — `scan_simple`, `scan_var` — fail in **all three** modes (m2 included), so they're pre-existing **interp-level** known-bad, fully orthogonal to any retag.

**The 77th plan was:** *ICON-BB lands the token fix → prove the retag against the now-GREEN gate.* That rested on a false premise. The gate is **not** green once lit and **won't be** until the excised m3/m4 boxes are built — a separate, larger ICON-BB effort.

---

## (3) ⛔ RETAG NOT LANDABLE THIS SESSION — concrete, code-grounded

This supersedes both the 77th's "wait for the token fix" *and* my own earlier "the pin is largely dissolved" nutshell — **that nutshell was wrong.** The discriminator is resolved (sval-keyed, dval untouched), but the *neutrality of relocating the decision* is not. Two findings from reading the emission code:

**(a) The scan-vs-call decision is split across two paths with inconsistent guards.**
- `emit_core.c` node-dispatch (467, `case IR_AUGOP: case IR_CALL:`) keys `g_icn_scan_regs_live && IR_LIT(nd).sval` → `bb_scan_*`, else falls through to `bb_call(nd)`.
- `emit_bb.c` flat-chain (2635–2720) keys `g_icn_scan_regs_live && IR_LIT(nd).dval == 3.0 && sval`.
- The dormant kind-cases the retag would activate — `emit_core.c` 503–511 (`IR_SCAN_POS`…`IR_SCAN_BAL`) — have **no guard and no `bb_call` fallthrough**; they emit `bb_scan_*` unconditionally.
- `g_icn_scan_regs_live` is a **dynamic** flag set to 1 only around the GEN_SCAN driver body (emit_bb.c 2002–2005).

So a neutral retag is **not** a mechanical emit→lower relocation. Activating the unguarded kind-cases requires the lower-time retag to fire *exactly* when both paths would have taken the scan branch — which forces a **semantic reconciliation of the `dval==3.0` discrepancy** between the node-dispatch and flat-chain paths, plus re-guarding the kind-cases (guard + `bb_call` fallthrough). That's a design decision, not a carve.

**(b) The proof harness is blind where the retag acts.**
Differential-parity certified the inert prep because inert prep flips **nothing**. The retag flips nodes, and its primary effect is on the **m3/m4 emission paths** — which 59/70 programs EXCISE, so they read `EXCISED → EXCISED` regardless and **mask** any emission drift. The differential is strong on m2 (44/26) but near-useless on exactly the m3/m4 paths the retag changes. Landing the retag on a blind differential would be cowboying it.

---

## (4) THE REAL UNBLOCK PATH (for ICON-BB + the next BB-FIXUP run)

**GOAL-ICON-BB lights the excised m3/m4 scan boxes.** That single move does two things at once:
1. Raises m3/m4 PASS well past the floor (11) → the gate becomes a *true* green acceptance gate.
2. Gives the differential **discriminating power** on the exact m3/m4 paths the retag touches.

Then the retag is **provable** rather than blind. The retag commit, when it comes, is:
- (a) `lower_icon` TT_SCAN **bsg-walk**: retag `IR_CALL` + scan-name sval → `IR_SCAN_*`, scoped to the scan body, keeping `dval`+`sval` (the 74th-run DEFINE-carve technique);
- (b) the **`dval==3.0` two-path reconciliation** (resolve the node-dispatch vs flat-chain guard inconsistency; either re-guard the kind-cases or prove scan-builtin nodes only appear in scan-live context);
- (c) DELETE the `emit_core.c` 467–479 live string block (503–511 kind-cases cover);
- (d) the RETAG-additional parallels: emit_bb 2541/2739/2847/2915 + emit_core 451 (arg-shape classifiers), 3083/3322 (chain-queue walkers), 2661 (tab-arg slot);
- proven by a **full scan-corpus m2/m3/m4 byte-identical differential** vs the inert-prep baseline; revert (keeping inert prep) if any gate regresses.

---

## Gates (at floors, pre/post, re-certified at `9902031`)
SNOBOL4 m4 7/7 HARD · Icon m2 12/12 HARD · Prolog 5/5 ×3 · prove_lower 0 rc=0 VACUOUS · purity 1 (bb_call_write_slot) · bin_t 0 · vstack 0 · icn_no_stack 0 · emit-blind 0. **GRAND 992 unchanged.**

## Outstanding verdicts (standing set + updates)
- m2 disj-backtrack (PROLOG-BB) · prove_lower VACUOUS ratify (IR-REDESIGN) · pK m4 silent-empty (PROLOG-BB/RAKU-BB) · brokered-catch m3/m4 silent (PROLOG-BB) · str-relop m3-empty (ICON-BB) · gvar-relop box ungated · rank rp-patch ratify · rank cv9/cv10 desync · ceiling-ratify 992 · LANGUAGE-BLIND audit category · Makefile header-dep gap · g_icn_scan_regs_live reconciliation.
- ⛔ **CLOSED:** scan-gate `IR_GEN_SCAN`/`GEN_SCAN` token bug — FIXED/LANDED `9902031`.
- ⛔ **NEW:** scan m3/m4 emission **84% LOUD-EXCISE (59/70)** = the real retag blocker; owner **GOAL-ICON-BB** (light the excised boxes).
- ⛔ **NEW:** emit_core node-dispatch (`g_icn_scan_regs_live && sval`) vs emit_bb flat-chain (`+ dval==3.0`) **guard inconsistency** on scan builtins — must be reconciled before/within the retag.
- scan-breakout **direction A**: inert prep landed; retag PENDING ICON-BB scan-box lighting + the two-path reconciliation.

No LADDER rungs closed (FIX-3 open; FIX-3-iii inert prep landed, retag pending for a concrete reason).

## NEXT SESSION
1. ENV setup + **clone corpus** (absent by default).
2. Baseline GREEN (sno 7/7/7, icon 12/12/12, prolog 5/5/5; GRAND 992).
3. Run the (now-lit) scan gate.
   - **IF** GOAL-ICON-BB has lit the excised m3/m4 scan boxes (m3/m4 PASS > 11, gate green): execute the retag **with** the `dval==3.0` two-path reconciliation + a full scan-corpus m2/m3/m4 differential proof (now discriminating).
   - **ELSE** the retag stays blind-unprovable — **do NOT cowboy it.** Pick up adjacent landable BB work on Lon's word, or surface the scan-box dependency to ICON-BB.
4. `make clean && make` after any header edit (the standing Makefile header-dep gap).
5. Cursor STAYS `bb_call.cpp`.

`# CURSOR: bb_call.cpp` · SCRIP @ `9902031` · .github @ this commit.
