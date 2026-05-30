# HANDOFF-2026-05-30-OPUS48-LANG-INDEP-RENAME-SLICE-2

**Session:** Opus 4.8, 2026-05-30 (continues SLICE-0-1 handoff)
**one4all HEAD:** `bf3f7928` (== origin/main) — was `d7f64afa` (Slice 1b) at session start
**.github HEAD:** (see git log — this handoff + GOAL update)
**Goal:** GOAL-LANG-INDEPENDENT-RENAME.md

---

## What this session did

Landed **Slice 2 (Icon)** gate-green and pushed, then **audited Slice 3 (Prolog)** to
decision-ready. Slice 3 is **NOT a clean blanket** — it needs Lon to ratify three things
before it can execute (below). Stopped on green rather than make those calls unilaterally
under budget pressure ("never a broken commit").

### ✅ Slice 2 — Icon (`bf3f7928`, was `d7f64afa`) — gate-green, pushed

**Rule applied:** `icn_/icon_ → gen_` (mirrors the `core_` namespace from Slice 1b; the runtime
stems — `call`, `type`, `frame`, `leaf`, `out` — are too generic to bare-strip).

**Files (git mv, 7):**
- `interp/icn_runtime.c/.h → gen_runtime.c/.h`
- `interp/icn_value.h → gen_value.h`
- `interp/icon_box_rt.h → box_rt.h`
- `interp/icon_gen.h → gen.h`
- `lower/lower_icn.c/.h → lower_graph.c/.h`
- `lower/lower_icn_bb.h → lower_graph_bb.h` — an **ORPHAN doc-stub** (no includers). Found only
  because its `icn` is **mid-name, not a prefix**, so `find -name 'icn_*'` missed it. Lesson:
  grep the substring, don't trust a prefix glob, when sweeping a stage for stragglers.

Include guards renamed to match (`ICN_RUNTIME_H → GEN_RUNTIME_H`, etc.). 4 Makefile refs
(source lists 176/179, obj recipes 385/398) + every `#include` site updated.

**Symbols:** blanket `s/icn_/gen_/g; s/icon_/gen_/g` over post-AST (everything **except**
`src/frontend/`). Covered `icn_bb_*`, the `icon_*_new` emitter ctors (in `emit_bb.c`), the
`_icn_*` driver hooks (`polyglot.c`, `scrip.c`), the `*_state_t` types, and `icn_bb_dcg`
(defined post-AST in `icn_runtime.c:333`).

**9 frontend exemptions reverted** (def-site in `src/frontend/`, but called from post-AST):
- `icn_cset_{canonical,complement,diff,inter,union}` — def `src/frontend/icon/icon_runtime.c`
- `icon_compile`, `icon_driver`, `icon_lex` — Icon parser API
- `g_icn_jcon` — lexer↔coerce global (def `icn_runtime.c:1880`, used in frontend `icon_lex.c`)

The pre-mutation guard caught 7 post-AST `#include`s of the frontend
`frontend/icon/icon_{driver,lex}.h`; the `\bgen_driver\b` / `\bgen_lex\b` reverts repaired them
(the revert boundaries align on `/` and `.`). `gen_` verified collision-free against the existing
`gen_resume / gen_chain_entry / gen_assign / gen_depth / gen_ast / gen_a / gen_b`.

**Result:** 51 files, 1007/1007 lines (pure rename — `git show --stat` is symmetric).

