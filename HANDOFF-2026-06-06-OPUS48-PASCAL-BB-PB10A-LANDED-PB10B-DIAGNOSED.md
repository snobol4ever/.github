# HANDOFF — 2026-06-06 — Opus 4.8 — PASCAL-BB session 19

## What landed

**PB-10a — boolean value semantics, parser-only.** SCRIP `6e6e29a` (pascal.y + regenerated
pascal.tab.c/h), corpus `440a19c` (probes) + boolarg follow-up commit, .github `c1b6a721` + this
handoff. Gate at close: **m2 41/0, m3 39/0, m4 39/0, SNOBOL smoke 19/0.**

The three session-18-audited bugs are fixed:
1. `b := relop_false` no longer kills the program — stores INTVAL(0).
2. `b := relop_true` stores INTVAL(1), not rv.
3. `not f` is boolean NOT, not goal-direction inversion.

Mechanism: `pas_bool(e)` wraps a relop as `TT_IF(relop, ilit(1), ilit(0))` at exactly two value
boundaries — assignment RHS (`mk_assign($1, pas_bool($3))`) and the call-arg value slot (width
expression untouched). `NOTSY factor` emits `pas_flip_rel(pas_cond($2))`.

## The deviation, and why (read before judging the diff against the old spec)

Session 18's spec said NOTSY should emit `TT_IF(pas_cond(f), ilit(0), ilit(1))`. **Measured fact: a
TT_IF subgraph as an ARITH OPERAND silently dies in m2 even on the TRUE path** (probe: `c := not a
or b` → TT_IF inside TT_ADD → no output, rc=0). The spec's own gate (`not/and/or chains`) is
unreachable with that shape. The flip-rel form keeps NOT inside the relop algebra (LT↔GE, LE↔GT,
EQ↔NE; non-relop factor → `EQ(x,0)`), which:
- works in condition position, assignment RHS (via pas_bool), and arg position (via pas_bool);
- is correct for or-encoded stored values >1 (`a or b` stores a+b — pre-existing encoding
  looseness, noted, not this rung);
- leaves the 10b/10c boundary IR shapes EXACTLY as session 18 designed (`TT_IF(relop,1,0)` at
  assignment/arg) — PB-10b's plan is untouched.

## Fourth bug discovered → new rung PB-10a2 (NOT fixed)

A FALSE relop as an arith operand propagates goal-failure and kills the m2 statement chain
(`c := (i = 0) or b` prints nothing; rest of program never runs). A TRUE relop leaks rv as its
value. Pinned by XFAIL probe `corpus/programs/pascal/boolmix.pas` (oracle `0`, scrip silent).
This is LOWER work — value-subgraphs don't run junctions — not parser work. Rung text in
GOAL-PASCAL-BB.md.

## PB-10b — DIAGNOSED, zero emitter code written

Probe `boolarg.pas` committed (booleans must flow through a user proc — `writeln(bool)` is
error 399). Oracle `1 0 1`; **m2 green; m3 and m4 both print `1 1 1`** — session 18's predicted
shape CONFIRMED: arg subgraph entry = IR_VAR (relop lhs), γ-chase (bb_call.cpp:233-234) runs to
fin=IR_LIT_I(1), relop IR_BINOP mid-chain with ω→IR_LIT_I(0); the gvar-read arm
(bb_call.cpp:246) fires first and marshals the lhs var (i=3, truthy → 1 every time).

Implementation map (all verified against source this session, no guesses):
- New arm in `marshal_call_arg` BEFORE the gvar-read arm. γ-walk lf for IR_BINOP with relop ival;
  require fin→IR_LIT_I(1) and relop→ω→IR_LIT_I(0).
- `arith_operands(sg, relop, &a, &b)` resolves BOTH binop layouts (direct α/β and PEERS
  operand_aux sidecar; sg is already threaded through the marshal chain since PB-9f).
- Reuse `arith_opnd_a` (→rax; spill to `bb_slot_alloc16` scratch) + `arith_opnd_b` (→rcx) —
  they already accept LIT_I/VAR/FRAME/FRAME_REF/CALL/nested-BINOP.
- Emit: `mov qword [r12+aoff], 6` (INTVAL tag) · reload rax · `cmp rax, rcx` ·
  `x86_jcc_id(fail_mnem, 0)` · store 1 → `[r12+aoff+8]` · `x86_jmp_id(1)` · `x86_deflabel_id(0)` ·
  store 0 · `x86_deflabel_id(1)`. Both MEDIUM_TEXT and MEDIUM_BINARY ride the same helpers.
- Label IDs 0/1 are collision-safe: `x86_internal_name` = `.Lx<_.x86_uid>_<n>`, uid per emitting
  box (x86_asm.h:216); ≤1 relop arg per call by spec.
- Duplicate (per RULES, never share) `arith_is_relop` + `relop_fail_mnem` into bb_call.cpp.
  Fail mnemonics (from bb_binop_gvar_relop.cpp `gvr_mnem`): LT→jge, LE→jg, GT→jle, GE→jl,
  EQ→jne, NE→je. Relop codes are the contiguous BINOP_LT..BINOP_NE range.
- Gate: boolarg m3+m4 → `1 0 1`; boolassign/boolnot m3+m4; legacy 39 m3/m4 + SNOBOL 19/0 hold.

## Landmines (each cost real time this session — do not skip)

1. **`scrip:` Makefile target has NO prerequisites.** With the binary present, `make scrip` does
   nothing and your edit silently doesn't take (symptom: AST/asm unchanged after a "successful"
   build). `rm -f scrip && make -j4 scrip` always.
2. **Do NOT run `regenerate_parser_and_lexer_from_sources.sh`** — it DELETED `snobol4.lex.c`
   (aborts at the snobol4 flex step). Regen pascal directly:
   `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y` (1 s/r conflict = pre-existing
   dangling-else). Restore casualties: `git checkout -- src/parser/snobol4/...`.
3. Template edits: `touch` the template before `make scrip` (explicit compile rules).
4. fpc install on this image: `apt-get install -y fp-compiler-3.2.2 fp-units-base-3.2.2
   fp-units-rtl-3.2.2` (full `fpc` metapackage 404s on liblzma-dev).
