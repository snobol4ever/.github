# FINDING — this row's architectural blocker (icon-n2 items 3-4) is CONFIRMED CLEARED for the first
# time in 12 passes, BUT the natural next assumption — "just hook Prolog into Icon's now-working
# generator-frame mechanism" — is exactly the mistake that already caused a real regression once.
# `icn_gen_regime()` exists specifically because Icon's N-2 machinery, when defaulted ON, silently also
# caught Prolog suspend graphs (both satisfy `is_generator && has_suspend`) and broke prolog smoke 5/5→3/5
# both modes. Prolog needs its OWN gated implementation of the SAME SHAPE, not a share of Icon's code path.

**seat02 · 2026-08-30 · row `prolog-pz4-gamma-retain-activation-frames`**

**Blocker-clearance confirmed + one load-bearing new precedent + the exact seam re-confirmed against
current HEAD. No code touched — this remains real implementation work, now more precisely scoped, not
attempted this pass.**

## 1. The blocker is genuinely clear — confirmed directly, not cited

`QUEUE.tsv`: `icon-n2-generator-activation-frames  ceo  DONE`. Its own task file confirms the SPECIFIC
bar hq_C set for this row's un-park (`## LEDGER`, hq_C 2026-08-27): *"the un-park condition is hq_P's
message that items 3–4 have landed, with the D2 witness at REPS=20."* The DONE-WHEN's own re-cut header
confirms exactly that: *"the umbrella's own mechanism is landed (D2 ALL-GREEN REPS=20 both modes,
default ON, fifth census class granted+pinned, legacy machinery deleted)."* **This is the first time in
this row's 12-pass history this has been true.** Mailed hq_C directly (`pz4-blocker-cleared-icon-n2-
items-3-4-confirmed-done`) since they own this row under Lon's split ruling.

## 2. The load-bearing new precedent — DO NOT hook Prolog into Icon's literal mechanism

Read `icn_gen_regime()` (`src/templates/x86/x86_asm.h:2107-2108`) directly while scoping what "build to
the seam" should mean now that item 2/3/4 are real:

```c
inline int icn_gen_regime() {   /* ⛔⛔ THE ICON-ONLY KEY (ceo s283f, minutes after the default flip):
   flat_gen alone is NOT Icon-only -- a PROLOG suspend graph satisfies is_generator&&has_suspend and,
   once the gate defaulted ON, took the region-resident alpha whose caller half exists only in Icon's
   bcps template: prolog smoke went 5/5 -> 3/5 BOTH MODES, restored by the killswitch (A/B measured).
   icn_cells_graph's only setters are lower_icon.c, so this predicate is the regime key every
   generator-protocol site uses INSTEAD of bare icn_genframe2(); the bare switch survives only as the
   killswitch input here. */
    return icn_genframe2() && g_emit_cfg && g_emit_cfg->icn_cells_graph;
}
```

**This already happened once.** The moment `icn_genframe2()` (N-2's generator-activation-frame
protocol) defaulted ON, it caught Prolog suspend graphs too — because the underlying predicate
(`is_generator && has_suspend`) is not language-specific, only `icn_cells_graph` (set exclusively by
`lower_icon.c`) is — and Prolog took Icon's ALPHA (region-resident carve) while its own CALLER-side
landing, which only exists in Icon's `bcps` template, never matched it. Real, measured regression:
prolog smoke 5/5 → 3/5, both modes. The fix was `icn_gen_regime()` itself: gate every N-2 site on
`icn_cells_graph`, not the bare cross-language predicate.

**Consequence for this row: Icon's N-2 machinery is not something Prolog can "join" — it is deliberately
fenced to exclude Prolog by construction, precisely because sharing it naively already broke Prolog
once.** Lon's own directive ("use Icon generators as a model") means model the SHAPE — RBP-promoted
retained frames, restore-and-jmp on resume instead of fresh reinvocation — not the CODE PATH. A
Prolog-side implementation of steps (a)-(f) needs its OWN regime predicate gated on `pl_cells_graph`
(mirroring `icn_gen_regime()`'s own shape exactly, substituting the Icon-only field for the Prolog-only
one), reusing the shared `emit_rec_pin()`/`x86_fb_pinned()` primitives underneath (those already ARE
language-generic — `emit_rec_pin()` itself doesn't mention either language) but never the Icon-specific
gate. Skipping this and reusing `icn_genframe2()`/`icn_gen_regime()` bare, or a predicate that doesn't
distinguish the two languages, would very plausibly repeat the exact 5/5→3/5 regression, just discovered
later and by a different measurement.

## 3. The exact seam, re-confirmed against current HEAD (matches seat02's own earlier design pass,
   `FINDING-2026-08-27-seat02-pz4-zframe-bblocals-design-seamed-against-item2.md`, now with a live target)

`src/templates/bb/bb_call_proc_staged.cpp:809-859`, the `pl_zf_resume` branch (armed when
`g_emit.zframe_graph && zf_cont_off >= 0`). Current shape, confirmed by direct read:
1. `mov FRQ(act), 0` — clear the "in-flight" flag.
2. `rt_pl_cp_pop3` — pop a saved (cursor, trail_mark) pair from a **global** stack (`rt_pl_cp_pop3`).
3. `rt_pl_zf_resume_set` — stash cursor/trail_mark/offsets into **five process-wide globals**
   (`g_pl_zf_pending_*`), later read back by `rt_jmp_frame_lexprep2` at fixed frame offsets `[fb+0]`/
   `[fb+8]` in the callee's fresh prologue.
4. `rt_proc_call_open_det`/`rt_proc_call_open` — called with the **same args as the original call** —
   this is the fresh re-invocation seat16's own pass gdb-confirmed (RSP and the resume-cell's address
   identical across all three calls in their witness).
5. `bcps_wire_cross_gen(3, 4)` then `jmp` into the callee's **α entry**, not a resume point.

**Target shape** (clauses a/c/d, unimplemented): retire steps 2-4 above. In their place: read a
CALLER-owned "retained base" slot (a new BB-local field in the caller's OWN pinned frame — this is
clause (a)'s "prologue saves caller base + pins own," applied at the CALL SITE rather than callee entry)
that clause (b)'s existing, already-landed `mov rax, rsp` (`xa_flat.cpp:385-390`, armed under
`SCRIP_PL_GAMMA_RETAIN`) should be storing into on the FIRST call — clause (c), "caller staged-call γ/β
landings re-anchor off their own pinned base," is precisely the currently-missing consumer hq_C's DUO
matrix measured ("rax is consumed nowhere"). On retry, restore rsp from that stored base and `jmp`
straight to the callee's **β entry** (skip α, skip the global mailbox, skip
`rt_proc_call_open_det` entirely) — the "restore + jmp, no recreation" shape hq_P's own ruling names.

## 4. What this does NOT resolve

- Does not implement anything — no code touched, `git status --short` clean throughout.
- Does not address seat03's own still-open question (whether the retract-synthesized `$dyn_iter`
  generator wrapper witnesses, `bcps_spine_gen_arm`'s branch rather than `pl_zf_resume`'s, need a second,
  parallel change at a different call site — seat16's pass argues yes, same class, same fix, not
  independently re-verified here).
- Does not touch clauses (d)/(e)/(f) (backtrack restore, ω release, top-graph exclusion) — all still
  needed for a complete cycle; a partial implementation of (a)/(c) alone would not reach DONE-WHEN and
  could plausibly introduce unbounded frame growth (no release) if landed alone. Do not land partially.

## 5. State

Floor re-confirmed unchanged (no source edits): rung13 5/5 · rung14 0/2 · rung15 3/4. Tree: SCRIP
`ae078681`+, corpus current as pulled this session.

## Next actor

1. Design and implement a Prolog-side `pl_gen_regime()` (mirroring `icn_gen_regime()`'s shape, gated on
   `pl_cells_graph`) before touching any shared N-2 predicate — do not reuse `icn_genframe2()`/
   `icn_gen_regime()` bare, per §2.
2. Implement clause (a): a per-call-site retained-base slot, written by clause (b)'s existing `mov rax,
   rsp` (already landed, currently unconsumed).
3. Implement clause (c) at `bb_call_proc_staged.cpp:809-859`'s `pl_zf_resume` branch per §3's target
   shape — replacing the fresh-reinvocation with a restore-and-jmp against the retained base.
4. Clauses (d)/(e)/(f) still needed for a complete, safe cycle — do not land (a)/(c) alone without them.
5. Budget the full shared-node verdict set (SNOBOL4 blocking set FAIL=0, Icon pinned watermark) before
   landing anything — `bb_call_proc_staged.cpp`/`xa_flat.cpp` are shared surface, exactly the surface
   `icn_gen_regime()`'s own origin story shows can silently break the OTHER language.
6. This is genuinely substantial implementation work, best done as a dedicated session (or by hq_C
   directly, who owns the row) rather than folded into a single fleet `next` pass — matching every one of
   the twelve prior passes' own judgment, now with a materially narrower, more concrete target.
