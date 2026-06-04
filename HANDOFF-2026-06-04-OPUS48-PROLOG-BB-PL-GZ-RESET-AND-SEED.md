# HANDOFF 2026-06-04 (Opus 4.8) — PROLOG-BB: PL-GZ RESET + SEED LANDED

.github `e0f77b8b` (reset) + `b4c935c3` (PL-GZ-0 seed) + this handoff commit · **SCRIP untouched** at
`89c730c` (build artifacts only, not committed) · **corpus untouched**. No SCRIP code changed this
session — gates re-verified at session start on `89c730c`: GATE-1 m2 5/5 (m3 4/5 = known harness
artifact) · GATE-3 m2/m3 **115/115**, m4 **105/0/10** · one-box PASS · FACT greps 0.

## The directive (Lon, second 2026-06-04 session)

**Reset Prolog development to square one on the Proebsting-pure track.** Rationale: Prolog was
bootstrapped in the Stack-Machine era, so its GDE control lives in a C engine (resolution.c
env-swap / `last_ok` / cut-flag / heap-CP + the unification.c meta rail) and the boxes are call-out
shims. The morning's PL-M34 and PL-BBL directives were retrofit ladders onto that substrate — Lon's
call: don't retrofit, REBUILD seed-first, GDE inside the boxes from rung 1. "No one does it this way,
BUT WE DO."

## The evidence (measured this session)

Control-coupling C-call sites emitted per template:

| Box | calls | character |
|---|---|---|
| bb_pat_alt / bb_pat_arb / bb_pat_cat / bb_every / bb_alt | 0 | — |
| bb_pat_span / bb_scan_any / bb_scan_many / bb_scan_tab | 1–2 | VALUE (`strchr`) |
| bb_unify | 4 | VALUE-leaning (unify helpers) |
| **bb_goal** | **14** | CONTROL (env push/pop/install, `last_ok`, bind_arg, cp_save) |
| **bb_choice** | **24** | CONTROL (`resolve_cp_current` ×10, cut flag ×2, trail, cp push/pop) |

SNOBOL4/Icon: the GDE *is* the box. Prolog: the box calls a C GDE engine ten times per dispatch.
This is the number PL-GZ-1's gate ratchets to zero.

## What landed

1. **GOAL-PROLOG-BB.md restructured** (`e0f77b8b`): new 🔴 **PL-GZ** ladder — 0 seed → 1 coupling
   gate → 2 hello → 3 facts/unify → 4 choice → 5 conj+recursion → 6 cut → 7 ITE → 8 builtins →
   9 corpus reconquest → FENCE. PL-M34 + PL-BBL **ABSORBED** (their laws are PL-GZ construction
   principles); PT + WAM-CP carry ⏸ **LEGACY** banners with a disposition table — survivors: PT-0
   predicate table, PT-4b's B-full LAW, PT-3's CP-truncate/ball-copy LAW, CP-7 unify
   specializations; starve-and-delete: the meta rail (at PL-GZ-9); post-FENCE optimization tier:
   CP-8 indexing, CP-11/12, PL-INDEX-L2-1. All ten shared FACT RULE blocks verified byte-identical
   vs GOAL-SNOBOL4-BB.md / GOAL-ICON-BB.md before AND after the edit (extractor caveat: three
   blocks end in per-language trailers — the Prolog NO-RESURRECT subsection, the `**Repo:**`
   lines — which differ BY DESIGN; the shared bodies match).

2. **PL-GZ-0 ✅ `test_pl_1.c`** (`b4c935c3`): the first written-down Proebsting translation of
   Prolog — the paper (§4.6) never gave the procedure-call template and never gave ANY Prolog
   template. Program: `edge(a,b). edge(b,c). edge(b,d). path(X,Y):-edge(X,Y).
   path(X,Z):-edge(X,Y),path(Y,Z). firstpath(Q):-path(a,Q),!.` driven by the all-solutions pump
   then the cut query. Output **PINNED `b c d b`** across -O0..-O3, 20/20 runs byte-identical.
   Laws embodied, one per former PL-BBL ledger row: clause cursor + trail-mark in the choice's OWN
   frame row (ARBNO arena) · ζ-TREE activations (per-call-site child-frame slots, `enter()`-reset
   on α) · verdict IN THE RETURN VALUE (no `last_ok`) · **cut as PURE WIRING** (`firstpath_β: goto
   firstpath_ω` — one goto; the entire `rt_get_cut_flag`/`rt_choice_cut_*` global protocol
   vanishes in the lexical case) · trail = the one spine · C stack = the recursion spine.

## SEED → EMITTED PROJECTION (read before citing the seed)

C cannot jump to a label inside another function, so the seed prints cross-predicate α/β entry as a
C call — the SAME convention as test_sno_2/3/4.c. **This is NOT license for brokered
`(ζ, int entry)` boxes in src/** — that signature remains FORBIDDEN (NO C BYRD-BOX FUNCTIONS fact
rule). The mapping (now pinned in the seed's header comment):

| Seed C form | Emitted machine-code form |
|---|---|
| `v = path(&ζ->p2_ζ, α, …)` | `jmp path_α` (callee frame slots reset at α) |
| `v = path(&ζ->p2_ζ, β, …)` | `jmp path_β` |
| `return 1` / `return 0` + λ-test | callee jumps to the caller's γ / ω continuation |
| the `int entry` dispatch | does not exist — α and β ARE the two emitted labels |

## Findings / lessons

- **goto over a C initializer leaves the variable uninitialized.** `goto q2_α` jumped over
  `firstpath_t * q2_ζ = 0;` → garbage frame pointer → `enter()` memset a garbage address. The
  crash was stack-luck dependent (the -g build happened to work; plain -O0..-O3 builds crashed).
  Fix and law: frame-slot init belongs AT THE α LABEL, never in the declaration — which is where
  emitted boxes do it anyway. Recorded in the GOAL PL-GZ-0 entry.
- (carry-over, unchanged) corpus `.s` labels are generation-nondeterministic; suite set-diff is
  the invariant.

## Next (in order)

1. **PL-GZ-1** — coupling gate `scripts/test_gate_pl_coupling.sh` (baseline choice 24 / goal 14 /
   unify 4 / others ≤2; VALUE calls sanctioned — the strchr class; ratchet to 0). First SCRIP
   commit of the new track.
2. **PL-GZ-2** — hello (write/nl) on the new path: ONE x86() body per box, m2==m3==m4
   byte-identical, ONE shared admission gate, EXCISED counted identically in m3 and m4.
3. Do NOT open PT-4b or WAM-CP work — legacy; see the disposition table in the GOAL file.

## Risk notes for the successor

- The legacy m4 path remains the GATE-3 suite runner during reconquest; legacy counts must not
  regress; the new-path counter starts at 0 and only ratchets up.
- The m2 oracle ITE-commit bug STANDS until PL-GZ-7 (paper §4.5 is the canon; do not "fix" rungs
  to match the buggy m2 in the interim).
- The seed answers every former PL-BBL-0 classification in executable form — when a PL-GZ rung has
  a design question, read the seed first, then the paper; gprolog/swipl are PRINT oracles only.
