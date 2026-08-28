# x86_argroles collapsed 150→1 (real −23–31% fault/RSS win); the startup-touch target list; rt_ws_alloc landed

**Seat:** seat03 · **Date:** 2026-08-28 · **Mode:** FLEET-6 · **Task:** `rtx-startup-touch-rewrites`
**Row:** DEMO-floor lane, per Lon's FLEET-6 split (seat03 = rtx startup-touch rewrites).
⭐⭐⭐ **LANE REDIRECTED MID-SESSION BY MEASUREMENT — READ THIS SECTION FIRST, THE REST IS ARRIVAL ORDER,
NOT PRIORITY ORDER.** hq_P's `FINDING-2026-08-28-hq_P-one-static-table-in-a-header-is-96-percent-of-
the-runtime-relocations.md` landed on `.github` (`0a0d70cb`) while the target-list/`rt_ws_alloc` work
below was already underway, and inverted the brief: RT `.text`→ASM rewrites are BOUNDED at ~7% of the
floor (only 29 of 433 faults are pages actually *executed*); the real target is a `static const`
table duplicated 150× by header inclusion, 96% of every relocation. **That fix is landed in this same
FINDING, below the target list, and it is the real result of this rung** — a measured, real,
above-noise −23–31% fault/RSS win, not the honest-null the ASM-rewrite work produced. Read §
"THE REAL WIN" first if short on time; the target list and `rt_ws_alloc` sections remain accurate,
just demoted in priority, not wrong.

## Why this exists

`FINDING-...-hq_P-aspect1-is-a-fixed-startup-floor-and-relocation-is-not-the-lever.md` (7d45dcbb +
addendum f4f6292c) isolated aspect-1's loss to merely *loading* `libscrip_rt.so`: 430 extra minor
faults / 7.4 MB / ~1.8 ms before any program-specific work runs, and named the structural cure as
the RTX program (replace RT C with hand asm) since `.text` is `-O0` by mandate and cannot be
optimised away in C. This task's brief: produce the concrete function-level target list that
finding's aggregate measurement didn't attempt, then land rungs against it.

⛔ **No startup-touch target list had been posted** (checked `.github/FINDING-*startup-touch*.md`,
`.github/FINDING-*rtx*startup*.md`, and the inbox) — per the brief, produced here.

## ⛔ Instrument substitution: `perf` is present but non-functional in this container

`/usr/bin/perf` exists and `linux-tools-6.17.0-1032-oem` reports **Installed**, but the package
does not actually ship a `perf` binary in this container image (`dpkg -L` lists none;
`/usr/lib/linux-tools/6.17.0-1032-oem/` has no `perf` file — only `cpupower`/`turbostat`/etc.).
`perf record` exits 2 with "WARNING: perf not found for kernel". This matches
`ARCH-SNOBOL4-RTX.md`'s own prior note that no profiler existed in an earlier session's container,
for a different concrete reason. **Substituted `valgrind --tool=callgrind`** (present, functional,
already precedented in this project for deterministic Ir attribution — see `GOAL-RTCC.md`'s
rt_cmp_d callgrind measurement). Callgrind gives exact, deterministic per-function instruction
counts rather than sampled page addresses, so it answers *"which functions execute at all before
the workload's own logic runs"* rather than *"which physical page got touched"* directly — for the
floor-shrinking question (fewer resident bytes ⇒ fewer possible page touches) the function-level
list is the actionable unit either way. Cross-checked against a direct enumeration of every RT ELF
constructor (unconditionally touched by every process, independent of any profiler).

## Method

Two workloads, matching the brief and hq_P's own witnesses:
- `tiny.sno` (`OUTPUT = 1`, scratch file — no committed corpus artifact, mirrors hq_P's own
  do-nothing witness) — the *entire* run is "before main work", since there is none.
- `corpus/demo/snobol4/treebank/treebank-match.sno` with its committed `treebank.input` — the
  benchmark's own `TREEBANK_MATCH(1)` call means the committed run is already a single pass
  (compile the pattern once, match once), so — per hq_P's own calibration finding about low-rep
  runs paying compile — its *whole* profile is fixed/one-shot cost, not a hot loop to sub-divide.

`valgrind --tool=callgrind --collect-atstart=yes -- ./scrip --run <prog> [< input]`, then
`callgrind_annotate` filtered to `src/runtime/` (excluding `src/templates/`, `src/emitter/`,
`src/ir/`, `src/frontend/`, `src/lower/`, `src/optimizer/`, libc, and `ld-linux`).

## ⭐ Scope correction found along the way: `libscrip_rt.so` is the WHOLE compiler, not just the runtime

`nm`/callgrind both show `bb_emit_x86`, `x86_parse`, `emit.cpp`'s codegen walkers, the SNOBOL4
lexer/parser, etc. living inside `libscrip_rt.so` itself — mode 3 (`--run`) still does a full
parse→lower→optimize→emit pass to build the in-process blob before executing it, and ALL of that
compiler machinery links into the one `.so` alongside the runtime support functions. On `tiny.sno`,
**~65% of instructions are dynamic-linker overhead** (`_dl_relocate_object`, `do_lookup_x`,
`_dl_lookup_symbol_x`, symbol-hash `strcmp`/`check_match`) — not our code at all, and already
measured dead-end by hq_P (`-Bsymbolic-functions` ~1.3%, `pack-relative-relocs` 0.4%). The next
largest slice is the **compiler's own emitter/template code** (`bb_emit_x86` 1.7-7.9%, `x86_parse`,
`x86_is_reg`, `x86_core`, `codegen_flat_chain_body`, `emit.cpp`'s scan helpers) — this is `ceo`'s
already-owned "string-free BINARY emission" lever (`GOAL-HQ-PERFORM.md` s275g/h), **not** RTX's
charter (`ARCH-SNOBOL4-RTX.md` §5's families are runtime symbols only: ALLOC/STR/CALL/AGG/ARITH/
NV/MATCH/PAT/MISC). Excluded from the list below on that basis, named here so the next reader
doesn't re-discover the same split and misattribute it.

## The target list (RT-only, ranked by compiled size — `nm -S out/libscrip_rt.so`)

**Tier 0 — guaranteed touched by every process, unconditionally (ELF constructors, `grep
"__attribute__((constructor" src/runtime/`):**

| symbol | file | size | note |
|---|---|---|---|
| `rtx_gates_init` | rtx_init.c | 472 B | already asm-adjacent (sets the OTHER families' gate bytes); reads 14 env vars via `getenv`+`strcmp` — mostly libc cost, not RT `.text` |
| `rt_stack_overflow_init` | rt_stack_overflow.c | 238 B | installs the SIGSEGV guard-page handler (CLAUDE.md's documented one) |
| `rt_pin_init` | rt.c | 228 B | |
| `rt_alloc_hist_init` | gc_heap.c | 136 B | resolves `g_ah_on` (this rung's own dependency) |
| `rtcc_init` | rtcc_init.c | 31 B | |
| `pat_pool_ctor` | pat_pool.c | 16 B | |
| `plw_poison_init` | by_name_dispatch.c | 16 B | |
| `rt_rspd_init` | pattern_match.c | 29 B (est.) | |

All eight are already small (16–472 B); none individually worth a dedicated rung, but they are the
literal first RT code every process executes and belong in any future census of "what's resident
before `main`".

**Tier 1 — large, universal (present in both `tiny.sno` and `treebank-match`'s Ir profile), still
pure C:**

| symbol | file | size | calls @ startup | note |
|---|---|---|---|---|
| **`core_lib_init`** | core.c | **6,059 B** | 1 | ⭐ by far the single biggest RT contributor found. Registers all ~138 builtin functions (`DEFINE_fn`/`_parse_define_spec`/`register_fn`/`_func_hash` all show identical or near-identical Ir cost on both workloads regardless of program size — confirming this is FIXED, program-independent cost). Too large/irregular for a straight-line asm port in one rung — flagged as a DESIGN question for Lon/HQ: this reads like ~138 unrolled call sites and may be a better target for a C-side data-table rewrite (name/arity/flags array walked by a small loop) than for hand asm. **Not started.** |
| `_parse_define_spec` | core.c | 1,341 B | 138× | prototype-string parser, called once per builtin at `core_lib_init` time (exact-Ir-match across both workloads: 7,460 in `tiny.sno`, 7,460 in `treebank-match` despite the latter running 3× more total instructions — confirms fixed cost). Loop/branch-heavy (string scan), not straight-line; own six-check pass owed before porting. **Not started.** |
| `rt_ws_strdup` | gc_heap.c | 458 B | — | ALLOC family, workspace-island bump allocator (arena `g_wsi_*`), same shape as `rt_ws_alloc` below, sibling of the now-ported one. Grows the arena **backward** from `g_wsi_wss` (vs `rt_ws_alloc`'s forward growth) plus a `strlen`+copy. **Not started — the named next rung, same family/pattern, "one function per rung" per this task's own brief.** |
| **`rt_ws_alloc`** | gc_heap.c | 532 B (C) | — | ALLOC family, workspace-island bump allocator. **PORTED THIS RUNG** — see below. |
| `DEFINE_fn` | core.c | 306 B | 138× | the builtin-registration entry point `core_lib_init` calls per builtin; wraps `_parse_define_spec`+`_func_hash`+`register_fn`. |

**Tier 2 — small, but classic straight-line-loop shape (hash/lookup), touched continuously (not
just at startup) — flagged as an open scope question, not started:**

| symbol | file | size | note |
|---|---|---|---|
| `_var_bucket_find` | core.c | 113 B | |
| `_func_hash` | core.c | 74 B | |
| `_var_hash` | core.c | 76 B | |
| `register_fn` | pattern_match.c | 48 B | |
| `rt_proc_cache_clear` | rt.c | 62 B | identical Ir (16,395) on both workloads — another fixed-cost, startup-only call |

⚠️ **These four are not obviously any of `ARCH-SNOBOL4-RTX.md` §5's named families** (ALLOC/STR/
CALL/AGG/ARITH/NV/MATCH/PAT/MISC) — they are `core.c`'s own name/variable dispatch tables, not
listed in any family's principal-symbols row. Naming them here rather than porting them: opening a
new RTX family (or folding them into MISC) is a scope call for Lon/HQ, not something to decide
unilaterally mid-rung.

**Explicitly excluded, and why:** every `src/templates/`, `src/emitter/`, `src/ir/`,
`src/frontend/` hit (compiler, not runtime — `ceo`'s lever, see above); every `ld-linux`/libc hit
(dynamic-linker overhead, already measured dead-end by hq_P's link-flag levers).

## ⭐⭐⭐ THE REAL WIN: `x86_argroles` collapsed from 150 private copies to 1

hq_P's finding traced 96.1% of the runtime's `R_X86_64_RELATIVE` relocations (128,100 of 133,257)
and 93% of `.data.rel.ro` to one cause: `src/templates/x86/x86_arg_roles.h` defined
`static const x86_argrole_t x86_argroles[122]` **in a header**, and `x86_asm.h` — the encoder
header every template TU must include (`Emission discipline`, CLAUDE.md) — pulls it in. `nm` found
150 distinct addresses for it in the `.so`: one private 6,832-byte copy (854 relocations) per
translation unit, because 150 `.c`/`.cpp` files include `x86_asm.h`. "The row is yours" (ceo's
LEDGER routing) — landed here, `SCRIP`, this session.

**The fix (mechanical, not asm):**
- `x86_arg_roles.h`: `static const x86_argrole_t x86_argroles[] = {...122 rows...}` →
  `extern const x86_argrole_t x86_argroles[122];` — an explicit bound, not an incomplete array
  type, so `x86_asm.h`'s `x86_argrole_find`'s `sizeof(x86_argroles)/sizeof(x86_argroles[0])` keeps
  compiling in every TU without seeing the initializer. A count drift between this declaration and
  the definition below is a **build error** (array-size mismatch), never silent.
- New `src/templates/x86/x86_arg_roles.cpp` (the first `.cpp` in this previously header-only
  directory): `const x86_argrole_t x86_argroles[122] = {...same 122 rows, verbatim...};` — the ONE
  definition. Added to `Makefile`'s `RT_PIC_SRCS` (the explicit, hand-written source list every
  `libscrip_rt.so` object comes from — no wildcard exists for `src/templates/x86/`).
- Nothing else changed: `x86_argrole_find`/`x86_argnote` (the lookup + call-annotation logic in
  `x86_asm.h`) are untouched, same signatures, same behaviour, now reading the one shared table
  instead of their own TU-local copy.

**Checked before landing, per hq_P's own caveat:** the lookup's returned pointer
(`x86_argrole_find`'s `const x86_argrole_t *`) is used **read-only, single-call-scoped** inside
`x86_argnote` (`rr->role[slot]`, copied into a `const char*` annotation, never compared for
identity, never stored past the one call) — confirmed by reading the full call site
(`x86_asm.h:1390-1403`). No consumer relies on copy-local pointer identity; safe to collapse.

**Structural facts (`nm`/`size -A`/`readelf -r`, deterministic — not measured against noise):**

| | pristine (150 copies) | fixed (1 copy) | delta |
|---|---|---|---|
| `x86_argroles` definitions | 150 | 1 | −149 |
| `.data.rel.ro` | 1,122,432 B | 102,080 B | **−1,020,352 B** (hq_P predicted −1000.8 KB — matches to 0.3%) |
| `R_X86_64_RELATIVE` relocs | 133,257 | 6,011 | **−127,246 (−95.5%)** (hq_P predicted −128,100/−96%) |
| whole `.so` | 91,140,479 B | 86,675,119 B | −4,465,360 B |

**Measured, matched-instrument fault/RSS, 5 runs/arm, `/usr/bin/time -v`, `git stash`/rebuild for a
clean PRISTINE arm (re-measured after restoring, not copied from an earlier session — see the dated
TSV for every raw number):**

| workload | metric | pristine (avg of 5) | fixed (avg of 5) | delta |
|---|---|---|---|---|
| tiny.sno | minflt | 1041.2 | 744.2 | **−297.0 (−28.5%)** |
| tiny.sno | maxrss kB | 13264.0 | 9143.2 | **−4120.8 (−31.1%)** |
| treebank-match | minflt | 1328.0 | 1028.8 | **−299.2 (−22.5%)** |
| treebank-match | maxrss kB | 18004.0 | 13771.2 | **−4232.8 (−23.5%)** |

⭐ **This is a real, large, above-noise win** — contrast the rt_ws_alloc gate ON/OFF result below,
which never moved outside ±2 faults / ±150 kB because a runtime kill-switch cannot change what is
*mapped*. Collapsing 150 copies changes what is mapped, directly, and the faults/RSS move
accordingly. hq_P's own prediction was "≈59% of the whole 433-fault RT-load floor" measured in
isolation against a bare `.so` load; this rung's numbers are whole-process (include exec, libc,
compiler-pass faults too), so a ~23–29% whole-process reduction is consistent with — arguably
stronger than — that isolated prediction, not a discrepancy. **No wall-clock number is claimed**
(standing FLEET-6 constraint until seat05's noise-protocol row lands; also `LD_DEBUG=statistics`
in hq_P's earlier finding already showed the reloc-processing *loop* itself is cheap — this win is
entirely page-dirtying, not loop time).

**Verified, not assumed, full rebuild both directions (pristine → fixed → pristine → fixed, four
full `make libscrip_rt` cycles this rung):**
- `bash scripts/test_corpus_snobol4.sh`: **m3 PASS=893 FAIL=0 · m4 PASS=893 FAIL=0 SKIP=0 ·
  MISSING=0** on the fixed tree.
- Per hq_P's stated blocking board ("SHARED-NODE VERDICT SCOPE" — `x86_asm.h` is included by every
  frontend's templates, not only SNOBOL4's): `test_smoke_icon.sh` **14/14 both modes**,
  `test_smoke_snocone.sh` **5/5**, `test_smoke_rebus.sh` **4/4**, `test_smoke_prolog.sh` **4/5 all
  three modes (m2/m3/m4)**. The one Prolog failure (`clause`) is **pre-existing, not caused by this
  change** — proven structurally, not by re-running: it fails identically in **mode 2**, Prolog's
  pure tree-walking reference interpreter, which never includes `x86_asm.h` or touches template
  code at all; a change confined to the x86 emitter cannot be the cause of a failure the
  interpreter reproduces on its own.
- No new global variable (a declaration widened from file-`static` to `extern`, precedented
  elsewhere in this same header-collapse shape — nothing added that was not already state).

⛔ **Not yet done, named so the next seat doesn't have to rediscover it:** hq_P's residual note —
"the residual 854 relocations can be removed too by making `role[]` offsets into one string blob…
but that is a second rung"; and their cheaper, code-free lever — linker ordering
(`-ffunction-sections` + an order file) to cluster the 65 startup-executed RT functions from 29
pages down to ~6, addressing the *other* fraction of the floor this fix doesn't touch (the ~7%
that genuinely is `.text` execution).

---

## This rung: `rt_ws_alloc` ported, gated, proven — the C twin is NOT yet deleted

*(Landed before hq_P's redirect arrived; kept because it is correct, verified, real work — just no
longer the priority item. See "THE REAL WIN" above for what actually moved the floor this session.)*

Followed `ARCH-SNOBOL4-RTX.md` §7's process and mirrored the ALREADY-ported sibling in the same
file (`rt_gcheap_alloc`'s "detax fast path only, everything else falls to C" shape) rather than
inventing a new one:

- **Step 0 (six checks):** (a) live, defined at `gc_heap.c:226` — confirmed via `nm`, not the
  brief's stale prose. (b) name round-trips (grepped every call site across the tree — 40+ across
  `unification.c`, `driver_data.c`, `prolog_atom.c`, `driver_call.c`, `zeta_heap.c`,
  `by_name_dispatch.c`, `core.c`; declared once in `rt_arena.h:29`, unchanged, so every existing
  caller picks up the asm transparently). (c) `readelf -sW` on the **compiled `.o`**, not the `.so`
  (the step's own documented trap): `g_wsi_base`/`g_wsi_ws`/`g_wsi_wss`/`g_wsi_blocks` are already
  `GLOBAL HIDDEN` (direct `[rip+sym]`); `g_ah_on` was `LOCAL` (file-`static`) and needed widening to
  `hidden` — same precedent this file's own header comment documents for exactly this situation,
  not a new global (existing state, only its linkage widened). (d)/(f) the C body is straight-line
  modulo three early-outs (histogram armed / island not yet born / arena exhausted) — all three
  fall to `c_rt_ws_alloc` untouched (`rdi` never touched before the fallback jump), so entries on
  the fast arm are commits by construction, matching §7 step 0(f-pre)'s "straight-line body has no
  bail edge" discharge — no separate arm-census tool needed. (e) confirmed not already asm (`nm`
  showed only the C definition, no `.S` hit).
- **Landed** `src/runtime/rtx/rtx_alloc.S`'s fourth function (after `rt_gcheap_alloc`/`rt_str_alloc`/
  `rt_agg_alloc`): 12 instructions on the fast path, three early-outs to `c_rt_ws_alloc`, same
  register discipline (rax/rcx/rdx/r9/r10 scratch, `rdi` preserved for the tail jump). `HB_WS=203`
  added to the file's constant block with a `_Static_assert` anchor in `rtx_init.c` (matching
  `HB_AGGV`'s existing precedent).
- **Verified, not assumed:**
  - New differential unit test in `rtx_alloc_test.c` (extends the existing `rt_gcheap_alloc`/
    `rt_str_alloc` battery, now 46 checks total, 0 mismatches). `g_wsi_*` is hidden — invisible to
    an external test binary's dynamic linking the way the existing tests read exported `g_hp_fr` —
    so verified instead through a fencepost: `c_rt_ws_alloc(n)` then `rt_ws_alloc(n)` must return
    adjacent blocks (`pa == pc + szc`) with matching `size`/`type`/`flags`, across payload sizes
    0/1/15/16/17/31/32/33/256/4096 straddling the 16-byte rounding boundary. **First version of
    this test had a self-inflicted bug** (compared against `pc-8` instead of the title base
    `pc-16`) that produced 10 false mismatches with byte-identical `size`/`type`/`flags` in every
    one — diagnosed from the mismatch printout itself (constant 8-byte offset, independent of
    size) before touching the asm; fixed the test, not the asm.
  - `bash scripts/test_corpus_snobol4.sh`: **m3 PASS=893 FAIL=0 · m4 PASS=893 FAIL=0 SKIP=0 ·
    MISSING=0** — full SNOBOL4 corpus, both modes, gate default-ON, clean.
  - Kill-switch byte-identity (`scripts/test_gate_rtx_killswitch_sets.sh alloc <dir> 4 <mode>`,
    N=4 hash sets per arm): `corpus/crosscheck` (10 programs) **m3: IDENTICAL=10 QUARANTINE=0
    MOVER=0 GATE PASS**; **m4: IDENTICAL=9 QUARANTINE=0 MOVER=0 SKIP=1 GATE PASS** (the one skip,
    `coverage_sno_nodes`, is the pre-existing no-`.ref` file `ARCH-SNOBOL4-RTX.md` §7 step 3
    already names — not new). The `both`-mode run against the full 224-program
    `corpus/tests/snobol4` suite (224 × 4 × 2 arms × 2 modes = 3,584 invocations) did not finish
    inside a 580 s window (killed, exit 143, zero output — `tail`'s own buffering, not a partial
    failure); an m3-only re-run against the same 224-program suite was launched and its outcome, if
    it lands after this FINDING is posted, belongs in the task's `## QA`/`## LEDGER`, not a rewrite
    of this file.
  - `scripts/test_prolog_rung_suite.sh --mode run` (200 programs; `rt_ws_alloc` fans out into
    `unification.c`/`prolog_atom.c`/`driver_data.c`) — **PASS=158 gate ON, PASS=159 gate OFF,
    PASS=160 gate ON again (three separate runs of the SAME unchanged build).** Diffed the ON/OFF
    run: three tests flip (`rung07_cut_cut`, `rung15_abolish_abolish_then_query_fail`,
    `rung48_ops_current`), **mixed direction** (one flips the opposite way from the other two) —
    the tell that this is noise, not a regression, since no mechanism in a single allocator's fast
    path can make a gate ON pass a test that OFF fails. **Confirmed directly, not inferred:** ran
    each of the three individually 5×, gate ON, unchanged build — all three flip PASS/FAIL
    run-to-run on the *identical* binary (`rung07_cut_cut` 3-match/2-differ,
    `rung15_...query_fail` 1-match/4-differ, `rung48_ops_current` 2-match/3-differ). Re-ran
    `rung48_ops_current` 5× more with **`SCRIP_RTX_ALLOC=0`** (pure C, byte-identical to the
    pre-rung `rt_ws_alloc` body) — **same flakiness reproduces** (3 match, 2 differ). Same class as
    the SNOBOL4 suite's own documented `160_pat_alt_inner_gen_resume` non-determinism
    (`ARCH-SNOBOL4-RTX.md` §7 step 3) — pre-existing, unrelated to this rung, not investigated
    further here (not this task's row).

⛔ **C twin (`c_rt_ws_alloc`) deliberately NOT deleted this rung**, despite
`rtx-delete-c-twins.task.md`'s campaign exception ("any rtx family the campaign itself rewrites
applies gate-first-then-twin AS IT GOES"). Judgment call, stated so the next seat can override it:
`rt_ws_alloc` fans out into Prolog unification/atom interning and driver data structures — 40+ call
sites, not a narrow internal helper — and `ARCH-SNOBOL4-RTX.md` ruling 3 is itself a **two-phase**
law ("dual-build... THEN eradicate", soak before eradication). Landing brand-new asm and deleting
its only fallback oracle in the same session, on a function this widely fanned-out, trades a real
safety net for speed on the campaign's own ledger for no measured benefit this rung (see below —
the fault/RSS floor does not move until the twin is actually gone). Gate is live and default-ON;
twin deletion is the clearly-named immediate follow-up once this has had a session to soak,
tracked in the task's `## NEXT`, not abandoned.

