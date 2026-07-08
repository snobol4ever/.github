# HANDOFF 2026-07-08 (cont. 4) — DEF-α AUDIT + ZLS2 FRAME PROTOCOL AT THE PORT SEAM

**Repos at handoff:** SCRIP main = `29baf0bb` (= `3f5c4a15` def-α + `29baf0bb` protocol); corpus = `97dcd400`
(unchanged — artifact regen produced ZERO diffs, the third independent proof of default-flags byte-identity);
dot-github = this commit. **Watermark unchanged:** m3 252/24, m4 251/9/16, DIVERGE=1 (1017_arg_local),
fail-sets character-identical to the record — proven at default, PORT=2, and rbp+PORT=2 (poison compiled-default
throughout); PORT=1 canary smoke-checked.

## What landed

**1. DEF-α AUDIT (Lon: "Ensure all active templates are using x86(\"def\",\"α\")").** Per-return-ARM,
function-granular audit over the 117 Makefile-live templates. 82 scoped fixes: 80 mechanical
`return x86_bomb(` → `return x86("def", "α") + x86_bomb(` across 44 files, applied ONLY inside 57 entry
functions first proven concat-safe (returned whole / dispatched, never concatenated — adding a def to a
concatenated helper would double-define), + bb_subject's two ternary bomb branches by hand. `x86_bomb`
itself stays def-less (used mid-string in marshal helpers). Verified-dead and skipped: bb_every / bb_ite /
bb_case_arm (0 dispatch call sites), bb_scan_stmt (not in Makefile); bb_repalt differently-driven (α lives
in bb_repalt_clear). The added defs matter only when a bombed node's α is referenced (closes the
unresolved-forward-ref emit abort class); byte-identical watermark proves no live corpus program affected.

**2. ZLS2 FRAME PROTOCOL INJECTED AT THE PORT SEAM (Lon: "Remove the x86_port_mode function and all its
usage in a top-level template function. That is not allowed in a template. The templates stay untouched for
this entire operation.").** The ZC_PORT_ALLOC arms of bb_match_arb + bb_match_arbno roles 0/1/2
(state-in-block, hand-placed push/load/pop) are DELETED — a template never branches on a flavor axis
(R2's sibling; `x86_port_mode` survives only inside x86_asm.h encoders/hook, the sanctioned seam).
Activation STATE stays in the static graph-frame quad in every mode; the state-in-block re-entrancy design
retires unexercised (same-node nesting needs DP-7 — the standing HONEST SCOPE caveat).

Under `SCRIP_ZETA_PORT=2`, **x86_port_hook injects the whole protocol at the templates' existing port
calls**, keyed on per-node **zls2_geom** grants (zeta_storage.c — the save-slot layout authority; the
former template-private K constants live there now):

- **BUMP** at the α define — `rt_zls2_push(K)`, prev-chain via the save slot, store block to slot.
- **RESTORE** at the β define — `rt_zls2_release_to(block)`: a β define IS the backtrack arrival, and one
  cursor reset reclaims every failed successor's frame. This is the FAIL-DIRECTION release — a mid-pattern
  node's exhaust ω lands on its predecessor's β, and it is THAT restore which frees the exhausted frame
  (stack discipline: reclamation belongs to the frame you fail INTO). Idempotent; the runtime hard-aborts
  on LIFO violation (a free assert).
- **RELEASE** before jmp-ω — unchain + `release_to(block+K)`, granted ONLY to roles whose ω-jumps are
  STATICALLY all activation-death (ARB's single exhaust ω; ARBNO role 2's outer-fail ω). **THE GRANT IS
  THE ω-DEATH CLASSIFIER** — role knowledge from the one layout authority. `op_omega_is_death` is never
  consulted (recorded broken — arbno L(9) note: an IR_MATCH_HEAD sharing the chain window makes role 2
  look resolved), and the six-decoy-ω trap cannot fire because aliased roles (ARBNO 0/1) carry no RELEASE
  grant.

γ carries no frame arm (success hands the live frame down) but the seam fires there — trace, assert, and
alternate GC schemes later are one hook arm each, zero template edits, both mediums free.

New machinery: `zls2_geom` (zeta_storage.c/h) · `ZLS2_BUMP/RESTORE/RELEASE` (zeta_choices.h) ·
`op_zls2_slot`/`op_zls2_ops` g_emit fields (DRIVE_FILL-inert; promoted at the walk_bb_node ARB/ARBNO
cases) · `x86_zls2_release_to_reg` encoder · hook body relocated below the zls2 helpers it calls
(fwd-decl pattern per x86_zeta_free_call). Dormant direct-sub α arm preserved, re-keyed
`bytes>0 && ops==0`.

## Bug found + fixed en route (worth remembering)

First zls2_geom wrote K=32 for the UNGRANTED ph1 before returning ops=0 — `bytes>0 && ops==0` is exactly
the dormant direct-sub arm's key, so ph1's α emitted `sub r12,32`: total frame corruption, 5 ARBNO tests
red. Fix: outputs written only when ops are granted. Lesson: the dormant arm's key is a live tripwire —
any future grant path must never leave bytes set without ops.

## Session-2 → session-3 design correction (recorded so it isn't re-litigated)

The first cut of this session modified the templates (hook-fired ALLOC arms + an `x86("free","ω")`
template-declared exit marker + an X86H_EXIT site). Lon corrected: templates stay untouched; route through
the port calls. The exit marker and X86H_EXIT are GONE — release rides the existing jmp-ω call, gated by
the role-static grant. The reason the template-marker approach was wrong: it accepts flavor-variance in
templates, the same disease as medium-branching; the port calls already mark every injection point and the
grant already knows what fires there.

## Verification (all fresh, final tip)

Default crosscheck byte-identical watermark THREE ways (results, re-run, artifact regen zero corpus
diffs). PORT=2 crosscheck watermark-identical. rbp+PORT=2 passes the full previously-failing ARBNO set
(052/070/075/117/W04). PORT=1 canary intact. `SCRIP_ZLS2_TRACE`: one push + one release per activation,
silent no-op restores under clean LIFO (release_to at cursor).

## NEXT (unchanged from the goal file, evidence strengthened)

(1) Lon to rule on flipping `ZC_PORT` default to ALLOC (bench run belongs to that ruling); (2) trampoline
retirement → rsp; (3) further consumers only WITH a live overlap exerciser (post-DP-7). See
GOAL-SNOBOL4-BB.md SESSION STATE for the authoritative list.
