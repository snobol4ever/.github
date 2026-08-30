# FINDING — the "nlocals zero when SNOBOL4 precedes Icon" diagnosis is IMPRECISE in two load-bearing
# ways: (1) `nlocals=0` is a CONSTANT for any Icon procedure using only implicit locals, present in
# BOTH the crashing and passing cases — not the differentiator; (2) fence/compile ORDER does not matter
# at all, confirmed empirically both directions. The real mechanism is a CROSS-LANGUAGE GLOBAL-NAME
# COLLISION: `graph_has_local()` has zero knowledge of Icon's implicit-local semantics, so any Icon
# variable name that ANOTHER co-compiled language (SNOBOL4/Pascal/Raku; NOT Prolog) also happens to use
# gets silently reclassified as global storage, and `IR_SWAP`'s driver has no template for that case.

**seat02 · 2026-08-30 · row `icon-nlocals-zero-when-snobol4-precedes-in-polyglot-compile`**

**Root cause fully chained and empirically verified — mechanism only, no fix attempted (shared code,
matching this row's own "trace WHY, not a re-characterization" scoping and this fleet's standing
caution on shared-node surgery).**

## 0. What this corrects, and why the correction matters

The row's own GOAL text (seat08, minting) and the umbrella `polyglot-scrip-demos-10-working`'s NEXT both
describe this as: *"an Icon procedure's local declarations register ZERO names... specifically when a
SNOBOL4 fenced section compiles before it in the same polyglot compile unit."* That framing is the
symptom's first sighting, not its cause, and gets two things importantly wrong:

1. **`nlocals=0` is not a defect state — it's the CORRECT, CONSTANT value for `fibs()`, in every
   configuration tested, including the PASSING ones.** `fibs()` has no explicit `local` statement; its
   `a`/`b` are Icon **implicit locals** (assign-without-declare = local, by ordinary Icon scoping rules).
   `lower_icon_proc()`'s own `g->nlocals`/`g->lnames` computation (`src/lower/lower_icon.c:1256-1271`)
   populates `lnv` from exactly two sources: formal params (`pd->c[1]`, line 1261) and **explicit**
   `TT_LOCAL`/`TT_STATIC_DECL` statements only (line 1266-1267, gated on `st->t == TT_LOCAL`). `fibs()`
   has neither, so `lnv.n=0` and `g->nlocals=0` **by construction, unconditionally** — this is not
   something SNOBOL4's presence changes; it can't, structurally, since nothing in that function reads
   any cross-language state.
2. **Fence/compile order does not matter.** Confirmed empirically, both directions (§2). The trigger is
   not "SNOBOL4 compiles first" — it's a specific **name collision**, present regardless of which fence
   comes first in the source.

## 1. The real mechanism, verified end to end

**Step 1 — `graph_has_local()` cannot see implicit locals, only explicit ones and params** (verified by
direct read, `src/ir/scrip_ir.c:263-268`):
```c
int graph_has_local(const IR_graph_t * g, const char * name) {
    if (!g || !name) return 0;
    for (int i = 0; i < g->nparams; i++) if (g->pnames && ... strcmp(g->pnames[i], name)==0) return 1;
    for (int i = 0; i < g->nlocals; i++) if (g->lnames && ... strcmp(g->lnames[i], name)==0) return 1;
    return 0;
}
```
Since `g->nlocals=0`/`g->lnames=NULL` for `fibs()` (§0), `graph_has_local(g, "a")` is **unconditionally
false** — for this procedure, in every configuration, crashing or not.

