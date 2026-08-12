# FINDING — HOME-WIRES s39b (Claude Sonnet 5) — X01 discriminator narrowed with 7 constructed witnesses
# (oracle-verified); NOT a fix, NOT gdb-confirmed, "purity" hypothesis from s39a also falsified

**SCRIP `0bbf092b`, corpus HEAD+witness-set commit (see below), .github this commit. Zero SCRIP source
edits. corpus gains 8 new files (7 `.sno` + `.ref` pairs + README) under
`probe/bb/probes_x01_witness_s39/` — NOT added to `run_suite.sh`, not graded, explicitly a scratch/witness
set per its own README.**

## Continuation of FINDING-2026-08-12p
That finding falsified the two candidate blanket-widening guards (`!op_arbno_body_k0`, `op_body_has_arbno`)
and proposed, as an untested hypothesis, that the real discriminator might be "outer ARBNO body span is
PURELY the nested ARBNO, no bracketing K=0 members" (X01's shape) vs. "wrapped in other members" (X02's
shape, passes). That finding explicitly flagged this as validated against only n=1 (X01 itself) with no
second positive witness in the suite.

## This session: built 7 witnesses, checked each against the real oracle (not assumed)
Cloned `snobol4ever/x64` (public — no credential needed, unlike `csnobol4`) and used
`/home/claude/x64/bin/sbl -b <file>` as ground truth for every witness before touching SCRIP, so results
below are oracle-verified, not hand-reasoned from the manual alone (though the manual's ARBNO-is-shy
semantics, p.121, predicts all seven should succeed: the outer ARBNO's own zero-instance case is always
available, and the inner ARBNO similarly, so `POS(0) ARBNO(ARBNO(LEN(1))) RPOS(0)` against a 1+-char
subject requires only that SOME split into LEN(1) chunks exists across some number of outer iterations —
trivially true for any subject whose length is expressible as a sum of the per-iteration LEN(1) counts,
which for an all-length-1 inner is every subject).

**The "purity" hypothesis from s39a is FALSIFIED.** X01W3/X01W4 (literal OUTSIDE the outer ARBNO's own
repeated arm — before or after the whole `ARBNO(ARBNO(LEN(1)))` — X02's superficial wrapping shape but at
the STATEMENT level, not the ARM level) still fail. Only X01W5 (literal INSIDE the outer arm, i.e.
`ARBNO(ARBNO(LEN(1)) 'x')` — a real co-member of the SAME repeated unit as the nested ARBNO) passes. X01W6/
X01W7 rule out "any co-member rescues it": a null-string literal or an explicit `LEN(0)` node inside the arm
does NOT rescue it — both still fail identically to the bare case. Full table in
`corpus/probe/bb/probes_x01_witness_s39/README.md`.

## Narrowed (not proven) discriminator
The outer ARBNO's own repeated arm needs a co-member alongside the nested ARBNO that **consumes at least
one subject character on its own turn** — matching X02's real shape (`'(' ... ')'` delimiters inside the
arm, each consuming a character) and explaining why X02 passes while bare `ARBNO(ARBNO(...))` (X01, and
X01W1/W2/W3/W4/W6/W7) does not.

**This is still not a proven mechanism, only a sharpened correlation over 7+2 data points (7 constructed +
X01 + X02).** No currently-staged emitter field distinguishes X01W1 (fails) from X01W5 (passes) — checked
directly: identical `framed=0 k0=0 sq=0 kk=16` on the outer node for both. Whatever mechanism actually
causes the wrong answer is invisible to every scan the K16 prelude currently runs. A plausible
hand-wave (untested): a character-consuming co-member forces at least one real subject-cursor advance per
outer-arm instance independent of the inner ARBNO's own bookkeeping, which may incidentally keep the
frameless arm's `[rsp+4]` yield-cursor write from colliding with whatever the bare/zero-consuming case
corrupts — i.e. the same general frontier-motion class W-7's finding already named for DEFER, now with a
second, structurally different trigger (nested ARBNO with no character-consuming sibling) rather than a
new independent bug. This is a hypothesis, not a finding — it needs the gdb hunt RULES.md prescribes, not
another round of black-box probing.

## Why this session stopped here (again) rather than writing a "has real-consuming sibling" guard
Same three reasons as FINDING-2026-08-12p, unchanged: (1) MON-CAP still blocks the prescribed mechanical
hunt (csnobol4 requires `TOKEN_SEE_LON`, not cloneable this session); (2) the real fix is very likely still
W-4's anchor-relative layout regardless of exactly which frontier-motion trigger causes it, so a third
guard variant is progressively more speculative interim tooling on top of interim tooling; (3) this is now
the SIXTH session this seat has spent on ARBNO-dispatcher territory instead of its own r10/r11 charter — the
s38 routing question is still unanswered and every additional session here deepens the ambiguity it was
already flagging. Constructing and oracle-verifying the witness set felt like the right amount of
unilateral work (pure data-gathering, zero source risk, throwaway if wrong) — writing a guard off an
unconfirmed correlation crossed the line into a design decision this seat keeps saying isn't its call to
make alone.

## What's committed
- `corpus`: 7 `.sno` + 7 `.ref` (oracle-generated) + 1 README under
  `probe/bb/probes_x01_witness_s39/` — NOT wired into `run_suite.sh`, explicitly a scratch/witness set.
  Deliberately kept out of the graded suite: these are diagnostic constructions, not committed regression
  tests, and adding 7 ungated files to the suite without Lon's sign-off would silently change what "green"
  means for this goal.
- `.github`: this finding + cursor update.
- **SCRIP: zero changes**, same as s39a.

## Recommended next steps (still not mine to pick, same reasoning as s39a)
- **(a)** MON-RE: get `csnobol4` building — now blocked THREE investigations running (s38, s39a, s39b) on
  this exact wrong-answer-class defect. The token is the one blocker across all three.
- **(b)** If/when someone has gdb access to trace this: X01W1 vs X01W5 is now a clean minimal-pair reduction
  — same emitter trace, opposite outcome, one character's difference in the pattern. This is about as small
  a repro as this class of bug is likely to get; worth using as the bisection target over X01 itself, which
  carries more incidental structure.
- **(c)** Escalate seat-routing (s38's Q1, now six sessions overdue) before a seventh session lands here.

## LIVE CURSOR — this session did NOT touch SCRIP source, did not move the watermark
Floor unchanged: **160 pass · 1 xfail · 5 REGRESSION {D12,D13,H31,X01,X10}**. W-3/W-4/W-6 (charter) still
untouched — now six sessions running. New artifact this session: 7 oracle-verified witness probes
narrowing (not solving) X01, committed to `corpus` as an explicitly non-graded scratch set.
