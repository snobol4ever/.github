# FINDING 2026-08-03e — SN4 HQ ADVISORY: ω-coverage is 26%, "already done" was a denominator error, and the directive needs a gate

**Seat:** Lon-directed advisory/HQ (not an ALPHA or OMEGA seat; zero SCRIP code edits this session). **Directive (Lon, verbatim):** *"I wanted to see OMEGA for every box, and it tells me already done. I think they are so confused. Help them."* and *"get those two sessions back on the proper track to completion."* Everything below is MEASURED AT HEAD this session (committed `.s` artifacts + `emit.cpp` source), not inherited from prose — per the STALE-ORIENTATION rule, the prose is the rot; the tree is the truth.

---

## 1 · THE CLAIM AND ITS SOURCE

OMEGA s39 cursor ("FOUR MEASURED CORRECTIONS", item 1): *"The model is already live for 100 of 120 programs. `sub rsp,16` per α + `add rsp,16` per β is the default emission... The per-BB model and the UNWIND ruling are THE SAME MODEL — β already frees own K and rolls to pred."* This is the artifact behind the "already done" answer Lon received. The session was not lying; it pattern-matched THE MODEL (ZD cells exist, β frees own K on the value spine) onto THE DIRECTIVE (ω on EVERY box, default, tree-wide) and reported the model's existence as the directive's completion.

## 2 · FALSIFICATION AT HEAD — MEASURED

All commands reproducible; run them before disputing a number.

**2.1 The gate is OFF.** `grep -n "SCRIP_UNWIND" src/emitter/emit.cpp` → the two gate reads at **:2370** and **:2605** are `_uw = (_e && *_e == '1') ? 1 : 0` — default 0. The unwind is a prototype proven on ONE witness chain (uw3, fire set 17), behind a default-OFF killswitch. U-2 (match family) unstarted; U-3 (delete voided machinery) unstarted.

**2.2 ω is on ~1 in 4 boxes in the flagship benchmark.** `corpus/benchmarks/snobol4/roman.s`: **135 `_α:` labels · 123 `_β:` · 35 `_ω`** — raw ω-label coverage ≈26%. (Caveat: raw proxy — K=0 protocol boxes need no release and their ω legitimately fuses to a wire; the LBL duplicate-body residue double-counts ~33% of boxes both sides. The U-GATE instrument in §5 computes the honest K>0-denominator number. The proxy is nonetheless a 4× gap from "every box.")

**2.3 Accumulated pops — clause 2's named defect — are alive in roman at HEAD.** Carve-size multiset (`grep -o 'sub *rsp, *[0-9]*'`): 8×11 · 16×54 · 32×4 · 48×5 · 192×2 · 240×2 (total 78). Release-size multiset (`add rsp`): 8×9 · 16×96 · 32×8 · 48×22 · **64×7 · 80×6 · 96×3 · 112×6 · 128×1 · 144×3** · 192×8 · **256×4 · 272×4** (total 177). **Eight release sizes match NO single carve — 34 instructions, each a site that knows accumulated depth.** 177 releases against 78 carves is the fused/duplicated exit surface in one line. The wholesale UCLAIM survives verbatim: 2× `sub rsp, 240` + 2× `sub rsp, 192`.

**2.4 The denominator.** "100 of 120" counts the admitted/armed subset. Corpus-wide: `grep -rl 'sub *rsp, *[2-9][0-9][0-9]' corpus/crosscheck --include=*.s | wc -l` → **132 of 485** crosscheck `.s` artifacts carry a ≥200B single carve (485 files > 318 programs — includes snocone etc.; the ratio stands). The excluded population is exactly where the model is NOT live.

## 3 · THE THREE-ERROR DECOMPOSITION OF "ALREADY DONE"

