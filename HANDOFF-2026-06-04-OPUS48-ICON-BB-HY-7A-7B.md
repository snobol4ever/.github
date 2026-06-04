# HANDOFF 2026-06-04 OPUS48 — ICON-BB: ICN-HY-7a + ICN-HY-7b (bb_call-family hygiene)

**HEAD (SCRIP) = `000158f`** (rungs `6764f03` HY-7a, `000158f` HY-7b; clean rebases over Prolog peers
`6f69e3f` PL-GZ-3b and `20f15db` PL-GZ-4a, merged-HEAD re-verified each). **HEAD (.github) = this handoff +
the GOAL-ICON-BB.md watermark/step update.**

## What landed

### HY-7a (`6764f03`) — shared encoders; raw-byte + no-stack debt cleared
- `x86_asm.h` gains FOUR shared encoders (additive, one place — the FACT rule's "the missing encoder is the
  bug" remedy): `x86_reg_disp32_load64(dst,base,disp)` (`mov dst,[base+disp32]`),
  `x86_reg_disp32_store64(base,disp,src)`, `x86_reg_disp32_store_imm64(base,disp,imm)`,
  `x86_reg_disp32_lea64(dst,base,disp)`. Byte-for-byte the same REX/opcode/ModRM/disp32 logic the deleted
  locals produced — byte-verified BY the corpus identity (m3 BINARY arm) + m4 (TEXT arm).
- DELETED the five per-file `x86_Lrec`+`u32le` local helpers: `bb_call.cpp` `bcall_fr_load64`/`bcall_fr_lea64`;
  `bb_var_frame.cpp`/`bb_var_frame_ref.cpp` `fr_load64`; `bb_assign_frame.cpp`/`bb_assign_frame_ref.cpp`
  `fr_load64`/`fr_store64`/`fr_store_imm`. All call sites → the shared encoders.
- **medium-invisible 363→343**: bb_call(4) + the SHARED frame family(16) are OFF the strict list. Every
  remaining site is the documented Prolog-lane `bb_builtin_*` WIP. The Icon lane reads ZERO.
- `rt_pop_write_int_nl`/`rt_pop_write_any_nl` ERADICATED from templates: `bb_call_write_legacy_str` →
  `x86_bomb("…awaits bb_var tier")`. Rationale: the rt targets are STACKLESS_ABORT stubs (rt.c:229/234), and
  every shape that routed there (write of a non-slot arg, e.g. `write(x)` for an unslotted var) EXCISES
  `[SMX]` pre-emission today — verified live. Dead path either way; now it is loud and stack-free.
  **icn_no_stack gate 10→0 — the GROUND ZERO 3 target is REACHED for the entire Icon emission path.**

### HY-7b (`000158f`) — bb_call-family pBB purity
- ALL SIX files read only `_`: bb_call 17→0 · bb_call_proc_staged 3→0 · bb_call_write_slot 2→0 ·
  bb_call_userproc 2→0 · bb_call_builtin 2→0 · bb_every 2→0.
- Two prologue carriers ADDED (`walk_bb_node` + `g_emit`): `op_dval`, `op_counter` (the existing
  `op_a_counter` precedent; IR_t.counter is int64_t, types match).
- Mapping used: `pBB->sval/ival/dval/counter` → `_.op_sval/_.op_ival/_.op_dval/_.op_counter`;
  `bb_node_id(pBB)` → `_.nid`; pointer-needing sites (`bb_slot_alloc16(pBB)`, marshal owner arg, `pBB->α`) →
  `_.node` (the bb_return.cpp precedent). Nested-call recursion inside `marshal_call_arg` (`lf->*`, `fin->*`)
  untouched — those are PARAMETER reads of operand subgraph nodes, i.e. the fusion item, not pBB reads.

## Transferable lessons
1. **STRUCT-LAYOUT HAZARD:** the two carriers were inserted MID-STRUCT in `g_emit` → field offsets after the
   insertion shift in every TU → any stale `.o` is SILENT memory corruption. This rung did
   `rm -rf /tmp/si_objs` + full clean rebuild of scrip AND `make libscrip_rt` (touch a template to force the
   monolithic .so rebuild) and re-gated. Future carrier additions: append at struct END, or always
   clean-rebuild both targets.
2. **FLAT-PATH PROLOGUE PROOF:** `FILL(nd,…)` (emit_bb.c:240) calls `walk_bb_node(nd,…)` — the prologue runs
   before EVERY template in BOTH dispatch paths (tree + flat-chain), so `_.op_*` carriers are always fresh
   for the dispatched node. The pBB→carrier migration class is safe by construction; verified empirically by
   corpus zero-drift.
3. The HY-7 baseline's "MEDIUM_TEXT/else pairs ~122-123/136" in bb_call are the marshal gvar-read sites:
   TEXT `lea rdi,[rip+label]; call f@PLT` vs BINARY baked-pointer load + call — two encodings of ONE logical
   load+call, the sanctioned per-medium difference (the goal's own `call foo@PLT` example). The gate agrees
   (bb_call now 0). Do not chase them.

## Gate record (held at BOTH rungs + post-rebase)
corpus ALL THREE columns byte-identical zero drift: m2 **129 HARD** / m3 **18** PASS+147 EXCISED / m4 **25**
PASS+86 EXCISED (full `test_icon_rung_suite.sh` at each rung; m2-only re-check after each rebase). Smokes:
Icon m2 12/12 HARD · m3 5/12 · m4 5/12; Prolog m2 5/5 HARD · m4 5/5; broker 32. Scan fence composite PASS
(28/28 probes; bucket N=47 at floors 31/7/7). Structural: bb_bin_t 0 · handencoded `--strict` 0 ·
one-reg-frame 0 · **icn_no_stack 0** · g_vstack 3 standing · prove_lower2 PASS · FACT
bytes-outside-templates 0.

## NEXT
- **HY-7 remaining = the marshal DUP-FORM-3 fusion** (`marshal_call_arg`/`marshal_varparam_addr` operand-kind
  reads). BLOCKED on the standing lowerer PREREQ: make literal operands producer boxes (the GZ-3/GZ-4 class)
  — a LOWERER rung first, then delete the operand-kind arms in favor of slot reads.
- **ICN-HY-FENCE** (extend the PROLOG-SCOPED `scripts/test_gate_bb_one_box.sh` file set to Icon) FOLLOWS the
  fusion fix or arrives RED.
- **Or jump to the bb_var tier** — still the largest single unblock: SCAN-13b native, var-subject scans
  (`s ? …`, hence every desugared `?:=`), and the relop/if/while/until control cluster (8 kinds, zero working
  native shape).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
