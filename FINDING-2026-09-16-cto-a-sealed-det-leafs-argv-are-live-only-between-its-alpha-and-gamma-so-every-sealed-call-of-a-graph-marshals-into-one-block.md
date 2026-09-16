# FINDING 2026-09-16 (cto, MODE DECTET, the SPINE) — a sealed det leaf's argv are live only between its alpha and its gamma, so every sealed call of a graph marshals into ONE block, and its result goes through the ordinary reader rule

Row: `frame-slot-reuse-a-live-range-in-a-byrd-graph-extends-to-every-point-reachable-by-recession` (CEO-684 slice 2), RUNG 2 = THE DET-LEAF ARGV NON-GRANT, landed at SCRIP bbd5c370a. Predecessors: rung 0 (a9461875f, the relation), rung 1 (d21da7354, the straight-temp pool), the two openers (09c0e5608 the census, 888f9a767 the dump IS the frame), the dead-record cure (5538c5a5e), rung 2 step 1 (ffebafe8e, the seal travels on the IR node).

## THE CLAIM, AND WHERE IT IS HELD

A call the lowerer sealed as a det leaf (`IR_SEAL_CALL_DET_LEAF`: the emitter's registry `dop_direct_fp` knows the callee) is emitted by `bb_call_fn.cpp`: the argv are marshalled on alpha (straight copies of producer slots, literals, or `NV_GET_fn` for a global — no box of this activation runs between the marshal and the call), one C function is called, it returns once, `beta` falls to `omega`. So the argv of a sealed call are live on the interval [alpha, gamma] of that call and nowhere else, and no two sealed calls of one activation are inside that interval at the same time. Therefore every sealed call of a graph can marshal into ONE argv block of 16 × (the widest sealed arity) bytes, granted once per graph. The block is a `call.argv (pooled: …)` field on the root scope, so the census (`util_frame_field_reference_census.py`, lea-covered argv blocks) and the dump-is-frame instrument (`util_frame_refs_land_in_grants.py`) both see it as a grant. The runtime zeroes the whole region as descriptors at activation entry and the collector scans it as descriptors, so a stale descriptor left in the block after gamma is traced like any pooled result slot — harmless.

The templates take the argv base from a new lookup, `zls_argv_off(nd)`, whose default is `result + 16` — byte-identical emission for every unsealed call. `bb_call_fn.cpp`, `bb_call.cpp` (by-name and by-name-gen) all read it; the layout entry carries the block base (`aoff`) for a sealed call and −1 otherwise. No new field on `IR_t`, no new global.

The sealed call's RESULT now goes through the ordinary reader rule of rung 0/1 (`zls_reuse_plan` no longer classes it `ZR_DETLEAF`): readers on the gamma spine, a beta-capable box between the write and the last read pins it (GUARD), a back-edge span pins it (LOOP), an unverified reader's template pins it (READER); a result nothing reads (every `$unify`, `$is_v`, `$cmp_*`) aliases the graph's shared dead-result scratch. The claim is printed on every sealed call's reuse line: `det leaf <name>: no beta, argv dead at gamma, argv@+N pooled` (or `no argv` for a zero-arity callee).

## MEASURED (honest dump = the emitted frame, test_gate_dump_zeta_is_the_emitted_frame.sh green)

| | rung-1 tree (head 59971a9d2) | rung 2 |
|---|---|---|
| r/1 of `scripts/fixtures/frame_r1_witness.pl` | 480 B, 28 slots | **304 B, 17 slots** (bar ≤ 320; row DONE-WHEN < 200 still needs rung 3) |
| r/1 sealed calls | 5, each with 2 own argv slots (160 B) | 5 marshalling into one 2-slot block (32 B) |
| r/1 sealed results | 5 own slots (80 B) | 4 elided to the dead-result scratch, 1 (`$ax_sub`, read by `$is_v`) pooled |
| Prolog prelude, 161 graphs | 45344 B, 2413 slots | **30496 B, 1485 slots** (14848 B returned, 33 %) |
| sealed calls with pooled argv / no argv | — | 481 / 5 (zero-arity: `$nl`, `$told`, `$seen`, `$flush_output`, `$at_end_of_stream`) |
| argv block slots granted over the prelude | — | 340 |
| Icon, SNOBOL4, Snocone emission (`--compile` diff vs head) | — | byte-identical |

Witnesses, both modes: Prolog `ok`; Icon `every write(image(1), 1 to 3)` → `11 12 13` (ref cut from icont/iconx), the builtin call read across the generator reads PINNED self (IR_CALL_ICON is never sealed; nothing in an unsealed graph grew an argv block); SNOBOL4 `ab`.

## GATE

`scripts/test_gate_frame_reuse_rung2_det_leaf_argv_share_one_pool.sh` (~2 s, wired blocking, adopted WIRED 365): r/1 ≤ 320 on the honest dump; the pooled block exists; all five sealed calls of r/1 print `argv@+N pooled` and none `own`; no per-call `call.argv IR_CALL` field survives in r/1; the Icon builtin call is PINNED and no argv block appears in the Icon dump; three witnesses print their refs in both modes. RED-BEFORE on the rung-1 tree: r/1 480, no block, rc=1. The step-1 instrument (`util_frame_det_leaf_bit_vs_registry.py`) reads the claim text instead of the retired `PINNED det leaf` class: 161/161 graphs agree, 486 sealed == 486 direct boxes.

## FOUND BESIDE THE ROW (the cfo's FYI, answered by measurement)

hq_snocone's 09-04 cell collapsed (fib_recur 1.95x → 0.285x, arith_loop 2.11x → 0.582x). On hq_snocone's own instrument (`bench_triangulate_snocone.sh`, callgrind Ir m4 vs the clean SPITBOL oracle) BASE 2f2b84d38 (before rung 0), HEAD 59971a9d2 and HEAD+rung 2 read identically: fib_recur 0.281x, arith_loop 0.571x, string_concat 1.30x, and the kernels' m4 emission is byte-identical across the three. The collapse predates the frame rungs; the window is 2026-09-04 .. 2f2b84d38 and it is hq_snocone's row.

## NEXT (rung 3)

The `< 200` of the row's DONE-WHEN: the staged calls' argv (+144, +208: `bb_call_proc_staged` marshals over rsp; a runtime witness must prove no beta path reads the frame argv before the grant stops), the two `callgen.act` quads, the resume quad, and whether the pooled-result pool (4 slots) can overlay the argv block (it cannot in general: a pooled temp is live across the marshal that reads it).
