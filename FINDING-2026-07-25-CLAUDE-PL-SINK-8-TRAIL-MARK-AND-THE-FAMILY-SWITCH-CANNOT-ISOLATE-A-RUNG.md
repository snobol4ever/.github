# FINDING 2026-07-25 (s146) — PL-SINK-8 `$trail_mark` LANDED; and the ONE-SWITCH A/B OVERSTATED THIS RUNG BY 30×

**Rung:** PL-SINK-8 (`$trail_mark`) of the PL-SINK ladder. **Result:** landed, gated, **1.056× (~5%)** on a mark-dense nrev shape.
**The lesson that outlives the rung:** the family kill switch `SCRIP_NO_SINK` **cannot measure a rung**, and using it to do so inflated this rung's own number from a true **1.056×** to a reported **1.59×**. Every rung after SINK-1 is exposed to this. See §3 — it is the reason this FINDING exists.

---

## §1 WHAT LANDED

`$trail_mark` was ~12% of the s145 45-sample profile for a leaf that computes `return t->top`. The load was never the cost; the **ceremony** was. `rt_pl_dop_trail_mark` (by_name_dispatch.c:1546) does: save `g_plw_unwind_floor` → call `rt_gc_point_arr` → call `plw_zh_mark_push` → call `plw_cw_mark_push` → call `rt_pl_cellws_on` → call `rt_zeta_mode` → restore floor. **In the shipped configuration every one of those inner calls early-returns**: the cellws island is off unless `SCRIP_PL_WS_RECLAIM=1`, and the zh pair stack is live only under `--zeta=zh`. So the entire zh/cw push is a **proven no-op by default** and the leaf's whole observable effect is `{DT_I, 0, (long long)g_pl_trail.top}`.

The inline arm (`sink_trail_mark_str`, bb_call_fn.cpp, label decade **100–101**) **proves that precondition at runtime instead of baking it** — mandatory, because `--zeta=` is a CLI flag the mode-4 compile cannot see and `SCRIP_PL_WS_RECLAIM` is read at run time (contract §3):

1. `g_plw_cellws_on != 0` → SLOW. The cell is `-1` (unresolved) / `0` (off) / `1` (on), so ONE `test/jne` rejects both "on" and "not yet known".
2. `g_zeta_mode == 2` (ZH) → SLOW. Read **live**, not snapshotted.
3. Else inline: `mov eax,[g_pl_trail+32]` → `movsxd rdx,eax` → `mov eax,6`. Result in the rax:rdx pair the call convention already returns in.

Both guards run **before anything is touched**, and the arm touches nothing — so deferral is bit-identical by construction (contract §1) and is reached with UNMODIFIED `rdi=args`, `esi=0`. GC safepoint and unwind floor stay in the leaf per contract §4: non-allocating, non-throwing, and with zero args there is nothing to protect.

**SELF-PRIMING (the trap that would have made this rung a silent no-op).** `g_plw_cellws_on` starts at `-1` and is resolved only when the C `rt_pl_cellws_on()` is first *called*. Had nothing ever called it, the guard would reject forever and the sink would emit, assemble, pass every gate, and **do nothing**. It works because the first `$trail_mark` necessarily takes the SLOW path (`-1` → defer), which resolves the cell, and every subsequent call inlines. Measured on the smoke: leaf entries **28 → 1**, the 1 being the priming call (96.4% eliminated). This is the same discipline as SINK-2's `dot_sl == 0 → SLOW`: **correctness never depends on the cell being populated, only performance does.**

**TWO CELLS EXPORTED, PROLOG FLOOR UNTOUCHED.** `g_plw_cellws_on` (rt_arena.c — function-static promoted to file scope, semantics identical) and `g_zeta_mode` (zeta_alloc.c — linkage widened `static`→`extern`; **the same cell, one storage class, not a new global**). Both files are OUTSIDE `test_gate_pl_no_new_global.sh`'s policed `PL_FILES` set — the s145 `gc_heap.c` precedent, **declared on purpose**. Gate PASSes, floor unmoved.

**ENCODER NOTE (the SINK-2 trap, dodged).** `movsxd` has **no memory-source form**. Unlike `cmp reg,[mem]` — which silently emits NOTHING (the s143 landmine) — `x86("movsxd", …)` **aborts loudly** on an unsupported operand pair, with a message naming the mode-3/mode-4 divergence class. So the shape here is `mov eax,[mem]` + `movsxd rdx,eax`. Worth recording that the encoder table is **inconsistent** about this: some mnemonics bomb, some vanish. Assume vanish; eyeball the `.s`.

---

## §2 NUMBERS (all RT `-O0`, mode-4, two baked binaries — no `-O2` anywhere this session)

