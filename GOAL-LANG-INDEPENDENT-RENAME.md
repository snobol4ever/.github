# GOAL-LANG-INDEPENDENT-RENAME.md — De-language the post-AST subsystems

**Repo:** one4all + .github
**Sister:** GOAL-AST-RENAME.md · GOAL-SNOBOL4-BB.md · GOAL-HEADQUARTERS.md
**Carved:** 2026-05-30 (Lon directive — PIVOT from SNOBOL4-BB Track B)

---

## ⛔ THE RULE (Lon directive 2026-05-30)

Everything **from the shared AST (`tree_t`) onward** — `lower → emitter → interpreter/runtime` —
must be **LANGUAGE-INDEPENDENT** in *file names, function names, variable names, macro names,
type names*. We cannot predict which language will start using a given opcode, so the post-AST
machinery must never be named after a source language.

**Pipeline (stages):** `parser → lower → emitter → interpreter/runtime`. The runtime/emitter/lower
must NOT be named after the language that fed them 1–3 stages upstream.

### Banned
- File names with a source-language prefix: `icn_`, `icon_`, `pl_`, `prolog_`, `sno_`, `snobol4_`,
  `rk_`, `raku_`, `sc_`, `snocone_`, `reb_`, `rebus_` — anywhere in `src/lower`, `src/emitter`,
  `src/processor`, `src/runtime`, `src/include`, `src/driver`, `src/ast`.
- Functions / variables / macros / types with those prefixes in those subsystems.

### Allowed (KEEP)
- **Cultural FEATURE names** — an opcode/box/datatype/keyword named after the *construct* by its
  cultural name: `TABLE`, `SUSPEND`, `ARRAY`, `CSET`, `ARBNO`, `SPAN`, `unify`, `cut`, `term`,
  `choice`, `goal`, `generator`, `scan`, `disjunction`, `conjunction`. These name a FEATURE, not a
  LANGUAGE.
- **The frontend** (`src/frontend/*`) — parser + lexer stay language-specific (that is correct;
  the parser IS per-language). Not in scope.
- **Output-target emitters** — a backend whose OUTPUT is a named language may carry that language
  in its name (like `emit_c`): `lower_sno.c` (`--dump-sno`, emits SNOBOL4 *source*) is **EXEMPT**.
  The `.il`/`.j`/`.wat` runtime libs are named after the SOURCE lang they support → those ARE in
  scope (deferred slice).

### The dominant transformation
**Strip the language prefix, keep the cultural feature word.** `pl_unify→unify`,
`icn_cset→cset`, `icn_to→to`, `sc_dat→dat`. Only collisions need a design decision.

---

## Audited scope (2026-05-30, HEAD 2b6394e1)

- **Files on live path:** ~25 (+13 backend output libs `.il/.j/.wat/.cs/.java/.js`, deferred).
- **Symbol hits:** ~2,400 — `pl_`+`prolog_` 1109 · `icn_`+`icon_` 438 · `raku_`+`rk_` 300 ·
  `sno_`+`snobol4_` 134 · `sc_dat` 62 · `rebus_` 5 · `snocone_` 3.

### Collision set (the only design decisions) — RATIFIED NAMES
Four boxes where Prolog and Icon both own a same-named, different-semantics construct:

| Prolog box | Icon box (exists) | Prolog → cultural name |
|---|---|---|
| `bb_pl_alt` (disjunction `;`) | `bb_alt` (alternation `\|`) | **`bb_disj`** |
| `bb_pl_seq` (conjunction `,`) | `bb_seq` (sequence) | **`bb_conj`** |
| `bb_pl_call` (goal call) | `bb_call` (proc call) | **`bb_goal`** |
| `bb_pl_var` (logic variable) | `bb_var` (variable) | **`bb_logicvar`** |

The 8 free Prolog boxes strip cleanly: `bb_pl_{arith,atom,builtin,catch,choice,cut,ite,unify}`
→ `bb_{arith,atom,builtin,catch,choice,cut,ite,unify}`. (`bb_pl.cpp` → `bb_clause.cpp`.)

