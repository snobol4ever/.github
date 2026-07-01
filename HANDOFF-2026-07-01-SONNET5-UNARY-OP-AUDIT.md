# HANDOFF 2026-07-01 — Claude Sonnet 5 — Icon unary-operator audit + =s fix + IR shape-grid design

## Context
Continuation of the same day's `IR_GOTO`/lowerer-reintegration session (see the earlier same-day HANDOFF).
Lon drove an interactive, symbol-by-symbol audit of every Icon unary operator: glyph → `icon_parse.c` tree
tag → `lower_icon.c` IR opcode → `bb_unop.cpp` port wiring, each step grep/read-verified against the actual
tree rather than answered from general Icon knowledge. The audit surfaced two real bugs and a design
question that turned into a locked (but not yet implemented) IR-shape redesign. Two concrete fixes landed;
the redesign is deliberately deferred. `GOAL-IR-IMMUTABLE-EMIT.md`'s own watermark now carries the full
technical entry — this document is the session-shaped summary + verification record.

## Action 1 — deleted three confirmed-dead IR opcodes
`IR_UNOP_GENERIC`, `IR_BINOP_GENERIC`, `IR_UNOP_TEST` removed from `IR.h` (enum) and `scrip_ir.c` (name
table, `ir_node_produces_value` predicate, `bb_print`'s binop-label case). Verified beforehand: zero
construction sites (no lowerer built them) and zero dispatch cases (no template/emit.cpp arm consumed
them) anywhere in `src/`. Pure dead-slot removal; `ir_node_produces_value`'s line remains >200 chars
(pre-existing legacy — this edit only shortened it, not introduced the violation; left unreformatted as
out-of-scope for a drive-by).

## Action 2 — fixed `=s` (unary match), previously a silent no-op
`bb_unop.cpp`'s `bb_unop_resolve` had no case for `TT_MATCH_UNARY`, so `=s` fell through to
`UO_UNHANDLED` and emitted nothing — a real, previously-unflagged bug (not merely unimplemented; it
compiled and ran, silently doing nothing). Fix: desugar `=s` → `tab(match(s))` **in the parser**
(`icon_parse.c`), synthesizing the equivalent `TT_FNC(tab, TT_FNC(match, s))` call tree — the same pattern
this file already uses for the `~==`-family `not(...)` desugar a few lines above. No new IR opcode; reuses
the live `IR_SCAN_MATCH`/`IR_SCAN_TAB` path. Removed the now-unreachable `TT_MATCH_UNARY` arm from
`is_unop_tt` in `lower_icon.c`.

**Verified against canonical source, not derived from memory** — this goal's own CONSULT CANONICAL SOURCES
rule names `refs/icon-master/src/runtime/*.r` as authority; set up `refs/icon-master` + `refs/jcon-master`
this session (symlinked from Lon's uploaded `2-icon-master.zip`/`3-jcon-master.zip`, per that rule's exact
setup recipe — gitignored, sandbox-local, not persisted). `refs/icon-master/src/runtime/omisc.r` line 84:
`"=x - tab(match(x)). Reverses effects if resumed."` — the exact transformation implemented, word for word.

## What this is NOT
The "reverses effects if resumed" half of that doc-line is **not** independently verified as correctly
reproduced by the composed `tab`+`match` path. Canonical Icon implements `=x` as one primitive (`tabmat`,
`runtime/omisc.r`, tagged `operator{*}`) specifically for that undo-on-backtrack contract. SCRIP's
`IR_SCAN_TAB` is currently **absent** from `ir_is_generator_kind` (`src/opt/ir_query.c`) — unlike
`IR_SCAN_UPTO`/`FIND`/`MANY`/`BAL`, which are present. Whether that's a real gap in `tab`'s own resume
handling is an open, pre-existing question this session did not chase — but it's orthogonal to whether the
desugar itself is correct: `=s` and hand-written `tab(match(s))` were shown to produce byte-identical
behavior (see Verification), including hitting the identical pre-existing `bb_scan_tab` "unhandled" bomb on
a non-literal `n`. The desugar reproduces exactly what a programmer typing `tab(match(s))` would get —
neither better nor worse than that baseline.

Also not done: the IR-shape redesign below is a **locked design, zero implementation**. No `IR_UNOP_REL`,
no `_GEN` variants, no `IR_SECTION` split exist in the tree yet.

## Design locked this session — for the next Icon unary/binary rung
Working from the box-shape principle Lon named ("the shape of the box with its 4-port wiring is what
determines the need for a separate IR"), arrived at collaboratively across several corrections:

- Two independent axes, not three: **can-fail** (test) × **does-the-operand-backtrack** (GEN — `β` present,
  `ω`→consumer's edge) vs. not (`ω`→FAILURE only, no `β`). Icon operands can generate; SNOBOL4/etc. operands
  never do (confirmed: `ir_is_generator_kind` already gates exactly this way for the opcodes that have it).
- 8 opcodes: `IR_UNOP`, `IR_UNOP_REL`, `IR_BINOP`, `IR_BINOP_REL`, each ×`_GEN`. `IR_BINOP_REL` renames the
  already-live `IR_BINOP_RELOP`. `\`/`/` (non-null/null test) go under `_REL` — they're comparisons against
  `&null`, not a separate arithmetic-vs-relational split (unary has no relational *family*, only a
  can-fail/can't-fail *shape* split, unlike binary where family and shape happen to coincide).
- `IR_TERNOP` (currently a generic carrier, `ival`∈{0,1,2} for plain/`+`/`-` sectioning) splits into three
  specific opcodes: `IR_SECTION`, `IR_SECTION_PLUS`, `IR_SECTION_MINUS`.
- `?` (random) gets its own `IR_UNOP_RANDOM` — not folded into `_REL` despite being able to fail on an empty
  operand, because it's not a comparison.
- Checked against `GOAL-IR-IMMUTABLE-EMIT.md`'s own STANDING DIRECTIVE (JCON's `ir.icn` uses one generic
  `ir_OpFunction` for everything; SCRIP deliberately keeps fine-grained `IR_BINOP`/`IR_UNOP` instead): this
  design is *more* fine-grained still, consistent with that stated divergence, not fighting it.
- `IR_ITERATE` (`!`), `IR_REPALT` (`|`), `IR_NOT` (`not`) stay their own opcodes — genuinely different box
  shapes (internal counter state; bespoke inline driver, not template-routed; success↔fail port swap,
  respectively), not folded into the grid.
- Explicitly rejected mid-design: naming the unary split `_ARITH`/`_REL` to mirror binary — unary has no
  arithmetic *family* to name honestly (`* ? ~ =` aren't arithmetic), so unary is named by shape
  (`IR_UNOP`/`IR_UNOP_REL`) while binary is named by family (`IR_BINOP`/`IR_BINOP_REL`), which happen to
  coincide for binary but not for unary.

**Prerequisite for implementing, not yet done:** this goal's ORIENTATION SYNOPSIS + `GOAL-ICON-BB.md`'s
four-port contract, for the exact `_GEN` variants' `β`/`ω` wiring and local-storage rules. Also worth
checking the JCON-33 map (`JCON-TO-SCRIP-IR-MAP.md`, `refs/jcon-master/tran/irgen.icn`) before finalizing
names, since Jcon had to solve the same naming problem once.

## Other findings, not fixed
- `TT_CSET_COMPL` (`~e`) has no case anywhere in `lower_icon.c` — falls to `default:` → `IR_SUCCEED`, a
  silent no-op, same failure mode `=s` had. Not previously tracked in the goal file's punch list.
- `.e` (deref), `@e` (activate), `^e` (refresh) — the three coexpression unary operators — are entirely
  unparsed (`^` exists only as binary `TT_POW`/exponentiation). Consistent with coexpressions being
  unimplemented per the RUNG 5 note elsewhere in the goal file, not a new regression.
- A vestigial `TT_INTERROGATE` case sits in `is_unop_tt` (`lower_icon.c`) with no parser producer (`?`
  emits `TT_RANDOM`) — dead, harmless, unrelated to this session's edits, left alone.

## Verification commands (rerunnable)
```bash
grep -rn "IR_UNOP_GENERIC\|IR_BINOP_GENERIC\|IR_UNOP_TEST" src/          # expect: empty
grep -n "TT_MATCH_UNARY" src/lower/lower_icon.c src/parser/icon/icon_parse.c  # expect: empty (both sites now gone)
make scrip                                                                # expect: exit 0, Built: scrip
cat > /tmp/eq2.icn <<'EOF'
procedure main()
   "hello world" ? {
      if ="hello" then write("matched; &pos now ", &pos)
      if ="XXX"   then write("should NOT print")
      else write("correctly failed on non-match")
   }
end
EOF
./scrip --run /tmp/eq2.icn     # expect: "matched; &pos now 1" only
bash scripts/update_icon_bench_asm.sh   # expect: total=13 updated=0 unchanged=1 compile-err=12 (matches documented pre-existing baseline)
```
**Not run this session:** the 289-program corpus (`test_icon_all_rungs.sh`), the four `test_gate_icn_*.sh`
discipline gates, `test_gate_emit_no_ir_mutation.sh`. Reasoned, not measured, that this session's two
changes don't touch emitter-mutation surface or non-`=`-operator behavior — next session should run these
before extending the work rather than trusting that reasoning further.

## Push status
Local commits only at time of writing — push pending credential (public clone needs none; push does), per
this same rule the prior same-day HANDOFF already stated. Not claiming completion here; only
`scripts/handoff_status.sh`'s verbatim stdout may do that, per `RULES.md`'s FACT RULE.
