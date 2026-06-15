# HANDOFF 2026-06-15 — Pascal BB: patch-table cap, gvar-call-assign guard, unique .Lcallfn label

## TL;DR

Three clean fixes this session, all verified, three files touched total:

1. **`emit_core.c`** — `IR_ASSIGN` gvar-assign dispatch guard now admits stamped call-kinds
   (`ir_is_call_kind(op_a->op)`). Restored Pascal **M3 122/0** and **M4 122/0** (had regressed
   to 119/3 / 119/0+3SKIP after the concurrent `2fa5086` "IR_CALL split rung 5").
2. **`bb_call.cpp`** — `.Lcallfn` rodata label now uses `g_flat_node_id++` (globally unique)
   instead of `bb_node_id(node)` (per-node, repeats when a node is marshalled >once).
   **pcom.pas M4 now assembles** (was 11 `symbol '.LcallfnNNNN' already defined` errors).
3. **`emit_core.h`** — `BB_PATCH_MAX` raised **512 → 65536**. This was the root cause of the
   long-standing **M3 listing-output divergence** (the `charA N≥64` drop, and pcom/pint emitting
   nothing in `--run`).

## Gate state at handoff (all green / no regression)

| Gate | Result |
|---|---|
| Pascal M3 `--run` | **122 / 0** (XFAIL=1 recursion.pas) |
| Pascal M4 `--compile`+as+link+run | **122 / 0** SKIP=0 (XFAIL=1) |
| SNOBOL4 M4 crosscheck | **166 / 87** SKIP=8 — byte-identical to prior baseline, same fail list |
| Icon mode-3 (4 inline probes) | correct (5 / abcd / big / 1 2 3) |
| Prolog mode-3 (hello) | correct (Hello, World!) |
| template-medium-invisible `--strict` | 0 violations |
| `git status` | only the 3 intended files modified, nothing stray |

NOTE on the obsolete M2 gate: a concurrent **DE-INTERP** push (`6e87566`) deleted `--interp`
(mode 2) from the driver. The GOAL-PASCAL-BB M2 gate scripts are now obsolete; **the Pascal gate
is M3 / M4 only**. The Icon and Prolog *crosscheck scripts* (`test_crosscheck_icon.sh`,
`test_crosscheck_prolog.sh`) still diff against `--interp` and therefore report spurious failures
— this is a stale-harness artifact of DE-INTERP, NOT a regression. Verify those two languages via
direct `--run` output instead until the crosscheck scripts are de-interp'd.

---

## Fix #1 — IR_ASSIGN gvar-assign guard (emit_core.c)

**Symptom:** `arr2dtype.pas`, `boolfn.pas`, `case2.pas` printed `; [walk_bb_node: kind=5 unhandled]`
(kind 5 = IR_ASSIGN) and dropped the assignment. All three do `globalvar := userfunc(...)`.

**Cause:** commit `2fa5086` made `resolve_call_kinds_gvar` re-stamp registered user-proc calls
`IR_CALL → IR_CALL_GVAR_USERPROC`. The `IR_ASSIGN` arm of `walk_bb_node` (emit_core.c ~l.395)
gated the `bb_gvar_assign()` template on bare `op_a->op == IR_CALL` only, so the stamped node fell
through to the `kind=%d unhandled` line.

**Fix:** add `|| ir_is_call_kind(op_a->op)` to that guard. `bb_gvar_assign` already normalizes via
`ir_norm_call_kind` (reads `op_a_node_kind`, set at emit_core.c l.334), so once admitted the stamped
node is correctly treated as IR_CALL. This mirrors the guard `emit_bb.c` `codegen_gvar_flat_chain_body`
(l.2975) already uses. Pure dispatch logic — no template/x86/binary change.

## Fix #2 — unique .Lcallfn label (bb_call.cpp)

**Symptom:** `scrip --compile pcom.pas` → `as` rejected with 11× `Error: symbol '.LcallfnNNNN'
is already defined`.

**Cause:** `marshal_single_call` named its rodata fn-name string `.Lcallfn<bb_node_id(lf)>`.
`bb_node_id` is deterministic per node, but a single nested call node (e.g. `arr_get(...)` used as
an argument inside an expression) is marshalled more than once in one statement chain → the same id
→ duplicate symbol.

**Fix:** use `g_flat_node_id++` for the label id (the label is a local rodata string with no external
cross-reference; it only needs to be unique, not node-stable). Exactly mirrors sibling labels
`.Lprocfn%d` (l.382) and `.Lbynamefn%d` (l.439). Only the `MEDIUM_TEXT` path emits this label; the
M3 binary path (`x86_load_ro` with raw ptr) is untouched. The `lblid` parameter is now unused but
left in place to avoid churning the declaration + 3 call sites; build is warning-clean (no
`-Wunused-parameter`).

## Fix #3 — BB_PATCH_MAX 512 → 65536 (emit_core.h) — THE M3 listing-output divergence

This is the big one. It resolves the open item #1 from
`HANDOFF-2026-06-14-PASCAL-BB-FRAME-ARENA-OVERFLOW-FIX.md` (the `charA N=64` M3 drop, and pcom/pint
producing no `--run` output).

**The handoff's description of #1 was stale** — it predated the frame-arena fix. After that fix,
the failing call *does* reach the sized-frame dispatcher correctly. The actual remaining chain:

