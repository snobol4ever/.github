# HANDOFF 2026-06-03 (Opus 4.8) — Prolog WAM-CP-9-rest SCOPED: NOT mechanical; ITE-commit divergence + m4 nested-ITE link gap

## TL;DR
Investigation only. **No SCRIP / corpus code touched.** SCRIP HEAD unchanged at `5dff1a8` (the
WAM-CP-7c commit). Goal was WAM-CP-9-rest. Finding: it is **three separate issues**, not one mechanical
step, and the riskiest one lives in shared `lower.c` port-wiring. Two of the three named WAM-CP-9 sub-items
are **already done/working**; the real open work is a semantics bug where the **mode-2 oracle itself is
wrong** per the canonical sources. Scoped here for whoever takes it with Lon's go-ahead. Gates re-verified
green (m2 111/111, m3 111/111, m4 75/0/36).

## What WAM-CP-9-rest listed, vs reality
The GOAL line: *"committed-ITE node; bare `!` in `(A;B)` through truncate; retire `g_pl_cut_flag`."*

1. **retire `g_pl_cut_flag`** — ALREADY DONE. `grep -rn g_pl_cut_flag src/` == **0**. It was renamed to
   `g_resolve_cut_flag` (live in `bb_choice.cpp`, `resolution.c`, `unification.c`, `IR_interp.c`, etc.) in
   an earlier rung. Nothing to retire.
2. **bare `!` in `(A;B)`** — WORKING in m2 AND m4. Test `t(X) :- ( X=1, ! ; X=2 ).` driven by backtracking
   prints `1` in both modes (cut commits to first branch, second pruned). No bug here.
3. **committed-ITE** — the REAL open work, and it is a semantics divergence (below), not a node-shape tweak.

## The real finding: ITE does NOT commit to the first condition solution (m2 oracle is WRONG)

`( Cond -> Then ; Else )` must take ONLY the first solution of `Cond` and commit (an implicit local cut on
the condition). **Canonical proof — swipl `src/pl-comp.c` lines 2312–2326:** for `A -> B ; C` it emits
`C_IFTHENELSE` then sets `ci->cut.var = var; ci->cut.instruction = C_LCUT` with the literal comment
**"Cut locally in the condition."** gprolog does the same via its `C_IFTHENELSE`/local-cut. So the
condition's choicepoints are pruned after its first success.

Test `a(1). a(2). a(3). f(X) :- ( a(X), X >= 2 -> true ; X = 0 ).` driven by `( f(R), write(R), nl, fail ; true )`:
- **m2 (`--run`):** prints `2`, `3`, `0`  ← **WRONG** (re-satisfies the condition's `a(X)` and even runs Else)
- **m4 (`--compile`):** prints `2`            ← **CORRECT** per ISO/swipl/gprolog

This is precisely the case RULES.md "CONSULT CANONICAL SOURCES" warns about: *the mode-2 oracle is a
transcription, not the source of truth; when in doubt the canonical source wins.* Here m4 is right and the
m2 transcription is wrong — so the usual "m2 is the correctness reference" inverts for ITE-commit, which is
why this needs Lon's explicit call before touching anything.

**Where it lives:** m2 `IR_interp.c` `case IR_ITE` (line ~3903) is trivial (`bb->value=1; return bb->α`) —
all ITE control flow is in the PORT TOPOLOGY the lowerer builds (`lower.c`, the `IR_ITE` arm; port table in
GOAL: `cond.α; ω_in semidet; cond.γ→Then, Then.γ→γ_in; cond.ω→Else, Else.ω→ω_in`). The fix is making the
condition's choicepoints get truncated on first success in BOTH the m2 port wiring and the m4 emit — a
shared-`lower.c` change (SHARED-LOWERER concurrency rule) that risks the 111/111 byte-identity gate. **Not
mechanical; needs Lon's design sign-off.**

## Bonus bugs found while probing (both real, both need their own fix)
- **m2 ITE with a bare-call condition prints nothing.** `( ( a(X) -> true ; fail ), write(X), nl, fail ; true )`
  → m2 emits NO output (expected `1`). Separate m2 ITE/var-binding bug from the commit issue above.
- **m4 nested-ITE-with-call fails to LINK.** Same program → m4 `as`/`ld` error:
  `undefined reference to '.Lplpred____2'` / `.Lplpred____2_redo` — a forward label to a predicate body the
  emitter referenced but never emitted (nested ITE inside a `( … ; true )` disjunction). A codegen
  completeness gap, independent of the semantics question.

## Why I stopped here (judgment)
At ~65% context on a codebase where broken commits are forbidden, and with the actionable part being a
shared-`lower.c` port-wiring change that (a) inverts the usual m2-is-oracle assumption, (b) touches the
concurrency-sensitive lowerer, and (c) risks the proven 111/111 gate — starting the fix now risks leaving
the tree half-converted. The right artifact is this scoped finding + canonical citation, not a rushed
structural edit. **No code touched; HEAD `5dff1a8`; all gates green.**

## NEXT — recommended order (all need Lon's nod for the ITE one)
1. **Decide the ITE-commit fix** (needs Lon): make `( C -> T ; E )` truncate C's CPs on first success.
   Likely a `bb_cut`-style local-cut barrier inserted on the condition in `lower.c`'s `IR_ITE` arm, mirrored
   into m2 port wiring + m4 emit. Re-baseline any rung whose `.expected` encodes the wrong `2 3 0` behavior
   (audit needed — some current rungs may PASS *because* they match the buggy m2).
2. **m4 nested-ITE link gap** — emit the missing predicate body / fix the forward-label (`.Lplpred____N`)
   resolution for ITE nested in disjunction. Independent; can land alone.
3. **m2 ITE bare-call no-output bug** — separate m2 fix.

Other unblocked WAM-CP work untouched and still available: WAM-CP-11 (deep-backtrack arg restore),
WAM-CP-12 (determinism→CP elision, lower-time), PL-INDEX-L2-1 (hash dispatch >8 clauses).

## Build / verify recipe (re-confirm green; no code to build beyond HEAD)
```bash
cd /home/claude/SCRIP && make -j4 scrip && make libscrip_rt
bash scripts/test_prolog_rung_suite.sh       # m2 111/111, m3 111/111, m4 75/0/36
# reproduce the ITE-commit divergence:
printf ':- initialization(main).\na(1). a(2). a(3).\nf(X) :- ( a(X), X >= 2 -> true ; X = 0 ).\nmain :- ( f(R), write(R), nl, fail ; true ).\n' > /tmp/ite.pl
./scrip --run /tmp/ite.pl </dev/null            # WRONG: 2 3 0
bash scripts/run_prolog_via_x86_backend.sh /tmp/ite.pl </dev/null | tail -3   # CORRECT: 2
# canonical proof: refs/swipl-devel-master/src/pl-comp.c lines ~2312-2326 ("Cut locally in the condition")
git -C /home/claude/corpus checkout -- programs/prolog/*.s   # suite regenerates .s; re-clean
```
Authors: LCherryholmes · Claude Opus 4.8
