# HANDOFF — BB-FIXUP 19th attended run (Opus 4.8), 2026-06-07
**Run record: LAP 2 stops bb_term_io + bb_to under NINE concurrents across five push races, including a mid-stop rewrite of the active stop file — the race-heaviest run of the goal.**

## STOPS
### bb_term_io.cpp → b8e3a04 ✅ 115→17 (the 6th-run RESET redo under corrected rule)
- ef 23→0 (emit_fmt→to_string/concat, string-identical incl. the no-qword-ptr `"[rsp + 0], rax"` kept verbatim) · pe 3→0 (Greek glyphs) · lv 26→0 (btio_* per-arm helpers; signature-line btio_lbl decls preserve strtab intern order per the 16th-run finding; dead succ_back local excised — pure-formatter, dead-nid precedent)
- rb 43→3: ALL FOUR MEDIUM_BINARY arms (numbervars / term_to_atom|term_string / format-PathA / format-PathB) bytes()→x86(); ZERO new encoders — every form re-byte-verified at source this head: movabs rsi=48BE rcx=48B9 rdx=48BA r8=49B8 r9=49B9 rax=48B8 · mov32 edx=BA esi=BE edi=BF r8d=41B8 · xor ecx=31C9 eax=31C0 r8d=4531C0 · mov-rr rdi←rax=4889C7 r8←rax=4989C0 · RSP(0) store=48890424 · call_ro=48B8+imm64+FFD0 · REX.W sub/add rsp 8+16 · test=85C0. Residual rb=3 = honest [S] x86_lit_bytes( bridges around emit_term_from_node_bin (audit substring artifact).
- PROOF: (1) standalone A/B harness vs the REAL x86_asm.h (/tmp/btio_h/harness.cpp; CXXRT flags + -I src/emitter/BB_templates; link /tmp/si_objs/emit_str.o + stubs g_emit/g_medium/rt_bomb; TERM() 4-byte marker identical both sides; fixed fake fn addrs + fake s-pointers; stripL walks L/J/D records) — ALL 12 BRANCH SHAPES BYTE-IDENTICAL FIRST PASS (nv×2 s2-present/NULL, tta×2, fb×2, fa×6 = s0{p,0}×a1{p+s1, p+0, NULL}); the 18th-run parameterize-both-sides lesson held. (2) asm-diff EMPTY ×5 three-pattern normalized (bbN + RESOLVE + .LcallN) vs EACH raced head. (3) ALL FIVE TEXT arms LIVE — probe shapes: `numbervars(foo(X,Y),0,E)` / `term_to_atom(foo(a,b),A)` / `format("hi~n")` (PathA null-store) / `format("~w~n",[42])` (PathB) / `format("~w~n",ok)` (PathA atom-lea); all `:- initialization(main, main).` + `main :- Goal.` shape. (4) behavior A/B identical ×15 + re-runs per raced head (m3 rc=134 pl_gz fence abort identical both sides). medium-invisible DELISTED 43→0. [S] nw=14 stands (a0/a1/a2->t kind reads; LOWER design unpinned; rise 8→14 = de-aliasing honesty).

### bb_to.cpp → 0152e23 ✅ v2 9→0, TICKED
ef 1→0 · pe 3→0 · lv 5→0 (lo/hi/off/cur → _.op_* inline at FRQ sites; is_by/by → bto_by() pure helper; step ternary → complementary lazy-IF pair, bb_scan_tab precedent; merged admission guard; bomb-in-_str + zero-local wrapper, gen_scan precedent). Zero intern sites — splice-free, no FOR ladder needed. asm-diff EMPTY ×2; TO box LIVE with BOTH step arms fired (`every write(1 to 3)` → inc arm; `every write(1 to 7 by 2)` → add arm); behavior A/B identical ×6, m4 LIVE 1-2-3 / 1-3-5-7.

## THE RACE STORY (the run's defining material)
Nine concurrents absorbed, all with per-head re-certification (8th-run precedent):
1. **6e3cb1e IRD-3d-CHAIN-CONSUMERS-CORE** + **470cdd0 -TEMPLATES** raced the FIRST bb_term_io push. ⛔ 470cdd0 REWROTE THE ACTIVE STOP FILE (γ-chain reads → ir_call_arg, 10 templates). NEW RACE CLASS + ITS RECIPE: rather than law-4-skip a fully-proven stop or stale-base clobber it (the da96b66 lesson), the fixup commit was RESET (git rebase --abort → reset --hard origin), the regeneration RE-DERIVED on the rebased head with the concurrent's shape applied VERBATIM (guards+aliases → ir_call_arg(pBB,0/1/2); format's a1=a0->γ hop kept exactly as theirs kept it), and ALL proofs RE-RUN vs the new A-side. eb 12→0 arrived via their conversion riding the regeneration. The byte harness needed NO re-run (emission sequences untouched by read-conversion) — stated, not assumed: asm-diff ×5 EMPTY vs the new head confirmed.
2. **9134387 IRD-3d-CHAIN-WRITERS-FLIP** raced the second push → re-certified; surfaced the format/2 m2/m4 divergence (below).
3. **e7e1e22 + 415e465 + 28dad0b** (pair consumers/writers/catch — IRD-3d COMPLETE) raced the third push; touched bb_is_cmp/bb_succ_plus/bb_resolve, not the stop.
4. **5334ead IRD-3e icon four-kinds** at the bb_to open (touched bb_every).
5. **07698c7 + 27c797f B0 PATND-DELETE** raced the bb_to push (runtime/contracts).
6. **3cedeea IRD-3d-FOLLOWUP** raced the bb_to re-push — see FLAG RESOLUTION.