1. `charA` canary has a hard threshold: **N=63 OK, N=64 DROP** (`[S][A]` instead of `[S][A][B][E]`).
2. Trace showed `ctypes` reaching `rt_call_named_proc_sl` is registered with correct
   `frame_bytes=9232`, BUT `rt_call_named_proc_sl` returns FAILDESCR at its very first guard
   `if (!p || !p->fn)` — i.e. **`ctypes.fn == NULL`** despite being registered.
3. `fn` is NULL because in the M3 driver loop (scrip.c ~l.2737-2740), `pfn = gvar_flat_chain_build_at(...)`
   returned NULL and `rt_proc_set_fn` is gated on `if (pfn)`. The proc was already `rt_proc_register`'d
   and `rt_proc_set_frame_bytes`'d, so it ends up registered-but-fnless.
4. `gvar_flat_chain_build_at` returns NULL because `bb_emit_overflow=1`. The specific trigger
   (confirmed by instrumented trace) is **`bb_patch_count >= BB_PATCH_MAX` — the binary emitter's
   forward-reference relocation table, capped at 512 — overflowing.** NOT the 256KB byte buffer
   (ctypes is only ~29KB of code).

**Why M4 worked but M3 didn't:** M4 emits *text* asm and the assembler resolves labels (no patch
table). M3 wires *binary* in-process with this fixed-size patch table.

**Why the cap is reached:** `bb_label_define` (emit_core.c l.203-226) back-patches and *removes*
entries when a label is defined, so `bb_patch_count` is the count of **simultaneously-pending**
forward refs. In a long linear statement chain the per-statement `jmp γ` / `jmp ω` targets resolve
only at proc end, so pending patches grow ~linearly with proc length. ~8 dangling/stmt × 64 ≈ 512.

**Measured peaks (with cap temporarily raised to instrument):**
- pcom worst proc (chartypes-like): **527**  ← just over old 512, why pcom dropped
- pint worst proc: **587**  ← also over 512
- rest of Pascal corpus: trivial (<60)

**Fix:** `BB_PATCH_MAX 512 → 65536`. Principled bound: pending rel32 patches cannot exceed the
rel32-jump count that fits in `FLAT_BUF_MAX` (256KB / ~5B ≈ 52K), so 65536 can never be the limiter
before the byte buffer. `bb_patch_t` is 24 B → 65536 entries = ~1.5MB BSS (negligible).
Drained per-proc, so it only ever holds one proc's peak. Comment block added at the #define
explaining all of this.

**Result:** charA N=64 now `[S][A][B][E]` in BOTH M3 and M4. Larger N works until the *next*
(separate) frontier — see below.

---

## NEXT FRONTIER (the new open #1) — `bb_gvar_assign call-result: op_a_slot==-1` BOMB

With the patch-table fixed, pcom/pint and large synthetic procs now *build* in M3 but hit a
**different, clean BOMB** at runtime:

```
libscrip_rt: BOMB — bb_gvar_assign call-result: op_a_slot==-1 (call result slot not promoted)
```

- Reproduces with the `charA`-style generator at **N≈90** (90 `array[char]` assigns), and with
  **pcom.pas `--run`** on any input.
- It is a clean abort (BOMB), not silent corruption — diagnosable.
- It is the `bb_gvar_assign` IR_CALL arm finding the call-result slot was never promoted
  (`op_a_slot == -1`). i.e. somewhere a `gvar := <call>` is reached where the call node's result
  slot wasn't allocated/registered before the assign template runs.
- **NEXT STEP:** in `bb_gvar_assign.cpp` (IR_CALL arm) and the gvar flat-chain pre-walk that should
  promote call-result slots, find why the producer-box slot for the call isn't registered at the
  point the assign consumes it. Likely a missing `bb_slot_alloc16`/`bb_slot_register` on the call
  node in one of the flat-chain walk paths for deeply-nested or high-count procs. Compare the
  working path (small N) vs the bombing path (large N / pcom) — the slotmap has `BB_SLOTMAP_MAX 512`
  (emit_bb.c l.66) and `BB_VARSLOT_MAX 256` (l.111); **check whether the slotmap is silently
  overflowing for large procs** (bb_slot_register no-ops past BB_SLOTMAP_MAX → bb_slot_get returns
  -1 → exactly this bomb). If so, this is the same *class* of fix as #3: a 512 static cap that
  doesn't scale to self-hosting-sized procs. STRONG LEAD — check BB_SLOTMAP_MAX first.

## Build / gate quickrefs

```
# build
cd SCRIP && make -j4 scrip && make libscrip_rt

# Pascal M3 gate (loop over corpus/programs/pascal/*.pas, skip pcom/pint/ppp, recursion=XFAIL)
#   compare `scrip --run f.pas` vs f.ref
# Pascal M4 gate
#   scrip --compile f.pas > p.s ; gcc -c p.s ; gcc -no-pie p.o -Lout -lscrip_rt -lgc -lm ; run vs f.ref
# (gate scripts were kept in /tmp this session; reconstruct or pull from corpus Makefile)

# cross-language (REQUIRED before committing shared emit_core.*/emit_bb.*/bb_*.cpp/headers):
bash scripts/test_crosscheck_snobol4.sh      # expect 166/87 SKIP=8
bash scripts/test_gate_template_medium_invisible.sh --strict   # expect 0 violations
# Icon/Prolog: verify via direct --run (crosscheck scripts are stale on --interp)
```

## Canary

`charA N=64` (nested proc `ctypes` doing 64 `chartp['x']:=letter` inside `outer`, `outer` called
from main with `[S]/[A]/[B]/[E]` markers): must print `[S][A][B][E]` in BOTH M3 and M4.
N=63 was the old patch-table boundary.
