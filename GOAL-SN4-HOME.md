# GOAL-SN4-HOME — SNOBOL4 ALL THE WAY HOME (master orchestrator)

**⛔⭐⭐⭐ CHARTER (Lon in-chat 2026-08-12 s30, verbatim in substance):** *"This is the final stretch. Make RUNGS and STEPS to take SNOBOL4 all the way HOME, i.e. 100% working with RSP stack relative and RBP stack relative and RBX GC heap-top relative. Use multiple Opus sessions concurrently. Rearrange EVERYTHING."*

**THE EMISSION KEY (Lon, same session, verbatim in substance):** *"A BB will EITHER access its operand's RESULT and its own LOCALS via RBP, OR via RSP."* Per-BB binary, decided at plan time by `frame_need_of` (EARN-1), emitted only by `x86_alpha`/`x86_omega` (s29 ruling: RBP is never glue work). The reading-edge sharpening keeps ALT/CAT on the RSP side even with `*P` operands.

This file is the MAP. Seats execute their own seat file (below); cursors live in seat files. All prior laws bind (RULES.md · MONITOR-FIRST · TEMPLATE-ONLY · BOTH-MEDIUM · LIVE CURSOR discipline · one clone per seat · `git config --local`, never global).

## ⛔⭐⭐⭐ EXECUTION MODEL — FIRE-AND-FORGET (s32; RULES 2026-08-10 applied to this plan: no windows, no waiting, no human scheduling. Supersedes every "solo" / "‖" / "SERIAL, one seat at a time" reading below.)

**LON'S ENTIRE JOB: keep FIVE sessions alive, ONE PER SEAT FILE, re-fired with the same line whenever one ends. Nothing else — no who/what/when decisions. The files route the work.**

| fire with (verbatim) | file the session owns |
|---|---|
| `here we go — RBP seat, GOAL-RBP-EARN.md` | `GOAL-RBP-EARN.md` |
| `here we go — BOARD seat, GOAL-SN4-HOME-BOARD.md` | `GOAL-SN4-HOME-BOARD.md` |
| `here we go — LOWER seat, GOAL-SN4-HOME-LOWER.md` | `GOAL-SN4-HOME-LOWER.md` |
| `here we go — WIRES seat, GOAL-SN4-HOME-WIRES.md` | `GOAL-SN4-HOME-WIRES.md` |
| `here we go — RBX seat, GOAL-SN4-HOME-RBX.md` | `GOAL-SN4-HOME-RBX.md` |

**THE ONE INVARIANT (the only scheduling rule in the plan): ONE LIVE SESSION PER SEAT FILE.** Two sessions in one file is the s38b race. Everything else is git.

**SELF-GATING PROTOCOL — every session, at orientation and before every rung:**
1. `git pull --rebase` every repo; read YOUR file's LIVE CURSOR and any `UNBLOCKS:` lines pushed since.
2. Walk YOUR rungs top-down. A rung carrying a ⛔ REQUIRES line: evaluate its predicate against the repo (one command, stated on the rung). TRUE ⇒ run it. FALSE ⇒ **skip DOWN — never wait, never park** (RULES). If the missing prerequisite is UNCLAIMED anywhere, doing it yourself IS your next rung — first push wins, the duplicate seat pulls and consumes (the s38b concurrent-repair pattern).
3. Own ladder exhausted, or every remaining rung predicate-false ⇒ **pull the top unclaimed POOL item** (below); claim it with a cursor line in the same push.
4. Every handoff cursor ends with **`UNBLOCKS: <seat> <rung>`** naming what your landing opened.
5. **Floors & controls — THE STALENESS LAW (s32b):** every published number is hash-stamped and STALE the moment another seat pushes — that is normal, not a defect, because **GATES RE-MEASURE; FILES RECORD.** Your per-rung A/B control is ALWAYS your own open-state, measured at your own HEAD and re-proved after every rebase — never a number transcribed from BOARD's file. BOARD's floors are the RATCHET: at close, re-RUN the instrument at your HEAD and hold ≥ floor **BY SET, never by count** (sets compose under concurrency — a program another seat broke appears in your set-diff with your diff clean of it; FINDING + bisect assigns the owner). The EARN-2 census works identically: `unearned==0 && owed==0` is evaluated by RUNNING the script at your HEAD; its committed output expires on the first frame-moving landing by its own rule. ⛔ Never quote an m4 number without the 30-second liveness check — **and the check is "at least one probe PASSES", NEVER "returns non-empty"** (BOARD s33 / FINDING-2026-08-12c: the non-empty form passed continuously through a two-day total m4 outage, because 159 failing probes each print a non-empty `got =[]` line; a dead mode is not a quiet one). Run `MODE=compile bash corpus/probe/bb/run_suite.sh X12` — X12 and `zleak_matchbegin_stfh` are the only m4 survivors at the s33 hash, so a green there is the cheapest true liveness signal. Dark ⇒ m3-only, say so — and B-0/B-0b are fair game to claim.

