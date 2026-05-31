# STUDY — JCON / ICON vs SCRIP control flow, feature by feature (Opus 4.8, 2026-05-29)

**Plan-only. Produces no bytes, changes no behaviour.** It turns a full read of the two
reference implementations into checkable rungs under IBB-9 in `GOAL-ICON-BB.md`. Every claim
below was verified against source this session, not against the GOAL doc's self-description —
which, as Section 0 shows, has drifted from the live tree.

**Sources read in full:**
- `jcon-master/tran/irgen.icn` (1559 lines) — the `ir_a_*` four-port wiring procedures. Read:
  `ir_a_Every` (309), `ir_a_While` (1008), `ir_a_Until` (981), `ir_a_Repeat` (847),
  `ir_a_If` (577), `ir_a_Binop` (472), `ir_binary` (430), `ir_augmented_assignment` (417),
  `ir_conjunction` (405), `ir_a_ToBy` (1168), `ir_a_Alt` (167), `ir_a_Compound` (1231),
  `ir_a_Limitation` (113), `ir_init_loop` (1435).
- `jcon-master/tran/ir.icn` — IR-node vocabulary (`ir_chunk`, `ir_Goto`, `ir_IndirectGoto`,
  `ir_Succeed`, `ir_OpFunction`/`ir_opfn` with its `failLabel`, `ir_MoveLabel`, `ir_ResumeValue`).
- `icon-master/src/runtime/ocomp.r` — canonical Icon's numeric/string comparison operators.
- SCRIP live tree (SCRIP `c7529bad`): `src/lower/lower_icn.c`, `src/emitter/emit_core.c`,
  `src/emitter/BB_templates/{bb_if,bb_seq,bb_every,bb_suspend}.cpp`.

Port correspondence used throughout: JCON `start/resume/success/failure` = SCRIP `α/β/γ/ω`.

---

## 0. The live tree has drifted from `GOAL-ICON-BB.md` (read this first)

The IBB-9 section of the GOAL doc describes an `emit_bb.c` architecture with `flat_drive_while`
(claimed at `emit_bb.c:1029`), `flat_drive_seq`, and `flat_drive_binop_tree`. **None of those
functions exist in the live tree.** The Icon BB emitters were refactored into per-kind templates
in `src/emitter/BB_templates/` dispatched from `emit_core.c`. Verified current state:

| GOAL doc says | Live tree (`c7529bad`) actually does |
|---|---|
| `flat_drive_while` (emit_bb.c:1029), JCON-faithful, cond doesn't gate | **`flat_drive_while` specifically does not exist** (only this one); `BB_WHILE`/`BB_UNTIL` had no `walk_bb_flat` case and fell to `default:` (degenerate skip). `flat_drive_seq`/`flat_drive_binop_tree` DO exist at the cited lines. IMPLEMENTED 2026-05-29 (Opus 4.8): added `flat_drive_while` (relop-cond while/until) — gate reuses `bb_if` bytes; corpus 56→57, 0 regressions. |
| `flat_drive_seq` is a node-keyed CFG BFS that special-cases `BB_IF` and keeps outer `lbl_ω` to avoid an operand double-walk SEGV | `bb_seq.cpp` is a clean template whose header states both γ and ω advance to the next statement (JCON compound semantics). The BFS/special-case is gone — **this divergence is already closed** (Section 4). |
| `flat_drive_binop_tree` (emit_bb.c:805) | Not present under that name; `bb_binop.cpp` handles the AG-pure relop arm. |
| `bb_if.cpp` router (IBB-8b) | Present and confirmed: `bb_if_str` emits `rt_pop_void; rt_last_ok; test eax,eax; jz ω; jmp γ` — a **flag-testing router** (Section 1). |