### File rename map
| Current | → New | Subsystem |
|---|---|---|
| `runtime/snobol4/` (dir) | `runtime/core/` | core rt |
| `snobol4.c/.h` | `core.c/.h` | |
| `snobol4_argval.c` | `argval.c` | |
| `snobol4_invoke.c` | `invoke.c` | |
| `snobol4_nmd.c` | `name_save.c` | |
| `snobol4_pattern.c` | `pattern.c` | |
| `snobol4_patnd.h` | `patnd.h` | |
| `snobol4_utf8.h` | `utf8.h` | |
| `snobol4_runtime_shim.h` | `runtime_shim.h` | |
| `interp/icn_runtime.c/.h` | `interp/gen_runtime.c/.h` | generator/scan rt |
| `interp/icn_value.h` | `interp/gen_value.h` | |
| `interp/icon_box_rt.h` | `interp/box_rt.h` | |
| `interp/icon_gen.h` | `interp/gen.h` | |
| `interp/pl_runtime.c/.h` | `interp/resolve_runtime.c/.h` | unify/resolution rt |
| `interp/raku_builtins.c/.h` | (by feature; peek before rename) | |
| `interp/raku_builtins_byname.c` | (by feature) | |
| `lower/lower_icn.c/.h` | `lower/lower_graph.c/.h` | stmt/expr→BB graph |
| `lower/lower_pl.c/.h` | `lower/lower_clause.c/.h` | clause→BB |
| `emitter/BB_templates/bb_pl_*.cpp` | strip `pl_` (+4 collisions above) | |

**Already clean (no touch):** `lower_pat_dcg.c`, `scan_builtins.c`, all `bb_pat_*`, all cultural
`bb_*` boxes, `src/ast/*`.

---

## Orchestration — slice order (build green + gate after EACH, one commit each)

Gate per slice (HARD): `make scrip` rc=0 · `make libscrip_rt` rc=0 · Icon smoke **m2 6/6** ·
FACT=0 · sm_dead ≤1. Baseline at carve: m2 6/6, FACT 0, sm_dead 1.

- [x] **Slice 0 — harness proof** ✅ (`5370695f`): `sc_dat→dat`, `ScDatType→DatType` (62 hits,
  record/datatype facility). **`rebus_`/`snocone_` turned out to be FRONTEND entry points
  (`rebus_lower`, `snocone_driver/compile` defined in `src/frontend/*`) — EXEMPT, not touched.**
  Gate green (Icon m2 6/6, FACT 0, sm_dead 1).
- [x] **Slice 1a — core runtime FILES** ✅ (`7d57c6bd`): `runtime/snobol4/`→`runtime/core/`;
  `snobol4.{c,h}`→`core.{c,h}`; `snobol4_argval/invoke/nmd/pattern`→`argval/invoke/name_save/pattern`;
  `snobol4_patnd/utf8/runtime_shim.h`→`patnd/utf8/runtime_shim.h`. Updated 41 `#include` sites +
  23 Makefile path refs + the `-I` flag. **TRAP HIT + FIXED:** there is ALSO a *frontend*
  `src/frontend/snobol4/snobol4.h` (defines `Token`); the basename-`#include "snobol4.h"` sed
  wrongly redirected 3 frontend files (`snobol4.lex.c`, `snobol4.tab.h`, `test_lex.c`) to `core.h`
  → reverted those to local `snobol4.h`. Gate green.
- [x] **Slice 1b — core runtime SYMBOLS** ✅ (`d7f64afa`): `sno_ → core_`, 67 runtime symbols
  (incl. `sno_pat_*`, `sno_runtime_error`, `sno_fn_registered`, `g_sno_err_*`, `_sno_abort_*`).
  8 frontend parser-API symbols EXEMPT (still `sno_`): `sno_parse`, `sno_parse_ast`,
  `sno_parse_string`, `sno_parse_string_ast`, `sno_add_include_dir`, `sno_error`, `sno_nerrors`,
  `sno_reset`. Method: blanket `s/sno_/core_/g` + revert-8. **`core.c` (was `snobol4.c`) is
  UTF-8-"binary" to grep** (contains α/β/γ/ω) → had to use `grep -a` for BOTH file selection AND
  verification (see Gotcha 4). Gate green.
