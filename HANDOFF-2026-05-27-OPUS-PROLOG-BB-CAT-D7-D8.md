# HANDOFF 2026-05-27 — Opus — PROLOG-BB: CAT-D-7 + CAT-D-8 (+4 rungs)

**Goal:** GOAL-PROLOG-BB.md — fix two pre-existing mode-4 gaps the goal file flagged.

**Result:** ✅ **+4 rungs in both --mode run and --mode compile.** GATE-1 5/5, GATE-3 88→89,
GATE-4 4/4 held, GATE-2 11→15, mode-4 rung suite 11→15. SCRIP `710ee0b0`.

## Gate ledger (clean rebuild, this session)
- GATE-1 smoke prolog: 5/5 ✅
- GATE-3 rung interp:  88 → **89/107** (+1 ITE wrapper unblocks one mode-2 path)
- GATE-4 mode-4 minimal: 4/4 ✅ (m4-seq, m4-call, m4-choice, m4-alt all hold)
- GATE-2 rung --mode run: 11 → **15/107** (+4)
- mode-4 rung suite --mode compile: 11 → **15/107** (+4 — same 4 unlocks as run)
- Sibling smoke icon/snocone/raku/rebus: 5/5/5/4 ✅

## What landed (template-pure throughout — every emitted byte from a template)

### CAT-D-7 (`d2ce06fc`) — write(compound) mode-4
The bb_pl_builtin write/1 TEXT arm had a `# unknown` comment stub for any arg kind that wasn't
BB_ATOM or BB_PL_VAR. So `write(foo(1,2))` silently emitted nothing in mode-4 even though
mode-2 rendered it correctly.

Three minimal runtime helpers added in `rt.c`:
- `rt_pl_write_int(long)` — `printf("%ld", v)`
- `rt_pl_write_float(double)` — `printf("%g", v)`
- `rt_pl_write_cstr(const char *)` — `fputs(s, stdout)` for ( , ) punctuation rail

Punctuation strings `(` `,` `)` pre-interned in `pl_pre_intern_pred_names` so any Prolog compile
has them in the strtab — `strtab_label("(") → ".S1"` etc.

`bb_builtin.cpp` gains static helper `emit_write_term(BB_t *)` that, at emit time, walks
BB_PL_STRUCT → α → γ → γ recursively, producing an asm string of rt_pl_write_* calls
interleaved with cstr-loaded punctuation. The existing write arm dispatches to it for
BB_PL_STRUCT and BB_LIT_I (atom + var paths unchanged). All bytes via s_2asm / s_1asm —
zero seg_byte / SL_B outside templates.

Probe pass (byte-exact vs --interp): `foo(1,2)`, `foo(a,b)`, `point(1,2,3)`,
`tree(node(1),node(2))` (nested), `empty` (atom path unchanged).

### CAT-D-8 (`710ee0b0`) — BB_PL_ITE wrapper for mode-4 if-then-else
The if-then-else `(Cond -> Then ; Else)` previously lowered by returning the bare Cond node as
both retval and *α_out, with node-pointer γ→Then and ω→Else. Mode-2 `bb_exec_once` follows
node-pointer γ → worked. Mode-4 `walk_bb_flat` ignores node-pointer γ for non-resumable kinds —
it uses the caller's outer γ/ω labels. So Cond's success in mode-4 jumped directly to the OUTER
SEQ's γ continuation, skipping Then entirely. Affected EVERY ITE — `( true -> a ; b )`,
`( 3 < 5 -> a ; b )`, `( a == a -> a ; b )` — all silently emitted no output.

Fix mirrors CAT-A's BB_PL_SEQ wrapper pattern:
- New `BB_PL_ITE` enum + `bb_pl_ite_state_t { cond, then_, else_ }` in BB.h.
- `lower_pl.c`: ITE lowering allocates BB_PL_ITE wrapper, stashes state in `ival`, returns
  wrapper as both retval and *α_out. The enclosing SEQ now sees `gnodes[i] = BB_PL_ITE`.
- `bb_exec.c`: trivial case `BB_PL_ITE → return nd->α` (mode-2 inherits port-pointer walk
  semantics — Cond's own γ/ω node pointers still drive Then/Else).
- `emit_bb.c`: byte-free `flat_drive_pl_ite` mints `xite%d_then_α / else_α` labels; walks Cond
  with γ=then_α / ω=else_α; then defines then_α and walks Then with outer γ/ω; ditto else_α
  and Else. `EP_FILL` emits the wrapper's β-tombstone via the bb_pl_ite.cpp template at the END
  (mirrors `flat_drive_cat` / `flat_drive_pl_seq` — tombstone AFTER bodies).
- `bb_pl_ite.cpp`: new template. Body is just the β-tombstone via EP channel (the wrapper's α
  label is already defined by the SEQ outer driver before walk_bb_flat invokes the dispatcher,
  so the template doesn't re-emit it).
- `bb_templates.h`: declaration. `emit_core.c`: dispatch. `Makefile`: build entry.

Probe pass (byte-exact vs --interp): `(true -> yes ; no)`, `(fail -> yes ; no)`,
`(1 =:= 1 -> yes ; no)`, `(3 < 5 -> yes ; no)`, `(a == a -> yes ; no)`. One fail revealed an
**orthogonal** bug: `( a == b -> ... )` returns `yes` instead of `no` in mode-4 — the `==/2`
template arm always succeeds regardless of atom identity. Not an ITE issue.

## Discipline check
- 100% byte emission via templates: `grep -rnE 'seg_byte\(SEG_CODE|SL_B\(|sl_emit_one|emit_standard_blob' src/`
  outside `*_templates/` + `emit_core.c` returns 0 ✅
- No C Byrd boxes added ✅
- Four Greek port names (α/β/γ/ω) throughout ✅
- No SM/BB walking at runtime in modes 3/4 — all BB walking happens at emit time ✅
- mode-2 BB executor's BB_PL_ITE case is `return nd->α` — same shape as BB_PL_SEQ ✅

## NEXT SESSION — recommended order

1. **==/2 mode-4 always-succeeds bug.** The handoff probe revealed this. Look in
   `bb_builtin.cpp` for the `==` arm (or wherever pl_runtime renders `==/2`). The fix is
   probably small and unlocks several puzzle rungs that compare atoms in ITE conditions.

2. **CAT-D-6 atom_chars/atom_codes mode-4.** Goal file note: "bigger surface due to list
   cons-cell construction." Likely needs a new rt_pl_atom_to_list helper that builds
   cons cells via existing term_new_* primitives.

3. **CAT-A-3 BB_PL_CALL + BB_CHOICE β-resume.** Blocked on a Lon directive on design.

4. **Investigate which 4 rungs unlocked.** Compare the list of mode-4 PASSes before
   (commit `cc5415c4`) vs now (`710ee0b0`); diff tells you which constructs CAT-D-7/D-8
   actually unblocked.

## Files touched
- SCRIP `d2ce06fc` CAT-D-7: rt.c, emit_sm.c, bb_builtin.cpp (3 files, +98 LOC)
- SCRIP `710ee0b0` CAT-D-8: BB.h, lower_pl.c, bb_exec.c, emit_bb.c, emit_core.c,
  bb_templates.h, bb_pl_ite.cpp (new), Makefile (8 files, +117 / -12 LOC)
