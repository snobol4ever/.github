# FINDING — HOME-RBX X-3: the residence gap is an UNRESERVED STACK WRITE, not a wrong-but-valid slot,
# and `bb_glue_flat_enter`'s own loud bomb does not guard the path that actually breaks

**Session:** Sonnet 5, 2026-08-12, immediately following s35 (this session did not know s35 had pushed
until mid-investigation — see § CONCURRENT-SESSION NOTE). Builds on and does not duplicate
`FINDING-2026-08-12j` (s35): that FINDING measured the gap (36/122 patterns under HEAP vs 76/122
FORTH-baseline, DIFF-not-crash dominant) and named the next step as pointing the MONITOR-FIRST 2-way
sync-step monitor at `041_pat_span`. This FINDING supplies the mechanism that monitor run was meant to
find, reached by a different RULES-sanctioned technique (asm-diff of a swapped-path pair) on an
independently-discovered, even smaller witness.

## SUMMARY

Under `--zeta-port=heap` / `SCRIP_ZETA_PORT=7`, every fc_geom-granted box that would have received a
FORTH per-BB `sub rsp,K` cell instead gets **nothing carved on the RSP side at all**. Its consumer side
(`FR`/`FRQ`, i.e. `x86_zop`) does not know this — `x86_fc_hit` is hard-gated to
`x86_port_mode()==ZC_PORT_FORTH`, so under HEAP it always reports "not granted," and `x86_zop_regime`
falls the reference through to regime 3 (pinned rbp) or regime 4 (flat `rsp+off`). Regime 4's `off` is a
real, legitimate flat-frame slot number — it is not garbage — but **no instruction has reserved that
stack space** under HEAP mode, because the RSP-side carve that would normally back it is the FORTH-only
`bb_glue_flat_enter` arm. The write lands below the current RSP, into unreserved (and in this build,
un-redzoned beyond the tiny fixed prologue) stack territory. This is not "reads a stale-but-valid cell,"
it is "writes into memory nothing allocated," which is exactly why the dominant failure mode is silent
wrong output (DIFF) rather than a fault: most of the time the corrupted bytes are never read back by
anything that would crash, they just aren't the bytes the program actually wrote.

## THE WITNESS (new, smaller than 041_pat_span)

`crosscheck/patterns/158_pat_cap_arbno_each_iter.sno` — **2 lines**:
```
 'abc' POS(0) ARBNO(LEN(1) . OUTPUT) RPOS(0)
END
```
Oracle / FORTH-port SCRIP: `a`/`b`/`c` (three lines). HEAP-port SCRIP: **empty output**, exit 0 (no
crash). Smallest program in the corpus that demonstrates the class; recommend promoting alongside
041_pat_span as the minimal member.

## THE MECHANISM, CONFIRMED BY ASM DIFF (RULES' own "diff their emitted asm" technique)

`scrip --compile` (mode 4 text) on the witness, FORTH vs `--zeta-port=heap`, `diff`'d:

FORTH — the box's own result cell, freshly carved immediately before use, LIFO-reused:
```
sub    rsp, 16
mov    qword ptr [rsp + 0], 2      # result
```
HEAP — same logical cell, same node, no carve anywhere nearby:
```
mov    rax, rbx
add    rbx, 16                      # REG-4b: the frontier bump. proven, byte-safe, UNREAD.
cmp    rbx, qword ptr [RT_WS_LIMIT]
...
mov    qword ptr [rsp + 272], 2    # result  <-- regime-4 fallback, RAW flat-frame slot number
```
The outer prologue in BOTH cases only ever emits `sub rsp, 8` (the fixed alignment amount) — confirmed
by grepping every `sub.*rsp` line in both `.s` files. So `[rsp+272]` is a write 264 bytes below the only
space actually reserved. Later in the same witness a second granted cell lands at `[rsp+112]` with,
again, no intervening carve. Neither offset is wrong *as a slot identity* — it is a real, otherwise-valid
flat-frame coordinate — it is simply never backed by an allocation under this port.

## WHY THIS ISN'T CAUGHT BY THE EXISTING GUARD

`bb_glue_flat.cpp` already anticipated exactly this failure class and tried to guard it:
```cpp
std::string bb_glue_flat_enter() {
    ...
    return IF(x86_zstorage() == ZC_STORAGE_CELL_STACK && _.op_fc_bytes > 0, x86("sub", "rsp", _.op_fc_bytes))
         + IF(x86_zstorage() == ZC_STORAGE_CELL_HEAP  && _.op_fc_bytes > 0,
              x86_bomb("bb_glue_flat_enter: CELL_HEAP per-BB carve is HZ-1, not implemented"));
}
```
with the file's own header comment naming the intent explicitly: *"deliberately loud rather than
silent, because the one failure mode this subsystem keeps re-learning ... is that a storage decision
which quietly does nothing produces plausible code and a wrong answer."* — i.e. the author built a
trap for exactly this class and wanted it to bomb, not misbehave silently.

