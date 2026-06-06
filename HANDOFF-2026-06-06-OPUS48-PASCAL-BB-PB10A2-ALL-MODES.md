# HANDOFF — 2026-06-06 — Opus 4.8 — PASCAL-BB session 21

**PB-10a2 LANDED in TWO same-session rungs; the second supersedes the first's mechanism. The Pascal
boolean story is CLOSED IN ALL MODES.** SCRIP `6baba7a` (v1, m2-only) + `e30988e` (v2, all modes);
corpus `3143424` (boolchain.pas); .github `8f5445d4` + `f1cd3fa3` + `95e755d2` (goal watermark ×2) +
this doc. Gate at close: **m2 44/1, m3 44/1, m4 44/1 — UNIFORM**, sole fail = recursion.pas (16-bit
maxint pin), over 45 probes. SNOBOL smoke 19/0. boolmix + boolchain oracle-exact m2/m3/m4 incl. double
diamonds; chains in if-condition position with proc calls verified all modes. sieve.s + m4wexpr.s
byte-identical vs the rebased base (stash-proven).

## What the bug was (s19 diagnosis, confirmed in source)

A relational operand of a Pascal arith binop (`c := not a or b` → `TT_ADD(TT_EQ(a,0), b)`) was
goal-directed in the IR: v_binop lowered the relop child with ω = the outer fail, so a FALSE relop
killed the statement chain (silent death, rc=0) and a TRUE one leaked rv (`binop_apply` returns the
RHS) as its value.

## v1 (SCRIP `6baba7a`) — ring-mode IR_IF join, m2-only

`pas_bool_operand`: relop γ→IR_LIT_I(1), ω→IR_LIT_I(0), both lits γ→one IR_IF join (α=β NULL). FACT
that makes it work in m2: the driver pushes EVERY node's value to the ag_ring after each step
(IR_interp.c:5282), so at the join ring(0) is always the just-executed lit, never FAIL; the join copies
ring(0) into its own value for `bb_operand_aux_get`. m2 went 44/1; m3/m4 bombed LOUD on boolmix/boolchain
(`walk_bb_node kind=7 IR_BINOP unhandled` + `bb_gvar_assign op_a_slot==-1`, rc=134) — pinned, then fixed
same session.

## v2 (SCRIP `e30988e`) — pas_bool_diamond prefix hoist, ALL MODES — the live mechanism

**The m3/m4 FACT that forced the redesign** (emit_bb.c read, carry forward for ALL gvar-chain value
work): `walk_bb_node` has NO bare IR_BINOP case — the gvar flat chain promotes IR_BINOP to
IR_BINOP_GVAR_{RELOP,ARITH,ARITH_SLOT} at the chain driver (emit_bb.c:2182) using α/β operand pointers
that are populated beforehand by `gvar_stmt_operand_refs` (emit_bb.c:2732): a STACK SIMULATION over the
γ-spine, arity per `gvar_chain_arity`/`descr_chain_arity` (leaves push; binops pop 2, push self; assigns
pop 1, push self; unknown kinds = arity −1 = STACK RESET). Consequence: **a consumer's operands must be
the MOST RECENT pushes on the spine.** Any in-place diamond interleaves junk pushes (the relop, the arm
assign) between sibling operand pushes and breaks every multi-operand case; IR_IF's arity −1 is exactly
why v1's join left the outer ADD with α=β NULL → raw kind=7 → bomb. An IR_SUCCEED γ-target BREAKS the
operand walk and spawns a fresh head (fresh stack) — barriers do NOT compose either (operands before the
barrier are lost).

Fix shape (lower.c only, ZERO emitter changes, LANGUAGE-BLIND rule untouched): for
`cx.lang==IR_LANG_PAS`, a RELATIONAL child of ANY v_binop lowers as the PROVEN statement-IF shape —
relop γ→LIT_I(1)→IR_ASSIGN(`__pbt%d`), ω→LIT_I(0)→IR_ASSIGN(same temp) — with the whole diamond HOISTED
AS A CHAIN PREFIX before the expression, and a bare `IR_VAR(__pbt%d)` left in operand position. With the
hoist, junk sinks below all expression pushes and every pop lines up; the operand refs resolve to
VAR/VAR, VAR/LIT, VAR/slot etc. and the EXISTING GVAR_RELOP / gvar lit-assign / gvar var-read /
GVAR_ARITH(_SLOT) arms emit everything. m2 unchanged in behavior: arms store via ring(0)=lit, rd reads
NV, binop aux reads rd.value. Temps: static counter, deterministic per run; P4 idents are
`[a-z][a-z0-9]*` so `__` can't collide. Wiring order with both operands relational: diamond1 → diamond2
→ rd1 → rd2 → bin; b2-only hoists diamond2 before the lhs (see residue 1).

## Residues (documented, no probe forces them)

1. Hoisting a RIGHT relop diamond over a LEFT non-relop operand reorders evaluation when the left
   operand has side effects (function calls). All modes uniformly; diverges from pcom's strict
   left-to-right only for side-effecting boolean operand mixes.
2. An NV `__pbt` temp can be clobbered if a call in a LATER operand recursively re-enters the same
   expression. Same hazard class as node-value aux reads; frame-slot temps would cure it.
3. PB-10c residue stands: `a[i] := relop` and `funcname := relop` still ride the value diamond.
4. case/goto remain TT_SUCCEED stubs; recursion.pas pinned on 16-bit maxint.

## Gotchas (each cost or saved real time this session)

1. **Concurrent-push discipline is now the dominant session tax.** THREE waves landed mid-session
   (HY-7d/7e call-arg slots + LIT adoption with PASCAL arms; then SNO-HY-2b/PL-GZ-7/FIXUP). Every
   `git pull --rebase` → `rm -f scrip && make` → FULL gate re-run. All three re-verifications held.
2. **Byte-identity baselines go stale at every rebase.** /tmp captures from before HY-7d/7e showed
   "drift" that was entirely theirs. Disambiguate with the stash test: `git stash` → build → capture
   rebased-base .s → `git stash pop` → build → cmp. Never compare against pre-rebase captures.
3. Standing landmines re-confirmed: `rm -f scrip` before `make scrip` (target has no prerequisites);
   `touch` templates before building; pascal regen ONLY via
   `cd src/parser/pascal && bison -d -o pascal.tab.c pascal.y`; fpc needs `apt-get update` first, then
   plain `apt-get install -y fpc` works.
4. Suite runner shape (no checked-in script): oracle = `./pcom < p.pas && cp prr prd && ./pint
   < /dev/null`; m2 `--interp`; m3 `--run`; m4 `--compile` → `gcc -no-pie p.s out/libscrip_rt.so
   -Wl,-rpath,SCRIP/out`. 45 probes = all *.pas minus pcom/pint/ppp. timeout 8s + `< /dev/null` per
   RULES.

## Next

Suite is clean AND uniform modulo the maxint pin. Lon picks: (a) PB-10c residue shapes (`a[i] := relop`,
`funcname := relop`); (b) case/goto when a probe forces them; (c) the 16-bit maxint rung for
recursion.pas.
