# HANDOFF 2026-06-13 — Opus 4.8 — BB-FIXUP Z→A Lap 1 (bb_scan_bal)

## Session identity
Model: Claude Opus 4.8 · Goal: GOAL-BB-FIXUP-Z-to-A.md · Attended by Lon (context % each turn, "Continue" ×3)

## Repos at handoff
SCRIP @ 321888f (local==origin; rebased onto concurrent 80dc1af mid-push)
.github @ this commit (local==origin)

## Cursor at handoff
`bb_scan_any.cpp` — Z→A ring, lap 1 (advanced from bb_scan_bal; next file alphabetically before it)

## Work completed this session — 1 cursor stop

| File | Violations before → after | Key conversions | Commit |
|---|---|---|---|
| `bb_scan_bal.cpp` | 4→1* | CV6 strchr_fp local→inline cast + over_col guard→bal_admit() R2-KEEP static; CV2 ro_load_q→ROQ(4) + ro_seal_str→def/.quad/label/.string decomposition | 321888f |

*residual = bal_admit() return, counter-scope-trio sanctioned (identical to ticked bb_scan_tab 1* / bb_scan_find 2* precedent — admit-helper return counts as "returns beyond 2" in the audit but is the R2-KEEP value-computer pattern).

## Conversions applied (exactly the handoff-predicted union of the 3 scan-family patterns)
1. **fp-cast inline (CV6):** `uint64_t strchr_fp; { const char *(*fp)(const char *, int) = strchr; strchr_fp = ...; }` → `(uint64_t)(uintptr_t)(void*)(const char *(*)(const char *, int))strchr` directly in the `x86("call", "strchr", ...)` operand. Clears local_vars=1.
2. **over-col admission guard (CV6):** the 259-char inline `if (!PLATFORM_X86 || !(g_descr_flat_chain && ...))` → `static int bal_admit() { return g_descr_flat_chain && _.op_off >= 0 && _.op_name1 && _.op_name1[0] && !strchr(_.op_name1, '(') && !strchr(_.op_name1, ')'); }` + `if (!PLATFORM_X86 || !bal_admit()) return x86_bomb(...)`. Clears over_col=1, adds the one sanctioned rp residual.
3. **bypass pair decomposition (CV2):** `x86_ro_load_q("rdi", 4)` → `x86("mov", "rdi", ROQ(4))`; `x86_ro_seal_str(4, _.op_name1)` → `x86("def", L(4)) + x86(".quad", LS(4), _.op_name1) + x86("label", LS(4)) + x86(".string", _.op_name1)`. Byte-identical by construction (the .quad (sym,str) arm bakes the lit pointer in BINARY; .string is BINARY-empty). Clears bypass=2.

## Proof standard maintained
- **C2 asm-identity:** bbN/RESOLVE/.LcallN-normalized A/B diff **EMPTY** (stash baseline rebuild vs new, IR_SCAN_BAL box live in both .s).
- **Probe:** the canonical icn_scan gate bal probe — `"(a)b" ? every write(bal('b'));` → expected 4.
- **Behavior parity:** m2 (interp) = m3 (run) = m4 (compile+gcc+exec) = **4**.
- **C3 floors held every check:** smoke all-modes 2/0 · icon m2 12/12 HARD (m3/m4 10/2 tracked) · prolog m2 5/5 HARD m3=m4 5/5 · pat M4 TIER 1+2 both HARD · bin_t 0 · vstack 3 · handencoded 0 · sno_pat_reg HARD · medium_invisible WIP-baseline · prove_lower rc=0 (documented DEAD GATE, 0 cases pending IR-REDESIGN) · **icn_scan bal_b OK**.
- icn_scan 8 pre-existing FAILs (eq_match_*/augop_*) — same set the 2nd-session handoff documented, NOT introduced here, untouched per law 5.

## ⛔ PRE-EXISTING REBUS REGRESSION (NOT from this session — needs owner)
`scripts/test_smoke_compile_hello_all_langs.sh` is at **PASS=5 FAIL=1** (baseline PASS=6 FAIL=0). Failing row = **rebus** (`ROW-DRIFT rebus expected=PASS-wired got=FAIL-compile`). VERIFIED present with this session's bb_scan_bal edit stashed → it entered in the `b063b07`→`fc307d9` concurrent-commit window, NOT from the scan-bal change (which touches only the Icon IR_SCAN_BAL template and is C2-empty). Left untouched per FIXUP law 5 (never widen scope; discovered functional bug → note + handoff, untouched). Rebus is ON HOLD per PLAN, but the hello-matrix gate now drifts red on it — flagging for Lon to route to whoever owns the regressing concurrent commit.

## Next stop: bb_scan_any.cpp
Pre-audit it on arrival (`scripts/audit_bb_fixup_file.sh src/emitter/BB_templates/bb_scan_any.cpp`). If it carries the same lv/bypass/over_col union, apply the identical 3 patterns above. Probe shape: `"hello" ? write(any('h'))` (the icn_scan any_h probe, expected 2) per the sibling list.

## Outstanding verdicts (unchanged + this session)
1. rp/hc counter-scope scope-widening (exclude lambda/helper returns from count?)
2. bb_arith dead-dispatch retirement (lower-unreachable finding, 37th run)
3. nw subscript-regex widen (audit misses param-alias form)
4. bb_scan_stmt IR_SCAN_LIT/IR_SCAN_GRAPH split (2nd-session [S], still unpinned — needs Lon/coordinated session)
5. NEW: rebus hello-compile regression (concurrent-window, see above)

## Environment notes
- install_system_packages.sh required before first build (gc/gc.h)
- corpus clone required for prolog/icon/pat corpus-backed gates (icn_scan probes are inline so run without it)
- .github remote needs token re-set on clone (`git remote set-url origin https://TOKEN@...`)
