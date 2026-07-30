# GOAL-SNOBOL4-BB — SNOBOL4 → native x86 Byrd-Box codegen

Frontend: SNOBOL4 → shared IR → BB emitter (mode-3 `--run` / mode-4 `--compile`). Protocol: RULES.md; template/encoder work requires the BB-CODEGEN design set (ARCH-ICON.md + GOAL-TEMPLATE-REVAMP-RULES-DRAFT.md) FIRST. The crosscheck watermark is SHARED STATE across parallel sessions — re-prove at session start AND close. History pruned 2026-07-30 (Lon directive): completed cursors compressed into the HISTORY INDEX; full text lives in the FINDING docs + git (this file pre-shrink = `.github` `2f3fd45a`).

---

## ⛔⭐ LIVE CURSOR — s21x-o (2026-07-30, Claude: ZTOS-1 SLIDING OFFSETS + GLUE-3 WIRED — the depth-displacement root cause is FOUND, NAMED, and FIXED at the address side).

**LON DIRECTIVES (s21x-o):** "Have each BB allocate its RESULT ... IF it has one and if it is used" · "one instruction, decrement RSP" · "Keep track of sliding offsets and index operands from RSP, not RBP" · "ONE main function that does graph traversal and calculates the zeta offsets" · "The actual allocation is always tied through x86_alpha() and x86_beta()" · "Do not put RSP references directly into the templates" · "turn on allocation dynamically FOR EVERY single BB ... no need to be shy" · "No pre-allocation calculation is necessary" · "Finish the RSP/RBP once and for all" · "All your choices."

**⭐ THE ROOT CAUSE OF s21x-j..n, ISOLATED TO TWO INSTRUCTIONS (SCRIP `b5754902`).** `028_arith_unary_minus` printed `5` for `-5`. Byte-diffing `--compile` against `SCRIP_BB_ALLOC=0` yields EXACTLY `sub rsp,16` / `add rsp,16` and nothing else. The literal pushes a 16B DESCR at TOS; `n1_unop_α` then carves its own cell and reads its operand at a template-private, HARDCODED `[rsp+0]/[rsp+8]` — which is now its OWN fresh uninitialised cell, 16 bytes below the operand. It negates garbage, stores into the dead cell, pops it, and `assign` reads the original un-negated `5`. **The allocation and the operand address were two authorities that did not know about each other**: the carve fires in `x86_port_hook` while each template had grown its own private `rspq()`/`rspd()` spelling raw `[rsp+off]`.

**ZTOS-1 — `op_zdepth` IS THE SLIDING OFFSET, AND IT IS ONE LINE.** Set at the ONE choke (`walk_bb_node_inner`, which every template invocation passes through) from the SAME `op_fc_bytes` the allocator spends, so allocator and accessor cannot hold two opinions — the `zw_node_k` ONE-K-AUTHORITY discipline extended to the address side. `ZTOS`/`ZTOSD` (x86_asm.h, the spine arm of `x86_zop`) resolve a TOS reference to `off + op_zdepth`: the producer's offset plus whatever the reader allocated beneath it. **LOCAL BY CONSTRUCTION — a box compensates for exactly what IT carved and knows nothing about its neighbours.** That is why NO pre-allocation pass is needed (Lon's directive is satisfied by the traversal the emitter already does) and why arming one BB can no longer displace another. `op_zdepth==0` reproduces the old raw spelling byte-for-byte, which is what makes the per-family conversion crawl safe. Converted: `bb_unop`, `bb_assign_global`, `bb_binop_arith`, `bb_binop_concat_slot`; their private helpers DELETED.

