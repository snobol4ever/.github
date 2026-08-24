# ARCH-BUILD-SYSTEM-DRAFT — the build system for the scrip executable

**Author:** hq_P (HQ-PERFORMANCE) · **Session:** 2026-08-23 s268 · **Brief:** ceo `src-reorg-build-design`
**Evidence:** every number here is measured in `FINDING-2026-08-23-hq_P-so-boundary-runtime-is-2.2MB-of-34.3MB.md`. Read that first; this file is the design, not the proof.
**Status:** ⛔ **DRAFT. Nothing moves before Lon rules.** CEO arbitrates this against hq_C's source-layout draft into one proposal.
**Binding through all of it:** per-checkout objdir (HQ-27) · flag-keyed `RT_TAG` cache · `RT_OPT` is `-O0`, no `-O2` arm ever (RULES.md § NO `-O2` BUILDS) · gates green through every step · m3 ≡ m4 · TEMPLATE-ONLY EMISSION · BOTH-MEDIUM · no-lang-past-lower.

---

## 1. The `.so` boundary

### What is actually true today

One library, `libscrip_rt.so`, holds all 262 built objects at `-fPIC`: parser, lower, optimizer, emitter, all 131 templates, contracts, driver, and the runtime. `./scrip` is `driver/scrip.c` alone, linked against it. **Every emitted mode-4 binary therefore links the entire compiler** — 34.3 MB to reach 2.2 MB of runtime.

The tempting framing is "the build ships junk". It does not. It ships a language whose runtime can compile: `EVAL()`, `CODE()`, and runtime-argument `LEN()`/`BREAK()` all call back into the emitter at run time. That coupling is real and no file-list edit removes it.

### The design

⭐ **The insight is directional.** The compiler leans on the runtime across **896** object-pair edges — correct, and it should. The runtime leans back across only **50**, and after relocating the code that is merely *filed* in the wrong directory, **30**, of which the genuine compile-at-runtime seam is **three objects with one purpose**. Fifty was never a wall. It is a door with a name on it.

**Two libraries, one dependency direction, one registration seam:**

```
libscrip_rt.so   runtime only        ~2.2 MB    linked by every emitted m4 binary
libscrip_cc.so   compiler            ~32 MB     depends on libscrip_rt; linked by ./scrip
```

The three back-edges invert into a vtable **owned by the runtime and populated by the compiler**:

```c
/* runtime/rt/rt_compile_hooks.h — the runtime declares what it may ask a compiler for */
typedef struct { void *(*pat_jit)(const void *tree, int64_t *zsz, int32_t *zstatic);
                 int   (*eval_source)(const char *src, DESCR_t *out);
                 void *(*parse_pattern)(const char *src); } rt_compile_hooks_t;
```

`libscrip_cc` registers its implementations at load; `libscrip_rt` calls through the struct. When the pointers are null — a program linked against the small library only — `EVAL()`/`CODE()`/dynamic patterns raise a clean, named runtime error instead of failing to link. ⛔ **This does not add a global.** It is one already-required piece of runtime state; if the reviewer reads it as a new global, it needs Lon's in-chat banner grant and does not ship until it has one.

⭐ **Mode 3 is unaffected and must stay that way.** `--run` compiles in-process by definition, so `./scrip` links both libraries and nothing about the m3 path changes. The split is a property of *what emitted programs carry*, never of what the driver can do. **m3 ≡ m4 output stays the invariant it is** — the split changes linkage, not codegen, and any step that perturbs emitted bytes is wrong by construction.

### Honest accounting of the win

18 of 553 corpus programs (**3.3%**) use `EVAL`/`CODE`. That is a **ceiling on eligibility, not a delivered 15.6x**: runtime-argument patterns reach the same machinery, and `$` indirect reference plus by-name dispatch force any compile-time predicate to be conservative. ⚠ The deliverable is that the runtime becomes small and *nameable*; the per-program saving is whatever a real conservative analysis yields, and that analysis has not been written. **Do not put a 15.6x in an announcement.** Link time is likewise not a selling point — the full link is 0.39 s.

### Sequencing

