# FINDING 2026-08-29 (seat01) — polyglot "main" collision found and fixable, but its fix unmasks a second bug in 2 demos outside this row's scope; neither landed

Row: `m3-passes-m4-fails-three-polyglot-demos`. Full receipts: `tasks/m3-passes-m4-fails-three-polyglot-demos.task.md` §LEDGER. This file is the reusable lesson, not a duplicate of that ledger.

## The shape: a "false green" is worse than the failure it's masking, and finding one usually means there are more
`corpus/demo/scrip/demoNN/*.scrip` files are markdown with fenced SNOBOL4 + Icon + Prolog sections, merged by
`src/driver/polyglot.c` into one compiled program. Every section that independently defines something reducible to
`main` (SNOBOL4's implicit top-level, Icon's `procedure main()`, Prolog's `:- initialization(main, main)` goal)
collides on that literal proc-table name. `src/driver/scrip.c`'s two `main`-resolution loops (`:1259` mode-compile,
`:1698` mode-run) pick the entry via `if (strcmp(pname, "main") == 0) { main_bb_idx = ...; continue; }` — no `break`,
no first-wins guard — so the **last**-registered "main" silently wins. In every one of these three-section demos,
that means a Prolog variant wins and SNOBOL4's own code is never emitted at all.

**This was invisible in `demo01` for one specific reason: its SNOBOL4 and Prolog sections both print "Hello, World!".**
The gate compares stdout, not which code ran. `demo01`'s recorded PASS has been a coincidence of matching
cross-language output the entire time, not evidence the intended section ever executed — confirmed the same way
`demo04`'s failure was diagnosed: `--dump-ir` shows 3 `; proc main` graphs, and the pre-fix `main:` body in the `.s`
is provably Prolog's code (`rt_pl_dop_trail_mark@PLT`, `CALL_PROLOG` chains), not SNOBOL4's `OUTPUT =` idiom.

**Enforcement for the next reader of ANY "this looks like it passes" polyglot/multi-source result:** matching output
is not evidence the intended code path ran, in any system that can silently select among multiple candidate entry
points. Where cheap, verify by content (`--dump-ir`, or diffing the emitted symbol's body against what the source
you *meant* to run should produce), not by output-string equality alone — especially when a corpus's own sections
are deliberately written to be *interchangeable in meaning*, which is exactly what makes coincidental matches likely
rather than rare here.

## Why the obvious fix isn't landed
The fix for the collision itself is a one-line guard (`if (main_bb_idx < 0) main_bb_idx = ...;` at `scrip.c:1259`)
and works cleanly in isolation (verified on a minimal 2-section SNOBOL4+Prolog repro — m4 goes from empty/rc=1 to
correct output). Landing it and re-running the **full** demo gate (not just this row's 3 named demos) measured a
regression outside this row's scope: `demo03` and `demo08` also carry the identical masked collision, and once
SNOBOL4's own code is correctly selected instead of Prolog's coincidentally-matching code, `demo03` SIGSEGVs and
`demo08` empties to rc=1 — both **newly failing**, dropping the gate's overall m4 PASS from 4 to 3, while this row's
actual targets (`demo04`/`demo09`) stay divergent regardless (same DONE-WHEN verdict, just a different failure
shape). Reverted; working tree confirmed back to the exact original baseline before any of this session's edits.

Root cause of what `demo03`/`demo04`/`demo08`/`demo09`'s *real* SNOBOL4 code hits once selected: `rt_proc_t.fn` for
a `DEFINE`'d procedure (`check`, `palindrome`, etc.) resolves to the wrong code address at the call site — measured
live via gdb (`rt_proc_call_open_slim`'s fast path takes a bogus, non-null address and jumps into it). Traced to the
compile-time argument passed to `rt_define_site`: `lea r9, [rip + <next-node-label>]`, i.e. "the DEFINE's own
function body is the very next node in program order" — true and correct for every plain single-language SNOBOL4
program (confirmed: a SNOBOL4-only build emits the identical-looking pattern and works), but evidently not safe
against however node numbering/ordering works across a polyglot-merged AST. Not localized further than "somewhere
in `lower_snobol4.c`'s DEFINE lowering or `bb_define.cpp`'s address computation" — a distinct, larger unit of work
from the collision fix, not attempted here.

## What this means for the campaign, stated as a question rather than decided here
At minimum 5 of the 10 "working" polyglot demos (`demo01`, `demo03`, `demo04`, `demo08`, `demo09`) carry this
"wrong section silently ran" defect underneath their current grade; only `demo01`'s happens to still read as correct
by coincidence. Fixing the collision (Bug 1) is honestly the right direction — it makes MORE demos actually run the
code they claim to, not fewer — but it can't land alone without also curing the DEFINE-address bug (Bug 2) or
accepting a measured, named regression on `demo03`/`demo08` in exchange for exposing (not creating) their real
state. Routed to hq_C (correctness owner) rather than decided unilaterally: `ask` topic
`polyglot-main-collision-bug1-vs-bug2`.
