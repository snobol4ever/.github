# GOAL-SNOBOL4-BB — SNOBOL4 → native x86 Byrd-Box codegen

Frontend: SNOBOL4 → shared IR → BB emitter (mode-3 `--run` / mode-4 `--compile`). Protocol: RULES.md; template/encoder work requires ARCH-ICON.md + GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md FIRST. Watermark is SHARED STATE — re-prove at session start AND close. History pruned 2026-07-30; full text in FINDING docs + git (pre-shrink = `.github` `2f3fd45a`).

## ⭐⭐⭐ HEADQUARTERS — UNFROZEN (Lon directive 2026-08-02, s26): "It is not just a source of truth, it is headquarters."

The s23p freeze is LIFTED by Lon's direct order. The TWO CONCURRENT FRONTS continue under their file-ownership contract: **`GOAL-SNOBOL4-BB-ALPHA.md`** (allocation/admission side — the ZD ladder: who gets planned) and **`GOAL-SNOBOL4-BB-OMEGA.md`** (release/frame side — the ZW ladder + SHED: where plans emit); execution HOW = `DESIGN-SN4-ZW-ZD-OPUS-PLAYBOOK.md`. But THIS file is HQ: Lon-directed work executes and lands from here, and this file's LIVE CURSOR records it so the fronts rebase with eyes open. THE MODEL, THE WHACK CONTRACT, and LAWS & TRAPS remain binding on all three seats. The LADDER sections below remain superseded by the front files except where an HQ cursor entry says otherwise.

## ⭐⭐⭐ LIVE CURSOR — 2026-08-06k (Sonnet — W-1c.3 Part B patstk slot retired; chain arm census stale)

⭐ **SESSION WORK (Sonnet, 2026-08-06k):**

**W-1c.3 Part B — patstk slot `op_off+8` retired (SCRIP `171e4a03`, corpus `f1726c29`):** The α patstk snapshot at `FRQ(op_off+8)` deleted from `bb_match_begin`. All four paths now read patstk from the sentinel `[r12+16]` directly: hfc fail-exit (LIFO `sub r12,24` → `[r12+16]`, prior commit), non-hfc fail-exit (sub moved to TOP of branch → `[r12+16]`, slot-read deleted), `bb_match_end` rfc/non-rfc fork unified on the L(9) scan (non-rfc slot-read at `FRQ(op_off+8)` deleted, both arms scan via r10). Slot `op_off+8` reverts to `head.zeta_mark` (its `zeta_storage.c` grant). The op_tail L(8) and `release_pump` L(5) scans are kept — they are pre-pump range-locators where live capture count is runtime-variable. Gates: 118/23/0/0 · witness 9/9. Regen ×3 real deltas.

**CHAIN ARM DELETION BLOCKED — census stale (NOT committed):** Goal file's "33 dispatches all legitimately declined; already xfail/DIVERGE" is **stale at HEAD `e65ff67d`**. Bombing the chain arm body caused **19 regressions** (D09-D13, G19-G20, H24-H25, X01-X08, X11 — all were PASSING via the chain arm). Correct sequence: promote these 19 programs to the frameless arm FIRST, then bomb. New prerequisite rung: `CHAIN-PROMOTE-19` — audit why each declines the frameless arm and fix the blocker.

**GATES:** run-suite 118/23/0 · compile-suite 0/141/0 · witness ladder 9/9. All green.

**NEXT RUNGS (in order):**
1. ✅ **XFAIL.compile birth** — DONE (corpus `10c87a40`).
2. ✅ **FENCE-WHACK-ON (W-1c.1)** — DONE (SCRIP `b07fe2c9`).
3. ✅ **ARBNO view-restore (W-1c.2)** — DONE (SCRIP `f11a59b2`).
4. ✅ **W-1c.4 `RT_CAS_TOP` rename** — DONE (SCRIP `a07e4143`).
5. ✅ **W-1c.3 NO-SCAN failure exits** — DONE (SCRIP `a897764e`).
6. ✅ **W-1c.3 NO-SCAN L(6) post-pump** — DONE (SCRIP `e65ff67d`).
7. ✅ **W-1c.3 Part B patstk slot retired** — DONE (SCRIP `171e4a03`).
8. **CHAIN-PROMOTE-19** — audit why D09-D13/G19-G20/H24-H25/X01-X08/X11 decline frameless arm; fix; then bomb the chain arm.
9. **W-2 ARM-ALL/flip** → W-4 xc318 reds → W-5 legacy forest.

⭐ **SESSION WORK (Sonnet, 2026-08-06j):**

**W-1c.4 `RT_CAS_TOP` → `RT_DCAP_TOP` rename (SCRIP `a07e4143`):** Mechanical rename across 11 files, 28 occurrences. Byte-neutral (symbol names only, zero instruction change). Consistent with existing `g_dcap_top` alias in `pattern_match.c`. Regen ×3 zero delta. Gate 118/23/0.

**W-1c.3 NO-SCAN — failure exits (SCRIP `a897764e`, corpus `1579ab74`):** The tag-0 sentinel scan at `IR_MATCH_BEGIN`'s failure exits (both hfc and non-hfc arms) is DELETED — replaced by `sub r12,24` (one instruction). Lon ruling: at the failure exit the un-match cascade has already popped every entry this match pushed via `bb_match_capture`'s COND β (`sub r12,24` UNGUARDED, "sound by the LIFO cascade"), so r12 arrives at marker+24 BY INVARIANT. The walk stopped on its first test in the common case — pure ceremony — and was WRONG in the seal classes (ABORT/FENCE-seal/ARBNO abandon, where a pushed COND's β never fires): it would halt on an orphaned live entry and read that entry's `saved_delta`/`len` as the rsp mark and patstk. Register arithmetic is depth-free; a frame-slot route to the marker is not (rsp at failure depth, not α depth — MEASURED crash on 40+ probes). Gates: 118/23/0 · witness 9/9 · xc318 m3 zero new regressions by set · mode-4 A/B all 122 pattern programs byte-identical. Regen ×3 real deltas (loop → one insn), idempotent.

**W-1c.3 NO-SCAN — L(6) post-pump pop (SCRIP `e65ff67d`, corpus `794c24bf`):** The L(6) loop inside `release_pump` (post-pump wholesale pop) is DELETED — replaced by `sub r12,24`. After the pump has consumed every entry via `rt_dcap_step`, r12 is at marker+24 BY INVARIANT (nested matches inside pumped assignments push balanced markers; r12 callee-saved through pump's C calls). L(5) (pre-pump range-locator scan) is KEPT — it runs before the pump when the count of live captures above the marker is runtime-variable; LIFO cannot locate it there. Gates: 118/23/0 · witness 9/9 · xc318 m3 zero new regressions by set. Regen ×3 real deltas, idempotent.

**MEASURED NEGATIVE RESULT ON RECORD (do not retry):** Routing the marker through a carried frame slot (`head.dcap_mark`, `op_off+32` — the slot `zeta_storage.c` grants and documents for exactly this) CRASHES 40+ probes across ALT/SEQ/FENCE. At the failure exit rsp sits at the failure depth, not α depth, so every `FRQ` spelling of the marker reads garbage. Register arithmetic (`sub r12,24`) is the only formulation that is both scan-free and depth-free.

**GATES:** run-suite 118/23/0 · compile-suite 0/141/0 · witness ladder 9/9. All green.

**NEXT RUNGS (in order):**
1. ✅ **XFAIL.compile birth** — DONE (corpus `10c87a40`).
2. ✅ **FENCE-WHACK-ON (W-1c.1)** — DONE (SCRIP `b07fe2c9`). `SCRIP_U2_FENCE=0` killswitch.
3. ✅ **ARBNO view-restore (W-1c.2)** — DONE (SCRIP `f11a59b2`). Slot+32 unconditional; `SCRIP_U2` retired.
4. ✅ **W-1c.4 `RT_CAS_TOP` rename** — DONE (SCRIP `a07e4143`). `RT_DCAP_TOP` everywhere.
5. ✅ **W-1c.3 NO-SCAN failure exits** — DONE (SCRIP `a897764e`). LIFO `sub r12,24`; scan deleted.
6. ✅ **W-1c.3 NO-SCAN L(6) post-pump** — DONE (SCRIP `e65ff67d`). LIFO `sub r12,24`; L(5) pre-pump scan kept.
7. **DELETE legacy chain arm** (K16 census done) + dead op_zw2/op_zw arms ride W-5.
8. **W-2 ARM-ALL/flip** → W-4 xc318 reds → W-5 legacy forest.

## ⭐⭐ CURSOR HISTORY — 2026-08-06f (Sonnet — STMT-BETA-LAND R1 LANDED + m4 -o flag; SCRIP `169ad6b4`, corpus `91659735`)

⭐ **SESSION WORK (Sonnet, 2026-08-06f) — R1 fully landed, three coordinated changes:**

**(1) β-TAG SPLIT** (`emit.cpp`): five raw `0xce 0xb2` byte-sniffs collapsed to `port_sz_beta()` per the s22k one-authority law.  New `beta_is_stmt_land(tgt)` predicate distinguishes label-selection (all β edges route to `betas[k]`) from release-suppression (only retry back-edges suppress; a β edge into `IR_STATEMENT_BEGIN` is a pure landing pad — by the UNWIND LAW every box freed own K rolling home, rsp at claim base on arrival).  Three steal guards (UNWIND/ENDJMP/ZW5) now read `omega_is_retry = omega_is_beta && !beta_is_stmt_land(otgt)`.  ZD-5b planner `oin` suppression gets the same conjunct.  Byte-neutral: six witness `.s` files byte-identical vs HEAD `cc39c095`.

**(2) fB dedicated exhaust GOTO** (`lower_snobol4.c` + new `lc_γ_tag_β` in `lower_common.c`): `sno_lower_match` gains `out_land` param; fB = `lc_build(IR_GOTO, fJ, NULL)` + `lc_γ_tag_β(fB)`.  **Tag-only** (not `lc_γ_to_β`) is the key insight: fB's `γ.node` stays `= fJ`, preserving the full GOTO chain to fT so the emitter's used-scan reaches every subsequent statement (the 175 root cause: `lc_γ_to_β` severed the chain from node 10@ to n11@→n12@→n13@, dropping the second `STATEMENT_BEGIN` from `used[]`).  Post-loop retags `fB.γ.sz = β` without touching `fB.γ.node`.

**(3) ZPOP-FOLD guard** (`emit.cpp`): when the fold's `betas[_fk]` lookup finds a `beta_is_stmt_land` target, set `_fk = -1` before the `while`.  Root cause of 06e Layer 2: fold entered, `flat_trivial_beta(STATEMENT_BEGIN)` returned 0, exited with `_sum=0`, trailing `g_emit.op_wpop = 0` erased the UCLAIM-staged release (`add rsp,192` vanished from 067's exhaust site — measured via `.s` diff).

**Also landed: m4 `-o` flag** (`scrip.c`): `scrip --compile -o out.s prog.sno` redirects `--compile` output to a file (both `-o FILE` and `-oFILE` accepted; NULL = stdout unchanged).  Note: `emit_textf()` preamble emits before the fopen in the current form — full capture requires fopen before the preamble; sufficient for the XFAIL.compile baseline rung which uses shell redirect.

**WATERMARK:** xc318 m3 **295/22** (+1 vs HEAD cc39c095 294/23) · m4 **275/40** (unchanged) · DIVERGE **19** (152 env-pad flake — byte-identical `.s`, nondeterministic on both builds). `067_pat_fence_fn_vs_kw` promoted FAIL→PASS m3. `175_pat_bal_generator_retry` holds PASS. No regressions. Regen ×3 clean. SCRIP `169ad6b4` · corpus `91659735` · `.github` this commit.

**NEXT RUNGS (in order):**
1. **CAS-R12-UNIFY** — every `ABSQ(RT_CAS_TOP)` reader/writer in `bb_match_begin/end` → r12; cell demoted to boot-seed; `g_patstk_sp` eradication with C-scanner retirement. RULING 4 island-narrowing rides along.
2. **FENCE-WHACK-ON** — `fence_u2_frame` default flip (SCRIP_U2=1 currently regresses 7 programs; needs investigation before flip).
3. **DELETE legacy chain arm** — replace chain arm body with `x86_bomb()` (33 dispatches all legitimately declined per K16 census; already xfail/DIVERGE; census: `sq=0` blocklist kinds majority, `osv=1` outer-pending SAVE, `framed=1` nested contexts).
4. **m4 `-o` fopen-before-preamble fix** — move fopen before `emit_textf()` calls for full file capture.
5. **W-2 ARM-ALL/flip** → W-4 xc318 reds → W-5 legacy forest (ZWR/UCLAIM, ENDJMP/op_wsteal, killswitch fold).



⭐ **SESSION FINDINGS (Sonnet, 2026-08-06e) — R1 rung fully diagnosed, two-layer blocker identified:**

**(Layer 1 — solved in analysis):** β is a **pure landing pad**, no release. By the UNWIND LAW every box already freed its own K rolling home through β/ω, so rsp is at the claim base on arrival at `STATEMENT_BEGIN.β`. This collapses R1 to ONE edge: `MATCH_BEGIN`'s exhaust only. Element failures belong to `MATCH_BEGIN.β` (the scanner retry loop, manual Ch.18 step 6) and must NOT move.

**(Layer 1 — first approach failed, root cause measured):** Simple `lc_γ_to_β(fJ, sbeg)` introduced 3 regressions (064 crash, 067 wrong output, 175 hang). Root cause: the **β tag propagates through GOTO chains** in `emit.cpp` flat_drive (`if (!gib) gib = (_g->γ.sz is β)`, lines 2166/2479). Re-porting the shared `fJ` retagged every edge chasing through it. Measured on 067: emission collapsed 546 → 306 lines, two statements fell out of the walk.

**(Layer 1 — correct approach found):** Mint a **dedicated exhaust-only GOTO** `fB` inside `sno_lower_match` (out-param `out_land`), wire only `MATCH_BEGIN.ω → fB`, β-port only `fB` in the post-loop. `fJ` untouched. With this: all 5 statements survive in 067, β chain correct end-to-end (`n4_β → n12_α`, `n12_β → n22_α`), 067 prints `both correct`. WIP patch at commit time: 100-line diff, not yet committed.

**(Layer 2 — newly surfaced, is the real blocker):** 067 **segfaults after printing correctly**. The β tag `0xce 0xb2` is **overloaded** — it means BOTH (a) "jump to the target's β label" AND (b) "this is a scanner retry back-edge: suppress release here" (`emit.cpp:2069`, `2475/2480`). When `MATCH_BEGIN.ω` acquires the tag via `fB`, its release is suppressed — correct output but broken rsp at exit. The five spellings of this check (`2069`, `2162-2167`, `2474-2480`, `2543`, `2587-2589`) are one decision spelled five times (s22k law violation). They need to be split: *"targets a β label"* vs *"is a retry back-edge that frees nothing"*.

**WATERMARK:** patterns m3 **107/15** (baseline, same as cc39c095 — no regressions introduced, no commits). SCRIP `cc39c095` · corpus `c04dd8d8` · `.github` `c50b3d0b`. All trees clean at origin.

**NEXT RUNGS (in order):**
1. **SPLIT the β-tag overload** in `emit.cpp` — separate `0xce 0xb2` meaning (a) label-selector from meaning (b) retry-back-edge release suppression. The five spellings (`2069`, `2162`, `2474`, `2543`, `2587`) are ONE authority; introduce a second port tag for (b) or a predicate that identifies retry edges by graph topology rather than tag. This is the GATE for R1 completion.
2. **STMT-BETA-LAND** (completes R1): land the `fB` dedicated-landing approach on top of the tag split. `sno_lower_match` gets `IR_t ** out_land`; `fB` β-ports to `sbeg`; `fJ` untouched. No release at β per the UNWIND LAW.
3. **DELETE the legacy chain arm** + counter/link/U2 quads (unblocked by K16 census, independent of above).
4. **CAS-R12-UNIFY.** 5. **FENCE-WHACK-ON.** 6. **m4 `-o` argv fix.** 7. W-2 ARM-ALL/flip.

## ⭐⭐ CURSOR HISTORY — 2026-08-06c (Fable, Lon hands-on — DECLINE CENSUS DOCUMENTED (queue-#1 doc half DONE); STATEMENT-PORT LAWS RULED; INDEPENDENT VERIFICATION GREEN)

⭐ **LON RULINGS 2026-08-06 (afternoon, binding — the STATEMENT-PORT LAWS):** (1) statement FAILURE lands at STATEMENT_BEGIN's **β** — the release there may WHACK-FREE BY ADD because the UNWIND law (ω frees own K) plus the abandon path's absolute `cas_rsp_mark` re-base guarantee rsp==claim base on every failure arrival; (2) statement SUCCESS lands at STATEMENT_END's **α**; (3) STATEMENT_BEGIN sets an RBP frame **ONLY for UNKNOWN stack-depth statements** ("DO NOT set up a frame when you do not need it") — known extent ⇒ `add rsp,ΣK`; unknown extent (a FRAMELESS_K arbno's committed growth) ⇒ STATEMENT_END pops the frame (`lea rsp,[rbp+K]` off stmt_base + old_rbp restore, the landed `op_stmt_dyn`/`dyn_whack` mechanism). **Census on HEAD emission (N04): all three laws HOLD** — success jmps `n19_statement_end_α` carrying the ONE dyn_whack in the program; the fail glue releases by ADD on the β side; frames added beyond the dyn statement: zero.

