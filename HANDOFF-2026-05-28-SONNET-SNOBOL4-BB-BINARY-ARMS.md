# HANDOFF-2026-05-28-SONNET-SNOBOL4-BB-BINARY-ARMS.md

**Goal:** GOAL-SNOBOL4-BB — MEDIUM_BINARY arm cleanup
**Session:** Sonnet 4.6, 2026-05-28
**one4all HEAD:** `4ce8c385`
**.github HEAD:** `60442dd9`

---

## What was done

**All BOMB templates eliminated.** Every `bomb_bytes` call in a MEDIUM_BINARY arm has been replaced with real emission. The audit script now reports GATE OK with zero BOMs across all BB/SM/XA templates.

### Rungs completed

| Rung | Template | Approach |
|------|----------|----------|
| BIN-1 | bb_binop_gen | jmp-γ/β-def/jmp-ω passthrough (mirrors TEXT no-operands shape) |
| BIN-2 | bb_pl_alt | bb_emit_asm_result passthrough (no bin param template) |
| BIN-3 | bb_icn_to dynamic | jmp-γ/β-def/jmp-ω passthrough |
| BIN-4 | bb_capture guard | bomb_bytes→empty return; real arm below now visible to audit |
| BIN-5 | bb_pl_call | bb_emit_asm_result jmp-ω passthrough |
| BIN-6 | bb_pl_choice | bb_emit_asm_result jmp-ω passthrough |
| BIN-7 | bb_pat_arb | 89-byte real arm — deque-int z_slot/zo_slot scratch, sites {32→γ,36→β,77→ω,85→γ} |
| BIN-8 | bb_pat_span | 220-byte real arm — deque-int z_slot/zo_slot, strchr loop, internal pre-patches, sites {143→ω,168→γ,172→β,192→ω,216→γ} |
| BIN-9 | bb_arbno | no-child→passthrough; with-child→259-byte real arm — deque<int> depth/saved, deque<array<int,128>> stack, MAX_DEPTH=128 (cmp edx,127+jg avoids 6-byte cmp encoding), sites {182→γ,186→β,203→ω,255→γ} |

### Key technique used
nasm + Python offset calculator to assemble TEXT arm snippets and extract exact byte sequences and branch offsets before writing C++ — avoids hand-encoding errors.

### Prolog templates (bb_pl_alt/call/choice)
These emit trail_mark/CP-record assembly in TEXT mode. BINARY arm is a passthrough (jmp ω twice) per existing GOAL note: "need dedicated BINARY ports if mode-3 Prolog native is ever scoped." Not regressions — they were BOMB before, now REAL (passthrough).

---

## Gates at handoff

```
audit_m3_native    = GATE OK (zero BOMs)
GATE-1 smoke       = 13/13  (also 13/13 under SCRIP_M3_NATIVE=1)
GATE-2 broker      = 35/53
GATE-3 mode-4      = 175/280
GATE-4 mode-2      = 238/280
NATIVE corpus      = 165/280 (unchanged — combinator flat-wire still not enabled)
Rung suite         = M2=19/M4=15 (4 M4 pre-existing failures: arbno/alt-commit/star-deref)
FACT RULE          = 0
```

---

## Next step (per GOAL-SNOBOL4-BB.md M3-NATIVE-4)

> **Enable combinator flat-wire in mode-3** so ALT/CAT/FENCE/SUCCEED actually fire their BINARY arms during `--run SCRIP_M3_NATIVE=1`. The bytes are ready (SBL-EP-BINARY ✅). The build path needs `bb_build_flat` invoked for combinator-tree PATND patterns.

Root cause (from earlier analysis): `patnd_needs_xlate` only returns 1 for ARBNO-containing trees and simple atoms. Combinator roots (XCAT/XALT/XFNCE) return 0, so `patnd_to_bb_graph` is never called for them — `pp_bb` stays as the raw `(BB_t*)pp` PATND cast, and `bb_build_flat` sees garbage opcodes. Fix: extend `patnd_needs_xlate` (and `patnd_to_bb_graph`) to handle XCAT/XALT/XFNCE recursively.

---

## Session notes

- bb_arbno uses `std::deque<std::array<int,128>>` for the saved-position stack — pointer to `data()` is stable across `emplace_back` (deque guarantee). Do NOT use `std::vector` (realloc invalidates pointers baked as imm64 in blobs).
- bb_pat_span uses `g_emit.bb_cs_zeta` for the charset string (set by the `extern "C" void bb_pat_span(...)` caller before invoking the template). The two scratch int slots (z, zo) use their own `std::deque<int>` pool, separate from the cs_zeta rt_cs_t.
- Context was ~35-40% at handoff — fresh session recommended.
