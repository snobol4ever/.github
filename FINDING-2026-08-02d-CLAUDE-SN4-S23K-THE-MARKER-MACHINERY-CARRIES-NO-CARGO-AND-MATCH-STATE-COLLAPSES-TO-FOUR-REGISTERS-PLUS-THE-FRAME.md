# FINDING s23k (2026-08-02) — THE MARKER MACHINERY CARRIES NO CARGO, AND THE ENTIRE MATCH STATE COLLAPSES TO FOUR REGISTERS PLUS THE FRAME MATCH_BEGIN ALREADY BUILDS

**Rung:** SNOBOL4-BB (`GOAL-SNOBOL4-BB.md`). **Session shape:** opened as the eval_fixed/eval_dynamic benchmark bracket, PIVOTED (Lon) into a ζ-cell/whack design session. **Result:** WHACK CONTRACT ruled + recorded (`.github 28f8ccac`) · MATCH_HEAD/MATCH_RELEASE → MATCH_BEGIN/MATCH_END rename LANDED (SCRIP `51ba262b`) · full four-principle violation census measured (338-program compiler sweep) · marker machinery proven cargo-free · MATCH-STATE + CAS design of record LOCKED (this doc §7) · LADDER ZW opened. **No behavioral code change this session** beyond the mechanical rename (neutrality proven).

**Directives (Lon, verbatim anchors):** *"PIVOT! …Scan all the generated code and report violations of these 4 principals"* · *"The GLUE does not do a WHACK-FREE"* · *"rename MATCH_HEAD to be MATCH_BEGIN… MATCH_RELEASE to be [M]ATCH_END"* · *"Do WHATEVER it takes to encapsulate the ENTIRE match state into REGISTERS"* · *"is the MARKER idea REALLY necessary… it seems that MATCH_END just POPS the entire FRAME as the whack"* · *"conditional assignment SIMPLIFIES to a PUSH going forward via GAMMA and a POP on back track via OMEGA"* · *"(1) yes frame slot not pinned register, however R10 might do nicely. (2) your choice (3) your choice… lock in the design and be verbose… Just complete the work."*

---

## 1. PART A — THE EVAL BRACKET (pre-pivot; findings stand, rung re-queued behind ZW)

1. **Benchmark watermark REPROVEN at session open, exact s23j hold:** 18/21 OK · eval_fixed CRASH · eval_dynamic 30s-timeout→SEGV · roman FAIL (the r9/wire-gated baseline red). Runner `test_bench_snobol4_modes.sh`, mode-4.
2. **Both eval benchmarks are pure `EVAL(string)`** (manual case 3, p.130-131: compile string as *expression*, evaluate with current values, fail on syntax error → `&ERRTEXT`).
3. **S234 §6 both pre-existing defects CONFIRMED at HEAD `0fdf7932`:** (a) deferred-ARITH `EVAL(*(X + 1))` SEGVs m3 (matrix probe: EVAL(int) ✓, EVAL(numstr) ✓, EVAL(*(X+1)) SEGV); (b) `1016_eval` m3 **PASS 3/3**, m4 **silent-empty rc=0** — the m4-EVAL blocker is alive and is the benchmark red's likely root.
4. **m4 EVAL is structurally possible:** `libscrip_rt.so` carries the whole pipeline — `parse_expr_pat_from_str`, `lower_snobol4`, `emit_chain`, `eval_string_transient` all `T` symbols. The blocker is not a missing stage; it is unlocated (superseded by the pivot before bracketing).
5. String-EVAL probes showed shape-dependent empty/SEGV in m3 under ASLR; under `setarch -R` both probe shapes went stable (ev1: `result: ` empty ×3; evm2: empty-stdout rc=0 ×3). Recorded, not chased.
6. **EVAL implementation map** (for the future rung): `runtime_eval.c` — parse `"(s)"` → synthesize `ZZEVALZZ = expr` stmt → lower → `emit_chain` → `rt_chain_enter` → `NV_GET(ZZEVALZZ)`; cache by string; thunks for PAT$N minted mid-eval (BLOCKER-C s144 comment).

## 2. PART B — THE FOUR-PRINCIPLE VIOLATION CENSUS (compiler sweep, 338 programs = crosscheck+benchmarks, 290k lines, m4 text; 1 emit-fail)

