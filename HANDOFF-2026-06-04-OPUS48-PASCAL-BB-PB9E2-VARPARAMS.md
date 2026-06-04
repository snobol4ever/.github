# HANDOFF — 2026-06-04 — OPUS48 — PASCAL-BB PB-9e-2 VAR PARAMS → CELL ADDRESSES (CLOSED)

**Session 16. Repos touched: SCRIP (code), .github (this doc + goal watermark). Corpus unchanged.**

## What closed

PB-9e-2 — var params across levels (SlotRef → cell address) in m3 `--run` and m4 `--compile`.
All six entry gates flipped FAIL→PASS vs the pcom/pint oracle in BOTH modes:
varparam **7**, swap **8/3**, alias **11**, varframe **107/7**, varmix **6**, vartrans **15**.

## The design pivot (read this before trusting PB-9E-DESIGN.md on this rung)

PB-9E-DESIGN.md assumed the var-param probes ride the PB-9e-1 frame substrate. They DON'T as written:
**all six probes are FLAT programs** — first-level procs carry `decl_level=1` (parser stores the level
AFTER `pas_proc_enter()` from a base of 1... net effect: only second-level-and-deeper procs exceed 1), so
the `decl_level>1` migration trigger never fired for them, and main-level vars are NV globals with no
frame cell at all. Two consequences drove the landed design:

1. **Migration trigger extended**: `decl_level > 1 || byref_mask != 0` (lower_program.c, the
   `pas_has_nesting` scan). Var-param programs now migrate program-wide (main still skipped/unmigrated,
   exactly as PB-9e-1 chose). Flat-no-varparam programs untouched BY CONSTRUCTION — proven by `cmp` on
   emitted .s pre/post: Pascal `sieve.s`, SNOBOL `hello.s`, SNOBOL `083_define_simple_return.s` all
   byte-identical.
