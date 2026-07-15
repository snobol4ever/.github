# FINDING 2026-07-15 — Icon: eradicate IR_MOVE_LABEL by making the BB hold its own state (IR_DISJUNCTION → nary self-state, IR_IF follow-on)

**Author:** Claude Sonnet (attended, Lon) · **Repo:** SCRIP · **Goal:** GOAL-ICON-BB.md
**Directive (Lon, 2026-07-15):** "Get rid of IR_MOVE_LABEL. Make the BB hold their own state variables. See how SNOBOL4 removed it. Make IR_DISJUNCTION almost like IR_MATCH_ALTERNATE." Kill MOST IR_MOVE_LABEL — only keep any use that is *absolutely* required (and none of Icon's is).

**Status:** ANALYSIS COMPLETE, not yet implemented. Main tree untouched/green. This note is the executable design for a fresh-context session (the refactor is coupled lowering+emission and needs full m3+m4 + suite + SNOBOL4-gate verification, which did not fit the session that found it).

---

## 1. The principle (why MOVE_LABEL is the wrong shape)

`IR_MOVE_LABEL` + `IR_INDIRECT_GOTO` implement multi-way resume by **writing a resume LABEL into a slot at runtime and computed-`jmp`ing to it**. That is state living in a *label indirection* instead of in the box. The Byrd-Box law (PER-BOX LOCAL STORAGE / "BB hold their own state") says every box owns its runtime state in its own frame (`[ζ+off]`) and a consumer reads a *fixed* producer slot. A runtime-varying label target is exactly the indirection that law removes. **MOVE_LABEL is the symptom of a box not holding its own state; the self-state nary form is the cure.**

SNOBOL4 already proved this out: **SN4-NARY-ALT** (Lon 2026-07-12, spec `seed/test_sno_1.c`). One `IR_MATCH_ALTERNATE` node with **2N operands = (entry_i, resume_i) pairs**; the "which alternative" state is `alt_i` in the node's **own ζ quad**, not graph structure; the SAVE+join triple (the MOVE_LABEL analog) was **DELETED**. `grep IR_MOVE_LABEL src/lower/lower_snobol4.c` == 0.

Icon has *already* done this for **scan** alternation: `IR_SCAN_ALTERNATE` → `bb_scan_alternate()` + the shared nary walker. `bb_scan_alternate.cpp` is the working Icon template embodiment (α saves the cursor, `alt_i` in `FR(op_off+24)`, β dispatches on `alt_i`, shared success-glue / fail-glue, ω = leftward exhaust). **This is the model to copy for `IR_DISJUNCTION`.**

---

## 2. Inventory — every Icon MOVE_LABEL / INDIRECT_GOTO (measured this session)

Producers in `src/lower/lower_icon.c`:
| Site | Construct | Nodes built | Emitted via |
|------|-----------|-------------|-------------|
| L826 | `lower_alt` (`\|` alternation) | `IR_DISJUNCTION` + per-arm `IR_MOVE_LABEL` | `bb_indirect_goto()` |
| L838/839/847 | `lower_if` (`if C then T else E`) | `IR_INDIRECT_GOTO` + `IR_MOVE_LABEL` (then, else) | `bb_indirect_goto()` |

Shared/out-of-lane: `src/lower/lower_prolog.c:718` also builds `IR_MOVE_LABEL` (Prolog goal's call — **do not touch from an Icon session**).

Emitter consumers (`src/emitter/emit.cpp`): `IR_MOVE_LABEL` ×8, `IR_INDIRECT_GOTO`/`IR_DISJUNCTION` ×2 (dispatch L810–811 + graph-walk lists L1586/1587, 1613/1614, 1755/1762, 1826).

**Conclusion:** Both Icon uses (alternation + if) are the indirection-instead-of-self-state anti-pattern; **neither is absolutely required.** The `IR_MOVE_LABEL` *kind* must remain declared only because **Prolog still produces it**; once Prolog is converted too, the kind can go.

---

## 3. Target IR shape for IR_DISJUNCTION (mirror IR_MATCH_ALTERNATE / IR_SCAN_ALTERNATE)

Current `lower_alt` (lower_icon.c ~820) builds `IR_DISJUNCTION` + one `IR_MOVE_LABEL` per arm carrying `(after-body-beta, disjunction, arm-result)` and a generator-flag ival. Replace with the SN4-NARY-ALT construction:

1. Build one `dj = build(cx, IR_DISJUNCTION, γ, ω)`; wire `dj.ω → ω`.
2. For each arm `i` (order per SNOBOL4): lower the arm with **succ = dj, fail = dj** (`lower(cx, arm_i, dj, dj, &res_i)`), capturing `entry_i` and `resume_i` (first node allocated during the arm's lowering, else `entry_i`).
3. Re-tag every edge allocated inside arm `i` that targets `dj`: `γ→dj` becomes success-glue tag **"σ"**, `ω→dj` (and a FAIL-goto's `γ→dj`) becomes fail-glue tag **"φ"** (byte-for-byte the SNOBOL4 loop, lower_snobol4.c ~1188–1206).
4. Push operands to carry per-arm state. **2N is not enough for value alternation** (see §4): push **(entry_i, resume_i, result_i)** — i.e. carry each arm's *result slot* node so the success-glue can route it. `IR_LIT(dj).ival = N`.
5. No `IR_MOVE_LABEL`, no `IR_INDIRECT_GOTO`.

---

## 4. The ONE real design point — value routing (this is why it's not a copy-paste)

Scan-alternation's value is a **uniform cursor-slice** (`rt_substr` computed identically for every arm in the success-glue — bb_scan_alternate.cpp L24–36). **General disjunction arms each produce their OWN value** (`1|2|3`: arm0=1, arm1=2, arm2=3). So the shared success-glue cannot compute one uniform value.

**Resolved by the "BB holds its own state" principle → OPTION B (per-arm copy dispatched by alt_i):**
- The disjunction box owns a **value slot** (`FRQ(op_off)`, `FRQ(op_off+8)`) and its `alt_i` counter (`FR(op_off+24)`), in its own frame.
- Each arm computes its value into **its own** result slot (not the parent's — cross-box writes violate the law; option "A" is rejected for that reason).
- **Success-glue** (the "σ" landing): dispatch on `alt_i` (a copy-variant of `scanalt_dispatch_chain`) to `mov` the succeeding arm's result DESCR (`FRQ(nd_slot(result_i))` / `+8`) → the disjunction's own slot (`FRQ(op_off)` / `+8`), then γ. Consumers then read the disjunction's fixed slot — no indirection, no MOVE_LABEL.
- α / β / fail-glue / ω are structurally identical to `bb_scan_alternate` (α: `alt_i=0`, enter entry_0; β: dispatch `alt_i`→resume_i.β; fail-glue: `alt_i++`, dispatch entry_{alt_i}.α or exhaust→ω). Drop the cursor save/restore that scan needs (`FR(op_off+16)=r14`) — pure value alternation has no subject cursor to preserve.

---

## 5. Emitter wiring (exact sites)

- **New template** `src/templates/bb_disjunction.cpp` — `std::string bb_disjunction()` per §4 (structure cloned from bb_scan_alternate.cpp; success-glue = the per-arm result-copy dispatch, not rt_substr). Add decl to `bb_templates.h`, source line to the Makefile `RT_PIC_SRCS` (append at end of the Icon group, one line = one hunk).
- **Dispatch** `emit.cpp` L811: split `IR_DISJUNCTION` out of the `bb_indirect_goto` case → `case IR_DISJUNCTION: bb_emit_x86(bb_disjunction()); return 0;`. Leave `IR_INDIRECT_GOTO` on `bb_indirect_goto` (still used by `if`, pending §6).
- **Nary walker** — add `IR_DISJUNCTION` to the nary-kind lists so the walker treats it as an N-operand node with entry/resume/glue labels: L1101 case set, and the operand-walk conditions at L1591, L1617, L1643, L1774. (These currently name `IR_MATCH_{ALTERNATE,SEQUENCE,ARBNO}` + `IR_SCAN_{ALTERNATE,SEQUENCE}`.) NOTE: operand stride becomes 3 (entry,resume,result) for DISJUNCTION vs 2 for the others — the walker's pair-indexing must branch on kind or read `n_operands / stride`. Confirm the label-count math (success-glue def, fail-glue def indices) against the 3N layout.
- Remove the L1586/1587, L1613/1614, L1755/1762 `IR_MOVE_LABEL` operand-walk special-cases **only** once `lower_if` is also converted (§6) — until then they stay for `if`.

---

## 6. Follow-on — IR_IF (lower_if, same disease)

`if C then T else E` uses `IR_INDIRECT_GOTO` + two `IR_MOVE_LABEL` (then/else). Convert analogously: the branch box holds its own "taken branch" state; C routes to entry_then / entry_else; on the taken branch's success, copy that branch's result → the if-box's own slot; resume re-enters the taken branch's β. It is a 2-way self-state dispatch (selection by C's outcome rather than an incrementing alt_i). Do this AFTER IR_DISJUNCTION lands and is green — then Icon's `IR_MOVE_LABEL` producers hit **zero**, and the emitter's MOVE_LABEL special-cases can be deleted.

---

## 7. Verification gates (all must pass before "landed")

- `bash scripts/build_scrip.sh` + `make libscrip_rt` clean.
- Alternation probes m3 AND m4: `every write(1|2|3)`, nested `every write((1|2)|(3|4))`, generator-in-arm `every write((1 to 2)|(5 to 6))`, value read-through `x := (1|2|3); write(x)`.
- Full Icon suite ≥ baseline, zero regressions: `bash scripts/test_icon_all_rungs.sh --corpus <corpus>/programs/icon` (clean baseline = **242/15/32 at SCRIP `b404fb95`**, the R12-frame default; on HEAD the RSP-frame flip masks 38 tests — see the regression note below).
- Icon gates: `test_gate_icn_no_stack.sh`, `test_gate_icn_one_reg_frame.sh`, `test_gate_icn_semicolon_required.sh`, `test_smoke_icon.sh`.
- **SNOBOL4 non-regression** (the walker is SHARED): `test_smoke_prolog.sh`, the SNOBOL4/Prolog crosscheck + emitter gates — because §5 edits `emit.cpp`'s shared nary walker. Prove SNOBOL4's `IR_MATCH_ALTERNATE` byte-identical before/after.

---

## 8. Related session finding — the RSP-frame Icon regression (context for gate baselines)

Measured this session: Icon is **242/15/32 at `b404fb95`** but **204/53/32 at HEAD `96fb698c`**. The 38-test delta is collateral from `f7de3863` (R12-ERAD s65) flipping the shared per-box frame default ζ=r12 → RSP/FORTH; that session's own s65 handoff records ALTERNATE-containing statements "correctly broken until the ALT-lift" follow-on. **The regressed Icon population is NOT top-level `|`** (`IR_DISJUNCTION` — measured working at HEAD) — it is the scan-family and complex generator/reflection paths that the RSP migration hasn't covered for Icon yet. That recovery is the R12-ERAD session's to complete (shared/SNOBOL4 territory; Icon's DO NOT list). The IR_DISJUNCTION refactor in this note is **frame-model-orthogonal** (uses FR/FRQ, which abstract the base) and rebases forward cleanly. Do the DISJUNCTION work from the clean `b404fb95` base for an unambiguous suite signal.