Bench: `nrev(30)` failure-driven ×2000 (repetition from backtracking over `rep/rep2/rep3`, **zero recursion depth** per contract §9's NO-LCO cap; `app/3` not `append/3` per the s145 gprolog correction). **1,056,422 marks.**

| A/B | ON | OFF | ratio |
|---|---|---|---|
| ⚠ `SCRIP_NO_SINK` (whole family) — **WRONG WAY TO MEASURE A RUNG** | 0.387s | 0.617s | 1.59× |
| ✅ `SCRIP_NO_SINK8` (this rung only, family held ON), 60 runs each | **0.4224s** | **0.4459s** | **1.056×** |

**SINK-8 alone is ~5%, i.e. ~22ns per mark** — a believable price for ~5 nested `-O0` calls through the PLT. The 1.59× was SINK-1/2/3 doing their work and this rung taking the credit.

---

## §3 ⚠⚠ THE LESSON — A FAMILY KILL SWITCH CANNOT ISOLATE A RUNG

Contract §8 specifies ONE switch, `SCRIP_NO_SINK=1`, disabling the whole family. That is correct as a *safety* hatch and wrong as a *measurement* instrument, and nothing in the ladder said so. Using it for the rung A/B compares **{1,2,3,8} vs {}**, not **{8} vs {}** — so on any bench where an earlier rung is also hot, the newest rung harvests every prior rung's win. nrev is exactly such a bench: SINK-2/3 own its list plane. **The first A/B on this rung read 1.59× and it was 30× too generous.**

The direction was also not obvious from a small sample: at 3 runs per arm the isolated measurement had one block where OFF was *faster*. Only at 60 runs per arm did the sign become consistent (ON faster in 6/6 blocks). **A ~5% effect needs ~10× the samples a ~50% effect needs; the ladder's per-rung recipe step 8 does not say how many.**

**PROPOSED CONTRACT §8 REFINEMENT (for Lon's review — trivially revertible, one `&& !getenv(...)` clause):** every rung gets a per-rung switch `SCRIP_NO_SINK<N>` **nested inside** the family switch. Default is enabled, so nothing changes for any user; the family hatch keeps working; and each rung becomes independently attributable forever after. Landed here as `SCRIP_NO_SINK8`. If Lon prefers the single-switch contract, delete the clause — but then **no rung after the first can honestly report its own number**, and the ladder's KPI (emitted share ≥90%) will be reached with a set of per-rung numbers that do not add up.

**COROLLARY — OUTPUT IDENTITY IS NOT WORK IDENTITY.** The bench is failure-driven and prints only `done`. A binary that silently did *fewer iterations* would print `done` too, and *faster* — indistinguishable from a win by output diff alone. Proof of equal work must be an independent counter: here, `rt_pl_dop_trail_unwind` (not sunk this session, pairs 1:1 with marks) measured **1,056,421 in BOTH** arms. **Any failure-driven A/B must carry such a counter or its ratio is unfalsifiable.**

---

## §4 GATES (all green)

- Rung suite **164/164 × 3 modes (interp/run/compile)** — run **three times** (twice pre-scaffold, once post).
- `test_smoke_prolog` 5/5/5 · `test_gate_pl_no_new_global` PASS (floor unmoved) · `test_gate_pl_no_value_stack` PASS.
- A/B byte-identical, sink on vs off, **mode-3 AND mode-4**, on a smoke covering backtracking across inline-made marks, findall, if-then-else both ways, and a failure-driven loop. m3 output == m4 output.
- Emitted `.s` eyeballed (7 blocks in the smoke, 9 in the bench); `as` accepts; isolation verified in the artifact itself — SINK-8 blocks 9→0 while SINK-1/2 blocks stayed 15/15 in both arms.
- Bench `.s` regenerated: emitted=22 changed=22 rejected=0.
- **PRE-EXISTING, NOT MINE:** `test_gate_bb_one_box` FAILs on **Icon** boxes (`bb_binop_gvar_relop.cpp` missing, two `bb_binop_*_slot.cpp` with 0 entries). Verified failing on the untouched tree at session start, before any edit.

## §5 NEXT

**REGAIN-1 slice C (THE SPINE)** remains the big one and is untouched: proc-call spine ~36% of profile, args staged into `g_call_args` then copied AGAIN into the callee frame (`rt_frame_bind_args`) — double copy per call over ~10M calls. Needs the driver-minted proc-entry `bb_label_t` table + one in-band `E`/`F` record. **Before starting it, re-measure the ladder's landed rungs with per-rung switches** — the family number (1.47×, s143) and the sum of the individual rungs should be reconciled, and per §3 there is no reason to expect they currently agree.

Remaining leaves: SINK-4 `$ix_g`, SINK-5 `$is_v`, SINK-6 `$ax_*`, SINK-7 `$cmp_*` (⚠ the double-compare trap), SINK-9 `$trail_unwind` (design-heavy, do last), SINK-10 sweep.

**BANKED (carried, none resolved this session):** NO-LCO deep-recursion segfault + cumulative exhaustion; nested-`\+` binding leak; `retractall/1` gaps; compiled-path silent-fail on undefined predicates.
