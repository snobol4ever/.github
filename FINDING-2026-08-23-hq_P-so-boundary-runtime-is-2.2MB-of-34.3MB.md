# FINDING 2026-08-23 hq_P — the runtime half of libscrip_rt.so is 2.2 MB of 34.3 MB, and the back-edges that keep them fused are 30, not 900

**Seat:** hq_P (HQ-PERFORMANCE, `/home/claude_P`) · **Brief:** ceo `src-reorg-build-design` (s268) · **Tree:** SCRIP f110760f, .github 2976719e
**Instrument:** `nm` symbol-graph closure over the 262 built objects + `gcc -shared` link timing + 60 real m4 binaries. No wall-clock perf claims here; sizes and link times only.
**Status:** measured evidence for `ARCH-BUILD-SYSTEM-DRAFT.md`. ⛔ Nothing moved. Lon rules before anything is carved.

## 0. What was measured, and how

Sixty crosscheck programs were compiled to mode-4 (`--compile`), assembled, and linked against `out/libscrip_rt.so` — all 60 succeeded. Their undefined-symbol sets give the *root set* the shipped runtime must satisfy. Every one of the 262 objects in `out/rt_pic-f65f143e2f/` was read with `nm` for defined and undefined symbols, giving an object-level call graph. Everything below is derived from that graph, not from directory names.

## 1. The naive closure argument does NOT justify a split — and that is the trap

| measure | value |
|---|---|
| symbols the 60 m4 binaries need from the .so | 47 |
| objects in the transitive closure of those 47 | **228 / 262** |
| objects outside the closure | 34 |

Reading only this, the .so looks irreducible: 87% of it is genuinely reachable. Cutting individual edges confirms it — removing the single worst back-edge changes the closure by **zero objects**, and cutting all six shortest compile-at-runtime paths removes **one**. The graph is far denser than any one path suggests, so an edge-by-edge attack fails.

**The closure is the wrong question.** It asks "what is reachable", which for a language whose runtime can compile is nearly everything. The right question is "which direction does the coupling run, and how wide is the seam".

## 2. The seam is narrow, and it runs almost entirely one way

Partitioning the 262 objects by role (RT = `runtime/**` and the RX slab; CC = parser, lower, optimizer, emitter, templates, contracts, driver):

| direction | object-pair edges | note |
|---|---|---|
| CC → RT | **896** | correct and expected — the compiler is built on the runtime |
| RT → CC | **50** (136 symbol refs) | the entire problem surface |

Fifty edges is a *nameable* surface. It was enumerated in full and every edge falls into one of two classes.

**Class M — misplaced runtime code filed under a compiler directory.** The edge is an artifact of file location, and moving the file deletes it outright. Measured members: `driver/driver_globals.c` (the `fh_*` file-handle table, 28 refs), `driver/driver_data.c` (`dat_*` DATA registry, 23), `parser/icon/icon_runtime.c` (`cset_*` set ops, 9), `parser/prolog/prolog_atom.c` (24), `prolog_unify.c` (2), `prolog_builtin.c` (7), `parser/raku/re.c` (`nfa_*`, 4), `machine/bb_pool.c` (the RX slab, 4).

**Class C — genuine compile-at-runtime.** SNOBOL4 semantics require a compiler at run time, and this is real:
- `runtime_eval.c` → emitter/lower/parser/IR (41 refs) — `EVAL()` and `CODE()`
- `runtime/rt/bb_pat_build.cpp` → emitter/optimizer/IR (20 refs) — JIT of runtime-argument `LEN()`/`BREAK()` and dynamic pattern trees
- `pattern_match.c` → `snobol4.tab[parse_expr_pat_from_str]` (1 ref)

After relocating the Class-M files, the residual is **30 object-pair edges / 83 symbol refs**, and the compile-at-runtime three account for 58 of the 83.

## 3. The size result

| configuration | objects | `.o` bytes | linked `.so` | stripped | link time |
|---|---|---|---|---|---|
| status quo (one library) | 262 | 121.2 MB | **34.3 MB** | 12.15 MB | 0.39 s |
| runtime-only, after Class-M moves | 63 | 3.4 MB | **2.2 MB** | 1.13 MB | 0.04 s |
| compiler half | 199 | 117.8 MB | — | — | — |

The runtime is **2.8% of the object bytes** of the library that every compiled program links. `-O0 -g` throughout, per RULES.md § NO `-O2` BUILDS.

⭐ **Link time is not the problem and must not be sold as one: 0.39 s.** The number that matters is the 34.3 MB every emitted binary carries in order to reach 2.2 MB of runtime.

## 4. How much of the corpus could take the small library

553 `.sno` programs across `crosscheck/`, `programs/snobol4/`, and `benchmarks/` (⛔ `programs/lon/` excluded by construction, never opened): **18 use `EVAL()` or `CODE()` — 3.3%.**

