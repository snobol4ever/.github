# FINDING 2026-07-28b — ZR-RSPRBP-3 lands; and the "closed at two" ζ basis is really closed at ONE

**Session:** s202 · **Goal:** GOAL-ICON-BB (ζ storage from RSP/RBP)
**SCRIP:** `d5b71d5b` · **corpus:** `bd61a95f` (unchanged — all four regens emitted zero artifacts)
**Icon:** 252/11/30 re-derived fresh AFTER the change · census gate green, unseeded=0

---

## 0. Two watermark hashes in the goal file do not exist

Measured first, before any work: `GOAL-ICON-BB.md`'s s201 watermark cites SCRIP `da8c2347` and corpus
`d706b860`. **Neither is a valid object in its repo** (`git cat-file -t` fails on both). The real HEADs
at session start were SCRIP `56cc4f09` and corpus `bd61a95f`. The ZR-RSPRBP commit is `c26a398a`, not
`da8c2347`.

This is the STALE-ORIENTATION rule's own failure mode, one layer deeper than the version it names: not a
push-status banner, but a **hash typed into prose rather than computed**. The fix is the same shape as
`handoff_status.sh` — a watermark line should be generated, never hand-copied. Recorded, not fixed:
changing the watermark mechanism is a Lon call.

Second-order consequence worth stating: corpus HEAD `bd61a95f` **is** the overdue `.s` regen that s201's
cursor flags as "the missing mechanism … it simply was not run." It WAS run and it IS landed. A session
orienting off that cursor would go hunting for work that no longer exists.

---

## 1. ZR-RSPRBP-3 — LANDED, proven inert

`bb_match_arbno.cpp:13` carried the SAME three-basis residue ZR-RSPRBP-1 collapsed in `x86_zr`/`x86_zr_num`,
and was missed:

```c
static inline const char * zv() { return ZC_FRAME == ZC_FRAME_RSP ? "rbp" : x86_zr(); }
```

With ζ closed at {RSP, RBP} both arms yield `"rbp"` — the RSP arm literally, the RBP arm because
`x86_zr()`'s own else-arm returns `"rbp"`. The ternary had no second value left to name. Collapsed to
`return "rbp";`.

**Proof to the s201 standard:** 8/8 emitted `.s` byte-identical, 3 languages, pinned + unpinned, both
ARBNO programs in the witness set (`scripts/util_zr_capture.sh`, committed).

**Falsifiability proven, not assumed** — this is the part that makes the identity result mean anything.
Injecting `zv() -> "r13"` and rebuilding makes `pat_arbno.s` differ by **14 lines**, while the other 7
witnesses correctly stay identical (they contain ARBNO but never reach the chain arm). So the witness set
demonstrably CAN see a `zv()` change, and its silence on the real edit is evidence rather than blindness.

**Independently corroborated:** all four RULES step-4 regens — benchmark, feature, demo, icon-bench —
committed **zero** changed artifacts over a far wider corpus than the 8-file witness set.

---

## 2. ⭐ THE REAL FINDING — the tree still advertises one more ζ basis than it has

s201 closed the basis 3 → 2 and stated "the ζ basis set is now CLOSED at RSP and RBP." **The measurement
says it is really closed at ONE.** `ZC_FRAME_RBP` is not a second basis; it is R12's code path wearing
RBP's name after s201 deleted the label above it.

**Evidence, measured:**

| # | measurement | result |
|---|---|---|
| 1 | `grep 'ZC_FRAME != ZC_FRAME_RSP' src/` | **17 arms** across 6 files (`bb_match_release`, `bb_match_capture`, `bb_match_head`, `bb_call_proc_staged`, `xa_flat`, `zeta_storage.c`) |
| 2 | what those arms say about themselves | `bb_call_proc_staged.cpp:281`: *"reachable solely when ZC_FRAME != ZC_FRAME_RSP … **configs where r12 IS the ζ frame** (pre-REG-MAP tenancy)"* |
| 3 | `x86_align_save()` — the documented mechanism that makes the C-call dance frame-safe under `ZC_FRAME_RBP` | **ZERO definitions.** 3 hits, all comments. The function is deleted (`xa_flat.cpp:122` even says so) while `x86_asm.h:1435` still describes it as live: *"r12 when the frame is rbp, which is precisely what makes the dance FRAME-SAFE under ZC_FRAME_RBP"* |
| 4 | does `-DZC_FRAME=ZC_FRAME_RBP` still compile? | **YES** — 6 template TUs, `-fsyntax-only`, clean |

