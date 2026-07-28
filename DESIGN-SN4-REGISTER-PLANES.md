# DESIGN-SN4-REGISTER-PLANES.md — one physical stack, four planes, four registers
**Status: DESIGN + TRIAL MATRIX (Lon directive, s203 2026-07-28). Nothing implemented. Seeds cell_1..cell_6 are the prior art.**

## THE MODEL
ONE physical stack. Four planes that the s188-s200 bug family let move independently; the cure is that one cell carries all four and ONE cut restores all four.

| reg | plane | role | WAM | restored |
|-----|-------|------|-----|----------|
| RSP | DEPTH   | TOP — allocation frontier; moves only by carve (`sub rsp,K`) and cut (`mov rsp,rbp`) | H  | is the cut |
| RBP | CONTROL | CP — newest TURNING POINT (choice cell)                                              | B  | is the anchor |
| RBX | VALUE   | E — frame base of the current static-arity region; slots `[rbx+16k]`, k from SEQ/ALT arity | E | by the cut |
| R12 | UNDO    | MH — capture-mark chain head (SNOBOL4 `.`)                                          | TR | by the cut (free undo) |

r13/r14/r15 = Σ/δ/Δ (SNOBOL4 subject/cursor/length; free in Icon). No C runtime ⇒ full register file available; entry via own `_start` or C `main`, undecided.

CHOICE CELL = { resume, δ|TAG, prev_CP, prev_E, prev_MH } — 40B, pad 48 (or 32 pre-MH).
CUT = `mov rsp,rbp` + pops + `jmp` — control, depth, cursor, frame and trail arrive TOGETHER. Reach-over unrepresentable.
INVARIANT: rsp <= rbp always, equality immediately after a cut.

## WHAT PROEBSTING SETTLES (Simple Translation of Goal-Directed Evaluation, 1997)
- Four ports are CODE CHUNKS, not locations (§4). start/resume synthesized; fail/succeed inherited.
- **One temporary per AST operator, STATICALLY allocated. NO STACK ANYWHERE.**
- `ifstmt.gate` (§4.5) = an indirect goto for connections resolved at run time = OUR `resume` FIELD. We already had his machine; the stack is what we added.

⇒ **BOUNDARY CLAIM (to be proven or disproven by the matrix below):** a stack frame is required ONLY where one AST node can be live in SEVERAL INSTANCES AT ONCE — ARBNO/ARB/BAL instances, recursive stored patterns, procedure activations. Every singly-live node can keep Proebsting's static temp: no frame, no offset arithmetic, no allocation. This is exactly the s195-s200 bug family's membership; static slots worked for years because most nodes are singly-live, and broke precisely at the multiply-live class.
⇒ RBX is therefore NOT needed everywhere. Proebsting's model is the RBX-is-static special case.

## TRIAL MATRIX — one falsifiable claim per variant; `.c` is the original, `.s` are the trials
Rule: implement, run, diff vs `sbl` oracle (SNOBOL4) or the compiled `.c` (Icon). PROVED or DISPROVED, recorded either way. A disproof is a result, not a failure.

| seed | idea under test | prediction |
|------|-----------------|------------|
| `test_sno_1a.s` | Proebsting-pure: static per-node temps, NO frame register, no stack | **DISPROVE** — ARBNO instances collide on one temp. Establishes the boundary from below. |
| `test_sno_1b.s` | frame at EVERY BB + sibling chain (= cell_3 regime) | PROVE, but costs a link per unit — already shown in cell_3 |
| `test_sno_1c.s` | frame at TURNING POINTS ONLY (RBX set at choice pushes; E and CP collapse) | PROVE, cheapest — retires the saved-E field, SEQ returns to nothing |
| `test_sno_2a/b.s` | axis TBD — **`test_sno_2.c` NOT YET READ.** First act: read it, pick the axis, then write the claim here BEFORE coding. | — |
| `test_sno_3a/b.s` | axis TBD — **`test_sno_3.c` NOT YET READ** (33KB). Same rule. | — |
| `test_icon_a.s` | Proebsting-pure static temps, NO stack, for `every write(5 > ((1 to 2)*(3 to 4)))` | **PROVE** — every node singly-live, no recursion, no unbounded generator |
| `test_icon_b.s` | turning-point frames, same program | PROVE; compare instruction count + live bytes vs `a` |

⭐ **THE DECISIVE PAIR IS `sno_1a` (predicted FAIL) AND `icon_a` (predicted PASS)** — same mechanism, opposite predictions, both cheap. The boundary claim lives or dies exactly between them. Run these two FIRST; everything else is refinement.

## PRIOR ART IN `SCRIP/seed/` (all run, all oracle-checked)
cell_1 control only (K=0) · cell_2 UNIT cell + postfix + operand invariant · cell_3 sibling chain, ARBNO breaks static offsets · cell_4 full test_sno_1.c incl. `$ OUTPUT`, ladder byte-identical to sbl · cell_5 recursive stored pattern, CALL unit + CL · cell_6 SEQ/ALT PREFIX allocation, live frame 1056B→96B · test_icon_cell_1 Icon generators as RETAIN boxes.
⚠ cell_6 anchors allocation at SEQUENCE, which is NOT a control boundary (nothing ever returns to a sequence). `1c` moves the anchor to turning points, where "everything above here is garbage" is a FACT. Allocation boundaries should coincide with garbage boundaries.
