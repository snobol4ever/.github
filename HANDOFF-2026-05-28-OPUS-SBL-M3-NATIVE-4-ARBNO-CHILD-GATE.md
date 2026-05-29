# HANDOFF — SBL-M3-NATIVE-4 ARBNO MEDIUM_BINARY child-gate fix

**Date:** 2026-05-28
**Author:** Claude Opus 4.7
**Commits:** one4all `4471b80d`, .github `58cfb84f`
**Predecessor:** `HANDOFF-2026-05-28-OPUS-SBL-M3-NATIVE-4-ARBNO-TREE-FOUNDATION.md`

---

## TL;DR

Two-line surgical fix to `src/emitter/BB_templates/bb_arbno.cpp:19`. The predecessor session diagnosed the bug exactly; this session landed the fix and verified the result.

**Diff:**
```diff
-        if (!child_lbl || !child_lbl[0]) {
+        int have_child = MEDIUM_BINARY ? (g_emit.bb_child_fn != NULL) : (child_lbl && child_lbl[0]);
+        if (!have_child) {
```

**Result:** native broad corpus 157/280 → **160/280 (+3)**, zero regressions. All sister gates byte-identical. Newly passing natively: `W04_arbno_basic`, `W04_arbno_backtrack`, `W04_arbno_zero`.

---

## Why this fix works

Root cause was correctly identified in the predecessor handoff. `bb_prepare_capture_arbno` in `src/emitter/emit_bb.c:608-628` populates:

- `g_emit.bb_child_fn` — **always set** (line 615, unconditional)
- `g_emit.bb_child_lbl` — **only set inside the `if (MEDIUM_TEXT)` branch** (line 618-621)

The pre-fix gate in `bb_arbno.cpp:19` (`if (!child_lbl || !child_lbl[0])`) tested `bb_child_lbl` unconditionally. In MEDIUM_BINARY this was always empty, so the gate fired the 10-byte no-define fallback (`bin = {{1,6},{γ_p,ω_p},{false,false}}`) — which omits the β-define needed by the outer flat slab. The outer slab's β-patch then went unresolved at `bb_emit_end`:

```
bb_emit_end: 1 unresolved forward reference(s):
  site=19 label='pat_brok_β'
```

After the fix, MEDIUM_BINARY consults `bb_child_fn` directly, falls through to the full 259-byte arm, β gets defined at offset 186, slab patches resolve.

## Why `bb_capture.cpp` did NOT need the same fix

I verified by reading `bb_capture.cpp` lines 30-140 directly. Its gating is already structured correctly:
- Line 38: `if (MEDIUM_BINARY) { if (!child_fn || !varname || !varname[0]) return std::string(); ... }` — BINARY arm gates on `child_fn`
- Line 132: `if (!child_lbl || !child_lbl[0] || !varname || !varname[0]) return std::string();` — only reached AFTER the BINARY arm has been exited; this is the TEXT arm guard

So the duplicate pattern was confined to `bb_arbno.cpp`. No further template needed the same surgical edit.

## What the gate fix did NOT fix (the surprise)

The predecessor handoff predicted: "After fix, 052 should yield `aaa` and 054 should yield `abba` natively."

That did not happen. 052 and 054 still fail natively — but now they **segfault at runtime** instead of aborting at `bb_emit_end`. The fix definitely worked: the ARBNO BINARY arm now emits its full 259 bytes and execution reaches the slab.

**But:** gdb traces the SIGSEGV to the **POS(0) arm preceding ARBNO in the same flat slab**, not the ARBNO arm itself.

```
0x7ffff7400013:  41 8B 02              mov eax, [r10]       ← POS arm [0]
0x7ffff7400016:  3D 00 00 00 00        cmp eax, 0            ← POS arm [3], ival=0
0x7ffff740001b:  0F 32                 rdmsr (CRASH)         ← should be 0F 85 (jne)
0x7ffff740001d:  01 00 00 00 ...
```

The byte at offset 0x1c is `0x32` where `0x85` should be. The `0F 85 <rel32>` jne opcode has been corrupted into `0F 32` (rdmsr). Almost certainly a rel32 patcher writing one byte too early.

**Confirming this is pre-existing (not introduced by my fix):** rung `044_pat_pos` (`X POS(0) LEN(3) . V`, no ARBNO involved) **also segfaults natively at HEAD before my fix.** I verified by `git stash` → rebuild → run → restore. So 052/054 hit two serially-related bugs, only the first of which (ARBNO) was mine to fix this session.

## SBL-POS-PATCH-OFFSET — the next obvious rung

Recommended next session work.

### Suspicious site declarations

`src/emitter/BB_templates/bb_pat_pos.cpp:17-18`:
```cpp
bin = rpos
    ? bb_bin_t{ {25, 31, 36, 37}, {_.lbl_ω_p, _.lbl_γ_p, _.lbl_β_p, _.lbl_ω_p}, {false, false, true, false} }
    : bb_bin_t{ {9, 15, 20, 21},  {_.lbl_ω_p, _.lbl_γ_p, _.lbl_β_p, _.lbl_ω_p}, {false, false, true, false} };
```

POS arm layout produced by lines 30-34:
```
[0-2]   41 8B 02              mov eax, [r10]
[3-7]   3D 00 00 00 00        cmp eax, imm32
[8-9]   0F 85                 jne opcode
[10-13] <rel32>                jne target (→ ω)
[14]    E9                    jmp opcode
[15-18] <rel32>                γ
[19]    E9                    jmp opcode
[20-23] <rel32>                β=ω
```

