# FINDING 2026-08-30 seat03 — pascal-bubble-m3-segv-and-devnull-masks-it

## BISECTED, decisively — the task's own "first act": Site 2 (SCRIP `ff1df778`) causes this, not just plausible fallout

`git checkout ff1df778~1` (`b5c64f86`), `make pristine`, `echo 1 | ./scrip --run
../corpus/benchmarks/pascal/bubble.pas`: **rc=0, output `-50000`/`15505` — matches `bubble.ref`
exactly. No crash.** Checked out back to `main` (current HEAD), `make pristine` again, same
command: **rc=139 SIGSEGV**, reproduced deterministically (matches the task's own report and this
session's own earlier bubble.pas work on `pascal-m4-site1-forloop-backedge-64byte-excess`). Both
directions rebuilt pristine, both reproduced, no ambiguity.

## THE MECHANISM, pinpointed by ASM-DIFF-FIRST (per the row's own instruction, never by flag)

`--compile`'d both trees, diffed the two `.s` files (`b5c64f86`: 2464 lines; current HEAD: 2489
lines). The diff concentrates almost entirely (146 of ~1784 diff lines are literal `rsp, N`
sub/add instructions) around the exact transition into the "littlest" branch this session's
sibling FINDING already characterized in full:

- **BEFORE Site 2:** `add rsp, 656; jmp n58_var_α` — a single, flat, upfront release covering the
  whole upcoming span, then jump in. This span was NOT `zd_plan`-claimed at all; it used
  whatever the older/non-zd mechanism computes, and that computation was correct (matches the
  clean `rc=0`).
- **AFTER Site 2:** the same transition point now threads through per-node `sub rsp,16` / `add
  rsp,16` pairs at every one of `n58`..`n67`, i.e. this span became `zd_plan`-CLAIMED (Site 2's own
  stated mechanism: admitting `IR_BINOP_TEST` into `zd_omega_head` makes new spans eligible for
  the claim-and-release-by-run accounting `zd_plan` already does elsewhere).

**This closes the causal chain end to end, combining with the sibling FINDING on
`pascal-m4-site1-forloop-backedge-64byte-excess`
(`FINDING-2026-08-30-seat03-pascal-site1-crash-is-post-loop-497-visit-net-overrelease-and-the-swap-framing-was-wrong.md`,
`.github` `922fe35c`):** Site 2 moved this span from an old, working, flat-release path onto
`zd_plan`'s newer per-node accounting; that per-node accounting has the exact -48-byte-per-visit
net imbalance the sibling FINDING measured (gdb, full run, zero variance); ~497 of the 500
for-loop iterations take this branch; the accumulated drift (measured directly there: RSP ends up
3888-4048 bytes ABOVE its own process-entry reference at crash time, in BOTH m3 and m4) finally
faults the first stack-scratch write after the loop exits.

## THIS IS THE SAME UNDERLYING DEFECT AS pascal-m4-site1-forloop-backedge-64byte-excess, NOT A NEW ONE

Same span (`h=58`/`i=58..66`, the first for-loop's `littlest` branch), same mechanism (`zd_plan`
per-node accounting introduced by Site 2, net -48/visit), same crash site in kind (first
stack-scratch use immediately after the leaking loop exits — `n78` in the sibling FINDING's mode-4
numbering; this session did not re-derive the exact mode-3 node correspondence, since the sibling
FINDING's own mode-3 RSP measurement already covers this exact binary/command). **The only new
fact this row's own DONE-WHEN adds is that the SAME defect breaks the m3 (`--run`, native BINARY)
arm, not just m4** — expected under this compiler's BOTH-MEDIUM design (every code-emitting
function must be correct for both TEXT and BINARY; a `zd_plan` defect in the shared planner hits
both mediums identically), but not previously confirmed by bisection until this session.

⛔ **`</dev/null` really does mask it completely, confirmed on both trees**: `./scrip bubble.pas
< /dev/null` returns `rc=0` printing `0`/`0` on EITHER side of the bisection (crashing or not) —
exactly the vacuous-arm hazard the task's own GOAL text warns about. Never trusted `</dev/null` for
any check in this session; every reproduction above used real stdin (`echo 1 |`).

## NOT ATTEMPTING THE REPAIR

The fix is `zd_plan`'s shared per-node accounting (the exact -48-byte/visit imbalance), which is
the SAME repair already reserved for hq_C on `pascal-m4-site1-forloop-backedge-64byte-excess` —
solo-fixing it here would mean touching the identical shared code that row's own authorization
already fences off. **This row's own DONE-WHEN (m3 bubble.pas rc=0, output matches `.ref`) should
close automatically once that shared fix lands and is verified in mode 3 too** — flagging that as
the closing condition rather than treating this as a second, independent repair task. No code
touched this session; `git status --short` clean across all three repos throughout (the only
non-repo artifacts are `/tmp/bubble_*.s` diff scratch, never committed).

Mailing hq_C (pascal-m4-site1-forloop-backedge-64byte-excess's own authority) with the
cross-reference. `.github` this commit.