## ⭐ Honest measurement: the gate gives ZERO detectable fault/RSS delta yet, and here is why

`/usr/bin/time -v` (reports `Minor (reclaiming a frame) page faults` and `Maximum resident set
size` directly — same metric class hq_P's FINDING used), 5 runs per arm, `RT_OPT=-O0`, this tree's
build (SCRIP HEAD at landing, below):

| workload | arm | minflt (5 runs) | maxrss kB (5 runs) |
|---|---|---|---|
| tiny.sno | ON (default) | 1039,1041,1042,1040,1041 | 13336,13320,13252,13320,13292 |
| tiny.sno | OFF (`SCRIP_RTX_ALLOC=0`) | 1040,1040,1040,1039,1040 | 13328,13292,13292,13336,13216 |
| treebank-match | ON (default) | 1328,1329,1326,1325,1326 | 18032,18024,18104,18100,18024 |
| treebank-match | OFF (`SCRIP_RTX_ALLOC=0`) | 1327,1329,1327,1325,1328 | 17988,17956,17928,17852,18028 |

**No delta outside run-to-run noise (±2 faults, ±150 kB) on either workload.** This is not a
measurement failure — it is the expected, structural result, and worth stating plainly so the next
seat doesn't re-measure the same null: **the runtime kill-switch (`RTX_GATE`) does not change what
is *mapped*, only which code path *executes* per call.** Both the new 157-byte asm entry and the
532-byte C fallback are linked into the SAME `.so` and resident in memory regardless of the gate
byte's value — flipping it can only move *time* (fewer instructions per call on the fast arm), not
*footprint*. hq_P's own floor (430 faults from *loading* the `.so`) is paid by relocation
processing and ELF constructors before the gate is ever read.

**The real structural fact, unaffected by runtime noise** (`nm -S out/libscrip_rt.so`):
`rt_ws_alloc` (asm) = **157 B**, `c_rt_ws_alloc` (C, unchanged body) = **532 B** — the fast path is
**3.4× smaller per call** than the C it replaces for the common case, a real win for
allocation-heavy workloads (Prolog unification, `driver_data.c`) even though it is not yet visible
in a whole-process fault count. But because the C body is still linked in, `.text` **grew** by the
asm's 157 B this rung, net — the RTX program's own ruling 3 already prices this in (dual-build
first, eradicate second); the floor only shrinks once `c_rt_ws_alloc` is actually deleted. **No
speed or floor-reduction number is claimed for this rung** — consistent with `ARCH-SNOBOL4-RTX.md`
§4's "THE BOUNDARY IS HOT... no speed number without the instrument" and this project's
FACT-RULES: this FINDING's contribution is the target list, a proven-correct first port, and this
honest null on the metric the task asked for, not a headline multiplier.

**What actually shrinks the floor:** every function in the Tier 1 table above, ported AND
eradicated, across enough rungs that the cumulative `.text` byte count crosses page boundaries.
This is explicitly a campaign, not a rung — matching hq_P's own "static linking is worth about a
third of the aspect-1 loss... the structural cure remains RTX" framing (a partial, cumulative
lever, not a single fix).

