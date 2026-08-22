# FINDING — a stale RUNPATH after a seat folder rename prints the exact false-all-FAIL signature, with no oracle involved

seat07, 2026-08-22. Side discovery while verifying row `oracle-asset-fallback-three`; not that row's
bug and not fixed by it.

## What happened

`board_beauty_m1.sh`, run clean on this seat, printed a **uniform `rc127` / `COMPILE-FAIL` wall across
every rung, both modes** — the identical shape of the "non-empty is not alive" false-signal class
CLAUDE.md warns about for a missing oracle. The oracle was not the cause: `util_beauty_override.sh`'s
`$SCRIP` leg failed the same way (`rc=127`) on a completely unrelated invocation.

```
$ /home/claude07/SCRIP/scrip /tmp/hi.sno < /dev/null
scrip: error while loading shared libraries: libscrip_rt.so: cannot open shared object file: No such file or directory
$ readelf -d scrip | grep RUNPATH
 Library runpath: [/home/claude7/SCRIP/out]        <-- note: no leading zero
```

`out/libscrip_rt.so` was present the whole time, at the correct, current path
(`/home/claude07/SCRIP/out/libscrip_rt.so`). The `scrip` binary simply could not find it, because its
baked RUNPATH pointed at `/home/claude7/SCRIP/out` — the pre-rename spelling of this seat's root
(`GOAL-SCRIP-HQ.md` item 15: seat roots were renamed `/home/claude7`→`/home/claude07`-style, zero-padded).

## Root cause — not a Makefile bug

`Makefile:24` computes `ROOT := $(shell pwd)` and links with `-Wl,-rpath,$(abspath out)` — dynamically
derived from the *build-time* working directory, correctly, every time. This `scrip` binary was linked
**before** this seat's folder was renamed, when `pwd` really was `/home/claude7/SCRIP`. RPATH is baked
into the ELF at link time; renaming the containing directory afterward does not update it. The binary
was silently unable to execute from that point on — anything that shells out to `./scrip` would report
a nonsense rc (127) that looks exactly like a language/compile defect, never mentioning the real cause.

## Why it matters beyond this seat

Any seat whose `scrip` was last linked before its own folder's zero-pad rename carries this same trap,
silently, until its next `make`/`make pristine`. It produces the *identical visual signature* as the
absent-oracle false-FAIL wall this project already has a named class for, but gates on it
(`test_gate_*`) would not catch it via oracle-presence checks — `scrip` itself is the thing not
running. Worth a cheap sanity check somewhere in the board/gate scripts (e.g. `"$SCRIP" --version
< /dev/null` or equivalent, refuse loudly if that itself fails) rather than only checking `[ -x
"$SCRIP" ]`, which is true of a binary that cannot actually load. Not proposing a queue row myself —
surfacing it for HQ to size.

## Fix applied (this seat only)

`make pristine` — full rebuild, correct RUNPATH now baked (`/home/claude07/SCRIP/out`), verified
`scrip` executes normally. This was a necessary prerequisite for verifying `oracle-asset-fallback-three`
end to end (needed a working `scrip` to see a real board ladder), not part of that row's fix.

## Scope check

Zero source changes. A rebuild from unmodified, already-committed source. Nothing to commit for this
finding beyond the finding itself.
