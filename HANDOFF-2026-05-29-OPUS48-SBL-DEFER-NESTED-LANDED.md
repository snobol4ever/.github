# HANDOFF — SNOBOL4-BB SBL-DEFER-NESTED — nested `*var` (XDSAR/DEFER) works native

**Author:** Claude Opus 4.8
**Date:** 2026-05-29
**Goal:** GOAL-SNOBOL4-BB.md — REAL BLOCKER: nested XDSAR (`*var`) inside a combinator under `sm_run_native`
**Repos touched:** one4all (`d2e88c72`, 3 source files), .github (`d10b56bd`: PLAN.md, GOAL-SNOBOL4-BB.md, this doc)
**Scope this session:** modes 2 and 3 only — mode 4 deferred per Lon ("we will run mode 4 pass way later").

---

## What landed

A nested deferred pattern reference — a `*var` (XDSAR → `BB_PAT_DEFER`) that is **not** the
top-level node, e.g. `SUBJ POS(0) *WORD` — matched correctly in mode-2 but failed under
`sm_run_native`. It now matches natively, with the string-valued and pattern-valued deref
forms, the capture-of-deref form, and the deref-as-ALT-alternative form all in agreement m2==m3.

**Native broad: 223 → 243 (+20). Mode-2 broad: also 223 → 243 (+20)** — both measured against
the *live* one4all base `30e7c0a1` (see "Sibling regression" below). Zero mode-2/3 regression
introduced by this commit. Newly native: 056, 070-073, 108, 110-112, 115, 128, 132-138, 144,
147, plus the fence/arbno-over-defer family (068, 117, 143, 150) which no longer SIGSEGV.

Gates: smoke 13/13 (m2) + 13/13 (native), rung M2=19/19, FACT=0, `audit_m3_native` GATE OK.

## Root cause — three coordinated gaps (all probe-confirmed, not hypothesized)

The prior handoff's "two-part fix" (gate + BINARY arm) was **necessary but not sufficient** and
mis-stated the mechanism. The actual chain, isolated by neutralizing each piece and re-probing:

1. **Missing flat-driver dispatch.** `walk_bb_flat` (src/emitter/emit_bb.c) had **no
   `case BB_PAT_DEFER`**, so DEFER fell to `default:` (`emit_label_define_bb(β); jmp ω; jmp ω`)
   and never reached `FILL` → never reached the template. The node degenerated to a zero-width
   no-op: `POS(0) *WORD RPOS(0)` on a *non-matching* subject reported MATCH (a **false match** —
   which had quietly inflated an earlier measurement). A `[DEFER]` stderr probe in
   `rt_defer_match` confirmed the helper was never called on the γ-chain path.

2. **Wrong builder shape.** `patnd_to_bb_graph` (the translator the BROKERED branch of `exec_stmt`
   used for defer-bearing trees) builds a **γ-pointer chain** (the mode-2 `bb_exec` walker's
   shape). But the flat/brokered driver `walk_bb_flat`/`flat_drive_cat` traverses **kids**
   (`bb_pat_kid`), not γ pointers. So `POS.γ → DEFER` was never followed: `walk_bb_flat(POS)`
   emitted POS and wired its γ to the box epilogue, dropping DEFER → bare `POS(0)`. The kid-tree
   builder `patnd_to_bb_tree`/`build_patnd_tree` is the one the flat driver consumes (its
   `default:` arm already delegates XDSAR → `build_patnd` → `BB_PAT_DEFER` leaf).

