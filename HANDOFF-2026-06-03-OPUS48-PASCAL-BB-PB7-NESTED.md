# HANDOFF 2026-06-03 OPUS48 — Pascal BB: PB-7 nested routines closed (static-link-as-static-chain)

**Goal:** `GOAL-PASCAL-BB.md`. **Repos:** SCRIP (PB-7 commit), corpus (4 new probes + `.gitignore`).
PLAN.md untouched (routine handoff).

---

## What landed — PB-7 (NESTED procedures & functions)

PB-7 is **COMPLETE**, marked `[x]`. The representation fork flagged last session (static chain vs display array)
was resolved to the **recommended static chain** (Lon: "your choice" → proceeded as recommended). It matches
`pint`'s `base()`, satisfies the goal's "no separate display array," and becomes the parent-port thread in
mode-3/4 (PB-9).

### The gate
`nestrec.pas` (recursive `outer` with nested `inner` mutating a per-activation local):
- **Baseline:** `11, 11, 11` (wrong — locals fell through to one shared NV global)
- **PB-7:** `11, 21, 31` — byte-identical to `pint`

### The model (grounded line-by-line in `pint` `base(ld)` + `pcom` `lod/str (level−vlev)`, `mst (level−pflev)`)
- `ProcEntry.decl_level` — lexical level the routine is **declared** at. main scope = 1; top-level procs declared
  there = 1 (bodies run at 2); their nested = 2 (bodies at 3); etc.
- `GenFrame` gains `GenFrame *static_link` + `int level`.
- **Call setup (dval==3.0):** `static_link = pas_base(caller, caller_level − callee_decl_level)`, where
  `pas_base` walks N static links (the `mst (level−pflev)` rule); `frame.level = decl_level + 1`. `caller` is the
  activation captured **before** `frame_depth++`, which is why recursion is correct — a nested helper links to its
  *own* parent activation, so each `inner` mutates the right `outer`'s `x`.
- **Uplevel access reuses PB-6's `Loc` chase:** in `IR_VAR`/`IR_ASSIGN`, if the name isn't in the current frame's
  scope, walk `static_link` (Pascal-guarded) checking each ancestor's scope; the found `(frame,slot)` feeds
  `pas_slot_read`/`pas_slot_write`. Only **then** fall to NV.
- **The chain bottoms out at NV:** a top-level proc's `static_link` is NULL; a walk reaching NULL resolves against
  NV. Keeps program-level globals (`sieve`) and the accidental-pass `nested.pas` correct while frame-scoping
  locals (the two were coupled — frame-scoping alone would have regressed `nested.pas`).

### Files (SCRIP, this commit)
- `src/contracts/stage2.h` — `ProcEntry.decl_level`.
- `src/parser/pascal/pascal.{y,tab.c,tab.h}` —
  - Lexical-level counter `g_pas_level` (program = 1) via **mid-rule actions** `pas_proc_enter`/`pas_proc_exit`
    on both `procedure_decl` block arms (bump on enter, restore after). The mid-rule shifts `$`-numbering: block
    is `$6` (proc) / `$8` (func).
  - Previously-**discarded non-array local var names** now captured per-proc (`pas_local_add`, guarded to
    `g_pas_level >= 2` so program-level vars stay in NV) into a small nesting stack, and appended as a **trailing
    `TT_VLIST` child** whose container `v.ival` carries `decl_level` (same free-slot trick PB-6 used for
    `byref_mask` on the params VLIST).
  - `mk_proc` signature grew `(…, int decl_level, const char **lnames, int lcount)`; all 3 callers updated
    (program/main passes `0,NULL,0`).
  - Regen via the documented direct workaround `bison -d -o pascal.tab.c pascal.y` (`pascal.lex.c`/`pascal.l`
    untouched). **1 s/r conflict = the pre-existing dangling-else** (proven by regenerating the committed `.y`);
    no new conflict. The big `.tab.c` diff is the benign `#line`/`yyrline[]` renumbering.
