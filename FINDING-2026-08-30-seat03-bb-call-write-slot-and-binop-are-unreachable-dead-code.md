# FINDING 2026-08-30 seat03 — bb_call_write_slot.cpp / bb_call_write_binop_str appear to be dead code

## Context: found while fixing up bb_call_write_slot.cpp for the bb-fixup-az-cleanup row

Picked `bb_call_write_slot.cpp` (TOTAL=19) as this row's next mechanical fixup target. Before
trusting the standard "corpus-firing witness" A/B proof, tried to find ANY Icon program that
actually reaches `bb_call_write_slot_str`/`bb_call_write_binop_str` (identifiable by their unique
runtime call targets, `rt_write_any_nl`/`rt_write_int_nl`) — **found none.** Compiled every `.icn`
file under `corpus/tests/icon`, `corpus/demos/icon`, and `corpus/tests/scrip_test/icon` (all
current sources, ~200 files) and grepped the `.s` output: **zero hits, corpus-wide.**

## Root cause 1, confirmed by instrumentation: `bb_call_write_route`'s own arg-count check reads the wrong field

`src/emitter/emit.cpp:909-920`, `bb_call_write_route(IR_t *nd)`:
```c
const char *fn = IR_LIT(nd).sval; int64_t narg = IR_LIT(nd).ival; IR_t *a0 = ir_call_arg(nd, 0);
if (!(fn && narg == 1 && a0 && !strcmp(fn, "write"))) return 0;
```
Added a temporary diagnostic print (reverted before landing anything — see below) and ran a probe
calling `write(x)`, `write(x || y)`, `write(3 + 4)`: for every one of these, `IR_LIT(nd).ival`
(`narg`) held **uninitialized-looking garbage** (e.g. `459013424`, changing between identical runs
— classic unread/leftover-memory signature), while `nd->n_operands` correctly read `1` every time.
`bb_slot_get(a0)` also returned a sane, non-negative slot for all three. **The `narg == 1` check
can never pass for an Icon `write()` call, because Icon's `IR_CALL` lowering apparently never
populates `IR_LIT(nd).ival` with the argument count** — that field is presumably meaningful for
some other caller/language's call-lowering convention, not Icon's.

## Root cause 2, suspected but NOT confirmed: `bb_call_route_classify` may short-circuit even earlier

Patched `narg` to read `nd->n_operands` instead (test-only, reverted — see below) and reran the
same probe: **still zero hits.** So fixing root cause 1 alone is insufficient. `bb_call_route_classify`
(`emit.cpp:926-949`) has several earlier returns before it ever consults `g_emit.op_write_route`
(populated by `bb_call_write_route`) at line 944 — in particular `emit.cpp:934`:
```c
if (k == IR_CALL_ICON && fn[0] && icn_builtin_is_known(fn)) return CALL_ROUTE_FN;
```
If `icn_builtin_is_known("write")` is true (plausible — `write` is a core, universally-known Icon
procedure), this returns `CALL_ROUTE_FN` (the generic by-name dispatch every witness in this
session's probing actually took, confirmed by the compiled `.s` calling `"write"` as a string-named
builtin rather than `rt_write_any_nl`/`rt_write_int_nl` directly) **before line 944's switch is
ever reached, regardless of what `op_write_route` holds.** Not verified with instrumentation this
session — named here as the next actual step, not chased further, per this row's own
never-widen-scope discipline.

## Why this matters (not urgent, but real)

If confirmed, `bb_call_write_slot_str`/`bb_call_write_binop_str`/`bb_call_write_legacy_str` are a
complete, compiling, but **entirely unreachable** fast path — every Icon `write(...)` call falls
through to the slower generic by-name builtin dispatch instead. This is the exact performance
shape FIX-3-i's own design rationale cites elsewhere in this codebase (bypassing by-name dispatch
for a hot, simple case) — so reviving this path (fixing both root causes, then re-verifying against
a live witness) is a genuine, if minor, performance opportunity, not just dead-code removal.

## Verification method used for THIS row's own fixup (since no live witness exists)

To get a real A/B proof despite the dead code, temporarily patched `narg` to `nd->n_operands` in a
local, uncommitted change, confirmed the write-family templates STILL didn't fire (root cause 2
above), and therefore could not exercise `bb_call_write_slot.cpp`'s logic via any live program
even with root cause 1 patched. **Reverted both the diagnostic print and the `narg` patch in full
before landing anything** — `git diff src/emitter/emit.cpp` is empty in the commit that follows
this FINDING. `bb_call_write_slot.cpp`'s own hygiene fixup (separate commit) is therefore
verified by direct static inspection only (line-by-line semantic equivalence: `x86_frame_load64`→
`x86("mov",...,FRQ(...))` dispatches to the identical internal encoder per `x86_asm.h:1736`; the
function-pointer-to-`uint64_t` cast is bit-for-bit the same whether routed through a named local or
inlined; eliminating `a0`/`off` locals by re-calling the same pure, side-effect-free lookups
(`ir_call_arg`, `bb_slot_get`) is behavior-preserving by construction) plus a clean `make pristine`
compile and the full standing battery (SNOBOL4 1669/1669 both modes, Icon 14/14, Prolog 5/5,
Snocone 5/5, Raku 724/724, purity/bin_t/handencoded/emit_blind/medium_invisible/emit_no_lang all
clean) — not a corpus-firing witness, because none exists for this file today.

Not attempting either root-cause fix — this is a functional/performance defect, out of scope for a
style-hygiene row (`bb-fixup-az-cleanup`) per its own never-widen-scope discipline. Naming it here
so it isn't lost; whoever owns Icon call-dispatch correctness/performance next has both root causes
and the exact instrumentation needed to confirm root cause 2.