1. **β ≠ ω.** The ruling: *"a deterministic (one-shot) box's β IS its ω-continuation."* That is an ALIAS granted to one-shot value-spine boxes. Generators need a real β (retry) AND a real ω (exhausted → free own K → roll to pred's β). Most boxes today emit NEITHER port body (U-1a's own finding: fire set EMPTY, βs elided by circular prophecy; §2.2's 35/135). Measuring β-alias penetration and reporting it as ω-for-every-box is the category error.
2. **Survivor denominator.** A fraction over the admitted subset silently excludes the declined/UCLAIM population — the exact programs the directive targets (§2.4).
3. **Gate-off ≠ done.** A default-OFF experiment proven on one witness is a landing, and a good one. It is not the emitter. "Done" is defined in §6, and nothing else may borrow the word.

## 4 · SYSTEMIC CAUSES — the seats are fine, the instrumentation is the disease

- **4.1 ACCEPTANCE INVERSION.** Every rung gates on BY-SET-IDENTICAL, which certifies *nothing changed*. The finishing plan's own Step 3: *"`.s` byte-change is expected and desirable here — this is the payoff."* A session optimizing identity gates will forever land the migration as a default-OFF experiment and truthfully report green. Law going forward: **BY-SET-IDENTICAL certifies only the killswitch-OFF arm; the migration itself gates on byte-change in the predicted direction + witnesses + census movement + BY-SET no-regression.**
- **4.2 THE DIRECTIVE HAD NO GATE.** ZD-DEPTH made walls countable; nothing made ω-coverage countable, so "show me ω for every box" was answered by frontier vibes. Fix = U-GATE (§5).
- **4.3 CURSOR FRAGMENTATION.** Three live cursors carried three different NEXTs (HQ: U-2 · OMEGA s40: O-PB-2b/3/PATREF-flip/O-PB-4 · ALPHA s38: wait-for-U-2). Nobody held the U-2 baton — rot-class (b) reborn as fragmentation. Fix = ONE NEXT, held at HQ (§7).
- **4.4 OWNERSHIP DRIFT.** O-PB-1's fix (`&& !g_emit.flat_pat` on the DYNARM override, emit.cpp:1995) sits inside the zdyn veto block the concurrency contract greps to ALPHA (`DYNAMIC-BOX DECLINE`). The edit is correct and stands; the ownership line is owed a sentence — ALPHA ratifies at RECON or HQ redraws the grep boundary. Reconcile, don't relitigate. Root cause: ALPHA finished its charter and idled while OMEGA absorbed everything; §7 re-charters ALPHA.

## 5 · U-GATE SPEC v1 — `scripts/test_gate_omega_own_k.sh` (ALPHA seat; census first, gate later, the ZD-DEPTH maturity path)

Concurrent-safe by construction: ONE NEW FILE in `scripts/`, collides with no contract-owned file; zero `src/` edits. Over `corpus/crosscheck/**/*.s` + `corpus/benchmarks/snobol4/*.s`, per file:

- **(a) BOX** = label `^(n[0-9]+|proc)_.*_α:`; **K(box)** = integer of the first `sub rsp, K` between this α and the next α label (0 if none).
- **(b) ω-COVERAGE** = fraction of K>0 boxes owning a release site: an emitted `_ω` body containing `add rsp, K_own`, OR the DRIVE_PAIR alias β (`add rsp, K_own` + `jmp *_β`) — the ruling's alias clause, honored.
- **(c) ORPHAN-ADDS** = count of `add rsp, J` where J matches no single carve size in the file. WHITELIST: `rsp, 8` alignment dance (until SHED-5 retires it) · framed restores `mov rsp, rbp` (no add to count) · migration-era STATEMENT_END/MATCH_END staged pops. A J equal to a CONTIGUOUS carve-run sum is the ΣK FOLD — legal fusion, its OWN column, never the orphan bucket. ⛔ **MODEL THE POP YOU AUDIT** — ALPHA s38 lesson 2b verbatim (the first wall census was wrong 3× for omitting zgpop); this instrument must model the fold or it will mint 100+ false orphans and reproduce the [ZD-GAP] disease in a new costume.
- **(d) OUTPUT:** per-file `ω-cov X/Y · fold N · orphan M`, corpus rollup, worst-10 files. **NOT pass/fail in v1** — a census, exactly like ZD-DEPTH; thresholds arrive when the DoD nears. Never wire `.s` byte-identity into it (RULES).
- **(e) HAND-MEASURED BASELINE to confirm on first run:** roman 135α/123β/35ω · orphan sizes {64,80,96,112,128,144,256,272} = 34 · crosscheck ≥200B-carve files 132/485. LBL duplication inflates roman both sides until finishing-plan Step 5 — note, don't chase.
- **(f) WATERMARK** gains two numbers permanently: `ω-cov X/Y · orphan N`.

⛔ **DENOMINATOR LAW (the error that produced "already done"):** never report a fraction whose denominator is the admitted/armed subset without saying so in the same sentence.

## 6 · DEFINITION OF DONE — "ω for every box" (no session may use the word "done"/"complete"/"already" for the directive before ALL six; partial = report the fraction)

1. `SCRIP_UNWIND` default ON tree-wide (killswitch retained per house convention) **+ U-3 deletions LANDED** (ENDJMP/op_wsteal · ZW-5 per-depth stub ladder · zd_wp accumulated fail staging).
2. **ω-coverage = 100%** of K>0 boxes (U-GATE), crosscheck + benchmarks.
3. **Orphan-adds = 0** outside the §5(c) whitelist.
4. **UCLAIM census = 0** — `zvo_uclaim_k` returns 0 every run; corpus grep `sub rsp, [2-9][0-9][0-9]` over SNOBOL4 `.s` = 0 (finishing-plan Step 4).
5. **Wall census == framed-enter count** (STATEMENT/MATCH/ARBNO/FENCE1/FUNCTION) — ZD-DEPTH instrument, finishing-plan Step 4 acceptance.
6. Behavioral floor: 318 BY SET ≥ baseline both modes · rc=139 tail (14 programs) cleared · bench 18/21 hold-or-better · regen ×4.

## 7 · ONE NEXT (Lon-directed this session)

**OMEGA = U-2** (match-family βs join the chain; MATCH_BEGIN/ARBNO/FENCE1 frames; MATCH_BEGIN.β owns the unanchored start bump; ABORT = O(1) frame-restore to the pinned floor — the ONE legal fail-side rsp reset, legal because RBP pins it, never because anything computes depth). **O-PB-4 is SUBSUMED by U-2** (it IS finishing-plan Step 2), lands AS U-2. **ALPHA = U-GATE** (§5). **PARKED until both land: O-PB-2b/3, the PATREF default flip, and the O-PB-2a closure-scoping coordination** (queues to ALPHA after U-GATE). HQ holds rulings + reconciliation only. RECON stays queued after U-2 + U-GATE.

## 8 · WHAT THIS SESSION DID NOT DO

No SCRIP/corpus edits. No rewriting of either front's cursor blocks in place — supersession blocks at top only, per house convention. No PLAN.md table edit (RULES step 3). Push pending Lon's credential; until pushed, the fronts cannot see any of this.

---

## 9 · PRE-HANDOFF SCAN ADDENDUM (2026-08-03e-2) — measured against origin before push

**S-1 · CONFIRMED — OMEGA s40's cursor hashes are pre-rebase GHOSTS.** origin/main: O-PB-1 = **`bf489b89`**, O-PB-2a = **`c9d84615`**, rebased ON TOP of U-1b `a9823228` (ancestry verified: `a9823228` IS an ancestor of HEAD; the cursor's `7f8e95dd`/`39833281` are NOT on origin — `git merge-base --is-ancestor` says NO). The cursor also names parent `c0c77585` (U-1a) though the pushed parent is U-1b, and records NO post-rebase gate re-run — contract §3's merge-gate rebuild is unverifiable from the cursor. Any session stashing/reverting against the recorded hashes hits unknown-object. **RULE (add to contract §3): the cursor records hashes AS-PUSHED (post-rebase), and when the rebase moved the base, the post-rebase gate line is mandatory. OMEGA: correct the s40 hash line at your next handoff.**

