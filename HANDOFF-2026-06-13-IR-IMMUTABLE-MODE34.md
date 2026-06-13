# HANDOFF — IR-IMMUTABLE in mode 3/4 (enforcement landed; physical purge pending)

**Rule (long-standing, ~3 months):** In mode 3 (`--run`) and mode 4 (`--compile`) the IR graph must
NEVER be touched, read, or looked at. No `nd->op`, no `IR_LIT(nd)`, no `nd->γ/ω.node`, no operand
walking — nothing. The native code generator must not reach into the IR at all.

## What landed — SCRIP `e50b089`
The native emitter (`src/emitter/emit_bb.c`: `walk_bb_flat`, `flat_drive_*`, `codegen_flat_*`, `bb_fill_*`,
plus the descr/gvar flat-chain builders) is, by construction, an IR-reading code generator and violated
the rule throughout (op-swap dispatch `nd->op = X; FILL; nd->op = _sk`, permanent operand rewrites, and
hundreds of `nd->op ==` / `IR_LIT(nd)` reads). Rather than leave a half-gutted, non-compiling tree, the
rule is **enforced at the mode boundary**: in `src/driver/scrip.c` both the mode-4 block (`if
(mode_compile_x86) {`) and the mode-3 block (`} else if (mode_run) {`) now execute `(*(volatile char
*)NULL);` as their FIRST statement — before `sm_preamble` and before any `s2->bbp` / IR access. So neither
mode can reach any IR-reading code: `--run` and `--compile` SIGSEGV (rc=139) immediately.

**Gate state at e50b089:** m2 interp HARD gate **PASS=202** (unchanged — the oracle never runs the emit
path). icon mode-2 smoke 12/12, prolog mode-2 smoke 5/5 (both HARD, green). Mode-3/4 smoke arms are 0 by
design (bombed). The native-only gates (`test_gate_icn_no_stack`, `test_gate_icn_one_reg_frame`,
`test_gate_bb_one_box`) are RED BY DESIGN — they exercise the now-bombed emitter.

## REMAINING WORK — physical purge of the now-dead IR-walking code
The entry bombs make the IR-reading backend unreachable; it is now DEAD CODE that must be physically
removed from the files (per "ensure the code is physically removed from the file"). This is a large,
multi-file deletion — do it on a fresh budget so it lands compiling + gated, not half-applied.

Order of removal (delete the body, stub each external call site with `(*(volatile char *)NULL);`):
1. `src/driver/scrip.c` — physically delete the dead bodies BELOW the two bombs: the entire
   `if (mode_compile_x86) { ... }` body (was lines ~2275–2539) and the entire `} else if (mode_run) { ... }`
   body (was ~2615 to its closing brace), leaving only the bomb. Keep the mode-2 `--interp` block (~2551–2613)
   and the `--monitor` / non-x86-target stubs intact.
2. `src/emitter/emit_bb.c` (3618 lines, the bulk) — delete the IR-reading walkers and bomb their (now
   external/cross-file) call sites: `walk_bb_flat` (2507), `codegen_flat_build` (3594, the public entry in
   `emit_bb.h:19`), `codegen_flat_body` (3085), `codegen_flat_chain_body` (2979),
   `codegen_gvar_flat_chain_body` (3434), `walk_bb_flat_or_inline_alt` (3061), and every `flat_drive_*` /
   `bb_fill_*` helper. Remove the matching prototypes in `src/emitter/emit_bb.h` and the
   `bb_build_flat_text` macro.
3. `src/emitter/emit_core.c` — the `EMIT_PAIR_FILL` dispatch switch reads `nd->op` to pick a template;
   delete it and the descr/gvar flat-chain builders (`descr_flat_chain_build_text`,
   `descr_flat_chain_build_proc_text`, `gvar_flat_chain_build_text`, `descr_flat_chain_build_proc`).
4. `src/emitter/BB_templates/` — these are already clean of IR MUTATION, but many READ the IR via `_.node`
   / `ir_call_arg(_.node, …)` / `bb_child0`. If the rule is read strictly, the templates that dereference
   `_.node` must also go (or the whole template layer, since with no walker nothing calls them).
5. Test infra: retire/adjust `test_gate_icn_no_stack`, `test_gate_icn_one_reg_frame`,
   `test_gate_bb_one_box`, and the mode-3/4 arms of `test_smoke_icon.sh` / `test_smoke_prolog.sh` /
   `test_icon_rung_suite.sh` (lower `MODE3_MIN`/`MODE4_MIN` to 0 or remove the native arms) so the gate
   reflects "native disabled." The m2 interp HARD gate stays the source of truth.

## Exact IR-mutation/read inventory already gathered (emit_bb.c)
Op-swap dispatch idiom `{ IR_e _sk = nd->op; nd->op = <specialized>; EMIT_PAIR_FILL(...); nd->op = _sk; }`:
lines 1432, 1466, 1516, 2080, 2731, 2740, 2747, 2755, 2763, 2778, 2802, 2815; binop-gen op-swap 2841–2843;
const-mutate-with-restore 2087–2092 (`c0->op` + `IR_LIT(c0).ival`); SNOBOL pattern op-swap 2283–2290,
2311–2313, 2358–2360; `IR_LIT(pBB).ival=` writes 437, 477, 2153. Permanent (unrestored) operand rewrites:
2714 (`nd->n_operands=0; ir_operand_push(nd,_ax[0]); ir_operand_push(nd,_ax[1])`), 3214, 3263–3264,
3374–3375. The BB templates themselves had ZERO `->op =` / `ir_operand_push` mutation (verified by grep).
Everything else in emit_bb.c is `nd->op ==` / `IR_LIT(nd).x` READS — all forbidden in mode 3/4 and all to
be removed in the purge.

## Rebuild contract (after the purge)
If mode 3/4 are ever rebuilt, the native code generator must consume a SEPARATE, already-lowered structure
(emitted once by the lowering pass) and must NOT dereference `IR_t` during emission. The lowering pass
(`src/lower/lower_icon.c` etc., which BUILDS the IR — allowed) would also produce the emit-ready structure;
the emitter walks only that. Until then, mode-2 (`--interp`) is the sole execution path.

## Note
The Icon pow `^` constant-fold (SCRIP `2831781`, prior commit) lives entirely in lowering
(`src/lower/lower_icon.c`) and is unaffected — it still yields the correct real in mode-2 (`2^10`→`1024.0`),
and m2 stayed 202 across this change.
