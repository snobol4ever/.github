# HANDOFF — 2026-05-28 Sonnet — GOAL-RAKU-BB opnames cleanup + M3-RK-NOINTERP-1 deep-dive

## What landed

**one4all (uncommitted edit, ready to push):**
- `src/lower/sm_prog.c:252` — opnames[] slot mislabel `"SM_UNUSED_8"` → `"SM_NAMED_CALL"`.
  One-line rename, no behavior change. This is option (a) from the prior handoff
  (M3-RK-NOINTERP-3 follow-up). Prevents future miscounts when triaging by opname
  in `--dump-sm` output.

**.github (uncommitted edits):**
- `PLAN.md` Raku BB row updated with the deep-dive finding.
- `GOAL-RAKU-BB.md` watermark + MODE3-NO-INTERP rung + mode-3 status block all updated.
- This handoff document.

## Gates (unchanged, all HOLD)

```
GATE-RK   mode-2:                23/33   HOLD
GATE-RK3  --run SCRIP_M3_NATIVE: 17/33 + 2 FAIL + 14 CRASH
GATE-RK4  mode-4:                26/33   (out of scope this session per Lon directive)
Smoke raku:       5/5    HOLD
Smoke prolog:     5/5    HOLD
Smoke snobol4:    13/13  HOLD
Smoke icon:       5/5    HOLD
FACT RULE grep:   0
Build:            clean
```

## What did NOT land — and why

**M3-RK-NOINTERP-1** (closing Cluster 1: 8 of 14 mode-3 crashes) was scoped
as the rung to attempt this session. It did not land. Surface diagnosis from
the prior handoff was that `sm_bb_invoke` `MEDIUM_BINARY` arm at
`src/emitter/SM_templates/sm_bb_switch.cpp:35-36` is a 5-byte no-op stub:

```cpp
+ IF(MEDIUM_BINARY,
  bytes(5, "\xE8\x00\x00\x00\x00"))
```

That diagnosis is correct. But deeper investigation found that fixing this
stub is not a localised one-template change — it is an ABI-level rung.

### The ABI mismatch

The `MEDIUM_TEXT` arm of `sm_bb_invoke` (sm_bb_switch.cpp:37-87) inlines:

1. A `.Lent` data byte for α/β fresh/resume gate.
2. `walk_bb_node_str_c(gen)` — the BB graph rendered as asm text.
3. Post-amble: `γ: rt_set_last_ok(1); ω: rt_set_last_ok(0)`.

The BB graph body, when rendered as text, uses **`rt_push_int@PLT`** to
push yielded values onto the SM rt-vstack (see e.g. `bb_to_by.cpp:89-90`
under MEDIUM_TEXT). Subsequent SM ops (`SM_STORE_VAR`) pop from that same
SM rt-vstack via `rt_nv_set`. Symmetric.

But the BB graph's `MEDIUM_BINARY` arm uses a **completely different ABI**:

```cpp
// bb_to_by.cpp:120-125 MEDIUM_BINARY:
b += bytes(4,"\x41\xC7\x04\x24") + u32le((uint32_t)DT_I);  // mov dword[r12],DT_I
b += bytes(5,"\x41\xC7\x44\x24\x04") + u32le(0);           // mov dword[r12+4],0
b += bytes(5,"\x49\x89\x4C\x24\x08");                       // mov [r12+8],rcx
b += bytes(4,"\x49\x83\xC4\x10");                           // add r12,16
```

**r12** is the value-stack pointer in the **brokered-slab** convention
(used by SNOBOL4 pattern matching via `bb_build_brokered` / `bb_pool`).
This ABI is **incompatible with the SM rt-vstack** that mode-3 native
uses.

The comment at `bb_to_by.cpp:87` admits this:

> "raw r12 here SEGFAULTS in mode-4 (--compile) — r12 is the value-stack
>  only in the MEDIUM_BINARY (brokered) path below; in TEXT it is not
>  set up."

And critically: `XA_FLAT_PROLOGUE` (`xa_flat.cpp:36-45`) initialises
only `r10 = &Δ`, NOT r12. `bb_broker` (`src/processor/bb_broker.c`)
calls `fn(state, esi)` without touching r12. `sm_run_native` doesn't
either.

The generator family of BB templates (BB_TO_BY, BB_UPTO, BB_SUSPEND,
BB_ITERATE, BB_ICN_TO — `grep -l r12 src/emitter/BB_templates/`)
assumes r12 was already initialised by some caller before the slab is
entered. **There is no such caller in mode-3 native.**

