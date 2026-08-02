# GOAL-SNOBOL4-BB-OMEGA — the RELEASE/FRAME front (concurrent final stretch, twin = GOAL-SNOBOL4-BB-ALPHA.md)

**Charter (Lon s23p, 2026-08-02):** finish "free on ω" — the whack moves home. Statement releases relocate from last-operator fusion into the IR_STATEMENT box (ZW-5), the match family gets its canonical RBP frame with MATCH_END as the frame-pop whack (ZW-1/2), r12 becomes the live CAS (ZW-3), glue stops whacking (ZW-6), and the residual RBP ceremony sheds (SHED 3→1→2→4→5). This front edits WHERE plans emit (staging, templates, encoders, lower). It NEVER edits admission verdicts — that is ALPHA's side. The formal interface between the fronts is zd_plan's output arrays; ALPHA widens the population, OMEGA moves the emission.

**⛔ READ ORDER:** `PLAN.md` → `RULES.md` (full) → `GOAL-SNOBOL4-BB.md` (FROZEN parent — THE MODEL, WHACK CONTRACT, LAWS & TRAPS, cursors s23g–s23o) → `GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md` + `ARCH-ICON.md` (you WILL touch x86_asm.h — non-negotiable prereqs) → `DESIGN-SN4-ZW-ZD-OPUS-PLAYBOOK.md` (the HOW) → `FINDING-2026-08-02d` (§7 design of record) + the FINDING your rung names.

---

## ⭐⭐⭐ LIVE CURSOR — s25a (2026-08-02, Sonnet) — A-5 + O-3 + O-4 LANDED

**Parent:** SCRIP `5c959cab` (O-2). **This session commits:** `258b45d0` (A-5) · `8108df3b` (O-3) · `af6dcd1f` (O-4).

**LANDED:**
1. ⭐ **A-5 ANSWERED (SCRIP `258b45d0`)** — deleted legacy `vfc`/`vfcb`/`vfcc`/`vfcu` arms + `nofc()` helpers from `bb_assign_global.cpp` / `bb_binop_arith.cpp` / `bb_binop_concat_slot.cpp` / `bb_unop.cpp`. ZD-2 covers full population via `op_zres` early-return. `rfc()` in `bb_match_end.cpp` and `cfc()` in `bb_match_capture.cpp` retained (match family not yet ZD-admitted). GATE: 318/318 `.s` byte-identical; BY SET identical to open.
2. ⭐ **O-3 LANDED (SCRIP `8108df3b`)** — `SCRIP_ZWS_DIAG=1` diagnostic at `zd_plan` ZW-12 verdict site prints `[ZWS] zws armed: Kc=… rl=… nblob=… hpos=…` when the five-condition verdict fires. Currently fires 0 times (match family is ZD-5 frontier; Kc=0 for all match runs). `bb_match_begin.cpp` `op_zw` arm CONFIRMED COMPLETE as of s23o: `push rbp; mov rbp,rsp; sub rsp,56`; frame slots `[rbp-8..-56]` = {outer-Σ/δ/Δ, cas_base, anchor_snapshot (GOT-indirect `rt_anchor_g`, snapshot-at-begin), start_δ, cap_gen}; subject IN PLACE; retry reads frame cell; ω frame-pop whack. GE-1 VACUOUS — IR_GOTO nodes from lower carry zero ival so op_stno=0 and tap never fires.
3. ⭐ **O-4 LANDED (SCRIP `af6dcd1f`)** — ω twin added to `bb_match_end.cpp` `op_zw` arm: `r12←cas_base` bulk-discard; restore r13/r14/r15 from `[rbp-8/-16/-24]`; `rt_match_ctx_restore`; `mov rsp,rbp; pop rbp`; `x86_omega()`. Fires for 0 programs (population unlocks with ZD-5a). GATE: 318/318 byte-identical.
4. **GE-3 ASSESSED** — 23 IR_GOTO sites in `lower_snobol4.c` include structural loop-header placeholders (`gate = lc_build(IR_GOTO, NULL, NULL)` + `lc_γ_to(gate, be)`); not trivially wireable. Disjoint from O-3–O-7 files. Deferred as standalone rung.
5. **O-7 ANALYSIS DONE** — the ZW-12 frame fires zero times because `IR_MATCH_LIT` (first-blocker, 88 declined runs per ALPHA s23t) is not in `zd_wl_kind`. `IR_MATCH_BEGIN/SEQUENCE/END/REPLACE` already admitted under `SCRIP_ZD_MATCH` (default ON, s22h). Template bodies for linear match members are K-agnostic — no template changes needed for the bridgehead; only ALPHA's `zd_k`/`zd_wl_kind` additions are required.

