# HANDOFF-2026-05-30-SONNET46-LANG-INDEP-RENAME-SLICE-5.md

**Date:** 2026-05-30 · **Author:** Claude Sonnet 4.6 · **Goal:** `GOAL-LANG-INDEPENDENT-RENAME.md`
**SCRIP HEAD:** `df3551a7` (pushed) · **.github HEAD:** (this commit)

---

## What shipped

### ICN_/Icn_ post-AST de-prefix (`df3551a7`, part of Slice 5)

44 sed rules across 20 post-AST files. All were missed in Slice 2 (gen_runtime.h/gen.h/stage2.h not
fully audited). Renamed:

**Types:** `IcnBinopKind→BinopKind`, `IcnFrame→GenFrame`, `IcnGenEntry_d→GenEntry_d`,
`IcnProcEntry→ProcEntry`, `IcnScope/ScopeEnt→GenScope/GenScopeEnt`, `IcnInitEnt/Slot→InitEnt/InitSlot`.

**Macros:** `ICN_BINOP_*→BINOP_*` (19 variants), `ICN_INIT_MAX/SLOTS→INIT_MAX/SLOTS`,
`ICN_FAIL_GEN→FAIL_GEN_NODE`, `ICN_ENTER→GEN_ENTER`, `ICN_TO_NESTED_MAX→TO_NESTED_MAX`,
`ICN_SEC_*→SEC_*`, `ICN_CASE/COMPOUND/LISTCON_MAX` stripped, `ICN_FIELD_NAME→FIELD_NAME`,
`ICN_KW_CSET_MAX→KW_CSET_MAX`, `ICN_MATH1/TONUM→MATH1/TONUM`, `ICN_STACKLESS_ABORT→STACKLESS_ABORT`.

**Global:** `g_icn_jcon→g_jcon` — also fixed in `src/frontend/icon/icon_lex.c` (cross-boundary use;
the definition moved to `gen_runtime.c` as `g_jcon`, the lexer's `extern` declaration updated to match).

**Exempt (not renamed):** `icn_cset_*` (defined in `src/frontend/icon/icon_runtime.c` — frontend file),
`icn_bb_dcg` (Icon-specific DCG entry, cultural name), `IcnTkKind` etc. (Icon lexer types from
`icon_lex.h` — frontend header). VM opcode strings `"ICN_SCAN_PUSH"` etc. in `gen_runtime.c`
strcmp calls — opcode name strings, not C identifiers (same precedent as Raku `__rk_jct_*` strings
left as-is in Slice 4).

### gen_-non-generator strip (same commit)

Per Lon directive: `gen_` prefix is only valid when it means generate/generator/generation. Stripped:
- `GenScope→Scope`, `GenScopeEnt→ScopeEnt` — variable-slot scope structs, not generators
- `GenEntry_d→ScopeEntry` — scope entry type
- `gen_descr_identical→descr_identical` — equality check, not a generator
- `gen_scope_patch→scope_patch` — scope walker, not a generator

**Kept with gen_ prefix (legitimately mean generator):**
`gen_alternate_state_t`, `gen_bal_state_t`, `gen_bang_binary_state_t` — Icon generator states.
`GenFrame` — call frame for generator execution. `GEN_ENTER` — enters a generator state struct.
`gen_bb_*`, `gen_*_state_t` (resume states), `gen_binop_apply`, `gen_resume` etc. — all generator machinery.

### PLAN.md session-start update

Step 1 is now: **check GOAL-LANG-INDEPENDENT-RENAME.md and do any remaining rename steps**,
before cloning and reading goals. The rename is an ongoing invariant, not a completed one-time task.

### LOWER-MERGE steps added to `GOAL-SNOBOL4-BB.md` (the live session goal)

Lon's directive to merge all `src/lower/*.c` into a single consolidated `lower.c` is recorded as the
LOWER-MERGE step block (LM-1..LM-5) **inside GOAL-SNOBOL4-BB.md** — NO new goal file. 5 steps, smallest
file first (`lower_ctx.c` → `lower_clause.c` → `lower_pat_dcg.c` → `lower_graph.c`), pure structural
merge, gate after each. The rename goal carries a one-line pointer to it.

---

## Gates (all green at `df3551a7`)

- `make scrip` rc=0
- `make libscrip_rt` rc=0
- `bash scripts/test_gate_sm_dead.sh` → 1/1 OK
- `bash scripts/audit_m3_native_binary_arms.sh` → GATE OK
- Icon m2 hello → `hello` ✅
- FACT=0

---

## Next steps

1. **LOWER-MERGE** (steps LM-1..LM-5 in `GOAL-SNOBOL4-BB.md`): LM-1 — merge `lower_ctx.c` (37 lines, smallest).
2. **Slice 5 remainder** (lowest priority): backend `.il/.j/.wat/.cs/.java/.js` — off live X86 path.
