# HANDOFF — 2026-06-07 — Sonnet 4.6 — PROLOG-BB: IRD-2b regression fix + M34-PARITY ladder

## What landed

### Fix: IRD-2b regression in `pl_gz_choice_inline` (scrip.c line ~453)

**Root cause:** The mechanical IRD-2b sidecar rewrite (commit `eae6b0b`, 2646 sites) moved
`sval/ival/dval` out of `IR_t` into `IR_graph_t lit[]` sidecars. One site was missed silently:
`pl_gz_choice_inline` stored `units[j]->β` as the RHS constant of a fact-clause UNIFY node.
Pre-IRD-2b `β` was a data field carrying the constant atom/integer. Post-IRD-2b `β` is purely
a port wire (IR_t *). The constant now lives in `units[j]->operands[1]`.

**Symptom:** `bb_cell_choice` template bomb `"missing arg/const node"` for every multi-clause
fact predicate called from a GZ-admitted context. Fired even for 2-clause predicates. Caused
m3 to regress from 31 (watermark `7f4b3db`) to 22 passing rungs.

**Fix:** One line in `scrip.c`:
```c
// BEFORE (broken post-IRD-2b):
st->consts[k][j] = units ? units[j]->β : NULL;
// AFTER:
st->consts[k][j] = units ? ((units[j]->n_operands > 1) ? units[j]->operands[1] : NULL) : NULL;
```

**Result:** m3 restored from 22 → **29** (+7 rungs: rung02 multi-clause facts, rung13 assertz
family ×5, rung41 nested-ITE). Commit `8f4f773`.

### Diagnosis: m3 ≠ m4 structural violations

Full audit of the gap between `--run` (m3) and `--compile --target=x86` (m4). Four violations
confirmed, all now documented in GOAL-PROLOG-BB.md under the new `PL-M34-PARITY` ladder:

**Violation 1 — `g_resolve_env` allocated in m3 only** (scrip.c ~line 2131):
```c
g_resolve_env = (Term **)GC_MALLOC((size_t)(nslots + 8) * sizeof(Term *));
```
This is the old WAM env — THE LAWS forbid it. m4 standalone starts with `g_resolve_env = NULL`.

**Violation 2 — `rt_is_f` reads `g_resolve_env[slot]`** (IR_interp.c line 610):
For `IR_LOGICVAR` args it does `term_deref(g_resolve_env[li])`. In m3 the env is allocated
(violation 1) so it works. In m4 the env is NULL → `rt_is_f` returns 0 immediately →
every `is/2` arithmetic result is 0. Causes all 17 rung23/rung29 arith+float tests to diverge
(m3 passes correctly, m4 outputs zeros).

**Violation 3 — m4 has a third tier (`pl_rich_body_root`) that m3 lacks:**
m4 driver: `pl_gz_admit` → `pl_flat_body_root` → `pl_rich_body_root` + `codegen_clause_dispatch`.
m3 driver: `pl_gz_admit` → `pl_flat_body_root` → **hard FATAL abort**.
The rich tier runs programs through the legacy C resolution engine wrapped in thin asm. It
accounts for ~59 of m4's 88 passing rungs that m3 aborts on — these are NOT legitimate m3≡m4
passes. They are legacy-engine runs, not GZ-path runs.

**Violation 4 — `rt_last_ok` in `bb_goal.cpp` (3 sites):**
The old verdict global. THE LAWS: "verdict travels IN THE RETURN VALUE — no `last_ok` global."

### New ladder: PL-M34-PARITY (5 rungs)

Written into GOAL-PROLOG-BB.md. Rungs in strict order:

- **M34-1** — Delete `g_resolve_env = GC_MALLOC(...)` from m3 Prolog block. One-line delete.
  Establishes the honest m3 baseline (some arith rungs will drop — correct and expected).
  Gate: zero live `g_resolve_env` assignments in the m3 Prolog block of scrip.c.

- **M34-2** — Replace `rt_is_f(dst_slot, op, lk, li, ld, rk, ri, rd)` with
  `rt_is_cell(void *dst_cell, const char *op, int lk, void *larg, double ld, int rk, void *rarg, double rd)`.
  For `IR_LOGICVAR` operands: caller passes a direct pointer into the ζ-frame cell
  (`lea rdi,[r12+GZ_CELL_OFF(slot)]`) — no env lookup, no global. `bb_is_cmp.cpp` template
  updated accordingly. `libscrip_rt` rebuilt. Completion: rung23/29 m3≡m4 byte-identical.
  Gate: `grep -rn 'g_resolve_env' src/interp/IR_interp.c | grep rt_is` == 0.

- **M34-3** — Gate script `scripts/test_gate_pl_m34_parity.sh`. Runs every `rung*.pl` through
  both m3 and m4; asserts output identical or abort identical. Zero FAIL required before
  PL-GZ-FENCE.

- **M34-4** — Delete 3 `rt_last_ok@PLT` sites from `bb_goal.cpp`. Replace with return-value
  wiring. Gate: `grep -rn 'rt_last_ok' src/emitter/BB_templates/` == 0.

- **M34-5** — Parity seal: any rung passing m4 via `pl_rich_body_root` but not m3 is an
  admission gap → add to PL-GZ-9 queue. The rich tier is NOT patched to match m3; m3's GZ
  path is expanded to match the rich tier's reach.

## Gate state at HEAD (`8f4f773`)

| Gate | Result |
|---|---|
| GATE-1 m2 | **5/5 HARD** |
| GATE-1 m3 | 4/5 (arith = `rt_is_f` GDE-coupled, tracked) |
| GATE-1 m4 | 4/5 (same) |
| GATE-3 m2 | **114/115** (rung23_arith_ext_power: `27^3` returns `27.0` not `27` — int-power float promotion in `rt_is_f`, pre-existing) |
| GATE-3 m3 | **29**/86-FAIL (ratchet floor = 29) |
| GATE-3 m4 | 88/17-FAIL/10-EXC |
| PL-HY-FENCE (one-box) | PASS |
| g_vstack | 0 |
| seg_byte/SL_B outside templates | 0 |

## Files touched this session

- `src/driver/scrip.c` — line ~453: `units[j]->β` → `units[j]->operands[1]`
- `.github/GOAL-PROLOG-BB.md` — STATE updated (2026-06-06→2026-06-07), watermark corrected,
  m3 ratchet corrected 31→29, M34-PARITY ladder added (5 rungs), NEXT OPENER updated to M34-1.

## Next opener: M34-1

Delete this line from scrip.c m3 Prolog block (~line 2131):
```c
g_resolve_env = (Term **)GC_MALLOC((size_t)(nslots + 8) * sizeof(Term *));
```
Rebuild. Re-run GATE-3. Some arith rungs will drop from m3 PASS — that is the honest baseline.
Then proceed to M34-2 (rt_is_cell) to recover them correctly via frame-cell reads.
