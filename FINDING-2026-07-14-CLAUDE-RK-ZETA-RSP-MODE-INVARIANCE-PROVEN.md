# FINDING 2026-07-14 (Claude Opus 4.8) — ζ-on-RSP two-flavor law is MODE-INVARIANT for SNOBOL4+Icon; Raku un-park planned (RK-ZETA ladder)

**Session type: DIAGNOSTIC. No code landed, no tracked file changed by the experiment.** The value of the
session is this finding + the RK-ZETA rung ladder now in `GOAL-RAKU-BB.md`.

## The directive (Lon, this session)
"Move all BB's ZETA to the RSP-topped FORTH-like stack, except so-called escapee-type BB's which go on the heap."

## Decode — this is the ARCH-ZETA §13 AMENDED TWO-FLAVOR LAW (already the design of record)
Not a new idea. §13 (Lon pivot s40, 2026-07-12) states it verbatim in spirit: **rsp spine = fixed cells only,
one per box (the non-escapees); escapable BBs' ζ + variable COLLECTION data heap-promote from birth (family A,
GC-visible), with γ/ω alloc/free overloads.** So:
- **"escapee" = family-A LIFO-breaker.** Canonical members (ARCH-ZETA §7/§8): Icon **suspend** frames + **coexpr**
  frames (a captured activation that OUTLIVES its creator's LIFO discipline) + the variable **COLLECTIONS** (ARBNO).
  For **Raku** the analogues are block/closure values carrying a captured ζ-env (RK-BLK) and EVAL/deferred thunks.
- Everything else rides the RSP FORTH spine (fixed cells).

## Config axes (verified in `src/.../zeta_choices.h` this session)
- **`ZC_ALLOC`** (activation allocator, BUILD CONSTANT): `BUMP_INFINITE`/`BUMP_LIFO`/`MALLOC`/`GC`.
  **Current default = `ZC_ALLOC_MALLOC`** (`zeta_choices.h:14`) — the ASan diagnostic (every block a real heap
  object; a wrong-ω free is caught loudly). Stack-with-LIFO = **`BUMP_LIFO`**.
- **`ZC_PORT`** (runtime): **default = `ZC_PORT_FORTH`** (`zeta_choices.h:97`) — the RSP FORTH spine port is
  ALREADY the default.
- Zero-edit mode swap (flags are NOT a make prereq — `rm` first):
  `rm -f scrip out/libscrip_rt.so && make ZCFLAGS='-DZC_ALLOC=ZC_ALLOC_BUMP_LIFO' scrip libscrip_rt`

## THE RESULT — the reusable finding (mode-invariance gate, SNOBOL4's own instrument)
Built `5ff8a92` clean. Ran `scripts/test_crosscheck_snobol4.sh` under BOTH allocators:
- **`MALLOC`** (baseline, all-heap): m3 PASS=304 FAIL=2 `{expr_eval, 141_pat_eval_double_fn_arbno}`;
  m4 PASS=303 FAIL=2 SKIP=1 `{expr_eval, 1017_arg_local}`.
- **`BUMP_LIFO`** (non-escapee ζ on RSP LIFO spine, escapees heap-promoted): **byte-identical** — same
  summary lines, same fail names, both modes. **DIVERGE = 0.**
- **Icon** (`test_crosscheck_icon.sh`) under `BUMP_LIFO`: **PASS=4 FAIL=0** — the suspend/coexpr escapee case
  holds on the LIFO spine.

**Conclusion:** the two-flavor law is **mode-invariant for the in-scope languages (SNOBOL4 + Icon)**. If any ζ
that must heap-promote were wrongly riding the LIFO stack, it would corrupt and the fail-set would diverge; it
does not. The flip `MALLOC → BUMP_LIFO` (i.e. moving non-escapee ζ onto the RSP FORTH spine, escapees to heap)
is **proven safe for SNOBOL4+Icon** — not asserted, measured. The 2 residual fails per mode are pre-existing
(identical under both allocators ⇒ NOT ζ-allocation bugs; unrelated feature gaps).

## THE METHOD to replicate for Raku (SNOBOL4's example, in order)
1. Bring up under **`MALLOC` + ASan** first — a wrong-ω free surfaces loudly with a trace instead of silently
   corrupting downstream.
2. Wire ω-free **construct-aware**, NEVER a universal `port==OMEGA` hook: `bb_match_arbno.cpp` emits SIX `jmp ω`
   and only the F-phase one is a true death; a universal hook fires `rt_zls_release` (snaps `g_zls_top` with no
   topmost-check) on live memory ⇒ silent free. Correct port model: **α=alloc+load+save, β=reload, γ=nothing,
   ω=free (construct-aware)**.
3. Flip to `BUMP_LIFO`; confirm the **mode-invariance gate** stays byte-identical (both modes).
4. Retire the compat shim (PARK-NEVER-DELETE → delete once green).

## OPEN BLOCKER (untouched by this diagnostic — it is an escapee-path issue)
`FINDING-2026-07-13-CLAUDE-SN4-DEFER-RSP-64KB-DONATION-IS-THE-BLOCKER.md` sits in the escapee/deferred-thunk
path — exactly the family that must heap-promote (RK-ZETA-2 relevant).

## DOC DRIFT to correct (STALE-ORIENTATION rule; source is truth)
`GOAL-IR-IMMUTABLE-EMIT.md` (lines ~163/370/1000) asserts `BUMP_LIFO` is the shipping default "since D15", but
`zeta_choices.h:14` reads `ZC_ALLOC_MALLOC`. Reconciliation: the newest box family is mid-bring-up under the
MALLOC-first discipline, so the default is temporarily MALLOC. The flat "BUMP_LIFO is default" claim has rotted
and should be corrected to "intended shipping default; currently MALLOC for the ASan bring-up of the FORTH-cell
family."

## Scope note
§13 DESCOPES Prolog/Pascal/**Raku** (alloc sites PARK behind a compat shim, PARK-NEVER-DELETE). SNOBOL4+Icon are
done+proven. Un-parking Raku = the **RK-ZETA ladder** authored in `GOAL-RAKU-BB.md` this session.

## Housekeeping
Nothing committed by the experiment; all three repos were clean throughout. Workspace binary was left as the
`BUMP_LIFO` diagnostic build (gitignored, regenerated on next `make` — the source default in `zeta_choices.h` is
unchanged MALLOC).
