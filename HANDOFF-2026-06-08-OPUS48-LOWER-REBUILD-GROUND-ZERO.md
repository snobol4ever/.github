# HANDOFF 2026-06-08 (Opus 4.8) — LOWER REBUILD, GROUND ZERO (Lon: "perform hand off")

## Pivot
Mid-session Lon pivoted off the IRD ladder to a **from-scratch ground-zero rebuild of the five
per-language LOWER functions.** Mandate: five segregated, isolated `lower_*.c` (SNOBOL4 ∪ Snocone ∪
Rebus as ONE language for lowering, Icon, Prolog, Raku, Pascal); mirrored file layout + parallel
function/case order so two scroll side-by-side with equivalent code at the same vertical position;
mutually-recursive switch-on-`TT_*` walkers; **NO language conditionals inside a file; NO sharing
between files; same names for the same things; everything `static` except the single `extern`
`lower_*()` entry.** Generated from scratch off the parser + `IR.h` (JCON `tran/irgen.icn` as the
Icon guide) — NOT salvaged from the old multi-file lowering.

## IR_t verdict
**IR_t needs NOTHING added** (Lon asked; verified by building Icon end-to-end). `op` selects the
construct; `operands[]` = all children/args (arity 0..N); `γ`/`ω` = all control wiring (SNOBOL
`:S`/`:F` gotos, Prolog success/backtrack, Raku NFA edges ARE γ/ω); `IR_LIT` (sval+ival+dval) +
`IR_EXEC` sidecars (keyed by idx/own) hold every payload (used sval+ival on one node already). Only
the per-file `cx` context grows (label tables, loop-exit continuation) — never `IR_t`.

## Four-attribute grammar (locked)
γ/ω = INHERITED (passed down as fn params). α/β = SYNTHESIZED. Under the slim IR_t, **α/β are no
longer fields — they are the node addressed at `sz="α"`/`sz="β"` inside someone's `IR_ref_t`.** So
the single returned `IR_t *` carries BOTH synthesized ports; the caller picks α vs β when it sets the
ref's `sz`. Hence `static IR_t *lower(cx, t, γ, ω) -> IR_t*` IS the four-attribute grammar correctly
expressed for the redesigned IR (not the old field-based shape with α_out/β_out).

## Architecture decided (vetoable)
1. **STRUCTURED marker nodes** — emit `IR_IF/WHILE/EVERY/…`, push lowered children as `operands[]`,
   wire the node's γ/ω to the continuations; the interp template owns each construct's internal
   control flow. (Alt = pure-CPS goto-flatten → would require rewriting the interp as a γ/ω-follower.
   Chose structured to keep the existing structured interp viable.)
2. **Generic `IR_BINOP` / `IR_UNOP` + operator lexeme in `IR_LIT.sval`** (Prolog: arithmetic are
   compound functors → `IR_STRUCT`). One arm per operator class; operator-as-data.
3. **Uniform arm shape**: alloc op / push children as operands / wire γ/ω / return.

## Files — WIP staging in `.github/lower-rebuild/` (SCRIP tree UNTOUCHED, still green)
`lower_icon.c` `lower_snobol4.c` `lower_raku.c` `lower_pascal.c` `lower_prolog.c`.
ALL compile clean (`gcc -c -std=gnu11 -fextended-identifiers` against `src/contracts` + `src/include`;
full -I list in `BUILD.md`). The header block (includes, `cx` typedef, `γ_to`/`ω_to`/`emit`,
`stmt_subj`, forward decls, `push_kids`/`lower_nary`/`lower_binop`/`lower_unop`) is byte-identical
across all five modulo the `cx` struct name + extern name; `lower_block` byte-identical in all five.

Ladder (same names/order in every file): `lower_<lang>` (extern) · `lower_decl` · `lower_block` ·
`lower` (dispatcher) + helpers.
`lower` switch band order: literals → names/field → arith-binary → arith-unary → rel-numeric →
rel-lexical → predicates → concat → csets → call/idx/section → list → {language band: SNOBOL pattern /
Prolog terms / Raku regex+io} → assign → generators → control → loop-ctrl → gotos → sequencing →
decl-delegation. Each file keeps only the arms its parser emits, in this order ⇒ side-by-side parity.

## Validation — Icon, graph-level, through the REAL parser
Harness `pipe_icon.c` links `icon_lex.o + icon_parse.o + lower_icon.o + scrip_ir.o + stmt_ast.o`
(provides `int g_jcon=0;` to avoid the runtime). Commands in `BUILD.md`.
- **rung 0**: parse `procedure main(); write("hello"); end` → `lower_icon` → `bb_print` ⇒
  `PROG → PROC(main) → CALL → [VAR "write", LIT_S "hello"]`. CORRECT.
