# FINDING 2026-08-12g — CLAUDE-OP5 — LOWER L-3 — **INSTRUMENT FIX LANDS AND CONFIRMS THE NON-CARVING ROOT CAUSE WITH RAW (PRE-CLAMP) DATA. I ALSO RETRACT MY OWN FINDING-2026-08-12f EXTRAPOLATION THAT TAB SHARES THE SAME DEFECT — IT DOES NOT.**

**Fingerprint:** SCRIP (uncommitted at write time, committed same session) · corpus `14dc06bd` (untouched) · `.github` `3e48ea0e`. Change scope: ONE runtime diagnostic edit (`src/runtime/builtins/gen_runtime.c`), zero emitter/template/x86_asm.h bytes, zero splice arithmetic changed.

## 1. INSTRUMENT FIX — LANDED, VERIFIED NO-OP ON BEHAVIOR

Per 2026-08-12f §5, `SCRIP_REPL_TRACE` printed post-clamp. Fixed: `c_rt_match_replace` now snapshots `raw_start`/`raw_end` **before** the existing clamp and prints both alongside the clamped values; the clamp arithmetic itself is byte-for-byte unchanged. Rebuilt `libscrip_rt.so` only (no emitted-`.s` change possible — same call site, same signature — so **regen ×N is NOT triggered**, consistent with the seat's own gate text "regen ×3 iff codegen touched"). Re-ran the l3 board post-rebuild: **3 PASS / 9 FAIL-silent, identical to pre-fix** — confirms the edit is diagnostic-only.

## 2. THE NON-CARVING ROOT CAUSE IS NOW CONFIRMED, NOT JUST INFERRED

Raw (pre-clamp) values for all five `ANY('+') <prim> 'g'`-shaped members:

| probe | raw_start | raw_end |
|---|---|---|
| `span_nonterm` | 3 | 4300136 |
| `arb_nonterm` | 3 | 4300136 |
| `break_nonterm` | 3 | 4300136 |
| `rem_nonterm` | 3 | 4300136 |
| `VACUOUS_terminal_trap` | (same pattern shape) | consistent |

**All five read the identical raw_end = 4300136 — not noise, not per-run garbage, the same address every time** (deterministic arena, `ARENA_MB=1024`, `SELFLOAD=OFF`). This is exactly `head.zeta_mark`, a `PTR_GC` cell, read as a signed 64-bit cursor — direct confirmation of 2026-08-12f's claim, now from the raw wire value instead of the clamped one. 2026-08-12f's mechanism (ZLS+48/+72 correct, template resolves 16 bytes low to ZLS+32's DT_I tag and ZLS+56's GC pointer, s35's REPL-ZDEPTH correction gated on `g_zd_arm`) **stands, and is now the best-evidenced finding on this board.**

## 3. RETRACTION — TAB/RTAB DO NOT SHARE THIS DEFECT (FINDING-2026-08-12f §7.4 WAS PREMATURE)

2026-08-12f's cursor said *"TAB is plausibly this same 16-byte defect on `start` only … re-measure the moment the 16 is fixed."* That was a hedge, correctly flagged as unproven — and the raw data now falsifies it:

| probe | raw_start | want start | raw_end | want end |
|---|---|---|---|---|
| `tab_nonterm` | 2 | 0 | **14** | **14** ✅ |
| `rtab_nonterm` | 2 | 0 | **14** | **14** ✅ |
| `tab_linear3` | 3 | 0 | **7** | **7** ✅ |

**`end` is CORRECT in all three.** If TAB shared the non-carving mechanism, `end` would read `head.zeta_mark` too and show a giant pointer — it does not. `start` is wrong, but by a **shape-dependent, non-constant** amount (2, 2, 3 — not the fixed `3`/`DT_I` tag), and `--dump-zeta` confirms TAB's ZLS map is byte-identical to SPAN's (`+48`=cursor, `+56`=zeta_mark, `+72`=end) — so this is NOT "same map, same bug." Structurally: TAB's graph has fewer preceding pattern boxes than the `ANY(+)…'g'` shapes (`LEN(2) TAB(14)` = 2 match boxes vs `ANY('+') SPAN('ef') 'g'` = 3), and `op_sa` sits at a genuinely different raw displacement (192 vs 176) — so TAB's raw offsets are **not comparable** to SPAN's without TAB's own same-box-count control, which this board does not contain.

⛔ **CORRECTED VERDICT: two independent open items remain, not one.**
1. **Non-carving class (SPAN/ARB/BREAK/REM/VACUOUS) — ROOT CAUSE CLOSED**, per 2026-08-12f, now doubly confirmed. Ready for a fix attempt (un-guard `g_zd_arm`, wire `g_zd_wpop`, gate on `P8_concat_repl`).
2. **Carving class (TAB/RTAB/tab_linear3) — STILL OPEN, mechanism NOT the same as #1.** `end` correct, `start` wrong by a shape-dependent amount. s41's original "genuine Series-T displacement" framing is NOT subsumed by the REPL-ZDEPTH story and should not be discarded on the strength of this session's work. Needs its OWN control pair (a passing same-box-count sibling) before any offset claim — none exists on the current l3 board.

⚠️ **DO NOT let "fixing #1" be graded against TAB rows.** A correct fix for the non-carving class should leave `tab_nonterm`/`rtab_nonterm`/`tab_linear3` exactly as wrong as they are now (2026-08-12f's board table already knew this — the fix belongs to a different guard than TAB's).

## 4. NEXT SEAT, IN ORDER
1. Find why the replace node declines the ZD arm for the non-carving class specifically (`zd_on[i]`, `emit.cpp:2656`) — unaffected by this correction, still the right next step for item #1.
2. Land the fix via `g_zd_wpop`; gate on `P8_concat_repl` + l3 board rows `{span,arb,break,rem,VACUOUS}_nonterm` only. Expect `{tab,rtab}_nonterm` and `tab_linear3` to remain FAIL — that is not a regression.
3. Mint a same-box-count PASS/FAIL control pair for TAB (e.g., a two-box `LEN(n) LEN(m)` replace probe, no var-length primitive, to isolate TAB's true correct displacement the way `len_nonterm` isolated SPAN's) before touching the carving class at all.
4. `bal` still its own row, untouched by this session.

**UNBLOCKS:** LOWER L-3 non-carving sub-class fix-ready. Carving sub-class explicitly NOT unblocked — do not inherit 2026-08-12f's hedge as fact. **m3 only, m4 arm still BOARD's.**
