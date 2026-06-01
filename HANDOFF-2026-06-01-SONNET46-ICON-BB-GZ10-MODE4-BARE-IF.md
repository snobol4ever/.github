# HANDOFF 2026-06-01 — Claude Sonnet 4.6 — ICON-BB GZ-10 mode-4 + bare-if-no-else

**Goal:** GOAL-ICON-BB.md (GZ-10 mode-4 + bare-if-no-else fall-through)
**SCRIP HEAD:** `b8f48bf`
**\.github HEAD:** `bd3d7c0d`

---

## Gates at handoff (all green)

- Icon smoke: **m2 12/12 HARD · m3 12/12 · m4 12/12**
- Prolog smoke: **m2 5/5 · m3 5/5**
- no-stack: **117 ≤ 127** · one-reg-frame: **20 ≤ 20** · FACT: **0** · ZERO-SM: **0** · prove\_lower2: **PASS**

---

## What landed

### Rung 1 — GZ-10 mode-4: user procs as named asm slabs (`2de9ff5`)

**Problem:** `--compile` emitted an `abort` stub for every user-procedure call — proc slabs weren't written to the `.s` output, and the proc name was an in-scrip AST pointer, not a stable asm symbol. m4 was 0/11.

**4-file fix, all Icon-gated:**

**`src/emitter/emit_bb.c`** — two changes:
- `icn_flat_chain_build_proc_text(entry, pnames, np, out, pname)` (new): TEXT twin of the BINARY proc builder. Emits each proc as `.globl icn_proc_<name>_α` labeled GAS slab with the same frame layout (return slot `[r12+0]`, param i at `[r12+16*(i+1)]`). Does NOT reset `g_flat_node_id` — persists across all proc+main slabs so `xchainN_*` labels are globally unique.
- `icn_flat_chain_build_text()`: Also no longer resets `g_flat_node_id` (same reason — main labels must not collide with preceding proc labels).

**`src/emitter/BB_templates/bb_call.cpp`** — MEDIUM_TEXT arm for `dval==3.0` (flat-chain user-proc call): replaced `abort` stub with full PLT-relative emission — `.rodata` proc-name string label + `rt_icn_arg_stage@PLT` per arg + `rt_icn_call_proc_descr@PLT` + result stored to `[r12+off]`/`[r12+off+8]`.

**`src/runtime/rt/rt.c`** — `rt_proc_set_fn()`: extended to CREATE a new proc entry when the name is not yet registered. Required for mode-4 startup: the asm startup stub calls `rt_proc_set_fn` before any `rt_proc_register` has run.

**`src/driver/scrip.c`** — mode-4 Icon driver:
- Emits each non-main proc slab via `icn_flat_chain_build_proc_text` before `main`.
- Emits `icn_proc_startup:` stub that calls `rt_proc_set_fn(name, icn_proc_<name>_α)` for each proc.
- `main:` calls `icn_proc_startup` before `rt_frame@PLT` + `main_α`.

**Result:** m4 **0/11 → 11/11**. First all-three-modes 11/11/11 on the Icon smoke.

---

### Rung 2 — Bare-if-no-else fall-through (`b8f48bf`)

**Problem (documented GZ-8/9/10):** `if c then e` with no else and a failing condition aborted the entire proc/compound instead of falling through to the next statement in all three modes.

**Root cause:** `lower_icon_body` in `src/lower/lower_program.c` was passing `ω_in = PFAIL` for EVERY statement. Per **JCON `ir_a_Compound` lines 1253-1254** (canonical authority):
```
suspend ir_chunk(L[i].ir.failure, [ ir_Goto(ir_coord(p.coord), L[i+1].ir.start) ])
```
Each non-last statement's failure goes to the NEXT statement's start — not to PFAIL.

**1-file fix — `src/lower/lower_program.c`, `lower_icon_body()`:**
Added `is_last` flag (true only for the first reverse iteration = last source statement). Each iteration now passes:
- `ω = PFAIL` when `is_last` (last statement's failure properly fails the compound)
- `ω = next_a` otherwise (failure falls through to the next statement's α)

New smoke case `bare_if` added to `scripts/test_smoke_icon.sh`:
```icon
procedure main()
  x := 2;
  if x > 5 then write("big");
  write("done");
end
```
Expected: `done` (cond fails, falls through). Passes m2/m3/m4.

**Result:** smoke **11 → 12/12/12** all modes.

---

## NEXT (per GOAL-ICON-BB.md)

**GZ-DEFER** — EVAL/CODE/`*P` deferred patterns. The reference implementation is `SCRIP/.github/test_sno_3.c`: `(ζζ, entry)` calling convention, frame lazily `calloc`'d by `enter()`, resumable at α/β, `empty` decoded as failure at `_λ`. This was the ONE thing that broke the prior stackless build; it is solved in the reference file.

After GZ-DEFER: **GZ-11+** — corpus features rebuilt stackless (lists, tables, records, scanning, csets, builtins, sort, …). Each: read the canonical JCON/Icon source first, then a flat slot/arena template, gated m2==m3==m4 + zero-SM + no-stack=0 + no corpus regression.

---

## Session setup for next session

```bash
git clone https://TOKEN@github.com/snobol4ever/.github.git /home/claude/.github
git clone https://TOKEN@github.com/snobol4ever/SCRIP.git /home/claude/SCRIP
git clone https://TOKEN@github.com/snobol4ever/corpus.git /home/claude/corpus
cd /home/claude/SCRIP
bash scripts/install_system_packages.sh
bash scripts/build_scrip.sh
make libscrip_rt
bash scripts/test_smoke_icon.sh      # PASS=12 m2/m3/m4
bash scripts/test_smoke_prolog.sh    # PASS=5
# Extract canonical sources (from uploaded zips or clone):
# git clone https://github.com/proebsting/jcon refs/jcon-master
# git clone https://github.com/gtownsend/icon refs/icon-master
```
