# FINDING — 2026-08-09 — Claude SN4.6 — RTCC RC-5-GVA: R9 = RT_GVA_VA (GVA Base Pointer) LANDED 1.036x

**Session:** s5 of GOAL-RTCC.md (Sonnet 4.6)
**SCRIP HEAD at session open:** `64e1bcbf` (AB-1 COMPLETE, concurrent seat)
**SCRIP HEAD at close:** `979f0db7` (after regen ×3)

---

## RC-5-GVA RUNG — LANDED

### Candidate Selection

Per the RC-5 anchor finding's directive ("next rung must target a global accessed inside the inner per-character scan loop or at every statement execution"), a census was run across 21 benchmark `.sno` files compiled with `SCRIP_RTCC=1 --compile`. Result: **1,038 `ABSQ(RT_GVA_VA + k*16)` GVA accesses** across 21 files, 48 sites across 7 template files.

Key properties of RT_GVA_VA that make it the ideal RC-5 candidate:

- **Compile-time constant** (`pin_va.h`: `0x70001000` — fixed by `rt_pin_init` mmap, never changes after process init). BLOCK-CANONICAL EXCEPTION: no C-side companion writes needed anywhere in the runtime.
- **Block slot seeded once** in `rtcc_init` constructor: `g_rtcc_block[RTCC_SLOT_R9] = RT_GVA_VA`. Eternal.
- **R9 already in the reload set** from RC-4 scratch-tier (`x86_rtcc_rl_bin` line 48: `mov r9, [r11+48]`). Zero new writeback/reload machinery.
- **RC-0(c) confirms zero ≥6-arg rt calls** (R9 = SysV arg5 never staged by any rt call).
- **disp8 range for all common variables**: roman.sno variables N/T/ROMAN are at GVA offsets 0–40 (k=0,1,2). All disp8 (`< 128`). Encoding win: 7B `ABSQ` (absolute disp32 + REX prefix, SIB no-base) → 4B `[r9+disp8]` per access.

### Implementation

**`rtcc.h`:** Added `RTCC_GLOBAL_R9_GVA 1`, `RTCC_SLOT_R9 6`, `RTCC_GVA_REG "r9"`, and design comment documenting the BLOCK-CANONICAL EXCEPTION.

**`x86_asm.h`:** Added same defines in extern-C block. Added `GVARQ(k, w)` helper returning `"qword ptr [r9 + k*16+w]"`. Parses as `XK_REGDISP` (base="r9", off=k*16+w) through the existing `x86_parse` path (line 1382–1384); routes to `x86_reg_disp32_load64` / `x86_reg_disp32_store64` which handle REX.B for R8+ bases via `if (b >= 8) rex |= 0x01`.

**`rtcc_init.c`:** Single line in `rtcc_init` constructor: `if (RTCC_GLOBAL_R9_GVA) g_rtcc_block[RTCC_SLOT_R9] = (uint64_t)(uintptr_t)(void *)RT_GVA_VA;`

**7 template files** — all 48 `ABSQ(RT_GVA_VA + k*16[+w])` sites converted to ternary:
`(g_rtcc_on && RTCC_GLOBAL_R9_GVA) ? GVARQ(k, w) : ABSQ(RT_GVA_VA + k*16 + w)`

Files: `bb_var_global.cpp` (2 sites), `bb_assign_global.cpp` (4), `bb_match_defer.cpp` (2), `bb_binop_gvar_arith.cpp` (2 via GVA_LD macro), `bb_call.cpp` (4), `bb_call_proc_staged.cpp` (26), `bb_save_restore.cpp` (4), `bb_func_activate.cpp` (4).

**`scrip.c`:** **Bug found and fixed** (see below) — `rtcc_load_all` call inserted at both main-entry inbound edges (mode-4 before `jmp flat_α`; mode-3 before `rt_outer_call`).

### Bug Found and Fixed: Main-Entry Inbound Load Gap

**Root cause:** The main program entry (`flat_α` in mode-4 / `rt_outer_call` → blob in mode-3) is the **first** C→generated crossing. RC-2/RC-3 wired `rtcc_load_all` into proc re-entries and `rt_call_arr`, but the cold-start main entry was missed. With RC-4, all block slots were BSS-zero — reloading zero was harmless. With RC-5-GVA, R9's slot holds `RT_GVA_VA = 0x70001000` — a non-zero constant. Any GVA access before the first C-RT call hit R9 still holding whatever `gva_register@PLT` left in it (garbage), causing immediate SIGSEGV.

**Fix (mode-4):** `scrip.c` line ~1484: `{ extern unsigned char g_rtcc_on; if (g_rtcc_on) emit_textf("  call rtcc_load_all@PLT\n"); }` inserted between the `r12` seed and `jmp flat_α`.

**Fix (mode-3):** `scrip.c` line ~1638: `{ extern void rtcc_load_all(void); extern unsigned char g_rtcc_on; if (g_rtcc_on) rtcc_load_all(); }` inserted before `rt_outer_call(fn, mf, 0)`.

Both gated on `g_rtcc_on` — killswitch OFF → byte-identical.

### Killswitch Verification

- `SCRIP_RTCC=0`: 0 `r9`-relative, 114 absolute GVA accesses in roman.sno asm — **byte-identical fallback CONFIRMED**.
- `SCRIP_RTCC=1`: 114 `r9`-relative, 0 absolute — **full conversion CONFIRMED**.

### Poison Probe

`g_rtcc_block[RTCC_SLOT_R9] = 0xDEADBEEFDEADBEEF` via `LD_PRELOAD` shim, then `SCRIP_RTCC=1 ./scrip --run arith_loop.sno`: **SIGSEGV** (arm is live). Clean run (no poison): **PASS 1000000 iterations**. BY-CONSTRUCTION falsified.

### Rail Result

Both arms `SCRIP_RTCC=1`. Two binaries: `RTCC_GLOBAL_R9_GVA=0` (ABSQ, built via `CPPFLAGS=-DRTCC_GLOBAL_R9_GVA=0`) vs `RTCC_GLOBAL_R9_GVA=1` (GVARQ, default build). min-of-6:

| Benchmark | OFF min ms | raw OFF | ON min ms | raw ON | OFF/ON ratio |
|-----------|-----------|---------|----------|--------|-------------|
| fibonacci.sno | 433 | 433 434 444 441 454 442 | 418 | 421 418 423 472 437 432 | **1.036x** |
| var_access.sno | 437 | 452 438 437 444 441 441 | 425 | 435 439 426 431 436 425 | **1.028x** |

Both > 1.00x → **RUNG LANDS. No revert.**

### Board Sweep

- **Mode-3 BY-SET:** RTCC-FAIL=0. PASS 241 DIVERGE 24 ERROR 52 TIMEOUT 1 ON; 6 programs moved (DIVERGE↔ERROR) — identical pre-existing flake set from RC-4. CRATER=ZERO.
- **Mode-4 BY-SET:** RTCC-FAIL=0. EMPTY diff (zero programs changed status). CRATER=ZERO.

### Regen

regen ×3 clean: benchmark `.s` (21 files changed), feature `.s`, demo `.s`. All committed.

---

## Gate

Smoke: arith_loop m3 PASS (RTCC=0 and RTCC=1). fibonacci m3 PASS both arms. Board sweep RTCC-FAIL=0 both modes. Poison probe SIGSEGV (arm live). Rail 1.036x > 1.00x (no revert). regen ×3 clean.
