# GOAL-ICON-FULL-PASS.md — Icon: m2 247/247 · m3/m4 parity

**Status:** m2 200/283 · m3 45/283 · m4 51/283 · XFAIL 36 (out of scope). HEAD=fb2daea.
**Gate every step:** `bash scripts/test_icon_rung_suite.sh` — m2 never decreases; m3/m4 trend up.

---

## M3/M4 gap — open work

**Failure categories (m3, ~104 FAIL):**
- **rc=134 (~28):** x86_bomb hit — missing BINARY arm. Run `./scrip --run foo.icn 2>&1` to see which bomb. ✅ `bb_to.cpp` descending TO (negative `by`) DONE (5dc543f). Next bomb targets: grep remaining `rt_bomb` hits per rung; `bb_alt`/`bb_scan_*` arms.
- **rc=124 (~12):** timeout — infinite retry loop. TO/EVERY retry wiring in BINARY path.
- **rc=139 (4):** segfault — `rung33_case_*`. IR_CASE has no native template (no `flat_drive_case`/`bb_case`). Build one from JCON `ir_a_Case` (refs/jcon-master/tran/irgen.icn:232).
- **silent-empty (reduced):** ✅ multi-statement loop-drop FIXED (fb2daea) — bounded EVERY exhaustion now routes to success continuation, not `main_ω`. `rung01_paper_lt`, `rung01_paper_to_by`, `rung07_control_to_by` now PASS m3/m4. Residual silent-empty cases: re-triage with `./scrip --run foo.icn` per still-failing rung.

**m4 vs m3:** m4 51 / m3 45 (m4 ahead by 6 — extra TEXT-arm coverage). Confirm any m3-only fail with stderr probe.

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

**HEAD (SCRIP) = `fb2daea`** — two Icon native-loop fixes. (1) `bb_to` descending TO: guard `by!=0`, loop-exit cmp picks `jg`/`jl` by sign of `by` (matches m2 `by>=0?counter>to:counter<to`); eliminated the rc=134 `bb_to` bomb. (2) flat-emit EVERY exhaustion: in `codegen_flat_chain_body` omega resolver (emit_bb.c ~2970), a generator whose `ω` resolved to its own EVERY was routed to `lbl_ω`=`main_ω` (proc failure) → every program died at its first loop's exhaustion; now routes to the EVERY node's α label (`lbls[omega_k]`) so the EVERY takes its γ to the next statement (or proc-success epilogue for a final/single `every`). m2 200 (HARD, graph untouched) · m3 44→45 · m4 50→51 · prolog 5/5. HEAD (.github) = HANDOFF-2026-06-13-OPUS48-ICON-FULL-PASS-TO-EVERY-CHAIN.md.

**Key intel:** `icn_ring_to_tree` returns NULL if chain has IR_BINOP or IR_LIT_I → falls to `descr_flat_chain_build(bbg->entry)`. `--dump-bb` does NOT show `operand_aux`. DESCR_t = {DTYPE_t(4)+slen(4) in low 8 bytes; int64/ptr in high 8 bytes} — passed as rdi:rsi pair. Asm chain node indices (`xchainN_nK_*`) are CHAIN POSITIONS, not graph node ids. m2 walking the same graph correctly = graph is right, bug is in the flat emitter — a safe class to fix (cannot move the m2 HARD gate).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
