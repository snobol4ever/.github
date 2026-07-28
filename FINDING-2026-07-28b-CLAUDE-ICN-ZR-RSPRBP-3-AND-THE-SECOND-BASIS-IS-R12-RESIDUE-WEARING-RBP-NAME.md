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

**⭐ RESOLVED IN-SESSION — the decisive experiment WAS run, and the arm is dead.** The first draft of this
finding stopped at "syntax-clean is not runtime-correct" and left the question open. It is now measured.
Full tree built under `-DZC_FRAME=ZC_FRAME_RBP` (compiler AND runtime, matched pair), same 22-program batch
across all three languages, against the saved RSP build as control:

| basis | ok | crash |
|---|---|---|
| `ZC_FRAME_RSP` (default) | **20** | 2 — both pre-existing (`jcon_args` = this goal file's own FZ-E1; `jcon_btrees` = known xfail) |
| `ZC_FRAME_RBP` | **7** | **15** |

**13 additional crashes attributable purely to the basis flip** — SNOBOL4 feat (`f03_numeric`,
`f06_builtins_predicates`, `f07_keywords`, `f08_data_array_table`), Icon rung36 (`arith`, `augment`,
`center`, `checkfpx`, `ck`), Prolog rung10 (`puzzle_02/03/04`), plus `pat_arbno`. It builds clean and runs
`hello`; it dies on anything real.

⚠ **A MEASUREMENT TRAP THIS SESSION FELL INTO AND CAUGHT — worth recording because RULES.md already warns
about it and I still hit it.** My first RBP batch read `ok=20 crash=2`, i.e. "RBP is fine." It was a
**MISMATCHED PAIR**: I had `cp`'d the RSP `.so` over `out/libscrip_rt.so` for the control run, which gave
that file a fresh mtime, so the next `make ZCFLAGS=... libscrip_rt` considered it up to date and **silently
relinked nothing**. RBP compiler + RSP runtime. This is verbatim the s126 lesson in RULES.md's
O2-DIRECTED-ONLY rule — *"make skips on unchanged timestamps even when flags change … verify the `.so` mtime
actually moved"* — which is about `-O2` but is really about ANY flag-only rebuild. Caught by `cmp`-ing the
rebuilt `.so` against the saved one; `rm -f` the target first, then rebuild, then `cmp` to prove it moved.
**Any ZCFLAGS A/B must prove the artifact actually changed before believing a single number.**

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

## 4. What landed instead of a 17-arm deletion — a LOUD guard

The remedy for a dead selectable value is not to leave it silently selectable. `zeta_choices.h` already has
a house idiom for exactly this — `#error` guards on `ZC_COL_GC` and `ZC_PROMOTE_ON`, both non-working
selectable values. `ZC_FRAME_RBP` now has the third, carrying the measurement above and pointing at this
finding.

**Why a guard and not the deletion.** The deletion is 17 arms across 6 files, several inside suspend/resume
protocols (`bb_call_proc_staged`'s spine-gen arm, `xa_flat`'s γ/ω epilogues). This goal file's own
BID-AT-LOWER ruling says half-landing a change to an emitted call's shape is worse than not starting, and
that judgment is unchanged by knowing the arm is dead. The guard is the proportionate move: it converts a
**silent 13-crash trap into a compile-time error that names the evidence**, costs zero emitted bytes, and
leaves the real decision clean and fully-evidenced for Lon.

Also corrected — three prose sites that made the dead arm look alive and maintained:
- `x86_asm.h:1435` certified the dance "FRAME-SAFE under ZC_FRAME_RBP" via `x86_align_save()`, a function
  with **zero definitions**. Rewritten to describe the push-based dance that actually exists, with the old
  claim quoted and refuted rather than silently dropped.
- `bb_call_proc_staged.cpp:121` — same dead helper, "while the ζ frame is r12".
- `bb_call_proc_staged.cpp:281` — "configs where r12 IS the ζ frame", now marked dead-code-awaiting-decision.

**Proof the whole change set is inert:** 8/8 emitted `.s` byte-identical, census gate green (unseeded=0),
**Icon 252/11/30 re-derived fresh**, guard verified to fire under `-DZC_FRAME=ZC_FRAME_RBP` and not under
the default.

## 5. Next rung — Lon's call, one question

Either **re-establish** the 17 RBP arms against the current register contract (under RBP, `x86_zr()` and
`x86_fb()` are both rbp — every `push x86_zr()` / `mov x86_zr(),rsp` arm needs rethinking), or **delete**
them and retire `ZC_FRAME` entirely, leaving the per-graph `x86_fb_pinned()` selection as the whole ζ
RSP/RBP story. The evidence now favors deletion, but it is a design call, not a cleanup.

---

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude Sonnet