**GLUE-3 — THE TWO GLUE CODES ARE WIRED (SCRIP `785e3a41`), BYTE-IDENTICAL.** The four `x86_sub/x86_add("rsp",K)` lines inside `x86_port_hook` now route to `bb_glue_flat_enter/leave` (declared and built s21x-n with ZERO callers). Allocation reaches rsp ONLY through `x86_alpha`/`x86_beta` now. `ZC_STORAGE` becomes load-bearing AT THE ALLOCATION SITE for the first time: the hook allocated identically under all four modes, so FRAME_R12/FRAME_RSP would carve a per-BB cell ON TOP of the whole-graph frame they already carved (roman, from the other direction) and CELL_HEAP would silently take the rsp arm instead of its rbx frontier — the glue answers each mode and BOMBS on the unimplemented one. PROVEN byte-identical over 100 crosscheck programs + unchanged watermark. ⚠ Removing `x86_begin()` from both glue fragments was REQUIRED: it mints a fresh `x86_uid` in TEXT medium and that uid names the box's RO labels, so calling it per-port renumbered every downstream `.Lx` label — instructions identical, `.Lx5_0`→`.Lx8_0`. A pure label rename executes correctly and is INVISIBLE to a run-only test; only the byte-identity A/B caught it.

**⛔ NEGATIVE RESULT — THE ARMING FRONTIER IS A PROPERTY OF A BOX'S *READERS*, NOT OF THE BOX (measured; do not retry blind).** Lon said arm every BB, and the `_spine` exclusion looked like pure shyness: its own s21x-m note blamed the mid-spine displacement that ZTOS retires. Set to 0 and MEASURED: **m3 214→108, m4 211→107.** The spine kinds are FINE — `OUTPUT = 1 + 2` still prints `3`, and the A/B shows ZTOS compensating the binop's reads correctly. What broke is **111 programs that are almost all MATCH statements** (`033_goto_success`: the match runs, fails, takes `:F`). ROOT CAUSE is the SAME root cause one level out: **the match family does not address through ZTOS — it speaks `FRQ()`/x86_zop arm 3–4, whose compensation is `op_flat_disp`, LOWER's STATIC prefix sum, blind to per-BB carves.** Arming a producer that FEEDS a match deepens rsp under a consumer that cannot see it. THE LAW: a BB may be armed once ALL of its consumers speak the live-depth authority; arming it while a consumer still speaks the static authority displaces that consumer by exactly the new carve. **This is why widening by KIND kept producing the "unknown reasons" of s21x-j..m.** The exclusion is restored, with this reason recorded in `emit.cpp` in place of the wrong one.

**NEXT, DEPENDENCY ORDER (the frontier is now named, not guessed):** (1) ⭐ **MIGRATE THE MATCH FAMILY OFF `op_flat_disp` ONTO `op_zdepth`** — this is the ONE blocker between here and Lon's "every single BB"; the `_spine` list then retires BY ITSELF rather than by directive. Start `bb_match_head`, monitor-first per RULES. (2) The remaining 11 templates spelling `"rsp"` (measured: `grep -ln '"rsp"' src/templates/bb_*.cpp | grep -v glue`) — retire through ZTOS/x86_zop; `bb_match_capture`'s deliberate raw `rsp#` marker is load-bearing inside the SAVE/COND protocol and needs the splice ruling first. (3) `bb_binop_arith` does its own mid-body `add rsp,16` to pop its second operand cell — traced and composes correctly with op_zdepth, but it is still a raw rsp reference in a template. (4) **Wire `bb_glue_framed_*`** — the RBP half of "finish RSP/RBP once and for all"; customers closed by the s21x-c four constructs. ⛔ LAYOUT CONTRACT, not a spelling switch (s21x-m measured SEGV): whoever wires it wires the prologue's rbp save/seed in the same breath. (5) ARBNO onto the framed glue = the VARIABLE-EXTENT ANCHOR that retires the SUSPENDED-CELL law.

**⚠ CONCURRENCY:** watermark is SHARED STATE. `SCRIP_BB_ALLOC=0` reproduces the s21x-l baseline (m3 312/4) exactly.

---

## ⛔⭐ WATERMARK OF RECORD (2026-07-30, s21x-o)