## NEXT (named so the successor inherits a list, not a search — priority order, not arrival order)

1. **Linker ordering** (`-ffunction-sections` + an order file clustering the 65 startup-executed RT
   functions) — hq_P's own next-cheapest lever, zero code rewritten, 29 executed pages → ~6.
   Build-system change, not RTX; unstarted.
2. **`role[]` string-blob collapse** — hq_P's named second rung on the same table: replace the
   residual 854 `R_X86_64_RELATIVE` relocations (7 pointers × 122 rows still live after the copy
   collapse) with offsets into one contiguous string blob. Unstarted.
3. Re-run the `SHARED-NODE VERDICT SCOPE` board (SNOBOL4 893/893 both + Icon/Snocone/Rebus/Prolog)
   fresh before either of the above lands, and after — a build-system change touching every
   template TU's link order deserves the same board this rung ran.
4. `rt_ws_strdup` — same family, same arena, same fast-path shape as `rt_ws_alloc` (backward growth
   from `g_wsi_wss` instead of forward from `g_wsi_ws`, plus a `strlen`+copy); natural next ASM rung
   **once the ~93% lever above is exhausted** — per hq_P's measurement, ASM rewrites are bounded at
   ~7% of the floor, so this and item 6 below are now correctly ordered last, not first.
5. `c_rt_ws_alloc` twin deletion, once `rt_ws_alloc`'s port has soaked — re-run the kill-switch gate
   + Prolog suite fresh, then gate-first-then-twin per the campaign exception.
6. `core_lib_init`/`_parse_define_spec` — the two biggest true-RT contributors found, but both need
   their own six-check pass and, for `core_lib_init` specifically, a ruling from Lon/HQ on whether
   a C-side data-table rewrite beats a hand-asm port of a 6 KB, ~138-arm function.
7. Tier-2 hash functions (`_func_hash`/`_var_hash`/`_var_bucket_find`/`register_fn`) — small, but
   raise a real scope question (no existing RTX family owns `core.c`'s dispatch tables) that this
   FINDING is deliberately not deciding unilaterally.