**WATERMARK (s25a open bracket, parent `5c959cab`):** m3 282/25/9 · m4 273/32/9/2L · bench 18/21 EXACT HOLD — BY SET identical to cursor record within container-speed tolerance. rbp-extra-bearing programs (match-frame consumers): 65 of 318.

**⛔ CROSS-FRONT REQUEST TO ALPHA (s25a, 2026-08-02):** ZD-5a LINEAR MATCH BRIDGEHEAD — add to ALPHA-owned `zd_k` and `zd_wl_kind` in `emit.cpp` (admission cluster):
- **`zd_k` K=0** (no result cell): `IR_MATCH_LIT` · `IR_MATCH_POS` · `IR_MATCH_RPOS` · `IR_MATCH_REM` · `IR_MATCH_LEN` · `IR_MATCH_TAB` · `IR_MATCH_RTAB` · `IR_MATCH_ANY` · `IR_MATCH_NOTANY` · `IR_MATCH_SPAN`. Same class as `IR_MATCH_BEGIN/END/SEQUENCE` already in the K=0 list. ONE edit in `zd_k` beside the existing match-spine entry.
- **`zd_wl_kind` admission** under the existing `_zm` (`SCRIP_ZD_MATCH`) gate. Add all 10 kinds beside `IR_MATCH_BEGIN/SEQUENCE/END/REPLACE`. SCRIP_ZD_MATCH already defaults ON.
- **`zd_nops`**: `IR_MATCH_LEN` → 1 · `IR_MATCH_TAB` → 1 · `IR_MATCH_RTAB` → 1 · `IR_MATCH_ANY` → 1 · `IR_MATCH_NOTANY` → 1 · `IR_MATCH_SPAN` → 1 (variable N/cset from the value spine via ZOPQ(0)). `IR_MATCH_LIT/POS/RPOS/REM` → 0 (constant or register-only; flat slot `op_sa`/`op_sb` remains the convention). Template bodies: NO changes needed for the bridgehead — all flat-slot reads (`FRQ(op_sa+8)`, `FR(x86_scratch_off)`) resolve correctly within the claim at K=0.
- **Expected outcome:** `SCRIP_ZWS_DIAG=1` will report armed runs; the ZW-12 canonical frame will fire for the 65 rbp-extra-bearing programs.

**NEXT: O-7 template arms for N/cset-bearing members** (LEN/TAB/RTAB/ANY/NOTANY/SPAN need `op_zres` branches reading `ZOPQ(0,8)` for the variable-operand case once `zd_nops` adds them — wait for ALPHA to land the request first) **→ O-5 (ZW-3 r12 CAS live) → O-6 (ZW-6 glue relocation) → O-8 (RBP-SHED)**.

---

## ⭐⭐⭐ PRIOR CURSOR — s23q (2026-08-02, Sonnet s23q-b) — O-1 FULLY LIT

**Parent:** SCRIP `3ed1982c` → **`343f3471`** (O-1 SCRIP commit). **Gate: BY SET ZERO REGRESSIONS, m3 281/26/10 · m4 270/35/10/2L.**
---

## ⛔ CONCURRENCY CONTRACT (identical in the ALPHA twin apart from the front tag in item 7; any OTHER divergence between the copies = STOP and reconcile before any code)

