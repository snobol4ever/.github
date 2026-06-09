# HANDOFF — 2026-06-08 — Sonnet 4.6 — PROLOG-BB: M34-2 LANDED

## What landed

### M34-2 complete: `rt_is@PLT` / `rt_is_lint@PLT` TEXT arms replaced

**Root cause (from prior session):** The three TEXT arms in `bb_is_cmp.cpp` for integer-only
`is/2` shapes called `rt_is@PLT` and `rt_is_lint@PLT`. Both delegate to `rt_arith()` which
reads `g_resolve_env[slot]` for IR_LOGICVAR operands. In m4 standalone (GZ-admitted procs)
`g_resolve_env` is NULL → every integer arithmetic result is 0 → outputs `[]`.

**Fix — three TEXT arms replaced (bb_is_cmp.cpp):**

| Arm | LHS type | RHS type | Old call | New call |
|-----|----------|----------|----------|----------|
| Binary | IR_LOGICVAR | IR_ARITH (binary) | `rt_is@PLT` | `rt_is_cell@PLT` |
| Lit-dst | IR_LIT_I | IR_ARITH (binary) | `rt_is_lint@PLT` | `rt_is_cell_lit@PLT` |
| Unary | IR_LOGICVAR | IR_ARITH (unary) | `rt_is@PLT` | `rt_is_cell@PLT` |

All arms: `sub rsp,8` / `add rsp,8` for 16-byte ABI alignment. `icm_arg_load_lit` for
operands: `lea rcx,[r12+GZ_CELL_OFF(slot)]` for IR_LOGICVAR, `mov rcx,value` for IR_LIT_I.
`xmm0=0.0` (ld), `xmm1=0.0` (rd) — no float in these arms.

**`rt_is_cell` op table completed (IR_interp.c):**
- Binary: `+`, `-`, `*`, `/`, `**`, `^`, `min`, `max` (pre-existing) + added `//`, `mod`,
  `rem`, `div`, `gcd`, `/\`, `\/`, `xor`, `>>`, `<<`
- Unary: `-`, `+`, `abs`, `sign`, trig family, float-conv family (pre-existing) + added
  `\` (bitwise NOT), `msb`

**New function `rt_is_cell_lit` (IR_interp.c + bb_common.h):**
Same LOGICVAR/LIT_I operand dispatch as `rt_is_cell`. Computes integer result, compares
with `lval`. Returns 1 iff equal. No cell write, no trail. Handles all the integer ops.
Used for `N is Expr` where N is a literal (e.g. `0 is X mod 2`).

## Gates at close

| Gate | Result |
|------|--------|
| GATE-1 m2 | **5/5 HARD** |
| GATE-1 m3 | 4/5 (smoke_arith: BINARY path unresolved-fwd-ref, pre-existing) |
| GATE-1 m4 | 4/5 (same) |
| GATE-3 m2 | **114/115** (rung23_power `27^3` float promotion, pre-existing) |
| GATE-3 m3 | **25**/90-FAIL (ratchet floor = 25, was 23) |
| GATE-3 m4 | **50**/55-FAIL (ratchet floor = 50, was 45) |
| PL-HY-FENCE (one-box) | PASS |
| g_vstack | 0 |
| seg_byte/SL_B outside templates | 0 |
| `g_resolve_env` in IR_interp.c \| grep rt_is | 0 ✓ |
| `rt_is@PLT\|rt_is_lint@PLT` in bb_is_cmp.cpp | 0 ✓ |

## Newly passing rungs

**m4 (+5):** rung23_sign, rung23_power, rung23_max_min, rung23_bitwise, rung29_gcd
**m3 (+2):** rung23_truncate, rung23_sign (via BINARY path, already had rt_is_cell; the
  TEXT arm completion closed some previously-open BINARY-path shapes)

## Files touched

- `src/emitter/BB_templates/bb_is_cmp.cpp` — three TEXT arm rewrites
- `src/emitter/BB_templates/bb_common.h` — added `rt_is_cell_lit` declaration
- `src/interp/IR_interp.c` — `rt_is_cell` op table completed; `rt_is_cell_lit` added
- `.github/GOAL-PROLOG-BB.md` — STATE updated 2026-06-07→2026-06-08, M34-2 checked,
  PL-GZ-9 m3 ratchet updated 29→25 (honest post-M34-1 baseline), m4 ratchet 45→50

## Next opener: M34-3

Write `scripts/test_gate_pl_m34_parity.sh`:
- For each `rung*.pl` in corpus, run m3 (`--run`) and m4 (`run_prolog_via_x86_backend.sh`)
- Compare stdout: if one side has output and other aborts → FAIL; if outputs differ → FAIL;
  if both abort → EXCISED (not a failure)
- Gate: zero FAIL before PL-GZ-FENCE

After M34-3 establishes the honest baseline, proceed to M34-4 (`rt_last_ok` deletion
from `bb_goal.cpp`).

## Session setup for next run

```bash
cd /home/claude
git clone https://ghp_TOKEN@github.com/snobol4ever/SCRIP.git SCRIP
git clone https://ghp_TOKEN@github.com/snobol4ever/.github
cd SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_smoke_prolog.sh          # GATE-1: m2 must be 5/5 HARD
bash scripts/test_prolog_rung_suite.sh     # GATE-3: m3≥25 m4≥50 m2≥114
bash scripts/test_gate_bb_one_box.sh       # PL-HY-FENCE: PASS
grep -rn 'g_resolve_env' src/interp/IR_interp.c | grep rt_is   # must be 0
grep -n 'rt_is@PLT\|rt_is_lint@PLT' src/emitter/BB_templates/bb_is_cmp.cpp  # must be 0
# Then write scripts/test_gate_pl_m34_parity.sh (M34-3)
```
