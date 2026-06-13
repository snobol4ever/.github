# HANDOFF-2026-06-13-OPUS48-RAKU-BB-USER-SUB-CALLS-LANDED.md

## Session: GOAL-RAKU-BB — user-sub m3/m4 calls landed; class_method scoped with confirmed specifics

**SCRIP HEAD at open: `242e1d0`. At close: `b1d58ae` (2 commits landed). `.github` updated (this doc + watermark).**

Gates at close: Raku m2 **31/31**, m3 **25 PASS / 0 FAIL / 6 EXCISED**, m4 **25 / 0 / 6** (no regression).
**Icon m2/m3/m4 = 12/12/12** (was 12/10/10 — `proc_zeroarg`+`proc_recursion` flipped green via the shared
`bb_return` fix below). SNOBOL4 m4 **7/7** HARD. NFA oracle **5/5**. `g_vstack`=0. Concurrency audit: 5
pre-existing VIOLATIONs (FACT-RULE md5 drift + stale `lower.c` path), identical baseline-vs-change — NOT
introduced this session.

---

## LANDED — commit `ca031f6` (Bug 1) + `b1d58ae` (Layers A+B)

### Bug 1 (`ca031f6`) — `rk_discover_procs` is the SOLE Raku registrar
`src/driver/polyglot.c:110-111`: extended the Raku-exclusion guard from `_is_raku_call` (only `TT_FNC`) to
`_is_raku_owned` (`TT_FNC || TT_SUB_DECL`). Raku subs were registered TWICE (`polyglot_init` +
`rk_discover_procs`) → duplicate `icn_proc_<name>_α/β/γ/ω/α_body` labels → `as` rejected every sub-containing
Raku m3/m4 program. Now single registration. Icon/Pascal `TT_PROC_DECL` untouched. Repro `sub f($a){return
($a+1)*$a;} say f(3);` now assembles clean (was: 2× `icn_proc_f_α`). This is the diagnosis from
`HANDOFF-2026-06-13-OPUS48-RAKU-BB-PROC-DOUBLE-EMIT-DIAGNOSIS.md`, Option A — landed verbatim.

### Layer A (`b1d58ae`, `lower_raku.c`) — user-proc value-calls get `dval=3.0`
A non-visible Raku call (a call used as a VALUE, e.g. `g(3)` as an arg to `say`) went through
`lc_call_argblks(nd, 2.0, …)` → `dval=2.0`. A registered user-proc with `dval=2.0` fell through the
descr-chain dispatch (`bb_call.cpp:593-595`: not a known builtin, not `__rk_bool`) to
`x86_bomb("IR_CALL dval=2 descr-chain arm aborted")`. **Icon already distinguishes** (`lower_icon.c:82`:
`is_idx_or_list ? 2.0 : 3.0`) — user-proc calls get `3.0` and route to the proven `bb_call_proc_staged_str`
(`bb_call.cpp:598`). Fix mirrors Icon: new `rk_proc_known(name)` scans `g_stage2.proc_table` (populated by
`rk_discover_procs` BEFORE bodies/main lower); in the `case TT_FNC` value path, after `lower_rcall`, set
`IR_LIT(*res).dval = 3.0` iff `rk_proc_known(nm)`. Builtins stay `2.0`. Reuses the existing emit path — no
new template, no NO-DUPLICATED-LOGIC violation. (Note: `lc_call_argblks` writes `dv` ONLY into the call
node's `dval`; nothing in the arg-blocks depends on it, so the post-hoc override is safe.)

### Layer B (`b1d58ae`, `bb_return.cpp` + `emit_core.c`) — IR_RETURN jumps to γ on a normal return
**This was the real second blocker — NOT the watermark's "Bug 2".** `bb_return()` (the descr template,
used by both Icon and Raku via `descr_flat_chain_build_proc_text`, `scrip.c:2300`) hardcoded
`x86("jmp", "ω")`. For a proc body, the chain's last node is the `return`; its ω resolves to the proc's FAIL
exit (`icn_proc_<name>_ω`), which OVERWRITES `frame[0]` with FAILDESCR (99) — clobbering the return value
the template just stored. So a proc ending in `return` always returned failure. `main()` (ending in `say`,
which succeeds→γ) worked, masking the bug. Fix mirrors the GVAR-path convention exactly
(`emit_bb.c:2953`: `dval==2.0 ? slab_fail : slab_succ`): `emit_core.c:463` now sets
`g_emit.op_dval = IR_LIT(nd).dval`; `bb_return.cpp` final jump is `IF(_.op_dval==2.0, jmp ω) +
IF(_.op_dval!=2.0, jmp γ)`. Icon/Raku returns have `dval=0.0` → γ. Template stays `x86()`-only (compliant
with ONE-MEDIUM; `bb_return.cpp` is NOT in the medium-invisible REMAINING list).

