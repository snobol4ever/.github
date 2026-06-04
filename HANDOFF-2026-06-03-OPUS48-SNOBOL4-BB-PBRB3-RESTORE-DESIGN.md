# HANDOFF 2026-06-03 (Opus 4.8, session 3 cont.) — PB-RB-3-RESTORE design: bb_match/bb_subject rebuilt on registers, 3-piece port-mapped decomposition (DESIGN ONLY — no code landed; tree green at SCRIP `a6bc843`)

## Why design-only

bb_match restoration was attempted this session after the regression discovery (see the PB-RB-3 `[~]` note in
GOAL-SNOBOL4-BB.md + SCRIP `a6bc843`). The original working body was RECOVERED from git
(`git show 706d665:src/emitter/BB_templates/bb_match.cpp` — full byte-level doc comment intact) and the new-API
design fully worked out, but remaining context could not absorb the integration surface + an x86 debug cycle
(REX.B precedent). Stopped at green. THIS DOC is the implementation spec; everything below was verified against
the live tree this session except the two VERIFY-FIRST items.

## Recovered reference semantics (`706d665` bb_match, LEGACY model — do NOT copy the storage, copy the algorithm)

α: Σ←[r12+subj] → movabs &Σ store; Σlen←[r12+subj+8] → movabs &Σlen store; r10←&Δ; start ζ-slot ←0 (ch.18 step 1).
match_retry: Δ(cursor)←start via [r10]; jmp elem_entry.
match_advance (element-ω target): inc start; cmp start,Σlen; jg→ω; kw_anchor (int64) nonzero jne→ω; jmp match_retry.
β: jmp ω (statement-level single-shot; within-pattern backtrack is the elements' own β/ω).
Element wiring (driver): walk_bb_flat(elem, lbl_γ, match_adv, elem_β) — elem γ exits MATCH to statement success
directly; elem_β is DEFINED by the element's own `def PORT_BETA` (nobody jumps it in single-element match).

## New design — registers (REG-0), 3 pieces from ONE IR_PAT_MATCH node, ports remapped per FILL

Key trick (verified: flat_drive_cat already maps kids' ports to arbitrary driver labels): a template emits ONLY
PORT records; the DRIVER chooses each emission's γ/ω/β targets. So no external-label vocabulary is needed:

- **piece 0 HEAD** (ports: γ→match_retry, ω→lbl_ω, β→lbl_β):
  `mov r13, FRQ(sa)` (Σ base, qword) · `mov r15d, FR(sa+8)` (Δ length) · `mov FR(start), 0` ·
  `jmp PORT_GAMMA` · `def PORT_BETA` · `jmp PORT_OMEGA`
- driver: `emit_label_define_bb(match_retry)`
- **piece 1 RETRY** (ports unused): `mov r14d, FR(start)` — FALLS THROUGH into the element (driver emits element
  immediately after; no elem_entry label needed at all).
- driver: `walk_bb_flat(elem, lbl_γ, match_adv, elem_β)` · `emit_label_define_bb(match_adv)`
- **piece 2 ADVANCE** (ports: γ→match_retry, ω→lbl_ω): `add FR(start), 1` · `mov eax, FR(start)` ·
  `cmp eax, r15d` · `jg PORT_OMEGA` · kw_anchor: `x86_load_ro("rcx","kw_anchor",(uint64_t)&kw_anchor)` ·
  `cmp qword [rcx], 0`-form · `jne PORT_OMEGA` · `jmp PORT_GAMMA`

Sub-kind dispatch: ONE bb_match template branching on a `_` int field (suggest `op_ival` ∈ {0,1,2}; driver sets it
before each FILL). start-slot offset: driver claims ONCE (`bb_slot_alloc16(pBB)`) and promotes via `op_off`
(promote-at-dispatch pattern, as walk_bb_flat IR_VAR does); subject-slot offset via `op_sa` from `g_subject_slot`.
Do NOT use bb_slot_claim inside the template for start — the slot must be SHARED across the 3 emissions, so it is
DRIVER-claimed. Template style: span skeleton (`IF(MEDIUM_TEXT, s_1asm(_.lbl_α":")+s_comment(...))` cosmetic only;
pure x86() instructions otherwise — medium-invisible).

- **bb_subject** (IR_SUBJECT): driver reads nd->α (IR_LIT_S for the probe; IR_VAR arm later) at dispatch —
  emit-time IR reads in the DRIVER are sanctioned; promote sval/len; `sa = bb_slot_alloc16(nd)`;
  `g_subject_slot = sa`. Template: `x86_load_ro("rax","??", ptr)` · `mov FRQ(sa), rax` ·
  `mov FR(sa+8), (long)len` · `jmp PORT_GAMMA` · `def PORT_BETA` · `jmp PORT_OMEGA`.

## Integration checklist (every site, verified on tree except *)

1. New files `src/emitter/BB_templates/bb_match.cpp`, `bb_subject.cpp` (genuine x86(), per STUB-CLEANUP rule).
2. Dispatch arms for IR_PAT_MATCH / IR_SUBJECT (*VERIFY-FIRST: locate the kind→bb_* switch — it is NOT in
   emit_core.c by grep; check emit_core.cpp / walk_bb_node FILL path; mirror however bb_gen_scan (d46b943, the
   newest box) was wired — that commit is the wiring template).
3. Declarations in `bb_templates.h`.
4. BOTH build lists: Makefile libscrip_rt sources + build_scrip.sh (the giant explicit file lists).
5. `flat_drive_match` rewrite (emit_bb.c) per the piece sequence above; `flat_drive_subject` gains the
   promote+claim; un-orphan `g_subject_slot`.
6. Probes: existing `_3_match`/`_3_match_fail` should go green unchanged (they build IR_SUBJECT+IR_PAT_MATCH).
   Then PB-RB-4 probes: ALT('q','b') over 'abc' (2nd-alternative within-position) + CAT('a','b') over 'aab'
   (right-ω→left-β inner backtrack) — flat_drive_alt/cat verified present and port-correct this session.

## VERIFY-FIRST (the two unconfirmed mechanics — check before writing code)

- **FRQ qword form**: x86_asm.h has `x86_frameq` overloads (lines ~396-402) but the constructor name was not
  read (FR() at :315 is the dword x86_frame). Confirm the qword constructor + that `mov r13, FRQ(off)` encodes
  REX.W+B correctly (the REX.B class of bug lives exactly here).
- **EMIT_PAIR_FILL multi-emission on one node**: PB-RB-8's `bb_fill_alpha` fix made the `bb%d_α` self-label
  per-EMISSION-unique, which implies re-emission is supported — confirm `_.lbl_α`/pair state fully resets per
  FILL (EMIT_PAIR_RESET between pieces) and that nothing else keys on the node pointer per-emission.

## Gate plan

m2 7/7 HARD held every step (this path is mode-3 JIT only — m2 untouched by construction); Icon m2 12/12;
pat-bb probe suite 3/3 then 5/5; prove_lower2 67; no_bb_bin_t 0; medium-invisible (new boxes must NOT need the
bb_scan_stmt exemption); REG-FENCE TIER1=0. On green: flip PB-RB-3 `[~]`→`[x] RESTORED`, flip REG-0 `[x]`.

## Tree state

SCRIP local `a6bc843` (probe rename sweep) on `454d9ff` (scan guards) on origin `991a26b` — NOT pushed.
.github local `86e08c4a` + this doc — NOT pushed. All gates green at `a6bc843` (m2 7/7 / m3 6/6 / m4 6/6,
Icon 12/12, prove_lower2 67, no_bb_bin_t 0). Push on Lon's handoff phrase.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
