# ⛔ CORRECTION BANNER — s202/s203 (2026-07-28). READ BEFORE ANY LINE BELOW.
Six executed seeds (`SCRIP/seed/test_sno_cell_1..6.s`, `test_icon_cell_1.s`, all oracle-checked) falsified or superseded parts of this contract. The text below is LEFT INTACT as the record; these override it:
1. **FALSIFIED — OPERAND PROTOCOL's "operand RESULT cells at `[rsp+K..K+16n)`, left directly on top by the children that just ran (LIFO invariant)".** A producer that RETAINS a choice cell (any ALT with untried arms = the normal case) interposes 32B between its result and the next operand's base, and whether it retains is PATH-dependent (arm 1 retains, arm N does not) — not a compile-time constant. Proved at runtime by cell_2; ARBNO makes it worse (cell_3 measured a 1056-byte dynamic span).
2. **DROPPED — "a resume point is only ever reached by POPPING the cell that names it".** That pop is what creates the gap in (1). cell_2 cuts to the cell WITHOUT popping. Popping became safe again only in cell_6, after result slots and choice cells separated.
3. **SUPERSEDED — "SEQUENCE — NOTHING (Lon ruling): pure wiring… delete `bb_match_sequence.cpp`" and the ALTERNATE section.** Lon s203: IR_SEQUENCE and IR_ALTERNATE are the ONLY nodes carrying an ARITY, and arity IS the allocation size. Made PREFIX (α allocates), everything else POSTFIX into a compile-time slot. **SEQ arity n → n slots; ALT arity n → 1 result slot + n−1 retry edges** (one arm survives — the two arities are NOT used for the same thing).
4. **⚠ (3) IS ITSELF SUSPECT AT ITS ANCHOR.** SEQUENCE is not a control boundary — nothing returns to a sequence; Ch.18 step 6 never consults one. Allocation boundaries must coincide with GARBAGE boundaries = TURNING POINTS (cell pushes: ALT, ARB/ARBNO/BAL, FENCE, scan BASE, recursive re-entry — rule is "anchors at cell pushes", never `if (op==IR_ALTERNATE)`). If the anchor moves there, E and CP COLLAPSE and "SEQ is nothing" is RESTORED. UNTESTED — `test_sno_1c.s`.
5. **CHOICE CELL is no longer "16B" nor "32B {resume, δ, prev_CP, markhead}".** Two distinct objects now: **RESULT SLOT 16B {start,len}, parent-allocated** · **CHOICE CELL 32–48B {resume, δ|TAG, prev_CP, prev_E, prev_MH}, pushed**. They were ever one object only because nobody owned the slots. `prev_E` disappears if (4) holds.
6. **ADDED — register planes.** RSP=TOP(WAM H) · RBP=CP(B) · RBX=E(E) · R12=MH(TR). One cell carries all four planes; one cut restores all four. See `DESIGN-SN4-REGISTER-PLANES.md`.
7. **ADDED — BOUNDARY CLAIM (UNPROVEN).** Proebsting 1997 allocates one STATIC temp per AST operator and needs no stack at all; his `ifstmt.gate` IS our `resume` field. A frame may be needed ONLY where a node is MULTIPLY LIVE (ARBNO/ARB/BAL instances, recursive stored patterns, procedure activations) = item-for-item the s195–s200 bug family. Decisive test pair: `test_sno_1a.s` (predict FAIL) vs `test_icon_a.s` (predict PASS).

# DESIGN-SN4-CELL-MACHINE.md — the ζ-CELL MACHINE for the SNOBOL4 scan blob
**Status: DRAFT for Lon review (s20x design session, 2026-07-28). Supersedes the s200 rungs (b)/(c) geometry plan; absorbs rung (a) (PATREF/STAR split) as CELL-7. Nothing landed yet.**

## THE DISEASE (not the symptom)
Reach-over was a RED HERRING (Lon, this session). The disease: control transfer decoupled from depth transfer. Every arrival site (`scanfail`, β resumes, DEFER release, ALT merge) receives rsp at a
depth its code must RECONSTRUCT — hence `op_flat_disp` prefix sums, `fc_geom` grants + the DEFER omission (s200), `fc_arm_member` declines, scanbase rebasing (s196/s198), parked anchors, the rbp
activation floor (s137/FLATDISP-5/7), and the `match_release` +16 (s198). One disease, many costumes. The cure is not better compensation: make control transfer and depth transfer THE SAME ACT.
A resume point is only ever reached by popping the cell that names it, and the pop leaves rsp exactly where the pusher stood. Reach-over becomes UNREPRESENTABLE, not merely prevented.

