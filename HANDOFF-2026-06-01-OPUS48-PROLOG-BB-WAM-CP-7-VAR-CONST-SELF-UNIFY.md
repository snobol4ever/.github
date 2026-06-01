# HANDOFF 2026-06-01 — Claude Opus 4.8 — PROLOG-BB WAM-CP-7a/7b head-unify specialization

**Goal:** GOAL-PROLOG-BB.md (WAM-CP-7 unify specialization)
**SCRIP HEAD:** `b716e8c`
**\.github HEAD (parent of this commit):** `0f9787a6`

Two slices of WAM-CP-7 landed: **7a var-vs-const** and **7b first-occurrence/self-unify**. Both are mode-4
head-matching optimizations grounded in gprolog (`Pl2Wam/code_gen.pl gen_unif_arg`, `EnginePl/wam_inst.c`
`Pl_Get_Atom`/`Pl_Get_Integer`) and swipl (`src/pl-vmi.c` `H_ATOM`/`H_SMALLINT`/`H_FIRSTVAR`), both of which
collapse a statically-known head arg to deref-one-then-(bind|compare), never the general unifier. Pure
optimization: pass counts unchanged, every mode byte-identical.

## Gates at handoff (all green, integrated tree incl. Raku `fbe38ea`)
- GATE-1 smoke (`test_smoke_prolog.sh`): m2/m3/m4 = 5/5/5
- GATE-3 rung suite (`test_prolog_rung_suite.sh`): m2 111/111, m3 111/111, m4 86 PASS / 0 FAIL / 25 EXCISED (exact baseline — optimization, no count change)
- 11 cross-mode probes byte-identical m2==m3==m4
- no-handencoded `bb_unify.cpp` = 1 (unchanged), template-purity = 8 (bb_unify unflagged), `pl_no_value_stack` PASS, `g_vstack` = 0, `seg_byte`/`SL_B` outside templates = 0

## What landed

Both shapes arise from `g_head_unify` (`lower.c:2339`), which emits `IR_UNIFY(LOGICVAR(slot), head_arg_term)`
per head arg. Current general emission per arg = `rt_pl_node_to_term`×2 + `rt_pl_unify_terms` (3 calls + an
atom alloc). Two files touched, Prolog-arm-only, additive: `rt.c` +17, `bb_unify.cpp` +58.

### Rung 1 — 7a var-vs-const (`b716e8c`)

**Shape:** `IR_UNIFY(LOGICVAR(i), {IR_ATOM|IR_LIT_I|IR_LIT_F})` (either orientation). The canonical
`get_atom`/`get_integer`: deref the var; unbound → bind+trail; bound → word-compare; never general unify.

**Runtime (`rt.c`):** new `rt_pl_unify_const(int slot, int kind, long ival, const char *sval, double dval)`.
Reads/vivifies `env[slot]` identically to `rt_pl_node_to_term`'s `IR_LOGICVAR` arm, then takes `unify()`'s leaf
branches verbatim — unbound `TERM_VAR` → `rt_pl_unify_terms(vt, rt_pl_node_to_term(...))` (the same bind+trail
path, identical); bound → scalar compare (`TERM_ATOM`&&`atom_id==intern(sval)` / `TERM_INT`&&`ival==` /
`TERM_FLOAT`&&`fval==`, mismatched tag → 0), skipping the const Term alloc. Provably `≡ node_to_term×2 +
unify_terms` because it is assembled from the exact `unify()` leaves. A conversion+effect (returns 1/0, makes
no jump) — KEEP side of PJ-RT-PURGE, like `rt_pl_unify_terms`.

**Emitter (`bb_unify.cpp`):** specialized TEXT + BINARY arms before the general path. TEXT: SysV
`edi=slot, esi=kind, rdx=ival, rcx=sval-label|0, xmm0=dval|0`, one `rt_pl_unify_const@PLT`, then the existing
γ/ω tail (`resolve_unify_tail_text`). BINARY twin uses hand-coded literal bytes with **hardcoded** base offsets
(45 atom / 37 int / 49 float — literal sums of the verified instruction sizes, no `b.size()`); every encoding
was assembler-round-trip verified, including the fresh `movq xmm0,rax` = `66 48 0F 6E C0`. Any non-matching
shape falls through to the unchanged general arm.

**Result:** `fact(a)`-style head-match 3 calls + 1 alloc → **1 call** (alloc only on unbound-bind).

### Rung 2 — 7b first-occurrence / self-unify (`b716e8c`, emitter-only)

