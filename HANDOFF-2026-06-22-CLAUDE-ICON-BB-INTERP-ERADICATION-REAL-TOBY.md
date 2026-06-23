# HANDOFF — GOAL-ICON-FULL-PASS (Claude Sonnet 4.6)
## Dead interpreter eradication + real TO/BY native LANDED (`e928643`). Suite 142→144 m3+m4. All gates green.

**SCRIP HEAD: `e928643`** (pushed). **m3/m4 = 144/283**, FAIL 14, XFAIL 36, EXCISED 89. All FACT gates green (no-stack 0, one-reg-frame 0, icon smoke 12/12, prolog 5/5 m3+m4).

---

## WHAT LANDED

### 1. Dead interpreter eradication — gen.h + emit_bb.c + gen_runtime.h/c + resolution.h

There was NO interpreter (GOAL-DE-INTERP closed), but dead remnants remained:

- **`gen.h`**: stripped 22 dead AST-interpreter state structs (`initial_state_t`, `intlit_state_t`, `strlit_state_t`, `proc_call_state_t`, `repalt_state_t`, `while_state_t`, `section_gen_state_t`, etc.). Kept only `BinopKind` enum + `tree_t` forward decl.
- **`emit_bb.c`**: deleted 34 dead `gen_bb_*(void*, int)` extern declarations (`gen_bb_initial`, `gen_bb_global`, `gen_bb_if_bb`, `gen_bb_link`, `gen_bb_intlit`, `gen_bb_proc_call`, …) — all from the abolished brokered/interpreter calling convention.
- **`gen_runtime.h`**: deleted `bb_node_t gen_bb_pump_proc_by_name` (dead).
- **`gen_runtime.c`**: deleted `extern bb_node_t gen_bb_make_proc_box` (dead).
- **`resolution.h`**: deleted `bb_node_t resolve_bb_once_proc_by_name` (dead).

Build clean. No behavioral change.

### 2. Real TO/BY native (+2: rung19_pow_toby_real_toby_neg + pos)

**Root cause:** `bb_to.cpp` had only integer comparison/step logic. Real TO/BY (`IR_LIT(pBB).sval == "ar"`) fell into the integer template → infinite loop (rc=124).

**Fix:**
- `flat_drive_to` in `emit_bb.c`: sets `g_emit.op_num_real = 1` when `sval == "ar"`; claims 16B counter slot (type+val DESCR) instead of 8B for the real case.
- `bb_to.cpp` real branch: uses `rt_jct_relop(cur, limit, BINOP_LE/GE)` for bound check and `rt_num_arith(cur, by, BINOP_ADD)` for step increment. RO seals: `L(0)` = DT_R (=7), `L(1)` = double bits of by-step. **Loop label is `L(10)`** to avoid collision with RO data labels `L(0)`/`L(1)` (duplicate label was the SEGV cause — m3 binary last-wins corruption).

**Verified:** `1.0 to 2.0 by 0.5` → `1.0 2.0` (pos); `3.0 to 1.0 by -1.0` → `3.0 2.0 1.0` (neg). Both modes.

### 3. IR_RASGN lvalue pre-registration fix

`flat_drive_rasgn` slot collision: `IR_RASGN` lvalue var was not in the `codegen_flat_chain_body` pre-registration sweep (which only covered `IR_ASSIGN` variants). Added `IR_RASGN` operand[0] to the sweep. This is a prerequisite for ungating BENCH-F2 (`<-`).

### 4. flat_drive_initial restructured (bb_initial.cpp scaffolded, NOT yet wired)

`flat_drive_initial` now passes `g_emit.op_sc = id` and adds `mark_done` label as pair[2]→lbl_γ, routing body success to `mark_done` (not directly to lbl_γ). `bb_initial.cpp` created — **NOT yet dispatched from `emit_core.c`** (IR_INITIAL still gated to EXCISE in `scrip.c`). The done-flag approach needs `bb_initial.cpp` to emit an inline `.quad 0` RO-data flag + branch, with `mark_done:` setting flag=1 before jmp γ. Blocked on: emit_core.c dispatch case + scrip.c gate removal.

