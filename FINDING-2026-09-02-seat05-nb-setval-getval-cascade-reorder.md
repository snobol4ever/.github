# FINDING nb-setval-getval-cascade-reorder — CURED (partial scope of P6)

⛔ **SUPERSEDED 2026-09-03 (seat05, FLEET-8) — DO NOT REAPPLY.** The Prolog rung-0 rebuild (SCRIP
`db299d417` onward, law RULES.md § THE PROLOG REBUILD GATE) deleted the code this cure touched:
`script_try_call_builtin_by_name` no longer contains `nb_setval`/`nb_getval` at all (`grep -rn
"nb_setval\|nb_getval" src/`, checked post-rebase on `a3faade17`, zero hits in `by_name_dispatch.c`).
`nb_setval`/`nb_getval`/`b_setval`/`b_getval` are now named in `src/lower/lower_prolog.c:186`'s
`pl_rung10_builtins[]` — explicitly deferred to construct-ladder rung 10 as a compile-time-wired leaf
(`rt_nb_setval_term`/`rt_nb_getval_term`, declared in `src/runtime/rt/rt.h` and
`src/templates/bb/bb_common.h`), not a runtime string dispatch at all. This session's local `git stash`
holding the matching code diff has been dropped as unappliable; the content was already preserved
unproven at `/home/resources/postoffice/salvage/seat05-prolog-builtins-wired-at-compile-time-not-dispatched-by-name-2026-09-02.patch`
per the task's own LEDGER. Kept below unmodified as the historical record of the METHOD (isolating a
cascade-position effect on a purpose-built fixed-work witness), which remains valid technique even
though this specific application is moot — do not cite the RESULT numbers below as current-tree facts.

## SYMPTOM
Task `prolog-builtins-wired-at-compile-time-not-dispatched-by-name` (ladder P, rung P6) was redirected
by a ceo ruling (routed via hq_P, 2026-09-02 ~08:37/08:38) away from `plc_*` internals (rung 1's
`dop_ax`/`dop_cmp` cure was confirmed harmless-but-waste, since it optimizes code C36 is about to
delete) and toward "the shared strcmp cascade" instead. The baton's own two paragraphs disagreed on
which function that cascade lives in (`try_call_builtin_by_name` vs `script_try_call_builtin_by_name`)
— verified directly rather than trusting either: `script_try_call_builtin_by_name`
(`src/runtime/by_name_dispatch.c:1702-4253`, confirmed via `grep -n "^int script_try_call_builtin_by_name\|^static int bn_type_datatype"`)
is the real ~251-entry flat `if (!strcmp(fn, "..."))` cascade, with no entry guard. It is genuinely
shared: reached from Prolog's `plc_det_exec` (unconditionally for `$write`, and for the whole
`case 'd'` ~99-entry det-builtin set via `s->det`), from `rt_call_arr_impl` (any frontend's dynamic
`$name` call), and as `try_call_builtin_by_name_bl`'s own fallback after its faster `bid_of`/datatype
paths miss.

