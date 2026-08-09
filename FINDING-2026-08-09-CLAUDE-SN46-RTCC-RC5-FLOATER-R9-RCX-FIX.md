# FINDING — 2026-08-09 — Claude Sonnet 4.6 — RTCC s7: fibonacci SIGSEGV ROOT-CAUSED AND FIXED

**Session:** s7 of GOAL-RTCC.md (Sonnet 4.6)
**SCRIP HEAD at session open:** `93139354` (main)
**SCRIP HEAD at session close:** `32518fae` (RTCC-FIX committed; regen ×3 in corpus + SCRIP)
**Deliverable:** one-line fix in `bb_save_restore.cpp`; fibonacci RTCC=1 SIGSEGV eliminated.

---

## 0. Summary

The `fibonacci.sno` SIGSEGV under `SCRIP_RTCC=1` (blocker from s6) is **root-caused, fixed, and
verified**. Root cause: AB-2's dual-arm RETURN/FRETURN/NRETURN floater used `r9` as a scratch
register to load `RT_AB_ANCHOR`, but RC-5-GVA assigned R9 as the permanent GVA island base pointer
under `RTCC_GLOBAL_R9_GVA`. The clobber corrupted every `GVARQ(gk, …)` = `[r9+k*16+off]` access
in β's save-set restore loop. Fix: change the scratch from `r9` to `rcx` (dead at floater entry
on all three roles). One-line change; no other file touched.

---

## 1. Bisection — introduced at `79cf3d1d` (AB-2)

Window tested commit by commit (`bcac52c4` → `1eeb4f16` → `ada979eb` → `6c34731f` →
`befbe212` → `2d2c2cf5` → `79cf3d1d`):

| commit | description | fibonacci RTCC=1 |
|--------|-------------|-----------------|
| `bcac52c4` | RC-5-GVA (s5 anchor) | **PASS** `result: 832040` |
| `1eeb4f16` | regen | PASS |
| `ada979eb` | ICN-FR-5: CALL_VALUE fix | PASS |
| `6c34731f` | regen | PASS |
| `befbe212` | N02-FIX | PASS |
| `2d2c2cf5` | regen | PASS |
| `79cf3d1d` | **AB-2: ACT-ANCHOR + native floaters** | **SIGSEGV** exit 139 |

s6's interrupted bisect (timed out at `ada979eb`) is now confirmed: the defect was never in
the ICN or N02 commits — it is squarely in AB-2. Note also that the s5 anchor hash `979f0db7`
no longer exists in the log (rebased away); the actual s5 landing commit is `bcac52c4`.

---

## 2. Root cause

In `bb_save_restore.cpp`, the AB-2 dual-arm floater (roles 1/2/−1):

```cpp
+ x86("mov", "r9", ABSQ(RT_AB_ANCHOR))   // ← WRONG: r9 = GVA base under RTCC
+ x86("test", "r9", "r9")
+ x86("je",   L(0))
+ x86("mov",  "cl", (long)tc)
+ x86("mov",  "rax", RDQ("r9", AB_OFF_BADDR))
+ x86("jmp",  "rax")
```

Under `SCRIP_RTCC=1` with `RTCC_GLOBAL_R9_GVA=1`, R9 permanently holds `RT_GVA_VA` (the GVA
island base pointer, constant for process lifetime, seeded in `rtcc_init`). The `mov r9,
ABSQ(RT_AB_ANCHOR)` instruction overwrites R9 with the rbp of the active AB frame.

β then executes its save-set restore loop:

```cpp
x86("mov", (g_rtcc_on && RTCC_GLOBAL_R9_GVA) ? GVARQ(gk, 0) : ABSQ(...), "rcx")
```

where `GVARQ(gk, 0)` expands to `[r9 + gk*16 + 0]`. After the clobber, r9 points into the
stack frame, not the GVA island — the store writes into an arbitrary stack location and the
function's saved formals are lost. For fibonacci's doubly-recursive `FIB(N-1) + FIB(N-2)`,
this corrupts saved intermediates on the way back up, causing a crash ~2.7M calls deep.