- [x] **Slice 2 — Icon interp** ✅ (`bf3f7928`): `icn_/icon_ → gen_` (mirrors `core_`). Files:
  `interp/{icn_runtime→gen_runtime.c/.h, icn_value→gen_value.h, icon_box_rt→box_rt.h, icon_gen→gen.h}`,
  `lower/{lower_icn→lower_graph.c/.h, lower_icn_bb→lower_graph_bb.h}` (last was an ORPHAN, no includers;
  found only because its `icn` is mid-name not prefix — `find -name 'icn_*'` missed it). Blanket
  `s/icn_/gen_/g; s/icon_/gen_/g` over post-AST (incl. `icn_bb_*`, `icon_*_new` emitter ctors,
  `_icn_*` driver hooks, `*_state_t`, `icn_bb_dcg`); 9 frontend exemptions reverted (def-site in
  `src/frontend/`, called from post-AST): `icn_cset_{canonical,complement,diff,inter,union}` (def
  `icon_runtime.c`), `icon_compile/icon_driver/icon_lex` (parser API), `g_icn_jcon` (lexer↔coerce
  global). 51 files, 1007/1007 (pure rename). Gate green (m2 6/6, FACT 0, sm_dead 1; runtime/stage2
  isolation rc=0; lower_isolation unchanged). **NOTE for next slices: `grep -o` on MULTIPLE files
  prefixes `filename:` — use `grep -oh` for identifier extraction or intersections silently break.**
- [ ] **Slice 3 — Prolog**: `pl_/prolog_` files + 1109 symbols + 8 free boxes + 4 collision boxes.
  Biggest slice.
- [ ] **Slice 4 — Raku**: `raku_/rk_` files + 300 symbols.
- [ ] **Slice 5 — backend output libs** (deferred): `.il/.j/.wat/.cs/.java/.js` named `Sno*` —
  off the live build path (X86 ONLY), lowest priority.

### Mechanics per slice
1. `git mv` the files; update Makefile `RT_PIC_SRCS` + `scrip:` recipe + `build_scrip.sh` source
   lists; update every `#include`.
2. `sed` the symbols across ALL consumers in the SAME commit (rename + all call sites atomic).
3. Rebuild (`make scrip`, `make libscrip_rt`), run the HARD gate, commit on green.
4. Never a broken commit.

---

## Gotchas (learned this session — read before any slice)

1. **Frontend entry points are NOT in scope even when called from the driver.** `rebus_lower`,
   `snocone_driver/compile`, `sno_parse*` are parser-stage (defined in `src/frontend/*`). The
   driver legitimately dispatches to per-language parsers by name. Check the DEFINITION site,
   not the call site, before renaming a symbol.
2. **Duplicate basenames across stages.** Both `src/frontend/snobol4/snobol4.h` (frontend, defines
   `Token`) and the old `src/runtime/snobol4/snobol4.h` (runtime) existed, disambiguated only by
   `-I` search order. A basename `#include` sed will hit BOTH. After any header rename, re-check
   that frontend files still point at their LOCAL header.
3. **Collision scans are noisy.** Naive `grep -rIE '\bWORD\b'` counts struct fields, locals, and
   comments — not link symbols. `sno_body→body` "645 collisions" is mostly `->body` field access.
   Real link clashes are rare; judge by whether the stripped name is a too-generic global
   (`error`, `init`, `path`, `call`, `reset`, `parse`) — those need a namespace, not a bare strip.
   This is why the `sno_` slice uses a `core_` namespace, not a bare strip.
4. **⚠ grep `-I` SKIPS "binary" files — use `grep -a` for EVERY slice.** Several post-AST source
   files contain the UTF-8 port names α/β/γ/ω (RULES: FOUR PORTS = FOUR GREEK NAMES) and grep
   classifies them as **binary**. `core.c` (was `snobol4.c`), and almost certainly `bb_exec.c`,
   `lower_icn.c`, `lower_clause.c`, `icn_runtime.c`, etc. `grep -rlI` / `grep -rlIE` (file
   selection) and `grep -rhoI` (verification) all carry `-I` → they SILENTLY skip these files.
   Slice 1b's first two build failures (`g_sno_err_stmt` undeclared) were exactly this: core.c was
   never sed'd because `-I` skipped it, and the "0 remaining" check was blind to it. **ALWAYS use
   `grep -a` (treat-as-text) for both the file-selection grep AND the residual-verification grep.**
   `sed -i` itself handles these files fine. Re-verify after every slice with `grep -arhoE`.

---

## 🎉 PARKED — POST-RENAME FUN (Lon idea 2026-05-30): 32-bit pointer aliasing + per-language registers

**Do AFTER the rename completes.** Captured here per Lon. Reconcile with `REGISTER-LAYOUT.md`,
`ARCH-x86.md`, `ARCH-SCRIP.md` before implementing. Two related ideas:

### Idea A — 32-bit pointer compression via a base register (the headline)
- **Kernel:** dedicate ONE callee-saved base register (Lon: **R15 or RBP**) to hold a heap/arena
  base. Store pointers as **32-bit offsets** from that base instead of full 64-bit pointers.
  Real pointer = `base + offset` (optionally `base + (offset << k)` with k from value alignment,
  e.g. 8-byte → 32 GB reach). This is classic *pointer compression* (cf. JVM compressed oops /
  V8 pointer compression).
- **Win:** halves the pointer field in `DESCR_t` (8→4 B) → smaller descriptors, better cache
  density, more values per line. "This will be amazing!" (Lon).
- **Command-line switch** to select the mode: e.g. `--ptr32` / `--compress-ptr` (full 64-bit
  pointers remain the default / fallback). Build- or run-time selectable.
- **Encapsulate 99% in `DESCR_t` + `sil_macros.h`** — the compress/decompress lives entirely in
  the descriptor accessors and the `sil_macros.h` access macros (MOVD-family gets a "via base"
  variant). The rest of the runtime/emitter stays oblivious. The CLI switch flips which macro
  expansion / which DESCR layout is active.
- **⚠ CRITICAL CAVEAT — Boehm GC cannot trace 32-bit offsets.** `libgc` scans memory for *real*
  pointers to find roots; a stored 32-bit offset is not recognized → premature collection (same
  hazard family as the "GC can't see mmap'd-pool imm64" note in GOAL-SNOBOL4-BB). Mitigations to
  evaluate: (a) allocate the compressed heap as a single GC-pinned/uncollectable arena and
  hand-manage it; (b) `GC_register_displacement` / interior-pointer registration; (c) keep the
  authoritative full pointer somewhere GC scans and use the 32-bit form only as a transient
  index. Decide this FIRST — it gates the whole design.
- **Base register must be callee-saved + never clobbered.** RBP is callee-saved (frees up under
  `-fomit-frame-pointer`); R15 is a clean callee-saved GP reg. Whichever is chosen is reserved
  process-wide and set once at entry.

### Idea B — per-language register roles (R13/R14/R15) + a LOCAL/frame register
- **Context (post-SMX-4):** the Stack Machine is deleted, so **r13 (was the SM-state register) is
  now FREE**. Current live assignments to respect: `r10` = broker current-node; `r12` = Icon zeta
  one-register BB-frame (moved r15→r12 in `03acf1be`); the one-register-frame + RO-IP-relative
  FACT rules in RULES.md still hold.
- **Lon's thought:** R13/R14/R15 can mean **different things for Prolog vs Icon** — "each has a
  different substance it is zippering through." Prolog zippers through its term store / choice-point
  trail; Icon zippers through generator / co-expression / scan state. Dedicate the freed registers
  per-language to that language's iteration substance (set at sequence entry, like the BB-frame reg).
- **All BBs return `DESCR`** — keep the uniform Byrd-box ABI (`bb_box_fn → DESCR_t`) as the glue so
  per-language register specialization stays behind one calling convention.
