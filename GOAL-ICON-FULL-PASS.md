# GOAL-ICON-FULL-PASS.md — Icon: m2 247/247 · m3/m4 parity

**PIVOT 2026-06-12 (Lon, session 2):** flat_drive_binop_gen_tree fixed (infinite loop + missing slot setup). m3/m4 now 44 (was 39). rung01_paper_lt now PASSES. paper_mult/compound still failing — retry-wiring interaction between EMIT_PAIR pair-table and bb_fill_alpha α-label needs one more session. Priority: finish binop_gen_tree retry wiring, then TO+relop compound chains.

**PIVOT 2026-06-06 (Lon):** REVAMP/HYGIENE in GOAL-BB-FIXUP. This goal owns: lowerer (`lower_icon.c`), m2 interpreter (`IR_interp.c`), Icon runtime (`by_name_dispatch.c`, `aggregates.c`, `keywords.c`), and now m3/m4 native codegen parity.

**Status:** m2 200/247 · m3 44/247 · m4 44/247 · XFAIL 36 (out of scope). HEAD=10db0c2.
**Gate every step:** `bash scripts/test_icon_rung_suite.sh` — m2 never decreases; m3/m4 trend up.

---

## M3/M4 parity — root cause and open work

**Diagnosed this session (99e96e9):**
- `flat_drive_call_intexpr` skipped `walk_bb_flat(a0)` when `dval==1.0` (single-arg write). Fixed: always walk when `g_descr_flat_chain`. COMMITTED.
- `bb_binop_relop` did not store result `y` (right operand) to `op_off`. Fixed: copy `op_sb` tag+value to `op_off` after cmp passes. COMMITTED. Icon relop returns `y` per `ocomp.r`.
- **Still failing:** `rung01_paper_lt` (`every write(2 < (1 to 4))`) outputs empty in m3/m4 even with both fixes. Asm is structurally correct (relop stores to slot 72/80, write reads 72/80, write's γ = TO.β retry). Root cause NOT yet found — likely in how `descr_flat_chain_build` calls `bb_build_flat(icn_root)` vs `descr_flat_chain_build(bbg->entry)` when `icn_ring_to_tree` returns NULL. Next step: instrument `rt_write_any_nl` or single-step the --run blob to find where control is lost.

**M3 FAIL categories (95 total):**
- Silent-empty output (no SMX, rc=0): generator-in-every + relop/arith chains. Core of the parity gap.
- rc=124 (timeout): `rung01_paper_mult`, `rung01_paper_paper_expr`, `rung02_arith_gen_nested_add`, etc. — likely infinite loops in retry wiring.
- rc=134 (abort): scan builtins (`find`, `find_gen`), `!` (LIST_BANG), `string_format`, `trim`, etc. — stub dispatch hits `x86_bomb`.
- rc=139 (segfault): `rung33_case_*` — CASE box not wired.

**Priority order:** (1) fix silent-empty for TO+relop+EVERY (the `rung01_paper_lt` class), then arith, then remove timeouts, then rc=134 stubs.

---

## Open m2 steps

- **FULL-18-resid assign-gen β** — `every (x := (1|2|3|4)) > 2 & write(x)` empty. `lower_call` resets `cx->beta=ω`; assign-generator doesn't propagate self-resume β. Do not loosen `c9ec94c` gate. Rung 13. +1.
- **FULL-12 coerce()** — `integer(x)`/`real(x)` all combos; consult `oarith.r`. Rungs 36,37. +5.
- **FULL-13-resid keywords** — rung37: `& &e` parse ambiguity, &error write-back, &dump/trace/random. +3.
- **FULL-14 scan-alt** — `IR_GEN_SCAN` resume across alt. Rung 37. +2.
- **FULL-15 str relop** — remaining lexicographic cases in `by_name_dispatch.c`. +1.
- **FULL-16 mutual recursion** — forward refs via `rt_call_named_proc`. +1.
- **FULL-17 sort()** — `rt_list_sort`/`rt_table_sort` in `aggregates.c`. Rung 31. +5.
- **FULL-32 rung36/37 sweep** — triage residuals; document XFAILs.

---

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/test_smoke_icon.sh        # m2 12/12 HARD
bash scripts/test_smoke_prolog.sh      # m2 5/5 HARD
bash scripts/test_gate_bb_one_box.sh
# Extract refs if absent:
unzip -q /mnt/user-data/uploads/2-icon-master.zip -d refs/
unzip -q /mnt/user-data/uploads/3-jcon-master.zip -d refs/
```

## Gate after every step

```bash
bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/test_icon_rung_suite.sh   # m2>=200 HARD; m3/m4 track up
bash scripts/test_gate_bb_one_box.sh
bash scripts/test_smoke_prolog.sh
```

## Canonical source rule

Port topology → `refs/jcon-master/tran/irgen.icn`. Runtime → `refs/icon-master/src/runtime/*.r` (`ocomp.r`, `fstranl.r`, `oarith.r`, `oref.r`). m2 oracle is a transcription; canonical wins.

---

## Watermark

**HEAD (SCRIP) = `7214e00`** — m4 double-colon label fix: x86("label",s) appends ":" — strip trailing ":" from _.lbl_β in bb_call_write_slot(×2)/bb_call_rk_bool/bb_call_proc_staged; m4 0→41. m2 **200** · m3 **44** · m4 **41**. HEAD (.github) = HANDOFF-2026-06-12-SONNET46-ICON-FULL-PASS-M4-DOUBLE-COLON.md.

**Key intel:** `icn_ring_to_tree` returns NULL if chain has IR_BINOP or IR_LIT_I → falls to `descr_flat_chain_build(bbg->entry)`. `--dump-bb` does NOT show `operand_aux`. DESCR_t = {DTYPE_t(4)+slen(4) in low 8 bytes; int64/ptr in high 8 bytes} — passed as rdi:rsi pair.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