Three observations:

1. **POS site=9 is INSIDE the `0F 85` opcode (offset 8-9)**, not at the rel32 start (10). Same off-by-one for RPOS site=25 (its `0F 85` is at 24-25, rel32 at 26).

2. **POS site=20 collides with the β-define position.** Site=20 is `lbl_ω_p` patch with `is_def=false`. Site=21 is `lbl_β_p` define with `is_def=true`. But the third `E9` is at offset 19 (β should be defined HERE), and its rel32 is at 20-23 (β=ω patch should go HERE). So sites should arguably be `{10, 15, 19-def, 20}` not `{9, 15, 20, 21}`.

3. **ANY's working sites (`bb_pat_any.cpp:55`):** `{17, 72, 86, 90, 100}`. ANY's first `0F 8D` opcode is at offset 15-16, rel32 at 17-20. So site=17 IS at the rel32 start (after the opcode). That's the consistent convention.

So POS's `0F 85` site convention is inconsistent with ANY's `0F 8D` convention. Both are two-byte `0F xx` opcodes. ANY works, POS doesn't.

### Validation path for next session

1. **Don't assume** which side is wrong. Instrument the patcher first.
2. Add temporary fprintf to wherever rel32 patches happen — likely `bb_emit_end` in `src/emitter/emit_bb.c` (or `sm_run_native` in `src/processor/sm_native.c` for SM-level rel32). Log `site_offset`, `opcode_byte_at_site`, `bytes_written`.
3. Run a passing native test (e.g. `039_pat_any.sno`) and a failing one (e.g. `044_pat_pos.sno`). Compare what the patcher does vs the site declarations.
4. Derive the actual convention from ANY (known good), apply to POS/RPOS.
5. Validate: 044 native should yield `hel`. 052 native should yield `aaa`. 054 native should yield `abba`.
6. Revert the fprintf instrumentation.

### Predicted impact

Fixing POS/RPOS opens (estimating from FAIL list):
- `044_pat_pos`, `045_pat_rpos`
- `052_pat_arbno`, `054_pat_arbno_alt` (ARBNO + anchors, blocked on this)
- All the `*POS(0) ... RPOS(0)*` framed tests (~10-15 tests)
- Possibly some FENCE tests that also use POS internally

So this is high-value: probably native 160 → 175+ in a single session.

## Other paths if SBL-POS-PATCH-OFFSET stalls

- **SBL-ARBNO inside combinators.** `patnd_tree_eligible` still rejects XARBN under combinators in some cases. Verify with `055_pat_concat_seq` patterns containing ARBNO. (Foundation is in `debb8a4e`; this would extend it.)
- **SPAN cluster.** SBL-SPAN-2 BINARY arm exists (per Sonnet 4.6 `4ce8c385`), but ~10 SPAN tests still fail natively. Bisect.
- **BREAKX cluster.** SBL-BREAKX-2 — `pBB->ival==1` branch needs own BINARY arm.
- **FENCE-with-flat-wire.** Combinator flat-wire is enabled (`10f97d29` "M3-NATIVE-4 combinator flat-wire LANDED"), FENCE template has bytes ready (SBL-EP-BINARY), but ~6 FENCE tests still fail natively. Check whether FENCE leaves are reaching the new flat path.

## Gate confirmation (this session, post-rebase)

| Gate | Value | Source |
|---|---|---|
| GATE-1 smoke default | 13/13 | `bash scripts/test_smoke_snobol4.sh` |
| GATE-1 smoke native | 13/13 | `SCRIP_M3_NATIVE=1 bash scripts/test_smoke_snobol4.sh` |
| GATE-2 broker | 39/53 | `bash scripts/test_smoke_unified_broker.sh` |
| GATE-4 mode-2 broad | 237/280 | `bash scripts/test_interp_broad_corpus_and_beauty.sh` |
| Native broad corpus | 160/280 | `SCRIP_M3_NATIVE=1 INTERP=$(pwd)/scrip bash /tmp/test_all.sh` (head -40 patched out) |
| Rung suite | M2=19 M4=14 SKIP=0 | `bash scripts/test_snobol4_pat_rung_suite.sh` |
| Prolog smoke | 5/5 | `bash scripts/test_smoke_prolog.sh` |
| Icon smoke | 5/5 | `bash scripts/test_smoke_icon.sh` |
| Raku smoke | 5/5 | `bash scripts/test_smoke_raku.sh` |
| FACT RULE grep | 0 | `grep -rnE 'seg_byte\(SEG_CODE\|SL_B\(\|sl_emit_one\|emit_standard_blob' src/` outside templates |
| audit M3 native | GATE OK | `bash scripts/audit_m3_native_binary_arms.sh` |

## Cleanup notes

- Working trees clean on both repos (one4all + .github).
- No instrumentation left behind. The only modification this session was the 2-line gate fix.
- One small latent issue noticed but NOT touched: `bb_arbno.cpp:23` returns `bytes(1,"\\xE9")+u32le(0)+bytes(1,"\\xE9")+u32le(0)` with **double-backslash** literals (4 character string, not 1 byte). This is in the no-child fallback that my fix made unreachable in the BINARY-has-child case. The fallback path is now only reachable when `bb_child_fn == NULL` in MEDIUM_BINARY — which currently doesn't happen in any test. Leave for a separate housekeeping pass; not load-bearing.

## Authors

Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