### What "fixing the stub" actually requires

Two paths:

**(a) Mode-3 native ABI branch in each generator BB template.**
Add a third arm alongside MEDIUM_TEXT and MEDIUM_BINARY-brokered
(or gate inside the existing MEDIUM_BINARY) that emits the same
sequence as MEDIUM_TEXT but as raw bytes: e.g. for `bb_to_by`:

```cpp
// instead of the r12 writes:
b += bytes(2,"\x48\x89\xCF");                              // mov rdi, rcx
b += bytes(2,"\x48\xB8") + u64le((uintptr_t)rt_push_int);  // movabs rax,&rt_push_int
b += bytes(2,"\xFF\xD0");                                  // call rax
```

The yielded value lands on the SM rt-vstack where STORE_VAR can pop it.
Templates affected: `bb_to_by.cpp`, `bb_upto.cpp`, `bb_iterate.cpp`,
`bb_suspend.cpp`, `bb_seq.cpp`, `bb_icn_to.cpp`.

**(b) Bridge in `sm_bb_invoke` MEDIUM_BINARY.**
Allocate a malloc'd r12 region, set r12 in the SM stream before the
BB graph, drive the BB graph inline (which writes to r12), then after
γ jumps to a glue tail that pops the top descriptor off r12 and calls
`rt_push_int/str` to transfer to the SM rt-vstack. Plus initialise r12
once per program at the entry of `sm_run_native`.

### Recommendation

Take (a). It puts the per-mode ABI choice where the value-emission
actually happens (in the template), keeps `sm_bb_invoke` as a thin
state-byte + γ/ω-wiring layer, and avoids cross-stack copying overhead
per yielded value. Risk is bounded because each template can be done
in isolation.

Suggested split:
- **M3-RK-NOINTERP-1a** — `bb_to_by.cpp` mode-3-ABI arm. Closes
  `rk_range_for`, `rk_for_array`, `rk_for_array_simple`,
  `rk_for_array_underscore`. (Easiest first; integer-yield only.)
- **M3-RK-NOINTERP-1b** — `bb_iterate.cpp` mode-3-ABI arm (array
  CONSUMER for lazy map/grep). Closes `rk_map_grep_sort24`,
  `rk_fileio38` (which is array-iterate over `lines($path)`).
- **M3-RK-NOINTERP-1c** — `bb_suspend.cpp` / `bb_seq.cpp` for
  gather/take. Closes `rk_gather`, possibly `rk_given18`.
- **M3-RK-NOINTERP-1d** — `bb_upto.cpp` / `bb_icn_to.cpp` if any
  Raku test exercises them (none apparent in Cluster 1 today; defer).

Each is a single template change + GATE-RK mode-2 / mode-3 / smoke check.

## Side note: the 17/33 vs 18/33 delta

The prior watermark recorded mode-3 native at 18/33. This session
re-measured at 17/33: `rk_stdio39` flipped from PASS to FAIL. The diff
is a stderr-ordering issue (not a crash, not Cluster 1 territory).
`rt_init`'s `setvbuf(stdout, NULL, _IOLBF, 0)` interacts differently
with the `2>&1`-style capture in the harness depending on whether
`SCRIP_M3_NATIVE=1` was added at the right moment in the runner. Not
investigated here; tagged in the watermark as separate from M3-RK-NOINTERP-1.

The other 17 PASS / 2 FAIL / 14 CRASH structure is unchanged from prior.

## Files to read first next session

```
src/emitter/BB_templates/bb_to_by.cpp        — MEDIUM_TEXT (working) vs MEDIUM_BINARY (r12 ABI)
src/emitter/SM_templates/sm_bb_switch.cpp    — sm_bb_invoke MEDIUM_BINARY stub (line 35-36)
src/emitter/XA_templates/xa_flat.cpp         — XA_FLAT_PROLOGUE does NOT init r12
src/processor/sm_native.c                    — sm_run_native (passes 1, 2, 3)
src/processor/bb_broker.c                    — confirms r12 not init'd by broker
test/raku/rk_range_for.raku                  — simplest Cluster 1 reproducer
```

## Session setup unchanged

Standard GOAL-RAKU-BB Session Setup applies. Side-by-side mode-2 / mode-3
reporter script was constructed at `/tmp/mode23.sh` during the session;
not committed (one-liner; rebuild as needed).

— Sonnet, 2026-05-28 follow-up-3
