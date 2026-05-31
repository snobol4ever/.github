# HANDOFF 2026-05-31 SONNET — DESCR8 MACRO FUNNEL (exploratory branch)

**Author:** Claude Sonnet · **Director:** Lon · **Branch:** `descr8-macro-funnel` (SCRIP repo)
**Status:** exploration, NOT an active PLAN goal. Branch isolates this from the three
muskeeters (Icon/Prolog/SNOBOL4 BB tracks). PLAN.md goals table UNTOUCHED.

---

## Premise

Lon wants a CLI switch selecting an **8-byte DESCR** (today 16 bytes) for a
"screaming" 32-bit-based representation, with **RBP** as the durable basing
register for all 32-bit pointer arithmetic (same offset math in 32- and
64-bit mode). All DESCR access is to be encapsulated so the layout can flip
behind one header.

## DESCR today (16 bytes) — `src/include/descr.h`

```c
typedef struct DESCR_t {
    DTYPE_t v;       /* off 0, 4B tag (enum, max value DT_DATA=100 — fits a byte) */
    uint32_t slen;   /* off 4, 4B string length / cset sentinel 0xFFFFFFFF       */
    union { char*s; int64_t i; double r; void*ptr; _PATND_t*p;
            _ARBLK_t*arr; _TBBLK_t*tbl; _DATINST_t*u; }; /* off 8, 8B payload */
} DESCR_t;
```

## Proposed 8-byte layout (both modes, identical bit layout)

```
byte 0   : v (tag, uint8, addressable)
byte 1-3 : slen (24-bit)
byte 4-7 : payload — 32-bit RBP-relative offset (ptr) OR int32 immediate
```
- Pointers → `RBP + off` (one arena based at RBP; 4B offset reaches 4GB).
- 64-bit mode: full int64/double must BOX into the arena; small-int fast path
  in the 32-bit immediate. 32-bit mode: int32 fits inline for free.
- **Use explicit-width members at fixed byte offsets, NOT C bit-fields.**
  Reason: the x86 emitter is a SECOND consumer of the layout and needs known
  byte offsets it can hardcode; bit-field packing is implementation-defined,
  bit-fields aren't addressable (`&d.payload` fails — and code does
  `*(DESCR_t*)d.ptr`), and bit-field access is mask+shift (slower, not
  "screaming"). Explicit layout gives single-`mov` access + known offsets.

## Register choice: RBP, not RBX (per ratified GOAL-ICON-BB layout)

- RBX = "NV/globals base" — already claimed, all langs. Overloading it would
  collide in pattern-match inner loops.
- RBP = "RESERVED, the sixth durable register, claimed ONLY if needed, NEVER
  for value flow." Basing = a basing role, not value flow. Claimed by NOT
  emitting a frame-pointer prologue (NOT by `-fomit-frame-pointer`).
- So RBP is the architecturally-sanctioned choice. Matches Lon's instinct.

---

## THE THREE-LAYER MODEL (key insight — makes DESCR8 tractable)

DESCR layout is encoded in THREE places; each needs its own funnel:

1. **C runtime** — raw `d.slen`/`d.ptr`/`d.tbl`/... field access.
   → Funnel through `GET_*` / `SET_*` macros. **Path A, IN PROGRESS.**
2. **Emitted x86 that passes SCALARS to `rt_*` helpers** (the `k0/i0/s0` =
   tag/int/string triples, e.g. `rt_pl_arith_cmp(op,k0,i0,s0,...)`).
   → LAYOUT-AGNOSTIC. The runtime (C, layer 1) reassembles descriptors.
   **ZERO variance. Nothing to do.** This is the MAJORITY of templates.
3. **Emitted x86 that BUILDS/STORES a descriptor INLINE** — hardcodes field
   offsets `+4`(slen)/`+8`(payload) and stride `add reg,16` as RAW BYTES.
   → **THIS is the variance Lon flagged.** ~6 sites, 7 files:
   `bb_upto.cpp` (`mov dword[r12+4],1; mov [r12+8],rax; add r12,16` =
   `\x41\xC7\x44\x24\x04`.. / `\x49\x83\xC4\x10`), `bb_iterate.cpp`
   (`[r12+4]`,`[r12+8]`), `bb_choice`, `bb_catch`, `bb_unify`,
   `bb_pat_break`, `bb_builtin`. NOTE: several of these are SM-value-stack
   pushes (`add r12,16`) that the ratified Icon layout DELETES anyway
   ("There is NO value stack ... not r12-as-TOS"), so the live count shrinks.
   The 55 `add rsp,16`/`[rsp+N]` hits are C-ABI alignment — UNRELATED to DESCR.

