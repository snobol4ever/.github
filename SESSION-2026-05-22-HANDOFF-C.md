# SESSION HANDOFF — 2026-05-22-C (session ~27, PL-T-1..3 + directives)

## Repos at handoff

| Repo | HEAD |
|------|------|
| SCRIP | `930df35a` |
| .github | `280c8c54` |
| corpus | `794dc0a` (unchanged this session) |

## Gates

**GATE-PK: PASS=419 FAIL=0 STUB=635** — up from 407 at session start.  
**smoke_prolog: PASS=5 FAIL=0** ✅  
Zero regressions.

## What was done this session

### Lon directives recorded
- **Invariant #14** — x86 only for BB template ladder. IS_JVM/JS/NET/WASM arms are stubs. Added to GOAL-BB-TEMPLATE-LADDER.md and GOAL-HEADQUARTERS.md.
- **Invariant #15** — All code emission goes through the template system via an XA_* opcode. Direct `fprintf`/`emit_textf` outside a template file = violation. Added to both files.
- **GOAL-PROLOG-BB-JCON.md → GOAL-PROLOG-BB.md** — JCON suffix removed (confusing). Applied twice; upstream session re-reverted once, re-applied. Current remote: `GOAL-PROLOG-BB.md`. PLAN.md updated.

### Build fix
PP-7 (`a3026409`) had already landed upstream fixing the same conflicting-decl issue we found. Rebased clean.

### PL-T-1 ✅ — `bb_pl_builtin.c`
`BB_PL_BUILTIN` x86 template: write/writeln (rt_pl_write_atom / rt_pl_write_var), nl (putchar 10), halt (exit 0), unknown (comment stub + succeed). Runtime helpers `rt_pl_write_atom` + `rt_pl_write_var` added to rt.c/rt.h.

### PL-T-2 ✅ — `bb_pl_var.c` + `bb_pl_atom.c` + `bb_pl_unify.c`
- `BB_PL_VAR` → `rt_pl_var_push(slot)`: deref g_pl_env[slot], push value
- `BB_PL_ATOM` → intern rodata + `rt_pl_atom_push(s)`
- `BB_PL_UNIFY` → three cases: VAR=ATOM (`rt_pl_unify_var_atom`), VAR=VAR (`rt_pl_unify_var_var`), generic (`rt_pl_unify_generic`)

### PL-T-3 ✅ — `bb_pl_arith.c` + `bb_pl_seq.c`
- `BB_PL_ARITH` → `rt_pl_arith(lk,li,ls,rk,ri,rs,op)`: resolves VAR slots, applies +/-/*/%, returns long
- `BB_PL_SEQ` → `rt_pl_seq_exec(goals,n)`: drives conjunction via C pump; NULL/0 = vacuous success (audit stub path)

All templates: x86 IS_TEXT arm only. IS_BIN/JVM/JS/NET/WASM return immediately.

## Architecture state

Every `BB_PL_*` kind now dispatched to its own template in `emit_core.c`:

| Kind | Template | Status |
|------|----------|--------|
| BB_PL_BUILTIN | bb_pl_builtin.c | ✅ PL-T-1 |
| BB_PL_VAR | bb_pl_var.c | ✅ PL-T-2 |
| BB_PL_ATOM | bb_pl_atom.c | ✅ PL-T-2 |
| BB_PL_UNIFY | bb_pl_unify.c | ✅ PL-T-2 |
| BB_PL_ARITH | bb_pl_arith.c | ✅ PL-T-3 |
| BB_PL_SEQ | bb_pl_seq.c | ✅ PL-T-3 |
| BB_PL_CALL | bb_pl.c (stub) | ⏳ PL-T-4 NEXT |
| BB_PL_CHOICE | bb_pl.c (stub) | ⏳ PL-T-5 |
| BB_PL_ALT | bb_pl.c (stub) | ⏳ PL-T-6 |
| BB_PL_CUT | bb_pl.c (stub) | ⏳ PL-T-7 |

## NEXT: PL-T-4 — `bb_pl_call.c`

`BB_PL_CALL` x86 template: predicate call dispatch.  
`nd->sval` = predicate name, `nd->n` = arity.  
Runtime helper `rt_pl_call(const char *name, int arity)` — look up `g_pl_bb_table`, drive via `bb_exec_once`. Mirror of `rt_pl_once` but called from within a BB graph (not from SM layer).

## Session start protocol for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus /home/claude/corpus
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip
bash scripts/test_per_kind_diff.sh
# Expect: PASS=419 FAIL=0 STUB=635 at SCRIP 930df35a
bash scripts/test_smoke_prolog.sh
# Expect: PASS=5 FAIL=0
```
