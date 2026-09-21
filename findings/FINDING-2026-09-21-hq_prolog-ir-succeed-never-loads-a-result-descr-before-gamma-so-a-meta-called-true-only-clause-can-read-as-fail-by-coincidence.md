# FINDING 2026-09-21 hq_prolog: `IR_SUCCEED` never loads a result DESCR before γ, so a meta-called `true`-only clause can read as FAIL by coincidence

⛔ SHARED NODE. `IR_SUCCEED` is emitted by all five lowerers (`lower_prolog.c`, `lower_snobol4.c`, `lower_icon.c`,
`lower_raku.c`, `lower_pascal.c` — measured `grep -rln IR_SUCCEED src/lower/*.c`). This is a report of measured
behavior, not a landing — RULES.md says a change to a node more than one frontend lowers to is an ASK to the
officer, never a landing from this seat. Routed to `ceo` the same session (`s4e_msg.sh ask`).

## What's measured

Row `prolog-three-blocking-gates-are-red-on-origin-and-the-cfo-proved-they-are-not-theirs`, gate
`test_gate_pl_iso_rung2_runtime_heads_and_meta_call_wrappers.sh`, group `asserta_1`: m3_pass=24 (floor 24, green),
m4_pass=21 (< floor 24, red) — three cases (`iso_asserta_1_01/02/03`) print `@V skipped` in m4 where m3 prints
`@V succ`. Tree `77922bcf8` (SCRIP), reproduced standalone outside the grader.

Minimal repro (`/tmp` scratch, not committed): a program containing `'$lgt_cond' :- true.` called only through
`catch('$lgt_cond', _, fail) -> ... ; ...` — i.e. through the generic call-by-name path, the same one
`plc_portray_hit` uses for `portray/1` (`src/runtime/unification.c:295`, `rt_pl_goal_gen_h_c` →
`rt_proc_call_gen_h`, `src/runtime/rt/rt.c:1157`). With the ISO asserta_1 shim file's 190 lines of scaffolding
present, `'$lgt_cond'` **reads as FAIL** in m4, even though its body is the literal atom `true` and m3 (interpreted)
reads it correctly as succeeding. Removing one unrelated clause anywhere earlier in the same file
(`lgt_near(A, B) :- A =:= B, !.`, never called) flips the verdict back to correct. Swapping that clause's body for
anything else that isn't `=:=` immediately followed by `!` also makes the bug disappear — the trigger is not
semantic, it is purely a side effect of total compiled-code layout shifting by a few bytes.

ASM-DIFF-FIRST, scoped to m4 (RULES.md § MODES MAY DIVERGE / § ASM-DIFF-FIRST): `FN__$lgt_cond$2F0`'s own emitted
bytes are byte-IDENTICAL between the passing and failing builds (`diff` on the extracted function body, zero
lines). Exonerated. The divergence is not in that function's code — it is in what garbage happens to be sitting in
`%rax` when it's read.

