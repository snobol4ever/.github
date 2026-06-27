# PAS-UNBOX — Pascal value-representation characterization (2026-06-27, Claude)

Asm-grounded re-diagnosis of the Pascal slowdown. **Corrects `corpus/BENCHMARKS-PASCAL.md`,**
whose stated root cause (boxed/gmp integers) is not supported by the build or the emitted asm.
No code changed in this rung — characterization only, design frozen below.

## What the benchmark doc gets wrong

The doc attributes the 5,000–38,000× array-kernel slowdown to "boxed / heap-allocated
integers" and "the runtime links libgmp and libgc." Two of those are false:

1. **No gmp is linked.** `SCRIP/Makefile:36` is `LIBS := -lgc -lm`. There is no `-lgmp` in
   the build or the M4 link recipe. (`libgmp-dev` appears only as an apt comment.)
2. **Scalar integer arithmetic is already unboxed and inline.** `bb_binop_arith.cpp`
   (the `!_.op_num_real`, ADD/SUB/MUL/DIV/MOD arm) emits register-native
   `add` / `sub` / `imul` / `cqo;idiv` straight on the descriptor value-halves, tags `DT_I`,
   and jumps `γ`. No call, no allocation. `rt_num_arith` itself (`runtime/arithmetic.c`)
   returns `INTVAL(li+ri)` by value — a 16-byte struct, no malloc, no gmp. A plain
   `i := i + 1` is already roughly fpc-class.

## True cost centers (asm evidence)

### 1. Aggregate element access = the dominant array-kernel cost

Pascal lowers `a[i]` → `IR_CALL "arr_get"` and `a[i] := v` → `IR_CALL "arr_set_pure"`
(`lower_pascal.c:468/246`). Both reach the runtime through `rt_call_arr@PLT` with the sink
name passed as a string operand (`.Lrkfn..: .string "arr_get"`), dispatching in
`by_name_dispatch.c` to a representation where **`array[1..N] of integer` is a C string with
elements separated by `SOH` (\x01) and stored as decimal ASCII text**:

- `arr_get(a,idx)` (`by_name_dispatch.c:802`): linear `strchr`-scan counting separators —
  **O(idx) per read** — then parses the text segment back to a number.
- `arr_set_pure(a,idx,v)` (`by_name_dispatch.c:1416`): `GC_malloc(slen*5 + …)` and **rebuilds
  the entire array string with `sprintf("%d")` of every untouched element — O(n) malloc +
  O(n) reserialize on every single store.**

Evidence — `a[i] := i*i` (probe `iarr.pas`, M4 `.s` lines 211–232): per iteration it marshals
args, reads `i` twice via `call rt_gvar_get_int@PLT`, `imul`, then
`# BOX IR_CALL arr_set_pure(...) -> rt_call_arr` → `call rt_call_arr@PLT`. A 500-element
bubble sort thus does a ~2.5 KB `GC_malloc` and re-stringifies all 500 elements *per swap*.
That compound — not boxing — is the 5,000–38,000×.

### 2. Global scalar reads are still by-name even with the arena

Same asm (iarr.s:224–227): reading `i` for `i*i` emits `call rt_gvar_get_int@PLT` ×2, not an
arena `[rbx+k*16]` load. PAS-GVA wired the arena and made literal *writes* land there, but the
read path still carries the DT_I tag-guard fallback and it fires on the hot path. This is what
the existing **PAS-GVA-3** rung targets (retire the by-name read fallback).

### 3. Reals are truncated to int — a correctness bug, not (yet) a speed one

Probe `rarith.pas` (`x:=1.5; y:=2.25; z:=x*y+x; writeln(z)`) should print 4.875; SCRIP prints
`3` — i.e. 1·2+1. Reals are **not routed to the real arith path in lowering**; they fall into
the integer inline arm with truncated values (zero `rt_num_arith`, zero SSE in the `.s`).
Separately, **no inline-SSE template exists anywhere** (`grep addsd|mulsd src/emitter/BB_templates`
== 0), so even Icon real arithmetic goes through the `rt_num_arith` call. Real arrays on the
text path are worse — `sprintf("%d")` cannot round-trip a double.

## The fix vehicle already exists, unused by Pascal

`ARBLK_t` (`runtime/core/core.h:70`) is a real flat block:
`{ int lo, hi, ndim, lo2, hi2, proto_bare; DESCR_t *data; }` — a contiguous descriptor array
with bounds. Icon / Raku / SNOBOL use it (`aggregates.c`, `core/core.c`). Pascal alone lowers
to the SOH-text string sinks. Routing Pascal arrays onto `ARBLK_t` makes `a[i]` read
`mov rax,[data + i*16 + 8]` and `a[i]:=v` `mov [data + i*16 + 8],rax` — O(1), zero per-access
allocation. `ARBLK_t` is language-blind, so no `LANG_PASCAL` guard is introduced.

## Implementation strategy — DT_A / DT_S coexistence (the safe, language-blind path)

The SOH-delimited-string aggregate representation is **shared across all languages**:
`arr_get` / `arr_set_pure` / `arr_init` / `arr_last` sit in the same `by_name_dispatch.c`
substrate as `split` / `join` / `elems` / `words` / `comb` / `lines`, which Raku and SNOBOL
lists use. So the flip CANNOT be a localized Pascal edit to those sinks, and it cannot replace
the string representation wholesale without cross-language regression.

