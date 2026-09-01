# FINDING: `make pristine` is not concurrency-safe **within one seat root**, and a raced build is indistinguishable from a good one.

**Seat:** seat08 (FLEET-8) · **Date:** 2026-09-01 · **Found while:** trying to get a trustworthy pristine build before quoting a DONE-WHEN number on `raku-frontend-real-world-syntax-gaps`.

## WHAT WAS MEASURED

Three-plus concurrent `make pristine` were live in the single seat root `/home/claude08`:

```
880609 -> 889621   another row's DONE-WHEN wrapper (started 17:25:56), which itself runs
                   `make pristine` and then a 2400s corpus suite
948266             a third make pristine
923068 -> 923070   mine
```

All share **one** objdir, `/tmp/si_objs-home-claude08-SCRIP`, and **one** `$(ROOT)/out`. `make pristine`'s recipe wipes both at start. Measured effect: objdir empty and `./scrip` **absent for 6+ minutes**, with three builders repeatedly deleting each other's output.

## WHY THE EXISTING GUARANTEE DOES NOT COVER IT

CLAUDE.md states, correctly, that the objdir is per-checkout by construction (`OBJ ?= /tmp/si_objs$(subst /,-,$(ROOT))`) and concludes: *"two trees never share `.o` files and the HQ-27 ABI-mix class is structurally impossible."*

⛔ **That covers cross-TREE mixing. It says nothing about two SESSIONS in one tree**, which is what this was. The derivation keys on `$(ROOT)` — the same value for every session in the same seat — so concurrent builds in one seat root collide by design, not by accident. HQ-27 PRISTINE-BUILD-BEFORE-VERDICT assumes a single builder and nothing enforces it.

## WHY IT MATTERS MORE THAN AN ORDINARY RACE

**The failure is silent.** A binary built while another `make pristine` was wiping the objdir looks exactly like a binary built cleanly — same path, same name, no warning, and `make` exits 0. Every gate verdict from this seat is untrustworthy while this holds, and nothing in the output says so. That is the same shape as the false-green class the instrument laws exist to close, arriving through the build rather than through a harness.

**How it happens routinely, with nobody at fault:** Lon drives the fleet with `/clear` + one fixed prompt. A new session can start while a prior session's background DONE-WHEN still holds the tree — and `done` runs DONE-WHEN by design, so a DONE-WHEN that itself calls `make pristine` (this one did) is a normal, sanctioned way for a long build to be running unattended in a seat that now has a live session in it.

## WHAT I DID

Stood my own build down rather than race the job that started first, and **reported no DONE-WHEN number**, since any figure I produced would have graded a binary I could not vouch for. The row's last honestly-measured figure (pass 37's 5/5) stands unchanged in its baton.

## QUESTION FOR HQ (asked, non-blocking: `q-make-pristine-not-concurrency-safe-within-one-seat-root`)

Is concurrent `make pristine` within one seat root expected? If so, either:
- `make pristine` takes a per-root lock and waits (or refuses loudly) rather than wiping a live objdir; or
- DONE-WHEN runners get their own `OBJ=`/`out` so an unattended criterion cannot collide with the seat's interactive build.

Refusing loudly is worth more than either fix on its own: **the danger is not the collision, it is that the collision is invisible.**
