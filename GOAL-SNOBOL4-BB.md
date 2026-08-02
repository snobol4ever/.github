# GOAL-SNOBOL4-BB — SNOBOL4 → native x86 Byrd-Box codegen

Frontend: SNOBOL4 → shared IR → BB emitter (mode-3 `--run` / mode-4 `--compile`). Protocol: RULES.md; template/encoder work requires ARCH-ICON.md + GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md FIRST. Watermark is SHARED STATE — re-prove at session start AND close. History pruned 2026-07-30; full text in FINDING docs + git (pre-shrink = `.github` `2f3fd45a`).

---

## ⭐⭐⭐ LIVE CURSOR — s23i (2026-08-02) — STATIC-SHAPE DEFER/PATREF ARMS · THE CAP-SLOT CRASH IS STACK PLACEMENT

**Directive (Lon):** complete the NON-POPPING FORTH-style RSP ZETA stack, C-style RBP only when absolutely necessary; *"All your choices. I'm with you on this. Continue."*

**LANDED (SCRIP; full text: `FINDING-2026-08-02b-...STATIC-SHAPE-ARMING...md`):**
1. ⭐⭐⭐ **`pat_static`** (new IR_t field) = lower's TRANSITIVE DEFER-FREE proof over `g_sno_seal`, stamped at the DEFER-of-VAR + PATREF sites; zd_plan's dynamic-box scan lets a static-shape DEFER/PATREF stop vetoing the quartet. Spine-vs-argument VAR distinction is load-bearing (LEN(N)'s N is a value read). FENCE1-in-statement still declines. `SCRIP_ZD_DYNARM` mask: =0 ≡ s23h regime byte-identical (proven vs committed artifacts); bits force-arm for A/B.
2. ⭐⭐ **Armed population 17/122** (fence-via-var 108–113, non-recursive star-vars, calc/regex/json-literal, 117); recursive 135/136 + statement-FENCE1 142 byte-verbatim declined.
3. ⭐⭐⭐ **CAP-SLOT BRACKET (core.3397, 127):** armed capture-in-blob died at `rt_cap_push(slot=rsp+176)` — the raw claim spelling is ENTRY-REGIME-DEPENDENT (blob compiled once, armed statements enter at shifted depth; slot lands on stale residue). Flip variable = ABSOLUTE STACK PLACEMENT: `SCRIP_NO_SEGV_HANDLER` is READ BY NOTHING — it merely shifts initial rsp by strlen; any dummy env flips 127 to 3/3 pass. Names 126/131/145/180/181's baseline reds as the same defect elsewhere. Narrowing = capture-bearing targets decline (25→17); the REAL fix is the r9/wire-carried claim base (CARRIED-OPEN), which also retires raw blob `[rsp+K]` spellings.
4. ⭐ **WATERMARK:** m3 281/26/10 · m4 266/39/10/2L — m4 EXACT BY SET incl. LERR pair {test_string, 1017_arg_local}; m3 +1 = the LAWS-named 213 flake (absent from non-pass set); armed-17 zero attributable P→F. Regen ×4: only crosscheck churned, exactly the 17, net −69 lines; emit-fail 15 / as-fail 2 held.

**NEXT:** ⭐ r9/wire claim-base rung (re-admits capture-bearing targets; retires raw blob spellings) · ZD-7 IR_CALL user-proc remainder · ON-4 pileup (⛔ GATED) · ⛔ PENDING LON: the ~21 column-1 files.

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
- **FOUR-modes confirmation** — `ZC_STORAGE_{FRAME_R12,FRAME_RSP,CELL_STACK,CELL_HEAP}`.
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
