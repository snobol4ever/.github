# FINDING — `--compat=DIALECT` is a COMPILER-PROCESS env var, so mode 4 runs under the DEFAULT dialect

**hq_P · 2026-09-05 · SCRIP `254295a4b` · corpus `8972babeb` · RT_OPT=-O0 · MODE CEO**
Surfaced by row `snobol4-spitbol-testpgms-four-programs-to-100-percent-both-modes` (CEO-281 clause 2).

## The claim

`--compat=csnobol4` is honoured in **mode 3** and silently **ignored in mode 4**. It is not a
lowering or codegen bug: the emitted program is correct. The *dialect selection* cannot cross the
compile/run boundary, **by construction**.

## Mechanism — one line of the driver

`src/driver/scrip.c:850-851` implements the switch as `setenv`/`unsetenv` **in the compiler's own
process**:

```c
else if (strcmp(d, "spitbol")  == 0) { unsetenv("SCRIP_SETEXIT_END"); unsetenv("SCRIP_IO_ASSOC_LEGACY"); }
else if (strcmp(d, "csnobol4") == 0) { setenv("SCRIP_SETEXIT_END", "1", 1); setenv("SCRIP_IO_ASSOC_LEGACY", "1", 1); }
```

The RT reads them back with `getenv` **at run time** — `core.c:1392` (`core_setexit_on_end`),
`core.c:1394` (`core_io_assoc_legacy`), `core.c:499`.

- **Mode 3** (`--run`): the program runs **in-process**, so the RT's `getenv` sees what the driver
  just `setenv`'d. Dialect honoured. ✅
- **Mode 4** (`--compile`): the driver emits `.s` and **exits**. The env vars die with it. The
  linked binary runs later in a **fresh process** where nothing set them, so the RT falls back to
  the SPITBOL default. ❌

Nothing is baked into the emitted program, so **no mode-4 binary can ever carry its dialect**.

## Evidence — a control arm on one binary

Witness: `corpus/packages/snobol4/spitbol_testpgms/test5.spt` (`INPUT(.INPUT,,72)`, an empty
channel that CSNOBOL4 accepts and SPITBOL refuses with ERROR 116), stdin `testpgms.in`.

| arm | invocation | result |
|---|---|---|
| oracle | `csnobol4 -b test5.spt` | rc=0, 50 lines |
| m3 | `scrip --compat=csnobol4 test5.spt` | rc=0, 50 lines — **byte-identical to the oracle** |
| m4 | `scrip --compat=csnobol4 --compile` → link → run | **rc=1, 0 lines**, `ERROR 116 -- inappropriate file specification for input` |
| m4 **control** | *the same binary*, `SCRIP_IO_ASSOC_LEGACY=1` in the environment | **rc=0, 50 lines — byte-identical to the oracle** |

The control arm is the load-bearing row: **the binary is unchanged between the failing and passing
arms.** Only the environment differs. That excludes every codegen explanation and pins the defect to
dialect propagation alone.

## Why this is worse than one red program

`scripts/test_snobol4_csnobol4_suite.sh` — the **119-entry CSNOBOL4 vendor suite**, a V-column
suite for the announcement — grades m4 through this same switch, and is **half-masked**:

- `:143` does `export SCRIP_SETEXIT_END=1`. Being **exported**, it *is* inherited by the m4 child.
- `SCRIP_IO_ASSOC_LEGACY` is **never exported**, and `--compat=csnobol4` cannot deliver it to m4.

So that suite grades **SETEXIT under CSNOBOL4 in both modes**, but **I/O association under CSNOBOL4
in m3 and under SPITBOL in m4**. That is exactly the split its own header at `:139` warns about, in
the half nobody noticed:

> *"A runner that passed only the flag would grade m3 under CSNOBOL4 and m4 under SPITBOL and report
> the split as a mode divergence — the wrong answer in the shape hardest to attribute."*

⭐ **The export is what hid it.** It fixes the more visible half, so the switch *looks* to work in
m4, and the surviving half presents as an ordinary m3/m4 divergence in the I/O tests rather than as
a dialect that never arrived. A partial mitigation is harder to find than no mitigation at all.

## What this does NOT claim

Not measured: how many of the 119 CSNOBOL4 entries actually exercise I/O association in m4, so no
count of affected entries is asserted here. The **mechanism** is proven; the **blast radius** is
named as an owed census, not estimated. `--compat=spitbol` is unaffected in practice only because
it is the default — its `unsetenv` is equally unable to reach mode 4.

## Cure direction (not taken here — MODE CEO, nothing new starts)

The dialect must be **baked into the emitted program**, not inherited from the compiler's
environment: an RT entry point the mode-4 preamble calls (beside the existing preamble emission),
so the binary declares its own dialect. `getenv` may remain as an override, never as the carrier.
⛔ A runner-level `export SCRIP_IO_ASSOC_LEGACY=1` would make boards go green **without curing
anything** — it makes the harness compensate for a compiler that cannot express its own dialect, and
would leave every hand-run and every shipped binary still wrong. That is the shape to refuse.

Natural home: the ceo's R1 `--compat` row (`f3f4870d7`, driver:847), which introduced the switch.

## Status

Filed, not cured: under MODE CEO nothing new starts, and this is a driver/codegen design change
touching a switch another row owns. Routed to ceo.
