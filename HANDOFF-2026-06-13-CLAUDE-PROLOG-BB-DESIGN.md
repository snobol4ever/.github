# HANDOFF 2026-06-13 — Prolog Byrd-Box design + PL-BB ladder

**Docs only. No code touched. HEAD was green at `521ab64` (GATE-1 5/5/5; m2 114/115, m3/m4 91/115, floor 91).**

## Landed this session
- `DESIGN-PROLOG-BB-ALL.md` — Proebsting-pure Byrd-Box design for ALL of Prolog. Four ports
  α/β/γ/ω as CODE CHUNKS; callee resumability is a CLOSURE VALUE (the `rt_enter` frame), re-driven
  from the caller's OWN β — NOT a port; `bounded` ⇒ no β/CP/closure; boxes ARE the engine (no WAM
  CP-stack loop, no bytecode dispatch, no C control engine/meta-rail). §1 control boxes, §2 det
  family (1 recipe), §3 DB, §4 catch/throw, §5 DCG (pure lowering), §6 excision, §7 bounded linchpin.
- `GOAL-PROLOG-BB.md` — PL-BB-0..6 rung ladder (before PL-GZ-9): test-first small→wide, LOWER (IR
  kind in lower_prolog.c) + EMITTER (BB template), gated GATE-1 5/5/5 HARD + ratchet floor, m3≡m4.
- `ARCH-PROLOG.md` — "Byrd-Box model" section: closure-as-frame, bounded determinacy, excision.

## The decision that drove it (δ/ε ABOLISHED)
`δ`/`ε` (`X86P_DELTA=4`/`EPSILON=5`, `PORT_DELTA/EPSILON`, `lbl_δ/ε`) were a 5th/6th port — illegit
per the four-ports FACT RULE. Canon proof: Proebsting composes boxes by `goto`-ing each child's OWN
four ports (`goto E1.start`/`goto E2.resume`); JCON `ir_a_Call` shows entering a callee is a `call`
returning a closure `(value, Resume())` and re-driving is `closure.Resume()` — a VALUE op from the
caller's β. So the two things SCRIP spelled as ports 4/5 are (a) a call-opcode target and (b) a
closure-resume — NEITHER a port. In SCRIP the closure IS the callee frame.

## Mechanism for the deletion (reverse-engineered, ready to cut at PL-BB-1)
Branches already resolve via `bb_emit_patch_rel32(bb_label_t*)` (both media). A port is just an id
0–5 into `x86_portlbl()`. The `F`/`xa_bb_emit_pair_jmp[]` record is the EXISTING port-free "branch
to a label object by index" pattern. Route the callee's own α/β label through a generic target
operand via that pattern; delete `PORT_DELTA/EPSILON`, the `X86P_*` cases, `lbl_δ/ε(+_p)`; rewire
5 templates (bb_cell_call/findall/ite, bb_query_frame, bb_callee_frame) + ~12 emit_bb.c driver writes.

## NEXT (fresh window — build-heavy)
PL-BB-0: add `bounded` to lower_prolog.c; bounded goals stop synthesizing β. Then PL-BB-1 (closure
β + delete ports 4/5). Gate each: GATE-1 5/5/5 HARD, floor 91, m3≡m4. Build: `make -j4 scrip &&
make libscrip_rt`; smoke `scripts/test_smoke_prolog.sh`; suite `scripts/test_prolog_rung_suite.sh`.

## BB inventory
Before: 26 modern (`bb_cell_*` 6 + `bb_det_*` 18 + frame 2) + ~16 legacy being retired.
Design: ~33 (control 8 + det 18 + DB 3 + catch 2 + frame 2; DCG 0). Adds disj/neg/assert/abolish/
retract+catch+throw modernization; reshapes all 26 (drop δ/ε, add bounded).