gdb (SIGSEGV/ptrace-clean, no monitor): `bb_succeed()` (`src/templates/bb/bb_succeed.cpp`) is
`x86_alpha() + x86_gamma() + x86_beta_trampoline()` — nothing between α and γ. For a clause whose ENTIRE body is
`true`, the lowerer (`lower_prolog.c:1516`, `if (!strcmp(nm, "true")) return build(cx, IR_SUCCEED, ...)`) reaches
this box with no other goal executed, so **nothing ever loads a defined DESCR_t into the result-carrying
registers before γ forwards them** (`γ: mov rdi, rax; mov rsi, rdx; ...`). At function entry, `%rax` had just been
used as scratch for `lea rax, [rip+...]` (saving a frame-map continuation address for `rt_jmp_frame_lexprep2`) and
is never touched again before the fall-through to γ, so **that leftover code-address bit pattern is what gets
carried out as "the call's result."** It threads unmodified through `rt_gen_spine_pass_γ` and lands at the
caller's own generic dispatch check, `cmp $0x68, %al` (`0x68` = `DT_FAIL`, `src/ir/descr.h:27`) — measured:
`%al == 0x68` in the failing build (`%rax = 0x41e368`, coincidentally `$lgt_cond$2F0_ω+21`'s address), `%al ==
0x4c` in the passing one (`%rax = 0x41e24c`). Same code, same semantics, different leftover pointer, different
low byte, different verdict — undefined behavior masquerading as a real answer, exactly the class of thing
RULES.md's cheap-recipe-test names ("what would be different if the stated reason were false?").

`bb_cut()` (`src/templates/bb/bb_cut.cpp`, Prolog-only per `grep -rln IR_CUT src/lower/*.c`) has the identical
shape — `cut_barrier()` does register/memory bookkeeping for B/F.CUR/F.RES but never loads a result DESCR either
— which is why the trigger needed a clause ending in cut (`A =:= B, !.`) rather than any arbitrary extra clause:
cut is the other construct on this file that reaches γ without ever setting a value, and it's what happened to
shift the layout by exactly the right amount this time. `bb_cut` is not itself shared (only Prolog lowers
`IR_CUT`), so it is in-lane, but a narrow Prolog-only cut fix does not touch the far larger `IR_SUCCEED` surface
every other language shares, so it is named here rather than treated as the fix.

## What this means

Any clause whose body is `true` (Prolog), or the equivalent trivial-success construct in SNOBOL4/Icon/Raku/Pascal,
returns an UNDEFINED garbage DESCR when invoked through a generic call-by-name/meta-call boundary (`catch/1`,
`call/N`, `\+/1`, `portray/1`'s hook, `findall`'s goal argument, and anything else that inspects the returned
DESCR rather than only following the port that was reached). Direct statically-wired calls inside a clause body
are NOT affected — they follow the wired α/β/γ/ω jumps directly and never inspect a returned DESCR as a boolean.
The failure is silent and content/layout-dependent: most of the time the leftover garbage's relevant tag byte
does not happen to collide with `DT_FAIL` (or whatever sentinel the reading side checks), so it reads as success
by luck. This is very likely an unnamed contributor to otherwise-unexplained flaky reds anywhere a board runs the
same source through a generic goal-call path — worth a grep for `IS_FAIL_fn`/`rt_proc_call_gen_h` callers across
languages before assuming any single one of those is a language-specific defect.

## Proposed shape of a cure (NOT landed, for the officer to judge)

`bb_succeed()` and `bb_cut()` both need to load a defined "TRUE" DESCR_t into the result-carrying registers
before falling into `x86_gamma()`, OR `x86_gamma()` itself needs a variant that defaults the result when the
caller hasn't supplied one. Either touches a node every frontend lowers to (`IR_SUCCEED`) or the shared γ helper
itself (`x86_asm.h`) — base-vs-head gate by gate across SNOBOL4/Icon/Raku/Pascal/Prolog is exactly the measurement
RULES.md's SHARED-NODE VERDICT SCOPE requires before any landing, which is beyond this seat's lane.

## Status on the row

`prolog-three-blocking-gates-are-red-on-origin-and-the-cfo-proved-they-are-not-theirs`: print_1 CURED and GREEN
(unrelated single-site Prolog-only fix, `src/runtime/unification.c` `plc_portray_hit`'s success check was
`r.v == DT_I` where the codebase's actual idiom is `!IS_FAIL_fn(r)` — landed). rung2 is BLOCKED on this shared-node
root cause for the `asserta_1` group specifically; the other eight rung2 groups are unaffected (assertz_1,
abolish_1, retract_1, retractall_1, clause_2, cut_0, call_1, call_N all green m3 and m4).

⭐ SECOND CONFIRMED INSTANCE, same session, DIFFERENT gate: rung7
(`test_gate_pl_iso_rung7_a_cut_inside_a_findall_bagof_setof_goal_has_its_own_barrier.sh`) is also red, in group
`if_then_2` only (the other six arms of that gate are green both modes) — case `lgt_if_then_2_10`, m4_pass=10 <
floor 11, same `skipped`/`the case's own condition(...) option is false on this system` shape, same absent
`condition(...)` on the case (`test/2`, not `test/3`), same shared `'$lgt_cond' :- true.` shim line every
generated program carries. **This is very likely NOT a genuine rung7 cut-barrier defect** — the row named it as
one of "three different defects wearing one row" and warned against looking for one cause, and that warning was
right to give, but the measurement now says two of the three (rung2's `asserta_1` and rung7's `if_then_2`) are
the SAME shared-node coincidence landing on two different files' incidental byte layouts, not two independent
Prolog defects. Only `print_1` was a real, distinct, Prolog-lane bug. Worth the ceo/cto knowing before either row
is graded as "two defects owed" — it is one shared-node cure away from clearing both.
