# FINDING 2026-07-25 CLAUDE ICN LV-1/VV-1 — LIST-FRAME SLOTS AND SNPRINTF WERE 12.6%; THE 2-3× GAP IS STRUCTURAL

**Session:** s162 (Claude Opus 4.5). **SCRIP:** `556d9b7c` (LV-1) + `030d6263` (VV-1). **Suite: PASS=249 FAIL=12 XFAIL=32** at every step (zero regression).
**tgrlink Ir 1,496,213,586 → 1,307,176,596 = −12.63%, 1.1446×.** Wall 0.73× → 0.83× vs iconx. Output byte-identical to the s161 baseline at every step.
**RT_OPT=-O0** on every number here (FACT RULE O2-DIRECTED-ONLY; no `-O2` was used or requested).

## Method

Both rungs were measured with the DYNLINK identical-emitted-code A/B: ONE `tgrlink.o` built once, relinked against each `libscrip_rt.so`. So every delta is runtime-side; the emitted code never moved. Baseline reproduced s161's figure to within 11K Ir (1,496,213,586 vs the cursor's 1,496,224,971), confirming the tree and the corpus are the same ones s161 measured.

## LV-1 — constant-slot list-frame access (−9.76%, the big one)

`get`/`put`/`push`/`pop`/`pull` each reached the list frame BY NAME. Line-level callgrind, not intuition, found the shape:

- `FIELD_GET_fn(ld,"gen_type")` — **17,336,032 Ir over 77,393 calls = 224 Ir each.** `gen_type` is field index **2**, so `FIELD_GET_fn`'s `strcasecmp` scan pays THREE case-insensitive compares to reach it.
- `FIELD_GET_fn(ld,"frame_elems")` — 102 Ir each. Field index **0**, found on the first compare. **The 2.2× spread between these two lines is the whole diagnosis: cost tracked field POSITION, which is what proves the scan — not the call — was the expense.**

`rt_list_view` (pattern_match.c, s-LIST-SLOT-ACCESS) already solved this for the subscript sites but was `static inline` in one TU. Promoted it to `src/runtime/rt/rt_list_view.h` (own cache variable per TU, so no shared mutable state) and adopted it in the five list builtins.

**SAFETY, verified before writing any code:** `FIELD_SET_fn` is not a pure store — it calls `rt_sxt_break(val.s)` when `val.v == DT_S`. Every field these five sites write is DT_DATA (`frame_elems`) or DT_I (`frame_size`, `frame_cap`), never DT_S, so the hook cannot fire and a direct slot write is equivalent. **Each arm retains its original by-name body as the fallback when `rt_lv_is_list` declines, so the rung is zero-regression by construction, not by test.**

Result: `__strcasecmp_avx2` (100,245,297 Ir, 6.70%) and `FIELD_GET_fn` (61,938,041 Ir, 4.14%) **both left the profile's top entirely.**

## VV-1 — VARVAL_fn integer path (−3.18%)

`VARVAL_fn` cost **87,067,398 Ir over 111,601 calls = 780 Ir each**, all from ONE caller: `right()`. Its DT_I arm ran `snprintf(buf,64,"%" PRId64, v.i)` — full format-string parsing to print an integer. Replaced with direct digit conversion into the same buffer; the `rt_ws_strdup_c` allocation path is untouched, so only the format parsing was removed. INT64_MIN is handled via `(uint64_t)(-(x+1)) + 1u` (no UB on negation).

Note the pattern: 111,601 `VARVAL_fn` calls == 111,601 `right()` calls exactly. **One caller generated all of them** — the same s161 SORT-1 lesson, and the reason to check caller attribution before optimizing a high-count function.

## ⛔ NEGATIVE RESULT — DO NOT RETRY: inlining the allocation carve

`rt_gcheap_carve` runs **936,326 times** (one per allocation, ~94 Ir each with `rt_gcheap_alloc`), which looked like a 6.55% target. Tried `always_inline` on the carve PLUS an inline 8-byte-store zero loop replacing `memset` for payloads ≤ 64 bytes. Verified safe first (`total = sizeof(rt_hblk_t) + ((payload_bytes + 15) & ~15)`, so `pay` is always a multiple of 16 and `pay/8` words writes exactly `pay` bytes — no overrun into the next block's header).

**Measured +0.06% — a wash, slightly worse. Reverted; revert confirmed byte-identical Ir (1,307,176,596).**

**This is the FOURTH data point for the same rule** (s159 `-O2` 1.15×, s160 jump table 2.4%, s161 field-scan first-char guards +1.4%): at `-O0`, adding a TEST to avoid a short libc call does not pay, and `always_inline` does not recover call overhead because GCC still spills everything at `-O0`. **Only removing work outright pays** — which is exactly why LV-1 (deletes a scan) and VV-1 (deletes format parsing) both did.

## ▶ NEXT RUNG — the remaining gap is STRUCTURAL, and it is in the COMPILER

Post-LV-1/VV-1 profile, and the honest read: **the runtime-side ladder is close to exhausted.** What is left on the runtime side totals well under 10% and would land near parity, NOT at Lon's 2–3×.

**`bid_of`: 75,177,697 Ir (5.57%) over 533,135 calls — one string hash + open-addressed `memcmp` probe PER DISPATCH.** This is the clearest statement of the real problem: **the compiler knows at LOWER time exactly which builtin `get` is, throws that knowledge away, and makes the runtime re-derive it by hashing a string 533,135 times.** Same for the 22,207,870 Ir (1.64%) SNOBOL4-uppercase `switch` and the 20,259,130 Ir (1.50%) `_setjmp`, both also once per dispatch.

**The rung (s159/s160 track 1, still unstarted):** `lower_icon.c` resolves a known-builtin callee to its `BID_*` at LOWER time and the emitter passes the INTEGER, so the runtime never sees a name. `src/runtime/builtin_ids.h` already generates the name→id table this needs. **Not attempted this session for an honest reason: it changes the emitted call's argument shape, so it must land in BOTH media (`bb_call.cpp` + the `x86()` encoders) under BOTH-MEDIUM MANDATORY — a dedicated full-budget rung, and half-landing it would be worse than not starting.**

**Why no runtime rung reaches 2–3×:** `iconx` is a bytecode interpreter, and SCRIP emits native code, yet loses. That is not any one hot function — it is that **every scalar operation still round-trips through a by-name runtime call.** `IR_BINOP_ARITH` already emits a correct inline DT_I fast path (verified in the emitted `.s` this session: `add rax, rcx`), which proves the emitter CAN do this. The gap is that `get`/`put`/`right`/`integer` cannot, because they go out through `rt_call_arr`. **Until the call spine stops being by-name, the ceiling stays near parity.** `dop_direct_fp` in `bb_call.cpp` is the in-tree precedent, and operators/known builtins are safe to bind early by construction (they are not identifiers and cannot be shadowed by a user procedure or record type).

## ⚠ Corrections to the s161 cursor (measured, not assumed)

The LIVE CURSOR's "⚠ LOCAL ONLY, PUSH BLOCKED — re-push before trusting origin" is **false**. The SORT work IS on origin: hashes `2d191182`/`9a82c7e2`/`4fac8a1d` do not exist in the repo (rebased away), but `a5ece162` "ICON PERF SORT-3 (s161)" is `origin/main` and a fresh clone contains all three steps. **This is exactly the STALE-ORIENTATION rule (a): a doc asserting push state cannot be true, and was not corrected afterward. Voided.**

Also: `geddump` still diverges (11,222L vs oracle 10,145L), and `rsg`'s 2.88× remains unexplained — unchanged by this session, still not to be counted as a win.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
