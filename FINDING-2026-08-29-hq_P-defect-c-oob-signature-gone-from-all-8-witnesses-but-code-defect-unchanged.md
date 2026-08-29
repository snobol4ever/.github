# FINDING — Defect C's out-of-bounds signature no longer reproduces on ANY of the 8 vlist witnesses
# (0/8, under the row's own primary detector), but the code defect is UNCHANGED. The ladder gate is now
# red for a DIFFERENT defect class. And the RBP destination Lon's criterion names now EXISTS.

**hq_P · 2026-08-29 · row `defect-c-zop-flat-regime-depth-compensate`** (rank 1, HQ-only per CEO-19).

**Not cured — nothing committed to SCRIP or corpus.** Four findings, the second of which is the one that
must not be lost.

## 1. The witnesses have gone quiet — 0/8, where the baton records 6/8 unclean

Pristine at SCRIP `373d6774`, `RT_OPT=-O0`, `REPS=20`, the row's own gate. Separating the two valgrind
signatures by hand (the gate reports only a combined count):

| witness | Defect-C OOB signature | `uninitialised` |
|---|---|---|
| c01, c02, v01, v02, v03, v04, v06 | **0** | 0 |
| v05_treebank_pushlist_235 | **0** | 6 |

`Invalid write / Invalid read / Access not within / is not stack'd` — Defect C's documented signature,
established by seat03 as **8/8 deterministic** under `env -i`+valgrind when the defect was live — is
**absent from every witness**, including the five that defined the row. m3, m4-ambient and m4-minimal
(20/20) all PASS on all eight.

## 2. ⛔ THIS IS NOT A CURE, AND THE DIFFERENCE IS THE WHOLE POINT

`x86_zop`'s regime-3/4 fallback is **byte-for-byte the code the row was minted against** — now at
`src/templates/x86/x86_asm.h:1019` (⛔ the baton's `src/templates/x86_asm.h:863` is a stale path *and* a
stale line; the file moved in srcreorg move-3):

```c
else { eff = off + ((x86_fb_data() || _.op_stmt_dyn) ? 0 : bump); spine = 0; }
```

Still no `x86_frame_off()` / `_.op_zdepth` compensation. Still falls through on `bump == 0`, the common
case. **So the defect is latent, not fixed** — the emitted code for these particular witnesses has
changed under a great deal of landed codegen and no longer positions the write where it is visible.

⭐ This is precisely the failure mode the row's own § VALIDATION was written to prevent, arriving from
the direction nobody guarded: that section warns *"an out-of-bounds write that lands somewhere harmless
produces the same exit code as a correct program"* and prescribes valgrind + two environment sizes as the
answer. That prescription assumed the **detector** could go blind. Here the **witness** went quiet
instead, and a green ladder is exactly what a real cure would also look like.
⛔ **So: do not close this row on the ladder going green.** On this tree the ladder cannot distinguish a
cure from a witness that stopped reproducing. Closing it needs either a witness that reproduces again, or
a positive argument about the code.
⚠️ **Limit of this finding, stated rather than papered over:** I proved the code is unchanged and the
signature is gone. I did **not** prove the raw arm is still *reached* by these eight witnesses — the
`zop_seen` regime bitmask is recorded per graph (`emit.cpp:3494 zop_audit_seen`) but nothing exposes it
to a script, and I did not add one. That census is the cheapest next measurement and it decides between
"still reached, write relocated" and "no longer reached at all".

## 3. The gate's red now comes from an unrelated defect class

v05's 6 errors are **not** Defect C. Every one is `Conditional jump or move depends on uninitialised
value(s)`, at:

- `rt_define_tiny_ok` (`rt.c:1952`) ← via `bb_tiny_shim_ok`, during runtime `EVAL` re-emission
- `eval_cache_insert_raw` (`runtime_eval.c:54`) and `eval_cache_get` (`runtime_eval.c:47`)
- `c_rt_svco_miss_d` (`pattern_match.c:1481`)

The gate greps `Invalid (read|write)|Access not within|uninitialised` as one bucket, so it counts these
and reports the ladder red. ⛔ **A seat reading `GATE FAILS` today will conclude Defect C is live. It is
not — not on this evidence.** The gate is not wrong to flag an unclean witness; it is wrong to let one
number stand for two defect classes on a row named for one of them. Splitting that column is a small,
honest change (I did not make it — see §5).

## 4. ✅ The RBP destination now EXISTS — Lon's meta-rule is satisfied

`RULES.md:72` (BB FRAME-PLACEMENT CRITERION) ends with: *"a ruling names a destination; grep the artifact
that the destination EXISTS before implementing against it."* Done, and it does:

```c
/* x86_asm.h:1020, inside x86_zop, and again at :1037 inside x86_zref */
{ int ft = icn_gen_zeta_ft(); if (ft > 0) return q ? RDQ("rbp", eff - ft) : RDD("rbp", eff - ft); }
```

An RBP re-homing arm, live in the same function as the defect, **default-ON** since `0b35b5fc` ("icon N-2
GATE FLIP: generator activation frames DEFAULT ON"). Admission is `icn_gen_regime() && _.flat_gen`.

⭐ **So the cure shape is now "widen an existing, working arm's admission predicate", not "invent a
destination".** That is a materially smaller and better-evidenced job than the baton describes.
⛔ **But read `icn_gen_zeta_ft`'s own comment before touching it** — the narrow keying is deliberate and
argued: it is keyed on the *consuming ζ regime* specifically so that no SNOBOL4 or Prolog graph can enter,
citing the s272 loss of **47 Icon programs** to a language-blind widening. Widening it is exactly the
move that regressed last time. The admission test must be Lon's **behavioural** predicate (can unbounded
growth intervene between definition and use), never a language or box-kind test.

## 5. ⛔ The baton's § "Ruled approach" is SUPERSEDED and still says the opposite

The baton reads: *"Depth-compensate every flat reference. Do NOT force-release before a flat box"* —
hq_C's position, correct when written. `RULES.md:72` (Lon, 2026-08-27, **after** that section) rules the
other way: when unbounded growth can intervene, the storage **moves up the ladder to a ζ-ACTIVATION-FRAME
(RBP)** rather than having its rsp offset corrected. The baton's own LEDGER spotted this — *"an early
draft of the direction Lon's BB FRAME-PLACEMENT CRITERION just ruled for THIS row (re-home to an RBP
activation frame rather than compensate the rsp offset)"* — but § "Ruled approach" was never updated, so
the section a next actor reads first still names the retired cure. Corrected in the baton's `## NEXT`.

## 6. Why I stopped here

I hold the row and it is mine to cure. I did not, and not for lack of a plan: on this tree **the row's
acceptance instrument cannot grade the cure** (§2) — every witness is already green on the Defect-C
signature — so any change I made would be unfalsifiable by the gate that exists. Landing a shared-node
codegen change into a suite that cannot detect its subject is how the 47-Icon-program regression happened.
The next actor needs a reproducing witness (or the §2 `zop_seen` census) *before* the cure, not after.

- Trees: SCRIP `373d6774`, corpus `a37491bd4`, `.github` `37ebb087`; `make pristine`, `RT_OPT=-O0`.
- Ladder: `REPS=20`, rc=1, 7/8 CLEAN + v05 `ERR(6)`. Corpus board not re-run (no code change made).
