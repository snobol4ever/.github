# FINDING — PL-SINK-2: emitted `$unify_lst` READ-mode fast path (s143, 2026-07-25)

**Author:** Claude (3rd dev). **Track:** GOAL-PROLOG-BB / PL-SINK ladder (Lon directive:
"Rewrite Prolog to use Byrd Boxes. Move 99% out of the runtime.").
**Rung:** PL-SINK-2 (`$unify_lst`, the nrev leaf) — the SECOND emitted data-plane fast
path, following PL-SINK-1 (`$unify`, s142) which is the reference implementation.

## What landed

An inline READ-mode fast path for `$unify_lst(Subject, Head, Tail)` emitted directly
into the calling Byrd box, in `SCRIP/src/templates/bb_call_fn.cpp`
(`sink_unify_lst_str`, internal label decade 60–77, `x86(...)` encoders only, both
media). The C leaf `rt_pl_dop_unify_lst` is demoted to a slow-path oracle, entered with
**unmodified `rdi=args` (esi=3)**, so every deferred shape is bit-identical to the leaf
by construction (SINK CONTRACT §1, WHOLE-ARM-OR-DEFER).

Hooked in `bb_call_fn_str`'s dfp chain beside the SINK-1 `$unify` branch:
```
else if (dfp && nargs == 3 && !strcmp(fn, "$unify_lst") && !getenv("SCRIP_NO_SINK"))
    s += sink_unify_lst_str(argbase, (uint64_t)(uintptr_t)dfp, dsym);
```

## The inline arm (deliberately conservative first cut)

Mirrors `dop_unify_lst` (by_name_dispatch.c) arm-for-arm. The inline path fires for
exactly ONE shape — nrev's input-list destructuring hot spot:

- **Subject** deref'd (reusing SINK-1's `sink_deref` verbatim) is a **bound `'.'/2`
  cons** (tag `DT_PLREF=14`, `slen == dot_sl`), AND
- **Head and Tail** both deref to **DISTINCT unbound cells**,

then → **double bind** (`Head ← kids[0]`, `Tail ← kids[1]`) via a single **2-entry trail
push**, result = `*Subject`.

Everything else defers to SLOW (bit-identical, zero partial state):
- **unbound Subject** → WRITE mode, which *allocates* the kids array — that is
  **SINK-3's carve**, not SINK-2's.
- **Head/Tail aliasing** (the two derefed cell pointers are equal) → SLOW. The C derefs
  Head, binds it, THEN derefs Tail; when `tc == hc` the second deref sees the first
  bind, so a blind inline double-bind would diverge. `cmp` the pointers; equal → SLOW.
- **any bound Head or Tail arm** → SLOW. The int-slen0 / bit-identical-vs-kid /
  recursive-`plw_unify_cells` sub-arms are SINK-2's follow-on; deferring them is provably
  zero-partial-state (no bind is executed before the SLOW jump).

This covers the O(n²) *input* traversal of nrev/append. The O(n²) *output* construction
(`append`'s 3rd arg `[X|L3]`, where the subject is unbound = WRITE mode) stays in the C
leaf until SINK-3.

### Trail write (2 entries)
Reuses SINK-1's validated trail model (verified against `pl_cell.h`:
`pl_area_t{base@0, top@8, limit@16, cap@24}`, `pl_trail_t{area@0, top@32}`; entries live
at `area.base + i*24`; grow condition `(top+1)*24 > cap`). The 2-entry variant: room
check `sub rax, 48` (need 48 bytes), write entry at `[top]` then `[top+1]`, `top += 2`.
Old cell bits are captured into each entry BEFORE the value copies, so entry order and
contents are identical to the leaf's two sequential `plw_bind` calls. Reuses SINK-1's
`_Static_assert` layout anchors beside `plw_bind` — no new baked offsets.

## Contract §3 — the runtime-interned id

`dot_sl = (intern(".") << 16) | 2` is assigned at RUNTIME (the mode-4 GZ preamble never
runs `prolog_atom_init`), so it CANNOT be a mode-4 immediate. Resolution: a new exported
cell `uint32_t g_plw_dot_sl` (by_name_dispatch.c), filled by `dop_unify_lst`'s existing
static-init on the first slow-path hit, RIPSEAL-loaded in the emitter
(`lea r10, [rip + g_plw_dot_sl]`, dual-medium — TEXT rip-relative symbol, BINARY live
address). Safety: **`g_plw_dot_sl == 0` → SLOW**, so a run that hasn't yet interned `.`
defers to the leaf (which interns and answers) rather than mis-failing a real cons.
Correctness never depends on the cell being populated. This is the one new global; SINK
CONTRACT §3 sanctions the per-leaf exported id cell (the `no_new_global` floor rises by 1).

## ⚠ Lesson of the session — a silent encoder gap

