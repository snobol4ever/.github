# FINDING — corrected 9-kernel baseline (only `bubble`/`quick` fail today, not the 5 named anywhere in this row's history), plus a dynamically-confirmed, precisely-localized `zd_plan` release-side over-release accounting for both

Row: `pascal-m4-for-spine-leak-64b-per-iter` (seat12, FLEET-16 per live MODE at claim time).

## Part 1 — the failing set has shrunk again; `sieve` is a stale witness, `perm`/`intmm`/`queens` are also clean now

`next` handed me this row with hq_P's CURRENT `## NEXT` built entirely around a *static* `.s`-only
reading of `sieve.s` (a join-depth mismatch at `n31_var_α`), explicitly flagged by hq_P as unconfirmed
("A check that STOPPED me generalising it... the metric does not discriminate failing from passing
kernels"). Before running hq_P's prescribed dynamic gdb confirmation on `sieve`, I rebuilt and graded
the full DONE-WHEN grid pristine at HEAD `a3275c6f` (`echo 1 |`, `setarch -R`, 5 reps/kernel, all
deterministic 5/5 in both directions):

| kernel | result | | kernel | result |
|---|---|---|---|
| bubble | **FAIL rc=139** 5/5 | | sieve | PASS 5/5 REF-MATCH |
| intmm | PASS 5/5 REF-MATCH | | towers | PASS 5/5 REF-MATCH |
| queens | PASS 5/5 REF-MATCH | | uplevel2 | PASS 5/5 REF-MATCH |
| quick | **FAIL rc=139** 5/5 | | uplevel3 | PASS 5/5 REF-MATCH |
| perm | PASS 5/5 REF-MATCH | | | |

This is a **third** distinct failing-set membership for this row, none matching the others:
- GOAL line (original, untested per hq_C's own s266-class warning): `bubble, intmm, queens, quick, sieve`
- hq_C's last measured grid, HEAD `43fa94a0`: `bubble, intmm, queens, quick, perm`
- **This measurement, HEAD `a3275c6f`: `bubble, quick` only** — `sieve` is what flipped back to PASS
  first (per seat07/hq_C's exchange below, `748f7698` cured it once already); `intmm`/`queens`/`perm`
  have evidently ALSO been cured as a side effect of unrelated commits landing between `43fa94a0` and
  `a3275c6f` — exactly the same shape as `748f7698` curing `sieve` the first time. I have not bisected
  which commit(s); I only re-measured pristine and confirmed determinism (5/5 both directions, no
  flake) before trusting it, per this row's own repeated `setarch -R` warning.

**Consequence: hq_P's `sieve` witness and the entire six-kernel "differing join depths" table built
around it describe a kernel that is not currently broken.** hq_P's own confusion — "`perm`/`towers`
are in the passing set yet show the same shape as failing kernels" — is best explained by exactly this:
by the time hq_P ran the static scan, `perm` had likely already flipped to PASS too (matching what I
measure now), so `sieve` was never a valid stand-in for "currently failing" in the first place. Not
asserting hq_P's static observation is wrong — only that it cannot be evidence for or against the live
bug, because its subject kernel isn't reproducing the live bug. **Do not re-pick `sieve` as a witness
for this row without re-confirming it fails first** — this is now the second time this row's witness
selection has rotted out from under a static analysis (see `748f7698` in seat07/hq_C's exchange,
below `## LEDGER`), and per `RULES.md:126`, a name/witness asserting relevance is the untested
hypothesis, not a fact.

## Part 2 — `bubble`: dynamically confirmed, exact mechanism, exact bytes, exact sites

Crash site (`setarch -R`, deterministic every run): `n58_var_bx+14` (`mov %rax,0x700(%rsp)`),
`$rsp=0x7fffffffeb30` at fault — 0x700 past `$rsp` lands ~0x230 bytes **above** the top of the mapped
stack region. This is hq_C's OVER-RELEASE direction (RSP climbing, stack shrinking-then-overflowing
upward), not the GOAL line's untested "leak/consumption" framing.

**Per-visit drift, measured directly (not inferred from a linear `.s` scan):** breakpoint at
`n58_var_bx`, logging `$rsp` on every hit: **96 hits, `$rsp` increases by a constant `+0x2d0` (720
bytes) every single visit, zero variance, then the 96th write goes past the stack top.** This is a
hard per-iteration invariant violation — a flat-wired back-edge must return to the *same* `$rsp` every
time by construction (every downstream `[rsp+K]` access assumes one canonical depth); it does not.

**Which edge is hot:** `n58_var_α` has 4 static predecessors (`n51_call_bx`'s two exits, releasing
`0x270`=624 each; `n53_binop_test_bx`'s two exits, releasing `0x290`=656 each — a 32-byte local
mismatch hq_P's static read would have flagged). Breakpointing all four for a full run: **only
`n53_binop_test_bx`'s first exit (`add $0x290,%rsp; jmp n58_var_bx` @ `0x402157`, the `jg`-not-taken
arm) ever fires — 96/96.** The other three are dead code for this input; the local 32-byte mismatch
between them is not the cause.

**Full-cycle instruction-level trace** (single-stepped with `nexti` from one hit of the hot exit to the
next, logging every instruction that changed `$rsp` — raw log available on request, not attached here
to keep this file short): exactly 464 instructions per iteration, net `$rsp` delta **+720**, confirming
the per-visit measurement independently and localizing it to two sites:

1. **`n53_binop_test_bx`'s hot exit** (`0x402150`/`0x402157`): releases 656+16=672 total, but only 27
   preceding nodes in that run each self-carve `sub rsp,16` (432 bytes) before it — **+224 excess**.
2. **`n70_assign_bx`'s back-edge** (the `for`-body's own back-edge, `add $0x220,%rsp`=544, jumping back
   to `n23_var_bx`, the loop head): only 3 nodes (`n67`,`n68`,`n69`) self-carve 16 bytes each (48 bytes)
   since the previous release — **+496 excess**.

`224 + 496 = 720`, exactly matching the measured per-visit drift — the accounting is closed, not a
partial match.

## Part 3 — `quick`: same class, different site, same signature

Crash site: `n236_var_bx+14` (`mov %rax,0x3a0(%rsp)`), same shape (write past `$rsp+0x3a0` near stack
top). Breakpoint-and-log on `n236_var_bx`: **101 hits, constant `+0x2b0` (688 bytes) every visit, zero
variance, crash on the last write.** I did not instruction-trace `quick`'s cycle (time-boxed this
session to `bubble`'s full derivation plus corroboration on `quick`) — the crash-site/monotonic-drift
signature alone is included here because it is decisive for the classification question below, not for
the exact byte-accounting.

## Why I am not attempting a fix, and where this sits against the row's standing authorization

The row's SUPERSEDED-NEXT history already carries hq_C's authorization split for this row: **SOLO —
the count above, and a release-side fix local to one carve/release pairing; BACK TO hq_C FIRST —
anything touching `zd_plan`'s arming decisions or depth/wall computation.** `bubble`'s two over-release
sites are not one isolated local pairing: they are two different exits of what the emitted code treats
as (at least) two overlapping runs whose bulk-release constants (672, 544) do not match what either run
itself carved (432, 48) — that is `zd_plan`'s `gback`/`oback`/`gpop`/`wpop` machinery (`emit.cpp`,
per seat07's prior multi-session mapping of this exact mechanism, elsewhere in this row's ledger),
which IS the depth/wall computation the authorization reserves for hq_C. `quick` showing the identical
monotonic-constant-drift-per-visit signature at a structurally unrelated site is, per `RULES.md`'s
class-defect rule, evidence this is one mechanism reachable through multiple BB family members, not
two coincidentally similar bugs — another reason not to hand-patch `bubble`'s two constants in
isolation and call it done.

Not attempting: any change to `emit.cpp`/`zd_plan`. Not re-deriving hq_P's `sieve` witness further —
it isn't reproducing. Tree byte-identical to origin throughout (only `/tmp` scratch artifacts and
gdb sessions were used; no tracked file was touched by this investigation).

## What the next actor gets for free

- The corrected, freshly-verified 9-kernel baseline above — re-verify before trusting it further out,
  but do not re-derive it from scratch.
- A working dynamic methodology (breakpoint-and-log on the crash-site label, then `nexti`-trace one
  full cycle between consecutive hits of the hot predecessor edge, summing `$rsp`-changing
  instructions) that resolved in under an hour what hq_P's static `.s` scan could not decide. This
  generalizes directly to `quick` (not yet instruction-traced) and to any future witness in this
  family — worth reusing before another static-only pass.
- `bubble`'s exact two over-release sites and byte amounts, ready for whoever hq_C authorizes to touch
  `zd_plan`'s depth computation next.
