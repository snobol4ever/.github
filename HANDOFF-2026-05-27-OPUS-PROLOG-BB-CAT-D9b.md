# HANDOFF 2026-05-27 — Opus — PROLOG-BB: CAT-D-9b (compound-term == correctness)

**Goal:** GOAL-PROLOG-BB.md — close the compound-term `==` correctness gap CAT-D-9 left
behind. CAT-D-9 only handled scalar args via flat (k,i,s) triples; compound operands fell
into `rt_pl_node_to_term`'s default arm and were squashed to `term_new_int(arity)`, which
made every compound look identical to every other compound of the same arity.

**Result:** ✅ Correctness fix landed. **0 rung delta** (corpus doesn't exercise
compound-`==` directly), but every probe in a 7-test compound-comparison battery is now
byte-identical between `--interp` and `--run`. All gates held. one4all `e15e86b0`.

## Gate ledger (clean rebuild, this session)
- GATE-1 smoke prolog:        5/5 ✅ held
- GATE-2 rung --mode run:     19/107 ✅ held
- GATE-3 rung interp:         89/107 ✅ held
- GATE-4 mode-4 minimal:      4/4 ✅ held
- mode-4 rung suite:          19/107 ✅ held
- Crosscheck (interp vs run): 52 PASS held
- Sibling smoke icon/snocone/raku/rebus: 5/5/5/4 ✅
- FACT RULE: 0 ✅

## What was wrong

CAT-D-9 closed the always-succeeds bug on the 12 comparison ops for scalar args
(LIT_I/LIT_F/ATOM/PL_VAR). But its helpers `rt_pl_term_cmp(op, k0,i0,s0, k1,i1,s1)`
take flat scalar triples — no way to carry compound structure. So:

```c
case BB_ATOM:  return term_new_atom(prolog_atom_intern(sval ? sval : "[]"));
case BB_LIT_F: return term_new_float(dval);
case BB_LIT_I: return term_new_int(ival);
default:       return term_new_int(ival);   // ← compound falls here
```

For a `BB_PL_STRUCT` operand, `rt_pl_node_to_term` returned `term_new_int(arity)`. Then
`pl_term_compare` compared two ints. Probe before fix:
- `f(a,b) == f(a,b)` → `same` (right by accident — both squashed to int(2))
- `f(a,b) == f(a,c)` → `same` (wrong — should be `diff`)
- `[1,2,3] == [1,2,4]` → `same` (wrong — should be `diff`)
- `point(1,2) == point(1,3)` → `same` (wrong)

## What landed (template-pure throughout — every emitted byte from a template)

### `bb_exec.c` — two new pure-effect helpers (+26 LOC)

```c
void *rt_pl_compound_build_n(const char *functor_name, int arity, void *args_ptr);
int   rt_pl_term_cmp_terms(const char *op, void *t0, void *t1);
```

- `rt_pl_compound_build_n` intern's the functor name, GC_MALLOCs an args array, copies
  the N Term* from the caller's stack-resident slot array, calls `term_new_compound`.
- `rt_pl_term_cmp_terms` is identical to `rt_pl_term_cmp` but takes two pre-built Term*
  instead of two scalar triples. Same op-string dispatch.

Both have zero port logic. Used only for the 6 term-compare ops on compound args; the 6
arith-compare ops (=:=/=\=/</>/<=/>=) on compounds is illegal in Prolog and stays on the
scalar fast path (will fail-extract → ω, semantically correct).

### `bb_pl_builtin.cpp` — emit-time walker + compound-arm wiring (+85 LOC)

```cpp
static std::string emit_build_compound_term(const BB_t *nd) {
    // Leaves (LIT_I/LIT_F/ATOM/PL_VAR): emit call rt_pl_node_to_term → rax = Term*.
    // BB_PL_STRUCT with arity N:
    //   1. frame = aligned(N*8) to 16
    //   2. sub rsp, frame
    //   3. for i in 0..N-1: recursively build child[i] (rax), mov [rsp+i*8], rax
    //   4. lea rdi, [rip + functor_strtab_label]
    //   5. mov esi, N
    //   6. mov rdx, rsp
    //   7. call rt_pl_compound_build_n@PLT  →  rax = Term*
    //   8. add rsp, frame
}
```

Wired into the comparison arm BEFORE the CAT-D-9 scalar fast path:

