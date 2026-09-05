# FINDING — two snobol4 master entries are pinned GREEN to their own "could not read" message

**Seat:** hq_T (HQ-TEST) · **Date:** 2026-09-05 ~14:05 CDT · **Mode:** FLEET-20
**Tree:** corpus `cb0723bb2` · **Found by:** materializing the companion closure and watching two green entries go red.

## The claim

Two entries of `corpus/tests/snobol4/ALL.sno` have a `.ref` that is, verbatim, the program's own missing-input error:

| entry | origin | its entire `.ref` |
|---|---|---|
| `user_function_arbno_span_replace_branch_3` | `scrip_test_demo_claws5__claws5` | `Could not read CLAWS5inTASA.dat` |
| `scrip_test_treebank-prepend` | `scrip_test_snobol4_treebank-prepend__treebank-prepend` | `Could not read VBGinTASA.dat` |

Both **PASS** on every board. They pass because the data file is not there and the program says so, and the ref
records it saying so. The entry grades its own inability to start.

## Measured

`CLAWS5inTASA.dat` (65 KB) and `VBGinTASA.dat` (98 KB) exist — under `corpus/demos/snobol4/{claws5,treebank}/`,
which the grader cannot reach (not beside the master, not in `corpus/include`, so not on `$SNO_LIB`;
see [[FINDING-2026-09-05-hq_T-the-corpus-resolves-includes-through-sno-lib-so-a-hand-run-and-the-board-disagree]]).
Copy them in beside the entry and both go **RED** at once:

```
user_function_arbno_span_replace_branch_3 : ref 32 bytes  ->  real output 229,009 bytes
scrip_test_treebank-prepend               : ref 29 bytes  ->  real output 133,156,180 bytes
```

⛔ **So supplying the missing dependency is not the cure by itself.** A 133 MB output is no kind of suite entry,
and the 229 KB one was never graded against anything. The refs would have to be re-cut from the oracle with the
data present, and the treebank entry probably should not be a master entry at all — it is a demo.

## ⭐ Why it matters more than two entries

This is the **failure shape a green board cannot show you**. `CLAUDE.md` already carries "a green board is
necessary, never sufficient" with the `(A , B)` witness; this is the same law from the other side — not a defect
the board misses, but a *pass* the board manufactures. Anything whose expected output is an error message about
its own inputs will pass forever, and it will pass hardest exactly when the corpus is most broken.

⭐ The tell is mechanical and worth sweeping for across all seven suites: **a `.ref` that matches the program's own
diagnostic vocabulary** (`could not read`, `cannot open`, `No such file`) is a candidate false green. Not yet swept
— named here so the sweep is a row and not a memory.

## Disposition

**Not cured here, deliberately.** `tests/snobol4/config/COMPANION_PATH` names the two demo dirs as excluded, with
this file as the reason, so the closure tool cannot "fix" them into two reds on the shared blocking board. The ref
question belongs with whoever owns the faulty-test class (hq_P's `snobol4-every-xfail-fixed-as-a-faulty-test-or-
cured-as-a-defect` is the nearest row).