- **A LOCAL / frame register** — "the other register" could carry a **function-local frame** that
  shadows globals: locals for the current function activation (non-global scope, Python-LEGB-style
  local namespace). Pairs naturally with the existing one-register BB-frame concept. ("Maybe. Just
  thinking out loud." — Lon.)

### Touch-points when this starts
`src/runtime/core/descr.h` (DESCR_t layout) · `sil_macros.h` (access macros) · the CLI parse in
`src/driver/scrip.c` · the emitter templates that materialize pointers · `REGISTER-LAYOUT.md` (must
be updated to record the base reg + per-language roles) · GC arena setup in `rt.c`/`bb_pool.c`.

---

## Session State

```
HEAD one4all  = bf3f7928  (LANG-INDEP Slice 2 — Icon)
HEAD .github  = (see git log)
Baseline      = Icon m2 6/6 (HARD), m3 2/6, FACT 0, sm_dead 1/1
Slices done   = 0 ✅ (5370695f), 1a ✅ (7d57c6bd), 1b ✅ (d7f64afa), 2 ✅ (bf3f7928) — all green
Next          = Slice 3 (Prolog: pl_/prolog_ + ~1109 symbols + 12 boxes). USE grep -oh + grep -a.
Handoff       = HANDOFF-2026-05-30-OPUS48-LANG-INDEP-RENAME-SLICE-2.md
```

### Slice 3 prep notes (Prolog) — OPEN NAMESPACE DECISION
- **Files (git mv):** `interp/pl_runtime.c/.h → resolve_runtime.c/.h`; `lower/lower_pl.c/.h →
  lower_clause.c/.h`; `emitter/BB_templates/bb_pl.cpp → bb_clause.cpp`; `bb_pl_*.cpp` strip `pl_`.
- **12 ratified boxes:** collisions `bb_pl_alt→bb_disj`, `bb_pl_seq→bb_conj`, `bb_pl_call→bb_goal`,
  `bb_pl_var→bb_logicvar`; free `bb_pl_{arith,atom,builtin,catch,choice,cut,ite,unify}` strip `pl_`.
- **⚠ DECISION NEEDED before bulk symbol rename (AUDITED bf3f7928, 2026-05-30 Opus):**
  - **Counts:** 128 distinct `pl_`/`prolog_` symbols (NOT 1109 — that was occurrences). Tractable.
  - **Namespace:** `pl_ → resolve_` is **collision-free** (0 existing `resolve_`), mirrors `core_`/`gen_`
    AND the ratified `pl_runtime→resolve_runtime`. Recommend option (b) `resolve_`. (Bare-strip per the
    GOAL's `pl_unify→unify` rule collides on ~24 generic stems: write/writeq/write_canonical/copy_term/
    functor/univ/arg/args/trail_mark/nb_getval/nb_setval/choice/builtin/leaf/key/cs/locals/...).
  - **Boxes are 18, not 12.** Ratified: 4 collisions (`bb_pl_alt→bb_disj`, `bb_pl_seq→bb_conj`,
    `bb_pl_call→bb_goal`, `bb_pl_var→bb_logicvar`) + 8 free strip (`arith,atom,builtin,catch,choice,cut,
    ite,unify`). **UNRATIFIED — need names:** `bb_pl_{findall,intern,ls,op,rs,str}`. (ls/rs/op/str look
    like list/struct/operator helpers; findall/intern are builtins.)
  - **⚠ ENUM COLLISIONS:** `BB_CONJ`(13), `BB_ARITH`(48), `BB_ATOM`(113), `BB_BUILTIN`(33),
    `BB_CHOICE`(73), `BB_CUT`(17), `BB_UNIFY`(15) ALREADY EXIST as enum constants. Present `BB_PL_*`
    enums are only ALT/CALL/CATCH/ITE/SEQ/STRUCT/VAR. So the box-name strip must reconcile fn names vs
    the pre-existing enums — confirm whether those enums are the SAME construct (already partly
    de-prefixed) or DIFFERENT (true clash). Investigate before renaming any enum.
  - **⚠ 32 cross-boundary symbols** (Slice 2 had 9). Tight frontend↔runtime coupling: `prolog_*` are
    frontend-defined (exempt), but `g_pl_trail`, `g_pl_cut_flag`, `pl_box_*`, `pl_broker`, `pl_write*`,
    `pl_univ`, `pl_functor`, `pl_arg`, `interp_exec_pl_builtin`, `lower_pl_clause_body`,
    `current_prolog_flag`, etc. appear in BOTH — each needs a def-site call (exempt vs rename-both-sides).
    Full list saved during audit; re-derive with `grep -oh` (NOT bare `grep -o`).
  - **`xa_prologue.cpp` is a FALSE POSITIVE** (assembly prologue, not Prolog) — DO NOT rename. `prolog_`
    won't match `prologue`, so the symbol sed is safe, but exclude the file from any `*prolog*` glob.
  - **Files confirmed present:** `lower/lower_pl.c/.h` (→lower_clause), `interp/pl_runtime.c/.h`
    (→resolve_runtime), `emitter/BB_templates/bb_pl.cpp`(→bb_clause) + 12 `bb_pl_*.cpp`.
- **Method (either way):** identical to Slice 2 — `git mv` + include/Makefile fix; robust cross-boundary
  intersection with `grep -oh` (NOT bare `grep -o`) to find frontend-defined symbols called from
  post-AST (Prolog parser API) → exempt+revert; blanket; revert; guards; residual `grep -a`; build;
  HARD gate; commit; push. Watch `bb_pl_*` must NOT collide with Icon's existing `bb_alt/seq/call/var`
  (that is exactly why the 4 collisions are renamed to disj/conj/goal/logicvar).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
