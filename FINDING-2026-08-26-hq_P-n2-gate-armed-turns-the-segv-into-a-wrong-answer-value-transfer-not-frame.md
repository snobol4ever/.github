# FINDING — N-2's five slices are all landed but gated OFF; arming them trades the SIGSEGV for a WRONG ANSWER, so the remaining defect is VALUE TRANSFER, not the frame

**Seat:** `hq_P` · **s273** · 2026-08-26 · row `icon-bench-correct-zero-of-eight` (the **acceptance** side of N-2)
**Trees:** SCRIP `8e03e1e0` · corpus `b1649085f` · .github `18af7fae` (after `merge --ff-only origin/main`)
**Oracle:** Arizona `icont` at `/home/resources/icon-master/bin/icont`, verified present and executed, not assumed.
⭐ Icon evidence is first-class again as of Lon's 2026-08-26 CROSS-LANGUAGE SCOPE ruling (`RULES.md:29`).

## What the baton said, and what has changed underneath it

The task's `## NEXT` step 3 said a generator procedure *"satisfies **neither** arm and falls through both, emitted
frameless while its body still uses frame-relative addressing."* **The emitter has moved since that was written.**
`emit.cpp:2783` now reads `} else if (icn_genframe2() && g_emit.flat_gen) {` — a dedicated generator arm exists, and
**all five N-2 slices are present**:

| slice | site |
|---|---|
| alpha carve | `emit.cpp:2783` |
| res landing | `emit.cpp:3101` |
| gamma suspend | `emit.cpp:3168` |
| omega retire | `emit.cpp:3187` |
| caller landing | `bb_call_proc_staged.cpp:720` |

They are **gated off by default** behind `icn_genframe2()` (`x86_asm.h:2049`), armed with `SCRIP_ICN_GENFRAME2=1`.
The gate's own comment: *"⛔ DEFAULT OFF until all five slices land and the D2-suspend witness set is green … a
half-built one crashes differently rather than better."*

## The measurement (mode-3 and mode-4, honest exit codes, 139 = SIGSEGV)

| witness | oracle | gate OFF | gate ARMED (m3) | gate ARMED (m4) |
|---|---|---|---|---|
| `suspend 1` (single) | `1` | ⛔ **SIGSEGV** 139 | ⚠️ **`` empty, rc=0** | ⚠️ **`` empty, rc=0** |
| `suspend 1 \| 2` (multi) | `1 2` | ⛔ **SIGSEGV** 139 | ⛔ **SIGSEGV** 139 | ⛔ **SIGSEGV** 139 |
| `return 1` | `1` | ✅ `1` | ✅ `1` | ✅ `1` |
| `every write(1 to 3)` | `1 2 3` | ✅ `1 2 3` | ✅ `1 2 3` | ✅ `1 2 3` |

## ⭐ The result, and it refines the root cause

1. ⭐ **The frame carve WORKS.** Arming removes the single-`suspend` SIGSEGV entirely. The baton's root cause — *"a
   procedure containing `suspend` is emitted with NO ACTIVATION FRAME"* — is **correct and now addressed**.
2. ⛔ **But the yielded VALUE never lands.** `write()` receives an empty value where the oracle prints `1`. So the
   remaining defect is **descriptor transfer through the resume record**, a *different* defect from the one N-2 was
   scoped against. Getting the frame right was necessary and is not sufficient.
3. ⛔ **Multi-value `suspend 1 | 2` still SIGSEGVs armed** — the alternation/resume path is not covered by the five
   slices at all. The single-value case is the only one the carve reaches.
4. ✅ **No regression:** `return` and `every … to` are byte-identical armed and unarmed. Arming is inert outside
   generator procedures, which is what a clean gate should look like.
5. ✅ **The m3 ≡ m4 invariant HOLDS armed** — both emit the identical (wrong) empty write.

## ⛔ Recommendation: the gate stays OFF, and the gate comment is already right

Arming today would trade one **loud** failure for one **quiet** one. ⭐ **For a benchmark row that is the whole
point: a SIGSEGV cannot be scored as a pass, but an empty write can.** `bench_correct` compares output — a program
that runs to `rc=0` and prints nothing is exactly the shape that banks a false green somewhere downstream. The gate's
author already wrote the correct rule (*"a half-built one crashes differently rather than better"*); this measurement
supplies the specific reason it is still true, and the D2-suspend witness set is **not** green.

## What N-2 needs next (for whoever takes the rung — ⛔ NOT this row, which may not cure)

- The value path, not the frame path: the descriptor yielded at `emit.cpp:3168` is not arriving at the caller
  landing (`bb_call_proc_staged.cpp:720`). The four-word record (rbp / omega / gamma / resume label) is carried; the
  **result descriptor is not** — that is the gap to close.
- ⚠️ `rt_icn_gen_frame_alloc` (`rt.c:1388`, the storage half claimed landed at s272) has **zero call sites** in
  `src/emitter/` or `src/templates/`. Nothing emitted calls it, armed or not — so the workspace-island record and the
  emitted protocol are not yet connected. Worth confirming that is intended sequencing rather than a missed wire.
- Multi-value `suspend` needs its own witness in the D2 set; the single-value case passing would not have caught it.

## ⚠️ Two process notes, both self-inflicted and both caught before they reached a claim

1. I first measured the witness set through a `| tr` pipe and read `$?` — which is the **pipe's** status, not
   `scrip`'s. It reported `rc=0` on a run that had actually **SIGSEGV'd**. This is the trap `CLAUDE.md` names
   verbatim ("Read the verdict line, not a pipeline's `$?`"). Re-measured without the pipe; the table above is the
   honest one.
2. I nearly reported an **m3 ≢ m4 invariant violation**: an early mode-4 run captured with `2>&1` printed `ARRAY`,
   which I read as divergent stdout. Re-running with the streams **separated** showed stdout is identical (`\n`) in
   both modes and `ARRAY` was never on stdout. ⭐ **A merged stream is not an observation of stdout** — and an
   invariant violation is exactly the kind of claim that would have sent the next seat hunting a codegen bug that
   does not exist.

## Row status

⛔ **No cure written** — the cure is rung `icon-n2-generator-activation-frames`, per this row's own standing
instruction. This row owns the witness, the honest board, and the re-score, and all three are advanced: the witness
now discriminates *three* states (crash / wrong-answer / correct) instead of two, which is what makes it a usable
acceptance test for N-2 rather than a smoke test.
`bench_correct` remains **0/8** and is **not** re-scored — DONE-WHEN requires N-2 to land first.
