# HANDOFF-2026-06-13-OPUS48-RAKU-BB-PROC-DOUBLE-EMIT-DIAGNOSIS.md

## Session: GOAL-RAKU-BB — diagnosis only, NO code landed

**SCRIP HEAD at open/close: `b9a2433` (UNCHANGED — working tree clean, no source edits).**
**`.github` HEAD at open: `13cc0dec`. This doc + watermark addendum are the only changes.**

Gates at open == close: m2 **31/31**, m3 **25 PASS / 0 FAIL / 6 EXCISED**, m4 **25 / 0 / 6**. Peers
invariant (not re-run — no code touched).

---

## NEW BUG FOUND — "BUG 1": whole-proc DOUBLE-EMISSION (separate from, and prior to, the watermark's nested-BINOP "Bug 2")

The watermark's Group-C blocker is the nested-BINOP operand double-emission (the `$factor` IR_VAR emitted
twice inside `scale`). That is real, but there is a SECOND, more fundamental bug that the session-7/8 analysis
did not isolate: **every named Raku `sub` (and every class method) is registered TWICE in `proc_table`, so the
mode-4 emitter writes its `icn_proc_<name>_α:` / `_β:` / `_γ:` / `_ω:` / `_α_body:` labels TWICE → the
assembler rejects the file with `symbol 'icn_proc_<name>_α' is already defined`.** This blocks ANY
sub-containing Raku program in m3/m4, not just `class_method`.

