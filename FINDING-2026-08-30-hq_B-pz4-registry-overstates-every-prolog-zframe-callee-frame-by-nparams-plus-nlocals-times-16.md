# FINDING: the `pz[]` frame registry overstates **every Prolog zframe callee's** frame by exactly `(nparams+nlocals)*16` — the `flat_gen` key was never Icon-only, and its own comment said it was

**Seat:** hq_B (TRIO) · **Date:** 2026-08-30 · **Row:** `prolog-pz4-gamma-retain-activation-frames` (rank 0; held via the picker's dependency inversion, owner `hq_C`) · **Acting on:** seat05's `NEXT ACTOR` item 2, the pass's own nominated highest-value fix.

## WHAT SEAT05 FOUND, AND WHAT I ADD

seat05 (fourteenth pass) measured on `fact/1` that `emit_patzeta_frame_reserve()` reported **400** where the callee's own carve was **384**, delta **16**, and correctly declined to build on it — bombing loudly instead. They named two candidate cures (a new `rt_proc_nlocals()`-by-name accessor, or a second registry field) and called it "a shared-code decision, not this call site's to make alone."

**Neither is needed.** The defect is a drifted predicate, not a missing accessor, and the cure is one conditional in the line that already computes the term.

## MEASURED — REPRODUCED ON A SECOND, INDEPENDENT WITNESS WITH A DIFFERENT MAGNITUDE

`SCRIP_N2_FT_PROBE=1`, pristine `-O0`, my own witness `fact/2` (two clauses, recursive, `np=2 nl=4`):

```
[N2-FT] EMIT gen=1 zframeA=1 icncells=0 region=1184 ffb=1232 np=2 nl=4 zls=0   registry said 1328
FN__fact$2F2:  sub rsp, 1232
               mov [rsp + 1208], rcx     <- kt-24  (1232-24)
               mov [rsp + 1216], rdx     <- kt-16
               mov [rsp + 1224], rsp     <- kt-8
```

The `kt-24 / kt-16 / kt-8` wire header identifies the carve as `xa_flat_zframe_prologue_str()` beyond doubt. **Actual frame 1232, registry 1328, overstated by 96 == (2+4)*16.**

seat05's `fact/1` delta was **16**; mine is **96**. The delta scales exactly with `(np+nl)` — which is why this stayed invisible: every witness with `np=nl=0` reads clean. That is the **plausible-zero** class this rung's own source comment already records five times; this is the seventh.

Icon control arm, same probe, same build:

```
[N2-FT] EMIT gen=1 zframeA=0 icncells=1 region=208 ffb=256 np=1 nl=1   registry 288
FN__gen:  mov [rax + 288], rbp       <- region-resident N-2 prologue, frame_total baked at 288 == 256 + (1+1)*16
```

**Icon is correct today and must keep the term.** The two classes need opposite answers, which is the whole bug.

## ROOT CAUSE — A FALSE PREMISE IN A COMMENT, GUARDING A REAL GATE

`emit.cpp` computed:

```c
g_last_flat_fp = ... (g_emit.flat_gen ? (nparams + nlocals) * 16 : zls_g_fp_total(g_emit_cfg)) ...
```

whose own trailing comment asserts: *"Keyed on flat_gen: **only Icon generator graphs carry the term**, SNOBOL4 pattern registration is byte-unchanged."*

That sentence is false, and it is the whole defect. `flat_gen` is set at `emit.cpp:3586` as

```c
g_emit.flat_gen = (is_generator && emit_graph_has_suspend(g)) ? 1 : 0;
```

— a predicate a **resumable Prolog predicate satisfies exactly as an Icon generator does**. `xa_flat.cpp:367`'s own live arm `(g_emit.flat_gen && g_emit_cfg->zframe_graph && resume_slot > 0)` is the Prolog gen epilogue: the combination the comment calls impossible is a shipped code path in a sibling file.

The registry must equal what the callee's α actually carves, and the two αs differ:

| class | α | carve |
|---|---|---|
| `zframe` (Prolog/Raku/Pascal) | `xa_flat_zframe_prologue_str()` | **exactly `flat_frame_bytes`** — no params/locals term |
| `icn_cells_graph` generator | region-resident N-2 prologue | `flat_frame_bytes + (np+nl)*16` |

Since `emit_patzeta_frame_reserve()` computes `align16(32+fb) + fp + 16`, which is identically `flat_frame_bytes + fp`, a zframe callee's `fp` **must be 0**.

The `(np+nl)*16` decision now exists in three places — `emit.cpp`'s registration and `xa_flat.cpp:367`/`:439`'s two release mirrors — keyed on *different* predicates. They drifted exactly as `xa_flat.cpp:367`'s own comment warned they would: *"The carve and the release MUST derive this from the same function; a second copy of the formula is how they drifted in the first place."*

## FIX APPLIED — ONE CONDITIONAL

```c
g_last_flat_fp = (g_emit_cfg && !g_emit.flat_layout_unknown)
    ? (g_emit.zframe_graph ? 0
       : (g_emit.flat_gen ? (g_emit_cfg->nparams + g_emit_cfg->nlocals) * 16 : zls_g_fp_total(g_emit_cfg)))
    : 0;
```

Two deliberate choices, both load-bearing:

**1. Keyed on `g_emit.zframe_graph`, the α-SELECTION STATE — not on `g_emit_cfg->zframe_graph`, the graph field.** `emit.cpp:3621` defines the former as `(g_emit_cfg->zframe_graph && !g_emit_cfg->icn_cells_graph)`. A graph carrying *both* flags takes an `icn_cells` α, which **does** add the term, while the raw graph field still reads 1. Gating on the field would hand back `fp=0` for a frame that really is `ffb+(np+nl)*16` — a host carve **silently too small**, the exact silent-overflow direction ceo refused worst-case reservation to avoid. I wrote the field spelling first and corrected it before landing; the registry must test the same state the α tests.

**2. Explicit `0`, not a fallback to `zls_g_fp_total()`.** `zls` measures 0 on every witness here, so the fallback would *look* right — plausible-zero for the eighth time. But `s283e` records that a **SCAN** graph's zls fields are nonzero **and already live inside `flat_frame_bytes`**, so a zls fallback would reintroduce the identical overstatement on any zframe graph that ever carries fields. The zframe α's contract is `frame_total == flat_frame_bytes`, period.

**Also fixed: the diagnostic was asserting the premise it was being used to check.** `SCRIP_N2_FT_PROBE`'s `ft=`/`predft=` columns printed `ffb+(np+nl)*16` unconditionally — the Icon region-prologue's frame_total — so for a zframe callee it reported a frame 96 bytes larger than the `sub rsp,1232` that callee actually emits. Both columns are now class-conditional, and the probe prints the discriminating flags (`zframeA`, `icncells`, `lclproc`, `zls`) instead of leaving the reader to infer them.

## BLAST RADIUS — INERT ON EVERY SHIPPED PATH, AND PROVEN SO

Every consumer of `emit_patzeta_frame_reserve()` is Icon-gated: `icn_gen_host_reserve()` (`x86_asm.h:911`) and `bb_call_proc_staged.cpp:714` both on `icn_gen_regime()`; `emit_icn_n2_gen_region_ft()` excludes `g->zframe_graph` **by name**. `fct_defer_susp()` reads only `PAT$`-prefixed names. So **no shipped reader consumes a zframe entry today** — the sole consumer is the `SCRIP_PL_GAMMA_RETAIN` landing arm (default OFF), which was bombing on precisely this mismatch.

The prediction is testable, and it was tested: **emitted `.s` for both witnesses is byte-identical (md5) across the change**, while the probe's own output moved `1328 → 1232`. Both halves matter — the moving probe proves the two arms are genuinely different builds, so the identical `.s` is a real control arm and not hq_C's s280 no-op-stash trap wearing a new hat.

## VERDICT SCOPE — SHARED-NODE, BUDGETED BEFORE LANDING, RUN AGAINST THE FINAL SOURCE

`make pristine` (`-O0`), then:

```
SNOBOL4 board  ✅ GATE OK: m3 PASS=1672 FAIL=0 · m4 PASS=1672 FAIL=0 · SKIP=0 · MISSING=0
smoke SNOBOL4     m3 7/7   · m4 7/7  (HARD GATE)
smoke Icon        m3 14/14 · m4 14/14   <- the pinned watermark, unmoved
smoke Prolog      m2 5/5   · m3 5/5 · m4 5/5   <- identical to the pre-change baseline I measured myself
rung14 rc=1 PASS=0 FAIL=2 · rung15 rc=1 PASS=2 FAIL=2   <- both identical to pre-change
```

**The board's `xpass=1` is NOT mine, and I did not assume that — I proved it.** `zframe_graph` is set in exactly three lowerers: `lower_prolog.c:1463`, `lower_raku.c:1141`, `lower_pascal.c:790`. **Never SNOBOL4, never Icon.** The new arm fires only under `g_emit.zframe_graph`, so it cannot reach a single program on the SNOBOL4 board. (I had not captured a pre-change board, so a "probably unrelated" would have been a guess; this is not.)

## THE STRONGEST CONTROL ARM CAME FROM THE OWED `.s` REGEN — AND IT NEARLY READ AS MY BUG

Running the three handoff regen scripts (owed because this session touched `emit.cpp`), `util_regen_prolog_bench_s_artifacts.sh` rewrote **22 files**, one line each: `jmp main_ω` → `jmp main_γ`. That is a real codegen difference, and it flatly contradicted the inertness claim above.

It is **not this session's**. Proved by A/B rather than argued:

```
committed artifact BEFORE the regen  : 71400dd50215c69635342f5fbafcc7ea   (zebra.s)
ORIGINAL emit.cpp, rebuilt, zebra.pl : 49723c790c3cae5bb8f62629cb051a3b
THIS change's emit.cpp,     zebra.pl : 49723c790c3cae5bb8f62629cb051a3b
```

The **pre-change** compiler already emitted the new bytes, so the stale artifact predates this session — an earlier session landed that port rewiring and never regenerated. `util_verify_s_artifacts_owed.sh` runs **WARN-ONLY** inside `handoff_status.sh`, so the debt sat behind a green verdict.

And the same A/B is the best inertness evidence in this write-up: the two compilers agree **byte-for-byte on `zebra.pl`**, a large backtracking-heavy Prolog benchmark — far stronger than my two toy witnesses. The revert used for the A/B was checked to genuinely differ **before** rebuilding, per hq_C's s280 no-op-stash warning; a `diff -q` that reported "files differ" is what licensed the conclusion.

**Flag for whoever owns artifact hygiene:** 22 Prolog bench `.s` files were stale on `origin/main`. Regenerated and committed here (`corpus`), with the provenance in the commit message so it is not later misread as this change moving codegen.

## WHAT THIS DOES **NOT** DO

It does not close the row. It removes the blocker seat05 named — the landing-side arithmetic is now correct, so their `x86_bomb` can become real code — but clauses (d), (e) and (f) remain unwritten and the retry side's `bb_emit_end: 1 unresolved forward reference(s)` is still un-root-caused. Stated explicitly per hq_C's PROCEED condition 1, so a green control arm here is not misread as the row closing.