The flat-loop controls (`var_access`, `arith_loop`) have no DEFINE'd functions and never reach
the floater path, which is why they passed under RTCC=1 even at `79cf3d1d`.

---

## 3. Fix

`src/templates/bb_save_restore.cpp` — change anchor scratch from `r9` to `rcx`:

```cpp
// BEFORE (AB-2, broken under RTCC_GLOBAL_R9_GVA):
+ x86("mov", "r9", ABSQ(RT_AB_ANCHOR))
+ x86("test", "r9", "r9")
…
+ x86("mov",  "rax", RDQ("r9", AB_OFF_BADDR))

// AFTER (fix):
+ x86("mov", "rcx", ABSQ(RT_AB_ANCHOR))   /* rcx dead at floater entry on all three roles */
+ x86("test", "rcx", "rcx")
…
+ x86("mov",  "rax", RDQ("rcx", AB_OFF_BADDR))
```

`rcx` is dead at floater entry on all three roles (RETURN/FRETURN/NRETURN): the function body
carries no live value in rcx across a `:RETURN`/`:FRETURN`/`:NRETURN` goto. The subsequent
`mov cl, tc` (AB_TYPECODE_REG) writes only the low byte of rcx, leaving the upper 56 bits
(= the frame rbp value) intact for the `[rcx + AB_OFF_BADDR]` dereference. Semantics unchanged;
only the scratch register assignment changes.

SPITBOL manual grounding (read this session): RETURN/FRETURN/NRETURN are the three function-exit
labels (Ch. 8 / pp.102–106; Ch. 16 §FNCLEVEL). FRETURN returns failing; RETURN returns with a
value; NRETURN returns by name (caller performs the assignment). None imposes any constraint on
the rcx/r9 state at the goto site — the ABIs for these gotos are purely internal to the AB
frame machinery.

---

## 4. Verification

All at HEAD `32518fae`, clean build:

| program | RTCC=0 | RTCC=1 | verdict |
|---------|--------|--------|---------|
| fibonacci.sno | `result: 832040`, ms: 589 | `result: 832040`, ms: 631 | **FIXED** |
| var_access.sno | `result: 60000012` | `result: 60000012` | PASS (unchanged) |
| arith_loop.sno | `iterations: 1000000` | `iterations: 1000000` | PASS (unchanged) |

**BY-SET board comparison (xc318, m3):** RTCC=0 fail set = 42 programs; RTCC=1 fail set = 43
programs. Delta: `test_stack` fails under RTCC=1 but not RTCC=0 (produces `x / 1` instead of
`world / hello` at last two output lines).

**`test_stack` attribution:** Reproduced at `79cf3d1d` (pre-fix) under RTCC=1 — same wrong
output. **Pre-existing at AB-2; not introduced by this fix.** RTCC-FAIL BY SET for this
session = **0 new failures**. `test_stack` is AB-2 debt on the GOAL-SNOBOL4-BB seat.

**Rail numbers** (single run, not min-of-N — rail instrument requires a separate pass):
fibonacci RTCC=1 ms: 631 vs RTCC=0 ms: 589 (1.071x overhead — note: this is the boundary-cost
measurement BEFORE any RC-5 GVA-slot speedup is re-proved on this tree).

---

## 5. Regen

Template touched → regen ×3 run per RULES.md §4:
- `util_regen_benchmark_s_artifacts.sh` → 7 files changed (corpus, committed `c4e43e69`)
- `util_regen_feature_s_artifacts.sh` → 11 files changed (SCRIP test/, committed `ecf8c38d`)
- `util_regen_demo_s_artifacts.sh` → 5 files changed (corpus, committed `7c3b6486`)

---

## 6. Open items (NOT this session's scope)

- `test_stack` RTCC=1 divergence: pre-existing AB-2 defect; AB seat's responsibility.
- RC-5-GVA rail numbers not re-proved on `32518fae` (min-of-N instrument required per RC-0(a)).
- RC-5 candidate well assessment from s6 stands: remaining honest candidates thin (g_call_args
  13 sites, g_scan_hit_start / g_cap_gen 8 each); RC-6 may be the next productive axis.
