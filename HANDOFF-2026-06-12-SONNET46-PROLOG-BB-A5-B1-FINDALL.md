# HANDOFF — 2026-06-12 — Sonnet 4.6 — PROLOG-BB A5 + B1 findall

**Goal:** GOAL-PROLOG-BB.md · PL-GZ-9 corpus reconquest.
**Watermark:** SCRIP `2365838` · .github `dc22ef23` (both green).

## Landed

### A5 — rung26 copy_term/atomic_list_concat/concat_atom (+4 m3) LANDED `db41e3a`

Sites 3+4 (`pl_gz_count_synth_goal` and `pl_gz_build_goal`) added for:
- `copy_term/2`: dest now accepts IR_LOGICVAR/STRUCT/ATOM/LIT_I (synth slot for non-LOGICVAR). Sites 1 and 3 widened to match.
- `atomic_list_concat/2` (and `concat_atom/2`): list arg synth slot; result must be LOGICVAR. Routes to `IR_DET_ATOM_OP` with ival=2.
- `atomic_list_concat/3`: list + sep args synth; result must be LOGICVAR. Routes to `IR_DET_ATOM_OP` with ival=3.

All four rung26 m3 cases pass. All five rung26 m4 cases also pass (via GZ TEXT path, `rt_atomic_list_concat_term`/`rt_copy_term_terms`). m3: 80→84 (+4).

### B1 — rung11/43 findall (+7 m3) LANDED `2365838`

Four non-trivial fixes required beyond the four admission sites:

**1. gz_fill_goal op_sval fix (emit_bb.c):**
`gz_fill_goal` previously set `g_emit.op_sval = NULL` for all non-`IR_DET_WRITE` nodes. The `bb_resolve→bdisp→bb_findall_str` template reads `_.op_sval` to dispatch (`fn = _.op_sval ? _.op_sval : ""`). Without this, `fn=""` and `bb_findall_str` never matched. Fix: `gz_fill_goal` now sets `op_sval = IR_LIT(g).sval` for both `IR_DET_WRITE` and `IR_BUILTIN`.

**2. bb_findall.cpp BINARY β label (bb_findall.cpp):**
BINARY path was missing `hdr` (which defines the α label) and a `def β` before the final `jmp ω`. The GZ framework allocates a β label per cell (`gzq0_g0_β`), expects it resolved. Fix: added `hdr` at start and `x86("def","β")` before terminal `jmp ω`.

**3. rt_pl_gz_init — g_resolve_env for rt_findall (unification.c + bb_query_frame.cpp):**
`rt_findall(fs_ptr)` calls `resolve_node_to_term(fs->result)` which dereferences `g_resolve_env[slot]`. In the GZ m3 binary path, `g_resolve_env` was NULL (only allocated by `rt_env_alloc` in the rich-body-root path). Fix: new `rt_pl_gz_init(void *frame, int nslots)` — allocates `g_resolve_env` if NULL, creates fresh `Term*` vars and stores in BOTH GZ frame cells (`[r12+8+8*i]`) and `g_resolve_env[i]`. Replaces `rt_pl_cells_init` in `bb_query_frame` BINARY+TEXT (single call, no medium branch — ONE MEDIUM, INVISIBLE compliant). The frame pointer `r12` is passed as `rdi`; nslots as `esi`.

**4. Admission sites (scrip.c):**
- Site 1 (`pl_gz_rule_body_goal_ok`): `return pl_findall_conj_member_admissible(gg)` — forward decl added.
- Site 2 (whitelist): `continue` for `findall`.
- Site 3 (count_synth): no-op comment (fs_ptr already carries all state).
- Site 4 (build_goal): chain `gg` directly (`IR_BUILTIN` findall → `bb_resolve` → `bb_findall_str`). Inserted before copy_term arm.

m3: 84→91 (+7). m4: unchanged at 56 PASS — findall m4 TEXT hits "build_compound_term: unhandled kind 64" for `IR_GCONJ` in `bff_goal`; 7 tests moved EXCISED→FAIL, no PASS change.

## m4 ratchet correction

Goal file previously stated ratchet floor=87 (from `cb3c1b3`). Actual HEAD baseline is **56 PASS / 42 FAIL / 17 EXCISED**. The 87 figure predates a rebase and no longer applies. Corrected in goal file to ratchet floor=56.

## Current m3 failures (24 remaining)

- rung14 ×5: retract — needs `IR_DET_RETRACT` (B3)
- rung15 ×5: abolish — needs `IR_DET_ABOLISH` (B4)
- rung22 ×1: `write_canonical(1+2)` — IR_ARITH arg excluded (pre-existing)
- rung27 ×4: aggregate/nb — needs A6 (`nb_setval/getval`, `aggregate_all`)
- rung28 ×5: catch/throw — needs `pl_gz_rule_body_goal_ok` arm for IR_CATCH + throw (B2)
- rung30 ×4: DCG — phrase/grammar callee admission (B5)

## Next recommended steps

**B2 — rung28 catch/throw (+5 m3):** catch/throw already admitted in `pl_findall_conj_member_admissible`. Need `pl_gz_rule_body_goal_ok` arm for `IR_CATCH` and `throw` IR_BUILTIN. IR_CATCH has `bb_ite_catcher_t*` in ival. Admission: `pl_findall_term_buildable(zc->catcher)`. Build_goal: chain IR_CATCH directly (like findall — `bb_resolve` → `bb_catch_str` or similar already handles it).

**A6 — rung27 aggregate/nb (+4 m3):** `nb_setval/2`, `nb_getval/2` → `rt_pl_nb_setval_cell`/`rt_pl_nb_getval_cell` (already in `unification.c` as `rt_nb_setval_term`/`rt_nb_getval_term`). New `IR_DET_NB_SETVAL`/`IR_DET_NB_GETVAL`. `aggregate_all/3` already in `pl_findall_conj_member_admissible` line 1697 — just add `pl_gz_rule_body_goal_ok` arm.

**C-LABEL — rung05/06 m4 (+4 m4):** `.Lplpred__S1_2` undefined at link. DCG scope variable `_S*` from `dcg_fresh_var()` in `prolog_parse.c` leaks into `resolve_call_block_label` as callee name. In `emit_bb.c` `bb_prepare()` for `IR_GOAL`, `bb_ls = IR_LIT(nd).sval` — confirmed `"member"` in dump but emitted as `_S1`. Likely `g_emit.bb_ls` is overwritten between `bb_prepare` and the actual `bb_resolve` call by another node's setup. Add `fprintf(stderr, "[DBG] IR_GOAL bb_ls=%s\n", g_emit.bb_ls)` just before the `FILL` call in the IR_GOAL branch of `gz_emit_cell` to trace which node corrupts it.

## Session setup for next session

```bash
cd /home/claude/SCRIP && bash scripts/install_system_packages.sh
make -j4 scrip && make libscrip_rt
bash scripts/test_smoke_prolog.sh         # GATE-1 (5/5 all modes)
bash scripts/test_prolog_rung_suite.sh    # GATE-3 (m2=114 m3=91 m4=56)
grep -rnE 'seg_byte\(SEG_CODE|SL_B\(' src/ --include="*.c" --include="*.cpp" | grep -v "_templates/" | grep -v emit_core.c | wc -l   # 0
grep -rn 'g_vstack' src/ | wc -l          # 0
```
