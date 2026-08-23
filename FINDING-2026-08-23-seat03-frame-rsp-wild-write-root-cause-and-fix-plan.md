# FINDING 2026-08-23 (seat03) — row `zeta-frame-rsp-second-wild-write`: ROOT CAUSE CONFIRMED, fix plan scoped and evidenced, NOT YET IMPLEMENTED (reassigned to `vlist-expr-alternation` by hq_C mid-session, higher priority)

## HEADLINE

Full root cause found by ASM-DIFF-FIRST (RULES.md), no gdb needed. **`--zeta-storage=frame-rsp`'s outer/top-level
scope never reserves real stack space for its ZLS (zeta local storage) region — every value-producing statement is
assigned a permanently-growing, never-reclaimed `[rsp+offset]` slot by `zls_build`/`ir_drive_slot_assign`, but the
program's actual entry prologue (`main:` in mode 4, `rt_outer_call` in mode 3) only ever does a tiny fixed `sub rsp,
8`. Once accumulated slot usage exceeds the real (unreserved) headroom above the entry rsp — empirically ~19.8-20KB
for a process at this call depth — the generated code writes past the top of the OS-mapped stack region: a genuine
wild-write SIGSEGV, exactly as the row describes.** CONFIRMED experimentally: setting the existing (already-present
but manual-only) `SCRIP_M4_HEADROOM=65536` env var cures the crash on the committed witness with ZERO source changes
— this is not a hypothesis, it is a reproduced cure. A scoped, low-risk fix (outer/top-level scope only, both modes)
is fully specified below with exact file:line targets, but **NOT YET IMPLEMENTED** — mid-session, hq_C reassigned
this seat to `vlist-expr-alternation` (re-ranked 5→1, "ahead of anything you picked yourself"), so this row is being
handed off at the root-cause-confirmed stage rather than pushed through to a verified fix.

## THE MECHANISM, WITH RECEIPTS

1. **`ir_drive_slot_assign`** (`src/contracts/scrip_ir.c:267`) calls **`zls_build(g)`**, which assigns every
   value-producing IR node in a graph a unique, monotonically-growing 16-byte DESCR slot — confirmed directly via
   `./scrip --zeta-storage=frame-rsp --dump-zeta <file>`, which prints the exact layout: for the committed witness
   (`corpus/probe/frame/frame_rsp_indexed_call_concat.sno`, N=96) the dump header reads
   `graph 0 'main' — slots=1251 region_end=20016`. **The REAL beauty.sno's own top-level graph needs
   `region_end=168112` (slots=10507, scopes=316)** — i.e. beauty's crash is this exact mechanism at ~8x the
   witness's scale.
2. This total (`region_end`) is stored on the graph as `g->jcon_value_region` (an Icon-flavored field name reused
   generically — `ir_drive_slot_assign` populates it for EVERY graph, all languages, unconditionally) and is
   accessible via `zls_g_region(g)` (`src/contracts/zeta_storage.c:721`).
3. **Icon's own "flat frame" mechanism DOES consult this total** to size a real reservation
   (`emit.cpp:3328`: `g_emit.flat_frame_bytes = (48 + g_emit_cfg->jcon_value_region + 15) & ~15`, gated on
   `zframe_graph`/`icn_cells_graph`). **SNOBOL4's plain (non-pattern-matching) value-producing statement path has NO
   analogous wiring.** Confirmed by direct search: `grep -rn 'flat_frame_bytes\s*='` finds only Icon/Prolog-flavored
   call sites; nothing for the SNOBOL4 outer/DEFINE prologue.
4. **Direct instruction-count proof that nothing ever reserves or reclaims this region under frame-rsp:** the
   compiled `.s` for the N=96 witness (13,243 lines) contains **exactly ONE `sub rsp` and ZERO `add rsp` for the
   entire program** (`main:`'s own 3-instruction prologue: `sub rsp, 8; push rdi; push rsi`), and **exactly 2 bare
   `push` instructions total, zero `pop`** — both are the same two prologue pushes; nothing else in the whole
   generated program ever moves rsp. Every one of the 3,748 `mov [rsp+N], ...`/`mov ..., [rsp+N]` instructions (N up
   to 20,008) addresses memory relative to that one never-changing rsp value.
5. **This directly contradicts the storage arm's own documented design law**
   (`.github/ARCH-ZETA-LOCAL-STORAGE.md:917`, "THE LAW", Lon's own ruling): *"STACK flavor — every ζ cell on rsp is
   FIXED SIZE, exactly ONE cell per BB, no other allocation on the spine (pure §10a: α=`sub rsp,K` · cell live
   through ALL γ/β cycling · ω=`add rsp,K`, compile-time offsets)."* Pattern-matching boxes (ARBNO/fence/DEFER —
   `bb_match_defer.cpp`, `bb_match_fence1.cpp`, gated on `x86_port_cstack()`) DO implement real per-box push/pop
   under frame-rsp. **Plain value-producing statements (assign/call/subscript/binop/concat — everything
   `ir_node_produces_value()` lists) do NOT** — they get a static offset from `drive_value_slot()`
   (`emit.cpp:1275`) with no surrounding α-push/ω-pop at all. The architecture's intended LIFO reuse (bounded by
   *live depth*) never happens for this whole class of node; instead usage grows unboundedly with *total node
   count*, which is why the crash threshold (~20KB) is reached by node count alone, independent of table
   size/growth/key reuse (already established in the prior FINDING) — 96 statements × ~13 slots/statement × 16
   bytes = the observed 20,016-byte region, matching the dump exactly.
6. **The crash is not main-specific.** A `DEFINE`d function wrapping the identical statement shape
   (`DOIT_α: sub rsp, 48` in its own compiled `.s`, followed by the same unboundedly-growing `[rsp+N]` addressing up
   to +20,072) crashes identically at the same N. `beauty.sno` itself never calls a `DEFINE`d function under empty
   stdin (confirmed in the prior session's bisection), so THIS row's DONE-WHEN only requires curing the
   outer/top-level scope — but a `DEFINE`-heavy program would hit the same wall today, and that is **NOT** fixed by
   the scoped plan below.

## EXPERIMENTAL CONFIRMATION (zero source changes)

`src/driver/scrip.c:1481` already contains an existing-but-manual escape hatch for mode 4 only:
```c
{ const char * hr = getenv("SCRIP_M4_HEADROOM"); if (hr && *hr) { long hb = atol(hr); if (hb > 0) { hb = (hb + 15) & ~15L; emit_textf("  sub rsp, %ld\n", hb); } } }
```
Compiling the committed N=96 witness normally (mode 4, gcc-linked, run) crashes rc=139 as expected. **Compiling the
identical witness with `SCRIP_M4_HEADROOM=65536` set produces a binary that runs clean, rc=0.** This is a full,
reproduced cure of the crash mechanism using only an already-existing knob — the strongest possible confirmation
short of shipping the automatic fix.

## FIX PLAN (scoped to outer/top-level scope only, both modes — NOT YET IMPLEMENTED)

Two edit sites, both bracket-add a reservation rather than touching proven-correct existing bytes:

**Mode 4 (`--compile`, TEXT), `src/driver/scrip.c:1480-1481`:** `sbbg` (the main graph, `IR_graph_t *`) is already
resolved at line 1405 and in scope. Immediately after the existing prologue + `SCRIP_M4_HEADROOM` block, add:
```c
if (rt_zeta_storage_get() == (int)ZC_STORAGE_FRAME_RSP) {
    extern int zls_g_region(const IR_graph_t *);
    long need = sbbg ? (long)zls_g_region(sbbg) : 0L;
    if (need > 0) { need = (need + 15) & ~15L; emit_textf("  sub rsp, %ld\n", need); }
}
```
Precise (not padded-guess) because mode 4 has compile-time access to the exact computed `region_end` for THIS
program via the same `zls_g_region()` accessor `ir_drive_slot_assign` already populates
(`g->jcon_value_region = zls_g_region(g)`, `scrip_ir.c:283`) — no waste, no risk of being too small for an
unusually large program. Gate on `ZC_STORAGE_FRAME_RSP` specifically so the other three arms (default cell-stack
included) are byte-for-byte unaffected.

**Mode 3 (`--run`, BINARY, in-process JIT), `src/runtime/rt/rt.c:28-49` (`rt_outer_call`, hand-written asm, compiled
once into `libscrip_rt.so`, shared by ALL programs/languages — SNOBOL4, Prolog directly, Icon via
`rt_outer_call_delta0` which calls it):** this trampoline cannot see a per-program computed size (it's build-once,
run-many), so the plan is a generous FIXED reservation rather than a precise one — beauty's own real need is
168,112 bytes, so a multi-MB constant leaves ample margin while staying far inside the default 8MB `RLIMIT_STACK`.
Bracket the existing `sub $8, %rsp` / `add $8, %rsp` (do not alter the existing 8s — new alignment reasoning below
shows why not) with a symmetric extra pair:
```
"  push %r12\n"
"  sub $8, %rsp\n"
"  sub $4194304, %rsp\n"      /* NEW: reserve headroom for the frame-rsp top-level ZLS region (~4 MiB) */
...(unchanged)...
"  call *%rax\n"
"  add $4194304, %rsp\n"      /* NEW: matching restore */
"  add $8, %rsp\n"
"  pop %r12\n"
```
**Alignment check (verified, do not skip when implementing):** at `rt_outer_call:` entry rsp ≡ 8 (mod 16) (standard
SysV post-`call` convention). `push %r12` → ≡0. `sub $8` → ≡8. The subsequent `call *%rax` then lands the JIT'd
blob's own entry at ≡0 (mod 16), the correct convention for a callee entry. Inserting an EXTRA `sub`/`add` pair
whose constant is itself a multiple of 16 (4,194,304 = 2^22, trivially ≡0 mod 16) preserves this alignment class
exactly — it does not require touching or re-deriving the existing `$8` literals at all, which is why the plan
brackets rather than replaces them.
**This reservation is unconditional (all 4 storage arms pay it)** since `rt_outer_call` cannot branch on the
runtime-selected storage arm without adding a runtime check to a hot(ish) shared trampoline — but the cost is two
extra instructions ONCE per process (not per-statement, not per-call), and `sub rsp` alone does not fault or commit
pages (Linux lazy stack growth), so this is a one-time-startup cost, not steady-state — should not need a
performance-taint re-measurement under the FACT RULE's "one-time startup" carve-out, but flag this explicitly to
whoever reviews the actual patch since it touches a file every SNOBOL4/Icon/Prolog run passes through.

## WHAT THE FIX PLAN DOES **NOT** COVER (explicitly out of scope, flagged for a follow-up row)

- **`DEFINE`d function activations under frame-rsp are NOT fixed by this plan.** Confirmed independently crashing
  (see mechanism §6 above) at the same ~20KB-equivalent threshold, and NOT exercised by beauty.sno under empty
  stdin, so it does not block THIS row's DONE-WHEN — but it is a live, reproducible defect under the identical
  mechanism. A `DEFINE`d function's prologue (`DOIT_α: sub rsp, 48` in the witness) would need the SAME per-graph
  `zls_g_region()`-sized reservation, PLUS (unlike `main`, which never meaningfully returns) a correctly placed
  matching `add rsp` on EVERY exit port (RETURN/FRETURN/NRETURN/omega) so the caller's own rsp is not corrupted on
  return — that exit-path enumeration is real, non-trivial surface area this session did not attempt to map, which
  is the specific reason this fix was scoped to outer/top-level only rather than pushed through to the general case
  in the time available.
- **The architecturally "correct" fix per `ARCH-ZETA-LOCAL-STORAGE.md`'s own STACK-flavor law (§ real per-box
  α-push/ω-pop, bounding memory to live depth not total node count) is NOT what this plan implements.** The plan
  above is a reserve-the-whole-computed-total stopgap, safe and sufficient for any single-scope program whose total
  node count fits comfortably under a few MB (every corpus/demo/benchmark program almost certainly qualifies), but
  it does not scale the way the documented design intends and leaves that gap for a future, more invasive rung if a
  pathological program ever needs it.

## RECEIPTS

SCRIP HEAD at investigation time (post `git pull --rebase`, fresh `make pristine` rebuild) `a71d3034`. All
investigation performed via `--dump-zeta`, direct `.s` reading/grepping, and one experimental `SCRIP_M4_HEADROOM`
run — **zero gdb**, consistent with RULES.md's ASM-DIFF-FIRST order (asm diff + the existing dump tooling fully
answered root cause; gdb was never reached because it was never needed). No source files were edited this session —
all witness variants live under the session scratchpad and are reproducible from the generator described inline
below; only the FINDING doc and task baton are being committed. Prior session's minimal witness
(`corpus/probe/frame/frame_rsp_indexed_call_concat.sno`) reproduces the exact same rc=139 on the fresh build,
re-verified before use.

**Witness generator used for the ad-hoc synthetic checks (N=95/96 pairs, DEFINE-wrapped variant), for
reproducibility — not committed, trivial to regenerate:**
```python
# double-call table-assignment shape, N repetitions, same key (key value proven irrelevant by the prior session):
lines = ["    UTF = TABLE()"] + ["    UTF[CHAR(65) CHAR(66)] = 'v%d'" % i for i in range(1, N+1)] + ["END"]
# DEFINE-wrapped variant (proves the defect is NOT main-specific):
# UTF = TABLE() / DEFINE('DOIT()') / DOIT() / END / DOIT / <N repetitions of the same line> / :(RETURN)
```
