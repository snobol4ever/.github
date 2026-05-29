# HANDOFF — 2026-05-28 — Opus 4.7 — IBB-4 rename + flat_drive_every WIP

**Repos touched:** one4all (single-repo session).
**Gates at handoff:** smoke_icon 5/5 · smoke_prolog 5/5 · smoke_raku 5/5 · smoke_snobol4 13/13 · smoke_unified_broker 39/14 · Icon corpus mode 2 PASS=200/47/36/283 unchanged · FACT 0.
**Canonical-5 mode-3 score:** 2/5 (unchanged from session start — hello.icn ✅, add.icn ✅; every_to.icn / alt.icn / full.icn still failing, but the failure surface has shifted forward — see "where the bug is" below).

---

## Three landed changes (clean, atomic value independent of the WIP)

### 1. `bb_icn_to.cpp` → `bb_to.cpp` (per Lon directive: BB_*/SM_* opcodes and templates are language-independent)
- `git mv src/emitter/BB_templates/bb_icn_to.cpp src/emitter/BB_templates/bb_to.cpp`
- `bb_icn_to_str` → `bb_to_str`, `bb_icn_to` → `bb_to`
- File-header comment rewritten to reflect language-independent posture (BB_TO is the counted-integer generator opcode; today only Icon's lower produces it but the opcode itself carries no language identity)
- Header decl in `bb_templates.h` updated: `void bb_to(BB_t *);`
- `emit_core.c:585` dispatch: `case BB_TO: bb_to(nd);`
- `Makefile` source list and compile recipe updated
- Stale comments in `bb_binop_gen.cpp` and `bb_to_by.cpp` updated to refer to `bb_to`

### 2. `bb_icn_stub.cpp` deleted (was redundant with `bb_stub.cpp`)
Both files were functionally identical no-op stubs. `bb_icn_stub` had exactly ONE call site: `emit_core.c:619` in the BB_SEQ_GEN dispatch. Now routes to the equivalent existing `bb_stub`.
- File deleted via `git rm`
- Header decl removed from `bb_templates.h`
- `emit_core.c:619` calls `bb_stub(nd)`
- `Makefile` source list and compile recipe entries removed

### 3. `BB_ALTERNATE` removed (per Lon directive: check if used, remove if not)
**Found zero `BB_node_alloc(*, BB_ALTERNATE)` call sites anywhere in `src/`.** The one case body in `bb_exec.c:1862-1864` was unreachable (a placeholder returning FAILDESCR). All remaining references were in dispatch fall-throughs and "is this a generator kind?" predicate lists. Removed from:
- `src/include/BB.h` (enum)
- `src/lower/scrip_ir.c` (`kind_names[]` table)
- `src/lower/bb_exec.c` (case body, two macros `ALT_IS_GEN`/`IR_IS_GEN_KIND_TO`, `bb_is_gen_kind_raw`, `ir_is_single_shot` switch)
- `src/lower/lower_icn.c` (`lic_gen_kind_raw`, `icn_kind_is_resumable`)
- `src/emitter/emit_core.c` (case fall-through under bb_limit, `bb_is_generator`)
- `src/emitter/BB_templates/bb_binop_gen.cpp` (`operand_is_gen` switch)
- `src/tools/emit_per_kind_audit.c` (audit table entry)

Note: enum-value shift. Every enum after `BB_CONJ` (index 16) is now one lower than before. Affects only the raw-int diagnostic dumps; nothing in source compares against numeric values.

---

## In-flight WIP — `flat_drive_every` + BB_TO/BB_ALT routing through BB_CALL

### What works
- `flat_drive_every` added to `emit_bb.c` (driver covers the ival=0, β=NULL shape used by `every <body>` where the generator lives inside body, like `every write(1 to 3)`)
- `walk_bb_flat`'s `BB_EVERY` arm now calls `flat_drive_every` (was abort)
- `walk_bb_flat`'s `BB_CALL` arm shape-dispatch widened: arg0 kinds `BB_TO` and `BB_ALT` route to `flat_drive_call_intexpr` alongside `BB_BINOP`/`BB_LIT_I`
- `bb_call.cpp` int_expr-trailer is_write_intexpr predicate widened similarly
- `bb_call.cpp` int_expr-trailer β-stub now jmps to the **driver-queued β-target** (was always lbl_ω). When called from `flat_drive_call_intexpr`, the queue carries `(define=lbl_β, jmp=arg_β)`, so the call's β chains back into the arg's β — necessary for BB_EVERY's re-pump to cascade through BB_CALL into its generator arg
- `flat_drive_call_intexpr` now does `EMIT_PAIR_DEF_JMP(lbl_β, arg_β)` (was `EMIT_PAIR_DEF_JMP(lbl_β, lbl_ω)`)
- `bb_every.cpp` MEDIUM_BINARY arm implemented as a pair-driven emit (mirrors `bb_pat_alt.cpp` style; iterates `g_emit.xa_bb_emit_pair_*[]`). Was an abort stub.
- `bb_to.cpp` MEDIUM_BINARY yield rewritten to use `rt_push_int` instead of r12-ring (r12 isn't initialized by XA_FLAT_PROLOGUE, so the prior 18-byte r12-push would have segfaulted; replaced with 15-byte `mov rdi, rcx; movabs rax, &rt_push_int; call rax` — same convention as `bb_lit_scalar` BB_LIT_I arm). Adds `void rt_push_int(int64_t);` to bb_to.cpp's extern "C" block.

### Where the bug is

every_to.icn (`every write(1 to 3)`) reaches the BB_EVERY → BB_CALL → BB_TO driver chain, the bytes emit successfully, mode 3 executes, prints `1`, then SM value stack underflow. The slab byte-level investigation pinned it precisely:

> The bb_to.cpp MEDIUM_BINARY `bin` field has sites listed in **NON-ascending** order: `{fail_off+2 (=64), succ_off+1 (=84), back_off (=19)}`. The patching loop in `bb_emit_asm_result` (`src/emitter/emit_str.cpp:70-77`) assumes ascending order — it emits bytes from `pos` up to `bin.sites[i]` then defines/patches at that offset. With sites out of order, by the time we reach the `back_off=19` DEFINE site, `pos` is already 88 (past the end of BB_TO's bytes), so the inner `for (; pos < bin.sites[i]; pos++)` loop doesn't execute and `bb_label_define(arg_β)` fires with `bb_emit_pos == end_of_BB_TO == 0x6B`. Hence `arg_β` resolves to address 0x6B (= `arg_done`'s position) instead of 0x26 (the actual β-re-entry instructions).

The trailer's `jmp arg_β` lands on the trailer's own first instruction (= arg_done = `movabs rax, &rt_pop_write_int_nl`), so on each re-pump we just re-run pop+print without an intervening rt_push_int. After the first iteration pops the lone "1" off the vstack, the second pop underflows.

**The fix** (NOT yet applied — handoff stops here): reorder bb_to.cpp's `bin` so sites are ascending. Either:
- `bin = { {back_off, fail_off+2, succ_off+1}, {_.lbl_β_p, _.lbl_ω_p, _.lbl_γ_p}, {true, false, false} };` (matches sorted sites with corresponding labels and is_def flags)

This is a one-line change. After it lands, every_to.icn mode 3 should print `1\n2\n3\n` matching mode 2.

### Verification used
- `IBB_DBG_SLAB` env-gated hex dump of the sealed slab (added to `bb_build_flat`, then reverted)
- `IBB_DBG` env-gated prints in `flat_drive_call_intexpr` showing `arg_β->offset = 107` (= 0x6B) immediately after `walk_bb_flat(BB_TO, ...)` returns — proves arg_β is mis-resolved before the trailer ever emits, ruling out any in-trailer issue
- `IBB_DBG_RT` env-gated prints in `rt_push_int` and `rt_pop_write_int_nl` showing the exact event sequence `push(1); pop; pop; underflow`

All instrumentation reverted before handoff.

---

## Still-pending mode-3 canonical-5 gaps after the one-line fix above

- **alt.icn** (`every write(1 | 2 | 3)`): arg0 to BB_CALL is BB_ALT (enum value 22 post-removal). `walk_bb_flat` has no `case BB_ALT:` (falls into the `default:` no-op). Per `lower_icn.c`, BB_ALT under Icon yields integers one at a time via three BB_LIT_I children chained via ω-port. Needs either a `flat_drive_alt_int` driver (Icon-side, vstack convention) or — more cleanly — extend `walk_bb_flat`'s BB_ALT arm to route through a new `bb_alt.cpp` MEDIUM_BINARY arm. The current `bb_alt.cpp` MEDIUM_BINARY is a port-wired passthrough (`α→γ, β→ω`), not a generator.
- **full.icn** (`every write(5 > ((1 to 2) * (3 to 4)))`): arg0 is BB_BINOP_GEN (kind 84 post-removal). Already has a real template in `bb_binop_gen.cpp` for SNOBOL4 patterns, but the int_expr arg0 dispatch in `walk_bb_flat` BB_CALL doesn't list BB_BINOP_GEN. Also needs a driver to walk the two operand sub-trees (each a BB_TO) in cross-product fashion and apply the `*`/`>` operations via `rt_arith` (BINOP_GEN's ival encodes the op like BB_BINOP does).

---

## Mode-3 templates and their honest state at handoff

| Template | MEDIUM_TEXT | MEDIUM_BINARY |
|---|---|---|
| `bb_fail.cpp` | real | real |
| `bb_seq.cpp` n==0 | real | real |
| `bb_seq.cpp` n>0 | real | real (`6393c743` EP-pair iteration) |
| `bb_call.cpp` write(strlit) | real | real (`6393c743`) |
| `bb_call.cpp` write(int_expr) — BINOP/LIT_I/**TO/ALT** | TEXT exists only for BINOP/LIT_I shape (no arg walk) | real for BINOP/LIT_I; **for TO**: emits but β-target resolves wrong (pending bin-reorder fix); **for ALT**: not yet implemented |
| `bb_every.cpp` | real (legacy walk_bb_node_str_c recursive) | real (NEW this session — pair-driven, mirrors `bb_pat_alt`) |
| `bb_to.cpp` (was `bb_icn_to.cpp`) | real (literal-bounds with `rt_push_int@PLT`) | real shape; sites out-of-order bug (pending fix) |
| `bb_lit_scalar.cpp` BB_LIT_I | empty (TEXT no-op; correct) | real (`3d85c4de`) |

---

## Where to start next session

1. Apply the bin reorder in `bb_to.cpp` MEDIUM_BINARY (one-liner; sites already ascending will fix every_to.icn mode 3). Re-verify canonical-5 mode 3 — should go from 2/5 → 3/5.
2. Add `case BB_ALT:` to `walk_bb_flat` and either (a) extend `bb_alt.cpp` MEDIUM_BINARY to be a real Icon-style int-arms generator, or (b) write a `flat_drive_alt_int` that walks the BB_LIT_I children and emits per-arm push+jmp_γ shapes. Verify alt.icn → 4/5.
3. Add BB_BINOP_GEN to the BB_CALL int_expr dispatch in `walk_bb_flat`. Author `flat_drive_binop_gen_tree` (mirrors `flat_drive_binop_tree` but cross-product re-pumps the operands). Verify full.icn → 5/5.
4. Then flip the SCRIP_ICN_BB default per the IBB-7 watermark in GOAL-ICON-BB.md.

---

## Commits in this session

| Repo | Hash | Subject |
|---|---|---|
| one4all | `057bc824` | IBB-4 WIP + rename bb_icn_to → bb_to + remove BB_ALTERNATE |
| .github | (this commit) | HANDOFF + PLAN/GOAL-ICON-BB update for the above |

## Author

Claude Opus 4.7, 2026-05-28.
