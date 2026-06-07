# HANDOFF 2026-06-07 OPUS48 — IR-REDESIGN: IRD-1 LANDED · IRD-2 VERIFIED · IRD-3 SCAFFOLDED

## Commits (SCRIP origin/main, post-rebase hashes)

- `6961de3` IRD-1 BREAKOUT: per-language lower split + canonical lower() signature
- `92422d9` IRD-1 drain: lower.c is pure spine — last cx.lang branches out
- `9fc612a` IRD-3 scaffold: operands/n_operands + ir_operand_push(); IRD-2 verified complete

Rebased over a PARALLEL session's `293b1d0` (IRD-1 closeout: prove_lower.sh
repaired, bb_label registry → spine) + FIXUP sweep commits. Merged HEAD
`9fc612a` re-verified after rebase: build green, icon 12/12 m2, prolog
5/5 m2, raku 25/25 m2, prove_lower 68 PASS, baselines byte-identical.

## NAMING CONTRACT (Lon directives this session — do not relitigate)

- AG signature, ratified: `IR_t * f(lcx_t cx, const tree_t * e, IR_t * γ,
  IR_t * ω, IR_ref_t * α, IR_ref_t * β)` — NO _in/_out suffixes.
- `lower` = the canonical new-signature dispatcher (lower.c):
  ICN→lower_icn · SNO/SCO/REB→lower_sno · RKU→lower_rku · PAS→lower_pas ·
  PL+default→role switch (lower_pattern/lower_goal/lower_value_shared),
  all wrapped through iref() (lower_internal.h: fills IR_ref_t{node,"α"/"β"}).
- `lower_program` = old-signature (IR_t** α/β) THIN UNWRAP WRAPPER over
  lower. Every legacy call site renamed lower( → lower_program( across
  lower_icon/sno/raku/pascal/internal + tools/tmatch_proto.c.
- `stage2_t * lower_program(const tree_t*)` → **lower_stage2** (name
  freed for the wrapper; 1 caller src/driver/scrip_sm.c). LON: flag if
  you want a different name.
- lower_value → lower_value_shared (pure shared TT dispatch, zero
  cx.lang); wire_if(cx, e, else_succeeds, ...) exported — shared passes
  0 (else→ω), RKU/PAS intercept TT_IF with 1 (else→γ);
  tt_is_relational/tt_to_binop exported; PAS bool-diamond moved whole
  into lower_pascal.c with b1/b2 checked BEFORE node alloc (preserves
  node indices → baselines identical).
- TT_LOOP_BREAK/NEXT now route to v_loop_break/v_loop_next (previously
  switch-break fallthrough = garbage return); baselines unaffected.
- lower_icon.c:479 fallthrough fixed → lower_value_shared.

## IRD-2 verification record

IR_t at HEAD carries NO sval/ival/dval/value/counter/state — lit[]/exec[]
sidecars, idx/own, IR_LIT/IR_EXEC macros pre-existed (prior session; the
goal file was stale). Audit greps: every ->ival hit in IR consumers is a
prolog `Term*` (different struct); ->value/->counter/->state outside
IR_EXEC = ZERO. IR_node_alloc sets idx/own, seeds exec.value=FAILDESCR.
IRD-5 lit/exec grep gates already pass.

## IRD-3 sizing (audited — consumers carry the bulk)

->α/->β touches: IR_interp.c 387 · emit_bb.c 320 · lower_icon.c 23 ·
lower_prolog.c 20 · lower.c 7 · lower_program.c 5 · lower_sno.c 2.
operand_aux call sites to fold+delete: 34. Each touch needs classifying
CHILD-OPERAND (→ operands[i]) vs PORT-WIRE residue (stays until IRD-4),
per op kind, against templates + jcon irgen.icn.

## ⚠ LON RULING NEEDED before IRD-4 closes

Ratified 5-member IR_t has no idx/own, but the sidecars key on idx and
IR_LIT/IR_EXEC walk own. IRD-5 "exactly 5 members" fence vs the sidecar
mechanism are in tension: either idx/own survive (7 members) or sidecar
access needs a different key.

## Known issues / environment notes

- scripts/test_lower_byte_identical.sh calls removed --dump-sm → the
  baseline baked this session is VACUOUS (every hash = empty-output
  md5). Rewrite to --dump-bb WITH ival-ptr masking, then rebake.
- bb_print emits the GCONJ ival heap pointer raw (IRD-2 debt: ival
  disguises bb_conj_state_t*) → prolog dump-bb baselines are
  ASLR-nondeterministic; mask: sed 's/ival=[0-9]\{12,\}/ival=PTR/'.
- Container setup: apt-get install -y libgc-dev before make.
- Broker gate not runnable here (csnobol4/swipl absent); substituted
  direct sweeps: sno feat 21/21 --interp, raku smoke 25/25, pascal x5
  (boolchain/boolassign/alias/m4wexpr/sieve) dump-bb AND --interp
  hashes byte-identical.

## NEXT

IRD-3 sweep, per-language commits in goal order: sno first. Per-language
helpers (sno_conj, v_raku_*, pas_*) migrate to the 5-param signature
during their own language's sweep — not as separate churn.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
