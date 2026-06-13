# HANDOFF 2026-06-13 — Sonnet 4.6 — BB-FIXUP Z→A Lap 1 (bb_scan_any)

## Session identity
Model: Claude Sonnet 4.6 · Goal: GOAL-BB-FIXUP-Z-to-A.md · Attended by Lon (context ~75-80% at handoff, "Perform hand off")

## Repos at handoff
SCRIP @ 55f5432 (local==origin)
.github @ this commit (local==origin)

## Cursor at handoff
`bb_return.cpp` — Z→A ring, lap 1 (advanced from bb_scan_any; next file alphabetically before it)

## Work completed this session — 1 cursor stop

| File | Violations before → after | Key conversions | Commit |
|---|---|---|---|
| `bb_scan_any.cpp` | 3→0 CLEAN | CV6 strchr_fp local→inline cast; CV2 ro_load_q→ROQ(0); CV2 ro_seal_str→def/.quad/label/.string decomposition | 55f5432 |

## Conversions applied
1. **fp-cast inline (CV6):** `uint64_t strchr_fp; { const char *(*fp)(const char *, int) = strchr; strchr_fp = (uint64_t)(uintptr_t)(void *)fp; }` → `(uint64_t)(uintptr_t)(void*)(const char *(*)(const char *, int))strchr` directly in the `x86("call", "strchr", ...)` operand. Clears local_vars=1.
2. **bypass: ro_load_q (CV2):** `x86_ro_load_q("rdi", 0)` → `x86("mov", "rdi", ROQ(0))`. Byte-identical: ROQ(0) parses XK_ROSLOT → line 569 of dispatcher → x86_ro_load_q("rdi", 0). Clears bypass count.
3. **bypass: ro_seal_str (CV2):** `x86_ro_seal_str(0, _.op_name1)` → `x86("def", L(0)) + x86(".quad", LS(0), _.op_name1) + x86("label", LS(0)) + x86(".string", _.op_name1)`. Byte-identical: .quad (sym,str) arm bakes lit pointer in BINARY; .string is BINARY-empty — matches x86_ro_seal_str(0, lit) exactly in both media. Clears bypass count.

**No admit-helper needed** (bb_scan_any has no over_col; the inline admission guard fits on one line, unlike bb_scan_bal's 259-char bracket-check that required bal_admit()). Result: fully CLEAN with no residual.

## Proof standard maintained
- **C2 asm-identity:** bbN/.LxN-normalized A/B diff **EMPTY** (baseline compiled, stash-equivalent rebuild diff run; IR_SCAN_ANY box live in both .s).
- **Probe:** `"hello" ? write(any('h'))` (icn_scan any_h probe, expected 2).
- **Behavior parity:** m2 (interp) = m3 (run) = m4 (compile+as+gcc+exec) = **2**.
- **C3 floors held:**
  - icon smoke m2: 12/12 HARD (m3/m4 10/2 tracked, proc_zeroarg/proc_recursion pre-existing)
  - icn_scan: any_h OK · bal_b OK · 8 inherited FAILs (eq_match_*/augop_*) unchanged
  - snobol4 smoke: 7/7/7 HARD
  - prolog: m2 5/5 HARD · m3 5/5 · m4 5/5
  - pat suite M2/M3/M4: 19/0 all
  - sno_pat_reg: HARD OK (r10 refs 0)
  - bin_t: 0 · handencoded: 0 · vstack: 3
  - medium_invisible: 84 ≤ 103
  - prove_lower: rc=0 (documented dead gate)
  - all-langs hello: PASS=5 FAIL=1 (rebus pre-existing concurrent-window regression — not mine)
- **C4 rank:** bb_scan_any CLEAN (3→0), GRAND ↓3, no growth elsewhere.
- **C5:** single commit 55f5432 to SCRIP, cursor-advance in same .github commit.

## ⛔ PRE-EXISTING REBUS REGRESSION (carry-forward, NOT from this session)
`scripts/test_smoke_compile_hello_all_langs.sh` at **PASS=5 FAIL=1**. Failing row = **rebus** (`ROW-DRIFT rebus expected=PASS-wired got=FAIL-compile`). First documented by Opus 4.8 bal-handoff (concurrent b063b07→fc307d9 window). Rebus is ON HOLD per PLAN; regression needs routing to whoever owns the concurrent commit.

## Next stop: bb_return.cpp
Pre-audit on arrival: `bash scripts/audit_bb_fixup_file.sh src/emitter/BB_templates/bb_return.cpp`
Read the file, check what conversions are flagged, apply the applicable CV1–CV10 set, run per-file checks (C1–C5).

## Outstanding verdicts (unchanged from bal-handoff)
1. rp/hc counter-scope scope-widening (exclude lambda/helper returns from count?)
2. bb_arith dead-dispatch retirement (lower-unreachable finding, 37th run)
3. nw subscript-regex widen (audit misses param-alias form)
4. bb_scan_stmt IR_SCAN_LIT/IR_SCAN_GRAPH split ([S] unpinned — needs Lon/coordinated session)
5. rebus hello-compile regression (concurrent-window, see above)

## Environment notes
- `bash scripts/install_system_packages.sh` required before first build
- corpus clone required for prolog/icon/pat corpus-backed gates; icn_scan inline probes run without it
- libscrip_rt.so is at `out/libscrip_rt.so` (not repo root) — use `-L/home/claude/SCRIP/out`
