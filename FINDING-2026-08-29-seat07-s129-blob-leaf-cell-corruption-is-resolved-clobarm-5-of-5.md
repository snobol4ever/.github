# FINDING — s129's blob leaf-cell/standing-frame memory corruption is RESOLVED: `probe/clobarm/` is 5/5 in every arm, on a pristine build

**seat07 · 2026-08-29 · row `corpus-crosscheck-probe-total-conversion`**

## What this closes out

`FINDING-2026-08-16-s129-blob-leaf-cell-overshoots-standing-frame.md` named a default-arm, no-killswitch
memory corruption: a framed pattern blob's leaf suspension cell was priced into the caller's standing
frame (`x86_frame_off`'s single `op_zdepth` compensation term had no `blob_frame_bytes()` term), landing
a `mov dword ptr [rsp+164], r14d` write on the upper half of the CAS-mark qword at `[standing_rbp-8]`,
later walked as a wild pointer by `rt_dcap_pump` → SIGSEGV. That FINDING's own §7 "NEXT RUNG" named its
acceptance test explicitly: *"Gate on `probe/clobarm/` 5/5 (4 red→green, `trueinline` stays green) before
anything else."*

**That criterion is now met, measured fresh on a pristine build, not inherited from prose:**

```
$ SCRIP_CHOICE_RBP=0 bash scripts/test_gate_clobarm.sh      # true OFF, explicit — not the unset-default trap below
clobarm: PASS=5 FAIL=0 (both modes must match .ref)
$ SCRIP_CHOICE_RBP=1 bash scripts/test_gate_clobarm.sh      # true ON, explicit
clobarm: PASS=5 FAIL=0 (both modes must match .ref)
$ bash scripts/test_gate_clobarm.sh                          # unset (defaults through sn4_pt_frame())
clobarm: PASS=5 FAIL=0 (both modes must match .ref)
```

All three arm states, both modes each, all 5 witnesses (including `clob_altarm_arm2direct_red` — s129's
own headline, unconditional rc=139 in both arms at mint time) now match the live-`sbl` `.ref` oracle
exactly (`id=iffoo`). `make pristine` exit 0 immediately before measuring, so this is not a stale-binary
artifact.

## A methodology note, since it nearly produced a false result

`SCRIP_CHOICE_RBP` (`emit.cpp:2404`) falls back to `sn4_pt_frame()` when unset, and `sn4_pt_frame()`
(`emit.cpp:2267`) now defaults to **1** unless `SCRIP_PT_FRAME=0`. A first pass leaving the env var unset
for "OFF" and setting `=1` for "ON" silently tests the SAME code path twice — the apparent "both arms
agree" result from that pass proved nothing. Caught before writing this up; the numbers above use the
explicit `=0`/`=1` forms, which are unambiguous. Whoever else compares against an old clobarm table:
check which convention the older measurement used before trusting an "unchanged" or "still red" read.

## Why it's plausibly actually fixed, not just newly inert

Not root-caused this session (out of this row's lane — corpus format conversion, not codegen), but the
current `emit.cpp` (around line 2927) carries a mature "R-4(b) BLOB ACTIVATION FRAME (THREE ZETAS)"
mechanism — real `push rbp; mov rbp,rsp; sub rsp,<bytes>` per-blob framing with the γ/ω pair explicitly
banked and restored — that has no counterpart in s129's description of the broken mechanism ("the caller
carves 56 bytes for its own five slots and reserves nothing above them for a callee"). s129 itself named
the fix as teaching `zd_plan`/`zvo_resolve` (then in `src/contracts/zeta_storage.c`, since folded into
`src/ir/` per the source reorg) that a framed blob's cells belong in the blob's frame. The ζ-storage
architecture (`src/ir/zeta_{choices,depth,storage}.h`) matured considerably after 2026-08-16 across a
large, separately-tracked body of work — this reads as an emergent side effect of that maturation, never
individually re-verified against this specific probe until this session's corpus-conversion pass forced a
full README read.

## Not attempted

No bisection to find the exact landing commit — a large amount of dcap/choice-record/ζ-storage work
landed in the intervening two weeks and isolating the one responsible change is a separate, sizeable
investigation. No `QUEUE.tsv` row referenced this bug by name (grepped, 0 hits), so there is nothing to
mark done there. `beauty.sno`'s `Command` rung, which s129 §6 explicitly declined to claim as blocked by
this (a *different*, wire-clobber-framed, zd-vetoed blob), is unexamined here — if anyone revisits that
rung, this FINDING is relevant background, not a new claim about it.

## Consequence for this row

Converting `probe/clobarm/` into suite format no longer needs XFAIL/dual-arm-preserving machinery — it
is now a plain, fully-green, arm-independent family, same shape as `leafsib` post-conversion. Proceeding
with a normal conversion; see this row's own `## NEXT` for the corpus/SCRIP commits.