### Minimal repro (Bug 1 ONLY — does NOT trigger Bug 2)
```raku
sub f($a) { return ($a + 1) * $a; }
say f(3);
```
```
cd /home/claude/SCRIP
./scrip --compile /tmp/f.raku 2>/dev/null > /tmp/f.s
as /tmp/f.s -o /tmp/f.o
# → /tmp/f.s:NN: Error: symbol `icn_proc_f_α' is already defined  (and _α_body, _β, _γ)
```
Confirmed: the emitted text contains TWO complete `icn_proc_f_α:` bodies (first chain-prefix `xchain0_*`,
second `xchain9_*`, different `bbNNNN` node-ids in each), AND the `icn_proc_startup:` section lists `"f"`
TWICE (`.Lstartup_pname0` and `.Lstartup_pname1` both `.string "f"`). This repro does NOT hit Bug 2 because
`f`'s body `($a+1)*$a` takes the `descr_flat_chain` `needs_walk == 0` path (operands already have slots), so
`flat_drive_binop_tree` is never entered. So Bug 1 is isolated and independently reproducible.

### Root cause — Raku procs are registered by TWO registrars
1. `polyglot_init` (`src/driver/polyglot.c:111`) registers procs for ICN/RAKU/PASCAL from
   `TT_FNC | TT_PROC_DECL | TT_SUB_DECL`. The guard at line 110, `int _is_raku_call = (s_lang == LANG_RAKU
   && proc->t == TT_FNC);`, was clearly meant to keep Raku procs OUT of this generic path — but it only
   excludes `TT_FNC` (a Raku call), NOT `TT_SUB_DECL` (a Raku declaration). So a top-level `sub f`
   (`TT_SUB_DECL`) IS registered here → `proc_table["f"]`, `bb_idx = -1`. **`TT_SUB_DECL` is Raku-only**
   (Icon/Pascal use `TT_PROC_DECL`), so this `|| proc->t == TT_SUB_DECL` clause fires ONLY for Raku and is
   pure redundancy with (2).
2. `lower_raku_stage2` → `rk_discover_procs` → `rk_register_proc` (`src/lower/lower_raku.c:398/433/443`)
   registers the SAME `TT_SUB_DECL` a SECOND time → another `proc_table["f"]`, `bb_idx = -1`. (This registrar
   also handles class methods as qualified `Class__method` names — which polyglot never sees, so it is the
   MORE COMPLETE registrar and cannot simply be deleted.)

Then `lower_raku_stage2`'s lowering loop (`lower_raku.c:499`) iterates ALL `proc_table` entries and lowers
each one where `proc->t == TT_SUB_DECL && bb_idx < 0` — so it lowers BOTH "f" entries into two separate BB
graphs, each getting a valid `bb_idx`. The m4 emit loop (`scrip.c:2422`) then emits BOTH (its skip-guard
`if (idx < 0 …) continue;` no longer fires, because both now have `bb_idx >= 0`).

### Why m2 (31/31) tolerates this but m3/m4 break
Mode-2 (`--interp`) also runs `sm_preamble → lower_stage2 → polyglot_init + lower_raku_stage2`, so it ALSO
double-registers. But m2 executes by walking the IR graph and dispatching proc calls BY NAME
(`rt_proc_register` / `rt_call_proc_descr`); both "f" entries lower to functionally identical graphs, so
calling "f" resolves correctly regardless of the duplicate. There are no emitted LABELS in m2 to collide.
m3/m4 emit machine code with real symbols, so the duplicate `icn_proc_f_*` labels are a hard assembler error.
This is exactly why the bug is invisible in the m2 oracle and only shows up as an m3/m4 "FAIL/EXCISE".

### Registration pattern across languages (so the fix matches convention)
- **Icon:** does NOT call `stage2_proc_grow` anywhere in `lower_icon.c` — it only READS `proc_table`
  (`icn_proc_is_generator` at `lower_icon.c:18`, plus loops at 436/441). Icon relies on `polyglot_init` as its
  SOLE proc registrar.
- **Prolog:** `resolve_pred_table` + `stage2_proc_grow` (`lower_prolog.c:520`).
- **SNOBOL4:** self-registers (`lower_snobol4.c:987/1010`).
- **Raku:** the ONLY language registered by BOTH `polyglot_init` AND its own `rk_discover_procs`. ← the defect.

---

## FIX — pick ONE (Option A recommended)

### Option A (recommended): make `rk_discover_procs` the SOLE Raku registrar — exclude Raku `TT_SUB_DECL` from `polyglot_init`
`src/driver/polyglot.c` lines 110-111, change:
```c
int _is_raku_call = (s_lang == LANG_RAKU && proc->t == TT_FNC);
if (!_is_raku_call && (proc->t == TT_FNC || proc->t == TT_PROC_DECL || proc->t == TT_SUB_DECL)) {
```
to (extend the exclusion to Raku declarations as well as Raku calls):
```c
int _is_raku_owned = (s_lang == LANG_RAKU && (proc->t == TT_FNC || proc->t == TT_SUB_DECL));
if (!_is_raku_owned && (proc->t == TT_FNC || proc->t == TT_PROC_DECL || proc->t == TT_SUB_DECL)) {
```
This leaves Icon/Pascal `TT_PROC_DECL` registration untouched and makes `rk_discover_procs` the single Raku
registrar (it already handles BOTH top-level subs AND class methods). **Verified safe:**
- `polyglot_init`'s proc-registration loop (lines 64-154) is its LAST action; the function returns at 155.
  Nothing after it depends on the Raku entry.
- In `lower_stage2` (`lower_common.c`), `polyglot_init` (257) is immediately followed by `lower_raku_stage2`
  (262) for a pure-Raku program; nothing reads `proc_table` between them, and `rk_discover_procs` repopulates.
- `module_registry.mods[].nprocs` and `.proc_start` (the only bookkeeping polyglot would stop updating for
  Raku subs) are WRITE-ONLY: grep across `src/` shows no reader outside `polyglot.c`. So dropping the Raku
  increment changes no consumer.

### Option B (conservative alternative): make `rk_register_proc` idempotent
Keep polyglot's registration; dedup the second insertion. In `src/lower/lower_raku.c` `rk_register_proc`
(line 398), before `stage2_proc_grow`, skip if a `proc_table` entry with the same `name` already exists:
```c
for (int i = 0; i < g_stage2.proc_count; i++)
    if (g_stage2.proc_table[i].name && !strcmp(g_stage2.proc_table[i].name, name)) return;
```
Top-level subs: polyglot's entry survives (`name` = `c[0]->v.sval`, identical to rk_discover's; `nparams` =
`(int)proc->v.ival`, identical). Class methods: qualified `Class__method` names are never in polyglot's table,
so no false dedup. Preserves all of polyglot's module bookkeeping. (Caveat: assumes no legitimate same-name
multi-dispatch subs — SCRIP does not appear to support that today.)

**Recommendation:** Option A — it repairs the actual design oversight (the incomplete `_is_raku_call`
exclusion) and removes a Raku-only redundant clause, rather than masking the duplicate after the fact.

---

## ORDER OF WORK for next session (Bug 1 BEFORE Bug 2)

1. **Land Bug 1 fix (Option A).** Rebuild `make -j4 scrip`. Verify the repro `sub f` now emits ONE
   `icn_proc_f_α:` and `as /tmp/f.s -o /tmp/f.o` returns clean. Run `bash scripts/test_smoke_raku.sh` — expect
   m2 still 31/31 and NO regression in m3/m4 (25/0/6 or better; any test that was EXCISED solely due to the
   duplicate-proc-label should improve). Run `test_smoke_icon.sh` + `test_smoke_snobol4.sh` (HARD) to prove
   Icon/Pascal/SNOBOL4 registration is unaffected by the polyglot.c edit. Commit.
2. **Then Bug 2** (the watermark's existing C blocker): the nested-BINOP operand double-emission in `scale`
   (`($!x+$!y)*$factor` emits the `$factor` IR_VAR twice — once as a chain node, once as the `*`-BINOP lhs via
   `flat_drive_binop_tree`). Start at `codegen_flat_chain_body` queue-build (`emit_bb.c:3057`, which enqueues a
   BINOP's `ω.node`) × `flat_drive_binop_tree` (`emit_bb.c:1403`, which ALSO walks `bb_child1`). Reproduce with
   a body that forces the `descr_flat_chain` `needs_walk == 1` path (operands WITHOUT pre-assigned slots), e.g.
   `sub g($a){ return ($a + 1) * ($a + 2); }` — verify whether a SECOND nested binop forces the walk that
   `sub f` avoided. Fix so a node is walked once (the chain walker should not enqueue an operand that
   `flat_drive_binop_tree` will itself emit).
3. **Then the FIELD_GET template + gate for `class_method`** per the watermark's Group-C item (1)+(2):
   `icn_rhs_kind_ok` admit `IR_CALL dval==1.0` + `IR_FIELD_GET`; `case IR_FIELD_GET` in `walk_bb_node`
   (`emit_core.c:372`); new `bb_field_get` template calling `dat_field_get` (`by_name_dispatch.c:3132`);
   Makefile + `bb_templates.h` wiring. Verify `class_method` EXCISED → PASS, m2 31/31, no peer regression.

---

## Files inspected (no edits)
- `src/driver/polyglot.c` (proc registration — root cause site)
- `src/lower/lower_raku.c` (`rk_discover_procs`, `rk_register_proc`, `lower_raku_stage2`)
- `src/lower/lower_common.c` (`lower_stage2` dispatch), `src/machine/sm_prog.c` (`stage2_reset`/`proc_grow`)
- `src/driver/scrip.c` (m2 + m4 driver loops), `src/driver/scrip_sm.c` (`sm_preamble`)
- `src/lower/lower_icon.c` (confirmed Icon has no self-registrar)
- `src/emitter/emit_bb.c` (`codegen_flat_chain_body`, `flat_drive_binop_tree` — for Bug 2 next session)
