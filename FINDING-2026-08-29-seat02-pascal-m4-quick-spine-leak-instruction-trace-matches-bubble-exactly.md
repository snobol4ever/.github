# FINDING — `quick`'s spine over-release fully instruction-traced: same two-site shape as `bubble`, one site numerically identical across both kernels

Row: `pascal-m4-for-spine-leak-64b-per-iter` (seat02, FLEET-16 per live MODE at claim time).

## Baseline re-confirmed, unchanged from seat12's handoff

Re-pulled all 3 repos (SCRIP HEAD unchanged at `7817f370` — a few commits landed since seat12's
`a3275c6f` baseline, none touching Pascal/emitter-shared code obviously, but per this row's own
repeated lesson re-measured rather than assumed). `setarch -R`, `echo 1 |`, 5 reps/kernel, all 9
kernels: **only `bubble` and `quick` FAIL (rc=139, 5/5 deterministic)**; `intmm`/`queens`/`sieve`/
`perm`/`towers`/`uplevel2`/`uplevel3` all PASS 5/5. Identical to seat12's grid — no further drift.

## `quick`, instruction-traced end to end, mirroring seat12's `bubble` methodology exactly

**Crash site:** `n236_var_bx+14` (`mov [rsp+928],rax`, i.e. `0x3a0(%rsp)`), same as seat12 reported.
Breakpointed `n236_var_bx` for a full run under `setarch -R`: **101 hits, `$rsp` climbing a constant
`+0x2b0` (688 bytes) every visit, zero variance**, crash on the 101st write. Matches seat12's report
exactly (they did not instruction-trace this kernel; this session did).

**Which edge is hot:** `n236_var_α` has 4 static predecessors — two in `n229_call_bx` (`al==0x68` arm
and its `n229_call_β` twin, each releasing `0x10+0x250`=608) and two in `n231_binop_test_bx` (the
`jg`-not-taken arm and the post-`rt_jct_relop` `jne`-not-taken arm, each releasing `0x10+0x270`=640 —
**a 32-byte local mismatch between the two release constants, same shape as `bubble`'s 656-vs-624
pair**). Breakpointing all 4 for a full run: **only `n231_binop_test_bx`'s first exit (the
`jg`-not-taken arm, `cmp rax,rcx` at `0x4040ec`) ever fires — 101/101.** The other 3 are dead code
for this input.

**Full-cycle `nexti` trace** (breakpoint on the hot exit, `nexti`-stepped — not `stepi`: a first attempt
with `stepi` ran into a runtime by-name dispatcher inside `rt_call_arr_bl` and blew a 4000-instruction
budget without returning, confirming this row's own standing note that Greek-symbol-adjacent
instrumentation needs care — switching to `nexti`, which steps over calls, closed one full cycle in
**464 steps**, net `$rsp` delta **+688**, matching the per-visit measurement independently) — and
localizing to **two sites, not one**:

1. **`n248_assign_bx`'s back-edge** (`add rsp,0x220`=544 @ `0x404778`, `jmp n201_var_bx` @ `0x40477f`)
   — confirmed as the `for`-loop back-edge structurally, not just by "jumps backward": `n248_assign_bx`
   writes `[r9+0x30]`/`[r9+0x38]` and `n201_var_bx` immediately reads the *same* offsets — the loop
   variable's own store/reload pair. Only **3 preceding nodes self-carve `sub rsp,16` (48 bytes)**
   since the previous release — **+496 excess**.
2. **`n231_binop_test_bx`'s hot exit** (`add rsp,0x10` then `add rsp,0x270`=624, combined 640 @
   `0x4040f1`/`0x4040f5`, same node whose own entry self-carves `sub rsp,0x10` — the local pop/carve
   pair is self-contained and cancels out of the excess calculation either way it's counted). **27
   other preceding nodes self-carve 16 bytes each (432 bytes)** since the previous release — combined
   with the node's own paired 16, **excess = 640 − 448 = 192** (equivalently, 624 vs the 432 owed by
   the *other* 27 nodes — same answer).

`496 + 192 = 688`, exactly matching the measured per-visit drift — closed, not a partial match,
identical to `bubble`'s own `224 + 496 = 720` closure.

## The cross-kernel correspondence is exact, not merely similar-shaped

- **Site 1 (`assign`-node for-loop back-edge) is numerically IDENTICAL across both kernels**: 3
  preceding nodes, 48 bytes carved, release constant 544, excess 496 — `bubble`'s `n70_assign_bx` and
  `quick`'s `n248_assign_bx` both hit this exact triple. This is not "the same class of bug," it is
  the same computed constant (544) coming out of `zd_plan` for a for-loop back-edge in two independently
  compiled programs.
- **Site 2 is the same node *type* (`binop_test`) in both kernels** (`bubble`'s `n53_binop_test_bx`,
  `quick`'s `n231_binop_test_bx`), with the same shape (~27 unrelated preceding self-carries, ~432
  bytes) but a kernel-specific release constant (672 vs 640) and correspondingly different excess (224
  vs 192) — consistent with `zd_plan` computing this release from each kernel's own accumulated depth
  at that point, while getting the accounting wrong by a similar, non-identical margin each time.

This is strong, direct corroboration of seat12's classification: one mechanism in `zd_plan`'s
release-side (`gback`/`oback`/`gpop`/`wpop`) accounting, reachable through (at least) two BB family
members — `assign` back-edges and `binop_test` exits — not two coincidentally similar bugs.

## Not attempting a fix, same standing authorization boundary as seat12's entry

Both sites are release-constant-vs-actual-carve mismatches computed by `zd_plan`'s depth/wall
machinery (`emit.cpp`), the reserved-for-hq_C surface per this row's standing authorization split
(SOLO: count + a single local carve/release pairing fix; BACK TO hq_C: anything touching `zd_plan`'s
arming/depth/wall computation). Two sites of two different node types, each internally consistent but
not answerable by a single local carve/release edit, is exactly the shape the authorization reserves.
Sent to hq_C. Tree byte-identical to origin throughout — only `/tmp` scratch artifacts and gdb/objdump
were used; no tracked file was touched.

## What the next actor gets for free

- `quick` is now instruction-traced to the same completeness as `bubble` — both kernels' full
  mechanism, exact sites, exact bytes, are now on record for whoever hq_C authorizes to fix
  `zd_plan`'s depth/wall computation.
- The site-1 constant (544, 3 nodes, 48 carved, 496 excess) recurring byte-for-byte across two
  independently-compiled kernels is a strong, cheap-to-check signature: if a future kernel in this
  family fails with `$rsp` climbing in increments containing a `+496` component from an `assign`-node
  back-edge, this is very likely the same `for`-loop back-edge accounting defect, not a new mechanism.
- The `nexti`-not-`stepi` lesson (recorded above) generalizes to any future instruction-level trace of
  this shared runtime — a call into `by_name_dispatch.c`-style builtin dispatch is expensive to
  single-step into and irrelevant to spine accounting.