⚠ That is a ceiling on eligibility, not a delivered win. `EVAL`/`CODE` is only the *visible* trigger; runtime-argument patterns reach the same machinery through `bb_pat_build`, and indirect reference (`$`) and by-name dispatch make a precise compile-time predicate necessarily conservative. Treat 96.7% as the optimistic bound to be narrowed by a real analysis, not as a promise.

## 5. Three build-model defects measured on the way

**(a) A wildcard source list would not link — carve first, wildcard second.** 292 sources on disk (excluding `backends/`), 265 in the build, **27 unbuilt strays** (CEO's census reproduced exactly). Zero phantom entries — the list does not rot in the missing-file direction, because `make` would fail. Test-compiling all 27 with the real runtime flags: **21 compile, 6 fail.** Linking the 21 alongside the built set: **fails with 16 duplicate `main` definitions plus three `rtx_str_shim` symbol collisions** (`rtx_gate_str`, `str_concat_d`, `VARVAL_fn` — exactly the collision survey 12 predicted). A wildcard switch before the attic carve breaks the build.

**(b) The objdir flattening hazard is silent, and the reorg triggers it.** `RT_PIC_OBJS` maps sources through `$(notdir)`, so two same-basename files in different directories collapse to one object path. Reproduced minimally: with `a/rt.c` and `b/rt.c`, make compiled `a/rt.c` only, **exited 0**, and `from_b` was simply absent from the object. No warning. Today there are **0 duplicate basenames across all 292 on-disk sources** — the scheme survives by accident with zero headroom, and survey 12's own recommendation (`rtx/sn4/`, `rtx/icn/`, `rtx/pl/`) would create collisions immediately. **Mirroring the tree in the objdir is a precondition of the reorg, not a cleanup.** This is the HQ-27 silent-wrong-build class through a third door.

**(c) `make setup` is broken and the prerequisites are wrong.** `make setup` runs `$(ROOT)/setup.sh`, **which does not exist** — `Error 127`. CLAUDE.md documents it as the fresh-environment path. The working installer is `scripts/install_system_packages.sh`. Separately, Makefile:20 documents prerequisites as `flex nasm build-essential libgmp-dev m4` — **`bison` is missing**, while five frontends ship bison-generated parsers.

## 6. Corrections to claims in circulation

- ⭐ **The two mandatory handoff-regen scripts are NOT broken.** `util_regen_benchmark_s_artifacts.sh` and `util_regen_feature_s_artifacts.sh` name `src/emitter/emit_bb.c`, `emit_core.c`, `x86_asm.h` **in header comments only** — documentation rot, no live logic. CEO's spot-check instinct was right; the alarming reading is wrong, and the recorded `.s` drift has some other cause.
- **`test_gate_rtcc_noclob_injection.sh` carries no fossils.** Its `src/runtime/rtx/rtx_inject_stub.S` and `src/templates/x86_asm.h` are files it *synthesizes* under `$TMP` as fixtures. A false positive of any grep-based fossil detector, mine included.
- **`test_gate_bb_one_box.sh` does carry `bb_alt.cpp` + 4 more deleted templates in a live file list** — this one needs re-proof that it can still fail.
- ⛔ **The snocone `.tab.c`-is-stale claim could NOT be verified in this root: `bison` and `flex` are not installed.** Reported unverified rather than repeated. The same fact is itself a finding — the committed generated parsers are load-bearing build inputs here, not conveniences.

## 7. Scripts↔src coupling (my method, stated)

Over all 506 files in `scripts/`: **168 reference `src/` paths**, 50 reference `backends/`, 122 distinct `src/` paths are named, and **52 of those do not exist.** (CEO measured 149/51/~52 on a different denominator; both stand, the denominators differ.)

The fossils stratify by era — `src/runtime/x86/*` (18 paths, the deleted mode-1/2 emitter), `src/backend/*`, `src/processor/*`, `src/include/{IR,SM,BB}.h`, `src/driver/interp*`. **Every previous reorg left a layer because none of them swept.** Without a sweep gate this reorg adds stratum four.

⭐ **The enforcement hook already exists and nobody has been reading it as one.** `test_gate_runtime_isolation.sh` and `test_gate_lower_isolation.sh` carry allowlists of headers "misfiled under parser/", each entry annotated with its owning relocation goal, and both are declared **ratchets: may shrink, must never grow.** Their entries — `parser/snobol4/scrip_cc.h`, and the four Prolog Term/atom/unify/builtin headers — are precisely the Class-M relocations the symbol graph found independently. The reorg should be **scored by allowlist entries removed.** (One detail: the runtime allowlist's rationale text cites `src/runtime/interp/pl_runtime.{c,h}`, itself now a fossil path.)

## 8. What this supports

The design that follows from it is in **`ARCH-BUILD-SYSTEM-DRAFT.md`** (this seat, same session): two libraries with one dependency direction, the three compile-at-runtime edges inverted through a registration vtable, a tree-mirroring objdir as a precondition, wildcards only after the carve, `make test` wired to the real blocking set, and a fossil-path gate so this reorg is the last one that needs a sweep.