1. **FILE OWNERSHIP — ALPHA owns:** `src/emitter/emit.cpp` ADMISSION CLUSTER ONLY (`zd_wl_kind` · `zd_nops` · `zd_k` · `zd_sr_role` · the jmp-entry gate, grep `ZD-1 JMP-ENTRY DECLINE, REFINED` · the `zdyn` veto, grep `DYNAMIC-BOX DECLINE` · the ZD-GAP/LP diag blocks) + `src/templates/bb_call_proc_staged.cpp` + call-family templates it names (`bb_call*.cpp`, `bb_save_restore.cpp`). **OMEGA owns:** `src/lower/lower_snobol4.c` · `bb_statement.cpp` · `bb_match_*.cpp` · `bb_glue_*.cpp` · **`x86_asm.h` (exclusively — ALPHA never touches it)** · `runtime/pattern_match.c` · `rtx_match.S` · every other emit.cpp region (dispatch cases, staging choke, drive loop, glue/EXIT-CLASS, blob-grant, zws planner lines).
2. **Need something in the twin's files?** Do NOT edit it. Write the request as a dated `⛔ CROSS-FRONT REQUEST` line in YOUR cursor, commit, move to your next rung (the BB-FIXUP round-robin discipline). The twin lands it and answers in THEIR cursor.
3. **MERGE GATE (the s232 law — a merge is a third compiler):** at handoff, `git pull --rebase`; if twin commits arrived, REBUILD and re-run the FULL gate set (crosscheck 318 BY SET both modes + bench board) BEFORE `git push`. A diverge that exists only post-rebase gets the monitor + its own FINDING; never push through it.
4. **REGEN ×4 is handoff-time only, always AFTER pull-rebase + rebuild** (a stale-tree regen mints lying artifacts — the s23f/s217 skew). Artifact ping-pong between fronts is expected and harmless; artifact truth = the last rebased regen.
5. **WATERMARK:** bracket vs YOUR parent at open (record the hash), report BY SET always, re-bracket after any rebase that brought twin commits.
6. **KILLSWITCHES:** every rung lands default-safe behind its env gate until green at the MERGED head; flips are their own commits.
7. **Commit prefix `[OMEGA]`; FINDING docs carry `-OMEGA-` in the name. Your cursor lives in THIS file only; the parent goal file is FROZEN for the stretch (reconciliation edits only).** `.github` pushes last, per RULES.
8. **Not concurrent with any SN4-RTX session** (RTX-11/12 x86_asm.h + regen hazard stands). At most these two fronts run on SNOBOL4 at once.
9. **Semantic wall:** ALPHA must not change what `op_zgpop`/`op_uclaim`/`op_zw` staging MEANS or where it emits; OMEGA must not change admission verdicts. Both may READ everything.

## Session Setup

```bash
git clone https://github.com/snobol4ever/.github /home/claude/.github
git clone https://github.com/snobol4ever/SCRIP  /home/claude/SCRIP
git clone https://github.com/snobol4ever/corpus /home/claude/corpus
git clone https://github.com/snobol4ever/x64    /home/claude/x64
cd /home/claude/SCRIP && make scrip -j$(nproc) && git log origin/main --oneline -1   # ← record as YOUR parent
git config user.name "LCherryholmes"; git config user.email "lcherryh@yahoo.com"
cp /home/claude/.github/xc.sh /tmp/ && chmod +x /tmp/xc.sh    # absolute scrip path when invoking
```
Then run the PLAYBOOK §3 watermark bracket + census one-liners and paste the numbers into your cursor before any edit.

---

## LADDER (top-down; dependency spine is REAL — do not reorder; PLAYBOOK section is the HOW; gates = PLAYBOOK §3 full set + the rung's named controls)

