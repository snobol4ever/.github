# GOAL-ICON-FULL-PASS.md — Icon: m2 247/247 · m3/m4 parity

**Status:** m2 197/283 (interp-suite tally) · XFAIL 36 (out of scope). HEAD=b3de0be.
**Gate every step:** `bash scripts/test_icon_rung_suite.sh` — m2 never decreases; m3/m4 trend up.
**Note:** the interp-suite reports m2=197 (`test_icon_rung_suite.sh --mode interp`); the prior "200" header was a different/combined count. Use the suite tally + an explicit before/after diff to judge regressions.

---

## M3/M4 gap — open work

**Failure categories (m3, ~104 FAIL):**
- **rc=134 (~28):** x86_bomb hit — missing BINARY arm. Run `./scrip --run foo.icn 2>&1` to see which bomb. ✅ `bb_to.cpp` descending TO (negative `by`) DONE (5dc543f). Next bomb targets: grep remaining `rt_bomb` hits per rung; `bb_alt`/`bb_scan_*` arms.
- **rc=124 (~12):** timeout — infinite retry loop. TO/EVERY retry wiring in BINARY path.
- **rc=139 (was 4):** ✅ segfault ELIMINATED (8b3eefb). ROOT CAUSE was NOT a missing template — `flat_drive_case` (emit_bb.c:1668) existed but read the OLD IR_CASE shape after IRD-3b (4699ab8) rewired the lowering to operand-wrappers (operands[0]=selector, operands[1..]=IR_LIT_NUL arm wrappers carrying [key,val] or [val]=default — the shape the interp reads). Emitter walked `operands[0]->γ.node` off the selector → garbage → segv. FIX: explicit IR_CASE reject in `icn_graph_native_emittable_mode` (scrip.c:267, the REAL gate; `icn_kind_native_stub` is dead/never-called) → case programs now [SMX] EXCISE cleanly. BUILDING BLOCK landed: `rt_case_eq(sel,key)` implemented (was dead abort-stub), interp === semantics. TODO for native CASE: rewrite `flat_drive_case` to the operand-wrapper shape + `bb_case_arm` template calling rt_case_eq; deposit matched value into the CASE node's own slot (write reads `bb_slot_get(ir_call_arg(node,0))`).
- **silent-empty (reduced):** ✅ multi-statement loop-drop FIXED (fb2daea) — bounded EVERY exhaustion now routes to success continuation, not `main_ω`. `rung01_paper_lt`, `rung01_paper_to_by`, `rung07_control_to_by` now PASS m3/m4. Residual silent-empty cases: re-triage with `./scrip --run foo.icn` per still-failing rung.

**m4 vs m3:** m4 51 / m3 45 (m4 ahead by 6 — extra TEXT-arm coverage). Confirm any m3-only fail with stderr probe.

---

## Open m2 steps

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

