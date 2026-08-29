# FINDING 2026-08-29 (seat10): N-2 default-ON (ceo s283f, `0b35b5fc`) exposes a general, pre-existing, 100%-reproducible SIGSEGV — ANY generator called via `!`-apply crashes, no self-recursion or other special shape required

**Build:** SCRIP `937d982d` (the commit immediately after the gate-flip landed, before this seat's own row's commit exists at all — confirmed with a disposable `git worktree` at that exact commit, zero trace of this seat's work). `RT_OPT=-O0`. Row this seat was actually working: `icon-n2-recursive-generator-per-activation-storage`. This finding is a **byproduct** of that row's own verification pass, not its subject — flagging separately because it is unrelated in cause and far wider in blast radius.

## The one cause

`src/templates/bb/bb_call_value.cpp` — the template that emits Icon's `PROC ! ARGLIST` apply-call form — has **zero references to `icn_genframe2()`, `icn_gen_regime()`, or any N-2 machinery** (confirmed by grep: zero hits). It never pushes a REGION pointer onto the entry stack the way `bb_call_proc_staged.cpp`'s plain positional-call path does (the "N-2 STEP 3 REGION HAND-OFF" block, `bb_call_proc_staged.cpp:774`). But a called generator's own α-prologue (`emit.cpp`, the `icn_gen_regime() && g_emit.flat_gen` arm, `emit.cpp:2862`) is **unconditional on how it was called** — it always reads `[rsp+16]` as REGION and writes through it. Call a generator via apply, and that slot holds whatever garbage happened to be on the stack, not a region pointer — the prologue then writes through it as if it were one.

## Reproduction — minimal, non-recursive, no flags

```icon
procedure gen(x);
   suspend x | x + 1 | x + 2;
end

procedure main();
   every write(gen ! [10]);
end
```

`./scrip --run witness.icn < /dev/null` (no env vars — the gate is default-ON as of `0b35b5fc`). **SIGSEGV, 3/3 runs, both on tree `f4e8487f` (this seat's own working tree) and independently on a disposable worktree at `937d982d` with zero trace of this seat's changes.**

## Why this reads as non-deterministic if you only see it once

Because the garbage read from `[rsp+16]` is uninitialized stack content, the *symptom* varies run to run even though the *cause* is 100% deterministic (always crashes eventually) — one capture in this session showed a clean SIGSEGV, another (on a self-recursive generator, different repro, same root cause) showed a controlled Icon-level `** Error 3 — Erroneous array or table reference` (rc=1), and a third showed rc=0 with silently empty output. **Do not read any single one of those symptoms as "the bug," and do not read a clean exit as evidence it's fixed** — re-run a few times before trusting a "doesn't crash" reading on anything that reaches this path.

## Scope — this is NOT about self-recursion, and NOT about this seat's row

This seat's own row (`icon-n2-recursive-generator-per-activation-storage`) exists because `geddump.icn`'s `gedwalk` (`suspend r | gedwalk(!r.sub)`) is *directly self-recursive*, and that row's own bounded-storage fix (SCRIP `f4e8487f`, gated behind a separate, additional, default-OFF `SCRIP_ICN_N2_SELFREC` flag, verified end-to-end correct for 24432 real calls via gdb) is unrelated to this gap. While chasing why `geddump.icn` *still* doesn't run clean even with that fix armed, the actual next crash turned out to be `gedsub` (a *different* generator in the same file, *also* self-recursive — `suspend gedsub ! push(f, x)`) — but the witness above proves the mechanism has nothing to do with self-recursion at all: **any** `PROC ! ARGLIST` call to **any** generator, recursive or not, hits this the moment the gate is on, which as of `0b35b5fc` is always, by default.

⛔ **The D2-suspend witness set (`test_icn_d2_suspend_witness.sh`), the instrument the gate-flip decision was measured against, does not appear to exercise `!`-apply at all** (not verified exhaustively against the script's own source in this pass — worth confirming directly before trusting that suite's ALL-GREEN as covering this shape). If it doesn't, the flip's own acceptance criterion has a blind spot of exactly the shape this project's culture already has a name for (a green, convenient suite is not a representative populator — see the raku frontend row's own `[[feedback_verify_against_populator_not_convenient_suite]]`).

## What this seat did NOT do

Not attempted: giving `bb_call_value.cpp` real N-2 region-handoff awareness. That is a second call-emission template needing the same care `bb_call_proc_staged.cpp` already received across many sessions (region sizing, stack-parity, the loud-refusal discipline) — real, separate, unscoped design/implementation work, not a quick patch, and squarely outside this seat's own row. Flagging with a minimal, fully-isolated, twice-independently-reproduced repro instead of guessing at a fix.

## Suggested next step (not a ruling — routing, not deciding)

Someone who owns N-2 / the gate decision should see this before more sessions build on the default-ON assumption. Candidate options, undecided here: (a) a targeted killswitch narrower than `SCRIP_ICN_GENFRAME2=0` — refuse loudly specifically at an apply-call site whose target is a registered generator, until `bb_call_value.cpp` gets real support, mirroring `bb_call_proc_staged.cpp`'s own "refuse loudly rather than read garbage" discipline; (b) mint `bb_call_value.cpp` N-2 support as its own row; (c) re-examine whether the gate-flip's own acceptance instrument needs an apply-call witness added before the flip is trusted as fully measured. Sent to this seat's owning HQ (`hq_B`) via `s4e_msg.sh ask`; not deciding unilaterally.
