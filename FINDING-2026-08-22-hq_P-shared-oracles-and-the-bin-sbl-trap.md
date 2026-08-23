# FINDING-2026-08-22-hq_P-shared-oracles-and-the-bin-sbl-trap

FROM hq_P, s259. **Two Lon in-chat rulings executed, and a measured trap that contradicts `RULES.md`.**
Full detail lives at **`/home/resources/ORACLES.md`** (written this session, beside the oracles themselves).

## Lon's rulings, routed per protocol law 6

1. *"But everyone should be using the shared /home/resources."*
2. *"there should be two SPITBOL versions in /home/resources, one that is pristine with minimal patches and
   the other with IPC tracing and the whole enchilada."*

**Executed.** `x64` promoted to **`/home/resources/x64`**, and every root's `x64/` replaced by a symlink to it
— **19 roots: 16 seats + hq_C + hq_P + ceo.** Each was checked clean (`git status` + unpushed count) before
being touched; none was dirty. **Oracle smoke-verified 19/19** (`sbl -bf` → `ok`), not merely present. ~1.0 GB
of duplication removed.

⛔ **This corrects work I did earlier in the same session**: on finding 8 of 16 seat roots missing the oracle,
I cloned x64 into each. Lon's ruling landed minutes later and the 8 private clones became 19 shared symlinks.

**Both of Lon's two versions exist, confirmed by measurement rather than by name:**

| role | path | `sysmc`/`sysml`/`sysmv` |
|---|---|---|
| pristine, minimal patches — **BENCHMARK** | `/home/resources/spitbol-clean/sbl` | **0 files** |
| the whole enchilada, IPC tracing — **CORRECTNESS + monitor** | `/home/resources/x64/bin/sbl` | **1 file** |

## ⛔⛔ THE TRAP: `spitbol-clean/sbl` ≠ `spitbol-clean/bin/sbl`

```
bcea36eb…  spitbol-clean/sbl            ⭐ the oracle — supports -f
172b206b…  spitbol-clean/bin/sbl        ⛔ NO -f support
172b206b…  spitbol-fork-rebuilt/bin/sbl ⛔ byte-identical
172b206b…  spitbol-upstream/bin/sbl     ⛔ byte-identical
```

On a two-line program that plainly contains `END`: `spitbol-clean/sbl -bf` → **`ok`**;
`spitbol-clean/bin/sbl -bf` → ⛔ **`No END statement found in source file(s).`** — but `-b` → `ok`.

⛔ **Those three identical binaries do not support `-f`, and `-bf` is MANDATORY for every program (s189). Under
our own required flag they reject EVERY program** — the "full, plausible, entirely false all-FAIL table" class
CLAUDE.md records hitting in three separate sessions.

⭐ **The trap is inherent to SPITBOL's build layout and will keep re-appearing.** A SPITBOL tree ships a
prebuilt `bin/sbl` as **BASEBOL, the bootstrap**; `make spitbol` consumes it and writes the product to the
**top level** as `./sbl`. In our `x64/` fork `bin/sbl` **is** the product; in upstream layout it is the
bootstrap. **The two layouts disagree, and the natural generalisation "the oracle is `<root>/bin/sbl`" lands
exactly on the trap.**

## ⛔ `RULES.md:65` NAMES THE TRAP

The FACT RULE directs benchmarking at **`/home/resources/spitbol-upstream`**, whose binary is byte-identical
to the trap and rejects every program under `-bf`. **The code is right and the rule text is wrong**:
`lib_oracle_flags.sh:sbl_clean_bin()` returns `/home/resources/spitbol-clean/sbl`, which works. Not edited
unilaterally — `RULES.md` is total authority; raised with hq_C and ceo. ⭐ Standing lesson: **name the oracle
through `lib_oracle_flags.sh`, never by assembling a path.**

## Preflight state this establishes

Firing gate (`GOAL-CEO.md` Phase 0): **`fleet` shows 0 unanswered questions** ✅ (Q=0 every mailbox) ·
**every seat root passes the oracle preflight** ✅ (was **8/16**, now **19/19 smoke-verified**) ·
**both HQ cursors pushed** ✅.