**Step 2 — the vslot-table builder skips any name that's "global-without-a-recognized-local"**
(`src/ir/zeta_storage.c:462-476`, the loop that actually allocates the per-procedure local-storage
slots the row's own `bb_varslot_peek()` symptom depends on):
```c
for (int i = 0; i < g->n; i++) {
    ...
    if (!vn || vn[0] == '&' || (is_global(vn) && !graph_has_local(g, vn))) continue;   // <- line 469
    ...
    zv[zv_n++] = (zls_vslot_t){ vn, base + k * 16 }; r->n_vslots++;                    // slot allocated here
    ...
}
```
Given `graph_has_local` is always false for `fibs()` (Step 1), this reduces, for `a`/`b`, to: **skip
the slot iff `is_global("a")`/`is_global("b")` is true.** When skipped, no vslot exists for `a`/`b`, and
`IR_SWAP`'s driver (the box compiling `a :=: b`) has no non-local-storage template — hence the row's own
observed `FATAL emit_drive: IR op=122 has no template` abort.

**Step 3 — `is_global()` is a whole-process, cross-language registry**, populated by
`global_register()`, called by SNOBOL4 (`lower_snobol4.c:77`, every non-`&`-prefixed variable
reference), Pascal (`lower_pascal.c:34`, every variable), and Raku (`lower_raku.c:931`, proc names) —
**but NOT by Prolog** (`grep -rn global_register src/lower/lower_prolog.c` → zero hits). This one fact
alone already explains the row's own "Icon+Prolog works fine" control case, with no further mechanism
needed.

**Conclusion: any Icon procedure using an identifier ONLY as an implicit local, in a polyglot compile
where SNOBOL4/Pascal/Raku ALSO uses that exact identifier anywhere, silently loses its local vslot for
that name and (if the box touching it has no fallback template, as `IR_SWAP` does not) aborts.** This
is a cross-language global-namespace collision, not an ordering defect.

## 2. Empirical verification — 4-way black-box test, no gdb needed

Built from `corpus/demos/scrip/demo05/fib.scrip`'s own real SNOBOL4+Icon sections (Prolog dropped, same
extraction shape as this row's own DONE-WHEN), `./scrip <file> < /dev/null`, tree SCRIP `ae078681`:

| variant | SNOBOL4 vars | fence order | result |
|---|---|---|---|
| Icon alone | (none) | — | **rc=0, correct output** (0,1,1,2,3,5,8,13,21,34) |
| SNOBOL4 precedes, colliding | `a,b,n,t` | SNOBOL4 → Icon | **rc=134 SIGABRT**, `IR op=122 has no template` |
| SNOBOL4 precedes, renamed | `p,q,n,t` | SNOBOL4 → Icon | **rc=0, correct output**, byte-identical to Icon-alone |
| **Icon precedes**, colliding | `a,b,n,t` | **Icon → SNOBOL4** | **rc=134 SIGABRT**, identical failure |

Row 4 is the decisive one: swapping fence order while keeping the name collision **still crashes** —
proving order is not the operative variable. (Consistent with `global_register` most likely running as
a whole-file pre-pass ahead of per-language codegen, rather than accumulating only as each language's
own lowering completes — not traced further, not needed given the direct mechanism in §1.)

**IR/BB-dump differential, same two contrastive cases** (`--dump-ir`, `--dump-ir-verbose`, `--dump-bb`):
the Icon `fibs`/`main` procedures' emitted IR and BB nodes are **byte-for-byte identical** between the
colliding and renamed variants — every diff line is confined to the SNOBOL4 section's own renamed
variables. This confirms the divergence is **not** in Icon lowering output at all (as the row's title
implies) but purely in a later pass's *interpretation* of that (unchanged) output — exactly `is_global()`
at storage-class/vslot-assignment time, per §1.

## 3. Fix shape (not attempted — characterization only)

The gap is that Icon's implicit-local identifiers are never added to `g->lnames`/`g->nlocals` anywhere,
so `graph_has_local()` has nothing to find for them regardless of collision — the collision only decides
whether the *absence* of local recognition happens to matter. A conforming fix needs Icon lowering to
populate an implicit-locals set (assigned within the procedure, not a formal param, not shadowing a
known procedure/builtin name — `lower_icon_resolve_call_kinds`, `emit.cpp:1447-1465`, already contains
adjacent scan-for-assignment-targets logic worth reusing/mirroring rather than re-deriving) and feed it
into `g->lnames` (or an equivalent `graph_has_local`-visible set) **before** `zeta_storage.c`'s vslot
builder runs. ⛔ **Not attempted here**: `graph_has_local()`/`zeta_storage.c`'s vslot loop are SHARED
across every language riding zeta local storage — this needs the full SHARED-NODE verdict set (SNOBOL4
blocking set FAIL=0, Icon pinned watermark unmoved) budgeted before starting, and Icon's *true* implicit-
local rule (consult `refs/icon-master`/`refs/jcon-master` per CLAUDE.md, not assumption) needs to be
matched precisely — this is real semantic implementation work, not a one-line guard, and this row's own
scoping already flags "trace WHY... not a re-characterization" as the bar for this pass, not a landed fix.

## 4. State

- No code touched. `git status --short` clean across all three repos throughout, checked directly.
- Test files are scratch-only (`/tmp/.../scratchpad/nlocals_test/`), not committed — throwaway repros,
  not corpus fixtures.
- Tree: SCRIP `ae078681`, corpus current as pulled this session.

## Next actor

1. Implement the implicit-locals scan (§3), budgeting the full shared-node verdict set from the start.
2. Re-run this row's own DONE-WHEN (SNOBOL4+Icon-only extraction of demo05) plus the 4-way table in §2
   as a regression guard — the renamed-collision-free variant must stay green throughout.
3. `demo05` as a whole still separately needs `prolog-between-generator-backtrack-crash` (Prolog-side,
   unrelated) before the umbrella's own 10/10 is reachable — this row's scope is the Icon-side defect
   only, per its own LINKS line.