- **rung 1 (sequencing)**: `write("a"); write("b")` ⇒ first `CALL` `γ=5α` (chains to the second
  `CALL`'s α). γ inherited threading CONFIRMED through the `IR_ref_t` `sz` carrier.
NOT yet done: the interp actually running the graph to stdout (the next chunk).

## KEY FINDING — statement convention (`src/driver/stmt_ast.c`; used by the Icon parser + `code_to_ast`)
`TT_STMT` carries `TT_ATTR` children `:lbl :lang :line :stno :subj :pat :eq :repl`, plus
`TT_GOTO_S/F/U` as direct children. Executable content = `stmt_attr_find(stmt,":subj")->c[0]`.
Public accessors in `stmt_ast.c`: `stmt_attr_find` / `stmt_attr_expr` / `stmt_attr_str`. All five
lowerers extract `:subj` via a static `stmt_subj()` helper. **SNOBOL rung climb hinges on this**:
`:pat`/`:repl` = scan-and-replace, `:eq` = match-replace marker, and the `:S`/`:F` goto children wire
directly onto γ/ω.

## Findings
- **`IR_CLAUSE` does NOT exist** in `IR_e`. Prolog clause → `IR_GOAL`.
- **`TT_COMPOUND` / `TT_ATOM` / `TT_UNKNOWN` are NOT real `tree_e` constants.** Prolog compounds =
  `TT_FNC` (c[0]=functor, c[1..]=args), atoms = `TT_QLIT`, vars = `TT_VAR`.

## Provisional arms (to confirm / drive via the rungs)
- **SNOBOL**: pattern family chosen `IR_PATTERN_*` (vs `IR_PAT_*`) — UNCONFIRMED which the
  interp/templates consume. `TT_STMT` goto-wiring (`:S`/`:F` → γ/ω + a label→node table) NOT yet
  implemented. `TT_CAT` → string concat `"||"`; pattern-context CAT unresolved. Captures →
  `IR_PATTERN_CAPTURE` with `ival` 0/1/2 (cond/immed/cursor).
- **Prolog**: `QLIT→IR_ATOM`, `NUL→IR_LIT_NUL`, `MAKELIST→IR_STRUCT`, `FNC→IR_STRUCT`
  (sval=functor, args=c[1..]). None verified.
- **Raku**: `REGEX_DECL`/`GRAMMAR_DECL` → `IR_SUCCEED` placeholders (regex→NFA is its own pass);
  `HASH_*` → `IR_IDX`/`IR_IDX_SET`; `SMATCH` → `IR_PAT_MATCH`.
- **Pascal**: `TT_FOR → IR_TO_BY` does NOT yet carry loop var/body properly; `GOTO_U`/`LABEL_DEF`
  store label in `LIT.sval` (resolution TBD).
- **ALL**: no goal-directed operand backtracking (e.g. `(1 to 3)+10`) — needs generator-aware
  templates (`IR_BINOP_GEN`/`IR_GEN_*`).

## NEXT (precise)
1. **Integrate Icon into the live build.** Old path is multi-file: `lower.c` (dispatcher ~line 56
   calls `lower_icn(lcx_t cx, tree_t*, γ, ω, &α_out, &β_out)`), `lower_program.c`
   (`lower_icon_body`), `lower_value.c`. Old `lower_icn` returns `IR_t*` into an existing flow; new
   `lower_icon(const tree_t*) -> IR_graph_t*` builds a fresh graph. Plan the swap: retire old
   `lower_*.c`, update `Makefile` + `lower.c` + driver flow + `lower.h`. Promote
   `.github/lower-rebuild/*.c` → `SCRIP/src/lower/`.
2. **Reconcile interp arms** to the new operand contracts (`IR_CALL` operands[0]=callee `IR_VAR`
   naming the builtin; `IR_PROG`/`IR_PROC` entry). Interp run entry = `IR_interp_pump(IR_graph_t*,
   bb_body_fn, void*)` in `src/interp/IR_interp.c`. Link `libscrip_rt` (write/builtins). Get
   `write("hello")` to ACTUAL stdout = rung 0 LIVE.
3. **Climb the shared rung ladder per language** (identical across languages): `0 hello · 1 int
   literal · 2 arithmetic · 3 assign+var · 4 if · 5 while · 6 call · …`. Each rung green before next.
4. **Bring SNOBOL/Prolog/Raku/Pascal online** the same way. SNOBOL first needs the `:pat`/`:repl`/goto
   statement handling + the `IR_PATTERN_*` vs `IR_PAT_*` family confirmation.
This phase is **LANE B — the byte-identical gate WILL churn**; re-baseline as rungs come green.

## DO NOT / state
- SCRIP tree UNTOUCHED this session — builds green at current HEAD. The five files live ONLY in
  `.github/lower-rebuild/` (not built). Promoting them into `src/lower/` collides with the existing
  `lower_icon`/etc. symbols — that collision IS the integration step; handle it deliberately.
- JCON guide = user-uploaded `jcon-master/tran/irgen.icn`: the `ir_a_*` procedures + the `ir()`
  dispatcher + `ir_opfn` are the canonical Icon port-wiring authority. Distilled loop wiring
  (if/while/until/repeat/every/to_by) is in the session transcript.
- Context was tracked all session (Lon polled every turn). The interp+runtime integration is large —
  start it fresh and checkpoint before the window runs low.

**Authors:** Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