⭐ **THE K16 DECLINE CENSUS (queue-#1 "document the declines" — DONE; deletion of the legacy chain arm is now UNBLOCKED):** the ONE routing authority (`emit.cpp` IR_MATCH_ARBNO prelude) arms FRAMELESS_K iff `_sq && !_k0 && _kk>0 && !_fr && !_osv`. The four decline classes, each with its mechanism: **(a) blocklist kinds in the body span** (ALTERNATE / ARBNO / FENCE1 / DEFER / PATREF / VALUE / CALL / CALL_VALUE / DISJUNCTION / ABORT) — path-dependent or unbounded frontier at body-γ makes σ's `[rsp+kk]` static offset unsound; FENCE1 is doubly load-bearing: a SEALED body re-aims PAIR(1)→na_f, and the arm's retract/null-progress jumps through PAIR(1) would land the fail-glue def with rsp mid-cells. DEFER/PATREF decline for the same reason as CALL: transfer boxes enter a foreign pattern graph through the pass-wires, so the frontier at their γ is the TARGET graph's runtime shape — unknowable here. **(b) `!_k0`** — K0 bodies belong to the in-place arm (512ff8cd made it top-level-unconditional). **(c) `!_fr` (contained)** — an arbno inside another arbno's span: the container's element machinery owns rbp/depth there; HEAD routes (chain/nary) are the sound ones. **(d) `!_osv` (OUTER-PENDING SAVE)** — a `MATCH_ASSIGN_SAVE` inside the match bracket but OUTSIDE the body span (e.g. `ARBNO(P) . W`) parks a cursor cell at a fixed depth that the growing frontier reads at iteration-varying displacement; this class belongs to a future CARRY-CAPABLE arm (the cell must ride the re-home). Each decline stages nothing and is byte-identical to the pre-rung routes.

⭐ **INDEPENDENT ADVERSARIAL VERIFICATION (this session, Fable seat 3):** HEAD `512ff8cd` re-verified from scratch after a stale-summary false start (seat note: the session's first hours re-derived the rung against a self-broken tree — reset --hard recovered; the re-derivation CONVERGED on `!_fr` independently, corroborating the committed predicate). Witnesses all green at HEAD: N03 N04 N14 X03 X05 = REF both media; micro-probes w_retract (`S:a`), w_nullk (null-progress guard, `S:`), w_exh (full 3-instance retract cascade, `F:`) = sbl-identical. **FRESH WATERMARK:** suite **133 / 8 xfail (D07 D08 D11 G01 G02 G16 H01 H21) / 0 / 0**; xc318 **m3 293/24 · m4 287/28 · DIVERGE 7** (test_stack 117 127 152 161 173 W02); regen ×3 `.s` artifacts = ZERO drift; build reproducibility proven (.s == reference byte-exact). `SCRIP_ARBNO_K16=0` correctly reverts the class to pre-rung behavior (N14 crash returns) — killswitch semantics are against the rung's PARENT, not HEAD-default.

**NEXT RUNGS (in order):** 1. **DELETE the legacy chain arm** (unblocked by the census above) + counter/link/U2 quads. 2. **CAS-R12-UNIFY.** 3. **FENCE-WHACK-ON** (`fence_u2_frame` default flip — cheapest real win). 4. **m4 `-o` argv fix** → `XFAIL.compile` birth. 5. W-2 ARM-ALL/flip → W-4 xc318 reds → W-5 remaining legacy (ZWR/UCLAIM forest, ENDJMP/op_wsteal, killswitch fold).

## ⭐⭐ CURSOR HISTORY — 2026-08-06b (Fable, Lon hands-on — ARB-LON-K16 LANDED; SUITE 131/10/0/0; xc318 m3 293 m4 287; ZW_RB PROVEN DEAD)

**Rung 1 of the 2026-08-06 queue is LANDED.** `bb_match_arbno_frameless_k`: the 16B `{Δ0,yield}` cell RE-HOMED to the frontier at each σ commit — σ reads the previous cell one level in at `[rsp+kk]` (kk = Σ zd_k over the body span, THE ONE K AUTHORITY), copies Δ0 forward; exhaust reads `[rsp+0]`; retract frees 16 onto the body frontier for PAIR(1). Non-popping growth kk+16/commit, released by bracket whacks only. Statement release goes mech-2 when the arm fired (`g_arbk16_stmt` latch → `op_stmt_dyn` → `lea rsp,[rbp+op_zgpop]` before the old_rbp reload); FAIL exits stay static LAWFULLY — the exhaust cascade retracts all growth during unwind (FOUR-CLAUSE LAW, witnessed).

**Admission (ONE routing authority = the emit.cpp IR_MATCH_ARBNO prelude, BEFORE the fc_tail claim; env killswitches `SCRIP_ARBNO_K16`/`SCRIP_ARBNO_FRAMELESS` read there ONLY; template keys purely on staged `op_arbno_body_kk>0`, above the geometry bombs):** sequence-only span ∧ kk>0 ∧ **!framed** ∧ **no outer-pending SAVE**. The two declines are LAWS, not caution — see `FINDING-2026-08-06-CLAUDE-SN4-ARB-LON-K16-LANDED-...md`: (A) net-zero-delta under a legacy chain outer (X03/X05), (B) static SAVE↔COND distance across the ARBNO (166; fc_tail's fpb CONFLATES body-interior with outer cells — the discriminator is the match-bracket scan, window = (MATCH_BEGIN, next MATCH_BEGIN) because **MATCH_END's cfg index precedes the body nodes**, a creation-order trap now on record).

**Gates:** suite **131 pass / 10 xfail / 0 XPASS / 0 REG** (N14 exhaust-retract promoted out of XFAIL.run same-commit; the K16=0 arm's single expected delta IS N14 = HEAD reproduced). xc318 default m3 **293/24** m4 **287/28**, movement = `158_pat_cap_arbno_each_iter` F→P BOTH modes, zero new, DIVERGE 7 = baseline. K16=0: m3 set EXACT; m4 delta = the 127/152 flake pair only. Killswitch-OFF `.s` byte-identical to `c7a276f6` (stash A/B ×4 programs). Regen ×3 clean, zero artifact drift.

⭐ **TOP-LEVEL-K0 CONVERGENCE LANDED SAME DAY (SCRIP `512ff8cd`, corpus `c04dd8d8`): suite 133/8/0/0.** The framed gate on the K0 arm was scoping conservatism — pure-rsp, +16 billed by zd_k(ARBNO)=16, so the static-distance laws hold at depth 0; non-tail only (op_tail wins first). Fixed N08/N09 (outer `$`/`.` over a K0-ARBNO group): **outer-pending cells compose with STATIC delta — the laws bar only DYNAMIC delta**, now witnessed from both sides. xc318 movement = the 127/152 flake alone (127 has no ARBNO node; no causal path).

⭐ **SCRIP_ZW_RB=1 IS DEAD CODE AT HEAD (W-1b list is STALE):** byte-identical both arms; the mech-2 predicate is parasitic on UCLAIM staging that only default-OFF `SCRIP_ZD_MATCH` populates. The default regime already IS the model trunk (shape census in the FINDING). **W-5 deletes the ZWR/UCLAIM forest; nobody debugs it.**

**NEXT RUNGS (in order):**
1. **K16 widen honestly or document the declines** (DEFER-body exclusion; the outer-pending class belongs to a future carry-capable arm) — then **delete the legacy chain arm + counter/link/U2 quads + top-level-K0 convergence** (top-level single-activation = the same two-compare form, cell in the head claim).
2. **CAS-R12-UNIFY** (Lon mandate): every `ABSQ(RT_CAS_TOP)` in bb_match_begin/end → r12; cell → boot-seed; then `g_patstk_sp` eradication. RULING 4 island-narrowing rides along.
3. **FENCE-WHACK-ON:** flip `fence_u2_frame` default — cheapest real win on the board.
4. **m4 `-o` driver argv fix** then `BASELINE=1 MODE=compile` → birth `XFAIL.compile`.
5. Then W-2 ARM-ALL/flip; W-4 the remaining xc318 reds toward ALL-programs; W-5 legacy deletion (chain, ZWR/UCLAIM, ENDJMP/op_wsteal, killswitch fold).

## ⭐⭐ CURSOR HISTORY — 2026-08-06 (Fable, Lon hands-on — ARBNO-LON LANDED; GATE GREEN 130/11/0/0, FIRST GREEN IN CURSOR HISTORY)

**THE 5 NESTED-ARBNO SIGSEGVs ARE CLEARED (H24 H25 X02 X06 X11), both media.** SCRIP `c7a276f6` + feature `.s` `77236760`; corpus `f47e2469` (35 XPASS dropped from XFAIL.run per the suite's same-commit law — deferred debt from s9, now paid). Suite: **130 pass / 11 xfail / 0 XPASS / 0 REGRESSION, exit 0.** Killswitch `SCRIP_ARBNO_FRAMELESS=0` reverts the class to the legacy chain arm.

⭐ **LON RULINGS 2026-08-06 (supersede the CSL frame draft and the 48B-frame sketch of the same morning):** ARBNO needs NO frame, NO counter, NO element links, NO view register, and NO chain — *"When will that chain be traversed? Never."* Growth is released wholesale by the BRACKET constructs only (MATCH_END final whack / FENCE commit / STATEMENT_END). **Frame census refined: {STATEMENT · FUNCTION · MATCH_BEGIN · FENCE1} — ARBNO dropped out** (CSL-5 answered). Operand law confirmed by Lon: **ALL operands rsp-relative; RBP holds housekeeping ONLY** (the FB-STMT directive, now construct-complete). Register mandate: pattern state via **R12(CAS island)/R13(Σ)/R14(δ)/R15(Δ) only** — no globals.

⭐ **THE LANDED MECHANISM (bb_match_arbno.cpp `bb_match_arbno_frameless`, ~12 insns vs ~40):** ONE 16B α-carved rsp cell `{Δ0 dword, yield dword}`; σ junction = `cmp r14d,[rsp+4]; je resume`; exhaust = `cmp r14d,[rsp+0]` — δ==Δ0 ⟺ nothing committed (σ guarantees every committed instance advanced; the un-match cascade restores δ instance-by-instance), so δ arrives at ω already ==Δ0: **the Δ-assert holds by construction**. Instance k's entry IS the (k−1)th yield — one rolling datum, the shipping semantics. Gated `op_arbno_framed && op_arbno_body_k0` (nested ∧ body-all-K0 via the zd_k ONE-AUTHORITY — never a second K list).

⭐ **X02 GDB GROUND TRUTH (this session, the prescribed s10 probe):** iteration-2's inner header was written at phys == iteration-1's LIVE outer element view (`e6d8`); corruption surfaced as MATCH_END `mov rsp,[rbp+64]` → rsp=0x3 (STRING tag). The counter/link machinery WAS the defect; deletion, not repair, was the fix.

⚠ **MODE=compile SUITE LANE IS DARK AT HEAD (pre-existing, NOT this rung):** `scrip --compile f -o out` fails `-o` parsing in this container ("cannot open '-o'"), so the suite's m4 lane is 0-pass and `XFAIL.compile` was never created. Direct as+gcc proof used instead: X02/X06/H25/X11 mode-4 binaries oracle-exact. **Named rung: fix `-o` (driver argv), then `BASELINE=1 MODE=compile` to birth XFAIL.compile.**

**NEXT RUNGS (in order):**
1. **ARB-LON-K16 — widen the frameless arm past body-K0:** K>0 bodies (ASSIGN_SAVE cells, DEFER records) need per-site static-depth compensation for the one cell (the op_zread shape, one level in). Then delete the legacy chain arm + counter/link/U2 quads for top-level too (top-level is single-activation — the same two-compare form with the cell in the head claim).
2. **CAS-R12-UNIFY (Lon mandate):** every `ABSQ(RT_CAS_TOP)` reader/writer in bb_match_begin/end → r12; cell demoted to boot-seed; fixes the documented blob-capture mismatch (emit.h ZW-16 note). Then `g_patstk_sp` eradication with the C-scanner retirement. RULING 4's match-scoped island narrowing rides along.
3. **FENCE-WHACK-ON:** flip `fence_u2_frame` default (built, documented, gated off — "cheapest real win on the board").
4. **m4 `-o` driver fix + XFAIL.compile baseline** (see above).



**⛔ READ `ARCH-SNOBOL4.md` §THE THREE COMBINATORS BEFORE PROPOSING ANY ERADICATION RUNG FOR SEQUENCE / ALTERNATE / ARBNO.**
Evidence: `FINDING-2026-08-05b-CLAUDE-SN4-ALT-SHELL-IS-WIRING-...md`. Embodiment: `test_sno_1.c` **341 → 312 insns** (-O0), oracle-exact.

| combinator | IR node | ports | **local storage** |
|---|---|---|---|
| SEQUENCE | NO | NO | **ZERO** — wiring. A "zipper" node may exist but is **worthless and slower.** |
| **ALTERNATE** | NO | NO | ⛔ **ONE PER-ITERATION DATUM — REQUIRED. IT IS A BOX.** |
| ARBNO | NO | NO | **ZERO** — every datum it appears to touch belongs to ALT. |

⭐ **ALT CHAIN IS `β → NEXT α` (Lon's form).** `Mi_ω` and `Mi_β` land on the SAME target — one edge set, not two.
`alt_i` written at **γ** (live arm known), not `++`-walked at ω. Measured 322→316 vs the ω-chain on probe d0.

⛔ **ALT's β ENTRY IS NOT WIRING — FALSIFIED BY EXHAUSTION.** Static target set is CLOSED (each arm's β, or A_ω);
every element fails against two probes whose live arm differs (`test_sno_alt_d0.c` → arm 2, `test_sno_alt_d5.c` → arm 1).
Perfect diagonal, none passes both. Selector = **DATA, not CONTROL**; integer or resume address, **must be a BB-local of ALT.**

⛔⛔ **THE TRAP FOR THE NEXT RUNG:** dropping the ALT kind while keeping the datum leaves the claim **UNOWNED** —
`zls_grant_locals` dispatches on KIND and would have no case to fire on. **That is the SE-6 defect verbatim** (the very
thing the 5 open SIGSEGVs are). Collapse ALT's ports if you want the −19 insns, but **NAME THE SURVIVING CLAIM AUTHORITY FIRST.**

⭐ **ARBNO ζ-STORAGE IS TWO-TIER (Lon question 2026-08-05).** **STATIC-depth ARBNO: ZERO — pure wiring, remove the box.**
**UNBOUNDED-depth (nested, or via a RECURSIVE pattern): exactly ONE slot** — the saved entry frontier. Not a list, not per-iteration.
⛔ **THE WHACK IS REQUIRED** (measured leak 0→10→20→30 over 3 successive matches; ζ=rsp ⇒ stack leak) but is **O(1): ONE STORE, +2 insns**,
because the region is **LIFO**. **NO LIST WALK FREES ANYTHING.** ⚠ The single-match probe CANNOT see the leak — probe the whack with ≥2 matches.
⭐ **The `cas_top → cap.prev` chain is the CAPTURE's, not ARBNO's, and it COMMITS rather than frees** (`test_sno_4.c`: *"READ AT EXACTLY ONE
PLACE — the commit on match success"*, `RPOS0_γ: commit(cas_top)`). Order is **COMMIT-THEN-WHACK**.
⛔ **The emitter stores `rsp_mark` UNCONDITIONALLY at every `match_arbno_α` — including the static case where the target is a constant and no slot
is needed. That store IS `mov [rbp+248],rsp` in `n19_match_arbno_α`, i.e. the thing aliasing in H24 H25 X02 X06 X11.**

⛔⛔ **CSL-1a DONE — "ARBNO OWNS ZERO BYTES" IS FALSIFIED AS STATED.** It was PARASITIC on the body claiming.
Body claims nothing ⇒ frontier never moves ⇒ `ζ==base` true on first pop ⇒ **retract exits immediately, cursor left CORRUPTED**
(measured Δ=3 vs correct Δ=0 on `POS(0) ARBNO(LEN(1)) 'z' RPOS(0)` / `'abc'`). ⚠ **BOTH variants print the oracle-correct
`Failure.` — ONLY THE CURSOR DISCRIMINATES.** Fourth vacuity: **assert Δ at ω, never output alone.**
⭐ **CORRECTED LAW: ARBNO owns zero bytes IFF its body claims a non-zero cell**; else ARBNO must supply the advance.
`test_sno_1.c`'s 341→312 STANDS — because ALT pays, not because ARBNO is free.
⛔ **EMITTER: `zls_grant_locals` must guarantee a NON-ZERO grant per ARBNO iteration.** A body of pure {0,1} matchers
(LEN/LIT/ANY/NOTANY — no ALT, no capture) claims zero and **silently corrupts the cursor.**

⭐ **ARBNO's remaining true content.** `ARBNO_Δ0` → consumer derives (DERIVE-DON'T-ACCUMULATE). `ARBNO_i` → WAS the ζ frontier
(= rsp under per-BB self-alloc), moved by ALT's own grant/release. Result member → derived. α is a **pure edge**.
**This re-aims the s146 ARBNO-frame eradication:** the per-iteration frame is the BODY's claim, not ARBNO's.

⚠ **SCOPE:** single-entry ARBNO only. Frontier **self-restores on ω** (measured); on **γ** cells stay live by design
(measured offset 10 at success exit) so re-entry needs the caller-side restore. **NESTED ARBNO NOT PROVED — it is the live defect below.**

⚠ **PROBE HYGIENE — `test_sno_1.c` alone returns a FALSE GREEN on any of this.** Its β selector fired **ZERO times**
before this session (instrumented); all four static ALT wirings "passed." Use the two `test_sno_alt_d*.c` probes.

## ⭐⭐⭐ PRIOR CURSOR — 2026-08-05b (Opus — COMBINATOR STORAGE LAWS; CSL LADDER CLOSED 2026-08-06 by the ARBNO-LON rulings above: CSL-1 root class FIXED, CSL-1a's corrected law SUBSUMED (the frameless σ/Δ0 form needs no minimum grant — the junction is cursor-compared, depth-free), CSL-4 done (watermark measured 90/35/11/5 then driven GREEN), CSL-5 answered ({STATEMENT·FUNCTION·MATCH_BEGIN·FENCE1}), CSL-2/3 fold into rung ARB-LON-K16, CSL-6 landed as the frameless arm itself.)

## ⭐⭐⭐ PRIOR CURSOR — 2026-08-05 (Sonnet s10 — SEQ-ERAD ROOT CAUSE DIAGNOSED; gate 90 pass, 5 REG — STILL NOT GREEN)

**NEXT RUNG: break at n21_match_arbno_β in X02 binary, print rbp and [rsp+0] after `mov [rsp],rbp` at each inner β firing. Confirm whether `[outer_view2 + 248]` (inner ARBNO saved_rsp slot in second outer iteration) overlaps with a slot from the first outer iteration's stack frames. Overlap = the bug.**

⭐ **ROOT CAUSE CONFIRMED BY GDB (rsp=0x3 at MATCH_END).** Two hypotheses falsified — see FINDING-2026-08-05-CLAUDE-SN4-SEQ-ERAD-S10. The crash is NOT a geometry offset error (mn hypothesis falsified) and NOT a missing view-restore (view-restore approach produced 11–17 regressions, falsified). True cause: RSP is corrupted with value 0x3 (STRING type tag) BEFORE inner ARBNO L(2) exhaust fires. The inner ARBNO saved_rsp slot at `[outer_view + 248]` reads as 0 at L(2), and rbp at the start of n21_af may have been corrupted before the `mov rsp,[rbp+0xf8]`. Suspect: when outer ARBNO β fires for the second outer iteration with first-iteration inner elements still live on the stack, the second outer element's body window (`[outer_view2 + 192 .. outer_view2 + 296)`) may overlap with first-iteration frame slots. **Next session: measure overlaps of slot addresses across iterations.**

⭐ **SCAFFOLD IN TREE (SCRIP `18e65150`):** `op_body_has_arbno` flag in `g_emit` (emit.h + emit.cpp); false WIP geometry-buffer blocks removed from zeta_storage.c. Template (`bb_match_arbno.cpp`) unchanged.

⭐ **GATE UNCHANGED: 90 pass / 11 xfail / 35 XPASS / 5 REGRESSION. The 5: H24 H25 X02 X06 X11 (all SIGSEGV nested ARBNO).**

## ⭐⭐⭐ PRIOR CURSOR — 2026-08-05 (Sonnet s9 — SEQ-ERAD AFTERMATH; gate 81→90 pass, 14→5 REG — STILL NOT GREEN)

**NEXT RUNG: fix nested-ARBNO ZLS geometry (H24 H25 X02 X06 X11 — 5 remaining SIGSEGV).** Full detail + all falsifications: `FINDING-2026-08-05-CLAUDE-SN4-SEQ-ERAD-S9-TWO-DEFECTS-ZD-CLAIM-9-OF-14-AND-NESTED-ARBNO-ZLS-GEOMETRY.md`.

⭐ **9 OF 14 FIXED.** `SCRIP_ZD_MATCH` default flipped OFF in `emit.cpp`. SE-6 deleted the SEQ container, which was keeping pattern elements (POS/LEN/FENCE1/RPOS/capture pairs) off the ZD run as blob-interior operand-closure members. With the container gone, those elements sit directly on the spine and are admitted individually — the claim-depth arithmetic prices a partition that no longer exists. Fix: default-off cures 9 of 14 (FENCE0 ×7 G04 G05 G08 G09 G21 G22 G23 + ALT3-capture ×2 A05 A06). Killswitch `SCRIP_ZD_MATCH=1` restores prior 81/34/12/14 byte-identically — the ladder's killswitch law is now SATISFIED. Re-arming requires a fresh evidence base against the container-free spine.

⭐ **GATE: 90 pass / 11 xfail / 35 XPASS / 5 REGRESSION.** 125 programs correct vs 93. Beats the green parent (95 correct). The 15 XPASS still need dropping from `corpus/probe/bb/XFAIL.run` — deferred to the rung that clears the 5.

⭐ **ROOT CAUSE OF REMAINING 5 — MEASURED (asm comparison HEAD vs `3baa8a5d`).** The inner ARBNO's rsp_mark store (`mov qword ptr [rbp+248], rsp` in `n19_match_arbno_α` for X02) aliases the claim's first qword (`stmt_base + 0`). This overwrites the outer statement claim's data with RSP. On inner ARBNO exhaust, `n19_match_arbno_af` reads back `[rbp+248]` to restore RSP — the slot was modified by iteration bookkeeping, corrupting RSP. In green, the SEQ container's 16B zls slot provided geometric separation; that separation is now missing. Fix belongs in `zeta_storage.c` — either price a 16B buffer into nested ARBNO body claim, or recompute outer ARBNO β frame layout.

⛔ **MON-RE DEFECT C STILL OPEN** but bracketed: monitor on comment-stripped X02 shows "PARTIAL EOF step 3: scr done, spl still emitting stno=2" — confirms crash is post-success. Defect B (stno numbering) needs fixing before monitor is fully usable.

⛔ **KILLSWITCH LAW WAS VIOLATED (prior cursor).** NOW SATISFIED: `SCRIP_ZD_MATCH=1` restores prior regime byte-identically. LON DECISION STILL NEEDED on re-arming timeline.

**WATERMARK: 90 pass / 11 xfail / 35 XPASS / 5 REGRESSION. The 5: H24 H25 X02 X06 X11 (all SIGSEGV nested ARBNO).**

## ⭐⭐⭐ PRIOR CURSOR — 2026-08-04 (Opus session 8 — SEQ-ERAD BISECT; gate 78→81 pass, 17→14 REG — STILL NOT GREEN)

**NEXT RUNG: the 14 — but FINISH MON-RE DEFECT C FIRST.** Full detail + both of this session's own falsifications:
`FINDING-2026-08-04g-CLAUDE-SN4-SEQ-ERAD-THE-17-BISECT-TO-SE6-AND-THREE-DIE-TO-AN-OVER-DELETED-SWITCH-IN-FC-WALK-RANGE.md`.

⭐ **THE 17 ARE SE-6's, PROVED BY BISECT (real builds + real gate runs, not inference):** `f5389c0c` 95/46/0/0 ·
`3baa8a5d` (SE-5, parent of the deletion) 95/46/0/0 · `a1caa5b6` (SE-6) 78/31/15/**17**. SE-0…SE-5 are CLEAN;
the whole set enters at the node deletion.

⭐ **3 CLEARED — `fc_walk_range` had TEN case labels, a `break`, and the `lit_ok` arm over-deleted** (only
`IR_MATCH_SEQUENCE` should have gone). What was left fell through to `default: lin = 0`, so the function
returned 0 unconditionally — dead. Its twin `fc_tail_walk`, edited in the NEXT HUNK of the same commit, was
edited correctly; **the two siblings disagreeing is the defect signature.** Fixed → **81/34/12/14, zero newly
broken** (L16 N03 N04). ⚠ **N03 is the probe the prior session burned its whole budget on with five falsified
design hypotheses** — the cause was a typo-class over-deletion two functions away. DIFF THE DELETION FOR
OVER-REACH BEFORE THEORIZING ABOUT ITS SEMANTICS.

⭐ **MON-RE DEFECT A FIXED** (one line, `SCRIP_TRACE="${SCRIP_TRACE:-99999}"` in the `want_scr` block).
**B and C remain OPEN; C is still where the next seat starts.**

**THE REMAINING 14, all SIGSEGV, all NESTING:** FENCE0 ×7 (G04 G05 G08 G09 G21 G22 G23) · nested ARBNO ×5
(H24 H25 X02 X06 X11) · ALT3+capture ×2 (A05 A06). MEASURED on G05: prints CORRECT output `=S` THEN crashes;
crash PC `0x200000002` (descriptor-shaped, `ret` into garbage, stack corrupt) ⇒ RSP imbalance at statement
exit. **Box-inventory delta vs the green parent is EXACTLY the two `match_sequence_α` boxes**; FENCE emission
(`mov rsp,rbp`) byte-identical. So the ladder's own untested question — box (proved pure wiring) vs NODE
(port-identity anchor + 2N operand container) — is LIVE. Not resolved: could still be a second over-deletion
of the HEADLINE-2 class.

⛔ **DO NOT RETRY (falsified BY MEASUREMENT this session):** (1) `res[i]` picks up the inner call's IR_GOTO
sentinel on nested elements — instrumented, `res_is_sentinel=0` on failing probes AND the passing control.
(2) Divergent `add rsp,N` sizes are the pass/crash discriminator — passing N02 has TWO distinct large releases,
crashing A05 has ONE. Family total is now **seven falsifications across two sessions** — that is the argument
for finishing the monitor, not for a smarter guess.

⛔ **STANDING FACTS TABLE BELOW IS STALE:** live census is 11 textual `IR_MATCH_SEQUENCE` refs, **0 live** (all
in comments, proved by comment-stripping); `BB_MATCH_SEQUENCE`/`bb_match_sequence` = 0; template file gone; kind
absent from every header; build clean; Icon `IR_SCAN_SEQUENCE` scope fence HELD (18 refs, template intact).

⛔ **THE LADDER'S LAW IS STILL VIOLATED — LON RULING NEEDED.** *"Every rung ships a killswitch giving
byte-identical revert. Do not half-land."* SE-6's deletion is UNCONDITIONAL: `seq_static_on` = 0 refs, only
`SCRIP_SEQ_FOLD` survives and is unrelated. **No byte-identical revert path exists.** Retrofit a killswitch, or
rule the ladder unrevertable and green it forward.

---

## ⭐⭐⭐ PRIOR CURSOR — 2026-08-04 (Opus session 7 — MON-RE; gate 78/31/15XPASS/17REG UNCHANGED — STILL NOT GREEN)

**NEXT RUNG: MON-RE — FINISH REINSTATING THE 2-WAY MONITOR, THEN attack the 17.** Full detail + all falsifications:
`FINDING-2026-08-04f-CLAUDE-SN4-SEQ-ERAD-SE6-THE-CURSORS-BLOCKER-IS-FALSE-AND-THE-MONITOR-WAS-DARK-ON-THREE-DEFECTS.md`.

⛔ **THE PREVIOUS CURSOR'S BLOCKER WAS FALSE — DO NOT SPEND BUDGET ON `sno_seq_nary`.** It named the φ-fixup's
nested-allocation scan. MEASURED (env-gated `SCRIP_SEQDBG` dump): `sno_seq_nary` fires EXACTLY ONCE on N03 — the
top-level spine — and its wiring is CORRECT. The ARBNO body never reaches it: `LEN(1) $ OUTPUT` parses as ONE
`TT_CAPT_IMMED_ASGN` node, NOT a `TT_SEQ` (`--dump-ast` proves it). The capture-pair arm (`lower_snobol4.c:1349`)
is the site. ⚠ ALSO: `res[i] = g->all[before]` is ALREADY CORRECT — `lc_build` mints the CONSTRUCT first and the arm
RETURNS the ARGUMENT, so first-allocated IS the resume surface; "fixing" it to `ei` scores **17→30 regressions**
(measured, reverted). And `--dump-ir` is SPINE-ordered, not `g->all`-ordered — do not read allocation order off it.

**MONITOR-FIRST is BLOCKED until MON-RE lands.** The monitor reported `DIVERGE step 1` on PASSING programs (N02)
identically to failing ones — it could bracket nothing. Three independent defects, all root-caused this session:
- **A ✅ cause found, fix NOT applied (ONE LINE):** the `want_scr` block of `test_monitor_3way_sync_step_auto.sh`
  never sets `SCRIP_TRACE`, so `kw_trace==0` and `comm_var` returns before emitting VALUE — even though the script's
  own header says the catch-all needs it. Add `SCRIP_TRACE="${SCRIP_TRACE:-99999}"`. With it, steps 1–2 agree BYTE-FOR-BYTE.
- **B ✅ root-caused, not fixed:** `snobol4.y:233` (`s->stno = ++pp->prog->nstmts`) numbers only grammar-reduced
  statements; SPITBOL counts every line except `*`/`-` **including BLANKS** (`scripts/monitor/build_stno_map.py` is
  the canonical rule). All 169 probes open with comments+blank ⇒ all diverge at step 1 on numbering alone.
- **C ⛔ OPEN — START HERE. EMITTER IS EXONERATED:** on comment-free `nc.sno`, spl says `LABEL stno=2`, scr says `6`.
  `SCRIP_TAPDBG` inside `emit_mon_label_tap` proves all five taps bake CORRECTLY AND IN ORDER (1,2,3,4,5). So the
  wrong stno is a RUNTIME/WIRE fact, not codegen. Two sub-hypotheses already dead: the `IR_GOTO` tap is NOT the source
  (gated it, no change), and the wire is NOT spine-vs-source ordered (STATEMENT_BEGIN nodes are in source order).

**LANDED (both codegen-NEUTRAL — proved by byte-compare vs pristine HEAD):** (1) `emit.cpp:858` `op_stno` promotion
restricted to the statement-bracket kinds — it was promoted from `IR_LIT(nd).ival` for EVERY kind, but that field is
the shared payload union, so `op_stno` was clobbered all walk long and the tap's `>0` guard selected accidents. Real
defect, keep. (2) `emit.cpp:991` `IR_GOTO` tap gated behind `MONITOR_GOTO_TAP` — ⚠ **LON DECISION NEEDED**, RULES.md
calls that site the monitor's trace anchor, it did NOT fix defect C, and it is a reversion candidate.

**WATERMARK: UNCHANGED, RE-PROVED at close — gate 78 pass / 31 xfail / 15 XPASS / 17 REGRESSION.** The 17:
A05 A06 G04 G05 G08 G09 G21 G22 G23 H24 H25 L16 N03 N04 X02 X06 X11 (all SIGSEGV, rc=139). The 15 XPASS still
need dropping from `corpus/probe/bb/XFAIL.run` — NOT done this session (gate not green, left for the rung that greens it).
⚠ GATE IS NOT GREEN — do not build on this commit for performance measurement.

⚠ **PRE-EXISTING DEBT PAID:** step-4 regen produced large `.s` diffs (benchmark 5 / feature 27 / demo 18 files).
NOT from this session — proved by byte-compare at pristine HEAD (`roman.s`: pristine compiler 2463 lines vs committed
artifact 2533, already disagreeing). Session s6 left the tree not-green AND skipped step 4; this handoff pays it.

⭐⭐ **LON RULING #1: GRANTED (2026-08-04 Sonnet session 3, "eradicate them / continue").** SE-4…SE-6 are unblocked.

⭐⭐ **SE-5 ZLS LANDED (Sonnet session 5, SCRIP `3baa8a5d`).** Three ZLS-only changes: `zls_grant_locals` case `IR_MATCH_SEQUENCE` → `return 0`; removed from `zls_locals_shifted`; removed from `zls_s4_ok`. Gate was 95/46/0.

⭐⭐ **SE-4 LANDED (Sonnet session 4, SCRIP `a9be14d`).** Counter arm and seqclean prepass deleted. Gate: 95/46/0.

**WATERMARK: BROKEN at WIP commit `a1caa5b6`.** gate-OFF 290/317 · gate-ON 278/317 carried from W-1b. Probe suite at WIP: **78 pass / 31 xfail / 15 XPASS / 17 REGRESSION.** Do not use WIP commit for performance measurement.

2. ✅ **DISSOLVED (prior session).** Was: *the 26 DAG sequences — call-with-frame or
   tree-ify?* **Both options assumed the DAG is real. It is not.** A SNOBOL4 statement's stage 2 **BUILDS**
   the pattern; a build yields a fresh object, so `A P B` and `X P Y` are two builds each stitching their own
   copy of P's material. The shared subtree is manufactured by LOWER, not present in the semantics — the 26
   are a DEFECT SIGNATURE. `sno_seal_pat(nm)` already returns a `const tree_t *` (**AST**, not IR), so the
   per-site copy is free at the seal; something downstream reuses lowered IR instead of re-lowering. SE-1
   classifies all 26 as **(a) VARIABLE** (memoized pattern reference) or **(b) FLATTEN** (inner/outer S
   sharing an element in one statement — no pattern variable involved at all). ⚠ The old option-A pointer
   named `test_sno_5/6.c`, which was the RETIRED frame-pointer design and is now DELETED (this session);
   the live call-unit embodiment is `corpus/probe/bb/test_sno_cell_5.s`.

**BB_SEQUENCE / IR_MATCH_SEQUENCE IS *NOT* ERADICATED — DELIBERATELY UNCUT.** 45 refs across 10 files
(`emit.cpp` 19 · `zeta_storage.c` 9 · `lower_snobol4.c` 7 · `emit.h`/`IR.h`/audit 2 each · template,
`pat_fold.c`, `ir_query.c`, `scrip_ir.c` 1 each) + `IR_SCAN_SEQUENCE` 18 (Icon). Both template files intact.

**PROVED (C embodiments, oracle-exact): SEQUENCE IS WIRING — and it is a 39-INSTRUCTION WIN, not neutral**
(412→373, `-O0`). Nesting proved too (n=1 degenerates to a pure alias). ⛔ **BUT "NEVER" IS QUALIFIED: the
DAG fence (`emit.cpp:2430`) is the real counterexample** — SNOBOL4 patterns are VALUES, a reused pattern
variable lowers as a SHARED SUBTREE, and the counter is that DAG's runtime disambiguator (a return-address
problem in a sequence-counter costume). MEASURED: probes 150/150 clean, 0 need the counter; full corpus
1061/1087 clean, **26 need it**, in 8 files incl. `beauty.sno`. Precise claim: **BB_SEQUENCE is never
required FOR SEQUENCING.**

**IR_GOTO: DO NOT DELETE — it is the 2-way monitor's trace anchor** (`emit.cpp:992` `emit_mon_label_tap`;
only 2 emitter sites do this; both optimizer passes protect stamped gotos). Deferred/indirect targets
(EVAL/CODE, `$X`) cannot be edges. Redundant instances are ALREADY folded by the optimizer. Opcode STAYS.

**WATERMARK: unchanged, NOT re-proved — zero SCRIP `src/` changes, NO codegen file touched** (so regen ×4
does NOT apply). Carried from W-1b: gate-OFF 290/317 · gate-ON 278/317 · 11 wrong-output regressions.
Probe suite re-run before AND after the consolidation: **95 pass / 46 xfail / 0 XPASS / 0 REGRESSION.**

**LAST SESSION: 2026-08-04 (Opus session 4). `bb_match_sequence.cpp` simplified: ZB-FC-3b arm (op_fc_seq) merged into the SEQ-STATIC arm (same four trampolines, H1b aliases them dead). DAG counter arm kept for the 26 dirty sequences including beauty.sno. Build green; gate 95/46/0 both before and after. No codegen change for the clean path — H1b aliasing was already making them dead.

**LAST SESSION BEFORE THAT: 2026-08-04 (Opus session 3).** Zero SCRIP `src/` commits. Deliverables = (1) independent
re-proof of SEQUENCE-is-wiring + the 39-instruction measurement; (2) nested/L13 embodiment; (3) the DAG
counterexample, measured; (4) IR_GOTO verdict; (5) ⭐ **ONE-COPY consolidation** — all BB embodiments moved
to `corpus/probe/bb/` (25 artifacts), `seq_*` labels now **0** everywhere, every edited file byte-identical
to baseline. FINDING: `FINDING-2026-08-04b-CLAUDE-SN4-SEQUENCE-PROVED-WIRING-IN-C-BUT-THE-DAG-FENCE-IS-THE-COUNTEREXAMPLE-AND-SCRIP-IS-UNCUT.md`.

⛔ **TWO RED FLAGS, NEITHER CAUSED BY THIS SESSION:** (a) `scripts/test_gate_call2bb_stub_regime.sh` is RED
at HEAD (`m4 gated stub kt: got [8] want [48]`) — PROVED pre-existing by re-running against the original
bytes restored from `git show HEAD:`; (b) `ARCH-ICON.md` pointed at `SCRIP/refs/bb/test_icon.c`, a path in
the gitignored `refs/` tree absent from any fresh clone — dead reference, repointed.

⚠ **ONE COPY IS NOW LAW: `corpus/probe/bb/` (see `CORPUS-LOCATIONS.md`).** `SCRIP/seed/` keeps only
`beauty_prog_0428.s`; `SCRIP/bench/` and `.github/` hold no embodiments. Two non-mechanical resolutions:
`test_sno_2/3.c` genuinely diverged (the `seed` copies are strict supersets — they won), and
`test_sno_4.c` was a NAME COLLISION not a duplicate (seed's is a different program, moved in as
**`test_sno_4_seed.c`** — ⚠ PROVISIONAL NAME, rename at will).


**NEXT RUNG: W-1c.0** — fix sequence-capture crash. Minimal reproducer `L13` (`'abcd' ? ((LEN(2) . A) LEN(2)) . B`, SIGSEGV, correct output). Passing neighbour `L12` (inner member capture, no outer parens) brackets it: trigger is a capture whose operand is a **parenthesized group**. MONITOR-FIRST.

Three candidates in cheapness order if W-1c.0 is blocked:
1. **H01** — `FENCE(P)` implemented as bare `FENCE`. Wrong output, exit 0, deterministic, three passing neighbours. No crash in the way.
2. **D07/D08** — `LEN(*N)` deferred integer fails to evaluate. Wrong output, exit 0.
3. **W-1c.0** — sequence-capture crash (MONITOR-FIRST).

**WATERMARK: unchanged, NOT re-proved this session** — SCRIP code untouched. Carried from W-1b: gate-OFF 290/317 · gate-ON 278/317 · 11 wrong-output regressions.

**LAST SESSION: 2026-08-04 (Sonnet session 2).** Zero SCRIP code commits. Deliverables = 141-probe BB test suite (`corpus/probe/bb/`, commit `04cc6415`) with SPITBOL goldens, XFAIL baseline (95 pass / 46 xfail / 0 regression), gate scripts `run_suite.sh` + `mkrefs.sh`. Theory results: (1) SEQUENCE is pure LOWER wiring — no box, no ports, no cell, proved by deletion; (2) leaf boxes carry no value cells — consumer derives from own entry cursor; (3) ALTERNATE irreducibly needs one word — proved negative with two-subject discriminator. New defects found by suite: H01 (FENCE1=FENCE0, wrong output), D07/D08 (LEN(*N) deferred int), false green in bb_witness_ladder.sh (trailing-statement canary exposes N07-class crash the 9-row ladder misses). FINDING: `FINDING-2026-08-04-CLAUDE-SN4-BB-PROBE-SUITE-141-PROBES-SEQUENCE-IS-WIRING-FENCE1-IS-FENCE0.md`.

### WHAT THIS SESSION ADDED / CHANGED

**`bb_witness_ladder.sh`** — 9-row SCRIP-vs-oracle instrument in `corpus/probe/bb/`. Hardened against SCRIP's swallowed-SIGSEGV hazard (handler exits 0 on crash; shell's "Segmentation fault" text never enters child stderr; any gate reading only stdout or `$?` is measuring nothing). Measures the ARBNO/capture frontier, full output compare, no prefix clipping.

**4th bug in test_sno_1.c found and fixed** — `ARBNO_γ` called `write_str(out, ARBNO)` *and* `write_nl(out)`, but `write_str` already terminates with `\n`. 24 lines emitted where oracle emits 13. The prior "GREEN" for case 1 was scored against a stale binary. `sbl -b` re-proof now required on every GREEN claim. All 4 repo copies (`corpus/probe/bb/`, `SCRIP/seed/`, `SCRIP/bench/`, `.github/`) are byte-identical, each verified against `sbl -b`.

**SCRIP measured state (bb_witness_ladder.sh, 5 pass / 4 fail):**
- ✅ ARBNO retried, no capture
- ✅ ARBNO retried, capture INSIDE body
- ✅ ARBNO not retried + outer capture
- ✅ case 1 inner (ARBNO⊗ALT, 11 of 12 yields byte-exact)
- ✅ case 5 (variable-extent SPAN arm — already green, no C reference needed)
- ❌ outer capture, no ARBNO — **correct output THEN CRASH** (the false green the hardened instrument caught)
- ❌ ARBNO retried + outer `$ OUTPUT` — heap exhaustion
- ❌ ARBNO retried + outer `. VAR` — empty result
- ❌ case 1 FULL (outer `$ OUTPUT`) — right inner yields, crashes on the outer

**⛔ REVISED BRACKET (supersedes prior session's "retried construct" diagnosis):**
"outer capture, no ARBNO" crashes with correct output — ARBNO is NOT the trigger. It is an amplifier: without it the value is right and only the process dies; with it the value is also lost. TWO defects stacked. **Fix the sequence-capture crash FIRST; re-run bb_witness_ladder.sh; then re-derive the ARBNO bracket from scratch.**

**W-1c.1 FALSIFIED for this class** — `SCRIP_U2=1` is inert on all 9 rows. "Cheapest real win on the board" does not apply to this defect class. (It also gates `arbno_u2_frame()`'s σ/φ view-restore, so it was never a fence-only switch.)

### W-1c — REVISED CONTENT (do these in order)
- [ ] **W-1c.0 · FIX sequence-capture crash** — "outer capture, no ARBNO" crashes (`SUBJ ? (POS(0) LEN(4) RPOS(0)) $ OUTPUT` → segv, correct output then die). This is the deeper defect. Fix it, re-run `bb_witness_ladder.sh`, update the bracket before touching ARBNO. MONITOR-FIRST.
- [ ] **W-1c.1 · FLIP THE FENCE WHACK.** `fence_u2_frame()` reads `SCRIP_U2` (**default OFF**) and `bb_match_fence1.cpp`'s header already states Lon's O(activations)→O(depth) argument verbatim. The mechanism is BUILT and DARK. Acceptance: 318 BY SET no regression both modes · retention measurably down on a nested-fence witness · regen ×4. ⚠ `SCRIP_U2` is inert on the ARBNO/capture class; this rung is about fence whack, not ARBNO.
- [ ] **W-1c.2 · EVICT `zv()="rbp"` from `bb_match_arbno.cpp:15`** — only after W-1c.0 lands and the bracket is re-derived. Do not code against the superseded "retried construct" paragraph.
- [ ] **W-1c.3 · CAS scope narrowing** — carve/reset at MATCH_BEGIN, release at MATCH_END; retire the process-wide `RT_CAS_TOP` pin. ⛔ Do NOT fold CAS into ζ — RULING 4 prices three schemes and all fail.
- [ ] **W-1c.4 · one-line `CAS` definition at `pin_va.h:9`** (undocumented in-tree; collides with Compare-And-Swap).

### BB CHALLENGE LADDER — `corpus/probe/bb/BB-CHALLENGE-LADDER.md`
One construct, one problem, one oracle-exact witness. **Cases 1 and 4 are GREEN (C byte-identical to SPITBOL). Case 5 is GREEN in SCRIP (no C reference needed).** Case 1 = ARBNO⊗ALT (4 bugs found total, incl. missing shy-null + harness double-newline). Case 4 = conditional capture INSIDE the ARBNO body.
⛔ **OWED NEXT: W-1c.0 (sequence-capture crash) → re-measure ladder → re-derive bracket → W-1c.2.**

---

## ⛔⭐⭐ LADDER SEQ-ERAD — delete `IR_MATCH_SEQUENCE` and `bb_match_sequence.cpp` completely

**Thesis (Lon, this session):** a SNOBOL4 statement's stage 2 **BUILDS** the pattern. A build yields a fresh
object, so `A P B` and `X P Y` are two builds each stitching their own copy of P's material. The DAG the
fence detects is therefore **manufactured by LOWER, not present in the semantics** — and the 26 dirty
sequences are a defect signature, not a requirement.

**Already proved (do not re-litigate):** SEQUENCE is wiring — box deleted, output byte-identical to `sbl -b`,
twice, including the ω→β backtrack chain and every failure path; **39 instructions cheaper per sequence**
(412→373, `-O0`). Nesting proved; n=1 degenerates to a pure alias. `seq_static_on()` already returns TRUE
for every node, and its own comment calls the counter *"pure glue-dispatch bookkeeping."*

**NOT proved, and SE-6 is where it gets tested:** every proof so far was about the **box**. The **node** does
separate structural work in LOWER (port-identity anchor + 2N operand container). Nothing on record has
tested its removal.

---

### ⛔ SCOPE FENCE

`IR_SCAN_SEQUENCE` (Icon, 18 refs) and `src/templates/bb_scan_sequence.cpp` are **OUT OF SCOPE** and are not
touched by any rung here. Named explicitly because a careless `grep SEQUENCE` hits both families and the
FACT RULE forbids the emitter knowing which language it serves — these are two kinds, not one kind with a
language flag.

### ⛔ `beauty.sno` IS NOT A GATE (Lon, 2026-08-04 session 5)

**`beauty.sno` is the FINAL FINAL DESTINATION** — it becomes SCRIP's new SNOBOL4 parser, `parser_snobol4.sc`
in Snocone source. It is the thing the compiler is being built *to run*, not an instrument to measure the
compiler *with*. **No rung in this ladder may depend on it.** It appears here only as one of the eight files
whose sequences the fence dirties — a datum, never an acceptance criterion.

⚠ **MEASURED SE-0, and it is why this rule is written down:** `beauty.sno` does not compile under the SPITBOL
oracle in a fresh checkout — `semantic.inc(16) : ERROR 217 -- syntax error: duplicate label`, with the listing
printing source line 588 **twice** while the sources hold exactly one `shift` label and exactly one
`-INCLUDE 'semantic.inc'`. SCRIP m3 additionally SIGSEGVs on it with empty output. Logged as its own finding;
**not this ladder's problem.** Had the first draft's `beauty.sno md5 EXACT` criterion survived into SE-4, every
rung below would have failed for a reason unrelated to its own change.

**The instrument is `beauty_suite/`** — 63 files, driver `.sno` + `.ref` golden pairs, per-module so a failure
names which module moved.

## ⛔ RULING #1 IS THE LADDER'S OWN SEAM

The owed ruling — *"stage the SEQUENCE deletion after W-1c.0 + W-2's flip, or now and accept voiding the
W-0b baseline + the killswitch-OFF byte-identity net that W-1..W-4 rests on?"* — gates **SE-4 and below only**.

- **SE-0 … SE-3 are safe to run NOW under either answer.** They diagnose and un-share; they delete no
  opcode, no template, no arm. The W-0b baseline survives intact.
- **SE-4 … SE-6 need the ruling.** They are the deletion.

If the ruling comes back "after W-1c.0," this ladder still runs to SE-3 and parks there with the DAG fixed
and the counter proved customerless — which is strictly better ground for W-1c.0 to stand on.

---

### STANDING FACTS — measured at SCRIP HEAD `f5389c0c`, **RE-RUN BEFORE CITING** (CENSUS SHELF LIFE)

| Symbol | Refs | Files |
|---|---|---|
| `IR_MATCH_SEQUENCE` | 46 | emit.cpp 19 · zeta_storage.c 9 · lower_snobol4.c 7 · emit.h/IR.h/audit 2 each · pat_fold.c, ir_query.c, scrip_ir.c, template, `.bak` 1 each |
| `BB_MATCH_SEQUENCE` / `bb_match_sequence` | 7 | emit.cpp 3 · bb_templates.h · template · zeta_storage.c · `.bak` |

- `src/templates/bb_match_sequence.cpp.bak` **is tracked in git.** A committed `.bak` beside a live template
  gets read as authority later. Dies at SE-0.
- DAG fence = `emit.cpp:2430`. Claim algorithm: for each clean sequence, walk its 2N operands; if an operand
  node is already claimed by a *different* sequence, mark **both** dirty.
- Dirty: **26 of 1087** corpus nodes in **8 files** — `Gen.sno` · `Gen_driver.sno` · `omega.sno` ·
  `omega_driver.sno` · `TDump_driver.sno` · **`beauty.sno`** · `treebank-list.sno` · `treebank-array.sno`.
  Probes: **0 of 150**.

### BASELINE TO CARRY THROUGH EVERY RUNG

- 318-program gate: **gate-OFF 290/317 · gate-ON 278/317 · 11 wrong-output regressions** (carried from W-1b).
- Probe suite: **95 pass / 46 xfail / 0 XPASS / 0 regression.**
- **`beauty_suite/` driver goldens** — `Gen_driver` · `omega_driver` · `TDump_driver` (**three of the eight
  DAG files**) plus `Qize_driver` · `ReadWrite_driver` · `ShiftReduce_driver` · `XDump_driver`. Verified
  reproducing byte-exact under `sbl -b` at SE-0. This is the ladder's oracle.
- Run under `setarch -R`; ASLR is ±2 noise on every m4 figure.

### ⛔ LAW FOR THIS LADDER

Every rung ships a **killswitch giving byte-identical revert**, md5-verified against the committed artifact.
**Do not half-land.** `zeta_choices.h:288` is the standing example: ZR-RSPRBP-1 deleted `ZC_FRAME_R12`'s
*label* while leaving its *code*, and 17 arms silently re-pointed at a basis they were never designed for —
nine net-new crashes, still unfixed. Delete the label and the code in the same slice or neither.

---

### ✅ SE-0 · HYGIENE + BASELINE — LANDED (s5). `.bak` removed, baseline 95/46/0 confirmed.

### ✅ SE-1 · THE DIAGNOSTIC — LANDED (s5). All 24 classified: FOREIGN-ω (not DAG).

### ⛔ SE-1 RESULT (2026-08-04 s5) — **THE DAG PREMISE IS FALSIFIED. ALL 24 ARE FOREIGN-ω.**

Three paths dirty a sequence, not one; the ladder's first draft knew only the DAG one. Instrumented all
three (`SCRIP_SEQDAG=1`, env-gated, zero codegen change) and swept **all 211 SNOBOL4 corpus + benchmark
programs**:

| path | site | events | files |
|---|---|---|---|
| CHAIN — element entry/resume root absent from this chain | `emit.cpp:2422` | **0** | 0 |
| DAG — one operand claimed by two sequences | `emit.cpp:2433` | **0** | 0 |
| **FOREIGN — σ/φ edge from a non-element-root origin** | `emit.cpp:2443` | **32** | **8** |

**32 events / 24 distinct nodes** (HEAD-stamped `f5389c0c`; the inherited "26" was never re-derived).
Origins: **26 `IR_CALL` + 6 `IR_LIT_INTEGER`**. **Side: 32/32 ω — every one is a FAIL edge.**
Files: `beauty.sno` 14 · `omega_driver` 4 · `treebank-list` 4 · `Gen`/`Gen_driver`/`TDump_driver`/`omega`/
`treebank-array` 2 each.

⛔ **CONSEQUENCE:** *"patterns are values → shared subtree → DAG"* is a real property of the compiler and the
claim algorithm at `emit.cpp:2430` implements it correctly — but **it is not why any sequence needs the
counter.** The stage-2 BUILD argument stands as semantics; it is not the live defect. The fence's own comment
named the real class and we read past it: *"GOTO-chased marks from foreign protocol glue — DEFER return,
ARBNO seal — must keep the counter."*

⚠ **The original SE-2a (un-share the flattener) and SE-2b (copy at the seal) are DELETED, not parked.** Both
targeted the DAG. Neither would have moved one of the 24, and both would have scored trivially green — the
vacuous-rung shape this file records four times over.

### SE-2 · THE FOREIGN-ω RUNG  *(replaces the deleted SE-2a/SE-2b)*

**The defect in one line:** a σ/φ-marked **ω** edge enters a sequence from a node that is not in its 2N
element-root list, so the static φ re-point has no legal target and the counter is retained as the runtime
disambiguator. 26 of 32 origins are `IR_CALL` — this is the `:F()` fail protocol re-entering the pattern
spine.

- ✅ **Step 1 (mark mis-attribution) — run per Sonnet session 2.** The 128-hop GOTO chase inherits `mk` correctly; all 24 FOREIGN-ω origins are real external edges (SE-2 step 1 finding: FINDING-2026-08-04c).
- [ ] **Classify each of the 24:** semantically an element (LOWER registration bug) or genuinely external (foreign re-entry).
- [ ] **IR_CALL majority:** call inside a pattern element is still that element — register it; `seqclean` flips to 1.
- [ ] **Genuinely external:** route to call unit (`test_sno_cell_5.s`); do not preserve counter.
- [ ] **6 `IR_LIT_INTEGER` origins:** check vs D07/D08 (`LEN(*N)` deferred int); may be same bug.
- [ ] Killswitch `SCRIP_SEQ_FOREIGN=0` → byte-identical.

**Acceptance:** dirty events **32 → 0**, or every survivor characterized and named · 318 BY SET no regression
both modes · probe 95/46/0 · `beauty_suite` goldens EXACT · regen ×4.

⚠ **`beauty.sno` holds 14 of the 32 — nearly half — and is NOT a gate** (see the exclusion above). Its events
are a *datum* that the class is real and concentrated in the destination program; measure it, never gate on it.

### SE-3 · PROVE THE COUNTER HAS ZERO CUSTOMERS

- [ ] `seqclean` == N/N on all three corpora: 141 probes · `corpus/programs/snobol4` ·
      `benchmarks/snobol4`. Report per corpus with node totals.
- [ ] Explicit re-check of the 8 files; report `beauty.sno`'s node count but **do not gate on it**.

**Acceptance:** zero dirty nodes tree-wide. **If ANY remain, STOP and report** — a residue is a third class
we have not named, not a rounding error, and SE-4 must not run on top of it.

---
**Ruling #1: GRANTED (Lon, 2026-08-04 Sonnet session 3).** SE-4…SE-6 unblocked.

⛔ **SE-4…SE-6 ATTEMPTED + REVERTED (Sonnet session 3).** Build green. Gate: 73/36/10 XPASS/**22 REGRESSION** — all capture SEGVs from frame geometry shift when `IR_MATCH_SEQUENCE` chain anchor removed. 10 genuine XPASS (correct fixes). FINDING-2026-08-04e. Tree at `f5389c0c`; gate 95/46/0. Next: SE-6a (accept regressions, monitor-bracket A05) then SE-6b (fix ZLS frame depth, 0 regression).

### SE-4 · DELETE THE COUNTER ARM

- [ ] Cut the DAG-counter arm from `bb_match_sequence.cpp`; SEQ-STATIC becomes the only arm.
- [ ] Cut the fence machinery (`claim[]` walk, `emit.cpp:2430`) and `SCRIP_SEQSTATIC_MAX`.
- [ ] `fc_seq_*` in `zeta_storage.c` (9 refs) — footprint arithmetic with no customer once every SEQ is
      static. Verify no live caller, then cut in the same slice.

**Acceptance:** 318 BY SET · probe 95/46/0 · `beauty_suite` goldens EXACT · regen ×4.

### SE-5 · DELETE THE BOX

- [ ] LOWER wires elements directly: σ = `elem_i → elem_{i+1}.α`, φ = `elem_i → elem_{i-1}.β`.
- [ ] Remove `bb_match_sequence.cpp`, its `bb_templates.h` entry, and the 3 `BB_MATCH_SEQUENCE` dispatch
      refs in `emit.cpp`.
- [ ] **Expect an instruction-count DROP.** Record the corpus-wide delta; a flat or rising count means the
      static edges are not replacing what the box was doing.

**Acceptance:** as SE-4, plus the measured size delta.

### SE-6 · DELETE THE NODE  ⬅ the untested half

The node's remaining job: **port-identity anchor** — S is first-allocated, so S.β *is* the construct's
resume surface and S.ω *is* the leftward exhaust, "zero chase machinery" — plus the 2N `(entry_i, resume_i)`
operand container.

- [ ] `sno_seq_nary` returns **(first, last)** instead of S. Parent wires α→`first.α`, β→`last.β`, receives
      γ from `last`, ω from `first`.
- [ ] The inside-edge TAG scheme goes with it: elements no longer rendezvous at S for σ/φ retagging (γ→S
      retagged σ, ω→S retagged φ, FAIL-goto's γ→S also φ). Wire neighbours at lower time instead.
- [ ] **Fence seams — preserve verbatim.** Each maximal fence-free run of ≥2 elements currently gets its own
      S with the run's shared fail target; a run right of a fence fails to the SEAL target, **never back
      across the fence**. This is the one behavior the node deletion is most likely to silently break.
- [ ] Delete `IR_MATCH_SEQUENCE` from `IR.h`, `scrip_ir.c`, `emit.h`, `ir_query.c`, `pat_fold.c`, the audit
      tool — **label and code in the same slice.**

**Acceptance:** census == **0** · 318 BY SET · probe 95/46/0 · `beauty_suite` goldens EXACT · regen ×4.

### SE-7 · CLOSE

- [ ] Repoint the LIVE CURSOR's ruling-#2 text — it names *"the `test_sno_5/6.c` model"*, which is the
      retired frame-pointer design and now a dangling reference. The live embodiment is
      `corpus/probe/bb/test_sno_cell_5.s` (call unit, `resume = MY continuation`, carved per entry).
- [ ] Fix `test_sno_cell_5.s:8`'s dangling `test_sno_5/6` reference.
- [ ] FINDING doc.
- [ ] Update LIVE CURSOR: next rung + watermark + last session. *(Handoff step 0 — if the cursor didn't
      move, the handoff didn't happen.)*

---

### ⛔ KNOWN HAZARDS

- **The transit guarantee is the correctness core.** Every element must transit its **own β** on the retreat
  — captures pop, generators resume, deterministic boxes undo-and-fail. Static edges must preserve this. A
  bug here shows up as a wrong *value*, not a crash.
- **MONITOR-FIRST.** Any divergence gets bracketed by the 2-way sync-step monitor before anyone reads code.
- **`.s` artifacts are honest current output, never goldens.** Never wire `.s` byte-identity into a gate.
- **Compare m4, never m3.** Diff fail sets BY SET, never by count.
- **A rung that turns green trivially is suspect.** Four OMEGA rungs ran vacuous s24a→s32 under
  trivially-green gates. If SE-2's fix scores identical everywhere, prove the arm actually fired.


---

## ⛔⭐⭐⭐ THE WHOLESALE PLAN — LADDER W (Lon directive 2026-08-03f, HQ seat, Fable planning session): FRONTS CLOSED, ONE GOAL, ONE SEAT

**Directive (Lon, verbatim this session):** *"ARBNO is not a family. It is one function. It seems we must change the way things are done. This alpha and omega is just not working. This is easy. Why not switch ALL the BB's at once and set the RBP frame for the unbounded case. And then debug that?"* · *"Alloc on alpha, free on omega, whack free on final success and on fenced success."* · *"Take back ALL the split tasks and bring them back into this one GOAL. We are on the home stretch with Opus taking us to the finish line."*

**⛔ FRONTS CLOSED.** `GOAL-SNOBOL4-BB-ALPHA.md` and `GOAL-SNOBOL4-BB-OMEGA.md` are ABSORBED here (banner in each). ONE seat executes LADDER W top-down; the concurrency contract is retired (this work touches `x86_asm.h` + fires regen ×4, so the single-seat rule was already forced — the SN4-RTX ban stands). Cursor lives HERE. Opus executes; stop at the first failing step; MONITOR-FIRST on every divergence per RULES.

### THE MODEL (one statement; sources: THE MODEL §below, WHACK CONTRACT, THE UNWIND four-clause law, STF-UNFLIP comment emit.cpp:2945, O-PB-4 Lon-confirmed frame independence)
Every BB allocates its own K at α (`sub rsp,K`) — blob-interior scanner kinds are K=0 BY DESIGN (s23t finding 1: they ride r13/r14/r15 + frame slots, never 16B spine cells). γ NEVER frees. Failure is an UNWIND: ω frees OWN K only and rolls to pred's β; no fail site ever computes accumulated depth. Whacks are FORWARD/COMMIT only: STATEMENT_END final success (mechanism 1 `add rsp,ΣK` when extent is compile-time determinable, mechanism 2 frame-pop when not) · MATCH_END (SN4 language fence) · FENCE(P) commit (manual: "alternatives within P are only visible moving forward") · FUNCTION return. RBP frames fire at exactly FIVE construct kinds, ONLY where extent is indeterminable: STATEMENT · MATCH_BEGIN (canonical ZW-1 frame, housekeeping at fixed rbp offsets) · ARBNO (manual: shy, null first, one more instance of P per retry — unbounded by definition) · FENCE1 · FUNCTION (SAVE_RESTORE). Frames are INDEPENDENT and nested via the saved-RBP chain (Lon s39 ruling in O-PB-4): ARBNO/FENCE1 never touch MATCH_BEGIN's frame data. Frame interiors address `[rbp+8+off]` (the ZW_RB spelling), never rsp+uclaim phantoms. Bare FENCE backward = O(1) unwind to the match frame floor; ARBNO exhaustion = own frame restore + roll to pred β. `push rbp;mov rbp,rsp` / `mov rsp,rbp;pop rbp` via `bb_glue_framed_enter/leave` ONLY — x86_asm.h:1751's own instruction: "ARBNO/FUNCTION/FENCE1 conversions parameterize the same pair instead of minting new shapes."

### WHY WHOLESALE IS LEGAL WHERE PER-NODE WAS REJECTED (answer the emit.cpp:2068 else-branch BEFORE Opus re-litigates it)
The UCLAIM branch's two diseases: (1) blob interiors re-enter α per backtrack retry → static per-node claims re-carve and leak; (2) head-exhaust release under-frees downstream claims. Under W neither applies: blob-interior kinds carve NOTHING (K=0), so there is no per-retry carve to leak; releases are own-K on ω + frame restore at the construct boundary, so no aggregate release exists to under-free. The UCLAIM head-claim was a stand-in for frames that didn't exist yet. Now they do.

### GATE POLICY DURING MIGRATION (ACCEPTANCE LAW, HQ 2026-08-03e — binding)
Master killswitch **`SCRIP_WHOLESALE`** (=0 → legacy verbatim; default OFF through W-1, flipped ON in W-2's own commit). Killswitch-OFF arm must stay byte-identical every rung through W-4 (that is the safety net; regen no-ops prove it). The migration arm is gated by LADDER PROGRESSION + WITNESSES + CENSUS MOVEMENT — **never BY-SET identity; an identity gate on the migration selects for never migrating.** The watermark WILL crater at the flip and recover through W-4; report the fraction honestly, per-session, vs the W-0 baseline. BY SET ≥ baseline both modes is the W-6 END condition, not a per-commit gate. DoD = the six conditions at the top of this file, unchanged.

### LADDER W (top-down; every rung ends with: cursor update here, regen ×4 if codegen touched, commit, U-GATE census line in watermark)

- [x] **W-0a · TAKE-BACK (THIS SESSION, docs only)** — this section + front banners + PLAN.md row collapse + take-back table below. Landed with this commit.
- [x] **W-0b · RE-BRACKET AT MERGED HEAD** — DONE (SN4 session, 2026-08-03). Baseline recorded: M3=282/24/11 · M4=273/33/10/1L · DIVERGE=10 · U-GATE=207 UCLAIM sites/317 programs · roman=`result: VI` (U-2 witness live). Killswitch inventory at session notes. Parent hashes: `.github`=`45edc7b0` · corpus=`8411e48f` · SCRIP=`4d902148`.
- [ ] **W-1 · FRAME THE CONSTRUCTS (construction; SCRIP_WHOLESALE minted, default OFF)**
  ⚠ **STEP 1 WIP — SCRIP `1b38958d`** (SN4 sessions, 2026-08-03/04). Gate-OFF byte-identical confirmed (161/161). Gate-ON: 155/161 pass — simple match+capture correct; 6 regressions remain in BAL/ARBNO/multi-iteration patterns. **GATE NAME CORRECTION: `SCRIP_WHOLESALE` is goal-doc only — actual env var is `SCRIP_ZW_RB=1` (drives `zw_rb_on()` in emit.h:6). All gate-ON tests must use `SCRIP_ZW_RB=1`.**

  **LANDED THIS SESSION (SCRIP `1b38958d` — three bugs in mech-2 blob-frame accounting):**

  **Bug 1 — Infinite retry loop** (`x86_asm.h`): `RDD("rbp",N)` when `x86_fb_data()=false` parses `XK_REGDISP32`; `x86("add",XK_REGDISP32,XK_IMM)` had no dispatch arm — ZB-FC-1 silent drop. The mech-2 β `start_δ` increment (`add dword ptr [rbp-48],1`) silently emitted nothing → infinite loop on every blob-armed pattern. Fix: added `x86_reg_disp32_add_imm32` encoder + `XK_REGDISP32+XK_IMM` arm to the `add` dispatcher (R7). Gate-OFF byte-identical by construction.

  **Bug 2 — SEGV at program exit** (`emit.cpp` line ~2054): mech-2 END depth correction subtracted only 8 (push_rbp) from running `zd`, not blob-member Ks (SAVE cells' `sub rsp,16` inside the frame). STATEMENT_END received inflated `_wzdepth` → `add rsp,256` instead of `add rsp,16` → RSP 240B too high at `ret`. Fix: mirror ZW-12's `_fci` sum: `zd -= 8 + _fci` where `_fci = sum(zd_k(nodes[run[r]]), hpos+1..END)`.

  **Bug 3 — Inflated kc** (`emit.cpp` line ~2063): `kc = (hpos >= 0 && r >= hpos) ? Kc : 0` included the UCLAIM blob span `Kc` for mech-2 members. Under mech-2 no UCLAIM head claim exists (push_rbp is the boundary). Fix: gate `!zwr`. Also removed `_ms` zeroing of STATEMENT_END/STATEMENT zgpop (was compensating for wrong kc; correct value now flows through).

  **LANDED W-1b (SCRIP `2a12b8fe` — Bug4 CAS-reset + ARBNO-rbp r12-save):**

  **Bug 4 — Stale CAS/patstk on mech-2 retry** (`bb_match_begin.cpp`): The mech-2 retry loop (`jmp L(0)`) was missing CAS pop-to-sentinel + patstk/rsp restore. Fix: save post-push `RT_CAS_TOP` (=sentinel_base+24) to `[rbp-72]` at α; at retry restore `RT_CAS_TOP←[rbp-72]`, `g_patstk_sp←[rbp-56]`, `rsp←[rbp-64]`. Two attempts: first saved sentinel_base (pre-push) causing new COND pushes to overwrite the sentinel tag=0 → scan ran off into garbage → SEGV in `rt_dcap_pump`. Corrected to save post-push value → sentinel preserved at sentinel_base[0..23], new entries go at sentinel_base+24 and above.

  **Bug 5 — ARBNO trashes rbp, mech-2 whack reads garbage** (`bb_match_begin.cpp` + `bb_match_end.cpp`): ARBNO uses `rbp` as element-view register (`zv()="rbp"`). After any ARBNO β, `rbp ≠ α-8`. MATCH_BEGIN fail-exit and MATCH_END γ/ω both read `[rbp-N]` header slots and then whack via `mov rsp,rbp`. Fix: save mech-2 frame base `α-8` into `r12` immediately after `mov rbp,rsp` at α (r12 is free per R12-ERAD/ARCH-ICON, callee-saved by C ABI). Restore `rbp←r12` before the first `[rbp-N]` header read; use `mov rsp,r12` for the whack instead of `mov rsp,rbp`.

  **Gate-OFF: 290/317 (was 289/318). Gate-ON: 278/317 (was 155/161 — +123 passes).**

  **OPEN — Bug 6 (W-1c next rung): STF+mech-2 nested frame conflict.** All 11 remaining gate-ON regressions are wrong-output (no crashes) in patterns that combine `flat_stmt_frame=1` (STF outer RBP frame) with mech-2 inner frame + multi-attempt. Gdb autopsy on 162: after mech-2 whack (`mov rsp,r12; pop rbp`), `rbp = STF's outer caller frame` (the value push saved). STATEMENT_END then reads `[rbp+328]` expecting the STF base — but rbp is the STF's parent, not the STF base. Root cause: `pop rbp` in mech-2 destroys the STF's rbp save. Fix direction: mech-2's push/pop must NOT clobber the STF rbp; or STATEMENT_END must recover STF rbp from a saved slot. MONITOR-FIRST on the 11 regressions once the STF/mech-2 nesting is resolved.

  **ZWR regressions (11, all wrong-output):** `064_replace_multi_arm` · `157_pat_cap_arb_alt_keep` · `162_pat_arbno_null_body_guard` · `164_pat_arbno_nested` · `174_pat_bal_manual_example` · `176_pat_bal_balanced_forms` · `W06_pos` · `W06_rpos` · `W06_tab` · `test_stack` · `209_gc_big_strings` (last 2 may be pre-existing).

  Parent hashes: `.github`=`7625ffa6` · corpus=`a330e8b7` · SCRIP=`35794222`.

- [ ] **W-2 · ARM ALL — THE FLIP**
  1. Delete the admission VERDICT in `zd_plan`: every run armed; `zd_wl_kind` + the veto tree (residual zdyn quartet, PATREF `pat_static=0`, FENCE-in-closure, DEFER) become ROUTING (flat vs frame at the nearest of the five boundaries) — a decline ceases to exist as an outcome (HQ ruling: "a decline is a ROUTING to mechanism 2, never a terminal verdict").
  2. The UCLAIM else-branch (emit.cpp:2068) routes to mechanism-2 under the gate: head = `push rbp` (the existing `!zwr` path), never `sub rsp,Kc`. `zvo_uclaim_k` returns 0 every run BY CONSTRUCTION → DoD condition 4.
  3. Land s23t's three written edits (s23t IMPLEMENTATION NOTES, ALPHA file tail): `has_blob` span gate (in-run OR off-run) · `zws` gated `!has_blob` · arm-element γ-chain descent via `operands[2i]`.
  4. O-PB-2 inflation bisect (three candidates + method already written there) — run it gate-ON; tripwire: `any.sno` max carve gate-ON ≤ gate-OFF; `sudoku` stmt_claim stores < 12.
  5. **THE FLIP: `SCRIP_WHOLESALE` default ON — its OWN commit.** Watermark craters here; record it.
  - Acceptance: UCLAIM census = 0 under gate (loose-whitespace grep `sub\s+rsp,\s*[2-9][0-9][0-9]` = 0 over regen'd SN4 `.s` — ⛔ the DoD's literal single-space grep is a FALSE INSTRUMENT against real emitter whitespace, measured 2026-08-03f) · killswitch-OFF byte-identical · witness set from W-1 still green.
- [ ] **W-3 · UNWIND UNIVERSAL (the U-2 content, simplified by frames)**
  1. Match-family fail-capable members join the chain: ALTERNATE arm β = retry next arm · ARBNO β = supply one more instance (manual's own words) · cursor-mover restores. Exhaustion ω = own-K free (mostly 0) + own-frame restore where the member owns one + `jmp pred_β`.
  2. MATCH_BEGIN.β owns the unanchored start bump; bare-FENCE-first = anchored regardless of &ANCHOR (manual pg §FENCE); ABORT = O(1) restore to the match frame floor (mechanism 2 as unwind, never a statement whack).
  3. Retire the r12 CAS parking (O-5) if the monitor demands live CAS coherence across backtrack (ZW16 finding is the hazard record); else defer to W-5.
  - Acceptance: monitor-bracketed vs SPITBOL on pattern rungs 6–7 · **prediction witnesses: roman prints MDCCLXXVI · eval_fixed rc=0** — if either does NOT flip, MONITOR-FIRST names the next bug (that is the instrument working, not the plan failing).
- [ ] **W-4 · DEBUG THE LADDER** — canonical rungs 1→12 (REPO-corpus.md), stop at first fail, MONITOR-FIRST only, one FINDING per land-mine. Known shakeout queue (s23t): 045_pat_rpos · W01_pat_lit_anchor · W03_alt_both_fail · W05_any · W07_capt_imm · pat_bal · capture-replacement · fence-fn-fail. The 127/152 env-pad class must become IMPOSSIBLE (frames kill absolute-sensitivity — the HQ beacon note); if either flakes post-W-3, that is a lead, not a flake. rc=139 tail (14 programs) cleared here. Exit: BY SET ≥ W-0b baseline BOTH modes.
- [ ] **W-5 · DELETE LEGACY (U-3 + the gate forest)** — the UCLAIM head-claim machinery + owner-table declined path + veto diagnostics + ENDJMP/op_wsteal residue + ZW-5 depth stubs (already deprecated) + `g_patstk_sp` six readers + marker scans (O-4 residue) + A-GE goto trampolines IF cheap (demoted: its frontier-noise motivation died with admission). Killswitch disposition table from W-0b executed: SCRIP_ZD_PROC/CAP/FENCE1/PATREF/DYNSCOPE/DYNARM/ZW_RB/ZW5/UNWIND/STMT_FRAME/ARBNO_LATCH/ZPOP_FOLD_OFF fold into SCRIP_WHOLESALE or die; diagnostics (ZD_DIAG/ZD_DEPTH/ZETA_TELEM/GLUEO) and non-SN4 gates survive. U-SHY is MOOT by construction — record it. Completion greps: `grep -rn 'x86_zclaim(' src/templates/bb_*.cpp` = 0 (U-AUTH) · veto strings = 0 · per-kind gate names = 0 outside this doc.
- [ ] **W-6 · CENSUS TO DoD** — U-GATE drives it: ω-cov 100% of K>0 boxes (DENOMINATOR LAW: always name the denominator) · orphan 0 (⛔ audit the whitelist first — SHED-5 landed s34, so the rsp,8 entry may already be stale-permissive) · UCLAIM 0 · wall census == framed-enter count over exactly {STATEMENT, MATCH, ARBNO, FENCE1, FUNCTION} · BY SET ≥ baseline both modes · bench 18/21 hold-or-better · regen ×4 · `rbp-op-refs` trend DOWN recorded (14198 at 2026-08-03f).
- [ ] **W-7 · FINISH** — U-LBL (proc_LBL 2-line trampolines; roman 2713→~1818 lines; kills the double-count in every roman measurement) · U-CALL verify (roman already flipped at W-3 or the monitor said why) · U-IDSP timing line · FINDING + this file's cursor + HISTORY INDEX one-liners. U-BENCH stays PARKED (O2-DIRECTED-ONLY rule — opens only on Lon's word).

### TAKE-BACK TABLE (every open split task → its W home; ✓ = already landed pre-consolidation)
| From | Item | Disposition |
|---|---|---|
| HQ U | U-1a/b unwind | ✓ landed, default ON (ALPHA s41) |
| HQ U | U-2 match-family | → W-3 |
| HQ U | U-3 deletions | → W-5 |
| HQ U | U-GATE census | ✓ landed s40 — the W-6 instrument |
| HQ U | U-WIT uw2/uw3 | ✓ committed corpus/probe |
| HQ U | U-SCOPE | ✓ landed byte-neutral-gated s40 — verify under W-2 |
| HQ U | U-SHY | MOOT at W-5 (gate forest deleted) — record table anyway |
| HQ U | U-AUTH | → W-5 completion grep |
| HQ U | U-CALL | → W-1.3 + W-7 verify |
| HQ U | U-LBL | → W-7 |
| HQ U | U-BENCH | PARKED (Lon-directed only) |
| HQ U | U-IDSP | → W-7 |
| OMEGA | O-PB-2 inflation | → W-2.4 (method as written) |
| OMEGA | O-PB-3 defer arm + PATREF | → W-1.4 (flip moot — no admission to flip) |
| OMEGA | O-PB-4 ARBNO/FENCE1 frames | → W-1.2 (spec verbatim, Lon-confirmed) |
| OMEGA | O-4 residue (markers, g_patstk_sp) | → W-5 |
| OMEGA | O-5 ZW-3 r12 CAS | → W-3.3 or W-5 (monitor decides) |
| OMEGA | O-6 remainder (CLASS C, PAT$N 302, FENCE0) | → W-3/W-5 |
| OMEGA | O-9 RECON | → W-0b (executed once, now) |
| OMEGA/HQ | ZW_RB ratified-exception fix | → W-1.1 (exception honored inside W) |
| ALPHA | A-GE goto-erad | DEMOTED → W-5 optional (motivation was decline-noise; declines cease to exist) |
| ALPHA | RECON / U-AUTH / O-PB-2a thread | → W-0b / W-5 / W-2 |

### WITNESS SET (the board Opus reports against, every session)
uw2 · uw3 · W04_arbno_* · 131 · 141 · 183 · 066 · the 40 ZW_RB pattern programs · 045_pat_rpos + s23t queue · roman (MDCCLXXVI) · eval_fixed (rc=0) · test_case (honest wedge, promotable) · 127/152 (must become impossible).

## ⛔⭐⭐⭐ HQ ADVISORY CURSOR — 2026-08-03e (Lon-directed advisory seat): "ALREADY DONE" FALSIFIED AT HEAD · DEFINITION OF DONE · ONE NEXT — U-2 (OMEGA) + U-GATE (ALPHA) · O-PB PARKED

**Directive (Lon, verbatim this session):** *"I wanted to see OMEGA for every box, and it tells me already done. I think they are so confused. Help them."* / *"get those two sessions back on the proper track to completion."* Full measurement + decomposition + U-GATE spec: `FINDING-2026-08-03-CLAUDE-SN4-HQ-ADVISORY-OMEGA-COVERAGE-IS-26PCT-AND-ALREADY-DONE-WAS-A-DENOMINATOR-ERROR.md`. **Receipts, measured at HEAD:** roman.s = **135 α labels · 123 β · 35 ω** (raw ω-coverage ≈26%); its release multiset carries **8 sizes matching no single carve** (64/80/96/112/128/144/256/272 — 34 accumulated-pop instructions, clause-2's named defect, alive in the flagship benchmark, plus the 2×240 + 2×192 UCLAIM verbatim); **132 of 485** crosscheck `.s` still carry a ≥200B UCLAIM head; `SCRIP_UNWIND` defaults **OFF** (emit.cpp:2370/:2605). The s39 claim *"the per-BB model and the UNWIND ruling are THE SAME MODEL — β already frees own K"* is a three-error compound: (1) β-alias-for-one-shot ≠ ω-on-every-box; (2) "100 of 120" is the ADMITTED subset, not the corpus; (3) a default-OFF gate proven on one witness is a prototype, not the emitter.

**⛔ DEFINITION OF DONE — "ω for every box." No session may use "done"/"complete"/"already" for the directive before ALL SIX; partial = report the fraction, never the word:**
1. `SCRIP_UNWIND` default ON tree-wide (killswitch retained per convention) + **U-3 deletions LANDED** (ENDJMP/op_wsteal · ZW-5 per-depth stubs · zd_wp accumulated fail staging).
2. **ω-coverage = 100%** of K>0 boxes (U-GATE instrument), crosscheck + benchmarks.
3. **Orphan-adds = 0** outside the whitelist (framed `mov rsp,rbp` restores · rsp,8 alignment until SHED-5 · migration-era END staged pops; ΣK folds get their own column, never the orphan bucket).
4. **UCLAIM census = 0** (`zvo_uclaim_k` returns 0 every run; SNOBOL4 `.s` grep `sub rsp, [2-9][0-9][0-9]` = 0) — finishing-plan Step 4.
5. **Wall census == framed-enter count** (STATEMENT/MATCH/ARBNO/FENCE1/FUNCTION) — ZD-DEPTH instrument.
6. Behavioral floor: 318 BY SET ≥ baseline both modes · rc=139 tail (14 programs) cleared · bench 18/21 hold-or-better · regen ×4.

**⛔ ONE NEXT (cursor fragmentation was the disease — three files carried three NEXTs and nobody held the U-2 baton):** OMEGA seat = **U-2** (O-PB-4 is SUBSUMED — it IS finishing-plan Step 2 and lands AS U-2). ALPHA seat = **U-GATE** (ω-coverage census, spec in ALPHA's advisory block + the FINDING §5). **PARKED until both land: O-PB-2b/3 · PATREF default flip · O-PB-2a closure-scoping coordination.** HQ holds rulings + reconciliation only. **ACCEPTANCE LAW for U-rungs:** byte-CHANGE in the predicted direction + witnesses + census movement + BY-SET no-regression are the gates; BY-SET-IDENTICAL certifies ONLY the killswitch-OFF arm — an identity gate on the migration itself selects for never migrating (finishing-plan Step 3's own words: "byte-change is expected and desirable here — this is the payoff"). **PRE-HANDOFF SCAN (e-2, FINDING §9):** OMEGA s40's cursor hashes are pre-rebase ghosts (true landed = `bf489b89`/`c9d84615` on `a9823228`; cursors record hashes AS-PUSHED from now on, post-rebase gate line mandatory) · uw2/uw3 witnesses committed NOWHERE — commit to `corpus/probe/` before U-2 · m3 watermark slid 295→289→280 across seats, invisible to vs-own-parent brackets — **RECON step 0 = ONE shared re-bracket at merged HEAD, recorded env** · ZW-13 is the second conviction for both the acceptance-inversion and ownership-drift diseases · audit s29/s30 φ-glue vs clause 2 as U-2 item 1 · the 127/152 rsp%16 knife-edge gets an owner (U-2 sub-item). **DIRECTIVE AUDIT (e-3, own FINDING `...-DIRECTIVE-AUDIT-SIX-NOT-TRUES-ROMAN-PRINTS-VI-...`):** six NOT-TRUEs measured against Lon's standing directives — roman `proc_LBL` 897-line dup body ALIVE at lines 5–900 (s39's "ALREADY EMPTY" was the label, not the body; Step 5 assigned as its OWN session → U-LBL rung below) · **roman prints `result: VI`** (silent wrong output on the flagship; the s23q last-recursion signature SURVIVED A-2) and `eval_fixed` segvs — **both join the U-2 witness set** · ≥4 carve authorities vs the ONE-traversal directive (`bb_match_begin.cpp:57/:175/:194` + `bb_save_restore.cpp:83` in-template zclaims) · owner-table cross-stmt contamination = live s21x-w breach (routed ALPHA post-U-GATE) · rbp-operand refs: roman 96, tree 9,842 vs "Not. None." — U-GATE gains the `rbp-op-refs` column · perf baseline at -O0: geomean 1.34× vs SPITBOL, losses cluster in CALL (0.40–0.53×) + TABLE (0.30×) = the un-migrated surface · **POSITIVE-CONTROL LAW:** every new instrument hand-verifies one known-good + one known-bad case before its number is quoted (convictions: ZD-DEPTH 3×, this session's 1/21 bench harness).

## ⛔⭐⭐⭐ HQ RULING — THE UNWIND (Lon, 2026-08-03b, verbatim eureka): FAILURE NEVER WHACKS — supersedes every fail-side release clause in this file, including the same-day ENDJMP landing below

**Lon:** the missing β sections were the DEFECT, not an optimization. A failure must NOT know the stack size and jump to a final failure spot. *"The failure from the one box jump through omega to the previous box, un rolling the stack until you reach STATEMENT_BEGIN's beta, whereby you jump to the FAIL label specified or the next statement. ONLY on SUCCESS do you WHACK the entire stack at STATEMENT_END. NEVER on failure do you whack. A failure is an UNWIND."* Second clause same session: *"one more place for a WHACK: a FENCE boundary which guarantees no backtracking... roll up moving forward. Roll down moving backward. whack on fenced (FENCE0 or FENCE1) sync point. whack at final success."* Language note (Lon): SNOBOL4's statement IS a natural FENCE boundary; Icon's statements are expressions and are NOT — Icon's sync points differ, but it is all the same Byrd-Box algebra with language-selected fences.

**THE FOUR-CLAUSE LAW:**
1. **ROLL UP forward:** α carves own K; the spine accumulates non-popping (unchanged).
2. **ROLL DOWN backward — failure is an UNWIND:** box N's ω frees N's OWN K only (restoring any cursor/CAS state from N's own cell first) and jumps to the PREDECESSOR's β. A deterministic (one-shot) box's β IS its ω-continuation: `add rsp,K_own; jmp pred_β` — the two dead-β conventions (n26 pair-with-adds vs n63 bare-leak) were this hole. INVARIANT: RSP at any box's β == RSP at its γ, by induction. NO fail site ever computes accumulated depth — the depth-knowledge problem is not solved, it is DELETED.
3. **WHACK at a fenced sync point, FORWARD path only:** FENCE0/FENCE1 commit = a no-backtrack guarantee → everything behind the fence dies at commit. MATCH_END is a language-guaranteed fence in SNOBOL4 (a succeeded match is never re-entered; replacement failure fails the statement without re-scan) — its frame-pop whack stands.
4. **WHACK at final success:** STATEMENT_END, γ side, the SOLE statement release. STATEMENT_BEGIN.β is the SOLE statement-fail terminus — the unwind arrives with RSP at statement-entry depth BY CONSTRUCTION and jumps to the `:F` target or the next statement. Each statement exits at exactly one end or the other.

**VOIDED by clause 2:** per-node zd_wp accumulated staging on fail edges (the 5,923-site over-free census IS this defect) · the ZW-5 O-2 per-depth ω stub ladder (IR.h's own END comment already says it is not coming back) · the ENDJMP STEAL + `op_wsteal` (a fail-side whack at END — landed this same day, superseded by this ruling; its three witnesses were real, its mechanism was wrong) · the n54-class mid-extent exclusions and every depth-equality guard (the unwind handles any-depth fail edges naturally). **SURVIVES:** the ΣK ζ-POP FOLD — a LEGAL FUSION of the unwind, iff every folded β is whitelisted-trivial (a β carrying a restore leaves the whitelist and the fold cannot fire); law-4 RBP frames — needed for the SUCCESS-side whack of indeterminable extents and for match housekeeping at fixed offsets; MATCH_END's whack (clause 3).

**LADDER U (execution home = OMEGA front; U-1 opened by HQ this session):**
- U-1 · deterministic-spine unwind behind `SCRIP_UNWIND` (default OFF): armed statement-exit fail edges retarget to the unwind chain (nearest prior fail-capable member's β, else STATEMENT_BEGIN's β); staged pop = LOCAL DIFFERENCE of planner totals `(zd_k+zd_wp)[i] − (zd_k+zd_wp)[pred]` (fusion over non-fail-capable members, same legality as the ΣK fold), never the global depth. ENDJMP + ZW5-stub arms stand down under the gate.
- U-2 · match family: generator βs (ALTERNATE arms, ARBNO extension, cursor-mover restores) join the chain as fail-capable members; MATCH_BEGIN.β owns the unanchored start bump; ABORT = unwind-to-match-boundary via the frame restore (mechanism 2 as O(1) unwind, not a whack of the statement).
- U-3 · delete voided machinery once green at the merged head: ω depth ladder, ENDJMP/op_wsteal, aggregate wpop staging.
- U-GATE · ω-coverage census (ALPHA seat, concurrent-safe — ONE NEW FILE `scripts/test_gate_omega_own_k.sh`, spec = FINDING 2026-08-03e §5): per-box own-K release coverage + ΣK-fold column + orphan-release census over crosscheck+benchmarks `.s`; joins the watermark as `ω-cov X/Y · orphan N`; the DoD instrument for conditions 2–3.
- U-LBL · finishing-plan Step 5 as its OWN session (HQ/OMEGA seat, `scrip.c` ~:887/~:1348 — emit main first, every `proc_LBL__*` a 2-line trampoline). Acceptance: roman 2713→~1818 lines · 318 BY SET identical · every `proc_LBL__*` section ≤5 lines (the ≤5-line grep joins U-GATE). Kills the double-counting in every roman measurement. FINDING e-3 §2.
- [ ] **U-WIT · COMMIT uw2/uw3 ACCEPTANCE WITNESSES to `corpus/probe/`** (HQ/OMEGA seat, pre-U-2 prerequisite — FINDING e-2 §S3). `uw2` and `uw3` are the U-1b acceptance programs cited in every cursor; they lived only in a session's `/tmp` and are committed nowhere (`find corpus/probe -iname "*uw[23]*"` = empty, confirmed e-2). Do: write `uw2.sno` + `uw2.ref` + `uw3.sno` + `uw3.ref` into `corpus/probe/` (uw3 is the rc=139 witness — the specific statement whose ω exits to `:F` with an accumulated whack, confirmed correct output then segv; uw2 is the success-path control). Acceptance: `timeout 8s /home/claude/x64/bin/sbl -b corpus/probe/uw3.sno` matches `uw3.ref` · `scrip --run corpus/probe/uw3.sno` with `SCRIP_UNWIND=1` rc=0 and matches ref · uw2 passes both engines both modes. ⛔ **POSITIVE-CONTROL LAW:** verify one known-good (uw2 PASS) and one known-bad (uw3 rc=139 gate-OFF) through the instrument before reporting the gate-ON verdict.
- [ ] **U-AUTH · CONSOLIDATE IN-TEMPLATE CARVE AUTHORITIES into `zls_build`** (OMEGA seat — touches `bb_match_begin.cpp` + `bb_save_restore.cpp`; FINDING e-3 §3). Directive: ONE main function does graph traversal and calculates zeta offsets. Measured exceptions at HEAD: `bb_match_begin.cpp:57` `x86_zclaim(32)` · `:175` `x86_zclaim(48)` (stfh frame — despite the comment quoting the directive verbatim, this is a second authority) · `:194` `x86_zclaim(32)` · `bb_save_restore.cpp:83` `x86_zclaim(sb)` (dynamic size). Routing: the two match_begin 32B claims fold into the planner K under U-2 (ZW-1 canonical frame owns them); the 48B stfh claim folds at U-2 likewise; save_restore's dynamic claim folds at ZD-7 protocol work. This rung is a POST-U-2 audit: after U-2 lands, `grep -rn 'x86_zclaim' src/templates/` must return 0 outside `x86_asm.h`. Acceptance: `grep -rn 'x86_zclaim(' src/templates/bb_*.cpp | wc -l` = 0. ⛔ Do NOT collapse prematurely — the fold is a side effect of U-2 and ZD-7 landing correctly; this rung VERIFIES, does not pre-delete.
- [ ] **U-SCOPE · FIX OWNER-TABLE CROSS-STATEMENT CLOSURE CONTAMINATION** (ALPHA seat, post-U-GATE — FINDING e-3 §4, OMEGA s40 O-PB-2a measurement). Directive: "NO FUNCTION-level processing whatsoever. ONLY statement level scoping." Measured breach: `cm[]` walk during `zd_plan` pulls ASSIGN_SAVE/LIT_STRING/ASSIGN_IMM from stmt1 into stmt2's claim span via `zvo_resolve`'s base scoping, inflating the claim by 224B on `any.sno` stmt2. Fix: clamp the owner-table base to the run's own `umin` as lower bound (O-PB-2a proposed a one-liner `umin = max(umin, run_base)` clamp; verify this is sufficient and doesn't introduce false exclusions). Acceptance: `SCRIP_ZD_DIAG=1` on `any.sno` stmt2 shows Kc ≤ stmt1's Kc (no cross-contamination) · `any.sno` max carve gate-ON ≤ gate-OFF · 318 BY SET no regression · U-GATE `rbp-op-refs` column non-increasing. ⛔ The CROSS-FRONT REQUEST from OMEGA s40 is already filed in ALPHA's cursor; this rung formalizes it.
- [ ] **U-SHY · VERIFY EVERY ADMITTED KIND IS DEFAULT-ON** (HQ audit seat, post-U-2 + U-GATE — FINDING e-3 §5). Directive: "You should be able to turn on allocation dynamically FOR EVERY single BB. No need to be shy." Audit: for each kind in `zd_wl_kind`, confirm its killswitch defaults ON (not OFF) at the merged-green HEAD. Specifically: `SCRIP_ZD_PATREF` (currently default OFF per O-PB-2a/3 prereq — flip is O-PB-3's own rung); `SCRIP_ZD_FENCE1` (default ON per O-PB-1, verify intact); `SCRIP_ZD_PROC` (default ON per A-2, verify intact); `SCRIP_ZD_BREAK`/`SCRIP_ZD_CAP`/`SCRIP_ZD_DYNSCOPE` (verify). This rung does NOT change any default — it is a POST-green audit that produces a table: `kind | killswitch | default | post-U-2 status`. Any kind still default-OFF after U-2 + U-SCOPE green needs a named reason OR a flip rung of its own. Acceptance: the table is committed to `.github` as a FINDING; zero kinds are "OFF — reason: unknown."
- [ ] **U-CALL · IR_CALL/IR_SAVE_RESTORE MINIMAL FRAME SHAPE** (OMEGA seat, post-U-2 — FINDING e-3 §6 + ZD-7 ladder). Directive: "The DEFINE, when CONSTANT FOLDED, emits two BBs, an IR_SAVE_RESTORE and an IR_CALL which just sets up the stack frame with RBP/RSP, and that is all it does." Measured reality: `bb_call_proc_staged.cpp` does argument staging, GVA installs, SCC paths, result-write pairs — far beyond frame setup. And the flagship: roman prints `result: VI` (last-recursion-level signature, call-chain state lost — U-2 witness). Target shape: SAVE_RESTORE = frame-entry only (`push rbp; mov rbp,rsp` + nothing else); CALL = argument wire + call + frame-exit (`mov rsp,rbp; pop rbp`). This rung is the ZD-7 protocol rung renamed with the directive's framing: verify after ZD-7 lands that the two-box shape matches the directive and that roman's output flips to `result: MDCCLXXVI`. Acceptance: roman PASS (result correct) · `func_call` bench ratio improves toward 1.0 · 318 BY SET no regression. ⛔ If roman does NOT flip after U-2+U-CALL, MONITOR-FIRST bracket — that is the next bug.
- [ ] **U-BENCH · DIRECTED -O2 PERF BASELINE** (HQ, requires explicit Lon directive per O2-DIRECTED-ONLY rule). At -O0 geomean is 1.34× vs SPITBOL; the CALL (0.40–0.53×) and TABLE (0.30×) families are the main losses, both C-sink heavy. A directed `-O2` runtime build (`make RT_OPT="-O2 -g -fno-strict-aliasing -fwrapv" libscrip_rt`) would move those families most and give a fair comparison. ⛔ Per s126 lesson: run detached + polled; verify worktree populated and `.so` mtime moved BEFORE and AFTER; label every number with `RT_OPT=-O2` explicitly. Acceptance: the full 21-benchmark board at -O2 committed to a FINDING with the `ms:` timing table + geomean + per-family breakdown. ⛔ **This rung does not open until Lon says "directed -O2" in the session.**
- [ ] **U-IDSP · `indirect_dispatch` EMITS NO TIMING LINE** (OMEGA or HQ seat, small). The benchmark passes correctness (output `6` matches ref) but prints no `ms:` line, so it cannot participate in the perf board and cannot regress visibly. Either add a timing wrapper to the program or add `ms: 0` to the `.ref` and note it is excluded from perf. Acceptance: `indirect_dispatch` contributes a timing number to the 18-bench perf table, or is formally marked EXCLUDED in the BENCHMARKS.md with a note.

**HQ CURSOR (2026-08-03c, Lon directive "get every BB to FREE on OMEGA / all your choices"):**

**⭐⭐⭐ U-1b LANDED — SCRIP `a9823228`, parent `b8b53450`, corpus untouched.**

THREE EDITS behind `SCRIP_UNWIND` (default OFF, gate-off byte-identical stash A/B):
1. `flat_unwind_beta()` — widened pred whitelist: VAR/LIT_INTEGER/LIT_STRING/BINOP/UNOP/ASSIGN/ASSIGN_VAR/CMP_TEST/COERCE_NUMERIC/COERCE_STRING/COERCE_INTEGER/COERCE_REAL/DEREF/SUBSCRIPT/FIELD_VAR + the four flat_trivial_beta kinds.
2. U-1b β LIVENESS pre-pass — conservative over-mark (never under-mark = wild jump), breaks the circular prophecy that kept value-spine βs elided.
3. U-1a retarget widened: `flat_trivial_beta` → `flat_unwind_beta`.

MEASURED on uw3 (FINDING-2026-08-03 baseline witness): `n9_cmp_test` ω gate-OFF = `add rsp,16 / add rsp,64 / jmp n30_stmt_begin_α` (accumulated whack). Gate-ON = `add rsp,16 / jmp n8_coerce_numeric_β` (own-K free + roll). The law is emitted verbatim. Fire set 0→17 jmp-to-β.

ACCEPTANCE: gate-off byte-identical · m3 BY SET IDENTICAL (excl. documented 127/152 alignment-flake instruments) · m4 BY SET IDENTICAL · uw3 rc=0 both.

**CENSUS SCOPE NOTE:** ZD-DEPTH wall census reads 469 both gates — not a regression. It measures multi-depth joins WITHIN the armed set; U-1b resolves non-join ω edges escaping to :F targets outside nodes[]. Those never appeared as joins. Census is correct; the acceptance instrument for U-1b is BY SET + uw3 behavioral, not wall count.

**NEXT = U-2** (match family: ALTERNATE/ARBNO/FENCE1/MATCH_BEGIN βs join the chain; OMEGA seat per the ladder). ALPHA and HQ recon owed once OMEGA O-9 lands. **WATERMARK (U-1b):** m3 **289/26/2** · m4 **282/36** · BY SET both modes · 127/152 flake instruments excluded per s38 ruling · regen ×4 owed (codegen gate-off unchanged; deferred to next code landing per RULES).

**HQ CURSOR (2026-08-03b — U-1a):** Ruling recorded (this block + relays in both fronts). U-1a LANDED INERT — gate-on fire set empty (no emitted βs to retarget into). U-1b recipe in `FINDING-2026-08-03-CLAUDE-SN4-HQ-UNWIND-RULING-U1A-SKELETON-INERT-...md`.

## ⭐⭐⭐ HQ LIVE CURSOR — 2026-08-03 (Lon-directed): ENDJMP STEAL — SCRIP `a571c6bc`, corpus `f34d76b6`

**Directive (Lon):** Scrutinize `&TRIM = 1` statement. Reduce the two RSP instructions at `n26_call_α`, jump to `n27_statement_end_α` in TWO places (fail edge and β stub). Three problems total.

**Three problems, one defect (WHACK CONTRACT item 4 — terminal release fused into operator exit edges instead of routed through END):**
1. Fail-edge `add rsp,16` + `add rsp,32` pair — two instructions for one release, forbidden per contract.
2. Fail-edge `jmp n28_statement_begin_α` — bypasses `n27_statement_end_α`, the SOLE whack authority.
3. β stub (`n26_call_β`) same pair + same bypass.

**Fix (drive-loop `node_ω` retarget, ZW-5 steal mechanism pointed at the right target):** A full-extent statement-exit ω is retargeted to the statement's `IR_STATEMENT_END` box whose existing `zgpop` becomes the single release. β inherits the retarget for free via `DRIVE_PAIR_DEF_JMP β,ω` — erasing the two contradictory dead-β conventions (n26 pair-with-adds vs n63 bare-leak). Own-K `flat_leave` stands down via new `op_wsteal` scalar at the ONE `X86H_JMP/OMEGA` arm; wpop zeroed at staging, the ZW-5 spelling. Guards: armed non-UCLAIM, planner `wp>0`, no pending ΣK fold (`op_wpop==0` pre-staging), depth equality `zd_k(node)+wp == END's gpop` (excludes n54-class mid-extent `:F` edges by arithmetic), NODE-EXACT successor equality through goto-chase (excludes full-extent `:F(elsewhere)`), `!scan_live !flat_stmt_frame`. Killswitch `SCRIP_ZD_ENDJMP=0` = byte-identical revert (md5-verified vs committed artifact).

**Edits (3 files, HQ seat; cross-front note — emit.cpp drive loop is OMEGA-adjacent, x86_asm.h is OMEGA-owned, bb_call* ALPHA-untouched):**
- `src/emitter/emit.h` — `op_wsteal` field appended after `op_wterm`.
- `src/emitter/emit.cpp` — `g_zd_wsteal` static declared; cleared at choke with ZD set; staged in the g_zd_stage block; END-JMP STEAL block inserted before the ZW-5 O-2 redirect (retargets `node_ω` to `lbls[END]`, zeroes `g_emit.op_wpop`); ZW-5 steal guards `!_endj_stolen` to prevent double-steal; staging: `g_zd_wpop=(_zw5_wpop_stolen||_endj_stolen)?0:zd_wp[i]; g_zd_wsteal=_endj_stolen`.
- `src/templates/x86_asm.h` — `X86H_JMP/OMEGA flat_leave` arm gains `&& !_.op_wsteal` (own-K suppression; wpop needs no guard — staged zero).

**Commits:** SCRIP `a571c6bc` (fix) + `c4936a91` (feature artifacts); corpus `fe469590` (benchmarks) + `f34d76b6` (crosscheck, −1490 net lines). Demo regen zero changes.

**Gate (318 A/B setarch-R, env-length-controlled):** PASS sets EXACT both modes (m3 282, m4 274); red sets BY SET IDENTICAL; F/T internal moves on 10 programs: 9 crashers (fileinfo, triplet, expr_eval, cross, word1–4, wordcount) FAIL→TIMEOUT both arms (removing accidental-terminator over-free, s26 test_case precedent) + test_case m4 TIMEOUT→FAIL. Zero P→F. func_call witness: n26/n31/n63 fail+β → statement_end, −16 instructions; m3/m4 result 10000000, ms flat.

**WATERMARK (this session):** m3 **282/24/11** · m4 **274/32/10+1L** · PASS sets EXACT · regen ×4 clean · bench **18/21 HOLD** (board not re-run; smoke flat).

**THE RULING (Lon):** the standing directive's second clause — *"with a C-style RBP used occasionally only when absolutely necessary"* — WAS the answer at every prompt. The depth-immune base at every indeterminacy boundary is a C-style RBP frame (`push rbp; mov rbp,rsp`, old_rbp in frame; nested indeterminacy = nested frames), whack = `mov rsp,rbp; pop rbp` — the WHACK CONTRACT's mechanism 2, verbatim. **r9/wire is RETIRED**; the s23i "the REAL fix is r9/wire" cursor prose was inherited-recon rot that outvoted the directive for ~15 sessions across every seat, HQ included. **Corrected model (HQ's own error this session, Lon's correction):** tip-relative operand access is fully deterministic — per-edge fail depths are compile-time constants (the ω-stub ladder is the standing proof) — so NO operator ever reads at unknown depth; the whack is the only depth-aware site, and it either adds a constant (mechanism 1) or pops a frame (mechanism 2). **A decline for indeterminable extent is a ROUTING to mechanism 2, never a terminal verdict** — the veto diagnostics are the frame-placement worklist. **MONITORING (same pass, HEAD `7f92a607`):** A-9 [RECON] landed — ALPHA ladder COMPLETE (m3 295/22 · m4 289/27 BY SET, bench 18/21, regen ×4 zero). OMEGA s35 cursor said "r9/wire is next" — RULING RELAY written into both front files to redirect before that session spends. 131 re-attributed (ALT+FENCE1 vetoes lifted; residual = PATREF `pat_static=0` class → same worklist). Env-pad/placement flakes are locator beacons for unconverted absolute-sensitive legacy spellings — impossible in the target model, always a lead. Earlier this pass: s26b patch confirmed RESOLVED via ALPHA s30 (r0 guard + BEGIN-skip + `zls_is_wiring`); ZW-13 recorded as the first measured ownership violation (s24a `zws` line, four OMEGA rungs vacuous s24a→s32 under trivially-green gates).

## ⭐⭐ HQ LIVE CURSOR — s26b (2026-08-02, Lon-directed, GATE-BLOCKED → REVERTED, patch preserved): IR_STATEMENT_BEGIN / IR_STATEMENT_END

**Directive (Lon)**: "Let's have a IR_STATEMENT_BEGIN and IR_STATEMENT_END. The former (BEGIN) can set up a frame if necessary, and jump to first BB. This label can be useful for performance attribution being each statement spans a range of bytes in the code. The latter (END) can do the pop frame." **Design mapping**: END = the ZW-5 trailer RE-KINDED (γ jmp carries op_zgpop, staging untouched); BEGIN = new head bracket minted by a post-loop shim (anchor[i]→BEGIN→first box — the g_sno_uses_stmtkw hook-pass shape, one edit reaches every statement form), stno stamped in ival, zw5_on() regime gate, chain α lands on BEGIN via the s26 entry chase so the attribution label IS the rt_chain_enter target. This design converges with FINDING-2026-08-02h (STF bracket for the armed-pattern population): BEGIN is the frame home that makes END's fail-side restore depth-free, retiring the deprecated ω stub ladder for good. **Ten edits, all applied and BUILT GREEN**: IR.h pair before IR_OP_COUNT (zero renumbering), scrip_ir.c names, lower re-kind at :1852 + BEGIN shim, walk + drive dispatch cases (BEGIN carries the MONITOR_BIN stno tap), zd_wl_kind admission, zd_k K=0 (THE ONE LINE), zeta_storage res-slot class, :2512 wpop-steal END exclusion. **Patch: `PATCH-s26b-stmt-begin-end.patch` (this repo, 116 lines) — apply with `git apply`, do not re-derive.**

**GATE VERDICT (xc318 A/B vs `fae9001b`, BY SET)**: m3 CLEAN — 282/24/11 verdict-identical. m4 **13 P→F**: {058,061,067,102,107}_pat_fence_*, {118,119,129,130,148,149,150}_pat_arbno*fence*, test_stack — plus one m4 F→P (W02_seq_fail_propagate, a directional hint the claim-home move is right). **058 anatomy (MEASURED)**: the UCLAIM statement claim MIGRATED onto BEGIN exactly per Lon's design — `n4_statement_begin_α: sub rsp, 272` + stmt_claim zero-fill — i.e. "BEGIN sets up a frame if necessary" MATERIALIZED UNPROMPTED because the run planner selects the run head and BEGIN became it. m4 then SEGVs (rc=139) on the fence abort/commit exit where ref says "aborted correctly"; m3 passes the same program. **Suspects, in order**: (1) BEGIN joins the run → every member's index shifts +1 → the index-parallel planner arrays (zd_uk/zd_on/zd_wp, the :2027 head-exhaust arms, :2512 group) may bake per-member depth/exit constants that now free the wrong amount on MID-RUN exits (fence abort is exactly a mid-run exit); (2) walk-vs-drive staging asymmetry (the two-dispatcher trap :1541 documents) around the head claim. **NEXT-SESSION RECIPE**: git apply the patch; MONITOR-FIRST bracket 058 m4-vs-m3 at the abort exit; audit the +1 shift through zd_plan's member arrays and the head-exhaust release; re-gate 318×2 + bench. Tree REVERTED to `fae9001b` (gate-green re-confirmed on 058 m4). The pair itself is RIGHT — the exit accounting under it is the rung.

## ⭐⭐ HQ LIVE CURSOR — s26 (2026-08-02, Lon-directed): LBL-chain de-proc — SCRIP `fae9001b` on parent `542776a5`, corpus `df1c43f3`

**Directive**: "There is no PROC level processing in SNOBOL4. However, the DEFINE will generate some code." Target: the roman.s entry block (`.globl proc_LBL__ROMAN_α` / α / α_body / `n0_goto_α: sub rsp,16; jmp n1` / `n0_goto_β: jmp ω`). **Landed (3 edits)**: (1) `emit.cpp` zd_k — **IR_GOTO joins K=0**; the s24b zd_wl_kind admission comment at :1882 claimed "zd_k already returns 0" and THE ONE-AUTHORITY LINE HAD NEVER BEEN EDITED, so every armed goto carved 16B nothing read, and the LBL entry gate leaked 16B per rt_chain_enter entry. (2) `emit.cpp` codegen_flat_chain_body entry chase — IR_GOTO joins SUCCEED/FAIL as a chased transparent relay, so a chain bound at a label-landing goto binds α at the landing's TARGET and the gate box is never collected. (3) `scrip.c` both proc loops — `.globl` skipped for `LBL__` pseudo-procs (registration is same-TU rip-lea; DEFINE stubs keep theirs). **Gates**: xc318 A/B vs `542776a5` BY SET, **zero P→F both modes**; fixed m3 282P/24F/11T · m4 272P/33F/11T/1L vs parent 280/27/10 · 272/34/10. Movers m3 F→P: `127_pat_json_keyvalue`, `152_pat_json_keyvalue_renamed` (parent m3-FAIL/m4-PASS mode split healed by the skew removal). Lateral: `test_case` FAIL(139)→TIMEOUT both modes — parent's SEGV was the goto leak exhausting the stack acting as an accidental loop terminator; fixed spins honestly (3/7 ref lines then loop; red stays red; promotable to a MONITOR-FIRST wedge). Bench board **18/21 HOLD**, red trio {roman, eval_fixed, eval_dynamic} unchanged; roman m4==m3 mod `ms:`; the observer's owed full 318×2+bench is DISCHARGED by this A/B. Benchmark .s regen committed (−2350 net lines; ZW5-stub removal + this fix).

**Residues for Lon's ruling**: (a) `proc_LBL__ROMAN_α_body:` remains — a zero-reference alias line for this shape; suppressing it for is_lbl means conditionally skipping the define while the jmp-entry res machinery sits between α and α_body in the binary medium — media-divergence risk judged not worth 1 cosmetic line without a ruling. (b) **MEASURED, the real next rung**: the body is EMITTED TWICE — the LBL chain re-emits main's graph suffix with fresh uids (uid = emission-order counter), then main emits everything again; roman carries ~850 duplicate lines, and a CODE-using program pays O(labels × suffix) text (beauty: 129 labels). Proposed shapes: emit main FIRST + an emitted-node memo so LBL sections collapse to a 2-line α→existing-label trampoline, or drop LBL sections entirely and register main-node label aliases (needs stable pre-assigned label names on landing nodes). **Cross-front**: edit (1) touches the ALPHA-owned zd_k line (their ZD-5b LEN edit lands on the same line — trivial one-line rebase, flagged); edit (2) sits in OMEGA-adjacent emit-region glue. HQ seat under Lon's unfreeze; both fronts rebase on `fae9001b`. **Owed**: push (all 3 repos, credential at handoff), feature/demo/crosscheck .s regens ×3.

---

## ⭐⭐⭐ LIVE CURSOR — s23o (2026-08-02) — ZW-4 FULL LANDED

**Directive (Lon):** *"Complete, once and for all, the NON-POPPING FORTH-style RSP ZETA stack with a C-style RBP used occasionally only when absolutely necessary. Continue."* + "All your choices. I'm with you on this. Continue."

**LANDED (SCRIP `7b209188` + `61bacbba` feature-.s; corpus `b3f08a4a`/`d24b2bbb` + crosscheck regen; full text: `FINDING-2026-08-02e-...S23O-ZW4-LANDS...md` — READ IT before touching any x86() cell-operand mnemonic or demoting any runtime data cell):**
1. ⭐⭐ **ZW-4 FULL** — SPD-2 scanhit/scanfail per-medium pair (the named forbidden shape) → single medium-invisible `x86()` chains; `g_anchor` → keywords.c-private `static`, `rt_anchor_g` alias = the ONE exported name, ALL emitted references GOT-indirect (`x86_load_got`, `XK_RIPGOT`); new encoders `x86_reg_disp32_cmp_imm` + `x86_inc_r`; `rbp#` raw-cell escape; loud cmp guard.
2. ⭐⭐⭐ **TWO LAWS MEASURED (FINDING §2/§3):** (a) pinned fr-prefix captures raw-rbp spellings → a guardless mnemonic (cmp) SILENTLY DROPPED both retry guard-cmps, probes stayed green on stale flags, ONLY the .s region diff caught it — probe suites cannot certify emission rewrites; (b) static demotion of a .so data cell with emitted TEXT refs REQUIRES the GOT form — the exported-global era worked only via copy-reloc interposition (the rtx_match.S 0(c) rule, now front-end-reachable).
3. **WATERMARK (s23o):** crosscheck 318 **BY SET IDENTICAL both modes vs parent binary (stash A/B)** — m3 280/27/10 · m4 266/39/10/2L, non-pass sets byte-equal · bench board **18/21 record hold** (roman + eval pair = pre-existing residue) · regen ×4 all insertions==deletions · SNAPSHOT-AT-BEGIN (SPITBOL manual: &ANCHOR read only at match start) deliberately deferred to ZW-1's anchor_snapshot cell — this rung preserved live-read behavior.
4. ⛔ **ZW-4's g_patstk_sp half stays with ZW-1/2** (six live template readers, bb_match_begin ×4 + bb_match_end ×2; rung text's own "die via ZW-1/2 regen"). Observed out-of-scope: core.c `kw_anchor` = a SECOND anchor cell beside keywords.c's — candidate ONE-AUTHORITY sweep.

**NEXT:** **ZW-5 slice 2** (lower mints IR_STATEMENT per statement: body lowers with succ:=γ-side, threaded `cx` fail continuations → the box's ω, DECLINE fail-arrival depth>0; stamp K_total into nd->ival; migrate the last-operator op_zgpop staging to the box; α→body child wire replaces the slice-1 bomb) → slice 3 (ω per-depth stub ladder WITH its planner, s22h atomicity) → **ZW-6** glue-whack relocation → r9/wire → m4-EVAL · ZD-7c.

**s23o-b addendum (same session): ZW-5 SLICE 1 LANDED DORMANT (SCRIP `bed92446`)** — `bb_statement.cpp` (house shape: x86_begin/alpha/bomb'd body-wire/gamma/trampoline) + dispatch case staging `op_zgpop = nd->ival`. ⭐ THE MEASUREMENT THAT SHAPED IT: op_zgpop emission is ALREADY ONE AUTHORITY (the X86H_JMP γ/ω hook arms; all template mentions are comments) — the 5,923 are FIRINGS of that arm on the last operator's port edges, so the debt is PLACEMENT and the box becomes the whack's home BY STAGING, never by a second spelling (s22k law). GATE: 318/318 `--compile` md5 byte-identical vs parent + m3 probe green; census figure STALE-CITED, re-run owed at the lighting slice.

---

## ⭐⭐⭐ PRIOR CURSOR — s23n (2026-08-02) — ZW-0-S2 + ZW-4 PARTIAL (g_anchor ACCESSOR)

**Directive (Lon):** *"Complete, once and for all, the NON-POPPING FORTH-style RSP ZETA stack with a C-style RBP used occasionally only when absolutely necessary. Continue."* + "All your choices. I'm with you on this. Continue."

**LANDED (SCRIP `eb1f574b` ZW-0-s2, `cd7f54c8` ZW-4-partial; both BY SET IDENTICAL m4; regen ×3 zero .s changes both):**
1. ⭐⭐ **ZW-0 STAGE 2** (`eb1f574b`) — all `ZC_FRAME_ISLE`/`x86_isle()` dead arms excised from 9 files (−39 lines). `x86_isle()` deleted; island arms stripped from all `x86_asm.h` inlines + 6 template files. Stage 2 COMPLETE.
2. ⭐ **ZW-4 PARTIAL** (`cd7f54c8`) — `rt_anchor_ptr()` accessor added in `keywords.c`; `bb_match_begin` + `emit.cpp` binary arm use it instead of `extern long g_anchor`. ⛔ **BLOCKER for full static demotion:** SPD-2 TEXT arm in `emit.cpp:2515` uses `g_anchor` as a linker symbol in an inline asm string — static demotion requires either a named export alias or rewriting that TEXT arm as `x86()` calls (the RULES-compliant fix; TEXT arm is a MEDIUM_TEXT-only path = forbidden shape under BOTH-MEDIUM rule). **Full demotion deferred.**
3. **WATERMARK (s23n):** m4 BY SET IDENTICAL to s23l/s23m open bracket both landings. Regen ×3 zero changes both commits.

**NEXT (superseded by s23o above):** ZW-4 full ✅ DELIVERED s23o. (The former PUSH PENDING line here is deleted per RULES rot-rule (a) — `handoff_status.sh` is the only push ground truth.)

---

## ⭐⭐⭐ PRIOR CURSOR — s23k (2026-08-02) — WHACK CONTRACT RULED · MATCH_BEGIN/MATCH_END RENAME · MARKER MACHINERY IS CARGO-FREE · LADDER ZW OPENED

**Directive (Lon):** PIVOT from the eval bracket into ζ-cell design. *"Scan all the generated code and report violations"* → the four-principle census; then the WHACK CONTRACT; then *"lock in the design… Just complete the work."*

**LANDED (full text: `FINDING-2026-08-02d-...S23K-THE-MARKER-MACHINERY-CARRIES-NO-CARGO...md` — READ IT BEFORE ANY ZW RUNG):**
1. ⭐⭐⭐ **WHACK CONTRACT** ruled + recorded in THE MODEL below (`.github 28f8ccac`): two mechanisms, four sites, GLUE NEVER WHACKS, BB_END_STATEMENT is the missing box, operator rule.
2. ⭐⭐⭐ **Census (338-program compiler sweep):** stmt heads 2,267 ok / **223 claim-at-head** (K≤496) · **5,923 operator over-frees** (assign 2,000, call 1,660…) · in-BB whacks 982 · glue whacks 1,264 (main_γ/ω 676, PAT$N exits 302) · fence1 whacks exist, FENCE0 rides the SNO$PB0 blob.
3. ⭐⭐ **RENAME LANDED** (SCRIP `51ba262b`): IR_MATCH_BEGIN / IR_MATCH_END, bb_match_begin/end.cpp, 35 files. Neutral: 100_pat exact both modes; roman BY SET {cc208bbc,e9af39a8} both arms (bistable pre-existing).
4. ⭐⭐⭐ **Marker machinery carries NO cargo:** patstk = 1,112 mark-only emitted sites, zero pushers ever; the 0x70000000 slab holds only nesting markers; captures are per-slot gen-gated stacklets (NOT a central CAS). r12 = zero uses corpus-wide.
5. ⭐⭐⭐ **MATCH-STATE DESIGN OF RECORD LOCKED** (FINDING §7): r12=CAS TOP · r13/14/15=Σ/δ/Δ · rbp=match frame · **cas_base = frame slot, no fifth pin** · **CAS LAW: push at γ, pop on backward traversal** · MATCH_END pops the frame AS the whack · deletions: g_patstk_* entire, g_cap_gen+stacklets, g_anchor demoted, ZC_FRAME 17 stale arms deleted.
6. ⭐ ZW-0 stage 1 landed (`b8ee3d6c`). ZW-5 slice 0 dormant (`45e9a1b1`). IR_STATEMENT design of record per s23k addendum.
- **WATERMARK (s23k close):** benchmark board **18/21 EXACT HOLD**; every code landing gated 338/338 `.s` byte-identity or BY-SET rename-neutrality. Full crosscheck-318 deliberately not re-run — zero behavioral change; owed at ZW-12 ✅ **DELIVERED s23l**.



**Directive (Lon):** *"Get benchmarks working using NON-POPPING FORTH-style RSP ZETA stack with a C-style RBP used occasionally only when absolutely necessary. Continue."* + "All your choices."

**LANDED (SCRIP `0fdf7932`; full text: `FINDING-2026-08-02c-...S23J-REPL-PIN...md`):**
1. ⭐⭐⭐ **REPL-PIN** — replacement statements (fence-denied subjc, PATREF-vetoed zres) were the UNPINNED deep-arrival population: rbp-flavored FRQ slots against the ambient C frame + raw `op_sa` spelling the deleted carve while the producer wrote through zvo. `rpin() = deep && hpin && (subjc || zres || !jmp_entry)`, ONE authority ×4 sites; pinned legacy subject read respells `RDQ("rsp", hoff(op_sa))` (hoffb falsified — resolved into outer_Σ). `bb_match_replace:33` gains release:78's `!op_stmt_pin` twin gate (measured: correct output then SEGV without).
2. ⭐⭐ **Benchmarks 16→18/21**: string_pattern + mixed_workload fixed, M3==M4 all 21 verdicts. Bisect law: the broken construct was STORED-pattern replacement exactly; inline+replace and stored+match-only were both green.
3. ⭐⭐ **jmp-entry containment**: roman (proc_LBL__ROMAN, LP jmp=1) crashed at 3 iters under unconditioned widening — runtime-transfer entry depth invalidates hoff's compile-time spelling by construction. jmp-entry keeps pre-session regime verbatim; roman back to known baseline-red DIFF. The named fix remains the r9/wire claim base.
4. ⭐ **WATERMARK:** m3 **282/25/10** (+127_pat_json_keyvalue) · m4 **266/39/10/2L EXACT** — zero P→F BY SET both modes, proven by parent-binary A/B (stash/rebuild), not remembered counts. 127/152 = ONE placement-flicker pair (env-pad reconfirmed), the s23i cap-slot class, not a regression. Regen ×5 (corpus `bd5be761`/`49350480`/`e6950c05`/`675240d9` + `919eb347`): the ×4 scripts MISS `programs/` — Lon caught it; `util_regen_programs` covers icon/prolog/rebus only (its 664-file churn = pre-existing entry-glue staleness trued up, call/ret→jmp, NOT this session's delta), and `programs/snobol4/` needed a direct sweep (18 regened, 2 differed incl. very-stale json.s). ⚠ RESIDUE: f13_eval_code.s (no clean .s — the eval family) + 6 include-driven demo artifacts (s23f graceful-skip class) still assert an older compiler.

**NEXT:** ⭐ eval_fixed/eval_dynamic bracket (deferred-eval family — the last two benchmark reds with roman) · r9/wire claim-base rung (retires roman + 127/152 + capture-bearing declines) · ZD-7c USER-PROC ARM (spec'd s23i, unspent) · ON-4 pileup (⛔ GATED) · ⛔ PENDING LON: the ~21 column-1 files · push awaits credential.

---

## ⭐⭐⭐ PRIOR CURSOR — s23i (2026-08-02) — STATIC-SHAPE DEFER/PATREF ARMS · THE CAP-SLOT CRASH IS STACK PLACEMENT

**Directive (Lon):** complete the NON-POPPING FORTH-style RSP ZETA stack, C-style RBP only when absolutely necessary; *"All your choices. I'm with you on this. Continue."*

**LANDED (SCRIP; full text: `FINDING-2026-08-02b-...STATIC-SHAPE-ARMING...md`):**
1. ⭐⭐⭐ **`pat_static`** (new IR_t field) = lower's TRANSITIVE DEFER-FREE proof over `g_sno_seal`, stamped at the DEFER-of-VAR + PATREF sites; zd_plan's dynamic-box scan lets a static-shape DEFER/PATREF stop vetoing the quartet. Spine-vs-argument VAR distinction is load-bearing (LEN(N)'s N is a value read). FENCE1-in-statement still declines. `SCRIP_ZD_DYNARM` mask: =0 ≡ s23h regime byte-identical (proven vs committed artifacts); bits force-arm for A/B.
2. ⭐⭐ **Armed population 17/122** (fence-via-var 108–113, non-recursive star-vars, calc/regex/json-literal, 117); recursive 135/136 + statement-FENCE1 142 byte-verbatim declined.
3. ⭐⭐⭐ **CAP-SLOT BRACKET (core.3397, 127):** armed capture-in-blob died at `rt_cap_push(slot=rsp+176)` — the raw claim spelling is ENTRY-REGIME-DEPENDENT (blob compiled once, armed statements enter at shifted depth; slot lands on stale residue). Flip variable = ABSOLUTE STACK PLACEMENT: `SCRIP_NO_SEGV_HANDLER` is READ BY NOTHING — it merely shifts initial rsp by strlen; any dummy env flips 127 to 3/3 pass. Names 126/131/145/180/181's baseline reds as the same defect elsewhere. Narrowing = capture-bearing targets decline (25→17); the REAL fix is the r9/wire-carried claim base (CARRIED-OPEN), which also retires raw blob `[rsp+K]` spellings.
4. ⭐ **WATERMARK:** m3 281/26/10 · m4 266/39/10/2L — m4 EXACT BY SET incl. LERR pair {test_string, 1017_arg_local}; m3 +1 = the LAWS-named 213 flake (absent from non-pass set); armed-17 zero attributable P→F. Regen ×4: only crosscheck churned, exactly the 17, net −69 lines; emit-fail 15 / as-fail 2 held.

**NEXT:** ⭐ ZD-7c USER-PROC ARM (SPEC BELOW in LADDER ZD — sized, site-anchored, ~20min) · r9/wire claim-base rung (re-admits capture-bearing targets; retires raw blob spellings) · ON-4 pileup (⛔ GATED) · ⛔ PENDING LON: the ~21 column-1 files.

---

## ⭐⭐⭐ PRIOR CURSOR — s23h (2026-08-02) — ZD-5 MATCH-SPINE ARMS · CLAIM-AT-HEAD · DEFAULT FLIPPED ON

**Directive (Lon):** complete the NON-POPPING FORTH-style RSP zeta stack for the match quartet — *"a var just needs a little space"*, subject read must not pop — then the s22y grant, twice: *"All your choices. I'm with you on this. Continue."*

**LANDED (SCRIP, default `SCRIP_ZD_MATCH` now ON; `=0` = byte-identical declined escape hatch):**
1. ⭐⭐⭐ **CLAIM-AT-HEAD v2** — `zuk` staged on the MATCH_HEAD member: the claim carves at the head's α (the match owns its scanner storage), pre-head producer cells ride ABOVE it, rsp at head-α IS the claim base at zero instruction cost — the blob's raw shift-fragile claim spellings (ON-5/ARGREAD escapes, gdb-bracketed as a wild `rt_cap_push` slot in 156) hold by construction. Pure non-popping; supersedes the same-session HEAD-FOLD. **The var carves ONLY its 16** — the complaint verbatim (strip probe: `n3_var ALLOC 16`, `n4_match_head ALLOC 240`).
2. ⭐⭐ **The coordinate laws, each with a witness:** pin arm = pure rebase (`zvo_resolve_base`/`zvo_owner_dout`; recovered 46/50) · blob dout delta ZERO (174 BAL counter corruption) · mirror gated `!subjc()` (054 clobber) · subject read = `op_uclaim + op_zread[0]` general form (061 read a coerce cell as the subject under a `+0` hardcode) · exit pops position-gated at hpos · span shrink excludes armed value members' dead extents (subjkeep exception).
3. ⭐⭐ **REPLACE seats measured:** op_sa = SUBJECT, replacement BY ADDRESS (armed r9 = lea of rv's cell). The inversion was invisible without the .s diff.
4. ⭐ **Dynamic-box decline** mirrors s22y (DEFER/PATREF/FENCE1 → declined regime verbatim). PATREF measured both ways: 117/142 arm GREEN (**the named next rung**), 135/136 crash → stays declined, degrade never die.
5. ⭐ **WATERMARK:** full 318 identical BY SET both modes (m3 280/27/10 · m4 266/39/10/2C == s23g record) · pattern-131 identical by set · zero P→F any arm. Regen ×4 auto-committed (corpus `e814a248`/`126b3c7f` + SCRIP feature) — artifacts assert HEAD with the armed default.
6. **FLAKE LEDGER +{135,136,164,165,183}:** identical-bytes ASLR/stdout-flush flicker, proven (same OFF binary, same path, P then rc=139; 165 armed ≡ OFF bytes, both die AFTER flushing correct output). Sweep law: BY SET + re-roll singleton flips.

**HONEST RESIDUE:** roman is baseline-RED at HEAD (never a valid vehicle; `/tmp/strip.sno` is the demonstration, green ×4) · 061_capture_in_arbno red→red both regimes (baseline POS(N) overrun loop, out of scope) · PATREF/roman class = next rung via the 117/142 green.

**NEXT:** ⭐ PATREF arming rung (static-shape stored patterns; bracket the recursive re-entry class 135/136 first) · ON-4 pileup (⛔ GATED, unchanged) · ⛔ PENDING LON: the ~21 column-1 files · push awaits credential (11 prior dotgithub commits + this session).

---

## ⭐⭐⭐ PRIOR CURSOR — s23g (2026-08-01/02) — CARVE CALCULATION DELETED + THE ARTIFACTS WERE ASSERTING A COMPILER THAT WASN'T HEAD

**Directive (Lon):** house-clean the doc pile; *"Ensure the code which was calculating whole-graph ZETA frames versus per-BB ZETA cells has been deleted as previously directed. If not, stop and DELETE it now"*; then *"All your choices. I'm with you on this. Continue."*

**LANDED:**
1. **Housekeeping prune** — 202 FINDING + 18 HANDOFF (≤2026-07-28) deleted from `.github` (`f505c6c`); 106+2 kept (07-29..08-01, the live-cursor working set). Full text stays in git at the parent.
2. ⭐⭐ **CARVE-JANITORIAL (SCRIP `39a2e63`)** — the whole-graph CALCULATION was still RUNNING every compile behind the dead prologue: `fc_leaf_walk` (lower) + twin `fct_leaf_range` (zeta_storage, ARBNO finalize) filled the `fcl` table whose reader had ZERO callers. Deleted: both walks + 4 call sites, `fcl` table + registrar/reader/highwater/header decl, caller-less `zd_stub_ok`, the two arithmetically-dead `+op_flat_disp` terms in `x86_frame_off`, the `op_flat_disp` field + reset. Every target proven dead by grep pre-cut (sole writer = the `=0` reset; returns discarded at all 3 fct sites). `fct_fp_range` (consumed returns → patzeta) untouched. Build green -O0 both targets.
3. ⭐⭐⭐ **ARTIFACT-TRUTH RESTORATION (regen ×4: corpus `7f35073`/`f8fd261`/`d530d85` + SCRIP feature)** — regen churned ~518 files, insertions==deletions, immediates only: dtype tags 1→2 / 6→3. **NOT this session's delta.** Parent `7ba8734` built clean emits 2/3 IDENTICALLY (janitorial exonerated by parent-diff), `descr.h` at HEAD says DT_S=0x02/DT_I=0x03 (TAG-3 `03cecd8`, re-applied s234 by the concurrent RTX session) — **and s23f's own committed artifacts carry tag 1**: that regen ran a pre-TAG-3 working tree. The s217/s235 skew class, now corrected: every `.s` in both repos is honest current output again.
4. ⭐ **ON-0 WATERMARK REPROVEN (owed since s23d) — the first bracket with TAG-3 live + true artifacts:** crosscheck 318, TIMEOUT=8 → **m3 280/27/10 · m4 266/39/10/2L**. m4 EXACT vs s23d incl. LERR pair {test_string, 1017_arg_local}; m3 = record ± the documented timeout/pass split (213 flake on its pass side). Raw verdict-diverge 19 (stricter metric than the curated 4; contains test_stack/164/1016; 170 passes both). TAG-3 costs zero corpus-wide.

**RULED (this session, under "all your choices"):** `flat_frame_bytes` is NOT the carve anymore — 48B wire header + the s22j-restored zero-cell region term, consumed by live wire-park/record protocol. Its removal = the STMT_FRAME/GEN_RESUMABLE re-land design rung (s22n §5), deferred there deliberately.

**⭐ LESSON:** an artifact regen proves the compiler THAT RAN IT, not HEAD — regen-after-fresh-clone is the only artifact truth (this is RULES prose-rot rule (a) wearing a `.s` extension). Also: `xc.sh` needs an ABSOLUTE binary path (it cd's to a workdir; `./scrip` = 127 = universal phantom CERR).

5. ⭐ **ON-3 CLOSED (SCRIP, this session):** the two statement-terminal `old_rbp` restores (x86_asm.h γ/ω jmp hooks, `HKN(0)`) + `x86_zls2_mark_save`'s three port-arm stores AND the release twin's read locked to new `HKN(5)="zls2_mark"` — save/read cannot drift, per the s23e one-authority law. ⛔ **`[rbp+368]` VOIDED:** absent from the tree AND from emitted output — cursor prose that outlived the code (RULES rot-class (a) wearing an offset). PROOF: `test_gate_argnote_sweep.sh` GREEN · notes col-89, zero on `j*`, zero stray `#@` · M3==M4 on probe · regen ×4 = 138 artifacts changed, insertions==deletions, **0/138 code-different after comment+trailing-ws strip** · 121 artifacts now carry `zls2_mark` (the corpus exercises all three arms). ⚠ INSTRUMENT: a naive `sed 's/#.*//'` strip-proof reports 138/138 false-different — the note's column padding leaves trailing whitespace; normalize `[[:space:]]*$` too.

**NEXT:** ON-4 pileup HAS its fresh bracket (the one genuinely open ON rung) · ⛔ PENDING LON: the ~21 column-1 files · push of 11 local commits awaits credential.

---

## ⛔⭐⭐ THE MODEL

**THERE IS NO GRAPH FRAME.** Every BB: **allocates at α** (`sub rsp,K`, *its own* K) · **reads/writes only its own cell** · **releases at γ/ω** · **jumps**. No pre-allocation, no whole-graph carve, no prefix-summed prologue.

⭐ **THE ONE REFINEMENT (law 4):** value spine rides RSP FORTH-style; housekeeping that must survive an unwind (ARBNO/FENCE1/CALL) rides a depth-immune RBP. `flat_stmt_frame` default is OFF (`SCRIP_STMT_FRAME=1` = opt-in); `op_zgpop` is the SOLE statement-terminal release authority.

### ⛔⭐⭐ THE WHACK CONTRACT (Lon ruling s23k, 2026-08-02) — supersedes ALL prior whack-placement prose, including the s22v glue-exit ledger's whack clauses

1. **WHACK-FREE has exactly TWO mechanisms:** (1) **DETERMINABLE** (extent known at compile time): ONE `add rsp, K_total` after the γ exit at FINAL SUCCESS — the whole extent freed at once. (2) **INDETERMINABLE** (runtime-variable extents — ARBNO/DEFER class): open an EMPTY RBP/RSP frame at the indeterminacy boundary; whack = `mov rsp, rbp` + `pop rbp`.
2. **WHACK SITES are exactly:** end of STATEMENT · end of PATTERN MATCH (`S ? P`) · FENCE0/FENCE1 commit points. Nowhere else.
3. **THE GLUE DOES NOT WHACK.** Glue is one-shot JUMP-IN/JUMP-BACK or pass-through — nothing more. Measured debt at ruling time (s23k compiler sweep, 338 programs): 1,264 glue whacks — `main_γ/ω` 676 · `proc_PAT$N_scanfail/ω` 302 · proc chain exits ~22 — ALL misplaced, to relocate into release BBs.
4. **BB_END_STATEMENT IS A MISSING FIRST-CLASS BB** — the statement-scope twin of BB_MATCH_RELEASE, the SOLE statement whack authority (`op_zgpop`'s emission home). Today the whack is FUSED INTO THE LAST OPERATOR BB (assign, call, …) — WRONG. That fusion is the 5,923-site edge-over-free census (s23k audit: assign 2,000 · call 1,660 · match_head 262 · binop 257 · cmp_test 240 · assign_var 206 · subscript 168 · …).
5. **OPERATOR RULE:** a binary/unary/nullary operator BB frees ONLY its own result, ONLY at ω — NEVER its operands. Consumers read; the whack releases. (Measured head-of-family violation: `bb_match_head` α pops its subject cell `add rsp,16` before pinning stmt_base.)
**NAMING (s23k):** IR_MATCH_HEAD → IR_MATCH_BEGIN, IR_MATCH_RELEASE → IR_MATCH_END (SCRIP rename landed; historical text below keeps old names).
6. **BB α-alloc range:** a BB's own α claim is ~16–64B (one result descriptor + a couple of locals). A statement head carrying the whole statement claim (`n1_var_α: sub rsp, 240`-class; s23k census: 223 of 2,490 statement heads, K up to 496) is INVALID under this contract — it is UCLAIM legacy debt, drained by the ZD ladder.

**THE WHOLE-GRAPH CARVE IS A CORPSE.** `flat_frame_bytes` is debt; so are ~1054 `FR`/`FRQ`/`FRQB` reader sites across ~109 templates. **The job is to delete their customers until there are none, then delete the carve.**

### ✅ CARVE-ERAD — CLOSED s23g (overtaken by Lon's s22n/s165 rulings; the staged manifest above is history)

Emission authority deleted s22n + s165 revert-of-re-land · displacement fill deleted s23a (`op_flat_disp` ≡ 0) · calculation + all janitorial residue deleted s23g (`39a2e63`: both leaf walks, `fcl` table, dead `+0` terms, the field). Readers resolve through `zvo_resolve`/UCLAIM statement claims. **SOLE SURVIVOR:** `flat_frame_bytes` = the 48B wire header + s22j zero-cell region term (live wire-park/record protocol, NOT the carve) — its removal is the STMT_FRAME/GEN_RESUMABLE re-land design rung, s22n §5.

### ⛔ THE FAILURE MODES
- Treating the frame as infrastructure. It is a corpse.
- Clamping the carve while readers still address into it. Tautological — the reds name unconverted boxes.
- Misreading law 4's RBP constructs as licensing a graph frame.

### ✅ THE ONLY DISCRIMINATING TEST
Convert one box's readers to its own cell; watch the carve requirement DROP. Progress = monotone decrease of the declined-statement census.

---

## HISTORY INDEX (one-liners; full text = FINDING docs + git)

- **s22m** (08-01) CLAWS5 + JSON oracle-match. Treebank root cause bracketed: H11 Pop_list rsp rose +104 (mod16=8), SIGSEGV glibc movaps. gdb available (`apt-get update && apt-get install -y gdb`).
- **s22l** (07-31) NOFC symmetric, +33 programs (ALL pat_*), m3 276/41 → 308/9. `SCRIP_NOFC` still off by default. ZD-SR (IR_SAVE_RESTORE roles 1/2/3 admitted, transparent). Attribution correction: the 33-program win is the CARVE SUPPRESSION, not the non-popping consumer read. Instrument law: run under `setarch -R`; ASLR is ±2 noise on every m4 figure.
- **s22k** (07-31) K authority collapsed to one site (was three). ZD-9 define-stub admission (`g_flat_frame_floor > 0` discriminator). Watermark m3 276/41 · m4 276/40 · DIV=3.
- **s22j** (07-31) ALT pair-defs were beta entries — every alternation segvd. `X86H_DEF_PAIR` new site code; `op_pair_rejoin` flag. m3 232/85 → 241/76, ZERO regressions.
- **s22i** (07-31) ZD-7 Slice 2 (IR_CALL builtin family). IR_CALL decline census 519→58. SIZE('hello')→5 ✅.
- **s22h** (07-31) ZD-7 Slice 2 engineering: PROC_STAGED exclusion mandatory (measured); planner changes require template arm atomically; `lea rsi` encoder gap identified.
- **s22g** (07-31) ZD-7 Slice 1 engineering: TAG-SAFE callee accessor; full callee partition; IR_CALL runs are not single-node; naive ZD arm −63 m3 (FRQ adds depth, wrong address).
- **s22f** (07-31) NON-POPPING RUNG OPENED. Five pops are Gen-1 FC, not STF consumers. Gate = ZD-7 (IR_CALL). FC census 163 firings / 29 programs; NOFC=1 breaks 20 (call-bearing statements). STF arming widen is the WRONG gate.
- **s22e** (07-31) LP-2 landed (RPO walk + zd_plan above xa_dispatch). `flat_all_zd` exact. Instrument trap: committed `.s` artifacts for claws5/json are ASSEMBLER-REJECTED at HEAD and will not regen until codegen defect fixed.
- **s22d** (07-31) LP-1 landed (BFS pre-prologue verdict). arithmetic.sno carve 248→8. Zero crosscheck programs fire.
- **s22b** (07-31) STF-UNFLIP (`flat_stmt_frame` default ON→OFF, SCRIP_STMT_FRAME=1 opt-in) + WPOP-1 (`!op_zres` guard at binop/unop sites). Crosscheck EXACT both ends, fail sets IDENTICAL BY SET both modes. **The fail edge was over-freeing by 32; the carve was absorbing it.** Carve deletion will EXPOSE every over-free it currently swallows.
- **s22a** (07-31) RPO-FILL v2 (post-order + per-root reversal; preorder trap: wholesale reversal loses `entry`) + ZGPOP-STF (zeroed at planner choke, not emission site). STF-armed 31/318. Consumer pops NOT deleted (serve the ~287 unarmed graphs). `add rsp,ΣK` FORBIDDEN — the seed's own annotation: "ZERO hand-counted pops."
- **s21x-z** (07-31) Four findings, zero commits. STF-FLIP is ceremony (HKQ never fires, 0/317). ZD-5a-PRE vacuous (cannot reach match-bearing graphs). Consumer pops violate port discipline. `.s` scramble is BFS fill.
- **s21x-y** (07-31) Value spine fully closed. ZD-2m IR_FIELD_VAR (last value-spine blocker). STF-FLIP (flat_stmt_frame OFF→ON). Watermark m3 232/85 · m4 229/86/2 · DIV=1 — held EXACT through s22b, s22c, s22r, s22u, s22v. Census 100% protocol: CALL 519 · MATCH_HEAD 247 · SAVE_RESTORE 18 · GOTO_DEFERRED 6.
- **s21x-x through s21x-v** (07-31) ZD-2 verdict widening complete (all value-spine kinds). ZD-1 landed (RSP FORTH per-BB stack, default-ON). ZD-2h retired (SNOBOL4 has no lexical locals). Carve debt re-derived live: 1054 sites / 109 templates, UNMOVED — ZD arms are additive, legacy arm survives beside each.
- **s21x-r** (07-30) STF defect was process-scope flag (ZLEAK-1/2). Armed set (31) and m4 regression set (41) DISJOINT. Declined-graph sweep 285→0: ALL-OR-NOTHING per graph now holds corpus-wide. Law: NO PROCESS-SCOPE FLAG MAY DRIVE A GRAPH-SCOPE REGIME.
- **s21x-q through s21x-e** (07-29/30) ζ-cell spelling sweep closed. ZTOS-1/2 sliding offsets. GLUE-3/4 wired. ZREL-1/2. LEN-GHOST fix. CALL2BB slices 1/2/3 landed. GOTO-ERAD survey. ZD whitelist widening beginning.
- **s186** (07-27) SN4-RTX split to its own file. Shrink-pass lesson: 8 live rungs deleted by prior prune, recovered from `950e6a9f`.

---

## ⛔ LON DIRECTIVE — s21x-c (2026-07-29): DESIGN OF RECORD

1. Every BB allocates its own storage: ONE `sub rsp,K`.
2. Sliding offsets, RSP-indexed; emitter tracks live depth at compile time.
3. RSP-only until a genuine brick wall, then RBP dance.
4. **Four RBP constructs: STATEMENT · FUNCTION · ARBNO · FENCE1.** Law 7: DEFINE's FUNCTION = IR_CALL's frame dance only.
5. Named anti-pattern (roman): `sub rsp,1344` whole-graph carve. WRONG.
6. DEFINE, constant-folded, emits exactly TWO BBs: IR_SAVE_RESTORE + IR_CALL.
7. **SCOPE LAW: statement level ONLY. No function-level processing.**

**DYNAMIC BOX GLUE (s21x-f):** any BB graph (one entrance, four ports) invokable by a DYNAMIC BOX. (A) DYNAMIC-FLAT: α `jmp [entry_cell]`, β `jmp [resume_record]`, γ/ω = supplied wires; zero frame. (B) DYNAMIC-FRAMED: + RBP/RSP dance. First customer: IR_MATCH_PATREF.

---

## ⛔ LAWS & TRAPS (binding; DO NOT RETRY marked experiments)

- **ζ GATE IS "ZERO MID-BODY CELL", NOT "ZERO RSP":** residual raw-rsp sites are classified NOT-ζ. Four legitimate classes: GLUE · C-ABI ALIGN · CSTACK SWAP ARM · PROLOGUE.
- **NO PROCESS-SCOPE FLAG MAY DRIVE A GRAPH-SCOPE REGIME:** `static int on = getenv(...)` inside a function taking `IR_graph_t*` is the defect signature. Cost 41 m4 programs.
- **DECLINED-GRAPH SWEEP before any default-flip:** every `live=0` graph must be byte-identical between regimes. Non-vacuous: check armed graphs still differ.
- **CENSUS UNITS:** always state the env with an armed count.
- **SUSPENDED-CELL (s21x-l):** no rsp cell may suspend across γ above an ARBNO/DEFER extent.
- **RESULT-IS-THE-CELL (s21x-k):** consumer overwrites the source cell IN PLACE, net-zero.
- **SOLE-CONSUMER FENCE (s21x-j):** subject registration requires IR_MATCH_HEAD be subjval's ONLY operand consumer.
- **UNION-TAG (s21x-g):** IR_t sval/ival/dval are ONE union — normalize at single dispatch point; never include IR_SAVE_RESTORE in op_sval promotion whitelist.
- **NODE-EXACT HANDOFF (s21x-g):** emission order is not a contract; key by CALL NODE POINTER.
- **STUB DISCRIMINATOR (s21x-h):** DEFINE-stub key = `g_flat_frame_floor > 0`.
- **DEFER-DEEP LOAD-BEARING (s197):** do NOT drop IR_MATCH_DEFER from deep-arrival until recursive-defer programs pass.
- **s206 DO-NOT-RETRY:** `x86_fc_cells()=(FORTH||HEAP)` predicate flip → wild jumps.
- **SCAN-RETRY = 5th rbp member (s196):** `&ANCHOR` is a runtime keyword; no static classifier retires the pin.
- **STALE-BINARY TRAP (s21x-j):** `[ -x scrip ]` is not a build check. Grep both make logs for `error:`.
- **op_flat_disp RIDES EMISSION ORDER** — any layout change must prove per-chain disp locality first.
- **CENSUS SHELF LIFE:** re-run, never cite. HEAD-STAMP every measurement.
- **COMPARE m4, NEVER m3:** `test_string`/`213_gc_exhaustion_churn` are harness-only flakes on m3. Diff fail sets BY SET, never by count.
- **RBPPAIR DO-NOT-RETRY:** mirrors the α guard at γ/ω, proven present, breaks `1016_eval`. The second pin authority is `rt_chain_enter` (CLASS C graphs).

---

## ⛔ PENDING LON RULINGS
- ✅ **FOUR-modes — RESOLVED s23k (Lon):** FRAME_R12 island RETIRED ("R12 all the way now for COND ASSIGN"); ZW-0 stage 1 landed. FRAME_RSP archaeology's fate rides Z4-9's own ladder. (Was: ⛔ **NOW FORCED by the s23k r12-CAS collision (LADDER ZW-0): FRAME_R12 and r12-as-CAS-top cannot both hold r12.** Options: (A) retire FRAME_R12 (+FRAME_RSP archaeology) per Z4-9's own plan — CELL_STACK is the stated ultimate goal, and your s5 ruling already returns r12 to the capture/CAS role; ZW-0/1/2 unblock. (B) keep four configs — CAS top must then stay cell-resident (`[RT_CAS_TOP]`, the s5 arrangement) under island selection, r12-CAS only under CELL_STACK: config-dependent register roles, both maintained. Recommendation on record: (A).
- **Replacement-splice ruling (s21x-j):** splice reads the cell, or write-through — retires sole-consumer fence for replacement class.
- **SRC-ORDER-LAYOUT ruling A/B/C.**
- **RBP-SHED-7:** ⛔ blocked.

---

## LADDERS

### ⭐⭐ LADDER OBJ-NOTE — one-term object names in the GOTO column (mechanism landed s23b, SCRIP `eb0c08a8`; Lon directive 2026-08-01)

**HOW TO USE THE SYSTEM (read before any step):**
- **The idiom:** prefix the instruction's `x86(...)` call with `x86("note", <name>) + ` inside the same `+` chain. The note renders `# <name>` at the GOTO column (col 89) on the NEXT instruction line. Jump lines (`j*`) silently DROP it — Lon: never comment a jump, the GOTO column is theirs. BINARY medium = empty string, so mode-3 bytes are untouched BY CONSTRUCTION — no mode-identity risk from any note you add.
- **Name sources:** `gva_name(k)` — GVA slot → variable name (gva_collect.c registry, extern"C"'d in x86_asm.h beside ABSQ) · `bb_kind_name(op)` — IR op → lowercase kind, the same spelling the `n<uid>_<kind>` labels use (exported from emit.cpp) · string literals for housekeeping terms (`"old_rbp"`, `"cas_top"`, …; bb_match_head's 11 are the reference vocabulary).
- **Mechanics (do NOT re-derive):** the note is an in-band `#@name` marker line folded by `x86_4col`; stateless across the templates' unspecified-evaluation-order `+` chains (it travels in the string, never a global); idempotent under the sink's second 4col pass; markers unmatched at chunk end re-emit so the sink completes cross-call folds. Implementation lives ONLY in x86_asm.h (`"note"` arm in `x86_core_` + the fold in `x86_4col`).
- **Verify recipe per step:** `scrip --compile probe.sno` → notes at col 89, ZERO on `j*` lines, `grep -c '^#@'` == 0 stray markers; assemble+link (`gcc -no-pie X.s -LSCRIP/out -lscrip_rt -Wl,-rpath,…/SCRIP/out`), run, diff vs `--run` output (**M4 == M3**); then the four regen scripts (`util_regen_{benchmark,feature,demo,crosscheck}_s_artifacts.sh "<step>"`) — equal insert/delete counts = pure in-line annotation; emit-fail must hold at 15 and as-fail at the 2L pair unless the watermark itself moved.

**STEPS:**
- [x] **ON-0 WATERMARK REPROVE — DONE s23d: `m3 279/27/11 · m4 266/39/10/2L`.** m4 EXACT vs carried s23a; LERR = the named 2L pair; the lone m3 delta is `213_gc_exhaustion_churn`, the LAWS-named harness-only m3 flake. BY SET, never by count. ⭐ This is a FRESH bracket — ON-5 should land against it.
- [x] **ON-1 operand-kind plumbing — LANDED s23e (SCRIP `45e44f0f`). THE RULING WAS DISCHARGED, NOT GRANTED:** the PEERS RULE governs BB_t/IR_t, NOT `sm_emit_t` (26 precedents + the s141 append-at-end law), and zd_plan's loop already held the producer node. `op_zkind[6]` staged in lockstep with `op_zread[]`, cleared to −1 at the per-node reset (a stale kind prints a WRONG name — worse than none). `ZOPN(k)` is a STRICT SUPERSET of ZOPAN via a `k==0` fallback, because op_zkind stages only on the ZD-armed arm and a bare swap would have silently dropped operand-a names on unarmed nodes. ~~(⛔ STILL needs Lon ruling — the s23c `ZOPAN()` interim covers operand-a ONLY and does NOT discharge this step — shared params struct): add `op_zkind[]` beside `op_zread[]` in the emit params, populated where `op_zread` is staged with each operand producer's IR op; templates then speak `x86("note", bb_kind_name(_.op_zkind[k])) +` before each `ZOPQ(k,·)` read. Interim without the ruling: operand-a only via existing `_.op_a_node_kind`.~~
- [x] **ON-2 operand-read sweep — CLOSED s23e:** 25 ZOPAN sites retired onto ZOPN(0) + 11 new operand-b..n notes across 12 templates; `ZOPAN` grep == 0. Both operands of a binop now name their producers. (Was: OPERAND-A DONE s23c (`afbcab9b`, 25 sites/12 templates via `ZOPAN()`); operands b..n await ON-1.** scripted insertion (the s23b pattern — python regex per file, see `eb0c08a8`'s 34-site GVA pass) across the `ZOPQ(`/operand-FRQ consumer sites; verify recipe per batch.
- [~] **ON-3 housekeeping-term sweep — BATCH 1 LANDED s23c (`816b1cf6`); ARGUMENT-LOAD FAMILY CLOSED s23d (`154a3fa8`)**: the SELF-CELL class is done via `ZRESN()` (41 sites/15 templates) + the CLAIM-ZERO pass named `stmt_claim`. ⭐ THE LESSON: `op_node_kind` at emit.cpp:861 is a CHOKE POINT — one accessor named every box's own result cell tree-wide, no per-template plumbing. Look for the choke point before batching by family. ⭐ ARG-NOTE (s23d) closed the **189 `call rt_*` argument loads** via a TEMPORAL choke point — `x86_argnote` walks BACKWARD from each `call` in the 4col pass, where `bb_emit_x86`'s whole-body handoff has already made loads and callee visible together; roles GENERATED from real prototypes, RTX asm ports read from their own non-C-ABI banner contract. ⭐ **s23e CLOSED THE RESTORE SIDE:** the saves were annotated and every RESTORE was bare (4 sites/3 files/5 slots) — `HKN(k)` in x86_asm.h is now the ONE naming authority so a term cannot drift from its twin, and the unanchored-retry loop reads `start_δ`/`patstk_mark`/`rsp_mark` (vocabulary anchored to SPITBOL manual pp.66–68). ⛔ `bb_rev_swap` reuses `op_off+48/56` for a DIFFERENT object and got its own `scan_δ/scan_Δ` — SAME OFFSET ≠ SAME OBJECT. REMAINING: the two statement-terminal `rbp` restores in `x86_asm.h` (~2023/2030, `op_stmt_pin` — they fire on EVERY statement cut), `x86_zls2_mark_save`'s `FRQ(off)` stores, `[rbp+368]` in match_sequence. Census after s23e: `[rsp]` 294 · `[rip]` 155 · `[rbp]` 26. bb_match_head stays the reference embodiment.
- [~] **ON-4 srccomment echo repair — DEDUP LANDED s23e (SCRIP `31300b3a`); PILEUP CURE IS GATED, ORDERING IS A DIFFERENT LADDER.** ⭐⭐⭐ **THE FINDING: `bb_src_of` IS NOT A COMMENT FACILITY.** `zd_plan` roots STATEMENT SEGMENTATION on it ("runs are rooted at bb_src_of statement heads"), so WHICH node carries a source note decides where a statement run BEGINS — and thus claims, offsets, depth. **MEASURED: the one-line pileup cure (`&& !bb_src_of(t->γ.node)` on the chase) moves EMITTED CODE in 9/21 benchmarks + 5/122 pattern crosschecks.** It therefore belongs to the ZD/segmentation ladder WITH a full ON-0 bracket, NOT to an annotation rung. In-place comment at `lower_snobol4.c`'s chase loop carries the measurement so it is not re-derived or landed unbracketed.
  - **LANDED (inert):** `bb_src_note` is idempotent — exact-SEGMENT dedup (not strstr, so `TEST(1,100)` is not swallowed by a longer echo). Changes the TEXT a node holds, never WHICH node holds one → segmentation-neutral BY CONSTRUCTION. roman adjacent dups 3→2, n129 pileup 5→4 lines. 163 programs code-identical with ALL comments stripped.
  - **OPEN — the pileup:** convergent GOTO chains bundle several statements onto one node (roman stacks 5 above n129, 4 attributed to the WRONG head). Needs the watermark bracket.
  - **OPEN — the ordering:** ⛔ NOT attemptable here at all. The `.s` lays chains out BFS, so reordering echoes means reordering CODE = **SRC-ORDER-LAYOUT, awaiting Lon's A/B/C ruling.**
- [x] **ON-5 — LANDED s23d (`efc11e5f`); census 6/12 runs collapsed → 0, watermark unmoved BY SET, regen ×4 done. Original s23c analysis below.** ⛔ The s23b framing ("find the two producers, delete one") is FALSIFIED: there is ONE producer, it fires ONCE per statement head, and the defect is a **misresolution**, not a duplicate. Census per claimed statement = **30 stores / 26 distinct**: 4 cells written twice AND **4 cells (top 32 BYTES of the claim) NEVER written**. Cause: `RDQ("rsp",_zi)` spells plain `[rsp+N]`, re-resolved by `x86_frame_off`→`zvo_resolve` — the ARGREAD hazard already documented at x86_asm.h:874. CLAIM-ZERO thus only partially discharges the `rt_cap_push` zero-fresh contract it was landed for. Fix = the `[rsp#]` raw escape, one line. **Changes emitted code → land it WITH the ON-0 watermark bracket.** Full write-up + gate list: `FINDING-2026-08-01-CLAUDE-SN4-ON5-IS-NOT-DUPLICATE-ZEROING-...md`.

### ⭐⭐⭐ LADDER ZW — THE WHACK CONTRACT IMPLEMENTATION (opened s23k; design of record = FINDING-2026-08-02d §7; gates every rung: full crosscheck BY SET both modes · benchmark board · regen ×4 · monitor on any diverge)

**⭐ EXECUTION PLAYBOOK: `DESIGN-SN4-ZW-ZD-OPUS-PLAYBOOK.md` (s23p) — per-rung steps/gates/traps for ZW + ZD + SHED, re-measured against HEAD (grep anchors, live census commands, staleness ledger §8). Executing sessions read it AFTER this ladder, before coding.**

- [~] **ZW-0** — **STAGE 1 LANDED s23k (`b8ee3d6c`; ruling resolved by Lon: island retired, r12=CAS).** Selector choke cut ×3, 338/338 `.s` byte-identical, CLI loud rc=2. **STAGE 2 REMAINS:** delete the 17 now-dead routed arms (16 files, `x86_zc_frame\|rt_zc_frame_live` census) + `ZC_FRAME_ISLE` + the stale :288 guard; several sit inside suspend/resume protocols — whole-arm excision with the byte-identity sweep gate.
- [ ] **ZW-1 MATCH_BEGIN CANONICAL FRAME** — `push rbp; mov rbp,rsp; sub rsp,K≤64`; own cell = {outer_Σ/δ/Δ, cas_base, anchor_snapshot, start_δ}; subject read IN PLACE (no pop — fixes the ZD-armed pop); dual marks DELETED; old_rbp slot ceremony DELETED; retire the emit.cpp:2509/2521 per-medium retry-blob pair into `x86()` encoders (named forbidden shape).
- [ ] **ZW-2 MATCH_END = FRAME-POP WHACK** — γ: apply-walk cas_base→r12, r12←cas_base, restore Σ/δ/Δ, `mov rsp,rbp; pop rbp`; ω: same minus walk. rsp_mark/patstk_mark/marker-scan DELETED.
- [ ] **ZW-3 R12 CAS LIVE = the R12-FREE-1 REVERSAL** (resized s23k on the dcap correction, FINDING §6.1): the slab already IS the CAS — `rt_dcap_e` records γ-pushed by bb_match_capture, pumped by bb_match_end. Do: reverse s5's 6 emitted sites + 2 m4 wrapper seeds + `rt_outer_call` thunk (r12 = live top, callee-saved coherence, cell = lazy-init seed only) · `rtx_match.S` r12-direct · fail-discard `r12←cas_base` (needs ZW-1/2 frame) · THEN cap_gen deletion; ⛔ stacklets (pattern_match.c:1313 iteration-reuse axis) AUDIT-first, separate.
- [~] **ZW-4 GLOBAL DELETIONS** — ✅ g_anchor half DONE s23o (static + rt_anchor_g GOT alias, SCRIP `7b209188`); SNAPSHOT-AT-BEGIN semantics move to ZW-1's anchor_snapshot cell. ⛔ g_patstk_sp + island + lazy-init arms (C + rtx_match.S) + the 1,112 emitted marks REMAIN WITH ZW-1/2 (six live template readers, FINDING s23o §4).
- [~] **ZW-5 IR_STATEMENT** — slice 0 (kind+K=0, `45e9a1b1`) + slice 1 (template+dispatch, dormant, `bed92446`, s23o) LANDED; REMAINING = slice 2 lower mint + staging migration, slice 3 ω ladder+planner. Original design text: the ENTIRE-statement bracket box per the s23k addendum design (α bare label · γ one-whack `add rsp,K_total` · ω per-depth stub ladder · `s<stno>_` labels · K=0 in `zd_k` emit.cpp:1908 · lower builds it first, body lowers with succ:=γ-side, threaded `cx` fail continuations := the matching ω stubs; fence-run shared targets lower:1444 route naturally). Retires the 5,923 fused pops.
- [ ] **ZW-6 FENCE + GLUE RELOCATION** — FENCE0 (SNO$PB0 blob element) commit-whack probe + wiring; FENCE1 whack canonicalized; glue whacks relocated (main_γ/ω 676 → terminal END_STATEMENT; PAT$N shared exits 302 → match machinery).

### ⭐⭐ LADDER ZD

**CENSUS (s21x-y, re-run after every rung): 790 declined, first-blocker ranked — `IR_CALL` 519 · `IR_MATCH_HEAD` 247 · `IR_SAVE_RESTORE` 18 · `IR_GOTO_DEFERRED` 6. 100% PROTOCOL — value spine has no remaining members.** ⚠ Clearing a cheap blocker PROMOTES the expensive one behind it; a decline count is a frontier reading, NEVER a backlog.

- ✅ **ZD-2 COMPLETE** — all value-spine kinds ride the cells (LIT · VAR/ASSIGN-global · UNOP · BINOP · COERCE · CMP_TEST · KEYWORD_SNOBOL4 · SUBSCRIPT · DEREF · ASSIGN_VAR · FIELD_VAR). Declines 1060→790.
- [ ] **ZD-2c** `bb_binop_relop` — zero first-blockers today; arm when a widened statement declines on it. (`IR_FIELD_GET`, `BINOP_XREP`: vacuous by construction — Icon/Raku-only, zero SNOBOL4 customers.)
- [ ] **ZD-2g** UNOP closure (NULL/NONNULL/NULLTEST_VAR) — never first-blocks today.
- [ ] **ZD-3** Legacy arm retirement — per kind fully covered by ZD arm, delete vfc/vfcu/vfcb/vfcc + the `op_fc_disp` registration.
- [ ] **ZD-4** Lift the jmp-entry decline — `SCRIP_ZD_JMPENTRY=1` hatch; diff 1019's fragment .s on/off; fix; delete gate.
- [ ] **ZD-5 MATCH FAMILY (247) — the 85/86-red target.**
  - [ ] **5a-PRE** Ledger the STFH-48: `bb_match_head:32` emits `IF(stfh(), x86_zclaim(48))` but `zw_carve_k` returns 0 for IR_MATCH_HEAD → second unledgered allocation authority. Enumerate non-HKQ `[rsp+off]` refs first.
  - [ ] **5a** Linear-match bridgehead (head → LEN/POS/RPOS/SPAN/ANY/NOTANY/REM/TAB/RTAB → release; no alt/arbno/fence/defer/capture).
  - [ ] **5b** Planner extension for branching runs (alt, arbno cycles, defer). ⛔ The ONE genuinely design-tier item.
  - [ ] **5c** Per-template conversions, smallest-first.
- [ ] **ZD-7** `IR_CALL` (519) + `IR_SAVE_RESTORE` (18) — the protocol rung, law 4's other genuine RBP citizen.
- [ ] **ZD-7c USER-PROC ARM — SPEC'D s23i, sized ~20min, DO NOT RE-DERIVE.** The `rt_proc_is_registered` exclusion in zd_wl_kind (emit.cpp ~1884) exists because `bb_call_proc_staged.cpp` lacks ZD spellings; the staging authority ALREADY EXISTS (`zd_nops(IR_CALL)=n_operands` stages `op_zread[k]` per arg — its own comment says so). Three spelling families, all conditional on `_.op_zres`, sibling idiom = bb_deref.cpp:13-22 verbatim (ZRES/ZOPQ + notes): (1) FOUR result-write pairs `rax:rdx → FRQ(off)/FRQ(off+8)` at :392/:485/:552/:562 → `ZRES(0)/ZRES(8)`; (2) per-arg stage reads `FRQ(slot)/FRQ(slot+8)` at :58 (slow) + :64-65 (GC-fast inline) → `ZOPQ(k,0)/ZOPQ(k,8)`; (3) the PL-REGAIN-4 FUSED-OPEN cell-address leas (~:196+, "leas each arg's CALLER-FRAME CELL ADDRESS into rsi rdx rcx r8") → lea of the arg's ZD cell. Then flip the zd_wl_kind exclusion to admit (killswitch `SCRIP_ZD_PROC=0` per ZD-SR precedent). ⚠ TRAPS recorded in advance: role-0 SR stays declined (CALL2BB-only, unmeasured); the naive-admission falsification (085/086/087 blank via FRQ(resoff)+op_zdepth) is the CONTROL — those three MUST flip green; dyn-scope (SNOBOL4) vs det (Icon/Raku) both route here, watermark both. Verify ladder: 085/086/087 + func_call bench + full 318 BY SET + regen ×4.
- [ ] **ZD-6** Standalone: 130/131 clean-HEAD segv · DIV member W04_arbno_basic · bb_op_name entries for ops 14/73–77.

### GOTO-ERAD
- [ ] GE-0 census; GE-1 monitor-tap relocation (prerequisite); GE-2 survivor unprotection; GE-3 SNOBOL4 lower-side; GE-4..7 per-language; GE-8 emitter sweep; GE-9 enum deletion + gate.

### RBP-SHED (order 3→1→2→4→5)
- [ ] SHED-3 REC-PIN-OWN: move stale-emission globals to per-graph g_emit mirror at emit_chain choke.
- [ ] SHED-1 NPARAMS: retire `g_flat_outer_nparams>=1` pin conjunct for depth-static graphs.
- [ ] SHED-2 ABORT-REBALANCE: route ABORT through statement fail exit.
- [ ] SHED-4 HOOK-ENCODE: scanhit/scanfail hooks through x86().
- [ ] SHED-5 ALIGN-DANCE-DELETE: retire transient push-rbp alignment window.

### ✅ FB-STMT RE-ARM — CLOSED s22c (DEFAULT-ON, SCRIP `bdd6c23b`). Ceremony unchanged · data refs −44% · IDENTICAL BY SET both modes. Residue: pat/gen blob class excluded by construction at emit.cpp:2650 — extension shares surface with ZD-5.

### SRC-ORDER-LAYOUT (s21x-b): statement layout order scrambled (BFS fill). Awaiting ruling A/B/C. Gates: watermark, census, .s regen ×5.

### CARRIED OPEN: MARKER-CAPTURE · r9 park-address anchor · arm-quad OVERLAY · fc_cond FIRST-WINS · SYM-VIS-M3 JIT map · Icon generator-scan FORTH cells.

---

## ↗ MOVED OUT / SUPERSEDED
- **SN4-RTX** → `GOAL-SNOBOL4-RTX.md`. RTX-11/12 NOT concurrency-safe.
- **ZHEAP / CELL ladder** — superseded by s21x-c design of record. ZC_PORT_HEAP rbx α-carve stays dormant-ratified (HZ-1).

---

## ⛔⭐ WATERMARK OF RECORD (s22y close)

| runner | m3 | m4 | DIVERGE |
|---|---|---|---|
| **crosscheck 318, TIMEOUT=8** | **233/84/1** | **229/88/1** | **4 {test_stack, 164, 170, 1016}** |

Harness: `/tmp/xc.sh` (lean resumable 2-arm runner from .github, bare container exec). Prior record s22x: 220/96/1 · 217/98/1 · DIV=3 — REPROVEN at s22y open before any edit (fail/timeout split shifts with container speed; pass sets and diverge set exact); s22y +13/+12 (SUBJECT-CELL default-on; 164 joins DIVERGE as m3-fixed over a pre-existing m4 fail).
