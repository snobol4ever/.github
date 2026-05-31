# REPO-csnobol4.md

**GitHub:** `snobol4ever/csnobol4`
**Clone:** `https://TOKEN_SEE_LON@github.com/snobol4ever/csnobol4`

## What it is

CSNOBOL4 2.3.3 — Philip L. Budne's C port of the original Bell Labs SIL macro SNOBOL4.
Forked here as the base for snobol4ever SNOBOL4 compatibility work.

Key files:
- `v311.sil` — SIL source, the canonical spec
- `isnobol4.c` — main interpreter (compiled by Makefile2; hand-edited for FENCE(P))
- `snobol4.c` — alternate/reference C translation (not compiled by default build)
- `proc.h` / `proc.h2` — function extern declarations
- `data_init.h` — static data initialization
- `res.h` — resource descriptor layout
- `test/fence_function/` — FENCE(P) test suite (10 tests)

Modifications vs vanilla CSNOBOL4 2.3.3:
- **FENCE(P)** — 1-arg form implemented (opcodes 37–40, FNCP builder). See FENCE.md.
- **STNO trace patch** — `chk_break(0)` early-out removed from `isnobol4.c`, `snobol4.c`,
  and `v311.sil`. This makes &STNO tracing fire unconditionally, required for the
  sync-step monitor harness. No functional difference for normal programs.

## Session Start

```bash
git config --global --add safe.directory /home/claude/csnobol4
cd /home/claude
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/csnobol4
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/x64
git clone https://TOKEN_SEE_LON@github.com/snobol4ever/SCRIP
cd csnobol4
git config user.name "LCherryholmes"
git config user.email "lcherryh@yahoo.com"
git log --oneline -3
```

**Build:**
```bash
bash /home/claude/SCRIP/scripts/install_system_packages.sh
bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh   # primary target
bash /home/claude/SCRIP/scripts/build_spitbol_oracle.sh    # oracle
```

## Build

⛔ **Use only the checked-in build script. No other build method. No exceptions.**

```bash
bash /home/claude/SCRIP/scripts/build_csnobol4_oracle.sh
# output: /home/claude/csnobol4/snobol4
```

This runs `make -f Makefile2 xsnobol4 -j4` against the committed source.
All generated C files (`isnobol4.c`, `proc.h`, `data_init.h`, etc.) are
**committed and correct** — do not regenerate them.

### Why not `./configure && make` or `genc.sno`?

`make snobol4` / `make all` try to regenerate C from SIL using an already-installed
`snobol4` binary — a bootstrapping dependency that does not exist in a fresh session.
`genc.sno` via SPITBOL produces a listing/assembly dump, not valid C.

The committed C files (`isnobol4.c`, `snobol4.c`, `proc.h`, `data_init.h`, `res.h`)
are the authoritative hand-maintained translation of `v311.sil`. When you edit `v311.sil`,
you must also manually update the corresponding C — there is no automatic regeneration path
in this environment. See FENCE.md for an example of what changed files look like.

### If you edit v311.sil

You must hand-edit the corresponding C files to match. Key correspondences:

| v311.sil construct | C files to update |
|--------------------|-------------------|
| New XPROC (pattern node) | `isnobol4.c` + `snobol4.c`: add `L_XNAME:` block in dispatch; add top-level `XNAME(ret_t retval)` if used as fn pointer |
| New PROC (function builder) | `isnobol4.c` + `snobol4.c`: add top-level `NAME(ret_t retval) { ENTRY(NAME) ... }` |
| New EQU opcode | `equ.h`: add `#define XNAME (N)` |
| New function extern | `proc.h` + `proc.h2`: add `extern int NAME(ret_t);` |
| New descriptor cell | `res.h` + `res.h2`: add struct field + `#define` |
| New static init | `data_init.h` + `data_init.h2`: add `D_A(res.name) = ...` |

After editing, rebuild with the build script and run the gate for your goal.

## Run fence tests

```bash
cd /home/claude/csnobol4/test/fence_function
make spitbol   # oracle — should be 10/10
make csnobol4  # our build — target 10/10
make diff      # side-by-side comparison
```

## Active goals using this repo

- GOAL-CSNOBOL4-FENCE.md — FENCE(P) 1-argument function ✑ DONE
