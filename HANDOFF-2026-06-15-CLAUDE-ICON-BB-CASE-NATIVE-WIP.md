# HANDOFF 2026-06-15 — Icon native `IR_CASE` (case-of) — **WIP, gate not green** (Claude)

**Goal:** GOAL-ICON-FULL-PASS — native `case` expression for `rung33_case_*` (the watermark's named next priority: "rc=139 IR_CASE native template").
**Result:** **NOT landed.** Full scaffold built and runs; one bug remains (matched arm's value never reaches the slot `write` reads → empty output). **Nothing committed. SCRIP trunk untouched, HEAD still `023fb43`.**
**Where the work lives:** `wip-icon-case-native.patch` (this repo, next to this file). Reapply with `git apply` onto SCRIP `023fb43`. HEAD (.github) = this file.

> This is a WIP design+code handoff, not a green landing. The patch builds clean (both `scrip` and `libscrip_rt`) but the cases produce empty values, so it must **not** be committed to SCRIP trunk as-is (no-broken-commits). Resume, fix the one bug below, gate, then commit.

---

## Reapply

```sh
cd SCRIP
git checkout 023fb43            # or rebase the patch onto current HEAD; conflicts unlikely (isolated sites)
git apply /path/to/.github/wip-icon-case-native.patch
bash scripts/build_scrip.sh && make libscrip_rt
```

To discard instead: the patch is the only record; SCRIP trunk has nothing to revert.

---

## Background — canonical shape (refs/jcon-master/tran/irgen.icn `ir_a_Case`, and lower_icon.c)

Icon `case e of { k1: v1; k2: v2; default: vd }` lowers (lower_icon.c ~191) to an **`IR_CASE`** node:
- `operands[0]` = the selector expression's result node.
- `operands[1..]` = **arm wrappers**, one per arm. Each wrapper is now an **`IR_CASE_ARM`** node (this patch; was `IR_LIT_NUL`):
  - normal arm → wrapper has 2 operands `[key_result, value_result]`
  - `default` arm → wrapper has 1 operand `[value_result]`

`case` value semantics: only the **matched** arm's value is evaluated (so the driver must `walk` each value lazily, on its own match path — never pre-evaluate all arm values). Equality is Icon `===`: int-by-value if both int, else string compare. That's `rt_case_eq`.

The blanket excise that made `rung33_case_*` print `[SMX]` (segfault-avoidance) was at `scrip.c` `graph_native_emittable_mode`: `if (nd->op == IR_CASE) return 0;`. This patch replaces it with a wrapper-shape admissibility check.

---

## What the patch does (10 files)

1. **`src/runtime/rt/rt.c`** — re-land `rt_case_eq` (it was stranded in `src/attic/runtime/rt/rt.c`, declared in live `rt.h` but **absent from `libscrip_rt.so`** — verified via `nm -D`). Pure value helper: both-int → `i==i`; else `VARVAL_fn` both → `strcmp==0`.
2. **`src/contracts/IR.h`** — new kind `IR_CASE_ARM` after `IR_CASE`.
3. **`src/contracts/scrip_ir.c`** — `kname[IR_CASE_ARM]`.
4. **`src/lower/lower_icon.c`** — tag both arm-wrapper builds (`default` and `key:value`) as `IR_CASE_ARM` instead of `IR_LIT_NUL`. (Two one-line edits.)
5. **`src/emitter/BB_templates/bb_case_arm.cpp`** — NEW template, dual-role via `_.op_ival`:
   - `op_ival==0` (compare): `lea rdi,[ζ+op_sa]` (selector slot); `lea rsi,[ζ+op_sb]` (key slot); `call rt_case_eq`; `test eax,eax`; `jz ω` (mismatch → next arm); else `jmp γ`.
   - `op_ival==1` (take): copy 16-byte DESCR from `op_a_slot` (value slot) → `op_off` (case slot); `jmp γ`.
6. **`src/emitter/BB_templates/bb_templates.h`** — decl.
7. **`src/emitter/emit_core.c`** — dispatch `case IR_CASE_ARM: bb_emit_x86(bb_case_arm()); return 0;`
8. **`src/emitter/emit_bb.c`** — `flat_drive_case` fully rewritten to the operand-wrapper shape (allocates a 16-byte case slot via `bb_slot_alloc16(pBB)`; walks selector; per arm: walk key → compare box → on match, walk value → take box → `bb_slot_register(pBB, case_slot)` + `jmp γ`; default arm walks value then take box; fall-through → `jmp ω`).
9. **`Makefile`** — `bb_case_arm.cpp` added to the PIC source list + a compile rule (mirrors `bb_swap`).
10. **`src/driver/scrip.c`** — `IR_CASE` decline → wrapper-shape admissibility (`operands[0]` present; every `operands[1..]` is an `IR_CASE_ARM` with ≥1 operand).

**Build:** clean. **Behavior:** all 5 `rung33_case_*` went from `[SMX]` → emit + run, with structurally-correct selector→per-arm-compare→branch flow in the mode-4 asm.

---

## THE REMAINING BUG (precisely located — start here)

Symptom: cases run (rc=0, no `[SMX]`/bomb) but print **empty values** — e.g. `rung33_case_case_arith` expects `10\n40\n700`, emits three blank lines. So control reaches the matched arm and reaches `γ`, but the **value never lands in the case slot** that `write` reads.

Two concrete leads, same root:

**(A) mode-4 asm shows the take box emitting a *second `rt_case_eq` compare* instead of the value-copy.** i.e. at the take site `_.op_ival` is read as **0**, not 1 — so the `op_ival==1` branch never fires. `bb_fill_alpha` does NOT clobber `op_ival`/`op_sa`/`op_sb`/`op_a_slot`/`op_off` (checked). So the reset happens on the path between the driver setting `g_emit.op_ival=1` and the template reading `_.op_ival`.

**Likely root — dispatch ambiguity.** `EMIT_PAIR_FILL` is defined in `emit_bb.c` and calls `walk_bb_node(...)`. There are **two** `walk_bb_node`s: emit_bb.c's **flat-chain dispatcher** (has the `flat_drive_*` cases + a `default:` that just emits `def β; jmp ω; jmp ω`) and emit_core.c's **single-box dispatcher** (where this patch's `case IR_CASE_ARM` lives). Same-TU resolution means `EMIT_PAIR_FILL(arm,...)` inside `flat_drive_case` dispatches the arm through **emit_bb.c's flat** `walk_bb_node`, which has **no `IR_CASE_ARM` case** → the arm likely falls to the flat `default`, and/or the value-walk done between the two FILLs resets `op_ival`. (The compares DID appear in asm, so the template is reached *somehow* — confirm the exact route before trusting it.)

**(B) mode-3 (`--run`) emitted NO template instrumentation** when I temporarily added an `fprintf` at `bb_case_arm` entry. The `--run` in-process emitter links its own copy; confirm `bb_case_arm` is actually invoked on the run path at all (it may be routing entirely through the flat `default`, which would explain empty output with no compare executed).

Also: **`rung33_case_case_no_default` still `[SMX]`** — the default-arm-only path (single-operand wrapper) trips the gate or driver differently from the others. Check the default branch in `flat_drive_case` and the admissibility check for the 1-operand wrapper.

---

## FIX DIRECTION (recommended)

Stop overloading one node with an `op_ival` role flag across an ambiguous two-dispatcher path. Either:

- **(preferred) Give the take its own dedicated kind** (e.g. `IR_CASE_TAKE`) + its own template, and add an explicit `case` to **emit_bb.c's flat `walk_bb_node`** (not just emit_core's) so both compare and take are routed unambiguously by the dispatcher that `EMIT_PAIR_FILL` actually reaches. Add `flat_drive_*` entries or `FILL`-style handling for both arm sub-roles in emit_bb.c's switch. This matches the codebase grain (one kind ↔ one role ↔ one template) and removes the survives-the-value-walk fragility.
- **(or)** Set the role field **inside the dispatch `case`** in the dispatcher that's actually reached, rather than in the driver before FILL — so it can't be reset by the intervening value-walk.

Either way: first add a `case IR_CASE_ARM` (and/or `IR_CASE_TAKE`) to **emit_bb.c's** flat `walk_bb_node` switch — its absence there is the most likely reason the take role is lost. Confirm with a one-line `fprintf` in *both* `walk_bb_node`s which one receives the arm node on the `--run` path.

---

## GATE (must pass before any SCRIP commit)

Touches shared `rt.c`, so run the full battery and diff:
- `bash scripts/test_icon_rung_suite.sh --mode run` and `--mode compile` — confirm `rung33_case_*` move PASS, **FAIL/XFAIL/EXCISED no regressions** elsewhere (baseline this session: m3=m4=**122/283**, FAIL 25, XFAIL 36, EXCISED 100).
- `bash scripts/test_smoke_prolog.sh` (m3/m4 must hold 5/5) and the SNOBOL smoke — `rt.c` is shared across all languages.
- Icon smoke `scripts/test_smoke_icon.sh` m3/m4 must hold 12/12.

**Note on m2:** mode-2 (`--run`) is **deleted** (commit `a2440f4`, GOAL-DE-INTERP). The smoke + rung scripts still *invoke* `--run`, so they report phantom m2 FAIL across the board — ignore m2, gate on m3/m4. (Separately worth fixing the harnesses to stop calling the dead flag; that's DE-INTERP territory, not this goal. The GOAL-ICON-FULL-PASS.md watermark is also stale — shows HEAD `bcef3df`, actual `023fb43`.)

---

## Provenance
Single Claude session, orientation + this WIP. Canonical sources consulted: `refs/jcon-master/tran/irgen.icn` (`ir_a_Case`), `refs/icon-master/src/runtime/{oarith,ocomp}.r` (=== coercion). Models for the template: `bb_section.cpp` (slot→reg→`call rt_*`→store), `bb_to.cpp` (internal `L(n)` labels), `flat_drive_section`/`flat_drive_swap` (driver walks + `EMIT_PAIR_FILL`).

---

## ADDENDUM (same session, continued) — root causes pinned, take+compare working, 3 issues left

Patch refreshed (`wip-icon-case-native.patch`, ~257 lines). **Still WIP / not green; SCRIP trunk still `023fb43`, nothing committed.**

### Root cause of the original "empty output" — FOUND and FIXED
`emit_core.c` `walk_bb_node` **auto-derives two `g_emit` fields from the node at every dispatch**:
- line 328: `g_emit.op_ival = IR_LIT(nd).ival;`
- line 335: `g_emit.op_a_slot = bb_slot_get(op_a)` (op_a = node's first operand)

So setting `g_emit.op_ival`/`g_emit.op_a_slot` in the driver before `EMIT_PAIR_FILL` is **useless** — both are clobbered the instant `walk_bb_node(arm)` runs. Fields that **survive** dispatch: `op_sa`, `op_sb`, `op_off` (not touched in the `IR_CASE_ARM` case).

**Fix applied:** role tag is now carried in the **arm node's own `IR_LIT(arm).ival`** (set right before each FILL; line 328 then *copies* it into `op_ival` — so it arrives correctly). The take's value slot is carried in **`op_sb`** (survives) instead of `op_a_slot` (clobbered); case slot in `op_off`. Template `bb_case_arm` take-role now reads `op_sb`(value) → `op_off`(case).

**Result:** `rung33_case_case_in_proc` (a `return case n of {...}` with a **var** selector) now emits **`one\ntwo\nmany`** — fully correct values, compare + take both working.

### 3 remaining issues (all now well-localized)

1. **Literal selector slot = 0 (breaks `case_str`/`case_int`/`case_arith`/`case_no_default`).** In the compiled asm the compare reads the selector from `[r12+0]` though the selector literal was stored elsewhere — `descr_binop_opnd_slot(sel)` returns 0 for a just-walked **literal** selector (works for a **var** selector, hence `in_proc` passes). Need the correct slot-capture for a literal selector after `walk_bb_flat(sel,...)`. Look at how other consumers capture a literal operand's slot post-walk (vs `descr_binop_opnd_slot`, which evidently 0s for these). Possibly the selector literal must be forced into a named slot (e.g. `bb_slot_alloc16_or_get(sel)` before/around the walk) rather than relying on `descr_binop_opnd_slot`.

2. **`write(case…)` arg-read.** These four are `write(case … )` — the CASE is a **builtin call argument**. Confirm the write-arg path reads the CASE result via the slot registered by `bb_slot_register(pBB, case_slot)` / `descr_binop_opnd_slot(case_node)`. `case_in_proc` uses the `return` consumer (works), so the arg-marshalling read is the untested edge. Once (1) is fixed and arms actually match, verify the value reaches `write`.

3. **Trailing extra empty line on `case_in_proc`** (`one|two|many|` — one extra blank). A spurious extra `write`/value of an empty case result, or the case fall-through path is also reaching `γ`/the consumer once. Check the per-arm `jmp γ` vs the final fall-through `jmp ω` wiring in `flat_drive_case` — likely the value path and the fall-through both reach the consumer, or the case-of node is consumed twice.

### Current `flat_drive_case` shape (in the refreshed patch)
- walk selector → `sel_done`; `sel_slot = descr_binop_opnd_slot(sel)` (← **bug for literals**, see #1); `case_slot = bb_slot_alloc16(pBB)`.
- per normal arm: walk key; `IR_LIT(arm).ival=0`, `op_sa=sel_slot`, `op_sb=descr_binop_opnd_slot(key)`; FILL(arm, take, next_arm, cmp_β) → compare; at `take:` walk value; `IR_LIT(arm).ival=1`, `op_sb=descr_binop_opnd_slot(val)`, `op_off=case_slot`; FILL(arm, γ, ω, β) → take; `bb_slot_register(pBB, case_slot)`; `next_arm:`.
- default arm: walk value(=key operand); take with `op_sb=descr_binop_opnd_slot(key)`; FILL → γ.
- fall-through after all arms → `jmp ω`.

### Gate status
Not yet run (not green, so no commit). Same battery as the main doc applies (Icon run/compile FAIL-diff at baseline m3=m4=122/283; Prolog+SNOBOL smokes for the shared `rt.c`). The `bb_case_arm` dual-role template is the only new emission surface besides `flat_drive_case`.