**HEAD (SCRIP) = `b3de0be`** — ICON FULL-18-resid LANDED: `every`-conjunction with an embedded generator now resumes correctly. Two `src/lower/lower_icon.c` fixes (lowering only; NO template/emitter/runtime change): (1) `lower_every` `!BODY` loop-back — `loop_target` was `(gen_result->op==IR_CONJ)?E:…`, forcing a conjunction's success edge to the EVERY node, which (ival=0) returns γ and exits after ONE value; now `(gen_node && gen_node!=gen_result && gen_node!=ω && gen_node!=E) ? gen_node : E`, i.e. loop back to the embedded generator's resume — unifies the CONJ case with the already-correct `every f(gen)` CALL case (which is why `every write(1 to 5)` always worked: CALL.γ→TO). (2) relop BINOP — `op` was built with the outer `ω` as its fail port, so a false comparison (`1>2`) exited to the every fail instead of resuming its generative operand; added `if (IR_LIT(op).dval==1.0 && lβ && lβ!=ω && lβ!=op) ω_to(op, lβ)` (relops are codes 5–10, marked `dval=1.0`; `lβ`=left operand's resume). VERIFIED via a 4-layer ladder: `every write(1 to 5)`→1-5 (unchanged); `every (1 to 5)>2 & write("hit")`→hit×3 (was ×1); `every (x:=(1 to 5)) & write(x)`→1-5 (was just 1); `every (x:=(1 to 5))>2 & write(x)`→3,4,5 (was empty). `rung13_alt_alt_filter` FAIL→PASS. m2 196→197 by EXPLICIT before/after `--mode interp` diff = EXACTLY one line changed, ZERO regressions. Smoke icon m2 12/12 + prolog 5/5 HARD; `test_gate_icn_no_stack`=0; `test_gate_icn_one_reg_frame`=0; filter m3/m4 cleanly `[SMX] EXCISE` (sanctioned). The 45 `test_gate_bb_one_box` FAILs are PRE-EXISTING (identical on pristine 8b3eefb — emitter template entry-count gate, untouched by this lowering change). HEAD shown is post-rebase onto remote (a430139: PL nb_setval + RAKU user-sub landings came in concurrently; fix re-verified green after rebase).

**OPEN — `cross_arg` multi-generator CALL args (NEXT, separate/deeper bug — NOT FULL-18):** `every write(1|2, ":", 3|4)` → `1:3, 334, 2:3, 334` (want `1:3,1:4,2:3,2:4`); `rung13_alt_alt_cross_arg` + `rung13_alt_alt_cross_arg_sideeffect` still FAIL. ISOLATED precisely: `write((1|2)||(3|4))` (concat, ONE arg) is CORRECT (13,14,23,24) — the conjunction/concat resume path is fine; `write(1|2, 3|4)` (TWO generator args) is BROKEN (13,**34**,23,**34**). Instrumented the CALL: it takes the **`is_deep=1` ag_ring-peek path with `has_gen_arg=0`** (the cross-product odometer block at IR_interp.c ~2576 is NEVER entered — multi-arg generators are lowered as flat chained producer boxes, so `ir_call_arg` sees them already-evaluated, not as generators). Resume is driven by flat back-edges (`CALL.γ → rightmost gen ALT`), but the ag_ring is not maintained across the literal-separated args on carry → the left arg's ring slot goes stale (the leading "3" in "334"). FIX LIVES IN: the `is_deep` CALL ring protocol and/or `lower_call`'s flat-chain arg wiring — a ring-protocol fix, materially larger than FULL-18, likely a fresh session. (Graphs: `--dump-bb` on `rung13_alt_alt_cross_arg` shows two ALT nodes whose `ω` both point at the FIRST ALT — the carry order is the suspect.)

 `flat_drive_case` (emit_bb.c:1668) was stale: it read the OLD IR_CASE shape, but IRD-3b (4699ab8/fbfd71c) had rewired the lowering to operand-wrappers (operands[0]=selector; operands[1..]=IR_LIT_NUL arm wrappers, [key,val] normal / [val] default — the shape the interp at IR_interp.c:4132 reads, which is why m2 passes all four rung33 cases). The emitter walked `operands[0]->γ.node` off the selector as a phantom key/val chain → garbage nodes → segv on int/str/arith (no_default happened to trip a gate and excise). FIX: added explicit `IR_CASE → return 0` to `icn_graph_native_emittable_mode` (scrip.c:267 — the REAL m3/m4 routing gate, permissive-by-default; `icn_kind_native_stub` is DEAD/never-called, do not edit it). Case programs now loudly `[SMX] EXCISE` (sanctioned interim state) instead of segfaulting. ALSO implemented `rt_case_eq(const DESCR_t*sel, const DESCR_t*key)` (rt.c:399) — was a dead abort-stub with a wrong single-DESCR sig; now int-by-value when both DT_I else VARVAL strcmp, matching the interp === — the first building block for a future native CASE. m2 200 (HARD, unchanged) · m3 45→65 · m4 51→71 (the +deltas vs the fb2daea watermark are cumulative incl. Pascal/IRD landings on the real HEAD; my change is segfault→excise, m2-neutral). prolog 5/5.

**Next for native CASE (clearly scoped):** rewrite `flat_drive_case` to the operand-wrapper shape (mirror the interp loop): eval selector via walk_bb_flat → its slot; per arm eval key → slot, `call rt_case_eq` with `lea rdi,[r12+sel_off]; lea rsi,[r12+key_off]`, test rax, je arm-value; arm value evals then COPIES its 16-byte DESCR slot into the CASE node's own slot (`bb_slot_get(case_node)`) before jmp γ; trailing 1-operand wrapper = default → γ; no match no default → ω. The compare + copy must go through a `bb_case_arm` template reached via EMIT_PAIR_FILL (driver has no direct emit primitives; all bytes live in templates). Remove IR_CASE from the gate the moment the template lands.

**Key intel:** `icn_ring_to_tree` returns NULL if chain has IR_BINOP or IR_LIT_I → falls to `descr_flat_chain_build(bbg->entry)`. `--dump-bb` does NOT show `operand_aux`. DESCR_t = {DTYPE_t(4)+slen(4) in low 8 bytes; int64/ptr in high 8 bytes} — passed as rdi:rsi pair. Asm chain node indices (`xchainN_nK_*`) are CHAIN POSITIONS, not graph node ids. m2 walking the same graph correctly = graph is right, bug is in the flat emitter — a safe class to fix (cannot move the m2 HARD gate).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