## THE POOL (unclaimed work for any seat whose ladder is exhausted or blocked; disjoint surfaces by construction; claim = cursor line, first push wins)
1. **DEFER-LATCH** — `g_star_peek` → per-site resolution (`pattern_match.c` only; witnesses `140`/`141`, RED m3 rc=139 / PASS m4 — two-sided for free). Authority: GOAL-SNOBOL4-RTX row + s31 ledger.
2. **LADDER KW** — GOAL-SNOBOL4-BB KW-0..6 (acceptance = xc318 keywords-12 green both modes).
3. **CLIMB C-10 / C-11** — GOAL-SN4-ZETA-CLIMB (C-11 doubles as the EARN reentrancy stress suite).
4. **LADDER AB** — GOAL-SNOBOL4-BB AB-3..6. ⛔ REQUIRES (predicate): EARN-11 sole-writer landed AND EARN-7's completion greps green in the tree you arm.
5. **BOARD B-8 / B-7(iv)** — RTX instrument debts · witness promotions · BREAKX mint (if BOARD's session is deep in B-0..B-4).

## REGISTER CONTRACT OF RECORD (the HOME state)

| reg | role | authority |
|---|---|---|
| RSP | FORTH spine: box operands, ζ cells, choice/resume records — compile-time-constant offsets always | ZETA-MECH ONE-SYSTEM + LIFO law |
| RBP | EARNED frames ONLY (LAW: cell↔RSP distance non-constant at a reading site); ONE ENTER at α; `[rbp+ANCHOR]` chain to MATCH_BEGIN; α/ω SOLE writer; callee-saved ⇒ free across C | `GOAL-RBP-EARN.md` LAW + s28/s29/s30 rulings |
| RBX | GC heap-top / allocation frontier: inline bump-alloc in emitted code; GC honors rbx as frontier; today's DESCR mint pointer, formalized | `GOAL-SN4-HOME-RBX.md` |
| R12 | capture-pending arena TOP (mmap'd, STACK discipline — Lon s30b: *"Capture pending are in their own MMAP'd R12-topped arena"*); restored at backtrack re-entry (oracle pin W5); GC-visible | RBP-EARN s30b + EARN-5 (ONE AUTHORITY vs ζ-cell arm) |
| R10 / R11 | rΓ / rΩ wires, BOTH glue kinds, one product-wide convention; per-activation template-emitted saves; preserved or veneered at every C crossing | `GOAL-SN4-HOME-WIRES.md` (absorbs LADDER WREG + PT) |
| R13 / R14 / R15 | Σ subject base / δ cursor / Δ subject length-end — the match-state file ("match state collapses to four registers plus the frame", FINDING 08-02d); δ restore rides the choice record by design; ⛔ Σ/Δ save-restore across a NESTED match is an EARN-0b crossing row — verify on `161_pat_defer_fn_nested_match` watching r13/r15 (the LIFO check verified rsp/rbp only) | `x86_asm.h` literals + GOAL-SNOBOL4-BB FACT RULE; full 16-row map = HOME-RBX X-0 deliverable (s31) |
| R9 | GVA base (RTCC LIVE claim) | GOAL-RTCC |
| R8 + arg tier (rax rcx rdx rsi rdi) | RTCC slots; arg tier: claim it or stop paying for it (RC-8b) | **HOME-RBX X-5 (RC-8b/8c ADOPTED s31, gated on X-1)**; GC gap = HOME-RBX X-1; GOAL-RTCC stays law+history |

## HOME GATE — Definition of DONE (every line measurable; "100%" means THIS)

1. probe suite · crosscheck/patterns · xc318 · broad-336 · demo board (honest denominator — fence-dupe fixed) · bench-22: **oracle-green BY SET, BOTH modes, m3 ≡ m4 outputs byte-identical**; xfail only where oracle-blessed (p.123 stack-overflow class, `-s` remedy).
2. EARN-2 census: **`unearned == 0 && owed == 0`**; emitted frame count == classifier output exactly.
3. Gates strict: claim gate DATA-DRIVEN over {rbx r9 r10 r11 r12 + tiers}; **zero r10/r11 scratch anywhere incl. RTX hand asm**; RC-8a GC coverage green; TEMPLATE-ONLY + BOTH-MEDIUM greps == 0.
4. Deletions complete: BLOB-GRANT pins · CLASS-D `{res,rbp}` records + res stubs + ω absolute unwind + scanfail whack · legacy ARBNO arm · every dead killswitch · **`g_blob_ctx`/`rt_blob_ctx_ptr` grep == 0** (largely discharged by `0970838f` g_zctx per-activation base stack — the gate VERIFIES, never assumes).
5. Monitor sees the classes it has been dark on: stdout-only divergence (MON-CAP) + table-element-assign VALUE events. `handoff_status.sh` prints COMPLETE.
6. **BEAUTY:** the `beauty_suite` drivers green BOTH modes AND `demo/beauty/beauty.sno` byte-identical to oracle — **Milestone-1's md5 `abfd19a7a834484a96e824851caee159` re-proved at HOME** (any delta must be Lon-blessed as an oracle-behaviour change).
7. **RE-ENTRY EDGE INVENTORY CLOSED (s31):** every RBP/R12 restore edge enumerated and INDIVIDUALLY witnessed — backtrack β per choice class (arena pin W5: verify, never assume) · ω unwind · FENCE whack · scanfail · ABORT drain · unanchored retry bump · **NRETURN · direct Goto `:<C>` into CODE() blocks · SETEXIT traps** (manual Ch.9/19 non-local transfers — named in no seat file before s31). One missed edge = the FF-0 class. Deliverable rides EARN-3 (see GOAL-RBP-EARN s31 cursor).

## INSTRUMENT MAP (scanned 2026-08-12 s30 at corpus `5c17de98` — every suite, its runner, who consumes it)

| suite | where / size | runner | consumed by |
|---|---|---|---|
| **BB probe suite** | `probe/bb/probes/` — **163 .sno**; prefix families A=13 D=13 F=6 G=27 H=31 L=20 **N=33 (ARBNO)** X=12 f=4 t=3 z=1; `SUITE.md` is the row authority | `SCRIP/scripts/run_suite.sh` both modes (⛔ m4 arm DARK → B-0 first) | UNIVERSAL per-rung BY-SET gate. Family→seat: N → RBP/EARN-4 · D (D06/D12/D13 recursion) → RBP + WIRES W-2 · F/f + 151 + fence_probe → RBP FENCE rows · X (defer×DEFINE) + A → P3 AB · G/H/L broad |
| **Named witnesses** | `probe/` top — `arb1` (⛔ EARN-4's NAMED gate, T1+T2) · `w_cap_*`×6 + `mv_*`×2 (⛔ EARN-5's BY-NAME gate) · `dc_*`×5 (**`dc_recur` = the W-5 flip witness**, MECH bulletin) · `pb_*`×4 (LADDER PB) · `pt_inline_*`×3 (PT/WREG-5 gate) · `ab_*`×11 (P3 AB) · `rtx11_dynvar*`/`rtx_func_11*` (RBX X-2) · `uw2/uw3` (unwind) · `z4_*`×5 | sbl `.ref` beside each | seat-specific acceptance, cited by name in rungs |
| **earn0 witnesses** | `probe/earn0/` — **16 .sno** (s29 defect set + s30 pending-lifetime pins W1–W5) | refs oracle-baked | RBP monitor hunt · LOWER L-0..L-2 · ANY arena change (W1–W5 = acceptance) |
| **crosscheck ≡ xc318** | `crosscheck/**` — 34 dirs, **318 .sno EXACTLY** (the sum IS xc318): `rung2..rung11` + `rungW01..07` = the rung suites · patterns **122** · capture 9 · **gc 15 → RBX** · keywords 12 (LADDER KW) · **functions 10 → P3 AB/EARN-8** · strings 17 · library 4 · arith 10 · assign 8 · control 8 · data 6 · output 8 · concat 6 · hello 4 · coverage 1 | `board_patterns_set.sh` (patterns, BY SET, watch the BROKEN set); ⛔ B-1 names ONE sanctioned runner per remaining dir — and pins the broad-336 / 622-sweep denominators to a SCRIPT, not lore | phase-boundary floor both modes; patterns+capture are RBP/LOWER per-rung gates |
| **DEMOS** | `programs/snobol4/demo/` — **24 .sno**: the 15-board = {claws5, json, calculator-1, calculator-2, treebank}×{base, -match, -match-fence} (+ treebank-array/-list); plus roman · porter · wordcount · counter · arithmetic · expression · pattern_test · hello | `board_sno15_ident.sh` (**the ONLY sanctioned demo correctness instrument**) · `board_sno15_perf/perf2.sh` · `board_demos_zeta.sh` · oracle-ms baselines on record (json-match 34ms · treebank-match 10ms · treebank-array 8118ms · calc-1 55ms) | ⛔ **CORRECTED s39 (BOARD, FINDING-2026-08-12i): the "2/15" figure below was the BROKEN count claim — actual measurement is the INVERSE: 2/15 PASSING (claws5-match, claws5-match-fence), 13/15 BROKEN, SCRIP `825ab0a4`.** Every non-passing member fails by direct SIGSEGV except `claws5` base (timeout). Minimal one-line-input reproducers exist for calculator-1/calculator-2/treebank-array; NOT yet shown to be the same class as {A06,X05} — do not assume already covered. This board is the plan's most legible progress meter, and it currently reads BADLY, not nearly-done · P4 timing board |
| **BENCHMARKS** | `benchmarks/snobol4/` — 23 .sno, 1 xfail ⇒ **22 graded** | `test_bench_snobol4_modes.sh` (post-09f floor OK=17) + `bench_sno_*` + `build_benchmarks.sh` | perf floor **"18/22 hold-or-better"** (BB DoD, carried) + CRASH-class tracker · RBX X-3 perf proof |
| **BEAUTY** | `programs/snobol4/demo/beauty/beauty.sno` (Milestone-1 flagship) + `programs/snobol4/beauty_suite/` + `smoke/beauty_compiled.sno` | `test_gate_sn7_beauty_self_host.sh` · `test_monitor_beauty_smoke.sh` · `test_gate_em_beauty_subsystems_mode4.sh` · `test_interp_broad_corpus_and_beauty.sh` | ⛔ **17/17 drivers SIGSEGV at HEAD (FUNC-11, one include)** ⇒ **RBX X-2's ACCEPTANCE**; the flagship byte-identity is **P4's seal (HOME GATE line 6)** |
| **lib/** | `case.sno` · `string.sno` · `math.sno` · `stack.sno` | exercised via demo/xc customers | LOWER L-3 (`test_case` is a splice customer) · L-5 (`test_string`) |

## PHASES — DEPENDENCY MAP ONLY (s32: NOT a schedule; the only gates are rung-level ⛔ REQUIRES predicates; the "solo"/"‖"/"SERIAL" wording below is legacy shape, non-binding — see EXECUTION MODEL)

- **P0 — BASELINE (BOARD seat, solo, opens immediately):** m4 harness repair → floors re-proved BOTH modes at ONE hash → EARN-2 census re-cut to UNEARNED/OWED (⛔ standing law: BEFORE any frame-moving rung; also settles 557-vs-263) → discriminating refs (the 10 unclearable + polarity siblings) → claim gate data+strict. **Output = the floors every later seat judges BY SET against.**
- **P1 — ‖ FOUR SEATS (disjoint file surfaces):** **RBP** (GOAL-RBP-EARN): MONITOR-FIRST on `earn0_disc_arbno_star_fence_positive` → EARN-1 dormant → EARN-3 anchor → EARN-4 ARBNO-from-scratch (discharges ruling (c) by execution; witnesses N22–N33 + arb1 T1/T2 + 151) ‖ **LOWER** (HOME-LOWER): Defect A → B → C-9 residuals → 061 ‖ **WIRES** (HOME-WIRES): claim sweep incl. asm → ZCTX r10/r11 scratch eradication → guard unification → WREG mechanism DORMANT ‖ **RBX** (HOME-RBX): contract → RC-8a → FUNC-11 allocation instrumentation → fix.
- **P2 — ‖ THREE SEATS:** **RBP**: EARN-5 (ONE AUTHORITY: ζ-cell vs arena; W1–W5 acceptance) + EARN-6 (MATCH_BEGIN/FENCE conditional; FENCE(P) row classified) ‖ **WIRES**: PROC-shim delete (PT) + **WREG FLIP — ⛔ REQUIRES EARN-1 + EARN-3 LANDED** (EARN-10 ordering: pass-thru with zero frame is only correct once needy constructs earned theirs; the old 19-SEGV+7-HANG residual is EXPECTED cured — measure, never assume) + RTCC re-entrant preservation + default-ON revalidated (kill the m4-130 class) ‖ **RBX**: inline bump-alloc arms + ZHP-exhaustion re-check post Defect B.
- **P3 — SERIAL, one seat at a time, FULL RUNWAY each (a half-flipped sole authority is a broken tree by construction):** EARN-11 α/ω sole-RBP-writer flip (dormant byte-identical → per-node arming) → EARN-7 residue sweep (CLASS-D scaffolding, BLOB-GRANT pins, legacy ARBNO remnants) → LADDER AB call path (`fn_cell` jmp; RTX call asm) → EARN-8 STATEMENT/FUNCTION re-exam (ruling (d) becomes DECIDABLE here, with EARN-7 measurements in hand).
- **P4 — SEAL:** full-suite sweep · killswitch deletion · regen ×N · census seal · FINDINGs · handoff per FACT RULE.

## SEATS

| seat | file | absorbs / owns |
|---|---|---|
| RBP | `GOAL-RBP-EARN.md` (existing — the EARN ladder IS the plan) | EARN-0..11, ARBNO, FENCE rows, 151, D12/D13 recursion class |
| LOWER | `GOAL-SN4-HOME-LOWER.md` | s29 Defects A/B, CLIMB C-9 residuals, 061, test_string |
| WIRES | `GOAL-SN4-HOME-WIRES.md` | LADDER WREG + LADDER PT (from RBP-EARN, by reference), MECH M-1c guards, RTCC wire half |
| RBX | `GOAL-SN4-HOME-RBX.md` | rbx contract, RC-8a, RTX-FUNC-11, inline alloc, arena GC visibility |
| BOARD | `GOAL-SN4-HOME-BOARD.md` | EARN-2 census, floors, refs/witness hygiene, gates, m4 harness, MON-CAP. **ZERO compiler bytes ever** — collision-free by construction |

Legacy goals (SNOBOL4-BB · SNOBOL4-RTX · RTCC · ZETA-MECH · ZETA-CLIMB) remain HISTORY + law authority; their open SNOBOL4 items are absorbed above; their Icon/Prolog scope is untouched.

## COLLISION PINS (named in advance — this is why the partition works)

- **`emit.cpp` frame arms:** RBP seat lands EARN-1/3/4 there; WIRES must NOT cut those arms before P3/EARN-11 — the s12 "highest collision surface" note is now an ORDERING LAW. **s31 extension:** the pin covers the ZCTX sequences and the push/pop guard pair (emit.cpp:2373/2806) — W-1/W-2 edits sit adjacent to the α/ω authority EARN-11 later claims. Under the CONSOLIDATED seat this is internal sequencing; on any re-fan-out it is a named pin.
- **Arena record layout (+16B wire-pair slot, WREG-3):** WIRES OWNS the layout; RBP/EARN-5 CONSUMES. One authority — the CAP-SYM lesson.
- **`x86_asm.h`:** encoder ADDS only (TEMPLATE-ONLY law); any seat may add, none may reshape.
- **RTCC veneer ↔ wires:** safe config = RTCC-ON **AND** wire capture/restore — neither alone (s14 arbitration). WIRES owns the pair.
- **Floors/census:** ONLY BOARD re-cuts instruments; every other seat consumes and cites.

## ADOPTED / PARKED LEDGER — s31 CONSOLIDATION AUDIT (legacy work the seat files did not carry, now assigned or explicitly parked; audit FINDING-2026-08-12b)

- **LADDER KW** (GOAL-SNOBOL4-BB KW-0..6, keywords native): **ADOPTED, P3.5** (after EARN-11/EARN-7, before P4 seal). Acceptance = the xc318 keywords-12 dir green both modes — HOME GATE 1's implied requirement made explicit. Authority stays the BB file. KW-5's native `&STLIMIT`/`&STCOUNT` also feeds the monitor (BOARD-adjacent).
- **DEFER LATCH** (`g_star_peek` → per-site resolution; GOAL-SNOBOL4-RTX row): **ADOPTED, P1-concurrent** — `pattern_match.c` only, zero collision with any seat surface. Witnesses `140_pat_eval_double_fn_trick`/`141_pat_eval_double_fn_arbno` (RED m3 rc=139 / m4 PASS — a two-sided gate for free) promoted to the named-witness layer (BOARD B-7(iv)). Manual-proven structurally wrong (Ch.7 p.86 + Ch.9 pp.122–3: deferred eval RE-ENTERS deferred eval; a one-entry name-keyed latch is guaranteed clobbered). Same single-cell disease as `g_blob_ctx`/`g_rtcc_block`.
- **MECH S-LADDER** (M-SLEN S0–S5 incl. S4 register-only MATCH_BEGIN α): **RIDES EARN-6** (RBP seat) — S4 is EARN-6's implementation arm, never orphaned. Authority GOAL-SN4-ZETA-MECH.
- **CLIMB C-10 / C-11** (data+keywords witnesses; EVAL/CODE/EXEC summit incl. the 1016/1019/161 gatekeep class): **ADOPTED, P3.5.** C-11 doubles as the EARN REENTRANCY STRESS SUITE — EVAL/CODE re-entry is exactly what earned frames + the R12 arena must survive. Authority GOAL-SN4-ZETA-CLIMB.
- **RTCC residue:** RC-8b/8c **ADOPTED at HOME-RBX X-5** (gated on X-1); RC-5 anchor re-open + RC-7 fold **PARKED** in GOAL-RTCC pending Lon + X-1.
- **RTX perf ladders** (RTX-4/6/9/10/12): **PARKED BY DESIGN** — correctness first; HOME GATE 3 already pulls the RTX hand-asm surface into W-0/W-1. RTX instrument debts adopted at **BOARD B-8**.
- **LADDER PB: CLOSED pre-consolidation** (all rungs `[x]`, BB cursor 07e "LADDER PB CLOSED") — PLAN.md's row is stale by design; do NOT reopen. Its `131` residual (`pat_static=0` 528B UCLAIM class) flows to EARN-7/M-3 deletion.
- **BB demo-board bisect** (`d2328f81..942ef1b1`, predicate `/home/claude/bisect_tb.sh`, witness treebank-match rc=139): **HELD AS FALLBACK** — P2's prediction is EARN restores the FF-0 defer members; if the 15-board does not recover, the bisect is the instrument, not a re-derivation.
- **Milestone-2** (stage2 self-host): explicitly **OUT OF HOME SCOPE** — GATE 6 re-proves Milestone-1 only.

## ⭐ LIVE CURSOR — 2026-08-12 s32 (Fable 5 — EXECUTION MODEL landed: fire-and-forget, five sessions one-per-seat-file, self-gating REQUIRES predicates + THE POOL; no human scheduling exists in this plan. The s31 audit facts below stand unchanged. ZERO compiler bytes.)
P0 STILL UNOPENED; first seat BOARD (B-0 m4 harness repair first). **s31 = the consolidation audit** (`FINDING-2026-08-12b-CLAUDE-FABLE5-SN4-HOME-CONSOLIDATION-AUDIT-…md`): the EARN scheme VERIFIED as frame-pointer-on-demand (alloca/VLA discipline) + side arena — sound, taxonomy total, conditional on (i) reads-based census incl. glue reads, (ii) the closed re-entry edge inventory (new GATE line 7), (iii) GC coverage (X-1). Ledger above minted; register contract completed (R13/R14/R15 rows; REGISTER-LAYOUT.md's r12=ζ row bannered STALE); RC-8b/8c → RBX X-5; defer-latch → P1; KW + C-10/C-11 → P3.5; three obligations attached to EARN rungs (RBP-EARN s31 cursor). Fingerprints at s30 mint stand: SCRIP `fc5b0754` · corpus `5c17de98`+witnesses · x64 `5035571`. Ruling ledger unchanged: (a) RULED s30/s30b (arena stands) · (b) OPEN, zero-cost · (c) discharged by EARN-4 execution when P1-RBP runs it · (d) decidable at P3.
