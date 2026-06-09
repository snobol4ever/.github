# HANDOFF — 2026-06-07 — Sonnet 4.6 — PROLOG-BB: M34-3 LANDED

## What landed

### M34-3: `scripts/test_gate_pl_m34_parity.sh` written and committed

SCRIP commit: `6877c61`  .github commit: `c8523aaf`

**Design — two key correctness decisions:**

1. **Temp files, not `$()` + `|| true`.**  
   `m3_out=$(run_m3 "$pl") || true; m3_rc=$?` masks all nonzero rc via `|| true`.  
   `m4_out=$(run_m4 "$pl") || true; m4_rc=$?` same.  
   Fix: write output to `mktemp` files; rc captured directly via `; m3_rc=$?` after `timeout`.

2. **m3 abort = rc=134 (SIGABRT) only. m4 abort = rc≠0 from `run_prolog_via_x86_backend.sh`.**  
   `run_prolog_via_x86_backend.sh` prints "FAIL link: …" to stdout on link error — that text  
   would pollute `m4_out` if captured. Temp file + rc check avoids both issues cleanly.

**Honest baseline: PASS=29, FAIL=75, EXCISED=11**

Dominant FAIL pattern (74 of 75): `m3 aborts rc=134, m4 outputs: X`  
→ m3's `pl_gz_admit` gate rejects the shape and SIGABRT; m4's legacy `pl_rich_body_root`  
  tier carries the rung and emits a binary that produces output (often wrong, e.g. `[] [] []`,  
  but nonzero output → not an abort → parity FAIL).

One FAIL-DIFFER (1 of 75): `rung03_unify_unify`  
→ Both exit rc=0; m3 outputs `b a` (correct); m4 outputs `[] []` (wrong).  
  Both admitted; different execution paths diverge in output. Genuine content bug.

## Gates at close

| Gate | Result |
|------|--------|
| GATE-1 m2 | **5/5 HARD** |
| GATE-1 m3/m4 | 4/5 (smoke_arith BINARY fwd-ref, pre-existing) |
| GATE-3 m2 | **114/115** (rung23_power float promotion, pre-existing) |
| GATE-3 m3 | **25**/90-FAIL (ratchet floor = 25) |
| GATE-3 m4 | **50**/55-FAIL (ratchet floor = 50) |
| PL-HY-FENCE (one-box) | PASS |
| M34-3 parity gate | Written; baseline 75 FAILs |
| g_vstack | 0 |
| seg_byte/SL_B outside templates | 0 |

## Next opener: M34-4 — DELETE `rt_last_ok` from `bb_goal.cpp`

**The 3 sites (lines 82, 99 in bb_goal.cpp):**

```
line 82:  out += x86("ins2", "call", "rt_last_ok@PLT")
          + x86("ins2", "test", "eax, eax")
          + x86("ins2", "je",   emit_fmt("%s_fail5", _.lbl_α));
          [α path: after call to callee blbl — tests if callee succeeded]

line 99:  + x86("ins2", "call", "rt_last_ok@PLT")
          + x86("ins2", "test", "eax, eax")
          + x86("ins2", "je",   emit_fmt("%s_nosol", _.lbl_α));
          [β path: after redo call — tests if redo succeeded]
```

**`rt_last_ok` internals (rt.c:644):**
```c
static int g_last_ok = 0;
int rt_last_ok(void) { return g_last_ok; }
void rt_set_last_ok(int ok) { g_last_ok = ok ? 1 : 0; }
```
A global flag — the FORBIDDEN verdict global. Per THE LAWS: verdict travels in the return
value of the emitted call, not a global. The callee (blbl / redo_lbl) returns something;
`rt_last_ok` is a side-channel that reads a global written by the C resolution engine.

**WARNING — bb_goal.cpp uses the OLD brokered env/CP engine:**  
The entire body of `bb_goal_str` calls `resolve_bb_env_save_push`, `resolve_bb_bind_arg`,
`resolve_bb_env_install`, `rt_cp_save_caller_env`, `resolve_bb_env_pop`, `resolve_cp_current`
— all from the old WAM-CP / C control engine (`resolution.c`). This box is the LEGACY
`IR_GOAL` path, NOT the GZ path. GZ-admitted programs use a different route; this template
is only reached for legacy shapes (those admitted via `pl_rich_body_root`).

**Approach for M34-4:**  
The spec says "delete rt_last_ok from bb_goal.cpp — identify the enclosing logic, replace
with return-value wiring per THE LAWS." However, `bb_goal.cpp` as a whole is legacy-coupled
(resolve_bb_env_*, resolve_cp_current, etc.) — it is NOT a GZ box. THE LAWS apply to GZ
boxes. The gate is: `grep -rn 'rt_last_ok' src/emitter/BB_templates/` == 0.

Options:
A) Simply delete the `rt_last_ok@PLT` calls and test eax logic from BOTH sites, replacing
   them with `x86_bomb("bb_goal: rt_last_ok removed — not yet replaced")` stubs per the
   LOUD stub convention. This keeps the build green, kills the gate violation, and marks
   the box as explicitly incomplete. Any legacy rung that reaches this box aborts loudly.
B) Understand what the callee's return value IS in this context and wire it correctly.
   The callee `blbl` is a C function label (from `resolve_call_block_label`) — it's part
   of the old `resolution.c` engine. Its return convention is not the GZ two-entry label
   convention. This path may not have a clean return-value to use.

Recommendation: option A — stub out with `x86_bomb`, delete the `rt_last_ok` references,
confirm gate == 0, confirm build green. Then M34-5 can assess whether to convert or delete
this whole box (since `pl_rich_body_root` is destined for deletion at GZ-FENCE anyway).

**Also note:** `rt_last_ok` is used in `IR_interp.c` (for `rt_catch_native`, m2 path) and
`unification.c` — those are NOT template files; the M34-4 gate only covers templates:
`grep -rn 'rt_last_ok' src/emitter/BB_templates/` == 0.

## Session setup for next run

```bash
cd /home/claude
git clone https://ghp_TOKEN@github.com/snobol4ever/SCRIP.git SCRIP
git clone https://ghp_TOKEN@github.com/snobol4ever/.github
cd SCRIP
bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh              # GATE-1: m2 must be 5/5 HARD
bash scripts/test_prolog_rung_suite.sh         # GATE-3: m3≥25, m4≥50, m2≥114
bash scripts/test_gate_bb_one_box.sh           # PL-HY-FENCE: PASS
bash scripts/test_gate_pl_m34_parity.sh        # M34-3: baseline 75 FAILs (NOT a blocker yet)
grep -rn 'g_vstack' src/ | wc -l              # 0
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include="*.c" --include="*.cpp" | grep -v "_templates/" | grep -v emit_core.c | wc -l  # 0
# Then do M34-4: delete rt_last_ok from bb_goal.cpp (3 sites: decl line 18, call line 82, call line 99)
# Gate: grep -rn 'rt_last_ok' src/emitter/BB_templates/ == 0
```
