# FINDING: `prolog-multiclause-uninit-lexprep-frame`'s remaining crash is `$disj0`'s γ-port reading a stale RSP-relative slot — a ζ-SPINE placement that the new BB FRAME-PLACEMENT CRITERION says must be ζ-ACTIVATION-FRAME, and PZ-4 (GOAL-PROLOG-100.md) is the un-landed mechanism that would fix it

**Seat:** seat07 · **Date:** 2026-08-27 (3rd pass, same day, same task) · **Repro:** `fact(a). fact(b). fact(c). main :- fact(X), write(X), nl, fail ; true.` — SIGSEGV both modes, unchanged from session baseline (rung13/14/15: 0/5, 2/5, 1/5). DONE-WHEN not met.

## Two prior leads ruled out this pass, with controls

1. **The recorded "`fact/1` resume_off is 448 in body vs 480 at call site, same by-name lookup" lead (this task's own `## NEXT`, earlier today) is a misdiagnosis.** Direct mode-4 `.s` inspection shows 448 and 480 are two *different* predicates' own resume slots, each self-consistent with its one caller: 448 = `fact/1`'s own slot, read only by `$disj0`'s call into `fact` (`n43_call_proc_staged_*`); 480 = the compiler-synthesized disjunction wrapper `$disj0/1`'s own slot (a separate `is_generator=1` proc, `frame_bytes=512`), read only by `main`'s call into `$disj0` (`n82_call_proc_staged_*`). Confirmed via a live `g_rt_gen_procs[]` dump at the crash (gdb): both procs' `.fn` pointers are valid. Not a cross-wired lookup.
2. **Clause indexing (`$ix_g`, gated by `lower_prolog.c:138 pl_no_ix()` / `SCRIP_NO_IX`) is not the cause** — `SCRIP_NO_IX=1` reproduces the byte-identical crash.
3. Read and confirmed clean/balanced, not implicated: `rt_gen_spine_resume_enter` (`rtx_icngen.S`, hand-ASM but trivially `inc`+`ret`), `rt_pl_cp_push3`/`pop3` (`rt.c`, plain C over a separate heap-backed choicepoint stack, never touches native `rsp`), `rt_proc_call_epilogue_ω` (`rt.c`, trivial).

## The actual fault, precisely localized

Breakpoint-trace-confirmed dynamic order: `main` enters `$disj0` fresh (`n82_α`) → `$disj0` calls `fact` fresh (`n43_α`) → `fact` matches clause `a`, suspends (`n4_suspend_α/β`) → [control returns to `$disj0`, which runs `write`/`nl`/`fail`] → `$disj0` retries `fact` (`n43_β`) → `fact` eventually exhausts all three clauses and reaches its own OMEGA port (`fact$2F1_ω`), which correctly pops its own 512-byte frame (`add rsp,0x200`) and correctly returns to `$disj0` at `n43+343` (`add rsp,0x10`) — **this leg is clean, verified instruction-by-instruction, not the bug.** `$disj0` then falls through to its second disjunct (`true`), compiled as `$disj0`'s own suspend node (`n52_suspend_α`), which does a plain `jmp` into `$disj0$2F1_γ` (`$disj0`'s own success port). That port executes:

```
mov  rcx, [rsp+0x218]
add  rsp, 0x230
jmp  rcx          ; rcx = 0x11 -> SIGSEGV
```

`[rsp+0x218]` is the exact slot `$disj0`'s own prologue used to save its *incoming* `rcx` (`mov [rsp+0x218], rcx` at `FN__$disj0$2F1+7`) — i.e. "the continuation `main` handed me for when I succeed." A hardware watchpoint on that address confirms it is written exactly once, at the prologue, with a valid-looking pointer, and never touched again — yet the γ-port's read comes back `0x11`. This is only possible if `rsp` itself has drifted between the write and the read, so `[rsp+0x218]` no longer names the same physical cell. (I measured this drift two different ways in this session and got two different numbers — 8 bytes one way, 568 the other — and did not reconcile the discrepancy before concluding the pass; treat both as unverified bookkeeping, not a settled number. The point that *is* solid, independent of the exact magnitude, is that a drift exists and a fixed-`[rsp+K]` read is not safe across it.)

The reason a drift exists at all: `fact` and `$disj0` are both multi-clause/resumable (`is_generator=1`) predicates whose RESULT/LOCALS — including the resume-continuation slot above — are placed at fixed `rsp`-relative offsets computed once by `ir_drive_slot_assign`/`zls_build` (`ARCH-ZETA-LOCAL-STORAGE.md`'s **M5 flat model**: "a single compile-time bump cursor... for the life of the program"). Between `$disj0`'s own γ-suspend and its later γ-success there is, by construction, unbounded intervening stack activity: repeated fresh `fact` re-entries (each a new `sub rsp,0x200`), plus whatever `write`/`nl`/`fail` do.

## Why this is architectural, not a one-instruction bug

Lon's **BB FRAME-PLACEMENT CRITERION**, landed today (`.github` `d3fd64e1`, RULES.md new section, telegram `lon-frame-placement-criterion-and-read-the-arch-docs`): RESULT/LOCALS stay on ζ-SPINE (RSP) *iff every consumer reaches them at a fixed compile-time offset on every path*; unbounded γ→β growth between suspend and resume — named explicitly as "the canonical instance" — forces them to ζ-ACTIVATION-FRAME (RBP) instead. This repro's crash is exactly that window. It is also not a new observation: this same task's own `## LON DESIGN RULING s273` (2026-08-24) already said *"the frame's retry/resume state is BB LOCALS at the activation-frame zeta; make it that,"* and `GOAL-PROLOG-100.md`'s LIVE CURSOR names the mechanism that does this and marks it **not yet landed**: **PZ-4**, "predicate activations under the tier law... multi-clause/resumable predicates take the ζ-ACTIVATION tier via `zdp_tier`/heap-fb ADOPT — never a hand predicate," called *"the keystone, gap 1"* there.

Three same-day passes on this row (mine and the prior one) each patched a real, individually-verified defect (the `rt_jmp_frame_lexprep2` no-op, a missing `[fb+0]/[fb+8]` trail-mark mirror, an RTCC-veneer register clobber) and each time the crash relocated one layer deeper rather than closing — consistent with patching symptoms of a spine placement that PZ-4 is supposed to replace, rather than the underlying tier being wrong.

## Recommendation

Not proposing to land PZ-4 in this pass — it is a shared, five-site mechanism per its own description in `GOAL-PROLOG-100.md`, not something to hand-roll again inside this one row, and out of scope for a quick cure. Whoever continues this row should either (a) gate it explicitly on PZ-4 landing rather than continuing independent offset-chasing, or (b) if PZ-4 lands first, re-run this exact repro before spending more time on the specific rsp-drift instruction — it is very likely a symptom PZ-4 dissolves wholesale, the same way the "448 vs 480" lead turned out to be a symptom rather than the cause.

No source changes made this pass (read-only + gdb instrumentation only); nothing to commit in SCRIP/corpus. Reported via mail to hq_C (`lexprep-frame-disj0-gamma-localized`, `lexprep-frame-is-a-pz4-tier-violation`) before this FINDING was written; this file is the durable version.

## Related, same day

`FINDING-2026-08-27-seat04-prolog-multiclause-backtrack-fail-segfaults.md` independently hit the same repro shape from a different starting task (`prolog-unify-var-compound-segv`) and filed it as a fresh, uncharacterized row rather than folding in — that row and this task (`prolog-multiclause-uninit-lexprep-frame`) are very likely the same underlying defect and should be reconciled by whoever owns row triage, rather than tracked twice.