3. **Empty + then misaligned BINARY arm.** `bb_pat_defer.cpp`'s MEDIUM_BINARY arm was empty.
   Once filled, a single `push r10` before `call rt_defer_match` left `rsp` misaligned at the
   call (brokered box prologue `push rbp; mov rbp,rsp` makes body-entry `rsp%16==0`; one `push r10`
   → `rsp%16==8` at the call → callee entry `rsp%16==0`, one slot off SysV). The string-valued
   path (`strncmp`) tolerated it, but the **pattern-valued** path recurses
   `rt_defer_match → exec_stmt → bb_broker` and hit an aligned SSE store → SIGSEGV (the exact
   Icon IBB-8a class). This is why 068/117/143/150 — `*var` resolving to a FENCE/ARBNO/ALT
   pattern used as a brokered child via `pre_build_children → bb_build_brokered(DEFER)` — crashed.

## The fix (3 files, template-pure)

**`src/emitter/emit_bb.c`** — add `case BB_PAT_DEFER: FILL(nd, lbl_γ, lbl_ω, lbl_β); break;` to
`walk_bb_flat` (DEFER is a single-attempt leaf, routes like `BB_PAT_LIT`). This is the true
missing wire → `FILL` → `walk_bb_node` → `emit_core.c:575` → `bb_pat_defer(nd)` → the template.

**`src/runtime/snobol4/stmt_exec.c`** —
- new `patnd_contains_defer(pp)` recursive helper; wired into `patnd_needs_xlate`.
- XDSAR added to `patnd_is_simple_atom` (so it is tree-eligible and `patnd_is_combinator_root`
  fires on XCAT/XOR/XNME/XFNME-over-defer).
- BROKERED branch made surgical: `int defer_combinator = patnd_contains_defer(pp) &&
  patnd_is_combinator_root(pp);` — if set, build via `patnd_to_bb_tree` (kid-tree, so DEFER
  survives the flat walk); otherwise keep the existing `patnd_to_bb_graph` / legacy-cast path.
  **Only defer combinator roots divert**; all other trees are untouched, so the
  legacy-cast-compensated XCAT/fence/capture trees are not disturbed.

**`src/emitter/BB_templates/bb_pat_defer.cpp`** — MEDIUM_BINARY arm (67 bytes), flat-shaped like
`bb_pat_pos`/`bb_lit`, with **bulletproof 16-byte alignment** around the call (works in both the
flat-slab and brokered-child entry contexts, which have different entry alignment):

```
[0-9]   48 BF +u64(&vname)   movabs rdi,&vname     ; pBB->sval (stable, JIT in-process)
[10-14] BE   +u32(ival)      mov    esi,ival
[15-17] 41 8B 12             mov    edx,[r10]       ; Δ = cur_delta
[18-27] 48 B8 +u64(&fn)      movabs rax,&rt_defer_match
[28-29] 41 52                push   r10             ; save Δ ptr
[30]    53                   push   rbx             ; callee-saved (survives the C call)
[31-33] 48 89 E3             mov    rbx,rsp
[34-37] 48 83 E4 F0          and    rsp,-16         ; force 16-align
[38-39] FF D0                call   rax
[40-42] 48 89 DC             mov    rsp,rbx         ; restore
[43]    5B                   pop    rbx
[44-45] 41 5A                pop    r10
[46-47] 85 C0                test   eax,eax
[48-49] 0F 88; [50-53] rel32 js     → ω             ; site 50
[54-56] 41 89 02             mov    [r10],eax        ; Δ = new delta
[57] E9; [58-61] rel32       jmp    → γ             ; site 58
[62] E9 (β-define); [63-66]  jmp    → ω             ; site 62 (is_def) / site 63
```
`bin = {{50,58,62,63}, {ω,γ,β,ω}, {false,false,true,false}}`. `rt_defer_match` (rt.c:693, already
existed) resolves the var and matches a string literal (strncmp) OR a sub-pattern (exec_stmt),
returning new Δ or -1. `extern "C"` decl added so the arm can bake `&rt_defer_match` (cf. bb_lit
baking `&memcmp`).

**FACT / purity:** every byte is produced inside the template's MEDIUM_BINARY arm reached via
`emit_core` dispatch; no `seg_byte`/`SL_B`/`emit_standard_blob`; FACT grep = 0; audit GATE OK.