**SHARED-BOX NOTE for the Icon session:** Layer B is in shared `bb_return.cpp`/`emit_core.c`, not a Raku box.
It is a bug fix (not an ABI/signature change → no FACT-RULE body edit needed). It moved **Icon m3/m4 from
10/12 to 12/12** (`proc_zeroarg`, `proc_recursion` were Icon's only two m3/m4 FAILs and are now PASS). This
is the concurrency model's win-win: a shared-scaffolding fix that helps a peer. Verified: SNOBOL4 7/7,
NFA 5/5 unchanged.

Mechanism proof: `sub f($a){return ($a+1)*$a;} say f(3);` → **12** in m3+m4; `sub g($a){return
($a+1)*($a+2);} say g(3);` → **20** in m3+m4.

---

## CORRECTION RECORD — the watermark's "Bug 2" framing was PARTLY WRONG

The prior watermark said the next blocker (after Bug 1) was a "nested-BINOP operand double-emission" in
`scale`, repro-able with `sub g($a){return ($a+1)*($a+2);}`. **That repro does NOT double-emit** — `sub g`
assembles clean (no dup labels) once Bug 1 is fixed. Its real failure was Layer B (return→ω). So:
- The double-emission is NOT triggered by nested binops in general.
- It IS triggered specifically by **FIELD_GET operands** in the nested binop (`($!x+$!y)*$factor` in
  `scale`) — confirmed by the probe below. Keep "Bug 2" as a class_method-only blocker, not a general one.

---

## REMAINING — `class_method` EXCISED→PASS (the only non-Group-A target). Confirmed specifics from a throwaway probe.

Repro (`/tmp/cm.raku`): `class Point { has $.x; has $.y; method sum(){return $!x+$!y;}
method scale($factor){return ($!x+$!y)*$factor;} } sub main(){ my $p=Point.new(x=>3,y=>4); say($p.x);
say($p.sum()); say($p.scale(2)); }`. m2 oracle = **3 / 7 / 14** (correct). m4 EXCISES via
`icn_graph_native_emittable` (`scrip.c:2245`).

**Probe (gate temporarily relaxed to admit `IR_CALL dval==1.0` + `IR_FIELD_GET` as ASSIGN rhs, then
reverted) revealed BOTH remaining gaps at once:**

1. **GATE — `icn_rhs_kind_ok` (`scrip.c:202`).** `my $p = Point.new(...)` lowers to `IR_CALL obj_new
   dval=1.0 ival=5`; `.x`/`.sum()`/`.scale()` are `meth_call dval=1.0`. `icn_rhs_kind_ok` admits only
   `IR_CALL` dval 0.0 (207) / 2.0 (208) → a `dval=1.0` assign-rhs is rejected → EXCISE before emit is even
   reached. FIX: add `if (r->op == IR_CALL && IR_LIT(r).dval == 1.0) return 1;` and
   `if (r->op == IR_FIELD_GET) return 1;` to `icn_rhs_kind_ok`; add `IR_FIELD_GET` to `icn_assign_safe_kind`
   (`scrip.c:258`). (Verify `obj_new`/`meth_call` dval=1.0 have a working assign-store emit path — the
   watermark claims walk_bb_node already handles `obj_new`/`meth_call`/`write`/BINOP/RETURN; FIELD_GET is the
   only missing leaf.)

2. **EMIT — FIELD_GET is `kind=123` UNHANDLED in `walk_bb_node` (`emit_core.c`).** With the gate relaxed, the
   emitter prints `; [walk_bb_node: kind=123 unhandled]` (5×). FIX (watermark Group-C item 2): add
   `case IR_FIELD_GET` to `walk_bb_node`, set `g_emit.op_a_slot`=object operand slot (auto via
   `bb_slot_get(operands[0])`), `g_emit.op_sval`=field name, `g_emit.op_off = bb_slot_alloc16(nd)`; new
   `bb_field_get.cpp` template sealing field-name→rdi, obj→rsi:rdx, `call dat_field_get`
   (`by_name_dispatch.c:3132`), store rax:rdx→`op_off`, jmp γ. Wire: decl in `bb_templates.h` + Makefile
   `RT_PIC_SRCS` + `scrip` compile rule. (Descr-chain style — `_.op_a_slot` resolved fine in a prior session
   per the watermark.)

3. **DOUBLE-EMISSION (the real "Bug 2") — CONFIRMED still present, FIELD-GET-operand-specific.** With the
   gate relaxed, `/tmp/cm.s` has **duplicate labels `bb94832_α`, `xchain29_n12_β`, `xchain29_n17_β`** — the
   nested `($!x+$!y)*$factor` in `scale` emits a FIELD_GET operand twice (once as a chain node, once as the
   `*`-BINOP child via `flat_drive_binop_tree`). `sum()`'s flat `$!x+$!y` is likely fine; `scale` breaks.
   Start at `codegen_flat_chain_body` queue-build (`emit_bb.c:3057-3071`, which enqueues a BINOP's `ω.node`)
   × `flat_drive_binop_tree` (`emit_bb.c:1403`, which ALSO walks `bb_child0/1`). The chain walker must not
   enqueue an operand that `flat_drive_binop_tree` will itself emit. **Order: do the FIELD_GET template
   (1+2) AND the de-dup (3) together, then verify `class_method` EXCISED→PASS, m2 31/31, no peer regression,
   no silent m3/m4 FAIL.**

**GROUP A (5) — `gather_take/map_range/grep_range/map_over_gather/grep_over_gather` — DEFERRED on Icon GZ-7
(IR_ASSIGN ζ-slot store). DO NOT ATTEMPT.**

---

## Files touched (committed)
- `src/driver/polyglot.c` (Bug 1) — `ca031f6`
- `src/lower/lower_raku.c` (Layer A: `rk_proc_known` + fwd-decl + dval override) — `b1d58ae`
- `src/emitter/BB_templates/bb_return.cpp` + `src/emitter/emit_core.c` (Layer B) — `b1d58ae`

## ORDER OF WORK for next session
1. class_method gate (item 1) + FIELD_GET template (item 2) + double-emission de-dup (item 3) — together.
2. Re-prove: Raku smoke (expect class_method EXCISED→PASS → m3/m4 26/0/5), Icon (HARD, must stay 12/12),
   SNOBOL4 (HARD 7/7), NFA oracle (5/5). Then commit + push (`.github` last).
3. GROUP A stays deferred (GZ-7).