**Consequence:** the IBB-9-2 plan as written ("find `flat_drive_while` at line 1029; detect the
tree-shape relop by opcode; add a bespoke router") targets code that no longer exists, and its
core instinct (add a second router) is the wrong direction per Sections 1–2. The rung is rewritten
in `GOAL-ICON-BB.md` against the live tree.

---

## 1. The spine: a relational operator is NOT a boolean (verified three ways)

Every Icon control construct rests on one fact: **comparisons succeed (yielding a value) or fail;
they never return true/false.** All three implementations agree, and SCRIP is the only one that
reifies a boolean.

**Canonical Icon** (`ocomp.r:10-42`): each comparison is declared
`operator{0,1} icon_op func_name(x,y)` — a generator producing *zero or one* results — and its
body is literally `return C_integer y;` on a hit and `fail;` on a miss. There is no boolean. The
"result" of `i <= 3` is either the value `3` (success path taken) or nothing (failure path taken).

**JCON** (`ir_a_Binop:472`, `ir_binary:430`): relops `< <= = ~= >= > == ~== === ~=== << <<= >> >>=`
are all in the `funcs` set (480-484). The success chunk is
`ir_opfn(target, op, args, failLabel = right.resume); goto ir.success`. `ir_opfn` builds an
`ir_OpFunction(... failLabel)`. When the operator fails, control transfers to `failLabel`; when it
succeeds, control falls into `goto ir.success`. **The operator routes control; nothing tests a
returned value.**

**SCRIP** (`lower_icn.c`): a relop lowers to `BB_BINOP` with `state = is_relop`. In `if`-context
it is built AG-pure by `lower_icn_new_If_ag` (389-427), which wires `cond.γ = cond.ω = BB_IF`
and `BB_IF.γ = then`, `BB_IF.ω = else`. The relop arm (per IBB-8b) calls `rt_acomp`/`rt_lcomp`,
sets a global `LAST_OK`, and unconditionally `jmp γ` to the `BB_IF` node. `bb_if.cpp` then emits
the router: `rt_pop_void; rt_last_ok; test eax,eax; jz ω; jmp γ`. **SCRIP turns the comparison
into a flag and adds a node whose only job is to test that flag.**

This works for `if` because `BB_IF` is exactly that router. It breaks for every other context
(`while`, `until`, `case`, expression-position relop) because there is no equivalent router —
which is why `BB_WHILE` currently falls through to `bb_alt` and the cond never gates.

```
                   condition "i <= 3"
  canonical Icon:  operator{0,1}: return y   (success edge)  |  fail   (failure edge)
  JCON:            ir_opfn(<=, [i,3], failLabel) — fail→failLabel, success→fallthrough
  SCRIP:           rt_acomp; set LAST_OK; jmp BB_IF;  BB_IF: test LAST_OK; jz else; jmp then
                   └────────────── extra node + extra flag the references do not have ─────────┘
```

---

## 2. Why if and while are the *same* problem in the references — and different in SCRIP

In JCON, condition handling is identical across `if`, `while`, `until` — the construct simply
chooses where the two intrinsic edges of the condition go:

| Construct | `cond.success →` | `cond.failure →` | body.success/failure → | source |
|---|---|---|---|---|
| `ir_a_If`    | `then.start` | `else.start`   | (then/else)→if.success/failure | irgen 596-619 |
| `ir_a_While` | `body.start` | `ir.failure`   | `expr.start` (re-test fresh)   | irgen 1024-1031 |
| `ir_a_Until` | `ir.failure` | `body.start`   | `expr.start`                   | irgen 1000-1006 |
| `ir_a_Repeat`| (no cond — body only) | — | `ir.start`            | irgen 856-863 |

The only inter-construct difference is the *destination* of the two condition edges (and whether
body loops to `start` vs `resume` — see Section 3). The condition itself is wired identically and
needs no per-construct logic, because the relop already carries its own success/failure edges.

SCRIP cannot reuse `if`'s mechanism for `while` because that mechanism is a *node* (`BB_IF`), not
a property of the relop. So today `while` has no gate at all.

**Better way (the IBB-9-2 redesign).** Make the relop carry its own edges, as the references do.
Two landing options, sequenced as rungs:

- **IBB-9-2 (immediate, low-risk): lowering-side unification.** Lower `while`/`until` conditions
  through the *same* AG-pure path `if` uses (`lower_icn_new_Binop_ag`), and give `BB_WHILE`/
  `BB_UNTIL` a driver that reuses the proven `bb_if` flag-test as its loop gate:
  `cond(AG-pure, sets LAST_OK) → gate(test LAST_OK: true→body, false→exit) → body → cond`.
  This unblocks while/until now, reuses audited bytes, needs **no opcode-detection**, and stops
  routing loops through `bb_alt`. It is still flag-based, but it is correct and incremental.
  - *Regression note carried from the GOAL doc, now explained:* a non-relop cond
    (`while line := read()`, `while c := a[i]`) signals truth via its **own γ/ω** and sets no
    `LAST_OK`. The gate must fire **only** when the lowerer marked the cond AG-pure-relop; an
    unconditional gate is what regressed 26 read-loop programs. Because option IBB-9-2 decides
    relop-ness *in the lowerer* (which built the node and knows `state==is_relop`) rather than by
    sniffing opcodes in the emitter, the marking is reliable.

- **IBB-9-RELOP-PORTS (deferred refactor, fully reference-faithful): emitter-side port routing.**
  Bake the branch into the relop template itself — `rt_acomp/rt_lcomp; jz ω; jmp γ` — so the relop
  routes control through its own γ/ω with no `LAST_OK` and no router node. Then `if`/`while`/
  `until`/`case` all simply wire `cond.γ`/`cond.ω`, the two relop shapes (AG-pure vs tree) collapse
  to one, and `BB_IF` can be retired for the relop case (kept only where a real value must be
  tested, if any remain). This is canonical Icon's `operator{0,1}` and JCON's `failLabel` exactly.
  Bigger blast radius (touches `bb_binop.cpp`, the `lower_icn_new_If_ag` funnel, and the BB_IF
  dispatch), so it follows once IBB-9-2 has the corpus stable.

---

## 3. every vs while: the body→resume vs body→start distinction (and an every gap)

The GOAL doc's one accurate structural claim: the loop family differs only in where body-success
routes. Verified:

- `ir_a_Every` (327-331): `body.success → expr.RESUME` and `body.failure → expr.resume` — pull the
  **next generator value**. `expr.success → body.start`, `expr.failure → ir.failure`.
- `ir_a_While` (1027-1031): `body.success → expr.START` and `body.failure → expr.start` —
  **re-evaluate the condition fresh.**

That single edge (`resume` vs `start`) is the whole every-vs-while difference.

**every gap for IBB-9-4/9-5.** JCON gives the generator `expr` and the do-`body` *separate* port
sets and routes between them (`expr.success→body.start`, `body.success→expr.resume`). SCRIP's
`bb_every.cpp` pumps a single `pBB->α` and wires `body.γ→outer_α`, `body.ω→outer_γ`,
`outer_β→outer_ω`; its own header admits this is "the simplest correct shape" and collapses
generator-resume and body-execution onto one sub-graph. That is fine for `every GEN` (no do-body)
and for the IBB-9-1 static-assign special case, but `every GEN do BODY` with a real, possibly
generator-bearing body (ival≥2/3) needs JCON's two-port split so that body-success re-pumps the
generator's **resume** rather than restarting it. IBB-9-4/9-5 should adopt the expr/body split
(generator sub-graph and body sub-graph as distinct boxes, `body.γ → gen.β`) instead of extending
the single-α phase machine.

---

## 4. Compound `{...}`: already aligned (no rung needed)

JCON `ir_a_Compound` (1231-1260): non-last statements wire **both** `L[i].success → L[i+1].start`
**and** `L[i].failure → L[i+1].start` (a failed statement in a block simply advances; failure is
swallowed in statement context). The last statement carries the block's value:
`L[-1].success → ir.success`, `L[-1].failure → ir.failure`. Each non-last statement is bounded
(no resume port).

SCRIP `bb_seq.cpp` header (lines 4-6) states exactly this: "Each child statement's γ AND ω point
to the NEXT stmt's entry … success or failure both advance, no backtracking across stmts." The
IBB-8b-era `flat_drive_seq` BFS-with-`BB_IF`-special-case (which the GOAL doc still describes) has
been replaced by this template. **This divergence is closed; do not re-open it.** The only residue
is the `bounded` distinction (Section 5).

---

## 5. The one structural idea SCRIP still lacks: `bounded` (resume-port elision)

In every JCON procedure the resume chunk is emitted under `/bounded &` — i.e. **only when the box
is used in expression/generator context.** A box in statement context (`bounded` true) gets no
`resume` chunk at all. This is how JCON avoids building backtracking machinery for code that can
never be resumed, and it is the hinge for unbounded expression-context generators: `ir_a_If` (596),
`ir_a_Alt` (183-188) emit `ir_MoveLabel(t, arm.resume)` + `ir_IndirectGoto(t)` *only* in the
unbounded case — the computed-goto continuation.

SCRIP builds a β port uniformly regardless of context. The GOAL doc already names this as deferred
IBB-9-8 ("the `bounded` flag SCRIP currently ignores"); this study confirms it is the same single
mechanism behind unbounded `if`/`alt`/`case` resumption, and that nothing before IBB-9-8 needs it.
No new rung — just the confirmation that 9-8's scope is correctly drawn.

---

## 6. Feature-by-feature scorecard (SCRIP rung → reference procedure → verdict)

| SCRIP feature (rung) | Reference | Verdict |
|---|---|---|
| write / call (IBB-1,3) | `ir_a_Call` 360 | aligned for builtin write; user-proc dispatch (9-6) is the gap |
| binop arith (IBB-3) | `ir_a_Binop`/`ir_binary` 472/430 | aligned (value via opfn) |
| every-to (IBB-4) | `ir_a_Every`+`ir_a_ToBy` 309/1168 | aligned; SCRIP odometer ≈ JCON `closure`+`ResumeValue` |
| alt (IBB-5) | `ir_a_Alt` 167 | aligned (bounded); unbounded computed-goto deferred (9-8) |
| full / relop+nested gen (IBB-6) | `ir_a_Binop` + BINOP_GEN | aligned (odometer ≈ nested resume) |
| assign + var (IBB-7) | `ir_binary` `:=` 430 | aligned (`:=` ∈ funcs) |
| every x:=…do (IBB-9-1) | `ir_binary` `:=` resume-transparent | aligned; the doc's IBB-9-1 JCON claim checks out |
| DT_R write (IBB-8a) | runtime, not irgen | n/a (ABI/format fix; no reference divergence) |
| **relop in if-cond (IBB-8b)** | `ir_a_If`+`ir_a_Binop` | **divergent design** — flag+`BB_IF` router vs `operator{0,1}` edges (Section 1) |
| compound block (IBB-8c) | `ir_a_Compound` 1231 | **now aligned** (Section 4) |
| **while cond (IBB-9-2)** | `ir_a_While` 1008 | **broken in live tree** — routed to `bb_alt`; fix via Section 2 |
| until (IBB-9-3) | `ir_a_Until` 981 | inherits IBB-9-2 fix (inverse edges) |
| every do ival≥2/3 (IBB-9-4/5) | `ir_a_Every` 309 | needs expr/body port split (Section 3) |
| user-proc dispatch (IBB-9-6) | `ir_a_Call` 360 | not yet built; JCON arg-chain is the spec |
| unbounded resume (IBB-9-8) | `bounded` + `ir_MoveLabel`/`ir_IndirectGoto` | confirmed scope (Section 5) |

---

## 7. Net new/changed rungs landed in `GOAL-ICON-BB.md`

1. **IBB-9-2 rewritten** against the live tree: stop routing `BB_WHILE`/`BB_UNTIL` through
   `bb_alt`; lower while/until conds AG-pure and reuse the `bb_if` flag-gate. Gate fires only on
   lowerer-marked relop conds. Target `rung35_block_body_while_do_block.icn` → `1 2 3`, hold 216.
2. **IBB-9-3** clarified: inverse-edge twin of 9-2 in the shared driver.
3. **IBB-9-4/9-5** annotated: adopt JCON's generator/body two-port split, not the single-α phase
   machine, for `every GEN do BODY`.
4. **IBB-9-RELOP-PORTS (new, deferred refactor)**: retire flag+router for relops; relop routes via
   its own γ/ω as canonical Icon/JCON do; collapse the two relop shapes; retire `BB_IF` for relops.
5. **Doc-hygiene note**: the IBB-9 architecture references (`flat_drive_*`, `emit_bb.c:NNNN`) are
   stale; the live emitters are `BB_templates/*.cpp` via `emit_core.c`.