**DEFAULT = RSP ACTIVATED (Lon s21x-m, unchanged):** **m3 PASS=214 FAIL=102** *(flaps ±1 run-to-run — see negative result 2 above; m4 is authoritative)* · **m4 PASS=211 FAIL=69 SKIP=36** · **DIVERGE=3**. This is the LADDER.  *(s21x-o ZTOS-1: 211/105 -> 214/102 and 208/72 -> 211/69, DIVERGE flat.)*
**KILLSWITCH `SCRIP_BB_ALLOC=0`:** **m3 PASS=312 FAIL=4** {test_case · 140 · 141 · 160} · **m4 PASS=312 FAIL=2 SKIP=2** {test_case · 160} · **DIVERGE=2** {140 · 141}.
Runner: `scripts/test_crosscheck_snobol4.sh` (~25s/arm). ⛔ Do NOT add `SCRIP_CALL2BB=1 SCRIP_CALL2BB_FC=1` for census work (s21x-i parked D2 defect).

---

## ⛔⭐ LON DIRECTIVE — s21x-c (2026-07-29): DESIGN OF RECORD = RBP/RSP FRAMES + FORTH-STYLE VARIABLE-LENGTH ζ CELLS. READ THIS BEFORE ROUTING ANYWHERE.

**TERMINOLOGY RULING: the s20x two-word name is BANNED — never write it, never speak it.** `GOAL-SN4-CELL-*.md` / `DESIGN-SN4-CELL-*.md` are DEAD routing targets (disk history only, outright deletion pending a Lon call).

