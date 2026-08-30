# FINDING 2026-08-30 seat14 — Raku array parameters passed to a `sub` are copied, not aliased: in-place mutation inside the sub never reaches the caller's array. New bug, isolated, NOT fixed — needs calling-convention work.

## CONTEXT
Surfaced while implementing hq_P's ruling on `insertion-sort.raku`/`merge-sort.raku` (see `FINDING-2026-08-30-seat14-raku-benchmark-refs-depend-on-prng-algorithm-match.md` — fixed those two kernels' input generation to be PRNG-independent, per ruling `ruling-prng-refs-are-ungradeable-by-construction`). After that fix, `insertion-sort.raku` generates the correct array (verified byte-identical to `/usr/bin/raku` at every checkpoint: elems, first, second, and last element) but still fails DONE-WHEN: SCRIP prints `224` (`/usr/bin/raku` prints `0`, matching the `.ref`).

## ROOT CAUSE, ISOLATED CLEANLY
`224` is exactly `@ints[0]`'s value **before** `insertion-sort(@ints)` runs — the array comes back from the call completely unsorted, as if the call had no effect at all.

Minimal repro (no sorting, no randomness, rules out every other confound):
```raku
sub zero-it(@a) { @a[0] = 999; }
my @x = (1, 2, 3);
zero-it(@x);
say @x[0];
```
- real raku: `999` (Raku aliases a `sub`'s array parameter to the caller's array by default — mutating `@a` inside the sub mutates the caller's `@x`, no `is copy`/`is rw` needed, this is ordinary Raku semantics for array/hash parameters specifically, unlike scalar parameters which default to read-only aliases that can't be reassigned but whose *elements* can still mutate through — same net effect here).
- SCRIP `--run`: `1` — the sub's `@a` is a distinct copy; mutating it inside the sub is invisible to the caller.

This means **any SCRIP Raku program that mutates an array parameter in place inside a `sub` silently does nothing to the caller's data** — a correctness gap much broader than these two benchmark kernels; any in-place algorithm taking an array parameter (sort, shuffle, filter-in-place, etc.) is affected.

## WHY THIS WASN'T CAUGHT BEFORE
`insertion-sort.raku` previously failed for an unrelated, upstream reason (the `xx`-does-not-reevaluate bug made its input array constant — see the other new FINDING filed this session), so nobody had a working input to notice the sort itself was a no-op. Fixing the input generator (this session, per hq_P's ruling) removed that mask and exposed this as the NEXT layer down. `test_smoke_raku.sh` (724/724) apparently has no case that both (a) takes an array parameter and (b) mutates it in place and (c) checks the caller's copy afterward — worth someone adding one once this is fixed, as a regression guard.

## NOT ATTEMPTED THIS PASS
This is calling-convention / parameter-binding behavior, not a one-file bug — the fix site is wherever SCRIP's Raku lowering binds a `sub`'s array-typed formal parameter to its actual argument (likely `src/lower/lower_raku.c`'s call/param-binding path, possibly interacting with the same box-IR machinery the `xx` finding named). I have not located the exact binding code or characterized what a fix would need to preserve (e.g. Raku scalar parameters are read-only aliases — reassigning the parameter itself is an error — while array/hash parameters allow element-level mutation through the alias; a fix must reproduce that distinction, not just blanket-alias everything). Flagging precisely rather than guessing at a fix site I haven't verified, consistent with this session's other two findings.

## WHAT THIS MEANS FOR insertion-sort.raku / merge-sort.raku RIGHT NOW
The generator fix (this session, `FINDING-...-prng-algorithm-match.md`) is real, verified, and worth keeping regardless — it removes the "ungradeable by construction" problem and both kernels' `.ref` files already happen to match the corrected live-oracle output exactly (`0` for both), no ref changes needed. But `insertion-sort.raku` still cannot pass DONE-WHEN until THIS bug (array-parameter aliasing) is also fixed — one layer closer to green, not there yet. `merge-sort.raku` is unaffected by this particular layering question since it's still independently blocked by the pre-existing, declined map/grep native-emitter gate regardless.

## NEXT ACTOR
1. Locate where SCRIP's Raku lowering binds array-typed sub parameters (likely near wherever scalar parameter binding happens in `lower_raku.c` — scalar aliasing apparently already works correctly, going by every other passing test in this corpus that takes a scalar parameter, so the bug is specific to the array/hash case).
2. Characterize what "alias" needs to mean at the box-IR level here (pointer/reference to the same underlying storage, not a copy) before attempting a fix — this may share machinery with, or be a prerequisite for, the `xx`/closure work already flagged as needing new infrastructure this session.
3. Minimal regression check once fixed: the `zero-it` repro above, plus re-running `insertion-sort.raku`'s DONE-WHEN check (should then need only the array-parameter fix to go green, per the verification above).

## ADDENDUM (seat14, same day) — checked whether this is array-specific or a class, per hq_P's ask BEFORE anyone lands a narrow fix
**Cannot actually compare against hash or indexed-scalar parameters — both hit an EARLIER, separate parse gap, so the copy-vs-alias question isn't even reachable for them yet:**
- `sub set-hash(%h) { ... }` — **parse error**. A `%`-sigil parameter in a sub signature doesn't parse at all (plain `%h<k>=1` hash literal/subscript usage outside a signature works fine — confirmed in isolation — so the gap is specifically the signature position, not hashes generally).
- `sub set-elem($s) { $s[0] = 999; }` — **parse error**. `[...]` indexing on a `$`-sigil variable doesn't parse (real Raku allows this: a scalar bound to an array argument can be indexed; SCRIP's grammar apparently ties `[...]` to `VAR_ARRAY` tokens specifically).

**Conclusion: this is NOT yet observable as a per-kind exception, because there is no working sibling case to be narrower than.** The plain `@a`-sigil array parameter (this FINDING's own repro) is the ONLY container-parameter shape that currently parses at all — so a fix scoped to it isn't the per-op-filter shape RULES.md forbids, it's just the only shape that exists yet. Both gaps above are separate, pre-existing, uncharacterized parse issues (not investigated further — out of scope here), worth their own row if someone wants hash-parameter or scalar-array-indexing support; they are NOT blocking or informing the array-alias fix.
