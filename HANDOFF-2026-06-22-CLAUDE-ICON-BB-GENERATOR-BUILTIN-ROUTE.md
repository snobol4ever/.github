# HANDOFF — GOAL-ICON-FULL-PASS
## Generator/mutator builtin call routing LANDED (`95e8b02`). Suite 140→142 m3+m4. Corpus benchmark folders merged. Goal file trimmed.

**SCRIP HEAD: `95e8b02`** (pushed). **m3/m4 = 142/283**, FAIL 16, XFAIL 36, EXCISED 89. All gates green (no-stack 0, one-reg-frame 0, prolog 5/5 m3+m4). Corpus HEAD: `37bc1bc5`.

---

## WHAT LANDED THIS SESSION

### 1. Corpus: `benchmarks/icon/` + `benchmarks/jcon/` merged → single `benchmarks/icon/`
Commit `37bc1bc5` (corpus). jcon-only files moved in (geddump/tgrlink/version); concord.dat replaced with jcon superset; rsg.dat icon-master (1000-poem) kept; README-ICON-JCON.md updated. No programs/icon/ rung36 files touched.

### 2. GOAL-ICON-FULL-PASS.md trimmed
350 lines → 118 lines. Added DESCR_t BB discipline rule. Committed to .github `134dea99`.

### 3. Generator/mutator builtin call routing (`95e8b02`)
**Root cause (three layers):**

`find`, `seq`, `upto`, `push`, `put` were excluded from `rt_builtin_is_known()` by `builtin_is_generator()`. In the `g_descr_flat_chain` IR_CALL dispatch, this caused them to fall through to `FILL(nd, ...)` with **stale `g_emit.op_sval`/`op_dval`** — `bb_call()` then hit `CALL_ROUTE_FATAL` and aborted.

**The dval encoding (crucial for next session):**
- `dv==1.0` = chain mode (args inline as γ-linked chain nodes)
- `dv==2.0` = subgraph mode, list/idx style (`[]`/`MAKELIST`)
- `dv==3.0` = subgraph mode, standard (args in `IR_EXEC(nd).counter` as `IR_graph_t**` blocks)

`find("b","abc")` has `dv==3.0` (2 args → subgraph). The route classifier checked `dv==2.0` only — missed it.

**Fix (5 touch-points, all in 4 files):**
1. `by_name_dispatch.c`: promote `static builtin_is_generator()` → `int rt_builtin_is_generator()` (public). Added `push`/`put` to the set.
2. `rt.h`: declare `rt_builtin_is_generator`.
3. `emit_bb.c` `resolve_call_kinds_descr()`: retag `dv==2.0` generator/mutator IR_CALL → `IR_CALL_BUILTIN` (so walk_bb_flat routes via `flat_drive_call_builtin` not raw FILL).
4. `emit_bb.c` walk_bb_flat IR_CALL descr-chain branch: add `flat_drive_call_builtin` dispatch for `dv==3.0` generator/mutator nodes (before the existing userproc/FILL fallthrough). This is the key fix — `flat_drive_call_builtin` walks arg subgraphs via `ir_call_arg()` then calls `EMIT_PAIR_FILL`, which correctly populates `g_emit` fields via the pre-pass.
5. `emit_bb.c` `bb_call_route_classify()`: extend generator BYNAME to `dv==2.0 || dv==3.0`.
6. `emit_bb.c` `builtin_ok` guard: admit `IR_CALL_BUILTIN + rt_builtin_is_generator()`.
7. `bb_call.cpp`: declare `rt_builtin_is_generator`, remove debug probe.

**Verified:** `rung08_strbuiltins_find` PASS, `rung22_lists_put_bang` PASS. +2 both modes. Zero EXCISE→FAIL.

---

## REMAINING 16 FAILs (m3 == m4)

| Test | Error | Root cause | Difficulty |
|------|-------|-----------|-----------|
| `rung22_lists_push_put_size` | wrong output: `*[]` → 3 not 0 | `rt_size_d` called with the SIZE node's frame args (3 DESCRs in frame) instead of the list's `frame_size` field. `image(L)` correctly shows `list(0)` — the list is right, SIZE is wrong. | Small — rt_size_d bug |
| `rung08_strbuiltins_find_gen` | rc=124 | `every write(find("ll","hello"))` — `find` as a generator (multiple results). `rt_call_arr` returns only first result; the Box has no resume mechanism. Needs a resumable find wrapper or scan-context threading. | Medium |
| `rung30_builtins_misc_seq` | rc=134 abort | `every write(seq(1) \ 3)` — `seq` lowers as `IR_CALL_BUILTIN dv==3.0`, then `\3` is `IR_LIMIT`. `flat_drive_limit` aborts: "generator kind=9 has no mode-3 two-port emission". `seq` is kind 9 (`IR_CALL_BUILTIN`). `flat_drive_limit` only accepts `IR_TO`/`IR_TO_BY`/`IR_ALT`/`IR_BINOP_GEN`/`IR_LIST_BANG`. | Medium — limit + generator-kind |
| `rung32_strretval_strret_every` | rc=134 abort | `every write(tag("a"\|"b"\|"c"))` — user proc `tag` called via `bb_call` with `fn='tag'`, `dv=1.0` (chain mode). `dv==1.0` user-proc calls in the descr flat chain aren't routed to `flat_drive_call_userproc`; they hit FATAL. | Small — dv=1 userproc routing |
| `rung37_proc_lookup` | rc=134 abort | `proc("write",1)` — `proc()` builtin returning a function value. `fn=''`, `dv=3.0`. The fn name is empty because `proc` returns a function descriptor, not a simple value. Needs `proc()` byname dispatch. | Medium |
| `rung02_proc_fact` | rc=134 depth | `fact(5)` recursive: "recursion depth exceeded (4096)". Each native frame allocates stack frames; deep recursion exhausts. | Medium — frame depth |
| `rung03_suspend_gen` ×3 | empty output | `suspend i do i:=i+1` — IR_SUSPEND in flat chain produces no output. The EVERY+SUSPEND co-routine wiring is incomplete. | Large — BENCH-F4 territory |
| `rung13_alt_alt_cross_arg` ×2 | empty/wrong | `every write(1\|2,":",3\|4)` — multi-generator CALL args. `is_deep` ag-ring stale on carry. | Large — BENCH-F3 territory |
| `rung14_limit_*` ×3 | rc=124 timeout | `(1 to 10)\3` — `flat_drive_limit` structurally incomplete: no counter, no value pass-through. Generates unbounded output. | Medium — needs bb_limit.cpp |
| `rung19_pow_toby_real_toby_*` ×2 | rc=124 timeout | `1.0 to -1.0 by -0.5` — `bb_to` real-step negative direction missing. | Small — bb_to real step sign |

