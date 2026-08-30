# FINDING 2026-08-30 seat03 — pascal-m4-site1-forloop-backedge-64byte-excess

## Two things, one corrects every prior FINDING on this row, one is new empirical ground truth.

## (1) CORRECTION: the node range everyone has been discussing is NOT the sort's swap conditional

Every prior session on this row (seat03's own 2026-08-29T22:44Z pass onward, then seat13, hq_P,
seat01, seat05) describes the `h=58` / `i=58..66` span as "the swap-conditional body (`if
a[j]>a[j+1] then swap`)" or "the swap body." **This was never verified against the actual emitted
source-line comments and is wrong.** Read directly off `/tmp/bubble.s` (`--compile` output,
`scrip` @ pristine tree this session):

- `n57_assign_α`'s store is commented `# biggest` and its real jump (after a red-herring `mov r11,
  58` that is NOT a control-flow wire, just this box's own data load) is `jmp n67_var_α`.
- `n58`..`n65` build a second array-index + comparison; `n66_assign_α`'s store is commented `#
  littlest`, releases `add rsp, 80`, then `jmp n67_var_α`.
- `n70_assign_α` stores to `# i` — this is the for-loop's own `i := i + 1`.
- `n71`/`n72` set `# top` immediately after — `top := srtelements`, the statement right after the
  for-loop's normal exit.
- `n78`/`n79` load `# i` and `# top` — this is `while i < top do` (the SORT's own inner-loop test),
  the very first thing in the OUTER while-loop that follows the for-loop.

So `h=58` is the **first for-loop's `else if sortlist[i] < littlest then littlest := sortlist[i]`
branch** (lines 20-21 of `bubble.pas`), not the sort's swap (lines 27-29). The swap body is a
*different*, lower-numbered node range this row has never actually discussed. This doesn't
invalidate any prior session's *numbers* — `zd_plan`'s own accounting doesn't care what a human
calls the branch — but it matters for anyone reasoning about hit-counts or program behavior by
source semantics, and it explains a numeric puzzle below: `if sortlist[i] > biggest` is true only
when a NEW MAXIMUM is seen (rare for random data, `H(500) ≈ 6.2` expected updates), so the *else*
branch (`h=58`) fires on almost every one of the 500 iterations — which is exactly what every
session has measured (497/500), not the ~50% rate a "swap on random data" framing would predict.

## (2) NEW: the crash is cleanly POST-LOOP, and RSP ends up ABOVE its own process-entry value

Built `/tmp/bubble.s` into a real ELF binary (`gcc -g -m64 -no-pie -rdynamic ... -o
/tmp/m4-built-bubble`, linked against `out/libscrip_rt.so`) specifically so gdb can resolve the
per-box labels by name — mode 3 (in-process JIT) does **not** expose these as breakpointable
symbols (`Function "n70_assign_α" not defined` even from a UTF-8-correct command file; the
charset warning is cosmetic, the symbol genuinely isn't there). The native binary reproduces the
identical crash (`rc=139`, same fault site) and DOES let gdb break by name.

**Counted, not sampled — full run, `setarch -R`, deterministic (`echo 1` stdin), the SIGSEGV is the
natural stopping point, not a truncation:**
- `n70_assign_α` (the for-loop's `i:=i+1`) fires **exactly 500 times** — the ENTIRE first for-loop
  completes. No crash during it.
- `n58_var_α` (the littlest branch) fires **497 times** — reproduces seat05's own count exactly on
  this build, cross-checked by an independent method (breakpoint+counter vs. their raw hit-log).
- The SIGSEGV fires at **`n78_var_bx+19: mov %rax,(%rsp)`** — the first `while i < top` test node,
  i.e. the very first instruction of the SORT loop, immediately after the for-loop's normal exit.
  **The crash is not mid-loop and not inside anything this row has previously named** — it is the
  first use of stack scratch space after the leaking loop has already finished.

**Absolute confirmation of the over-release direction (not just a relative delta between two
checkpoints, which is all prior sessions measured):** this compiler never touches `rbp` (`grep -c
rbp /tmp/bubble.s` → 0), so `rbp` at any point is simply whatever the OS/CRT left there at process
entry — a free, always-available zero-reference. At the crash:
- mode-3 JIT: `rsp=0x7ffffffff0b0`, `rbp=0x7fffffffe0e0` → **rsp is 4048 bytes ABOVE its own
  process-start reference.**
- mode-4 native (`/tmp/m4-built-bubble`): `rsp=0x7ffffffff110`, `rbp=0x7fffffffe1e0` → **3888
  bytes above**, same direction, same order of magnitude, independently built and linked.

Both reproduced twice, byte-identical each time (`setarch -R`, no variance). **RSP climbing above
its own starting point — not drifting deeper below it — is direct, quantified proof of the row's
own name: this is excess release, not under-release**, and it rules out a "runs into the bottom
guard page" mechanism cleanly: the fault is `n78`'s own `mov %rax,(%rsp)` right after its `sub
rsp,16` prologue, i.e. RSP itself is already outside any mapped stack region — writing 16 bytes of
brand-new scratch space is what finally touches memory the process doesn't own.

## ⛔ UNRECONCILED — flagging per this row's own standing discipline, not chasing further this session

A naive `497 hits × 48 bytes/hit (seat05's own measured per-visit net carve) ≈ 23,856` bytes does
**not** match the observed ~3,900-4,048 byte total drift — off by roughly 6×. Two live hypotheses,
not distinguished: (a) seat05's -48-byte figure is h=58's own run measured **in isolation** and
does not sum linearly into the whole-program drift once the surrounding per-iteration accounting
(computed once per `i`, not once per `h=58` visit) is taken into account — some fraction may be
absorbed/re-corrected by other nodes' own zgpop/zwpop in the same iteration; or (b) only a subset
of the 497 visits actually contribute net drift for a reason not yet identified (e.g. an
alternation with the ~3 "biggest" updates that changes the per-iteration total in a way that
partially cancels). **Whoever continues: checkpoint $rsp at the n70 boundary on EVERY iteration
(not just entry/exit of one h=58 run) and correlate the per-iteration delta against which branch
fired that iteration — that is the concrete measurement that resolves this, and it was not
attempted this session** (this session's contribution is the absolute total and the corrected
node semantics, not a per-iteration trace).

## NOT ATTEMPTING THE REPAIR

Same restraint as every prior actor on this row (hq_P, seat13, seat16, seat01×2, seat05×2, seat03's
own earlier pass) — the actual fix is `zd_plan`'s shared arming/depth/wall computation, reserved
for hq_C per this row's standing authorization. No code touched; `git status --short` clean across
all three repos throughout, checked directly, not assumed.

Mailing hq_C (this row's authority). `.github` this commit.
