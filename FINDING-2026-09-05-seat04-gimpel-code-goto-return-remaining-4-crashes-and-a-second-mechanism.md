# FINDING: 4 of the 9 gimpel CODE()+indirect-goto crashes need a second fix, not this one

seat04, 2026-09-05, working `snobol4-return-after-a-code-object-transfer-crashes` (minted by hq_C).

## What the row's own fix covers (landed: SCRIP 2802d93db, corpus cfa277fa9)

`bb_goto_deferred()`'s two fast-path arms (DEFINE-FOLD, TAIL-TRANSFER) jump straight to an
external label from inside a runtime `CODE()`/`EVAL` fragment without releasing the fragment's
own CLASS-C stack carve (`xa_flat_chain_prologue_str`'s `sub rsp,kt`). The enclosing function's
next `RETURN` then pops that leftover carve instead of its own `{gamma,omega}` pair. Fixed by
releasing the carve in both arms, gated on `g_rt_fragment_emit && xa_flat_class_c_pred()` so
ordinary procedure-internal gotos are untouched.

Verified against the task's own witness and against the Gimpel drivers named in its GOAL text:
**SEQ, AI, AOPA, CATA, TRUNC** now match the SPITBOL oracle exactly (rc=0, both modes). Two
corpus witnesses testing this exact mechanism were promoted from XFAIL: `array_replace_2` and
`user_function_code_eval_array_replace_branch_1`.

## What's still red (same GOAL text named these too, as part of "9 of 11")

**LPROG, TPROFILE, FPROFILE, RSELECT** (`corpus/packages/snobol4/gimpel/{LPROG,TPROFILE,
FPROFILE,RSELECT}_driver.sno`) still crash after this fix — 2 of the 4 with a *different signal*
than before (TPROFILE/FPROFILE: rc=132 SIGILL; LPROG/RSELECT: rc=139 SIGSEGV, same as before).

`LPROG.sno` shows why this is a **separate mechanism**, not a residual case of the one just fixed:

```
	DEFINE('LPROG()')			:(LPROG_END)
LPROG		:<CODE(' LPROG = &STNO :(RETURN)')>
LPROG_END
```

The witness this row fixed had the *fragment* goto to an ordinary named label back in the
enclosing function (`:(F_2)`), and the enclosing function's *own, separate* `RETURN` statement
crashed afterward. Here the **fragment itself** directly targets the literal name `RETURN` —
there is no separate enclosing-`RETURN` statement for the stack-carve fix to protect. Every
`DEFINE`'d procedure emits its own `RETURN`/`FRETURN` floater as a same-named local assembly
label (confirmed: `src/templates/bb/bb_define.cpp`'s role 1/2 arms literally emit a label named
`RETURN:`), so a `CODE()` fragment's `rt_goto_resolve("RETURN")` — a global, name-keyed lookup
(`body$RETURN` cell / `rt_label_get_fn`) — has no way to know which enclosing activation's
`RETURN` it should mean. This is a resolution-target question, not a stack-hygiene question, and
is outside this row's fix and its DONE-WHEN.

Not investigated further here — SHARED-NODE scope note on the row says CODE()/call-return is
reached by more than SNOBOL4, and rank5's own note calls the gimpel_triage class5 SIGSEGV "still
open — not this row's to fix"; this is the same posture applied to the 4 remaining drivers.
Recommend a new row, e.g. `snobol4-code-fragment-goto-return-resolves-wrong-activation`,
scoped to whichever HQ/lane owns gimpel triage next (hq_C at time of writing, MODE FLEET-16
SNOBOL4-only).

## A separate, pre-existing, unrelated master-suite FAIL noticed in passing

`user_function_len_defer_branch_6` (master suite) fails in both m3 and m4 — wrong match outcome
on `p = LEN(1) . *(n = n + 1)` matching `subj p` against `subj = "A"` (expects "nomatch", SCRIP
matches). No `CODE()`/`EVAL`/indirect-goto involved; confirmed present, byte-identical, before
this row's SCRIP change (base tree 36a34de53) and after — not caused by, and not fixed by, this
row. Flagging so nobody re-chases it as a regression from 2802d93db/cfa277fa9.