## Verification (discriminating, m2 == m3)

```
POS(0) *WORD            cat/cat   → MATCH  (string deref, positive)
POS(0) *WORD RPOS(0)    cat       → MATCH
POS(0) *WORD RPOS(0)    xyz/cat   → NOMATCH (was false MATCH before the wire/align fix)
("x" | *W)              dog       → M       (deref as ALT alternative)
(*W . V)                dog       → dog     (capture of deref)
056 *PAT . V                      → hello
068/117/143/150 (fence/arbno-over-deref)  → no SIGSEGV, m2==m3
```
Regression diff vs live base `30e7c0a1`: empty FAIL-line regression set; net +20 = exactly the
20 gains (arithmetic-confirmed zero true regression). word1-4 etc. that appear in a naive
FAIL-line `comm` were the ~17 baseline crashes (PASS=223 but only 40 FAIL-lines printed) now
surfacing as FAIL-lines — already failing at baseline, not regressions.

## ⚠ Sibling regression (NOT this goal — flag for cross-goal review)

The original SNOBOL4 mode-2 baseline at `baf8397d` was **252**. A sibling Raku commit
(one4all `30e7c0a1` "RK-BB-4 mode-2 junctions + mode-2 gather + ACOMP") regressed SNOBOL4 mode-2
**252 → 223** via shared `bb_exec.c` (BB_SEQ Raku-gather driver) and/or `SM_ACOMP` coercion in
`sm_interp.c`. This goal's defer fix then recovered **223 → 243**. The residual **243 < 252** gap
is the sibling's, not this commit's. Whoever owns Raku BB / shared-runtime should diff
`30e7c0a1` against `c64b4770`'s parent on the SNOBOL4 mode-2 corpus to find the −9 (the Raku
session reported "zero regression on SNOBOL4 crosscheck" via a narrow stash check; the broad
corpus tells a different story).

## NEXT

- **Capture/ALT-over-deref edge cases** beyond the proven set: deeply-nested defer under
  multiple combinators where `patnd_is_combinator_root` returns false (the `defer_combinator`
  gate then falls back to the γ-chain and drops DEFER again). If more star_var corpus tests
  remain native-fail, widen the tree-route condition carefully (watch the legacy-cast trees).
- **Mode-4 (deferred):** when mode-4 work resumes, the `bb_pat_defer.cpp` **TEXT arm** still uses
  the old `push r10; call rt_defer_match@PLT; pop r10` and will SIGSEGV on pattern-valued derefs
  in the mode-4 standalone the same way the BINARY arm did — apply the same `and rsp,-16`
  alignment. Also re-gate mode-4 (146/152/1011/1017 were perturbed by an earlier broad gate and
  must be re-measured against the surgical `defer_combinator` gate that actually landed).
- **Cross-goal:** the sibling mode-2 −9 above.

## Key files / line anchors

- Flat driver dispatch: `src/emitter/emit_bb.c` `walk_bb_flat` (`case BB_PAT_DEFER`)
- Gate + BROKERED routing: `src/runtime/snobol4/stmt_exec.c` (`patnd_contains_defer`,
  `patnd_is_simple_atom`, `defer_combinator` in the BROKERED branch)
- Template: `src/emitter/BB_templates/bb_pat_defer.cpp` (MEDIUM_BINARY arm)
- Runtime helper: `src/runtime/rt/rt.c:693` `rt_defer_match` (string + sub-pattern semantics)
- m2 oracle (semantic spec): `src/lower/bb_exec.c:2861` `case BB_PAT_DEFER`
- Tree builder: `src/lower/lower_pat_dcg.c:541` `build_patnd_tree` (XDSAR via `default:`),
  `:309` `build_patnd` (XDSAR → BB_PAT_DEFER at `:468`)
- emit_core dispatch: `src/emitter/emit_core.c:575`
