# GOAL-ICON-FULL-PASS.md — Icon: m3/m4 → 283/283 (full pass, parity)

**Status:** m3 **132/283** · m4 **132/283** · FAIL 23 · XFAIL 36 · EXCISED 92. HEAD(SCRIP)=`c26f89f`.
mode-2 `--interp` is DELETED (GOAL-DE-INTERP); the suite still invokes it and reports phantom m2 FAIL across the board — **ignore m2, gate on m3/m4**. m3 and m4 FAIL sets are currently identical.
**Gate every step:** `bash scripts/test_icon_rung_suite.sh` — m3/m4 must not regress. A net +PASS can hide an EXCISE→FAIL: always do an explicit FAIL-name **and** EXCISED-name diff vs baseline in BOTH modes (capture single-mode VERBOSE output: `--mode run`/`--mode compile`, grep `^FAIL`/`^EXCISED`).

---

## Open work — current 23 FAIL (m3==m4), by category

- **rc=134 — missing native arm / unsupported call shape (`x86_bomb`).** Probe with `./scrip --run foo.icn 2>&1`.
  - `rung22_lists_push_put_size`, `rung22_lists_put_bang` — list builtins (push/put) not wired into the native call path.
  - `rung08_strbuiltins_find`, `rung08_strbuiltins_find_gen` — `find` builtin.
  - `rung30_builtins_misc_seq`, `rung32_strretval_strret_every`, `rung37_proc_lookup` — misc builtin/call shapes.
  - `rung02_proc_fact` — user-proc recursion depth 4096 (m3 silent-empty / m4 depth).
- **rc=124 — generator-resume / timeout.**
  - `rung03_suspend_gen{,_compose,_filter}` — `suspend` (canonical `ir_a_Suspend`; `ir_Succeed`/resume into body).
  - `rung14_limit_limit_{large,to,zero}` — `limit` (`ir_a_Limitation`: counter decremented on resume, `>0` gate).
  - `rung19_pow_toby_real_toby_{neg,pos}` — **real TO/BY** (`bb_to` real-step arm); generator-retry track.
- **rc=139 — segfault.**
  - `rung22_lists_get`, `rung22_lists_pull` — list builtins (get/pull).
  - `rung31_sort_sort_{already_sorted,every}` — `sort()` (`rt_list_sort`/`rt_table_sort` in `aggregates.c`).
- **wrong-output.**
  - `rung13_alt_alt_cross_arg{,_sideeffect}` — multi-generator CALL args `write(1|2,3|4)` → `is_deep` ag-ring stale on carry; `lower_call` flat-chain arg wiring. Materially larger (own session). `write((1|2)||(3|4))` (one concat arg) is already correct — the bug is two generator args, not the resume path. `--dump-bb` shows both ALT ω's pointing at the FIRST ALT (carry-order suspect).
  - `rung29_builtins_type_mixed` — `type(x)`/`image(x)` of a var → null/&null: builtin-call arg not marshalling the VAR value (arg DESCR uninitialised). `image(cset)` also returns &null (same arg-marshal class).

**NEXT real-arith (binop path landed `c26f89f`):** native real-POW — route `BINOP_POW`→`bb_binop_arith`, add `BINOP_POW` to `binop_is_num_real`; `rt_num_arith` already computes `REALVAL(pow(ld,rd))`. Unblocks `rung19_pow_toby_pow_var` (today EXCISED). `real_relop_goal` (`every write(3.0<(2.5|3.5|4.5))`) stays EXCISED — gen-alt resume (`cross_arg` track).

---

## Session Setup

```bash
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/test_smoke_icon.sh        # m3 12/12 · m4 12/12 HARD (m2 line is phantom — ignore)
bash scripts/test_smoke_prolog.sh      # m3 5/5 · m4 5/5 HARD (m2 phantom)
bash scripts/test_gate_bb_one_box.sh
# Extract refs if absent:
unzip -q /mnt/user-data/uploads/2-icon-master.zip -d refs/
unzip -q /mnt/user-data/uploads/3-jcon-master.zip -d refs/
```

## Gate after every step

```bash
bash scripts/build_scrip.sh && make libscrip_rt
bash scripts/test_icon_rung_suite.sh   # m3/m4 must not regress (m2 phantom)
bash scripts/test_gate_bb_one_box.sh
bash scripts/test_smoke_prolog.sh
bash scripts/test_gate_icn_no_stack.sh ; bash scripts/test_gate_icn_one_reg_frame.sh   # == 0
```
The full three-mode suite ×283 can exceed an 8s/30s timeout under load — run one mode at a time (`--mode run`, then `--mode compile`) with an explicit `timeout`.

## Canonical source rule

Port topology → `refs/jcon-master/tran/irgen.icn`. Runtime → `refs/icon-master/src/runtime/*.r` (`ocomp.r`, `fstranl.r`, `oarith.r`, `oref.r`). The (now-deleted) m2 oracle was a transcription; canonical wins.

## Key intel (reusable)

