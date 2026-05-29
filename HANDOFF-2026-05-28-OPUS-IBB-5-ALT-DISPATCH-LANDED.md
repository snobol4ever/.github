# HANDOFF-2026-05-28 — Opus 4.7 — IBB-5 alt.icn mode-3 LANDED (counter-state dispatch)

**Goal:** ICON-BB (`GOAL-ICON-BB.md`)
**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7
**one4all HEAD:** `1a97c0a3`
**.github HEAD:** to be set by handoff push

## Headline

Canonical-5 Icon BB **mode-3 advances 3/5 → 4/5**. `alt.icn` (`every write(1 | 2 | 3)`) now produces `1\n2\n3\n` byte-identical to mode-2. The architectural blocker named in HANDOFF-2026-05-28-SONNET-IBB-EVERY-TO-LANDED-ALT-PLUMBING (Option A: fold counter-state dispatch into `bb_alt.cpp`) is closed.

## What landed (one4all `1a97c0a3`)

### Fix: BB_ALT counter-state dispatch slab (the named architectural blocker)

**`src/emitter/emit_bb.c` — `flat_drive_alt_icn` driver rewritten:**
- Walks arms via `pBB->α` ω-chain (per `lower_icn_new_Alt`: arm[0]=pBB->α; arm[i+1]=arm[i]->ω). NOT via `bb_pat_kid`, which would read `pBB->counter` as a kids-state pointer and crash for Icon BB_ALT (where `counter` is a runtime int64 slot).
- Allocates per-arm α-labels (`xalt%d_a%d_α`) and per-arm β-labels.
- Queues arm-α labels into `g_emit.xa_bb_emit_pair_jmp[]` via `EMIT_PAIR_JMP` (one entry per arm; defines all NULL).
- `EMIT_PAIR_FILL(pBB, ...)` triggers `bb_alt` template to emit the dispatcher FIRST.
- Then lays down arm bodies: each gets its α-label defined immediately before `walk_bb_flat(arm[i], lbl_γ, lbl_ω, arm_β[i])`. Arm.γ → outer γ (yield path), arm.ω → outer ω (never reached for single-shot BB_LIT_I).
- Architectural pattern mirrors `flat_drive_pl_choice` (template-first-then-bodies).

**`src/emitter/BB_templates/bb_alt.cpp` MEDIUM_BINARY rewritten** from 10-byte port-wired stub to counter-state dispatch slab. Reads arm-α targets from `g_emit.xa_bb_emit_pair_jmp[]`. Uses `&pBB->counter` (same int64 slot mode-2 uses at `bb_exec.c:1720`) as the arm index. Bytes layout (offsets exact for any n):

| Offset | Bytes | Asm |
|---|---|---|
| 0 | `48 B9` + u64 `&counter` | movabs rcx, &counter |
| 10 | `48 C7 01 00 00 00 00` | mov qword[rcx], 0 |
| 17 | `EB <imm8>` | jmp short dispatch (disp computed at emit time, fits since dispatch is 19 bytes away) |
| **19** | **(lbl_β defined)** | |
| 19 | `48 B9` + u64 `&counter` | movabs rcx, &counter |
| 29 | `48 81 01 01 00 00 00` | add qword[rcx], 1 |
| 36 | **(dispatch label, implicit — fall through)** | |
| 36 | `48 B9` + u64 `&counter` | movabs rcx, &counter |
| 46 | `48 8B 09` | mov rcx, [rcx] |
| 49 + 13·i | `48 81 F9` + u32 `i` | cmp rcx, i (7 bytes; imm32 form so n > 127 works) |
| 56 + 13·i | `0F 84` + u32 rel32 | je arm_α[i] (6 bytes; patched to external arm label) |
| 49 + 13·n | `E9` + u32 rel32 | jmp lbl_ω (5 bytes; patched to outer ω) |

For canonical-5 n=3: total slab = 88 + 5 = 93 bytes.

