# HANDOFF — SNOBOL4-BB — B6 STITCH-CAT (Sonnet 4.6, 2026-06-08)

## TL;DR
- **B6 STITCH-CAT verified and LANDED on main.** `origin/main = 69b3417`. B0–B6 all on main.
- Gates GREEN: smoke 7/7 · pat-rung 19/19 no-SKIP · corpus **155**/280 (floor held) · beauty 1/17 · fence HARD.
- **NEXT: B7 NULLARY** — ARB/REM/BAL/FENCE/FAIL/SUCCEED/ABORT. ⛔ CRITICAL: bare nullary keywords parse as TT_VAR, not TT_xxx tokens — see B7 recipe in `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md`.

## What landed

`bb_pattern_cat.cpp` — pure pointer-patch stitch (no pool allocation, no new thunk):
1. `*left.γ_site = right.entry` — success chain: left → right
2. `*right.ω_site = left.β` — fail chain: right.ω → left.β code (= left.ω_site_addr + 8 via `lea rcx,[rcx+8]`)
   - For one-shot LEFT (LIT/LEN/SPAN/etc.): left.β restores δ then exits via left.ω_slot → DTP head _w thunk → ω trampoline ✓
   - For BREAKX LEFT: left.β re-generates at next break char → correct nearest-left-resume ✓
3. Output fragment: `{left.entry, right.γ_site, left.ω_site}` — DTP_ASSIGN wires left.ω_slot to _w_head

`lower_sno.c`:
- `sno_seq_is_pattern` (new): returns 1 for TT_LEN/TT_SPAN/etc. — NOT TT_QLIT/TT_ILIT
- `sno_pattern_buildable` TT_SEQ/TT_CAT: `flatten_seq` + `has_pat` via `sno_seq_is_pattern`. Critical: guards plain string concat `'ab' 'cd'` from misrouting into the builder (smoke `concat` regression, caught and fixed)
- `lower_pattern_build` TT_SEQ/TT_CAT arm: pairwise left-assoc IR_PATTERN_CAT chain with `lastβ` tracking

## Probes (4/4 sbl-MATCH)
| pattern | subject | scrip=sbl |
|---|---|---|
| `'a' LEN(2)` | abcd | `abc` ✓ |
| `LEN(1) 'b'` | abcd | `ab` ✓ |
| `SPAN('a') 'b'` | aaab | `aaab` ✓ |
| `'x' LEN(2)` | abcd | `fail` ✓ |

## Merge conflicts resolved
Concurrent session (`42f07cd`) had independently scaffolded B6. Conflicts in `lower_sno.c` + `bb_pattern_cat.cpp` + `emit_bb.c` (duplicate cases) + `Makefile` (duplicate entries). Resolution: took concurrent's `sno_seq_is_pattern` + β-chain template, kept `lastβ` tracking, removed duplicates.

## B7 recipe — CRITICAL FINDING (from concurrent session `ec4718c`)

Bare nullary keywords `REM`/`FAIL`/`SUCCEED`/`ARB`/`BAL`/`FENCE`/`ABORT` parse as **`TT_VAR`** (sval=name), NOT dedicated `TT_xxx` tokens. Token forms arise only from `REM(...)` function syntax (invalid for argument-free primitives). `case TT_FAIL:` in `lower_pattern_build` is DEAD CODE.

**Corrected routing for B7a (FAIL/REM/SUCCEED):**
- `sno_pattern_buildable`: `if (e->t==TT_VAR && e->v.sval && is_nullary_pat_name(e->v.sval)) return 1;`
- `lower_pattern_build`: `case TT_VAR:` name-switch → `nalloc(IR_PATTERN_FAIL/REM/SUCCEED)` + `emit_leaf`
- `sno_seq_is_pattern`: name-check TT_VAR sval (so `'a' REM` flags `has_pat`)

Full B7 recipe (b7a trivial one-shots FAIL/REM/SUCCEED + b7b ARB/FENCE/ABORT) in `SCRIP/SNOBOL4-5STAGE-OWNED-BUILD.md`.

## Session Setup reminder
```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh && make libscrip_rt
git clone https://TOKEN@github.com/snobol4ever/x64 /home/claude/x64
```
Gates (MODE-4 ONLY):
```bash
bash scripts/test_smoke_snobol4.sh                               # 7/7 HARD
bash scripts/test_snobol4_pat_rung_suite.sh                      # 19/19 no-SKIP
SCRIP=$PWD/scrip bash scripts/test_mode4_only_corpus_snobol4.sh  # 155 floor
bash scripts/test_gate_em_beauty_subsystems_mode4.sh             # 1/17 floor
bash scripts/test_gate_sno_pat_reg.sh                            # fence HARD
```

— Sonnet 4.6, co-dev. GATES: MODE-4 ONLY.