**S-2 · WATERMARK SLIDE, invisible by construction.** Own-cursor arithmetic: m3 passes **295 (A-9) → 289 (HQ U-1b) → 280 (OMEGA s40 baseline)**, m4 **289 → 282 → 274**, with T≈2 at both ends — ~15 passes lost across landings that were nominally default-OFF/BY-SET-identical. Every bracket is vs-OWN-parent, so a monotone cross-session slide is structurally invisible to every seat. Could be harness/env variance (the 127/152 lesson) — which is precisely why the fix is procedural: **RECON step 0 = ONE shared re-bracket at merged HEAD, same harness, recorded env pad; bisect if the slide is real.**

**S-3 · CONFIRMED — the uw2/uw3 acceptance witnesses are committed NOWHERE.** `find SCRIP corpus -iname "*uw[23]*"` = empty. U-1b's acceptance ("uw3 rc=0 both") and U-2's gate cite files that lived only in the HQ session's /tmp. **Commit the pair to `corpus/probe/` (with .ref) before U-2 lands** — an uncommitted acceptance witness is unreproducible prose.

**S-4 · ZW-13 IS THE SECOND WITNESS OF BOTH DISEASES.** OMEGA's own s32-era finding (cursor line ~135): the ZW-12 canonical frame was DARK since ALPHA s24a — ALPHA substituted `!has_blob` on the OMEGA-owned `zws` planner line, `zws` was permanently zero, and **O-3/O-4/O-5s2/O-7 all "landed" into a dead arm with BY-SET-IDENTICAL certifying zero-emission no-ops.** That is (a) the acceptance-inversion disease (§4.1) with a prior conviction, and (b) an ALPHA→OMEGA ownership edit mirroring O-PB-1's OMEGA→ALPHA edit (§4.4). Two witnesses each; the e-cursor's acceptance law and ownership reconciliation are not hypothetical.

**S-5 · φ-GLUE AUDIT OWED BEFORE U-2 BUILDS ON s29/s30.** The landed ALTERNATE/SEQUENCE (s29) + FENCE1 (s30) arms implement the ZD-5b proposal's depth model ("every arm at ALTERNATE.α depth; φ restores before next arm") — written BEFORE the UNWIND ruling. If any φ fail-glue restores by computed depth, it is voided-class under clause 2. One read-only pass over `bb_match_alternate/sequence/fence1.cpp` fail paths, first item of U-2.

**S-6 · THE 127/152 ALIGNMENT KNIFE-EDGE HAS SIX WITNESSES AND NO OWNER.** An rsp%16 ABI bug at some call site (verdict = f(initial rsp parity)) is a bug, not weather. Assign an owner — natural home: U-2's framed-enter work standardizes alignment; make the fix (or a `test rsp,15` canary) an explicit U-2 sub-item or an HQ rung.

**S-7 · nit:** both fronts' READ ORDER lines still call the parent "FROZEN" post-unfreeze (s26). Fix at next front handoff.

**Also verified clean:** .github origin did NOT move during this session (local ahead only); this session's three GOAL-file insertions render intact (markers present ×2 per file, UNWIND heading whole); `scripts/handoff_status.sh` present and executable.