### Gates — green (Slice 2, identical to baseline → zero regression)
`make scrip` rc=0 · `make libscrip_rt` rc=0 · **Icon smoke m2 6/6 (HARD)**, m3 2/6 · FACT=0 ·
sm_dead 1/1 · runtime_isolation rc=0 · stage2_isolation rc=0 · lower_isolation **unchanged**
(same pre-existing `src/lower/lower.c:17 → frontend/raku/raku_re.h` that is already in HEAD and
is NOT in the slice gate — must not *worsen*, and didn't).

---

## Gotcha discovered this session (added to the GOAL — read before any slice)

5. **⚠ `grep -o` on MULTIPLE files PREFIXES each match with `filename:`.** So identifier
   extraction and set-intersections (the cross-boundary symbol hunt) **silently break** — you
   get `path/file.c:icn_foo` tokens that match nothing. **Use `grep -oh`** (and keep `-a` from
   Gotcha 4 for the α/β/γ/ω UTF-8-"binary" files → `grep -aohE`). This (not Gotcha 4) is what
   produced a false "cross-boundary = 0" mid-audit.

(Gotchas 1–4 from the prior handoff still all apply: judge scope by DEFINITION site; re-check
frontend headers after a rename; collision scans are noisy → namespace generic stems; `grep -a`
always. Also: the bash subshell is `sh` — no `<(...)`, no `column`; use temp files + `grep -Fxf`
instead of `comm`.)

---

## ⚠ Slice 3 — Prolog — AUDITED, decision-ready, NOT yet executed

Audited at `bf3f7928`. **Tractable but not a blanket.** Three ratifications needed from Lon
before bulk rename:

**(i) Namespace.** `pl_ → resolve_` is **collision-free** (0 existing `resolve_`), mirrors
`core_`/`gen_`, and matches the already-ratified file rename `pl_runtime → resolve_runtime`.
**Recommend `resolve_`.** A bare strip (per the GOAL's `pl_unify → unify` rule) collides on ~24
generic stems: write / writeq / write_canonical / copy_term / functor / univ / arg / args /
trail_mark / nb_getval / nb_setval / choice / builtin / leaf / key / cs / locals / …

**(ii) Names for 6 extra boxes.** There are **18** `bb_pl_*`, not the 12 the GOAL ratified.
- Ratified (12): collisions `bb_pl_alt→bb_disj`, `bb_pl_seq→bb_conj`, `bb_pl_call→bb_goal`,
  `bb_pl_var→bb_logicvar`; free strip `bb_pl_{arith,atom,builtin,catch,choice,cut,ite,unify}`.
- **UNRATIFIED — need names:** `bb_pl_{findall,intern,ls,op,rs,str}`. (`ls`/`rs`/`op`/`str` look
  like list / struct / operator helpers; `findall`/`intern` are builtins.)

**(iii) Enum-collision resolution.** Bare-strip targets `BB_CONJ`(13), `BB_ARITH`(48),
`BB_ATOM`(113), `BB_BUILTIN`(33), `BB_CHOICE`(73), `BB_CUT`(17), `BB_UNIFY`(15) **already exist**
as enum constants. The present `BB_PL_*` enums are only ALT/CALL/CATCH/ITE/SEQ/STRUCT/VAR. So the
box-name strip must reconcile the function names against the pre-existing enums — confirm whether
those enums are the **same** construct (already partly de-prefixed) or a **true clash** before
renaming any enum.

**Other audit facts (so the next session doesn't re-derive them):**
- **128 distinct** `pl_`/`prolog_` symbols (118 `pl_` + 10 `prolog_`) — NOT 1109; that figure was
  *occurrences*.
- **32 cross-boundary symbols** (Slice 2 had 9 — tight frontend↔runtime coupling). The `prolog_*`
  are frontend-defined (exempt: `prolog_atom/atom_init/intern/name/builtin/compile/driver/runtime`
  in `src/frontend/prolog/`), but `g_pl_trail`, `g_pl_cut_flag`, `pl_box_*`, `pl_broker`,
  `pl_write*`, `pl_univ`, `pl_functor`, `pl_arg`, `interp_exec_pl_builtin`, `lower_pl_clause_body`,
  `current_prolog_flag`, `pl_term_to_string`, `pl_env_new`, `pl_flatten_conj`,
  `pl_pred_table_lookup_global`, `pl_assert_term`, `pl_throw_existence_error_procedure`,
  `pl_unified_term_from_expr`, … appear in BOTH and each needs a def-site call (exempt vs.
  rename-both-sides). Re-derive the set with **`grep -oh`** (Gotcha 5), not bare `grep -o`.
- **`xa_prologue.cpp` is a FALSE POSITIVE** (assembly *prologue*, not Prolog) — DO NOT rename.
  `prolog_` won't match `prologue`, so the symbol sed is safe, but exclude the file from any
  `*prolog*` glob. `src/runtime/wasm/prolog_runtime.wat` is deferred Slice 5.
- **Files confirmed present:** `lower/lower_pl.c/.h` (→`lower_clause`), `interp/pl_runtime.c/.h`
  (→`resolve_runtime`), `emitter/BB_templates/bb_pl.cpp` (→`bb_clause`) + 12 `bb_pl_*.cpp`.

---

## NEXT — pick up here

1. **Get Lon's ratification** on (i) `resolve_` vs bare-strip, (ii) the 6 box names, (iii) the
   enum-collision strategy. Then **execute Slice 3** with the proven Slice-2 method:
   `grep -a`/`grep -oh` selection → classify the 32 boundary symbols by def-site (exempt list) →
   `git mv` files + Makefile + includes → blanket `pl_ → resolve_` → the 12+6 box-specific renames
   (functions + enums + dispatch in `emit_core` / `walk_bb` / `build_patnd`) → revert exemptions +
   guards → residual `grep -a` → build → **HARD gate** (Icon m2 6/6, FACT 0, sm_dead ≤1) →
   commit → push. **Watch:** `bb_pl_*` must NOT collide with Icon's existing
   `bb_alt/seq/call/var` — that is exactly why the 4 collisions become disj/conj/goal/logicvar.
2. **Slice 4 — Raku** (~300 symbols). **Slice 5 — backend output libs** (`.il/.j/.wat/.cs`),
   deferred. Slices 3 + 4 remain to fully "finish" the rename.

---

## Session setup for next time
```bash
git clone https://TOKEN@github.com/snobol4ever/.github  /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/one4all  /home/claude/one4all
cd /home/claude/one4all && git config user.name LCherryholmes && git config user.email lcherryh@yahoo.com
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/test_smoke_icon.sh        # MUST be m2 6/6 (HARD); m3 2/6
bash scripts/test_gate_sm_dead.sh      # 1 (MAX 1)
# Read GOAL-LANG-INDEPENDENT-RENAME.md — esp. Gotchas 4 (grep -a) & 5 (grep -oh), and the
# Slice 3 prep block (the three open ratifications) before touching anything.
```

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
