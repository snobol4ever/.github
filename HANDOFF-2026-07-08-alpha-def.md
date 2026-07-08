# HANDOFF — α-DEF UNIFICATION (ONE-WAY-OUTPUT FIX) — 2026-07-08 02:32 UTC

**Status: BUILD IS CURRENTLY BROKEN. Do not merge/commit as-is. Root cause is
identified and the fix is scoped below, but not yet applied.**

## What Lon asked for, in sequence

1. Get BB-OWNED-ζ moving with "a new Zeta Local Storage technique."
2. While investigating the α self-load hook design (§5h of
   ARCH-ZETA-LOCAL-STORAGE.md), I hit a wall: α has no template-level splice
   point to hook, because α's byte position was being defined entirely by the
   driver (`codegen_flat_chain_body`'s `emit_label_define_bb(lbls[i])`),
   never by any template.
3. Lon: "Unify TEXT and BINARY... There is one way to output code, x86.
   PERIOD... the RULE is being violated." — meaning: the driver's direct
   `bb_label_define()` call is a *second output path* for the same logical
   operation `x86("def","β")` already performs correctly (one function,
   both media, internal branch). Fix **this one thing** (α's def
   mechanism), do not audit the rest of the file.
4. Lon: "Change only the live bb_*.cpp templates." — scoped the sweep to
   templates actually reachable from `emit_drive`'s dispatch + confirmed
   compiled into the binary (Makefile), not dead/parked code.

## What was done (all still in the tree, uncommitted)

- **`src/emitter/emit.cpp`**: removed the driver's direct
  `emit_label_define_bb(lbls[i])` call at the top of `codegen_flat_chain_body`'s
  main per-node loop (was line ~1491). Comment left in place explaining why.
- **149 `bb_match_arbno.cpp`-style templates**: converted the vestigial
  TEXT-only `x86("label", _.lbl_α)` to a real `x86("def", "α")`, via one
  manual edit (ARBNO, all 6 roles) + a sed sweep across the other 148 files
  (verified: identical literal string in every case, safe to batch).
- **7 additional live templates** that had *neither* the old vestigial line
  *nor* a def, and were relying entirely on the now-removed driver call:
  `bb_goto.cpp`, `bb_conjunction.cpp`, `bb_enter_init.cpp`, `bb_gen_scan.cpp`,
  `bb_repalt.cpp` (added to `bb_repalt_clear()`, the first sub-function
  `flat_drive_repalt` actually runs for a node). Each got its own
  `x86("def", "α")` inserted at the point where that template's own body
  begins.
- **Confirmed out of scope, correctly untouched**: `bb_match_cat.cpp` (its
  IR op, `IR_MATCH_CAT`, only exists in the parked pre-GZ#5 lowerer file,
  never produced by the live lowerer — genuinely dead in the current
  pipeline). `bb_callee_frame.cpp`, `bb_match_advance.cpp`,
  `bb_match_retry.cpp`, `bb_scan_splice_empty.cpp` (not in the Makefile at
  all — not compiled into the binary). `bb_case_arm.cpp`, `bb_every.cpp`,
  `bb_ite.cpp` (compiled, but zero call sites anywhere in `emit.cpp` —
  unreachable dead code; `bb_iterate()` is the live replacement for at
  least the ITERATE case).
- `bb_gather.cpp` and `bb_mapgrep.cpp` already had a correct `x86("def","α")`
  before this session — no change needed.

## ROOT CAUSE FOUND, NOT YET FIXED — this is the actual blocker

`hello.sno` (`OUTPUT = 'HELLO WORLD'` — the simplest possible program) still
crashes:

```
bb_emit_end: 1 unresolved forward reference(s):
  site=67 label='xchain0_n1_α'
Aborted
```

Traced precisely (see `CLAUDE_TMP_TRACE` env-var trace still sitting in
`bb_assign_global.cpp` line 15 — **remove this before considering the tree
clean**, it's harmless but not meant to be permanent):

- Node `i=1` in this chain is the `IR_ASSIGN` for `OUTPUT`, dispatched to
  `bb_assign_global()`. Confirmed via trace: `op_a_slot=32 op_off=16
  op_gva_k=-1 g_gva_active=0` — the guard passes, the plain-global
  `NV_SET_fn` branch fires, and **that branch does contain `x86("def","α")`**
  (verified by direct reading, twice).
- So the def genuinely gets emitted. The crash is not "missing def" — it's
  that **the def and the reference are for two different label objects.**

**The actual plumbing bug**, found by reading `bb_fill_alpha` closely:

```c
static bb_label_t g_α_ring[8];
static int        g_α_ring_i = 0;
void bb_fill_alpha(IR_t *nd) {
    bb_label_t *a = &g_α_ring[g_α_ring_i++ & 7];
    ...emit_label_initf(a, "bb%d_α", ...);
    g_emit.lbl_α_p = a;
}
```

`bb_fill_alpha` (called from the `FILL`/`DRIVE_FILL` macros, which is what
every `emit_drive` case uses) recycles a **name-mismatched, ring-buffer**
label (`"bb<node_id>_α"`, 8 slots, reused/overwritten across nodes) and
assigns it to `_.lbl_α_p` — which is exactly what `x86_portlbl(X86P_ALPHA)`
resolves to, i.e. exactly what `x86("def","α")` defines.

But **the label other nodes actually jump to** is `lbls[i]`
(`"xchain<id>_n<i>_α"`), allocated once per node by
`codegen_flat_chain_body` itself and used whenever some OTHER node's γ/ω
resolves to this node (`node_γ = ... lbls[k]` in the resolution loop).

**These are two different `bb_label_t` objects.** `x86("def","α")` defines
the ring-buffer one; `lbls[i]` (the one everything actually jumps to) is
never defined by anything anymore, now that the driver's direct call is
gone. This is why every template conversion in this session was individually
correct but the whole thing still doesn't work: the def target was wrong
all along, just papered over previously by the driver defining `lbls[i]`
directly and bypassing `_.lbl_α_p` entirely.

**Why β never had this problem**: `emit_drive`'s signature is
`emit_drive(IR_t *nd, bb_label_t *lbl_γ, bb_label_t *lbl_ω, bb_label_t
*lbl_β)` — β (and γ/ω) are passed in directly from the one real call site
(`emit_drive(nodes[i], node_γ, node_ω, betas[i])`, `betas[i]` being the
SAME object the chain-BFS allocated and the same one other nodes' targets
resolve against). α is the one field `emit_drive` never receives as a
parameter — `bb_fill_alpha` invents a substitute out of the ring buffer
instead.

## The fix (scoped, not yet applied — do this first)

1. Add a 5th parameter to `emit_drive`: `bb_label_t *lbl_α` (keep γ/ω/β in
   their existing positions to minimize diff noise).
2. Update the one real call site (`codegen_flat_chain_body`, currently
   `emit_drive(nodes[i], node_γ, node_ω, betas[i])`) to pass `lbls[i]` too:
   `emit_drive(nodes[i], lbls[i], node_γ, node_ω, betas[i])` (or whatever
   argument order is cleanest — γ/ω/β order shouldn't change).
3. Update the `DRIVE_FILL`/`FILL` macros: add an `a` parameter, drop the
   `bb_fill_alpha(nd)` call, and instead directly do
   `g_emit.lbl_α = (a)->name; g_emit.lbl_α_p = (a);` — mirroring exactly how
   γ/ω/β are already set in the same macro body.
4. Every one of the ~70 `DRIVE_FILL(nd, lbl_γ, lbl_ω, lbl_β)` call sites
   inside `emit_drive`'s own switch needs updating to
   `DRIVE_FILL(nd, lbl_α, lbl_γ, lbl_ω, lbl_β)` — since `lbl_α` will now be
   `emit_drive`'s own parameter name, this is a uniform textual substitution
   (confirmed: all 70 call sites currently use the identical literal string
   `DRIVE_FILL(nd, lbl_γ, lbl_ω, lbl_β)` — a single sed/str_replace sweep
   should cover them, but VERIFY the count and literal uniformity again
   before batch-editing, the way this session did for the template sweep).
5. **RESOLVED before handoff was finalized**: the third call site,
   `DRIVE_FILL(nodes[i], node_γ, node_ω, betas[i])` at line 867, lives
   inside `flat_drive_repalt` (the REPALT special-case driver function this
   session already touched — added `x86("def","α")` to `bb_repalt_clear()`,
   the first sub-function it runs for a node). `flat_drive_repalt` already
   receives `lbls` as a parameter (`bb_label_t **lbls`, in its own
   signature), so this site needs the exact same treatment as the other 70:
   `DRIVE_FILL(nodes[i], lbls[i], node_γ, node_ω, betas[i])`. No new
   investigation needed — just include it in the same batch edit as step 4.
   **Total: 71 `DRIVE_FILL` call sites to update, not 70.**
6. Once `bb_fill_alpha`'s ring buffer is no longer used for α (still fine
   to leave the function itself defined/unused for now, or remove it — call
   depends on whether anything else calls it; grep `bb_fill_alpha(` before
   deleting), rebuild both `scrip` and `libscrip_rt`, rerun
   `hello.sno` directly first (fast sanity check), THEN the full crosscheck:
   ```
   cd /home/claude/work/SCRIP
   CORPUS=/home/claude/work/corpus bash scripts/test_crosscheck_snobol4.sh
   ```
   Target: back to the pre-session watermark (mode-3 252/276, mode-4
   251/9/16, 1 DIVERGE) as the floor — this whole exercise should be a
   byte-identical no-op refactor for every program that isn't touching the
   new self-load hook, so any NEW fail/diverge beyond that watermark means
   something in this fix is still wrong.
7. Remove the `CLAUDE_TMP_TRACE` block from `bb_assign_global.cpp` (and its
   two added `#include`s, `<cstdio>`/`<cstdlib>`, if nothing else in that
   file needs them) once the fix is confirmed — it was diagnostic-only.

## Why this matters beyond just unbreaking the build

Once α is a real, correctly-targeted def (not a decorative ring-buffer
stand-in), it becomes a genuine template-level splice point — which is
what BB-OWNED-ζ's self-load hook (§5h, ARCH-ZETA-LOCAL-STORAGE.md) actually
needs: a central place, hit by every template via the same `x86()` funnel,
where a per-plane-cell load/compare/store can be inserted with zero
per-template edits. That was the original goal before the driver-vs-template
asymmetry was found and became the thing actually being fixed. Once this α
plumbing fix lands and the crosscheck is clean, the self-load hook design
(ASSERT mode first, per D13 in `GOAL-IR-IMMUTABLE-EMIT.md`'s dated plan) is
the natural next step, unblocked.

## Environment notes for next session

- Repos cloned to `/home/claude/work/{.github,corpus,SCRIP}` (all public,
  no credential was ever needed this session).
- `CORPUS` env var must be set explicitly (`/home/claude/work/corpus`) when
  running `scripts/test_crosscheck_snobol4.sh` — its hardcoded default
  (`/home/claude/corpus`) doesn't match this clone location.
- `scripts/install_system_packages.sh` must be run once before the first
  build in a fresh container (installs `libgc-dev`, `libgmp-dev`, etc.) —
  already done in this session's container, but a NEW container/session
  will need it again.
- `make -j4 scrip` and `make libscrip_rt` both build clean as of this
  handoff (RC=0) — the crash is a runtime emit-time abort in the *compiler*
  itself when compiling `hello.sno`, not a build failure.
