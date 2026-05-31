# HANDOFF — ICON-BB IBB-10 — Icon builtin dispatch + record-constructor recognition

**Author:** Claude Opus 4.8
**Date:** 2026-05-29
**Goal:** GOAL-ICON-BB.md, rung IBB-10 (LANDED) + IBB-11 (scoped, NOT started)
**SCRIP:** committed this session (see `git log origin/main -1`); base was `c117aa16`
**Repos touched:** SCRIP (5 files), .github (GOAL watermark + Current-state + this doc)

---

## What landed — IBB-10 (corpus 105 → 130 PASS, +25)

Icon BUILTIN calls now dispatch in mode-3. This was the single largest ABORT
cluster: 120 of the 127 `bb_call: unsupported call shape` aborts. The rung is
the direct analogue of IBB-9-6's user-proc arm, for the builtin (non-user-proc)
case — exactly the "builtin-dispatch rung" the prior Current-state named as the
biggest single lever.

### Architecture (mirror of IBB-9-6)

A builtin call compiles to: walk the arg γ-chain (each arg pushes one
single-shot value onto the vstack, arg0 deepest), then a trailer that calls
`rt_icn_call_builtin(name, nargs)`, which pops the args and routes through
`icn_try_call_builtin_by_name` — **the same mode-2 oracle table the bb_exec.c
BB_CALL arm calls** — so m2==m3 by construction. Result left on the vstack for
the enclosing write trailer / assign / arg slot.

### 5 files

1. **`src/runtime/rt/rt.c`**
   - `rt_icn_call_builtin(name, nargs)`: pop nargs (arg0 deepest) →
     `icn_try_call_builtin_by_name` → push result, set LAST_OK. A name the table
     can't serve pushes FAILDESCR+LAST_OK=0 (NO fall-through to INVOKE_fn — Icon
     stays decoupled from SNOBOL4 dispatch).
   - `rt_icn_builtin_is_known(name)`: emit-time gate. Allow-list of pure
     single-shot builtins; EXCLUDES generator builtins (find/upto/any/many/bal/
     key/seq → odometer path) and registered user procs; ALSO returns true for a
     registered record type (`sc_dat_find_type`) so a `record T(...)` ctor routes
     here.
   - `icn_builtin_is_generator(name)`: the find/upto/any/many/bal/key/seq set.

2. **`src/runtime/rt/rt.h`** — decls for the two public functions.

3. **`src/emitter/BB_templates/bb_call.cpp`** — `is_builtin` arm. Byte layout is
   IDENTICAL to the IBB-9-6 userproc arm (movabs rdi,name; mov esi,nargs; movabs
   rax,&fn; call rax; jmp γ; β: jmp ω — patch sites {28,32,33}); only the called
   fn pointer differs (rt_icn_call_builtin). Gated `is_builtin = rt_icn_builtin_is_known(fn)
   && !is_write_strlit && !is_write_intexpr`, checked AFTER the userproc arm and
   the specialized write arms, BEFORE the fatal abort.

4. **`src/emitter/emit_bb.c`**
   - `flat_drive_call_builtin` — byte-free driver, structurally identical to
     `flat_drive_call_userproc` (walk arg γ-chain, EMIT_PAIR_FILL → builtin arm).
   - `icn_bb_is_gen_arg` / `icn_call_args_single_shot` — guards mirroring
     bb_exec.c `bb_is_gen_kind_raw` (seeing through a BB_ASSIGN wrapper). A
     generator arg → the call falls through to the FILL→ABORT path exactly as
     before (no regression); it needs the IBB-9-4/5 odometer.
   - dispatch wiring in `walk_bb_flat` BB_CALL case. Order: **userproc → builtin
     → intexpr → FILL**. `write`/`writes` with a single simple arg keeps its
     proven IBB-3/IBB-7 trailer via the `write_simple1` exclusion.

5. **`src/driver/scrip.c`** — after the proc-registration loop, walk EVERY BB
   graph for BB_RECORD_DEF nodes and `sc_dat_register(nd->sval)`. This makes a
   record type visible at EMIT time so a constructor call routes to
   flat_drive_call_builtin instead of aborting. (The runtime BB_RECORD_DEF node
   also registers — idempotent — and runs before any ctor call, so the RUNTIME
   dispatch through icn_try_call_builtin_by_name's record-ctor fallback already
   worked; this only fixed the emit-time gate.)

### Two bugs found + fixed

- **DT_S slen=0.** The mode-2 builtin table returns string results via
  `STRVAL(buf)`, which sets slen=0 (mode-2's write path uses `VARVAL_fn`/`fputs`
  and never reads slen). The mode-3 `rt_pop_write_any_nl` DOES read d.slen
  (`fprintf "%.*s"`), so a slen=0 DT_S printed NOTHING. Fixed by normalizing
  `out.slen = strlen(out.s)` in `rt_icn_call_builtin` before pushing. This was
  the reason `write(repl(...))` / `write(type(x))` emitted empty lines despite
  the builtin returning the right string. (Found by tracing: dispatch was
  correct, rt handled it, write_any ran with d.v=DT_S — but slen=0.)