## THIS IS THE MANUAL'S OWN MACHINE
SPITBOL manual Ch.18 p.204, verbatim algorithm: a pushdown stack remembers backtracking possibilities; step 3 pushes {alternative, current cursor}; step 6 pops it on failure; empty stack + &ANCHOR==0
advances the start cursor and restarts. The choice cell below IS the manual's stack entry. Fullscan (p.123-124): matching is exhaustive, no heuristics, deferred expressions never assumed nonnull —
cells implement exactly that, no shortcut machinery to model. We are not inventing; we are finally embodying Ch.18 natively on the machine stack.

## THE MACHINE
- **RSP** — the one ζ stack, frontier. ALL match-lifetime state rides it as 16-byte cells. C-call 16-alignment holds by construction (cells are 16B multiples; align_enter/leave stays for odd sites).
- **RBP = CP** — pointer to the NEWEST CHOICE CELL (WAM's B). Set only when a choice is pushed/popped. Callee-saved ⇒ survives every NV_GET/runtime C call for free. NOT an activation floor, NOT a
  static frame base. The scan bracket (HEAD) saves the caller's rbp once and restores at RELEASE — the statement-level flat frame outside the blob keeps its current regime untouched.
- **Σ/δ/Δ = R13/R14/R15** unchanged (subject base / cursor / length). R12: dcap island stays as-is until CELL-5 retires it into MARK cells (which also fixes its re-entrancy hole — a deferred *FN(T)
  can run arbitrary code including nested scans; rsp cells are naturally re-entrant, the island and g_patstk_sp are not).
- **CHOICE cell** (16B pushed + rbp update): { resume_addr, saved_δ } then `mov rbp, rsp`-style link — concrete layout: push prev_rbp; push saved_δ; push resume; `mov rbp, rsp`. (Exact field order =
  CELL-0 ruling; keep resume on top so fail is pop-jmp.)
- **UNIVERSAL FAILURE (ω anywhere)** = one shared stub: `mov rsp, rbp` (cut the abandoned suffix — see FREE UNDO below); `pop rax` (resume); `pop r14`? — δ restore folded per layout; `pop rbp`
  (unlink); `jmp rax`. ~5 instructions, correct from ARBITRARY depth. The entire ω-edge topology of the pattern graph DISSOLVES into this stub; the emitter stops wiring ω ports inside blobs.
- **MARK cell** (conditional capture, `.`): { tag|target_descr, start_δ } pushed by SAVE; COND completes it in place with end_δ. NOT popped on success — it is the capture journal.
- **FENCE cell**: a choice cell whose resume = the fence action (FENCE0: scan-abort; FENCE1: fail-past-P). Details per construct below.
- **BASE cell**: the scan bracket's own choice cell; resume = unanchored-advance (δstart+1, bound r15d, runtime &ANCHOR test — the existing SPD-2 scanfail logic verbatim) or scan-fail exit.
- **FREE UNDO THEOREM**: cells are pushed in match-thread order, so `mov rsp, rbp` at failure discards EXACTLY the mark/fence/window cells of the abandoned suffix. Conditional-capture rollback on
  backtrack — the risk s19x MARKER-CAPTURE flagged ("backtrack exactness is THE risk") — is free. COND.β re-open logic: DELETED before it was ever written.
- **COMMIT WALK**: on whole-match success, RELEASE walks cells base→top (uniform 16B typed cells ⇒ the stack IS a scannable array) performing completed MARK assignments in left-to-right completion
  order, then cuts rsp to base. `$` immediate assignment is NOT a cell: write-through at its close-twin, survives backtrack (manual p.87: occurs whenever the subpattern matches, even if the whole
  match ultimately fails). `@` cursor-assign likewise write-through.

## CONSTRUCT MAP (manual anchors cited)
- **SEQUENCE — NOTHING (Lon ruling this session: pure wiring).** γ-chain = emission-order fallthrough; failure inside a sequence is the stack's business (Ch.18 step 6), never the sequence's. The
  SEQ-STATIC cursor slot and the FORTH-arm trampoline glue both die; four ports alias children at the driver (label aliasing, zero instructions); delete `bb_match_sequence.cpp`. SNOBOL4 side only —
  `bb_scan_sequence.cpp` (Icon) untouched this campaign.
- **ALTERNATE**: α of an N-ary alt pushes CHOICE{resume=arm2_entry, δ}; each armK entry (K≥2) rewrites its cell's resume to armK+1 (or pops itself and re-pushes — CELL-0 detail); arm γ falls to the
  merge. Replaces ALT-FLAT (s202) wholesale: the {delta,resume,next} static quad triple, address-over-index stubs, fc/zls grant, and the fc_arm_member decline machinery all die. Merge depth is
  dynamic per live cells and NOBODY CARES — nothing downstream addresses across the blob statically. Ch.18 step 3 verbatim.
- **ARB**: implicit alternatives (p.207: behaves as LEN(0)|LEN(1)|...). α: push CHOICE{resume=own_extend, δ}; match null; γ. extend (arrived by fail-pop): δ from cell; if δ<Δ re-push with δ+1
  semantics and γ, else fall to universal fail. Two labels, one cell, no quads.
- **BAL**: same shape as ARB with the paren-depth walk in the extend body (shortest-first, p.203).
- **ARBNO**: right-recursive shy form ARBNO(P) ≡ Q = '' | P Q (p.121: matches null first, extends per retry). α: push CHOICE{resume=try_P, δ}; γ. try_P: EPSILON GUARD — if δ == cell's saved δ
  (last instance matched null) fall to fail (SPITBOL stops extending on null instance; this is the s19x epsilon-resume-zero-guard, now ONE compare against the cell); else α(P); P.γ → recurse into
  ARBNO.α (push another cell). Instance count = live cells; the 310-line template, its counter, and the per-box .bss depth arena collapse. Recursion depth bounded by the machine stack — the manual
  itself documents recursive-pattern stack overflow + the -s growth remedy (p.123); we inherit SPITBOL's own contract honestly.
- **SAVE/COND (`.`)** — the TWINS, the eureka generalized: SAVE pushes MARK{target,start_δ}; COND finds it as the nearest open mark (it is at a known cell distance on the current thread — CELL-0
  detail: either scan-down over typed cells or carry the mark's address in the sub-graph's γ handoff) and completes in place. Journal semantics per COMMIT WALK; rollback per FREE UNDO. Retires the
  cross-extent FRQ read (the s19x reach-over), the SAVE zls slot, the fc_leaf_walk 1046-1049 special case, and (at maturity) the r12 dcap island.
- **FENCE0 (primitive)**: p.204: matches null; if the scanner backs up through it, the match fails; first-position FENCE anchors regardless of &ANCHOR. Cell form: α pushes CHOICE{resume=scan_abort};
  γ. Any later failure pops TO IT first ⇒ scan_abort (whole-scan fail — which is also exactly the anchoring behavior, since unanchored retry lives in the BASE cell below it and is never reached).
  The s137 `mov rsp,rbp` floor-whack and its rbp-floor dependency die. NOTE — RETENTION (honest cost): the s137 OVER-SEAL existed because json-match.sno retained >32MB of committed-span ζ; under
  cells, choices left of a committed fence are unreachable-dead but unpopped until scan end. Correctness first; a FENCE-SQUASH compaction rung (fence commit slides the live mark journal down over
  the dead span) is the measured follow-up, gated on re-running the json-match measurement.
- **FENCE1 (FENCE(P) function)**: p.127: alternatives within P are visible only moving forward. α pushes FENCE cell recording entry CP; P runs, pushing its own cells; P.γ (the seal): cut rsp to the
  fence cell, relink rbp := fence's recorded prev CP — P's interior choices, windows, and retained frames die in two movs (the whack, now EXACT and floor-free) — then push nothing and continue; a
  later backtrack pops past the fence to the choices BEFORE it, per the manual. β ≡ abandon exactly as today. The [rbp+off] watermark quad and its "no fc_geom BY DESIGN" carve-out die.
- **ABORT**: p.203: immediate failure of the ENTIRE match, no alternatives, no unanchored retry (manual's '-1B-A-' example fails outright). = cut to BASE cell, jmp scan-fail exit. One label.
- **FAIL**: = jmp universal fail. **SUCCEED**: choice cell whose resume is its own α (the oscillator, p.126); the SUCCEED/ABORT/@N loop idiom from the manual falls out with zero special code.
- **DEFER (`*expr`, IR_MATCH_STAR) / PATREF (eager stored-pattern ref)** — the s200 SPLIT DIRECTIVE lands here as CELL-7, unchanged in taxonomy, changed in machinery: at match time evaluate (STAR:
  re-evaluate the expression, incl. recursion — p.85-86, p.122: recursion REQUIRES *; PATREF: one descr fetch) then enter the resulting pattern structure ON THE SAME CELL STACK. The x86_frame_sink
  window, park at [rsp+0], `mov rsp,[rsp]` release, and fc_geom's k=16 question all evaporate — there is no static reader left to protect. The s200 4-line gate reproducer (PAT=',' / S PAT) stays
  the falsifiable witness. Full re-entrancy (deferred user function running nested scans) is native.
- **SCAN BRACKET (HEAD/RELEASE, `S ? P` statement)**: the ONE real box that remains real: saves caller rbp, swaps Σ/δ/Δ in, pushes BASE cell, α(P). P.γ → scanhit: commit walk, cut to base, restore,
  statement γ. Universal fail bottoming at BASE = the Ch.18 step-6 retry (start+1, &ANCHOR runtime test — reuse SPD-2's scanfail block logic verbatim, minus the rsp=rbp floor whack). This retires
  the 42-ref PAT$ scan-retry pin (s196 "irreducible") — it was irreducible only under jmp-from-arbitrary-depth; under cells the depth ARRIVES WITH the control.

## WHAT DIES / WHAT STAYS
DIES (blob domain): op_flat_disp compensation; fc_geom grants + fc_leaf_walk prefix sums + the whole "16 short after DEFER" class (s200 root cause moot); fc_arm_member; scanbase (s196/s198);
x86_frame_sink DEFER window; ALT-FLAT quads + stubs; SEQ box + cursor slot; FENCE watermark quad + rbp floor whack; ARBNO counter + .bss depth arena; SAVE zls slot + COND cross-extent read; the
rbp-as-static-base role in blobs entirely — `flat_pat` drops out of emit_jmp_pin_rbp. STAYS: statement-level flat frames + their op_flat_disp (outside blobs, depth-static, correct); Icon generators
and the suspend pin (untouched — shared x86_asm.h additions are ADDITIVE per the keystone discipline); Σ/δ/Δ registers; the monitor; the watermark. rbp census meaning CHANGES: refs remain but every
one is CP-discipline (choice push/pop, fail stub, fence relink); the gate below makes that greppable.

## ROLLOUT — per-graph regime, never interleaved
Mixed regimes inside ONE blob re-create the disease (a cell pushed between two legacy static readers shifts their depths — the exact s188 failure shape). Therefore: a blob compiles ALL-CELLS or
ALL-LEGACY, chosen per graph by a classifier ("every construct present is converted"), env-forceable `SCRIP_CELLS={auto,0,1}` for A/B and monitor bisection. Corpus migrates construct-by-construct;
the watermark can only ratchet. Ladder (each rung: monitor-first per RULES.md, watermark re-proven, fail sets diffed programmatically):
- **CELL-0** contract landing: cell layouts, CP register ruling, x86_asm.h encoders (push_choice / fail_stub / cell tags / commit-walk helpers) — additive shared-file edit, byte-verified vs `as`.
- **CELL-1** scan bracket: BASE cell + universal fail + unanchored retry via BASE resume. Lands alone (interior boxes' ω labels point at the fail stub). Kills the scanfail floor-whack.
- **CELL-2** ALT → choice cells (delete ALT-FLAT machinery). **CELL-3** SEQ → nothing (driver aliasing; delete template). **CELL-4** ARB/BAL/ARBNO (+epsilon guard). **CELL-5** SAVE/COND marks +
  commit walk (then retire r12 island). **CELL-6** FENCE0/FENCE1 (+ FENCE-SQUASH measured follow-up). **CELL-7** DEFER/PATREF split on cells (absorbs s200 rung (a); reproducer = the 4-liner).
- **CELL-FENCE** gates: (a) grep blob templates for static frame reads against rbp == 0; (b) fc_geom/op_flat_disp callers in blob domain == 0; (c) census re-run — every surviving rbp ref classified
  CP; (d) json-match retention measured before/after FENCE-SQUASH; (e) perf labeled -O0 per the O2-DIRECTED-ONLY rule.

## RULINGS NEEDED FROM LON
1. **CP register = rbp** (proposed: callee-saved, C-call-immune, frees it from the floor role) — or spend a different callee-saved reg and leave rbp to gcc-visible framing?
2. **Cell field order** (resume-on-top pop-jmp vs ret-dispatch — s19x verdict said stack delivery unnecessary under flat arms; under cells it is natural again, but ret without call mispairs the RSB;
   propose pop-jmp).
3. **COND→mark linkage** (typed-cell scan-down vs mark-address carried in the sub-graph γ handoff).
4. **Rollout switch default** (`SCRIP_CELLS=auto` from CELL-1, or dark until CELL-4?).

## ⭐ REVISION 2 — THE BOX IS THE FRAME (Lon correction, same session): per-BB self-allocation KEPT, unified with the cells
**Supersedes above where they conflict: "match results ride registers-only", "uniform 16B walkable stack", "MARK found by scan-down", "choice cell = 16B".** The cells above are the SMALLEST boxes;
the general law is ZB-ACT (PLAN.md 2026-07-06 per-BB self-allocation, ZB-PORTS alloc flavor), now unified with CP/cut:
- **α = CALLEE-SIDE CARVE**: `sub rsp, K_box`; K_box is a BOX-LOCAL template constant (RESULT slot + LOCALS + embedded choice-cell fields for backtrackable boxes). NO graph geometry pass: zls_build
  K_total summing, fc_geom, op_flat_disp die because PLANNING MOVES FROM THE GRAPH TO THE BOX — which is precisely why EVAL/CODE (runtime-compiled statements) work: there is no compile-time frame
  plan to be missing. Recursion = fresh carve per entry (the .bss depth arenas die). K_box multiples of 16 (C-call alignment invariant).
- **ADDRESSING IS SELF-RELATIVE, ALWAYS**: own carve at [rsp+0..K); operand RESULT cells at [rsp+K..K+16n), left directly on top by the children that just ran (LIFO invariant). Static offsets
  survive SCOPED TO THE BOX, never across the graph. Reach-over stays unrepresentable.
- **γ = CALLER-SIDE FREE, two flavors**: (a) TRANSIENT: shrink-to-result — slide the 16B RESULT DESCR down over locals+consumed operands, `add rsp` → net FORTH effect ( op1..opn — result ); parent's
  consumption of the cell IS the free. (b) RETAIN: generators keep the carve (β re-enterable), CP points at the embedded choice cell; downstream unaffected (self-relative).
- **β = ARRIVE BY THE CUT**: fail stub lands rsp exactly at the box's own embedded cell, locals adjacent — self-relative at every entry mode. Frame and resume point are ONE allocation; that is WHY
  the cut works from arbitrary depth.
- **ω = CALLER-SIDE FREE WHOLESALE**: the CP cut reclaims carve + consumed operands + abandoned suffix in one mov. Both return edges free caller-side — the 4/28 one4all free-delineation, verbatim.
- **CHOICE CELL = 32B**: { resume, saved_δ, prev_CP, saved_markhead } — WAM choice point saving its trail pointer. MARK cells become a CHAIN (prev-mark link; head quad in the scan bracket): commit
  walks the chain (order fixed at CELL-5: reverse-collect or forward-append); the cut restores markhead from the choice cell, orphaning the abandoned suffix's marks WITH their memory (free-undo
  intact). Stack walkability is NOT required and NOT claimed (carves are variable-size).
- **SEQ = literally nothing** now — children's carves/frees compose LIFO around it; zero residual glue.
- SCOPE NOTE: ladder targets the SNOBOL4 blob first (CELL-1..7 unchanged, CELL-0 = ZB-PORTS alloc-flavor encoders = ZB-ACT-0, aligning with PLAN.md's stated priority sequence); statement-side and
  other languages migrate to per-box carve as the follow-on campaign (the ZB-ACT ladder proper).

## OPERAND PROTOCOL (Lon probe, same session — the responsibility flip, stated once)
OLD: producer owns its result slot at a graph-global offset; CONSUMER carries the knowledge — every operand address wired by the driver at emit time, kept honest by op_flat_disp. Knowledge O(edges),
graph-global, stale-prone (the s188..s200 class). NEW: the operand cells sit ALL TOGETHER, OWNED BY THE OPERATOR'S BOX — contiguous directly below its carve, self-relative [rsp+K..K+16n), consumed
and freed by its γ. Producers "know where to stuff" — and the answer is TOS, ALWAYS, for every box in the program: a POSITION, not an address; the FORTH contract ( — r ). Ownership transfers to the
operator BY LIFO ADJACENCY, no pointer passed. The flip therefore EVAPORATES the knowledge on both sides: no box ever holds another box's address; the driver stops plumbing operand addresses and
merely sequences emission — LIFO order IS the delivery mechanism (the child-address handoffs into `_` go dead in the blob domain). Coherent under backtracking (a half-built operand list of an
abandoned attempt is cut wholesale; the operator's body is unreachable until all n cells exist, so a partial list is unobservable) and under re-pump (a retained generator's β lands at its own
embedded cell via the cut, leaves the NEXT value at the new TOS, and the operator re-carves on top).

## ⭐⭐ DL — THE DYNAMIC LINK PAIR (added 2026-07-31, Lon directive "make it so number one"; audited at CELL-0 `63ee4164` / CELL-1a `04defc9f` HEAD)

Static edges (label/rel32, the four ports) cover targets known at emit time. Five language features carry their target as DATA and cannot ride rel32: DEFINE binds name→body AT RUNTIME (manual Ch.8 pp.102–103; RETURN/FRETURN p.103; NRETURN Ch.9 p.133 — same control shape, value protocol differs); stored patterns are pattern VALUES entered at match time; `*expr` is evaluated at match time and recurses (Ch.9 p.122); CODE()/EVAL() compile NEW graphs at runtime, entered by direct goto (Ch.9 p.130); computed goto `:($X)`. Every dynamic BB-graph invocation composes from exactly TWO shapes — the caller builds a LINK record, enters the target α through a register, and the invoked graph returns THROUGH THE RECORD, never through rel32:

**DL-ONESHOT (call-shaped: FUNCTION via IR_SAVE_RESTORE/IR_CALL; EVAL/CODE; direct goto into a code object).** The invoked graph runs to exactly one of γ/ω and its whole accumulation dies there. Caller: `x86_call_frame_enter(γ,ω)` builds the 32B record `{[+0] pad · [+8] caller rbp · [+16] γ wire · [+24] ω wire}`, rbp = the record; α entry = fetch target from data + `x86_jmp_reg` (LANDED for functions: `bb_call_proc_staged.cpp:240-243` `call rt_proc_open_fn; jmp rax`). Return from ANY depth: `x86_return_floater`/`x86_freturn_floater` — `mov rsp,rbp` cuts the whole accumulation, load wire, restore caller rbp, jmp. Nothing consumes; scope frees; the rbp-cut IS the free. ✅ **SHAPE VERIFIED BY DIRECT READ (2026-07-31, this session):** `SCRIP/seed/test_sno_stmt_frame_2.s` — ⛔ note the path, these are in **SCRIP/seed**, NOT `.github/seed` (only `test_sno_cell_1.s` was relocated there, s20x+1) — carries `lea rcx,[rip+.Lret_γ_Fr]` · `lea rdx,[rip+.Lret_ω_Fr]` · push/push/push rbp · `mov rbp,rsp`, header commented in-file as `[rbp+0]=pad [rbp+8]=caller rbp [rbp+16]=γ [rbp+24]=ω`. **THE TWO LANDING PADS ARE REAL LABELS IN THE CALLER'S OWN CODE** — Lon's description of the mechanism is the shipped shape, not an aspiration. ⚠ *"executed and oracle-checked incl. recursion + FRETURN" is INHERITED PROSE from `GOAL-SNOBOL4-BB.md` s21x-c, NOT re-measured this session* — the shape is verified, the oracle run is not.

**DL-PASSTHRU (transparent: stored/deferred pattern — the invoker forwards α→inner-α and β→inner-β; inner γ/ω forward to the invoker's own static γ/ω edges).** The inner graph SUSPENDS at γ: its cells stay on the spine (that is what a suspended alternative IS), and it deposits its own resume address into the record before jumping the γ pad; invoker-β = jmp through the deposited resume. ω = cut to the record's watermark (the whole retained subtree dies at once — the s137 OVER-SEAL fence in `bb_match_defer.cpp` is this cut, already shipped for sealed defers) then unwind. The in-graph half is LANDED: choice cell `[+0]=resume_addr` + `x86_cell_unwind_tail` (pop resume, `jmp rax`). The cross-graph half exists today as the ZS-2 jmp-entry protocol brokered through `rt_defer_step` (`bb_match_defer.cpp`/`bb_match_value.cpp` + `rtx_match.S`) — **CELL-7 rebuilds it ON this pair, it does not invent a third shape.** Embodiment: `SCRIP/seed/test_sno_cell_5.s` (recursive stored pattern; oracle claim inherited from the ladder's PRIOR ART line, not re-measured this session).

⭐⭐ **THE GAP IS NOT "NO MECHANISM" — IT IS STATE IN A C GLOBAL STACK, AND THAT IS THE WHOLE OF CELL-7's JOB (verified by direct read this session, `src/runtime/pattern_match.c:941`).** Control transfer is ALREADY template-side and already correct: `rt_defer_step` does not itself jump — it returns a frame base which `bb_match_defer` enters via `jmp rax`, the DL-ONESHOT α shape. What it *does* own is the deferred-evaluation STATE, held in the file-scope pair `g_dfx[] / g_dfx_top` (a `rt_dfx_t` stack with `->val`, `->failed`, `->dtx_used`). **That is a GLOBAL STACK holding backtrack-lifetime state — the exact shape `ARCH-ICON.md` forbids ("unbounded-depth backtrack state lives in a per-box arena indexed by depth — never a global stack"), and it is re-entrancy-hostile by construction: a deferred `*FN(T)` evaluated inside another deferred `*FN(T)` shares one `g_dfx` top.** ⚠ **THIS IS THE SAME DISEASE THE CONTRACT ALREADY NAMES ONE PARAGRAPH ABOVE, IN A SECOND LOCATION** — cf. § THE MACHINE's r12 note, *"the dcap island … which also fixes its re-entrancy hole — a deferred `*FN(T)`"*. Two independent C-side holders of pattern-recursion state, same hole, and CELL-5/CELL-7 each retire one. **The DL framing's real payoff is therefore precise: DL-PASSTHRU does not add a transfer mechanism (that exists) — it moves the state from `g_dfx` onto the ζ spine where the LIFO discipline makes re-entrancy free.** ⛔ DO NOT open CELL-7 as a codegen rung; open it as a state-relocation rung.

**THE UNIFICATION (RULING NEEDED FROM LON):** the call-frame record `{pad·prev·γ·ω}` and the choice cell `{resume·δ/tag·prev·MH}` are plausibly the SAME OBJECT — a 32B control record at rbp, newest-first chained by its prev field, discriminated by TAG. Proposal: **rbp = NEWEST CONTROL RECORD, always** (the CP=rbp ruling generalized); DL adds two tags (4=ONESHOT_LINK · 5=PASSTHRU_LINK) and the pass-thru record carries the deposited resume in `[+0]` exactly where the choice cell already keeps it. If YES, one fail-stub walk serves backtracking AND cross-graph unwind with ZERO new encoders. If NO, the two records stay siblings and only the register handshake is shared.

**REGISTER HANDSHAKE:** target address in rax at every dynamic α (the `bb_call_proc_staged` shape — keep it); &record = rbp on entry (the invoked graph stows it in its own base cell). rdi/esi keep the existing jmp-entry wire meaning (frame base, entry) until the cell regime retires flat frames.

**CUSTOMER MAP:** (1) FUNCTION = DL-ONESHOT — the IR_CALL/IR_SAVE_RESTORE protocol rung lands ON it. (2) DEFER/PATREF = DL-PASSTHRU — CELL-7's substrate. (3) EVAL/CODE = DL-ONESHOT into a mode-3 freshly-compiled island — today a plain C builtin (`lower_snobol4.c:49`/`:906` only set flags); adopts the pair LAST, after (1)/(2) prove it; needs NO new mechanism. (4) The C→graph bootstrap is the degenerate DL-ONESHOT whose pads are the driver's own labels — one shape, not a special case.

**GATES:** additive only; `SCRIP_CELLS=0` watermark byte-identical; any genuinely new encoder byte-verified vs `as` (expected count: ZERO — composition of landed primitives).