---

## RECOMMENDED NEXT STEPS (smallest +PASS first)

### 1. `rt_size_d` list-size bug (rung22_push_put_size) — +1, ~15 min
`rt_size_d` is called with the SIZE node's 3 frame-slot args (tag, slen, ptr) rather than the list's internal `frame_size` field. The list object itself is correct (`image` shows `list(0)`). Fix: in `rt_size_d`, when the DESCR is `DT_DATA` with `gen_type=="list"`, return `FIELD_GET_fn(v,"frame_size").i` (integer). Verify: `[]:=0, [1,2]:=2, [1,2,3]:=3`.

### 2. dv=1.0 userproc chain routing (rung32_strret_every) — +1, ~20 min
`every write(tag("a"|"b"|"c"))` — `tag` is a user proc called in chain mode (`dv==1.0`). In the descr flat chain, dv=1.0 calls currently only hit the FILL fallthrough if they're not in `rt_proc_is_registered`. Fix: in walk_bb_flat IR_CALL descr-chain block, before the existing `if (IR_LIT(nd).dval == 3.0 && rt_proc_is_registered(...))` check, add a dv==1.0 userproc dispatch: `if (IR_LIT(nd).dval == 1.0 && IR_LIT(nd).sval && rt_proc_is_registered(IR_LIT(nd).sval)) flat_drive_call_userproc(nd, ...)`. Verify: `tag("x")` → `[x]`.

### 3. `limit \` counter (rung14 ×3) — +3, ~1 hour
`flat_drive_limit` (emit_bb.c:1956) walks the count expr and the generator but has NO counter — just jmps. Need a `bb_limit.cpp` template (DESCR_t slot for counter, DESCR_t slot for limit value) implementing canonical `ir_a_Limitation` (irgen.icn:113): evaluate limit → `t := #limit; c := 1; goto gen.start; gen.success → emit; resume → if (t > c) { c++; resume gen } else fail`. **All temporaries must be DESCR_t (16-byte frame slots) per BB discipline.** Edge case: `\0` must yield nothing (gate first emission). Verify: `(1 to 10)\3` → `1 2 3`; `(1 to 10)\0` → nothing + `done`.

### 4. `rt_size_d` for `seq` + limit generator kind (rung30_seq) — ~30 min after #3
`seq` is `IR_CALL_BUILTIN` (kind 9). `flat_drive_limit` only accepts `IR_TO`/`IR_TO_BY`/`IR_ALT`/`IR_BINOP_GEN`/`IR_LIST_BANG`. Need to either: (a) add `IR_CALL_BUILTIN` to the accepted generator kinds in `flat_drive_limit`, or (b) wrap `seq` as a native generator kind. The simplest is (a): `IR_CALL_BUILTIN` with `rt_builtin_is_generator()` name can be treated as a resumable generator (rt_call_arr first call gives first value; subsequent calls via resume give next). Needs a save-slot for call state.

### 5. `real_toby` negative step (rung19 ×2) — +2, ~30 min
`1.0 to -1.0 by -0.5` — `bb_to.cpp` real-step arm. Canonical: `for (r=from; step>0 ? r<=to : r>=to; r+=step)`. Add `step<0` direction gate.

---

## DESCR_t BB discipline (all new BBs)
**Every frame temporary must be a full DESCR_t (16-byte slot), claimed via `bb_slot_claim(16)`, addressed as `FRQ(slot)` (low 8) and `FRQ(slot+8)` (high 8).** No raw int/pointer spills. SNOBOL4 pattern BBs use sub-16 `x86_scratch_off` for internal counters — separate discipline, don't touch.

## CANONICAL ANCHORS
- `limit`: `corpus/programs/icon/jcon-ref/irgen.icn:113` `ir_a_Limitation`
- `<-` (BENCH-F2, still gated): `oasgn.r` + irgen.icn:472
- dval encoding: `lower_icon.c:90` — `dv==1.0` chain, `dv==2.0` idx/list, `dv==3.0` subgraph
- `rt_builtin_is_generator`: `by_name_dispatch.c:18` (now public)
- `flat_drive_call_builtin`: `emit_bb.c:2243` — walks subgraph args via `ir_call_arg()` + EMIT_PAIR_FILL

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