```cpp
if (pBB->α && pBB->β
    && (pBB->α->t == BB_PL_STRUCT || pBB->β->t == BB_PL_STRUCT)
    && (term-compare op)) {
    // sub rsp, 16
    // <emit_build_compound_term(pBB->α)>   ; rax = t0
    // mov [rsp + 0], rax                    ; save t0
    // <emit_build_compound_term(pBB->β)>   ; rax = t1; inner builds preserve [rsp+0]
    // mov rdx, rax                          ; t1 → arg3
    // mov rsi, [rsp + 0]                    ; t0 → arg2
    // lea rdi, [rip + op_lbl]               ; op  → arg1
    // call rt_pl_term_cmp_terms@PLT
    // add rsp, 16
    // standard test eax / je ω / jmp γ / β-tombstone
}
```

Stack safety: outer frame `[rsp+0]` is preserved across the second `emit_build_compound_term`
call because every recursive walker invocation is balanced (`sub rsp, frame` matched by
`add rsp, frame`).

### `bb_exec.h` — 5 lines of decls.

## Verification probe (all byte-identical to --interp)

```
f(a,b)==f(a,b)              → same
f(a,b)==f(a,c)              → diff   (was `same` before fix — the smoking gun)
[1,2,3]==[1,2,3]            → same
[1,2,3]==[1,2,4]            → diff   (was `same` before fix)
f(g(x),y)==f(g(x),y)        → same   (3-level nesting via walker recursion)
f(g(x),y)==f(g(z),y)        → diff
a == f(a)                   → diff   (mixed atom-vs-compound class)
point(1,2) @< point(1,3)    → lt     (compound @< works too)
```

No rung in the current corpus uses compound-== directly, so PASS count unchanged.
The fix is correctness insurance for any future rung that does.

## Discipline check

- 100% byte emission via templates: `grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob' src/`
  outside `*_templates/` + `emit_core.c` returns 0 ✅
- No C Byrd boxes added ✅
- Four Greek port names (α/β/γ/ω) throughout ✅
- No SM/BB walking at runtime in modes 3/4 — walker runs at emit time only ✅
- New helpers are pure effect (no port logic) ✅

## NEXT SESSION — recommended order

1. **CAT-D-6 — atom_chars/atom_codes mode-4.** Bigger surface: bidirectional list↔atom
   needs cons-cell construction (forward: atom → `.(c1,.(c2,...,[]))`) and list traversal
   (backward: list → atom). The cons-cell construction can reuse `rt_pl_compound_build_n`
   from CAT-D-9b for `.(H,T)` — that helper is now general-purpose for any compound.

2. **CAT-A-3 — BB_PL_CALL + BB_CHOICE β-resume.** Blocked on Lon directive on design
   (inline-on-demand vs resumable-call protocol). Large structural unlock; +15-25 PASS
   estimated.

3. **rung26_copy_term independent gap.** Not a compound-== issue (CAT-D-9b verified to
   be correct). The gap: `copy_term(f(X,X), f(A,B))` should make A and B alias to the
   same fresh var so `A == B` succeeds. In mode-4 `--run` it currently doesn't. Either
   `bb_copy_term` doesn't share var renaming correctly, or the renamed Terms aren't
   landing in `g_pl_env[slot_A]` and `g_pl_env[slot_B]` as aliases.

4. **Latent bug: lower_pl.c:65 garbage `sval` on BB_PL_VAR.** Goal file note from
   CAT-D-1. One-line fix; do alongside next CAT-D work.

## Files touched

- one4all `e15e86b0` CAT-D-9b: bb_exec.c (+26), bb_exec.h (+5), bb_pl_builtin.cpp (+85) — 3 files, +116 LOC

## Reproducible probe

```bash
cd /home/claude/one4all
apt-get install -y libgc-dev
bash scripts/build_scrip.sh && make libscrip_rt

bash scripts/test_smoke_prolog.sh                                      # 5/5
bash scripts/test_prolog_mode4_rung.sh                                 # 4/4
bash scripts/test_prolog_rung_suite.sh --mode interp  2>&1 | tail -1   # 89/107
bash scripts/test_prolog_rung_suite.sh --mode run     2>&1 | tail -1   # 19/107
bash scripts/test_prolog_rung_suite.sh --mode compile 2>&1 | tail -1   # 19/107

# Compound == correctness probe (should all match):
for expr in 'f(a,b)==f(a,b)' 'f(a,b)==f(a,c)' '[1,2,3]==[1,2,3]' '[1,2,3]==[1,2,4]' \
            'f(g(x),y)==f(g(x),y)' 'f(g(x),y)==f(g(z),y)' 'point(1,2)@<point(1,3)'; do
    echo "main :- ( $expr -> write(y) ; write(n) ), nl." > /tmp/p.pl
    a=$(./scrip --interp /tmp/p.pl 2>/dev/null)
    b=$(./scrip --run    /tmp/p.pl 2>/dev/null)
    printf "%-35s interp=%s run=%s %s\n" "$expr" "$a" "$b" "$([ "$a" = "$b" ] && echo OK || echo DIFF)"
done
```