**Method:** swept the COMPILER at HEAD (never artifacts, per RULES); statement grouping via the `#====` separators; port labels are literal Greek (`n<uid>_<kind>_α/β/γ/ω`).

- **P1 (own α alloc, ~16–64B):** statement heads 2,490: **2,267 compliant (91%) · 223 violating (9%)** — first BB carries the whole `# stmt_claim` (K to 496; `n56_lit_integer_α: sub rsp,496` heading `OUTPUT = fib(6)`, eyeballed). By head kind: var 157 · lit_string 42 · lit_integer 24 — Lon's `n1_var_α: sub rsp,240` verbatim. Family heads: match_begin K=208–272, match_arbno 80, call 96. Mid-body subs 1,146 (call 678 ≈ C-ABI marshal).
- **P2/P5 (free only own, only at ω):** self-only edge frees 876 ✓. **Over-freeing edges 5,923 ✗** — assign 2,000 · call 1,660 · match_begin 262 · binop 257 · cmp_test 240 · assign_var 206 · subscript 168 (hello.s: assign allocates 0, frees operand's 16 at cut). Mid adds ~1,458 + ~320 marshal pops.
- **P3 (whack placement):** in-BB whacks 982; glue whacks 1,264 = `main_γ/ω` 676 · `proc_PAT$N_scanfail/ω` 302 · proc-chain ~22. Under the WHACK CONTRACT (glue never whacks) BOTH populations are misplaced except release-class boxes: match_end 278 ✓-by-role, fence1_as/af 46 ✓-by-role.
- **P4 (FENCE):** fence1 whacks exist (placement to canonicalize). FENCE0 lowers via `SNO$PB0` blob primitive — commit-release probe owed.
- **Regime asymmetry:** claim-regime match_begin reads the subject cell in place (no pop); ZD-armed regime POPS it (`add rsp,16`) — the armed spelling is the violator.

## 3. PART C — THE WHACK CONTRACT (ruled + landed, `.github 28f8ccac`; full text in GOAL-SNOBOL4-BB.md §THE MODEL)

Two mechanisms (determinable `add rsp,K` after γ at FINAL SUCCESS; indeterminable = empty RBP frame, `mov rsp,rbp; pop rbp`) · four sites (statement end, match end, FENCE0/FENCE1 commits) · **THE GLUE DOES NOT WHACK** · **BB_END_STATEMENT is a missing first-class BB** (statement twin of MATCH_END; `op_zgpop`'s home; the 5,923 fused pops are its absence) · operator BBs never free operands.

## 4. PART D — THE RENAME (SCRIP `51ba262b`)

`IR_MATCH_HEAD→IR_MATCH_BEGIN`, `IR_MATCH_RELEASE→IR_MATCH_END`, templates `bb_match_begin.cpp`/`bb_match_end.cpp`, 35 files + Makefile, kind strings (labels now `n*_match_begin_*`). **Neutrality:** 100_pat_fence m3+m4 md5 EXACT; roman BY SET `{cc208bbc,e9af39a8}` both arms under `setarch -R` (roman is genuinely bistable run-to-run pre-rename — pre-arm measured `{cc208bbc,e9af39a8}` too; the flake-ledger law applied, not a regression). ⚠ INSTRUMENT: per-repo `git config` identity is not inherited — the first SCRIP commit failed on unknown author; configure BOTH repos at session start.

## 5. PART E — REGISTER FORENSICS (the STOP-AND-TELL Lon asked for)

- **r12 carries NOTHING:** zero occurrences across all 338 emitted programs; ARCH row says FREE since ZR-RSPRBP-1 (s205, Lon's own directive, SCRIP `da8c2347`). The r12-CAS model Lon stated was the pre-s205 design.
- **cas_top lives at absolute `0x70000000`** = `RT_PIN_BASE` (pin_va.h; s75 relocation note: above brk-reach, below disp32 ceiling); `rt_match_enter` (RTX asm) inlines the lazy-init test against it.
- **g_cap_gen is mint-paired:** `rtx_match.S:35-48` — `rt_match_enter` mints `g_cap_gen = ++g_cap_gen_next` per match; MATCH_BEGIN's α saves the OUTER id for nesting. Its consumers are the per-slot stacklet validity tests (§6), nothing else.
- **g_anchor** = keywords.c:16, the SOLE &ANCHOR storage (not a mirror); read by the β retry loop via an emitter-inline blob.
- **r11** = RTX's busiest scratch (26 uses rtx_match.S alone) and SysV caller-saved; **r10** likewise caller-saved AND the reserved idiv-divisor scratch. Neither can pin cheaply.
- ⭐ **DISCOVERED DEBT:** the retry loop at `emit.cpp:2509` (text printf) + `:2521` (`ef_b2` binary twin) is the NAMED FORBIDDEN SHAPE (hand-written per-medium pair) from GOAL-TEMPLATE-REVAMP-RULES. Dies in the ZW rewrite; recorded so it cannot be copied meanwhile.

## 6. PART F — THE HEADLINE MEASUREMENTS

1. ⭐⭐⭐ **THE MARKER MACHINERY CARRIES NO CARGO.** g_patstk: all **1,112** emitted references corpus-wide are the mark/restore shape (`lea rcx,[rip+g_patstk_sp]`); `pattern_match.c` contains **zero** sp-arithmetic pushers; the island (lazy-init :616-627) has never held a record. The `0x70000000` slab holds ONLY the 24-byte nesting markers `{type=0, cas_rsp_mark, cas_patstk}`. Two whole structures exist solely to mark and scan themselves. Lon's frame observation ("MATCH_END just POPS the entire FRAME as the whack") eliminates both.
2. ⭐⭐⭐ **THERE IS NO CENTRAL CONDITIONAL-ASSIGNMENT STACK TODAY.** Captures are per-slot mini-stacklets `rt_cap_stk_t{sp,gen,buf}` living inside each capture's ζ slot (`pattern_match.c:755-780`), validity-gated by `s->gen != g_cap_gen` lazy reset (the `_Static_assert` at :748 pins `.gen` at +8 for the RTX twin). The R12-CAS reinstatement is therefore a capture-subsystem REWRITE, not a pointer relocation — and it deletes g_cap_gen/_next, the stacklets, AND the marker slab in one stroke.
3. ⭐⭐ **MATCH_BEGIN vs Lon's 4-item model (roman `n2` audit, 31 instructions):** items (1)(2)(3)(4) all present. Extras JUSTIFIED: E1 cap_gen save (nesting id, §5) · E2 `rt_match_enter` (SUBJECT DELIVERY — manual-required string coercion + Σ/Δ registration in rdx:rax). CONDEMNED: G1 saves spelled into STATEMENT-claim slots (223-class debt) · G2 **dual mark recording** (rsp/patstk marks written into BOTH the CAS marker and the head cell — s23e one-authority violation) · G3 `old_rbp` self-save `mov [rbp+280],rbp` (degenerate ceremony under claim-at-head) · G4 memory cas_top load-modify-store ×2 per marker. Honest post-cleanup head need: 3 saves + cas_base + anchor + start_δ ≈ **48–64B — inside the ≤64 range**.
4. ⭐⭐ **THE ZC_FRAME LANDMINE** (`zeta_choices.h:288` #error, pre-existing, flagged "Lon's call"): ZR-RSPRBP-1 deleted the R12 *label* but left **17 arms** written for r12-as-ζ-FRAME (a DIFFERENT role) silently repointed at RBP; s202 measured RBP arm broken (ok=6/crash=14 vs RSP 15/5). Reinstating r12-as-CAS must ride the guard's option 2 so the dead role cannot half-resurrect under the live one. **RULED THIS SESSION (delegated, exercised): DELETE the 17 arms, RETIRE ZC_FRAME; FLATDISP-8 per-graph rsp/rbp selection is the whole ζ-basis story.**

## 7. PART G — DESIGN OF RECORD (LOCKED, Lon 2026-08-02)

**REGISTERS — the complete match state:** `r12` = CAS TOP (reinstated; slab allocation unchanged) · `r13/r14/r15` = Σ/δ/Δ · `rbp` = the MATCH frame (canonical `push rbp; mov rbp,rsp`). **CAS BASE = frame slot `[rbp-K]`, NOT a register** — base is COLD (BEGIN writes, END reads; nothing else touches it). R10 considered per Lon ("might do nicely") and set aside: SysV caller-saved + reserved RTX idiv scratch ⇒ every C `rt_*` call in match scope would need bracketing; revisit only inside pure-RTX phase-2 regions. **NO FIFTH PIN NEEDED.**

**THE CAS LAW (Lon, verbatim rule):** conditional assignment = **PUSH at γ going forward, POP on the backward traversal.** Seam resolution (derived, determinate): a capture wrapper's β fires ONLY after its own γ pushed ⇒ **pop at β re-entry** (then forward the retry into the subpattern); a fresh subpattern γ re-pushes; ω is reached only record-clean. Net invariant = at most one live record per capture instance, removed by any backward traversal — Lon's rule with the pop instruction homed at β. **Choice points need NO r12 snapshots** — element-wise γ-push/backward-pop keeps r12 exact along every path. Record: `{target-kind, target, value.lo, value.hi}` (32B, layout final at ZW-3). MATCH_END-γ applies base→top then whacks; MATCH_END-ω restores r12←base (bulk discard) then whacks.

**MATCH_BEGIN α (target):** `push rbp; mov rbp,rsp; sub rsp,K(≤64)` · save r13/r14/r15 · `mov [rbp-32], r12` (cas_base) · anchor SNAPSHOT (ruled: read &ANCHOR once at BEGIN into the frame — "examined at match initiation"; a `*FN()` mutating &ANCHOR mid-match does not steer the in-flight scan, documented behavior) · `start_δ=0` · subject delivery: READ the producer's cell IN PLACE (no pop), `rt_match_enter` → r13/r15, r14←0. **MATCH_END:** γ = apply-walk `[rbp-32]`→r12, `mov r12,[rbp-32]`, restore r13/14/15, `mov rsp,rbp; pop rbp`, jmp continuation — **the pop of the frame IS the whack, all member/producer cells between frame and rsp freed at once**; ω = identical minus the apply-walk, jmp fail wire.

**DELETIONS (all measured safe or made safe by the above):** `g_patstk_sp` + island + lazy-init + both mark slots + the scan (cargo-free, §6.1) · `g_cap_gen`/`g_cap_gen_next` + per-slot stacklets + `rt_cap_push/pop/top` family (replaced by the r12 CAS, §6.2) · `g_anchor` DEMOTED to keywords.c-private static (the &ANCHOR feature keeps its storage; the match architecture stops referencing it — snapshot at BEGIN) · the `0x70000000` marker records (slab becomes the r12 CAS arena; `RT_PIN_BASE` seed = r12 init) · `old_rbp` slot ceremony · the dual marks.

## 8. PART H — LADDER ZW (the road to finishing the FORTH-style stack; gates: full crosscheck BY SET both modes + benchmarks board + regen ×4 + monitor on any diverge)

- **ZW-0** ZC_FRAME retirement: delete the 17 stale arms + guard; FLATDISP-8 stands alone. (Prerequisite — clears r12's old role before the new one lands.)
- **ZW-1** MATCH_BEGIN canonical frame: `push rbp` spelling, own ≤64B cell, subject read WITHOUT pop, dual-marks deleted, anchor snapshot; retire the emit.cpp:2509/2521 forbidden-shape retry blob into x86() encoders.
- **ZW-2** MATCH_END = frame-pop whack (γ walk + ω discard); rsp_mark/patstk_mark/scan deleted.
- **ZW-3** R12 CAS live: pin r12, slab-as-arena, capture templates γ-push/β-pop, END apply-walk (RTX leaf `rt_cas_apply` or inline); DELETE cap_gen/stacklets.
- **ZW-4** Global deletions land: g_patstk_* (island, lazy-init, 1,112 emitted marks die via ZW-1/2 regen), g_anchor demotion.
- **ZW-5** BB_END_STATEMENT: new IR kind + lower insertion + template; method-1/2 whacks; retires the 5,923 fused pops with the ZD ladder's 223 UCLAIM heads.
- **ZW-6** FENCE0/FENCE1 commit whacks at the ruled sites; glue-whack relocation (1,264: main_γ/ω 676 → terminal END_STATEMENT; PAT$N exits 302 → match machinery).

## 9. INSTRUMENT NOTES
- Sweep the COMPILER, never artifacts (practiced; the `#====` statement separators make statement-grouping free).
- roman is bistable run-to-run even under `setarch -R` (env-length sensitivity, s23i class) — every roman comparison must be BY SET, N≥3/arm.
- Per-repo git identity is not global here — configure in EVERY repo touched, at session start.
- `find corpus/crosscheck -name` before trusting a program name from memory (105_pat_simple_match does not exist; 100_pat_fence_two_alts_first does).