**Shape:** a head variable at its own positional slot → `IR_UNIFY(LOGICVAR(i), LOGICVAR(i))`. `unify(env[i],
env[i])` hits `unify()`'s `t1==t2` short-circuit: always true, no binding, no trail. The canonical
`get_variable`/`H_FIRSTVAR`: the first occurrence is free.

**Emitter (`bb_unify.cpp`):** detect `lhs->t==IR_LOGICVAR && rhs->t==IR_LOGICVAR && lhs->ival==rhs->ival`,
elide to a bare success jump (reuse the missing-operand vacuous-success emission: `α:` + `jmp γ` + `β: jmp ω`
TEXT; the `{1,5,6}` two-jmp `bin` for BINARY — framework registers `α` at the box start). 3 calls → **0**.

**Soundness:** the only side-effect of the general path here is `resolve_node_to_term`'s lazy vivification of
`env[i]` if NULL — but every reader vivifies-if-NULL and stores back the identical `term_new_var(i)`, so eliding
merely *defers an idempotent op*; a NULL slot and a vivified-unbound-var slot are observationally identical.
Holds regardless of the calling convention. Verified by the decisive probes: `unbound_arg` (`p(Y)` self-unify
elided, `Y` still binds to 5 downstream), `crossframe_bt` (sound across frames + backtracking), repeated-var
`eq(X,X)` (self-unify on arg0 + var-vs-var on arg1), and mixed `rec(zero,X,X)` (const-match + self-unify-elision
+ var-vs-var in one clause).

**Combined emission** (`rec(zero,X,X)`, the three shapes side by side): arg0 `zero` → `rt_pl_unify_const`;
arg1 `X` (first occ) → bare `jmp γ`; arg2 `X` (repeated) → general `node_to_term×2 + unify_terms` (the 7c gap).

## NEXT (per GOAL-PROLOG-BB.md)

**WAM-CP-7c — var-vs-var / `get_value`** (the last WAM-CP-7 slice). Shape: `IR_UNIFY(LOGICVAR(j),
LOGICVAR(i))` with i≠j — a repeated-var head arg (e.g. `eq(X,X)` arg2, `rec(_,X,X)` arg2). Mirror 7a's pattern:
add a runtime `rt_pl_unify_var_var(int slot_a, int slot_b)` that reads both env slots directly and calls the
same `mark+unify+unwind` (the general `unify`'s var-var branches are already optimal — bind one to the other,
trail iff `var_slot!=-1`), collapsing 3 calls → 1. Detect in `bb_unify.cpp` (both operands `IR_LOGICVAR`,
different slots) before the general path; TEXT + BINARY arms + the existing γ/ω tail. Provably `≡` the general
path (same `unify`). Prove with the same byte-identity discipline (GATE-1/GATE-3 unchanged + cross-mode probes
on repeated-var heads). Then WAM-CP-7 is fully closed.

Other open items unchanged: PLG-7 (remove `bb_node_state_t` — still blocked on Icon migration, live caller
`bb_exec.c:1589`), WAM-CP-9 (rest), WAM-CP-11 (deep-backtracking arg restore).

## Trigger phrases
- "perform hand off" = mark Goal done + update watermark + write this doc + commit per RULES.md (code repos first, `.github` last, `git pull --rebase && git push`).

## Session setup for next session
```bash
# Clone repos (token in URL):
git clone https://TOKEN@github.com/snobol4ever/SCRIP /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/.github /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/corpus /home/claude/corpus
# Git identity (all repos):
git config user.name "LCherryholmes"; git config user.email "lcherryh@yahoo.com"
# Build:
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh && make -j4 scrip && make libscrip_rt
# Canonical Prolog sources (consult before any unify/clause/control work — RULES.md):
#   gprolog: EnginePl/unify.c, EnginePl/wam_inst.{c,h}, Pl2Wam/code_gen.pl  (https://github.com/didoudiaz/gprolog)
#   swipl:   src/pl-vmi.c, src/pl-prims.c                                    (https://github.com/SWI-Prolog/swipl-devel)
#   plus GOAL-PROLOG-BB.md MANDATORY READ: SWIPL-STUDY / GPROLOG-STUDY docs.
# Gates: bash scripts/test_smoke_prolog.sh ; bash scripts/test_prolog_rung_suite.sh
# Single mode-4 run: bash scripts/run_prolog_via_x86_backend.sh <file.pl>   (all scrip calls need < /dev/null)
```
