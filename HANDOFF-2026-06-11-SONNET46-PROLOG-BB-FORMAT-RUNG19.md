# HANDOFF — 2026-06-11 — Sonnet 4.6 — PROLOG-BB PL-GZ-9 format/1,2 (rung19)

**Goal:** GOAL-PROLOG-BB.md · PL-GZ-9 corpus reconquest.
**Watermark:** SCRIP `8a41154` · .github `cb44126b` (both pushed, battery green).

## Landed

**rung19 format/1,2 admitted onto the native m3/m4 path — 5 new rungs.**
GATE-3 m3 ratchet **38 → 43**. No regressions: m2=114, m4=49+17excised. GATE-1 5/5/5.

### New components

- **`IR_DET_FORMAT`** — new IR kind in `src/contracts/IR.h` + name table in `scrip_ir.c`.
- **`rt_pl_format_cell(const char *fmt, void *list_cell)`** — new runtime function in `src/runtime/unification.c`. Walks the format string dispatching on `~n/~N`, `~a/~w/~p` (write), `~d` (integer), `~i` (skip/ignore), `~t` (tab), `~~` (literal tilde). `list_cell` is NULL for arity-1.
- **`bb_det_format.cpp`** — new BB template in `src/emitter/BB_templates/`. Parameterless, CV9-compliant. Delivers: `ROQ(0)` for the sealed format string pointer (RO data), `FRQ(GZ_CELL_OFF(list_slot))` for the list cell pointer (arity-2), or `xor esi,esi` (arity-1, NULL list). Single `call rt_pl_format_cell`, then `jmp γ`. β → `jmp ω`.
- **`bb_prepare` block for `IR_DET_FORMAT`** in `src/emitter/emit_bb.c`: delivers `op_parts_str[0]=fmt_string`, `op_parts_ival[0]=arity`, `op_parts_ival[1]=list_slot` (slot index of the list cell, or -1 for arity-1).
- **`emit_core.c`** dispatch case: `case IR_DET_FORMAT: { extern void bb_det_format(void); bb_prepare(nd); bb_det_format(); return 0; }`
- **Makefile**: `bb_det_format.cpp` added to `RT_PIC_SRCS` and explicit compile rule.

### Admission wiring (all in `src/driver/scrip.c`)

- **`pl_gz_rule_body_goal_ok`**: format/1 (ATOM arg0) and format/2 (ATOM arg0, STRUCT/ATOM arg1) admitted.
- **`pl_gz_rule_clause`** BUILTIN whitelist: `if (IR_LIT(nd).sval && !strcmp(IR_LIT(nd).sval, "format") && (IR_LIT(nd).ival == 1 || IR_LIT(nd).ival == 2)) continue;`
- **`pl_gz_count_synth_goal`**: format/2 with non-LOGICVAR list arg counts +1 synth slot.
- **`pl_gz_build_goal`**:
  - format/1: handled inside the `gg->op==IR_BUILTIN && ival==1` arm — guard `strcmp(fn,"format") != 0` prevents early rejection; format case emits `IR_DET_FORMAT` with `sval=fmt`, `ival=1`, no operands.
  - format/2: handled inside the `gg->op==IR_BUILTIN && ival==2 && ir_pair_arg(0) && ir_pair_arg(1)` arm (the comparator arm) — guard `&& strcmp(fn,"format") != 0` added to the `!is_arith_cmp && !is_tcmp` rejection; format case materialises list arg into a synth slot via `IR_CELL_UNIFY` if not already a LOGICVAR, then emits `IR_DET_FORMAT` with `sval=fmt`, `ival=2`, operand = list LOGICVAR slot.

### Key admission bug found and fixed

format/2 was being swallowed by the generic `IR_BUILTIN && ival==2 && ir_pair_arg(0) && ir_pair_arg(1)` arm in `pl_gz_build_goal`, which rejected it as neither arith-cmp nor tcmp. Fix: guard the rejection, inline the format/2 build inside the `else` branch of that arm. format/1 had the same problem in the arity-1 arm.

## Gates at commit `8a41154`

- GATE-1: m2/m3/m4 5/5 HARD ✓
- GATE-3: m2=114 · m3=43 · m4=49+17excised ✓
- bb_bin_t: 0 ✓ · vstack: 3 (pre-existing) · handencoded: 0 · med_inv: 102 · purity: 2 · prove_lower: 21P rc=0 · sno_pat_reg HARD ✓ · sno m4 7/7 HARD ✓

## Next open in PL-GZ-9

Per the goal file: next open shape after rung19 is **rung16 `at_*` sort predicates** — wait, those landed with the term-order commit. The actual next open target is whatever the next INTERP-FALLBACK abort reveals. A survey pass recommended by the prior session:

```bash
for f in /home/claude/corpus/programs/prolog/rung*.pl; do
  name=$(basename $f .pl); exp=$(cat /home/claude/corpus/programs/prolog/${name}.expected 2>/dev/null)
  m3=$(cd /home/claude/SCRIP && ./scrip --run $f < /dev/null 2>/dev/null)
  [ "$m3" != "$exp" ] && echo "FAIL m3: $name"
done | head -20
```

Likely candidates: `rung12_atom_builtins_*` (atom_length/atom_concat/atom_chars), `rung15_*` (number_chars/number_codes), `rung18_succ_plus_*`.

## Session notes

- Prolog reference zips (gprolog-master, swipl-devel-master) extracted at `/home/claude/refs/`. Per RULES, these are observable-semantics oracles only — gprolog/SWI are NOT design authority.
- `/tmp` is NOEXEC in this container — link m4 probe binaries to `/home/claude/` when running `ld` for m4 probes (the 50th-run note).
- `make libscrip_rt` requires an explicit `touch src/runtime/unification.c` if the Makefile timestamp check misses it.
