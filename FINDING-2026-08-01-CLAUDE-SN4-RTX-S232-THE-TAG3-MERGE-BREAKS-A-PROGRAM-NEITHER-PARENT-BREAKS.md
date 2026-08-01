# FINDING s232 (2026-08-01) — THE TAG-3 MERGE IS BLOCKED BY A DEFECT PRESENT IN NEITHER PARENT

**Rung attempted:** owed item (2) of the s231 cursor — merge `tag-renumber-s229` to main.
**Outcome: MERGE NOT LANDED. It must not land as-is.** Nothing pushed to `origin/main`.

---

## ⭐⭐ THE RESULT THAT OUTRANKS THE MERGE

`1016_eval` **passes mode-3 on main. Passes mode-3 on the branch. FAILS mode-3 on the merge.**
Measured on all three legs, N=4 each, `setarch -R`:

| tree | `1016_eval` m3 | evidence |
|---|---|---|
| `main` @ `dda156eb` | **PASS** | absent from main's m3 FAIL set, present in DIVERGE (m3 pass / m4 fail) — my own crosscheck run, not prose |
| `tag-renumber-s229` @ `0bc20587` | **PASS** 4/4 | direct run, `PASS 1016_eval (3/3)` |
| trial merge `fe9d692c` | **FAIL** 4/4 | `FAIL 1016/001: eval concat expr`, one hash, rc=0 |

⇒ **THE DEFECT IS CREATED BY THE MERGE, NOT INHERITED FROM EITHER SIDE.** `EVAL(*('abc' 'def'))` stops
returning `'abcdef'`. Deterministic, so it is a semantic fault and not the s231 ASLR class.

⛔ **THE MECHANISM IS A CLEAN TEXTUAL AUTO-MERGE.** `src/templates/bb_call_fn.cpp` was edited by BOTH
sides and git raised **no conflict** on it. A clean build plus a green-looking tree is exactly what a
session merging this would have seen. **Textual merge success is not semantic correctness, and this
tree has no gate that says otherwise** — the only thing that caught it was running the watermark and
requiring EXACT hold.

---

## WATERMARK — THE GATE FAILED, SAID OUT LOUD

Baseline **main** (`setarch -R`, 31 s): **m3 200/117/0 · m4 198/118/1 · DIVERGE=2** {`170_pat_abort_kills_match`, `1016_eval`}
Trial **merge** (`setarch -R`, 30 s): **m3 199/118/0 · m4 198/118/1 · DIVERGE=1** {`170_pat_abort_kills_match`}

m4 held EXACTLY. m3 lost one. DIVERGE dropped one. **Both deltas are the single program `1016_eval`**
moving from (m3 pass / m4 fail) to (fail / fail) — set-diff confirms: one name added to m3 FAIL, zero removed.
⇒ **`require EXACT hold` is NOT satisfied. The merge is BLOCKED by the ladder's own standard.**

⚠ **THE BASELINE FOR THIS MERGE IS MAIN'S, NOT THE BRANCH'S — AND THEY ARE 76 PROGRAMS APART.**
s231 recorded the branch at m3 276/41/0. Main measures **m3 200/117/0**. Main is mid-flight on the ζ
ladder and knowingly depressed (its own HEAD message: *"landed DARK (plan stages, emission link broken)"*);
its recorded watermarks run 198/119, 199/118, 204/113, 229/88, so 200/117 is squarely inside their
operating range and was **not** caused by this session. Quoting 276/41 as the merge gate would have been
the s228 error — reading another ladder mid-flight. **The no-regression gate is against the tree you
merge INTO, measured now.**

---

## ⭐ THE HAZARD I EXPECTED WAS MEASURED ABSENT — AND IT WAS THE WRONG HAZARD

