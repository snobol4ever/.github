# HANDOFF 2026-06-03 (Opus 4.8) — Prolog PL-HY-1a: BINARY-half compound-Term walker collapsed; TEXT twin proven NOT a dup

## TL;DR

PL-HY-1a (DUP FORM 1 on `bb_builtin.cpp`). The two compound-`Term` builders
`emit_build_compound_term` (TEXT/mode-4) + `emit_build_compound_term_bin`
(BINARY/mode-3) were the SAME post-order IR→`Term` walker in two media, and
BOTH duplicate `resolve_node_to_term()` already living in `IR_interp.c`.

**Landed (SCRIP `abae7c1`, local — push at handoff):**
- Added one exported wrapper `rt_node_to_term_ptr(void*)` over the recursive
  `resolve_node_to_term` (in `IR_interp.c`).
- **DELETED** `emit_build_compound_term_bin` (90 lines) and rerouted all **23**
  mode-3 BINARY call-sites through a 2-instruction marshal+call helper
  `emit_term_from_node_bin` (`movabs rdi,&node ; movabs rax,&rt_node_to_term_ptr ;
  call rax` → `Term*` in rax).
- **KEPT** `emit_build_compound_term` (TEXT) deliberately — see "Why the TEXT
  half stays" below.

**Gate state (clean rebuild, verified):** GATE-3 **m2 111/111 · m3 111/111**
byte-identical · **m4 75 / 0 FAIL / 36 EXCISED** held. GATE-1 m2 **5/5**.
Icon m2 **12/12**, SNOBOL4 m2 **7/7** (shared-file invariant intact).
medium-invisible **384→343**; no_bb_bin_t 0; seg_byte/SL_B 0; handencoded
`b.size()` 0; prove_lower2 PASS. `bb_builtin.cpp` 2282→2187 (−95).

## Why the rt-call replacement is valid (mode-3 only) — and MORE correct

`resolve_node_to_term` is the recursive IR→`Term` walker the mode-2 oracle uses;
it handles exactly the kinds the deleted `_bin` walker did (LOGICVAR via env
slot, ATOM/LIT_I/LIT_F leaves, STRUCT γ-chained recursion, ARITH α/β recursion),
producing identical trees. Baking the live `IR_t*` and letting a runtime helper
walk it is the **already-live, gate-covered pattern** of the `is`/`rt_is_eval`
arm (proven this session: `X is 2+3*4` → `14` via `--run`). Mode-3 `--run` is
IN-PROCESS, so the `IR_t*` is valid at run time.

**Net more correct:** the deleted inline `_bin` leaf path emitted `xorps xmm0`
(dval=0.0) for ALL leaves, so a float literal reached as a bare leaf would build
as `0.0`; `resolve_node_to_term` reads `dval`. No currently-passing rung relied
on the bug (a passing rung diffs against the mode-2 oracle, which is correct), so
this cannot regress and may latently fix.

**Regression net:** 24 compound-term rungs (rung09/17/20/22/25/26 — sort, msort,
numbervars, writeq-compound, term_to_atom, copy/concat/alc) all PASS m2+m3
byte-identical before and after.

## Why the TEXT half STAYS (this corrects the GOAL file's "delete BOTH" premise)

The GOAL-PROLOG-BB 1a bullet (now updated) said replace BOTH walkers with one rt
call. That is only half-right. With `_bin` deleted, the DUP-FORM-1 ("same algo in
two media") is **RESOLVED** — there is now exactly ONE walker, and it is the
**mode-4 serialized encoding**: it bakes the node's scalars as immediates +
`lea [rip+strlbl]` for atom names and calls `rt_node_to_term@PLT` /
`rt_compound_build_n`. Mode-4 (`--compile --target=x86`) emits a SEPARATE binary
via `as`+`gcc`; an in-process `&node` baked into it would be a dangling pointer at
run time — so the BINARY trick CANNOT transfer.

Verified live: a compound call-arg rung (`show(mary) :- likes(X,Y), write(Y)`)
compiles+runs to `food` in mode-4 with 3 walker calls in its emitted `.s`; and
`bb_goal.cpp` (MEDIUM_TEXT-only) externs + uses `emit_build_compound_term` to
build IR_STRUCT call-args. Deleting it would regress mode-4.

Collapsing the TEXT walker to one `rt_*` call is a REAL feature — it needs an
IR→rodata serialization substrate so the separate mode-4 binary can pass a valid
pointer (this is the same "needs a real runtime substrate" the GOAL file already
flags for mode-4 dynamic/compound). It is NOT part of the 1a duplication-kill.

## Files touched

- `src/interp/IR_interp.c`: +2 lines — `rt_node_to_term_ptr` wrapper after
  `resolve_node_to_term` (exported `T` symbol in `libscrip_rt.so`).
- `src/emitter/BB_templates/bb_builtin.cpp`: −95 lines net — deleted `_bin`
  walker + its comment block; added the 5-line `emit_term_from_node_bin` helper;
  rerouted 23 call-sites; added the `rt_node_to_term_ptr` prototype.
- `GOAL-PROLOG-BB.md`: PL-HY-1a bullet rewritten with the corrected analysis;
  gate-table watermark → `abae7c1`.

Commits: SCRIP `abae7c1`; .github `a01a734e` (GOAL update) + this handoff.

## NEXT — PL-HY-1b (de-cram the builtin families)

`bb_builtin.cpp` is still 2,187 lines = ~18 builtin family shapes crammed in one
`bb_builtin_str`. Split each family (type-tests, arith/is, sort/format,
atom/string, writeq/numbervars/copy_term, functor/arg/univ, atom_concat/chars/
codes, nb_setval/getval, aggregate, atomic_list_concat, succ/plus, format, …)
into its own `bb_builtin_<family>.cpp`; group 95%-identical functors within a
family. Keep `bb_builtin.cpp` as a thin name-dispatch ROUTER (keeps the
`extern "C" void bb_builtin(IR_t*)` so `emit_core.c` dispatch is untouched).
**Worked pattern to copy: `bb_binop_*.cpp` + the 38-line `bb_binop.cpp` router.**
GATE-3 m2/m3 111/111 byte-identical after EACH family; m4 75 held; commit per family.

Note: the shared `emit_build_compound_term` (TEXT) + the new `emit_term_from_node_bin`
(BINARY) + `bb_pl_op_floaty` are file-local helpers several families call — when
splitting, either keep them in the router file and `extern` them into the family
files (as `bb_goal.cpp` already externs `emit_build_compound_term`), or move them
to `bb_template_common.h`. Pick one and be consistent.

## Build / verify recipe (next session)

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh        # nasm/m4/libgc-dev
make -j4 scrip && make libscrip_rt             # BOTH — emit path lives in scrip AND libscrip_rt
bash scripts/test_smoke_prolog.sh              # GATE-1 (m2 5/5 HARD)
bash scripts/test_prolog_rung_suite.sh         # GATE-3 (m2 111/111, m3 111/111, m4 75/0/36)
bash scripts/test_smoke_icon.sh ; bash scripts/test_smoke_snobol4.sh   # sibling HARD m2 (shared-file check)
bash scripts/test_gate_no_bb_bin_t.sh          # 0
bash scripts/test_gate_template_medium_invisible.sh   # 343 (informational)
bash scripts/prove_lower2.sh                   # PASS
```

Authors: LCherryholmes · Claude Opus 4.8
