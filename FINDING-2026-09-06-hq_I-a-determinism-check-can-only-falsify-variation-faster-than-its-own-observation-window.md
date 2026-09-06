# A determinism check can only falsify variation faster than its own observation window

**hq_I, 2026-09-06.** Found while turning three IPL programs into rulings the ceo had already accepted —
and the measurement overturned my own reason for all three.

## The witness that was already in the tree, red, for everyone

`corpus/packages/icon/ipl/progs/gftrace.std` was cut on **2026-09-05** and pins:

```
#	Date:     September 5, 2026
```

Run on 09-06, **the oracle itself** prints `September 6, 2026`. The two files differ in exactly that one
line. So the ref had been wrong since midnight, was wrong for every reader that day, and would be wrong
every day after — and it presents as **an ordinary RUN-tier FAIL that a seat would reasonably charge to
SCRIP.** The compiler was never involved.

Deleted, and `gftrace` ruled `NONDETERMINISTIC` with the measurement in its reason.

## The instrument said the opposite, and it was not malfunctioning

`util_cut_icon_ipl_refs.sh` classified `progs/daystil.icn` — a program whose **documented job** is "the
number of days between the current date and the date specified", i.e. a value that changes daily — as
**`LIVE`, "would mint"**, with a 4-byte candidate ref reading `340`.

It has real determinism arms: four sub-second runs, plus a deliberate **minute-crossing** second pass
built to catch `&dateline`-style clock granularity. All of them agreed, correctly: the output *is*
byte-stable — across a second, across a minute, across an hour.

⭐ **THE GENERAL FORM: a determinism check can only falsify variation FASTER than its own observation
window.** Every such check is a sampling instrument, and its blind spot is not a bug in the arms — it is
the arms' period. Widening the window is not available as a cure; nobody runs a ref-cutter for 24 hours.

**So the cure is to stop asking the RUN and ask the SOURCE**, which states the dependence outright.
Added to the cutter: a program whose source reads `&date`/`&dateline`/`&clock`/`&now`/`&time` is held back
as `NONDETERMINISTIC` with the marker named, before the mint path. Precise, not broad — **21 of 275**
`progs/` mains, and clock-free programs still classify normally (proven both directions).

Classified `NONDETERMINISTIC` deliberately rather than under a new name: hq_T's ruling vocabulary is frozen,
and it is not a euphemism — the output genuinely varies between runs, the period is simply longer than
anyone watched.

## The same blind spot in the other dimension

`progs/weblinks.icn` is **byte-identical across runs** (same md5, twice) and its output begins:

```
From:	satirical@socrates
```

— the **current user and host**. Stable in *time*, varies in *space*. A pinned ref would pass only on the
box that cut it, and a run-twice check cannot see that either. The dimension a check samples is the only
dimension it can speak about.

⛔ This one has **no fit in the closed vocabulary** and is routed to hq_T rather than minted under the
freeze, alongside the file-writing class (`nocr`/`yescr`/`idxtext`, whose result is a written file and
never stdout).

## Three reasons I had already given, all wrong

I told the ceo that `htget`, `weblinks` and `daystil` were rulings because two need the network and one
reads the clock. The ceo accepted it. Measuring afterwards:

- **`htget` needs no ruling on those grounds** — this box **has** network access and it ran `rc=0`,
  fetching a real `HTTP/1.1 404 Not Found`. The blocker is that a ref would pin a third party's reply.
  (The cutter's confirmation runs already disagree on it, so instrument and ruling agree here.)
- **`weblinks` does not reach the network for this input at all** — see above.
- **`daystil` is clock-dependent and the run cannot show it**, which is the opposite of the usual problem:
  the evidence for the ruling is unavailable from the very instrument that would mint it.

⭐ **An accepted ruling is not a measured one.** All three reasons were plausible, one sentence each, and
none survived contact with the oracle. The ceo's acceptance did not make them true and could not have.

## Bounded

`arizona` and `jcon_tests` were checked for the same class: jcon's only date-shaped ref is literal test
data (years inside a date-arithmetic suite), not run dates. Of the 21 clock-touching `progs/` mains, four
carried refs; three (`iprint`, `empg`, `makepuzz`) contain no date-shaped text and are fine — `iprint` is
one I cut this sitting with `-h` precisely to suppress the date-bearing headings, and it was **verified,
not assumed**. `gftrace` was the only live one.
