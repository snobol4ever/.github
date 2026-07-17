# FINDING 2026-07-17 (s83, Claude, attended) — REG-7 U4/U5 DELETIONS ARE GATED ON THE DECLINE-CLASS CONVERSIONS; THE ANCHORED RESIDUE IS 5 PROGRAMS, MEASURED

**ONE LINE:** FN-SEAL-RBP + U3 + U4-slice-0 LANDED at watermark; the remaining U4 deletions (op_anchored fields/registrars/zr arms) and U5 (+40 reclaim + zr seal) are BLOCKED by live machinery — a zr-arm flip probe fails exactly the 5 walk/multi-arbno window programs — so they park behind ZB-FC-3d-ALT and ZB-ITER, exactly the shape the s81 finding predicted for the original REG-7 one-liner.

## WHAT LANDED (s83)

| Commit | Rung | Content |
|--------|------|---------|
| `05894a4a` | FN-SEAL-RBP | bb_match_head +40 save → unconditional FRQ (self-referential, depth-immune); rspq40 deleted; the 067 rbp=0 mine defused |
| `74fb951d` | U3 | s82 parked patch re-landed (context-adapted to the FN-SEAL fix): x86_fb()/fb_num split off zr; fr prefixes unconditional rbp; modrm/rex/text_mem re-based; op_flat_disp FR/FRQ terms deleted; head materialization deleted |
| `35c33a89` | U3 regen | feature .s (SCRIP) |
| corpus `b25bd5fb` + `1c32b2ba` | U3 regen | benchmark + demo .s |
| `4bf8c6f1` | U4 slice 0 | op_flat_disp field + init + fc_leaf_disp delivery deleted (write-only post-U3) |

All watermark-exact: **m3 303/4 · m4 293/13/1 · DIVERGE=10 identical names**. 067's m3 segfault under U3 is GONE (the FN-SEAL diagnosis was correct and sufficient).

## THE MEASUREMENT THAT PARKS U4/U5 (do not re-derive)

Scratch-flip of the zr/zr_num anchored arms (`(_.op_anchored || _.op_anchor_head) ? "rbp"` → deleted), full crosscheck:
**m3 303→298, m4 293→288 — the 5 new failures in BOTH modes are exactly `070_pat_arbno_star_var_digits`, `117_pat_arbno_of_star_var_fence`, `142_pat_arbno_fence_arbno`, `164_pat_arbno_nested`, `165_pat_arbno_defer_var_body`** — the walk/multi-arbno decline class of the s81 census. Mechanism: the anchored window's zr(=rbp) is the ARBNO **element view register** — `bb_match_arbno`'s chain dance saves/re-points/restores it per element and interior boxes read view-relative slots through it; the flat rt_cap capture array and DEFER wiring ride the same view ("a real register", the s66 comment's premise). Post-U3 this is the ONLY thing op_anchored still does (fr prefixes and disp compensation no longer read it), but it is genuinely load-bearing for those statements.

Corollary for U5: the per-head +40 outer-rbp save/restore protocol is NOT redundant while the anchored class lives — the element chain re-points rbp mid-statement and the statement-exit restores are what recover the outer frame base. Deleting +40 now would hand the next statement a dangling element view.

## THE PARK

- [ ] **U4 remainder** (op_anchored/op_anchor_head fields, delivery, fcanc/fcah registrars, !tail_ok registration, zr anchored arms) — **parked behind ZB-FC-3d-ALT (ALT lift) + ZB-ITER (arbno element scheme for the walk/multi-arbno residue)**. When the last decline class converts, the flip probe above becomes the completion test (expect zero movement) and the deletions land in one sweep.
- [ ] **U5** (+40 reclaim + zr seal) — same gate; the flat_pat zr arm decision (blob interior pushes on rbp vs shared rsp stream) still needs Lon's ruling per the s81 ladder text.

## RESIDUE ACCOUNTING (the honest census)
- r12: pend shapes + outer seed ONLY (REG-6/REG-7-s0 state, unchanged this session).
- rbp: universal frame base (U1/U2/U2b seeds + FN-SEAL discipline) + the 5-program element-view borrow (statement-bracketed by +40).
- rsp: FORTH cursor everywhere; granted-window element rebase (fc_hit) rides it by design.
- op_flat_disp: GONE (field, init, delivery). fcl registrar machinery left standing for the dead-code sweep / possible HZ-1 reuse — its consumer chain is now severed at the delivery point.

## s83 SECOND HALF — GC ROUTE RECEIPTS (appended same session)

**GC-U-5 raw-malloc sweep, SNOBOL4-runtime slice LANDED (`11e36fae`):** 24 sites → `rt_ws_*` (keywords ×4, runtime_eval ×6 with 2 free() deletions, rt.c registries ×4, core.c loader/growth/varnames ×10). Scope fences honored: Prolog family, coexpr ctx/pkg (§6b-ii fix home unchanged), pat_pool/pinned mmaps (region 3), zcol realloc (ZB-ITER), getline buffers. Cross-language stash-proof: icon 12/2+10/4, prolog 3/2+3/2 IDENTICAL at pre-sweep HEAD. SNOBOL4 watermark exact.

**HZ-1 slice-2 SNOBOL4 escapee census = ∅ (structural + empirical):** ZH's sole client is `rt_proc_call_gen_h` (rt.c:584, `ZC_ZETA_ZH`-gated) — the generator-procedure suspend path, emitted only via `bb_call_proc_staged` gen arms + Prolog `by_name_dispatch` worker calls. SNOBOL4 lowering emits none (Lon s50 all-stack ruling holds: determinate DEFINE fns, no coexprs). Empirical: define-heavy pattern program under `SCRIP_ZH_TELEM` = zero `[ZH]` lines. **Consequence: HZ-1 heap-RESIDENCE plumbing (FR→block-base translation) is Icon/Prolog-owned work; the SNOBOL4 side of HZ-1 is CLOSED by census.** The unification target stands as: rt_ws (title-worded Region-2 workspace, now fed by the sweep) + gc_heap (collected value world) consolidate under `gc_collect_ex` at GC-U-6/7/8; rbx = the live frontier (REG-4b).

**PRE-EXISTING, not-s83, recorded for honesty:** `test/snobol4/patterns/zb_act_arbno_in_define.sno` aborts rc=134 ("stack smashing detected") at origin `98029a79` — worktree-bisect-proven pre-existing; outside crosscheck+smoke gates; ZB-ACT family is SUPERSEDED per PLAN.md s64 ruling. Route with Lon: delete with the superseded ladder, or hunt monitor-first if the family resurrects.
