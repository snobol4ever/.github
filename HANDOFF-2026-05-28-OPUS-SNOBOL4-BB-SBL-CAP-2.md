# HANDOFF — 2026-05-28 · Opus 4.7 · SNOBOL4-BB · SBL-CAP-2

## Repos / HEADs

| Repo    | HEAD       |
|---------|------------|
| one4all | `e9a9d7f3` |
| .github | (this commit) |

Tree: **CLEAN** after this push.

---

## Gates

| Gate | Before | After |
|------|--------|-------|
| G1 SNOBOL4 smoke (default `--run`) | 13/13 | 13/13 |
| G1 SNOBOL4 smoke (SCRIP_M3_NATIVE=1) | 13/13 | 13/13 |
| G2 unified broker | 31 | 31 |
| G3 broad corpus mode-4 (`--compile`) | 175/280 | 175/280 |
| G4 broad corpus mode-2 (`--interp`) | 238/280 | 238/280 |
| **NATIVE corpus** (`--run` SCRIP_M3_NATIVE=1) | **156/280** | **165/280** (+9) |
| Rung suite | M2=19 M4=15 SKIP=0 | M2=19 M4=15 SKIP=0 |
| FACT RULE | 0 | 0 |
| audit_m3_native_binary_arms.sh | GATE OK | GATE OK |

---

## What was done

### SBL-CAP-2 ✅ — bb_capture.cpp MEDIUM_BINARY arm

Closed via commit `e9a9d7f3`. The previous EMERGENCY commit `33ca255d` left an unconditional `bomb_bytes(...)` return on line 52 of `bb_capture.cpp` because the partial implementation behind it had three bugs that together produced the `bb_emit_end: site=19 label=''` unresolved-forward abort under brokered build.

**Bugs found & fixed:**

1. **Wrong sites array.** Old `{35, 45, 68, 116}` had the `0F 84` rel32 sites off-by-one. The `je rel32` opcode is two bytes (`0F 84`) and the rel32 starts at opcode+2, not opcode+1. Corrected to `{40, 49(def), 77, 124}`.

2. **Wrong internal jmp pre-patch.** Old computed `target=73, after-addr=45, rel32=28`. Corrected to `target=81, after-addr=49, rel32=32` (matches new layout where the lbl_β define is at offset 49 not 45).

3. **GC-unsafe scratch.** Old used `GC_MALLOC(sizeof(int))` for `saved_Δ`. But the bb_pool is mmap'd and not GC-scanned; the saved_Δ pointer baked as imm64 into blob bytes is invisible to the GC, so collection could free saved_Δ. Same bug class blocked SBL-SPAN-2's earlier attempt.

   **Fix (key pattern for future scratch needs):** allocate via process-lifetime `std::deque<int>`:
   ```cpp
   static int * cap_alloc_saved_delta_slot(void) {
       static std::deque<int> pool;
       pool.emplace_back(0);
       return &pool.back();
   }
   ```
   std::deque guarantees pointers/refs to existing elements stay valid across `push_back`. C++ heap is real OS memory, not GC-managed — no collection concerns. This is the GC-safe replacement for any per-template-call BINARY scratch and applies to **SBL-SPAN-2, SBL-ARBNO-3, SBL-BREAKX-2**.

4. **Missing r10 preservation.** SysV ABI makes r10 caller-saved. The brokered child re-establishes r10=&Δ in its own prologue (XA_FLAT_PROLOGUE) so r10's value is incidentally preserved across the call, but defensive `push r10` / `pop r10` matches bb_pat_any's pattern around strchr. Added.

**Layout (128 bytes total):**

