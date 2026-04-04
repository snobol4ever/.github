# MILESTONE-WASM-ARTIFACTS — WASM artifact parity + emit-diff gate

**Session:** SW (SNOBOL4 WASM) — parked but artifact gate is infrastructure
**Status:** ✅ COMPLETE — 2026-04-01 SJ-8 addendum

---

## Goal

Generate `.wat` artifacts for all corpus crosscheck tests and wire
`snobol4_wasm` into `run_emit_check.sh` — same pattern as `.s`/`.j`/`.il`/`.js`.

---

## Situation before

- 27 of 179 `.sno` files had `.wat` alongside (hello, rung2–4, rungW* only)
- `run_emit_check.sh` had no WASM support at all (`snobol4_wasm` not a valid CELLS value)
- WASM emit-diff gate: **0/0** (not wired)

---

## Work done

1. Generated `.wat` for all 175 compiling tests (`scrip-cc -wasm`)
2. 4 `library/` tests fail to compile (same as JS/all backends — known issue)
3. Wired `snobol4_wasm` into `run_emit_check.sh`:
   - `_want_sno_wasm` flag
   - CELLS dispatch: `snobol4_wasm` → `_want_sno_wasm=1`
   - regen: `-wasm wat` line in UPDATE block
   - check: `-wasm wat` line in check_one dispatch
4. Emit-diff gate: **175/0** ✅

---

## Gate

```bash
cd /home/claude/one4all
CELLS=snobol4_wasm CORPUS=/home/claude/corpus bash test/run_emit_check.sh
# expect: 175/0
```

---

## Notes

- WASM session (SW) is parked — but artifact gate is shared infrastructure
- Same 4 `library/` compile failures as all other backends
- `.wat` files are WebAssembly Text format — human-readable, version-controlled
- When WASM session resumes, emit-diff will catch regressions automatically

---

*MILESTONE-WASM-ARTIFACTS.md — completed SJ-8 addendum, 2026-04-01*
