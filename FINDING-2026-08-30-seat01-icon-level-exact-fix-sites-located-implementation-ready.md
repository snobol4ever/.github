# FINDING — addendum to the same day's `icon-level-fix-location-...` correction: the ACTUAL two
# emission sites for `&level` tracking on the `flat_lcl_proc`/`icn_cells_graph` call path are now
# located precisely, by direct trace-matching against the emitted `.s`, not by re-reading source and
# guessing. One side is safe/simple to implement (x86 DSL, already Icon-scoped). The other needs
# careful raw-byte BINARY-arm work this session did not attempt. Implementation-ready handoff.

**seat01 · 2026-08-30 · row `icon-rung-ladder-absorption`**

**Still not a cure.** This session found the wrong-location problem, then this same session located the
right one — but stopping short of landing it is a deliberate choice, not a time-out: this bug's own
corroborating measurement (seat02's FINDING, `RTX-CLAIMS.md:180`) shows it moves the graded corpus board
by exactly **one program**. Low priority, low blast radius, but the BINARY arm needs raw-byte
verification this pass didn't do, and this project's own R10 rule ("BINARY must byte-agree with `as` on
the TEXT arm") is not satisfiable by hand-reasoning about ModRM/REX bytes without checking.

## 1. Exit side (decrement) — LOW RISK, ready to implement as described

`src/templates/xa/xa_flat.cpp`, `xa_flat_zframe_epilogue_γ_str()` (~line 421-426) and
`xa_flat_zframe_epilogue_ω_str()` (~line 463-466) — the specific arms already gated
`icn_wire_stack_on() && g_emit_cfg->icn_cells_graph && g_emit.flat_lcl_proc`, and **already
self-documented "Guarded to the Icon (icn_cells_graph) case only."** Confirmed by direct trace: this is
exactly the arm that emits `p_γ`/`p_ω`'s `mov rdi,rax / mov rsi,rdx / add rsp,kt / jmp [...]` sequence
in the minimal repro's `.s`. These functions build their output entirely via the `x86(...)` DSL (no raw
bytes) — mirroring `bb_define_activate`'s own leave_env decrement (`bb_define.cpp:185-193`) here is a
same-shape, low-risk addition:
```
+ x86("mov", "rax", std::string("[rip@got + __]"), (uint64_t)(uintptr_t)(void *)&rt_k_level_p, "rt_k_level_p")
+ x86("mov", "rax", RDQ("rax", 0))
+ x86("mov", "ecx", RDD("rax", 0))
+ x86("sub", "ecx", (long)1)
+ x86("mov", RDD("rax", 0), "ecx")
+ x86("mov", "rax", std::string("[rip@got + __]"), (uint64_t)(uintptr_t)(void *)&kw_fnclevel, "kw_fnclevel")
+ x86("mov", RDD("rax", 0), "ecx")   // kw_fnclevel := rt_k_level - 1, matching rt_ab_leave_env's own formula
```
placed before the existing `+ bb_glue_wire_γ()` / `+ bb_glue_wire_ω()` tail in each function (register
usage: rax/rcx are dead by this point in both arms — rdi/rsi already carry the marshaled result, and
`rt_k_level`/`kw_fnclevel` aren't in any live register — verify this holds at insertion time, not
assumed here).

## 2. Entry side (increment) — the part this session declined to hand-encode

`src/emitter/emit.cpp`, inside the `else if (g_emit.flat_lcl_proc)` branch (~line 2917-2961). Confirmed
by direct trace: this is exactly where `FN__p`'s `sub rsp,128 / call rt_icn_zframe_args_install@PLT`
prologue comes from — `_use_zframe_install = (g_emit_cfg && g_emit_cfg->icn_cells_graph) ? 1 : 0`
already gates the Icon-specific call target, confirming this branch is genuinely shared cross-language
(other graphs can reach `flat_lcl_proc` via the OTHER disjunct in its own assignment,
`emit.cpp:3632` — `flat_jmp_entry && (nparams>0||nlocals>0)`, no `icn_cells_graph` required) and any
addition here MUST be gated the same way `_use_zframe_install` already is.

⛔ **Why this session stopped here:** this specific branch emits through TWO separate arms — a TEXT arm
(`snprintf`-built assembly text, ~line 2940-2947) and a BINARY arm (hand-encoded raw bytes via
`ef_b1`/`ef_b2`/`ef_b3`/`bb_emit_u64`, ~line 2949-2959), NOT the `x86(...)` DSL this file uses
everywhere else for this kind of thing. The TEXT arm is a five-minute edit (add the mirror-image
`mov`/`add` text lines, gated on `_use_zframe_install`, matching `kw_fnclevel`'s formula from §1). The
BINARY arm requires either (a) assembling the equivalent instructions with `as`, disassembling the
result, and copying the exact bytes — this project's own R10 rule for exactly this situation — or (b)
confirming this specific raw-byte region can safely be replaced with an `x86(...)`-DSL call instead
(cleaner, but a bigger diff against surrounding code this session did not fully map). Neither attempted.

## 3. What "done" looks like, so a future landing doesn't skip a step

Per every other change on this shared surface in this file's own commit history (see the neighboring
"N-1(a)" comment's own m3≢m4 story, `emit.cpp:2953`, an actual TEXT/BINARY divergence caught the hard
way): **build BOTH arms, verify BOTH modes reproduce `1 2 1` on the minimal repro**, then run a broad
Icon regression (smoke at minimum) plus a non-Icon control arm (SNOBOL4 blocking set, since
`flat_lcl_proc` is reachable without `icn_cells_graph` and a careless edit could leak into that path) —
same shared-node discipline as every high-blast-radius change on this project, even though this one's
actual radius is small.

## 4. Not attempted

No code touched (`git status --short` clean, SCRIP `4cc1ccbb`). This FINDING is deliberately
implementation-ready rather than an implementation: the remaining work is real (raw-byte verification,
broad regression) but no longer open-ended — every open question from the original FINDING and from
this session's own correction is now closed except "do the surgery and prove it."