`bin.sites` ascending (required by `bb_emit_asm_result`'s patching loop):
- 19 (β define)
- 49+13·i+2 for i=0..n-1 (each je's u32 rel32 displacement site)
- 49+13·n+1 (final ω jmp's u32 rel32 site)

`pBB->counter` is a fixed runtime address (`(uintptr_t)&pBB->counter`); valid at emit time and at runtime. Mode-2 and mode-3 never coexist for the same node so the slot is unshared.

## Empirical validation

```
$ SCRIP_ICN_BB=1 ./scrip --interp /tmp/alt.icn
1
2
3
$ SCRIP_ICN_BB=1 ./scrip --run /tmp/alt.icn
1
2
3
```

Byte-identical mode-2 vs mode-3. Plus edge cases:
- `every write(42)` (n=1, no alt — goes through general `lower_icn_new_Call` path, not alt driver): still prints `42` both modes.
- `every write(10 | 20 | 30 | 40 | 50)` (n=5): both modes print `10..50`.

## Canonical-5 mode-3 status

| Test | Mode-2 | Mode-3 | Notes |
|---|---|---|---|
| hello.icn | ✅ | ✅ | `6393c743` |
| add.icn | ✅ | ✅ | `e612d519` |
| every_to.icn | ✅ | ✅ | `fac53504` |
| alt.icn | ✅ | **✅ NEW** | `1a97c0a3` (this handoff) |
| full.icn | ✅ | ❌ | BB_BINOP_GEN dispatch gap |

## Gates HOLD (verified post-rebase against `1a97c0a3`)

```
smoke_icon              5/5     ✅
smoke_prolog            5/5     ✅
smoke_raku              5/5     ✅
smoke_snobol4          13/13    ✅
smoke_unified_broker   39/14    ✅
FACT-RULE grep          0       ✅
icon crosscheck         2/4     ✅ (concat/if_expr --run FAILs are PRE-EXISTING)
```

`if_expr --run` and `concat --run` FAILs in `test_crosscheck_icon.sh` were verified PRE-EXISTING via `git stash` baseline run on `a21dc32b`. Both root-cause to the same `flat_drive_binop_tree: missing α or β child` abort (unchanged from prior sessions). NOT regressions.

## Why this works (semantics)

For canonical-5 `every write(1|2|3)`, control flow per pump:
1. EVERY pumps body (write call). Enter write.α → arg.α (= alt's slab entry @ offset 0).
2. alt.α: counter=0, jmp short dispatch.
3. dispatch (offset 36): mov rcx, counter[=0]; cmp rcx,0; je arm_α[0] → arm 0 fires (push 1, jmp γ_outer).
4. γ_outer hits the call's trailer: pop+write_int_nl → "1\n" printed, jmp lbl_γ_of_call.
5. lbl_γ_of_call is wired to body_β by `flat_drive_every` (re-pump).
6. body_β → call.β → arg.β (via `flat_drive_call_intexpr` EMIT_PAIR_DEF_JMP(lbl_β, arg_β)).
7. arg_β = alt.lbl_β (= slab offset 19). Counter++ (now 1), fall through to dispatch.
8. dispatch: counter=1; cmp rcx,0 fails; cmp rcx,1 matches → je arm_α[1] → arm 1 fires (push 2, jmp γ).
9. ... arm 2 yields 3 ...
10. Next pump: counter=3; cmp rcx,0/1/2 all fail; jmp lbl_ω.
11. lbl_ω → call.ω → arg's outer ω → EVERY's lbl_γ (every-succeeds-on-exhaustion path, per `flat_drive_every`).

Mode-2 reference for the same semantics: `bb_exec.c:1720` BB_ALT handler walks the same ω-chain with `bb->counter` as the arm index.

## NEXT (in priority order)

1. **`full.icn` mode-3 → 5/5:** BB_BINOP_GEN dispatch in `bb_call` int_expr predicate + new `flat_drive_binop_gen_tree` driver (cross-product walk of two `BB_TO` operand sub-trees applying `*`/`>` via `rt_arith`). PLAN.md NEXT (2).
2. After canonical-5 5/5: flip `SCRIP_ICN_BB` default per IBB-7 watermark; run full mode-3 corpus sweep.
3. Crosscheck `flat_drive_binop_tree: missing α or β child` abort fix (would close `concat`/`if_expr --run` failures concurrently).

## Files touched

```
src/emitter/BB_templates/bb_alt.cpp | 92 ++++++++++++++++++++++++++++---------
src/emitter/emit_bb.c               | 56 ++++++++++++----------
2 files changed, 104 insertions(+), 44 deletions(-)
```

## Architectural notes for future generators on this driver

The bb_alt template-first emit pattern (queue arm targets via xa_bb_emit_pair_jmp[], EMIT_PAIR_FILL emits dispatcher, then lay down bodies) generalizes cleanly to:
- BB_BINOP_GEN (next gap, full.icn): cross-product over two generator operands; the same "queue targets then emit dispatcher then bodies" shape applies for the inner loop's reset.
- More-than-3 arm BB_ALT (verified n=1 and n=5).
- Future ALT with generator arms (BB_TO mixed in): would need per-arm.ω routed to "advance counter and re-dispatch" instead of outer ω. Adapter point: change `walk_bb_flat(arms[i], lbl_γ, lbl_ω, arm_β[i])` to `walk_bb_flat(arms[i], lbl_γ, dispatch_advance_label, arm_β[i])` where `dispatch_advance_label` is a new label defined at the slab's β-section start. For canonical-5 all single-shot, this is moot.