**Emitter-side cure (layer 3):** stop hand-writing `+4`/`+8`/`16` as magic
literals; emit them from NAMED layout constants. These belong on the
**`g_emit` (`sm_emit_t`) context** reached via the template `_.` convention
(e.g. `_.descr_off_slen`, `_.descr_off_payload`, `_.descr_stride`), same
idiom as `_.lbl_α`, `_.bb_ls`. Flip layout → update constants → emitter
regenerates correct bytes. This is the emitter-side mirror of Path A.

**Basing (RBP) is ORTHOGONAL to offset variance:** `base+off` only changes how
a *pointer payload* is dereferenced, not the descriptor's own field offsets.
Layer 2 untouched entirely. Only the pointer-payload SUBSET of the ~6 layer-3
sites needs the `RBP+` add — most store ints/cursors, not pointers.

---

## PATH A PROGRESS (C funnel)

**Accessor macros added to `src/include/descr.h`** (placed there, not
sil_macros.h, so they're in scope wherever DESCR_t is — descr.h is pulled via
core.h everywhere). All expand to the IDENTICAL 16-byte field access →
build is byte-for-byte behavior-identical.

```
GET_V/SET_V  GET_SLEN/SET_SLEN  GET_I/SET_I  GET_R/SET_R  GET_S/SET_S
GET_PTR/SET_PTR  GET_P/SET_P  GET_ARR/SET_ARR  GET_TBL/SET_TBL  GET_U/SET_U
CSET_SENTINEL  IS_CSET  MK_CSET_SLEN
MK_DATA(ptr)  MK_TBL(tbl)  MK_ARR(arr)   /* for field-by-field builds */
```
Naming per Lon: `GET_`/`SET_` with underscore; `IS_` keeps no underscore.

**Inventory (scanner `scripts/descr8_scan.py`, full list
`/tmp/desc8/sites_unique.json`):** 318 DESCR-UNIQUE field accesses
(slen/ptr/arr/tbl/u/p — near-zero false positive) outside the macro layer:
READ=188, WRITE=53, SENTINEL=77, across 25 files. Concentrated:
gen_runtime.c 68, core.c 54, pattern.c 51, bb_exec.c 33 (=65% in 4 files);
long tail 1-16 each. (Tag reads `d.v==DT_X` are a separate lower-risk tranche;
most already go through `IS_*`.)

**Converted + committed (commit `f433672`):**
- `src/runtime/interp/script_builtins.c` (`.u` reads → GET_U/GET_V)
- `src/runtime/interp/script_builtins_byname.c` (meth_call `.u`/`.v`)

**Build green; smokes byte-match baseline** (`/tmp/desc8/BASELINE.txt`):
snobol4 smoke PASS=3/13, icon smoke m2 5/6 (HARD), m3 0/6. These pre-existing
non-greens are baseline — contract is NO REGRESSION vs baseline, not all-green.

**Build note:** needs `libgc-dev` (`apt-get install -y libgc-dev`); build via
`make -j4 scrip` from SCRIP root.

---

## CRITICAL LESSON: do NOT auto-rewrite with regex

`scripts/descr8_rewrite.py` exists but is UNSAFE to run blind — the scanner
flags FALSE POSITIVES that a regex rewriter would corrupt:
`ctx.p` (parser context, snocone_parse.tab.c), `tbl[i].p` (builtin table,
prolog_builtin.c). The `.p`/`.s`/`.i`/`.v` fields collide with non-DESCR
structs. **Convert by hand-verified edits, per cluster, confirming the
receiver is genuinely a DESCR_t.** Rebuild + re-smoke + commit per file.

---

## NEXT STEPS (resume here)

