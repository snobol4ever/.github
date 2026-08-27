# FINDING — N-2 item 2: a callee generator's frame bytes ARE knowable before emission, but NOT where you would first look

**Seat:** hq_P (HQ-PERFORMANCE, `/home/claude_P`) · **Date:** 2026-08-27 · **Mode:** FLEET-12
**Row:** `icon-n2-generator-activation-frames` (rank 0, ASSIGNED:hq_P) — item 2, step 1b
**Acceptance row:** `icon-bench-correct-zero-of-eight` (still BLOCKED; `bench_correct` deliberately NOT re-scored)
**Tree:** SCRIP `b6703276` · corpus `e4be0d8c2` · RT_OPT `-O0`

## What was owed

Step 1 (`5cf65ded`) measured **3 genuine forward host→generator edges** across the eight `bench_correct` programs —
`geddump` (`event`→`gedval`, `gedload`→`gedwalk`) and `tgrlink` (`dumpcode`→`aseq`) — and ruled a pre-pass
**MANDATORY before step 2, not optional**: those edges read `proc_fb_buf[]` as **0 rather than erroring**, sizing a
host carve silently too small. The settled remedy was *"(a) a pre-pass recording all generator procs' frame bytes
before ANY graph is emitted; a loud REFUSE is the acceptable floor."*

## What was measured

⭐ **THE ARRAY IS THE HAZARD, NOT THE INFORMATION.** `proc_fb_buf[]` is filled *during* the emission loop
(`scrip.c:1310`) from `g_last_flat_frame_bytes`, so a host emitted before its callee reads an unwritten slot. But
`g_last_flat_frame_bytes` is only `g_emit_cfg->jcon_value_region` (`emit.cpp:3475`) — a **per-graph field assigned in
exactly one place in all of `src/`** (`scrip_ir.c:283`, `g->jcon_value_region = zls_g_region(g)`) and never assigned
again. So item 2 can read the callee graph directly at host-α time: **no table, no two-pass emission, and NO NEW
GLOBAL**, which the standing rule forbids without an in-chat grant. The mandated pre-pass is a *lookup*, not a table.

⛔⭐ **THE CORRECTION THE PROBE CAUGHT, AND IT IS THE REASON IT WAS BUILT INSTEAD OF ASSERTED.** The field is **not
live as soon as the stage2 table exists**. Probed at `sm_preamble()` time — the obvious "before any graph is emitted"
point, and where step 1's own host scan already sits — it reads `region=0` for nearly every proc:

| probe point | result |
|---|---|
| after `sm_preamble()` | **AGREE=2 · MISMATCH=427** of 429 (region=0 vs post-emit 992 / 720 / 3616 / 2800 / …) |
| after `drive_slots_all()` | ✅ **AGREE=429 · MISMATCH=0** |

`jcon_value_region` is assigned by `drive_slots_all()` → `ir_drive_slot_assign()` (`scrip.c:419-422`), called at
`scrip.c:1261/1439/1683/1805` — **still before every emission loop**, so the claim survives, but only when read after
that pass. ⛔ **An item-2 carve sized from the field any earlier would have read 0 for every callee** — precisely the
silent-too-small carve the guard exists to prevent, and it would have been blamed on the codegen landing on top of it.

⭐ **This is the same shape this project keeps paying for** — `command -v icont`, and item 1's "true as a count, wrong
as a diagnosis". The instrument was correct; the *question* was narrower than the one it appeared to answer. A field
that is populated is indistinguishable from one that is not yet populated if you only read it once.

## Instrument

`scripts/test_icn_n2_fb_prepass.sh` — three-state, **REFUSES `rc=2`** when it cannot measure (no `./scrip`, no corpus,
or **zero comparisons** — an empty denominator is never a pass), **FAILS `rc=1`** on any mismatch.
⭐ **Proven before trusted:** refused `rc=2` in a tree with no `./scrip`; caught a deliberately poisoned probe (`+8`)
as **429/429 MISMATCH, rc=1**. A guard that has never failed once is not known to be a guard.

## Inertness and control arms

- `.s` **byte-identical** probe-on vs probe-off, on the four-line witness **and** on `rsg.icn`.
  **Negative control:** armed vs unarmed = **77 lines**, so the diff is not vacuous.
- SNOBOL4 `m3 PASS=365 FAIL=0 · m4 PASS=365 FAIL=0 SKIP=0 · MISSING=0` **rc=0** — measured, then **re-measured after
  the rebase** brought in others' `core.c` / `gc_heap.{c,h}` changes (FETCH-IS-NOT-CHECKOUT: the first reading graded
  a tree that no longer existed).
- `emit_no_lang` rc=0 · `template_medium` rc=0 · Icon smoke m3 14/14 m4 14/14.
- **D2 gate-OFF = pinned baseline**: all five suspend shapes `CRASH 10/10` m3=m4, controls CORRECT.
  ⭐ **Unmoved is the CORRECT result for an inert step**; had any arm moved, the change would have been wrong.
- ⚠️ Arms are **incremental**, not `make pristine` — documentation of the denominator, **not a gate verdict** (HQ-27).

## Not claimed

⛔ Not a cure for the N-2 crash: `bb_call_proc_staged.cpp:733`'s `lea rsp,[rax+32]` is **untouched**.
⛔ `bench_correct` remains **0/8** and was deliberately **not re-scored** — DONE-WHEN needs N-2 to land.
⛔ Step 2 (host promotion to a real RBP activation frame) is **not started**; its blast radius
(`x86_main_prologue()` / `bb_glue_framed_enter()`, shared by every frontend) is unchanged and still binds
SHARED-NODE VERDICT SCOPE — SNOBOL4 + Icon + Prolog + Snocone boards all owed.
⛔ The armed-m4 intermittency remains **uncharacterized** (s274 stands); nothing here bears on it.
⛔ Measured on Icon programs only (23 programs, 429 comparisons, both modes). The write-once property of
`jcon_value_region` is a whole-`src/` grep result and so is language-blind, but the **agreement** was not measured on
the SNOBOL4/Prolog/Snocone paths — do not upgrade this to a cross-frontend invariant without measuring it.

## Consequence for step 2

✅ The forward-reference guard step 1 demanded is **satisfied structurally rather than by a refusal**: the 3 forward
edges are safe, because the callee's frame bytes are already correct in the callee's own graph by the time any host
is emitted. **Step 2 must read `s2->bbp.table[callee_bb_idx]->jcon_value_region`, and must do so after
`drive_slots_all()`** — never `proc_fb_buf[]`, and never at `sm_preamble()` time.