**The trap does not fire for this witness.** The witness's own carve is emitted through REG-4b — the
CENTRAL `x86_port_hook` arm in `x86_asm.h` (~2320-2333), fired unconditionally at every
`X86H_DEF/X86P_ALPHA` site with `hk>0` under `ZC_PORT_HEAP` — a *different* emission path from
`bb_glue_flat_enter`. REG-4b happily bumps rbx (that side is genuinely correct and byte-safe — the
consumer never reads it, exactly as documented). `bb_glue_flat_enter`'s own CELL_HEAP branch is never
even reached for this box, so its bomb is silent-by-construction for the actual failing path. The
guard the author built protects one call site; the bug lives at a sibling call site with no equivalent
guard, and the true failure surfaces three layers downstream, at the *consumer* (`x86_zop` regime-4
fallback), which has no way to know its `off` was never backed.

**Standing lesson (offer for RULES.md, same genus as the WIRES/BOARD instrument-lesson entries already
on record):** a loud-bomb guard placed at one emission site for a documented failure class does not
cover a second, structurally-independent emission site that can produce the identical downstream
symptom. Census both the *decision* side (who decides a cell is granted) and the *emission* side (who
actually carves it) before trusting a single guard to be complete — REG-4b and `bb_glue_flat_enter`
are two different authors of "K bytes for this box," discovered independently at two different rungs
(REG-4b at legacy s78, this guard at the ZW-1 ladder), and neither cross-references the other.

## RECONCILING WITH s35's NUMBERS (STALENESS LAW, not a disagreement)

s35 measured 36/122 patterns under HEAP (48 DIFF) at their HEAD; this session measured 31/122 (53 DIFF,
23 crash, 15 hang) at an earlier HEAD, before LOWER L-3b (`05e6b1ae`) and BOARD B-1 (`e7424687`) landed.
Both FORTH baselines agree exactly at 76/122. The ~5-program delta between the two HEAP counts is
consistent with ordinary concurrent-seat drift on unrelated surfaces (per s32b's STALENESS LAW) and is
not investigated further here — the mechanism above is invariant to which exact HEAD either session sat
at, since it follows from a *design gap* (missing carve emission under a specific port), not from any
of the commits that landed between the two measurements.

## THE FORK FOR THE NEXT RUNG (not resolved here — naming it is this FINDING's job)

Two structurally different fixes exist, and they are NOT the same rung:

**(a) SAFE / CONSERVATIVE — restore the documented invariant.** Make the RSP-side carve fire under
CELL_HEAP too, identically to CELL_STACK (i.e. delete/replace the `x86_bomb` arm in
`bb_glue_flat_enter`/`_leave` with the same `sub rsp,K` / `add rsp,K` FORTH already does, AND find and
patch the REG-4b/central-hook path's sibling gap so *every* carve site double-allocates under HEAP).
This makes HEAP mode pay for both an rbx bump (unread) and an rsp carve (read) — genuinely wasteful,
but it converts today's *broken* dormant state into the *actually* dormant, byte-safe state § A already
claims exists. This is the fix that makes X-3's own stated positive-control claim true, and is a
prerequisite for measuring anything else about HEAP port with any confidence.

**(b) AMBITIOUS / THE REAL SLICE-2 — implement residence.** Extend `x86_fc_hit`/`x86_zop_regime` with a
genuine HEAP-aware granted regime that rebases through the box's own heap-block base rather than rsp.
This is the actual "HZ-1 slice 2" the REG-4b comment names, and it inherits every hazard already on
record in this file's § J, principally HAZARD-3 (the block base lives only in caller-saved `rax` across
the bump — not `jmp_buf`-visible, not call-survivable — so a durable per-box stash has to be designed,
and CELL_HEAP does not carve any RSP slot of its own to spill into, unlike FORTH, so the stash needs its
own new carve infrastructure, not a reuse of existing plumbing).

**Recommendation, not committed to a cursor as done:** (a) is the correct *next* rung — it is small,
mechanical, symmetric with existing FORTH code, and turns a currently-false safety claim into a true
one, which everything downstream (including (b)) should be built on top of. (b) should not be attempted
until (a) is landed and re-verified with the SAME positive control this FINDING used (full
`crosscheck/patterns` under `--zeta-port=heap`, BY SET against the FORTH baseline, expecting **identical
sets**, not just an improved count — a HEAP run that merely improves the pass count without matching the
FORTH set exactly has not actually proven byte-safety, it has proven "different wrong answers").

## ZERO CODE CHANGED THIS SESSION

Every measurement above is read-only (compile + diff + grep). Tree is clean. No commits beyond this
FINDING and the cursor move.