## FLAG RAISED → TRIAGED → RESOLVED (within ~40 min, same night)
At 9134387 the run flagged (law 5, tracker note): `format("~w~n",[42])` prints 42 m2 but EMPTY m4 — proven inherited (identical with/without the fixup edit), candidate one-liner named (a0->γ → ir_call_arg(pBB,1)). **3cedeea applied exactly that one-liner AND corrected the root-cause**: pristine pre-session build (6e3cb1e~1) reproduces the m4-empty — compound format/2 was NEVER admitted by the gz/flat native tiers; the hop was LATENT, the divergence PRE-EXISTING (this run's 42-at-470cdd0 observation was a transient of that head; both observations true at their respective heads). Flag RESOLVED; replaced by its backlog item: **compound-format/2 native-tier admission, owner admission layer** (fence-era backlog per 3cedeea). Lesson banked: a pre-flip behavioral observation at one raced head is not a pre-existing-baseline proof — the pristine-worktree reproduction is.

## ERRATA / LESSONS THIS RUN
- Mid-stop file rewrite by a concurrent: RESET + RE-DERIVE + RE-PROVE recipe above (first landed use).
- The sh-vs-bash process-substitution failure in the normalizer one-liner → temp-file diff form used throughout.
- First harness compile appeared to fail (warnings-only output raced the ls) — recompile confirmed clean; check the .o, not the log tail.

## STATE AT CLOSE
- SCRIP @ 0152e23 (fixup work) verified local==origin at close; b7a2717 (B0b) landed post-close, pulled, nothing of fixup's outstanding.
- Close rank at extension end: 31 dirty / 75 clean; emit-blind 235→119 ring-wide (IRD-3d's ir_call_arg conversion collapsed the direct-read class); rank totals moved −208 across the run (fixup −95, IRD burst de-aliasing −113ish — the N-generate/ONE-clean dynamic both directions).
- Gates at floors on every pushed head: smoke m4 7/7 HARD · pat M4=18 (053 pre-existing SKIP) · icon m2 12/12 HARD m3=m4 10/12 (pre-existing) · pl smoke m2 5/5 HARD m3=m4 3/2 · purity 2-floor · bin_t 0 · vstack 3 · sno_pat_reg HARD · handencoded 0 · prove 68 PASS + 3 inherited FAIL (law-5 trio unchanged).

## CURSOR + NEXT SESSION
`# CURSOR: bb_type_test.cpp` — rb=15 + ef=8; the conversion recipe is six-times-proven (aggregate_nb/atom_string/findall/succ_plus/term_inspect/term_io). ⛔ HOT-CHECK ON ARRIVAL: IRD edits touched bb_type_test ~22:2x UTC 06-07 (470cdd0 class) — window to ~04:2x UTC 06-08; also bb_is_cmp/bb_succ_plus/bb_resolve HOT from the e7e1e22/415e465 burst to ~04:4x. Behind it bb_unify/bb_unop/bb_var* close LAP 2. After the lap: FIX-4 (gvar 3c capture) → FIX-3 family (bb_return op_sa model, per-member design calls) → bb_resolve dedicated TIER S session.

## OUTSTANDING VERDICTS (6)
x86_movimm uint32-truncation (bb_call_fn) · RING/DIRECTORY RECONCILE (dir vs tracker vs rank counts) · prove rc=0-on-FAIL hardening · PL-GZ-8 arith-is 2-vs-5 (owner PL-GZ) · m2 disj-backtrack silent-empty (owner PROLOG-BB) · IRD-2b IR_t.own DEVIATION ratification. (The format/2 flag is RESOLVED — its successor item is the admission-layer backlog above, not a fixup verdict.)

No LADDER rungs closed (FIX-1 standing; nothing deleted per handoff rule 1).
