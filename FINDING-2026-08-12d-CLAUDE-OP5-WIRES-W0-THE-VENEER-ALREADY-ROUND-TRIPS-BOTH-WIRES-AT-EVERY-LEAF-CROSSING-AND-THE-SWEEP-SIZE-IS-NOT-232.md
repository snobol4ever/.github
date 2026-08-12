# FINDING — WIRES W-0: the RTCC veneer ALREADY round-trips BOTH wires at every leaf crossing, the bare crossings are prologue-only, and the "232-occurrence sweep" is not 232 units of work

**Seat:** WIRES (`GOAL-SN4-HOME-WIRES.md`), rung W-0 (CLAIM SWEEP, HONEST).
**Session:** 2026-08-12, Opus 5. **Trees:** SCRIP `52545cbf` · corpus `c91d1adf` · x64 `5035571` (fresh clones, canonical paths).
**Compiler bytes changed: ZERO.** One new script (`scripts/test_census_wreg_artifacts.sh`), census only.

---

## 1. THE SOURCE GATE REPRODUCES — AND MIS-SIZES THE WORK

`test_gate_wreg_claim.sh` at HEAD: templates+emitter **26 files / 199 lines / 232 occurrences**; RTX hand asm **10 files / 182 lines / 223 occurrences**; quoted-spelling drift 130 vs the design's 178 at `bce9a4b0`.

**The 232 is not 232 units of work.** It is at least four classes with opposite meanings, and the gate sums them:

| class | evidence | meaning |
|---|---|---|
| **PRESERVERS** (~52 occ) | 13 × `bb_scan_*.cpp`, each `push r10` / `call` / `pop r10` bracketing a C crossing | ⛔ **the CURE, counted as the disease.** A seat driving the number to 0 would DELETE the saves that make wires survive crossings |
| **DECODER NOISE** | `x86_asm.h:46,47,57` — `strcmp(r,"r10")` in the name→number mapper | not a use of r10 at all; it is the machinery that encodes *every* register |
| **COMMENT NOISE** | `x86_asm.h:281-284` | the gate's comment-stripping does not reach these block comments |
| **GENUINE SCRATCH** | `bb_call_fn.cpp` 93 occ · `xa_flat.cpp` 25 · `bb_var.cpp:19` (PL-ZK-5B dual-write uses both regs as copy scratch) | the real sweep |

⛔ **INSTRUMENT-TRUTH DEFECT: the whitelist is EMPTY and the licensed sites already exist.** The gate prints *"licensed: 0 lines / 0 occurrences — whitelist is empty until WREG-1 creates the glue emitters."* But the glue emitters **are in the tree**: `emit.cpp:2687` (W-MAP(3) res landing, reloads both wires), `:2720-2722` (pass-thru suspension record `{res,r10,r11,pad}`, 32B, wires saved per-activation on the spine), `:2737` (CLASS D ω = `jmp r11`). Six licensed occurrences are sitting in the SWEEP column. Populate `wreg_claim_whitelist.txt` from those three sites before anyone reads the burn-down as debt.

## 2. THE SCAN FAMILY PRESERVES rΓ AND NEVER PRESERVES rΩ

Mechanical, whole-family: **26 `push r10`, 0 `push r11`.**

```
bb_scan_{alternate,any,bal,find,many,move,sequence,tab,upto}  push_r10=2  push_r11=0
bb_scan_match                                                 push_r10=4  push_r11=0
```

Each bracket wraps a libc/`rt_` crossing (e.g. `bb_scan_any.cpp:22-25` around `call strchr`). Today this is pre-existing scratch preservation and harmless. **At W-5 it becomes an asymmetry:** if both registers are live wires, every one of these sites protects γ and abandons ω. ⛔ Not a conviction — a NAMED PREDICTION for the flip, to be witnessed, not assumed.

## 3. NEW INSTRUMENT — THE ARTIFACT HALF W-0 ASKED FOR

`scripts/test_census_wreg_artifacts.sh` (self-testing per the s15b law; `-M intel`; counts **WRITES**, not mentions, because a read is harmless to a wire and a write destroys it).

Shipped runtime `out/libscrip_rt.so`: **173 r10/r11 writes total.** Split honestly:
- **`rt_*` C runtime — 38 symbols / 94 writes.** These execute while emitted code is on the stack ⇒ a live wire is exposed. Top: `rt_subscript_var` 9 · `rt_defer_close` 9 · `rt_coerce_num2_d` 8 · `rt_match_replace` 6.
- **compile-time C++ — 10 symbols / 12 writes.** HARMLESS.

⛔ **SELF-CORRECTION, SAME SEAT:** the script's first heuristic bucketed "match-time" by symbol NAME (`/match|scan|pat/`). That caught `bb_match_defer[abi:cxx11]()` and `bb_scan_bal[abi:cxx11]()` — **compile-time template functions returning `std::string`**, whose r10 writes are g++'s own allocation and cannot touch a wire. `nm -C` settles it in one command. The filter is now `^rt_` and the false-positive class is documented in the script header.

