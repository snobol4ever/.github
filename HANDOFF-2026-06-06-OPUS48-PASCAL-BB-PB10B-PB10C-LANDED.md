# HANDOFF — 2026-06-06 — Opus 4.8 — PASCAL-BB session 20

**PB-10b + PB-10c LANDED. SCRIP `1ad0019` (10b) + `3ec6470` (10c). The boolean m3/m4 story is closed.**
Gate at close: Pascal m2 42/2 · m3 42/2 · m4 42/2 — UNIFORM across modes for the first time; fails =
boolmix (PB-10a2) + recursion (16-bit maxint) only, identical in every mode. SNOBOL smoke 19/0.
sieve.s + m4wexpr.s byte-identical through both rungs. Re-verified green after rebasing onto concurrent
BB-FIXUP pushes (incl. the bb_builtin_*->bb_* rename). Repos: SCRIP (2 commits) + .github (goal + this
doc). corpus untouched.

## PB-10b — call-arg relop marshal (bb_call.cpp, +44 lines)

Session 19's map executed verbatim with ONE forced deviation. New arm in `marshal_call_arg` BEFORE the
gvar-read arm: γ-walk lf to the relop IR_BINOP, require fin→IR_LIT_I(1) and relop→ω→IR_LIT_I(0);
operands via `arith_operands` (both binop layouts); reuse `arith_opnd_a` (→rax, `bb_slot_alloc16`
spill) + `arith_opnd_b` (→rcx); `cmp rax,rcx` + conditional INTVAL(0/1) store. `arith_is_relop` +
`relop_fail_mnem` duplicated into bb_call.cpp per RULES.

**The deviation — label IDs.** The map blessed internal ids 0/1 as collision-safe on the premise "uid
is per emitting box". FALSE on the Pascal gvar flat chain in MEDIUM_TEXT: the whole chain shares ONE
`_.x86_uid` — m4 assembled `.Lx4_0` three times (one per show() call). m3 passed because BINARY label
records genuinely ARE per-box. Fix per the session-17 single-call precedent: TEXT labels
`.Lbrel%d_f/_e` keyed by `bb_node_id(relnd)`; BINARY keeps per-box `idx*2/idx*2+1` (the LIT_S id
namespace — an arg is one or the other, never both), guarded against X86_INTERNAL_MAX (16). **Carry
forward: never assume per-box uid for TEXT internal labels inside the Pascal flat chain.**

## PB-10c — assignment RHS (pascal.y only; the emitter-arm sketch was wrong)

The rung mandated diagnosis first; diagnosis killed the sketch. Measured facts (boolassign m4 asm +
emit_core.c + bb_gvar_assign.cpp read): the IR diamond is CORRECT — relop γ→LIT(1)→ASSIGN,
ω→LIT(0)→ASSIGN, converging control. The bug is `IR_ASSIGN(lit_i)` resolving its RHS at EMIT time to
whichever single literal `assign.α` points at (`walk_bb_node`: `op_a_node_kind = α->t`,
`op_a_ival_sg = α->ival` — boolassign stmt 1 stored constant 0, stmts 2-6 stored 1; output `0 1 1 1 1 1`
vs oracle `1 0 0 1 1 0`). The relop is UNREACHABLE from template handles: no back-pointers, nothing in
the emit context. An emitter arm therefore needs new dispatcher plumbing plus a redundant relop
re-eval — and the LANGUAGE-BLIND FACT RULE puts language-shaped behavior in parser/LOWER, never in a
template arm.

Fix: the `assignment:` action rewrites `var := relop` (dst TT_VAR only) into the statement-IF
`TT_IF(relop, var:=1, var:=0)` — proven-green statement-IF + lit-assign shapes in ALL modes, fixing
gvar AND frame destinations at once. The pas_bool diamond is retained where it is correct: the
call-arg boundary (10b's arm) and non-VAR destinations.

RESIDUE (no probe forces these yet): `a[i] := relop` and `funcname := relop` (funcname selector is
TT_FNC via mk_ident's pas_is_func branch) still ride the diamond → wrong in m3/m4 if ever exercised.

## Gotchas (each verified this session)

1. `rm -f scrip` before `make scrip` — target has no prerequisites.
2. `touch` templates before building — explicit compile rules.
3. Pascal regen ONLY via `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y` (1 s/r =
   dangling-else). Never the full regen script.
4. fpc on this image: `apt-get update` first, then plain `apt-get install -y fpc` works — s19's
   liblzma 404 is cured by the update; the fp-compiler-3.2.2 split-package workaround is obsolete.
5. Suite runner shape: oracle = `./pcom < p.pas && cp prr prd && ./pint < /dev/null`; m3 = `--run`;
   m4 = `--compile` → `gcc -no-pie p.s out/libscrip_rt.so -Wl,-rpath,SCRIP/out`. timeout 8s +
   `< /dev/null` everywhere per RULES.
6. Regression discipline that paid off twice: capture pre-edit m4 .s baselines (sieve, m4wexpr) and a
   git-stash pre/post run of any probe whose status is ambiguous — the stash test proved
   boolassign/boolnot m3/m4 failures pre-dated 10b in one cycle.

## Next

PB-10a2 — the LAST boolean rung and the only non-pin failure (LOWER: relop/IF as arith operand,
boolmix.pas; FALSE relop operand of TT_ADD/TT_MUL propagates goal-failure and kills the statement
chain, TRUE leaks rv; fix in `v_binop`/`lower_value_subgraph`). After it the suite is clean modulo the
recursion maxint pin; case/goto remain TT_SUCCEED stubs until a probe forces them.
