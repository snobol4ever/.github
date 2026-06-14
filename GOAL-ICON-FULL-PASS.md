# GOAL-ICON-FULL-PASS.md — Icon: m2 247/247 · m3/m4 parity

**Status:** m2 202/283 · m3 84 · m4 84 (interp-suite tally) · XFAIL 36 (out of scope). HEAD=a06554a. ✅ m3 brought to PARITY with m4 (76→82) by fixing the `x86_jcc_op` silent-`0x85` default (jz was encoded as jnz — inverted — in BINARY only; TEXT was correct). IR-IMMUTABLE rule = no IR access DURING EXECUTION of the emitted mode-3 image / mode-4 binary; the one EMISSION-time read of the IR is required & correct (the e50b089 entry-bomb misread was reverted). See HANDOFF-2026-06-13-IR-IMMUTABLE-MODE34.md.
**Gate every step:** `bash scripts/test_icon_rung_suite.sh` — m2 never decreases; m3/m4 trend up.
**Note:** the interp-suite reports m2=197 (`test_icon_rung_suite.sh --mode interp`); the prior "200" header was a different/combined count. Use the suite tally + an explicit before/after diff to judge regressions.

---

## M3/M4 gap — open work

**Failure categories (m3, ~104 FAIL):**
- **rc=134 (~28):** x86_bomb hit — missing BINARY arm. Run `./scrip --run foo.icn 2>&1` to see which bomb. ✅ `bb_to.cpp` descending TO (negative `by`) DONE (5dc543f). ✅ **pow `^` DONE (2831781)** — `const^const` constant-folded to `IR_LIT_F` in `lower_icon.c` (Icon `^` always real; interp's int^int via `**` path was the bug). rung19 pow_int/pow_real + rung26 int/assoc/zero/real_pow PASS all modes; m2 197→202, m3 70→76, m4 76→82. **NEXT rc=134 target = REAL ARITHMETIC native path** — `write(2.0*3.5)` (rung17), real relops (rung18), and `2^3+1` (rung26_pow_pow_expr, now `LIT_F + LIT_I`) all still bomb/decline: `descr_binop_opnd_slot` (emit_bb.c:1420) returns -1 for `IR_LIT_F`, so real/mixed operands never get a slot and the arith template only does int `add/sub/imul/idiv`. Fix: slot LIT_F operands + a real-arith template arm (call a DESCR-in/out `rt_*` arith, or SSE `addsd/mulsd` on the boxed doubles). Then `bb_call: unsupported call shape fn='push'/'read'/'iand'` (lists rung22, read rung27, math rung37) — builtins not wired into the native call path.
- **var reads (`bb_var` arm):** `libscrip_rt: BOMB — bb_var: unhandled arm` on global reads (rung21, rung25) — touches the OLD(frame-slot)/NEW(NV-dict) var-model switch (`g_icn_globals_nv`); riskier, consult GOAL-ICN-GLOBAL-NV.
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

**HEAD (SCRIP) = `521ab64`** — Icon m3 string-relops FIXED (m3 76→82, now at PARITY with m4). ROOT CAUSE
was a BINARY-vs-TEXT divergence (ONE-MEDIUM-INVISIBLE violation), NOT relop logic: `x86_jcc_op`
(`src/emitter/BB_templates/x86_asm.h`) had no `"jz"` (or `"js"`) case and fell through to `return 0x85`
(JNZ). So in the in-process BINARY medium `x86("jz",…)` emitted **JNZ — the inverted condition** — while
the TEXT medium emitted the literal `jz` mnemonic that GAS assembled correctly. The string-relop arm of
`bb_binop_relop` (`test eax,eax; jz ω`) was the visible victim: rung12 seq/sge/slt/sne + rung37
str_relop/strrelop_hello (6 programs) ran INVERTED in m3 only — m4 (linked) already produced the correct
output, which is why m4 was 6 ahead. `js` (1 use, signed-jump) was the same latent bug (0x85 vs 0x88);
`jnz` (5 uses) happened to be correct since the silent default WAS 0x85. FIX: completed the Jcc opcode
table (`jz/jnz/js/jns/jb/jae/jbe/ja` + signed aliases `jnae/jnb/jna/jnbe/jnge/jnl/jng/jnle`) and made the
default a LOUD `abort()` so any future missing condition code fails at emit time instead of mis-encoding.
DIAGNOSIS METHOD (reusable): numeric relops (which use `cmp`+`jge/jne`, never `test`+`jz`) PASSED m3 →
isolated the bug to `test eax,eax`/`jz`; then `as`+`gcc -no-pie -lscrip_rt` of the mode-4 `.s` proved m4
correct while m3 inverted → BINARY-only encoder bug. Verified: m2 202 (HARD, unchanged) · m3 76→82 · m4 82
unchanged; icon smoke 12/12/12 · prolog 5/5/5 · no-stack 0 · one-reg-frame 0 · bb_one_box 45 (pre-existing)
· unified 36. One file, +13/−7. Pushed onto a fast-moving remote (rebased clean over concurrent
Prolog/SNOBOL4/Raku landings). See HANDOFF-2026-06-13-SONNET-ICON-BB-JZ-ENCODER-FIX.md.

**Watermark — IR_SWAP `:=:` LANDED.** Native `IR_SWAP` for `x:=:y` now emits & runs in m3/m4
(rung15_real_swap_swap_basic + swap_str). New `bb_swap.cpp` four-port box: reads both var slots into
`rax:rdx`/`rcx:rsi`, cross-stores (left←rv, right←lv), writes result `rv`→own slot, `jmp γ`/`def β`/`jmp ω`
— pure `x86()` (template-pure; 0 byte-producers; not in the medium-invisible remaining list). `flat_drive_swap`
(emit_bb.c) resolves `op_sa`/`op_sb` via `bb_varslot_peek` + `op_off` via `bb_slot_alloc16`; `walk_bb_node`
(emit_core.c) dispatches `IR_SWAP→bb_swap()`; `icn_graph_native_emittable_mode` (scrip.c) admits IR_SWAP ONLY
when both operands are `IR_VAR` with sval (non-VAR-operand swaps like `a[i]:=:a[j]` clean-`[SMX]` decline, never
abort). Makefile: `bb_swap.cpp` in RT_PIC_SRCS + scrip: compile line. VERIFIED: m2 202 (HARD, unchanged, explicit
before/after suite diff) · m3 82→84 · m4 82→84 · icon smoke 12/12/12 · prolog 5/5/5 · no-stack 0 · one-reg-frame 0
· FACT gate 0. 6 files (+8 / new bb_swap.cpp). Both operands read BEFORE either store (classic swap); the wasted
operand-VAR reads from the producer chain are harmless (reads don't mutate). 5 files changed, +8, +1 new file.

**NEXT (highest-leverage native, prioritized):** (1) **REAL ARITHMETIC native path** (rung17 mul, rung18 relops×2,
rung26_pow_pow_expr — 4 progs). `descr_binop_opnd_slot` (emit_bb.c:1451) returns -1 for `IR_LIT_F`; the const-fold
path (emit_bb.c:2759 `LIT_F op LIT_F`) and write-binop slot path both miss real operands. Slot LIT_F operands +
add a real-arith template arm (SSE `addsd/mulsd/divsd` on boxed doubles, or DESCR-in/out `rt_*`). Failures:
`write(2.0*3.5)` → `[GZ-3] FATAL bb_call_write_binop: slot miss`; `1.5>2.5` → `bb_binop_relop: shape mismatch`.
(2) **`bb_every` four-port rebuild** — rc=124 generator-resume cluster (~12: rung01/02/03/14/19). (3) **list
builtins** (rung22, incl. 2 rc=139 segfaults on get/pull).


**HEAD (SCRIP) = `ae008c6`** — IR-IMMUTABLE "ACTUAL task" (execution-time IR-access audit) LANDED.
The mode-3/4 runtime proc registry no longer holds an `IR_t *`: dropped `void *entry` from
`rt_proc_t`, dropped the `entry` param from `rt_proc_register` (all 4 driver blocks now
`rt_proc_register(name,pn,np)`), and DELETED the IR-walker hook `g_rt_gen_proc_builder` /
`rt_proc_set_builder` (it installed `bb_build_flat`). Audit result: the active Icon/SNOBOL
execution path was already IR-free (dispatch via `p->fn`, an emitted code ptr); the builder was
never invoked — so this is enforcement-by-deletion (no live runtime IR-deref existed to NULL-bomb),
the `bb_bin_t`-ABOLISHED philosophy. The sanctioned mode-3 emission read `bb_build_flat(icn_root)`
is kept; the emitter is NOT bombed (that was the reverted e50b089). Remaining IR reads all
sanctioned: mode-2 interp (`IR_interp.c`), emission (`emit_bb.c`), Prolog `sm_interp_run`
(`resolution.c`). m2 interp 202 unchanged (HARD, explicit before/after diff empty); icon smoke
12/12/12; prolog 5/5+5/5; `test_gate_icn_no_stack`=0; `test_gate_icn_one_reg_frame`=0; the 45
`test_gate_bb_one_box` FAILs PRE-EXISTING (zero template files touched). 3 files, −26/+15. See
HANDOFF-2026-06-13-SONNET-ICON-BB-IR-IMMUTABLE-REGISTRY-LANDED.md.

**HEAD (SCRIP) = `8b9a58e`** — Reverted the e50b089 entry-bomb (CORRECTED understanding of IR-IMMUTABLE).
The rule is about EXECUTION, not emission: mode 3/4 require ONE full read of the IR at EMISSION time to
build the artifact (mode 3 → in-process image; mode 4 → `.s` source) — that read is required and correct.
The IR must only be untouched DURING EXECUTION of the emitted image/binary (no runtime helper deref'ing an
`IR_t *`, no IR pointer chased by the running generated code). The earlier reading ("emitter must never read
IR" → bomb the entry → disable native) was wrong and is reverted: native emission is restored and working
(`--run`/`--compile` emit & run again, rung26 pow → 1024.0/27.0). m2 interp HARD gate PASS=202; icon smoke
12/12 all three modes; prolog 5/5. Tally back at the pow-fold baseline m2 202 / m3 76 / m4 82. The ACTUAL
task is an audit of EXECUTION-time IR access (runtime `IR_t *` derefs reachable from a running emitted
program), NOT a teardown of the emitter — full corrected plan in HANDOFF-2026-06-13-IR-IMMUTABLE-MODE34.md.
Do NOT physically purge `emit_bb.c`; its IR read IS the sanctioned emission read.

**HEAD (SCRIP) = `e50b089`** — IR-IMMUTABLE rule enforced in mode 3/4. Per the long-standing rule (the IR
must never be touched/read/looked at in `--run`/`--compile`), both mode-3 and mode-4 entry blocks in
`src/driver/scrip.c` now execute `(*(volatile char *)NULL);` as their FIRST statement — before
`sm_preamble` or any `s2->bbp`/IR access — so the native emitter (`emit_bb.c` walkers, an inherently
IR-reading codegen) can never be reached. `--run`/`--compile` SIGSEGV (rc=139) immediately; `--interp`
(mode-2, the oracle) is untouched. **m2 interp HARD gate INTACT: PASS=202**; icon mode-2 smoke 12/12 +
prolog mode-2 smoke 5/5 (HARD). Mode-3/4 smoke arms 0 and the native-only gates (no-stack / one-reg-frame
/ bb_one_box) RED BY DESIGN — native is disabled pending rebuild. The physical purge of the now-dead
IR-walking code (emit_bb.c walkers + emit_core dispatch + flat-chain builders + the dead mode-3/4 dispatch
bodies below the bombs in scrip.c) is the next step — full inventory + removal order + rebuild contract in
**HANDOFF-2026-06-13-IR-IMMUTABLE-MODE34.md**. NOTE: this supersedes the prior m3/m4 tally tracking (m3 76 /
m4 82 at `2831781`) — those scores no longer apply while native is disabled.

**HEAD (SCRIP) = `2831781`** — Icon pow `^` constant-fold (single file, `src/lower/lower_icon.c`, +9 lines; NO template/emitter/runtime change). Icon `^` ALWAYS yields a real — the `.expected` files encode `2^10`→`1024.0`, not `1024`. The interp HAS a `^`→`REALVAL(pow)` branch (IR_interp.c:553) but Icon `^` (BINOP code 18) dispatches through the `**` path (IR_interp.c:549) which returns `INTVAL` for int^int, so `1024` printed — and with NO `.xfail` markers the pow rungs were real FAILs in ALL THREE modes. FIX: fold a fully-constant pow to `IR_LIT_F` at the lowering binop site (before `build(IR_BINOP)`), reusing the existing real-literal path end-to-end: m2 prints a `LIT_F` identically to a computed real, and native `bb_lit_scalar` already has a working `IR_LIT_F` arm storing `{DT_R, double-bits}` to `[r12+off]` (slotted at emit_bb.c:2576). `icn_const_step` (the existing const-extractor at lower_icon.c, used by TO-`by`) extended with a recursive `TT_POW` case so `2^2^3 = 2^(2^3) = 2^8` folds whole (right-assoc, inner first); `<math.h>` added for `pow()`; forward-decl of `icn_const_step` added at file scope. VERIFIED by the suite harness (not ad-hoc `tr`, which mis-adds a trailing `|`): rung19 pow_int/pow_real + rung26 pow_int/pow_assoc/pow_zero/pow_real_pow PASS interp+run+compile. `rung26_pow_pow_expr` (`2^3+1` → folds the `^` to `LIT_F(8.0)`, leaving `LIT_F+LIT_I` real+int add) still PASSes m2 but FAILs native — the real-arith gap, NOT a regression (was failing before). TALLIES by explicit before/after suite diff: **m2 197→202** (HARD gate UP — fold makes int^int correct everywhere), **m3 70→76**, **m4 76→82**. Smoke icon m2/m3/m4 12/12; prolog 5/5 all modes; `test_gate_icn_no_stack`=0; `test_gate_icn_one_reg_frame`=0. The 45 `test_gate_bb_one_box` FAILs remain PRE-EXISTING (untouched by a lowering change). **NEXT (own session): the REAL ARITHMETIC native path** (see the rc=134 line above) — unblocks rung17/18 and `2^3+1`; then native builtin call wiring (push/read/math). The architectural `bb_every` rebuild (below, 27e7dd8 entry) remains the standing fix for the rc=124 generator-resume cluster.

**HEAD (SCRIP) = `27e7dd8`** — (1) Deleted dead `if(((IR_t*)0))` block (81 lines) from `flat_drive_every` in `src/emitter/emit_bb.c` — literal `if(NULL)`, doubly dead (guard NULL + `IR_EVERY.ival` always 0); proven zero behavior change (m3 byte-identical before/after on rung01/07/09/16; smoke icon 12/12 ALL THREE MODES; prolog 5/5). (2) **FINDING (Lon, not fixed): `bb_every.cpp` is NOT a real EVERY box — it is worse than a no-op.** It emits only `<def β>; jmp ω` (no α, no γ), and the `def β` is a DUPLICATE of the `β:` label `flat_drive_every` already emits via `EMIT_PAIR_DEF_JMP` → redundant `β:`/`jmp ω` (confirmed in m4 asm: IR_EVERY `xchain0_n4_α:` falls through into a DOUBLED `xchain0_n4_β: jmp main_ω`). `every write(1 to N)` still works ONLY because the loop is carried by the TO generator box's self-resume back-edge + `flat_drive_every`'s flat chaining — the EVERY box is reached just once (exhaustion→ω). So the goal-directed EVERY drive/resume/exhaust logic lives in a DRIVER (`flat_drive_every`), not in the `bb_every()` TEMPLATE (against TEMPLATE-ONLY EMISSION), and the template is logic-empty. `bb_every()` IS called once via `EMIT_PAIR_FILL`→`emit_core.c` dispatch (a first "0 calls" probe was a STALE BINARY — force-rebuild the .cpp before trusting call-count probes). **NEXT STEP (own session): build a real four-port `bb_every` box mirroring canonical `ir_a_Every` (start→gen; expr.success→body; body.success/fail→expr.resume = the loop; expr.failure→ir.failure), move the topology out of `flat_drive_every`, kill the duplicate β stub; gate m2 HARD unmoved + m3/m4 loop rungs byte-checked.** See HANDOFF-2026-06-13-OPUS48-ICON-BB-EVERY-BOX-MISSING.md.

 `every`-conjunction with an embedded generator now resumes correctly. Two `src/lower/lower_icon.c` fixes (lowering only; NO template/emitter/runtime change): (1) `lower_every` `!BODY` loop-back — `loop_target` was `(gen_result->op==IR_CONJ)?E:…`, forcing a conjunction's success edge to the EVERY node, which (ival=0) returns γ and exits after ONE value; now `(gen_node && gen_node!=gen_result && gen_node!=ω && gen_node!=E) ? gen_node : E`, i.e. loop back to the embedded generator's resume — unifies the CONJ case with the already-correct `every f(gen)` CALL case (which is why `every write(1 to 5)` always worked: CALL.γ→TO). (2) relop BINOP — `op` was built with the outer `ω` as its fail port, so a false comparison (`1>2`) exited to the every fail instead of resuming its generative operand; added `if (IR_LIT(op).dval==1.0 && lβ && lβ!=ω && lβ!=op) ω_to(op, lβ)` (relops are codes 5–10, marked `dval=1.0`; `lβ`=left operand's resume). VERIFIED via a 4-layer ladder: `every write(1 to 5)`→1-5 (unchanged); `every (1 to 5)>2 & write("hit")`→hit×3 (was ×1); `every (x:=(1 to 5)) & write(x)`→1-5 (was just 1); `every (x:=(1 to 5))>2 & write(x)`→3,4,5 (was empty). `rung13_alt_alt_filter` FAIL→PASS. m2 196→197 by EXPLICIT before/after `--mode interp` diff = EXACTLY one line changed, ZERO regressions. Smoke icon m2 12/12 + prolog 5/5 HARD; `test_gate_icn_no_stack`=0; `test_gate_icn_one_reg_frame`=0; filter m3/m4 cleanly `[SMX] EXCISE` (sanctioned). The 45 `test_gate_bb_one_box` FAILs are PRE-EXISTING (identical on pristine 8b3eefb — emitter template entry-count gate, untouched by this lowering change). HEAD shown is post-rebase onto remote (a430139: PL nb_setval + RAKU user-sub landings came in concurrently; fix re-verified green after rebase).

**OPEN — `cross_arg` multi-generator CALL args (NEXT, separate/deeper bug — NOT FULL-18):** `every write(1|2, ":", 3|4)` → `1:3, 334, 2:3, 334` (want `1:3,1:4,2:3,2:4`); `rung13_alt_alt_cross_arg` + `rung13_alt_alt_cross_arg_sideeffect` still FAIL. ISOLATED precisely: `write((1|2)||(3|4))` (concat, ONE arg) is CORRECT (13,14,23,24) — the conjunction/concat resume path is fine; `write(1|2, 3|4)` (TWO generator args) is BROKEN (13,**34**,23,**34**). Instrumented the CALL: it takes the **`is_deep=1` ag_ring-peek path with `has_gen_arg=0`** (the cross-product odometer block at IR_interp.c ~2576 is NEVER entered — multi-arg generators are lowered as flat chained producer boxes, so `ir_call_arg` sees them already-evaluated, not as generators). Resume is driven by flat back-edges (`CALL.γ → rightmost gen ALT`), but the ag_ring is not maintained across the literal-separated args on carry → the left arg's ring slot goes stale (the leading "3" in "334"). FIX LIVES IN: the `is_deep` CALL ring protocol and/or `lower_call`'s flat-chain arg wiring — a ring-protocol fix, materially larger than FULL-18, likely a fresh session. (Graphs: `--dump-bb` on `rung13_alt_alt_cross_arg` shows two ALT nodes whose `ω` both point at the FIRST ALT — the carry order is the suspect.)

 `flat_drive_case` (emit_bb.c:1668) was stale: it read the OLD IR_CASE shape, but IRD-3b (4699ab8/fbfd71c) had rewired the lowering to operand-wrappers (operands[0]=selector; operands[1..]=IR_LIT_NUL arm wrappers, [key,val] normal / [val] default — the shape the interp at IR_interp.c:4132 reads, which is why m2 passes all four rung33 cases). The emitter walked `operands[0]->γ.node` off the selector as a phantom key/val chain → garbage nodes → segv on int/str/arith (no_default happened to trip a gate and excise). FIX: added explicit `IR_CASE → return 0` to `icn_graph_native_emittable_mode` (scrip.c:267 — the REAL m3/m4 routing gate, permissive-by-default; `icn_kind_native_stub` is DEAD/never-called, do not edit it). Case programs now loudly `[SMX] EXCISE` (sanctioned interim state) instead of segfaulting. ALSO implemented `rt_case_eq(const DESCR_t*sel, const DESCR_t*key)` (rt.c:399) — was a dead abort-stub with a wrong single-DESCR sig; now int-by-value when both DT_I else VARVAL strcmp, matching the interp === — the first building block for a future native CASE. m2 200 (HARD, unchanged) · m3 45→65 · m4 51→71 (the +deltas vs the fb2daea watermark are cumulative incl. Pascal/IRD landings on the real HEAD; my change is segfault→excise, m2-neutral). prolog 5/5.

**Next for native CASE (clearly scoped):** rewrite `flat_drive_case` to the operand-wrapper shape (mirror the interp loop): eval selector via walk_bb_flat → its slot; per arm eval key → slot, `call rt_case_eq` with `lea rdi,[r12+sel_off]; lea rsi,[r12+key_off]`, test rax, je arm-value; arm value evals then COPIES its 16-byte DESCR slot into the CASE node's own slot (`bb_slot_get(case_node)`) before jmp γ; trailing 1-operand wrapper = default → γ; no match no default → ω. The compare + copy must go through a `bb_case_arm` template reached via EMIT_PAIR_FILL (driver has no direct emit primitives; all bytes live in templates). Remove IR_CASE from the gate the moment the template lands.

**Key intel:** `icn_ring_to_tree` returns NULL if chain has IR_BINOP or IR_LIT_I → falls to `descr_flat_chain_build(bbg->entry)`. `--dump-bb` does NOT show `operand_aux`. DESCR_t = {DTYPE_t(4)+slen(4) in low 8 bytes; int64/ptr in high 8 bytes} — passed as rdi:rsi pair. Asm chain node indices (`xchainN_nK_*`) are CHAIN POSITIONS, not graph node ids. m2 walking the same graph correctly = graph is right, bug is in the flat emitter — a safe class to fix (cannot move the m2 HARD gate).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