| Off | Bytes | Asm | Comment |
|-----|-------|-----|---------|
| 0   | 41 8b 02 | mov eax, [r10] | eax = current Δ |
| 3   | 48 b9 \<8\> | movabs rcx, &saved_Δ | |
| 13  | 89 01 | mov [rcx], eax | *saved_Δ = Δ |
| 15  | 31 ff | xor edi, edi | zeta=0 |
| 17  | 31 f6 | xor esi, esi | entry=0 |
| 19  | 48 b8 \<8\> | movabs rax, child_fn | |
| 29  | 41 52 | push r10 | preserve |
| 31  | ff d0 | call rax | |
| 33  | 41 5a | pop r10 | restore |
| 35  | 83 f8 63 | cmp eax, 99 | DT_FAIL? |
| 38  | 0f 84 [r32] | je ω | **site[0]** rel32 @40 |
| 44  | e9 [r32] | jmp assign | internal, pre-patched rel32=32 @45 |
| 49  | (lbl_β define) | | **site[1]** label-define |
| 49  | 31 ff | xor edi, edi | |
| 51  | be 01 00 00 00 | mov esi, 1 | entry=1 (retry) |
| 56  | 48 b8 \<8\> | movabs rax, child_fn | |
| 66  | 41 52 | push r10 | |
| 68  | ff d0 | call rax | |
| 70  | 41 5a | pop r10 | |
| 72  | 83 f8 63 | cmp eax, 99 | |
| 75  | 0f 84 [r32] | je ω | **site[2]** rel32 @77 |
| 81  | (assign) | | |
| 81  | 48 bf \<8\> | movabs rdi, varname | |
| 91  | 48 b9 \<8\> | movabs rcx, &saved_Δ | |
| 101 | 8b 31 | mov esi, [rcx] | esi = saved_Δ |
| 103 | 41 8b 12 | mov edx, [r10] | edx = current Δ |
| 106 | b9 \<imm32\> | mov ecx, imm | |
| 111 | 48 b8 \<8\> | movabs rax, &rt_cap_assign_cursor | |
| 121 | ff d0 | call rax | |
| 123 | e9 [r32] | jmp γ | **site[3]** rel32 @124 |
| 128 | (end) | | |

`bin = { {40, 49, 77, 124}, {ω_p, β_p, ω_p, γ_p}, {false, true, false, false} };`

**Validated:**
- 039_pat_any.sno under `SCRIP_M3_NATIVE=1` → "e" (matches oracle and `--interp`).
- GATE-1 smoke 13/13 both default and native.
- Broad corpus native: **156→165/280** (+9). Fixed: 039_pat_any, 040_pat_notany, 042_pat_break, 043_pat_len, 058_capture_dot_immediate, 059_capture_dollar_deferred, W07_capt_cond, W07_capt_fail, W07_capt_imm.
- Zero new regressions across G1/G2/G3/G4 and rung suite.
- FACT RULE = 0; audit_m3_native_binary_arms.sh = GATE OK.

### Goal file pruning

GOAL-SNOBOL4-BB.md trimmed 363→287 lines. Verbose multi-paragraph session-log entries collapsed to one-liners; completed steps marked `[x]` with terse summary; full byte layouts moved to in-source comments and the handoff doc (here).

---

## Next session

Continue **M3-NATIVE-4 corpus parity** — knock down the remaining ~73 native-only failures by cluster:

| Cluster | ~Count | Blocker |
|---------|--------|---------|
| SPAN | ~10 | SBL-SPAN-2 BINARY arm — apply deque-int scratch pattern (NOT GC_MALLOC, NOT rt_cs_t widening); absolute-z_orig, not [r10]-relative |
| ALT | ~6 | `bb_pat_alt` is EMPTY/COMMENT (deferred from M3-NATIVE-0); investigate stub vs structurally-empty |
| ARBNO | ~8 | SBL-ARBNO-3 BINARY arm — same deque pattern; brokered child via movabs+call (cf. now-working bb_capture) |
| FENCE | ~6 | Investigate `bb_pat_fence` native correctness — may be combinator like ALT |
| POS/RPOS/TAB/RTAB/REM/ARB/TWO | ~10 | Individual leaf arms |
| capture-of-complex compositions | ~10 | Derive from atomic fixes above |

After ~73 → ~0: flip default off `SCRIP_M3_NATIVE` getenv at scrip.c:449. Then mode-3 `--run` is pure x86 by default, matching ARCH-SCRIP end state.

**Reference for next session:** bb_capture.cpp is now the canonical BINARY arm with brokered child call-out + per-node scratch. Pattern for SPAN/ARBNO/BREAKX is "copy this template, change the inner logic". Don't introduce new scratch mechanisms.

---

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Opus 4.7
