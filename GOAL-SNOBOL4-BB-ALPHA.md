# GOAL-SNOBOL4-BB-ALPHA — the ALLOCATION/ADMISSION front (concurrent final stretch, twin = GOAL-SNOBOL4-BB-OMEGA.md)

**Charter (Lon s23p, 2026-08-02):** finish "alloc on α" — every statement that today falls to a UCLAIM head claim (the `n1_var_α: sub rsp,240` class) gets ADMITTED to the per-cell regime so each BB carves its own K. This front edits WHO gets planned (zd_plan's admission inputs). It NEVER edits where plans emit — that is OMEGA's side. The formal interface between the fronts is zd_plan's output arrays; ALPHA widens the population, OMEGA moves the emission.

**⛔ READ ORDER:** `PLAN.md` → `RULES.md` (full) → `GOAL-SNOBOL4-BB.md` (FROZEN parent — THE MODEL, WHACK CONTRACT, LAWS & TRAPS, cursors s23g–s23o) → `DESIGN-SN4-ZW-ZD-OPUS-PLAYBOOK.md` (the HOW; this file carries ORDER + OWNERSHIP + STATE) → the FINDING doc your rung names.

---

## ⭐⭐⭐ LIVE CURSOR — s23p (2026-08-02, opened by Fable; no ALPHA session has run yet)

**NEXT: A-1 (ZD-4 jmp-entry lift).** Parent bracket to beat: crosscheck 318 m3 280/27/10 · m4 266/39/10/2L BY SET (s23o record) · bench 18/21. Parent SCRIP hash: record YOURS at open (`git log origin/main -1` after clone).

---

## ⛔ CONCURRENCY CONTRACT (identical in the OMEGA twin apart from the front tag in item 7; any OTHER divergence between the copies = STOP and reconcile before any code)

1. **FILE OWNERSHIP — ALPHA owns:** `src/emitter/emit.cpp` ADMISSION CLUSTER ONLY (`zd_wl_kind` · `zd_nops` · `zd_k` · `zd_sr_role` · the jmp-entry gate, grep `ZD-1 JMP-ENTRY DECLINE, REFINED` · the `zdyn` veto, grep `DYNAMIC-BOX DECLINE` · the ZD-GAP/LP diag blocks) + `src/templates/bb_call_proc_staged.cpp` + call-family templates it names (`bb_call*.cpp`, `bb_save_restore.cpp`). **OMEGA owns:** `src/lower/lower_snobol4.c` · `bb_statement.cpp` · `bb_match_*.cpp` · `bb_glue_*.cpp` · **`x86_asm.h` (exclusively — ALPHA never touches it)** · `runtime/pattern_match.c` · `rtx_match.S` · every other emit.cpp region (dispatch cases, staging choke, drive loop, glue/EXIT-CLASS, blob-grant, zws planner lines).
2. **Need something in the twin's files?** Do NOT edit it. Write the request as a dated `⛔ CROSS-FRONT REQUEST` line in YOUR cursor, commit, move to your next rung (the BB-FIXUP round-robin discipline). The twin lands it and answers in THEIR cursor.
3. **MERGE GATE (the s232 law — a merge is a third compiler):** at handoff, `git pull --rebase`; if twin commits arrived, REBUILD and re-run the FULL gate set (crosscheck 318 BY SET both modes + bench board) BEFORE `git push`. A diverge that exists only post-rebase gets the monitor + its own FINDING; never push through it.
4. **REGEN ×4 is handoff-time only, always AFTER pull-rebase + rebuild** (a stale-tree regen mints lying artifacts — the s23f/s217 skew). Artifact ping-pong between fronts is expected and harmless; artifact truth = the last rebased regen.
5. **WATERMARK:** bracket vs YOUR parent at open (record the hash), report BY SET always, re-bracket after any rebase that brought twin commits.
6. **KILLSWITCHES:** every rung lands default-safe behind its env gate until green at the MERGED head; flips are their own commits.
7. **Commit prefix `[ALPHA]`; FINDING docs carry `-ALPHA-` in the name. Your cursor lives in THIS file only; the parent goal file is FROZEN for the stretch (reconciliation edits only).** `.github` pushes last, per RULES.
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

## LADDER (top-down; every rung: PLAYBOOK section is the HOW, gates = PLAYBOOK §3 full set + the rung's named controls)

- [ ] **A-1 · ZD-4 JMP-ENTRY LIFT** — PLAYBOOK §5/ZD-4. The measured roman blocker: `proc_LBL__ROMAN n=30 armed=0` while every node admits individually (SCRIP_ZD_GAP). Step 0 is re-reading the gate at HEAD (`zd_stub_ok` was deleted s23g; the [LP] `proc_ROMAN armed=2` vs `proc_LBL__ROMAN armed=0` split names the live discriminator — likely `g_flat_frame_floor`, the s22v ledger's own predicate). Admit CLASS-C chains with ordinary statement bodies under hatch `SCRIP_ZD_JMPENTRY=1`; diff 1019's fragment `.s` on/off; monitor any diverge; flip + delete the gate for the admitted class. ⛔ Controls that MUST stay green: 1016_eval · 1019 · 161 · expr_eval (the two recorded falsifications live in the gate's own comment — read them before widening). EXPECTED: roman `n1_var_α` 240→16, its `stmt_claim` loop gone; roman stays red on IR_CALL until A-2/A-3 (bench board: roman is a NAMED expected mover — BY SET with that annotation, not a silent 18/21 break).
- [ ] **A-2 · ZD-7c USER-PROC ARM** — spec'd verbatim in the frozen parent's ZD-7c entry (sized ~20min + gates); verified at HEAD: `zd_nops` already returns `n_operands` for IR_CALL and auto-stages per-arg reads; the exclusion is `rt_proc_is_registered` in `zd_wl_kind`; sibling idiom = `bb_deref.cpp:13-22`. Killswitch `SCRIP_ZD_PROC=0`. Controls: 085/086/087 MUST flip green (they are the recorded naive-admission falsification) + func_call bench + full 318 BY SET + regen ×4.
- [ ] **A-3 · ZD-7 IR_CALL FAMILY** — builtin-call spellings on the same staging authority; SR roles 1/2/3 stay admitted, role 0 stays DECLINED (a recorded decision — CALL2BB-only, unmeasured; its rationale lives in zd_wl_kind's comment). Re-run the frontier census after: expect IR_MATCH_BEGIN to promote to top blocker (a decline count is a frontier reading, never a backlog).
- [ ] **A-4 · ZD-5a-PRE STFH-48 LEDGER** — READ-ONLY + doc rung: enumerate `bb_match_begin`'s `stfh()` 48B claim's non-HKQ `[rsp+off]` refs; ledger the second allocation authority in a FINDING. No code. (The code half belongs to OMEGA — match templates are theirs.)
- [ ] **A-5 · ZD-3 LEGACY ARM RETIREMENT** — per kind fully covered by its ZD arm: delete vfc/vfcu/vfcb/vfcc + `op_fc_disp` registration, kind by kind, byte-identity sweep on the untouched population per deletion.
- [ ] **A-6 · ZD-2c/2g CLOSE-OUT** — verify zero first-blockers at the post-A-3 frontier; if still zero, mark closed-vacuous with the census line; arm only if a widened statement first-blocks.
- [ ] **A-7 · ZD-5b WRITTEN PROPOSAL (⛔ NO CODE)** — the ONE design-tier item: planner extension for branching match runs (alt/arbno cycles/defer). Deliver as `DESIGN-SN4-ZD5B-*.md` for Lon's ruling; OMEGA's O-7 consumes the ruling.
- [ ] **A-8 · ZD-6 STANDALONES** — 130/131 clean-HEAD segv (MONITOR-FIRST; if the fix lands in an OMEGA file → CROSS-FRONT REQUEST, contract §2) · W04_arbno_basic DIV member · bb_op_name entries ops 14/73–77.
- [ ] **A-9 · RECONCILIATION (shared final rung, present in both fronts)** — when BOTH ladders are done: pull-rebase, rebuild, run PLAYBOOK §7's five completion tests + a FRESH-CLONE regen ×4 (artifact-truth restoration, the s23g lesson), reconcile the parent goal file's cursor + watermark of record, single `[RECON]` commit. First front to arrive waits or does tail census work; the rung is executed ONCE.

## Handoff
Per RULES: update THIS cursor (rung + watermark + parent/rebased hashes) · delete completed rungs · regen ×4 (contract §4) · commit `[ALPHA] ...` · pull-rebase (MERGE GATE if twin landed) · push code repos then `.github` · `bash scripts/handoff_status.sh` and paste verbatim — its output, not yours, says COMPLETE.