- `DESCR_t` = {DTYPE_t(4)+slen(4) low 8 bytes; int64/ptr high 8 bytes}; passed/returned as the **rdi:rsi** (args) / **rax:rdx** (return) pair — the 2nd eightbyte is INTEGER-class even when it holds a `double`.
- `icn_ring_to_tree` returns NULL when the chain has IR_BINOP or IR_LIT_I → falls to `descr_flat_chain_build(bbg->entry)`. `--dump-bb` does NOT show `operand_aux`. Asm chain-node indices (`xchainN_nK_*`) are CHAIN POSITIONS, not graph node ids.
- The REAL native gate is `icn_graph_native_emittable_mode` (scrip.c, permissive-by-default); `icn_kind_native_stub` is DEAD/never-called — do not edit it. To EXCISE a kind, reject it in the gate.
- **m3 binary tolerates duplicate labels (last-wins); m4 `as` rejects them (rc=1).** Always assemble the m4 `.s` standalone (`./scrip --compile --target=x86 f.icn > f.s; as f.s -o f.o`) whenever a kind passes m3 but not m4.
- Globals are NV-only (the `--icn-globals` switch + `g_icn_globals_nv` were removed, `b11d3a7`): global read/assign route through the shared NV dictionary in every mode; locals keep frame slots.
- RT = value, BOX = ports (no-duplicated-logic law): a builtin/arith helper takes/returns `DESCR_t` with no α/β/γ/ω; the box marshals args, `call`s it, wires the four ports.

---

## Watermark

**HEAD (SCRIP) = `c26f89f`** — Icon native **real-arithmetic binops + relops** (m3/m4 127→132, +5 each). FAIL 25→23, EXCISED 95→92 (both modes). FAIL→PASS: `rung18_real_relop_mixed_relop`, `rung18_real_relop_real_gt`; EXCISED→PASS: `rung17_real_arith_real_add`, `rung18_real_relop_real_eq`, `rung18_real_relop_real_lt`; `rung19_pow_toby_pow_var` baseline→EXCISED (Fix 1, not a regression). Verified by explicit FAIL-name AND EXCISED-name diffs in both modes = zero new FAIL, zero EXCISE→FAIL. Landed the prior-session WIP patch (`git apply` clean over moved HEAD) + two fixes: **Fix 1** new `graph_has_pow()` in `scrip.c` (the WIP relaxed `local_assign_rhs_ok_g`'s LIT_F guard to `return 1`, admitting POW-bearing graphs that route to generic `IR_BINOP` not the real arm → garbage; restored `return !graph_has_pow(g)` so POW-bearing LIT_F-assign stays EXCISED). **Fix 2** skip re-walking an already-slotted child in `flat_drive_binop_tree` (`emit_bb.c`) — the root_node tree path re-walked LIT_F chain operands → duplicate `bb<id>_α`; now `if (bb_slot_get(child)>=0) emit_jmp_label(<child>_done,JMP_JMP)`, `descr_binop_set_slots` reuses the chain slot (verified `real_gt` `.s` has zero dup labels + assembles clean). Path is value=RT/ports=BOX: `rt_num_arith(DESCR,DESCR,op)` (int/real/mixed coercion, div0→FAILDESCR) + `rt_jct_relop` additive real branch + `op_num_real` flag + `descr_binop_set_slots` + real arms in `bb_binop_arith`/`bb_binop_relop` (pure `x86()`, 0 byte-producers, no `bb_bin_t`). icon smoke 12/12 m3+m4 · prolog 5/5 m3+m4 · no-stack 0 · one-reg-frame 0 · FACT 0 · g_vstack 0. Rebased clean TWICE over concurrent landings, re-gated identical each time. 7 files. See HANDOFF-2026-06-15-CLAUDE-ICON-BB-REAL-ARITH-LANDED.md.

**HEAD (SCRIP) = `176ecda`** — Icon native **IR_CASE (case-of)**: `rung33_case_*` 5/5 both modes (m3/m4 122→127). Six coordinated fixes: `descr_chain_arity IR_CASE→0` (consumer CALL adopts the result); `lower_icon.c TT_CASE` pushes the operand RESULT node; `case_slot_binop_operands()` hydrates arm-value operands from `operand_aux`; `scrip.c rhs_kind_ok` admits `IR_CASE` local-assign RHS; `bb_case_arm.cpp` drops a redundant α-label; `flat_drive_case` stops re-walking the selector and gives each take box a unique β (both were m4 dup-label `as` breakers). `rt_case_eq` re-landed from attic. See HANDOFF-2026-06-15-CLAUDE-ICON-BB-CASE-NATIVE-LANDED.md.

**Earlier landings (terse — full detail in git log + the named HANDOFF-* files):**
`9354db7` local IR_VAR reader aliases its varslot (shared frame slot, not a private copy) + cset literals canonicalized (sorted/deduped) at lowering — m3/m4 118→122. ·
`1fcd8c5` deterministic builtins (read/iand/…) added to `rt_builtin_is_known` allow-list + native subscript `s[i]` + constant unary-minus fold + global-VAR reads wired to NV — m3/m4 87→104. ·
`521ab64` completed the Jcc opcode table in `x86_asm.h` (`jz` had fallen through to `0x85`=JNZ — a BINARY-only inverted-condition bug; default now `abort()`) — m3 string-relops 76→82, parity with m4. ·
IR_SWAP `:=:` native (`bb_swap.cpp`, both VAR operands). ·
`1b71e43` real-arith CONSTANT-fold (ADD/SUB/MUL/DIV/MOD/POW of all-constant operands → `IR_LIT_F`) + guarded LIT_F local-assign — m3/m4 84→87. ·
`2831781` pow `^` constant-fold (`^` is always real in Icon) — m3 70→76, m4 76→82. ·
`bb_every` rebuilt as a real four-port box (canonical `ir_a_Every` has no `ir.success`; loop edges live in the child subtree; α/β both → ω). ·
`ae008c6` IR-IMMUTABLE execution-time audit: dropped `void *entry` from `rt_proc_t`, deleted the `g_rt_gen_proc_builder` hook (the active path was already IR-free; emission-time IR read is the ONE sanctioned read). ·
generator-resume fixes in `descr_flat_chain_build` (cross-product odometer; ω routes into an earlier generator's β; EVERY-ω resumes the innermost gen) + `lower_every` conjunction/relop loop-back.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