**THE DESIGN (supersedes prior storage plans for BB RESULT/LOCALS wherever they conflict — including the s205 off-stack region split; RESULT and LOCALS both ride RSP):**
1. **Every BB allocates its own storage**: RESULT iff it has one AND it is used; LOCALS iff any. **ONE instruction: `sub rsp, K`.** Never a site allocating more than a few bytes for one BB.
2. **Sliding offsets, RSP-indexed**: the emitter tracks live depth at compile time; operands index from RSP, not RBP.
3. **RSP-only for EVERY box and construct until a genuine BRICK WALL**, then and only then the RBP/RSP dance (create the frame pointer forward, roll it back backward).
4. **The four RBP constructs: STATEMENT · FUNCTION · ARBNO · FENCE1** (~99.999% of storage is RSP; ARBNO's variable-length-children housekeeping is RBP). FUNCTION means only IR_CALL's frame dance — law 7.
5. **Named anti-pattern (roman)**: `sub rsp,1344` whole-graph carve + slot zero-fill + unconditional rbp pin. Whole-graph prefix-summed prologue carves are WRONG.
6. **DEFINE, constant-folded, emits exactly TWO BBs: IR_SAVE_RESTORE + IR_CALL** — and IR_CALL just sets up the RBP/RSP frame. That is all it does.
7. **SCOPE LAW: reduce the SCOPE of ALL processing DOWN to the STATEMENT level. NO FUNCTION-level processing WHATSOEVER.** IR_SAVE_RESTORE handles the globals (SNOBOL4's one NV namespace — fname/formals/locals are globals; manual Ch.19 save/restore); IR_CALL sets up the frame, nothing else; NO ζ in the call path except IR_SAVE_RESTORE's own carved slots (itself a BB — law 1). CONSEQUENCES: per-function/graph storage planning DIES (zls_build graph scope over); proc jmp-entry carve + zero-fill DIES; `[rbp+16/24]` param cells DIE (args land in NV globals); slot0 result protocol DIES (return value = the fname global at RETURN). Statement scope is the ceiling of every planning pass.

**s21x-f COMPANION DESIGN — DYNAMIC BOX GLUE:** any BB graph (one entrance, four ports) invokable by a full four-port DYNAMIC BOX: **(A) DYNAMIC-FLAT** — α: `jmp [entry_cell]`, β: `jmp [resume_record]`, γ/ω = supplied wire landings; zero frame, zero pcall record, zero C crossings; first customer **IR_MATCH_PATREF** (eager stored pattern, cannot recurse — manual p.122). **(B) DYNAMIC-FRAMED** — same shape + the RBP/RSP dance. Open rungs: x86_asm.h dynamic-flat glue primitives (both-medium, runtime cells, no rel32 patching) · PATREF rides dynamic-flat under the regime · fc_geom PATREF k=16 after the template splits its sink window. (The original list's CALL2BB slices LANDED s21x-g/h.)

---

## ⛔ LAWS & TRAPS (binding; falsified experiments — DO NOT RETRY)

- **SUSPENDED-CELL (s21x-l):** no rsp cell may suspend across γ above an ARBNO/DEFER extent until the anchor lands (cursor above).
- **RESULT-IS-THE-CELL (s21x-k):** the consumer overwrites the popped source cell IN PLACE ([rsp+0/8], no pop, net-zero); flat result stores are the environ-smash disease (bb_assign_global cured; assign_local/stub bodies unaudited — NEXT 5).
- **RBP HOUSEKEEPING (s21x-k):** the five POST-UNWIND head fields ride statement-bracket slots `[rbp−48+8k]`, carved `sub rsp,48` at head α (+8 pad keeps C-call 16-align), spelled via x86_parse generic reg-disp, NO frame compensation BY DESIGN.
- **SOLE-CONSUMER FENCE (s21x-j):** subject registration requires IR_MATCH_HEAD be subjval's ONLY operand consumer (pure dataflow scan of g->all, no kind naming); replacement statements decline wholesale pending the splice ruling.
- **UNION-TAG (s21x-g):** IR_t sval/ival/dval are ONE union — roles normalized to clean op_ival/op_sval at the single dispatch point; the op_sval promotion whitelist must NEVER include IR_SAVE_RESTORE.
- **NODE-EXACT HANDOFF (s21x-g):** emission order is not a contract (BFS interleaves); producer→consumer keyed by CALL NODE POINTER. Corollary: EVERY template return path defines α (m3 dangling-label class; m4 masks it — TEXT resolves by name).
- **STUB DISCRIMINATOR (s21x-h):** the DEFINE-stub key is `g_flat_frame_floor > 0` (the driver's own verdict, mode-uniform); admit-all-jmp-entry regresses EVAL/CODE chains. A call's result cell is `op_fc_wbytes` WINDOW-ONLY, never an alpha-sub (would sit on sr0's live block and shift the c2 landings' restores by 16).
- **fc grant = per-kind dispatch preamble** (emit.cpp 843/852 3-line shape) until NEXT 4 consolidates; the base varies per kind — copy the shape, not a neighbor's base.
- **DEFER-DEEP LOAD-BEARING (s197):** do NOT drop IR_MATCH_DEFER from deep-arrival until recursive-defer programs pass — that green is false (every recursive witness sat inside the old FAIL set). The correct narrowing was eager-vs-unevaluated (s199 DEFER-STAR, landed).
- **s206 DO-NOT-RETRY:** the `x86_fc_cells()=(FORTH||HEAP)` predicate flip → wild jumps (3 OK → 0 OK). The ONE port opinion is `fc_cells_on` (Z4-6); port-blind grant vs port-gated consumption was the defect class.
- **SCAN-RETRY = 5th rbp member (s196):** PAT$ `scanfail` unwinds from arbitrary carve depth (SPITBOL Ch.18 step 6); `&ANCHOR` is a runtime keyword — no static classifier retires the pin.
- **GOTO J3 (s21x-e):** `case IR_GOTO` fires `emit_mon_label_tap` — the monitor's ONLY scr event source; GE-1 relocation is the prerequisite to ANY goto deletion.
- **ALL-OR-NOTHING PER GRAPH:** a blob compiles ALL-NEW or ALL-LEGACY, never interleaved.
- **STALE-BINARY TRAP (s21x-j):** `[ -x scrip ]` is not a build check — `grep -c error:` on BOTH make logs + fresh mtimes. Edit only from RAW viewed lines (two truncated-view self-inflictions on record).
- **op_flat_disp RIDES EMISSION ORDER** — any schedule/layout change must first prove per-chain disp locality (blocks the SRC-ORDER blind fix).
- **CROSSCHECK MASK:** stdout-only `|| true` hides post-output crashes; the rc-checking arm is NEXT 7 (safe to add since s21x-k).
- **CENSUS SHELF LIFE:** re-run, never cite. HEAD-STAMP every measurement when parallel sessions share the volume (s197 concurrent-writer incident).
- **PROSE-ROT (s196, partly fixed since):** verify doc claims against live source before citing (ARCH-ICON register table corrected 2026-07-18; TEMPLATE-REVAMP's r12 ζ-scratch note is stale history).

---

## ⛔ PENDING LON RULINGS
- **Default-flip license** for the statement regime (armed 44/316; gate-on == gate-off at HEAD).
- **FOUR-modes confirmation** — s21x-l read "the FOUR modes" as `ZC_STORAGE_{FRAME_R12,FRAME_RSP,CELL_STACK,CELL_HEAP}` (zeta_choices.h). Confirm or veto.
- **Replacement-splice ruling (s21x-j):** splice reads the cell, or a write-through — retires the sole-consumer fence for the replacement class (gates NEXT 2's replacement arm).
- **SRC-ORDER-LAYOUT ruling A/B/C** (ladder below).
- **RBP-SHED-7:** ⛔ blocked (ARBNO `zv()` borrow is inside the sanctioned four) — DO NOT START.
- (ZHEAP ζ_self ruling: moot unless Lon revives ZHEAP — see SUPERSEDED.)

---

## LADDERS (live, unchecked — a shrink pass must NEVER delete a live rung: s186 lesson)

### GOTO-ERAD (s21x-e survey verdict: the wire already IS the design — branch_chain rewires past IR_GOTO carrying port tags, dead_goto deletes husks; load-bearing consumers = J3 monitor taps + J4 operand-protected survivors; IR_GOTO_DEFERRED STAYS — its target is data)
- [ ] GE-0 census: compiler sweep of emitted `_goto_` boxes; autopsy the 037 operand-list protector.
- [ ] GE-1 ⛔ MONITOR TAP RELOCATION (the prerequisite): move emit_mon_label_tap to the statement-head walk (bb_src_of heads); delete bc_stamped/dg_mon exemptions; PROOF = 2-way monitor event-stream parity (also closes the s195 scr-granularity gap).
- [ ] GE-2 survivor unprotection (J4); default-arm .s shows zero `_goto_` boxes.
- [ ] GE-3 SNOBOL4 lower-side: label-fixup direct edges at the 14 minting sites (re-derive the ~624 both-edge router's chase semantics per site); `grep IR_GOTO lower_snobol4.c` → 0 excl. DEFERRED.
- [ ] GE-4..7 per-language, one file each, concurrent-safe: icon 24 · pascal 10 · prolog 8 · raku 7 sites.
- [ ] GE-8 emitter sweep: delete `case IR_GOTO`, the six sz-sniffing chase loops, bb_goto; branch_chain drops passthrough; dead_goto retires.
- [ ] GE-9 enum deletion; gate `test_gate_no_ir_goto.sh` == 0 plain matches.

### RBP-SHED (order 3→1→2→4→5; SHED-1/2/4/5 need the BB-CODEGEN design set and fire `.s` regen — NOT concurrency-safe; SHED-3 is emitter-C only, safe)
- [ ] SHED-3 REC-PIN-OWN: emit_rec_pin's `g_gen_proc_active||g_resumable_callable_active` are stale-emission globals leaking blob→main (w1 witness, refreshed only at emit.cpp ~1821); move to a graph-own g_emit mirror at the emit_chain choke; gate = ZETA-FB-1 divergence instrument reads 0 + w1 hook-skip rc 1→0.
- [ ] SHED-1 NPARAMS: retire the `g_flat_outer_nparams>=1` pin conjunct (xaf_deep, xa_flat.cpp:171) for depth-static graphs; first deliverable = the conjunct's unrecorded provenance; census FIRST (shelf life).
- [ ] SHED-2 ABORT-REBALANCE: route ABORT's kill through the statement fail exit (manual Ch.9/18 — immediate whole-match failure) so abort-bearing graphs stop disqualifying fb refinement; 170/171 tripwire BOTH directions.
- [ ] SHED-4 HOOK-ENCODE: scanhit/scanfail hooks (emit.cpp 2183/2197) through x86() — the named forbidden medium-branch shape with hand-spelled rbp; completion = byte-identical pattern_bt/string_pattern .s + medium-invisible gate green.
- [ ] SHED-5 ALIGN-DANCE-DELETE: retire the transient push-rbp alignment window per x86_asm.h:419's own death-path comment (run the env-gated assert clean first; dirty sites ARE the rung).
- [ ] SHED-6 pointer: PL-DC seed gating (xa_flat.cpp:763) → copy into GOAL-PROLOG-BB.md at the next Prolog session, then strike here.
- SHED-7 ⛔ blocked on Lon (rulings above).

### SRC-ORDER-LAYOUT (s21x-b, diagnosed; awaiting ruling): `# <source>` comments are CORRECT; the statement LAYOUT ORDER is scrambled (cm2: 1,5,2,3,4 · cm3 zero-goto: 1,2,4,3,5 — label-correlated, possibly two mechanisms; reorder exists by emission-walk time). Execution correct (control rides edges). ⛔ Blind-fix hazard = op_flat_disp emission-order dependence (law above). Ruling: (A) emit-side stno sort — prove/make disp schedule-independent first (byte-diff unpinned benchmarks under SCRIP_FB_STMT=1 is the falsifier), make the :stno store unconditional · (B) lower-side scramble bisect (cm3 is the cleanest probe: instrument node-id vs stmt-index at lc_build) · (C) accept. Gates either way: watermark start+close, census, `.s` regen ×5.

### FB-STMT RE-ARM (s21x; landed opt-in `SCRIP_FB_STMT=1`, default OFF — SCRIP `81345044`): per-node frame-base refinement; measured pinned-benchmark rbp value refs 1015→220, survivors = match-family housekeeping only. Falsified premise "statement exits rebalance rsp": (a) ARBNO hit-path element retention (180_pat_arbno_defer_nonrecursive) · (b) DEFER/VALUE-alt backtrack re-pump of a retained blob (072_pat_star_var_alt_backtrack); default-on regressed 7 programs, reverted same session. RE-ARM LICENSE: monitor-first 180 then 072; extend the bit map downstream of any retaining statement until release_to provably sweeps, OR land free-on-final-success — then flip the default.

### CARRIED OPEN (verify liveness before executing): MARKER-CAPTURE (s202 ALT-FLAT next rung — SAVE/COND pend-stack marks carrying start cursor, deletes SAVE's zls slot + COND's cross-extent FRQ read + the fc_leaf_walk special case) · r9 park-address anchor (the s202 named defer-window fix — the candidate mechanism for NEXT 1) · arm-quad OVERLAY in zls_build (union max-not-sum) · fc_cond FIRST-WINS audit (s195) · SYM-VIS-M3 perf JIT map (s195, `SCRIP_PERF_MAP=1`) · Icon generator-scan FORTH cells (fc_geom NOT-YET note: UPTO/FIND/MATCH/BAL inside a scan env).

---

## ↗ MOVED OUT / SUPERSEDED
- **SN4-RTX** → `GOAL-SNOBOL4-RTX.md` (contract ARCH-SNOBOL4-RTX.md). Phase-1 rungs touch zero templates, safe concurrent; **RTX-11/12 are NOT** (x86_asm.h + `.s` regen). Watermark is shared state between the ladders.
- **ZHEAP (s204/s205/s206) + the CELL ladder (s202/s203 seeds): SUPERSEDED by the s21x-c design of record** — RESULT and LOCALS both ride RSP; the whole-graph carve is REPLACED by per-BB carves, not re-plumbed. ZC_PORT_HEAP's rbx α-carve stays dormant-ratified (HZ-1, x86_asm.h ~1620); the s206 laws above still bind. Do not resume the CELL files (terminology ruling). Full plan text recoverable at `.github` `2f3fd45a`.

---

## HISTORY INDEX (one line per session; full text = FINDING docs + git)
- s21x-o (07-30) ZTOS-1 sliding offsets (`b5754902`) + GLUE-3 wired byte-identical (`785e3a41`); depth-displacement root cause found = allocator and operand address were two authorities; arming frontier proven to be a property of a box's READERS (spine-armed m3 214->108, 111 match programs, FRQ/op_flat_disp is the blocker). m3 214/102, m4 211/69, DIV=3. FINDING-2026-07-30-CLAUDE-SN4-ZTOS-1-SLIDING-OFFSETS-AND-THE-ARMING-FRONTIER-IS-THE-READERS-NOT-THE-BOX.md
- s21x-m (07-30) UNIVERSAL PER-BB RSP CARVE ACTIVATED BY DEFAULT (Lon directive); zw_node_k K-authority; two glue codes; SCRIP_BB_ONLY/SKIP bisect keys; three laws (four-port bracket · spine-is-already-the-cell-machine · pin-is-a-layout-contract). Ladder opens at m3 210/106, m4 208/72/36, DIV=3.
- s21x-l (07-30) SEQ-CELL dormant, suspended-cell law; record in SCRIP `7839c64e` commit message (FINDING doc pending handoff).
- s21x-k (07-30) SUBJ-ARM: first armed match statements 31→44; bracket rbp slots; result-is-the-cell; STF-EXIT-SEGV cured. FINDING-2026-07-30-CLAUDE-SN4-SUBJ-ARM-FIRST-ARMED-MATCH-STATEMENTS-ENVIRON-SMASH-ROOT-AND-STF-EXIT-SEGV-CURE.md
- s21x-j (07-30) SUBJECT-CELL v1; sole-consumer fence; stale-binary trap. FINDING-2026-07-30-CLAUDE-SN4-SUBJ-CELL-V1-LANDED-SOLE-CONSUMER-FENCE-AND-THE-STALE-BINARY-BUILD-OK-TRAP.md
- s21x-i (07-30) CALL2BB 3b dormant (SCRIP `8437c3d7`); sr0 rides the γ spine; D1/D2 fence defects. FINDING-2026-07-30-CLAUDE-SN4-CALL2BB-3B-V1-LANDED-DORMANT-SR0-RIDES-THE-GAMMA-SPINE-AND-TWO-FENCE-DEFECTS.md
- s21x-h (07-30) CALL2BB 3a: stub blobs ride the regime (`126645fc`); g_flat_frame_floor law; roman half-dead; gate-on 313/2 · 311/2 · DIV=0 (two-gate world). FINDING-2026-07-30-CLAUDE-SN4-CALL2BB-SLICE3A-STUB-BLOBS-RIDE-STMT-REGIME.md
- s21x-g (07-30) CALL2BB 2: role-0 prefix + staged skip (`3e3096a2`); union-tag + node-exact laws. FINDING-2026-07-30-CLAUDE-SN4-CALL2BB-SLICE2-ROLE0-PREFIX-AND-STAGED-SKIP.md
- s21x-f (07-29) OP-SPLIT PATREF/DEFER (`fc27a7b3`); CALL2BB slice 1 gated (`aa4cbff0`); dynamic-glue design ratified (kept above).
- s21x-e (07-29) admit-all classifier, registration-is-the-license (`35aa7cbd`); DIV/MOD/POW (`13a0dbc4`); frontier measured; GOTO-ERAD survey. FINDING-2026-07-29-CLAUDE-SN4-S21XE-ACROSS-THE-BOARD-CLASSIFIER-AND-THE-FRONTIER-IS-ORDINARY-SCALARS-IN-SUBJECT-POSITION.md
- s21x-d (07-29) per-graph all-or-nothing regime opt-in (`SCRIP_STMT_FRAME=1`); st_x/st_pre stubs; fc-flavor conjunct; armed 7/316. FINDING-2026-07-29-CLAUDE-SN4-STMT-FRAME-SLICE1-LANDED-AND-THE-FC-FLAVOR-CONJUNCT.md
- s21x-c (07-29) DESIGN OF RECORD (kept above in full).
- s21x-b (07-29) artifact provenance sweep (506 dead files deleted, SCRIP `2c22b2c5`); RBP-SHED + SRC-ORDER ladders written; regen scripts added.
- s21x (07-29) FB-STMT opt-in (`81345044`); rebalance premise falsified (kept above as ladder).
- s206 (07-28) port-7 selectability fixed (`cca948c5`); predicate-flip DO-NOT-RETRY (kept as law).
- s205/s204 (07-28) ZHEAP plan of record + α/ω discipline + addressing contract — superseded s21x-c.
- s203 (07-28) SEQ/ALT prefix-allocation seed (`d5c7a72b`) + register-planes model (DESIGN-SN4-REGISTER-PLANES.md); cell_6 self-suspect note.
- s202 (07-28) cell seeds 2-5 + icon_cell_1 (`1e881ce5`). s202 ALT-FLAT (`0f31f7f7`): zero-cell ALT, flat arms via fc_arm_member (registration order load-bearing, lower ~1509); 155 fixed, 123 broke — defer-window root + r9 park fix named.
- s200 (07-28) bisect → FLATDISP-1 first-bad; fc_geom DEFER omission; PATREF split directive; 4-line gate reproducer. FINDING-2026-07-28-CLAUDE-SN4-DEFER-GEOM-AND-PATREF-SPLIT.md
- s199 (07-28) DEFER-STAR eager/unevaluated split, census 113→48 (`9b19bb5a`). FINDING-2026-07-28-CLAUDE-SN4-DEFER-STAR-SPLIT-IS-THE-NARROWING-S197-MISSED.md
- s198 (07-28) SCANBASE reland (`6c16762a`); stored-pattern segv localized to bb_match_release. FINDING-2026-07-28-CLAUDE-SN4-SCANBASE-LANDED-AND-STORED-PATTERN-SEGV-LOCALIZED.md
- s197 (07-28) DEFER removal falsified (kept as law); deferred-arg family found; concurrent-writer incident. FINDING-2026-07-28-CLAUDE-SN4-DEFER-DEEP-IS-LOAD-BEARING-AND-DEFERRED-ARG-FAMILY-BROKEN.md
- s196 (07-27) SCANBASE; FLATDISP-5a premise falsified → scan-retry 5th member (kept as law). FINDING-2026-07-27j-CLAUDE-SN4-SCANBASE-AND-FLATDISP-5A-PREMISE-FALSIFIED.md
- s195 (07-27) two FLATDISP displacement mines killed, m3 185→221 (`62aaf9ff`); FRQB born. FINDING-2026-07-27i-CLAUDE-SN4-FLATDISP-CAPTURE-CALL-DISPLACEMENT-MINES-AND-ARBNO-ELEMENT-CLOBBER.md
- s194 (07-27) FLATDISP-7 per-graph pin gate, rbp census 237→119 (`d95b1a98`). FINDING-2026-07-27h-CLAUDE-SN4-FLATDISP-7-JMP-ENTRY-PIN-GATED-AND-RK-SUBS-PREEXISTING-SEGV.md
- s193 (07-27) FLATDISP-5b/5c + ABORT-NODE + bracket gate (`b3996516`); Lon's per-BB directive first stated. FINDING-2026-07-27g-CLAUDE-SN4-FLATDISP-5B5C-ABORT-NODE-BRACKET-GATE.md
- s186 (07-27) SN4-RTX split out to its own file; the shrink-pass lesson (8 live rungs deleted by a prior prune, recovered from `950e6a9f`).