2. **NV globals get stable cell addresses**: NEW `DESCR_t *rt_gvar_cell(const char *name)` in rt.c —
   a thin wrapper over the PRE-EXISTING `NV_PTR_fn` in core.c (find-or-create; chained hash buckets,
   entries GC_malloc'd and never moved → `&e->val` is stable for process lifetime). No new storage model.

## Mechanism

- **IR**: `IR_VAR_FRAME_REF` / `IR_ASSIGN_FRAME_REF` before IR_OP_COUNT (IR.h; names in scrip_ir.c).
  Same fields as the non-REF kinds (ival=slot, dval=hops, sval preserved); semantics = ONE extra pointer
  indirection — the frame slot holds the ADDRESS of the actual cell, not the value. Language-blind: any
  reference-parameter language can lower onto them.
- **LOWER** (lower_program.c): `pas_scope_chain` grew a `pis[]` out-array (proc index per chain level);
  `pas_rewrite_node` resolves name → (slot, hops) as before, then
  `isref = slot < proc_table[pis[c]].nparams && (byref_mask >> slot) & 1` selects REF vs plain kinds.
- **Runtime** (rt.c/rt.h): `rt_proc_t` grew `uint64_t byref_mask` (init 0 in BOTH new-entry branches —
  register AND set_fn); `rt_proc_set_byref` / `rt_proc_byref_mask`; `rt_gvar_cell`.
  **`rt_call_named_proc_sl` is UNCHANGED** — the marshal writes {tag 0, ptr} into the arg DESCR and the
  verbatim 16-byte slot copy forwards it. No runtime ABI change; m4 startup emission unchanged (the mask
  is EMIT-TIME-ONLY knowledge).
- **Driver** (scrip.c): both build spots (m3 ~line 1357, m4 ~line 1070) call
  `rt_proc_set_byref(pname, proc_table[_pi].byref_mask)` right after the set_frame line, so the emitter's
  emit-time queries see the mask before any chain build.
- **Call site** (bb_call.cpp): NEW `marshal_varparam_addr(lf, aoff, idx)` + NEW `bcall_fr_lea64` byte
  helper (REX.W 8D, [base+disp32]). Branched per-arg on `rt_proc_byref_mask(fn)` in BOTH userproc marshal
  loops (TEXT + BINARY) and the nested-call arm (which queries the inner callee's mask). Arg shapes:
  - `IR_VAR_FRAME` → hop chain + `lea rax,[base+16+slot*16]` (address OF the slot);
  - `IR_VAR_FRAME_REF` → hop chain + `mov rax,[base+16+slot*16+8]` (FORWARD the stored address —
    the transitive vartrans case);
  - `IR_VAR` → `rt_gvar_cell` (@PLT in TEXT, fptr in BINARY);
  - anything else → `x86_bomb` (var-param arg must be a variable).
  Also: value-marshal arm for IR_VAR_FRAME_REF (writeln of a ref var — ungated, added for completeness);
  inline-binop arm accepts REF operands (load addr from slot+8, then value from [addr+8]).
- **Templates**: NEW `bb_var_frame_ref.cpp` (hop, load cell addr from `[base+voff+8]`, copy DESCR through
  it into own slot) and `bb_assign_frame_ref.cpp` (same `hop` prologue + addr load into rcx; all stores go
  `[rcx+0]/[rcx+8]`; rhs arms LIT_I/LIT_NUL/LIT_S/IR_VAR/IR_VAR_FRAME/IR_VAR_FRAME_REF/IR_BINOP/IR_CALL,
  else bomb). Plain `bb_assign_frame.cpp` grew an IR_VAR_FRAME_REF rhs arm (`t := x` in swap, x byref).
  Both `bb_binop_gvar_{arith_slot,relop}.cpp` slot_disp functions accept the REF kind (+8 — the REF box
  deposits a full dereffed DESCR in its own slot, so binop consumption is identical to VAR_FRAME).
- **emit_bb.c**: flat-drive cases (REF kinds ride the same FILL / flat_drive_gvar_assign[_binop] paths);
  descr_chain_arity lists (REF read → 0, REF assign → 1). **emit_core.c**: two dispatch cases.
- **m2** (IR_interp.c): REF kinds are ADDITIONAL CASE LABELS on the existing FRAME arms — the slotref
  machinery set up at call time already performs the indirection, so no new m2 code paths. The byref
  slotref seeding check accepts `IR_VAR_FRAME_REF` arg entries (m2 transitivity).
- **Makefile**: explicit compile rules for the two new templates (link is the $(OBJ) glob, but compile
  rules are explicit — same landmine as session 15).

## Gates (all verified this session)

- m3 var-param six: 6/6 PASS byte-identical vs oracle (values above).
- m2+m3 combined regression: **15/15** (the six + nestrec/nestshadow/nest2/nested/nestcount/nestfunc +
  hello/flatnoarg/sieve, each diffed against fresh pcom+pint oracle output in both modes).
- recursion fact-7 m3 line `7 5040 13` intact.
- m4 `--compile` (gcc -no-pie + out/libscrip_rt.so): **7/7** — six var-param probes + nestrec.
- SNOBOL4 canonical smoke: **19/0** (m2 7/0, m3 6/6, m4 6/6).
- Byte-identity: `sieve.s` / `sno hello.s` / `083_define_simple_return.s` cmp-identical pre/post.

## Landmines for the next session

- `marshal_varparam_addr` walks the arg subgraph to its FINAL node (γ-chase, 256 cap) before shape
  dispatch — same idiom as the inline-binop arm. A single var node is its own final; do not "simplify"
  the walk away, deferred-init prologue chains depend on it.
- The {tag 0, ptr} encoding in a var-param arg slot is indistinguishable from NULVCL+garbage if printed —
  if a debug path ever prints arg DESCRs raw, byref slots will look like nulls. The REF templates are the
  ONLY legitimate readers.
- `rt_proc_byref_mask` returns 0 for unknown/unset procs → every non-Pascal language and every flat
  Pascal program takes the old marshal path verbatim (that is the byte-identity proof's mechanism).
- m2's REF arms rely on the slotref seeding having run (registered-proc call block). If a future rung
  routes m2 calls around that block, the REF case labels alone will NOT indirect.
- Cross-language full matrix (Icon/Prolog/Raku smokes) NOT re-run this session — SNOBOL 19/0 + the three
  .s byte-identities are the drift proof; bb_call.cpp shared-path edits are mask-gated to 0 for them.

## NEXT

Per GOAL-PASCAL-BB.md ladder: PB-9e is now fully closed (9e-0/1/2/3 all [x]). Next frontier per the goal
file: the known deeper m3/m4 walls — rec2/ptr5 segv at record-field/heap `__pas_*` arms (stash-proven
never-passing, NOT regressions), and LB-7-NEW remains parked on ICN-SCAN. Nested variants of the var-param
probes (varparam/swap inside nested procs at depth ≥2, exercising hop>0 LEA paths) would make a cheap
hardening rung: the mechanism supports them (hop chains are emit-time-constant) but only hop==0/1 shapes
are gate-covered today.