## 4. ⭐⭐⭐ THE CENTRAL RESULT — THE VENEER IS ALREADY CORRECT AT LEAF CROSSINGS

Emitted text, measured (not read): writeback before the crossing is
`mov [rax+56], r10` · `mov [rax+64], r11`; reload after is
`mov r11, [rip+g_rtcc_block@GOTPCREL]` · … · `mov r10, [r11+56]` · `mov r11, [r11+64]`.

**r11 is restored LAST**, exactly as `x86_asm.h:281-284` specifies, so the block base stays valid for every prior restore. Counts are **balanced 14/14** on the `ANY` probe. Across 15 BB probes: **172 crossings VENEERED**, including `rt_match_enter` **15/15**, `rt_dcap_step` 30, `rt_match_ctx_restore` 30, `NV_SET_fn` 31.

**The only BARE crossings are `core_lib_init` (15), `gva_register` (15), `rt_gva_island` (15) and `exit` (30)** — program prologue and termination, where no wire can be live.

⇒ **The wires already survive every leaf C crossing.** The exposure named in W-0's charter is not where the raw 173/94 numbers point.

⛔ **SELF-CORRECTION #2, SAME SEAT — A VOIDED TABLE.** An intermediate scan of mine reported `rt_match_enter` BARE in 10 of 15 probes. **That table is VOID and must not be carried forward.** Cause: `for (n in calls)` yields awk array keys as **STRINGS**, so the lookback guard `i < n` compared `"92" < "104"` **lexicographically** and the loop body never ran. Fix is `n = k+0`. Verified by direct per-site inspection (F06: single site at line 104, writeback at 102) and by deterministic recompile (`cmp` identical). ⭐ This is the s14/s15b instrument-units conviction in a third costume, committed by the seat that had just read the header warning about it. **Rule earned: a scanner reports a class only after one member of that class is confirmed BY HAND.**

## 5. WHERE THE REAL EXPOSURE IS — AND IT IS W-6, EXACTLY AS WRITTEN

`g_rtcc_block` is **ONE FLAT BLOCK at fixed offsets** (r10→+56, r11→+64). A leaf crossing is safe with a flat cell. A **RE-ENTRANT** crossing is not: any `rt_*` that re-enters emitted code (deferred evaluation, `rt_dcap_step`, `rt_proc_open_fn`, a user function called from inside a pattern) makes the INNER writeback overwrite the OUTER saved wires at the same two offsets. The outer γ/ω are then destroyed on return.

**This is the same single-cell disease this project has convicted three times already** — `g_blob_ctx`, `g_zctx`, `g_star_peek` (the DEFER-LATCH pool item). W-6's wording is exact and now has a measurement behind it: *"The veneer round-trips wires on leaf crossings only; fix the re-entrant case."* The cure is the shape `emit.cpp:2720` already uses for the suspension record — **per-activation on the FORTH spine**, never a flat block (s14 arbitration; the same reasoning that killed a flat `g_rtcc_block[32]` as a wire home).

⛔ **NOT YET WITNESSED.** A nested-crossing witness (a deferred fn call inside a pattern that itself crosses) is the missing evidence. Candidates already named in the plan: `140_pat_eval_double_fn_trick` / `141_pat_eval_double_fn_arbno`.

## 6. ENCODER LANDMINE SPECIFIC TO r10

`x86_asm.h:1713` — an operand parsing as `XK_R10MIR` dispatches to `x86_store_cursor_mirror()`, which emits `mov [r10], r14d` (binary `0x45 0x89 0x32`). **Writing `[r10]` in a template silently produces a STORE THROUGH r10**, not an addressing mode. Two templates already carry hand-written workarounds:
- `xa_flat.cpp:249` — `[r10 + 0]` "to avoid XK_R10MIR parse"
- `bb_call_fn.cpp:372` — comment records the same hazard

This is the raw-byte-encoder risk LADDER WREG named as its only fallback trigger, and it is live. Any W-3/W-5 template touching `[r10]` must use `[r10 + 0]` or the encoder must be taught to disambiguate.

---

## NEXT SEAT, IN ORDER

1. **Populate `wreg_claim_whitelist.txt`** from `emit.cpp:2687/2720/2737`; re-run the gate so `licensed` is non-zero and the burn-down is honest. Cheap, no compiler bytes.
2. **W-6 nested-crossing witness** — compile `140`/`141`, count writeback/reload pairs on a re-entrant path, show the inner pair overwriting the outer. That converts §5 from prediction to conviction.
3. **W-1 (ZCTX scratch)** is unaffected by any of this and remains runnable; W-2's push/pop guard pair is the D12/D13 regression owner.
4. The `push r10` / no-`push r11` asymmetry (§2) is a **flip-time** item — record it on W-5, do not "fix" it now against a register that is not yet a wire.
5. ⛔ Do not drive the 232 to zero. Classify first; ~52 of it is the preservation discipline W-3 mandates.
