# GOAL-ICON-FULL-PASS.md — Icon: m2 247/247 · m3/m4 parity

**Status:** m2 200/283 · m3 44/283 · m4 41/283 · XFAIL 36 (out of scope). HEAD=7214e00.
**Gate every step:** `bash scripts/test_icon_rung_suite.sh` — m2 never decreases; m3/m4 trend up.

---

## M3/M4 gap — open work

**Failure categories (m3, 105 FAIL):**
- **rc=134 (~30):** x86_bomb hit — missing BINARY arm. Run `./scrip --run foo.icn 2>&1` to see which bomb. First target: `bb_to.cpp` BINARY arm for real-step TO (`rung01_paper_to_by`).
- **rc=124 (~12):** timeout — infinite retry loop. TO/EVERY retry wiring in BINARY path.
- **rc=139 (4):** segfault — `rung33_case_*`. IR_CASE has no native template.
- **~47 silent-empty:** control lost in BINARY path. `rung01_paper_lt` class (TO+relop+EVERY): `descr_flat_chain_build` path loses control somewhere; add `fprintf(stderr,"[DBG]")` to `rt_write_any_nl` or gdb the --run blob.

**m4 gap vs m3 (41 vs 44):** 3 additional m4 failures — likely TEXT-arm templates missing BINARY. Confirm with stderr probe.

---

## Open m2 steps

- **FULL-18-resid assign-gen β** — `every (x := (1|2|3|4)) > 2 & write(x)` empty. `lower_call` resets `cx->beta=ω`; fix: detect `last_gen` after lowering args, set `cx->beta=call`. Rung 13. +1.
- **FULL-12 coerce()** — `integer(x)`/`real(x)`; consult `oarith.r`. Rungs 36,37. +5.
- **FULL-13-resid keywords** — `& &e` parse ambiguity, &error write-back, &dump/trace/random. Rung 37. +3.
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

**HEAD (SCRIP) = `7214e00`** — m4 double-colon fix: x86("label",s) appends ":"; strip trailing ":" from _.lbl_β in bb_call_write_slot(×2)/bb_call_rk_bool/bb_call_proc_staged; m4 0→41. m2 **200** · m3 **44** · m4 **41**. HEAD (.github) = HANDOFF-2026-06-12-SONNET46-ICON-FULL-PASS-M4-DOUBLE-COLON.md.

**Key intel:** `icn_ring_to_tree` returns NULL if chain has IR_BINOP or IR_LIT_I → falls to `descr_flat_chain_build(bbg->entry)`. `--dump-bb` does NOT show `operand_aux`. DESCR_t = {DTYPE_t(4)+slen(4) in low 8 bytes; int64/ptr in high 8 bytes} — passed as rdi:rsi pair.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
