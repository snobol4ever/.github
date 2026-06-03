# HANDOFF 2026-06-03 (Opus 4.8) — Prolog PL-HY-FENCE: test_gate_bb_one_box.sh authored + wired

## TL;DR
PL-HY-FENCE — the one remaining actionable piece of the BB-HYGIENE ladder per the morning audit
(`HANDOFF-2026-06-03-OPUS48-PROLOG-BB-HY-LADDER-AUDIT.md`) — is DONE. Authored
`scripts/test_gate_bb_one_box.sh` (SCRIP `1a0127e`, pushed): asserts ONE box per Prolog template file.
The property already held; the gate makes it enforced. **SCRIP HEAD `1a0127e`.** GATE-3 byte-identical
to baseline. `.github` updated (FENCE marked `[x]`, gate wired into Session Setup, gate-table caption).

## What landed (SCRIP `1a0127e`)
`scripts/test_gate_bb_one_box.sh` — for each Prolog-OWNED box file
(`bb_arith/atom/builtin/catch/choice/conj/cut/disj/fail/goal/ite/logicvar/unify.cpp`) assert EXACTLY ONE
`extern "C" void bb_*(…)` entry; for each `bb_builtin_*.cpp` helper assert ZERO (they are `_str` helpers
behind the `bb_builtin.cpp` router — exempt, mirroring how `bb_binop_*.cpp` sits behind `bb_binop`).
Comments stripped with `perl -0777` (same idiom as `test_gate_no_bb_bin_t.sh` / `test_gate_pl_no_value_stack.sh`).
File lists are explicit (not a glob) so a new Prolog box must be added deliberately — and a stray second
box in any existing file trips immediately.

## Verification
- Gate **PASS** from clean HEAD.
- **Two proven negatives** (each restored clean):
  - appended a 2nd `extern "C" void bb_cut_fake(...)` to `bb_cut.cpp` → `FAIL: … has 2 … (expected exactly 1)`, exit 1.
  - appended `extern "C" void bb_builtin_io(...)` to the helper `bb_builtin_io.cpp` → `FAIL: helper file … has 1 … (expected 0)`, exit 1.
- GATE-1 smoke **m2 5/5**, m3 4/5 (known `unify` harness artifact), m4 5/5.
- GATE-3 rung suite **m2 111/111 · m3 111/111** byte-identical · **m4 75 / 0 FAIL / 36 EXCISED** — unchanged baseline.
- FACT greps: `seg_byte(SEG_CODE`/`SL_B(` outside templates **0**; `g_vstack` **0**.

## FACT-RULE integrity (verified, untouched)
No template / runtime / FACT-RULE code touched. Confirmed byte-identity across siblings:
- NO-VALUE-STACK block: identical across GOAL-PROLOG/SNOBOL4/ICON (`cba1c10d…`).
- NO-C-BYRD-BOX block: identical across all five GOAL-PROLOG/SNOBOL4/ICON/RAKU/SNOCONE-IR (`5e81271…`).
`.github` diff to `GOAL-PROLOG-BB.md` is exactly 3 Prolog-only regions (FENCE ladder line, Session-Setup
gate list +1 line, gate-table caption) — 3 insertions / 2 deletions. No FACT block in the edit window.

## Ladder status after this session
- **PL-HY-FENCE** ✅ DONE (this session).
- **PL-HY-1c** — still BLOCKED: needs the `g_pl_flat_chain` lowerer prereq (slot-filling Prolog operand
  boxes) — a DESIGN step touching shared `lower.c` + risking the 111/111 byte-identity gate. **Lon sign-off.**
- **PL-HY-2/3/4** — SUBSUMED by the `x86()` revamp (a router-split would over-split); **PL-HY-5** —
  effectively complete. Left as `[ ]` per the morning audit's deferral — awaiting Lon's call to reclassify
  `[x]` vs delete. I did NOT touch them (not my work to reclassify).

## NEXT (unblocked, mechanical) vs (blocked, needs Lon)
**Unblocked forward engineering** (no decision required):
- **WAM-CP-7c** — var-vs-var unify spec: `eq(X,X)` arg2 routes `rt_pl_unify_var_var` reading both env
  slots (3→1 calls). Touches unify codegen + runtime; must hold GATE-3 111/111 byte-identity.
- **WAM-CP-9 (rest)** — committed-ITE node; bare `!` in `(A;B)` through truncate; retire `g_pl_cut_flag`.

**Blocked on Lon:** PL-HY-1c design sign-off; reclassify PL-HY-2/3/4/5.

**m4 75→86** remains gated on a runtime substrate for the 36 EXCISED rungs (findall / retract / abolish /
assertz / aggregate / catch-throw / dcg_generate / compound+float unify) — PLG-9g / PLG-10 / WAM-CP-13.

## Build / verify recipe
```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh            # GATE-1 m2 5/5
bash scripts/test_prolog_rung_suite.sh       # GATE-3 m2 111/111, m3 111/111, m4 75/0/36
bash scripts/test_gate_bb_one_box.sh         # PL-HY-FENCE — PASS
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include='*.c' --include='*.cpp' | grep -v _templates/ | grep -v emit_core.c | wc -l   # 0
grep -rn 'g_vstack' src/ | wc -l             # 0
# the rung suite regenerates corpus/programs/prolog/*.s — `git checkout -- programs/prolog/*.s` to re-clean
```
Authors: LCherryholmes · Claude Opus 4.8
