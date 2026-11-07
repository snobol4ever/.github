---
name: scrip-build
description: How SCRIP is built: make -j8 and its targets, the outputs, the per-root objdir, ccache, the build cache, the freshness guard, generated tables, the header rule. REQUIRED by the skill gate before editing the Makefile.
---

# Building SCRIP

The shared box's caches and pools are skill `shared-box`; the C style is skill `scrip-c-code`. Detail is in `reference.md` beside this file.

## 1. The build

```bash
cd SCRIP && make -j8                    # ./scrip + out/libscrip_rt.so + out/scrip-ipp; never above -j8
make parsers-sc                         # the seven Snocone parsers as out/parser_<lang> and their modules
make pristine                           # wipe and rebuild
make test                               # the blocking set (the coo's)
```

- **Outputs**: `scrip` (the driver alone, a few hundred KB) linked against `out/libscrip_rt.so` (the compiler and the runtime, since the runtime compiles at run time: EVAL, CODE, `call/N`); `out/libscrip_rt0.so` and `out/scrip0` (stage 0: no parser module linked); `out/libscrip_parser_<lang>.so` (a parser's descriptor reached only by `dlsym`, CEO-1823); `out/buildinfo` (the tree hash the freshness guard reads); runtime objects cached in-tree under `out/rt_pic-<RT_TAG>`.
- **The objdir** is per root: `/tmp/si_objs<root path with / as ->`; a reboot empties `/tmp`, after which every runner refuses rc 2 on a stale `./scrip` until `make` runs. Rebuild after every commit or the gates refuse a stale binary.
- **ccache** wraps every compile (`CCACHE_BASEDIR=/home`, so trees under /home share hits); `S4E_NO_CCACHE=1` builds without it (the control arm).
- **The build cache** `/home/resources/builds/scrip/<key>/` (the key from SCRIP's tree, the harness tree and the toolchain): `make` on a clean tree at a cached key copies the build in and prints `FETCHED <key>`; the first clean build of a tree publishes it. A dirty tree builds locally and publishes nothing.
- **`RT_OPT` is `-O0`** with frame pointers; no `-O2` build, ever (RULES.md § NO -O2 BUILDS).
- **Generated sources are regenerated, never edited**: the bison and flex parsers by `harness/scripts/regenerate_parser_and_lexer_from_sources.sh` (a grammar edit is invisible until it runs); `box_cell_shapes.inc`, `gc_allocating_table.inc`, `rt_entry_table.inc`, `builtin_table.inc` by their generators, before the build, or the freshness guard refuses.

## 2. The header rule (CEO-2032, the header-split design; Lon: "how about re-design our headers")

- **R1 one header, one structure**: a type header declares one structure (or one closely bound family) with its fields, constants, one-line accessors and the prototypes over that type; an interface header `foo.h` declares what `foo.c` defines for others.
- **R2 include what you use, and only that**, by its path from `src/` (`#include "ir/ir_node.h"`); a pointer needs a forward declaration (`ir/ir_fwd.h`), not the struct's header.
- **R3 no inline bodies but one-liners** in a header (at `-O0` an inline body is a static copy per unit).
- **R4 the fan-in ceiling**: a header outside the base set reaches at most its users plus 4 units, and at most a third of the units; no umbrella header (two or more includes, no declarations of its own).
- **R5 the proof of a header move**: every object byte-identical after `objcopy --strip-debug` against the parent, both trees compiled the same way at the same path (`util_objects_identical_stripped.sh`); a body-moving step is proved instead by its smokes and the identity of what it did not move.
- **The gate** `test_gate_no_header_reaches_more_units_than_its_users.sh` (in the blocking set), over `util_header_fanin.py`, which asks the compiler (`make -B -n build-all`, `gcc -MM`), never the possibly stale `.d` files. On 2026-11-01 (SCRIP 9cb24d2ca) it reads RED: 31 headers over the ceiling and one umbrella, after all seven header steps closed DONE.