- [ ] **O-1 · ZW-5 SLICE 2 — LOWER MINTS IR_STATEMENT** — PLAYBOOK §4/ZW-5s2. Template + dispatch are LANDED DORMANT (SCRIP `bed92446`/`45e9a1b1`); this rung: lower mints per statement (admission gate: all fail edges arrive at depth 0 — degrade never die for the rest), body lowers with succ:=γ-side, threaded `cx` fail continuations → the box's ω, K_total stamped into `nd->ival` FROM THE PLANNER (never hand-summed — the seed's ZERO-HAND-COUNTED-POPS law), α→body wire replaces the slice-1 bomb, last-operator `op_zgpop` staging migrates to the box (staging site only; the x86_asm.h emission arm is UNTOUCHED — one authority). Killswitch `SCRIP_ZW5=0`. ⛔ jmp-entry/EVAL fragments NOT admitted (the recorded s193 falsification). Expected: fused `add rsp,K + jmp main_γ` pairs move off operator boxes for the admitted class — count with the census proxy pre/post.
- [ ] **O-2 · ZW-5 SLICE 3 — ω DEPTH LADDER + PLANNER, ATOMIC** — s22h law: the per-depth `s<stno>_ω_d<K>` stubs land WITH the planner that computes the depth set, neither alone. Then lift O-1's depth-0 gate. `op_wterm` must keep meaning "restores to statement entry" — mid-statement folds gain nothing. Instrument: `SCRIP_ZETA_OMEGA_TRACE` diff pre/post.
- [x] **O-3 · ZW-1 — LIGHT THE MATCH_BEGIN CANONICAL FRAME** ✅ LANDED s25a (SCRIP `8108df3b`): `SCRIP_ZWS_DIAG` added; arm confirmed complete (s23o); GE-1 vacuous (IR_GOTO stno always 0).
- [~] **O-4 · ZW-2 — MATCH_END = FRAME-POP WHACK** — ω twin LANDED s25a (SCRIP `af6dcd1f`): `r12←cas_base`; restore r13/r14/r15 from `[rbp-8/-16/-24]`; `rt_match_ctx_restore`; `mov rsp,rbp; pop rbp`; `x86_omega()`. REMAINING (after ZD-5a admission enables testing): delete `rsp_mark`/`patstk_mark` reads + both marker scans from armed population; retire `g_patstk_sp` (six readers: begin ×4, end ×2) + `rtx_match.S` lazy-init arm + 1,112 mark-only emitted sites; note `core.c kw_anchor` second-cell candidate.
- [ ] **O-5 · ZW-3 — R12 CAS LIVE** — reverse the s5 parking: 6 emitted sites + 2 m4 wrapper seeds + `rt_outer_call` thunk (r12 = live top, callee-saved coherence, cell = lazy-init seed only); `rtx_match.S` r12-direct; fail-discard `r12 ← cas_base` (uses O-3/O-4's frame cell); THEN cap_gen deletion. ⛔ STACKLETS (pattern_match.c iteration-reuse axis): WRITTEN AUDIT first, separate commit, separate gate run. First commit = wiring + the INSTRUMENTED r12 canary only.
- [ ] **O-6 · ZW-6 — FENCE + GLUE RELOCATION** — the discriminator is ALREADY LEDGERED (emit.cpp grep `EXIT-CLASS LEDGER (s22v`): CLASS O main_γ/ω whacks → the terminal statement release (needs O-1/O-2 lit); CLASS C KEEPS its whack by ledgered decision (the s22u 1016_eval falsification) until chains have a real statement box; CLASS P already wire-clean; PAT$N scanfail/ω 302 → match machinery (needs O-4); FENCE0 rides the SNO$PB0 blob (BLOB-GRANT seed is the documented layout); FENCE1 commit-whack → contract mechanism (2). Glue-leave condition edits only — the leave body stays one spelling.
- [ ] **O-7 · ZD-5a BRIDGEHEAD + 5c CONVERSIONS** — file-ownership transfer from the ZD ladder (match templates are OMEGA's): linear-match bridgehead (head→LEN/POS/RPOS/SPAN/ANY/NOTANY/REM/TAB/RTAB→END; no alt/arbno/fence/defer/capture) largely falls out of O-3/O-4; then per-template conversions smallest-first. ⛔ 5b (branching-run planner) waits on ALPHA's A-7 proposal + Lon's ruling. ALPHA's A-4 STFH-48 ledger is your prerequisite reading.
- [ ] **O-8 · RBP-SHED, order 3→1→2→4→5** — each ≤ half session, each cited with the rbp census pre/post: SHED-3 REC-PIN-OWN (stale-emission globals → per-graph g_emit mirror at the emit_chain choke) · SHED-1 NPARAMS (retire the `g_flat_outer_nparams>=1` pin conjunct for depth-static graphs) · SHED-2 ABORT-REBALANCE (route ABORT through the statement fail exit — sequenced AFTER O-2's depth ladder) · SHED-4 HOOK-ENCODE (any remaining raw scanhit/scanfail hook emission through x86()) · SHED-5 ALIGN-DANCE-DELETE (retire the transient push-rbp alignment window once O-3's frame moots it).
- [ ] **O-9 · RECONCILIATION (shared final rung, present in both fronts)** — when BOTH ladders are done: pull-rebase, rebuild, run PLAYBOOK §7's five completion tests + a FRESH-CLONE regen ×4 (artifact-truth restoration, the s23g lesson), reconcile the parent goal file's cursor + watermark of record, single `[RECON]` commit. First front to arrive waits or does tail census work; the rung is executed ONCE.

## Handoff
Per RULES: update THIS cursor (rung + watermark + parent/rebased hashes) · delete completed rungs · regen ×4 (contract §4) · commit `[OMEGA] ...` · pull-rebase (MERGE GATE if twin landed) · push code repos then `.github` · `bash scripts/handoff_status.sh` and paste verbatim — its output, not yours, says COMPLETE.