Predicted risk: main's 27 new commits mint descriptors with OLD tag numbers, which the renumber then
silently corrupts (the "asm is symbolic" class that has now failed five times, most recently a tag fused
inside `mov rax,0x200000009`). **Measured: 1252 lines of main-only src diff across 17 files contain
ZERO `DT_` references, ZERO `99`/`100` literals, and ZERO descriptor mints.** Three grep hits on mint
idioms were all false positives (`IR_LIT_INTEGER`/`IR_LIT_STRING` opcodes and comment prose).
The ζ ladder's 27 commits are entirely control-flow spine — frames, prologue/epilogue, zeta storage.

⇒ **THE NAMED, WELL-REHEARSED HAZARD WAS CLEAN AND THE MERGE BROKE ANYWAY.** The fault came through the
one file both sides touched, in a template whose control flow main restructured (`ZD-PL-A`, adding
`if (zdfp) {...} else {}` around the by-name dispatch) while the branch edited tags in the same file.
**An audit aimed at a known failure class does not license the merge; it only retires that class.**

⛔ **INSTRUMENT DEFECT, CAUGHT IN-SESSION, STATED BECAUSE IT NEARLY REACHED THIS DOCUMENT:** my first
reproducibility run reported `1016_eval` failing 4/4 deterministically — from a **relative path run out of
`SCRIP/`**, so all four runs measured `scrip: cannot open`. I had the "deterministic regression, N=4"
line ready. Re-run with absolute paths gave the real (and still deterministic) result. **A hash set that
agrees 4/4 proves determinism of whatever you actually ran; it says nothing about what you think you ran.**

---

## CONFLICT RESOLUTION OF RECORD (for whoever lands this)

Real source conflicts: **ONE.** `src/templates/xa_flat.cpp`, a single delete/modify hunk (HEAD side empty,
~500 lines on the branch side).
- Main deleted `xa_flat_prologue_str` + helpers outright (CARVE-KILL, Lon *"carve: just DELETE IT"*).
- The branch's **only** changes to that file are **11 lines, every one replacing a hardcoded `99` with
  symbolic `DT_FAIL`**, all inside the deleted block.
- ⇒ **Resolution is forced, not a judgment call: take main's deletion.** Deleted code needs no constants.

`src/templates/bb_call_fn.cpp` **auto-merged with no conflict — and is the prime suspect for the defect.**
The other 150 conflicts are generated `.s` artifacts (regenerable per RULES step 4, never a pinned golden).

---

## NEXT RUNG — MONITOR FIRST, DO NOT GUESS

1. ⭐⭐ **RUN THE 2-WAY MONITOR ON `1016_eval` AGAINST THE TRIAL MERGE.** Per RULES' MONITOR-FIRST rule this
   bug is NOT hunted by reading `bb_call_fn.cpp` and guessing — and this document deliberately does not.
   The bracket theorem applies cleanly: assertion 1 of 3 fails, so the divergence is early and the interval
   is short. **I name `bb_call_fn.cpp` as a suspect and explicitly do NOT claim it as the cause.**
2. The trial merge is reproducible from scratch: `git checkout -b <x> main && git merge tag-renumber-s229`,
   resolve `xa_flat.cpp` to main's deletion, `.s` to either side. Local scratch commit `fe9d692c`
   (**NOT pushed, must not be**).
3. Only after (1): re-merge, re-gate at main's THEN-CURRENT watermark (main moves — re-measure, never reuse
   this document's 200/117).
4. Still owed from s231, untouched this session: `SCRIP_NO_CU=1` Prolog gate · TAG-4 vs `rtx_arith.S` ·
   `VARVAL_fn` port · `eval_dynamic` 430× investigation.

⚠ **`.s` regen ×3 is OWED by any landing of this merge** (the branch touches templates) and was NOT run
this session, because nothing was landed.

⚠ **REPO HAZARD, UNRELATED BUT WORTH ONE LINE:** a fresh `git clone` of SCRIP lands on
`tag-renumber-s229`, **not `main`** — GitHub's default branch is currently the branch. Every parallel
session cloning fresh starts 27 commits behind main on a feature branch. Someone should flip the default.

`handoff_status.sh` is the push truth — NOT this block. **Nothing from this session is on origin.**