- **Record constructors aborting.** Neither user-procs nor table names at emit
  time. Fixed via the driver pre-registration (file 5) + the sc_dat_find_type
  check in the gate.

### Verified gains (full pass-list diff, 0 of 105 prior passes lost)

25 new passes: rung28_builtins_str_{char_ord,pad,repl,reverse,trim_map},
rung29_builtins_type_{copy,image,mixed,numeric,type}, rung30_builtins_misc_{abs,
sqrt}, rung22_lists_{get,pull}, rung13_table_member, rung17_real_arith_{integer,
real_conv,string_conv}, rung15_real_swap_real_literal, rung36_jcon_{center,
concord,diffwrds,nargs,radix,trim}.

### Gates (all green)

- Corpus same-sweep: **105 → 130 PASS, SEGV 0, ABORT 127→68, FAIL 0**, MISMATCH
  26→60 (all 34 new mismatches were previously ABORTing — pure progress, none
  was a prior pass), TIMEOUT 1.
- FACT 0; bytes-outside-templates 12 (UNCHANGED from baseline — the driver and
  the flat driver are byte-free per the FACT RULE; all bytes are in bb_call.cpp,
  a template).
- canonical-5 (hello/add/every_to/alt/full) byte-identical + zero-SM.
- smoke icon 5/5, prolog 5/5, broker 57 (5 pre-existing non-Icon fails).
- 0 regressions (verified by capturing the pass-list at `c117aa16` via git stash,
  diffing against the post-change pass-list).

---

## Gate methodology used this session

`/tmp/sweep.sh` — for each `/home/claude/corpus/programs/icon/*.icn`: run m2
(`--interp`), skip if m2 rc≠0; run m3 (`--run`); PASS iff `m3 rc==0 && m2==m3`
byte-identical. Counts PASS/SEGV(139)/ABORT(≥134)/FAIL(other)/TIMEOUT(124).
**Post-IBB-10 = 130 PASS, SEGV 0.** Use this exact filter; a drop below 130 is a
regression. Regression check: `git stash`, rebuild, capture pass-list, `git stash
pop`, rebuild, diff — the only sound way (absolute counts shift with corpus).

---

## NEXT — three clusters in the 68 remaining ABORTs

**IBB-11 (scoped, NOT started) — record field get/set.** `obj.field` /
`obj.field := rhs` lower to BB_FIELD_GET / BB_FIELD_SET, which have NO mode-3
template and route to the `interp_eval` stub (`[NO-AST] interp_eval stub`). NOTE:
that stub fires even in mode-2 / `--dump-bb` for a `(null)`-kind BB node, so the
LOWERING side needs inspection too — a `c.x` lowers to a node that prints as
`(null)` in dump-bb (see `/tmp/t_field.icn`). Mode-2 oracle: bb_exec.c
BB_FIELD_GET (~line 2483) calls `data_field_ptr(sval, obj)`; BB_FIELD_SET writes
through it. Plan: rt helpers `rt_icn_field_get(name)`/`rt_icn_field_set(name)` +
bb_field_get/bb_field_set templates + drivers (walk α=object, then the trailer).
Unblocks rung24_records_{two_types,field_assign}. rung24_records_record_loop also
needs IBB-9-4 (it has `every c.n := 1 to 3 do …`).

**IBB-9-4/5 — `every E do B` ival=2/3** (10 aborts: `flat_drive_every: do-body
ival=0/2/3 not yet flat-wired`). The generator-bearing two-port split. Adopt
JCON's separate expr/body boxes (STUDY-JCON-... doc). Also unblocks rung10/rung13
augop-in-every mismatches and generator-bearing concat.

**I/O + generator builtins** — `open`/`read`/`reads` (file-handle plumbing into
the rt; the table has `read` arms but needs a real FILE* path under --run);
`upto`/`max`/`point` (upto is a generator builtin → odometer; max/point may just
need adding to the mode-2 table or the allow-list — verify each).

The 60 MISMATCHes (now running, wrong output) are dominated by string scanning
(`rung05_scan`, `rung06_cset`, `rung08` match/move/tab) which need the BB_SCAN /
cset-match generator path — a larger rung.

---

## Reference material used this session

- `bb_call.cpp` IBB-9-6 userproc arm (the byte-layout template the builtin arm
  clones).
- `rt.c` `rt_icn_call_proc` (the helper rt_icn_call_builtin mirrors) and the
  pre-existing `rt_call` icn-fallback chain (line ~1765) which already calls
  `icn_try_call_builtin_by_name` — confirming the table is the right dispatch
  target and is linked into the scrip binary.
- `src/runtime/interp/icn_runtime.c` `icn_try_call_builtin_by_name` (the full
  builtin table; the record-ctor fallback at line ~1860; the DT_S `STRVAL`
  returns that surfaced the slen=0 bug).
- `bb_exec.c` `ir_is_single_shot` / `bb_is_gen_kind_raw` (the generator-kind set
  the emit-time guard mirrors) and BB_RECORD_DEF / BB_FIELD_GET arms.
- `src/driver/interp_data.c` `sc_dat_find_type`/`sc_dat_register` (record-type
  registry the gate and the driver pre-reg use).
