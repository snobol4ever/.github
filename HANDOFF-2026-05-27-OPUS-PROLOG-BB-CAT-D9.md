# HANDOFF 2026-05-27 — Opus — PROLOG-BB: CAT-D-9 (mode-4 12-comparison sweep, +4 rungs)

**Goal:** GOAL-PROLOG-BB.md — fix the ==/2 mode-4 always-succeeds bug flagged at the end of
the CAT-D-7..8 handoff. Discovered the bug applied to *all 12 comparison ops*, not just `==`.

**Result:** ✅ **+4 rungs in both --mode run and --mode compile.** GATE-1 5/5,
GATE-2 15→19/107 (+4), GATE-3 89/107 held, GATE-4 4/4 held. one4all `b1a37351`.

## Gate ledger (clean rebuild, this session)
- GATE-1 smoke prolog:        5/5 ✅
- GATE-3 rung interp:         89/107 ✅ (held — comparisons were already correct in --interp)
- GATE-4 mode-4 minimal:      4/4 ✅ (m4-seq, m4-call, m4-choice, m4-alt all hold)
- GATE-2 rung --mode run:     15 → **19/107** (+4)
- mode-4 rung suite --mode compile: 15 → **19/107** (+4 — same lift as run)
- Sibling smoke icon/snocone/raku/rebus: 5/5/5/4 ✅
- FACT RULE: grep returns 0 ✅ (100% byte emission via templates)

## What was wrong

The CAT-D-7..8 handoff caught one symptom: `( a == b -> write(yes) ; write(no) )` printed
`yes` in --run but `no` in --interp. The wider truth: **all 12 comparison operators**
(==, \==, @<, @>, @=<, @>=, =:=, =\=, <, >, <=, >=) had no template arm in
`bb_pl_builtin.cpp` and therefore fell through to:

```cpp
return hdr + s_1asm(emit_fmt("# PL_BUILTIN: unknown '%s' — stub", fn)) + succ_back;
```

where `succ_back = jmp γ; lbl_β: jmp γ;`. Every comparison silently succeeded.

Probed before fix:
- `( 5 < 3 -> write(yes) ; write(no) )` → `yes` (wrong; should be `no`)
- `( 3 < 5 -> write(yes) ; write(no) )` → `yes` (right by accident)
- `( b @< a -> write(yes) ; write(no) )` → `yes` (wrong)
- `( 1 =:= 2 -> write(yes) ; write(no) )` → `yes` (wrong)

## What landed (template-pure throughout — every emitted byte from a template)

### `bb_exec.c` — two effect helpers (+48 LOC)

```c
int rt_pl_term_cmp(const char *op, int k0, long i0, const char *s0, int k1, long i1, const char *s1);
int rt_pl_arith_cmp(const char *op, int k0, long i0, const char *s0, int k1, long i1, const char *s1);
```

- `rt_pl_term_cmp` dispatches op string → `pl_term_compare` (already in file at line 194) →
  returns 1/0 by op family. Handles ==, \==, @<, @>, @=<, @>=.
- `rt_pl_arith_cmp` calls a small static `rt_pl_arith_cmp_extract` to deref each side
  to a double (handles BB_LIT_I directly, plus BB_PL_VAR + BB_LIT_F via
  `rt_pl_node_to_term` → `term_deref`), then compares. Handles =:=, =\=, <, >, <=, >=.

Both are pure effect — no port logic, no γ/ω. Same shape as CAT-D-1..5 helpers.

Scope: scalar args (LIT_I, LIT_F, ATOM, PL_VAR). Compound term comparison
(`f(a) == f(a)`) requires emit-time term walk like CAT-D-7's `emit_write_term` —
deferred to CAT-D-9b.

### `bb_pl_builtin.cpp` — single template arm (+41 LOC)

```cpp
if (pBB->α && pBB->β && (strcmp(fn,"==")==0 || ... 11 other ops ...)) {
    BB_t *a0 = pBB->α, *a1 = pBB->β;
    /* flatten to k,i,s scalars; strtab_label for ATOM args */
    /* System V 7-scalar: rdi=op, rsi=k0, rdx=i0, rcx=s0, r8=k1, r9=i1, [rsp+0]=s1 */
    /* sub rsp,16 (8B data + 8B pad) — same pattern as atom_concat's 32B frame */
    const char *callee = is_arith ? "rt_pl_arith_cmp@PLT" : "rt_pl_term_cmp@PLT";
    return hdr
         + s_2asm("sub", "rsp, 16")
         + ... 7 arg loads ...
         + s_2asm("call", callee)
         + s_2asm("add", "rsp, 16")
         + s_2asm("test", "eax, eax")
         + s_2asm("je",   _.lbl_ω)
         + s_2asm("jmp",  _.lbl_γ)
         + s_L2asm(emit_fmt("%s:", _.lbl_β), "jmp", _.lbl_ω);
}
```

