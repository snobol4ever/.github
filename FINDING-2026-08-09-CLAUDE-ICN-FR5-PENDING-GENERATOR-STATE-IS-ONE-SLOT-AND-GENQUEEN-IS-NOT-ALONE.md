# FINDING 2026-08-09 — ICN FR-5: pending-generator state is ONE SLOT; two simultaneously-pending generators clobber each other. genqueen is not alone.

**Session:** Sonnet s16 (concurrent set). **SCRIP HEAD at open:** `2d2c2cf5` (watermark re-derived 246/17/30, matches s15 cursor exactly). **This session's prior commit:** `64fe9c18` (lexcmp, 247/16/30).

## THE CLAIM

The FR-4 (s8) fix moved all generator resume state that must survive a yield into **four one-slot process globals** (`src/runtime/rt/rt.c:1408-1411`): `g_gen_pending_cont`, `g_gen_pending_caller_rbp`, `g_gen_pending_gamma_wire`, `g_gen_pending_omega_wire`. One slot is correct for exactly one pending generator. The moment TWO generators are pending simultaneously — nested (`suspend h()` inside a generator) or siblings in one bounded expression (`g() & h()` under `every`) — the second generator's prologue/suspend overwrites the first's state, and the first's β-resume or γ/ω epilogue jumps through the wrong frame. Symptom is a silent infinite loop (or lost exit), never a crash.

## MINIMAL REPROS (all ≤7 lines; rc=124 is `timeout 8s`)

| probe | shape | result |
|---|---|---|
| pd | `every write(g()); every write(h())` — sequential, never simultaneous | **GREEN** `1 2 10 20 done` |
| pb3 | `every write(g() & h())` — siblings pending | `10 20` then **HANG** (dies resuming g for its 2nd value after h's state overwrote the slot) |
| pb4 | `procedure p(); suspend h(); end` + `every write(p())` — nested pending | **HANG, zero output** (p's γ epilogue reads caller_rbp last written by h's prologue = p's own rbp; yields to itself) |
| pb1/pb2 | `suspend g() & 10` / `suspend 1 & h()` | HANG, zero output |
| pa | `(x <- 2) & (x = 3)` reversible-assign restore | **GREEN** — `<-` is innocent |

`rung36_jcon_genqueen` (cursor: "0L: produces nothing") is in fact **rc=124 zero-output hang** = pb4's shape (`suspend placequeen(c) & solvequeen(c+1)`). One-deep suspension (`gen.icn`, `suspend 1; suspend 2`) has been green since s13 because one pending generator fits one slot — which is why the suite never saw this until the multi-generator jcon programs.

## THE HALF-WIRED PER-ACTIVATION STORE (the tell)

`rt.c:1412`: `c_rt_gen_save_caller_rbp` **already dual-writes** the value into per-activation storage — `g_pcall[g_pcall_top-1].rname` — exactly as s8's own Layer-3 "Recommended option B" specified. But `rt.c:1413` `c_rt_gen_get_caller_rbp` returns the GLOBAL. The per-activation half was built and then not read. `c_rt_gen_get_fb` (rt.c:1393) DOES read per-activation (`g_pcall[top-1].fb`) — but `top-1` is only the right index for the INNERMOST pending generator; an outer generator's resume needs its own record, not the top.

## FIX DIRECTION (not implemented this session — this is a template-ABI rung, not a runtime patch)

Key every pending value by the generator's OWN activation. The caller's β arm already holds the callee's `generator_rbp` in its own frame slot `FRQ(act+8)` (written at the L(3) landing, s8 notes). Two shapes:
- (a) pass `generator_rbp` as an argument to `rt_gen_get_{cont,caller_rbp,gamma_wire,omega_wire}` and store the four values in the pcall record (fields: `rname` already carries caller_rbp; cont/wires need slots or a parallel array keyed by fb). Getter finds the record by `.fb == arg` (LIFO scan from top is O(depth)).
- (b) full parallel pending-stack pushed at prologue / popped at ω, indexed the same way.
Either way the template call sites change arity → BOTH-MEDIUM edits in `bb_suspend.cpp` / `bcps_spine_gen_arm` / `xa_flat` epilogues + the `rtx_icngen.S` veneers + `.s` regen. Budget a full session; the s141 ABI law (append-only struct growth) applies to the pcall record.

## BLAST RADIUS

**Measured this disease:** genqueen (pb4 shape), and the pb-family probes. **Predicted, untested:** `rung36_jcon_recogn` (recursive suspend = nesting depth n), `rung36_jcon_cxprimes` (sieve chains generators; co-expr pthreads may ALSO race these process globals — separate hazard, noted not proven). **Explicitly NOT claimed:** `level` (s11 recorded a distinct rsp-drift-per-β mechanism), `prepro`, `proc_lookup` (DC-stub double-execute, s15 note) — test each against pd/pb probes before billing them to this defect.

## ALSO THIS SESSION (already committed, SCRIP `64fe9c18`)

lexcmp cured (+1, 247/16/30): rtx_icnrel.S carried pre-s229 tags DT_S=1/DT_I=6 (live 0x02/0x03) → `rt_str_coerce`'s asm identity arm returned csets unconverted. Fixed tags, added cset exclusion to the string arm the fix armed, made the by-name relop path return `rt_str_coerce(rhs)` for SLT..SNE per `ocomp.r` StrComp. Killswitch-identical; R-ICN-D roman output md5 `e02da06b49f64c44168830cff34bba94` with/without zframe (matches s15's recorded value). Instrument note: bare `--compile | md5sum` oscillates with ASLR (S231 disease); `setarch -R` pins it — pre==post `c748c9e1…`. Still stale elsewhere: rtx_icnagg/icnsub.S DT_DATA=100 (live 0x70).
