# FINDING-2026-08-08-CLAUDE-SN4-RTX-CENSUS-M4-ARM-AND-QUARANTINE-CHARACTERIZATION.md

**Session:** s_this (2026-08-08) — Claude Sonnet 4.6  
**Goal:** GOAL-SNOBOL4-RTX.md  
**Commit:** SCRIP `2d687dab` — `RTX census: add m4 (--compile) arm to util_rtx_arm_census.sh`

---

## 1. CENSUS M4 ARM — STANDING GAP CLOSED

`util_rtx_arm_census.sh` now accepts `[m3|m4|both]` as a second argument (default `m3`, backward-compatible).  The m4 path compiles the `.sno` via `scrip --compile`, links against `libscrip_rt.so` with `-rpath` (same `compile_m4()` shape as `test_gate_rtx_killswitch_sets.sh`), and runs the resulting binary under `LD_PRELOAD` of the same interposer.  The interposer's `ac_init` `RTLD_NOLOAD` guard works identically for m4 binaries since they link `libscrip_rt.so`.  `print_table()` was factored out of the former single-mode report block; m3 and m4 each get a labelled table.

**Why this gap was load-bearing:** every coverage number from `util_rtx_arm_census.sh` was `--run` only, making the audit structurally blind to the exported/hidden data-symbol class that mode 4 exists to catch (ARCH §7 step 0(c)).  The `g_cap_gen` visibility episode cost 173/316 mode-4 link failures while mode 3 stayed green — that class lives exactly here.

**Verified on three workloads:** `413_arith_mixed`, `json-match-fence`, `claws5-match` — m3 and m4 produce identical census tables on all three.  Default behaviour (no MODE arg) unchanged.

---

## 2. WATERMARK STATE AT SESSION OPEN

Cursor (`372d4b60`) said: m3 **265/52/0** · m4 **253/63/1 SKIP** · DIVERGE **11**.

At HEAD `709d5f19` (after four concurrent commits: ZK-2, M-2 HFC-WINDOW, RC-0a, RC-1 RTCC skeleton), the crosscheck reads: m3 **257/60/0** · m4 **235/81/1 SKIP** · DIVERGE **21**.

Baseline verified: `372d4b60` rebuilt and re-measured — reproduces cursor exactly (265/52/0 · 253/63/1 · DIVERGE 11).  The delta is entirely from concurrent-seat commits; this session made zero changes to codegen.  The watermark must be updated at handoff to reflect current HEAD.

---

## 3. KILL-SWITCH GATE CHARACTERIZATION (MATCH family, patterns corpus)

Gate at N=4 reported 6 movers (4 m3 + 2 m4).  At N=8 the stable picture is:

**Genuine mover (1, m3 only, pre-existing at `372d4b60`):**
- `056_pat_star_deref` — `*PAT` as bare whole-pattern deferred reference.  Gate-ON stable `cfb0e3ab` (`say hello` — too much captured), gate-OFF stable `5d701824` (empty — misses entirely), ref is `hello`.  Both arms wrong, different ways.  Program already in crosscheck FAIL list; mover classification correct.  Belongs to the PATREF/deferred-eval surface — not a new regression.

**False movers at N=4 (resolved at N=8):**
- `131_pat_boolean_expr_grammar` — SEGV (rc=139) after producing correct output `true AND false` in both arms.  Hash includes rc; ON=OFF=identical across 8 runs.  Gate noise at N=4.
- `153_pat_operand_edge_matrix` — both arms produce same truncated output (crashes mid-run).  Stable ON=OFF.  Noise.
- `154_pat_construction_time_hoist` — ON=OFF=identical (rc=139) across 8 runs.  Noise.

**Lesson:** N=4 is insufficient for the patterns corpus on this machine.  Three of four reported "movers" at N=4 resolved as identical at N=8.  The ARCH contract says N≥4; in practice N=8 is the reliable floor for this suite.

---

## 4. QUARANTINE PROGRAMS — THREE FROM THE LADDER

**`413_arith_mixed`:** passes m3 stably (5 runs, output matches ref, rc=0).  Not in the patterns corpus; MATCH gate in its own directory: IDENTICAL=5 QUARANTINE=0 MOVER=0.  The ladder's N≫4 concern appears resolved at HEAD — not quarantine here.

**`W06_len`:** same — passes m3 stably, MATCH gate clean in rungW06 directory.  Not quarantine at HEAD.

**`160_pat_alt_inner_gen_resume`:** SEGVs (rc=139) every run, produces empty stdout, ref is `V=[X]`.  8 runs give identical hash (all `68b329da`).  No longer observably non-deterministic at HEAD — the prior session's three-distinct-hash observation may have been fixed by concurrent commits.  Still failing (wrong output + crash), XFAIL.run status appropriate.

---

## 5. ITEMS NOT ACTIONED (LON-ROUTED)

- **Defect-2** (140/141 SIGSEGV, pcall mismatch in EXPR$N blob after inner jmp-entry γ-return) — Lon routes.
- **RTX-4 CALL surface** (`rt_call_arr` + `try_call_builtin_by_name` ruling) — Lon routes.
- **`util_rtx_count_syms.sh` SEGFAULT on `rt_dcap_lazy_init`** — pre-existing, not touched.
- **Min-of-N rail mode / hugepage pinning** — pre-existing open item, not touched.

`handoff_status.sh` is the push truth — NOT this block.