- `src/lower/lower_program.c` —
  - `is_function` made **type-aware**: `proc->c[3]->t == TT_VAR` (return-var) so a **procedure's** trailing
    locals `TT_VLIST` at `c[3]` is never mistaken for a return-var. (A function's layout is
    `[name, params, body, retvar, locals]`; a procedure's is `[name, params, body, locals]`.)
  - `lower_sc` now seats **params then locals** (loop appends locals after the param loop, de-duped via
    `scope_get`); `decl_level` read off the trailing locals VLIST's `v.ival`.
- `src/interp/IR_interp.c` —
  - `pas_base(f, ld)` and `pas_uplevel_find(cur, name, &of, &os)`.
  - `pas_loc_of_name` **extended to chase uplevel** — a `var` actual that is an enclosing-frame local now resolves
    to its true home (transitivity for nested `var`-passing). PB-6 var probes unaffected (flat → no static link).
  - At the dval==3.0 call setup: set `static_link`+`level` on the new frame (Pascal-guarded by
    `g_current_cfg->lang == IR_LANG_PAS`); param loop extended to seat locals (slots `≥ nparams`) init `NULVCL`.
  - `IR_VAR`/`IR_ASSIGN`: uplevel walk before the NV fallthrough (same Pascal guard).
- `src/runtime/builtins/gen_runtime.h` — `GenFrame.static_link` + `GenFrame.level`.

### Probes (corpus/programs/pascal/, committed)
- `nestrec.pas` — the gate, `11,21,31` byte-identical (was already committed last session as the failing probe).
- `nestcount.pas` — sibling nested procs share an outer counter, bumped 3× → `3`.
- `nest2.pas` — **three-level** nesting; innermost does a **Δ2 grandparent** uplevel read+write and a Δ1 →
  `15,101`.
- `nestfunc.pas` — a nested **function** with its own param, reading uplevel `base` (Δ1 local) + `n` (Δ1 param)
  and returning → `213`.
- `flatnoarg.pas` — **XFAIL discriminating probe** for the separate gap below (oracle `10`, scrip `0`).

### Zero cross-language regression (stash→rebuild→diff, the prescribed method)
Stashed the working tree, rebuilt clean, ran both suites, compared, restored, rebuilt, re-verified the gate:
- Icon `--interp` full ladder: **130 PASS / 117 FAIL / 36 XFAIL** identical baseline-vs-post.
- Prolog honest mode-2: **132/132, 0 ABORT** identical.
- Baseline `nestrec` = `11,11,11`; post = `11,21,31`.
All edits are isolated to the `LANG_PASCAL`/`IR_LANG_PAS`-guarded path.

---

## SEPARATE GAP discovered — parameterless function call in an expression (recommend next: PB-6b)

While building `nestfunc.pas` I first wrote `inner` with **no** parameter and it returned `0`. Root cause is
**not** nesting: in `pascal.y`, `factor` derives a bare identifier as `selector → mk_ident → TT_VAR` (a variable
read); only `IDENT LPARENT … RPARENT` becomes `mk_call`. So a zero-arg function used inside an expression
(`x := f + f`) reads an **unset variable**, never invoking the function. Proven orthogonal by `flatnoarg.pas` —
a **flat** parameterless function fails identically. No prior probe exposed it because every function probe
(`fact`, `fib`, and now `inner(k)`) is parameterized.

**Fix (its own small rung, recommend before PB-8):** give the parser/lower knowledge of declared **function
names** and promote a non-local bare-IDENT-that-names-a-function to a call — being careful **not** to turn genuine
variable reads (params, locals, globals, the function's own result-var assignment target) into calls. `pcom.pas`
(the end-state test) uses parameterless calls heavily, so PB-6b is on the critical path eventually; `nestfunc.pas`
was rewritten to use a parameter so PB-7 has a clean nested-function probe in the meantime.

---

## Still deferred (unchanged)
- **16-bit overflow.** `fact(8)`=40320 > `maxint`=32767: `pint` traps, SCRIP computes 40320. Own integer-model
  rung. `recursion.pas` matches `pint` through `fact(7)`.
- **Per-activation local arrays** in nested/recursive procs (array-fill prologue still global-name-based). No
  probe needs it.
- **`var` actuals that aren't simple variables** (array element/field) fall back to by-value. No probe needs it.

## Setup / gotchas
- **Parser regen workaround still required** (`regenerate_parser_and_lexer_from_sources.sh` is `set -e`, aborts at
  the snobol4 flex step). Regen Pascal directly: `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y`.
- **corpus build artifacts** (`pcom`,`pint`,`*.o`,`prr`,`prd`) are untracked — a `.gitignore` was added this
  session under `programs/pascal/` so the RULES.md `git add -A` step can't capture binaries. Add probe `.pas`
  files explicitly anyway.
- `test/raku/rk_array_literal.raku` FAILS on the clean baseline (pre-existing).
- Lower-priority Icon adjacency unchanged: `src/driver/polyglot.c:43,90,128`.

## Build / verify
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip
( cd /home/claude/corpus/programs/pascal && fpc -Ci -Co -Cr -gl pcom.pas && fpc -Ci -Co -Cr -gl pint.pas )
# gate: ./pcom < nestrec.pas >/dev/null && cp prr prd && ./pint </dev/null   vs   scrip --interp nestrec.pas
```
