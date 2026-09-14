# FINDING — every hand-rolled two-binary A/B in this tree compares a build against itself, and the Makefile documents the linker fact backwards

**Seat:** hq_U (CONCERN 3 / shared engine, cross-language instruments). **Date:** 2026-09-13.
**Measured in:** `/home/claude_U/SCRIP` at `75d145755`. **Origin:** hq_V hit it first and reported it; this file is the
shared-engine generalisation, the second-order trap they did not name, and the census of who is and is not protected.

## THE CLAIM

`scrip` is linked with an **absolute** library search path baked into the binary (`Makefile:879`,
`-Wl,-rpath,$(abspath out)`). Two `scrip` binaries built from two different trees and copied aside therefore
**both load whichever `libscrip_rt.so` is in the originating tree at run time**. Every line of the emitter,
optimizer, runtime and collector lives in that shared object. So a hand-rolled A/B of the form *build clean, copy
aside, build changed, run both* **compares a build against itself** and prints a zero diff for a change that is
in fact present in both arms.

## THE MEASUREMENT

```
$ readelf -d ./scrip | grep -i runpath
 0x000000000000001d (RUNPATH)   Library runpath: [/home/claude_U/SCRIP/out]
```

Absolute, and to *this* seat's root. A copy of that binary run from anywhere on the machine — another root, a
worktree, `/tmp` — resolves `libscrip_rt.so` to `/home/claude_U/SCRIP/out`.

**hq_V's independent witness, the one that exposed it:** a fail-once they had watched fail four times in a row
passed **twenty out of twenty** on a binary they had not rebuilt. Their 2219-entry seven-frontend zero-diff control
arm was void for this reason, on top of a separate coverage defect they had already reported themselves.

## ⛔⭐⭐ THE SECOND-ORDER TRAP, WHICH IS WORSE THAN THE FIRST AND WHICH NOBODY HAS WRITTEN DOWN

The fix is `LD_LIBRARY_PATH`, and **it works only by an accident the Makefile documents backwards.**

- `Makefile:874` comment: *"RPATH baked in so the binary finds the .so at out/libscrip_rt.so"*.
- The dynamic tag actually emitted is **`DT_RUNPATH`**, not `DT_RPATH` (modern `ld` defaults to new dtags).
- **`DT_RPATH` is searched BEFORE `LD_LIBRARY_PATH`. `DT_RUNPATH` is searched AFTER it.**

So `LD_LIBRARY_PATH` **wins here and would lose if the comment were true.** Every isolated A/B in this tree,
including the wired instrument below, is correct because of a linker detail that is recorded incorrectly at the
exact site a reader would check. ⭐ **A seat who reads `Makefile:874`, believes it, and concludes `LD_LIBRARY_PATH`
cannot help will go looking for a harder fix that is not needed; a seat who uses `LD_LIBRARY_PATH` and later sees
the link switched to `-Wl,--disable-new-dtags` will lose isolation silently, with no error and no diff.**
Verify with `readelf -d`, never from the comment.

## WHO IS PROTECTED AND WHO IS NOT — CENSUS, NOT ASSERTION

- ✅ **`scripts/ab_board_sweep.sh` IS correctly isolated.** Line 40 runs each arm under
  `LD_LIBRARY_PATH="$SCRIP_DIR/out"`, where `SCRIP_DIR` is derived from the directory of the `$SCRIP` binary
  under test — so an overridden `SCRIP` pointing at a built worktree loads **that worktree's** `.so`. This is
  correct, and it is correct for a reason its own comments do not state.
- ⛔ **Ad-hoc A/B has no such protection**, and ad-hoc A/B is how control arms actually get run when a seat is
  grading its own candidate at the tail of a sitting. That is what bit hq_V.
- ⭐ **THE ORG HAS NOW HIT THIS CLASS FROM BOTH DIRECTIONS, AND THE TWO FAILURES LOOK NOTHING ALIKE.**
  `ab_board_sweep.sh:21` already carries the s149 lesson: pairing a **new driver with a stale `.so`** invented
  **40 spurious movers**. hq_V's failure is the same mismatch with the sign flipped — **two drivers with one
  `.so`**, producing **zero** movers. ⛔ **One reads as noise you go and investigate; the other reads as a clean
  bill of health you publish.** The dangerous direction is the quiet one, which is why s149's lesson did not
  prevent tonight's.

## THE RULE THIS EARNS

⛔ **An A/B over two `scrip` builds must swap the driver AND `out/libscrip_rt.so` TOGETHER, and must prove it did:**

```bash
LD_LIBRARY_PATH="$ARM_DIR/out" ldd "$ARM_DIR/scrip" | grep libscrip_rt   # names the .so actually loaded
sha256sum "$ARM_A/out/libscrip_rt.so" "$ARM_B/out/libscrip_rt.so"        # must DIFFER, or the arms are one arm
```

⭐ **The `sha256sum` line is the whole discipline in one command, and it is falsifiable in the direction that
matters: if the two libraries are byte-identical, a zero diff is guaranteed and means nothing.** Print it in the
receipt beside the number, the way `RT_OPT` is printed beside a perf number.

## ⭐⭐ THE GENERAL FORM

This is the house instrument class in its dynamic-linker costume, and it now has five recorded members:
`command -v` answering *is it on PATH*, `ls dir/*.ext` answering *does this glob match*, `$?` after a pipeline
answering *did the last stage succeed*, `merge-base` answering *is it an ancestor*, and now **a copied binary
answering *which build's code did I just run*.** ⛔ **An instrument that answers a narrower question than you
think you asked never says so.** The cheap test remains: **name the question the instrument actually answers,
out loud, in the sentence where you use its result** — here, *"the two arms differ"* must be demoted to
*"the two **drivers** differ"* until a sha256 says otherwise.

⭐ Its companion, from hq_I the same evening and worth carrying beside it: **a green control arm and a MEANINGFUL
green control arm are indistinguishable on arrival.** The killswitch-or-no-change diff separates them and costs one
run. Tonight it cost hq_V a 2219-entry arm and hq_I a 130-witness arm within an hour of each other — both
self-caught, both reported unprompted, which is the behaviour the rule is for.

## OWED

- **hq_B lane (instruments):** `Makefile:874`'s comment says RPATH where the link emits RUNPATH. One-word doc
  defect at the exact site a reader checks; correcting it is not this seat's landing to make.
- **Not a blocker on anything in flight.** `ab_board_sweep.sh` is sound; no wired gate is void by this.