So the second arm compiles, but every argument for its correctness is written against a register
assignment (r12-as-ζ) and a helper (`x86_align_save`) that no longer exist. Under `ZC_FRAME_RBP` today,
`x86_zr()` returns `"rbp"` — which is also `x86_fb()`'s pinned value — so arms like
`bb_match_release.cpp:32`'s `push x86_zr()` / `mov x86_zr(), rsp` would be pushing and repointing the
frame base itself. That shape was coherent when `x86_zr()` was `r12` and rbp was the align-save register.
It is not obviously coherent now.

**⛔ WHAT I DID NOT PROVE — stated plainly rather than implied.** I did **not** build the full tree under
`ZC_FRAME_RBP` and run the corpus. Syntax-clean is not runtime-correct, and I am NOT claiming the arm is
broken — only that **its correctness argument has been voided by deletions elsewhere and nothing has
re-established it.** The decisive experiment is one full `-DZC_FRAME=ZC_FRAME_RBP` build + crosscheck run.
It is cheap (~4 min build) and I stopped short of it deliberately: if it fails, the remedy is deleting 17
arms across 6 template files, and that is a design call, not a cleanup.

---

## 3. ⭐ THE CONFLATION THAT HID THIS — "RSP/RBP" names TWO different axes

The goal file, `ARCH-ICON.md`, and s201's cursor all say "ζ based from RSP and RBP." There are **two
distinct RSP/RBP dualities** in the tree and the prose merges them:

| axis | what it selects | granularity | live? |
|---|---|---|---|
| **`ZC_FRAME`** (`zeta_choices.h`) | the ζ **register** — `x86_zr()` | BUILD CONSTANT, whole program | default RSP; **the RBP arm is the R12 residue above** |
| **`x86_fb_pinned()`** (`x86_asm.h:359`, FLATDISP-8 s197) | the frame **base** — `x86_fb()` = rbp for pinned graphs, rsp for depth-static ones | **PER-GRAPH** | ⭐ **YES — this is the real, working, measured RSP/RBP duality** |

**The ζ storage "based on RSP and RBP" that actually runs is the second row, and it is COMPLETE** — that
is exactly what FLATDISP-9's census proved (~285,000 frame references, unseeded=0) and what re-measured
green this session. s201's two slices operated on the FIRST row, which is a different axis, and reported
the result as if it finished the second.

Practical consequence for the next session: **do not go looking for unfinished per-graph fb work — there
isn't any.** The open question is only whether `ZC_FRAME`'s second arm should continue to exist at all.

---

## 4. Recommended next rung — needs Lon's call, one question

**Run the `-DZC_FRAME=ZC_FRAME_RBP` full build + crosscheck.** Then one of:

- **(a) It runs clean** → the second basis is real; fix the stale prose (`x86_asm.h:1435`,
  `bb_call_proc_staged.cpp:121/281`) so it stops describing r12 and `x86_align_save()` as live, and keep both.
- **(b) It does not** → `ZC_FRAME` has one reachable value. Collapse it the way `ZC_FRAME_R12` was
  collapsed: delete the 17 `!= ZC_FRAME_RSP` arms, retire the constant, and let `x86_fb_pinned()` be the
  whole ζ RSP/RBP story. Provably inert under the default by construction, same as ZR-RSPRBP-1/2/3.

⚠ **Do not half-land (b).** 17 arms across 6 template files, several inside suspend/resume protocols
(`bb_call_proc_staged`'s spine-gen arm, `xa_flat`'s epilogues) — this goal file's own BID-AT-LOWER ruling
applies: half-landing a change to an emitted call's shape is worse than not starting.

---

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
