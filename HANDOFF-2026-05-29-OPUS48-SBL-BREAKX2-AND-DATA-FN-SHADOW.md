# HANDOFF 2026-05-29 Opus 4.8 — SBL-BREAKX-2 + SBL-DATA-FN-SHADOW

**Goal:** GOAL-SNOBOL4-BB. **Base:** SCRIP `5d5cede1`. **Result:** native 245 → 250 (+5), zero regression.

## Two fixes

### 1. SBL-BREAKX-2 (BB_template BINARY arm — FACT-pure)
`src/emitter/BB_templates/bb_pat_break.cpp` — the BREAKX (`is_breakx`, `pBB->ival==1`)
MEDIUM_BINARY arm was a 2-jump stub with malformed sites `{1,2}`: the patcher consumed
the second `E9` opcode, landing a rel32 at output offset 19 against an empty-named label
→ `bb_emit_end: unresolved forward reference site=19 label=''` → SIGABRT on **every**
native BREAKX.

Replaced with a real 302-byte α-scan + β-rescan blob:
- **α** (shared shape with plain BREAK): scan from Δ counting z until subject[Δ+z] ∈ cset;
  end → jmp ω; found → Δ += z, jmp γ.
- **β** (the BREAKX-specific retry): recover `z_orig = Δ − z` arithmetically (no second
  persistent slot — plain-BREAK's note that Δ is read fresh each loop applies), step past
  the break char (`z++`), rescan to the NEXT cset char: jmp γ on found, jmp ω on exhausted.
- `z` persists in `[zeta+8]` (the `rt_cs_t` delta field), matching the plain-BREAK convention.

Method: wrote the intended GAS, assembled with `as`, read exact bytes+offsets via objdump,
transcribed mechanically into `bytes()`/`u64le()`/`u32le()` (all bytes inside the template).
Sites (stream order): γ(139)/ω(144)/β-DEF(148)/γ(293)/ω(298), is_def {F,F,T,F,F}.

Native +2: `W05_breakx`, `word4` (word4 exercises BREAKX mid-pattern with REM+SPAN
backtracking into β — byte-exact vs ref). Oracle + mode-4 TEXT arm untouched.

### 2. SBL-DATA-FN-SHADOW (native dispatch ordering)
`src/runtime/rt/rt.c` + `src/runtime/snobol4/snobol4.c` — native `rt_call` consulted the
**ungated** cross-language `icn_try_call_builtin_by_name` table (intentionally ungated to
serve Raku/Icon `write`, `writes`, `integer`, `image`, list ops) BEFORE the SNOBOL4
`INVOKE_fn`. Icon has a `real()` builtin, so a SNOBOL4 `real(X)` on a
`DATA('complex(real,imag)')` object was intercepted by Icon's `real` (fails on `DT_DATA`)
instead of reaching the DATA field accessor. `imag` worked only because Icon has no `imag`.

Evidence chain: `imag(3.5)` no-DATA → Error 5 (undefined; APPLY_fn is case-sensitive);
`real(3.5)` no-DATA → 3.5 (Icon `real`); fields renamed `real,imag`→`rrr,iii` → native
passes; `foo,bar` DATA → passes. So the only failure mode is a field name colliding with
an Icon builtin.

Fix: exported `int sno_fn_registered(const char *)` in snobol4.c (case-sensitive
`_func_buckets` presence check — like `fn_has_builtin` but without the `fn!=NULL` filter,
so user-DEFINE bodies count too) and wrapped the icn fallback in rt.c with
`if (!sno_fn_registered(name)) { ...icn... }`. A registered SNOBOL4 fn (user `DEFINE` or
`DATA` accessor) now shadows any cross-language builtin and reaches its home dispatcher
(`INVOKE_fn`); unregistered names (Icon/Raku `write`, Icon `real` without a SNOBOL4 DATA
def) are unaffected. This aligns native with the mode-2 oracle (which already prefers the
registered fn).

Native +3: `094_data_define_access`, `811_size` (SIZE/`size` shadow, same class),
`match_driver` — all byte-exact.

## Gates (all green)
- Native broad corpus 245 → 250 (+5), zero regressions (exact FAIL-set diff)
- GATE-1 smoke 13/13 (both modes)
- Rung suite M2=19/0, M4=18/1 (053_pat_alt_commit pre-existing)
- GATE-2 broker 44
- Cross-language smokes: icon/prolog/raku/snocone/snobol4 = 5/5/5/5/13 (icn path touched → verified)
- FACT RULE = 0 · audit_m3_native = GATE OK

## Files
- `src/emitter/BB_templates/bb_pat_break.cpp` (BREAKX BINARY arm + sites + comment)
- `src/runtime/rt/rt.c` (icn-fallback guard)
- `src/runtime/snobol4/snobol4.c` (`sno_fn_registered`)
- `.github/GOAL-SNOBOL4-BB.md`, `.github/PLAN.md`

## Next session (native-only gaps, oracle-pass / native-fail)
- **1010_func_recursion SEGV — BISECTED:** plain recursion is fine native (`fact(5)`→120).
  TWO distinct native-dispatch sub-bugs, each isolated:
  (a) OPSYN-alias recursion — `OPSYN(.facto,'fact'); facto(4)` SIGSEGVs (register_fn_alias
      path under recursive native call);
  (b) alternate entry point — `DEFINE('fact2(n)', .fact2_entry)` + recursive call SIGSEGVs
      (DEFINE_fn_entry / entry-label≠name native dispatch).
  gdb each in isolation; likely the native call/return frame setup for aliased / alt-entry fns.
- 1016_eval SEGV; 1013 NRETURN-lvalue / 1011 redefine / 1017 arg_local (oracle gaps too).
- Mode-4 BREAKX TEXT arm: already correct; not re-gated (mode-4 deferred per Lon).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet · Claude Opus