1. Continue Path A C funnel, largest files first: `core.c` (54),
   `pattern.c` (51), `gen_runtime.c` (68), `bb_exec.c` (33), then tail.
   Per file: view real context → convert only confirmed-DESCR sites →
   `make scrip` → snobol4+icon smokes match baseline → commit.
   - Compound builds (`DESCR_t d; d.v=..;d.slen=0;d.tbl=nt;`) → `MK_TBL`/
     `MK_DATA` etc. Designated-init literals `{.v=..,.slen=..,.s=..}` are
     already the STRVAL/BSTRVAL constructor pattern — route to those.
   - Sentinels: `slen==0xFFFFFFFF` → `IS_CSET`; `slen==1`/`==0` name
     discriminators already have `IS_NAMEPTR`/`IS_NAMEVAL` in sil_macros.h.
2. Tag-read tranche (`d.v==DT_X`) — convert raw ones to `IS_*`/`GET_V`.
3. GATE for "C funnel complete": grep proves ZERO raw DESCR field access
   outside descr.h/sil_macros.h.
4. THEN emitter-side funnel (layer 3): add `descr_off_*`/`descr_stride` to
   `sm_emit_t g_emit`; replace the ~6 inline-build sites' magic bytes.
5. ONLY THEN attempt the 8-byte struct + RBP basing behind a CLI flag.
   **Gating decision still open: GC.** Boehm (`gc/gc.h`) is conservative — an
   arena object reachable ONLY via a 32-bit offset (no real pointer anywhere)
   may be collected. Arena-as-single-root or non-GC arena needed. This gates
   the whole 8-byte switch and must be decided before step 5.

## GC GATE — RESOLVED DIRECTION (Lon + Sonnet, 2026-05-31)

Three options were weighed (see issue-3 analysis):
- **A — arena as a single Boehm GC root.** `GC_malloc` one big block, pin it
  as a permanent root; Boehm keeps the whole arena alive as one unit; you
  sub-allocate inside. Still uses Boehm for everything outside the arena.
- **B — per-object Boehm with a custom mark proc that decodes `RBP+off`.**
  REJECTED. Taxes the GC hot path (defeats the "scream" goal), adds a THIRD
  lockstep layout consumer (struct + emitter + mark proc) in the least-
  testable place (only runs under collection pressure), and is in
  architectural TENSION with the contiguous arena the offset scheme needs
  (offsets presuppose one base; per-object Boehm objects are scattered).
- **C — non-GC arena.** `mmap`-reserved region Boehm never scans; allocate by
  bump-pointer; reclaim in BULK by resetting the pointer (NOT per-object
  malloc/free). Matches the box engine's existing region discipline
  (REGISTER-LAYOUT.md: "the save IS the allocation; the restore IS the
  unlink"). Long-lived values need a promotion path (generational split:
  ephemeral match arena that resets at match/stmt boundary + a long-lived
  value arena, or promote survivors to Boehm).

**DECISION: A to prototype, C as the end state.**
- A is the PROVING RUNG: fastest to stand up, proves the full chain (macro
  funnel + 8-byte struct + emitter offset constants + RBP basing) on real
  programs while the cost of being wrong is low; keeps Boehm as a safety net
  so the long-lived-value problem and the layout problem aren't solved at once;
  reversible and gate-able with the existing "smokes match baseline" discipline.
- A's KNOWN LIMIT (Lon spotted it): once the base is pinned, the arena can't
  grow — 32-bit offsets can't survive the base address moving (realloc-moves-
  base ⇒ every descriptor becomes a wild pointer). So A is NOT the permanent
  end state.
- GROWTH = graduate to C: `mmap`-RESERVE a large virtual range up front (up to
  the 4GB the 32-bit offset addresses) so the BASE NEVER MOVES, COMMIT pages
  lazily as touched. Stable base + growth without moving. (Pure-Boehm A can't
  do lazy-reserve cleanly; the growable version of A IS C.) Alternative if
  4GB/one-base is limiting: segmented arena (`{segment:offset}`, SIL-heritage).
- Growth is mostly moot for the MATCH arena anyway — it RESETS per match
  (bounded by nesting depth); only the long-lived value arena grows, slowly.

This decision resolves the step-5 gate: build A first (prototype/proof),
plan the mmap-reserve-stable-base C migration for real growth. B is off the
table.

## Files created this session
- `src/include/descr.h` — accessor block added (committed)
- `scripts/descr8_scan.py` — site inventory scanner (committed)
- `scripts/descr8_rewrite.py` — UNSAFE auto-rewriter, kept for reference only
- `/tmp/desc8/` — BASELINE.txt, sites_unique.json, emit_offset_files.txt
  (NOT committed — regenerate scanner output with `python3 scripts/descr8_scan.py`)