Op string interned automatically by existing `pl_pre_intern_pred_names` flow —
`BB_BUILTIN` is in `pl_ir_kind_uses_sval` (`emit_sm.c:295`), so `nd->sval` (= `"=="` etc.)
hits `strtab_intern` before any template runs. Template's `strtab_label(op_lbl, sizeof, fn)`
resolves cleanly.

### `bb_exec.h` — 5 lines of decls.

## What flipped

```
--- New PASSes ---                              --- Lost PASSes ---
PASS rung04_arith_arith                         PASS rung26_copy_concat_copy_term
PASS rung16_atop_at_ge                                (was spurious — relied on ==-always-succeeds)
PASS rung16_atop_at_gt
PASS rung16_atop_at_le
PASS rung16_atop_at_lt
```

Net: +5 genuine -1 spurious = **+4 honest**. The rung26 copy_term loss reveals a
pre-existing mode-4 gap (`copy_term(f(X,X), f(A,B))` doesn't share var identity between
A and B in --run, so `A == B` correctly says `diff` instead of `same`). That gap was
masked by the always-succeeds bug; now that `==` tells the truth, the gap surfaces.

The smoking gun: `rung04_arith_arith.pl` literally tests `(3 < 5 -> true ; false)` AND
`(5 < 3 -> true ; false)`. Before: both printed `true`. Now: `true` then `false`.

## Discipline check

- 100% byte emission via templates: `grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob' src/`
  outside `*_templates/` + `emit_core.c` returns 0 ✅
- No C Byrd boxes added ✅
- Four Greek port names (α/β/γ/ω) throughout ✅
- No SM/BB walking at runtime in modes 3/4 — all BB walking happens at emit time ✅
- New helpers are pure effect (no port logic) ✅

## NEXT SESSION — recommended order

1. **CAT-D-9b — compound-term comparison.** `rung26_copy_term` will not recover until both
   compound `==` works AND copy_term's var-identity gap is fixed. Compound `==` needs an
   emit-time recursive walker similar to CAT-D-7's `emit_write_term` — flatten both
   compound subgraphs to Terms inline (recurse on BB_PL_STRUCT children via α + γ chain),
   then call `pl_term_compare`. The flat-scalar helper signature can't carry compound shape,
   so the walker emits a sequence of `term_new_compound` calls building both sides on the
   stack before comparing. Same shape as `emit_write_term` but constructive instead of
   destructive.

2. **CAT-D-6 atom_chars/atom_codes mode-4.** Bigger surface (list cons-cell construction).
   Goal file flagged this from previous handoff.

3. **CAT-A-3 BB_PL_CALL + BB_CHOICE β-resume.** Blocked on Lon directive on design (two
   options: inline-on-demand multi-clause vs resumable-call protocol). Large structural
   unlock estimated at +15–25 PASS.

4. **Investigate rung26 copy_term var-identity gap.** Once compound `==` works, this is
   the remaining piece. Likely in how mode-4 `copy_term` reuses (or fails to reuse) the
   slot mapping for aliased vars.

## Files touched

- one4all `b1a37351` CAT-D-9: bb_exec.c (+48), bb_exec.h (+5), bb_pl_builtin.cpp (+41) — 3 files, +94 LOC

## Reproducible probe

```bash
cd /home/claude/one4all
apt-get install -y libgc-dev
bash scripts/build_scrip.sh
make libscrip_rt

bash scripts/test_smoke_prolog.sh                              # 5/5
bash scripts/test_prolog_mode4_rung.sh                         # 4/4
bash scripts/test_prolog_rung_suite.sh --mode interp 2>&1 | tail -1   # 89/107
bash scripts/test_prolog_rung_suite.sh --mode run     2>&1 | tail -1   # 19/107
bash scripts/test_prolog_rung_suite.sh --mode compile 2>&1 | tail -1   # 19/107
```
