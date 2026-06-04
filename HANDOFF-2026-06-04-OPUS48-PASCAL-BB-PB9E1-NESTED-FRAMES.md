# HANDOFF — 2026-06-04 — OPUS48 — PASCAL-BB PB-9e-1 NESTED FRAMES + STATIC LINKS (CLOSED, + PB-9e-3)

**Commits: SCRIP `bd79c8b`, .github `23022d4b` (goal watermark = session 15). Corpus unchanged. All pushed.**

## What closed

PB-9e-1 (SL plumbing + nested locals/params → frame slots) and, by the same mechanism, PB-9e-3
(nested functions under recursion — per-activation fb makes the recursion clobber structurally impossible).
Forks decided per delegation: **(A) program-wide nested-only migration** — if ANY proc has decl_level>1,
ALL procs in that program migrate to frame slots; flat programs untouched BY CONSTRUCTION.
**(B) explicit `rt_call_named_proc_sl(name, args, nargs, void *sl)`** — fb[0]=SL, slots seeded
params-then-NULVCL for k < max(frame_nslots, nparams), funcname NV-save only, result via NV_GET.

## Gates (all verified this session)

- m2 `--interp`: **36/0 + recursion XFAIL** with the rewrite LIVE (nested programs run through the new IR kinds).
- m3 `--run` vs pcom/pint oracle: nestrec **11/21/31**, nestshadow **7/101**, nest2, nested, nestcount,
  nestfunc — ALL PASS; flat hello/flatnoarg/sieve PASS; recursion fact-7 line `7 5040 13`.
- m4 `--compile` (gcc -no-pie t.s -L SCRIP/out -lscrip_rt -Wl,-rpath,... -lm): same six nested probes PASS
  end-to-end, plus flat hello/flatnoarg/sieve and recursion fact-7. Runtime lib: `make libscrip_rt` → `out/libscrip_rt.so`.
- Byte-identity stash-proofs: Pascal `sieve.s` and SNOBOL `hello.s` `cmp`-identical pre/post (also re-proven
  after the 200-col line splits). Var-param m3 outputs byte-identical pre/post. SNOBOL m3 19-program ad-hoc
  pattern identical pre/post (5 pass / 14 pre-existing fails in that set — NOT the canonical 19/0 smoke set; don't panic at it).

## Mechanism (detail in goal watermark + PB-9E-DESIGN.md)

- IR: `IR_VAR_FRAME` / `IR_ASSIGN_FRAME` before IR_OP_COUNT in `src/contracts/IR.h` (ival=slot, dval=hops,
  sval preserved); names in `scrip_ir.c`.
- LOWER (`lower_program.c`): helpers `pas_scope_chain`/`pas_rewrite_node`/`pas_rewrite_graph` ABOVE `lower()`;
  migration pass inside the LANG_PASCAL block before `g_stage2.lang = IR_LANG_PAS;`. Walks the lexical chain
  via proc_table decl_levels (skips entries named "main"), recurses into IR_CALL dval 2.0/3.0 arg subgraphs,
  idempotent. **Marker: `IR_graph_t.nslots` with +1 encoding — 0 = unmigrated, k+1 = migrated with k slots.**
- m2 (`IR_interp.c`): arms before `case IR_SWAP:` hop `GenFrame.static_link`, pas_slot_read/write via ring
  peek; byref check extended to accept IR_VAR_FRAME.
- Runtime (`rt.c`/`rt.h`): rt_proc_t + `frame_nslots` (−1 = unset, initialized in BOTH new-entry branches —
  rt_proc_register AND rt_proc_set_fn) + `decl_level`; rt_proc_find/set_frame/frame_nslots/decl_level;
  rt_call_named_proc_sl.
- Emitter: `emit_bb.c` arity (VAR_FRAME→0, ASSIGN_FRAME→1), walk_bb_flat cases, both gvar builders reserve
  `g_flat_slot_count = 16 + (nslots−1)*16` when nslots>0, global `int g_emit_frame_caller_dl = -1`.
  `emit_core.c` dispatches to the two new templates.
- Templates: NEW `bb_var_frame.cpp` / `bb_assign_frame.cpp` — local byte helpers fr_load64/fr_store64/
  fr_store_imm ([base+disp32], bases rax/rcx only — r12 base would need SIB so chains start with
  `x86_frame_lea(reg, 0)`); hop chains at emit-time-constant depth. ASSIGN_FRAME rhs shapes: LIT_I, LIT_NUL,
  LIT_S, IR_VAR (NV global — call rt_gvar_get_descr FIRST, then hop, rcx is caller-saved), IR_VAR_FRAME,
  IR_BINOP (raw qword at op_a_slot → tag6), IR_CALL (DESCR at op_a_slot); **else x86_bomb — IR_SEQ
  concat-into-frame-var is a known loud gap.** gva/gvr_slot_disp in both binop templates +8 for IR_VAR_FRAME.
- bb_call.cpp: pas_sl_setup (h = caller_dl+1 − callee_dl, caller_dl<0 or callee_dl<1 → mov32 ecx,0);
  SL wired into direct gvar userproc call (TEXT @PLT + BINARY fptr switch), marshal nested-call arm,
  NEW marshal IR_VAR_FRAME arg arm, inline-binop α/β frame-operand loads.
- Driver `scrip.c`: m3 non-icon loop — rt_proc_set_frame + g_emit_frame_caller_dl around each
  gvar_flat_chain_build, reset −1 after. m4 block — same around gvar_flat_chain_build_text per proc;
  sno_proc_startup emits `rt_proc_set_frame@PLT` (lea rdi .Lsno_pnN / mov esi nslots / mov edx dl) per
  migrated proc after the register/set_fn pair.
- Makefile: explicit compile rules for the two new templates (link is `$(OBJ)/*.o` glob; the SRC list at
  ~96-128 is NOT the build driver).

## Landmines for the next session

- Single-pass register+build in m3 is order-safe ONLY because the parser emits procs post-order and Pascal
  forward bodies are ignored; a self-call registers in the same iteration before its own build.
- `rt_proc_t *p = &g_rt_gen_procs[...]` appears TWICE in rt.c — anchor edits on the full field-setting lines.
- bb_call.cpp has ONE pre-existing >200-char line (the `a0->t == IR_NEG || ...` condition list) — left alone.
- bb_binop_gvar_relop.cpp uses `gvr_` prefix, arith uses `gva_` — easy grep miss.
- DESCR tags: 6=int, 7=real, 1=string, 0=null; NULVCL in IR.h.

## NEXT: PB-9e-2 — var params across levels (SlotRef → cell address)

Var params have NO m3 mechanism at all. Entry gates, all currently FAIL m3 (stash-proven pre-existing,
oracle expected → current m3): varparam **7**→5, swap **8/3**→3/8, alias **11**→0, varframe **107/7**→7/7,
varmix **6**→1, vartrans **15**→4. m2 handles these via the SlotRef byref machinery in IR_interp.c (now
IR_VAR_FRAME-aware); m3/m4 need cell addresses — frame slots give every local a stable
`fb + 16 + slot*16` address for the activation's lifetime, which is exactly the substrate PB-9e-2 needs.
Then PB-9e-4+ per GOAL-PASCAL-BB.md.
