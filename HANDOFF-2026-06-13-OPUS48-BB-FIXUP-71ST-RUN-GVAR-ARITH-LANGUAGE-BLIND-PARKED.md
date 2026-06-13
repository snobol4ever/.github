# HANDOFF — 2026-06-13 — BB-FIXUP 71st run (Opus 4.8) — bb_binop_gvar_arith + LANGUAGE-BLIND finding — PARKED

## TL;DR
`bb_binop_gvar_arith.cpp` was converted 22→0 (audit CLEAN) AND de-language-blinded (all `g_gvar_flat_chain` reads removed), with emission **proven byte-identical to baseline** across all five dispatch arms. **It is NOT committed.** No corpus is present in this workspace, so the floor battery was not run; per Law 7 the change is parked, not landed. SCRIP stays at `758d7b1` with two files modified in the working tree. The full reproduction is embedded below.

## State
- SCRIP HEAD `758d7b1` — UNCHANGED. Working-tree modified (uncommitted): `src/emitter/BB_templates/bb_binop_gvar_arith.cpp`, `src/emitter/emit_bb.c`.
- `.github` — this handoff + the 71st-run watermark committed.
- Cursor STAYS `# CURSOR: bb_binop_gvar_arith.cpp` (parked, not certified).

## What was done
1. **Conversion 22→0** (relop pattern from the 70th run): dropped `IF(MEDIUM_TEXT)` gates (both-medium); inlined all 6 statics; **CV7** `x86_load_ro(reg,lbl,ptr)`→`x86("lea",reg,"[rip + __]",ptr,lbl)` and `x86_call_ro(sym,fp)`→`x86("call",sym,fp)` — identity-by-routing (the `x86()` dispatch at x86_asm.h:549/577/587 literally calls those helpers with the same args); terse CV1 comment; one `x86()` per line; CV8 explicit return; `extern DESCR_t POWER_fn` hoisted.
2. **CV10 prep-relocation in `bb_fill_alpha`** (DEVIATION from relop's per-arm placement): one op-keyed block interns the gvar-name / pow-target strtab labels into `op_parts_lbl[0..2]`, covering all 5 GVAR_ARITH producer sites at a single choke. `op_sval` (slot[2]) is interned **only for the POW shape** — interning it for every arm caused a spurious strtab insert and an `.S2/.S3` renumber; the `op_kind=="POW"` gate fixed it.
3. **LANGUAGE-BLIND fix**: removed every `g_gvar_flat_chain` read (and the `extern` line) from the template. The reads were redundant-with-dispatch (the box only fires when the driver already set the flag → invariantly 1 at template entry), so removal is byte-identical; the operand-shape guards (incl. the bomb arm) are retained. The variable **stays in the driver** (`emit_bb.c` `IR_BINOP` dispatch 2768–2839), where it is the load-bearing gvar-vs-descr selector (it is 0 during Icon/Raku descr emission). FIX-3's "g_*_flat_chain SANCTIONED — stays" applies to the driver, not to templates.

## Proof (C2)
Probes in `/tmp/gva/{litlit,varvar,varlit,litvar,pow}.sno` exercise all five arms (all LIVE under `--compile`, unlike the non-reachable relop sibling). Method: `./scrip --compile p.sno` → strip `#`-comment lines → `diff baseline vs final`. Result: **0 instruction-stream diffs** on every probe; the only raw delta is the sanctioned verbose→terse comment text. (Byte-identical emission ⇒ the floor battery is logically unchanged — but it still must be RUN to satisfy the protocol.)

## Findings for Lon (PIN needed)
- **Tree-wide LANGUAGE-BLIND breach, audit-blind.** The same `extern int g_gvar_flat_chain;` language-read pattern is in ~7 templates: `bb_binop_gvar_relop`, `bb_var`, `bb_var_frame`, `bb_assign_frame`, `bb_assign_frame_ref`, `bb_binop_gvar_arith_slot`, and `bb_call` — several already ratified CLEAN. `g_descr_flat_chain` (21 template decls) is the Icon/Raku counterpart; also `g_icn_scan_regs_live`, `g_gvar_callarg_live`. `scripts/audit_bb_fixup_file.sh` has **no LANGUAGE-BLIND check**, which is exactly why all of these passed as CLEAN.
- **Scope to pin:** (a) extend the byte-neutral strip to the sibling gvar/descr templates; (b) add a LANGUAGE-BLIND audit category that flags reads of driver-mode/language state-globals inside `bb_*.cpp` (distinct from legitimate `extern` FUNCTION decls like `rt_*` / `POWER_fn`); (c) certify+commit `bb_binop_gvar_arith` first.

## NEXT SESSION (to land this)
1. Clone the corpus; reproduce the two edits below.
2. Build (`bash scripts/build_scrip.sh`); confirm audit `bash scripts/audit_bb_fixup_file.sh src/emitter/BB_templates/bb_binop_gvar_arith.cpp` == CLEAN.
3. Re-run the C2 probes (above) AND the FULL floor battery: sno m4 7/7 HARD · pat M4 19/0 · icon m2 12/12 HARD (m3=m4 10/2) · prolog 5/5 ×3 · purity 1 · bin_t 0 · vstack 3 · handencoded 0 · sno_pat_reg · emit-blind 0 — pre AND post.
4. Only if all green: commit (template + emit_bb.c), recompute ceiling (−22), advance cursor toward `bb_binop_gvar_arith_slot` (24).
5. Take Lon's pin on the tree-wide LANGUAGE-BLIND scope.

---

## REPRODUCTION — edit 1: `src/emitter/BB_templates/bb_binop_gvar_arith.cpp` (full file)
```cpp
#include <string>
#include <stdint.h>
#include "emit_str.h"
extern "C" {
#include "bb_template_common.h"
#include "SM.h"
#include "ast.h"
#include "../../runtime/builtins/gen.h"
extern int64_t rt_gvar_arith(const char *a, const char *b, int op);
extern int64_t rt_gvar_get_int(const char *name);
void rt_gvar_assign_descr(const char *name, int64_t lo, int64_t hi);
extern DESCR_t POWER_fn(DESCR_t, DESCR_t);
}
#include "x86_asm.h"
/*--------------------------------------------------------------------------------------------------------------------*/
std::string bb_binop_gvar_arith() {
    if (PLATFORM_X86) return IF(_.op_off >= 0 && _.op_kind && !strcmp(_.op_kind, "POW") && !_.op_name1 && !_.op_name2 && _.op_sval,
                            x86("label", _.lbl_α)
                          + x86("comment", "IR_BINOP_GVAR_ARITH")
                          + x86("mov", "rdi", (long)DT_I)
                          + x86("mov", "rsi", (long)_.op_sa)
                          + x86("mov", "rdx", (long)DT_I)
                          + x86("mov", "rcx", (long)_.op_sb)
                          + x86("call", "POWER_fn", (uint64_t)(uintptr_t)(void *)POWER_fn)
                          + x86("push", "rdx")
                          + x86("lea", "rdi", "[rip + __]", (uint64_t)(uintptr_t) _.op_sval, _.op_parts_lbl[2])
                          + x86("mov", "rsi", "rax")
                          + x86("pop", "rdx")
                          + x86("call", "rt_gvar_assign_descr", (uint64_t)(uintptr_t)(void *) rt_gvar_assign_descr)
                          + x86("jmp", "γ")
                          + x86("def", "β")
                          + x86("jmp", "ω"))
                          + IF(_.op_off >= 0 && !(_.op_kind && !strcmp(_.op_kind, "POW"))
                              && (_.op_ival == BINOP_ADD || _.op_ival == BINOP_SUB || _.op_ival == BINOP_MUL || _.op_ival == BINOP_DIV || _.op_ival == BINOP_MOD)
                              && _.op_name1 && _.op_name2,
                            x86("label", _.lbl_α)
                          + x86("comment", "IR_BINOP_GVAR_ARITH")
                          + x86("lea", "rdi", "[rip + __]", (uint64_t)(uintptr_t) _.op_name1, _.op_parts_lbl[0])
                          + x86("lea", "rsi", "[rip + __]", (uint64_t)(uintptr_t) _.op_name2, _.op_parts_lbl[1])
                          + x86("mov", "rdx", (long)_.op_ival)
                          + x86("call", "rt_gvar_arith", (uint64_t)(uintptr_t)(void *) rt_gvar_arith)
                          + x86("mov", FRQ(_.op_off), "rax")
                          + x86("jmp", "γ")
                          + x86("def", "β")
                          + x86("jmp", "ω"))
                          + IF(_.op_off >= 0 && !(_.op_kind && !strcmp(_.op_kind, "POW"))
                              && (_.op_ival == BINOP_ADD || _.op_ival == BINOP_SUB || _.op_ival == BINOP_MUL || _.op_ival == BINOP_DIV || _.op_ival == BINOP_MOD)
                              && (_.op_name1 || _.op_name2) && !(_.op_name1 && _.op_name2),
                            x86("label", _.lbl_α)
                          + x86("comment", "IR_BINOP_GVAR_ARITH")
                          + x86("lea", "rdi", "[rip + __]", (uint64_t)(uintptr_t)(_.op_name1 ? _.op_name1 : _.op_name2), (_.op_name1 ? _.op_parts_lbl[0] : _.op_parts_lbl[1]))
                          + x86("call", "rt_gvar_get_int", (uint64_t)(uintptr_t)(void *) rt_gvar_get_int)
                          + IF( _.op_name1, x86("mov", "rcx", (long)_.op_sb))
                          + IF(!_.op_name1, x86("mov", "rcx", "rax"))
                          + IF(!_.op_name1, x86("mov", "rax", (long)_.op_sa))
                          + IF(_.op_ival == BINOP_ADD, x86("add",  "rax", "rcx"))
                          + IF(_.op_ival == BINOP_SUB, x86("sub",  "rax", "rcx"))
                          + IF(_.op_ival == BINOP_MUL, x86("imul", "rax", "rcx"))
                          + IF(_.op_ival == BINOP_DIV, x86("cqo"))
                          + IF(_.op_ival == BINOP_DIV, x86("idiv", "rcx"))
                          + IF(_.op_ival == BINOP_MOD, x86("cqo"))
                          + IF(_.op_ival == BINOP_MOD, x86("idiv", "rcx"))
                          + IF(_.op_ival == BINOP_MOD, x86("mov", "rax", "rdx"))
                          + x86("mov", FRQ(_.op_off), "rax")
                          + x86("jmp", "γ")
                          + x86("def", "β")
                          + x86("jmp", "ω"))
                          + IF(_.op_off >= 0 && !(_.op_kind && !strcmp(_.op_kind, "POW"))
                              && (_.op_ival == BINOP_ADD || _.op_ival == BINOP_SUB || _.op_ival == BINOP_MUL || _.op_ival == BINOP_DIV || _.op_ival == BINOP_MOD)
                              && !_.op_name1 && !_.op_name2,
                            x86("label", _.lbl_α)
                          + x86("comment", "IR_BINOP_GVAR_ARITH")
                          + x86("mov", "rax", (long)_.op_sa)
                          + x86("mov", "rcx", (long)_.op_sb)
                          + IF(_.op_ival == BINOP_ADD, x86("add",  "rax", "rcx"))
                          + IF(_.op_ival == BINOP_SUB, x86("sub",  "rax", "rcx"))
                          + IF(_.op_ival == BINOP_MUL, x86("imul", "rax", "rcx"))
                          + IF(_.op_ival == BINOP_DIV, x86("cqo"))
                          + IF(_.op_ival == BINOP_DIV, x86("idiv", "rcx"))
                          + IF(_.op_ival == BINOP_MOD, x86("cqo"))
                          + IF(_.op_ival == BINOP_MOD, x86("idiv", "rcx"))
                          + IF(_.op_ival == BINOP_MOD, x86("mov", "rax", "rdx"))
                          + x86("mov", FRQ(_.op_off), "rax")
                          + x86("jmp", "γ")
                          + x86("def", "β")
                          + x86("jmp", "ω"))
                          + IF(!(_.op_off >= 0 && !(_.op_kind && !strcmp(_.op_kind, "POW"))
                                && (_.op_ival == BINOP_ADD || _.op_ival == BINOP_SUB || _.op_ival == BINOP_MUL || _.op_ival == BINOP_DIV || _.op_ival == BINOP_MOD))
                              && !(_.op_off >= 0 && _.op_kind && !strcmp(_.op_kind, "POW") && !_.op_name1 && !_.op_name2 && _.op_sval),
                            x86_bomb("bb_binop_gvar_arith: shape mismatch (dispatch chose this arm but predicate failed)"));
    return std::string();
}
```

## REPRODUCTION — edit 2: `src/emitter/emit_bb.c` — `bb_fill_alpha` (add the op-keyed GVAR_ARITH interning block; the `if (nd && nd->op == IR_BINOP_GVAR_ARITH)` lines are the only addition)
```c
static void bb_fill_alpha(IR_t *nd) {
    extern int g_sno_m4_dense_nid;
    bb_label_t *a = &g_α_ring[g_α_ring_i++ & 7];
    if (g_sno_m4_dense_nid) emit_label_initf(a, "bb%d_α", ++g_bb_alpha_seq);
    else                    emit_label_initf(a, "bb%d_α", nd ? bb_node_id(nd) : 0);
    g_emit.lbl_α   = a->name;
    g_emit.lbl_α_p = a;
    if (nd && nd->op == IR_BINOP_GVAR_ARITH) { static char gvapool[3][64]; g_emit.op_parts_lbl[0] = NULL; g_emit.op_parts_lbl[1] = NULL; g_emit.op_parts_lbl[2] = NULL;
      if (g_emit.op_name1 && g_emit.op_name1[0]) { strtab_label(gvapool[0], 64, g_emit.op_name1); g_emit.op_parts_lbl[0] = gvapool[0]; }
      if (g_emit.op_name2 && g_emit.op_name2[0]) { strtab_label(gvapool[1], 64, g_emit.op_name2); g_emit.op_parts_lbl[1] = gvapool[1]; }
      if (g_emit.op_kind && !strcmp(g_emit.op_kind, "POW") && g_emit.op_sval && g_emit.op_sval[0]) { strtab_label(gvapool[2], 64, g_emit.op_sval); g_emit.op_parts_lbl[2] = gvapool[2]; } }
}
```