The principled path is **representation coexistence**: make a Pascal array a `DT_A` `ARBLK`
descriptor; add a `DT_A` branch to each sink that does the O(1) indexed load/store; leave the
existing `DT_S` string branch **byte-identical** for the other languages. Dispatch is on the
descriptor type (`args[0].v == DT_A`), never on `LANG_PASCAL` — so it passes
`BB-TEMPLATES-LANG-AUDIT.md`, and the four-language gate stays green by construction (non-`DT_A`
callers hit unchanged code). This also makes the rung **incrementally safe**: each `DT_A` branch
is an addition, and the win appears only once Pascal *creation* emits `DT_A`. The pieces below
must land as one coherent change (create + read + write + print all speak `DT_A`), but each is a
guarded addition rather than a rewrite of the shared path.

## Proposed rung ladder — PAS-UNBOX (priority order)

The single root fix is: replace the SOH-decimal-text aggregate representation with a flat
typed `ARBLK_t` block (native element) reachable by O(1) indexed load/store, via the `DT_A`/`DT_S`
coexistence above. Integer and real elements share the descriptor-element form; char arrays want
a flat byte buffer.

- [x] **PAS-UNBOX-0 — CHARACTERIZE (this; no code change).** Findings above; design frozen.
- [ ] **PAS-UNBOX-1 — integer-array READ via ARBLK.** Route `arr_get` of an `ARBLK`-backed
  array to an O(1) indexed descriptor load (keep the string sink as fallback for any
  representation not yet migrated). Gate: M3 128/0, M4 128/0; nest/array probes green;
  four-language cross-check (shared `by_name_dispatch.c` → landmine #6); template byte-identity.
- [ ] **PAS-UNBOX-2 — integer-array WRITE in place.** `arr_set_pure` of an `ARBLK`-backed
  array becomes an O(1) `data[idx]=v` store — **no `GC_malloc`, no reserialize.** This is the
  headline win. Same gate set.
- [ ] **PAS-UNBOX-3 — creation / init / pass / print.** Array allocation builds an `ARBLK`
  (with `lo..hi` bounds) rather than a SOH-string; `arr_init`, value-param copy, var-param
  cell, and `writeln` of an element all consume the block. Same gate set.
- [ ] **PAS-UNBOX-4 — packed array of char as flat byte buffer.** `s[i]:=c` → `mov byte`;
  whole-string compare via `memcmp` rather than descriptor coercion. (Matters chiefly if
  PAS-BENCH pursues Dhrystone; smallest of the set for the current corpus.) Same gate set.
- [ ] **PAS-UNBOX-5 — real correctness (multi-part; correctness > speed).** Root cause located:
  `lower_pascal.c` tracks **no declared types**, so a real *variable* read lowers to a bare
  `IR_VAR`/`IR_VAR_FRAME` with no real tag. The emit-time detector `binop_is_num_real`
  (`emit_bb.c:1377`) decides integer-vs-real *statically* from operand shape, so `z := x*y + x`
  on real variables is mis-classified as integer and run through `imul`; and `x := 1.5` itself
  truncates (the real-literal store arm is incomplete on some assign paths). A real *literal*
  alone is fine (`TT_FLIT` → `IR_LIT_F`). Fix spans: (a) propagate declared real type in
  `lower_pascal.c` and tag real variable reads; (b) make all assign arms (frame + gvar) store
  `DT_R` for a real RHS uniformly; (c) let `binop_operand_real_static` see real-typed variables;
  (d) real arrays use a native `double` `ARBLK` element. Gate: real probes correct in both modes;
  `realparam` `.ref` fixed from the 1-byte stub to `       3.0`.
- [ ] **PAS-UNBOX-6 — (speed, optional) inline-SSE real arm.** `movsd`/`addsd`/`mulsd`/`divsd`
  on the descriptor value-halves (the value half is exactly 8 bytes = one IEEE double),
  eliminating the `rt_num_arith` call. Net-new template, dispatched on a real-type IR flag,
  language-blind (no `LANG_PASCAL` guard); reusable by Icon. Same gate set.
- [ ] **PAS-GVA-3 (existing) — retire by-name read fallback for globals.** Kills the
  `rt_gvar_get_int` hot-read calls shown above once arena writes are complete.

After the cluster lands, re-run PAS-BENCH: the array kernels (sieve / intmm / bubble / quick)
should collapse from 5,000–38,000× toward fpc, since the per-write `GC_malloc`+reserialize is
the term that dominates them.

## Landmines specific to this work

- **Migrate read-side first, behind the existing string path as fallback**, and flip writes
  only once reads prove out — never leave the corpus half-converted between gate runs.
- `by_name_dispatch.c` is shared runtime: after any edit run `make libscrip_rt` and ALL FOUR
  language gates + template byte-identity before landing (landmines #4, #6).
- `ARBLK_t` is the language-blind vehicle; introducing a `LANG_PASCAL` guard would fail
  `BB-TEMPLATES-LANG-AUDIT.md`. Keep dispatch on representation/IR shape.
- Correct the `corpus/BENCHMARKS-PASCAL.md` "Interpretation" section (the boxed/gmp claim)
  when the first array rung lands, with the measured before/after.