First build made nrev *fail* (empty output) while `SCRIP_NO_SINK=1` was correct. The
symptom was diagnostic: the **minimal 1-shot** list-unify worked, but **recursive**
append/nrev failed. Reading the emitted `.s` showed the cause:

```
lea r10, [rip + g_plw_dot_sl]
mov eax, dword ptr [r10 + 0]    ; eax = dot_sl
test eax, eax
je  .Lx33_72                     ; ==0 -> SLOW   (correct)
jne .Lx33_73                     ; <- NO cmp before this jne!
```

`x86("cmp", "eax", "dword ptr [r8 + 4]")` — a **`cmp reg, mem` form** — **emitted
nothing** (SINK-1 only ever uses `cmp reg,imm` / `cmp reg,reg`; the encoder has no
reg,mem case and drops it WITHOUT a bomb). So the following `jne` tested the leftover
flags from `test eax,eax`: whenever `dot_sl` was populated (nonzero), it jumped to
inline-FAIL. That exactly explains "minimal works (first call `dot_sl==0` → SLOW
populates it), recursion fails (2nd+ call `dot_sl!=0` → FAIL)."

**Fix:** load the slen into a register first, then compare registers:
```
mov edx, dword ptr [r8 + 4]
cmp eax, edx
jne .Lx..._73
```

**Takeaway for future rungs:** when a sink half-fires, eyeball the emitted `.s`. The
`x86()` front-end drops unsupported operand shapes silently; the missing encoder is the
bug, the wrong branch is the symptom. (`mov reg, mem` IS supported — `sink_deref` uses
it — so the load-then-compare workaround needs no new encoder.)

## Gates (all green)

- Prolog rung suite **164/164 across all three modes (interp / run / compile), run
  TWICE**.
- **Byte-identity** ON vs `SCRIP_NO_SINK=1` on nrev(30), nrev(5), append, rung06_lists,
  rung03_unify.
- **Mode-3 (`--run`) and mode-4 (`--compile`)** both correct on nrev.
- **Backtrack across inline trail entries** unwinds correctly (explicit test:
  `p([a,b,c],H,T), ..., fail` then a fresh `p([x,y],H2,T2)` → `got(a,[b,c])` then
  `again(x,[y])`); the append/nrev choice points also exercise this at scale.
- 22 corpus bench `.s` regenerated (10 changed — the list-heavy benches), 0 rejected.

## Performance — the first nrev movement of the ladder

Two mode-4 binaries, sink baked on/off at compile time, nrev(30) in a failure-driven
`between/3` loop ×20000 (trail rewinds per iteration; avoids the banked NO-LCO
deep-recursion trap):

| build            | best-of-3 |
|------------------|-----------|
| SINK OFF         | 6.055 s   |
| SINK ON          | 5.638 s   |
| **movement**     | **~7% (1.07×)** |

SINK-1 was FLAT on nrev (its heat is `$unify_lst`, not bare `$unify`), so this is the
first real nrev movement. It is modest and expected: only the READ half (input
destructuring) is inlined. nrev's dominant O(n²) cost is the OUTPUT-list construction,
which is WRITE mode and stays in the C leaf until **SINK-3's cons-carve** completes the
split. (The emitted-share KPI re-sample is a whole-ladder step at PL-SINK-FENCE, not
per-rung, per the ladder spec.)

## Files touched (local — push pending credential)

- `SCRIP/src/templates/bb_call_fn.cpp` — `sink_unify_lst_str` + `extern "C" uint32_t
  g_plw_dot_sl;` + the dfp-chain hook.
- `SCRIP/src/runtime/by_name_dispatch.c` — `uint32_t g_plw_dot_sl = 0;` + mirror into it
  from `dop_unify_lst`'s static-init.
- `corpus/benchmarks/prolog/bench/*.s` — 10 regenerated.
- `.github/GOAL-PROLOG-BB.md` — s143 LIVE CURSOR + PL-SINK-2 rung marked LANDED.

## Next

**PL-SINK-3 — the `$unify_lst` WRITE arm + `$mkc`** (the carve). Bump-allocate the kids
array against the `rt_plj` frontier (ARCH-ICON rbx-carve idiom
`mov rax,rbx; add rbx,K; cmp rbx,[limit]; ja slow`, HZ-1), seed unbound kids as
self-PLVARs, bind the subject to the `'.'/2` PLREF. This is where nrev's remaining ~86%
moves; allocating inline keeps GC in C by construction (exhausted → SLOW, CONTRACT §4).
Also revisit SINK-2's deferred bound-arm classes (int-slen0 / bit-identical / recursion)
once the carve lands.

## Banked (carried, none resolved here)

NO-LCO deep-recursion segfault + its cumulative-exhaustion sibling; nested-`\+` binding
leak; retractall/1 gaps; compiled-path silent-fail on undefined user predicates.
