# FINDING — a gate pinned to an env switch goes RED, not dark, when the switch is deleted by law

**Seat:** hq_raku · **Date:** 2026-09-16 · **Tree:** SCRIP `0a3f38904` corpus `9e75ac5ce` RT_OPT=-O0
**Instrument:** `scripts/test_gate_raku_zframe.sh` (RK-ZC-8, the Raku ζ-frame regime pin gate)

## The measurement

Running every Raku gate on origin HEAD this sitting, `test_gate_raku_zframe.sh` returned **rc=1**:

```
--- INVARIANT A: killswitch SCRIP_RK_ZFRAME=0 (class-b witness must exit nonzero) ---
  FAIL class-b witness: rc=0 (expected nonzero — zframe_graph not disabling correctly)
--- INVARIANT B: full smoke suite must be 719/0 both modes ---
  OK   m3 FAIL=0  m4 FAIL=0
```

`SCRIP_RK_ZFRAME` occurs in exactly one file in the whole tree — **the gate itself**. No source reads it:

```bash
grep -rin 'rk_zframe' --include=*.c --include=*.h --include=*.cpp --include=*.sh --include=*.py .
# -> only scripts/test_gate_raku_zframe.sh, 4 hits, all in the gate
```

It was deleted on **2026-09-09** by `709a755df` — *"the 29 frame-placement switches and the enumerated rbp
helpers are deleted, each folded to the code it selected"* (CEO-447, Lon 09-09 09:2x: *"Get rid of enumerated
shape class now!!!"*). The same commit wired **`test_gate_no_zeta_frame_switches.sh` BLOCKING**, whose census
forbids exactly this class of name under `src/` forever.

## Why this is worth a FINDING and not just a fix

**The two gates were in direct contradiction, and only one could be green.** Invariant A could be satisfied
only by re-adding a `getenv("SCRIP_RK_ZFRAME")` that a blocking gate exists to convict. The law wins; the arm
had to be recut, not repaired.

⭐ **The general form: an env switch is the worst thing to pin a gate to, because of HOW it fails.** When the
switch is deleted, the gate does not refuse and does not go dark — the run with `SCRIP_RK_ZFRAME=0` is simply
an ordinary default-regime run. The witness ran **correctly** and exited 0, and the arm read that as
*"zframe_graph not disabling correctly"*. So:

- the gate went **RED on a perfectly healthy tree**, for **seven days**, and
- it **accused the compiler of the instrument's own obsolescence**.

This is the **outer-layer-wins** shape one level up (the same class as the `rc>=124` bucket wearing the clock's
name over three signal deaths, hq_raku 2026-09-15, carried in the cto's ledger — deliberately not linked here,
no FINDING file was cut for it): the gate's *frame* (a switch exists to flip) outlived the thing it framed, and the false frame
produced a confident, specific, entirely wrong accusation rather than a refusal. A gate that cannot tell
"the property is broken" from "my mechanism for observing the property was deleted" is not measuring the property.

⛔ **The corollary for every seat: a deletion campaign must sweep the INSTRUMENTS that consumed what it deleted.**
`709a755df` correctly swept `src/` and wired a gate to hold the line — and left behind a gate in another lane
whose central arm consumed the deleted name. Nothing caught it because nothing ran it: a red gate in no runner
is indistinguishable from a green one.

## The cure (landed this sitting)

Invariant A is recut into three arms that no switch can satisfy, and the obituary is in the gate's own header:

- **A1 — behavioural:** the class-b witness `sub f($a){return $a*2} say f(21);` (a user sub call with an
  argument — the shape that needs the ζ-frame entry's γ/ω wires) must print `42` in **both** modes.
- **A2 — census, scoped to this lane's own files:** zero frame-placement `getenv` across `lower_raku.c` +
  `src/parsers/raku/*.c`. The `src/`-wide line stays with `test_gate_no_zeta_frame_switches.sh`; this holds it
  next to the construct it would corrupt.
- **A3 — ask the BUILT COMPILER:** `--dump-zeta` on the witness must show sub `f` with its own `FN` scope and a
  vslot for its parameter — the observable the regime exists to produce.

⭐ **A first cut of A2 grepped `lower_raku.c` for the `zframe_graph = 1` assignment `709a755df` left there —
and went RED on a healthy tree within the hour**, because that assignment has since folded into the central
derived selector (`fl_derive_tier`, `src/ir/frame_layout.c`). That is *the same failure as the arm being
replaced*, committed while writing its obituary. It is recorded in the gate's header as a `⛔ DO NOT` so the
next reader does not re-point A2 at a spine file: **a gate in one lane must not pin another lane's internals.**

## Fail-once, each arm proven to red

| Arm | Planted defect | Result |
|---|---|---|
| A1 | witness returning `$a*3` | `out=63` → predicate rejected |
| A2 | `getenv("SCRIP_RK_ZFRAME")` planted in `lower_raku.c` | convicted, named `lower_raku.c:1217`; reverted |
| A3 | program with no user sub (`say 42;`) | no `FN f` scope, no vslot → rejected |

Note the A2 plant first drew **`GATE UNPROVEN(2)`** from the stale-binary guard — the guard firing ahead of a
source census is correct ordering, and rc=2 UNPROVEN is the honest answer rather than a red or a green.

**Gate now:** `=== RK-ZC-8 gate PASS ===`, A1+A2+A3+B all OK, on `0a3f38904`.
