# FINDING s136 — `zdp_analyze` PERTURBS THE PROGRAM IT MEASURES. EVERY ZDP NUMBER EVER REPORTED IS SUSPECT.

**Status:** MEASURED, ROOT CAUSE NOT YET LOCALISED. Repro is one command. Default paths are unaffected (all gates OFF).

## THE MEASUREMENT

```bash
f=/home/claude/corpus/programs/snobol4/parser/binary_opsyn.sno
./scrip --compile $f > off.s                 # lattice not run
SCRIP_ZDP=1 ./scrip --compile $f > on.s      # lattice run, nothing else changed
diff off.s on.s
```

```
68c68
< .Lbynamefnzd4:          .string          "&"
> .Lbynamefnzd3:          .string          "&"
71c71
<                         lea              rdi, [rip + .Lbynamefnzd4]
>                         lea              rdi, [rip + .Lbynamefnzd3]
```

Corpus-wide: **81 of 656 programs move** when the lattice pass runs. `SCRIP_ZDP=1` alone
reproduces it — the zone plan, the ZREF accessor and the every-port probe are all irrelevant to it
(each was suspected in turn and each was cleared by isolation).

## WHY THIS IS SERIOUS

`zdp_analyze` is supposed to be a pure static analysis: a worklist fixpoint over the γ/ω graph that
computes a depth per node and writes into its own side tables. It is **DEFAULT-INERT** precisely so
that it can be believed. But when it runs, the emitted code changes — so a ZDP verdict is a verdict
on a DIFFERENT PROGRAM than the one that ships.

That is the s132 MONITOR lesson exactly, and it was already written down in RULES.md: *"a monitor
verdict is a verdict on a DIFFERENT program until every one of its differences from the shipped
build is independently proven inert."* The same trap, in the instrument built to replace the monitor.

**Consequences, stated plainly:**
- The s133 tier census (70,095 verdicts, 654 programs), the s134 bomb counts (3,938 / 519 programs),
  the s134 static TEARDOWN-SKEW set (MATCH_BEGIN 820 · MATCH_DEFER 498 · MATCH_ARBNO 139), the s135
  anchor zeros, and the s136 every-port probe census were **all produced with the lattice enabled**.
  None of them describe the shipped program. **Do not cite any of them as fact.**
- The s136 probe's "found nothing on the `deferclob` corpse" result is included in that. The corpse
  may be reachable by the probe on the *unperturbed* program; nobody has run that.
- The s136 probe's OFF null (1 mover, `unary_not.sno`, over 656) is NOT affected — that measured the
  instrument disabled, and it is sound.

## WHAT WAS ELIMINATED (do not re-suspect these)

1. **Registry ordering in the zone plan** — `zzone_off_of` asking capture→arbno→fence→leaf and taking
   the first non-refuse. Tested with a multi-claim diagnostic: **0 nodes are claimed by two registry
   classes** on the movers. Refuted.
2. **Registry side effects via the plan** — the plan was rewritten to never call the registry at all.
   **Still 81 movers.** Refuted.
3. **The ZREF accessor / the probe** — both off in the isolating run. Refuted.

## WHERE TO LOOK NEXT (ranked, not guessed at random)

The pass reads two foreign authorities inside its transfer function, and those are the only places it
can touch shared state:

- `zdp_carve()` → **`zw_carve_k(nd)`** — THE ONE CARVE AUTHORITY.
- `zdp_out_gamma()` → **`zls_result_live(nd)`**.

The moved symbol is `.Lbynamefnzd<N>` — a **by-name-function label counter**, which says the
perturbation is an ALLOCATION or NUMBERING, not an arithmetic difference. Check whether either of the
two functions above lazily assigns an id / allocates a slot / bumps a counter on first call for a
node. If so, the lattice's read ORDER differs from the emitter's read order and the numbering shifts.

**The fix shape, once localised:** the analysis must consult a non-allocating query form of whichever
authority is bumping, or the pass must run after all numbering is final. ⛔ Do NOT "fix" it by making
the lattice reproduce the emitter's visit order — that is a second opinion about an order somebody
else owns, and it will drift.

## THE GATE THAT SHOULD HAVE CAUGHT THIS, AND MUST EXIST NOW

Every default-inert analysis pass needs its own null: **compile-STDOUT manifest with the pass ON vs
OFF must be 0 movers.** The existing manifest (`scripts/util_zdp_stdout_manifest.sh`) only ever
compared instrument-OFF against a prior build — it proved the pass contributes nothing *when
disabled*, which is not the property that matters for a pass whose whole purpose is to run.

**A default-inert pass is not automatically an inert pass. Prove the ON null, not just the OFF null.**