The Class-M relocations (`fh_*` file handles, `dat_*` DATA registry, `cset_*`, the Prolog Term/atom/unify/builtin family, `re.c`'s NFA, the RX slab) are worth doing **on their own merits and first**, because each one deletes back-edges without any library split at all. They are also exactly the entries already sitting in the `test_gate_runtime_isolation.sh` allowlist, each annotated with an owning relocation goal, in a gate declared a ratchet that may shrink and must never grow. ⭐ **Score the reorg by allowlist entries removed.** If the split is later judged not worth it, the relocations remain correct.

---

## 2. Source-list model

### Order is law: carve, then wildcard

The hand-maintained `RT_PIC_SRCS` does **not** rot in the missing-file direction — a deleted file breaks the build loudly. It rots in the other direction: **27 sources sit on disk unbuilt**, unnoticed, some uncompilable.

⛔ **A wildcard switch today does not link.** Of the 27 strays, 21 compile and 6 do not; adding the 21 to the link produces **16 duplicate `main` definitions** plus three `rtx_str_shim` symbol collisions. Wildcards are a *reward* for the attic carve, never a substitute:

1. **Carve first.** Test scaffolding → `src/**/t/`, built into executables by their own rule, never into the `.so`. Dead files → deleted (hq_C verifies each DEAD claim before anything is removed). Tools → built or deleted with their flag.
2. **Then per-directory wildcards** over the carved tree, with `src/**/t/` and any `attic/` excluded *by construction* — an exclusion expressed as a pattern, not as a hand-maintained skip list, or the rot simply moves.
3. **A census gate** that fails when a source is on disk, outside `t/`/`attic/`, and not in the build. That is what makes wildcards safe to keep, and it is the check whose absence produced the 27.

### The objdir must mirror the tree — this is a precondition, not a polish item

`RT_PIC_OBJS` flattens through `$(notdir)`. Two same-basename sources in different directories collapse to one object path, and the failure is **silent**: reproduced minimally, `b/rt.c` was never compiled, `make` **exited 0**, and its symbol was simply absent. Today there are **0 duplicate basenames across all 292 on-disk sources** — survival by accident, with zero headroom. Survey 12's own recommended `rtx/sn4/`, `rtx/icn/`, `rtx/pl/` split creates collisions on contact.

⛔ **So the objdir mirrors the source tree before any file moves.** This is the HQ-27 silent-wrong-build class through a third door, and the reorg is precisely the event that opens it. `-MMD -MP` dependency tracking and the `-include $(shell find ...)` line carry over unchanged; `vpath` disappears with the flattening, which is a simplification, not a loss.

### What is preserved, and one thing that changed underneath it

**Preserved as law:** the per-checkout objdir (`OBJ ?= /tmp/si_objs$(subst /,-,$(ROOT))`) and the flag-keyed `RT_TAG`/`RT_OBJDIR`/`RT_SO` cache with its `FORCE`-refreshed canonical symlink. Both exist to make ABI mixing and silent-wrong-build *structurally impossible*, and both keep that job in any new layout.

⭐ **Worth stating plainly: `RT_TAG` now has one live value.** It hashes `RT_OPT|ZCFLAGS`; `ZCFLAGS` is empty in every normal build, and `-O2` is banned outright (s262). The mechanism was built at s258 to make `-O0`↔`-O2` switching cheap and that motivation is gone. **Keep it anyway** — it is cheap, it is law, and it is the structural guard against the exact "flags changed, objects didn't" failure that made `pristine` feel mandatory. Just do not describe it as a performance feature any more.

### Makefile defects to fix in the same motion

- **`RT_OPT` is defined twice** (`:34` and `:361`), and **both carry the retired `O0-DEV-O2-BENCH` text** promising an `-O2` benchmark arm. Collapse to one definition; the comment states RULES.md § NO `-O2` BUILDS.
- **`make setup` runs `$(ROOT)/setup.sh`, which does not exist** — `Error 127`. CLAUDE.md documents it as *the* fresh-environment path. Point it at `scripts/install_system_packages.sh`, which works.
- **Makefile:20 omits `bison`** from the documented prerequisites while five frontends ship bison-generated parsers.
- **`out/rt_pic`, unkeyed, 116 MB, survives `make pristine`** — `pristine` can only reach the current tag's directory. Pre-s258 residue; `clean`/`pristine-all` should sweep any `out/rt_pic*` that is not a live tag.
- **`run-jvm` / `run-net` (`:494`, `:512`) invoke `scrip -jvm` / `-net`, flags that do not exist** — they fail with `cannot open '-jvm'`. Delete with the `JASMIN` plumbing when `backends/` moves out (survey 11).

---

## 3. `make test` / `test-ir` / `test-all`

All three are named in `.PHONY` (`:51`) with no recipe anywhere. Measured: each **exits 0** with `Nothing to be done`. A build target that reports success having run nothing is the same false-green class this project already legislates against everywhere else, and it sits under the most obvious name a newcomer will type.

- **`make test` → wire to the real blocking set**: `test_corpus_snobol4.sh`, `test_gate_emit_no_lang.sh`, `test_gate_template_medium_invisible.sh`. Non-zero on any failure. ⛔ Per SNOBOL4-FIRST it must **not** invoke the Icon/Prolog/Snocone/Rebus smokes.
- **`make test-ir`, `make test-all` → delete.** Neither has a defensible meaning; a name that must be explained away is worse than no name.
- Fix the stale header (`:7`) that documents `make test` as "run corpus (mode-4 gate)" — it has not done that for as long as it has had no recipe.

---

## 4. Generated-parser policy

Five frontends commit bison/flex output. ⛔ **`bison` and `flex` are not installed in this root**, so the committed generated files are **load-bearing build inputs here, not conveniences** — and the snocone `.tab.c`-is-stale claim **could not be verified in this seat**. It is carried forward unverified, not repeated as fact.

- **Keep generated output committed.** With the tools absent, this is what makes the tree buildable at all. Reversing it would make `bison` a hard prerequisite on every machine.
- **Add a sync gate** that regenerates into a temp dir and diffs. It requires the tools, so it must **SKIP loudly and visibly** where they are missing and never silently pass — a gate that cannot run must say so, or it is another false green.
- **`make setup` must install `bison`** (see §2) so the gate can actually run somewhere.
- **Delete the dead divergent regen path** — `parser/snobol4/Makefile` plus `scripts/build_snobol4_frontend.sh`, which nothing calls (survey 01). One regen path: `scripts/regenerate_parser_and_lexer_from_sources.sh`.
- **Rename `lex.rebus.c` → `rebus.lex.c`**, matching the other four (regen script `:59`, Makefile `:336`).

---

## 5. Switch collapse — the build side is nearly free

⭐ **The finding here is a negative one, and it is good news: collapsing to one ZETA mode barely touches the Makefile.** The build's compile-time `-D` surface is only `-DDYN_ENGINE_LINKED`, `-DIR_DEFINE_NAMES`, `ZCFLAGS` (empty by default), and `-DWITH_CSNOBOL4=1` for `scrip-monitor`. ZETA configuration is **not** selected by `-D`: it is a compile-time default in `src/contracts/zeta_choices.h` overridden by a **runtime** CLI flag.

So the collapse lands almost entirely in `zeta_choices.h` and the ~200 `ZC_*` preprocessor sites (`ZC_FRAME_RSP` 49, `ZC_LIT_GUTS` 26, `ZC_PORT_FORTH` 24, `ZC_PORT_HEAP` 15, …) — source work, not build work, and it belongs to whoever owns the collapse, not to this file.

Build side, when it lands: `ZCFLAGS` becomes dead and drops out; `RT_TAG` reduces to `md5(RT_OPT)`. **Keep `RT_TAG`** (§2). One caution — mode-4 *bakes* a `rt_zeta_set_mode` call into the emitted preamble only when a flag overrides the compiled default, so **collapsing the default silently changes emitted bytes for any arm that previously overrode it.** That interacts directly with m3 ≡ m4 and with every pinned `.s` artifact, so the collapse must be staged against a regenerated `.s` sweep, not dropped in.

---

## 6. The scripts sweep

Measured over all 506 files in `scripts/`: **168 reference `src/` paths**, 50 reference `backends/`, 122 distinct `src/` paths are named, **52 do not exist.**

⭐ **The fossils are stratigraphy: `src/runtime/x86/*` (18 paths) is the deleted mode-1/2 emitter, `src/backend/*`, `src/processor/*`, `src/include/{IR,SM,BB}.h` are older layouts still. Every prior reorg left a layer because none of them swept.** Without a sweep this one deposits stratum four.

**Corrections that change how urgent this is** — all three verified, and two of them defuse alarms:
- The two **mandatory handoff-regen scripts** carry their fossil paths **in header comments only**. Documentation rot, no live logic. The recorded `.s` drift has some other cause and hunting it here is a dead end.
- **`test_gate_rtcc_noclob_injection.sh` carries no fossils at all** — it *synthesizes* those files under `$TMP` as fixtures. Any grep-based detector, mine included, false-positives on it, and the sweep's allowlist must cover this class or the gate will be "fixed" into meaninglessness.
- **`test_gate_bb_one_box.sh` genuinely carries `bb_alt.cpp` + 4 deleted templates in a live file list** and needs re-proof that it can still fail.

**Plan, keyed to hq_C's layout draft:**
1. Emit `old → new` as a machine-readable path map — the layout draft is the single source, applied mechanically, never by hand-editing 168 scripts.
2. Rewrite in one commit per script family (`test_gate_*`, `util_*`, `board_*`/`bench_*`), each family re-proven green before the next.
3. ⛔ **Re-prove every touched gate can still FAIL** — introduce the violation, watch it go red, revert. A gate whose file list silently lost five entries is a gate that passes for the wrong reason, and this reorg edits the file lists of gates wholesale.
4. **Add `test_gate_no_fossil_src_paths.sh`**: fail when a script names a nonexistent `src/` path, with an explicit allowlist for synthesized fixtures (§ the `rtx_noclob` class). ⭐ **This is the piece that makes this the last reorg needing a sweep**, and it is worth more than the rewrite itself.
5. The ~50 `backends/` references move with the tree or die with it (survey 11).

---

## 7. Order of operations

Each step is independently green, independently revertable, and valuable even if the next is never taken.

| # | step | why it is first |
|---|---|---|
| 0 | Makefile hygiene: single `RT_OPT`, fix `make setup`, add `bison` to prereqs, sweep orphan `out/rt_pic*`, wire `make test`, delete `test-ir`/`test-all` | touches no source file; removes two false-greens and a broken first command |
| 1 | `test_gate_no_fossil_src_paths.sh` + re-prove the fossil-carrying gates can fail | the net must exist **before** the moves, or the moves are unmeasurable |
| 2 | objdir mirrors the tree | ⛔ precondition — after this, a basename collision is loud instead of silent |
| 3 | attic carve (test scaffolding → `t/`, dead files deleted on hq_C's verification) | must precede wildcards; **21 of 27 strays would otherwise be linked and 16 of them define `main`** |
| 4 | per-directory wildcards + census gate | now safe, and now self-maintaining |
| 5 | Class-M relocations, scored by isolation-allowlist entries removed | deletes back-edges; correct even if step 6 never happens |
| 6 | `libscrip_rt` / `libscrip_cc` split behind the registration vtable | the only step needing a NO-NEW-GLOBALS ruling |
| 7 | `backends/` out of `src/`; delete `run-jvm`/`run-net` + `JASMIN` | independent of all the above; announcement-relevant |

⛔ **Steps 5–7 change what ships. None of them start before Lon rules.**

## 8. Open questions for CEO/Lon

1. **Does the registration vtable count as a new global?** If yes it needs an in-chat banner grant naming it, and step 6 does not start without one.
2. **Is the `.so` split worth doing at all** given that the honest win is "the runtime is small and nameable" rather than a quotable multiple? Steps 0–5 stand on their own regardless; step 6 is the one that needs the ruling.
3. **`SM.h`/`SM_op_t`** — vocabulary of a deleted mode kept alive through `stage2.h` across 19 includers (survey 09). Retire the name in this reorg, or record a note-of-intent and leave it?
4. **Announcement wording.** ⛔ The measured facts do not support a link-time or a per-binary-size claim yet. The defensible sentence is about *structure* — one dependency direction, a runtime that stands alone — not about a number.
