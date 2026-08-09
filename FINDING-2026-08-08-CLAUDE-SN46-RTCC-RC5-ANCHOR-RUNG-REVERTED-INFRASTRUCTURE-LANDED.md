# FINDING — 2026-08-08 — Claude SN4.6 — RTCC RC-5: &ANCHOR Rung Attempted, Rail 1.000x, Reverted; Infrastructure Committed

**Session:** s4 of GOAL-RTCC.md (Sonnet 4.6, same day as RC-0..RC-4)
**SCRIP HEAD at session open:** `129dbb06` (RC-4 regen artifacts)

---

## RC-5 ANCHOR RUNG — REVERTED PER ≤1.00x RAIL LAW

### Candidate Selection

Read SPITBOL manual Ch.18 (pattern match algorithm) and Ch.16 (keywords) and cross-referenced against emitted `roman.s`. The `&ANCHOR` value (`rt_anchor_g` / `g_anchor`) is read in every `bb_match_begin` retry loop via a 3-instruction GOT-deref sequence:

```
mov rcx, [rip + rt_anchor_g@GOTPCREL]
mov rax, [rcx]
cmp rax, 0
jne .exhaust
```

Per SPITBOL Ch.18 step 6: when the pattern stack is empty and `&ANCHOR` is nonzero, the match fails immediately instead of advancing the start cursor. This fires O(subject_length × match_attempts) times. Assignment to R8 (RTCC_SLOT_R8, already reloaded by RC-4's scratch-tier reload) would collapse the 3-insn sequence to `test r8, r8`.

### Implementation

- `rtcc.h`: `RTCC_GLOBAL_R8_ANCHOR` killswitch + `RTCC_SLOT_R8` define in `x86_asm.h`
- `keywords.c`: block-canonical companion — `if (g_rtcc_on) g_rtcc_block[RTCC_SLOT_R8] = (uint64_t)(int64_t)iv` at the `g_anchor` write site
- `core.c`: same companions at both `kw_anchor` write sites (the `kw_anchor` in `core.c` and `g_anchor` in `keywords.c` are separate globals that both track `&ANCHOR`; block companion writes added to both)
- `x86_asm.h`: `rt_anchor_ptr` declared with C linkage, `x86("rtcc_anchor_cmp")` encoder arm (OFF path = original 3-insn GOT-deref; ON path = `test r8, r8`)
- `bb_match_begin.cpp` + `bb_match_advance.cpp`: replaced 3-insn sequences with `x86("rtcc_anchor_cmp")`

### Rail Result

Proper A/B: same binary, two `.so` variants (RTCC_GLOBAL_R8_ANCHOR=0 vs =1), both SCRIP_RTCC=1. roman.sno (the only benchmark with pattern matching in the hot loop), min-of-6:

| Arm | min ms | raw |
|-----|--------|-----|
| anchor-OFF (GOT-deref) | 24 | 24 26 24 26 25 24 |
| anchor-ON (test r8,r8) | 24 | 25 25 25 25 24 25 |
| **OFF/ON ratio** | **1.000x** | |

**REVERT LAW TRIGGERED: ≤1.00x → template changes reverted.**

### Root Cause Analysis

The anchor check fires in the **backtrack retry path** — after a complete pattern match attempt fails and the matcher considers whether to advance the start cursor. For roman.sno with subject `'1776'` (4 characters), the retry loop fires at most 4 times per `ROMAN('1776')` call. At 100K outer loop iterations, that is 400K anchor checks. Saving 3 instructions at ~3ns/instruction = ~1.2ms on a 22ms run, or ~5% — but only if RTCC writeback overhead doesn't dominate.

The boundary overhead from the 9-GPR writeback/reload (≈18 mov instructions per C-RT crossing) swamps the 3-instruction saving. Every `rt_match_enter` call (which happens once per pattern match attempt) already pays the full RTCC crossing cost. The anchor check saving is inside the generated-code-only retry loop and therefore DOES save the GOT-deref — but the box is too noisy at 22ms to resolve it.

func_call.sno (no pattern matching) showed no effect, confirming the isolation.

### Correctness Win (Retained)

`099_keyword_rw` (anchor round-trip test) consistently PASS ON vs DIVERGE OFF across two board sweep runs. The block-canonical write companions in `keywords.c` and `core.c` correctly update `g_rtcc_block[RTCC_SLOT_R8]` when `&ANCHOR` is written, so the R8 cache stays coherent. This fix is retained even though the performance rung reverted.

### What Was Committed

After stashing the template changes (bb_match_begin/bb_match_advance), the remaining diff is:

- `src/runtime/rtx/rtcc.h`: RC-5 design comment + `RTCC_GLOBAL_R8_ANCHOR` killswitch define
- `src/runtime/keywords.c`: `#include "rtx/rtcc.h"` + block-canonical companion at `g_anchor` write
- `src/runtime/core/core.c`: `#include "../rtx/rtcc.h"` + block-canonical companions at both `kw_anchor` write sites
- `src/templates/x86_asm.h`: `RTCC_SLOT_R8` define, `RTCC_GLOBAL_R8_ANCHOR` define, `rt_anchor_ptr` C-linkage extern, `x86("rtcc_anchor_cmp")` encoder arm (wired, no template calls it post-revert)

Smoke: 6/6 OFF and ON. CRATER=ZERO by set (board sweep, both runs). Gate clean.

### Next RC-5 Rung

The anchor retry path is too cold to beat boundary overhead at O0. Next rung must target a global that is accessed **inside the inner per-character scan loop** or at **every statement execution**. Census candidates by dynamic frequency, not static guessing:

- **GVA base (RBX already!)** — RBX holds the heap frontier / GVA base (callee-saved, already SCRIP-owned, NOT in the caller-saved claimed set). Variables `N`, `T`, `ROMAN`, etc. in roman.sno are accessed as `qword ptr [1879052304]` — absolute addresses into the GVA island. If a GVA-base register replaced those absolutes, every named-variable read/write would benefit. This is the ICN-GVA-M3 pattern applied to SNOBOL4.
- **NV dict base** — `NV_GET_fn` / `NV_SET_fn` are the hottest dynamic call targets (RC-0 census: 43 NV_SET sites). But there's no exposed base pointer — it's opaque.
- **pat/dcap pool frontier** — `g_pat_pool_cur` is written per pattern node allocation, but only during pattern compile, not per-character scan.

The GVA base angle is the most promising but requires the SNOBOL4 emitter to emit `[R_GVA_BASE + k*16]` addressing instead of absolute slot addresses — a larger change than a simple slot assignment.

---

## Gate

Smoke: 6/6 (OFF and ON).
Board sweep m3: RTCC-FAIL=0 (two runs, nondeterministic flake set varies between runs — preexisting class).
Rail: roman.sno 1.000x (boundary of revert law; reverted).
