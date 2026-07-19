# FINDING 2026-07-19 — ICN-CASE-ALT-CLOSE: jtran parse_expr11 blocker closed; runerr() added; ucode pipeline advances

Session (Lon: "get JCON self-hosting under SCRIP"). Base SCRIP `3615fb50`, .github `7a65d854`.
Rung suite baseline (this sandbox, pre-fix): **241/20/32** — same environmental math drift as prior finding.

## CONTEXT: previous open blocker

Prior finding (R8-CLOSED) ended: parse 4-stage pipeline `preproc:yylex:parse:stdout` yielded
`File hello_t.icn; Line 2 # Expecting ;`.  Hypothesis was `do_proc_set` construction or a
missing-resume family in `parse_locals`/`parse_do_initial`.

## DIAGNOSIS: hypothesis disproven; root cause ICN-CASE-ALT residual

Five probes injected at the `while member(do_proc_set, parse_tok_rec)` guard:
- P1: tok.str=[write] setsize=46  — set intact, 46 members
- P2: tok===IDENT=Y               — token record identity correct
- P3: member(set,tok)=Y           — member SUCCEEDS
- P4: member(set,lex_IDENT)=Y     — lex_IDENT in set
- P5: END.str=[end] SEMI.str=[;] END===SEMI=N  — tokens distinct

Entry probes on all 14 precedence-ladder procedures showed the full descent through
parse_expr → parse_expr1a → ... → parse_expr11 → **"Expecting ;"**.

`parse_expr11` is a large `case parse_tok_rec of` with ALTERNATED selectors in the
primary arm: `lex_CSETLIT | lex_INTLIT | lex_REALLIT | lex_STRINGLIT : parse_literal()`.
When the selector is `lex_IDENT` (= `write`), the alternated literal chain is resumable —
it iterates the alternatives — exhausts all four — and then the **exhaustion exit was
case-ω rather than the next clause** (`lex_IDENT : a_Ident(...)`).  This is exactly the
ICN-CASE-ALT residual documented in the prior commit (2026-07-19 `3615fb50`): "bites only
when an alternated arm is followed by more arms AND matches none of its alternatives".

## FIX A — ICN-CASE-ALT-CLOSE [src/lower/lower_icon.c TT_CASE]

Canonical `ir_a_Case` (refs/jcon-master/tran/irgen.icn line ~274):
```
suspend ir_chunk(L[i].expr.ir.failure, [ ir_Goto(..., L[i+1].expr.ir.start) ])
```
i.e. clause-expr **failure/exhaustion → next clause**.

Previous attempt to wire `fail → chain_next` regressed rung14_case_return_arm +
4× rung33_case (emit-walk/fold interaction — the literal arms have a statically-dead ω
edge and passing chain_next there confused the BFS fold).

**Fix:** gate on `is_resumable(t->c[ki])`:
- **Resumable selector** (alternation, generator, `!`, `to`): `ksel_ω = chain_next` —
  exhaustion falls through to the next clause exactly as canonical ir_a_Case requires.
- **Non-resumable selector** (literal, plain ident): `ksel_ω = ω` — byte-identical to
  baseline; their ω edge is statically dead (literals cannot fail), so BFS fold sees
  no change.

Verified: 5-shape repro battery green both modes:
1. `case 9 of { 1|2:"A"; 3|4:"B"; default:"dflt" }` → dflt (exhaustion→default) ✓
2. `case 4 of { 1|2:"A2"; 3|4:"B2"; default:"d2" }` → B2 (exhaustion→next-arm then match) ✓
3. `case 2 of { 1|2|3:"alt-hit"; default:"d3" }` → alt-hit (alt-match in first arm) ✓
4. `case (1 to 5) of { 9:...; 7:... } | write("case-failed")` → case-failed (bounded gen selector, case-ω→alternation) ✓
5. `case x of { 1|2:"no" } | write("lastfail-ok")` → lastfail-ok (no match, no default, case fails) ✓

Rung suite: **241/20/32, fail-list BYTE-IDENTICAL to baseline** (zero regressions).

## FIX B — runerr() builtin [src/runtime/by_name_dispatch.c]

`runerr(i, x)` is called throughout jtran (lexer.icn, parse.icn, irgen.icn, gen_ucode.icn)
as the canonical assertion/error termination.  It was unresolved — `SCRIP_DEBUG_APPLY=1`
named it as the Error 5 source in the ucode stage.

Added arm mirrors canonical `fmisc.r`:
- Prints `Run-time error N\n` to stderr
- If second arg present: calls `image(x)` via the dispatcher's own arm, prints `offending value: <img>\n`
- `exit(1)` — error path, unlike `stop()`'s held rc-0

## Pipeline state after both fixes

```
hello_t.icn (canonical newline-Icon, 3 lines):
  procedure main()
     write("hello")
  end

./jtran preproc hello_t.icn : stdout           ✓  (4 lines)
./jtran preproc hello_t.icn : yylex : stdout   ✓  (13 tokens)
./jtran preproc hello_t.icn : yylex : parse : stdout  ✓  a_ProcDecl
./jtran preproc hello_t.icn : yylex : parse : u_gen_File -out:hello_t  → OPEN BLOCKER
```

The ucode stage now runs past `runerr` (which is gone as a blocker) and hits a new
Error — **`SCRIP_DEBUG_APPLY=1` diagnosis needed next session** to name the next
unresolved operation or misfiring assertion.  The `.u1`/`.u2` output files are still 0 bytes.

## NEXT SESSION OPENER

1. `SCRIP_DEBUG_APPLY=1 ./jtran preproc hello_t.icn : yylex : parse : u_gen_File -out:hello_t 2>&1`
   — read the `[apply-err5]` line to name the next unresolved or the `runerr` offending value.
2. If `runerr(500, p)` fires from gen_ucode.icn: `p` is an AST node whose `u_` dispatch
   table has no entry — check `gen_ucode.icn` `fn` table construction and the `ir_a_*`
   types it covers; compare `image(p)` output to the `a_*` record types in ast.icn.
3. Advance the pipeline rung by rung until `.u1`/`.u2` are non-empty.
4. Then: link `.u1`/`.u2` via `jlink` (or direct ucode→x86 path), run, compare output.
5. Performance bench (iconx vs JCON vs SCRIP-jtran) deferred until selfhost round-trip works.

## jtran workdir: /home/claude/jt/

- `hello_t.icn` — 3-line canonical newline-Icon (NOT semicolonized — only jtran's own sources need that)
- `jtran` — the SCRIP-compiled 17-module merge binary (m4, SCRIP_BETA_ELIDE_OFF=1)
- `jtran_all.icn` — merged source (dump → do_ops → ... → jtran_main, semicolonized)
- `oplexgen`, `interfacegen`, `do_ops.icn`, `interface.icn` — generated, correct

## Board

Icon rungs 241/20/32. Smokes: n/a (test_icon_smoke.sh path not found in this build).
Gates: icn_no_stack OK (count 0 ≤ 127), one_reg_frame OK (count 0 ≤ 21), emit_no_lang OK.
medium_invisible --strict FAILS at baseline (xa_flat.cpp 112 — pre-existing, not this session).
Authors: Lon Jones Cherryholmes · Jeffrey Cooper M.D. · Claude