## ROOT CAUSE
The cascade pays one `strcmp` PLT call per entry scanned before a match (or a miss). Order is
significant only for cost, never for correctness (each check is a self-contained exact-string test
with no dependency on any earlier check having run, confirmed by reading every branch's guard). Two
specific entries, `$nb_setval`/`$nb_getval` (`nb_setval/2`, `nb_getval/2` — global-variable set/get,
no I/O, fully deterministic), sat at cascade rank ~122 of 251 — up to 121 preceding `strcmp` calls
paid on every call. The task's only crash-free van Roy witnesses (`fib`/`tak`/`deriv`) make 7 total
by-name calls combined and never reach this path, so a purpose-built witness was required to measure
it at all (see METHOD).

## FIX
`src/runtime/by_name_dispatch.c`: relocated the `$nb_setval`/`$nb_getval` block (unchanged internally,
own local `extern` declarations, no dependency on file position) from its original position to the
very first check inside `script_try_call_builtin_by_name`, right after the function's opening brace
(which carries no preamble/null-guard to preserve). Pure data-order change: 8 lines removed from their
old position, the same 8 lines (plus a 14-line WHY comment) added at the top. No new global or static
state (the project's NO-NEW-GLOBALS law needs an in-chat grant from Lon that this session has no path
to obtain, so a call-site pointer-identity MRU cache — the alternative shape considered and rejected —
was out of reach; a pure reorder needs no such grant). This is a *partial* cure of the row's scope: the
other ~249 entries, and the general "shared cascade is O(n)" shape, are untouched — see NEXT ACTOR in
the task baton.

## METHOD — witness
`nb_setval_getval_loop.pl` (new, purpose-built; not committed to corpus — a diagnostic instrument for
this row, not a published benchmark): `loop(N) :- nb_setval(counter,N), nb_getval(counter,_), N1 is
N-1, loop(N1).` driven from `N=2000`. First attempt used `N=20000` (matching the scale of other Ir
witnesses in this codebase) and reliably stack-overflowed under valgrind's simulated stack
(`Stack overflow in thread #1... at pl_make_ref`) even with `ulimit -s unlimited` on the host — valgrind
caps its own client stack independent of the host rlimit. `N=2000` is clean in both arms, direct-run
and under callgrind, in both the control and treatment binaries.

Compiled mode-4 (`--compile --target=x86`, `as --64`, `gcc -no-pie ... libscrip_rt.so`), measured with
`scripts/profile_callgrind.sh` (`valgrind --tool=callgrind --smc-check=all-non-file`), `RT_OPT=-O0`,
fresh `make pristine` for each arm (control = tree at `8441fd263` post-rebase, before this file's edit;
treatment = same tree plus only this edit), `git diff` reviewed clean before each build (no stray
changes). stdout captured separately from the callgrind run and diffed byte-for-byte between arms.

## RESULT
```
control:    TOTAL_Ir=33,807,029   stdout="done"   (script_try_call_builtin_by_name: 5,725,334 Ir, 16.94% ; __strcmp_avx2: 13,323,719 Ir, 39.41%)
treatment:  TOTAL_Ir=15,975,435   stdout="done"   (script_try_call_builtin_by_name:   657,446 Ir,  4.12% ; __strcmp_avx2:  1,359,999 Ir,  8.51%)
```
Multiple (reference/ours, FACT RULE): **2.1162x** (33,807,029 / 15,975,435). 17,831,594 Ir saved
(52.7%) on this fixed-work witness. Output byte-identical both arms (`diff` clean); no crash, no
valgrind warning in either arm's log. `script_try_call_builtin_by_name`'s own cost fell 8.7x;
`__strcmp_avx2` fell 9.8x — consistent with cutting ~120 `strcmp` calls from each of the witness's
4,000 dispatch calls (2,000 `nb_setval` + 2,000 `nb_getval`).

⛔ This multiple is specific to a witness built to isolate this one mechanism — it is not a claim about
whole-program Prolog performance. Ordinary Prolog programs that rarely or never call `nb_setval`/
`nb_getval` will see zero effect from this specific change; the value is in the METHOD (isolating and
proving the cascade-position mechanism) and the ~120-strcmp-call class it demonstrates, not in this one
pair of builtins mattering on its own.

Gates (this tree, post-edit, pristine): SNOBOL4 blocking board, Prolog/Icon/Snocone smokes, Prolog
master board — see task LEDGER for the verbatim run this session logged them in.

## NEXT ACTOR
The general shape (~251-entry flat cascade, no structural pruning) is untouched. Two honest
directions, unchanged from the baton's own prior framing: (a) a systematic first-byte/second-byte
bucket restructuring (like the existing `SNO$NOFAIL`/`rt_call_arr_impl` s271 precedent, generalized)
— bigger, touches most of the ~251 sites, real risk of transcription error at that scale in one
sitting; (b) keep promoting individually-justified, individually-measured hot entries one at a time,
same shape as this cure — safer per-step, slower to converge. This session picked (b) once, on the
best-justified single entry found; did not attempt (a).

## LINKS
LADDER:P RUNG:P6 · task `/home/resources/postoffice/tasks/prolog-builtins-wired-at-compile-time-not-dispatched-by-name.task.md`
· precedent: `FINDING-2026-08-24-seat08-by-name-dispatch-sno-nofail-cure.md` (the byte-guard shape,
not used here since a pure reorder needed no new comparison logic at all) · SCRIP commit: see task LEDGER.