---

## REMAINING 14 FAILs (m3 == m4)

| Tests | Error | Root cause |
|-------|-------|-----------|
| `rung02_proc_fact` | rc=134 depth | recursion depth (4096 frame limit) |
| `rung03_suspend_gen` ×3 | empty/rc=124 | IR_SUSPEND/EVERY co-routine wiring incomplete |
| `rung08_strbuiltins_find_gen` | rc=124 | `find` as generator needs resumable call state |
| `rung13_alt_alt_cross_arg` ×2 | wrong output | multi-gen CALL args; is_deep ag-ring stale on carry (BENCH-F3) |
| `rung14_limit_*` ×3 | rc=124 timeout | `flat_drive_limit` has no counter (BENCH-F2 prereq) |
| `rung22_lists_push_put_size` | wrong output | `rt_size_d` returns frame-slot count not list frame_size |
| `rung30_builtins_misc_seq` | rc=134 abort | `seq` IR_CALL_BUILTIN not accepted by flat_drive_limit |
| `rung32_strretval_strret_every` | rc=134 abort | dv=1.0 userproc chain not routed to flat_drive_call_userproc |
| `rung37_proc_lookup` | rc=134 abort | `proc()` builtin returning fn value; needs byname dispatch |

---

## NEXT STEPS (priority order)

### 1. rung22 rt_size_d list bug — +1, ~15 min
`rt_size_d` called with the SIZE node's 3 frame args (tag, slen, ptr) not the list's `frame_size` field. Fix in `src/runtime/by_name_dispatch.c`: when DESCR is DT_DATA with gen_type=="list", return `FIELD_GET_fn(v,"frame_size").i`. Verify: `[]:=0, [1,2]:=2`.

### 2. rung32 dv=1.0 userproc routing — +1, ~20 min
In `walk_bb_flat` IR_CALL descr-chain: before the existing `dv==3.0` check, add: if `dv==1.0 && sval && rt_proc_is_registered(sval)` → `flat_drive_call_userproc`. Verify: `tag("x")` → correct.

### 3. IR_INITIAL native — +multiple (queens depends on it)
Complete `bb_initial.cpp`: emit `.quad 0` done-flag (use `L(10)` for the flag def to avoid collision with pair machinery), α: RIP-relative load + test + branch to pair[1] (body) or pair[0] (γ). `mark_done:` (pair[2] define): write 1 to flag + jmp γ. β (pair[3]): jmp ω. Add dispatch to `emit_core.c` and remove `IR_INITIAL` gate in `scrip.c`.

### 4. IR_RASGN ungate — queens dependency
Gate at `scrip.c:293` can be removed once RASGN tested clean. Repro to verify: `x:=5; y:=1; (y <- x) & write(y)` → `5`. Check `op_a_slot` is now correctly resolved (pre-registration fix landed).

### 5. limit `\` counter — +3, ~1 hour
New `bb_limit.cpp` template + `flat_drive_limit` counter logic. Canonical: `ir_a_Limitation` (irgen.icn:113).

---

## KEY INTEL

- **Real TO/BY loop label**: must use `L(10)` (or any N≥2 for 2 RO seals); `L(0)` and `L(1)` are consumed by `x86_ro_seal_q`. Mixing loop and RO labels on the same uid → GAS dup-label error in m4 / binary corruption in m3.
- **bb_initial done-flag**: can use `L(10)` for the `.quad 0` (no RO seals used) and `L(11)` etc. for any needed internal labels. The EMIT_PAIR mechanism: pair[0]=lbl_γ (skip), pair[1]=body_entry (run), pair[2].define=mark_done→pair[2].jmp=lbl_γ (set flag+continue), pair[3].define=lbl_β→pair[3].jmp=lbl_ω (β arm).
- **RASGN pre-reg**: fixed. `flat_drive_rasgn` now correctly resolves both dest-var and rhs-var slots because dest-var is pre-registered before BFS walk order matters.
- **`bb_node_t`** remains in `bb_box.h` and `lower.h` — it's the native code ptr struct, not interpreter. `gen.h` no longer has it (stripped all dead interpreter state).

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
