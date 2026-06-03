# HANDOFF 2026-06-03 OPUS48 — Pascal BB: PB-6 `var` params closed + PB-7 nested-routine design

**Goal:** `GOAL-PASCAL-BB.md`. **Repos:** SCRIP (HEAD `9af83ea`), corpus (probes). PLAN.md untouched (routine handoff).

---

## What landed this session — PB-6 `var` (pass-by-reference) parameters

PB-6 is now **COMPLETE** (value params were session 5; `var` params are this session). Marked `[x]`.

### The design decision
The prior watermark's open item said to co-design `var` params with PB-7 "rather than bolting on a copy-out."
Honored: `var` params are implemented as **true references**, not copy-in/copy-out. Grounded in `pint`'s
P-machine — a `var` actual is passed as an *address* (`lda`), the callee's param slot *holds* that address, and
every use *dereferences* it (`ind` read / `sto` write). That is the same `base()` static-chain machinery PB-7
uplevel access uses, which is why the two are co-designed.

### The unified slot-reference model (mode-2)
A **location** (`Loc`) is `(GenFrame*, slot)` for a frame-resident variable, or `(NULL, NV-name)` for a global.
Top-level `main` runs **frame-less**, so its variables (e.g. `varparam.pas`'s `k`) live in NV — the
`(NULL,name)` case. A frame slot is either a **value** (`env[slot]`) or a **reference** to a `Loc`. `var`-param
call setup resolves the actual's `Loc` **in the caller** — chasing if the caller's own variable is itself a
reference, which gives **transitivity** (a `var` passed onward as a `var`) and **`f(a,a)` aliasing** for free —
and installs it as the callee slot's reference. Reads/writes of a reference slot chase to the home.

### Files (SCRIP `9af83ea`)
- `src/contracts/stage2.h` — `ProcEntry.byref_mask` (`uint64_t`, bit k set ⇒ param k is `var`).
- `src/parser/pascal/pascal.{y,tab.c,tab.h}` — `VARSY id_list COLON IDENT` arm pushes a sentinel `TT_SUCCEED`
  child onto each by-ref param node (value params have `n==0`); `mk_proc` detects `pv->n > 0`, sets the bit on
  the **`TT_VLIST` container's** unused `v.ival`, and clears the sentinel. The container's `v` is free (verified:
  every other `TT_VLIST` consumer reads the *children's* `v.sval`, never the container's `v`; my read is
  `LANG_PASCAL`-guarded). VLIST arity is untouched, so `nparams = proc->c[1]->n` still holds.
- `src/driver/polyglot.c` — `s2->proc_table[_pi].byref_mask = (LANG_PASCAL && TT_PROC_DECL && n>=2) ?
  (uint64_t)proc->c[1]->v.ival : 0`.
- `src/runtime/builtins/gen_runtime.h` — `GenFrame` gets a tag; new `SlotRef { unsigned char is_ref;
  GenFrame *frame; int slot; const char *name; }`; `GenFrame.slotref[FRAME_SLOT_MAX]`. `memset(_f,0,…)` at frame
  push zeroes it ⇒ non-`var` slots default to value behavior.
- `src/interp/IR_interp.c` —
  - `pas_slot_read(f,slot)` / `pas_slot_write(f,slot,v)` — chase: ref→frame recurses; ref→NV uses
    `NV_GET_fn`/`NV_SET_fn`; else `env[slot]`.
  - `pas_loc_of_name(caller,name,&f,&slot,&nm)` — resolve a name in the caller to a home `Loc`, chasing a ref.
  - `IR_VAR` read: if `FRAME.slotref[slot].is_ref` → `pas_slot_read` **before** the existing `sv.v != 0`
    NV-fallthrough (a referenced home may legitimately hold 0).
  - `IR_ASSIGN`: if ref → `pas_slot_write`, else `env[slot]=val`.
  - dval==3.0 call setup: capture `caller = (frame_depth>0)?&FRAME:NULL` **before** `frame_depth++`; for each
    `k` with `byref_mask` bit set whose arg block `call_blks[k]->entry` is an `IR_VAR`, `pas_loc_of_name` →
    install the slot's reference.

### Evidence (probes in corpus/programs/pascal/, committed)
- `varparam.pas` — byte-identical to `pint` (`7`). The gate.
- Cases copy-out gets **wrong**, all byte-identical: `swap.pas` (two-way ref), `alias.pas` (`addto(a,a)`→`11`,
  proving real aliasing), `vartrans.pas` (var passed onward as var; chain flattens at setup), `varframe.pas`
  (callee writes a live ancestor's frame slot — the PB-7-shaped `(frame,slot)` Loc).
- `varmix.pas` — value params unaffected by the ref path.
- `sieve.pas` byte-identical; `recursion.pas` identical through `fact(7)`.

### Zero cross-language regression (stash→rebuild→diff, the prescribed method)
Stashed the 7 files, rebuilt clean, ran the suites, compared:
- Icon `--interp` full ladder: **130 PASS / 117 FAIL / 36 XFAIL** identical baseline-vs-post (the 117 are
  rung36 advanced reflection/scan/structures — unimplemented Icon, not Pascal).
- Prolog honest mode-2: **132/132, 0 ABORT** identical.
Restored, rebuilt, re-verified the gate.

### Honest limitation
A `var` actual that is **not a simple variable** (array element `a[i]`, record field) falls back to by-value —
guarded by `call_blks[k]->entry->t == IR_VAR`. `pcom.pas` (end-state test) will eventually need it, but no
current probe does, so per "climb only as far as the probes demand," left for when a probe forces it.

---

## Next — PB-7 (NESTED procedures & functions): DESIGNED, build held for Lon's representation call

### The gap, precisely characterized
`nestrec.pas` (committed) is the discriminating gate: a recursive `outer(d)` with a local `x := d*10`, a nested
`inner` doing `x := x+1`, recursing `outer(d-1)`, then `writeln(x)`.
- `pint` (correct, per-activation `x`): **`11, 21, 31`**
- SCRIP (current): **`11, 11, 11`**

Root cause: **procedure locals are not frame-scoped** — a local `var x` falls through to one shared NV global.
`fact`/`fib` only dodge this by using parameters (frame-scoped, per-activation-correct) plus the NV-return
trick. The simple `nested.pas` (non-recursive nested uplevel) passes **only accidentally**: `outer`'s local and
`inner`'s uplevel both resolve to the same shared NV slot.

**Frame-scoping locals and static-link uplevel are coupled.** Frame-scoping locals *alone* would regress
`nested.pas` (inner loses the shared-NV path to outer's `x`); uplevel is what restores it. So PB-7 is one design.

### The model (grounded line-by-line in `pcom`/`pint`)
- `pcom`: each routine has a lexical `level` (bumped entering a nested decl, restored on exit; globals/main =
  level 1). Each variable carries its declaring level `vlev`. Access uses the **difference**:
  `lod (level−vlev), dplmt` read, `str (level−vlev), …` write, `lda (level−vlev), …` address-of; `vlev ≤ 1`
  uses direct global ops. A call sets the static link with `mst (level − pflev)`, `pflev` = the level of the
  scope where the callee was **declared**.
- `pint`: `base(ld)` walks `ld` static links via `store[ad+1]` (the static link); `mst` stores `base(p)` as the
  callee's static link. A pure **static chain**, no display.
- The `level − pflev` rule verified on all cases: outer→inner = 0 links (caller frame); sibling call = 1;
  self-recursion = 1; routine nested in the callee = 0.

### SCRIP mapping
- `ProcEntry.decl_level` (main's scope = 1; top-level procs declared there = 1, bodies run at 2; their nested =
  2, bodies at 3 …). Tracked in `pascal.y` with a level counter (mid-rule action on `procedure_decl`'s block).
- `lower_sc` = params **then locals**. The parser must **capture each proc's local `var` names** (currently
  discarded) and attach them to the proc node; the dval==3.0 setup loop already `scope_add`s — extend it to add
  locals (init `NULVCL`).
- `GenFrame { GenFrame *static_link; int level; … }`. At dval==3.0 setup:
  `static_link = base(caller_frame, caller_body_level − callee_decl_level)`.
- **Uplevel access reuses the PB-6 `Loc` + chase**: in `IR_VAR`/`IR_ASSIGN`, if the name isn't in the current
  frame's scope, walk `static_link` and check each ancestor's scope; the found `(frame,slot)` is a `Loc` →
  `pas_slot_read`/`pas_slot_write`. Only *then* fall to NV.

### The frame-less-`main` wrinkle (worked through)
`pint` gives the level-1 program its own activation for globals; SCRIP runs `main` frame-less with globals in NV.
So the static chain **bottoms out at NV**: a top-level proc's `static_link` is NULL (its lexical parent is
`main`), and any walk reaching a NULL link resolves against NV. Verified on `nestrec`: `inner.static_link =
outer_frame`; `inner` reading `x` (Δ1) walks one link → `outer` ✓; `inner` reading a true global (Δ2) walks
`inner→outer→NULL` → NV ✓. This is also what keeps `sieve` (program-level array/loop-var = true globals) and
the accidental-pass `nested.pas` from regressing.

### THE FORK (Lon's call) — recommendation
Representation of the static link: a per-frame **`GenFrame *static_link` (static chain), not a display array.**
Matches `pint`'s `base()`, satisfies the goal's "no separate display array," and in mode-3/4 (PB-9) that link is
what becomes the **parent-port thread**. Recommending, not committing — this is the representation flagged last
session as Lon's to set. "Yes, as recommended" is a one-word go.

### Implementation plan (in order, once the fork is set)
1. `pascal.y` — lexical-level counter (mid-rule on `procedure_decl` block: bump on enter, restore after);
   capture per-proc local `var` names; attach `decl_level` + locals to the proc node.
2. `stage2.h` — `ProcEntry.decl_level`; `lower_sc` from params then locals.
3. `polyglot.c`/`lower_program.c` — set `decl_level`; extend `lower_sc` with locals.
4. `gen_runtime.h` — `GenFrame.static_link` + `GenFrame.level`.
5. `IR_interp.c` — compute `static_link` at dval==3.0 setup (base-walk); uplevel walk in `IR_VAR`/`IR_ASSIGN`
   before the NV fallback, feeding the existing `Loc` chase.

### Deferred
Per-activation **local arrays** in nested/recursive procs — the array-fill prologue is still global-name-based.
No probe needs it; add when one forces it.

### Gate
`nestrec.pas` (committed) → must become `11,21,31`. `nested.pas`, `sieve.pas`, `recursion.pas`(through
`fact(7)`), and all PB-6 `var` probes must stay byte-identical. Re-run Icon 130/117/36 + Prolog 132/0/0
baseline-vs-post.

---

## Setup / gotchas for the next session
- **Parser regen workaround still required.** `scripts/regenerate_parser_and_lexer_from_sources.sh` is `set -e`
  and aborts at the snobol4 flex step (clobbers `snobol4.lex.c`, never reaches Pascal). Regen Pascal directly:
  `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y` (only `.y` changed this session; `pascal.lex.c`
  untouched). The 452-line `pascal.tab.c` diff was benign `#line`/`yyrline[]` renumbering from the grammar
  growing a few lines — tables structurally unchanged. Script still wants a fix.
- **corpus build artifacts must NOT be committed.** `programs/pascal/{pcom,pint,*.o,prr,prd}` are untracked and
  not gitignored — `git add -A` in corpus would commit binaries. Add probe `.pas` files explicitly (a
  `.gitignore` for these artifacts would harden against the RULES.md `git add -A` step; left as a recommendation,
  out of scope this handoff).
- `test/raku/rk_array_literal.raku` FAILS on the clean baseline (pre-existing, proven by stash+rebuild).
- Lower-priority Icon adjacency unchanged: `src/driver/polyglot.c:43,90,128` still gate `LANG_PASCAL` alongside
  `LANG_ICN`/`LANG_RAKU`.

## Build / verify
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
cd /home/claude/SCRIP && make -j4 scrip
( cd /home/claude/corpus/programs/pascal && fpc -Ci -Co -Cr -gl pcom.pas && fpc -Ci -Co -Cr -gl pint.pas )
# check a probe: ./pcom < p.pas && cp prr prd && ./pint < /dev/null   vs   scrip --interp p.pas
```
