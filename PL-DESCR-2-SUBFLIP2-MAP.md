# PL-DESCR-2 SUB-FLIP 2 — EXECUTION MAP (the atomic Term* → inline-cell flip)

Recovery point: SCRIP `82d4c4d` (green: 115/115 m3+m4, smoke 5/5, bench 16/0/0, no-new-global doomed 15, no-vstack 0).
This step has NO buildable-and-green midpoint: every frame slot's bytes change meaning in one build
(an unbound var cell's low 8 bytes are `{DT_PLVAR(4), slot(4)}`, which is garbage read as a `Term*`),
so every reader/writer of a slot flips together. Edit ALL sites, build once, debug, then re-run the floor.

---

## 0. The representation change

| | BEFORE (today, post sub-flip 1) | AFTER (sub-flip 2) |
|---|---|---|
| slot `[r12 + GZ_CELL_OFF(s)]`, stride 16 | low 8 bytes = a `Term*` (24-byte heap `Term`); high 8 = pad | the inline 16-byte `pl_cell_t` IS the value |
| int | `Term*` → `{TERM_INT, ival}` on heap | `{DT_I, 0, ival}` inline, NO heap |
| atom | `Term*` → heap | `{DT_A, atom_id, atom_id}` inline |
| unbound var | `Term*` → heap `{TERM_VAR, slot}` | `{DT_PLVAR, slot, &self}` inline (self-ref) |
| compound | `Term*` → heap `Term{args=Term*[]}` | `{DT_PLREF, fn<<16|ar, heap}`; heap = block of inline `pl_cell_t[]` |
| trail | `g_resolve_trail : Trail` (of `Term*`), mark = `top` (int) | `g_pl_trail : pl_trail_t` (of cell words), mark = `top` (int) — **mark stays an int**, so mark/cursor frame cells are UNCHANGED |
| shadow env | `g_resolve_env[slot]` aliases the cell's `Term*` | DELETED — the cell is the only value |

Funnels already built (sub-flip 1, isolated-tested): `pl_cell.h` (`pl_deref`/`pl_bind`/`pl_unify`/`pl_init_var`/
`pl_make_*`/`pl_trail_*`, test 33/33) and `pl_cell_conv.h` (`pl_cell_to_term`/`pl_unify_term_into_cell`, test 11/11).

---

## 1. Call-site patterns (28 template files, 74 GZ_CELL_OFF sites)

### Pattern A — load-cell-to-pass-to-helper: `mov <reg>,[r12+off]` → `lea <reg>,[r12+off]`  (~50 sites)
The reg is passed as a `void*cell` arg to a helper that today does `(Term*)cell→term_deref`. After the flip the
helper reads the cell inline, so the call site must pass the cell's ADDRESS, not the loaded `Term*`. Sites:
- `bb_cell_unify.cpp` L68,L69 (var-var), L76,L84 (unify-const lhs)
- `bb_det_is.cpp` L22,L32,L33,L48,L49,L50,L64 ; `bb_det_cmp.cpp` L24,L27,L43,L45
- `bb_det_arg/atom_op/char_type/copy_term/format/functor/nb_getval/nb_setval/numbervars/`
  `retract/sort/succ_plus/term_string/type_test/univ/abolish/assertz/write` — every arg-load `mov rdi/rsi/rdx/...,[r12+off]`
- `bb_det_write.cpp` L20,L23,L26 (three writeq/write_canonical variants, all the same slot)
- `bb_cell_findall.cpp` L38,L39 (acc,result), L72,L74 ; `bb_cell_choice.cpp` L38 (cond) ; `bb_cell_dyniter.cpp` L19

### Pattern B — frame-base lea (ALREADY `lea`, NO CHANGE): 4 sites
`bb_callee_frame.cpp` L27, `bb_cell_call.cpp` L24, `bb_cell_dyniter.cpp` L20, `bb_cell_findall.cpp` L61 — these
compute a child/local cell BLOCK base for `rt_*_cells_init`; an address is already what's wanted.

### Pattern C — inter-frame argument passing (THE #1 RISK SEAM): `bb_cell_call.cpp` + `bb_callee_frame.cpp`
Today an arg is an 8-byte `Term*` copied caller→callee (both frames alias the same heap `Term`). A cell is 16 bytes
and lives IN the slot, so a Term*-copy is wrong. **Design: pass cell ADDRESSES; copy the 16-byte word.** Copying a
self-ref var word `{DT_PLVAR,slot,&caller_cell}` makes the callee cell a REF to the caller cell — exactly the desired
arg aliasing, for free. Concrete:
- `bb_cell_call.cpp`:
  - args 0–3 (L36 loop): `mov <areg>,[r12+off]` → `lea <areg>,[r12+off]` (pass caller arg-cell ADDRESS).
  - args 4+ (L28/29 loop): today `mov r11,[r12+caller_off]; mov [rdi+off(i)],r11` (8-byte). →
    16-byte word copy into the callee frame: `movdqu xmm0,[r12+caller_off]; movdqu [rdi+off(i)],xmm0`
    (or two 8-byte `mov` via r11). The copied self-ref word becomes a ref to the caller cell — correct.
  - `β` resume (L?): `mov rdi,[r12+GZ_CELL_OFF(child_slot)]` (load the callee frame closure ptr) — this loads the
    CLOSURE pointer (the `rt_enter` block addr stored in the child slot), NOT a Term value. **Stays `mov`** —
    the child slot holds a frame pointer, which is genuinely an 8-byte pointer, not a 16-byte cell. (Confirm:
    `rt_enter(void**slot,...)` stores the frame ptr at `*slot` = low 8 bytes of the child cell; treat the child
    slot as a raw pointer cell, not a value cell. Reserve it but never `pl_init_var` it.)
- `bb_callee_frame.cpp`:
  - op_sa==0 arg-receive (L22 loop): today `mov [r12+off(i)],<areg>` stores the incoming Term* register. With
    addresses-in-registers, copy 16 bytes from `[<areg>]` into the formal cell `[r12+off(i)]`:
    `movdqu xmm0,[<areg>]; movdqu [r12+off(i)],xmm0` (areg = caller arg-cell address). Self-ref→ref gives aliasing.
  - L27 `lea rdi,[r12+GZ_CELL_OFF(arity)]; rt_pl_cells_init` — initializes the NON-arg locals only (cells
    [arity..nslots)). UNCHANGED except `rt_pl_cells_init` itself flips to write `pl_init_var` words (§3).
  - mark store/load (L?): `rt_trail_mark`/`rt_trail_unwind` return/take an int — UNCHANGED at the template; only
    their bodies retarget `g_pl_trail` (§4).

### Pattern D — control cells (NO CHANGE): marks / cursors / gates / accumulators
`bb_cell_choice.cpp` L26,L27 (mark_off/cur_off computes), `bb_cell_catch.cpp` L16, `bb_cell_ite.cpp` L10,
`bb_cell_dyniter.cpp` L35 (mark, eax-int),L39 (cursor),L42 (load mark), `bb_callee_frame.cpp` FR(0)/FR(4) mark
slots, `bb_cell_findall.cpp` L56 (acc store). These hold ints (trail marks, clause cursors, ITE gates) or the
findall accumulator pointer — NOT logic-var values. The mark is an int into the trail (whose mark is still an int),
so these are byte-compatible. **VERIFY findall L56 acc**: if it stores a Term* list accumulator that later feeds a
cell-native consumer, it routes via the bridge; if it stays a Term* consumed only by `rt_pl_findall_*` Term helpers,
leave it. (Findall builds a Term list result and unifies it into the result cell → bridge `pl_unify_term_into_cell`
at the result-bind site.)

### The `gzu_build` dual-role seam (THE #2 RISK SEAM) — `bb_cell_unify.cpp` `gzu_build()`
`gzu_build` lowers an IR term to rax. Today rax = a `Term*` used two ways that DIVERGE after the flip:
1. as a UNIFY operand (stored to rsp, passed to `rt_unify_terms`) → now wants the operand's cell ADDRESS.
2. as a COMPOUND ARG (stored into the rsp arg array for `rt_compound_build_n`) → now wants the arg's 16-byte cell WORD.

Split it:
- `gzu_build_operand(nd)` → returns a cell ADDRESS in rax for var/the-cell-itself; for a literal int/atom/float,
  it must MATERIALISE a temp cell (stack or a tiny helper `rt_pl_lit_cell(kind,ival,sval,dval)→pl_cell_t*`) and
  return its address, because a literal has no home cell. Used by `bb_cell_unify` operand build.
- compound build (`IR_STRUCT`/`IR_ARITH`): build an array of 16-byte cell WORDS (not Term*), then call a new
  `rt_pl_compound_cell(functor,arity,pl_cell_t*arg_words)` that allocates `{DT_PLREF, fn<<16|ar, heap}` with `heap`
  = a GC block holding the `arity` inline arg cells (copied from the word array). For each arg: a var → copy its
  cell word (self-ref→ref aliases the caller var into the structure); a literal → an inline `{DT_I/A/R}` word; a
  nested compound → recurse. The rsp array becomes `arity*16` bytes; per-arg store is a 16-byte `movdqu`.
- `rt_compound_build_n` (Term-building) is then OFF the hot GZ path. Keep it for m2/legacy; GZ uses the cell builder.

NOTE measured (PL-DESCR-0): fib/tak are 100% scalar — compound build never fires there, so the arithmetic-bench
win is unaffected by this seam. But zebra/qsort/sendmore DO build lists/structs, so the cell builder MUST be correct
to hold the 115 floor + those benches. This seam is not skippable.

---

## 2. Helper internals (rt_runtime.c + unification.c) — hot native, deep bridged

Signatures DO NOT change (every helper already takes `void*cell` / `int slot`-free). Only bodies change.

### HOT (rewrite native on `pl_cell.h`), each `(Term*)cell→term_deref→unify(&g_resolve_trail)` ⇒ `(pl_cell_t*)cell→pl_deref→pl_unify(&g_pl_trail)`:
- `rt_runtime.c`: `rt_pl_is_cell_int`, `rt_pl_is_cell_float`, `rt_pl_is_cell_arith`, `rt_pl_is_cell_bivar`,
  `rt_pl_arith_cmp_cell_val`. Each: read operand cells inline (`pl_is_int`/`pl_int_val`/`pl_float_val`), compute,
  build a result cell word (`pl_make_int`/`pl_make_float`), `pl_unify` into the lhs cell, trail = `g_pl_trail`.
- `unification.c`: `rt_unify_terms` — becomes `rt_pl_unify_cells(pl_cell_t*a, pl_cell_t*b)` = `pl_unify(a,b,&g_pl_trail)`
  (the var-var + operand-address path). `rt_pl_unify_cell_const(cell,kind,ival,sval)` — build the const cell word,
  `pl_unify` into `cell`. `rt_pl_unify_cell_float(cell,dval)` — same. `rt_pl_type_test_cell(cell,fn)` — `pl_deref`,
  switch on `pl_tag`. `rt_pl_write_cell/writeq_cell/write_canonical_cell(cell)` — `pl_deref`, print inline
  (recurse compound arg cells); for atoms use `prolog_atom_name(pl_atom_id(c))`.

### DEEP (wrap via bridge, do NOT rewrite): copy_term, `=..` (univ), functor, arg, sort, numbervars, term_string, format, atom-ops, char_type, succ, assertz/retract/abolish clause terms, dyniter scan, findall result-bind.
Pattern at each call: BOUND inputs → `pl_cell_to_term(cell)` (read-only Term view) → call the existing Term-based
deep helper → `pl_unify_term_into_cell(dst_cell, result_term, &g_pl_trail)`. UNBOUND inputs are handled cell-natively
at the site (`pl_is_var` + `pl_unify` into the cell) so there is NO writeback-through-a-materialised-var (the bridge
landmine the conv header warns about). The clause store (assertz/retract/dyniter) keeps Term clauses; head/goal
terms cross the bridge at assert (cell→Term) and at unify-against-store (Term→cell via `pl_unify_term_into_cell`).

### `rt_node_to_term` IR_LOGICVAR arm
Today: `rt_pl_env_ensure(slot); g_resolve_env[slot] ?: term_new_var`. This is the legacy node→Term materialiser.
On the GZ path it is reached only from `gzu_build` literal/atom arms (which build fresh Terms for compound args) —
those move to the cell builder (§1 gzu seam). Audit remaining callers; if none on the GZ path, the IR_LOGICVAR arm
+ its `g_resolve_env` read die with the env.

---

## 3. Frame init — write inline var cells, drop the env sync

- `rt_pl_gz_init(frame,nslots)`: replace `Term*v=term_new_var(i); *(Term**)(base+8+16*i)=v; g_resolve_env[i]=v;`
  with `pl_init_var((pl_cell_t*)(base+8+16*i), i);`. Drop `rt_pl_env_ensure` + the `g_resolve_env[i]=v` line.
  (offset base is `+8` for the main/gz frame; the leading 8 bytes are the frame header/closure word.)
- `rt_pl_cells_init(cells,n)`: replace the per-cell `term_new_var`+env-sync with `pl_init_var((pl_cell_t*)(base+16*i),i)`
  for `i in [0,n)`. (callee local-cell init; offset base is `+0` here — confirm against `bb_callee_frame` L27 lea.)
- `rt_enter(slot,nslots)`: allocation size already `8 + 16*nslots` — UNCHANGED. (Cells are zero-from-GC then
  `pl_init_var`'d by `rt_pl_cells_init`; the arg cells [0,arity) are filled by the arg-copy seam, §1 Pattern C.)

---

## 4. Trail — `g_resolve_trail` (Term) → `g_pl_trail` (cell)

- Define `pl_trail_t g_pl_trail;` (init at startup; `pl_trail_init`). It is the Prolog runtime spine; mark = int top
  (so the `mark_slot` frame cells are byte-unchanged). Per the BIG NOTE this is a GLOBAL for now; the r13/r14/r15
  register move is a SEPARATE deferred rung — do NOT attempt it here.
- `rt_trail_mark()` → `return pl_trail_mark(&g_pl_trail);` ; `rt_trail_unwind(m)` → `pl_trail_unwind(&g_pl_trail,m);`.
- Every hot helper's `unify(...,&g_resolve_trail)` → `pl_unify(...,&g_pl_trail)`; every `trail_mark/trail_unwind`
  on `g_resolve_trail` in the GZ helpers → the `pl_trail_*` equivalents.
- `g_resolve_trail` (the Term trail) stays defined for m2/legacy `unify()` callers; it is simply unused on GZ.

---

## 5. Delete `g_resolve_env` + `rt_pl_env_ensure`; handle the dead readers

LIVE readers of `g_resolve_env` today (the rest are `src/attic/*` = dead residue):
- `unification.c` — `rt_node_to_term`/`rt_unify_const`/`rt_unify_var_var`/`rt_pl_env_ensure`/`rt_pl_gz_init`/
  `rt_pl_cells_init`. The cell-native rewrites (§2,§3) remove every read/write here.
- `arithmetic.c` `rt_arith` (lines 121–134) — the by-SLOT arith path. **Reached only from the legacy non-`cell`
  boxes** (e.g. `bb_arith`/`bb_unify`, dispatched via `IR_UNIFY`/`IR_ARITH`-by-slot, not `IR_CELL_*`). On the GZ
  path arith goes through `rt_pl_is_cell_arith` (cell-based). ACTION: confirm `rt_arith` has no GZ caller (grep the
  emit dispatch); if dead, leave it referencing a local stub or delete with its box. If any GZ caller survives,
  convert it to cell form. Do NOT let it keep `g_resolve_env` alive.
- `bb_unify.cpp` `rt_unify_const`/`rt_unify_var_var` (slot-indexed) — the legacy `IR_UNIFY` box. GZ uses
  `IR_CELL_UNIFY`/`bb_cell_unify`. These become dead readers; they vanish when the box is stubbed (or leave them
  on a private stub trail with no `g_resolve_env`).
- `resolution.c:22` (the definition `Term **g_resolve_env=NULL;`) + `resolution.h:35` (extern) — DELETE.
- `polyglot.c:57` (`g_resolve_env=NULL;` reset) — DELETE.
- `scrip.c:3234` (`extern Term **g_resolve_env;`) — DELETE (verify the surrounding emit helper no longer needs it).

Gate: `scripts/test_gate_pl_no_new_global.sh` — remove `g_resolve_env` from the LEGACY-DOOMED list and drop
`DOOMED_FLOOR` 15 → 14. (This is the §"NO NEW GLOBAL" ratchet: the floor only ever DROPS.)

---

## 6. Edit order (one batch — no buildable midpoint) + validate sequence

1. **Runtime first (compiles independently of templates):** add `pl_trail_t g_pl_trail` + retarget `rt_trail_*`;
   rewrite the HOT helpers native; wrap the DEEP helpers via bridge; flip `rt_pl_gz_init`/`rt_pl_cells_init` to
   `pl_init_var`; add `rt_pl_compound_cell` + `rt_pl_lit_cell`; neutralise `rt_arith`/`bb_unify` env reads.
2. **Templates:** Pattern A `mov→lea` (~50 sites); Pattern C arg-copy seam (call + callee_frame); the `gzu_build`
   operand/compound split + compound cell builder calls. Patterns B/D untouched.
3. **Delete** `g_resolve_env` def/extern/reset; drop it from the gate; `DOOMED_FLOOR` 15→14.
4. **Build:** `make -j4 scrip && make libscrip_rt`. Fix compile errors (signature/extern drift) until clean.
5. **Validate, fail-fast order (cheapest first):**
   - `bash scripts/test_smoke_prolog.sh` (m3+m4 5/5).
   - `./scrip --compile bench/fib.pl` → assemble → run → diff `fib.expected` (the scalar hot path — first proof).
   - `bash scripts/test_prolog_rung_suite.sh` (115/115 m3+m4 — the HARD floor).
   - `bash scripts/test_bench_prolog_modes.sh` (16/0/0; zebra/qsort/sendmore prove the compound cell builder).
   - `bash scripts/test_gate_pl_no_new_global.sh` (doomed 14), `grep -rn g_vstack src/ | wc -l` (0).
6. **Only on full green:** regen `.s` artifacts (codegen changed — RULES.md step 4), commit SCRIP, push, run
   `scripts/handoff_status.sh`. If the wall is hit before green: `git checkout -- .` (or `git reset --hard 82d4c4d`)
   and write the handoff; the tree returns to the green recovery point. NEVER commit a non-green tree.

## Risk ranking (validate in this order)
1. **Inter-frame arg copy (Pattern C)** — wrong unit/aliasing = recursion segfault. Prove on fib FIRST.
2. **`gzu_build` compound split + `rt_pl_compound_cell`** — wrong arg-block = struct programs corrupt. Prove on
   zebra/qsort.
3. **Trail swap** — a missed `g_resolve_trail`→`g_pl_trail` = bindings not undone on backtrack = wrong solutions
   under choice. Prove on queens_8 (deep backtracking).
4. **Deep-builtin bridge sites** — a writeback-through-materialised-var = lost binding. Prove on the term-ops rungs.
